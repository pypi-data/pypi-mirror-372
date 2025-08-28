#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Simple constrained quadratic problem with undefined regions/points
Solve the following optimization problem:

min   (x^2 + y^2)
s.t.  x + y <= -2

with some probability to get NaN while calculating objective and constraint
'''

from da.p7core import gtopt
from da.p7core import loggers

import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import random

random.seed(1)
NAN_PROBABILITY = 0.1

class ConstrainedQuadraticNaN(gtopt.ProblemConstrained):
  def __init__(self):
    self.hist = []
    self.nan_hist = []

  def prepare_problem(self):
    # add one objective
    self.add_objective()
    # add variables
    self.add_variable((None, None) , -1.2)
    self.add_variable((None, None) , -1.2)
    # add constraint
    self.add_constraint((None, -2.))

  def define_objectives(self, x):
    f = x[0]*x[0] + x[1]*x[1]
    if random.random() < NAN_PROBABILITY:
      f = np.nan
      self.nan_hist.append(x)
    else:
      self.hist.append(x)
    return f

  def define_constraints(self, x):
    con = x[0] + x[1]
    if random.random() < NAN_PROBABILITY:
      con = np.nan
    return con

def solve_problem(problem):
  # create optimizer instance
  optimizer = gtopt.Solver()
  # set logger
  optimizer.set_logger(loggers.StreamLogger(sys.stdout, loggers.LogLevel.DEBUG))
  # set options
  options = []
  options.append(('GTOpt/DiffType', 'Framed'))
  for option in options:
    optimizer.options.set(*option)
  # print information about problem
  print(str(problem))
  # here the problem is solving
  result = optimizer.solve(problem)
  # print solution
  print(str(result))
  print("Optimal:")
  result.optimal.pprint()
  return result

def plot(problem,result):
  plt.clf()
  fig = plt.figure(1)
  ax = fig.add_subplot(111)
  ax.axis([-1.5, 0., -1.5, 0.])
  x = y = np.linspace(-1.5, 0., 30)
  [X, Y] = np.meshgrid(x, y)
  Z = X * X + Y * Y
  CS = ax.contour(X,Y,Z, 8)
  plt.clabel(CS, fontsize=10, inline=1)
  tr1 = [z[0] for z in problem.hist]
  tr2 = [z[1] for z in problem.hist]
  nantr1 = [z[0] for z in problem.nan_hist]
  nantr2 = [z[1] for z in problem.nan_hist]
  cx1 = np.linspace(0, 1, 60)
  cx2 = np.array([np.sqrt(1- z*z) for z in cx1])
  ax.plot(tr1, tr2, 'g+', label = 'Optimization Steps')
  ax.plot(nantr1, nantr2, 'bo', label = 'Nan points')
  ax.plot(result.optimal.x[0][0], result.optimal.x[0][1], 'ro', label = 'Optimal Solution')
  title = 'Constrained quadratic with Nan'
  plt.title(title)
  plt.legend(loc = 'best')

  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  print('=' * 60)
  print('Solve problem ConstrainedQuadraticNaN')
  problem = ConstrainedQuadraticNaN()
  result = solve_problem(problem)
  plot(problem,result)
  print('Finished!')
  print('=' * 60)

if __name__ == '__main__':
  main()

