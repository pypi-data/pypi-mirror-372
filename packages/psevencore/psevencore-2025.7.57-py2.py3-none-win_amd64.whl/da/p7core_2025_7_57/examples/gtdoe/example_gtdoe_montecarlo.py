#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Example of Monte Carlo integration of multidimensional integral using GTDoE for sample points generation. The result of such integration is highly dependent on the random point generation method. In this example we test available sequential GTDoE techniques and show that sequential techniques with low discrepancy give much better accuracy than plain random sampling.
"""

#[0]
from da.p7core import gtdoe
from da.p7core.loggers import StreamLogger

import os
import numpy as np
import matplotlib.pyplot as plt
#[0]

#[1]
seqTechniqes = {'RandomSeq' : u'Random sampling',
                'SobolSeq' : u'Sobol sequence',
                'FaureSeq' : u'Faure sequence',
                'HaltonSeq' : u'Halton sequence'}
#[1]

#[m1]
def monteCarloIncremental(dim, maxPoints, step):
#[m2]
  print('=' * 50)
  print('Run GTDoE MonteCarlo example with the following inputs: ')
  print('Dimension: %s' % dim)
  print('Number of points: %s' % maxPoints)
  print('Step: %s' % step)
  print('Techniques: %s' % list(seqTechniqes.keys()))
  print('=' * 50)
  print('Calculating exact value of the integral.')
  correctValue  = np.prod([np.sin(i+1) for i in range(dim)])
  print("Correct value: %f" % correctValue)

#[m3]
  techDrivers = {}
  pointGens   = {}
  techY       = {}
  sums        = {}

  print('Create a generator for each DoE technique.')
  bounds = ([0.] *dim, [1.] *dim)
  for tech in seqTechniqes:
    # initialize generator
    techDrivers[tech] = gtdoe.Generator()
    # set options
    techDrivers[tech].options.set('GTDoE/Seed', '100')
    techDrivers[tech].options.set('GTDoE/Deterministic', True)
    techDrivers[tech].options.set('GTDoE/Technique', tech)
    # generate points
    pointGens[tech] = techDrivers[tech].generate(bounds)
    sums[tech] = 0.0
    techY[tech] = []
#[m4]
  deltaPoints = step
  totalPoints = 0

  print('Perform Monte Carlo integration using different techniques.')
  pointsArray = []
  while totalPoints <= maxPoints:
    print('Points: %d / %d          \r' % (totalPoints, maxPoints))
    for (tech, name) in seqTechniqes.items():
      points = pointGens[tech].take(deltaPoints)
      value = np.sum(np.prod(np.array([(i+1.0) *np.cos((i+1.0)*points[:,i]) for i in range(dim)]).T, axis=1) / deltaPoints)
      sums[tech] = sums[tech] + value
      techY[tech].append(np.abs(sums[tech] / (totalPoints / deltaPoints + 1) - correctValue))
    totalPoints = totalPoints + deltaPoints
    pointsArray.append(totalPoints)
#[m5]
  # print and visualize results
  plt.figure(0, figsize=(9, 8), dpi=100)

  for tech in sorted(seqTechniqes.keys()):
    print('Technique "%s", result: %f' % (seqTechniqes[tech], sums[tech] / (totalPoints / deltaPoints)))
    coeff = np.polyfit(pointsArray, techY[tech], 1)
    yV = [np.polyval(coeff, x) for x in pointsArray[:-10]]
    plt.semilogy(pointsArray[:-10], yV, label = seqTechniqes[tech])

  # configure plot
  plt.legend(loc = 'best')
  plt.ylabel(u'Error')
  plt.xlabel(u'N')
  plt.title(u'Monte Carlo integration, dimensionality: %d' % dim)
  name = 'doe_montecarlo_' + str(dim)
  plt.savefig(name)
  print('Plot is saved to %s.png' % os.path.join(os.getcwd(), name))
  if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
    print('Close window to continue script.')
    plt.show()
#[m6]

#[m0]
if __name__ == "__main__":
  """
  Example of Monte Carlo integration with GTDoE.
  """
  #3 dimensions, 1000 points
  monteCarloIncremental(3, 1000, 20)

  #5 dimensions, 15000 points
  monteCarloIncremental(5, 15000, 500)
#[m0]
