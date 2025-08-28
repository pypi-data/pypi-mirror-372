#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Solve a simple problem illustrating surrogate based optimization capability of GTOpt.
"""

#[0] required imports
from da.p7core import gtopt
from da.p7core import loggers

import sys
#[0] end imports

#[1] problem definition
class SBOSampleProblem(gtopt.ProblemUnconstrained):

  def __init__(self):
    self.count = 0

  def prepare_problem(self):
    self.add_variable((-1, 1), 0.75)
    self.add_variable((-1, 1), 0.75)
    self.add_variable((-1, 1), 0.75)
    self.add_objective()

  def define_objectives(self, x):
    #f = x1^2 + 4*x2^2 + 8*x3^2
    self.count += 1
    return x[0]*x[0] + 4*x[1]*x[1] + 8*x[2]*x[2]
#[1] end problem definition

#[2] configure optimizer
def optimizer_prepare():
  opt = gtopt.Solver()
  opt.set_logger(loggers.StreamLogger(sys.stdout, loggers.LogLevel.DEBUG))
  opt.options.set({'GTOpt/LogLevel': 'INFO'})
  return opt
#[2] end configuration

#[3] solve problem
def solve_problem(problem, optimizer):
  print(str(problem))
  result = optimizer.solve(problem)
  return result
#[3]

#[4-0] main
def main():
  optimizer = optimizer_prepare()
#[4-1]
  # solve problem not using SBO
  problem = SBOSampleProblem()
  print("\n\nSolving the sample problem without using surrogate based optimization...\n")
  result = solve_problem(problem, optimizer)
  print("\nSolved, wait for SBO version to finish...\n")
#[4-2]
  # solve the same problem using SBO
  problem_sbo = SBOSampleProblem()
  # define an objective expensive
  problem_sbo.set_objective_hints(0, {'@GTOpt/EvaluationCostType': 'Expensive'})
  # uncomment the following line to obtain the full trace of SBO process (WARNING: this log is about 6 MB size!)
  # optimizer.options.set({'GTOpt/LogLevel': 'DEBUG'})
  print("\n\nSolving the sample problem using surrogate based optimization...\n")
  result_sbo = solve_problem(problem_sbo, optimizer)
  print("\nSolved.\n\nResults:")
#[4-3]
  # compare results
  print("=" * 60)
  print("Without SBO.\n")
  print("Optimal point:")
  result.optimal.pprint()
  print("User function calls: %s" % (problem.count))

  print("=" * 60)
  print("Using SBO.\n")
  print("Optimal point:")
  result_sbo.optimal.pprint()
  print("User function calls: %s" % (problem_sbo.count))

  print("=" * 60)
  print("\nFinished!\n")
#[4-4]

if __name__ == '__main__':
  main()
