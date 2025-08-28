#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Solve the following optimization problem:
(minimization of 2D noisy Rosenbrock function)

min f = (100 * (x_1 - x^2_0)^2 + (1. - x_0)^2) * (1 + eps)

where eps has uniform distribution in range (-1, 1)

See: http://en.wikipedia.org/wiki/Rosenbrock_function

The purpose is to illustrate convergence to long valley in noisy case if framed gradients are used.
The problem is solved many times from different starting points.
'''

from da.p7core import gtopt
from da.p7core import loggers
from pprint import pprint

import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import math
import random
random.seed(1)

NOISE =  0.08

class RosenbrockNoisedProblem(gtopt.ProblemUnconstrained):
  def prepare_problem(self):
    # add one objective
    self.add_objective()
    # add variables x1,x2
    for _ in range(2):
      self.add_variable((0.0, 2.0), 2. * random.random())

  def define_objectives(self, x):
    f = 100.0 * (x[1] - x[0]*x[0])*(x[1] - x[0]*x[0]) + (1.0 - x[0])*(1.0 - x[0])
    f *= 1. + NOISE * (2. * random.random() - 1.)
    return f

def solve_noised_problem():
  distr_x1 = []
  distr_x2 = []
  max_cnt = 20
  cnt = 0
  for cnt in range(max_cnt):
    print('Step : %d' % cnt)
    #create optimizer instance
    optimizer = gtopt.Solver()
    # set logger
    optimizer.set_logger(loggers.StreamLogger(sys.stdout, loggers.LogLevel.INFO))
    # set options
    options = []
    options.append(('GTOpt/DiffType', 'Framed'))
    options.append(('GTOpt/ObjectivesSmoothness', 'Noisy'))
    for option in options:
      optimizer.options.set(*option)
    # solve the problem
    result = optimizer.solve(RosenbrockNoisedProblem())
    distr_x1.append(result.optimal.x[0][0])
    distr_x2.append(result.optimal.x[0][1])
  return distr_x1, distr_x2

def plot(distr_x1, distr_x2):
  plt.clf()
  fig = plt.figure(1)
  title = 'Minimization of 2D noisy Rosenbrock function'
  plt.title(title)
  ax1 = fig.add_subplot(111)
  ax1.set_xlabel('x1')
  ax1.set_ylabel('x2')
  # draw function contours
  x = y = np.linspace(0., 2., 100)
  [X, Y] = np.meshgrid(x, y)
  Z_det = (100.0 * (Y - X*X)*(Y - X*X) + (1.0 - X)*(1.0 - X))
  Z = []
  for row in Z_det :
    Z.append([])
    for i in row:
      Z[-1].append(i*(1. + NOISE * (2. * random.random() - 1.)))
  ax1.contour(X,Y,Z, 60)
  p1 = ax1.plot(distr_x1, distr_x2, 'gD', markersize = 5., label = 'Solution Valley')
  ax1.legend()

  fig.savefig(title)
  print('Plot is saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  print('=' * 60)
  print('Solve problem RosenbrockNoisedProblem')
  distr_x1, distr_x2 = solve_noised_problem()
  plot(distr_x1, distr_x2)
  print('Finished!')
  print('=' * 60)

if __name__ == '__main__':
  main()

