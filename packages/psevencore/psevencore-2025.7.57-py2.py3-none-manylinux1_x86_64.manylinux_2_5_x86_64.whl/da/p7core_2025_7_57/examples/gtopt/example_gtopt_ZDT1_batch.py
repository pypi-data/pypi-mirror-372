#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Solve the ZDT1 problem using GTOpt in batch mode.
"""

#[0] required imports
from da.p7core import gtopt
from da.p7core import loggers

from pprint import pprint

import sys
from math import sqrt
#[0] end imports


#[1] problem definition
class ZDT1(gtopt.ProblemUnconstrained):

  def __init__(self):
    self.count = 0

  def prepare_problem(self):
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    self.add_objective()
    self.add_objective()

  def define_objectives(self, x):
    f1 = x[0]
    g = 1.0 + 9.0 * x[1]
    f2 = g * (1.0 - sqrt(f1 / g))
    # counter
    self.count += 1
    return f1, f2
#[1] end problem definition

#[2] batch problem definition
class ZDT1Batch(gtopt.ProblemUnconstrained):

  def __init__(self):
    self.count = 0

  def prepare_problem(self):
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    self.add_objective()
    self.add_objective()

  def define_objectives_batch(self, x):
    f_batch = []
    for xi in x:
      f1 = xi[0]
      g = 1.0 + 9.0 * xi[1]
      f2 = g * (1.0 - sqrt(f1 / g))
      f_batch.append([f1, f2])
    # counter
    self.count += 1
    return f_batch
#[2] end batch problem definition

#[3] problem solving
def solve_problem(problem, batch_size = 1):
  print(str(problem))
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger())
  optimizer.options.set({'GTOpt/FrontDensity': 15, 'GTOpt/BatchSize': batch_size})
  result = optimizer.solve(problem)
  return result
#[3]

#[4] main
def main():
  # solve in normal mode

  problem = ZDT1()
  print('=' * 60)
  print('Solve the ZDT1 problem in normal mode.')
  result = solve_problem(problem)
  print(str(result))
  print("\nOptimal points:")
  result.optimal.pprint(limit=10)  # most points omitted to shorten output

  # solve in batch mode, maximum batch size is 10
  problem_batch = ZDT1Batch()
  print('=' * 60)
  print('Solve the ZDT1 problem in batch mode.')
  result_batch = solve_problem(problem_batch, 10)
  print(str(result_batch))
  print("\nOptimal points:")
  result_batch.optimal.pprint(limit=10)  # most points omitted to shorten output

  # print evaluations
  print('=' * 60)
  print('Number of evaluation calls\n')
  print('Normal mode: %s total' % (problem.count))
  print('Batch mode: %s total' % (problem_batch.count))

  print('Finished!')
  print('=' * 60)
#[4]

if __name__ == '__main__':
  main()