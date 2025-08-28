#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""GTOpt python example usage."""

from da.p7core import gtopt
from da.p7core import loggers
from pprint import pprint

class UnconstrainedProblemExample(gtopt.ProblemUnconstrained):
  """
  Problem: find minimum functions f = (x - 1)^2 + 42 in interval (-inf, +inf)
  Initial guess: x_0 = 100500.
  """

  def prepare_problem(self):
    # variable x in (-inf, +inf), initial value = 100500
    self.add_variable((None, None), 100500.)
    self.add_objective()

  def define_objectives(self, x):
    return [(x[0] - 1)**2 + 42]


class TwoObjectivesUnconstrainedProblem(gtopt.ProblemUnconstrained):
  """
  Problem: find minimum functions f1 = (x-1)**2 f2 = (x+1)**2 in interval (-inf, +inf)
  Initial guess: x_0 = 1000.
  """

  def prepare_problem(self):
    # variable x in (-inf, +inf), initial value = 1000.
    self.add_variable((None, None), 1000.)
    for i in range(2):
      self.add_objective()

  def define_objectives(self, x):
    x = x[0]
    return [(x - 1)**2, (x + 1)**2]


class TwoObjectivesConstrainedProblem(gtopt.ProblemConstrained):
  """
  Problem: find minimum functions f1 = (x1 - 1)^2 + (x2 - 1)^2, f2 = (x1 + 1)^2 + (x2 + 1)^2 in interval (0, 1) x (0, 1)
           under the constraint 0. < x1 + x2 < 0.8
  Initial guess: x1_0 = 0.5,  x2_0 = 0.5
  """

  def prepare_problem(self):
    # variable x1 is in interval (0., 1.), initial value = 0.5
    self.add_variable((0., 1.), 0.5)
    self.add_variable((0., 1.), 0.5)
    self.add_constraint((0., 0.8))
    self.add_objective()
    self.add_objective()

  def define_objectives(self, x):
    return [(x[0] - 1)**2 + (x[1] - 1)**2, (x[0] + 1)**2 + (x[1] + 1)**2]

  def define_constraints(self, x):
    return [x[0] + x[1]]


class MyDistribution:
  def __init__(self, dimension, vector):
    self._dimension = dimension
    self._vector = vector
  def getNumericalSample(self, quantity):
    out = []
    for i in range(0, quantity):
      for j in range(0, self._dimension):
        out.append(self._vector[j])
    return out
  def getDimension(self):
    return self._dimension


class ConstraintSatisfactionProblemExample(gtopt.ProblemCSP):
  """
  Problem: find a point (x0, x1) that satisfies the  constraint x0 + x1 > 1
  Initial guess: x0_0 = 500.,  x1_0 = -700.
  """

  def prepare_problem(self):
    self.add_variable((None, None), 500.)
    self.add_variable((None, None), -700.)
    # there is no upper limit
    self.add_constraint((1, None))

  def define_constraints(self, x):
    return [x[0] + x[1]]


class StochasticProblemExample(gtopt.ProblemConstrained):
  """
  Problem: find minimum functions f = (x1 - k1)^2 + (x2 - k2)^2
           under the constraint -1 < x1 + x2 < 1
  Initial guess: x1_0 = -10,  x2_0 = 50
  """

  def prepare_problem(self):
    # variable x1 is in interval (0., 1.), initial guess is 0.5
    self.add_variable((-1000.0, 10.0), -10.0, 'x1')
    self.add_variable((-10.0, 1000.0), 50.0, 'x2')
    self.add_constraint((-1.0, 1.0), 'c')
    self.add_objective('f')
    self.set_stochastic(MyDistribution(4, [-2.0, -1.0, 1.0, 0.5]))

  def define_objectives(self, x):
    ksi = x[2:]
    return [(x[0] - ksi[0])**2 + (x[1] - ksi[1])**2]

  def define_constraints(self, x):
    return [x[0] + x[1]]


class CustomWatcher(object):
  """
  Watcher is an object that is capable of interrupting a process.
  Define watcher to check intermediate results and terminate optimization.
  """

  def __call__(self, obj):
    return True

def trivial_example():
  # create optimizer with default parameters
  optimizer = gtopt.Solver()
  # create problem
  problem = UnconstrainedProblemExample()
  print(str(problem))
  # solve problem and get result
  result = optimizer.solve(problem)
  # print general info about result
  print(str(result))
  # print optimal points
  print("Optimal answer:")
  result.optimal.pprint()

def trivial_example_two():
  optimizer = gtopt.Solver()
  # it set optimization stop criteria
  # look documentation for details
  optimizer.options.set("GTOpt/ObjectiveTolerance", "0.1")
  problem = TwoObjectivesUnconstrainedProblem()
  print(str(problem))
  result = optimizer.solve(problem)
  print(str(result))
  print("Optimal answer:")
  result.optimal.pprint()

def advanced_example():
  optimizer = gtopt.Solver()
  # set logger, by default output -- to sys.stdout
  optimizer.set_logger(loggers.StreamLogger())
  # set watcher
  optimizer.set_watcher(CustomWatcher())

  # work with options
  print("Options list:")
  pprint(optimizer.options.list)
  print("")
  optionname = 'GTOpt/FrontDensity'
  print('Option: %s' % optionname)
  print('Info: %s' % optimizer.options.info(optionname))
  optimizer.options.set(optionname, "5")
  print('New value: %s' % optimizer.options.get(optionname))
  optimizer.options.reset()
  print('After reset: %s' % optimizer.options.get(optionname))
  print("")
  optimizer.options.set(optionname, "15")

  problem = TwoObjectivesConstrainedProblem()
  print(str(problem))
  result = optimizer.solve(problem)
  print(str(result))
  print('Optimal points:')
  result.optimal.pprint()

def constraint_example():
  optimizer = gtopt.Solver()
  problem = ConstraintSatisfactionProblemExample()
  result = optimizer.solve(problem)
  print(str(result))
  print("Found point:")
  result.optimal.pprint()

def stochastic_example():
  optimizer = gtopt.Solver()
  optimizer.options.set("GTOpt/ObjectiveTolerance", "0.1")
  problem = StochasticProblemExample()
  print(str(problem))
  result = optimizer.solve(problem)
  print(str(result))
  print('Optimal point:')
  result.optimal.pprint(components=['x', 'f', 'c', 'fe', 'ce', 'psi'])

def main():
  """Example of GTOpt usage."""

  print('Find the minimum of function')
  print('=' * 60)
  trivial_example()
  print('=' * 60)
  print('Finished!')
  print('')

  print('Find the minimum of two functions')
  print('=' * 60)
  trivial_example_two()
  print('=' * 60)
  print('Finished!')
  print('')

  print('Find the minimum of functions with constraint')
  print('=' * 60)
  advanced_example()
  print('=' * 60)
  print('Finished!')
  print('')

  print('Find a point satisfying the constraint')
  print('=' * 60)
  constraint_example()
  print('=' * 60)
  print('Finished!')
  print('')

  print('Stochastic problem example')
  print('=' * 60)
  stochastic_example()
  print('=' * 60)
  print('Finished!')
  print('')

if __name__ == "__main__":
  main()
