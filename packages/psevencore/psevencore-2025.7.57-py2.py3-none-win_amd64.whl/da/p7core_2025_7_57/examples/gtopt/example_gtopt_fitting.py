#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example demonstrates usage of :class:`ProblemFitting<da.p7core.gtopt.ProblemFitting>`, that provides a short-cut for a formulating models fitting problem.

The problem is finding coefficient `x` minimizing:

   (\\sum_{i=1}^N (f(model^x_i, x) - model^y_i)^2/N)^{1/2}

:class:`ProblemFitting<da.p7core.gtopt.ProblemFitting>` requires to define model (`f`), variables and data.

"""


#[imports] begin
from da.p7core import gtopt # is required for GTOpt functionality
import numpy # for plot and data generation
import matplotlib.pyplot as plt # depicts results
import os
#[imports] end

#[problem] begin
class SineFit(gtopt.ProblemFitting):
  def __init__(self, model_x, model_y):
    self.model_x = model_x
    self.model_y = model_y

  def prepare_problem(self):
#[x_sample] begin
    self.add_model_x(self.model_x)
#[x_sample] end
#[variables] begin
    self.add_variable((None, None), 1)
    self.add_variable((None, None), 2)
#[variables] end
#[y_sample] begin
    self.add_model_y(self.model_y)
#[y_sample] end
#[model] begin
  def define_models(self, x, p):
    return p[0] * numpy.sin(p[1] * x)
#[model] end
#[problem] end

#[generate] begin
def generate_data(N=10):
  task = SineFit([1], [1]) #formally create instance of SineFit to reuse define_models method
  x = numpy.linspace(0, 1, N)
  numpy.random.seed(1234) # fix seed
  y = task.define_models(x, [2, 5]) * (1 +  numpy.random.uniform(-.1, +.1, N))
  return x, y
#[generate] end


def fit(model_x, model_y):
#[fitting] begin
  optimizer = gtopt.Solver()
  task = SineFit(model_x, model_y)
  result = optimizer.solve(task)
#[fitting] end
#[plot] begin
  x = numpy.linspace(0, 1, 20)
  y = [task.define_models(t, result.optimal.x[0]) for t in x]

  plt.plot(model_x, model_y, linestyle="", marker="o", label="data")

  plt.plot(x, y, '-.', label="fit")
  title = "Fitting"
  plt.title(title)
  plt.legend(loc="best")
  plt.savefig(title)
  print("Plots are saved to %s.png" % os.path.join(os.getcwd(), title))
  if "SUPPRESS_SHOW_PLOTS" not in os.environ:
    plt.show()
#[plot] end

if __name__ == '__main__':
  fit(*generate_data())
