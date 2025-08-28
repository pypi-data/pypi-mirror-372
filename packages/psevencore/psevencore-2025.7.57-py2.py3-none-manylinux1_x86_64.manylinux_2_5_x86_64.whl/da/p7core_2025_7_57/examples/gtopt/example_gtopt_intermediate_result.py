#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Example of using watcher to obtain intermediate results from GTOpt"""

#[imports] begin
from da.p7core import gtopt # is required for GTOpt functionality
import matplotlib.pyplot as plt # to show some plots
from math import exp # for objective computation
#[imports] end

#[problem] begin
class faf(gtopt.ProblemUnconstrained):
  """
  Fonseca and Fleming function.
  Number of variables: n = 2.
  Number of objectives k = 2.
  Source: C. M. Fonzeca and P. J. Fleming, “An overview of evolutionary algorithms in multiobjective optimization,” Evol Comput, vol. 3, no. 1, pp. 1-16, 1995.
  """

#[prepare] begin
  def prepare_problem(self):
    self.n = 2
    for i in range(self.n):
      self.add_variable((-4.0, 4.0))

    self.add_objective(hints={"@GTOpt/EvaluationCostType": "Expensive"})
    self.add_objective(hints={"@GTOpt/EvaluationCostType": "Expensive"})
#[prepare] end
#[objectives] begin
  def define_objectives(self, x):
    n_sqrt = self.n**-.5
    return [- exp(-sum([(t - n_sqrt)**2 for t in x])),
            - exp(-sum([(t + n_sqrt)**2 for t in x]))]
#[objectives] end
#[problem] end

#[watcher] begin
class IntermediateResult():
  def __init__(self):
      self.counter = 0;

#[callback] begin
  def __call__(self, report):
  #[query] begin
    if report.get("ResultUpdated", None): # test if there updates for intermediate result are available
      result = report["RequestIntermediateResult"]() #query intermediate result
  #[query] end
      data = plt.plot(result.optimal.f[:, 0], result.optimal.f[:, 1], ".", label="Update %d" % self.counter)
      print("Optimal set size: %s" % result.optimal)
      self.counter += 1
      plt.legend(loc="lower left")
      plt.pause(0.0001) # show results
      data[0].set_label(None)
    return True
#[callback] end
#[watcher] end



def main():
  plt.axis([-1, 0, -1, 0])
#[optimize] begin
  optimizer = gtopt.Solver()
  optimizer.set_watcher(IntermediateResult())
  result = optimizer.solve(faf(), options={"GTopt/MaximumExpensiveIterations": 200})
#[optimize] end
  plt.plot(result.optimal.f[:, 0], result.optimal.f[:, 1], "bo", label="Final result")
  plt.legend(loc="lower left")
  plt.show()

if __name__ == "__main__":
  main()
