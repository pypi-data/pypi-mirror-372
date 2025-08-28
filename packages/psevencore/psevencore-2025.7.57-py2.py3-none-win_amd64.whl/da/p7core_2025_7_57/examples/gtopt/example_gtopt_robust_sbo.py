#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example demonstrates usage of GTOpt Robust Design Optimization.
Comparing to examples in :py:mod:`example_gtopt_rdo.py` that also is about optimization with uncertainty,
this example does not rely on common random numbers (i.e. no controllable random generator is needed)
and suppose that evaluations of objectives are time consuming.

The problem is modification of  Vibrating Platform Design problem from  Narayanan, S. and S. Azarm, 1999,
"On Improving Multiobjective Genetic Algorithms  for  Design  Optimization" *Structural and Multidisciplinary Optimization*, 18, pp. 146-155.

The problem statement is

   E f_n(t_1, t_2, t_3, xi) =
   (frac{\\pi}{2L^2} )
   (frac{2w
   (E_1 t^3_1 + E_2 ( t^3_2 - t^3_1 ) + E_3 ( t^3_3 - t^3_2 ))
   }{3 * mu} )^{1/2}
   c(t_1, t_2, t_3) = 2wL(c_1 t_1 + c_2 ( t_2 - t_1 ) + c_3 ( t_3 - t_2 ))
   mu = 2 w (rho_1 t_1 + rho_2 ( t_2 - t_1 ) + rho_3 ( t_3 - t_2 ))
   mu L- 2800 <= 0
   0 <= t_2 - t_1 <= 0.15
   0 <= t_3 - t_2 <= 0.01
   0.05 <= t_1 <= 0.5
   0.2 <= t_2 <= 0.5
   0.2 t_3 <= 0.6


where t = t_1, t_2, t_3 is design variables, xi is material uncertainty,
w, L are fixed geometrical parameters of platform.
Values (rho_1, rho__2, rho_3), (E_1, E_2, E_3), and (c_1, c_2, c_3) refer to the density,
modulus of elasticity, and material cost for the inner, middle, and outer layer of the
platform, respectively and are discrete variables.
"""

#[imports] begin
from __future__ import with_statement
from da.p7core import gtopt  # is required for GTOpt functionality
import random  # is required for stochastic problem definition
from math import pi  # is used in objectives definition
import pickle  # is used for exporting raw results
from da.p7core import loggers  # tracks optimizer activity
import matplotlib.pyplot as plt  # depicts results
import os  # is used for determine a path for saving a resulting plot to
#[imports] end

#[seed] begin
random.seed(111)
#[seed] end

#[distribution] begin
class Sequential:
  current_value = 0
  def getNumericalSample(self, quantity):
    out = list(range(self.current_value, self.current_value + quantity))
    self.current_value += quantity
    return out
  def getDimension(self):
    return 1
#[distribution] end

#[problem] begin
class VibratingPlatform(gtopt.ProblemConstrained):
  def __init__(self):
    self.p_def = [100, 2770, 7780]  # kg/m^3
    self.E_def = [1.6, 70, 200]  # GPa
    self.c_def = [500, 1500, 800]  # $
    self.w = 0.4  # m
    self.L = 4.  # m
#[init] end
  def p(self, i):
    i = int(i)
    return self.p_def[i] * (1. - random.random()/10.)

  def c(self, i):
    i = int(i)
    return self.c_def[i]

  def E(self, i):
    i = int(i)
    return self.E_def[i] * (1. - random.random()/10.)
#[matprop] end
  def prepare_problem(self):
    self.add_objective("-freq", hints={"@GTOpt/EvaluationCostType": "Expensive"})
    self.add_objective("cost", hints={"@GTOpt/EvaluationCostType": "Expensive"})

    self.add_variable((0.05, 0.5), name="t1")
    self.add_variable((0.2, 0.5), name="t2")
    self.add_variable((0.2, 0.6), name="t3")

    self.add_variable((0, 2), name="M1", hints={"@GTOpt/VariableType" : "Integer"})
    self.add_variable((0, 2), name="M2", hints={"@GTOpt/VariableType" : "Integer"})
    self.add_variable((0, 2), name="M3", hints={"@GTOpt/VariableType" : "Integer"})

    self.add_constraint((None, 2800.0), hints={"@GTOpt/EvaluationCostType": "Expensive"})
    self.add_constraint((0, 0.15), hints={"@GTOpt/LinearityType" : "Linear"})
    self.add_constraint((0, 0.01), hints={"@GTOpt/LinearityType" : "Linear"})

    self.set_stochastic(Sequential())

    self.disable_history()
#[prepare] end

  def mu(self, t1, t2, t3, M1, M2, M3):
    return 2 * self.w * (self.p(M1) * t1 + self.p(M2) * (t2 - t1) + self.p(M3) * (t3 - t2))

  def define_constraints(self, t):
    return [
      self.mu(t[0],t[1],t[2], t[3],t[4],t[5]) * self.L,
      t[1] - t[0],
      t[2] - t[1]
      ]

  def define_objectives(self, t):
    EI = (2. * self.w / 3.) * (self.E(t[3]) * t[0]**3 + self.E(t[4]) * (t[1]**3 - t[0]**3) + self.E(t[5]) * (t[2]**3 - t[1]**3))
    freq = (pi / 2 / self.L**2) * EI / self.mu(t[0],t[1],t[2], t[3],t[4],t[5])**.5
    cost = 2 * self.w * self.L * (self.c(t[3]) * t[0] + self.c(t[4]) * (t[1] - t[0]) + self.c(t[5]) *(t[2] - t[1] ))
    return [-freq * 10**1.5, cost]  # multiplied by 10**1.5 to convert to MHz (G^{1/2} = 10^{4.5} = M 10^{1.5})

#[problem] end


def optimize():
#[instancing] begin
  optimizer = gtopt.Solver()  # instancing solver
  optimizer.set_logger(loggers.StreamLogger())  # set logger
  optimizer.options.set({"GTOpt/GlobalPhaseIntensity": 0.1})  # low globalization intensity
  optimizer.options.set({"GTOpt/FrontDensity": 5})  # five desirable points on Pareto frontier
  optimizer.options.set({"GTOpt/MaximumExpensiveIterations" : 2500})  # restriction on the total number of evaluations
  optimizer.options.set({"GTOpt/OptimalSetType" : "Strict"})  # Seek approximation of front. Alternative extended mode returns screened points, that we encontered while approximation was build
  result = optimizer.solve(VibratingPlatform())  # run optimization
#[instancing] end

  with open("results_rdo.pkl", "wb") as f:  # save raw results
    pickle.dump(result, f, -1)

def main():
  optimize()  # ~ 1200 sec

  with open("results_rdo.pkl", "rb") as pklFile:
    result = pickle.load(pklFile)

  plt.plot(result.optimal.f[:, 0], result.optimal.f[:, 1], "or", label="Front approximation")
  plt.gca().set_xlabel("-Frequency (MHz)")
  plt.gca().set_ylabel("Cost ($)")

  plt.errorbar(result.optimal.f[:, 0], result.optimal.f[:, 1],
               xerr=10 * result.optimal.fe[:, 0],
               yerr=10 * result.optimal.fe[:, 1],
               fmt='.', ecolor='g', markeredgewidth=2, label="Error estimation")
  plt.legend(loc="best")

  plt.savefig("platfrom_result")
  print('Plot is saved to %s.png' % os.path.join(os.getcwd(), "platfrom_result"))

  from os import environ
  if 'SUPPRESS_SHOW_PLOTS' not in environ:
    plt.show()

if __name__ == '__main__':
  from time import sleep
  print("WARNING: The execution of this example can be time consuming!")
  print("Depending on the execution environment it can take an hour to complete.")
  print("Press Ctrl-C in 10 seconds to avoid execution...")
  sleep(10)
  print("Starting example...")
  main()

