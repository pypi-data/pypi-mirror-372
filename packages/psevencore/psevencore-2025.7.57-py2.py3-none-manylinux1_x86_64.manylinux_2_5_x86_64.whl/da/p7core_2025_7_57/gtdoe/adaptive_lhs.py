#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import numpy as np
from .. import exceptions as _ex
from ..six.moves import xrange, range, zip

from . import measures

def _generate_adaptive_lhs(bounds, points_number, categorical_variables, integer_variables, initial_points, iterations_number, seed, sift_logger, quality_measure, smooth, validation_mode=False):
  """
  Generate design that is close to LHS using the given design with Python.
  If it is possible (initial design is LHS or OLHS and point_number is good)
  we keep LHS design property

  :param bounds: design space bounds
  :type bounds: ``tuple(list(float), list(float))``
  :param points_number: number of points to generate
  :type points_number: ``int``, ``long``
  :param categorical_variables: list of pairs (not tuples): 0-based index of categorical variable followed by list of categorical levels
  :type categorical_variables: ``list``
  :param initial_points: initial design for which we append LHS design
  :type initial_points: numpy.ndarray
  :param iterations_number: number of OLHS iterations, if 1 the function generates LHS design
  :type iterations_number: ``int``, ``short``
  :param seed: seed value to guarantee results to be reproducible or None to use random initialization
  :type seed: ``int``, ``long``, ``None``
  :param sift_logger: :ref:`logger <Logger>` object
  :param quality_measure: selected measure to optimize for OLHS, valid values are 'PhiP', 'PotentialEnergy', 'MinimaxInterpoint'
  :type quality_measure: ``str``
  :param smooth: randomize position of the new points within respective LHS bands.
  :type smooth: ``bool``
  :return: info, points
  :rtype: dict, numpy.ndarray
  """
  # set correct random state
  random_state = np.random.get_state()
  try:
    np.random.seed(seed)

    # check iterations number option
    if (iterations_number < 1) or (int(iterations_number) != iterations_number):
      raise _ex.InvalidOptionValueError("Option 'GTDoE/OLHS/Iterations=%s' is not correct." % iterations_number)

    points_dim = len(bounds[0])

    if initial_points is None:
      initial_points = np.empty((0, points_dim), dtype=float)
    elif np.shape(initial_points)[1] != points_dim:
      raise _ex.InvalidProblemError("Length of the initial sample vectors does not conform length of the design space bounds.")

    categorical_variables = _get_categorical_variables_dict(list(categorical_variables))

    initial_sample_size = np.shape(initial_points)[0]
    if initial_sample_size and (points_number % initial_sample_size):
      sift_logger.warn("For a new design to have LHS property number of new points should be divisible by the initial sample size.")

    # normalize and filter points
    normalized_initial_points, normalization_parameters = _normalize_points(initial_points, bounds, categorical_variables, integer_variables)

    # expand lhs
    if normalized_initial_points.size:
      # check if initial design is LHS or not
      continuous_variables = [info["origin"] for info in normalization_parameters if info["type"] == "continuous"]
      if continuous_variables and not _check_if_lhs(normalized_initial_points[:, continuous_variables] if len(continuous_variables) < normalized_initial_points.shape[1] else normalized_initial_points): # avoid excessive array copy:
        sift_logger.warn("Provided design is not LHS, so constructed design also is not LHS")
    elif points_number is None:
      raise _ex.InvalidProblemError('The number of requested points must be greater than zero or initial sample must be provided.')

    if validation_mode:
      return {}, np.empty(((points_number or 0), 0)) # None is zero

    #baskets_number = "adaptive" if (normalized_initial_points.size and smooth and iterations_number > 1) else None
    baskets_number = None # adaptive algorithm is turned off because it's not as good as expected
    info, new_points, baskets_number = _expand_lhs(points_number, initial_points=normalized_initial_points,
                                                   iterations_number=iterations_number, baskets_number=baskets_number,
                                                   quality_measure=quality_measure, smooth=smooth)

    # denormalize points
    new_points = _denormalize_points(new_points, normalization_parameters, baskets_number)

    return info, np.vstack((initial_points, new_points))
  finally:
    # get back to initial random state
    np.random.set_state(random_state)

def _get_categorical_variables_dict(categorical_variables):
  """ Get dict of categorical variables

  :param categorical_variables: describes categorical variables
  :type categorical_variables: ``list``
  :return: categorical_variables_dict - dict of categorical variables
  :rtype: dict
  """
  categorical_variables_dict = dict()
  if categorical_variables:
    for index, value in zip(categorical_variables[::2], categorical_variables[1::2]):
      categorical_variables_dict[index] = value
  return categorical_variables_dict

def _normalize_points(points, bounds, categorical_variables, integer_variables):
  """ Normalize and filter points to [0, 1]^d using bounds and categorical_variables.

  :param points: not normalized points in bounds
  :type points: numpy.ndarray
  :param bounds: design space bounds
  :type bounds: ``tuple(list(float), list(float))``
  :param categorical_variables: describes categorical variables
  :type categorical_variables: dict of keys with indexes of categorical variables and levels for these keys
  :return: normalized_points, normalization_parameters
  :rtype: numpy.ndarray, dict

  """
  normalization_parameters = []
  normalized_points = []

  initial_points_count = np.shape(points)[0]

  for dimension, (lower_bound, upper_bound) in enumerate(zip(bounds[0], bounds[1])):
    if dimension not in categorical_variables:
      if lower_bound == upper_bound:
        normalization_parameters.append({"type": "const", "value": lower_bound})
      elif dimension in integer_variables:
        normalization_parameters.append({"type": "integer", "origin": len(normalized_points),
                                         "lower_bound": lower_bound, "upper_bound": upper_bound})
        if initial_points_count:
          normalized_points.append(np.multiply(np.subtract(points[:, dimension], lower_bound), 1. / (upper_bound - lower_bound)).reshape(-1, 1))
      else:
        normalization_parameters.append({"type": "continuous", "origin": len(normalized_points),
                                         "scale": (upper_bound - lower_bound), "bias": lower_bound})
        if initial_points_count:
          normalized_points.append(np.multiply(np.subtract(points[:, dimension], lower_bound), 1. / (upper_bound - lower_bound)).reshape(-1, 1))
    else:
      values = [_ for _ in categorical_variables[dimension]]
      if len(values) == 1:
        normalization_parameters.append({"type": "const", "value": values[0]})
      else:
        mapped_bounds = np.linspace(0., 1., 2 * len(values) + 1)[::2]
        normalization_parameters.append({"type": "categorical", "origin": len(normalized_points), "values": values,
                                         "lower_bounds": mapped_bounds[:-1], "upper_bounds": mapped_bounds[1:]})

        if initial_points_count:
          normalized_vector = np.empty(initial_points_count)
          normalized_vector.fill(-1.) # initialize with invalid value
          for interval_index, (value, interval_lb, interval_ub) in enumerate(zip(values, mapped_bounds[:-1], mapped_bounds[1:])):
            selected_indexes = points[:, dimension] == value
            if selected_indexes.any():
              points_number = np.count_nonzero(selected_indexes)
              # for selected interval [s_{k}, s_{k + 1}] we put points in a uniform way
              # for example, if we want to put 5 points to [0.3, 0.5] we put them to [0.32, 0.36, 0.4, 0.44, 0.48]
              remapped_values = np.linspace(interval_lb, interval_ub, 2 * points_number + 1)[1::2]
              normalized_vector[selected_indexes] = np.random.permutation(remapped_values)
          normalized_points.append(normalized_vector.reshape(-1, 1))

  if not normalized_points:
    return np.empty((initial_points_count, 0), dtype=float), normalization_parameters

  normalized_points = np.hstack(normalized_points)

  # filter invalid points
  valid_points = np.logical_and(np.greater_equal(normalized_points, 0.).all(axis=1),
                                np.less_equal(normalized_points, 1.).all(axis=1))

  return (normalized_points if valid_points.all() else normalized_points[valid_points]), normalization_parameters

def _denormalize_points(normalized_points, normalization_parameters, stripes_per_dimension):
  """ Denormalize points from [0, 1]^d to initial bounds.

  :param normalized_points: normalized points in [0, 1]^d
  :type normalized_points: numpy.ndarray
  :param bounds: design space bounds
  :type bounds: ``tuple(list(float), list(float))``
  :param categorical_variables: describes categorical variables
  :type categorical_variables: dict of keys with indexes of categorical variables and levels for these keys
  :param normalization_parameters: normalization parameters contains info about constant variables
  :type normalization_parameters: dict with the single field 'constant_variables'
  :return: points - denormalized points
  :rtype: numpy.ndarray

  """

  points = np.empty((normalized_points.shape[0], len(normalization_parameters)), dtype=float)
  normalized_dimension = -1
  for dimension, variable_spec in enumerate(normalization_parameters):
    kind = variable_spec.get("type", "const")
    if kind == "const":
      points[:, dimension] = variable_spec.get("value", 0.)
      continue

    normalized_dimension += 1 # note constant dimensions are eliminated in normalized_points and stripes_per_dimension
    if kind == "integer":
      lower_bound, upper_bound = variable_spec.get("lower_bound", 0.), variable_spec.get("upper_bound", 1.)

      # see backend implementation for details
      stripe_width = float(upper_bound - lower_bound) / stripes_per_dimension[normalized_dimension]
      if stripe_width > 1.:
        stripe_index = np.floor(normalized_points[:, normalized_dimension] * stripes_per_dimension[normalized_dimension])
        stripe_lb = stripe_index * stripe_width
        stripe_ub = stripe_lb + stripe_width
        closes_int = np.round(normalized_points[:, normalized_dimension] * float(upper_bound - lower_bound))
        points[:, dimension] = closes_int + (closes_int < stripe_lb) - (closes_int >= stripe_ub)
      elif stripe_width == 1.:
        points[:, dimension] = np.floor(normalized_points[:, normalized_dimension] * stripes_per_dimension[normalized_dimension])
      else:
        stripe_index = np.floor(normalized_points[:, normalized_dimension] * stripes_per_dimension[normalized_dimension])
        stripe_lb = stripe_index * stripe_width
        stripe_ub = stripe_lb + stripe_width
        closes_int = np.round(normalized_points[:, normalized_dimension] * float(upper_bound - lower_bound))
        points[:, dimension] = closes_int \
            + ((stripe_lb - closes_int) > (closes_int + 1. - stripe_ub))\
            - ((closes_int - stripe_ub) >= (stripe_lb + 1. - closes_int))

      points[:, dimension] = np.clip(lower_bound + points[:, dimension], lower_bound, upper_bound)
    elif kind == "continuous":
      points[:, dimension] = normalized_points[:, variable_spec.get("origin")] * variable_spec.get("scale", 1.) + variable_spec.get("bias", 0.)
    elif kind == "categorical":
      normalized_vector = normalized_points[:, variable_spec.get("origin")]
      destination_vector = points[:, dimension]
      for value, lb, ub in zip(variable_spec.get("values"), variable_spec.get("lower_bounds"), variable_spec.get("upper_bounds")):
        destination_vector[np.logical_and(normalized_vector >= lb, normalized_vector < ub)] = value
      destination_vector[normalized_vector == variable_spec.get("upper_bounds")[-1]] = variable_spec.get("values")[-1]  # upper bound is allowed

  return points

def _get_cell_indices(points, n_cells):
  """ Determine indices of corresponding cells for each point.

  :param points: set of design points in [0, 1]^d
  :type points: numpy.ndarray
  :return: cell_indices - array of cell indices
  :rtype: numpy.ndarray
  """
  return np.clip(np.floor(np.multiply(points, n_cells)).astype(type(points.shape[0])), 0, np.subtract(n_cells, 1))


def _check_if_lhs(points):
  """ Check if given design is LHS design or not.

  :param design: set of design points in [0, 1]^d
  :type design: numpy.ndarray
  :return: is_lhs - is provided design LHS design
  :rtype: bool
  """
  cell_indices = _get_cell_indices(points, points.shape[0])
  cell_hits = np.zeros((points.shape[0]), dtype=bool)
  for dimension in range(points.shape[1]):
    cell_hits.fill(False)
    cell_hits[cell_indices[:, dimension]] = True
    if not cell_hits.all():
      return False
  return True

def _adaptive_select_baskets(new_points_number, initial_values):
  n_baskets = new_points_number + len(initial_values)
  if n_baskets == new_points_number or n_baskets < 2:
    return n_baskets

  index_type = type(initial_values.shape[0])

  ubound = n_baskets
  lbound = 0

  while n_baskets > lbound:
    free_cells = np.ones((n_baskets,), dtype=bool)
    free_cells[np.clip(np.floor(np.multiply(initial_values, n_baskets)).astype(index_type), 0, n_baskets - 1)] = False
    free_count = np.count_nonzero(free_cells)

    if free_count > new_points_number:
      ubound = n_baskets
      n_baskets -= free_count - new_points_number
      if n_baskets <= lbound: # assuming we've checked lbound (or it has no sense as at the first step)
        n_baskets = (ubound + lbound) // 2
    elif free_count < new_points_number:
      lbound = n_baskets # update lbound because n_baskets always greater than or equal to the lbound
      n_baskets = (ubound + lbound) // 2
    else:
      return n_baskets #converged

  return ubound

def _expand_lhs(new_points_number, initial_points, iterations_number, baskets_number, quality_measure, smooth):
  """  Expand existed design to make it close to LHS

  :param new_points_number: number of points to generate
  :type new_points_number: ``int``, ``long``
  :param initial_points: initial design for which we append LHS design
  :type initial_points: numpy.ndarray
  :param iterations_number: number of OLHS iterations, if 1 the function generates LHS design
  :type iterations_number: ``int``, ``short``
  :param baskets_number: the number of stripes per dimension
  :type baskets_number: ``int``, ``list``
  :param quality_measure: selected measure to optimize for OLHS, valid values are 'PhiP', 'PotentialEnergy', 'MinimaxInterpoint'
  :type quality_measure: ``str``
  :param smooth: randomize position of the new points within respective LHS bands.
  :type smooth: ``bool``
  :return: info, points
  :rtype: dict, numpy.ndarray
  """
  initial_sample_size, points_dimension = np.shape(initial_points)
  bounds = np.empty((2, points_dimension))
  bounds[0].fill(0.)
  bounds[1].fill(1.)

  if new_points_number is None:
    new_points_number = initial_sample_size

  info = dict([("Generator", {})])

  if not new_points_number or not points_dimension:
    return info, np.empty((new_points_number, points_dimension), dtype=float), (baskets_number or initial_sample_size)

  if baskets_number is None or not initial_sample_size:
    baskets_number = [(initial_sample_size + new_points_number),]*points_dimension
  elif str(baskets_number).lower() == "adaptive":
    baskets_number = [_adaptive_select_baskets(new_points_number, initial_values) for initial_values in initial_points.T]
  else:
    baskets_number = [baskets_number,]*points_dimension

  occupied = _get_cell_indices(initial_points, [baskets_number])
  free_cells = []

  free_cells_marks = np.empty(np.amax(baskets_number), dtype=bool)
  for i, (occupied_i, n_baskets) in enumerate(zip(occupied.T, baskets_number)):
    free_cells_marks[:n_baskets] = True
    free_cells_marks[occupied_i] = False
    free_cells_marks[n_baskets:] = False
    free_cells.append(np.where(free_cells_marks)[0])
  del free_cells_marks

  if iterations_number == 1:
    design_quality = lambda new_points: 0.0
  elif quality_measure.lower() == 'minimaxinterpoint':
    design_quality = lambda new_points: measures._minimax_distance(bounds, new_points, normalize=False, initial_points=initial_points)
  elif quality_measure.lower() == 'phip':
    design_quality = lambda new_points: measures._phi_p(bounds, new_points, normalize=False, initial_points=initial_points)
  elif quality_measure.lower() == 'potentialenergy':
    design_quality = lambda new_points: measures._potential(bounds, new_points, normalize=False, initial_points=initial_points)
  elif quality_measure.lower() == 'discrepancy':
    design_quality = lambda new_points: measures._discrepancy(bounds, new_points, initial_points=initial_points)
  else:
    raise _ex.InvalidProblemError('Invalid quality measure kind specified: %s' % quality_measure)

  best_quality = np.inf
  best_new_points = None
  for _ in xrange(iterations_number):
    if smooth:
      new_points = np.random.uniform(0., 1., size=(new_points_number, points_dimension))
    else:
      new_points = np.empty((new_points_number, points_dimension))
      new_points.fill(0.5)

    for i, (free_cells_i, n_baskets) in enumerate(zip(free_cells, baskets_number)):
      np.add(new_points[:, i], np.random.permutation(free_cells_i)[:new_points_number].astype(float), out=new_points[:, i])
      np.multiply(new_points[:, i], 1. / n_baskets, out=new_points[:, i])

    if iterations_number == 1:
      best_new_points = new_points
    else:
      quality = design_quality(new_points)
      if quality < best_quality:
        best_new_points = new_points
        best_quality = quality

  return info, best_new_points, baskets_number
