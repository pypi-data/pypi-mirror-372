#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


"""
Example of Full Factorial GTDoE with multidimensional factors.
"""

import itertools
import numpy as np
from da.p7core import gtdoe

def main():
  generator = gtdoe.Generator()
  factors_doe = []
  # factor 1 (2-dimensional, with SobolSeq DoE)
  doe_result = generator.generate(count=3, bounds=([0, 0], [1, 1]),
                                  options={'GTDoE/Technique': 'SobolSeq'})
  factors_doe.append(doe_result.points)
  # factor 2 (2-dimensional, with LHS DoE)
  doe_result = generator.generate(count=2, bounds=([0, 0], [1, 1]),
                                  options={'GTDoE/Technique': 'LHS'})
  factors_doe.append(doe_result.points)
  # factor 3 (1-dimensional, just two points)
  doe = np.array([0, 1])[:, np.newaxis]
  # newaxis is used since it's important to have two-dimensional array
  factors_doe.append(doe)

  for (count, factor_doe) in enumerate(factors_doe):
    print('Factor %i' % count)
    print(str(factor_doe))
    print('')

  try:
    # calculate Cartesian product using itertools.product
    ta_doe = np.array([np.hstack(x_i) for x_i in itertools.product(*factors_doe)])
  except AttributeError:
    # manual Cartesian product
    ta_doe = factors_doe[-1]
    for factor_data in factors_doe[-2::-1]:
      ta_doe = np.hstack((np.repeat(factor_data, ta_doe.shape[0], axis=0), \
                              np.tile(ta_doe, (factor_data.shape[0], 1))))

  print('Generated Full Factorial DoE with multidimensional factors')
  print(ta_doe)

if __name__ == "__main__":
  main()
