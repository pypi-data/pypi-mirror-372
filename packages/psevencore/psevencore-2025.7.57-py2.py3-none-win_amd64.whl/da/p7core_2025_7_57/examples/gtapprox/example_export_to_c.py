#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Export to C: example of usage and comparison of evaluation speed
'''
#[0] required imports
from __future__ import with_statement

from math import pi
from os import access, getcwd, mkdir, path, F_OK, P_WAIT
from sys import platform, stdout
from time import time

import ctypes
import numpy as np
import subprocess

from da.p7core import gtapprox, gtdoe
from da.p7core.loggers import LogLevel, StreamLogger
#[0]

#[plat]
if platform == 'win32':
  _library_ext = '.dll'
else:
  _library_ext = '.so'
#[plat]

#[1] x sample generator
def full_factorial(a, b, levels, dim):
  '''
  Generate multidimensional full factorial DoE using Generic Tool for Design of Experiment.
  '''
  generator = gtdoe.Generator()
  result = generator.generate(count=levels**dim,
                              bounds=(np.tile(a, (1, dim))[0],np.tile(b, (1, dim))[0]),
                              options={'GTDoE/Technique': 'FullFactorial'})
  return np.array(result.points)
#[1]

#[2] true function for f sample generation
def data_generator(points):
  '''
  Calculate normalized Michalewicz function on given sample.
  '''
  points = points * pi
  values = np.zeros((points.shape[0],1))[:, 0]
  for i in range(points.shape[1]):
    values = values + np.sin(points[:, i]) * np.sin(points[:, i]**2 / pi)
  return values
#[2]

#[3] compare two vectors
def calculate_errors(value1, value2):
  residuals = np.zeros((len(value1), 1))
  for i in range(len(value1)):
    residuals[i] = np.abs(value1[i] - value2[i])
  rms_error = np.mean(residuals**2)**0.5
  return rms_error
#[3]

#[4]
def main(main_directory = getcwd()):
  x_dim = 5
  y_dim = 1
  factor_size = 15
  test_sample_size = 50000
#[4]

#[5]
  results_location = path.join(main_directory, 'results')
  if access(results_location, F_OK):
    print('The results directory already exists. Will overwrite all saved files!\n')
  else:
    mkdir(results_location)
#[5]

#[6]
  print('Generating full-factorial training sample... \n')
  train_points = full_factorial(0, 1, factor_size, x_dim)
  train_values = data_generator(train_points)

  print('Generating random test sample... \n')
  test_points = np.random.rand(test_sample_size, x_dim)
  test_values = data_generator(test_points)
#[6]

#[7] create builder
  builder = gtapprox.Builder()
  log = StreamLogger(stdout, LogLevel.DEBUG)
  builder.set_logger(log)
  options = {
    'GTApprox/LogLevel': 'ERROR',
    'GTApprox/EnableTensorFeature': 'on',
  }
  builder.options.set(options)
#[7]

#[8]
  print('Training the model (may take a few minutes)...')
  start_time = time()
  model = builder.build(train_points, train_values)
  print(' - training took %s seconds' % str(time() - start_time))
#[8]
#[8a]
  #smoothing_factor = 0.1 # any value in [0, 1]
  #model = model.smooth(smoothing_factor)
#[8a]

#[9]
  print(' - calculating prediction...\n')
  start_time = time()
  test_values_prediction = model.calc(test_points)
  eval_time_python = (time() - start_time) / test_sample_size * 1e6
#[9]

#[10] standalone mode
  print('Exporting and compiling the standalone model...')
  start_time = time()
  model.export_to(gtapprox.ExportedFormat.C99_PROGRAM, 'model_standalone', 'Example: how to export gtapprox model to C. Standalone version', path.join(results_location, 'model_standalone.c'))
  subprocess.check_call(['gcc', '-std=c99', '-O2', '-o', path.join(results_location, 'model_standalone'), path.join(results_location, 'model_standalone.c'), '-lm'])
  print(' - export took %s seconds' % str(time() - start_time))
#[10]

#[11]
  points_as_str = '\n'.join([','.join([repr(point_Comp) for point_Comp in point]) for point in test_points])
  with open(path.join(results_location, 'test_points.csv'), 'w') as f:
    f.write(points_as_str)
#[11]

#[12]
  print(' - calculating prediction...\n')
  start_time = time()
  standalone_parameters = [path.join(results_location, 'model_standalone'), path.join(results_location, 'test_points.csv')]
  if hasattr(subprocess, 'check_output'):
    all_predictions_standalone = subprocess.check_output(standalone_parameters, cwd=results_location)
  else:
    # The subprocess.check_output() hasn't been implemented yet
    standalone_process = subprocess.Popen(standalone_parameters, stdout=subprocess.PIPE, cwd=results_location)
    all_predictions_standalone, standalone_process_err = standalone_process.communicate()
    standalone_process_retcode = standalone_process.poll()
    if standalone_process_retcode:
      raise subprocess.CalledProcessError(standalone_process_retcode, standalone_parameters, output=all_predictions_standalone)

  try:
    # Required to keep Python 2/3 compatibility
    all_predictions_standalone = str(all_predictions_standalone.decode('latin1'))
  except:
    pass

  all_predictions_standalone = all_predictions_standalone.split('\n')

#[12]

#[12a]
  test_values_prediction_standalone = []
  for j in range(test_sample_size):
    test_values_prediction_standalone.append(float(all_predictions_standalone[j].split(', ')[0]))
  eval_time_standalone = (time() - start_time) / test_sample_size * 1e6
#[12a]

#[13] shared library mode
  print('Exporting and compiling the shared model...')
  start_time = time()
  model.export_to(gtapprox.ExportedFormat.C99_SOURCE, 'model_shared', 'Example: how to export gtapprox model to C. Shared library version', path.join(results_location, 'model_shared.c'))
  # On Win64 platform GCC can generate 64-bit shared library although it is called from the 32-bit Python and vice versa.
  # So we should explicitly set 32-bit or 64-bit environment for GCC.
  gcc_env = {4: ['-m32'], 8: ['-m64']}.get(ctypes.sizeof(ctypes.c_void_p), [])
  subprocess.check_call(['gcc', '-std=c99', '-O2', '-shared', '-fPIC'] + gcc_env + ['-o', path.join(results_location, 'model_shared') + _library_ext, path.join(results_location, 'model_shared.c')])
#[13]

#[14]
  library = ctypes.CDLL(path.join(results_location, 'model_shared') + _library_ext)
  model_shared = ctypes.CFUNCTYPE(ctypes.c_int,
                          ctypes.c_int,
                          ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                          ctypes.POINTER(ctypes.c_double), ctypes.c_int)
  print(' - export %s took seconds' % str(time() - start_time))
#[14]

#[15]
  sample = (ctypes.c_double * (test_sample_size * x_dim))()
  for i in range(test_sample_size):
    for j in range(x_dim):
      sample[i * x_dim + j] = test_points[i][j]
#[15]

#[16]
  print(' - calculating prediction...\n')
  all_predictions_shared = (ctypes.c_double * (test_sample_size * (y_dim + x_dim * y_dim)))()
  start_time = time()
  model_shared(("model_shared", library))(ctypes.c_int(test_sample_size), sample, ctypes.c_int(x_dim), all_predictions_shared, ctypes.c_int(y_dim + x_dim * y_dim))
  eval_time_shared = (time() - start_time) / test_sample_size * 1e6
#[16]

#[17]
  test_values_prediction_shared = []
  for j in range(test_sample_size):
    for i in range(y_dim):
      test_values_prediction_shared.append(float(all_predictions_shared[j * (y_dim + x_dim * y_dim) + i]))
#[17]

#[18]
  print('Evaluation time:')
  print(' - Python model        : %s microseconds per point' % str(eval_time_python))
  print(' - C, standalone model : %s microseconds per point' % str(eval_time_standalone))
  print(' - C, shared model     : %s microseconds per point\n' % str(eval_time_shared))
#[18]

#[19]
  print('RMS error on the test sample:')
  print( ' - Python model        : %s' % str(calculate_errors(test_values, test_values_prediction)))
  print( ' - C, standalone model : %s' % str(calculate_errors(test_values, test_values_prediction_standalone)))
  print( ' - C, shared model     : %s\n' % str(calculate_errors(test_values, test_values_prediction_shared)))
#[19]

#[20]
  print('RMS difference between Python model and standalone C model: \n \t%s' % str(calculate_errors(test_values_prediction, test_values_prediction_standalone)))
  print('RMS difference between Python model and shared library model: \n \t%s\n' % str(calculate_errors(test_values_prediction, test_values_prediction_shared)))
#[20]

#[21]
if __name__ == "__main__":
  main()
#[21]
