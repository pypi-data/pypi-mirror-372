#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Example demonstrates usage of GTOpt for multidisciplinary optimization.
It solves geometric programming problem using Analytical Target Cascading.
Reference: Kim, H.M., Target cascading in optimal system design, 2001, The University of Michigan
(See Chapter 5: Demonstration Studies)

WARNING: The execution of this example can be time consuming!
'''

from da.p7core import gtopt
from da.p7core import loggers

import sys
import math
import datetime
import numpy as np
from pprint import pprint

class SystemLevelExampleProblem(gtopt.ProblemConstrained):
  """
  System level problem:
  Responses: x01, x02
  Local variables: x04, x05, x07
  Linking variables: No
  Responses from lower level: x03, x06
  """
  def __init__(self, l):
    #initialize responses from lower level
    self.l = l
    #counter for number of evaluations
    self.evals = 0

  def prepare_problem(self):
    self.add_variable((1.0e-5, None), None, 'x03')
    self.add_variable((1.0e-5, None), None, 'x04')
    self.add_variable((1.0e-5, None), None, 'x05')
    self.add_variable((1.0e-5, None), None, 'x06')
    self.add_variable((1.0e-5, None), None, 'x07')
    self.add_variable((1.0e-5, None), None, 'x11')
    #target deviation tolerances
    self.add_variable((0.0, None), None, 'eps1')
    self.add_variable((0.0, None), None, 'eps2')
    self.add_variable((0.0, None), None, 'eps3')
    #deviation constraints
    self.add_constraint((None, 0.0), 'eps1_constr')
    self.add_constraint((None, 0.0), 'eps2_constr')
    self.add_constraint((None, 0.0), 'eps3_constr')
    #analysis model constraints
    self.add_constraint((None, 1.0), 'g1')
    self.add_constraint((None, 1.0), 'g2')
    self.add_objective('obj')

  def calculate(self, var):
    #calculate responses
    return {'x01': math.sqrt(var['x03']**2 + var['x04']**(-2) + var['x05']**2), 'x02': math.sqrt(var['x05']**2 + var['x06']**2 + var['x07']**2)}

  def define_objectives(self, var):
    #calculate objective function
    #objective function of the problem is x01^2 + x02^2
    #upper bounds of additional deviation constraints are also to be minimized
    #so, they are appended to the objective with some weights
    var = dict(zip(self.variables_names(), var))
    local = self.calculate(var)
    self.evals += 1
    return local['x01']**2 + local['x02']**2 + 500.0 * (var['eps1'] + var['eps2'] + var['eps3'])

  def define_constraints(self, var):
    var = dict(zip(self.variables_names(), var))
    con = {}
    #calculate deviation constraints
    con['eps1_constr'] = (var['x11'] - self.l['x11_1'])**2 + (var['x11'] - self.l['x11_2'])**2 - var['eps1']
    con['eps2_constr'] = (var['x03'] - self.l['x03'])**2 - var['eps2']
    con['eps3_constr'] = (var['x06'] - self.l['x06'])**2 - var['eps3']
    #calculate analysis model constraints
    con['g1'] = (var['x03']**(-2) + var['x04']**2) / var['x05']**2
    con['g2'] = (var['x05']**2 + var['x06']**(-2)) / var['x07']**2
    return [con[k] for k in self.constraints_names()]

class Subsystem1ExampleProblem(gtopt.ProblemConstrained):
  """
  Subsystem 1 problem:
  Response: x03
  Local variables: x08, x09, x10
  Linking variable: x11
  """
  def __init__(self, targets):
    #targets for responses and linking variables
    self.targets = targets
    #counter for number of evaluations
    self.evals = 0

  def prepare_problem(self):
    for i in range(8, 12):
      self.add_variable((1.0e-5, None), None, 'x%02d' % (i))
    self.add_constraint((None, 1.0), 'g3')
    self.add_constraint((None, 1.0), 'g4')
    self.add_objective()

  def calculate(self, var):
    #calculate response
    return math.sqrt(var['x08']**2 + var['x09']**(-2) + var['x10']**(-2) + var['x11']**2)

  def define_objectives(self, var):
    var = dict(zip(self.variables_names(), var))
    responses = {}
    responses['x03'] = self.calculate(var)
    self.evals += 1
    #calculate deviation
    return (responses['x03'] - self.targets['x03'])**2 + (var['x11'] - self.targets['x11'])**2

  def define_constraints(self, var):
    var = dict(zip(self.variables_names(), var))
    con = {}
    con['g3'] = (var['x08']**2 + var['x09']**2) / var['x11']**2
    con['g4'] = (var['x08']**(-2) + var['x10']**2) / var['x11']**2
    return [con[k] for k in self.constraints_names()]

class Subsystem2ExampleProblem(gtopt.ProblemConstrained):
  """
  Subsystem 2 problem:
  Response: x06
  Local variables: x12, x13, x14
  Linking variable: x11
  """
  def __init__(self, targets):
    #targets for responses and linking variables
    self.targets = targets
    #counter for number of evaluations
    self.evals = 0

  def prepare_problem(self):
    for i in range(11, 15):
      self.add_variable((1.0e-5, None), None, 'x' + str(i))
    self.add_constraint((None, 1.0), 'g5')
    self.add_constraint((None, 1.0), 'g6')
    self.add_objective(())

  def calculate(self, var):
    #calculate response
    return math.sqrt(var['x11']**2 + var['x12']**2 + var['x13']**2 + var['x14']**2)

  def define_objectives(self, var):
    var = dict(zip(self.variables_names(), var))
    responses = {}
    responses['x06'] = self.calculate(var)
    self.evals += 1
    #calculate deviation
    return (responses['x06'] - self.targets['x06'])**2 + (var['x11'] - self.targets['x11'])**2

  def define_constraints(self, var):
    var = dict(zip(self.variables_names(), var))
    con ={}
    con['g5'] = (var['x11']**2 + var['x12']**(-2)) / var['x13']**2
    con['g6'] = (var['x11']**2 + var['x12']**2) / var['x14']**2
    return [con[k] for k in self.constraints_names()]

def optimize_problem(problem, options, level):
  """
  Run optimization of a given problem and return first point from the solution
  (for the single-objective optimization there is the only point in the solution).
  """
  print('Optimizing problem %s' % problem.__class__.__name__)
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger(sys.stdout, level))
  for option in options:
    optimizer.options.set(*option)
  result = optimizer.solve(problem)
  print('Problem %s was optimized successfully. Number of evaluations: %d' % (problem.__class__.__name__, problem.evals))
  problem.evals = 0
  print('Optimal point:')
  print('Variables: %s' % result.optimal.x[0])
  print('Objectives: %s' % result.optimal.f[0])
  print('Constraints: %s' % result.optimal.c[0])
  optimalArray = np.concatenate((result.optimal.x[0], result.optimal.f[0], result.optimal.c[0]))
  return dict(zip(result.names.x + result.names.f + result.names.c, optimalArray))

def optimize_problem_multi(problem, options, level, output_queue):
  """
  Optimize problem and put solution to queue
  """
  output_queue.put(optimize_problem(problem, options, level))

def atc_flow(max_iterations, tolerance):
  #measure time
  time_start = datetime.datetime.now()
  #initial values for variables passed from lower (subsystem) level to upper (system) level
  to_upper = {'x11_1' : 1.0, 'x11_2' : 1.0, 'x03' : 1.0, 'x06' : 1.0}
  #create problem instances
  problem_system = SystemLevelExampleProblem(to_upper)
  problem_subsystem1 = Subsystem1ExampleProblem(None)
  problem_subsystem2 = Subsystem2ExampleProblem(None)
  #numerical differentiation will be used instead of framed gradients
  options = [('GTOpt/DiffType', 'Numerical')]
  history = []
  for i in range(max_iterations):
    print("=" * 60)
    print('Iteration #%d' % i)
    #solve system level problem
    to_lower = optimize_problem(problem_system, options, loggers.LogLevel.WARN)
    history.append(to_lower['obj'])
    print('Check termination criteria')
    if math.fabs(history[i] - history[i-1]) < tolerance and i > 0:
      print('Terminate target cascading')
      break
    #pass optimal values to subsystem level
    problem_subsystem1.targets = to_lower
    problem_subsystem2.targets = to_lower
    #solve subsystem level problems
    ss1_vars, ss2_vars = [optimize_problem(problem, options, loggers.LogLevel.WARN) for problem in [problem_subsystem1, problem_subsystem2]]
    #pass optimal values to system level
    to_upper = {'x11_1' : ss1_vars['x11'], 'x11_2' : ss2_vars['x11'], 'x03' : problem_subsystem1.calculate(ss1_vars), 'x06' : problem_subsystem2.calculate(ss2_vars)}
    problem_system.l = to_upper
    print("=" * 60)
  time_stop = datetime.datetime.now()
  #print various information
  print('History of optimal values:')
  pprint (history)
  optimal_design = problem_system.calculate(to_lower)

  optimal_design.update({k : v for k, v in ss1_vars.items() if k.startswith('x')})
  optimal_design.update({k : v for k, v in ss2_vars.items() if k.startswith('x')})
  optimal_design.update({k : v for k, v in to_lower.items() if k.startswith('x')})

  print('Optimal design: ')
  for k in sorted(optimal_design.keys()):
    print("%s %s" % (k, optimal_design[k]))
  print('Total time elapsed: %s' % (time_stop - time_start))

if __name__ == '__main__':
  # simple long-run warning
  from time import sleep
  print("WARNING: The execution of this example can be time consuming!")
  print("Depending on the execution environment it can takes minutes to complete.")
  print("Press Ctrl-C in 10 seconds to avoid execution...")
  sleep(10)
  print("Starting example...")

  atc_flow(1000, 2.0e-4)


