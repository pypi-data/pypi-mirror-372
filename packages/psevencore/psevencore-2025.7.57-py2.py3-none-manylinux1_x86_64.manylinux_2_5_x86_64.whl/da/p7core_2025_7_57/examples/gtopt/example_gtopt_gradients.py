#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Example of using generic problem definition with analytical gradients in GTOpt python interface"""

from da.p7core import gtopt
from da.p7core import loggers

import matplotlib.pyplot as plt

import os

class SimpleProblem(gtopt.ProblemGeneric):
  """
  minimize:    f1 = x0, f2 = (1 + x1) / x0
  where:       0.1 < x0 < 1
               0 < x1 < 0.5
  """
  def prepare_problem(self):
    # 2 variables
    self.add_variable((0.1, 1.0), None)
    self.add_variable((0.0, 0.5), None)
    # 2 objectives
    self.add_objective()
    self.add_objective()
    # dense objectives jacobian
    self.enable_objectives_gradient()

  def evaluate(self, queryx, querymask):
    batch_f = []
    batch_mask = []
    for x, mask in zip(queryx, querymask):
      responses, output_mask = self.eval_single(x, mask)
      batch_f.append(responses)
      batch_mask.append(output_mask)
    return batch_f, batch_mask

  def eval_single(self, x, mask):
    # The order of responses here is
    # f dim = 2
    # c dim = 0
    # f gradients 2 * 2
    # c gradients 0 * 2

    output_mask = [False] * len(mask)
    f = [None] * 2
    grads = [None] * 4

    if any(mask[:2]): # We suppose that we can not separate objectives computation.
      f = self.eval_objectives(x) # We provide them both always
      output_mask[:2] = [True] * 2 #and may extended mask sometimes.

    if any(mask[2:]): #  Each gradient entry has a separate mask, but as above we assume that we can not avoid simultaneous computation of Jacobian,
                      #  we provide all values at once and may extend the mask.
      grads = sum(self.eval_gradients(x), [])
      output_mask[2:] = [True] * 4

    return f + grads, output_mask

  def eval_objectives(self, x):
    objectives = [None, None]
    objectives[0] = x[0]
    objectives[1] = (1 + x[1]) / x[0]
    return objectives

  def eval_gradients(self, x):
    objectives_gradient = [[None, None], [None, None]]
    objectives_gradient[0][0] = 1.0
    objectives_gradient[0][1] = 0.0
    objectives_gradient[1][0] = -(1 + x[1]) / x[0]**2
    objectives_gradient[1][1] = 1 / x[0]
    return objectives_gradient

def plot(result):
  plt.clf()
  fig = plt.figure(1)
  ax = fig.add_subplot(111)
  ax.grid(True)
  x1 = [x[0] for x in result.optimal.f]
  x2 = [x[1] for x in result.optimal.f]
  ax.plot(x1, x2, 'bo' , label = 'Pareto Frontier')
  ax.set_xlabel('f1')
  ax.set_ylabel('f2')
  ax.legend(loc = 'best')
  title ='Simple problem with gradients'
  plt.title(title)
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()

def main():
  # create problem
  problem = SimpleProblem()
  print(str(problem))
  # create optimizer with default parameters
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger())
  # solve problem and get result
  result = optimizer.solve(problem)
  # print general info about result
  print(str(result))
  # print Pareto optimal points
  result.optimal.pprint()
  # plot Pareto frontier
  plot(result)

if __name__ == "__main__":
  main()
