#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
# cloned ShellScript/batch_manager.py

import re
import sys

from .. import six as _six
from .. import shared as _shared

def _postprocessReadFile(data, pos):
  if data is None or isinstance(data, _six.string_types):
    return data, pos

  try:
    return data.decode('latin1'), pos
  except AttributeError:
    return data, pos


class BatchJobSpecification(object):
  """
  Specification of the batch job that contains parameters required to start a new job

  NOTE: if an instance of BatchJobSpecification has field ``task_id`` - then it is Array Job emulation
  """

  def __init__(self,
               shell=None,
               command=None,
               name=None,
               startTime=None,
               workingDirectory=None,
               array=None,
               array_slot_limit=None,
               stdOutPath=None,
               stdErrPath=None,
               timeLimit=None,
               nodeCount=None,
               cpusPerNode=None,
               nodeConstraints=None,
               destination=None,
               restartable=None,
               exclusive=None,
               customOptions=None):
    """
    Instantiate a new BatchJobSpecification

    @param command: Command to execute on all requested nodes
    @type command: str

    @param name: Name of the job to show in job manager.
    @type name: str

    @param startTime: Start execution of command not earlier than startTime
    @type startTime: datetime

    @param workingDirectory: Working directory where the startup script will be placed and submitted to batch manager. SysOut and SysErr will also go to files inside this directory
    @type workingDirectory: str

    @param array: Array job specification (comma separated ranges eg: 1,2-3,4-10:2)
    @type array: str

    @param array_slot_limit: Maximum amount of jobs that can run concurrently in the job array
    @type array_slot_limit: int

    @param stdOutPath: Put standard output to this file
    @type stdOutPath: str

    @param stdErrPath: Put standard error output to this file
    @type stdErrPath: str

    @param timeLimit: Maximum execution time. Shouldn't be greater than execution time allowed for the destination (cluster, partition or queue)
    @type timeLimit: timedelta

    @param nodeCount: requested number of nodes for the job
    @type nodeCount: int

    @param cpusPerNode: number of processors per node
    @type cpusPerNode: int

    @param nodeConstraints: list of strings that express additional node constraints (depends on particular cluster instance)
    @type nodeConstraints: list

    @param destination: Cluster, partition or queue where the job should be started
    @type destination: str

    @param restartable: If the job may be restarted in case of failure
    @type restartable: bool

    @param exclusive: Exclusive execution mode (jobs runs exclusively on the host)
    @type exclusive: bool

    @param customOptions: Custom (batch manager dependent) options that will be appended to the startup script after common options
    @type customOptions: str
    """

    self.job_id = None
    self.task_list = []
    self.shell = '/bin/sh' if not shell else shell
    self.command = command
    self.name = name
    self.startTime = startTime
    self.workingDirectory = workingDirectory
    self.array = array
    self.array_slot_limit = array_slot_limit
    self.__stdOutPath = stdOutPath
    self.__stdErrPath = stdErrPath
    self.timeLimit = timeLimit
    self.nodeCount = nodeCount
    self.cpusPerNode = cpusPerNode
    self.nodeConstraints = nodeConstraints
    self.destination = destination
    self.restartable = restartable
    self.exclusive = exclusive
    self.customOptions = customOptions

  def _get_stdOutPath(self):
    return self.__stdOutPath or './.stdout'

  def _set_stdOutPath(self, stdOutPath):
    self.__stdOutPath = stdOutPath

  stdOutPath = property(_get_stdOutPath, _set_stdOutPath)

  def _get_stdErrPath(self):
    return self.__stdErrPath or './.stderr'

  def _set_stdErrPath(self, stdErrPath):
    self.__stdErrPath = stdErrPath

  stdErrPath = property(_get_stdErrPath, _set_stdErrPath)


class BatchJobStatus(object):
  """
  Batch manager independent batch job status
  """
  OTHER = 'Other'
  PENDING = 'Pending'
  RUNNING = 'Running'
  FINISHED = 'Finished'
  ERROR = 'Error'

def fix_replacements(value, replacements):
  if value:
    for r in replacements:
      value = value.replace(*r)
  return value

def replace(value, what, to):
  """replace, leaving %what untouched"""
  regExp = re.compile('(?<=[^%])' + re.escape(what))
  return regExp.sub(to.replace('\\', '\\\\'), value)


def getFullPath(workingDirectory, path):
  from . command import Transport
  return Transport.getFullPath(workingDirectory, path)


class BatchManager(object):
  def __init__(self, transport, logger=None):
    self._transport = transport
    self._logger = logger
    from . command import Command
    self.Command = Command

  def dbg(self, message):
    if self._logger:
      self._logger.dbg(message)

  def info(self, message):
    if self._logger:
      self._logger.info(message)

  def warn(self, message):
    if self._logger:
      self._logger.info(message)

  def error(self, message):
    if self._logger:
      self._logger.error(message)

  def fatal(self, message):
    if self._logger:
      self._logger.fatal(message)

  def submit(self, job_spec):
    """
    Submits batch job for execution and return it's ID on success

    @param job_spec: parameters of the new batch job
    @type job_spec: L{BatchJobSpecification}

    @return: ID of the submitted job or None on error
    @rtype: str
    """
    raise NotImplementedError()

  def getStatus(self, job_id, array_summary=False):
    """
    Returns batch job generic status. Generic status is batch manager independent representation.

    @param job_id: id of the batch job
    @type job_id: str

    @param array_summary: if True - return array job summary as additional info (see @return value) if possible
    @type array_summary: bool

    @return: tuple(batch job status, None or additional info to display (str))
    @rtype: L{BatchJobStatus}
    """
    raise NotImplementedError()

  def get_exit_code(self, job_id):
    """
    Returns job(script) exit code if applicable.

    @param job_id: id of submitted job
    @type job_id: int

    @return: exit code
    @rtype: L{int}, L{None}
    """
    return None

  def getOutput(self, job_spec, stdOutPos=0, stdErrPos=0, required=True, merge_array_output=False):
    """
    Returns [stdOut, stdOutPos, srdErr, stdErrPos]
      stdOut - portion of standard output that was appended since last read
      stdOutPos - standard output file length
      stdErr - portion of error output that was appended since last read
      stdErrPos - error output file length
      required - if True requested file absence will cause error

    @param job_spec: parameters of the batch job
    @type job_spec: L{BatchJobSpecification}

    @param stdOutPos: start reading standard output from position stdOutPos
    @type stdOutPos: int

    @param stdErrPos: start reading error output from position stdErrPos
    @type stdErrPos: int

    @return: batch job output pair
    @rtype: str
    """
    try:
      stdout = replace(job_spec.stdOutPath, '%j', str(job_spec.job_id))
      stderr = replace(job_spec.stdErrPath, '%j', str(job_spec.job_id))

      if required:
        # hack: make NFS update file list
        self._transport.executeCommand(self.Command('touch "%s"' % job_spec.workingDirectory))

      # @todo: simplify replace().replace
      if merge_array_output:
        merge_script = "#!/bin/sh\n"
        merge_script += 'merged_stdout=%s\n' % replace(stdout, '%i', '').replace('%%', '%')
        merge_script += 'rm -rf ${merged_stdout}\n'

        reg_exp = re.compile('(?<=[^%])%i')
        if reg_exp.search(stdout):
          fixed_stdout = replace(stdout, '%i', '${TASK_ID}').replace('%%', '%')
          merge_script += 'for TASK_ID in %s ; do\n' % (' '.join(map(str, job_spec.task_list)))
          merge_script += '  cat %s >> ${merged_stdout}\n' % fixed_stdout
          merge_script += '  rm %s\n' % fixed_stdout
          merge_script += 'done\n'

        merge_script += 'merged_stderr=%s\n' % replace(stderr, '%i', '').replace('%%', '%')
        merge_script += 'rm -rf ${merged_stderr}\n'
        if reg_exp.search(stderr):
          fixed_stderr = replace(stderr, '%i', '${TASK_ID}').replace('%%', '%')
          merge_script += 'for TASK_ID in %s ; do\n' % (' '.join(map(str, job_spec.task_list)))
          merge_script += '  cat %s >> ${merged_stderr}\n' % fixed_stderr
          merge_script += '  rm %s\n' % fixed_stderr
          merge_script += 'done\n'

        if reg_exp.search(stdout) or reg_exp.search(stderr):
          scriptFilePath = getFullPath(job_spec.workingDirectory, 'merge_output.sh')
          self._transport.writeFile(scriptFilePath, _six.BytesIO(merge_script.encode("utf8")))
          command = self.Command('cd "' + job_spec.workingDirectory + '" && ./merge_output.sh', {})
          self._transport.executeCommand(command)
          self._transport.deleteFile(scriptFilePath)

          # update stdout/stderr path to make cleanup() work
          job_spec.stdOutPath = replace(stdout, '%i', '').replace('%%', '%')
          job_spec.stdErrPath = replace(stderr, '%i', '').replace('%%', '%')

      stdout = replace(stdout, '%i', '').replace('%%', '%')
      stderr = replace(stderr, '%i', '').replace('%%', '%')

      [out, outPos] = _postprocessReadFile(*self._transport.readFile(getFullPath(job_spec.workingDirectory, stdout), stdOutPos))
      [err, errPos] = _postprocessReadFile(*self._transport.readFile(getFullPath(job_spec.workingDirectory, stderr), stdErrPos))
    except Exception:
      if required:
        _shared.reraise(*sys.exc_info())
      else:
        return [None, 0, None, 0]
    return [out, outPos, err, errPos]

  def cancel(self, job_id):
    """
    Cancel running job on cluster

    @param job_id: batch job identifier returned by the submit method, or list of job identifiers
    @type job_id: str, list
    """
    raise NotImplementedError()

  def cleanup(self, job_spec):
    """
    Remove temporary files create by the submit method (stdout, stderr, etc)

    @param job_spec: parameters of the batch job
    @type job_spec: L{BatchJobSpecification}
    """
    raise NotImplementedError()

class TorqueBatchManager(BatchManager):
  __scriptFileName = 'script.sq'

  JOB_STATE_MAP = {
    'C': BatchJobStatus.FINISHED, # Job is completed after having run
    'E': BatchJobStatus.RUNNING,  # Job is exiting after having run
    'H': BatchJobStatus.PENDING,  # Job is held - this means that it is not going to run until it is released
    'Q': BatchJobStatus.PENDING,  # Job is queued and will run when the resources become available
    'R': BatchJobStatus.RUNNING,  # Job is running
    'T': BatchJobStatus.PENDING,  # Job is being transferred to a new location - this may happen, e.g., if the node the job had been running on crashed
    'W': BatchJobStatus.PENDING,  # Job is waiting its execution time - you can submit jobs to run, e.g., after 5PM
    'S': BatchJobStatus.PENDING   # Job is suspend (Unicos only)
  }

  def __init__(self, transport, logger=None):
    """
    Instantiates L{TorqueBatchManager}

    @param transport: transport to communicate with cluster head
    @type transport: L{Transport}
    """
    super(TorqueBatchManager, self).__init__(transport, logger)

  def submit(self, job_spec):
    scriptFilePath = getFullPath(job_spec.workingDirectory, self.__scriptFileName)
    self._transport.writeFile(scriptFilePath, _six.BytesIO(self._create_startup_script(job_spec).encode("utf8")))
    job_spec.stdOutPath = job_spec.stdOutPath.replace('%', '%%')
    job_spec.stdErrPath = job_spec.stdErrPath.replace('%', '%%')
    if job_spec.array:
      job_spec.stdOutPath += '-%i'
      job_spec.stdErrPath += '-%i'
    job_id = self._start_task(job_spec, self.__scriptFileName)
    return job_id

  def getStatus(self, job_id, array_summary=False):
    args = ''
    if array_summary:
      args = '-t'

    command = self.Command('qstat ' + args + ' ' + job_id)
    commandResult = self._transport.executeCommand(command)

    if commandResult.exitCode == 0:
      return self.__parseQstatOutput(commandResult.stdOut, job_id, array_summary)
    return self.__parseQstatError(commandResult.stdErr), None

  def cancel(self, job_id):
    if isinstance(job_id, list):
      command = self.Command('qdel ' + ' '.join(job_id))
    else:
      command = self.Command('qdel ' + str(job_id))
    self._transport.executeCommand(command)

  def cleanup(self, job_spec):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self.__scriptFileName))

  def __parseQstatOutput(self, out, job_id, array_summary=False):

    lines = [line for line in out.splitlines() if line.strip()]
    if not lines:
      return BatchJobStatus.FINISHED, None

    # skip header
    del lines[0:2]

    # assume job is finished if we will not find it in the output
    status = BatchJobStatus.FINISHED
    status_info = None

    if array_summary:
      job_states = [self.JOB_STATE_MAP.get(line.split()[-2], BatchJobStatus.OTHER) for line in lines]
      run = job_states.count(BatchJobStatus.RUNNING)
      pend = job_states.count(BatchJobStatus.PENDING)

      if run:
        status = BatchJobStatus.RUNNING
      elif pend:
        status = BatchJobStatus.PENDING
      status_info = 'Running %d, Pending %d' % (run, pend)
    else:
      # find job and get status
      for line in lines:
        if line.startswith(job_id): # always true?
          job_state = line.split()[-2]
          status = self.JOB_STATE_MAP.get(job_state, BatchJobStatus.OTHER)
          break

    return status, status_info

  def __parseQstatError(self, err):
    if err.startswith('qstat: Unknown Job Id'):
      return BatchJobStatus.FINISHED
    return BatchJobStatus.OTHER

  def _is_job_array_supported(self):
    return True

  def _start_task(self, job_spec, scriptFileName):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))

    command = self.Command('cd "' + job_spec.workingDirectory + '" && qsub', [scriptFileName])
    commandResult = self._transport.executeCommand(command)
    if commandResult.exitCode == 0 and commandResult.stdOut:
      job_id = commandResult.stdOut.strip()
    else:
      raise Exception("Can't start job: " + commandResult.stdErr)

    return job_id

  def _create_startup_script(self, job_spec):
    script = ''
    # Header
    script += '#!' + job_spec.shell + '\n'
    # Start time
    if job_spec.startTime:
      script += '#PBS -a ' + self._format_start_time(job_spec.startTime) + '\n'
    # Path to save stdout
    if job_spec.stdOutPath:
      script += '#PBS -o ' + job_spec.stdOutPath + '\n'
    # Path to save stderr
    if job_spec.stdErrPath:
      if job_spec.stdErrPath == job_spec.stdOutPath:
        script += '#PBS -j oe \n'
      else:
        script += '#PBS -e ' + job_spec.stdErrPath + '\n'
    # Node count, processors per node and custom constraints
    script += '#PBS -l nodes=' + str(job_spec.nodeCount or 1)
    if job_spec.cpusPerNode:
      script += ':ppn=' + str(job_spec.cpusPerNode)
    if job_spec.nodeConstraints:
      for constraint in job_spec.nodeConstraints:
        script += ':' + constraint
    script += '\n'
    # Job Name
    if job_spec.name:
      script += '#PBS -N ' + job_spec.name + '\n'
    if job_spec.array:
      slot_limit = ''
      if job_spec.array_slot_limit:
        slot_limit = '%%%d' % (job_spec.array_slot_limit)
      script += '#PBS -t ' + job_spec.array + slot_limit + '\n'
    # Target queue
    if job_spec.destination:
      script += '#PBS -q ' + job_spec.destination + '\n'
    # Is job restartable?
    if job_spec.restartable is not None:
      script += '#PBS -r ' + ('y' if job_spec.restartable else 'n') + '\n'
    if job_spec.exclusive:
      script += '#PBS -l naccesspolicy=singlejob\n'
    # Custom options
    if job_spec.customOptions:
      script += '#PBS ' + job_spec.customOptions + '\n'
    script += '\n'
    script += '\n'
    # Working dir
    if job_spec.workingDirectory:
      script += 'cd ' + job_spec.workingDirectory + '\n'
    # Command to execute
    script += (job_spec.command or '') + '\n'
    return script

  def __escape_bash_command(self, command):
    return command.replace('"', '\\"')

  def _format_start_time(self, dt):
    # Datetime format is [[[[CC]YY]MM]DD]hhmm[.SS]
    if dt:
      return dt.strftime('%Y%m%d%H%M.%S')
    return None

class SlurmBatchManager(BatchManager):
  __sbatchOutFile = 'sbatch.out'
  __scriptFileName = 'script.sh'

  JOB_STATE_MAP = {
    'CA': BatchJobStatus.FINISHED, #Job is cancelled
    'CD': BatchJobStatus.FINISHED, #Job is completed
    'CF': BatchJobStatus.PENDING,  #Job is configuring
    'CG': BatchJobStatus.RUNNING,  #Job is completing
    'F':  BatchJobStatus.FINISHED, #Job is failed
    'NF': BatchJobStatus.FINISHED, #Job has failed node
    'PD': BatchJobStatus.PENDING,  #Job is pending
    'PR': BatchJobStatus.FINISHED, #Job is preempted
    'R':  BatchJobStatus.RUNNING,  #Job running
    'S':  BatchJobStatus.PENDING,  #Job suspended
    'TO': BatchJobStatus.FINISHED, #Job timed out
  }

  def __init__(self, transport, logger=None):
    """
    Instantiates L{SlurmBatchManager}

    @param transport: transport to communicate with cluster head
    @type transport: L{Transport}
    """
    super(SlurmBatchManager, self).__init__(transport, logger)
    self._script_files = set()

  def submit(self, job_spec):
    scriptFilePath = getFullPath(job_spec.workingDirectory, self.__scriptFileName)
    if scriptFilePath not in self._script_files:
      self._script_files.add(scriptFilePath)
      self._transport.writeFile(scriptFilePath, _six.BytesIO(self._create_startup_script(job_spec).encode("utf8")))
    job_id = self._start_task(job_spec, self.__scriptFileName)
    return job_id

  def getStatus(self, job_id, array_summary=False):
    command = self.Command('squeue -h -j' + str(job_id) + ' -o "%t"; echo')
    # squeue - show task status
    # -h - do not output header
    # -j - show selected job only
    # -o - output format
    commandResult = self._transport.executeCommand(command)

    if commandResult.exitCode == 0:
      return self.__parseSqueueOutput(commandResult.stdOut), None
    return self.__parseSqueueError(commandResult.stdErr), None

  def getStatuses(self):
    command = self.Command("squeue -h -o '%i %t'; echo")
    commandResult = self._transport.executeCommand(command)

    if commandResult.exitCode == 0:
      lines = [line for line in commandResult.stdOut.split('\n') if line.strip()]
      result = {} # {} means all have finished (no running jobs (left))
      for line in lines:
        job_info = line.strip().split()
        job_id = int(job_info[0])
        result[job_id] = self.JOB_STATE_MAP.get(job_info[1], BatchJobStatus.OTHER)
      return result
    return {}

  def cancel(self, job_id):
    command = self.Command('scancel ' + str(job_id) + '; echo')
    self._transport.executeCommand(command)

  def cleanup(self, job_spec):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self.__sbatchOutFile))
    scriptFilePath = getFullPath(job_spec.workingDirectory, self.__scriptFileName)
    self._transport.deleteFile(scriptFilePath)
    self._script_files.remove(scriptFilePath)

  def __parseSqueueOutput(self, out):
    lines = [line for line in out.splitlines() if line.strip()]
    if not lines:
      return BatchJobStatus.FINISHED

    jobState = lines[0].strip()
    return self.JOB_STATE_MAP.get(jobState, BatchJobStatus.OTHER)

  def __parseSqueueError(self, err):
    if err.startswith('slurm_load_jobs error: Invalid job id specified'):
      return BatchJobStatus.FINISHED
    return BatchJobStatus.OTHER


  def _is_job_array_supported(self):
    command = self.Command('sbatch -a ; echo', {})
    commandResult = self._transport.executeCommand(command)
    if 'invalid option' in commandResult.stdErr:
      return False
    return True

  def _start_task(self, job_spec, scriptFileName):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))
    # Redirect sbatch output to file. Otherwise ssh client may hang in case of wrong queue name (for example). In such
    # case sbatch command produces no text to stdout and ssh client waits until timeout.

    env_cmd = ''
    options = ''
    if hasattr(job_spec, 'task_id'):
      task_id = job_spec.task_id
      env_cmd = 'SLURM_ARRAY_TASK_ID=%s' % task_id

      def apply_replacements(name):
        if job_spec.job_id:
          name = name.replace('%j', '%s' % job_spec.job_id)
        name = name.replace('%i', '%s' % task_id)
        return name
      stdout = apply_replacements(job_spec.stdOutPath)
      stderr = apply_replacements(job_spec.stdErrPath)
      options = '-J %s[%s] -o %s -e %s' % (job_spec.name, task_id, stdout, stderr)

    command = self.Command('cd "' + job_spec.workingDirectory + '" && ' + env_cmd + ' sbatch %s ' % (options) + scriptFileName +  ' > ' + self.__sbatchOutFile + ' 2>&1 ; echo', {})
    self._transport.executeCommand(command)
    [outFileContents, outFilePos] = _postprocessReadFile(*self._transport.readFile(getFullPath(job_spec.workingDirectory, self.__sbatchOutFile), 0))
    if outFileContents is None:
      raise Exception("Can't start job: unable to get sbatch output")
    if outFileContents.startswith('Submitted batch job '):
      numbers = [int(s) for s in outFileContents.split() if s.isdigit()]
      job_id = numbers[0]
    else:
      raise Exception("Can't start job: " + outFileContents)

    return job_id

  def _create_startup_script(self, job_spec):
    script = ''
    # Header
    script += '#!' + job_spec.shell + '\n'
    # Start time
    if job_spec.startTime:
      script += '#SBATCH --begin ' + self._format_start_time(job_spec.startTime) + '\n'
    # Path to save stdout
    if not hasattr(job_spec, 'task_id'):
      if job_spec.stdOutPath:
        stdout_path = job_spec.stdOutPath
        if job_spec.task_list:
          stdout_path = fix_replacements(job_spec.stdOutPath, [('%j', '%A'), ('%i', '%a')])
        script += '#SBATCH -o ' + stdout_path + '\n'
        # Path to save stderr
      if job_spec.stdErrPath and job_spec.stdErrPath != job_spec.stdOutPath:
        stderr_path = job_spec.stdErrPath
        if job_spec.task_list:
          stderr_path = fix_replacements(job_spec.stdErrPath, [('%j', '%A'), ('%i', '%a')])
        script += '#SBATCH -e ' + stderr_path + '\n'
    # Node count, processors per node and custom constraints
    script += '#SBATCH -N ' + str(job_spec.nodeCount or 1) + '\n'
    if job_spec.cpusPerNode:
      script += '#SBATCH -c ' + str(job_spec.cpusPerNode) + '\n'
    if job_spec.nodeConstraints:
      script += '#SBATCH -C '
      first = True
      for constraint in job_spec.nodeConstraints:
        if not first:
          script += ' & '
        script += constraint
      script += '\n'
    # Job Name
    if job_spec.name and not hasattr(job_spec, 'task_id'):
      script += '#SBATCH -J ' + job_spec.name + '\n'
    # Target queue
    if job_spec.destination:
      script += '#SBATCH -p ' + job_spec.destination + '\n'
    # Is job restartable?
    if job_spec.restartable:
      script += '#SBATCH --requeue\n'
    if job_spec.exclusive:
      script += '#SBATCH --exclusive\n'
    # Custom options
    if job_spec.customOptions:
      script += '#SBATCH ' + job_spec.customOptions + '\n'

    if job_spec.array and not hasattr(job_spec, 'task_id'):
      # @todo: support array_slot_limit
      script += '#SBATCH --array ' + job_spec.array + '\n'

    script += '\n'
    script += '\n'

    # Command to execute
    script += (job_spec.command or '') + '\n'
    return script

  def _format_start_time(self, dt):
    # Datetime format is YYYY-MM-DD[THH:MM[:SS]]
    if dt:
      return dt.strftime('%Y-%m-%dT%H:%M:%S')
    return None

class LSFBatchManager(BatchManager):
  __sbatchOutFile = 'sbatch.out'
  __scriptFileName = 'script.sh'

  JOB_STATE_MAP = {
    'PEND':  BatchJobStatus.PENDING,   # the job is pending, that is, it has not yet been started.
    'PSUSP': BatchJobStatus.PENDING,   # the job has been suspended while pending.
    'RUN':   BatchJobStatus.RUNNING,   # the job is currently running
    'USUSP': BatchJobStatus.PENDING,   # the job has been suspended while running.
    'SSUSP': BatchJobStatus.PENDING,   # the job has been suspended by LSF
    'DONE':  BatchJobStatus.FINISHED,  # the job has terminated with status of 0.
    'EXIT':  BatchJobStatus.FINISHED,  # the job has terminated with a non-zero status
    'UNKWN': BatchJobStatus.OTHER,   # the master batch daemon (mbatchd) has lost contact with the slave batch daemon (sbatchd) on the host on which the job runs.
    'ZOMBI': BatchJobStatus.FINISHED,  # the job has became ZOMBI
  }

  def __init__(self, transport, logger=None):
    """
    Instantiates L{LSFBatchManager}

    @param transport: transport to communicate with cluster head
    @type transport: L{Transport}
    """
    super(LSFBatchManager, self).__init__(transport, logger)

  def submit(self, job_spec):
    scriptFilePath = getFullPath(job_spec.workingDirectory, self.__scriptFileName)
    self._transport.writeFile(scriptFilePath, _six.BytesIO(self._create_startup_script(job_spec).encode("utf8")))
    job_id = self._start_task(job_spec, self.__scriptFileName)
    return job_id

  def getStatus(self, job_id, array_summary=False):
    args = ''
    if array_summary:
      args = '-A'

    command = self.Command('bjobs ' + args + ' ' + str(job_id) + '; echo')
    commandResult = self._transport.executeCommand(command)
    if commandResult.exitCode == 0:
      return self._parse_bsub_output(commandResult.stdOut, array_summary)
    return self._parse_bsub_error(commandResult.stdErr), None

  def cancel(self, job_id):
    if isinstance(job_id, list):
      command = self.Command('bkill ' + ' '.join(job_id))
    else:
      command = self.Command('bkill ' + str(job_id) + '; echo')
    self._transport.executeCommand(command)

  def cleanup(self, job_spec):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self.__sbatchOutFile))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self.__scriptFileName))

  def _parse_bsub_output(self, out, array_summary):
    lines = [line for line in out.splitlines() if line.strip()]
    status_info = None
    if not lines:
      batchJobStatus = BatchJobStatus.FINISHED
    else:
      try:
        bjobs_data = lines[1].strip().split()
        if array_summary:
          njobs, pend, done, run, exit_code = map(int, bjobs_data[3:8])
          if done == njobs:
            batchJobStatus = BatchJobStatus.FINISHED
          elif run > 0:
            batchJobStatus = BatchJobStatus.RUNNING
          elif pend > 0:
            batchJobStatus = BatchJobStatus.PENDING
          elif exit_code > 0:
            batchJobStatus = BatchJobStatus.ERROR
          else:
            batchJobStatus = BatchJobStatus.OTHER
          status_info = 'Running %d, Pending %d, Error %d, Done/Total %d/%d' % (run, pend, exit_code, done, njobs)
        else:
          batchJobStatus = self.JOB_STATE_MAP[bjobs_data[2]]
      except:
        self.dbg('Unable to determine job status')
        batchJobStatus = BatchJobStatus.OTHER
    return batchJobStatus, status_info

  def _parse_bsub_error(self, err):
    if re.match(r'Job <\d+> is not found', err):
      return BatchJobStatus.FINISHED
    return BatchJobStatus.OTHER

  def _is_job_array_supported(self):
    return True

  def _start_task(self, job_spec, scriptFileName):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))
    # Redirect sbatch output to file. Otherwise ssh client may hang in case of wrong queue name (for example). In such
    # case sbatch command produces no text to stdout and ssh client waits until timeout.
    command = self.Command('cd "' + job_spec.workingDirectory + '" && bsub < ' + scriptFileName + ' > ' + self.__sbatchOutFile + ' 2>&1 ; echo', {})
    self._transport.executeCommand(command)
    [outFileContents, outFilePos] = _postprocessReadFile(*self._transport.readFile(getFullPath(job_spec.workingDirectory, self.__sbatchOutFile), 0))
    if outFileContents is None:
      raise Exception("Can't start job: unable to get bsub output")
    m = re.match(r'Job <(\d+)> is submitted', outFileContents)
    if m:
      job_id = m.groups()[0]
      self.dbg(outFileContents)
    else:
      raise Exception("Can't start job: " + outFileContents)

    return job_id

  def _create_startup_script(self, job_spec):
    script = ''
    # Header
    script += '#!' + job_spec.shell + '\n'
    # Start time
    if job_spec.startTime:
      script += '#BSUB -b ' + self._format_start_time(job_spec.startTime) + '\n'
    # Path to save stdout
    if job_spec.stdOutPath:
      script += '#BSUB -o ' + fix_replacements(job_spec.stdOutPath, [('%j', '%J'), ('%i', '%I')]) + '\n'
      # Path to save stderr
    if job_spec.stdErrPath:
      if job_spec.stdErrPath != job_spec.stdOutPath:
        script += '#BSUB -e ' + fix_replacements(job_spec.stdErrPath, [('%j', '%J'), ('%i', '%I')]) + '\n'
    # Node count, processors per node and custom constraints
    # @todo: node per job is not supported?
    #script += '#BSUB -n ' + str(job_spec.nodeCount or 1) + '\n'
    if job_spec.cpusPerNode:
      script += '#BSUB -n ' + str(job_spec.cpusPerNode) + '\n'
    if job_spec.nodeConstraints:
      for constraint in job_spec.nodeConstraints:
        script += '#BSUB -R ' + constraint + "\n"

    # Job Name + array
    if job_spec.array:
      slot_limit = ''
      if job_spec.array_slot_limit:
        slot_limit = '%%%d' % (job_spec.array_slot_limit)
      script += '#BSUB -J %s[%s]%s\n' % (job_spec.name or 'unnamed', job_spec.array, slot_limit)
    elif job_spec.name:
      script += '#BSUB -J %s\n' % (job_spec.name)

    # Target queue
    if job_spec.destination:
      script += '#BSUB -q ' + job_spec.destination + '\n'
    # Is job restartable?
    if job_spec.restartable:
      script += '#BSUB -r\n'
    if job_spec.exclusive:
      script += '#BSUB -x\n'
    # Custom options
    if job_spec.customOptions:
      script += '#BSUB ' + job_spec.customOptions + '\n'
    script += '\n'
    script += '\n'

    # Command to execute
    script += (job_spec.command or '') + '\n'

    return script

  def _format_start_time(self, dt):
    # Datetime format is [[year:][month:]day:]hour:minute
    if dt:
      return dt.strftime('%Y:%m:%dT:%H:%M')
    return None

class SSHBatchManager(BatchManager):
  """Run background job via ssh (no resource management)"""

  _exitcode_file = '.script_exitcode'   # contains exit code of user script
  _script = '.script.sh'          # user script
  _script_wrapper = '.script_wrapper.sh'  # wraps _script to get its return code
  _script_runner = '.script_runner.sh'  # runs _script_wrapper in background

  JOB_STATE_MAP = {
    'D': BatchJobStatus.PENDING,   #  uninterruptible sleep (usually IO)
    'R': BatchJobStatus.RUNNING,   #  running or runnable (on run queue)
    'S': BatchJobStatus.RUNNING,   #  interruptible sleep (waiting for an event to complete)
    'T': BatchJobStatus.PENDING,   #  stopped, either by a job control signal or because it is being traced.
    'W': BatchJobStatus.PENDING,   #  paging (not valid since the 2.6.xx kernel)
    'X': BatchJobStatus.FINISHED,  #  dead (should never be seen)
    'Z': BatchJobStatus.FINISHED,  #  defunct ("zombie") process, terminated but not reaped by its parent.
  }

  def __init__(self, transport, logger=None):
    """
    Instantiates L{SSHBatchManager}

    @param transport: transport to communicate with remote host
    @type transport: L{Transport}
    """
    super(SSHBatchManager, self).__init__(transport, logger)
    self._exitcode_files = {} # mapping job_id => exitcode_path for the job

  def submit(self, job_spec):
    scriptFilePath = getFullPath(job_spec.workingDirectory, self._script)
    self._transport.writeFile(scriptFilePath, _six.BytesIO(self._create_startup_script(job_spec).encode("utf8")))
    scriptRunnerFilePath = getFullPath(job_spec.workingDirectory, self._script_runner)
    self._transport.writeFile(scriptRunnerFilePath, _six.BytesIO(self._create_script_runner(job_spec).encode("utf8")))
    scriptWrapperFilePath = getFullPath(job_spec.workingDirectory, self._script_wrapper)
    self._transport.writeFile(scriptWrapperFilePath, _six.BytesIO(self._create_script_wrapper(job_spec).encode("utf8")))
    job_id = self._start_task(job_spec, self._script_runner)
    self._exitcode_files[job_id] = getFullPath(job_spec.workingDirectory, self._exitcode_file)
    return job_id

  def getStatus(self, job_id, array_summary=False):
    command = self.Command('ps -o state -p ' + str(job_id))
    commandResult = self._transport.executeCommand(command)
    if commandResult.exitCode == 0:
      batchJobStatus = self._parse_ps_output(commandResult.stdOut)
      return batchJobStatus, None
    return BatchJobStatus.FINISHED, None

  def get_exit_code(self, job_id):
    try:
      [exitcode, _] = self._transport.readFile(self._exitcode_files[job_id])
      del self._exitcode_files[job_id]
      exitcode = int(exitcode)
    except ValueError:
      exitcode = None
    return exitcode

  def cancel(self, job_id):
    # kill all child processes, after that parent process (wrapper script) will finish by itself
    command = self.Command('ps -opid= --ppid=%d | xargs kill' % job_id)
    self._transport.executeCommand(command)

  def cleanup(self, job_spec):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self._script))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self._script_runner))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self._exitcode_file))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, self._script_wrapper))

  def _parse_ps_output(self, out):
    lines = [line for line in out.split('\n') if line.strip()]
    if not lines or len(lines) < 2:
      return BatchJobStatus.FINISHED
    try:
      jobState = lines[1].strip()
      batchJobStatus = self.JOB_STATE_MAP[jobState]
    except:
      self.dbg('Unable to determine job status')
      batchJobStatus = BatchJobStatus.OTHER
    return batchJobStatus

  def _is_job_array_supported(self):
    return False

  def _start_task(self, job_spec, scriptFileName):
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdOutPath))
    self._transport.deleteFile(getFullPath(job_spec.workingDirectory, job_spec.stdErrPath))
    command = self.Command('cd "' + job_spec.workingDirectory + '" && ./' + scriptFileName, {})
    result = self._transport.executeCommand(command)
    try:
      job_id = int(result.stdOut.strip())
    except ValueError:
      ex, tb = sys.exc_info()[1:]
      _shared.reraise(Exception, Exception('Unable to start job: %s' % result.stdErr.strip()), tb)
    return job_id

  def _create_startup_script(self, job_spec):
    script = '#!' + job_spec.shell + '\n'
    script += (job_spec.command or '') + '\n'
    return script

  def _create_script_wrapper(self, job_spec):
    script = '#!/bin/sh\n'
    script += 'rm -f ' + self._exitcode_file + '\n'
    script += 'chmod a+x ' + self._script + '\n'
    script += './' + self._script + '\n'
    script += 'echo $? > ' + self._exitcode_file + '\n'
    return script

  def _create_script_runner(self, job_spec):
    script = '#!/bin/sh\n'
    script += 'nohup ./' + self._script_wrapper + ' > ' + job_spec.stdOutPath + ' 2> ' + job_spec.stdErrPath + ' </dev/null &\n'
    script += 'echo $!\n'
    return script
