#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Internal Validation Example"""

from da.p7core import gtapprox, gtdoe
from da.p7core.loggers import StreamLogger

import numpy as np

def rosenbrock(x):
  """
  Rosenbrock function (simple one)
  """
  x1 = x[:,0]
  x2 = x[:,1]
  return (1.0-x1)**2 +100*(x2-x1**2)**2

def rastrigin(x):
  """
  Rastrigin function (very complex one)
  """
  x1 = x[:,0]
  x2 = x[:,1]
  return 20. + (x1**2 -10 *np.cos(2.0*np.pi*x1)) +(x2**2 - 10* np.cos(2.0*np.pi*x2))

def main():
  """
  Example to demonstrate IV
  """
  # create generator
  generator = gtdoe.Generator()

  # create builder
  builder = gtapprox.Builder()
  builder.options.set('GTApprox/LogLevel', 'Info')
  builder.options.set('GTApprox/InternalValidation', 'on')
  #set logger
  logger = StreamLogger()
  builder.set_logger(logger)

  # data description
  dim_x = 2
  dim_f = 1
  bounds = ([-1]*dim_x, [1]*dim_x)
  training_sample_size = 20
  test_sample_size = 25**dim_x

  # generating training input sample
  result = generator.build_doe(bounds, training_sample_size, options={'GTDoE/Technique': 'LHS'})
  x_sample = result.solutions(["x"])

  print("IV example\n---------------")
  # generating training output sample for rosenbrock model
  y_sample = rosenbrock(x_sample)
  print("Training model 1...")
  model_rosenbrock = builder.build(x_sample, y_sample)
  print("Done!\n")

  # generating training output sample for rastrigin model
  y_sample = rastrigin(x_sample)
  print("Training model 2...")
  model_rastrigin = builder.build(x_sample, y_sample)
  print("Done!\n\n")

  # generating test sample
  result = generator.build_doe(bounds, test_sample_size, options={'GTDoE/Technique': 'FullFactorial'})
  x_test = result.solutions(["x"])
  f_rosenbrock = rosenbrock(x_test)
  f_rastrigin = rastrigin(x_test)

  # calculating error on test sample
  err_rosenbrock = model_rosenbrock.validate(x_test, f_rosenbrock)
  err_rastrigin = model_rastrigin.validate(x_test, f_rastrigin)

  print("Actual RMS error on Rosenbrock function:")
  print(str(err_rosenbrock["RMS"]))
  print("Internal validation results for Rosenbrock function:")
  print(str(model_rosenbrock.iv_info["Componentwise"]["RMS"]))

  print("\n\nActual RMS error on Rastrigin function:")
  print(str(err_rastrigin["RMS"]))
  print("Internal validation results for Rastrigin function:")
  print(str(model_rastrigin.iv_info["Componentwise"]["RMS"]))

if __name__ == "__main__":
  main()
