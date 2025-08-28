#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Example of solving some well-known benchmarking problems using GTOpt"""

from da.p7core import gtopt
from da.p7core import loggers
from pprint import pprint
import os
import matplotlib.pyplot as plt
import numpy as np

class AckleyDesignSpaceExampleProblem(gtopt.ProblemUnconstrained):
  """
  Ackley function
  Number of variables: n = 2.
  global optima: x* = [- 1.5096201, -0.7548651]
  f(x*) = -4.59010163
  Link: http://www.it.lut.fi/ip/evo/functions/node14.html
  Source: D. H. Ackley. "A connectionist machine for genetic hillclimbing". Boston: Kluwer Academic Publishers, 1987.
  """
  def prepare_problem(self):
    self.enable_history()
    for i in range(2):
      self.add_variable((-2.0, 2.0), 0.5)
    self.add_objective()

  def define_objectives(self, x):
    pass

class AckleyProblemListExampleProblem(AckleyDesignSpaceExampleProblem):
  """
  Ackley function: define_objectives returns list
  """
  def define_objectives(self, x):
    a, b, c = np.exp(-0.2), 3.0, 2.0
    objectives = a * np.sqrt(x[0]**2 + x[1]**2) + b * (np.cos(c * x[0]) + np.sin(c * x[1]))
    return [objectives]

class AckleyProblemSingleExampleProblem(AckleyDesignSpaceExampleProblem):
  """
  Ackley function: define_objectives returns float
  """
  def define_objectives(self, x):
    a, b, c = np.exp(-0.2), 3.0, 2.0
    obj = a * np.sqrt(x[0]**2 + x[1]**2) + b * (np.cos(c * x[0]) + np.sin(c * x[1]))
    return obj

def run_singleobjective_example(problem):
  print(str(problem))
  # create optimizer with default parameters
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger())
  # solve problem and get result
  result = optimizer.solve(problem)
  # print general info about result
  print(str(result))
  # print list of of all answers:
  print("Optimal answer:")
  result.optimal.pprint(['x'])
  # print list of the best answers:
  print("Converged answer:")
  result._converged.pprint(['x'])
  print("Functions values on answer:")
  result._converged.pprint(['f'])
  hist = [[],[]]
  hist[0] = [[x[0]] for x in problem.history]
  hist[1] = [[x[1]] for x in problem.history]
  return result, hist

def plot(result, hist):
  plt.clf()
  fig = plt.figure(1)
  ax = fig.add_subplot(111)
  title = 'Ackley function'
  plt.title(title)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  x = y = np.linspace(-2., 2., 50)
  [X, Y] = np.meshgrid(x, y)
  a, b, c = np.exp(-0.2), 3.0, 2.0
  Z = a * np.sqrt(X**2 + Y**2) + b * (np.cos(c * X) + np.sin(c * Y))
  ax.contour(X,Y,Z, 8)

  x,y = hist
  ax.plot(x, y, 'b+', markersize = 5., label = 'Optimization Steps')
  ax.plot(result.optimal.x[0][0], result.optimal.x[0][1], 'ro', markersize = 5., label = 'Optimal Solution')
  ax.legend(loc = 'best')
  plt.title(title)
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()


def main():
  """Example of GTOpt usage."""
  result = []
  hist = []
  for problem in [AckleyProblemListExampleProblem(), AckleyProblemSingleExampleProblem()]:
    print('Find minimum function')
    print('=' * 60)
    result, hist = run_singleobjective_example(problem)
    print('=' * 60)
    print('Finished!')
  plot(result, hist)

if __name__ == "__main__":
  main()
