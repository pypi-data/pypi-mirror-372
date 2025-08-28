#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import random
import numpy as np

from ..six.moves import xrange, range
from .utilities import _interrupt, _factorize_covariance, _calculate_kurtosis_coefficient, _calculate_skewness_coefficient, _find_minimum_spanning_tree, _find_principal_components
from ..utils import _normal, _chi2
from .. import shared as _shared
from numpy.random import RandomState

def _format_test_result(is_uniform):
  return {'uniform': is_uniform}

def _check_uniformity(sample, confidence_level=0.99, method='all', max_budget=pow(10, 9)):
  """
  Implements test on uniformity.
  """
  sample = np.array(sample, dtype=np.float64, ndmin=2)
  number_points = len(sample)
  number_dimensions = _shared.get_size(sample[0])

  possible_number_points = int(min(round(max_budget / number_dimensions), number_points))
  if number_points > possible_number_points:
    subsample_indexes = random.sample(range(number_points), possible_number_points)
    subsample = sample[subsample_indexes, :]
  else:
    subsample = sample

  is_uniform = True
  if (number_points <= 1) or (number_dimensions == 0):
    return _format_test_result(is_uniform)

  min_coordinate = sample.min(axis=0)
  max_coordinate = sample.max(axis=0)

  elementary_interval = (max_coordinate - min_coordinate) / (number_points - 1)
  min_boundary = min_coordinate - elementary_interval
  max_boundary = max_coordinate + elementary_interval
  sample_range = elementary_interval * (number_points + 1)
  if any(sample_range == 0.):
    is_uniform = False
    return _format_test_result(is_uniform)
  subsample = (subsample - min_boundary) / sample_range

  if method not in ['minimum_spanning_tree', 'discrepancy']:
    if number_dimensions > 4:
      method = 'discrepancy'
    else:
      method = 'minimum_spanning_tree'

  if method == 'discrepancy':
    is_uniform = _discrepancy_test(subsample, confidence_level)
  elif method == 'minimum_spanning_tree':
    is_uniform = _calculate_mst_stastistic(subsample, confidence_level)

  return _format_test_result(is_uniform)

def _discrepancy_test(sample, confidence_level=0.99):
  """Implements L^2-type discrepancies test on uniformity.
  """
  sample = np.array(sample, dtype=np.float64, ndmin=2)
  number_points = len(sample)
  number_dimensions = _shared.get_size(sample[0])

  def U_1_for_point(point):
    return np.vectorize(lambda x: (3. - pow(x, 2))/ 2.)(point).prod()

  U_1 = _shared.fsum([U_1_for_point(_) for _ in sample]) / number_points

  def U_2_for_pair(first, second):
    if first < second:
      max_column_vals = sample[[first, second], :].max(axis=0)
      return (2. - max_column_vals).prod()
    else:
      return 0.
  U_2 = _shared.fsum((U_2_for_pair(first, second) for first, second in _shared.product(xrange(number_points), repeat=2)))
  U_2 = float(U_2 * 2) / (number_points * (number_points - 1))

  M_pow_d = pow(4. / 3., number_dimensions)
  xi_1 = pow(9. / 5., number_dimensions) - pow(16. / 9., number_dimensions)

  A_n = float(pow(number_points, 0.5) * (U_1 + 2 * U_2 - 3 * M_pow_d)) / (5 * pow(xi_1, 0.5))

  normal_distribution = _normal()
  upper_tail = normal_distribution.quantile((1.0 - confidence_level) / 2, complement=True)

  is_uniform = True
  if abs(A_n) > upper_tail:
    is_uniform = False

  return is_uniform

def _calculate_mst_stastistic(sample, confidence_level=0.99):
  """Implements minimum spanning tree test on uniformity.
  """
  sample = np.array(sample, dtype=np.float64, ndmin=2)
  number_points = len(sample)
  number_dimensions = len(sample[0])

  lower_bound = 0
  upper_bound = 1

  random_flow = RandomState(1234567809)
  uniform_sample = random_flow.uniform(lower_bound, upper_bound, (number_points, number_dimensions))

  full_sample = np.concatenate((sample, uniform_sample), axis=0)

  nodes = list()
  for node_number in xrange(number_points * 2):
    nodes.append(node_number)

  edges = list()
  for first_node in xrange(number_points * 2):
    for second_node in xrange(first_node):
      edges.append((second_node, first_node, np.dot(full_sample[first_node, :] - full_sample[second_node, :],
                                                    full_sample[first_node, :] - full_sample[second_node, :])))

  minimum_spanning_tree, _ = _find_minimum_spanning_tree(nodes, edges)

  mst_statistic = 0
  for edge_number in xrange(number_points * 2 - 1):
    if ((minimum_spanning_tree[edge_number][0] >= number_points) and (minimum_spanning_tree[edge_number][1] < number_points) or
        (minimum_spanning_tree[edge_number][0] < number_points) and (minimum_spanning_tree[edge_number][1] >= number_points)):
      mst_statistic += 1

  mst_statistic = float(mst_statistic - number_points - 1) / pow(float(number_points * (number_points - 1)) / float(2 * number_points - 1), 0.5)

  normal_distribution = _normal()
  upper_tail = normal_distribution.quantile((1.0 - confidence_level) / 2, complement=True)

  is_uniform = True
  if abs(mst_statistic) > upper_tail:
    is_uniform = False

  return is_uniform

def _choose_principal_components(eigenvalues, condition_number=10**10):
  """ chooses eigenvalues which are not too small """
  small_positive_number = 10**(-10)
  largest_eigenvalue = max(max(eigenvalues), small_positive_number)
  is_principal = (eigenvalues * condition_number > largest_eigenvalue)
  return is_principal

def _get_reduced_sample(score, is_principal):
  """ get coordinates in embedded space """
  return score[:, is_principal]

def _check_normality(sample, confidence_level=0.95, max_budget=pow(10, 9)):
  """Implements test on normality
  """
  sample = np.array(sample, dtype=np.float64, ndmin=2)

  coefficients, scores, eigenvalues = _find_principal_components(sample)
  is_principal = _choose_principal_components(eigenvalues)
  are_features_strongly_correlated = False
  if any(is_principal == False):
    reduced_sample = _get_reduced_sample(scores, is_principal)
    are_features_strongly_correlated = True
  else:
    reduced_sample = sample

  number_points, number_dimensions = reduced_sample.shape

  possible_number_points = int(min(round(max_budget / number_dimensions), number_points))
  if number_points > possible_number_points:
    subsample_indexes = random.sample(range(number_points), possible_number_points)
    subsample = reduced_sample[subsample_indexes, :]
  else:
    subsample = reduced_sample

  number_points = subsample.shape[0]

  means = subsample.mean(axis=0)
  centered_data = np.subtract(subsample, means)

  covariances = np.zeros((number_dimensions, number_dimensions))
  for first_dimension in range(0, number_dimensions):
    if not _interrupt():
      for second_dimension in range(0, number_dimensions):
        dot_product = np.multiply(centered_data[:, first_dimension], centered_data[:, second_dimension])
        covariances[first_dimension, second_dimension] = (covariances[first_dimension, second_dimension] + \
                                                         _shared.fsum(dot_product)) / max(1, number_points - 1)
    else:
      return {}

  factorized_covariances = _factorize_covariance(covariances)
  kurtosis_coefficient = _calculate_kurtosis_coefficient(centered_data, factorized_covariances, True) / float(number_points)
  skewness_coefficient = _calculate_skewness_coefficient(centered_data, factorized_covariances, True) / float(pow(number_points, 2))

  k = float(((number_dimensions + 1) * (number_points + 1) * (number_points + 3))) / float((number_points * (((number_points + 1) * (number_dimensions + 1)) - 6))) # Small sample correction
  v = (number_dimensions * (number_dimensions + 1) * (number_dimensions + 2)) / 6 # Degrees of freedom

  if number_points < 400:
    g1 = (number_points * skewness_coefficient * k) / 6            # Skewness test statistic corrected for small sample (approximates to a chi-square distribution)
  else:
    g1 = (number_points * skewness_coefficient) / 6               # Skewness test statistic (approximates to a chi-square distribution)


  degrees_freedom = v
  chi2_distribution = _chi2(degrees_freedom)
  target_quantile = chi2_distribution.quantile(1.0 - confidence_level, complement=True)

  is_normal_skewness = (g1 < target_quantile)


  g2 = (kurtosis_coefficient - (number_dimensions * (number_dimensions + 2))) / (pow((8. * number_dimensions * (number_dimensions + 2)) / number_points, 0.5)) # Kurtosis test statistic (approximates to a unit-normal distribution)
  is_normal_kurtosis = (abs(g2) < 1.644853626951) # 1.644853626951 - 0.005 quantile of N(0, 1)


  test_normality_result = {'normal_skewness': is_normal_skewness,
                           'normal_kurtosis': is_normal_kurtosis}

  return test_normality_result, are_features_strongly_correlated
