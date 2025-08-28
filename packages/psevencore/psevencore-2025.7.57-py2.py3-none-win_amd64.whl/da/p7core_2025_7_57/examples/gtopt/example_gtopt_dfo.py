#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Example demonstrates using of different strategies for estimating derivatives."""

from da.p7core import gtopt
from da.p7core import loggers

import matplotlib.pyplot as plt
import numpy

import os

def noisy_function(x):
  return x * x * (1 + 0.03 * numpy.sin(800 * x))

class MultimodalProblemExample(gtopt.ProblemUnconstrained):
  def prepare_problem(self):
    self.add_variable((-1.0, 1.0), 0.9)
    self.add_objective()

  def define_objectives(self, x):
    return noisy_function(x)

def solve_problem(problem, options):
  # create optimizer with default parameters
  optimizer = gtopt.Solver()
  #set options
  for option in options:
    optimizer.options.set(*option)
  #display problem general info
  print(str(problem))
  # solve problem and get result
  result = optimizer.solve(problem)
  # print general info about result
  print(str(result))
  # print list of of all answers:
  print("Optimal:")
  result.optimal.pprint(["x", "f"])
  return (result.optimal.x[0][0], result.optimal.f[0][0]), numpy.array(problem.history)

def main():
  print("Find the minimum of function")
  print("=" * 60)
  results = {}
  hist = {}
  for diff_type in ["Framed", "Numerical"]:
    results[diff_type], hist[diff_type] = solve_problem(MultimodalProblemExample(), [("GTOpt/DiffType", diff_type)])
  plot(results, hist)
  print("=" * 60)
  print("Finished!")
  assert(results["Framed"][1] < results["Numerical"][1])


def plot(results, hist):
  plt.clf()
  fig = plt.figure(1)
  ax = fig.add_subplot(111)
  title = "DFO"
  colors = {"Framed": ["ro", "r+"], "Numerical": ["bD", "b+"]}
  x = numpy.linspace(-0.1 , 1., 500)
  y = noisy_function(x)
  ax.plot(x,y, "c-")
  for n in ["Framed", "Numerical"]:
    ax.plot(results[n][0], results[n][1], colors[n][0], label="%s Solution"%n, markersize=10)
    ax.plot(hist[n][:, 0], hist[n][:, 1], colors[n][1], label="%s Optimization steps"%n, markersize=10)
  ax.legend(loc = "best")
  plt.title(title)
  ax.set_xlabel("x")
  ax.set_ylabel("f")
  ax.axis([-0.1, 1., -0.1, 1.])
  ax.grid(True)
  plt.title(title)
  fig.savefig(title)
  print("Plots are saved to %s.png" % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

if __name__ == "__main__":
  main()
