#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
This example shows how to reuse evaluations in surrogate based optimization in GTOpt.
"""

#[0] required imports
from da.p7core import gtopt
from da.p7core import loggers

import math
import numpy
#[0] end imports

#[1] problem definition with Booth's function. Optimum is f(1,3) = 0
class BoothProblem(gtopt.ProblemUnconstrained):
  def prepare_problem(self):
    self.add_variable((-10, 10))
    self.add_variable((-10, 10))
    # define an expensive objective
    self.add_objective(hints = {'@GTOpt/EvaluationCostType': 'Expensive'})

  def define_objectives(self, x):
    return (x[0] + 2 * x[1] - 7)**2 + (2 * x[0] + x[1] - 5)**2
#[1] end problem definition

#[2] main
def main():
  # configure optimizer
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger())
  # logging options
  optimizer.options.set({'GTOpt/LogLevel': 'Warn'})
  # limit SBO iterations

  print("*"*90)

  optimizer.options.set({'GTOpt/MaximumExpensiveIterations': 10})
  optimizer.options.set({'GTOpt/GlobalPhaseIntensity': 0})
#[2] end configuration
#[3] create and solve problem
  problem = BoothProblem()
  print(str(problem))
  # solve problem using SBO the first time
  result = optimizer.solve(problem)
  print("Initial result %s" % result.optimal.f)
  # all evaluated points are stored in history and can be obtained with designs property
  data = numpy.array(problem.designs)
  print("History 1 %d %s" % (len(data), data))
#[3] problem was solved the first time
#[4] Let's extract stored data and rerun optimization
  x = data[:, 0:2]  #x values
  y = data[:, 2]    #x responses
  # resolve the problem with initial data
  problem.clear_history()
  result = optimizer.solve(problem, sample_x=x, sample_f=y)
  print("Improved result %s" % result.optimal.f)
  # Note, that history contains only evaluated points.
  # Points supplied as initial data does not goes to history.
  data = numpy.array(problem.designs)
  print("History 2 %d %s" % (len(data), data))
#[4] problem was solved the second time

if __name__ == '__main__':
  main()
