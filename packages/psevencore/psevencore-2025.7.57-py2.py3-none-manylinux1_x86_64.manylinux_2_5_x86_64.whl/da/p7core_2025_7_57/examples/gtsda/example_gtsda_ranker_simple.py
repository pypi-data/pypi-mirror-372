#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from da.p7core import blackbox, gtsda
from da.p7core.loggers import StreamLogger
import numpy as np

class ExampleBlackbox(blackbox.Blackbox):
  """
  Problem representation for GTSDA ranker in blackbox mode
  """
  def prepare_blackbox(self):
    # add new variable in problem
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    # add new response in problem
    self.add_response()

  def evaluate(self, queryx):
    result = []
    for x in queryx:
      result.append(sum(x))
    return result


def blackbox():
  """
  Example for estimate variable scores for a blackbox
  """
  # create ranker
  ranker = gtsda.Analyzer()
  # set options
  ranker.options.set("GTSDA/Seed", 100)
  # set logger, by default StreamLogger output to sys.stdout
  ranker.set_logger(StreamLogger())

  # create problem
  bbox = ExampleBlackbox()
  budget = 350
  # get result
  result = ranker.rank(blackbox=bbox, budget=budget)
  # print some info about result
  print(str(result))
  print("\nResults with default options (screening indices are selected):")
  print('-' * 60)
  for i, s in enumerate(result.scores):
    print('score for blackbox response[%d]: %s' % (i, s))
  print('-' * 60)

  result = ranker.rank(blackbox=bbox, budget=budget, options={'GTSDA/Ranker/Technique':'sobol'})
  # print some info about result
  print(str(result))
  print("\nResults with Sobol indices:")
  print('-' * 60)
  for i, s in enumerate(result.scores):
    print('score for blackbox response[%d]: %s' % (i, s))
  print('-' * 60)


def sample():
  """
  Example for estimate variable scores for input variables with respect to each output variable based on a "solid" sample given by user
  """
  # prepare data
  # note, than tool need big training sample
  number = 1000
  input_dimension = 4
  output_dimension = 2
  np.random.seed(100)
  # input part of sample
  x = np.random.rand(number, input_dimension)
  # output part of sample
  y = np.hstack((x[:, [0]] + 2 * x[:, [1]], x[:, [3]]))

  # create ranker
  ranker = gtsda.Analyzer()
  # set Logger
  ranker.set_logger(StreamLogger())

  # get result
  result = ranker.rank(x=x, y=y)
  # print info about results:
  print(str(result))
  print("\nResults:")
  print('-' * 60)
  for i, s in enumerate(result.scores):
    print('score for output[%d]: %s' % (i, s))
  print('-' * 60)

def main():
  """
  Example of GTSDA Ranker usage.
  """
  print('=' * 60)
  # example for Sample-based type of algorithm
  sample()
  print('=' * 60)
  # example for Blackbox-based type of algorithm
  blackbox()
  print('=' * 60)

if __name__ == "__main__":
  main()
