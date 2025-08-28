#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Example of solutions of sequence of perturbed multiobjective problems."""

from da.p7core import gtopt
from da.p7core import loggers
from pprint import pprint
import matplotlib.pyplot as plt
import os
import sys
import math


class ConstrainedMOProblem(gtopt.ProblemConstrained):
  """
  Problem: min f1 = (x1 - 1)^2 + (x2 - 1)^2, f2 = (x1+1)^2 + (x2 + 1)^2, where -2 < x1,x2 < 2
           s.t. (x1-0.2)^2 + x2^2 >= (R+pert)^2
  Initial guess: x1_0 = 1,  x2_0 = 0
  """
  def __init__(self, radius = 1., perturbation = 0., initial_guess = None):
    gtopt.ProblemConstrained.__init__(self)
    self._r = radius
    self._pert = perturbation
    self._ig = initial_guess
    self._n_calls = 0

  def prepare_problem(self):
    if not self._ig is None:
      self.add_variable((-2., 2.), self._ig[0])
      self.add_variable((-2., 2.), self._ig[1])
    else:
      self.add_variable((-2., 2.), 1)
      self.add_variable((-2., 2.), 0)
    self.add_constraint(((self._r+self._pert)**2, None))
    self.add_objective(hints = {'@GTOpt/LinearityType' : 'Quadratic'})
    self.add_objective(hints = {'@GTOpt/LinearityType' : 'Quadratic'})

  def define_objectives(self, x):
    self._n_calls += 1
    return [(x[0] - 1.)**2 + (x[1] - 1.)**2, (x[0] + 1.)**2 + (x[1] + 1.)**2]

  def define_constraints(self, x):
    return [(x[0]-0.2)**2 + x[1]**2]

  def get_n_calls(self):
    return self._n_calls

def perturbed_problem_example():
  optimizer = gtopt.Solver()
  # set logger, by default output -- to sys.stdout
  optimizer.set_logger(loggers.StreamLogger())
  optimizer.options.set('GTOpt/MOPIsGlobal', 'True')
  optimizer.options.set('GTOpt/FrontDensity', 12)
  problem = ConstrainedMOProblem(perturbation = 0., initial_guess = None)
  print("TEST")
  print(str(problem))
  result = optimizer.solve(problem)
  print(str(result))
  x_store , f_store = [], []
  x, f = result.optimal.x, result.optimal.f
  x_store.append(x)
  f_store.append(f)
  ig_x = x
  for ipert in range(1,3,1):
    # Setup options
    optimizer.options.set('GTOpt/MOPIsGlobal', 'False')
    pert = ipert*0.05
    pert_n_calls = 0
    ig_x_new = []
    ig_f_new = []

    for ix in ig_x:
      pert_problem = ConstrainedMOProblem(perturbation = pert, initial_guess = ix)
      print(str(pert_problem))
      result = optimizer.solve(pert_problem)
      print(str(result))
      pert_x, pert_f = result.optimal.x, result.optimal.f
      if len(pert_x) > 0:
        pert_n_calls += pert_problem.get_n_calls()
        print('POINT : %s' % pert_x[0])
        ig_x_new.append(pert_x[0])
        ig_f_new.append(pert_f[0])
      else :
        print('No optimal point for %s' % ix)
    ig_x = ig_x_new
    x_store.append(ig_x_new)
    f_store.append(ig_f_new)
  return x_store, f_store

def plot(x_store, f_store):
  plt.clf()
  fig = plt.figure(1)
  fig.subplots_adjust(left=0.2, wspace=1.2)
  title = 'Perturbed_Problem'
  plt.axis('off')
  ax = fig.add_subplot(111)    # The big subplot
  ax1 = fig.add_subplot(212)

  ax1.set_xlabel('X1')
  ax1.set_ylabel('X2')
  circle0 = plt.Circle((0.2, 0), 1, facecolor='none',
              edgecolor='g', linewidth=1, alpha=0.5)
  ax1.add_patch(circle0)

  ax1.axis([-1.5, 1.5, -1.5, 1.5])
  x1 = [e[0] for e in x_store[0]]
  x2 = [e[1] for e in x_store[0]]
  p0 = ax1.plot(x1, x2, 'go', markersize = 4., label = 'Initial')
  circle0 = plt.Circle((0.2, 0), 1.05, facecolor='none',
              edgecolor='r', linewidth=1, alpha=0.5)
  ax1.add_patch(circle0)
  x1 = [e[0] for e in x_store[1]]
  x2 = [e[1] for e in x_store[1]]
  p1 = ax1.plot(x1, x2, 'ro', markersize = 4., label = 'P = 0.05')
  circle0 = plt.Circle((0.2, 0), 1.1, facecolor='none',
              edgecolor='b', linewidth=1, alpha=0.5)
  ax1.add_patch(circle0)
  x1 = [e[0] for e in x_store[2]]
  x2 = [e[1] for e in x_store[2]]
  p2 = ax1.plot(x1, x2, 'bo', markersize = 4., label = 'P = 0.1')
  ax1.legend(loc = 'best')

  ax2 = fig.add_subplot(211)
  ax2.set_xlabel('f1')
  ax2.set_ylabel('f2')
  f1 = [e[0] for e in f_store[0]]
  f2 = [e[1] for e in f_store[0]]
  p0 = ax2.plot(f1, f2, 'go', markersize = 4., label = 'Initial')
  f1 = [e[0] for e in f_store[1]]
  f2 = [e[1] for e in f_store[1]]
  p0 = ax2.plot(f1, f2, 'ro', markersize = 4., label = 'P = 0.05')
  f1 = [e[0] for e in f_store[2]]
  f2 = [e[1] for e in f_store[2]]
  p0 = ax2.plot(f1, f2, 'bo', markersize = 4., linewidth=3 , label = 'P = 0.1')
  ax2.legend(loc = 'best')
  plt.title('Pareto Frontier')
  fig.savefig('Perturbed_Problem_Example')
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

if __name__ == "__main__":
  x_store, f_store = perturbed_problem_example()
  plot(x_store, f_store)
