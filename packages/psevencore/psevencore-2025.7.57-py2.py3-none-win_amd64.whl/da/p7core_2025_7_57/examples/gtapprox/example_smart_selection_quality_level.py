#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example illustrates how behaviour of Smart Selection procedure can be tuned via AcceptableQualityLevel hint.
"""

#[0] imports needed
from da.p7core import gtapprox, loggers

import numpy as np
import time
#[0]

#[1] output function
def ellipsoidal(x):
  y = np.maximum(x[:, 0]**2 + x[:, 1]**2, 0.1 * (x[:, 0] - 1)**2 + 0.1 * (x[:, 1] - 1)**2)
  return y

#[2] data generation procedure
def get_data(size):
  x = np.random.rand(size, 2)
  y = ellipsoidal(x)
  return x, y
#[2]

#[3]
def main():
  #[3.1]
  # generate training data
  x, y = get_data(100)

  # generate test data
  x_test, y_test = get_data(5000)

  builder = gtapprox.Builder()
  builder.set_logger(loggers.StreamLogger())

  #[3.2] construct GTApprox model with Smart Selection and AcceptableQualityLevel=0.1
  hints = {'@GTApprox/AcceptableQualityLevel': 0.1}

  rough_time = time.time()
  model_smart_rough = builder.build_smart(x, y, x_test=x_test, y_test=y_test, hints=hints)
  rough_time = time.time() - rough_time

  #[3.3] construct GTApprox model with Smart Selection and AcceptableQualityLevel=0.1
  hints = {'@GTApprox/AcceptableQualityLevel': 0.02}

  precise_time = time.time()
  model_smart_precise = builder.build_smart(x, y, x_test=x_test, y_test=y_test, hints=hints)
  precise_time = time.time() - precise_time

  #[3.4] compute approximation errors on the test data and output results
  print("Model smart rough technique: %s" % model_smart_rough.details['Technique'])
  print("Model smart rough error: %s" % model_smart_rough.validate(x_test, y_test)['RRMS'])
  print("Training time of model smart rough: %s seconds" % rough_time)
  print("Model smart precise technique: %s" % model_smart_precise.details['Technique'])
  print("Model smart precise  error: %s" % model_smart_precise.validate(x_test, y_test)['RRMS'])
  print("Training time of model smart precise : %s seconds" % precise_time)

#[3]

if __name__ == "__main__":
  main()
