#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Simple constrained quadratic problem with undefined regions/points

  Solve the following optimization problem with quadratic asymmetric polynomials :

  if sqrt{(x_1 - 1)^2 + (x_2 - 1)^2} <= 0.5

  f1 = 2*x_1^2 + x_2^2
  f2 = (x_1-2)^2 + (x_2-2)^2

  else

  f1 = f2 = NaN
'''
from da.p7core import gtopt
from da.p7core import loggers
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import os

class MOPNaNpolynomials(gtopt.ProblemUnconstrained):

  def prepare_problem(self):
    # add variables
    self.add_variable((0., 3.), 1.)
    self.add_variable((0., 3.), 1.)
    # add objectives
    self.add_objective(hints = {'@GTOpt/LinearityType' : 'Quadratic'})
    self.add_objective(hints = {'@GTOpt/LinearityType' : 'Quadratic'})

  def define_objectives(self, x):
    print("%s %s" % (x, np.linalg.norm(x - np.array([1, 1]))))
    if np.linalg.norm(x - np.array([1, 1])) > 0.5:
      return [np.nan] * 2
    f1 = 2. * x[0]**2 + x[1]**2
    f2 = (x[0] - 2)**2 + (x[1] - 2)**2
    return f1, f2

def solve_problem(problem):
  #create optimizer instance
  optimizer = gtopt.Solver()
  # set logger
  optimizer.set_logger(loggers.StreamLogger())
  # set options
  optimizer.options.set({
    'GTOpt/DiffType': 'Numerical',
    'GTOpt/LogLevel': 'Info',
    'GTOpt/FrontDensity': 5
  })
  #print information about problem
  print(str(problem))

  #problem solving
  result = optimizer.solve(problem)

  #print solution
  print(str(result))
  print("Optimal points:")
  result.optimal.pprint()
  return result

def plot(result):
  plt.figure(1)
  f1, f2 = result.optimal.f.transpose()
  plt.plot(f1, f2, 'bo' , label = 'Pareto Frontier')
  plt.xlabel('f1')
  plt.ylabel('f2')
  plt.legend(loc = 'best')
  title ='Multi-objective problem using polynomials with Nan'
  plt.title(title)
  plt.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  print('=' * 60)
  print('Solve problem MOPNaNpolynomials')
  problem = MOPNaNpolynomials()
  result = solve_problem(problem)
  plot(result)
  print('Finished!')
  print('=' * 60)

if __name__ == '__main__':
  main()
