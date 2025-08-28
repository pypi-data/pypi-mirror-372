#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
import numpy as np

"""Using adaptive DOE for approximation example."""

from da.p7core import gtapprox
from da.p7core.loggers import LogLevel, StreamLogger
from da.p7core import blackbox as bb

class TestProblem(bb.Blackbox):
  def prepare_blackbox(self):
    self.add_variable((0, 1))
    self.add_variable((0, 1))
    self.add_response()

  def evaluate(self, queryx):
    x1 = queryx[:,0]
    x2 = queryx[:,1]
    f = 2.0 +0.25 *(x2 - 5.0 *x1**2)**2 + (1.0 -5.0 *x1)**2 +2.0 *(2.0 -5.0*x2)**2 +7.0 *np.sin(2.5 *x1) *np.sin(17.5 *x1 *x2)
    return f.reshape((queryx.shape[0], 1))

initial_x = np.array([[0.65, 0.15],
                      [0.55, 0.45],
                      [0.75, 0.85],
                      [0.35, 0.25],
                      [0.05, 0.05],
                      [0.15, 0.55],
                      [0.95, 0.65],
                      [0.45, 0.75],
                      [0.85, 0.35],
                      [0.25, 0.95]])

def get_sample(problem, points, x_sample=None, f_sample=None):
  """Data set generation."""
  from da.p7core import gtdoe
  doegenerator = gtdoe.Generator()
  doegenerator.options.set({'GTDoE/Technique': 'LHS'})
  result = doegenerator.build_doe(problem, count=points, sample_x=x_sample, sample_f=f_sample)

  xSample = result.solutions(["x"], filter_type="new")
  fSample = result.solutions(["f"], filter_type="new")

  return xSample, fSample

def main():
  """Example to demonstrate AE and adaptive sampling."""
  # create builder
  builder = gtapprox.Builder()
  options = {
    'GTApprox/InternalValidation': 'off',
    'GTApprox/AccuracyEvaluation': 'on',
    'GTApprox/ExactFitRequired': 'on',
    'GTApprox/Technique': 'GP',
    'GTApprox/LogLevel': 'Info'
  }
  builder.options.set(options)
  builder.set_logger(StreamLogger(log_level=LogLevel.ERROR))

  # prepare initial training sample
  problem = TestProblem()
  initial_f = problem.evaluate(initial_x)

  print("Training initial model...")
  model = builder.build(initial_x, initial_f)
  print("Done!")

  # improve model
  iterations = 6
  additionalSize = 10
  testSize = 500
  x_sample = initial_x
  f_sample = initial_f

  for _ in range(iterations):
    # generate new big test sample
    x_test, f_test = get_sample(problem, testSize, x_sample, f_sample)

    # calculate actual and predicted errors on test sample
    errors = model.validate(x_test, f_test)
    print("Training sample size: %d, RMSE: %s" % (len(x_sample), errors["RRMS"]))

    # find max predicted error in test sample points
    ae_predictions = model.calc_ae(x_test).reshape((len(x_test,)))
    idx = np.argsort(ae_predictions)

    # add additionalSize points with maximal AE values to the training samples
    x_sample = np.vstack((x_sample, x_test[idx[-additionalSize:]]))
    f_sample = np.vstack((f_sample, f_test[idx[-additionalSize:]]))

    # build next improved model
    model = builder.build(x_sample, f_sample)

  # calculate final error
  x_test, f_test = get_sample(problem, testSize, x_sample, f_sample)
  errors = model.validate(x_test, f_test)
  print("Training sample size: %d, RRMS: %s" % (len(x_sample), errors["RRMS"]))

  print("Final result:\n--------------\nSample size: %d, RRMS: %s" % (len(x_sample), errors["RRMS"]))

if __name__ == "__main__":
  main()
