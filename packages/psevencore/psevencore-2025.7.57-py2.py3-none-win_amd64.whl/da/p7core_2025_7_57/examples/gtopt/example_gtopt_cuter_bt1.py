#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
The following optimization problem is solved in this example:

Constrained quadratic problem BT1 from CUTER test suite

minimize          100 * x0^2 + 100 * x1^2 - x0 - 100
subject to        x0^2 + x1^2 = 1
with respect to   0 <= x_1, x_2 <= 1
starting point    (0.08, 0.06)
'''

from da.p7core import gtopt
from da.p7core import loggers

import numpy as np
import matplotlib.pyplot as plt

import os
import sys

class CUTER_BT1(gtopt.ProblemConstrained):
  def prepare_problem(self):
    # enable saving objective and constraint evaluations
    self.enable_history()
    # add one objective
    self.add_objective(hints = {'@GTOpt/LinearityType' : 'Quadratic'})
    # add variables
    self.add_variable((0.0, 1), 0.08, 'x0')
    self.add_variable((0.0, 1), 0.06, 'x1')
    # add constraints
    self.add_constraint((1.0, 1.0) , hints = {'@GTOpt/LinearityType' : 'Quadratic'})

  def define_objectives(self, x):
    return 100. * x[0] * x[0] + 100. * x[1] * x[1] - x[0] - 100.

  def define_constraints(self, x):
    return x[0] * x[0] + x[1] * x[1]

def solve_problem(problem):
  # create optimizer instance
  optimizer = gtopt.Solver()
  # set logger
  optimizer.set_logger(loggers.StreamLogger())
  # set options
  optimizer.options.set('GTOpt/DiffType', 'Numerical')
  # print information about problem
  print(str(problem))
  # solve the problem
  result = optimizer.solve(problem)
  # print solution
  print(str(result))
  print("Optimal:")
  result.optimal.pprint(['x'])
  result.optimal.pprint(['f'])
  return result

def plot(problem, result):
  fig = plt.figure(0, figsize = (5,10), dpi = 96)
  title = problem.__class__.__name__
  plt.title(title)
  ax = fig.add_subplot(111)
  ax.axis('off')
  ax1 = fig.add_subplot(211)
  ax1.axis([0., 1.05, 0., 1.05])
  ax2 = fig.add_subplot(212)
  ax2.axis([0.95, 1.05, 0., 0.1])
  x = y = np.linspace(0., 1.05, 50)
  [X, Y] = np.meshgrid(x, y)
  Z = 100. * X * X + 100. * Y * Y - X - 100.
  ax1.contour(X,Y,Z, 8)

  tr1 = [x[0] for x in problem.history]
  tr2 = [x[1] for x in problem.history]

  cx1 = np.linspace(0., 1., 1000 , True)
  cx2 = np.array([np.sqrt(1- x*x) for x in cx1])
  ax1.plot(cx1, cx2, label = 'constraint')
  ax1.plot(tr1, tr2, 'b+', label = 'Optimization Steps')
  ax1.plot(result.optimal.x[0][0], result.optimal.x[0][1], 'ro', markersize = 5., label = 'Optimal Solution')
  ax1.legend(loc = 'best')

  ax2.contour(X, Y, Z, 50)
  ax2.plot(cx1, cx2, label = 'constraint')
  ax2.plot(result.optimal.x[0][0], result.optimal.x[0][1], 'ro', markersize = 5., label = 'Optimal Solution')
  ax2.legend(loc = 'best')

  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  problem = CUTER_BT1()
  print('=' * 60)
  print('Solve problem %s' % problem.__class__.__name__)
  result = solve_problem(problem)
  plot(problem, result)
  print('Finished!')
  print('=' * 60)

if __name__ == '__main__':
  main()

