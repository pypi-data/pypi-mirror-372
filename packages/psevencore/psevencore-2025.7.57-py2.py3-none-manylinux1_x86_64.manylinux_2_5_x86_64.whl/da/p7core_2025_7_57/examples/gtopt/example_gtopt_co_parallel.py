#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
This example provides a use-case for options GTOpt/MaxParallel and GTOpt/ResponsesScalability.
These options are intended to be used on multiprocessor systems to reduce overall time consumed
on optimization.

GTOpt/MaxParallel directs the GTOpt optimizer how to parallel its internal routines.

GTOpt/ResponsesScalability is related to parallelization that can be done for evaluation optimized
responses (constraints and/or objectives) and tells the pSeven Core optimizer to match actual evaluations
batches to be multiple of desire parallelization. This options, however, efficiently works only in
expensive and/or stochastic problems. The correct use of this options supposes that responses for
different designs are calculated independently and can be solved simultaneously while solving of
each responses problem cannot be efficiently parallelized or have natural parallelization limits.
For example, we have machine with 2 physical 2-cores processors.

Here we consider collaborative optimization problem in which optimization problem has expensive
constraints thus to evaluate when we need to solve others optimization problems. The optimization
subproblems have cheap responses and can not be parallelized.

We create optimization problem that can run evaluation of its constrains in parallel
processes using Python multiprocessing library. And then we provide this information
to the pSeven optimizer using GTOpt/ResponsesScalability and GTOpt/MaxParallel options.

Note this example is incompatible with Python 2.5 due to usage of the 'multiprocessing'
Python library implemented since Python 2.6.
'''
import os
import sys
import numpy

from datetime import datetime
from time import sleep

from da.p7core import gtopt
from da.p7core import loggers

PROCESSORS_NUMBER = 2 # The number of physical processors on our imaginary test machine.
CORES_NUMBER = 4 # The number of each physical processor cores

def main():
  # Create optimizer object
  optimizer = gtopt.Solver()

  # Set console logger
  optimizer.set_logger(loggers.StreamLogger())

  # Create problem description object.
  problem = SystemLevelExampleProblem()

  # Solve problem and measure the time elapsed
  time_start = datetime.now()
  # Considering our problem is using all available cores for parallel evaluation of
  # the sequentially calculated constrains, while gtopt.Solver cannot effectively
  # parallelize itself across different physical processors.
  result = optimizer.solve(problem, options = {'GTOpt/GlobalPhaseIntensity': 0.,
                                               'GTOpt/MaximumExpensiveIterations': 400,
                                               'GTOpt/ResponsesScalability': PROCESSORS_NUMBER * CORES_NUMBER,
                                               'GTOpt/MaxParallel': CORES_NUMBER
                                               })
  time_finish = datetime.now()

  # Print solution and some extras
  print(result)
  print('-'*80)
  if result.optimal.x.size:
    print('Variables:   %s' % ', '.join('%s=%g' % (name, val) for name, val in zip(result.names.x, result.optimal.x[0])))
    print('Objective:   %g' % result.optimal.f[0][0])
    print('Constraints: %s' % ', '.join('%s=%g' % (name, val) for name, val in zip(result.names.c, result.optimal.c[0])))
  else:
    print('Optimal solution is not found.')
  print('The number of system level define_constraints_batch() calls: %d' % problem.con_evals)
  print('Total time elapsed: %s' % (time_finish - time_start))

  # Plot solution
  plot(result, problem.objectives, problem.constraints)

try:
  from multiprocessing import Pool
except ImportError:
  print("ERROR: the 'multiprocessing' library is required for this example.")
  exit()

class SystemLevelExampleProblem(gtopt.ProblemConstrained):
  """
  System level problem with extremely expensive constraints
  """
  def prepare_problem(self):
    # Add variables
    self.add_variable((-10.0, 10.0), None, 'z1_t')
    self.add_variable((0.0, 10.0), None, 'z2_t')
    self.add_variable((0.0, 10.0), None, 'x1_t')
    self.add_variable((3.16, 10.0), None, 'y1_t')
    self.add_variable((-10.0, 24.0), None, 'y2_t')

    # Add system level objective
    self.add_objective('obj')

    # Add feasibility constraints
    self.add_constraint((None, 0.0), hints={'@GTOpt/EvaluationCostType': 'Expensive'})
    self.add_constraint((None, 0.0), hints={'@GTOpt/EvaluationCostType': 'Expensive'})

    # Pool of processes for parallel constraints evaluation.
    # Considering each particular evaluation is sequential,
    # so it is worth to use all available cores.
    # You can set self.pool to None or even comment this line out
    # to switch to the sequential mode
    self.pool = Pool(PROCESSORS_NUMBER * CORES_NUMBER)

    # We are going to use custom evaluations history.
    self.disable_history()

    # Helper dictionary that maps variables name to its indices.
    self.var_map = dict((var_name, var_index) for var_index, var_name in enumerate(self.variables_names()))

    # Custom history holders.
    self.con_evals = 0 # evaluations counter
    self.objectives = [] # objectives history
    self.constraints = [] # constraints history

  @staticmethod
  def define_constraints(targets):
    """
    Implements constraints evaluation by solving optimization problems.
    """
    constraints = []
    for subproblem_type in (Subsystem1ExampleProblem, Subsystem2ExampleProblem):
      print('Optimizing problem %s' % subproblem_type.__name__)
      sys.stdout.flush()

      subproblem = subproblem_type(targets)
      subproblem_result = gtopt.Solver().solve(subproblem, options={'GTOpt/GlobalPhaseIntensity': 1.,
                                                                  'GTOpt/Techniques': '[RL]',
                                                                  'GTOpt/MaxParallel': 1}) # Let us solve problem in the sequential way
      constraints.append(subproblem_result.optimal.f[0][0])

      print('Problem %s was optimized successfully. Number of evaluations: %d' % (subproblem_type.__name__, subproblem.evals))
      print('Optimal point:')
      print('  Variables: %s' % ', '.join('%s=%g' % (name, val) for name, val in zip(subproblem_result.names.x, subproblem_result.optimal.x[0])))
      print('  Objective: %g' % subproblem_result.optimal.f[0][0])
      sys.stdout.flush()

    return constraints

  def define_objectives_batch(self, v):
    return v[:, self.var_map['x1_t']]**2 + v[:, self.var_map['z2_t']] + v[:, self.var_map['y1_t']] + numpy.exp(-v[:, self.var_map['y2_t']])

  def define_constraints_batch(self, x):
    print('=' * 60)
    print('System level: define_constraints_batch() evaluation #%d' % self.con_evals)
    print('=' * 60)

    targets_list = [dict(zip(self.variables_names(), v)) for v in x]

    if getattr(self, 'pool', None) is not None:
      # Evaluate constraints in parallel.
      # Due to the multiprocessing module limitations in Python 2.x
      # we cannot directly map SystemLevelExampleProblem.define_constraints
      # function and must use module-level proxy function 'evaluate_constraints'.
      constraints = self.pool.map(evaluate_constraints, targets_list)
    else:
      # sequential constraints evaluation
      constraints = [evaluate_constraints(target) for target in targets_list]

    self.constraints += constraints

    # Evaluate objective for history purpose. The real-world problem should not do it.
    self.objectives += self.define_objectives_batch(x).tolist()
    self.con_evals += 1 #update counter

    return constraints

def evaluate_constraints(targets):
  """
  Proxy-function for redirecting constraints evaluation to the SystemLevelExampleProblem problem
  """
  return SystemLevelExampleProblem.define_constraints(targets)

def calculate_residuals(targets, local_vars):
  """
  Helper function calculating distance between targets and their local copies in the subsystems
  """
  residual = 0.0
  for (name, value) in local_vars.items():
    residual += (targets[name + '_t'] - value)**2
  return residual


class Subsystem1ExampleProblem(gtopt.ProblemUnconstrained):
  """
  Subsystem 1 problem:
  Local variable: x1
  Shared variables: z1, z2
  Coupling variable: y2
  """
  def __init__(self, targets):
    self.targets = targets

  def prepare_problem(self):
    # problem definition
    self.disable_history()
    self.add_variable((-10.0, 10.0), None, 'z1')
    self.add_variable((0.0, 10.0), None, 'z2')
    self.add_variable((0.0, 10.0), None, 'x1')
    self.add_variable((-10.0, 24.0), None, 'y2')
    self.add_objective('obj')

    # Helper dictionary that maps variables name to its indices.
    self.var_map = dict((var_name, var_index) for var_index, var_name in enumerate(self.variables_names()))

    # Helper evaluations counter
    self.evals = 0

  def calculate(self, v):
    # calculate response
    return v[self.var_map['z1']]**2 + v[self.var_map['z2']] + v[self.var_map['x1']] - 0.2 * v[self.var_map['y2']]

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

  def prepare_problem(self):
    # problem definition
    self.disable_history()
    self.add_variable((-10.0, 10.0), None, 'z1')
    self.add_variable((0.0, 10.0), None, 'z2')
    self.add_variable((3.16, 10.0), None, 'y1')
    self.add_objective('obj')

    # Helper dictionary that maps variables name to its indices.
    self.var_map = dict((var_name, var_index) for var_index, var_name in enumerate(self.variables_names()))

    # Helper evaluations counter
    self.evals = 0

  def calculate(self, v):
    #calculate response
    return numpy.sqrt(v[self.var_map['y1']]) + v[self.var_map['z1']] + v[self.var_map['z2']]

  def define_objectives(self, x):
    local_vars = dict(zip(self.variables_names(), x))
    local_vars['y2'] = self.calculate(x)
    self.evals += 1
    return calculate_residuals(self.targets, local_vars)

def plot(result, hist_obj, hist_con):
  """
  Helper function for optimization history plotting
  """
  try:
    import matplotlib.pyplot as plt
    plt.clf()
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    x = list(range(len(hist_obj)))
    f = hist_obj
    c = numpy.array(hist_con).max(axis=1)
    ax.plot(x, f, 'b-' , label = 'Values during optimization')
    ax.plot(x, c, 'r.' , label = 'Cons during optimization')
    if result.optimal.f.size:
      ax.plot(x[-1], result.optimal.f[0][0], 'go' , label = 'Solution')
    ax.set_xlabel('Iter')
    ax.set_ylabel('f')
    ax.legend(loc = 'best')
    title ='Collaborative optimization'
    plt.title(title)

    # Python 2/3 compatibility workaround
    try:
      filename = os.path.join(os.getcwdu(), title)
    except AttributeError:
      filename = os.path.join(os.getcwd(), title)

    fig.savefig(filename)
    print('Plots are saved to %s.png' % filename)

    if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
      plt.show()
  except ImportError:
    print("WARNING: Plotting is disabled because matplotlib library is absent.")

if __name__ == '__main__':
  print("WARNING: The execution of this example can be time consuming!")
  print("Depending on the execution environment it can takes minutes to complete.")
  print("Press Ctrl-C in 10 seconds to avoid execution...")
  sleep(10)
  print("Starting example...")
  main()
