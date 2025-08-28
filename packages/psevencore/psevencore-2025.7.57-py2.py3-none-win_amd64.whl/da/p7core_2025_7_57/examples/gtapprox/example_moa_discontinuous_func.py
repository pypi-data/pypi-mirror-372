#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""MoA vs. GP technique on discontinuous function."""

#[0] required imports
from da.p7core import gtapprox
from da.p7core.loggers import StreamLogger

import numpy as np
from matplotlib import pyplot, cm, lines
from mpl_toolkits.mplot3d import Axes3D

import os
#[0] imports end

#[1] function to be approximated
def function(X):
  center1 = 0.5 + np.zeros((len(X), 2))
  gamma = np.ones((len(X), 2))
  Y = (np.sum(gamma * X, axis=1) + 1 * (np.sum((X - 0 * center1)**2, axis=1) <= 0.5**2) -
   2 * (np.sum((X - 0.7)**2, axis=1) <= 1**2))
  return Y
#[1]

#[2] RMS calculation
def rms(predictedValues, trueValues):
  '''
  Calculate normalized root mean square error.
  '''
  dataRange = np.max(trueValues) - np.min(trueValues)
  return np.sqrt(np.mean((predictedValues - trueValues)**2.0)) / dataRange
#[2]

#[3] plot figures
def plot(x_train_sample, y_train_sample, model=None, model_name=None):
  x = np.arange(-1, 1, 0.05)
  y = np.arange(-1, 1, 0.05)
  x, y = np.meshgrid(x, y)
  x1 = x.reshape(x.shape[0] * x.shape[1], 1)
  x2 = y.reshape(y.shape[0] * y.shape[1], 1)
  grid_points = np.append(x1, x2, axis = 1)

  fig = pyplot.figure()
  fig.suptitle('MoA discontinuous function', fontsize=18)
  ax = fig.add_subplot(111, projection='3d')
  ax.set_title(model_name, fontsize=12)
  ax.view_init(azim=-35, elev=60)

  if model is None:
    z = function(grid_points)
    z = z.reshape(x.shape)
  else:
    z = model.calc(grid_points)
    z = z.reshape(x.shape)
    ax.scatter3D(x_train_sample[:, 0], x_train_sample[:, 1], y_train_sample,
                 c='r', marker='o', s=20)
    scatter_proxy = lines.Line2D((0, 0), (1, 1), marker='.', color='r',
                                 linestyle='', markersize=10)
    ax.legend([scatter_proxy],['training points'], loc='best')

  ax.plot_surface(x, y, z, rstride=1, cstride=1, cmap=cm.jet,
                  linewidth=0.1, alpha=0.6, antialiased=True)

  ax.set_xlabel('$X_1$', fontsize='18')
  ax.set_ylabel('$X_2$', fontsize='18')
  pyplot.xlim(-1, 1)
  pyplot.ylim(-1, 1)


  # save and show plots
  title = 'moa_example_discontinuous_function_' + model_name
  fig.savefig(title)
  #[3]

#[4] main workflow
def main():

  #[4-1] read train data
  print("Generate training data")
  train_sample_size = 150
  number_of_clusters = list(range(2, 11))
  dim = 2
  x_sample = -1 + 2 * np.random.rand(train_sample_size, dim)
  y_sample = function(x_sample)
  #[4-1]

  #[4-2] create moa model
  print('Initialize and configure GTApprox Builder.')
  moa_builder = gtapprox.Builder()
  print('Set logger.')
  logger = StreamLogger()
  moa_builder.set_logger(logger)
  print('Set logging level to Info.')
  moa_builder.options.set('GTApprox/LogLevel', 'Info')
  print('Set approximation technique to "MoA"')
  moa_builder.options.set('GTApprox/Technique', 'MoA')
  #[4-2]

  #[4-3]
  print('Set approximation technique for local models to "GP"')
  moa_builder.options.set('GTApprox/MoATechnique', 'GP')
  #[4-3]
  print('Set type of covariance matrix to "Full"')
  moa_builder.options.set('GTApprox/MoACovarianceType', 'full')
  print("Define possible number of clusters")
  number_of_clusters = np.arange(2, 11)
  moa_builder.options.set('GTApprox/MoANumberOfClusters', number_of_clusters)

  #[4-4] train model
  print('='*50)
  print("Building MoA model...")
  moa_model = moa_builder.build(x_sample, y_sample)
  #[4-4]

  #[4-5] build single approximation
  print('Initialize and configure GTApprox model for single approximation.')
  gtapprox_builder = gtapprox.Builder()
  print('Set logger.')
  gtapprox_builder.set_logger(logger)
  print('Set logging level to Info.')
  gtapprox_builder.options.set('GTApprox/LogLevel', 'Info')
  print('Set approximation technique to "GP"')
  gtapprox_builder.options.set('GTApprox/Technique', 'GP')

  print('='*50)
  print("Building single surrogate model...")
  gtapprox_model = gtapprox_builder.build(x_sample, y_sample)
  #[4-5]

  #[4-6] make prediction and calculate errors
  # get data for test

  x_test_sample = np.random.rand(1000, 2) * 2 - 1
  y_test_sample = function(x_test_sample)
  print("Making prediction...")
  moa_prediction = moa_model.calc(x_test_sample)
  gtapprox_prediction = gtapprox_model.calc(x_test_sample)
  print("Calculating errors...")
  gtapprox_errors = rms(gtapprox_prediction, y_test_sample)
  moa_errors = rms(moa_prediction, y_test_sample)
  print("MoA rms error: %s" % moa_errors)
  print("GP rms error: %s" % gtapprox_errors)
  #[4-6]

  #[4-7]
  print("Plotting figures...")
  plot(x_sample, y_sample, model_name='TrueFunction')
  plot(x_sample, y_sample, moa_model, 'MoA')
  plot(x_sample, y_sample, gtapprox_model, 'GP')
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    pyplot.show()
  #[4-7]

#[4]

if __name__ == "__main__":
  main()

