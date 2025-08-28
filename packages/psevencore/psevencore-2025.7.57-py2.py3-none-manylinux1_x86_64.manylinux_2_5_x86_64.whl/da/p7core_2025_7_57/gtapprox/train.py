#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
# pSeven Core GTApprox submit script

from __future__ import with_statement

import getopt
import sys
import re
import os
import numpy as np

from ..loggers import StreamLogger, LogLevel
from ..six import iteritems
from ..six.moves import range
from .build_manager import SSHBuildManager, BatchBuildManager
from .builder import Builder


# Std.ShellScript.utils
def parse_range(value, N=None):
  if not value:
    return []
  re_scope = re.compile(r'^((-?[0-9]+)\-(-?[0-9]+))(:(-?[0-9]+))?$')
  re_number = re.compile(r'^-?[0-9]+$')
  lst = []
  for item in value.split(','):
    number = re_number.match(item.strip())
    scope = re_scope.match(item.strip())
    if scope:
      lb = int(scope.group(2))
      ub = int(scope.group(3))
      if N and lb < 0: # process negative indices
        lb += N
      if N and ub < 0:
        ub += N
      step = scope.group(5) or 1
      lst.extend(range(lb, ub + 1, int(step)))
    elif number:
      n = int(number.group(0))
      if N and n < 0:
        n += N
      lst.append(n)
    else:
      raise ValueError('Wrong value: cannot parse %s' % item)
  return sorted(set(lst))


class Params(object):
  def __init__(self):
    self.input_file = None
    self.x_input_file = None
    self.y_input_file = None
    self.x_indices = None
    self.y_indices = None
    self.delimiter = ','
    self.skip_header = 0

    self.options = {"GTApprox/Technique": "MoA"}

    self.config = None
    self.workdir = None
    self.output_file = 'model.gtapprox'

    self.ssh_hostname = None
    self.ssh_username = None
    self.ssh_password = None
    self.ssh_keyfile = None

    self.environment = {}

    self.cluster = None
    self.cluster_queue = None
    self.cluster_job_name = None
    self.cluster_exclusive = None
    self.cluster_slot_limit = None
    self.cluster_custom_options = None

    self.omp_num_threads = None

  def __str__(self):
    r = "Training parameters:\n"
    for name in ['input_file', 'x_input_file', 'x_indices', 'y_input_file', 'y_indices', 'delimiter', 'skip_header',
                 'options', 'output_file', 'workdir', 'config',
                 'ssh_hostname', 'ssh_username', 'ssh_password', 'ssh_keyfile', 'environment',
                 'cluster', 'cluster_queue', 'cluster_job_name', 'cluster_exclusive', 'cluster_slot_limit', 'cluster_custom_options',
                 'omp_num_threads']:
      value = getattr(self, name)
      if name == 'delimiter':
        if value:
          value = "'%s'" % value
        else:
          value = 'any consecutive whitespaces'
      if isinstance(value, dict):
        r += '\t%s = {\n' % name
        for k in value:
          r += '\t\t%s = %s\n' % (k, value[k])
        r += '\t\t}\n'
      elif value:
        if name == 'ssh_password':
          value = '*' * len(value)
        r += '\t%s = %s\n' % (name, value or '')
    return r

def report_error(msg, show_usage=False):
  sys.stderr.write(msg)
  if show_usage:
    usage()
  sys.exit(2)


def usage():
  from textwrap import dedent
  print(dedent("""
  Usage: train_gtapprox.py [OPTION(s)]... XY_CSV_FILE
          train_gtapprox.py [OPTION(s)]... X_CSV_FILE Y_CSV_FILE

  Train pSeven Core GTApprox model on data from CSV-file(s)

    -x <indices>                       indices of X columns (in form 1,2,3,5 or 1-3,5)
    -y <indices>                       indices of Y columns (in form 1,2,3,5 or 1-3,5)
    -d <delimiter>                     csv delimiter (',' is default). Use empty value (-d "") to make any consecutive whitespaces act as delimiter
    --skip-header <N>                  the numbers of lines to skip at the beginning of the CSV file(s)

    -o <name>=<value>                  set value of GTApprox option named <name> to <value>
    --omp-num-threads <N>              limit the maximum number of threads (OMP_NUM_THREADS) (only if ssh or cluster is used)

    -e <name>=<value>                  set environment variable named <name> to <value>

    --output-file <filename>           filename trained model will be saved to
    --workdir <dir_name>               working directory (local or remote)

    --ssh-hostname <hostname>          connect to host <hostname> via ssh
    --ssh-username <username>          ssh username
    --ssh-password <password>          ssh password, if password is empty (i.e. --ssh-password= ) it will be requested interactively
    --ssh-keyfile <keyfile>            file containing private key for ssh

    --cluster <type>                   use cluster (the only supported cluster is LSF). If cluster type is not set the model is trained remotely withou using HPC cluster
    --cluster-queue <queue>            cluster destination queue name
    --cluster-job-name <name>          job name
    --cluster-exclusive                use node exclusively by jobs (destination queue must support exclusive jobs)
    --cluster-slot-limit <N>           limit number of simultaneously running jobs to <N>
    --cluster-custom-options <options> custom options to be passed to the resource manager

    --config <filename>                path to config file (JSON) containing some of the mentioned above options (ssh- and cluster-)


  Examples:

      train.py -x1-10 -y11-12 -o GTApprox/Technique=MoA -o GTApprox/LogLevel=Debug data.csv

      train.py --ssh-hostname submit-node --ssh-username user --ssh-password password \\
                --cluster lsf --cluster-exclusive data.csv

      train.py --cluster lsf --cluster-exclusive data.csv

      train.py --config mycluster.json data.csv

  Config example:
      {
          "omp_num_threads": 2,

          "ssh-hostname": "submit-node",
          "ssh-username": "user",
          "ssh-password": "password",

          "environemnt": {"SHELL": "/bin/bash -i", "PYTHONPATH": "~/.local/lib/"},

          "cluster": "lsf",
          "cluster-queue": "normal",
          "cluster-exclusive": True
      }
  """))

def parse_config_options(config=None, options=None):
  if not options:
    options = {}
  config_options = {}
  if config:
    from ..shared import parse_json_deep
    with open(config, "rt") as f:
      config_options = parse_json_deep(f.read(), dict)
  config_options.update(options)

  hostname = username = password = private_key_path = workdir = omp_num_threads = cluster = environment = None
  cluster_options = {}

  for k, v in iteritems(config_options):
    if k == "omp_num_threads":
      omp_num_threads = v
    elif k == "workdir":
      workdir = v
    elif k == "ssh-hostname":
      hostname = v
    elif k == "ssh-username":
      username = v
    elif k == "ssh-password":
      password = v
    elif k == "ssh-keyfile":
      private_key_path = v
    elif k == 'environment':
      environment = v
    elif k == "cluster":
      cluster = v.lower() if v else None
    elif k == "cluster-queue":
      cluster_options['queue'] = v
    elif k == "cluster-job-name":
      cluster_options['job_name'] = v
    elif k == "cluster-exclusive":
      cluster_options['exclusive'] = v
    elif k == "cluster-slot-limit":
      cluster_options['array_slot_limit'] = int(v)
    elif k == "cluster-custom-options":
      cluster_options['custom_options'] = v
    else:
      raise Exception("Unknown option '%s'" % k)

  return hostname, username, password, private_key_path, workdir, omp_num_threads, cluster, cluster_options, environment

def train(params):
  def load_data(filename):
    if not os.path.exists(filename):
      report_error("ERROR: unable to open file '%s'" % (filename))

    print("Loading data from '%s'" % filename)
    data = np.genfromtxt(filename, delimiter=params.delimiter, skip_header=params.skip_header)

    if len(data.shape) != 2:
      report_error("ERROR: '%s' - invalid CSV-file or bad CSV-delimiter" % filename)
    else:
      print("- %d samples, sample size: %d" % (data.shape[0], data.shape[1]))

    return data

  print('')
  if params.input_file:   # single .csv for both X and Y
    data = load_data(params.input_file)
    params.x_indices = parse_range(params.x_indices or '0--2', data.shape[1])
    params.y_indices = parse_range(params.y_indices or '-1', data.shape[1])
  else:                   # separate .csv for X and Y
    data_x = load_data(params.x_input_file)
    data_y = load_data(params.y_input_file)
    params.x_indices = parse_range(params.x_indices or '0--1', data_x.shape[1])
    params.y_indices = parse_range(params.y_indices or '0--1', data_y.shape[1])

  print('')
  print(params)

  if params.input_file:
    x_train = data[:, params.x_indices]
    y_train = data[:, params.y_indices]
  else:
    x_train = data_x[:, params.x_indices]
    y_train = data_y[:, params.y_indices]

  if params.delimiter == " ":
    params.delimiter = None # default for numpy.genfromtxt() - consecutive whitespaces

  if params.input_file:  # ensure X and Y don't intersect
    for i in params.x_indices:
      if i in params.y_indices:
        report_error("ERROR: index %d both in x_indices and y_indices" % i)


  if os.path.exists(params.output_file):
    if not os.access(params.output_file, os.W_OK):
      report_error("ERROR: file '%s' is not writable" % (params.output_file))
  else:
    try:
      with open(params.output_file, 'w+b') as f:
        pass
      try:
        os.remove(params.output_file)
      except:
        pass
    except IOError:
      e = sys.exc_info()[1]
      report_error("ERROR: file '%s' is not writable: %s" % (params.output_file, e))

  hostname, username, password, private_key_path, workdir, omp_num_threads, cluster, cluster_options, environment = parse_config_options(params.config)

  if params.ssh_hostname:
    hostname = params.ssh_hostname
  if params.ssh_username:
    username = params.ssh_username
  if params.ssh_password:
    password = params.ssh_password
  if params.ssh_keyfile:
    private_key_path = params.ssh_keyfile
  if params.workdir:
    workdir = params.workdir
  if params.omp_num_threads:
    omp_num_threads = params.omp_num_threads
  if params.cluster:
    cluster = params.cluster
  if params.cluster_exclusive:
    cluster_options['exclusive'] = True
  if params.cluster_queue:
    cluster_options['queue'] = params.cluster_queue
  if params.cluster_job_name:
    cluster_options['job_name'] = params.cluster_job_name
  if params.cluster_slot_limit:
    cluster_options['array_slot_limit'] = params.cluster_slot_limit
  if params.cluster_custom_options:
    cluster_options['custom_options'] = params.cluster_custom_options
  if params.environment:
    environment = params.environment

  if cluster and cluster != 'lsf':
    raise Exception("Invalid argument value '%s': only supported cluster is lsf" % (cluster))

  use_ssh = bool(hostname)
  use_cluster = bool(cluster)

  builder = Builder()
  bm = None
  if use_ssh and not use_cluster:
    bm = SSHBuildManager(host=hostname, username=username, password=password, private_key_path=private_key_path, workdir=workdir,
                         environment=environment)
  elif use_ssh and use_cluster:
    bm = BatchBuildManager(host=hostname, username=username, password=password, private_key_path=private_key_path, workdir=workdir,
                           cluster_options=cluster_options, environment=environment)
  elif not use_ssh and use_cluster:
    bm = BatchBuildManager(host=None, workdir=workdir, cluster_options=cluster_options, environment=environment)

  if bm:
    try:
      bm.test_connection()
    except Exception:
      e = sys.exc_info()[1]
      report_error('Unable to connect to %s: %s' % (hostname, e))
    if omp_num_threads:
      bm.set_omp_thread_limit(omp_num_threads)
    builder._set_build_manager(bm)

  builder.set_logger(StreamLogger(sys.stdout, LogLevel.INFO))

  print('Building model...\n')
  model = builder.build(x_train, y_train, options=params.options)

  print("\nSaving model to '%s'..." % params.output_file)
  model.save(params.output_file)

  print("\nModel info:\n")
  print(model)

def parse_args_and_train(args):
  try:
    opts, args = getopt.gnu_getopt(args,
                                   'x:y:o:d:e:', ['skip-header=',
                                                 'omp-num-threads=',
                                                 'output-file=',
                                                 'workdir=',
                                                 'ssh-hostname=',
                                                 'ssh-username=',
                                                 'ssh-password=',
                                                 'ssh-keyfile=',
                                                 'cluster=',
                                                 'cluster-queue=',
                                                 'cluster-job-name=',
                                                 'cluster-exclusive',
                                                 'cluster-slot-limit=',
                                                 'cluster-custom-options=',
                                                 'config='])
  except getopt.GetoptError:
    e = sys.exc_info()[1]
    report_error(str(e), True)

  params = Params()

  for o, a in opts:
    if o == "-x":
      params.x_indices = a
    elif o == "-y":
      params.y_indices = a
    elif o == "-d":
      params.delimiter = a
    elif o == "-o":
      values = a.split('=', 1)
      if len(values) < 2:
        raise Exception("Invalid argument value %s='%s': option should be passed in form OptionName=Value" % (o, a))
      opt_name, opt_value = values
      params.options[opt_name] = opt_value
    elif o == "-e":
      values = a.split('=', 1)
      if len(values) < 2:
        raise Exception("Invalid argument value %s='%s': environment variable should be passed in form VariableName=Value" % (o, a))
      var_name, var_value = values
      params.environment[var_name] = var_value
    elif o == "--skip-header":
      params.skip_header = int(a)
    elif o == "--omp-num-threads":
      params.omp_num_threads = int(a)
    elif o == "--output-file":
      params.output_file = a
    elif o == '--workdir':
      params.workdir = a
    elif o == '--ssh-hostname':
      params.ssh_hostname = a
    elif o == '--ssh-username':
      params.ssh_username = a
    elif o == '--ssh-password':
      params.ssh_password = a
    elif o == '--ssh-keyfile':
      params.ssh_keyfile = a
    elif o == '--cluster':
      params.cluster = a.lower() if a else None
    elif o == '--cluster-queue':
      params.cluster_queue = a
    elif o == '--cluster-job-name':
      params.cluster_job_name = a
    elif o == '--cluster-exclusive':
      params.cluster_exclusive = True
    elif o == '--cluster-slot-limit':
      params.cluster_slot_limit = int(a)
    elif o == '--cluster-custom-options':
      params.cluster_custom_options = a
    elif o == '--config':
      params.config = a
    else:
      raise Exception("Unknown option '%s'" % o)

  L = len(args)
  if L < 1:
    report_error("ERROR: argument required", True)
  elif L == 1:
    params.input_file = args[0]
  elif L == 2:
    params.x_input_file = args[0]
    params.y_input_file = args[1]
  else:
    report_error('ERROR: only one or two input file is supported', True)

  if params.ssh_hostname and params.ssh_password == '':
    import getpass
    params.ssh_password = getpass.getpass("\nPlease enter password for remote host '%s':" % params.ssh_hostname)

  train(params)


if __name__ == "__main__":
  parse_args_and_train(sys.argv[1:])
