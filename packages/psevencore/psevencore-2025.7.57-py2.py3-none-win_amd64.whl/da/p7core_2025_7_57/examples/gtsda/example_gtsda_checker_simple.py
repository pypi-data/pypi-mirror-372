#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from da.p7core import gtsda

import numpy as np

def run_example():
  """Example of correlation analysis for simple linear data
  """
  # prepare data
  number_points = 50
  number_dimensions = 2
  x = np.random.rand(number_points, number_dimensions)
  y = -0.3 * x[:, 0] + x[:, 1] + 0.05 * np.random.rand(number_points)

  print('Original dependency is: y = -0.3 * x1 + x2 + 0.05 * random()')
  print('The number of points is %d' % number_points)
  print('')

  # create GTSDA Analyzer object
  analyzer = gtsda.Analyzer()

  # perform checking procedure with default options
  result_default = analyzer.check(x=x, y=y)

  print('Results of correlation analysis with default options:')
  print('=====================================================')
  print('scores:    %s' % result_default.scores)
  print('p_values:  %s' % result_default.p_values)
  print('decisions: %s' % result_default.decisions)
  print('\n')

  # run checking procedure with Person correlation and asymptotic estimation of the p-value
  options = {'GTSDA/Checker/Technique': 'PearsonCorrelation', 'GTSDA/Checker/PValues/Method': 'Asymptotic'}
  result_asymp = analyzer.check(x=x, y=y, options=options)

  print('Results of correlation analysis with Pearson correlation\ncoefficient and "Asymptotic" estimation of the p-value:')
  print('========================================================')
  print('scores:    %s' % result_asymp.scores)
  print('p_values:  %s' % result_asymp.p_values)
  print('decisions: %s' % result_asymp.decisions)
  print('\n')

  # run checking procedure with Person correlation and permutations estimation of the p-value
  options = {'GTSDA/Checker/Technique': 'PearsonCorrelation', 'GTSDA/Checker/PValues/Method': 'Permutations'}
  result_permut = analyzer.check(x=x, y=y, options=options)

  print('Results of correlation analysis with Pearson correlation\ncoefficient and "Permutations" estimation of the p-value:')
  print('========================================================')
  print('scores:    %s' % result_permut.scores)
  print('p_values:  %s' % result_permut.p_values)
  print('decisions: %s' % result_permut.decisions)
  print('\n')

  # compute checking procedure with partial correlation coefficient
  # Note partial correlations require explicit explanatory variable
  options = {'GTSDA/Checker/Technique': 'PearsonPartialCorrelation'}

  # Let us calculate correlation between components of x and y while the other components of x are used as explanatory variables
  partial_scores = np.empty((1, number_dimensions)) # 1 is the number of outputs
  partial_p_values = np.empty((1, number_dimensions))
  partial_decisions = np.empty((1, number_dimensions))
  for input_index in range(number_dimensions):
    z = np.hstack((x[:,:input_index], x[:, (input_index + 1):]))
    result_partial_i = analyzer.check(x=x[:, input_index], y=y, z=z, options=options)
    partial_scores[:, input_index] = result_partial_i.scores
    partial_p_values[:, input_index] = result_partial_i.p_values
    partial_decisions[:, input_index] = result_partial_i.decisions

  print('Results of correlation analysis with partial correlation coefficient:')
  print('=====================================================================')
  print('scores:    %s' % partial_scores)
  print('p_values:  %s' % partial_p_values)
  print('decisions: %s' % partial_decisions)
  print('\n')

def main():
  """
  Example of GTSDA Checker usage.
  """
  print('=' * 80)
  run_example()
  print('=' * 80)

if __name__ == "__main__":
  main()
