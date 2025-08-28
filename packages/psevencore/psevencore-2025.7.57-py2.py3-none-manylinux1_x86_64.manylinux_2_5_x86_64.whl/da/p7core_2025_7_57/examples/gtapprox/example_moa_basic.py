#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Basic MOA usage example"""

#[0] required imports
from da.p7core import gtapprox, loggers

from matplotlib import pyplot, cm, lines
from mpl_toolkits.mplot3d import Axes3D

import numpy  as np

import random

import os
#[0] imports end

#[1] function to be approximated
def branin(x):
  x1 = 15 * x[:, 0] - 5
  x2 = 15 * x[:, 1]
  Y = (x2 - 5.1 / 4 / np.pi**2 * x1**2 + 5 / np.pi * x1 - 6)**2 + 10 * (1 - 1 / 8 / np.pi) * np.cos(x1) + 10
  return Y
#[1]

def main():
  #[2] prepare data
  dim = 2

  x_sample = np.random.rand(30, dim)
  y_sample = branin(x_sample)
  #[2]

  #[3]
  builder = gtapprox.Builder()
  builder.options.set('GTApprox/Technique', 'MoA')
  #[3]

  #[4]
  info_stdout_logger = loggers.StreamLogger()
  builder.set_logger(info_stdout_logger)
  #[4]

  #[5]
  builder.options.set('GTApprox/MoACovarianceType', 'Full')
  number_of_clusters = [1, 2, 3]
  builder.options.set('GTApprox/MoANumberOfClusters', number_of_clusters)
  #[5]

  #[6]
  model = builder.build(x_sample, y_sample)
  #[6]

  #[7]
  model.save('moa_model.gta')
  loaded_model = gtapprox.Model('moa_model.gta')
  #[7]

  #[8] print model information
  print('----------- Model -----------')
  print('SizeX: %d' % loaded_model.size_x)
  print('SizeF: %d' % loaded_model.size_f)
  print('Model has AE: %s' % loaded_model.has_ae)
  print('----------- Info -----------')
  print(str(loaded_model))
  #[8]


  #[9] create test sample
  sSize = 7
  test_xsample = [[random.uniform(0., 1.) for i in range(dim)] for j in range(sSize)]

  # calculate and display approximated values
  for x in test_xsample:
    y = loaded_model.calc(x)
    print('Model Y: %s' % y)
  #[9]

  #[10] calculate and display gradients
  for x in test_xsample:
    dy = loaded_model.grad(x, gtapprox.GradMatrixOrder.F_MAJOR)
    print('Model gradient: %s' % dy)
  #[10]

  #[11]
  x = np.arange(0, 1, 0.02)
  y = np.arange(0, 1, 0.02)
  x, y = np.meshgrid(x, y)
  x1 = x.reshape(x.shape[0] * x.shape[1], 1)
  x2 = y.reshape(y.shape[0] * y.shape[1], 1)
  grid_points = np.append(x1, x2, axis = 1)
  z = model.calc(grid_points)
  z = z.reshape(x.shape)

  # plot figure
  fig, ax = pyplot.subplots(subplot_kw=dict(projection='3d'))
  fig.suptitle('MoA basic', fontsize = 18)
  ax.plot_surface(x, y, z, rstride = 2, cstride = 2, cmap = cm.jet, alpha = 0.5)
  ax.scatter3D(np.array(x_sample)[:, 0], np.array(x_sample)[:, 1], y_sample, alpha = 1.0, c ='r',
               marker='o', linewidth = 1, s = 100)
  scatter_proxy = lines.Line2D((0, 0), (1, 1), marker = '.', color = 'r', linestyle = '', markersize = 10)
  ax.set_xlabel('$x_1$', fontsize ='16')
  ax.set_ylabel('$x_2$', fontsize ='16')
  ax.legend([scatter_proxy],['training points'], loc = 'best')
  ax.view_init(elev=30, azim=-60)

  fig.savefig('example_gtapprox_moa')
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    pyplot.show()
  #[11]

if __name__ == "__main__":
  main()
