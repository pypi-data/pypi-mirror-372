#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
This example illustrates the fundamental usage of correlation analysis in treating high-dimensional
problems. Commonly used Pearson correlation fails to correctly detect dependency in this case.
This difficulty is solved by using partial Pearson correlation. The difference is due to the fact
that the method excludes the possible influence of other inputs when calculating correlation between
the considered input and output.
"""
#[0]

from da.p7core import gtsda
import os
import numpy as np

#[m1]
def run():
  dirpath = os.path.dirname(__file__)
  filepath = os.path.join(dirpath, 'TAXI2000.csv')
  print("Load data from %s" % filepath)

  data = np.loadtxt(filepath, delimiter=",")

  x = data[:, :-1]
  y = data[:, -1:]

#[m2]

  print('Create analyzer object.')
  print('The Pearson partial correlation will be used in current case.')
  analyzer = gtsda.Analyzer()

  print('Compute score values...')

  scores_partial = []
  scores_pearson = []
  for input_index in range(x.shape[1]):
    z = np.hstack((x[:,:input_index], x[:, (input_index + 1):])) # let other x columns be the explanatory variables matrix

    # Calculate scores with partial Pearson correlation coefficient
    result = analyzer.check(x=x[:, input_index], y=y, z=z, options={'GTSDA/Checker/Technique': 'PearsonPartialCorrelation'})
    # use only statistically significant correlations
    if result.decisions[0, 0]:
      scores_partial.append(np.fabs(result.scores[0, 0]))
    print(' feature #%-3d: partial Pearson score=%-15.5g p-value=%-15.5g decision: %d' % (1 + input_index, result.scores[0, 0], result.p_values[0, 0], result.decisions[0, 0]))

    # Calculate scores with Pearson correlation coefficient
    result = analyzer.check(x=x[:, input_index], y=y, z=z, options={'GTSDA/Checker/Technique': 'PearsonCorrelation'})
    # use only statistically significant correlations
    if result.decisions[0, 0]:
      scores_pearson.append(np.fabs(result.scores[0, 0]))
    print(' feature #%-3d:         Pearson score=%-15.5g p-value=%-15.5g decision: %d' % (1 + input_index, result.scores[0, 0], result.p_values[0, 0], result.decisions[0, 0]))
    print('')
#[m3]

  # Convert correlation coefficients to sorted list of scores
  scores_partial = sorted(scores_partial, reverse=True)
  scores_pearson = sorted(scores_pearson, reverse=True)

  print('\nTotal features number: %d' % x.shape[1])
  print('The number of statistically significant scores based on the partial Pearson correlation coefficients: %d' % len(scores_partial))
  print('The number of statistically significant scores based on the Pearson correlation coefficients: %d\n' % len(scores_pearson))

  print('Statistically significant scores based on the partial Pearson correlation coefficients: %s\n' % scores_partial)
  print('Statistically significant scores based on the Pearson correlation coefficients: %s\n' % scores_pearson)

  plot(scores_partial, scores_pearson)

#[m4]
def plot(scores_partial, scores_pearson):
  try:
    import matplotlib.pyplot as plt

    print('Plotting...')
    # GTSDA scores
    plt.subplot(111)
    features_number = max(len(scores_partial), len(scores_pearson))
    plt.scatter(np.arange(1, 1 + len(scores_partial)), scores_partial, s=10, c='r', label='Pearson partial correlation')
    plt.scatter(np.arange(1, 1 + len(scores_pearson)), scores_pearson, s=10, c='b', label='Pearson correlation')
    plt.xlabel('Feature number')
    plt.ylabel('Statistically significant score')
    plt.grid(True)
    plt.legend(loc='best')
    # save and show plots
    name = 'gtsda_example_checker_partial'
    plt.savefig(name)
    print('Plots are saved to %s.png' % os.path.join(os.getcwd(), name))
    print('On the plot we see that relative score values closely resemble the index of variability.')
    print('From this plot one may conclude that there are only 12 important variables in the considered region and the rest 151 may be dropped in the analysis.')
    if 'SUPPRESS_SHOW_PLOTS' not in os.environ:
      plt.show()
  except ImportError:
    print('Plotting is not available due to the matplotlib library absence.')

#[m0]
if __name__ == "__main__":
  # run GTSDA example
  run()
