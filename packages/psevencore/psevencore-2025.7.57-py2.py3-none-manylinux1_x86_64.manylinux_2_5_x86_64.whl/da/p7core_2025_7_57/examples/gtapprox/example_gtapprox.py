#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Basic GTApprox Usage."""

from da.p7core import gtapprox
from da.p7core.loggers import StreamLogger

import math, random

def main():
  """
  Example of GTApprox usage.
  """

  # prepare data
  sSize = 7
  dim = 2
  random.seed(10)
  # generate random hypercube and evaluate function
  x_sample = [[random.uniform(0., 1.) for i in range(dim)] for j in range(sSize)]
  y_sample = [[x[i]**(i+1) for i in range(len(x))] for x in x_sample]

  # create approximation builder
  builder = gtapprox.Builder()
  # setup options
  options = {
  'GTApprox/AccuracyEvaluation': 'on',
  'GTApprox/Technique': 'GP',
  'GTApprox/InternalValidation': 'on',
  'GTApprox/LogLevel': 'Info'
  }
  builder.options.set(options)
  # setup logger function (optional)
  logger = StreamLogger()
  builder.set_logger(logger)
  # train model
  model = builder.build(x_sample, y_sample)
  # save trained model
  model.save('approxModel.gta')

  # load trained model and use it
  loaded_model = gtapprox.Model('approxModel.gta')

  # print model information
  print('----------- Model -----------')
  print('SizeX: %d' % loaded_model.size_x)
  print('SizeF: %d' % loaded_model.size_f)
  print('Model has AE: %s' % loaded_model.has_ae)
  print('----------- Info -----------')
  print(str(loaded_model))

  # create test sample
  test_xsample = [[random.uniform(0., 1.) for i in range(dim)] for j in range(sSize)]

  # calculate and display approximated values
  for x in test_xsample:
    y = loaded_model.calc(x)
    print('Model Y: %s' % y)

  # calculate and display gradients
  for x in test_xsample:
    dy = loaded_model.grad(x, gtapprox.GradMatrixOrder.F_MAJOR)
    print('Model gradient: %s' % dy)

  # calculate and display AE
  for x in test_xsample:
    ae = loaded_model.calc_ae(x)
    print('Model AE: %s' % ae)

if __name__ == "__main__":
  main()
