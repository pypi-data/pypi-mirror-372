#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Example on how to control RAM used by GTApprox when building the model on big sample."""

#[0] required imports
import sys
import traceback
import numpy as np

from da.p7core import gtapprox
from da.p7core.loggers import StreamLogger

#[0] imports end

#[1] function to be approximated
def function(X):
  Y = np.sum(X**2, axis=1) + 1
  return Y[:, np.newaxis]
#[1]

#[2] function tries to build the model on given subsample of train data (subset is specified by two offsets)
def build_attempt(x, y, offsets, initial_model=None, max_allowed_memory=0):

  if len(y.shape) == 1:
      y = y[:, np.newaxis]

  try:
    # function tries to build (or if initial_model is not None to update) the model
    builder = gtapprox.Builder()
    builder.set_logger(StreamLogger())

    model = builder.build(x[offsets[0]:offsets[1], :], y[offsets[0]:offsets[1], :],
                                     options={'GTApprox/Technique': 'GBRT',
                                              'GTApprox/MaxExpectedMemory': max_allowed_memory})

    # if no exception was raised function checks if memory overflow occurred
    if ('/GTApprox/MemoryOverflowDetected' in model.info['ModelInfo']['Builder']['Details'])\
      and (model.info['ModelInfo']['Builder']['Details']['/GTApprox/MemoryOverflowDetected']):
      status = False
    else:
      status = True

    # note that even if memory overflow occurred model could still be updated to some extent
    # so in such case we always return modified model object

  except Exception:
    # here function processes the exception if any occurred
    traceback.print_exception(*sys.exc_info())
    model = initial_model # if exception occurred initial_model returns unchanged
    status = False

  return model, status  # status True means that build was successful
#[2]

#[3] function does model building process with memory limit control
def build_with_memory_control(x, y, max_allowed_memory, sample_split_coefficient=1.6):

  print('\nModel building process started...\n')

  number_of_parts = 1  # at first no splitting is done
  unprocessed_offset = 0  # current offset of processed points
  number_of_points = x.shape[0]
  model = None  # no initial model is initialized

  while unprocessed_offset < number_of_points:  # training continues until all data is processed
    # this line gets number of points that would be used in the next training attempt
    number_to_process = round((number_of_points - unprocessed_offset)/float(number_of_parts))

    processing_end_offset = int(np.min((unprocessed_offset + number_to_process, number_of_points)))

    offsets = (unprocessed_offset, processing_end_offset)

    # this function runs the building attempt
    model, status = build_attempt(x, y, offsets, initial_model=model, max_allowed_memory=max_allowed_memory)

    # here function processes building attempt outcome
    if status:
      # building succeeded
      number_of_parts -= 1
      unprocessed_offset = processing_end_offset
      print('')
      print('Updated model for %dpoints.' % int(number_to_process))
      print('%d unprocessed points remain.' % int((number_of_points - unprocessed_offset)))
      print('Unprocessed data is split in %d parts now.' % int(number_of_parts))
      print('')
    else:
      # building failed, we split data more
      number_of_parts = round(sample_split_coefficient * number_of_parts)
      print('')
      print('Failed to build model for %d points.' % int(number_to_process))
      print('%d unprocessed points remain.' % int((number_of_points - unprocessed_offset)))
      print('Unprocessed data is split in %d parts now.' % int(number_of_parts))
      print('')

  return model
#[3]

#[4] main workflow
def main():

  #[4-1] read train data
  print("Generate training data")
  train_sample_size = 1000000
  dim = 128
  x_sample = -1 + 2 * np.random.rand(train_sample_size, dim)
  y_sample = function(x_sample)
  #[4-1]

  #[4-2] set_maximum allowed memory to be used
  try:
    import psutil
    all_free_memory = psutil.virtual_memory().available/1024./1024./1024. # in Gbs
    print('%s Gb is free.' % all_free_memory)
    # we allow builder to use up to 10% of all memory
    max_allowed_memory = np.max((round(0.1 * all_free_memory), 1))
  except:
    # if psutil is not installed or other error occurred we just set limit to 1 Gb
    max_allowed_memory = 1

  print('%s Gb may be used to construct model.' % max_allowed_memory)
  #[4-2]

  #[4-3] building and saving the model
  model = build_with_memory_control(x_sample, y_sample, max_allowed_memory=max_allowed_memory)
  model.save('model.gtapprox')
  #[4-3]

#[4]

if __name__ == "__main__":
  main()
