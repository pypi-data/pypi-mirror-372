#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from da.p7core import gtsda
from da.p7core.loggers import StreamLogger
import numpy as np
import sys

def _make_sample(sample_size, input_dim, func):
  x = np.random.rand(sample_size, input_dim)
  # output part of sample
  y = func(x)
  return x, y

def mystery_function(x):
  """Example function.

  Args:
    x: 2D point or points batch (a list of two NumPy arrays).

  Returns:
    Single function value, or an array of values. Array shape is the same
    as input shape.
  """
  term1 = x[:, 1] - 5 * x[:, 0] * x[:, 0]
  term2 = 1 - 5 * x[:, 0]
  term3 = 2 - 5 * x[:, 1]
  term4 = np.sin(2.5 * x[:, 0]) * np.sin(17.5 * x[:, 0] * x[:, 1])
  result = 2 + 0.25 * term1 * term1 + term2 * term2 + 2 * term3 * term3 + 7 * term4 + 10 * x[:, 2]**2

  return result

def get_ranking(x, y, analyzer, direction='dec'):
  try:
    scores = analyzer.rank(x=x, y=y).scores[0]
    error = None
  except:
    error = "Error occurred in the ranking procedure: %s." % sys.exc_info()[1]
    scores = None

  if error is not None:
    raise Exception(error)

  # Get ranks based on scores
  if direction == 'inc':
    ranks = np.argsort(scores)
  elif direction == 'dec':
    ranks = np.argsort(-scores)
  else:
    raise ValueError("Direction of the ranking should be 'inc' or 'dec'")

  print('SCORES: %s' % str(scores))
  print('RANKS: %s' % str(ranks))

  return ranks, scores

def run_example():
  """Example for estimate variable scores for input variables with respect to each output variable based on a "solid" sample given by user
  """
  # prepare data
  sample_size = 100
  input_dim = 4
  np.random.seed(100)
  x, y = _make_sample(sample_size, input_dim, mystery_function)

  optimal_feature_list = [0, 1, 2]

  # create analyzer
  analyzer = gtsda.Analyzer()
  # set Logger
  analyzer.set_logger(StreamLogger())

  ranking, _ = get_ranking(x, y, analyzer)

  # get results with internal validation error computation (IV)
  options = {'GTSDA/Selector/ValidationType': 'internal'}
  result_internal = analyzer.select(x=x, y=y, ranking=ranking, options=options)

  # get results with train sample error computation
  options = {'GTSDA/Selector/ValidationType': 'trainsample'}
  result_test = analyzer.select(x=x, y=y, ranking=ranking, options=options)

  print("\nOptimal features: %s" % optimal_feature_list)
  print("Selected features with IV: %s" % result_internal.feature_list[:, 0])
  print("Selected features with train sample validation: %s" % result_test.feature_list[:, 0])

def main():
  """
  Example of GTSDA Selector usage.
  """
  print('=' * 60)
  run_example()
  print('=' * 60)

if __name__ == "__main__":
  main()
