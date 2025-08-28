#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

from da.p7core import gtsda
import numpy as np

def main():
  """
  Example of Sobol indices computation with GTSDA Ranker.
  """
  # prepare data
  number_points = 2000
  input_dimension = 4
  np.random.seed(100)
  # input part of sample
  x = np.random.rand(number_points, input_dimension) * 2 - 1
  # output part of sample
  y = x[:, 0]**2 + 2 * x[:, 0] * x[:, 1] + x[:, 2]**2

  # doing analysis...
  analyzer = gtsda.Analyzer()
  rank_result = analyzer.rank(x=x, y=y, options={'GTSDA/Ranker/Technique': 'sobol'})

  # and reading results...
  total_indices = rank_result.info['Ranker']['Detailed info']['Total indices']
  main_indices = rank_result.info['Ranker']['Detailed info']['Main indices']
  interact_indices = rank_result.info['Ranker']['Detailed info']['Interaction indices']

  print("Total indices: %s" % total_indices)
  print("Main indices: %s" % main_indices)
  print("Intearaction indices: %s" % interact_indices)

if __name__ == "__main__":
  main()
