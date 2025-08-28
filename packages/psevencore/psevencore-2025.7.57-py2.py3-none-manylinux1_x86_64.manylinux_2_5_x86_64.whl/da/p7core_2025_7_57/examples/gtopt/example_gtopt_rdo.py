#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Example demonstrates usage of GTOpt for Robust Optimization.
It solves chance-constrained programming problem:

minimize f
s.t.
Pr{zeta1 * x1 + zeta2 * x2 + zeta3 * x3 + f >= 0} >= 0.9
Pr{eta1 * x1^2 + eta2 * x2^2 + eta3 * x3^2 <= 8} >= 0.8
x1,x2,x3 >= 0

In this example for solving the problem, common random numbers variance reduction technique is used (i.e. a random generator with controllable state is required).
'''

from da.p7core import gtopt
from da.p7core import loggers

from pprint import pprint
import random
random.seed(0)

class ExampleDistribution:
  def getNumericalSample(self, quantity):
    out = []
    for i in range(0, quantity):
      ksi = [random.uniform(1.0, 2.0),
              random.normalvariate(1.0, 1.0),
              random.expovariate(1.0),
              random.uniform(2.0, 3.0),
              random.normalvariate(2.0, 1.0),
              random.expovariate(2.0)]
      out.extend(ksi)
    return out
  def getDimension(self):
    return 6


class ChanceConstrainedExampleProblem(gtopt.ProblemConstrained):
  def prepare_problem(self):
    #add one objective
    self.add_objective()
    #add x1,x2,x3 >= 0
    for _ in range(3):
      self.add_variable((0.0, None))
    #add variable without bounds
    self.add_variable((None, None))
    #add chance constraints
    self.add_constraint((0.0, None), hints = {'@GTOpt/ConstraintType' : 'ChanceConstraint', '@GTOpt/ConstraintAlpha' : '0.1'})
    self.add_constraint((None, 8.0), hints = {'@GTOpt/ConstraintType' : 'ChanceConstraint', '@GTOpt/ConstraintAlpha' : '0.2'})
    #add 6 random variables: uniform(1,2), normal(1,1), exp(1), uniform(2,3), normal(2,1), exp(2)
    self.set_stochastic(ExampleDistribution())

  def define_constraints(self, x):
    c = [0] * 2
    zeta = x[4:7]
    c[0] = zeta[0] * x[0] + zeta[1] * x[1] + zeta[2] * x[2] + x[3]
    eta = x[7:10]
    c[1] = eta[0] * x[0] * x[0] + eta[1] * x[1] * x[1] + eta[2] * x[2] * x[2]
    return c

  def define_objectives(self, x):
    return x[3]

def main():
  #create optimizer
  optimizer = gtopt.Solver()
  #set logger
  optimizer.set_logger(loggers.StreamLogger())
  #create problem
  problem = ChanceConstrainedExampleProblem()
  #print information about problem
  print(str(problem))
  #optimize problem
  result = optimizer.solve(problem)
  #print information about the result
  print(str(result))
  #print optimal values
  print('optimal values:')
  result.optimal.pprint(components=['x', 'f', 'c', 'fe', 'ce', 'psi'])

if __name__ == '__main__':
  main()

