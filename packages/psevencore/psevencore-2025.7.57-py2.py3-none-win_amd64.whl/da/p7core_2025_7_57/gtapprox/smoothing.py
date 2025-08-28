#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


"""smoothing function for gtapprox"""
from __future__ import division

import sys
import ctypes
import numpy as np

from ..six import string_types
from ..six.moves import range

from .. import shared as _shared
from . import utilities as _utilities

class _AnisotropicSmoothing(object):
  def __init__(self, error_title):
    from . import model as _gtamodel

    self.__Model = _gtamodel.Model
    self.__smooth_model = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                              ctypes.c_size_t, ctypes.POINTER(ctypes.c_double),
                              ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p))\
                              (('GTApproxModelAnisotropicSmoothing', _shared._library))
    self.__error_title = error_title

  def smooth(self, model, smoothing_factors, vector_size=None):
    csmoothing_factors = _shared.py_matrix_2c(smoothing_factors, vector_size, name="'smoothing_factors' argument")
    errdesc = ctypes.c_void_p()
    smoothed_model_ptr = self.__smooth_model(model._Model__instance,
                                             csmoothing_factors.array.shape[0],
                                             csmoothing_factors.array.shape[1],
                                             csmoothing_factors.ptr, csmoothing_factors.ld,
                                             ctypes.byref(errdesc))
    if not smoothed_model_ptr:
      _shared.ModelStatus.checkErrorCode(0, self.__error_title, errdesc)

    return self.__Model(handle=smoothed_model_ptr)

def _get_basic_error_types_list():
  basic_error_types_list = ['RMS', 'RRMS', 'R^2', 'Max', 'Mean', 'Median', 'Q_0.95', 'Q_0.99', 'RMS_PTP', 'Max_PTP', 'Mean_PTP']

  return np.array(basic_error_types_list)


def _get_complex_error_types_list():
  basic_error_types_list = _get_basic_error_types_list()

  averaging_types_list = ['Mean', 'Max', 'RMS']

  complex_error_types_list = []
  for averaging_type in averaging_types_list:
    for error_type in basic_error_types_list:
      complex_error_types_list.append(averaging_type + ' ' + error_type)

  for error_type in basic_error_types_list:
    complex_error_types_list.append(error_type)

  return np.array(complex_error_types_list)


def _is_list(x):
  return _shared.is_iterable(x) and not isinstance(x, string_types)


def _process_sample(train_x, train_y, model_size_x, model_size_y):
  x = _shared.as_matrix(train_x, name="Reference inputs sample ('x_sample' argument)")
  y = _shared.as_matrix(train_y, name="Reference responses sample ('f_sample' argument)")

  sample_size = x.shape[0]
  if sample_size == 0:
    raise ValueError('Reference dataset is empty.')

  if x.shape[0] != y.shape[0]:
    raise ValueError('The number of vectors in input (X) and output (F) parts of reference dataset do not match: %d != %d' % (x.shape[0], y.shape[0]))

  size_x = x.shape[1]
  size_y = y.shape[1]
  if size_x != model_size_x:
    raise ValueError('Input (X) dimensionality of the reference dataset should be equal to the model input dimension: %d != %d' % (size_x, model_size_x))
  if size_y != model_size_y:
    raise ValueError('Output (F) dimensionality of the reference dataset should be equal to the model output dimension: %d != %d' % (size_y, model_size_y))

  # Remove samples with all non-finite outputs
  finite_y = np.isfinite(y).any(axis=1)
  if not finite_y.all():
    if not finite_y.any():
      raise ValueError('The whole output (F) part of the reference dataset is invalid (NaN or Inf).')
    else:
      x = x[finite_y]
      y = y[finite_y]

  # if there are non-finite values in X then raise an exception
  if not np.isfinite(x).all():
    raise ValueError('Invalid values (NaN or Inf) are found in the input (X) part of the reference dataset.')

  # if there are columns with all NaN raise exception
  if not np.isfinite(y).any(axis=0).all():
    raise ValueError('There are columns in the output (F) part of the reference dataset containing invalid (NaN or Inf) values only.')

  return x, y


def _check_input_x_weights(x_weights, size_x, size_f):
  if x_weights is None:
    return np.ones((1, size_x))

  x_weights, sgl_vector = _shared.as_matrix(x_weights, ret_is_vector=True, name="The amount of smoothing for different input components ('x_weights' argument)")
  if sgl_vector:
    x_weights = x_weights.reshape((1, -1))

  outputwise_smoothness_size, inputwise_smoothness_size = x_weights.shape
  if outputwise_smoothness_size != 1 and outputwise_smoothness_size != size_f:
    raise ValueError('Wrong outputwise x_weights dimensionality: %d (1%s expected).'
                       % (outputwise_smoothness_size, ('' if 1 == size_f else ' or %d' % size_f)))

  if inputwise_smoothness_size != size_x:
    raise ValueError('Wrong inputwise x_weights dimensionality: %d (1%s expected).'
                       % (inputwise_smoothness_size, ('' if 1 == size_x else ' or %d' % size_x)))

  if not np.isfinite(x_weights).all():
    raise ValueError('Invalid (NaN or Inf) values are found in x_weights.')

  if (x_weights < 0.).any() or (x_weights > 1.).any():
    invalid_points = np.where((x_weights < 0.)|(x_weights > 1.))
    raise ValueError('The x_weights[%d][%d] value %s is out of valid range [0 ... 1]%s.' % \
                      (invalid_points[0][0], invalid_points[1][0], \
                       x_weights[invalid_points[0][0], invalid_points[1][0]], \
                       ('' if 1 == len(invalid_points[0]) else ' (%d more invalid value(s) found)' % (len(invalid_points[0]) - 1))))

  return x_weights


def _check_input_f_smoothness(f_smoothness, size_f):
  f_smoothness = _shared.as_matrix(f_smoothness, shape=(1, None), name="Output smoothing factors ('f_smoothness' argument)").reshape(-1)

  f_smoothness_size = len(f_smoothness)
  if f_smoothness_size != 1 and f_smoothness_size != size_f:
    raise ValueError('Wrong f_smoothness dimensionality: %d (1%s expected).'
                       % (f_smoothness_size, ('' if 1 == size_f else ' or %d' % size_f)))

  if not np.isfinite(f_smoothness).all():
    raise ValueError('Invalid (NaN or Inf) values are found in f_smoothness.')

  if (f_smoothness < 0.).any() or (f_smoothness > 1.).any():
    invalid_points = np.where((f_smoothness < 0.)|(f_smoothness > 1.))[0]
    raise ValueError('The f_smoothness[%d] value %s is out of valid range [0 ... 1]%s.' % \
                     (invalid_points[0], f_smoothness[invalid_points[0]], \
                      ('' if 1 == len(invalid_points) else ' (%d more invalid value(s) found)' % (len(invalid_points) - 1))))

  return f_smoothness


def _check_input_error_thresholds(error_thresholds, error_type, size_f):
  error_type, aggregate_error = _check_error_type(error_type, size_f)

  try:
    if _is_list(error_thresholds):
      error_thresholds = np.array([threshold for threshold in error_thresholds], dtype=float)
    else:
      error_thresholds = np.array([error_thresholds,], dtype=float)
  except ValueError:
    message, tb = sys.exc_info()[1:]
    _shared.reraise(ValueError, ('The value of error_thresholds=%s is invalid: %s' % (error_thresholds, message)), tb)

  if aggregate_error:
    if 1 != error_thresholds.size:
      raise ValueError('error_type=%s requires one dimensional error_thresholds' % (error_type))
  elif error_thresholds.size != size_f:
    if 1 == error_thresholds.size:
      error_thresholds = np.tile(error_thresholds, size_f)
    else:
      raise ValueError('Wrong error_thresholds dimensionality: %d (1%s expected).'
                       % (error_thresholds.size, ('' if 1 == size_f else ' or %d' % size_f)))

  if (error_thresholds < 0.).any():
    invalid_points = np.where(error_thresholds < 0.)[0]
    raise ValueError('The error_thresholds[%d] value %s is out of valid range [0 ... +inf]%s.' % \
                     (invalid_points[0], error_thresholds[invalid_points[0]], \
                      ('' if 1 == len(invalid_points) else ' (%d more invalid value(s) found)' % (len(invalid_points) - 1))))

  if not np.isfinite(error_thresholds).all():
    raise ValueError('Invalid (NaN or Inf) values are found in error_thresholds.')

  # now find and replace R^2 error
  if aggregate_error:
    separated_error_types = error_type[0].split(' ')
    r2_points = np.array([(separated_error_types[1] == 'R^2'),], dtype=bool)
    r2_error = separated_error_types[0] + ' RRMS'
  else:
    r2_points = (error_type == 'R^2')
    r2_error = 'RRMS'

  if np.any(r2_points):
    if (error_thresholds[r2_points] > 1.).any():
      invalid_points = np.where(r2_points & (error_thresholds > 1.))[0]
      raise ValueError('The R^2 error_thresholds[%d] value %s is out of valid range [0 ... 1.]%s.' % \
                       (invalid_points[0], error_thresholds[invalid_points[0]], \
                        ('' if 1 == len(invalid_points) else ' (%d more invalid value(s) found)' % (len(invalid_points) - 1))))
    else:
      error_thresholds[r2_points] = np.sqrt(1. - error_thresholds[r2_points])
      error_type = np.array([(r2_error if r2_points[i] else error_type[i]) for i in range(error_type.size)])

  return (error_thresholds[0], error_type[0]) if aggregate_error else (error_thresholds, error_type)

def _check_error_type(error_type, size_f):
  basic_error_types_list = _get_basic_error_types_list()
  complex_error_types_list = _get_complex_error_types_list()

  try:
    if _is_list(error_type):
      error_type = np.array([str(error) for error in error_type])
    else:
      error_type = np.array([str(error_type),])
  except Exception:
    message, tb = sys.exc_info()[1:]
    _shared.reraise(ValueError, ('The error_type=%s is invalid: %s' % (error_type, message)), tb)

  aggregate_error = any(criterion not in basic_error_types_list for criterion in error_type)

  if aggregate_error:
    if any(criterion not in complex_error_types_list for criterion in error_type):
      raise ValueError('The error_type=%s should be one of the following: %s'
                        % (error_type, complex_error_types_list))
    elif 1 != error_type.size:
      raise ValueError('The error_type=%s is aggregate and should have dimension 1' % error_type)
  elif error_type.size != size_f:
    if 1 == error_type.size:
      error_type = np.tile(error_type, size_f)
    else:
      raise ValueError('Wrong error_type dimensionality: %d (1%s expected).'
                       % (error_type.size, ('' if 1 == size_f else ' or %d' % size_f)))

  return error_type, aggregate_error


def _check_errors(model, x_sample, f_sample, error_type, error_thresholds):
  # calculate standard errors
  if isinstance(model, ctypes.c_void_p):
    from . import model as _gtamodel
    model = _gtamodel.Model(handle=model, weak_handle=True)
  errors = model.validate(x_sample, f_sample)

  # calculate PTP errors, x_sample and _f_sample should be already ndarrays with ndim=2
  finite_indices = np.isfinite(f_sample)
  if not finite_indices.all():
    f_range = np.array([np.ptp(f_sample[finite_indices[:, i], i]) for i in range(f_sample.shape[1])])
  else:
    f_range = np.ptp(np.array(f_sample, dtype=float), axis=0)

  nonzero_range = np.not_equal(f_range, 0.)
  zero_range = np.equal(f_range, 0.)

  for error_name in ['Mean', 'Max', 'RMS']:
    normalized_name = error_name + '_PTP'
    if normalized_name not in errors:
      normalized_error = np.array(errors[error_name], dtype=float)
      normalized_error[nonzero_range] /= f_range[nonzero_range]
      normalized_error[zero_range] = np.nan
      errors[normalized_name] = normalized_error

  if isinstance(error_type, string_types):
    # aggregate error
    averaging_type, error_type = error_type.split(' ')
    averaged_errors = _utilities.calculate_errors(np.array(errors[error_type]).reshape(-1, 1), np.zeros((model.size_f, 1)))
    return averaged_errors[averaging_type][0] <= error_thresholds
  # componentwise error
  return all(errors[error_type[i]][i] <= error_thresholds[i] for i in range(model.size_f))

def _perform_errbased_smoothing(x_sample, f_sample, error_type, error_thresholds, x_weights, model):
  inputwise_smoothness_size = x_weights.shape[1]
  batch_smooth = _AnisotropicSmoothing('Error-based smoothing has failed.')

  least_smoothed_model = batch_smooth.smooth(model, [[0.]], 1)
  if not np.any(x_weights > 0.) or not _check_errors(least_smoothed_model, x_sample, f_sample, error_type, error_thresholds):
    # even zero-smoothed model does not meet the requirements
    return least_smoothed_model

  most_smoothed_model = batch_smooth.smooth(model, [[1.]], 1)
  if _check_errors(most_smoothed_model, x_sample, f_sample, error_type, error_thresholds):
    return most_smoothed_model

  # we've already checked that there is at least one positive component
  minimal_smoothing_component = x_weights[x_weights > 0.].min()

  scaling_parameter = 0.5 / minimal_smoothing_component
  scaling_step = scaling_parameter / 2.

  optimal_model = None
  while not (scaling_step < 0.00001):
    current_smoothing_weights = x_weights.copy() * scaling_parameter
    current_smoothing_weights[current_smoothing_weights > 1.] = 1.
    current_smoothing_weights[current_smoothing_weights < 0.] = 0.

    smoothed_model = batch_smooth.smooth(model, current_smoothing_weights, inputwise_smoothness_size)

    if _check_errors(smoothed_model, x_sample, f_sample, error_type, error_thresholds):
      optimal_model = smoothed_model
      scaling_parameter = scaling_parameter + scaling_step
    else:
      scaling_parameter = scaling_parameter - scaling_step

    scaling_step = scaling_step / 2

  return least_smoothed_model if optimal_model is None else optimal_model


def _smooth(f_smoothness, model):
  f_smoothness = _check_input_f_smoothness(f_smoothness, model.size_f)
  return _AnisotropicSmoothing('Model smoothing has failed.').smooth(model, f_smoothness.reshape((-1, 1)), vector_size=1)


def _smooth_anisotropic(f_smoothness, x_weights, model):
  f_smoothness = _check_input_f_smoothness(f_smoothness, model.size_f)
  x_weights = _check_input_x_weights(x_weights, model.size_x, model.size_f)

  if x_weights.max() == 0:
    return _AnisotropicSmoothing('Model smoothing has failed.').smooth(model, [0], vector_size=1)

  outputwise_smoothness_size, inputwise_smoothness_size = x_weights.shape
  f_smoothness_size = len(f_smoothness)

  final_smoothing_weights = np.zeros((max(outputwise_smoothness_size, f_smoothness_size),
                                     inputwise_smoothness_size))

  for input_index in range(inputwise_smoothness_size):
    if f_smoothness_size == 1 and f_smoothness[0] == 0:
      break
    if outputwise_smoothness_size == 1 and f_smoothness_size == 1:
      max_weight = max(x_weights[0])
      final_smoothing_weights[0][input_index] = x_weights[0][input_index] * f_smoothness[0] / max_weight
    elif outputwise_smoothness_size == 1 or f_smoothness_size == 1:
      max_weights = [max(weights_vector) for weights_vector in x_weights]
      max_weights = [1 if weight == 0 else weight for weight in max_weights]

      if outputwise_smoothness_size == 1:
        for output_index in range(f_smoothness_size):
          final_smoothing_weights[output_index][input_index] = x_weights[0][input_index] * f_smoothness[output_index] / max_weights[0]

      if f_smoothness_size == 1:
        for output_index in range(outputwise_smoothness_size):
          final_smoothing_weights[output_index][input_index] = (x_weights[output_index][input_index] * f_smoothness[0] /
                                                                max_weights[output_index])
    else:
      max_weights = [max(weights_vector) for weights_vector in x_weights]
      max_weights = [1 if weight == 0 else weight for weight in max_weights]

      for output_index in range(outputwise_smoothness_size):
        final_smoothing_weights[output_index][input_index] = (x_weights[output_index][input_index] * f_smoothness[output_index] /
                                                              max_weights[output_index])

  return _AnisotropicSmoothing('Anisotropic smoothing has failed.').smooth(model, final_smoothing_weights, vector_size=inputwise_smoothness_size)

def _smooth_errbased(x_sample, f_sample, error_type, error_thresholds, x_weights, model):
  x, f = _process_sample(x_sample, f_sample, model.size_x, model.size_f)

  error_thresholds, error_type = _check_input_error_thresholds(error_thresholds, error_type, model.size_f)
  x_weights = _check_input_x_weights(x_weights, model.size_x, model.size_f)

  return _perform_errbased_smoothing(x, f, error_type, error_thresholds, x_weights, model)
