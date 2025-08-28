#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import copy
import numpy as np

from .. import exceptions as _ex
from .. import shared as _shared
from ..six.moves import xrange, range, reduce, zip

def _generate_orthogonal_array(bounds, points_number, categorical_variables, levels_number, max_iterations, multistart_iterations, seed, sift_logger):
  """
  Generate a Orthogonal Array DoE with Python.

  :param bounds: design space bounds
  :type bounds: ``tuple(list(float), list(float))``
  :param points_number: number of points to generate)
  :type points_number: ``int``, ``long``
  :param categorical_variables: list of pairs (not tuples): 0-based index of categorical variable followed by list of categorical levels
  :type categorical_variables: ``list``
  :param levels_number: required levels number for DoE
  :type levels_number: ``string`` with a list of ints
  :param max_iterations: max iterations per dimension
  :type max_iterations: ``int'', ``short''
  :param multistart_iterations: max number of multistart iterations
  :type multistart_iterations: ``int'', ``short''
  :param seed: seed to fix randomness
  :type seed: ``int``, ``long``
  :param sift_logger: :ref:`logger <Logger>` object
  :return: info, points
  :rtype: dict, numpy.ndarray

  """
  factors_number = len(bounds[0])
  if factors_number < 2:
    raise _ex.InvalidProblemError("Orthogonal arrays are constructed only if the number of factors is greater or equal than two.")
  if factors_number > 50:
    raise _ex.InvalidProblemError("Orthogonal arrays are constructed only if the number of factors is lower or equal than fifty.")
  maximum_points_number = 150
  if points_number > maximum_points_number:
    raise _ex.InvalidProblemError("Orthogonal arrays are constructed only if the number of points is lower or equal than one hundred and fifty.")
  levels_number = np.array(_shared.parse_json(levels_number))
  if not (np.shape(levels_number)[0] == factors_number and all(levels_number > 0) and
          all(levels_number % 1 == 0) and all(levels_number <= maximum_points_number)):
    raise _ex.InvalidOptionValueError("Option 'GTDoE/OrthogonalArray/LevelsNumber' is not correct.")
  levels = get_levels(bounds, list(categorical_variables), levels_number, sift_logger)

  if reduce(lambda a, b: a // b, levels_number, points_number - 1):
    raise _ex.InvalidProblemError('"Count"=%d should be less or equal than the number of points in full factorial design determined by "GTDoE/OrthogonalArray/LevelsNumber": %d.'
                                  %(points_number, np.prod(levels_number)))

  factors_decreasing_order = np.argsort(levels_number)
  factors_decreasing_order = factors_decreasing_order[::-1]
  sorted_levels_number = levels_number[factors_decreasing_order]
  N_min = 1
  for first_factor in xrange(len(levels_number)):
    for second_factor in xrange(first_factor):
      N_min = lcm(N_min, sorted_levels_number[first_factor] * sorted_levels_number[second_factor])
  N_max = 1
  for factor in xrange(len(levels_number)):
    N_max = min(N_max * sorted_levels_number[factor], maximum_points_number)
  if N_min > N_max:
    raise _ex.InvalidProblemError("Options conflict. The interval [%d, %d] of count possible values is empty. Such interval is based on 'GTDoE/OrthogonalArray/LevelsNumber'."
                                  %(N_min, N_max))
  if N_min > points_number or N_max < points_number:
    raise _ex.InvalidProblemError("Options conflict. Points count= %d should be from [%d, %d]. Such interval is based on 'GTDoE/OrthogonalArray/LevelsNumber'."
                                  %(points_number, N_min, N_max))
  user_defined_points_number = points_number
  points_number = N_min * (points_number // N_min)
  if points_number != user_defined_points_number:
    sift_logger.warn("Options conflict. The least common multiple %d among pair product of 'GTDoE/OrthogonalArray/LevelsNumber' values isn't a divider of the points_number=%d. Points_number is replased by %d" %(N_min, user_defined_points_number, points_number))
  info = {}
  is_precalculated, points = get_precalculated_design(points_number, sorted_levels_number)
  if is_precalculated:
    weights = sorted_levels_number
    lower_bounds = calculate_lower_bounds(sorted_levels_number, weights, points_number)
    J2 = calculate_J2(points, weights, factors_number + 1)
    good_columns_number = factors_number
    penalty_best = 0
  else:
    is_in_full_factorial = np.array([False] * factors_number)
    current_product = points_number
    sorted_levels_number = levels_number[factors_decreasing_order]
    for factor_index in xrange(factors_number):
      ratio = divmod(current_product, sorted_levels_number[factor_index])
      if ratio[1] == 0:
        current_product = ratio[0]
        is_in_full_factorial[factor_index] = True
    factors_decreasing_order = np.hstack((factors_decreasing_order[is_in_full_factorial],
                                          factors_decreasing_order[is_in_full_factorial == False]))
    sorted_levels_number = levels_number[factors_decreasing_order]
    weights = sorted_levels_number
    lower_bounds = calculate_lower_bounds(sorted_levels_number, weights, points_number)
    points = np.zeros((points_number, factors_number))
    for point_number in xrange(points_number):
      points[point_number, 0] = divmod(divmod(point_number, sorted_levels_number[1])[0], sorted_levels_number[0])[1]
      points[point_number, 1] = divmod(point_number, sorted_levels_number[1])[1]
    np.random.seed(seed)
    J2_best = np.inf # *_best is best over all multistart iterations, best_* is best for current multistart iteration and column
    penalty_best = np.inf
    for multistart_iteration in xrange(multistart_iterations):
      good_columns_number = 2
      J2 = calculate_J2(points, weights, 2)
      penalty = 0
      for column in xrange(2, factors_number):
        points[:, column:] = 0
        tempory_points = points[:, ::-1]
        tempory_points = tempory_points[np.lexsort(list(zip(*tempory_points)))]
        points = tempory_points[:, ::-1]
        current_iteration = 0
        if good_columns_number < column:
          current_max_iterations = 1
        else:
          current_max_iterations = max_iterations

        best_J2 = np.inf
        best_penalty = 0.
        while good_columns_number < column + 1 and current_iteration < current_max_iterations:
          for point_number in xrange(points_number):
            points[point_number, column] = divmod(point_number, sorted_levels_number[column])[1]
          if current_iteration > 0:
            points[:, column] = points[np.random.permutation(points_number), column]
          J2_new = J2 + calculate_J2_plus(points, sorted_levels_number, weights, column)
          possible_duplicates_number = max(1, reduce(lambda a, b: a // b, sorted_levels_number[:column+1], len(points)))
          tempory_points = points[:, ::-1]
          tempory_points = tempory_points[np.lexsort(list(zip(*tempory_points)))]
          points = tempory_points[:, ::-1]
          points_list = list(list(point) for point in points)
          equal_points_tree = EqualPointsTree(points_list, column)
          penalty_new = equal_points_tree.calculate_penalty(possible_duplicates_number)
          if J2_new + penalty_new != lower_bounds[column]:
            is_decrease = True
            while is_decrease and J2_new != lower_bounds[column]:
              is_decrease = False
              best_delta = 0
              best_delta_penalty = 0
              best_pair = (0, 0)
              for first_point in xrange(points_number):
                for second_point in xrange(first_point):
                  delta = calculate_delta(points, column, first_point, second_point, weights)
                  penalty_delta = equal_points_tree.get_delta_penalty(list(points[first_point, :column + 1]),
                                                                      list(points[second_point, :column + 1]),
                                                                      possible_duplicates_number)
                  if delta + penalty_delta > best_delta + best_delta_penalty:
                    best_delta = delta
                    best_delta_penalty = penalty_delta
                    best_pair = (first_point, second_point)
              if best_delta + best_delta_penalty > 0:
                is_decrease = True
                equal_points_tree.remove_point(list(points[best_pair[0], :column + 1]))
                equal_points_tree.remove_point(list(points[best_pair[1], :column + 1]))
                points[best_pair[0], column], points[best_pair[1], column] = points[best_pair[1], column], points[best_pair[0], column]
                equal_points_tree.insert_point(list(points[best_pair[0], :column + 1]))
                equal_points_tree.insert_point(list(points[best_pair[1], :column + 1]))
                J2_new = J2_new - 2 *  weights[column] * best_delta
                penalty_new = penalty_new - best_delta_penalty
            if J2_new + penalty_new == lower_bounds[column]:
              good_columns_number = column + 1
            elif J2_new + penalty_new < best_J2 + best_penalty:
              best_J2 = J2_new
              best_penalty = penalty_new
              best_coordinates = points[:, column]
          if J2_new + penalty_new == lower_bounds[column]:
            good_columns_number = column + 1
            current_iteration = max_iterations
          current_iteration = current_iteration + 1
        if good_columns_number < column + 1:
          points[:, column] = best_coordinates
          J2 = best_J2
          penalty = best_penalty
        else:
          J2 = J2_new
          penalty = penalty_new
      if J2 + penalty < J2_best + penalty_best:
        J2_best = J2
        penalty_best = penalty
        points_best = np.copy(points)
      if J2 + penalty == lower_bounds[-1]:
        break
    if J2 + penalty != lower_bounds[-1]:
      J2 = J2_best
      penalty = penalty_best
      points = points_best
  points[:, factors_decreasing_order] = np.copy(points)
  points = np.float32(points)
  for factor_number in xrange(factors_number):
    for point_number in xrange(len(points)):
      points[point_number, factor_number] = levels[factor_number][int(points[point_number, factor_number])]
  if good_columns_number < factors_number:
    sift_logger.warn("Constructed design is not orthogonal. Proposed design is orthogonal only for the factors " + str(np.sort(factors_decreasing_order[:good_columns_number])) + ".")
  info = dict([("Generator", {}),
               ("OrthogonalArraySummary", dict([("good columns number", good_columns_number),
                                                ("criteria value", int(J2)),
                                                ("lower bound for the criteria", int(lower_bounds[-1])),
                                                ("equal points penalty", int(penalty_best)),
                                                ("factors internal order", list(factors_decreasing_order)),
                                                ("orthogonal array for factors", list(np.sort(factors_decreasing_order[:good_columns_number])))]))])
  tempory_points = points[:, ::-1]
  tempory_points = tempory_points[np.lexsort(list(zip(*tempory_points)))]
  points = tempory_points[:, ::-1]
  return info, points

def get_levels(bounds, categorical_variables, levels_number, sift_logger):
  """
  Get required number of levels for each factor.

  :param bounds: design space bounds
  :type bounds: ``tuple(list(float), list(float))``
  :param categorical_variables: describes categorical variables
  :type categorical_variables: list in JSON format
  :param levels_number: required levels number for DoE
  :type levels_number: list of ints
  :param logger: :ref:`logger <Logger>` object
  :return: levels
  :rtype: ``numpy.ndarray``

  """

  factors_number = len(bounds[0])
  levels = [np.linspace(bounds[0][factor_number], bounds[1][factor_number], levels_number[factor_number]) for factor_number in xrange(factors_number)]
  for categorical_factor in xrange(len(categorical_variables) // 2):
    number_levels = len(categorical_variables[2 * categorical_factor + 1])
    if number_levels == levels_number[categorical_variables[2 * categorical_factor]]: # check if 0 levels are prohibited
      levels[categorical_variables[2 * categorical_factor]] = categorical_variables[2 * categorical_factor + 1]
    else:
      raise _ex.InvalidProblemError("Categorical factor %d from 'GTDoE/CategorialVariables' contains %d levels. But the required by 'GTDoE/OrthogonalArray/LevelsNumber' is %d."
                                    %(categorical_variables[2 * categorical_factor],
                                     number_levels,
                                     levels_number[categorical_variables[2 * categorical_factor]]))
  return levels

def calculate_lower_bounds(levels_number, weights, points_number):
  """ Calculates lower bounds for J2 criteria.

  :param levels_number: required levels number for DoE
  :type levels_number: list of ints
  :param weights: weights for factors
  :type weights: list of ints
  :param points_number: number of points to generate)
  :type points_number: ``int``, ``long``
  :return: lower_bounds
  :rtype: ``numpy.ndarray``

  """
  factors_number = len(levels_number)
  lower_bounds = np.zeros((factors_number, 1))
  for factor in xrange(1, factors_number):
    first_term = 0
    second_term = 0
    for element in xrange(factor + 1):
      first_term = first_term + points_number // levels_number[element] * weights[element]
      second_term = second_term + (levels_number[element] - 1) * (points_number // levels_number[element] * weights[element])**2
    lower_bounds[factor] = 0.5 * (first_term**2 + second_term - points_number * (np.sum(weights[:(factor + 1)]))**2)

  return lower_bounds

def get_precalculated_design(points_number, levels_number):
  """ Get precalculated design if it is in the base

  :param points_number: number of points to generate)
  :type points_number: ``int``, ``long``
  :param levels_number: required levels number for DoE
  :type levels_number: list of "int" with a list of ints
  :return: is_precalcilated, points
  :rtype: boolean, numpy.ndarray
  """
  precalculated_points_number = [18, 25, 27, 32, 32, 50]
  precalculated_factors_number = [list(range(3, 9)), # L18
                                  list(range(2, 7)), # L25
                                  list(range(9, 14)), # L27
                                  list(range(16, 32)), # L32
                                  list(range(6, 11)), # L32'
                                  # list(range(15, 24)), # L36
                                  list(range(7, 13))] # L50'''
  precalculated_levels_number = [np.hstack(([3] * 7, [2])), # L18
                                 [5] * 6, # L25
                                 [3] * 13, # L27
                                 [2] * 31, # L32
                                 np.hstack(([4] * 9, [2])), # L32'
                                 # np.hstack(([3] * 12, [2] * 11)), # L36
                                 np.hstack(([5] * 11, [2]))] # L50
  precalculated_points = [
    np.array([[1, 1, 1, 1, 1, 1, 1, 1],
              [1, 2, 2, 2, 2, 2, 2, 1],
              [1, 3, 3, 3, 3, 3, 3, 1],
              [2, 1, 1, 2, 2, 3, 3, 1],
              [2, 2, 2, 3, 3, 1, 1, 1],
              [2, 3, 3, 1, 1, 2, 2, 1],
              [3, 1, 2, 1, 3, 2, 3, 1],
              [3, 2, 3, 2, 1, 3, 1, 1],
              [3, 3, 1, 3, 2, 1, 2, 1],
              [1, 1, 3, 3, 2, 2, 1, 2],
              [1, 2, 1, 1, 3, 3, 2, 2],
              [1, 3, 2, 2, 1, 1, 3, 2],
              [2, 1, 2, 3, 1, 3, 2, 2],
              [2, 2, 3, 1, 2, 1, 3, 2],
              [2, 3, 1, 2, 3, 2, 1, 2],
              [3, 1, 3, 2, 3, 1, 2, 2],
              [3, 2, 1, 3, 1, 2, 3, 2],
              [3, 3, 2, 1, 2, 3, 1, 2]]), # L18
    np.array([[1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2],
            [1, 3, 3, 3, 3, 3],
            [1, 4, 4, 4, 4, 4],
            [1, 5, 5, 5, 5, 5],
            [2, 1, 2, 3, 4, 5],
            [2, 2, 3, 4, 5, 1],
            [2, 3, 4, 5, 1, 2],
            [2, 4, 5, 1, 2, 3],
            [2, 5, 1, 2, 3, 4],
            [3, 1, 3, 5, 2, 4],
            [3, 2, 4, 1, 3, 5],
            [3, 3, 5, 2, 4, 1],
            [3, 4, 1, 3, 5, 2],
            [3, 5, 2, 4, 1, 3],
            [4, 1, 4, 2, 5, 3],
            [4, 2, 5, 3, 1, 4],
            [4, 3, 1, 4, 2, 5],
            [4, 4, 2, 5, 3, 1],
            [4, 5, 3, 1, 4, 2],
            [5, 1, 5, 4, 3, 2],
            [5, 2, 1, 5, 4, 3],
            [5, 3, 2, 1, 5, 4],
            [5, 4, 3, 2, 1, 5],
            [5, 5, 4, 3, 2, 1]]), # L25
    np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3],
            [1, 2, 2, 2, 1, 1, 1, 2, 2, 2, 3, 3, 3],
            [1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 1, 1, 1],
            [1, 2, 2, 2, 3, 3, 3, 1, 1, 1, 2, 2, 2],
            [1, 3, 3, 3, 1, 1, 1, 3, 3, 3, 2, 2, 2],
            [1, 3, 3, 3, 2, 2, 2, 1, 1, 1, 3, 3, 3],
            [1, 3, 3, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1],
            [2, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
            [2, 1, 2, 3, 2, 3, 1, 2, 3, 1, 2, 3, 1],
            [2, 1, 2, 3, 3, 1, 2, 3, 1, 2, 3, 1, 2],
            [2, 2, 3, 1, 1, 2, 3, 2, 3, 1, 3, 1, 2],
            [2, 2, 3, 1, 2, 3, 1, 3, 1, 2, 1, 2, 3],
            [2, 2, 3, 1, 3, 1, 2, 1, 2, 3, 2, 3, 1],
            [2, 3, 1, 2, 1, 2, 3, 3, 1, 2, 2, 3, 1],
            [2, 3, 1, 2, 2, 3, 1, 1, 2, 3, 3, 1, 2],
            [2, 3, 1, 2, 3, 1, 2, 2, 3, 1, 1, 2, 3],
            [3, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3, 2],
            [3, 1, 3, 2, 2, 1, 3, 2, 1, 3, 2, 1, 3],
            [3, 1, 3, 2, 3, 2, 1, 3, 2, 1, 3, 2, 1],
            [3, 2, 1, 3, 1, 3, 2, 2, 1, 3, 3, 2, 1],
            [3, 2, 1, 3, 2, 1, 3, 3, 2, 1, 1, 3, 2],
            [3, 2, 1, 3, 3, 2, 1, 1, 3, 2, 2, 1, 3],
            [3, 3, 2, 1, 1, 3, 2, 3, 2, 1, 2, 1, 3],
            [3, 3, 2, 1, 2, 1, 3, 1, 3, 2, 3, 2, 1],
            [3, 3, 2, 1, 3, 2, 1, 2, 1, 3, 1, 3, 2]]), # L27
    np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2],
            [1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1],
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1],
            [1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
            [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2],
            [1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1],
            [1, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1],
            [1, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2],
            [1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1],
            [1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2],
            [1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2],
            [1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1],
            [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
            [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1],
            [2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2],
            [2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1],
            [2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2],
            [2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2],
            [2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1],
            [2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1],
            [2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2],
            [2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2],
            [2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 1, 2, 2, 1],
            [2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2],
            [2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1],
            [2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 2, 1],
            [2, 2, 1, 2, 1, 1, 2, 2, 1, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 2]]), # L32
    np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 3, 3, 3, 3, 3, 3, 3, 3],
            [1, 1, 4, 4, 4, 4, 4, 4, 4, 4],
            [1, 2, 1, 1, 2, 2, 3, 3, 4, 4],
            [1, 2, 2, 2, 1, 1, 4, 4, 3, 3],
            [1, 2, 3, 3, 4, 4, 1, 1, 2, 2],
            [1, 2, 4, 4, 3, 3, 2, 2, 1, 1],
            [1, 3, 1, 2, 3, 4, 1, 2, 3, 4],
            [1, 3, 2, 1, 4, 3, 2, 1, 4, 3],
            [1, 3, 3, 4, 1, 2, 3, 4, 1, 2],
            [1, 3, 4, 3, 2, 1, 4, 3, 2, 1],
            [1, 4, 1, 2, 4, 3, 3, 4, 2, 1],
            [1, 4, 2, 1, 3, 4, 4, 3, 1, 2],
            [1, 4, 3, 4, 2, 1, 1, 2, 4, 3],
            [1, 4, 4, 3, 1, 2, 2, 1, 3, 4],
            [2, 1, 1, 4, 1, 4, 2, 3, 2, 3],
            [2, 1, 2, 3, 2, 3, 1, 4, 1, 4],
            [2, 1, 3, 2, 3, 2, 4, 1, 4, 1],
            [2, 1, 4, 1, 4, 1, 3, 2, 3, 2],
            [2, 2, 1, 4, 2, 3, 4, 1, 3, 2],
            [2, 2, 2, 3, 1, 4, 3, 2, 4, 1],
            [2, 2, 3, 2, 4, 1, 2, 3, 1, 4],
            [2, 2, 4, 1, 3, 2, 1, 4, 2, 3],
            [2, 3, 1, 3, 3, 1, 2, 4, 4, 2],
            [2, 3, 2, 4, 4, 2, 1, 3, 3, 1],
            [2, 3, 3, 1, 1, 3, 4, 2, 2, 4],
            [2, 3, 4, 2, 2, 4, 3, 1, 1, 3],
            [2, 4, 1, 3, 4, 2, 4, 2, 1, 3],
            [2, 4, 2, 4, 3, 1, 3, 1, 2, 4],
            [2, 4, 3, 1, 2, 4, 2, 4, 3, 1],
            [2, 4, 4, 2, 1, 3, 1, 3, 4, 2]]), # L32'
    np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
            [1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
            [1, 1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
            [1, 1, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
            [1, 2, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
            [1, 2, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1],
            [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2],
            [1, 2, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3],
            [1, 2, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4],
            [1, 3, 1, 3, 5, 2, 4, 4, 1, 3, 5, 2],
            [1, 3, 2, 4, 1, 3, 5, 5, 2, 4, 1, 3],
            [1, 3, 3, 5, 2, 4, 1, 1, 3, 5, 2, 4],
            [1, 3, 4, 1, 3, 5, 2, 2, 4, 1, 3, 5],
            [1, 3, 5, 2, 4, 1, 3, 3, 5, 2, 4, 1],
            [1, 4, 1, 4, 2, 5, 3, 5, 3, 1, 4, 2],
            [1, 4, 2, 5, 3, 1, 4, 1, 4, 2, 5, 3],
            [1, 4, 3, 1, 4, 2, 5, 2, 5, 3, 1, 4],
            [1, 4, 4, 2, 5, 3, 1, 3, 1, 4, 2, 5],
            [1, 4, 5, 3, 1, 4, 2, 4, 2, 5, 3, 1],
            [1, 5, 1, 5, 4, 3, 2, 4, 3, 2, 1, 5],
            [1, 5, 2, 1, 5, 4, 3, 5, 4, 3, 2, 1],
            [1, 5, 3, 2, 1, 5, 4, 1, 5, 4, 3, 2],
            [1, 5, 4, 3, 2, 1, 5, 2, 1, 5, 4, 3],
            [1, 5, 5, 4, 3, 2, 1, 3, 2, 1, 5, 4],
            [2, 1, 1, 1, 4, 5, 4, 3, 2, 5, 2, 3],
            [2, 1, 2, 2, 5, 1, 5, 4, 3, 1, 3, 4],
            [2, 1, 3, 3, 1, 2, 1, 5, 4, 2, 4, 5],
            [2, 1, 4, 4, 2, 3, 2, 1, 5, 3, 5, 1],
            [2, 1, 5, 5, 3, 4, 3, 2, 1, 4, 1, 2],
            [2, 2, 1, 2, 1, 3, 3, 2, 4, 5, 5, 4],
            [2, 2, 2, 3, 2, 4, 4, 3, 5, 1, 1, 5],
            [2, 2, 3, 4, 3, 5, 5, 4, 1, 2, 2, 1],
            [2, 2, 4, 5, 4, 1, 1, 5, 2, 3, 3, 2],
            [2, 2, 5, 1, 5, 2, 2, 1, 3, 4, 4, 3],
            [2, 3, 1, 3, 3, 1, 2, 5, 5, 4, 2, 4],
            [2, 3, 2, 4, 4, 2, 3, 1, 1, 5, 3, 5],
            [2, 3, 3, 5, 5, 3, 4, 2, 2, 1, 4, 1],
            [2, 3, 4, 1, 1, 4, 5, 3, 3, 2, 5, 2],
            [2, 3, 5, 2, 2, 5, 1, 4, 4, 3, 1, 3],
            [2, 4, 1, 4, 5, 4, 1, 2, 5, 2, 3, 3],
            [2, 4, 2, 5, 1, 5, 2, 3, 1, 3, 4, 4],
            [2, 4, 3, 1, 2, 1, 3, 4, 2, 4, 5, 5],
            [2, 4, 4, 2, 3, 2, 4, 5, 3, 5, 1, 1],
            [2, 4, 5, 3, 4, 3, 5, 1, 4, 1, 2, 2],
            [2, 5, 1, 5, 2, 2, 5, 3, 4, 4, 3, 1],
            [2, 5, 2, 1, 3, 3, 1, 4, 5, 5, 4, 2],
            [2, 5, 3, 2, 4, 4, 2, 5, 1, 1, 5, 3],
            [2, 5, 4, 3, 5, 5, 3, 1, 2, 2, 1, 4],
            [2, 5, 5, 4, 1, 1, 4, 2, 3, 3, 2, 5]])] # L50
  # arrange factors cardinality in descending order
  precalculated_points[4][:, 0], precalculated_points[4][:, -1] = np.copy(precalculated_points[4][:, -1]), np.copy(precalculated_points[4][:, 0])
  # precalculated_points[5] = precalculated_points[5][:, 1:]
  # precalculated_points[5][:, :11], precalculated_points[5][:, -11:] = np.copy(precalculated_points[5][:, -11:]), np.copy(precalculated_points[5][:, :11])
  precalculated_points[5][:, 0], precalculated_points[5][:, -1] = np.copy(precalculated_points[5][:, -1]), np.copy(precalculated_points[5][:, 0])
  is_precalcilated = False
  points = []
  for design_candidate in xrange(len(precalculated_factors_number)):
    if (precalculated_points_number[design_candidate] == points_number and
        precalculated_factors_number[design_candidate][-1] >= len(levels_number) and
        precalculated_factors_number[design_candidate][0] <= len(levels_number)):
      if np.all(levels_number == precalculated_levels_number[design_candidate][:len(levels_number)]):
        points = precalculated_points[design_candidate][:, :len(levels_number)] - 1 # make 0-based indexes
        is_precalcilated = True
  return is_precalcilated, points

def gcd(first_number, second_number):
  """Calculate the Greatest Common Divisor of first_number and second_number.

  Unless second_number==0, the result will have the same sign as second_number (so that when
  second_number is divided by it, the result comes out positive).
  """
  while second_number:
    first_number, second_number = second_number, first_number%second_number
  return first_number

def lcm(first_number, second_number):
  ''' Calculates least common multiple for two numbers.

  :param first_number: first number
  :type first_number: int
  :param second_number: second number
  :type second_number: int
  :return: lcm_value
  :rtype: int
  '''
  return first_number * second_number // gcd(first_number, second_number)

def calculate_J2(points, weights, dimensionality):
  ''' Calculates J2 for a first columns of a given matrix.

  :param points: matrix with points coordinates
  :type points: numpy.ndarray
  :param weights: weights for factors
  :type weights: list of ints
  :param dimensionality: number of used columns
  :type dimensionality: int
  :rtype: double
  '''
  J2 = 0
  for first_point in xrange(len(points)):
    for second_point in xrange(first_point):
      J2 = J2 + (np.dot(points[first_point, :dimensionality] == points[second_point, :dimensionality], weights[:dimensionality]))**2
  return J2

def calculate_penalty(points, levels_number, dimensionality, penalty_step=100000):
  ''' Calculates penalty for equal points in design

  :param points: matrix with points coordinates
  :type points: numpy.ndarray
  :param levels_number: required levels number for DoE
  :type levels_number: list of "int" with a list of ints
  :param dimensionality: number of used columns
  :type dimensionality: int
  :param penalty_step: penalty for one pair of equal points
  :type penalty_step: int
  :rtype: double
  '''
  possible_duplicates_number = max(1, len(points) // int(np.prod(levels_number[:dimensionality+1])))
  penalty = 0
  for first_point in xrange(len(points)):
    number_equal_points = 0
    for second_point in xrange(first_point + 1):
      if np.all(points[first_point, :dimensionality + 1] == points[second_point, :dimensionality + 1]):
        number_equal_points = number_equal_points + 1
    if number_equal_points > possible_duplicates_number:
      penalty = penalty + penalty_step * (number_equal_points - possible_duplicates_number)
  return penalty

def calculate_J2_plus(points, levels_number, weights, dimensionality):
  ''' Calculates J2 change if one adds one more column.

  :param points: matrix with points coordinates
  :type points: numpy.ndarray
  :param levels_number: required levels number for DoE
  :type levels_number: list of ints
  :param weights: weights for factors
  :type weights: list of ints
  :param dimensionality: number of new column
  :type dimensionality: int
  :rtype: double
  '''
  J2_plus = 0
  points_number = len(points)
  for first_point in xrange(points_number):
    for second_point in xrange(first_point):
      if points[first_point, dimensionality] == points[second_point, dimensionality]:
        J2_plus = J2_plus + 2 * weights[dimensionality] * np.dot(points[first_point, :dimensionality] == points[second_point, :dimensionality], weights[:dimensionality])
  J2_plus = J2_plus + 0.5 * points_number * (points_number // levels_number[dimensionality] - 1) * weights[dimensionality]**2
  return J2_plus

def calculate_delta(points, current_dimension, first_point, second_point, weights):
  ''' Calculates delta for two swap of two coordinates (first_point, current_dimension) and (second_point, current_dimension).

  :param points: matrix with points coordinates
  :type points: numpy.ndarray
  :param current_dimension: number of new column
  :type current_dimension: int
  :param first_point: number of the first point to swap
  :type first_point: int
  :param second_point: number of the second point to swap
  :type second_point: int
  :param weights: weights for factors
  :type weights: list of ints
  :rtype: double
  '''
  new_component_difference = np.array(points[:, current_dimension] == points[first_point, current_dimension], dtype=int) - np.array(points[:, current_dimension] ==
                             points[second_point, current_dimension], dtype=int)
  new_component_difference[first_point] = 0
  new_component_difference[second_point] = 0
  old_component_difference = np.dot(np.array(points[:, :current_dimension] == np.tile(points[first_point, :current_dimension], (len(points), 1)), dtype=int) - np.array(
                                             points[:, :current_dimension] == np.tile(points[second_point, :current_dimension], (len(points), 1)), dtype=int),
                                    weights[:current_dimension])
  delta = np.dot(old_component_difference, new_component_difference)
  return delta

def calculate_penalty_delta(points, dimensionality, levels_number, first_point, second_point, penalty_step=100000):
  ''' Calculates delta penalty for two swap of two coordinates (first_point, current_dimension) and (second_point, current_dimension).

  :param points: matrix with points coordinates
  :type points: numpy.ndarray
  :param dimensionality: number of new column
  :type dimensionality: int
  :param levels_number: required levels number for DoE
  :type levels_number: list of ints
  :param first_point: number of the first point to swap
  :type first_point: int
  :param second_point: number of the second point to swap
  :type second_point: int
  :param penalty_step=: penalty for one pair of equal points
  :type penalty_step=: int
  :rtype: double
  '''
  possible_duplicates_number = max(1, len(points) // int(np.prod(levels_number[:dimensionality+1])))
  changed_first_point = np.copy(points[first_point, :dimensionality + 1])
  changed_first_point[-1] = points[second_point, dimensionality]
  changed_second_point = np.copy(points[second_point, :dimensionality + 1])
  changed_second_point[-1] = points[first_point, dimensionality]
  number_equal_points_initial = [0, 0]
  number_equal_points_final = [0, 0]
  for compare_point in xrange(len(points)):
    if first_point != compare_point and second_point != compare_point:
      if np.all(points[first_point, :dimensionality + 1] == points[compare_point, :dimensionality + 1]):
        number_equal_points_initial[0] = number_equal_points_initial[0] + 1
      if np.all(points[second_point, :dimensionality + 1] == points[compare_point, :dimensionality + 1]):
        number_equal_points_initial[1] = number_equal_points_initial[1] + 1
      if np.all(changed_first_point == points[compare_point, :dimensionality + 1]):
        number_equal_points_final[0] = number_equal_points_final[0] + 1
      if np.all(changed_second_point == points[compare_point, :dimensionality + 1]):
        number_equal_points_final[1] = number_equal_points_final[1] + 1
  penalty_delta = penalty_step * (max(0, number_equal_points_initial[0] + 1 - possible_duplicates_number) +
                                  max(0, number_equal_points_initial[1] + 1 - possible_duplicates_number) -
                                  max(0, number_equal_points_final[0] + 1 - possible_duplicates_number) -
                                  max(0, number_equal_points_final[1] + 1 - possible_duplicates_number))
  return penalty_delta

def bisect_left(users_list, item, lower_element_position=0, higher_element_position=None):
  '''Return the index where to insert item x in users_list, assuming a is sorted.

  The return value i is such that all e in users_list[:i] have e < x, and all e in
  users_list[i:] have e >= x.  So if x already appears in the list, users_list.insert(x) will
  insert just before the leftmost x already there.

  Optional args lower_element_position (default 0) and higher_element_position (default len(users_list)) bound the
  slice of users_list to be searched.

  :param users_list: sorted list to search in
  :type users_list: list
  :param item: item to be searched
  :type dimensionality: int
  :param lower_element_position: lower element in search interval
  :type lower_element_position: int
  :param higher_element_position: higher element in search interval
  :type higher_element_position: int
  :param lower_element_position: int
  '''

  if lower_element_position < 0:
    raise ValueError('lower_element_position must be non-negative')
  if higher_element_position is None:
    higher_element_position = len(users_list)
  while lower_element_position < higher_element_position:
    middle_element_position = (lower_element_position+higher_element_position)//2
    if users_list[middle_element_position] < item:
      lower_element_position = middle_element_position+1
    else:
      higher_element_position = middle_element_position
  return lower_element_position

def get_index(users_list, element):
  '''Locate the leftmost value exactly equal to element'''
  index = bisect_left(users_list, element)
  if index != len(users_list) and users_list[index] == element:
    return index
  return -1

def insert_left(users_list, item, lower_element_position=0, higher_element_position=None):
  '''Insert item in users_list, and keep it sorted assuming users_list is sorted.

  If item is already in users_list, insert it to the left of the leftmost item.

  Optional args lower_element_position (default 0) and higher_element_position (default len(users_list)) bound the
  slice of a to be searched.
  '''
  if higher_element_position is None:
    higher_element_position = len(users_list)
  while lower_element_position < higher_element_position:
    middle_element_position = (lower_element_position+higher_element_position)//2
    if users_list[middle_element_position] < item:
      lower_element_position = middle_element_position+1
    else:
      higher_element_position = middle_element_position
    users_list.insert(lower_element_position, item)
    return users_list

class EqualPointsTree(object):
  '''
  Class helps to calculate penalty. It contains points with number of their entrances.
  '''
  def __init__(self, points, colomn):
    '''
    Generates initial tree from sorted list of points. All colomns from points are ignored after colomn.
    '''
    self.tree = list()
    for point in points:
      if len(self.tree) == 0:
        index = -1
      else:
        index = get_index(tuple(_[0] for _ in self.tree), point[:colomn])
      if index < 0:
        self.tree.append([point[:colomn], [point[colomn], 1]])
      else:
        last_column_index = get_index(tuple(_[0] for _ in self.tree[index][1:]), point[colomn])
        if last_column_index < 0:
          self.tree[index].append([point[colomn], 1])
        else:
          self.tree[index][last_column_index + 1][1] = self.tree[index][last_column_index + 1][1] + 1

  def get_duplicates_number(self, point):
    '''
    Calculates duplicates number for a given point.
    '''
    index = get_index(tuple(_[0] for _ in self.tree), point[:-1])
    if index < 0:
      return 0
    last_column_index = get_index(tuple(_[0] for _ in self.tree[index][1:]), point[-1])
    if last_column_index < 0:
      return 0
    return self.tree[index][last_column_index + 1][1]

  def insert_point(self, point):
    '''
    Inserts point into the tree.
    '''
    index = get_index(tuple(_[0] for _ in self.tree), point[:-1])
    if index < 0:
      self.tree = insert_left(self.tree, [point[:-1], [point[-1], 1]])
    else:
      last_column_index = get_index(tuple(_[0] for _ in self.tree[index][1:]), point[-1])
      if last_column_index < 0:
        self.tree[index][1:] = insert_left(self.tree[index][1:], [point[-1], 1])
      else:
        self.tree[index][last_column_index + 1][1] = self.tree[index][last_column_index + 1][1] + 1

  def remove_point(self, point):
    '''
    Removes point from the tree.
    '''
    index = get_index(tuple(_[0] for _ in self.tree), point[:-1])
    if index >= 0:
      last_column_index = get_index(tuple(_[0] for _ in self.tree[index][1:]), point[-1])
      if last_column_index >= 0:
        if self.tree[index][last_column_index + 1][1] > 1:
          self.tree[index][last_column_index + 1][1] = self.tree[index][last_column_index + 1][1] - 1
        else:
          self.tree[index].pop(last_column_index + 1)
          if len(self.tree[index]) == 1:
            self.tree.pop(index)

  def get_delta_penalty(self, first_point, second_point, possible_duplicates_number, penalty_step=100000):
    '''
    Calculates delta penalty if one changes last elements of first_point and second_point.
    '''
    changed_first_point = copy.copy(first_point)
    changed_first_point[-1] = second_point[-1]
    changed_second_point = copy.copy(second_point)
    changed_second_point[-1] = first_point[-1]
    return penalty_step * (max(self.get_duplicates_number(first_point) - possible_duplicates_number, 0) +
                           max(self.get_duplicates_number(second_point) - possible_duplicates_number, 0) -
                           max(self.get_duplicates_number(changed_second_point) - possible_duplicates_number + 1, 0) -
                           max(self.get_duplicates_number(changed_first_point) - possible_duplicates_number + 1, 0))

  def calculate_penalty(self, possible_duplicates_number, penalty_step=100000):
    '''
    Calculates penalty for the tree.
    '''
    penalty_counter = 0
    for node in self.tree:
      for suffix in node[1:]:
        penalty_counter = penalty_counter + max(0, (suffix[1] - possible_duplicates_number) * (suffix[1] - possible_duplicates_number + 1) // 2)
    return penalty_counter * penalty_step
