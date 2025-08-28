#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

from da.p7core import gtsda
import numpy as np

def main():
  """
  Example of screening indices computation with GTSDA Ranker.
  """
  # prepare data
  number_points = 100
  input_dimension = 4
  np.random.seed(100)
  # input part of sample
  x = np.random.rand(number_points, input_dimension) * 2 - 1
  # output part of sample
  y = x[:, 0] + 2 * x[:, 1] + x[:, 2]**2 + x[:, 3]**3

  # doing analysis...
  analyzer = gtsda.Analyzer()
  rank_result = analyzer.rank(x=x, y=y, options={'GTSDA/Ranker/Technique': 'screening'})
  # or just rank_result = analyzer.rank(x=x, y=y) as 'screening' is the default index type

  # and reading results...
  mu_star = rank_result.info['Ranker']['Detailed info']['mu_star']
  mu = rank_result.info['Ranker']['Detailed info']['mu']
  sigma = rank_result.info['Ranker']['Detailed info']['sigma']

  print("mu_star: %s" % mu_star)
  print("mu: %s" % mu)
  print("sigma: %s" % sigma)

if __name__ == "__main__":
  main()
