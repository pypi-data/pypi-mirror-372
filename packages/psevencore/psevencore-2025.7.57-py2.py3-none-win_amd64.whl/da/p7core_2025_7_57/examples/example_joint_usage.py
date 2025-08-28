#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example of collaborative usage of 3 generic tools: GTDoE, GTApprox and GTOpt.

Problem DTLZ2 is optimized using surrogate models.
First, Optimal Latin Hypercube with 10 points is generated (GTDoE is used).
Then, surrogate model is constructed using this DOE (GTApprox is used).
After this, the surrogate model is optimized and Pareto-frontier is obtained (GTOpt is used).
At the end, this Pareto-frontier is compared with true Pareto-frontier.
True Pareto-frontier is obtained as a result of optimization of the original problem with big value of front density (GTOpt is used).
2 plots are generated: surrogate model vs original function and true Pareto-frontier vs approximate Pareto-frontier.
One can see, that result for the surrogate model is close to the result for the original function, albeit only 10 evaluations is used.
Matplotlib is required for displaying plots.
"""

from da.p7core import gtapprox
from da.p7core import gtopt
from da.p7core import gtdoe
from da.p7core.loggers import StreamLogger

from pprint import pprint
from math import cos, sin, pi

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('EXAMPLE')

try:
  import numpy as np
  import matplotlib.pyplot as plt
  show_plots = True
except:
  log.warn('Matplotlib isn\'t found. No plots will be shown')
  show_plots = False

def DTLZ2(x):
  """
  Detailed description: http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz2/index.php
  """
  a = 0.5
  obj = 0.0
  for j in range(1,len(x)):
    obj = obj + (x[j]-a)**2
  g = obj
  f1 = (1.0+g)*cos(a*x[0]*pi)
  f2 = (1.0+g)*sin(a*x[0]*pi)
  return [f1, f2]

class DTLZ2Problem(gtopt.ProblemUnconstrained):
  """
  Definition of unconstrained multi-objective optimization problem DTLZ2
  """
  def prepare_problem(self):
    self.add_variable((0.0, 1.0), 0.5)
    self.add_variable((0.0, 1.0), 0.5)
    self.add_objective()
    self.add_objective()

  def define_objectives(self, x):
    return DTLZ2(x)


class DTLZ2SurrogateProblem(DTLZ2Problem):
  """
  Problem with design space (defined in function 'prepare_problem') from DTLZ2
  It calculates trained surrogate model in 'define_objectives'
  """
  def __init__(self, rsm):
    self.__rsm = rsm

  def define_objectives(self, x):
    return list(self.__rsm.calc(x))

def generate_OLHS(num_points):
  """
  Generate Optimal Latin Hypercube DOE which contains given number of points
  """
  log.info('Generating Optimal Latin Hypercube with %d points' % num_points)
  generator = gtdoe.Generator()
  generator.set_logger(StreamLogger())
  options = {
    'GTDoE/Technique': 'OLHS',
    'GTDoE/Deterministic': 'on',
    'GTDoE/Seed': 10000
  }
  generator.options.set(options)
  result = generator.generate(bounds=([0.0, 0.0], [1.0, 1.0]), count=num_points)
  return result.points

def optimize_problem(problem, options):
  """
  Run optimization of a given problem, print and return result
  """
  log.info('Optimizing problem %s' % problem.__class__.__name__ )
  optimizer = gtopt.Solver()
  optimizer.set_logger(StreamLogger())
  for option in options:
    optimizer.options.set(*option)
  result = optimizer.solve(problem)
  print(str(result))
  return result

def approx_function(func, doe):
  """
  Train approximator. Training sample is calculated using given DOE and function.
  """
  log.info('Approximating function %s' % func.__name__)
  builder = gtapprox.Builder()
  builder.set_logger(StreamLogger())
  model = builder.build(doe, [func(x) for x in doe])
  return model

def generate_plot_data(func):
  """
  Generate data for contour plots
  """
  num_x = 50
  num_y = 50
  X = np.linspace(0.0, 1.0, num_x)
  Y = np.linspace(0.0, 1.0, num_y)
  X, Y = np.meshgrid(X, Y)
  Z1 = np.zeros((num_y, num_x))
  Z2 = np.zeros((num_y, num_x))
  for i in range(num_y):
    for j in range(num_x):
      Z1[i][j], Z2[i][j] = (func([X[i][j], Y[i][j]]))
  return X, Y, Z1, Z2

def set_limits(subplot):
  """
  Set x and y limits for a given subplot.
  """
  subplot.set_xlim(0.0, 1.0)
  subplot.set_ylim(0.0, 1.0)

def plot_countour(fig, func, **kwargs):
  """
  Construct 2 contour plots. Suits for visualization of 2-objective problem in 2D design space
  """
  X, Y, Z1, Z2 = generate_plot_data(func)
  sub1 = fig.add_subplot(211)
  CS = plt.contour(X, Y, Z1, 10, **kwargs)
  sub1.clabel(CS, fontsize=9, inline=1)
  set_limits(sub1)
  sub1.set_title('f0')
  sub1.set_xlabel('x0')
  sub1.set_ylabel('x1')
  sub2 = fig.add_subplot(212)
  CS = plt.contour(X, Y, Z2, 10, **kwargs)
  sub2.clabel(CS, fontsize=9, inline=1)
  set_limits(sub2)
  sub2.set_title('f1')
  sub2.set_xlabel('x0')
  sub2.set_ylabel('x1')
  return sub1, sub2

def plot_points(sub, doe, label):
  """
  Visualize DOE
  """
  sub.plot([item[0] for item in doe], [item[1] for item in doe], '.', label=label)
  set_limits(sub)
  sub.legend()

def plot_pareto(fig, result, **kwargs):
  """
  Visualize Pareto-frontier
  """
  sub = fig.add_subplot(111)
  sub.plot([item[0] for item in result.optimal.f], [item[1] for item in result.optimal.f], '.', **kwargs)
  sub.legend()
  return sub

def print_pareto(result):
  """
  Print optimal points
  """
  log.info("Obtained optimal points")
  result.optimal.pprint(components=['x', 'f'])

def workflow():
  """
  Run example
  """
  log.info("Start execution")
  if show_plots:
    #construct contour plots
    fig = plt.figure(1)
    plot_countour(fig, DTLZ2, colors='k', label='original function')
  #generate DOE
  num_points = 10
  doe = generate_OLHS(num_points)
  #train approximator
  model = approx_function(DTLZ2, doe)
  if show_plots:
    #construct contour plots for the surrogate model
    sub1, sub2 = plot_countour(fig, model.calc, colors='r', label='approximate function')
    #represent training sample
    plot_points(sub1, doe, 'DOE, %d points' % num_points)
    plot_points(sub2, doe, 'DOE, %d points' % num_points)
  #run optimization of the surrogate model
  surrogateProblem = DTLZ2SurrogateProblem(model)
  result = optimize_problem(surrogateProblem, [])
  #represent the solution of the optimization problem
  if show_plots:
    fig2 = plt.figure(2)
    plot_pareto(fig2, result, label='pareto (surrogate model)', markersize=10, color='b')
  else:
    print_pareto(result)
  #run optimization of the original problem
  originalProblem = DTLZ2Problem()
  result = optimize_problem(originalProblem, [('GTOpt/FrontDensity', 50)])
  #represent the solution of the optimization problem
  if show_plots:
    sub = plot_pareto(fig2, result, label='pareto (original function)', markersize=5, color='r')
    #finalize plots
    fig.suptitle('Contour plot (black lines - original function, red lines - approximation)')
    fig2.suptitle('Optimizing DTLZ2 using 10 evaluations')
    sub.set_xlim((0, 1.05))
    sub.set_ylim((0, 1.05))
    log.info("Finish execution. Saving plots.")
    plt.savefig('example_joint_usage.pdf')
  else:
    print_pareto(result)
    log.info("Finish execution")

if __name__ == '__main__':
  workflow()
