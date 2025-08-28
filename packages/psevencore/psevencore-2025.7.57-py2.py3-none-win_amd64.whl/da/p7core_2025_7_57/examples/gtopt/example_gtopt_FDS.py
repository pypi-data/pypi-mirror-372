#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Problem FDS taken from:
J. Fliege, L. M. Grana Drummond, and B. F. Svaiter
Newton's Method for Multiobjective Optimization
SIAM J. Optim. 20, pp. 602-626 (25 pages)
Paper is available online at optimization-online.org

  D = 2

  F_1 = \\frac{1}{D^2} \\sum_{k=1}^D k(x_k - k)^4
  F_2 = exp(\\sum_{k=1}^D \\frac{x_k}{D}) + \\left \\| x \\right \\|_2^2
  F_3 = \\frac{1}{D(D+1)} \\sum_{k=1}^D k(D-k +1)exp(-x_k)

  Constraint surface |x|^2 >= 1
'''

from da.p7core import gtopt
from da.p7core import loggers
import matplotlib.pyplot as plt
import numpy as np
import os

class FDS(gtopt.ProblemConstrained):

  def prepare_problem(self):
    # add variables
    self.add_variable((-2., 2.))
    self.add_variable((-2., 2.))
    # add three objectives
    self.add_objective('f1')
    self.add_objective('f2')
    self.add_objective('f3')
    # add constraint
    self.add_constraint((0., 1.))

  def define_objectives(self, x):
    dimx = self.size_x()
    # use vector evaluations
    indices = np.arange(1, dimx + 1)
    f1 = np.sum(indices * (x - indices)**4) / dimx**2
    f2 = np.exp(sum(x) / dimx) + np.linalg.norm(x)
    f3 = np.sum(indices * (np.ones((dimx,)) * (dimx + 1) - indices) * np.exp(-x)) / dimx / (dimx + 1)
    return f1, f2, f3

  def define_constraints(self, x):
    return np.linalg.norm(x)


def solve_problem(problem):
  # create optimizer instance
  optimizer = gtopt.Solver()
  # set logger
  optimizer.set_logger(loggers.StreamLogger())
  # set options
  optimizer.options.set({
    'GTOpt/DiffType': 'Numerical',
    'GTOpt/LogLevel': 'Info',
    'GTOpt/FrontDensity': 5
  })
  # print information about problem
  print(str(problem))
  # here the problem is solving
  result = optimizer.solve(problem)

  # print solution
  print(str(result))
  print("Optimal points:")
  result.optimal.pprint()
  return result

def plot(result):
  fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

  # get columns as separate arrays for plotting
  X, Y, Z = result.optimal.f.transpose()

  ax.scatter(X,Y,Z)
  ax.view_init(elev=20, azim=120)
  ax.set_xlabel('f1')
  ax.set_ylabel('f2')
  ax.set_zlabel('f3')
  ax.grid(True)

  title = 'FDS'
  plt.title('Pareto Frontier for %s' % title)
  plt.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  problem = FDS()
  print('=' * 60)
  print('Solve problem %s' % problem.__class__.__name__)
  result = solve_problem(problem)
  plot(result)
  print('Finished!')
  print('=' * 60)

if __name__ == '__main__':
  main()

