#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

import sys
import ctypes as _ctypes
from re import match
import numpy as np

from ..six.moves import xrange, zip
from .. import shared as _shared
from .. import exceptions as _ex

def check_sample(x, y,
                 dif_sizes='Sizes of inputs and outputs do not match!',
                 empty_sample='Sample is empty!',
                 x_dim_is_zero='X dimensionality should be greater than zero!',
                 y_dim_is_zero='Y dimensionality should be greater than zero!'):
  """Checks the proper dimensions of inputs and outputs matrices
  """
  if x is None or y is None:
    raise ValueError(empty_sample)

  x, vector_x = _shared.as_matrix(x, ret_is_vector=True, name="Input sample ('x' argument)")
  y, vector_y = _shared.as_matrix(y, ret_is_vector=True, name="Output sample ('y' argument)")

  if x.shape[0] != y.shape[0]:
    # may be we have misinterpreted single vector data
    if vector_x and vector_y:
      x = x.reshape(1, x.size)
      y = y.reshape(1, y.size)
    elif vector_x:
      if 1 == y.shape[0]:
        x = x.reshape(1, x.size)
      else:
        raise ValueError(dif_sizes)
    elif vector_y:
      if 1 == x.shape[0]:
        y = y.reshape(1, y.size)
      else:
        raise ValueError(dif_sizes)
    else:
      raise ValueError(dif_sizes)

  if 0 == x.shape[0]:
    raise ValueError(empty_sample)

  if 0 == x.shape[1]:
    raise ValueError(x_dim_is_zero)

  if 0 == y.shape[1]:
    raise ValueError(y_dim_is_zero)

  return x.shape[0], x.shape[1], y.shape[1]


def check_one_sample(x,
                     empty_sample='Sample is empty!',
                     x_dim_is_zero='X dimensionality should be greater than zero!'):
  """Checks the proper dimensions of inputs matrices
  """
  if x is None:
    raise ValueError(empty_sample)

  x, vector_x = _shared.as_matrix(x, ret_is_vector=True, name="Input sample ('x' argument)")

  if x.ndim == 1:
    x = x.reshape(x.size, 1)

  if 0 == x.shape[0]:
    raise ValueError(empty_sample)

  if 0 == x.shape[1]:
    raise ValueError(x_dim_is_zero)

  return x.shape[0], x.shape[1]

def check_coinciding_points(training_points, training_values,
                            excluded_points, excluded_values):
  """Check for points with equal values
  """
  unique_indexes = get_unique_rows_idxs(training_points, training_values)

  processed_training_points = training_points[unique_indexes]
  processed_training_values = training_values[unique_indexes]
  return processed_training_points, processed_training_values

def itertools_product(*args, **kwds):
  """product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
  product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
  """
  pools = [tuple(_) for _ in args] * kwds.get('repeat', 1)
  result = [[]]
  for pool in pools:
    result = [x+[y] for x in result for y in pool]
  for prod in result:
    yield tuple(prod)

def is_constant(column, tolerance=None):
  """Check whether vector consist of constant values with given tolerance
  """
  if tolerance is None:
    tolerance = 1.e-8#np.finfo(float).eps
  finite_values_mask = np.isfinite(column)
  if not finite_values_mask.all():
    if np.count_nonzero(finite_values_mask) < 2:
      return False
    column = np.array(column, copy=_shared._SHALLOW)[finite_values_mask]
  c_max, c_min = np.amax(column), np.amin(column)
  return (c_max - c_min) <= tolerance * max([1., abs(c_max), abs(c_min)])

def check_for_constant_columns(train_points):
  """Returns list of constant columns and list of non-constant columns in matrix
  """
  number_dimensions = train_points.shape[1]
  columns_include_list = []
  columns_exclude_list = []

  for index, column in enumerate(train_points.T):
    (columns_include_list if not is_constant(column) else columns_exclude_list).append(index)

  # Sorted indices are crucial for some algorithms
  return sorted(columns_include_list), sorted(columns_exclude_list)

def preprocess_data(x):
  """Preprocess data
  """
  # reshaping
  if len(x.shape) == 1:
    x = x[:, np.newaxis]

  constant_columns_x = [i for i in xrange(x.shape[1]) if is_constant(x[:, i])]

  return x, constant_columns_x

def get_unique_rows_idxs(x, y=None, return_equivalence_sets=False):
  ''' Gets indices of unique rows
  '''
  idx = _shared._lexsort(x) # list of indices that sorts x
  diff = np.empty(len(x), dtype=bool) # unique elements marks
  diff[0] = True # the first element is always unique
  (x[idx[1:], :] != x[idx[:-1], :]).any(axis=1, out=diff[1:]) # marks adjacent x-points differences
  if y is not None:
    diff[1:] |= (y[idx[1:], :] != y[idx[:-1], :]).any(axis=1) # marks adjacent y-points differences

  if return_equivalence_sets:
    equivalence_sets = dict()
    diff_changes = np.hstack((np.where(diff)[0], [len(x)]))
    for first_index, second_index in zip(diff_changes[:-1], diff_changes[1:]):
      equivalence_sets[idx[first_index]] = idx[np.arange(first_index, second_index)]
    return np.sort(idx[diff]), equivalence_sets
  return np.sort(idx[diff])

def literal_eval(string_array, option_name):
  is_literal_eval = True
  try:
    _ast = __import__("ast", globals(), locals(), ['literal_eval'])
    _literal_eval = _ast.literal_eval
  except (ImportError, AttributeError):
    is_literal_eval = False
  if match(r"\[[\d.,\ ]*\]", string_array):
    try:
      if is_literal_eval:
        output_array = _literal_eval(string_array)
      else:
        output_array = eval(string_array)
    except SyntaxError:
      _shared.reraise(_ex.InvalidOptionValueError, ('Invalid option value: ' + option_name + '=' + string_array + '.'), sys.exc_info()[2])
  else:
    raise _ex.InvalidOptionValueError('Invalid option value: ' + option_name + '=' + string_array + '.')
  return output_array
