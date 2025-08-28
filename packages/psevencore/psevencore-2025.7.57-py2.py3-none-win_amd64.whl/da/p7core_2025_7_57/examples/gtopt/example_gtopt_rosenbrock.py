#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Find the minimum of Rosenbrock function.
2 problems: unconstrained and constrained.
'''

from da.p7core import gtopt
from da.p7core import loggers

import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import math
from pprint import pprint

class RosenbrockUnconstrainedProblem(gtopt.ProblemUnconstrained):
  '''
  Solve the following optimization problem:

  min f = 100 (x_1 - x^2_0)^2 + (1. - x_0)^2

  Solution is at x_1 = x_2 = 1, and the objective function is 0.

  Link: http://en.wikipedia.org/wiki/Rosenbrock_function
  '''
  def prepare_problem(self):
    # add one objective
    self.add_objective()
    # add 0 <= x1,x2 <= 2
    self.add_variable((0.0, 2.0))
    self.add_variable((0.0, 2.0))

  def define_objectives(self, x):
    return 100.0 * (x[1] - x[0]*x[0])*(x[1] - x[0]*x[0]) + (1.0 - x[0])*(1.0 - x[0])

class RosenbrockConstrainedProblem(gtopt.ProblemConstrained):
  '''
  Minimizing of Rosenbrock function with additional constraint:

  x_0^2 + x_1^2 <= 1
  '''
  def prepare_problem(self):
    # add one constraint
    self.add_constraint((0., 1.))
    # add one objective
    self.add_objective()
    # add 0 <= x1,x2 <= 2
    self.add_variable((0.0, 2.0))
    self.add_variable((0.0, 2.0))

  def define_constraints(self, x):
    return x[0] * x[0] + x[1] * x[1]

  def define_objectives(self, x):
    return 100.0 * (x[1] - x[0]*x[0])*(x[1] - x[0]*x[0]) + (1.0 - x[0])*(1.0 - x[0])

def solve_problem(problem):
  # create optimizer instance
  optimizer = gtopt.Solver()
  # set logger
  optimizer.set_logger(loggers.StreamLogger())
  # print information about problem
  print(str(problem))
  # solve problem
  result = optimizer.solve(problem)
  # print solution
  print(str(result))
  print("Optimal:")
  result.optimal.pprint()
  # make plots
  return result

def plot(problem, result):
  plt.clf()
  fig = plt.figure(1)
  fig.subplots_adjust(left=0.2, wspace=0.6, hspace=0.6)
  title = 'Rosenbrock unconstrained problem'
  plt.title(title)
  ax = fig.add_subplot(111)
  ax.axis('off')
  ax1 = fig.add_subplot(211)
  ax1.set_xlabel('x1')
  ax1.set_ylabel('x2')
  ax2 = fig.add_subplot(212)
  ax2.set_title('In the neighborhood of the optimal point')
  ax2.set_xlabel('x1')
  ax2.set_ylabel('x2')
  ax2.axis([0.95, 1.05, 0.95, 1.05])
  # draw function contours
  x = y = np.linspace(0, 2, 60)
  [X, Y] = np.meshgrid(x, y)
  Z = 100.0 * (Y - X*X)*(Y - X*X) + (1.0 - X)*(1.0 - X)
  ax1.contour(X,Y,Z, 60)
  x = y = np.linspace(0.95, 1.05, 30)
  [X, Y] = np.meshgrid(x, y)
  Z = 100.0 * (Y - X*X)*(Y - X*X) + (1.0 - X)*(1.0 - X)
  ax2.contour(X,Y,Z, 60)
  tr1 = [z[0] for z in problem.history]
  tr2 = [z[1] for z in problem.history]

  ax1.plot(tr1, tr2, 'b+', label = 'Optimization Steps')
  ax1.plot(result.optimal.x[0][0], result.optimal.x[0][1], 'ro', label = 'Optimal Solution')
  ax1.legend()
  ax2.plot(tr1, tr2, 'b+', label = 'Optimization Steps')
  ax2.plot(result.optimal.x[0][0], result.optimal.x[0][1], 'ro', label = 'Optimal Solution')
  ax2.legend()

  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  # solve constrained problem
  print('=' * 60)
  print('Solve problem RosenbrockConstrainedProblem')
  problem = RosenbrockConstrainedProblem()
  result = solve_problem(problem)
  print('Finished!')
  print('=' * 60)

  # solve unconstrained problem and draw solution
  print('=' * 60)
  print('Solve problem RosenbrockUnconstrainedProblem')
  problem = RosenbrockUnconstrainedProblem()
  result = solve_problem(problem)
  plot(problem,result)
  print('Finished!')
  print('=' * 60)

if __name__ == '__main__':
  main()
