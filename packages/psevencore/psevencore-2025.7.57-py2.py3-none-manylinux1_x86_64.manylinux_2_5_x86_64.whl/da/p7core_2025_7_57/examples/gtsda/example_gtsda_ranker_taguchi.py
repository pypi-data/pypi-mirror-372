#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

from da.p7core import gtsda
import numpy as np

def main():
  """
  Example of Taguchi indices computation with GTSDA Ranker.
  """

  # define sample
  x = np.array([[100, 2, 4, 0.1],
                [100, 5, 6, 0.2],
                [100, 8, 8, 0.3],
                [150, 2, 6, 0.3],
                [150, 5, 8, 0.1],
                [150, 8, 4, 0.2],
                [200, 2, 8, 0.2],
                [200, 5, 4, 0.3],
                [200, 8, 6, 0.1]])
  y = np.array([[87.3, 82.3, 70.7],
                [74.8, 70.7, 63.2],
                [56.5, 54.0, 45.7],
                [79.8, 78.2, 62.3],
                [77.3, 76.5, 54.0],
                [89.0, 87.3, 83.2],
                [64.8, 62.3, 55.7],
                [99.0, 93.2, 87.3],
                [75.7, 74.0, 63.2]])
  x = np.tile(x, (3, 1))
  y = y.reshape(27, 1, order='F')

  # set options
  options = {"GTSDA/Ranker/Technique": "Taguchi",
             "GTSDA/Ranker/Taguchi/Method": "signal_to_noise"}

  # rank
  ranker = gtsda.Analyzer()
  result = ranker.rank(x=x, y=y, options=options)

  # print result
  print(str(result.scores))

if __name__ == "__main__":
  main()
