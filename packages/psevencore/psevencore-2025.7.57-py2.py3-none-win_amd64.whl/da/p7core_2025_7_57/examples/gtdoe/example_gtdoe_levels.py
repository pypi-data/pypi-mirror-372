#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


"""
Example of GTDoE usage with levels.
"""

from da.p7core import gtdoe

def main():
  print('\nExample of DoE with levels:\n')
  print('=' * 60)

  generator = gtdoe.Generator()

  # factors 0 and 2 are leveled
  levels = [0, [0.3, 1.1, 2.4, 2.8], 2, [1.2, 1.6, 2.9]]

  # set design space bounds
  # note that despite the two factors above are leveled,
  # we still need to specify bounds for all factors since it is
  # the only way to set the design space dimension
  lower = [0, 0, 0, 0, 0]
  upper = [3, 3, 3, 3, 3]

  # set options
  options = {
    'GTDoE/Technique': 'LHS',
    'GTDoE/CategoricalVariables': levels  # specifies factor levels
  }
  generator.options.set(options)

  # get result
  result = generator.generate(bounds=(lower, upper), count=50)

  # show result
  points = result.points
  number = len(points) # may be less than initial
  toShow = min(number // 10, 10)
  print('\nResults:')
  print('-' * 60)
  maxlen = 0
  for i, s in enumerate(points[:toShow]):
    s = [round(value, 4) for value in s]
    p = '[%3d]: %s' % ((i + 1), s)
    maxlen = max(len(p), maxlen)
    print(str(p))
  print('      %s' % ('.' * (maxlen - 7)))
  for i, s in enumerate(points[-toShow:]):
    s = [round(value, 4) for value in s]
    print('[%3d]: %s' % ((number - toShow + i + 1), s))
  print('Info:')
  print(str(result))

if __name__ == "__main__":
  main()
