#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example illustrates how Smart Selection in default mode can find the best suited technique for different outputs of the model.
"""

#[0] imports needed
from da.p7core import gtapprox, loggers

import numpy as np
#[0]

#[1] output function
def linear(x):
  return (x[:, [0]] + 2 * x[:, [1]])

def ellipsoidal(x):
  y = x[:, [0]]**2 + x[:, [1]]**2
  return y

def six_hump_camel_back(x):
  x1 = 3 * x[:, [0]]
  x2 = 2 * x[:, [1]]
  a = 4.0
  b = 2.1
  c = 3.0
  y = (a - b * (x1**2) + (x1**4) / c) * (x1**2) + x1 * x2 + a * ((x2**2) - 1) * (x2**2)
  return y

def f(x):
  return np.hstack((linear(x), ellipsoidal(x), six_hump_camel_back(x)))
#[1]

#[2] data generation procedure
def get_train_data(size):
  x0 = x1 = np.linspace(-1, 1, size)
  x0, x1 = np.meshgrid(x0, x1)
  x0 = x0.reshape(-1, 1)
  x1 = x1.reshape(-1, 1)
  x = np.hstack((x0, x1))

  y = f(x)
  return x, y

def get_test_data(size):
  x_test = np.random.rand(size, 2) * 2 - 1
  y_test = f(x_test)
  return x_test, y_test
#[2]

#[3]
def main():
  # generate training sample
  x, y = get_train_data(100)

  # generate test sample
  x_test, y_test = get_test_data(5000)

  builder = gtapprox.Builder()
  builder.set_logger(loggers.StreamLogger())

  # construct default GTApprox model
  model_default = builder.build(x, y)

  # construct GTApprox model with Smart Selection
  model_smart = builder.build_smart(x, y)

  # compute approximation errors on the test data and output results
  print("Default model technique: %s" % model_default.details['Technique'])
  print("Default model error: %s" % model_default.validate(x_test, y_test)['RRMS'])
  print("Training time of default model: %s " % model_default.details["Training Time"]["Total"])

  print("Smart model technique: %s" % model_smart.details['Technique'])
  print("Smart Selection technique for output 0: %s" % model_smart.details['Model Decomposition'][0]['Technique'])
  print("Smart Selection technique for output 1: %s" % model_smart.details['Model Decomposition'][1]['Technique'])
  print("Smart Selection technique for output 2: %s" % model_smart.details['Model Decomposition'][2]['Technique'])
  print("Smart model error: %s" % model_smart.validate(x_test, y_test)['RRMS'])
  print("Training time of Smart Selection: %s " % model_smart.details["Training Time"]["Total"])
  print("Smart Selection training options for output 0: %s" % model_smart.details['Model Decomposition'][0]['Training Options'])
  print("Smart Selection training options for output 1: %s" % model_smart.details['Model Decomposition'][1]['Training Options'])
  print("Smart Selection training options for output 2: %s" % model_smart.details['Model Decomposition'][2]['Training Options'])

#[3]

if __name__ == "__main__":
  main()
