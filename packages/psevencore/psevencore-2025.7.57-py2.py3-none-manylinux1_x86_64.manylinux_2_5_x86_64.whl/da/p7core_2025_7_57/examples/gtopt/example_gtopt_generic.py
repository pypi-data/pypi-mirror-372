#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Example of using generic problem definition in GTOpt python interface"""

from da.p7core import gtopt
from da.p7core import loggers

import matplotlib.pyplot as plt

import sys
import os

class TP7GenericProblemExample(gtopt.ProblemGeneric):
  """
  Problem TP7 - constrained multi-objective problem without analytic gradients:
  minimize:    f0 = x0, f1 = (1 + x1) / x0
  where:       0.1 < x0 < 1
               0 < x1 < 0.5
  subject to:  x1 + 9 * x0 - 6 > 0
              -x1 + 9 * x0 - 1 > 0
  """

  def prepare_problem(self):
    #for variables and constraints names are not set - they will be named automatically: (x0, x1, ...), (c0, c1, ...)
    #define variables: bounds are specified, initial guess is not set
    self.add_variable((0.1, 1.0), None)
    self.add_variable((0.0, 0.5), None)
    #define constraints: lower bounds are specified, upper bounds are not set (will be interpreted as positive infinity)
    self.add_constraint((0.0, None))
    self.add_constraint((0.0, None))
    #define 2 objectives: names are set
    self.add_objective("first_objective")
    self.add_objective("second_objective")

  def evaluate(self, queryx, querymask):
    """
    Batch mode is supported in generic problem definition, i.e. optimizer may ask several points.
    Masks are supported - optimizer specifies required responses, user must give at least these responses.

    In this example, regardless of mask, all responses (all objectives and constraints) are calculated.
    All points in batch are calculated sequentially and in the same way.
    """
    #functions_batch will be filled with lists of outputs
    functions_batch = []
    #output_masks_batch will be filled with lists of output masks
    output_masks_batch = []
    #queryx is a 2D array, x is a point to evaluate
    #querymask is a list of lists, mask marks with by nonzero values required responses
    for x, mask in zip(queryx, querymask):
      #calculate objectives
      objectives = []
      objectives.append(x[0] if mask[0] else None)
      objectives.append((1 + x[1]) / x[0] if mask[1] else None)
      #calculate constraints
      constraints = []
      constraints.append(x[1] + 9 * x[0] - 6 if mask[2] else None)
      constraints.append(-x[1] + 9 * x[0] - 1 if mask[3] else None)
      #add responses to list
      functions_batch.append(objectives + constraints)
      # this example calculates only those responses that were requested by the input mask,
      # so it should return exactly the same mask
      output_mask = mask
      output_masks_batch.append(output_mask)
    return functions_batch, output_masks_batch

class TP7GenericProblemWithGradientsExample(gtopt.ProblemGeneric):
  """
  Problem TP7 - constrained multi-objective problem with analytic gradients:
  minimize:    f0 = x0, f1 = (1 + x1) / x0
  where:       0.1 < x0 < 1
               0 < x1 < 0.5
  subject to:  x1 + 9 * x0 - 6 > 0
              -x1 + 9 * x0 - 1 > 0

  objectives Jacobian: (      1             0  )
                       (-(1 + x1)/(x0^2)   1/x0)

  constraints Jacobian: (9   1)
                        (9  -1)
  """

  def prepare_problem(self):
    #for variables and constraints names are not set - they will be named automatically: (x0, x1, ...), (c0, c1, ...)
    #define variables: bounds are specified, initial guess is not set
    self.add_variable((0.1, 1.0), None)
    self.add_variable((0.0, 0.5), None)
    #define constraints: lower bounds are specified, upper bounds are not set (will be interpreted as positive infinity)
    self.add_constraint((0.0, None))
    self.add_constraint((0.0, None))
    #define 2 objectives: names are set
    self.add_objective("first_objective")
    self.add_objective("second_objective")
    """
    turn on analytic objectives gradient
    objectives gradient is sparse: non-zero elements are (0, 0), (1, 0), (1, 1)
    we need to specify non-zero rows and columns in Jacobian
    rows are (0, 1, 1), columns are (0, 0, 1)
    """
    self.enable_objectives_gradient(([0, 1, 1], [0, 0, 1]))
    """
    turn on analytic constraints gradient
    constraints gradient is dense - all values are non-zero
    respectively, no parameter is needed
    """
    self.enable_constraints_gradient()

  def evaluate(self, queryx, querymask):
    """
    Batch mode is supported in generic problem definition, i.e. optimizer may ask several points.
    Masks are supported - optimizer specifies required responses, user must give at least these responses.

    All points in batch are calculated sequentially and in the same way.
    List with responses has the following structure: [objectives, constraints, objectives gradients, constraints gradients]
    It's length is equal to 11 = 2 + 2 + 3 + 4
    Here, if optimizer asks for at least one response of the corresponding type, all responses of this type are calculated
    """
    #functions_batch will be filled with lists of outputs
    functions_batch = []
    #output_masks_batch will be filled with lists of output masks
    output_masks_batch = []
    #queryx - list of lists, x - list with values of input variables
    #querymask - list of lists, mask - list of required responses
    for x, mask in zip(queryx, querymask):
      output_mask = []
      #calculate objectives required by mask
      objectives = [None] * 2
      if mask[0]:
        objectives[0] = x[0]
      if mask[1]:
        objectives[1] = (1 + x[1]) / x[0]

      #calculate constraints required by mask
      constraints = [None] * 2
      if mask[2]:
        constraints[0] = x[1] + 9 * x[0] - 6
      if mask[3]:
        constraints[1] = -x[1] + 9 * x[0] - 1

      #calculate non-zero elements of objectives Jacobian (the order of partial derivatives should be same as in input of enable_objectives_gradient)
      objectives_gradient = [None] * 3
      if mask[4]:#df0/dx0
        objectives_gradient[0] = 1.0
      if mask[5]:#df1/dx0
        objectives_gradient[1] = -(1 + x[1]) / x[0]**2
      if mask[6]:#df1/dx1
        objectives_gradient[2] = 1 / x[0]

      #calculate all elements of constraints Jacobian demanded by the mask. The order is dc_1/dx_1 dc_1/dx_2 dc_2/dx_1 dc_2/dx_2
      constraints_gradient = [None] * 4
      if mask[7]:#dc0/dx0
        constraints_gradient[0] = 9
      if mask[8]:#dc0/dx1
        constraints_gradient[1] = 1
      if mask[9]:#dc1/dx0
        constraints_gradient[2] = 9
      if mask[10]:#dc1/dx1
        constraints_gradient[3] = -1
      #add responses to list
      functions_batch.append(objectives + constraints + objectives_gradient + constraints_gradient)
      #add mask to list
      output_masks_batch.append(mask) #In this example we calculate only what is requested by an incoming mask, so we should return exactly the incoming mask
    return functions_batch, output_masks_batch

def solve_problem(problem):
  #create optimizer instance
  optimizer = gtopt.Solver()
  # set logger
  optimizer.set_logger(loggers.StreamLogger(sys.stdout, loggers.LogLevel.DEBUG))
  #set options
  options = []
  options.append(('GTOpt/LogLevel', 'WARN'))
  options.append(('GTOpt/FrontDensity', 8))
  for option in options:
    optimizer.options.set(*option)
  #print information about problem
  print(str(problem))

  #here the problem is solving
  result = optimizer.solve(problem)

  #print solution
  print(str(result))
  print('Optimal points:')
  result.optimal.pprint()
  return result

def plot(result):
  plt.clf()
  fig = plt.figure(1)
  ax = fig.add_subplot(111)
  ax.axis('off')
  title = 'TP7 Generic Solution: case of numerical gradients'
  plt.title(title)
  axv = [fig.add_subplot(211), fig.add_subplot(212)]
  for i in range(2):
    x1 = [x[0] for x in result[i].optimal.f]
    x2 = [x[1] for x in result[i].optimal.f]
    axv[i].plot(x1, x2, 'bo', label = 'Pareto Frontier')
    axv[i].legend(loc = 'best')
    if i == 1:
      title = 'TP7 Generic Solution: case of analytical gradients'
      plt.title(title)
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  result = []
  for problem in [TP7GenericProblemExample(), TP7GenericProblemWithGradientsExample()]:
    print('=' * 60)
    print('Solve problem %s' % problem.__class__.__name__)
    result.append(solve_problem(problem))
  plot(result)
  print('Finished!')
  print('=' * 60)

if __name__ == "__main__":
  main()
