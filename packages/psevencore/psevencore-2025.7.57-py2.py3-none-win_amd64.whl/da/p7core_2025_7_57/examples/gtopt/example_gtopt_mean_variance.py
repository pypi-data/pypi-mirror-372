#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Solve the following optimization problem:

min          f(x) = - [5 * (11 - x)^2 + 2]^-1 + (x - 15)*(x - 16)/120 - 2
w.r.t        0 <= x <= 20
stochastic:  x -> x + zeta,   zeta ~ N(0,2)

Get Pareto frontier in space of mean-variance, i.e.
problem is two-objective : f_0 = <f(x)>,  f_1 = sqrt{ <f^2> - <f>^2

WARNING: The execution of this example can be time consuming!
"""

from da.p7core import gtopt
from da.p7core import loggers

import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import random
import datetime

class MeanVarProblem(gtopt.ProblemMeanVariance):
  def __init__(self, initial_guess = None):
    gtopt.ProblemMeanVariance.__init__(self)
    self.hist = {}

  def prepare_problem(self):
    self.add_variable((0., 20.), None, 'x1')
    self.set_objective('f1')
    self.set_stochastic(MyDistributionNormal(2.), 'stoh')

  def define_objective(self, x):
    def _f(x):
      return -1./(5. * (x - 11.) * (x - 11.) + 2.) + (x - 15.) * (x - 16.)/120. - 2.
    F = _f(x[0] + x[1])
    if x[0] not in self.hist:
      self.hist[x[0]] = []
    self.hist[x[0]] = self.hist.get(x[0])+[-F]
    return F

  def get_n_calls(self):
    return self._n_calls

  def define_constraints(self, x):
    return [ ]
  def define_objective_gradient(self, x):
    return [ ]
  def define_constraints_gradient(self, x):
    return [ ]

class MyDistributionNormal:
  def __init__(self, sigma):
    self._sigma = sigma
  def getNumericalSample(self, quantity):
    out = []
    for i in range(0, quantity):
      ksi = random.normalvariate(0.0, self._sigma)
      out.append(ksi)
    return out
  def getDimension(self):
    return 1

def solve_problem(problem):
  optimizer = gtopt.Solver()
  # set logger, by default output -- to sys.stdout
  optimizer.set_logger(loggers.StreamLogger(log_level = loggers.LogLevel.DEBUG))
  # set options
  optimizer.options.set('GTOpt/MOPIsGlobal', 'True')
  optimizer.options.set('GTOpt/RobustObjectiveTolerance', 0.005)
  optimizer.options.set('GTOpt/FrontDensity', 8)
  optimizer.options.set('GTOpt/LogLevel', 'Debug')
  print(str(problem))
  result = optimizer.solve(problem)
  print(str(result))
  print("Optimal:")
  result.optimal.pprint()
  return result

def plot(problem, result):
  plt.clf()
  fig = plt.figure(1)
  fig.subplots_adjust(left=0.2, wspace=0.6, hspace=0.6)
  plt.title('Robust Optimization Problem Example')
  plt.axis('off')
  ax = fig.add_subplot(111)    # The big subplot
  ax1 = fig.add_subplot(211)

  ax1.set_xlabel('x')
  ax1.set_ylabel('f')
  x = list(problem.hist.keys())
  fmean = [sum(problem.hist.get(t))/len(problem.hist.get(t)) for t in x]
  ax1.plot(x, fmean, 'cD', label = 'Mean Value at point')
  t = np.arange(4.,20.1, 0.1)
  s = [(1/(5*(11-x)**2 + 2) - (x - 15)*(x - 16)/120 + 2 ) for x in t]
  ax1.plot(t,s)
  x = [ z[0] for z in result.optimal.x]
  m = [-z[0] for z in result.optimal.f]
  ax1.plot(x,m, 'ro', label = 'Robust Optimal Solution')
  ax1.legend(loc = 'best')

  ax2 = fig.add_subplot(212)
  ax2.set_xlabel('M')
  ax2.set_ylabel('S')
  merr = [z[0] for z in result.optimal.fe]
  serr = [z[1] for z in result.optimal.fe]
  s = [z[1] for z in result.optimal.f]
  ax2.errorbar(m,s, serr, merr, marker = 'o', ls = 'None')
  title = 'MeanVariance'
  plt.title(title)
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  problem = MeanVarProblem()
  print('=' * 60)
  print('Solve problem %s' % problem.__class__.__name__)
  #measure time
  time_start = datetime.datetime.now()
  result = solve_problem(problem)
  time_stop = datetime.datetime.now()
  plot(problem, result)
  print('Finished!')
  print('=' * 60)
  print('Total time elapsed: %s' % (time_stop - time_start))


if __name__ == "__main__":
  main()
