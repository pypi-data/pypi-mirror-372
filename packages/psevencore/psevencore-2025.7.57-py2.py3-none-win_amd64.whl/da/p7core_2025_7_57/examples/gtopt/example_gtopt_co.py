#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Example demonstrates usage of GTOpt for multidisciplinary optimization.
It solves Sellar problem using Collaborative Optimization.
Reference: Sellar, R. S., Batill, S. M., and Renaud, J. E., "Response Surface Based, Concurrent Subspace Optimization for Multidisciplinary System Design", Proceedings References 79 of the 34th AIAA Aerospace Sciences Meeting and Exhibit, Reno, NV, January 1996.
Also see: http://openmdao.org/docs/mdao/co.html
'''

from da.p7core import gtopt
from da.p7core import loggers

import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import datetime

def calculate_residuals(targets, local_vars):
  """
  Calculate distance between targets and their local copies in the subsystems
  """
  residual = 0.0
  for (name, value) in local_vars.items():
    residual += (targets[name + '_t'] - value)**2
  return residual

class SystemLevelExampleProblem(gtopt.ProblemConstrained):
  """
  System level problem
  """
  def __init__(self):
    #counters for evaluations
    self.obj_evals = 0
    self.con_evals = 0
    #subsystem problems instances
    self.sub1problem = Subsystem1ExampleProblem(None)
    self.sub2problem = Subsystem2ExampleProblem(None)

  def prepare_problem(self):
    #history
    self.enable_history()
    #all system level variables are targets
    self.add_variable((-10.0, 10.0), None, 'z1_t')
    self.add_variable((0.0, 10.0), None, 'z2_t')
    self.add_variable((0.0, 10.0), None, 'x1_t')
    self.add_variable((3.16, 10.0), None, 'y1_t')
    self.add_variable((-10.0, 24.0), None, 'y2_t')
    #system level objective
    self.add_objective('obj')
    #feasibility constraints
    self.add_constraint((None, 0.0))
    self.add_constraint((None, 0.0))

  def define_objectives(self, v):
    print('System level: objective evaluation #%d' % self.obj_evals)
    v = dict(zip(self.variables_names(), v))
    #calculate objectives
    objective = v['x1_t']**2 + v['z2_t'] + v['y1_t'] + np.exp(-v['y2_t'])
    self.obj_evals += 1
    return objective

  def define_constraints(self, x):
    print('=' * 60)
    print('System level: constraints evaluation #%d' % self.con_evals)
    #use numerical differentiation instead of framed gradients
    options = [('GTOpt/DiffType', 'Numerical')]
    #update values of targets
    self.sub1problem.targets = dict(zip(self.variables_names(), x))
    self.sub2problem.targets = dict(zip(self.variables_names(), x))
    #run subsystems optimization
    #values of feasibility constraints are optimal subsystems objectives
    c = [optimize_problem(problem, options, loggers.LogLevel.WARN) for problem in [self.sub1problem, self.sub2problem]]
    #update counter
    self.con_evals += 1
    print('=' * 60)
    return c

class Subsystem1ExampleProblem(gtopt.ProblemUnconstrained):
  """
  Subsystem 1 problem:
  Local variable: x1
  Shared variables: z1, z2
  Coupling variable: y2
  """
  def __init__(self, targets):
    self.targets = targets
    self.evals = 0

  def prepare_problem(self):
    self.add_variable((-10.0, 10.0), None, 'z1')
    self.add_variable((0.0, 10.0), None, 'z2')
    self.add_variable((0.0, 10.0), None, 'x1')
    self.add_variable((-10.0, 24.0), None, 'y2')
    self.add_objective('obj')

  def calculate(self, v):
    #calculate response
    v = dict(zip(self.variables_names(), v))
    return v['z1']**2 + v['z2'] + v['x1'] - 0.2 * v['y2']

  def define_objectives(self, x):
    local_vars = dict(zip(self.variables_names(), x))
    local_vars['y1'] = self.calculate(x)
    self.evals += 1
    return calculate_residuals(self.targets, local_vars)

class Subsystem2ExampleProblem(gtopt.ProblemUnconstrained):
  """
  Subsystem 2 problem:
  Local variables: No
  Shared variables: z1, z2
  Coupling variable: y1
  """
  def __init__(self, targets):
    self.targets = targets
    self.evals = 0

  def prepare_problem(self):
    self.add_variable((-10.0, 10.0), None, 'z1')
    self.add_variable((0.0, 10.0), None, 'z2')
    self.add_variable((3.16, 10.0), None, 'y1')
    self.add_objective('obj')

  def calculate(self, v):
    #calculate response
    v = dict(zip(self.variables_names(), v))
    return np.sqrt(v['y1']) + v['z1'] + v['z2']

  def define_objectives(self, x):
    local_vars = dict(zip(self.variables_names(), x))
    local_vars['y2'] = self.calculate(x)
    self.evals += 1
    return calculate_residuals(self.targets, local_vars)

def optimize_problem(problem, options, level):
  """
  Run optimization of a given problem and return optimal objective value (single-objective problem is supposed)
  """
  print('Optimizing problem %s' % problem.__class__.__name__)
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger(sys.stdout, level))
  for option in options:
    optimizer.options.set(*option)
  result = optimizer.solve(problem)
  print('Problem %s was optimized successfully. Number of evaluations: %d' % (problem.__class__.__name__, problem.evals))
  print('Optimal point:')
  print('Variables: %s' % list(zip(result.names.x, result.optimal.x[0])))
  print('Objectives: %s' % list(zip(result.names.f, result.optimal.f[0])))
  return result.optimal.f[0][0]

def optimize_problem_multi(problem, options, level, output_queue):
  """
  Optimize problem and put solution to queue
  """
  output_queue.put(optimize_problem(problem, options, level))

def main():
  #measure time
  time_start = datetime.datetime.now()
  #create optimizer
  optimizer = gtopt.Solver()
  #set logger
  optimizer.set_logger(loggers.StreamLogger())
  #choose strategy for estimating derivatives
  optimizer.options.set('GTOpt/DiffType', 'Numerical')
  #create problem
  problem = SystemLevelExampleProblem()
  #solve problem
  result = optimizer.solve(problem)
  time_stop = datetime.datetime.now()
  #print various information
  print(str(result))
  print('Variables: %s' % list(zip(result.names.x, result.optimal.x[0])))
  print('Objective: %s' % result.optimal.f[0][0])
  print('Constraints: %s' % list(zip(result.names.c, result.optimal.c[0])))
  print('System level evaluations of objective: %s' % problem.obj_evals)
  print('System level evaluations of constraints: %s' % problem.con_evals)
  print('Total time elapsed: %s' % (time_stop - time_start))

  obj_hist = np.array(problem.history, dtype=float)[:, 5]
  hist = obj_hist[np.where(np.isfinite(obj_hist))]
  plot(result, hist)

def plot(result, hist):
  plt.clf()
  fig = plt.figure(1)
  ax = fig.add_subplot(111)
  x = list(range(len(hist)))
  f = hist
  ax.plot(x, f, 'b-' , label = 'Values during optimization')
  ax.plot(x[-1], result.optimal.f[0][0], 'ro' , label = 'Solution')
  ax.set_xlabel('Iter')
  ax.set_ylabel('f')
  ax.legend(loc = 'best')
  title ='Collaborative optimization'
  plt.title(title)
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

if __name__ == '__main__':
  # simple long-run warning
  from time import sleep
  print("WARNING: The execution of this example can be time consuming!")
  print("Depending on the execution environment it can takes minutes to complete.")
  print("Press Ctrl-C in 10 seconds to avoid execution...")
  sleep(10)
  print("Starting example...")

  main()
