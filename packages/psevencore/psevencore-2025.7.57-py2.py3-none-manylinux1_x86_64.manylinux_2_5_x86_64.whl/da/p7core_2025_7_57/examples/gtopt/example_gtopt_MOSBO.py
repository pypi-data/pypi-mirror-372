#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Solve a simple problem illustrating the multi-objective surrogate based optimization (MOSBO) capability of GTOpt.
"""

#[0] required imports
from da.p7core import gtopt
from da.p7core import loggers

import numpy
import math
import sys
#[0] end imports

#[1] problem definition
class SBOSampleProblem(gtopt.ProblemUnconstrained):

  def __init__(self, use_sbo):
    self.use_sbo = use_sbo
    self.count = 0

  def prepare_problem(self):
    self.add_variable((0, 1), 0.75)
    self.add_variable((0, 1), 0.75)
    # Initialize objectives.
    # If we have at least one 'expensive' objective in a multi-objective problem, MOSBO algorithm will be used.
    self.add_objective(hints={'@GTOpt/EvaluationCostType': 'Expensive' if self.use_sbo else 'Cheap'})
    self.add_objective(hints={'@GTOpt/EvaluationCostType': 'Expensive' if self.use_sbo else 'Cheap'})

  def define_objectives(self, x):
    # ZDT1 test problem
    self.count += 1
    f1 = x[0]
    g = 1.0 + 9.0 * x[1]
    f2 = g * (1.0 - math.sqrt(f1 / g))
    return f1, f2
#[1] end problem definition

#[2] configure optimizer
def optimizer_prepare():
  opt = gtopt.Solver()
  opt.set_logger(loggers.StreamLogger())
  opt.options.set({'GTOpt/LogLevel': 'INFO'})
  return opt
#[2] end configuration

#[3-0] main
def main():
  optimizer = optimizer_prepare()
#[3-1]
  # Solve problem without using MOSBO.
  problem = SBOSampleProblem(False)
  print("\n\nSolving the sample problem without using surrogate based optimization...\n")
  result = optimizer.solve(problem)
  print("\nSolved, wait for SBO version to finish...\n")
#[3-2]
  # Solve the same problem using MOSBO.
  problem_sbo = SBOSampleProblem(True)

  # Use automatic choice of search intensity.
  #optimizer.options.set({"GTOpt/GlobalPhaseIntensity": "auto"})
  print("\n\nSolving the sample problem using surrogate based optimization...\n")
  result_sbo = optimizer.solve(problem_sbo, options={"GTOpt/MaximumExpensiveIterations": 80})
  print("\nSolved.\n\nResults:")
#[3-3]
  # compare results
  print("=" * 60)
  print("Without SBO.\n")
  print("Optimal points:")
  result.optimal.pprint(limit=10)
  print("User function calls: %s" % (problem.count))

  print("=" * 60)
  print("Using SBO.\n")
  print("Optimal points:")
  result_sbo.optimal.pprint(limit=10)
  print("User function calls: %s" % (problem_sbo.count))

  print("=" * 60)
  print("\nFinished!\n")
#[3-4]

if __name__ == '__main__':
  main()
