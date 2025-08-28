#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
We try to approximate gSobol function in R^6. Training sample is full factorial in R^6 with 10 points along each direction,
so the sample size is 10^5 points. If we use automatic selection of GTApprox technique, HDA will be used.
Training HDA model usually takes a few hours for such sample sizes.
On the other hand, the full factorial data structure of the training sample (a particular case of Cartesian product DoE)
allows us to use the Tensor Approximation technique for which the training time is significantly lower.
It is shown that TA provides fast and accurate approximation for gridded data even if sample is very large.
"""

#[0] required imports
from da.p7core import gtdoe, gtapprox, loggers

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D

from pprint import pprint
import time
import sys
import os
#[0] imports end

#[1] x sample generator
def full_factorial(a, b, levels, dim):
  '''
  Generate multidimensional full factorial DoE using Generic Tool for Design of Experiment.
  '''
  generator = gtdoe.Generator()
  bounds=(np.tile(a, (1, dim))[0],np.tile(b, (1, dim))[0])
  count=levels**dim
  result = generator.build_doe(bounds, count, options={'GTDoE/Technique': 'FullFactorial'})
  return result.solutions(["x"])
#[1]

#[2] true function for f sample generation
def data_generator(points):
  '''
  Calculate Sobol g-function on given sample.
  '''
  a = [4.5, 4.5, 1, 0, 1, 9];
  values = np.ones((points.shape[0],1))[:, 0]
  for i in range(points.shape[1]):
    values = values * (np.abs(4 * points[:, i] - 2) + a[i]) / (1 + a[i])
  return values
#[2]

#[3] RMS calculation
def rms_ptp(model, points, trueValues, dataRange):
  '''
  Calculate normalized root mean square error.
  '''
  predictedValues = model.calc(points)[:, 0]
  return np.mean((predictedValues - trueValues)**2.0)**0.5 / dataRange
#[3]

#[4-0] main workflow
def main():
  print('='*50)
  print('Generate training sample.')
  numberOfPointsInFactor = 10
  problemDimension = 6
  print('Generate full factorial DoE.')
  trainPoints = full_factorial(0, 1, numberOfPointsInFactor, problemDimension)
  print('Calculate function values.')
  trainValues = data_generator(trainPoints)
#[4-1]
  print('='*50)
  print('Generate test sample.')
  numberOfTestPoints = 50000
  print('Generate random DoE.')
  testPoints = np.random.rand(numberOfTestPoints, problemDimension)
  print('Calculate function values.')
  testValues = data_generator(testPoints)
#[4-2]
  print('='*50)
  print('Initialize and configure GTApprox builder.')
  builder = gtapprox.Builder()
  logger = loggers.StreamLogger(sys.stdout, loggers.LogLevel.DEBUG)
  print('Set logger.')
  builder.set_logger(logger)
  print('Set logging level to debug.')
  builder.options.set('GTApprox/LogLevel', 'DEBUG')
  print("By default TA technique isn't used, so we should explicitly turn this branch of decision tree on.")
  builder.options.set('GTApprox/EnableTensorFeature', 'On')
#[4-3]
  print('='*50)
  print('Build approximation model.')
  startTime = time.time()
  model = builder.build(trainPoints, trainValues)
  finishTime = time.time()
#[4-4]
  print('='*50)
  print('Information about training and model:')
  print('Sample is %s points in R%s' % (trainPoints.shape[0], str(problemDimension)))
  print('Training time is %s seconds' % (finishTime - startTime))
  dataRange = np.max(testValues) - np.min(testValues)
  print('...Calculating error on training sample...')
  print('RMS/PTP error on training sample is %s' % rms_ptp(model, trainPoints, trainValues, np.max(trainValues) - np.min(trainValues)))
  print('...Calculating error on test sample...')
  print('RMS/PTP error on test sample is %s' % rms_ptp(model, testPoints, testValues, np.max(testValues) - np.min(testValues)))
  print('Model info:')
  pprint(model.info)
#[4-5]
  print('='*50)
  print('Plot function and its approximation.')
  plot(model, trainPoints[:numberOfPointsInFactor**2, :2], trainValues[:numberOfPointsInFactor**2], problemDimension)
#[4-6]

#[5] plotting
def plot(model, trainPoints, trainValues, problemDimension):
  '''
  Plot a slice of approximation along 1st and 2nd components of X.
  It means that X3, X4, X5 and X6 are fixed at 0 and X1, X2 is varied.
  '''
  # generate points for visualizing surface
  X12 = full_factorial(0, 1, 30, 2)
  gridPointsX1 = X12[:, 0].reshape(30, 30)
  gridPointsX2 = X12[:, 1].reshape(30, 30)
  gridPoints = np.hstack([X12, np.zeros((900, problemDimension - 2))])
  gridValues = data_generator(gridPoints)
  gridValuesPrediction = model.calc(gridPoints)
  # create figure
  fig = plt.figure(figsize = (22, 10))
  fig.suptitle('Tensor Approximation', fontsize = 18)
  # make plot for function
  ax = fig.add_subplot(121, projection='3d')
  ax.set_title('True function slice')
  ax.view_init(35, -65)
  ax.scatter3D(trainPoints[:, 0], trainPoints[:, 1], trainValues, alpha = 1.0, c ='r', marker='o', linewidth = 1, s = 50)
  scatter_proxy = matplotlib.lines.Line2D((0, 0), (1, 1), marker = '.', color = 'r', linestyle = '', markersize = 10)
  reshapeSizes = [gridPointsX1.shape]
  ax.plot_surface(gridPointsX1, gridPointsX2, gridValues.reshape(reshapeSizes[0]), rstride = 1, cstride = 1, cmap = matplotlib.cm.jet,
                  linewidth = 0.1, alpha = 0.6, antialiased = False)
  ax.set_xlabel('$X_1$', fontsize ='18')
  ax.set_ylabel('$X_2$', fontsize ='18')
  ax.legend([scatter_proxy],['training points'], loc = 'best')
  # make plot for approximation
  ax2 = fig.add_subplot(122, projection='3d')
  ax2.set_title('Approximation model slice')
  ax2.view_init(35, -65)
  ax2.scatter3D(trainPoints[:, 0], trainPoints[:, 1], trainValues, alpha = 1.0, c ='r', marker='o', linewidth = 1, s = 50)
  reshapeSizes = [gridPointsX1.shape]
  ax2.plot_surface(gridPointsX1, gridPointsX2, gridValuesPrediction.reshape(reshapeSizes[0]), rstride = 1, cstride = 1, cmap = matplotlib.cm.jet,
                   linewidth = 0.1, alpha = 0.6, antialiased = False)
  ax2.set_xlabel('$X_1$', fontsize ='18')
  ax2.set_ylabel('$X_2$', fontsize ='18')
  ax2.legend([scatter_proxy],['training points'], loc = 'best')
  # save and show plots
  title = 'tensor_approximation'
  fig.savefig(title)
  print('Plots are saved to %s.png' % os.path.join(os.getcwd(), title))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()
#[5]

#[6]
if __name__ == "__main__":
  main()
#[6]
