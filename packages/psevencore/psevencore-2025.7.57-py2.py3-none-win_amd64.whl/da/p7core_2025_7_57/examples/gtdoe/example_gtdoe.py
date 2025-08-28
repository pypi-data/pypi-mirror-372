#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


from da.p7core import gtdoe
from da.p7core.loggers import StreamLogger

import random

def batch():
  """Example of GTDoE usage."""
  print('\nPython batch DoE example:')
  print('=' * 60)
  # prepare data
  number = 50
  iDim = 3
  random.seed(100)
  lb = [random.uniform(0, 1) for _ in range(iDim)]
  ub = [2 + random.uniform(0, 1) for _ in range(iDim)]

  # create generator
  generator = gtdoe.Generator()
  # set logger
  generator.set_logger(StreamLogger())

  # set options
  options = {
    'GTDoE/Technique': 'OLHS',
    'GTDoE/Deterministic': 'yes',
    'GTDoE/LogLevel': 'Debug'
  }
  generator.options.set(options)

  # get result
  result = generator.generate(bounds=(lb, ub), count=number)

  # result if finite point generator, can get all points
  points = result.points
  number = len(points) # may be less than initial
  toShow = min(number // 10, 10)
  print('\nResults:')
  print('-' * 60)
  maxlen = 0
  for i, s in enumerate(points[:toShow]):
    p = '[%3d]: %s' % ((i + 1), s)
    maxlen = max(len(p), maxlen)
    print(str(p))
  print('      %s' % ('.' * (maxlen - 7)))
  for i, s in enumerate(points[-toShow:]):
    print('[%3d]: %s' % ((number - toShow + i + 1), s))
  print('Info:')
  print(str(result))
  print('-' * 60)

  print('    PhiP metric for generated set: %s' % gtdoe.measures.phi_p((lb, ub), points))
  print('      Potential for generated set: %s' % gtdoe.measures.potential((lb, ub), points))
  print(' Minimax metric for generated set: %s' % gtdoe.measures.minimax_distance((lb, ub), points))
  print('-' * 60)

def sequential():
  """Example of GTDoE usage."""
  print('\nPython sequential DoE example:')
  print('=' * 60)
  number = 50
  iDim = 3
  generator = gtdoe.Generator()
  generator.set_logger(StreamLogger())

  random.seed(100)
  lb = [random.uniform(0, 1) for _ in range(iDim)]
  ub = [2 + random.uniform(0, 1) for _ in range(iDim)]

  result = generator.generate(bounds=(lb, ub))
  # result is infinite points generator
  # take first 50 points
  points = result.take(number)
  toShow = min(number // 10, 10)
  print('\nResults:')
  print('-' * 60)
  maxlen = 0
  for i, s in enumerate(points[:toShow]):
    p = '[%3d]: %s' % ((i + 1), s)
    maxlen = max(len(p), maxlen)
    print(str(p))
  print('      %s' % ('.' * (maxlen - 7)))
  for i, s in enumerate(points[-toShow:]):
    print('[%3d]: %s' % ((number - toShow + i + 1), s))
  print('Info:')
  print(str(result))
  print('-' * 60)

  print('    PhiP metric for generated set: %s' % gtdoe.measures.phi_p((lb, ub), points))
  print('      Potential for generated set: %s' % gtdoe.measures.potential((lb, ub), points))
  print(' Minimax metric for generated set: %s' % gtdoe.measures.minimax_distance((lb, ub), points))
  print('-' * 60)

if __name__ == "__main__":
  batch()
  sequential()

  # oneliner
  for k in gtdoe.Generator().generate(count=10, bounds=([0,0], [10,100]), options={'GTDOE/LogLevel': 'Debug'}):
    print(['%05.2f' % i for i in k])
