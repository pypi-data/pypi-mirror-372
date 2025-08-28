#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
This example illustrates the usage of check dependence functionality for various types of dependences.
You can change the technique and compare results.
"""
import os
import numpy as np
from matplotlib import pyplot as plt
from da.p7core import gtsda

def benchmark_generate_samples(n, key):
  x = np.random.random(size=n)-0.5
  if key == 0:
    y = x
  elif key == 1:
    y = 0.7 * x + 0.3 * (np.random.random(n) - 0.5)
  elif key == 2:
    y = 0.3 * x + 0.7 * (np.random.random(n) - 0.5)
  elif key == 3:
    y = 0. * x + 0.9 * (np.random.random(n) - 0.5)
  elif key == 4:
    y = -0.3 * x + 0.7 * (np.random.random(n) - 0.5)
  elif key == 5:
    y = -0.8 * x + 0.2 * (np.random.random(n) - 0.5)
  elif key == 6:
    y = -x
  elif key == 7:
    y = x
  elif key == 8:
    y = 0.5 * x
  elif key == 9:
    y = 0.2 * x
  elif key == 10:
    y = np.zeros(n)
  elif key == 11:
    y = -0.2 * x
  elif key == 12:
    y = -0.5 * x
  elif key == 13:
    y = -x
  elif key == 14:
    y = 0.7 * (0.7 * np.cos(x * 3 * np.pi) + 1. * (np.random.random(n) - 0.5))
  elif key == 15:
    x_ = x
    y_ = np.random.random(n) - 0.5
    alpha = np.arctan(0.3)
    x = x_ * np.cos(alpha) + y_ * np.sin(alpha)
    y = x_ * np.sin(alpha) - y_ * np.cos(alpha)
  elif key == 16:
    x_ = x
    y_ = np.random.random(n) - 0.5
    alpha = np.pi / 4.
    x = x_ * np.cos(alpha) + y_ * np.sin(alpha)
    y = x_ * np.sin(alpha) - y_ * np.cos(alpha)
  elif key == 17:
    y = 3 * (0.9 * x**2 + 0.3 * (np.random.random(n))) - 0.5
  elif key == 18:
    y = 3 * (0.9 * x**2 + 0.15 * (np.random.random(n)))
    for s in range(n):
      if np.random.randint(2) == 0:
        y[s] *= -1
  elif key == 19:
    phi = x * 2 * np.pi
    r = 0.8 * (1. + 0.3 * (np.random.random(n) - 0.5))
    x = r * np.cos(phi)
    y = r * np.sin(phi)
  elif key == 20:
    phi = x * 2. * np.pi
    r = np.random.random(n)*0.3
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    for s in range(n):
      a = np.random.randint(4)
      if a == 0 or a == 1:
        y[s] = y[s] + 0.5
      else:
        y[s] = y[s] - 0.5
      if a == 0 or a == 2:
        x[s] = x[s] - 0.5
      else:
        x[s] = x[s] + 0.5
  elif key == 21:
    y = 0.7 * (0.9 * np.cos(x * 3. * np.pi) + 0.1 * (np.random.random(n) - 0.5))
  elif key == 22:
    x_ = x
    y_ = np.random.random(n) - 0.5
    alpha = np.arctan(0.3)
    x = x_ * np.cos(alpha) + y_ * np.sin(alpha)
    y = (x_ * np.sin(alpha) - y_ * np.cos(alpha))/2.
  elif key == 23:
    x_ = x
    y_ = np.random.random(n) - 0.5
    alpha = np.pi / 4.
    x = x_ * np.cos(alpha) + y_ * np.sin(alpha)
    y = (x_ * np.sin(alpha) - y_ * np.cos(alpha)) / 4.
  elif key == 24:
    y = 3 * (0.95 * x**2 + 0.05 * (np.random.random(n))) - 0.5
  elif key == 25:
    y = 3 * (0.95 * x**2 + 0.01 * (np.random.random(n)))
    for s in range(n):
      if np.random.randint(2) == 0:
        y[s] *= -1
  elif key == 26:
    phi = x * 2 * np.pi
    r = 0.8 * (1. + 0.1 * (np.random.random(n) - 0.5))
    x = r * np.cos(phi)
    y = r * np.sin(phi)
  elif key == 27:
    phi = x * 2. * np.pi
    r = np.random.random(n)*0.2
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    for s in range(n):
      a = np.random.randint(4)
      if a == 0 or a == 1:
        y[s] = y[s] + 0.5
      else:
        y[s] = y[s] - 0.5
      if a == 0 or a == 2:
        x[s] = x[s] - 0.5
      else:
        x[s] = x[s] + 0.5

  return x.reshape(-1, 1), y.reshape(-1, 1)

def calc_correlation(x, y, corrtype):
  analyzer = gtsda.Analyzer()
  options = {'gtsda/checker/technique':corrtype, 'gtsda/checker/pvalues/enable':False}
  analyzer.options.set(options)

  return analyzer.check(x, y).scores[0][0]

def make_big_plot(corrtype='distancecorrelation', save=False):
  fig = plt.figure(figsize=(21, 12))
  fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.4, hspace=0.4)
  for k in range(28):
    x, y = benchmark_generate_samples(1000, k)
    plt.subplot(4, 7, 1 + k)
    plt.axis([-1, 1, -1, 1])
    plt.scatter(x, y, marker='.', color='b')

    printedvalue = calc_correlation(x, y, corrtype)
    print("Sample #%d, score: %s" % (k, printedvalue))

    plt.text(-0.8, 0.8, str(round(printedvalue, 15)), color='r')
  if save == True:
    plt.savefig('example_gtsda_checker_'+corrtype + '.png')
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    plt.show()


if __name__ == "__main__":
  make_big_plot(corrtype="distancecorrelation", save=True)
