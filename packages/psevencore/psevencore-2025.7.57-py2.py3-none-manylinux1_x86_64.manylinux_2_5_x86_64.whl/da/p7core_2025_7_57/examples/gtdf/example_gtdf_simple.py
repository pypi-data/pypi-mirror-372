#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Approximate 1-dimensional function using various techniques including GT Approx Gaussian processes, GTDF VFGP, GTDF BB VFGP
"""

#[1]
from da.p7core import gtapprox
from da.p7core import gtdf
from da.p7core import blackbox
from da.p7core import loggers

import numpy as np
import matplotlib.pyplot as plt

import os
#[1]

#[2]
# functions to approximate
def highFidelityFunction(x):
  return (6. * x - 2.) ** 2. * np.sin(12. * x - 4.)

def lowFidelityFunction(x):
  return 0.5 * highFidelityFunction(x) + 10. * (x - 0.5) - 5.
#[2]

#[3]
def getTrainData():
  '''
  Generate training samples.
  '''
  lowFidelityPoints = np.linspace(0., 1., 15)
  highFidelityPoints = np.array([0.01, 0.35, 0.45, 0.55, 0.99])

  lowFidelityValues = lowFidelityFunction(lowFidelityPoints)
  highFidelityValues = highFidelityFunction(highFidelityPoints)

  return lowFidelityPoints, lowFidelityValues, highFidelityPoints, highFidelityValues
#[3]

#[4]
def trainGpModel(highFidelityTrainPoints, highFidelityTrainValues):
  '''
  Build GTApprox model using GP technique.
  '''
  # create builder
  builder = gtapprox.Builder()
  # set logger
  logger = loggers.StreamLogger()
  builder.set_logger(logger)
  # setup options
  options = {
  'GTApprox/Technique': 'GP',
  'GTApprox/LogLevel': 'Info',
  }
  builder.options.set(options)
  # train GT Approx model
  return builder.build(highFidelityTrainPoints, highFidelityTrainValues)
#[4]

#[5]
def trainVfgpModel(highFidelityTrainPoints, highFidelityTrainValues, lowFidelityTrainPoints, lowFidelityTrainValues):
  '''
  Build GTDF model using VFGP technique.
  '''
  # create builder
  builder = gtdf.Builder()
  # set logger
  logger = loggers.StreamLogger()
  builder.set_logger(logger)
  # setup options
  options = {
  'GTDF/Technique': 'VFGP',
  'GTDF/LogLevel': 'Info',
  }
  builder.options.set(options)
  # train GT DF model
  return builder.build(highFidelityTrainPoints, highFidelityTrainValues, lowFidelityTrainPoints, lowFidelityTrainValues)
#[5]

#[6]
class LowFidelityFunctionBlackBox(blackbox.Blackbox):
  '''
  Blackbox class for evaluating low fidelity function.
  '''
  def __init__(self):
    blackbox.Blackbox.__init__(self)

  def prepare_blackbox(self):
    self.add_variable((0, 1))
    self.add_response()

  # low fidelity function evaluation
  def evaluate(self, points):
    result = []
    for point in points:
      result.append([lowFidelityFunction(point[0])])
    return result
#[6]

#[7]
def trainVfgpBbModel(highFidelityTrainPoints, highFidelityTrainValues, lowFidelityFunctionBlackBox):
  '''
  Build GTDF model using VFGP_BB technique.
  '''
  # create builder
  builder = gtdf.Builder()
  # set logger
  logger = loggers.StreamLogger()
  builder.set_logger(logger)
  # setup options
  options = {
  'GTDF/Technique': 'VFGP_BB',
  'GTDF/LogLevel': 'Info',
  }
  builder.options.set(options)
  # train blackbox-df model
  return builder.build_BB(highFidelityTrainPoints, highFidelityTrainValues, lowFidelityFunctionBlackBox)
#[7]

#[8]
def buildModels(lowFidelityTrainPoints, lowFidelityTrainValues, highFidelityTrainPoints, highFidelityTrainValues):
  '''
  Build surrogate models.
  Three techniques are used to build an approximation: GTApprox GP, GTDF VFGP, GTDF BB VFGP.
  '''
  gtaModel = trainGpModel(highFidelityTrainPoints, highFidelityTrainValues)

  vfgpModel = trainVfgpModel(highFidelityTrainPoints,
                             highFidelityTrainValues,
                             lowFidelityTrainPoints,
                             lowFidelityTrainValues)

  lfBlackBox = LowFidelityFunctionBlackBox()
  blackboxModel = trainVfgpBbModel(highFidelityTrainPoints,
                                   highFidelityTrainValues,
                                   lfBlackBox)

  return gtaModel, vfgpModel, blackboxModel
#[8]

#[9]
def getTestData(sampleSize):
  '''
  Generate test data.
  '''
  points = np.reshape(np.linspace(0., 1., sampleSize), (sampleSize, 1))

  lowFidelityValues = lowFidelityFunction(points)
  highFidelityValues = highFidelityFunction(points)

  return points, lowFidelityValues, highFidelityValues

def calculateValues(testPoints, gtaModel, vfgpModel, blackboxModel):
  '''
  Calculate models on given sample.
  '''
  gtaValues = gtaModel.calc(testPoints)
  vfgpValues = vfgpModel.calc(testPoints)
  bbValues = blackboxModel.calc_bb(LowFidelityFunctionBlackBox(), testPoints.tolist())
  return gtaValues, vfgpValues, bbValues
#[9]

#[10]
def plot_train(lowFidelityTrainPoints, lowFidelityTrainValues, highFidelityTrainPoints, highFidelityTrainValues):
  '''
  Visualize training sample.
  '''
  plt.plot(lowFidelityTrainPoints, lowFidelityTrainValues, 'sb', markersize = 7.0, linewidth = 2.0, label = 'Low fidelity sample points')
  plt.plot(highFidelityTrainPoints, highFidelityTrainValues, 'or', markersize = 7.0, linewidth = 2.0, label = 'High fidelity sample points')

def plot_test(testPoints, lowFidelityTestValues, highFidelityTestValues):
  '''
  Visualize test sample.
  '''
  plt.plot(testPoints, lowFidelityTestValues, '-.b', linewidth = 2.0, label = 'Low fidelity function')
  plt.plot(testPoints, highFidelityTestValues, 'r', linestyle = '--', linewidth = 2.0, label = 'High fidelity function')

def plot_approximations(testPoints, gtaValues, vfgpValues, bbValues):
  '''
  Visualize approximations.
  '''
  plt.plot(testPoints, gtaValues, ':m', linewidth = 2.0, label = 'GTApprox GP')
  plt.plot(testPoints, vfgpValues, 'c', linewidth = 2.0, label = 'GTDF VFGP')
  plt.plot(testPoints, bbValues, '--k', linewidth = 2.0, label = 'GTDF BB VFGP')

def show_plots():
  '''
  Configure, show and save plots.
  '''
  plt.xlabel(r'$x$', fontsize = 30)
  plt.ylabel(r'$y(x)$', fontsize = 30)
  plt.grid(True)
  plt.title('GTDF example')
  plt.legend(loc = 'best')
  name = 'gtdf_simple_example'
  plt.savefig(name)
  print('Plot is saved to %s.png' % os.path.join(os.getcwd(), name))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()
#[10]

#[m]
def main():
  """
  Toy example of GTDF usage.
  """
  print('GTDF usage example')
  print('=' * 50)
  print('Generate training sample...')
  trainData = getTrainData()
  print('Build models...')
  models = buildModels(*trainData)
  print('Generate test sample...')
  testPoints, lowFidelityTestValues, highFidelityTestValues = getTestData(1000)
  print('Calculate model values for the test sample...')
  modelsValues = calculateValues(testPoints, *models)
  print('Plotting...')
  figure_handle = plt.figure(figsize=(8.5, 8))
  # visualize training sample
  plot_train(*trainData)
  # visualize test sample
  plot_test(testPoints, lowFidelityTestValues, highFidelityTestValues)
  # visualize approximations
  plot_approximations(testPoints, *modelsValues)
  # show and save plots
  show_plots()

if __name__ == "__main__":
  main()
#[m]
