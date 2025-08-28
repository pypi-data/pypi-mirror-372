#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

'''
Solve the ZDT1 problem showing the multi-objective optimization capability of GTOpt.
'''

#[0] required imports
from da.p7core import gtopt
from da.p7core import loggers

import numpy as np
import matplotlib.pyplot as plt

import os
#[0] end imports

#[1] problem definition
class ZDT1(gtopt.ProblemUnconstrained):
  def prepare_problem(self):
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    self.add_objective()
    self.add_objective()

  def define_objectives(self, x):
    f1 = x[0]
    g = 1.0 + 9.0 * x[1]
    f2 = g * (1.0 - np.sqrt(f1 / g))
    return f1, f2
#[1] end problem definition

#[2] problem solving
def solve_problem(problem):
  print(str(problem))
  optimizer = gtopt.Solver()
  optimizer.set_logger(loggers.StreamLogger())
  optimizer.options.set('GTOpt/FrontDensity', 15)
  result = optimizer.solve(problem)
  print(str(result))
  print("Optimal points:")
  result.optimal.pprint(limit=10)
  return result
#[2]

#[3] plotting
def plot(result):
  fig = plt.figure(1)
  f1, f2 = result.optimal.f.transpose()
  plt.plot(f1, f2, 'bo' , label = 'Pareto Frontier')
  f1_sample = np.linspace(0, 1, 1000)
  plt.plot(f1_sample, 1 - np.sqrt(f1_sample), "r", label='Pareto frontier (analytical)')
  plt.xlabel('f1')
  plt.ylabel('f2')
  plt.legend(loc = 'best')

  title = 'ZDT1 problem'
  plt.title(title)

  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()
#[3]

#[4] main
def main():
  problem = ZDT1()
  print('=' * 60)
  print('Solve problem %s' % problem.__class__.__name__)
  result = solve_problem(problem)
  plot(result)
  print('Finished!')
  print('=' * 60)
#[4]

if __name__ == '__main__':
  main()
