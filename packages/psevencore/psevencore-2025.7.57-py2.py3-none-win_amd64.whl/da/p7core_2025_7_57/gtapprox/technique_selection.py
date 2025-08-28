#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present


# Note: It is assumed that the training sample is already preprocessed (constant columns are removed, duplicates are removed, etc.)
from __future__ import with_statement
from __future__ import division

import sys
import math
import ctypes as _ctypes
import numpy as np

from ..six import string_types, iteritems
from ..six.moves import xrange, range

from .. import shared as _shared
from .. import exceptions as _ex
from .. import options as _options
from .. import loggers
from .moa_preprocessing import calc_cluster_size
from .utilities import Utilities, _parse_dry_run
from .model import Model

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_void_ptr_ptr = _ctypes.POINTER(_ctypes.c_void_p)

    self.get_unique_points = _ctypes.CFUNCTYPE(_ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t
                                          , self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr
                                          , self.c_double_ptr, self.c_size_ptr, self.c_size_ptr, self.c_size_ptr, self.c_size_ptr
                                          , self.c_size_ptr, self.c_size_ptr)(('GTApproxUniquePointsIndices', self.__library))
    self.is_ita = _ctypes.CFUNCTYPE(_ctypes.c_int, _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_ptr,
                                    _ctypes.c_size_t, _ctypes.c_void_p)(('GTApproxUtilitiesCheckIncompleteTensorStructure', self.__library))
    self.select_nan_marker = _ctypes.CFUNCTYPE(_ctypes.c_double, _ctypes.c_size_t, _ctypes.c_size_t, # marker or nan on failure, vectors number, vector dim
                                               self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t, # pointer to te first vector, next vector, next vector element
                                               _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxSelectNanMarker', self.__library))
    self.hardware_configuration = _ctypes.CFUNCTYPE(_ctypes.c_short, self.c_size_ptr, self.c_size_ptr, self.c_size_ptr,  # succeeded, recommended concurrency, physical cores number, L1 cache size in bytes
                                                    self.c_size_ptr)(('GTApproxUtilitiesHardwareConfiguration', self.__library)) # L2 cache size in bytes
    self.is_compatible_inputs_encoding = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_short),
                                                           self.c_void_ptr_ptr)(('GTApproxUtilitiesIsCompatibleInputsEncoding', self.__library))
    self.encode_inputs = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t
                                           , self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr
                                           , self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr
                                           , _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxUtilitiesEncodeInputs', _shared._library))

_api = _API()

def _get_technique_official_name(technique):
  official_names = {'gbrt': 'GBRT',
                    'gp': 'GP',
                    'hda': 'HDA',
                    'hdagp': 'HDAGP',
                    'ita': 'iTA',
                    'moa': 'MoA',
                    'rsm': 'RSM',
                    'pla': 'PLA',
                    'splt': 'SPLT',
                    'sgp': 'SGP',
                    'ta': 'TA',
                    'tbl': 'TBL',
                    'tgp': 'TGP',
                    'auto': 'Auto'
                   }
  return official_names[technique.lower()]

def _read_iv_options_impl(iv_subsets, iv_subset_size, iv_rounds, sample_size, validate):
  if iv_subset_size <= 0:
    if iv_subsets and validate and (iv_subsets > sample_size or (iv_subsets < 2 and sample_size >= 2)):
      raise _ex.InvalidOptionsError('Invalid option value: GTApprox/IVSubsetCount=%d not in [2, %d] range' % (iv_subsets, sample_size,))
  elif iv_subsets <= 0:
    iv_subsets = (sample_size + iv_subset_size // 2) // iv_subset_size # integer division with rounding
    if iv_subsets and validate and (iv_subsets > sample_size or (iv_subsets < 2 and sample_size >= 2)):
      iv_subset_size_maxval = (2 * sample_size) // 3
      raise _ex.InvalidOptionsError('Invalid option value: GTApprox/IVSubsetSize=%d. Valid range is [1, %d] where %d is 2/3 of the sample size %d.' % (iv_subset_size, iv_subset_size_maxval, iv_subset_size_maxval, sample_size,))
  else:
    raise _ex.InvalidOptionsError('Options GTApprox/IVSubsetCount and GTApprox/IVSubsetSize are mutually exclusive. ' +
                                  'Current options values are GTApprox/IVSubsetCount=%d, GTApprox/IVSubsetSize=%d.' % (iv_subsets, iv_subset_size,))

  if 0 == iv_subsets:
    iv_subsets = min(10, sample_size)

  if 0 == iv_rounds:
    max_subset_size = (sample_size + iv_subsets - 1) // iv_subsets # maximal size of single test subsample
    min_test_points = int(sample_size / (sample_size - 10)**0.5 + 0.5) if sample_size > 11 else 9 if sample_size == 11 else max(1, sample_size)
    min_iv_rounds = (min_test_points + max_subset_size - 1) // max_subset_size # that's why we must perform at least this number of training sessions
    normal_iv_rounds = (sample_size + 99) // sample_size # this is usual number of training sessions: ceil(100 / sample_size)
    proposed_rounds = 1 if sample_size < 1 else max(1, min(sample_size, max(min_iv_rounds, normal_iv_rounds)))
    iv_rounds = min(iv_subsets, proposed_rounds)

  return max(1, iv_subsets), max(1, min(iv_subsets, iv_rounds))


class _SampleData(object):
  def __init__(self, x, y, outputNoiseVariance, weights, catvars, x_tol=None, xy_nan_mode={'x': 'raise', 'y': 'raise'}):
    assert isinstance(x, np.ndarray) and isinstance(y, np.ndarray) and x.shape[0] == y.shape[0]
    assert outputNoiseVariance is None or (isinstance(outputNoiseVariance, np.ndarray) and outputNoiseVariance.shape == y.shape)
    assert weights is None or (isinstance(weights, np.ndarray) and weights.shape == (y.shape[0],))

    def columnwise_eps(x_min, x_max, eps=np.finfo(float).eps):
      # Keep it synced with other constant-column checks (#constantcolumncheck)
      return eps * np.array([max(1, a, b) for a, b in zip(x_min, x_max)])

    def finite_minmax(data):
      result = np.empty((2, data.shape[1]))
      for k, x in enumerate(data.T):
        i = np.isfinite(x)
        if not i.all():
          x = x[i]
          if not x.size:
            result[:, k] = np.nan
            continue
        result[0, k] = x.min()
        result[1, k] = x.max()
      return result[0], result[1]

    x_min, x_max = finite_minmax(x)

    self.__original = {'x': x, 'y': y, 'tol': outputNoiseVariance, 'w': weights}
    self.__original_shape = (x.shape[0], x.shape[1], y.shape[1],)
    self.__catvars = sorted(catvars)

    self.__x_tol = np.array(x_tol if x_tol is not None else [], dtype=float)
    if np.any(self.__x_tol != 0.):
      zero_mask = (self.__x_tol <= 2. * columnwise_eps(x_min, x_max, np.finfo(float).tiny))

      x_step = self.__x_tol.copy()
      x_step[zero_mask] = 1.

      x_clean = np.divide(x, x_step)
      np.add(0.5, x_clean, out=x_clean)
      np.floor(x_clean, out=x_clean)
      np.multiply(x_clean, x_step, out=x_clean)

      x_clean[:, zero_mask] = x[:, zero_mask]
      x = x_clean

    unique_pts = np.arange(x.shape[0], dtype=_ctypes.c_size_t)
    ambiguos_pts = np.zeros((1 + y.shape[1],), dtype=_ctypes.c_size_t)
    duplicate_pts = np.zeros((1 + y.shape[1],), dtype=_ctypes.c_size_t)
    n_pts = _api.get_unique_points(x.shape[0], x.shape[1], y.shape[1]
                              , x.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(x.ctypes.strides, _api.c_size_ptr)
                              , y.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(y.ctypes.strides, _api.c_size_ptr)
                              , _api.c_double_ptr() if outputNoiseVariance is None else outputNoiseVariance.ctypes.data_as(_api.c_double_ptr)
                              , _api.c_size_ptr() if outputNoiseVariance is None else _ctypes.cast(outputNoiseVariance.ctypes.strides, _api.c_size_ptr)
                              , _api.c_double_ptr() if weights is None else weights.ctypes.data_as(_api.c_double_ptr)
                              , _api.c_size_ptr() if weights is None else _ctypes.cast(weights.ctypes.strides, _api.c_size_ptr)
                              , unique_pts.ctypes.data_as(_api.c_size_ptr), _ctypes.cast(unique_pts.ctypes.strides, _api.c_size_ptr)
                              , ambiguos_pts.ctypes.data_as(_api.c_size_ptr), _ctypes.cast(ambiguos_pts.ctypes.strides, _api.c_size_ptr)
                              , duplicate_pts.ctypes.data_as(_api.c_size_ptr), _ctypes.cast(duplicate_pts.ctypes.strides, _api.c_size_ptr)
                              )
    self.__unique_x = x if n_pts == x.shape[0] else x[unique_pts[:n_pts]] # the unique input points. Needed to check tensor structure
    self.__ambiguos_pts = ambiguos_pts # the outputwise number of ambiguous points extended by the number of ambiguous point if outputs are dependent
    self.__duplicate_pts = duplicate_pts # the outputwise number of duplicate points (NaNs are not duplicated even if they are) extended by the number of ambiguous point if outputs are dependent

    # detect and save invalid values structure
    if 'preserve' == xy_nan_mode['x'].lower():
      # only nans and finite values allowed s.t. at least one finite value is required
      invalid_x = ~np.logical_and(np.logical_or(np.isnan(x), np.isfinite(x)).all(axis=1), np.isfinite(x).any(axis=1))
    else:
      invalid_x = ~np.isfinite(x).all(axis=1) # all vector values must be finite

    invalid_y = ~np.isfinite(y)

    # find variable inputs and outputs with respect to NaNs structure
    with np.errstate(all='ignore'):
      x_vars = (x_max - x_min) > columnwise_eps(x_min, x_max)
      x_vars[list(self.__catvars)] = False
      y_min, y_max = finite_minmax(y)
      y_vars = (y_max - y_min) > columnwise_eps(y_min, y_max)

    if 'predict' == xy_nan_mode['y'].lower():
      # any output column with NaNs prediction should not be constant
      if np.any(invalid_y):
        y_vars[np.any(invalid_y, axis=0) != np.all(invalid_y, axis=0)] = True

      # NaN y should not be marked as invalid_y_cw (Use XOR taking into account that invalid_y is False implies np.isnan(y) is False too)
      invalid_y_cw = np.logical_xor(invalid_y, np.isnan(y)).any(axis=0)
    else:
      invalid_y_cw = invalid_y.any(axis=0)

    self.__variables = {'x': np.where(x_vars)[0], 'y': np.where(y_vars)[0]}

    self.__nan_properties = {  'count': np.zeros((1 + y.shape[1],), dtype=_ctypes.c_size_t)  # should be empty to indicate abcense of NaNs in output
                             , 'mixed': False
                             , 'invalid_x': invalid_x
                             , 'has_invalid_y': np.hstack((invalid_y_cw, invalid_y_cw.any()))}

    invalid_y[invalid_x, :] = True

    if np.any(invalid_y):
      self.__nan_properties['invalid_y'] = invalid_y
      self.__nan_properties['count'][:-1] = invalid_y.sum(axis=0)
      self.__nan_properties['count'][-1] = np.all(invalid_y, axis=1).sum()

      # 'mixed' indicates that some output vectors contains both NaN and non-NaN values.
      self.__nan_properties['mixed'] = (invalid_y.shape[1] > 1) and (np.any(np.any(invalid_y, axis=1) != np.all(invalid_y, axis=1)))

      # Collect outputwise boolean indices of unique input elements that should be excluded because relative output is NaN.
      # Note it's boolean indices of the self.__unique_x matrix, not the self.__original['x']!
      unique_x_filter = np.empty((n_pts, invalid_y.shape[1] + 1), dtype=bool)
      unique_x_filter[:, :-1] = invalid_y[unique_pts[:n_pts]]
      unique_x_filter[:, -1] = np.any(unique_x_filter[:, :-1], axis=1)
      if np.any(unique_x_filter[:, -1]):
        np.logical_not(unique_x_filter, out=unique_x_filter)
        self.__nan_properties['x_filter'] = unique_x_filter

    # check output noise variance presence and effectiveness
    if outputNoiseVariance is not None:
      ignorable_tol = np.isnan(outputNoiseVariance)
      ignorable_tol = np.logical_or(outputNoiseVariance == 0., ignorable_tol, out=ignorable_tol)
      self.__has_output_tol = ~np.all(ignorable_tol, axis=0)
    else:
      self.__has_output_tol = [False,]*y.shape[1]

    self.__effective_shape = None # cached value

  def slice(self, output_index):
    if output_index is None:
      return self

    try:
      output_index_list = [i for i in output_index if i >= 0]
      if len(output_index_list) == 1:
        output_index = output_index_list[0]
        output_index_list = None
    except:
      output_index_list = None

    if (output_index < 0 if output_index_list is None else not output_index_list):
      return

    sample = _SampleData.__new__(_SampleData)

    x = self.__original['x']
    y = self.__original['y'][:, output_index]
    if y.ndim == 1:
      y = y.reshape((-1, 1))

    tol = self.__original['tol']
    if tol is not None:
      tol = tol[:, output_index]
      if tol.ndim == 1:
        tol = tol.reshape((-1, 1))

    weights = self.__original['w']

    sample.__original = {'x': x, 'y': y, 'tol': tol, 'w': weights}

    sample.__original_shape = (x.shape[0], x.shape[1], y.shape[1],)
    sample.__catvars = self.__catvars
    sample.__x_tol = self.__x_tol
    sample.__unique_x = self.__unique_x

    if output_index_list is None:
      # simple case
      sample.__ambiguos_pts = self.__ambiguos_pts[[output_index, output_index]]
      sample.__duplicate_pts = self.__duplicate_pts[[output_index, output_index]]
      sample.__variables = {'x': self.__variables['x'], 'y': ([0,] if output_index in self.__variables['y'] else [])}
      sample.__nan_properties = {'count': self.__nan_properties['count'][[output_index, output_index]], 'mixed': False,
                                 'invalid_x': self.__nan_properties['invalid_x'],
                                 'has_invalid_y': self.__nan_properties['has_invalid_y'][[output_index, output_index]],
                                 'mixed': False,}
      if sample.__nan_properties["count"][-1] > 0 and self.__nan_properties.get("invalid_y") is not None:
        sample.__nan_properties['invalid_y'] = self.__nan_properties['invalid_y'][:, output_index].reshape(-1, 1)
      if self.__nan_properties.get('x_filter') is not None:
        sample.__nan_properties['x_filter'] = self.__nan_properties['x_filter'][:, [output_index, output_index]]
      sample.__has_output_tol = [self.__has_output_tol[output_index], self.__has_output_tol[output_index]]
    else:
      # not so simple case and it's easer to re-evaluate some parameters
      ambiguos_pts = np.zeros((1 + y.shape[1],), dtype=_ctypes.c_size_t)
      duplicate_pts = np.zeros((1 + y.shape[1],), dtype=_ctypes.c_size_t)
      if np.count_nonzero(self.__ambiguos_pts[output_index_list]) or np.count_nonzero(self.__duplicate_pts[output_index_list]):
        unique_pts = np.arange(x.shape[0], dtype=_ctypes.c_size_t)
        n_pts = _api.get_unique_points(x.shape[0], x.shape[1], y.shape[1]
                                  , x.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(x.ctypes.strides, _api.c_size_ptr)
                                  , y.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(y.ctypes.strides, _api.c_size_ptr)
                                  , _api.c_double_ptr() if tol is None else tol.ctypes.data_as(_api.c_double_ptr)
                                  , _api.c_size_ptr() if tol is None else _ctypes.cast(tol.ctypes.strides, _api.c_size_ptr)
                                  , _api.c_double_ptr() if weights is None else weights.ctypes.data_as(_api.c_double_ptr)
                                  , _api.c_size_ptr() if weights is None else _ctypes.cast(weights.ctypes.strides, _api.c_size_ptr)
                                  , unique_pts.ctypes.data_as(_api.c_size_ptr), _ctypes.cast(unique_pts.ctypes.strides, _api.c_size_ptr)
                                  , ambiguos_pts.ctypes.data_as(_api.c_size_ptr), _ctypes.cast(ambiguos_pts.ctypes.strides, _api.c_size_ptr)
                                  , duplicate_pts.ctypes.data_as(_api.c_size_ptr), _ctypes.cast(duplicate_pts.ctypes.strides, _api.c_size_ptr)
                                  )
        sample.__unique_x = x if n_pts == x.shape[0] else x[unique_pts[:n_pts]] # the unique input points. Needed to check tensor structure
        if not np.logical_or(sample.__unique_x == self.__unique_x, np.logical_and(np.isnan(sample.__unique_x), np.isnan(self.__unique_x))).all():
          raise _ex.UnsupportedProblemError("The dataset given have too complicated NaN landscape.")

      sample.__ambiguos_pts = ambiguos_pts # the outputwise number of ambiguous points extended by the number of ambiguous point if outputs are dependent
      sample.__duplicate_pts = duplicate_pts # the outputwise number of duplicate points (NaNs are not duplicated even if they are) extended by the number of ambiguous point if outputs are dependent
      sample.__variables = {'x': self.__variables['x'], 'y': [k for k, i in enumerate(output_index_list) if i in self.__variables['y']]}

      sample.__has_output_tol = [self.__has_output_tol[i] for i in output_index_list]
      sample.__has_output_tol.append(any(sample.__has_output_tol))

      invalid_y_cw = self.__nan_properties["has_invalid_y"][output_index_list]

      sample.__nan_properties = {'invalid_x': self.__nan_properties['invalid_x'],
                                 'has_invalid_y': np.hstack((invalid_y_cw, invalid_y_cw.any())),
                                 'count': self.__nan_properties["count"][output_index_list + [-1,]],
                                 'mixed': False}

      if sample.__nan_properties["has_invalid_y"][-1] and self.__nan_properties.get("invalid_y") is not None:
        invalid_y = self.__nan_properties['invalid_y'][:, output_index_list]
        sample.__nan_properties['invalid_y'] = invalid_y
        sample.__nan_properties['count'][-1] = np.all(invalid_y, axis=1).sum()
        sample.__nan_properties['mixed'] = (np.any(np.any(invalid_y, axis=1) != np.all(invalid_y, axis=1)))

      if self.__nan_properties.get('x_filter') is not None:
        sample.__nan_properties['x_filter'] = self.__nan_properties['x_filter'][:, output_index_list + [-1,]]
        sample.__nan_properties['x_filter'][:, -1] = np.any(sample.__nan_properties['x_filter'][:, :-1], axis=1)

    sample.__effective_shape = None # cached value
    return sample


  @property
  def original_shape(self):
    return self.__original_shape

  @property
  def original_sample(self):
    return self.__original

  @property
  def effective_shape(self):
    if self.__effective_shape is None:
      self.__effective_shape = (_shared.long_integer(max(1, self.__original['x'].shape[0] - self.__ambiguos_pts[-1] - self.__duplicate_pts[-1] - self.__nan_properties['count'][-1])) \
                                , len(self.__variables['x']), len(self.__variables['y']),)
    return self.__effective_shape

  @property
  def x_tol(self):
    return self.__x_tol

  @property
  def duplicate_points(self):
    return self.__duplicate_pts

  @property
  def ambiguous_points(self):
    return self.__ambiguos_pts

  @property
  def variable_columns(self):
    return self.__variables

  @property
  def catvars(self):
    return self.__catvars

  @property
  def has_output_tol(self):
    return np.any(self.__has_output_tol)

  @property
  def nan_info(self):
    """
    Properties of the output NaNs. Dictionary with the following keys:
    'count' - (size_y + 1) dimensional np.array of integers. The number of NaNs per output
              extended by the number of NaNs in dependent outputs mode.
    'mixed' - indicates existance of output vector with mixed NaN and finite values.
              If 'mixed' is True then model can be trained in a componentwise mode only.
    'x_filter' - Optional m-by-(size_y+1) dimensional boolean array, where m is the number of unique input points.
                 If absent then all unique inputs are valid, otherwise each column is filter of
                 unique inputs matrix w.r.t. output NaNs. The last column is 'dependent outputs'
                 mode filter
    'invalid_x' - Boolean vector of invalid inputs.
    'has_invalid_y' - (size_y + 1) dimensional np.array of booleans. Indicators of outputwise
                       non-finite values presence in the original output sample
                       extended by the whole sample indicator. Note NaN output is valid value
                       in case of 'predict' mode
    """
    return self.__nan_properties

  def unique_inputs(self, filtered, output_index=None):
    return self.__unique_x if not filtered or self.__nan_properties.get('x_filter') is None \
      else self.__unique_x[self.__nan_properties['x_filter'][:, (-1 if output_index is None else output_index)], :]

  def same_nan_structure(self, left_output, right_output):
    if left_output == right_output:
      return True
    x_filter = self.__nan_properties.get('x_filter')
    return x_filter is None or np.all(x_filter[:, left_output] == x_filter[:, right_output])

  def effective_cardinality(self, output_index=None):
    if output_index not in [-1, None] and output_index not in self.__variables['y']:
      return 0

    n_invalid_points = 0
    output_index = -1 if output_index is None else output_index
    if self.__nan_properties.get('x_filter') is not None:
      # After unique points filtering, those with all nan input components will be filtered as well,
      # while valid_y is a mask of points with no nans in input or output components (considering cw mode as well).
      # Hence x_filter is a mask of points that are unique and valid at the same time.
      x_filter = self.__nan_properties['x_filter'][:, output_index]
      n_invalid_points = x_filter.shape[0] - np.count_nonzero(x_filter)
    else:
      n_invalid_points = self.__nan_properties['count'][output_index]
    return _shared.long_integer(len(self.__unique_x) - n_invalid_points)

def _get_unique_elements(x, return_indices):
  """
  Find unique rows in a given matrix
  Return:
    array-like: - unique rows
    list[array_like]: - list of indices of duplicate rows
  """
  valid_x = np.where(~np.isnan(x).any(axis=1))[0] if np.isnan(x).any() else None
  sort_order = _shared._lexsort(x) if valid_x is None else valid_x[_shared._lexsort(x[valid_x])]

  if len(sort_order) == 0:
    return x if not return_indices else []
  elif len(sort_order) == 1:
    return x[sort_order] if not return_indices else [sort_order[0],]

  x_sorted = x[sort_order]

  differences = np.diff(x_sorted, axis=0)
  unique_indices = np.ones(len(x_sorted), dtype=bool)
  unique_indices[1:] = (differences != 0).any(axis=1)

  if np.all(unique_indices) and valid_x is None:
    # all input elements are unique and valid
    return x if not return_indices else []
  elif not return_indices:
    return x_sorted[unique_indices]

  # @todo : refactor it!
  nonzero_diff_indices = np.argwhere(unique_indices).reshape(-1) # argwhere returns a single column matrix

  duplicate_indices = []
  for i in xrange(1, len(nonzero_diff_indices)):
    duplicate_indices += [sort_order[np.arange(nonzero_diff_indices[i - 1], nonzero_diff_indices[i])]]

  duplicate_indices += [sort_order[np.arange(nonzero_diff_indices[-1], len(x_sorted))]]

  return duplicate_indices

def check_GBRT(sample, options, initial_model, check_only_sample=False):
  reason = ''

  if check_only_sample:
    return reason

  _test_initial_model('GBRT', initial_model, True)

  #not supported options
  get_reason_list = [_get_linearity_reason, _get_exactfit_reason,
                     _get_accuracy_evaluation_reason, _get_outputNoiseVariance_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('GBRT', options, sample.has_output_tol)

  if not initial_model and options.get('GTApprox/Technique').lower() != 'gbrt':
    reason += '\nthis technique trains a piecewise constant model that does not support gradient evaluation'

  return reason


def check_GP(sample, options, initial_model, check_only_sample=False):
  reason = ''

  # check sample size, input and output dimensions
  sample_size, x_dim, y_dim = sample.effective_shape
  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample_size, 2 * (max(1, x_dim) + max(1, y_dim)) + 1)

  sample_limit = 4000
  try:
    sgp_range = options.info("GTApprox/SGPNumberOfBasePoints").get("OptionDescription", {}).get("Ranges")
    if sgp_range is not None:
      sample_limit = int(sgp_range.split(",")[-1].strip(" )]"))
  except:
    pass

  if sample_size > sample_limit:
    error_message = "The effective training sample size (%d) exceeds the %d points limit." % (sample_size, sample_limit)
    raise _ex.InapplicableTechniqueException(error_message)

  if x_dim < 1:
    reason += "\neffective dimensionality of input vector is equal to %d" % x_dim

  if y_dim > 15 or _shared.parse_bool(options.get('GTApprox/ExactFitRequired')):
    if sample_size > int(options.get('/GTApprox/MaxSampleSizeForHDAGP')):
      reason += "\ntraining sample size is equal or greater than default threshold value (%s)" % options.get('/GTApprox/MaxSampleSizeForHDAGP')
  else:
    if sample_size >= int(options.get('/GTApprox/MaxSampleSizeForGP')):
      reason += "\ntraining sample size is equal or greater than default threshold value (%s)" % options.get('/GTApprox/MaxSampleSizeForGP')

  if check_only_sample:
    return reason

  _test_initial_model('GP', initial_model, True)

  #not supported options
  get_reason_list = [_get_linearity_reason, _get_covariance_type_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('GP', options, sample.has_output_tol)

  #check outputNoiseVariance
  if _shared.parse_bool(options.get('gtapprox/ExactFitRequired')):
    if sample.has_output_tol:
      reason += "\nthe 'exact fit' mode is not available for GP with known variance of the output noise"
    if int(options.get('GTApprox/MaxAxisRotations')) > 0:
      reason += "\nthe 'exact fit' requirement is incompatible with gradient bagging mode"
    if options.get("GTApprox/GPLearningMode").lower() == "robust":
      raise _ex.InvalidOptionsError("The 'Robust' learning mode is incompatible with the 'Exact Fit' requirement.")

  return reason


def check_HDA(sample, options, initial_model, check_only_sample=False):
  reason = ''

  # check sample size, input and output dimensions
  sample_size, x_dim, y_dim = sample.effective_shape
  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample_size, 2 * (max(1, x_dim) + max(1, y_dim)) + 1)

  if x_dim < 1:
    reason += "\neffective dimensionality of input vector is equal to %d" % x_dim

  if sample_size < int(options.get('/gtapprox/MinSampleSizeForHDA')):
    reason += "\ntraining sample size below threshold (%s)" % options.get('/gtapprox/MinSampleSizeForHDA')

  if check_only_sample:
    return reason

  _test_initial_model('HDA', initial_model, False)

  # check options
  get_reason_list = [_get_linearity_reason, _get_exactfit_reason, _get_accuracy_evaluation_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('HDA', options, sample.has_output_tol)

  return reason


def check_HDAGP(sample, options, initial_model, check_only_sample=False):
  reason = ''

  # check sample size, input and output dimensions
  sample_size, x_dim, y_dim = sample.effective_shape
  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample_size, 2 * (max(1, x_dim) + max(1, y_dim)) + 1)

  sample_limit = 4000
  try:
    sgp_range = options.info("GTApprox/SGPNumberOfBasePoints").get("OptionDescription", {}).get("Ranges")
    if sgp_range is not None:
      sample_limit = int(sgp_range.split(",")[-1].strip(" )]"))
  except:
    pass

  if sample_size > sample_limit:
    error_message = "The effective training sample size (%d) exceeds the %d points limit." % (sample_size, sample_limit)
    raise _ex.InapplicableTechniqueException(error_message)

  if x_dim < 1:
    reason += "\neffective dimensionality of input vector is equal to %d" % x_dim

  if y_dim > 15:
    reason += "\neffective dimensionality of output vector is greater than 15"

  if sample_size > int(options.get('/GTApprox/MaxSampleSizeForHDAGP')):
    reason += "\ntraining sample size is greater than default threshold value (%s)" % options.get('/GTApprox/MaxSampleSizeForHDAGP')

  if sample_size < int(options.get('/GTApprox/MaxSampleSizeForGP')):
    reason += "\ntraining sample size is less than default threshold value (%s)" % options.get('/GTApprox/MaxSampleSizeForGP')

  if check_only_sample:
    return reason

  _test_initial_model('HDAGP', initial_model, True)

  #not supported options
  get_reason_list = [_get_linearity_reason, _get_exactfit_reason, _get_covariance_type_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('HDAGP', options, sample.has_output_tol)

  #check outputNoiseVariance
  if _shared.parse_bool(options.get('gtapprox/ExactFitRequired')):
    if sample.has_output_tol:
      reason += "\nthe 'exact fit' mode is not available for GP with known variance of the output noise"
    if int(options.get('GTApprox/MaxAxisRotations')) > 0:
      reason += "\nthe 'exact fit' requirement is incompatible with gradient bagging mode"

  return reason


def check_PLA(sample, options, initial_model, check_only_sample=False):
  reason = ''

  # check sample size, input and output dimensions
  sample_size, x_dim, y_dim = sample.effective_shape
  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample_size, max(1, x_dim) + 1)

  complexityLog10 = ((x_dim + 1.0) / 2.0) * math.log(sample_size) / math.log(10.)
  if complexityLog10 >= 9:
    reason += "\nalgorithmic complexity is O(1.e%d)" % math.ceil(complexityLog10)

  if check_only_sample:
    return reason

  _test_initial_model('PLA', initial_model, False)

  # check options
  get_reason_list = [_get_accuracy_evaluation_reason, _get_outputNoiseVariance_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('PLA', options, sample.has_output_tol)

  if x_dim < 1:
    reason += "\neffective dimensionality of input vector is equal to %d" % x_dim

  if options.get('GTApprox/Technique').lower() != 'pla':
    reason += '\nthis technique trains a piecewise linear model with discontinuous gradients, and PLA models are expensive to evaluate'

  return reason


def check_RSM(sample, options, initial_model, check_only_sample=False):
  reason = ''


  # check sample size, input and output dimensions
  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample.effective_shape[0], 1)

  if check_only_sample:
    return reason

  _test_initial_model('RSM', initial_model, False)

  # check options
  errorMessage = _get_rsm_options_incompatibility_reason(sample.effective_shape[1], sample.effective_shape[2], options)
  if errorMessage:
    raise _ex.InapplicableTechniqueException(errorMessage)

  if _shared.parse_bool(options.get('GTApprox/LinearityRequired')):
    surface_type = options.get('GTApprox/RSMType').lower()

    if surface_type in ('linear', 'auto'):
      pass
    elif surface_type in ('quadratic', 'purequadratic', 'interaction'):
      raise _ex.InvalidOptionsError("The value of option %s=%s is incompatible with the linear approximation requirement" %
                                    (options.info('gtapprox/rsmtype')['OptionDescription']['Name'], surface_type.title()))

    else:
      raise _ex.InvalidOptionsError("Unknown value of option %s=%s" % (options.info('gtapprox/rsmtype')['OptionDescription']['Name'],
                                                                       surface_type))

  #not supported options
  get_reason_list = [_get_accuracy_evaluation_reason,]

  # RSM can fit training sample if there are no duplicates and sample size is not greater than input dimensionality
  # @todo: There are more cases when RSM fits training sample. Additional linear/quadratic validation is needed.
  if sample.ambiguous_points[-1] or sample.effective_shape[0] > sample.original_shape[1]:
    get_reason_list.append(_get_exactfit_reason)

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('RSM', options, sample.has_output_tol)

  return reason


def check_SGP(sample, options, initial_model, check_only_sample=False):
  if not check_only_sample:
    _test_initial_model('SGP', initial_model, False)

  reason = ''
  #not supported options
  get_reason_list = [_get_linearity_reason, _get_exactfit_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('SGP', options, sample.has_output_tol)

  sample_size, x_dim, y_dim = sample.effective_shape
  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample_size, 2 * (max(1, x_dim) + max(1, y_dim)) + 1)

  if sample.has_output_tol and sample_size < int(options.get('/GTApprox/MaxSampleSizeForSGP')):
    return reason

  if x_dim < 1:
    reason += "\neffective dimensionality of input vector is equal to %d" % x_dim

  if sample_size <= int(options.get('/GTApprox/MaxSampleSizeForHDAGP')):
    reason += "\ntraining sample size is equal or less than default threshold value (%s)" % options.get('/GTApprox/MaxSampleSizeForHDAGP')

  if sample_size >= int(options.get('/GTApprox/MaxSampleSizeForSGP')):
    reason += "\ntraining sample size is equal or greater than default threshold value (%s)" % options.get('/GTApprox/MaxSampleSizeForSGP')

  #not supported options
  reason += _get_covariance_type_reason('SGP', options, sample.has_output_tol)

  return reason


def check_SPLT(sample, options, initial_model, check_only_sample=False):
  reason = ''

  # check sample size, input and output dimensions
  sample_size, x_dim, y_dim = sample.effective_shape

  if x_dim != 1:
    raise _ex.InapplicableTechniqueException("All inputs except one must be either categorical or constant.")

  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample_size, 2 * x_dim + 3)

  if sample.ambiguous_points[-1] > 0:
    raise _ex.InapplicableTechniqueException('%s technique does not support ambiguous samples in the training dataset.' % _get_technique_official_name('splt'))

  if check_only_sample:
    return reason

  _test_initial_model('SPLT', initial_model, False)

  #not supported options
  get_reason_list = [_get_linearity_reason,]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('SPLT', options, sample.has_output_tol)

  if _shared.parse_bool(options.get('/TSplines/Smooth')) and _shared.parse_bool(options.get('GTApprox/ExactFitRequired')):
    raise _ex.InapplicableTechniqueException("Can not build smooth splines in the 'exact fit' mode!")

  return reason

def check_TBL(sample, options, initial_model, check_only_sample=False):
  x_dim = sample.effective_shape[1]
  reason = '' if 0 == x_dim else '\neffective dimensionality of input vector is greater than 0 (%d)' % x_dim

  if check_only_sample:
    return reason

  _test_initial_model('TBL', initial_model, True)

  if _get_technique_official_name('tbl').lower() != options.get('GTApprox/Technique').lower():
    if len(sample.catvars) < sample.original_shape[1]:
      raise _ex.InapplicableTechniqueException('all input variables should be categorical.')

  if _shared.parse_bool(options.get('GTApprox/InternalValidation')):
    raise _ex.InapplicableTechniqueException('%s technique does not support internal validation.' % _get_technique_official_name('tbl'))

  #not supported options
  get_reason_list = [_get_linearity_reason, _get_accuracy_evaluation_reason,
                     _get_outputNoiseVariance_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('TBL', options, sample.has_output_tol)

  return reason

def _normalize_tensor_structure(tensor_factors):
  if not tensor_factors:
    return tensor_factors

  iinf = np.iinfo(int).max
  tensor_factors = [sorted(factor, key=lambda x: iinf if isinstance(x, string_types) else int(x)) for factor in tensor_factors]
  return sorted(tensor_factors, key=lambda x: x[0]) # duplicates are not allowed so

def _validate_tensor_structure(sample, options, check_ta_tech):
  # check tensor structure
  proposed_tensor_factors = _normalize_tensor_structure(_shared.parse_json(options.get('GTApprox/TensorFactors')))
  actual_tensor_factors = _normalize_tensor_structure(_shared.parse_json(options.get('//Service/CartesianStructure')))

  proposed_factor_techniques = ['auto' for _ in range(len(actual_tensor_factors))]
  x_dim = sample.original_shape[1]

  if len(proposed_tensor_factors):
    if len(actual_tensor_factors) != len(proposed_tensor_factors):
      raise _ex.InapplicableTechniqueException("The dataset given doesn't have the proposed tensor structure %s" % (str(proposed_tensor_factors),))

    # compare proposed and actual tensor structure.
    for i, factor in enumerate(proposed_tensor_factors):
      if isinstance(factor[-1], string_types):
        proposed_factor_techniques[i] = factor[-1].lower()
        factor = factor[:-1]

      if max(factor) >= x_dim:
        raise _ex.InvalidOptionsError("Option %s=%s contains invalid input index %d >= %d" % \
                                      (options.info('GTApprox/TensorFactors')['OptionDescription']['Name'],
                                       options.get('GTApprox/TensorFactors'), max(factor), x_dim))
      elif min(factor) < 0:
        raise _ex.InvalidOptionsError("Option %s=%s contains invalid input index %d < 0" % \
                                      (options.info('GTApprox/TensorFactors')['OptionDescription']['Name'],
                                       options.get('GTApprox/TensorFactors'), min(factor)))

  if 0 == len(actual_tensor_factors):
    raise _ex.InapplicableTechniqueException("The dataset given doesn't have tensor structure.")


  categorical_factor = []
  for i, factor in enumerate(actual_tensor_factors):
    if isinstance(factor[-1], string_types):
      factor = factor[:-1]
    categorical_factor.append('dv' == proposed_factor_techniques[i] or all((_ in sample.catvars for _ in factor)))

  def _cardinality():
    cardinality = []
    for i, factor in enumerate(actual_tensor_factors):
      if isinstance(factor[-1], string_types):
        factor = factor[:-1]
      cardinality.append(1 if categorical_factor[i] else len(_get_unique_elements(sample.original_sample['x'][:, factor], return_indices=False)))

    return cardinality

  cardinality = [sample.effective_shape[0]]*len(actual_tensor_factors) if _parse_dry_run(options) == "quick" else None

  if check_ta_tech:
    linearity_required = _shared.parse_bool(options.get('GTApprox/LinearityRequired'))
    exactfit_required = _shared.parse_bool(options.get('GTApprox/ExactFitRequired'))

    failure_reason = ''
    if cardinality is None:
      cardinality = _cardinality()

    for i, factor in enumerate(actual_tensor_factors):
      if categorical_factor[i]:
        continue

      if isinstance(factor[-1], string_types):
        factor = factor[:-1]

      subspace_size = cardinality[i]
      factor_dim = len(factor)

      factor_technique = _select_approximator_technique(proposed_factor_techniques[i], subspace_size, factor_dim, options)

      if factor_technique.lower() == 'bspl':
        if factor_dim != 1:
          failure_reason += "Technique 'BSPL' requested for %d-dimensional factor %s\n" % (factor_dim, str(factor))
          factor_technique = _select_approximator_technique('Auto', subspace_size, factor_dim, options)

      elif factor_technique.lower() not in ['dv', 'gp', 'hda', 'lr', 'lr0', 'pla', 'sgp']:
        failure_reason += "Unknown technique '%s' selected for subspace %s\n" % (factor_technique, str(factor))
        factor_technique = _select_approximator_technique('Auto', subspace_size, factor_dim, options)

      if exactfit_required:
        if (factor_technique.lower() not in ['bspl', 'dv', 'gp', 'pla']) and not (factor_technique.lower() in ['lr0'] and subspace_size == 1):
          failure_reason += "Non-interpolating technique '%s' requested for subspace %s\n" % (factor_technique, str(factor))
          factor_technique = _select_approximator_technique('Auto', subspace_size, factor_dim, options)

      if linearity_required and factor_technique.lower() in ['bspl', 'gp', 'hda', 'sgp']:
        failure_reason += "Non-linear technique '%s' requested for subspace %s%s\n" % (factor_technique, str(factor),
                          " Try to turn off either 'ExactFit' or 'Linearity' requirement." if exactfit_required else "")
        factor_technique = _select_approximator_technique('Auto', subspace_size, factor_dim, options)

      if subspace_size < 2 and (factor_technique in ["bspl", "gp", "sgp"]):
        failure_reason += "The '%s' technique cannot be used for the constant subspace %s. Please, consider using the 'LR0' technique.\n" % (factor_technique.upper(), str(factor))

    if failure_reason:
      raise _ex.InvalidOptionsError(failure_reason)

  if _shared.parse_bool(options.get('GTApprox/InternalValidation')):
    if cardinality is None:
      cardinality = _cardinality()
    if all((_ <= 2 for _ in cardinality)):
      raise _ex.InapplicableTechniqueException("All tensor factors are either categorical or have too small cardinality to perform internal validation.")

  actual_factors_count = np.count_nonzero(np.logical_not(categorical_factor))
  if actual_factors_count < 2:
    return '\nall factors%s are categorical - factored structure is degenerated.' % (" except one" if actual_factors_count else "")

  return ''

def check_iTA(sample, options, initial_model, check_only_sample=False):
  if sample.effective_shape[1] < 2:
    raise _ex.InapplicableTechniqueException("All inputs%s are either categorical or constant." % (" except one" if sample.effective_shape[1] else ""))

  if not check_only_sample:
    _test_initial_model('iTA', initial_model, False)

  # ignore check_only_sample, because sample validation is the most expensive procedure here
  reason = ''

  #not supported options
  get_reason_list = [_get_linearity_reason, _get_accuracy_evaluation_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('iTA', options, sample.has_output_tol)

  # check sample for structure
  sample_size, x_dim, y_dim = sample.effective_shape
  if not _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning')):
    _validate_candidates_sample_size(sample_size, 2 * x_dim + 3) # iTA always have independent outputs

  # effective size
  c_sample = _shared.py_matrix_2c(sample.unique_inputs(filtered=True), name="Filtered sample")
  c_options = options._Options__impl if isinstance(options, _options.Options) else _ctypes.c_void_p()
  ta_code = _api.is_ita(c_sample.array.shape[0], c_sample.array.shape[1], c_sample.ptr, c_sample.ld, c_options)

  if ta_code == 2:
    # emit warning if TA is enabled and input sample is full factorial sample
    if _shared.parse_bool(options.get('GTApprox/EnableTensorFeature')):
      reason += "\nTA technique enabled and can be used for the dataset given"
  elif ta_code != 3:
    # raise an exception if input sample is not incomplete full factorial neither full factorial
    raise _ex.InapplicableTechniqueException("The dataset given is not cartesian product of 1-dimensional subsets with reasonable number of holes.")

  _get_reduction_ratio_reason(options)

  return reason

def check_TA(sample, options, initial_model, check_only_sample=False):
  if sample.effective_shape[1] < 2:
    raise _ex.InapplicableTechniqueException("All inputs%s are either categorical or constant." % (" except one" if sample.effective_shape[1] else ""))

  if not check_only_sample:
    _test_initial_model('TA', initial_model, False)

  reason = _get_accuracy_evaluation_reason('ta', options)

  reason += _validate_tensor_structure(sample, options, True)
  reason += _get_reduction_ratio_reason(options)

  return reason


def check_TGP(sample, options, initial_model, check_only_sample=False):
  if sample.effective_shape[1] < 2:
    raise _ex.InapplicableTechniqueException("All inputs%s are either categorical or constant." % (" except one" if sample.effective_shape[1] else ""))

  if not check_only_sample:
    _test_initial_model('TGP', initial_model, False)

  reason = _get_linearity_reason('TGP', options, sample.has_output_tol)

  if _shared.parse_bool(options.get('gtapprox/ExactFitRequired')) and options.get("GTApprox/GPLearningMode").lower() == "robust":
    raise _ex.InvalidOptionsError("The 'Robust' learning mode is incompatible with the 'Exact Fit' requirement.")

  reason += _validate_tensor_structure(sample, options, False)

  return reason


def check_MoA(sample, options, initial_model, check_only_sample=False):
  reason = ''

  get_reason_list = [_get_linearity_reason, _get_exactfit_reason]

  for get_not_supported_option_reason in get_reason_list:
    reason += get_not_supported_option_reason('MoA', options, sample.has_output_tol)

  alt_tech = None

  iterative_iv_session = _shared.parse_bool(options.get('//IterativeIV/SessionIsRunning'))

  # check for sample size and constant columns
  sample_size, x_dim, y_dim = sample.effective_shape
  if not iterative_iv_session:
    min_sample_size = 2 * (x_dim + y_dim) + 2
    if sample_size < min_sample_size:
      reason += "training sample is too small (%s < %s)." % (sample_size, min_sample_size)
      alt_tech = "RSM" # try to switch technique
    elif 0 == x_dim and not iterative_iv_session:
      reason += 'all outputs are constant.'
      alt_tech = "RSM" # try to switch technique
    else:
      moa_technique = options.get('GTApprox/MoATechnique').lower()

      if 'auto' != moa_technique:
        technique = options.get('GTApprox/Technique')
        try:
          options.set('GTApprox/Technique', _get_technique_official_name(moa_technique))
          reason += TechniqueSelector(options, None).checklist[moa_technique](sample, options, None) # Note cluster models does not use initial models.
        except (_ex.InvalidOptionsError, _ex.InapplicableTechniqueException):
          error_message, tb = sys.exc_info()[1:]
          reason += _shared._safestr(error_message)
          _shared.reraise(_ex.InapplicableTechniqueException, ('MoA cluster technique %s is not applicable because %s' %
                                                   (_get_technique_official_name(moa_technique), error_message)), tb)
        finally:
          options.set('GTApprox/Technique', technique)

      # validate_candidates cluster size
      try:
        calc_cluster_size(options, x_dim, sample_size, iterative_iv_session)
      except _ex.GTException:
        error_message = sys.exc_info()[1]
        reason += '\n%s' % error_message

  if check_only_sample:
    return reason.strip()

  # Note we must call _test_initial_model
  explicit_moa = _test_initial_model('MoA', initial_model, True) \
              or options.get('GTApprox/Technique').lower() == 'moa'

  if alt_tech:
    if explicit_moa:
      try:
        options.set('GTApprox/Technique', _get_technique_official_name(alt_tech))
        TechniqueSelector(options, None).checklist[options.get('GTApprox/Technique').lower()](sample, options, initial_model)
        return (reason + '\nTraining has been switched to %s technique.' % _get_technique_official_name(alt_tech)).strip()
      except (_ex.InvalidOptionsError, _ex.InapplicableTechniqueException):
        alt_reasons = _shared._safestr(sys.exc_info()[1])
        reason += "\nCannot switch to %s technique" % _get_technique_official_name(alt_tech)
        if alt_reasons:
          reason += " because " + alt_reasons
      except:
        pass
      raise _ex.InapplicableTechniqueException(reason) # MoA is inapplicable and we cannot switch it to RSM or something
  elif not explicit_moa:
    reason += '\nthis technique is specifically intended to model a discontinuous but well-clustered dependency'

  return reason.strip()

def _test_initial_model(technique, initial_model, supports_model_update):
  # Test technique for compatibility with the initial model and
  # returns boolean indicating this technique is the only one that is compatible.
  if not initial_model:
    return False
  elif not supports_model_update:
    raise _ex.InapplicableTechniqueException("this technique does not support updating the initial model.")
  compatible_techniques = initial_model._compatible_techniques
  technique = _get_technique_official_name(technique.lower())
  if technique not in compatible_techniques:
    raise _ex.InapplicableTechniqueException("the initial model is incompatible.")
  return len(compatible_techniques) == 1

def _get_linearity_reason(technique, options, has_output_tol=False):
  if _shared.parse_bool(options.get('GTApprox/LinearityRequired')):
    if technique.lower() == 'hda':
      return "\nlinearity is required"
    raise _ex.InapplicableTechniqueException("Linear mode not supported.")
  return ''

def _get_accuracy_evaluation_reason(technique, options, has_output_tol=False):
  if not _shared.parse_bool(options.get('GTApprox/AccuracyEvaluation')) and technique.lower() == 'sgp':
    return "\nrecommended use with Accuracy Evaluation"
  elif _shared.parse_bool(options.get('GTApprox/AccuracyEvaluation')) and not technique.lower() == 'sgp':
    raise _ex.InapplicableTechniqueException("Accuracy Evaluation is not available for %s." % technique)

  return ''


def _get_exactfit_reason(technique, options, has_output_tol=False):
  if _shared.parse_bool(options.get('GTApprox/ExactFitRequired')):
    raise _ex.InapplicableTechniqueException("The 'exact fit' mode is not available for %s." % technique)
  return ''

def _get_covariance_type_reason(technique, options, has_output_tol=False):
  heteroscedastic = _shared.parse_auto_bool(options.get('GTApprox/Heteroscedastic'), None)
  if heteroscedastic == True and options.get('GTApprox/GPType').lower() == 'mahalanobis':
    raise _ex.InvalidOptionsError("Mahalanobis covariance function doesn't support heteroscedasticity.")
  return ''


def _get_reduction_ratio_reason(options):
  reduction_ratio_default = _shared.parse_float(options.info('GTApprox/TAModelReductionRatio')['OptionDescription']['Default'])
  reduction_ratio_actual = _shared.parse_float(options.get('GTApprox/TAModelReductionRatio'))
  if not np.isnan([reduction_ratio_default, reduction_ratio_actual]).all() and reduction_ratio_actual != reduction_ratio_default:
    if _shared.parse_auto_bool(options.get('GTApprox/TAReducedBSPLModel'), None) == True:
      errorMessage = "Options %s=%s and %s=%s are mutually exclusive." % \
          (options.info('GTApprox/TAReducedBSPLModel')['OptionDescription']['Name'],
           options.get('GTApprox/TAReducedBSPLModel'),
           options.info('GTApprox/TAModelReductionRatio')['OptionDescription']['Name'],
           options.get('GTApprox/TAModelReductionRatio'))

      raise _ex.InvalidOptionsError(errorMessage)

    if _shared.parse_bool(options.get('GTApprox/ExactFitRequired')) and reduction_ratio_actual != 1.:
      errorMessage = "%s=%s option violates 'Exact Fit' requirement." % \
          (options.info('GTApprox/TAModelReductionRatio')['OptionDescription']['Name'],
           options.get('GTApprox/TAModelReductionRatio'))
      raise _ex.InvalidOptionsError(errorMessage)

  return ''


def _select_approximator_technique(proposed_technique, subspace_size, factor_dim, options):
  if proposed_technique.lower() != 'auto':
    return proposed_technique

  if _shared.parse_bool(options.get('GTApprox/ExactFitRequired')):

    if 1 == subspace_size:
      return 'LR0'
    elif 1 == factor_dim:
      return 'BSPL'
    elif subspace_size < int(options.get('/GTApprox/MinSampleSizeForHDA')):
      return 'GP'

  if subspace_size <= factor_dim:
    return 'LR0'
  elif _shared.parse_bool(options.get('GTApprox/LinearityRequired')):
    return 'LR'
  elif factor_dim == 1:
    return 'BSPL'
  elif subspace_size <= 2 * (factor_dim + 1):
    return 'LR'
  elif subspace_size < int(options.get('/GTApprox/MinSampleSizeForHDA')):
    return 'GP'

  return 'HDA'


def _get_outputNoiseVariance_reason(technique, options, has_output_tol):
  return ''  if not has_output_tol else ('\n%s technique does not use variance of the output noise' % technique)


def _get_rsm_options_incompatibility_reason(size_x, size_y, options):
  reason = ''
  if size_x != 0 and size_y > 1:
    rsm_feature_selection = options.get('GTApprox/RSMFeatureSelection').lower()
    if rsm_feature_selection == 'stepwisefit':
      reason = "'StepwiseFit' feature selection algorithm can be used with 1-D response data only." + \
               "Please, consider using GTApprox/DependentOutputs=False or specify another feature selection algorithm."

  return reason


def _get_discrete_variables(options, x_dim, enableTA):
  categorical_variables = _shared.parse_json(options.get('GTApprox/CategoricalVariables'))
  tensor_factors = _shared.parse_json(options.get('GTApprox/TensorFactors')) if enableTA else []

  if enableTA: # deperecated option
    categorical_variables += _shared.parse_json(options.get('GTApprox/TADiscreteVariables'))

  for factor in tensor_factors:
    if isinstance(factor[-1], string_types) and factor[-1].lower() == 'dv':
      categorical_variables += factor[:-1]

  categorical_variables = np.unique(categorical_variables).tolist()
  if categorical_variables and categorical_variables[-1] >= x_dim:
    raise _ex.InvalidOptionsError("Option %s=%s contains invalid input index %d >= %d" % \
                                  (options.info('GTApprox/CategoricalVariables')['OptionDescription']['Name'],
                                   options.get('GTApprox/CategoricalVariables'), categorical_variables[-1], x_dim))

  for factor in tensor_factors:
    if isinstance(factor[-1], string_types):
      factor = factor[:-1]
    if any((_ not in categorical_variables for _ in factor)) and any((_ in categorical_variables for _ in factor)):
      raise _ex.InvalidOptionsError('Invalid tensor structure is given: %s=%s\nThe subspace %s contains both categorical and continuous variables' \
                                  % (options.info('GTApprox/TensorFactors')['OptionDescription']['Name'],
                                     options.get('GTApprox/TensorFactors'), factor,))


  return categorical_variables


def _validate_candidates_sample_size(sample_size, min_sample_size, sample_name='Effective training'):
  if sample_size < min_sample_size:
    error_message = "%s sample is too small (%s < %s)!" % (sample_name, sample_size, min_sample_size)
    raise _ex.InapplicableTechniqueException(error_message)

def supports_encoding(technique):
  return technique.lower() not in ['tbl', 'tgp', 'ta', 'ita', 'pla']

def encoded_dims_number(encoding, n):
  # We can't estimate it for auto encoding, i.e. in case of using initial model encoding
  return {'dummy': max(1, n - 1), 'binary': max(1, np.ceil(np.log2(n))), 'target': 1, 'ordinal': 1, 'none': 0}.get(encoding.lower(), 0)

def _build_inputs_encoding_model(x, y, options, weights=None, tol=None, initial_model=None):

  if not isinstance(getattr(options, '_Options__impl', None), _ctypes.c_void_p):
    options_manager = _options._OptionManager('GTApprox/')
    options_impl = _options.Options(options_manager.pointer, None)
    if options is not None:
      _shared.check_concept_dict(options, 'options')
      options_impl.set(options)
      options = options_impl

  errdesc = _ctypes.c_void_p()
  # Note the method will actualize 'GTApprox/CategoricalVariables' and '//Encoding/InputsEncoding' options after encoding,
  # i.e. update categorical variables list and disable encodings for encoded categorical variables.
  encoding_handle = _api.encode_inputs(x.shape[0], x.shape[1], y.shape[1]
                                     , x.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(x.ctypes.strides, _api.c_size_ptr)
                                     , y.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(y.ctypes.strides, _api.c_size_ptr)
                                     , _api.c_double_ptr() if tol is None else tol.ctypes.data_as(_api.c_double_ptr)
                                     , _api.c_size_ptr() if tol is None else _ctypes.cast(tol.ctypes.strides, _api.c_size_ptr)
                                     , _api.c_double_ptr() if weights is None else weights.ctypes.data_as(_api.c_double_ptr)
                                     , _api.c_size_ptr() if weights is None else _ctypes.cast(weights.ctypes.strides, _api.c_size_ptr)
                                     , options._Options__impl, (initial_model._Model__instance if initial_model else _ctypes.c_void_p()), _ctypes.byref(errdesc))
  encoding_model = Model(handle=encoding_handle) if encoding_handle else None
  _shared._raise_on_error(not errdesc, 'Failed to build inputs encoding model. ', errdesc)
  return encoding_model

class TechniqueSelector(object):
  def __init__(self, options, logger=None):
    self.__options = options
    self.__logger = _shared.Logger(logger, options.get('GTApprox/LogLevel').lower())
    self.__datasets = []
    self.__categorical_variables = []
    self.__categorical_variables_encoding = []
    self.__checklist = {
      'gbrt': check_GBRT,
      'gp': check_GP,
      'hda': check_HDA,
      'hdagp': check_HDAGP,
      'ita': check_iTA,
      'moa': check_MoA,
      'pla': check_PLA,
      'rsm': check_RSM,
      'sgp': check_SGP,
      'splt': check_SPLT,
      'ta': check_TA,
      'tbl': check_TBL,
      'tgp': check_TGP
    }

  @property
  def checklist(self):
    return self.__checklist

  @property
  def options(self):
    return self.__options

  @property
  def has_encoding(self):
    for encoding in self.__categorical_variables_encoding:
      if isinstance(encoding[-1], string_types):
        idx, name = encoding[:-1], encoding[-1].lower()
      else:
        idx, name = encoding[:], 'none'
      if name != 'none':
        return True

    return False

  def _log(self, level, msg, output_column=None, comment=None):
    if output_column is not None:
      prefix = _shared.make_prefix(('output #%d' % output_column) if not comment else ('output #%d, %s' % (output_column, comment)))
    else:
      prefix = _shared.make_prefix(comment)

    for s in msg.splitlines():
      self.__logger(level, prefix + s)

  @staticmethod
  def _find_name_ignore_case(options, name):
    name_lc = name.lower()
    for option_name in options:
      if option_name.lower() == name_lc:
        return option_name
    return name

  def _read_iv_options(self, sample_size, validate, unfiltered_sample_size, override_options):
    requested_iv_subsets = int(self.options.get('GTApprox/IVSubsetCount'))
    requested_iv_subset_size = int(self.options.get('GTApprox/IVSubsetSize'))
    requested_iv_rounds = int(self.options.get('GTApprox/IVTrainingCount'))

    iv_subsets, iv_rounds = _read_iv_options_impl(requested_iv_subsets, requested_iv_subset_size,
                                                  requested_iv_rounds, sample_size, validate)
    override_iv_subsets, override_iv_rounds = False, False

    if (iv_subsets or iv_rounds) and unfiltered_sample_size and sample_size < unfiltered_sample_size:
      # reduce cardinality of the internal validation if we've filtered out some points
      reduction_ratio = float(sample_size) / float(unfiltered_sample_size)

      if iv_subsets and not requested_iv_subset_size:
        # Reduce the number of subsets to keep implied subset size.
        # Ignore reduction if user explicitly specified subset size.
        reduced_iv_subsets = max(2, int(iv_subsets * reduction_ratio + 0.5))
        if reduced_iv_subsets < iv_subsets:
          iv_subsets = reduced_iv_subsets
          if override_options is not None:
            override_options[self._find_name_ignore_case(override_options, 'GTApprox/IVSubsetCount')] = iv_subsets

      if iv_rounds:
        # Reduce the number of IV rounds.
        reduced_iv_rounds = max(1, int(iv_rounds * reduction_ratio + 0.5))
        if iv_subsets:
          reduced_iv_rounds = min(iv_subsets, reduced_iv_rounds)
        if reduced_iv_rounds < iv_rounds:
          iv_rounds = reduced_iv_rounds
          if override_options is not None:
            override_options[self._find_name_ignore_case(override_options, 'GTApprox/IVTrainingCount')] = iv_rounds

    return iv_subsets, iv_rounds

  def batch_recommended(self, componentwise, limited_time, all_outputs_categorical):
    technique = self.options.get('GTApprox/Technique').lower()
    if technique == "gbrt" or all_outputs_categorical:
      return False
    elif technique == "moa" or _shared.parse_bool(self.options.get("//Service/SmartSelection")):
      return True

    n_cores = int(self.options.get("GTApprox/MaxParallel"))
    if not n_cores:
      n_cores = _ctypes.c_size_t()
      if _api.hardware_configuration(_ctypes.byref(n_cores), _api.c_size_ptr(), _api.c_size_ptr(), _api.c_size_ptr()):
        n_cores = int(n_cores.value)
      else:
        return False # something wrong with parallelization

    if n_cores > 4:
      # It's always worth outer parallelization
      return True

    workload = np.zeros((n_cores if n_cores > 0 else 4,), dtype=int)

    iv_requested = _shared.parse_bool(self.options.get("GTApprox/InternalValidation"))
    for current_candidate in self.__datasets:
      original_shape = current_candidate['sample'].original_shape
      for output_index in (range(original_shape[2]) if componentwise else [-1,]):
        current_sample_size = current_candidate['sample'].effective_cardinality(output_index)
        workload[np.argmin(workload)] += current_sample_size
        if iv_requested and current_sample_size > 2:
          iv_subsets, iv_rounds = self._read_iv_options(current_sample_size, False, original_shape[0], None)
          current_sample_size -= current_sample_size // iv_subsets
          for _ in range(iv_rounds):
            workload[np.argmin(workload)] += current_sample_size

    if np.count_nonzero(workload) < 2:
      return False

    return limited_time or 0.9 * workload.max() < workload.min()

  def _make_single_dataset(self, sample, switch_tech_reason, requested_technique_name, enabledTA, technique_list):
    self.__categorical_variables = []
    self.__datasets = [{'sample': sample}]
    if switch_tech_reason:
      exact_fit_required = _shared.parse_bool(self.options.get('GTApprox/ExactFitRequired'))
      iv_requested = _shared.parse_bool(self.options.get('GTApprox/InternalValidation'))
      ae_requested = _shared.parse_bool(self.options.get('GTApprox/AccuracyEvaluation'))

      if ae_requested:
        raise _ex.InvalidOptionsError('Accuracy Evaluation is not supported since %s.' % switch_tech_reason)

      if exact_fit_required and iv_requested:
        raise _ex.InvalidOptionsError('Internal Validation can not be performed since %s and the \'exact fit\' requirement is ON.' % switch_tech_reason)

      available_techniques = {
        (False, False): ['rsm', 'gbrt', 'tbl'],
        (False, True): ['rsm', 'gbrt'],
        (True, False): ['tbl'],
      } [exact_fit_required, iv_requested]

      available_technique_names = ', '.join([_get_technique_official_name(_) for _ in available_techniques])

      if technique_list and not [_ for _ in available_techniques if _ in technique_list]:
        if len(technique_list) > 1:
          reason = 'The enabled techniques ' + ','.join([_get_technique_official_name(_) for _ in technique_list]) + ' are not compatible'
        else:
          reason = 'The enabled technique ' + _get_technique_official_name(technique_list[0]) + ' is not compatible'
        raise _ex.InvalidOptionsError('%s with the specified options since %s. Consider enabling %s technique(s).' % (reason, switch_tech_reason, available_technique_names))

      if requested_technique_name == 'auto':
        requested_technique_name = available_techniques[0] if not technique_list else [_ for _ in available_techniques if _ in technique_list][0]
      elif requested_technique_name not in available_techniques:
        raise _ex.InvalidOptionsError('The requested technique %s is not compatible with the specified options since %s. Consider using %s technique(s).' % (_get_technique_official_name(requested_technique_name), switch_tech_reason, available_technique_names))

      self.__datasets[-1]['technique'] = requested_technique_name
      self.__datasets[-1]['reason'] = '%s technique is selected since %s.' % (_get_technique_official_name(requested_technique_name), switch_tech_reason)
      enabledTA = False

      self._log(loggers.LogLevel.INFO, '- %s.' % switch_tech_reason)

    if enabledTA:
      ta_technique_name = self.options.get('GTApprox/MoATechnique').lower() if requested_technique_name == 'moa' else requested_technique_name
      enabledTA = ta_technique_name in ['ta', 'ita', 'tgp', 'auto']

    return requested_technique_name, enabledTA

  def _validate_vector_options(self, size_x, size_y, options):
    c_options = options._Options__impl if isinstance(options, _options.Options) else _ctypes.c_void_p()
    do_check_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p,
                                      _ctypes.c_size_t, _ctypes.c_size_t,
                                      _ctypes.POINTER(_ctypes.c_void_p))
    do_check = do_check_type(('GTApproxUtilitiesValidateVectorOptions', _shared._library))
    error_ptr = _ctypes.c_void_p()
    if not do_check(c_options, size_x, size_y, _ctypes.byref(error_ptr)):
      _shared.ModelStatus.checkErrorCode(0, "Invalid option given.", error_ptr)

  def slice_outputs(self, effective_outputs):
    # two-pass scheme to preserve original data in case of exception
    sliced_samples = [dataset['sample'].slice(effective_outputs) for dataset in self.__datasets]
    for sample, dataset in zip(sliced_samples, self.__datasets):
      options_list = dataset['options']
      dataset['options'] = [options_list[i] for i in effective_outputs] + [options_list[-1],]
      dataset['sample'] = sample

  def select_encoding(self, x, y, technique, allowed_techniques, initial_model):
    user_encodings = _shared.parse_json(self.options.get('//Encoding/InputsEncoding'))
    encodings_idx = [_[:-1] if isinstance(_[-1], string_types) else _ for _ in user_encodings]
    encodings_type = [_[-1] if isinstance(_[-1], string_types) else 'none' for _ in user_encodings]

    def find_categorical_inputs(info):
      # Find categorical variables without encoding,
      # assuming they are the same for all submodels
      if isinstance(info, dict):
        for key, value in iteritems(info):
          if key == 'Categorical inputs':
            return value
          result = find_categorical_inputs(value)
          if result is not None:
            return result
      return None

    if '//Encoding/InputsEncoding' in self.options.values:
      if not supports_encoding(technique):
        if encodings_type and any(_ not in ['none', 'auto'] for _ in encodings_type):
          raise _ex.InvalidOptionsError('Specified encodings %s are incompatible with %s technique.' % (str(user_encodings), _get_technique_official_name(technique)))
      if allowed_techniques and all(not supports_encoding(_) for _ in allowed_techniques):
        if encodings_type and any(_ not in ['none', 'auto'] for _ in encodings_type):
          allowed_techniques = str([_get_technique_official_name(_) for _ in allowed_techniques])
          raise _ex.InvalidOptionsError('Specified encodings %s are incompatible with all of the allowed techniques %s.' % (str(user_encodings), allowed_techniques))
      if initial_model:
        errdesc = _ctypes.c_void_p()
        result = _ctypes.c_short()
        _shared._raise_on_error(_api.is_compatible_inputs_encoding(initial_model._Model__instance, self.options._Options__impl, _ctypes.byref(result), _ctypes.byref(errdesc)),
                                'Failed to check compatibility with initial model encodings!', errdesc)
        if not result.value:
          raise _ex.InvalidOptionsError('Specified encodings %s are incompatible with inputs encoding of the initial model.' % str(user_encodings))
      if all(_ != 'auto' for _ in encodings_type):
        return user_encodings

    if initial_model:
      # The initial model encoding will be used
      none_encodings = find_categorical_inputs(initial_model.info) or []
      auto_encodings = [_ for _ in self.__categorical_variables if _ not in none_encodings]
      if auto_encodings:
        # Allows to rearrange indices inside wrt initial model (or its submodel) encoding
        self.options.set('//Encoding/FixedEncodingIndices', False)
        return [auto_encodings + ['auto']]
      else:
        # Initial model was trained without any encoding
        return []

    if not supports_encoding(technique):
      # These techniques do not support encoding - make sample split
      return [[index, 'none'] for index in self.__categorical_variables]
    elif allowed_techniques and all(not supports_encoding(_) for _ in allowed_techniques):
      return [[index, 'none'] for index in self.__categorical_variables]

    if not encodings_idx:
      encodings_idx = [[_] for _ in self.__categorical_variables]
    if not encodings_type:
      encodings_type = ['auto' for _ in encodings_idx]
    encodings_n = [len(_get_unique_elements(x[:, _], return_indices=False)) for _ in encodings_idx]
    enumerators = _shared.parse_json(self.options.get('//Encoding/InputsEnumerators'))

    candidate_encodings = []
    for i, idx in enumerate(encodings_idx):
      if encodings_type[i] != 'auto':
        candidate_encodings.append([encodings_type[i]])
      elif encodings_n[i] <= 2:
        # Just replace it with binary variable
        candidate_encodings.append(['dummy'])
      elif np.max(idx) < len(enumerators) and np.all([len(enumerators[_]) for _ in idx]):
        # We know ordering of unique values
        candidate_encodings.append(['ordinal'])
      else:
        candidate_encodings.append(['dummy', 'binary', 'target'])

    dim_x, dim_y = x.shape[1], y.shape[1]
    base = _shared.parse_float(self.options.get('//Encoding/MaxDimensionCoefficient'))
    expected_new_dims = np.floor(dim_x * np.log(base) / np.log(dim_x))
    # Estimating here minimum number of points as n_min = 2 * (dim_x + dim_y) + 2.
    max_encoded_dim = max(x.shape[0] / 2.0 - dim_y - 1.0, x.shape[1])
    # If the sample is too small we require the size of encoded inputs to be the same as the original one (e.g. all target encodings)
    max_new_dims = max_encoded_dim - (x.shape[1] - len(self.__categorical_variables))

    best_result = {
      'encodings': [],
      'new_dims': [],
      'penalty': np.inf,
      'cache': [],
    }

    def update_best(encodings, result):
      if '-'.join(encodings) in result['cache']:
        return result
      else:
        result['cache'].append('-'.join(encodings))

      new_dims = [encoded_dims_number(encoding, encodings_n[i]) for i, encoding in enumerate(encodings)]

      if sum(new_dims) <= max_new_dims:
        penalty = np.abs(expected_new_dims - sum(new_dims))
        if penalty < result['penalty']:
          result['penalty'] = penalty
          result['encodings'] = [encodings[:]]
          result['new_dims'] = [new_dims]
        elif penalty == result['penalty']:
          result['encodings'].append(encodings[:])
          result['new_dims'].append(new_dims)

      return result

    n_candidates = [len(_) for _ in candidate_encodings]
    if np.prod(n_candidates) > 1e6:
      for _ in np.arange(1e6 / (len(candidate_encodings) * np.mean(n_candidates))):
        if len(best_result['encodings']):
          candidate_encoding = best_result['encodings'][int(_ % len(best_result['encodings']))]
        else:
          candidate_encoding = [_[0] for _ in candidate_encodings]
        best_result = update_best(candidate_encoding, best_result)
        for i, encoding in enumerate(candidate_encoding):
          new_encodings = candidate_encodings[i][:]
          new_encodings.remove(encoding)
          for new_encoding in new_encodings:
            candidate_encoding[i] = new_encoding
            best_result = update_best(candidate_encoding, best_result)
    else:
      for candidate_encoding in _shared.product(*candidate_encodings):
        best_result = update_best(candidate_encoding, best_result)

    if len(best_result['encodings']) == 0:
      # The training sample seems to be too small
      return [[index, 'none'] for index in self.__categorical_variables]
    elif len(best_result['encodings']) > 1:
      updated_penalties = np.empty(len(best_result['encodings']))
      for i, best_encoding in enumerate(best_result['encodings']):
        # Penalize the usage of binary and target encoders
        updated_penalties[i] = sum(best_result['new_dims'][i]) + best_encoding.count('binary') + 2 * best_encoding.count('target')
      best_idx = updated_penalties == updated_penalties.min()
      best_result['encodings'] = np.array(best_result['encodings'])[best_idx]
      best_result['new_dims'] = np.array(best_result['new_dims'])[best_idx]
      if len(best_result['encodings']) > 1:
        updated_penalties = np.empty(len(best_result['encodings']))
        for i, best_encoding in enumerate(best_result['encodings']):
          # Variables with more unique values should be encoded by target
          updated_penalties[i] = sum([{'binary': 1, 'target': -1}.get(_, 0) * encodings_n[k] for k, _ in enumerate(best_encoding)])
        best_idx = updated_penalties == updated_penalties.min()
        best_result['encodings'] = np.array(best_result['encodings'])[best_idx]
        best_result['new_dims'] = np.array(best_result['new_dims'])[best_idx]

    return [idx + [encoding] for idx, encoding in zip(encodings_idx, best_result['encodings'][0])]

  def preprocess_sample(self, x, y, outputNoiseVariance, weights, componentwise, build_manager, comment=None, technique_list=None, initial_model=None, sample_id=None):
    self._validate_vector_options(x.shape[1], y.shape[1], build_manager.options)
    requested_technique_name = self.options.get('GTApprox/Technique').lower()
    x_tol = _shared.parse_json(self.options.get('GTApprox/InputsTolerance'))
    if len(x_tol) != 0:
      try:
        x_tol = np.array(x_tol, dtype=float).reshape((-1,))
        if x_tol.shape[0] != x.shape[1] or not np.all(x_tol >= 0):
          raise ValueError()
      except:
        tb = sys.exc_info()[2]
        _shared.reraise(_ex.InvalidOptionsError, ('Input tolerance array should be %d-dimensional vector of non-negative values. Actual value is %s' % (x.shape[1], self.options.get('GTApprox/InputsTolerance'))), tb)

    iv_requested = _shared.parse_bool(self.options.get('GTApprox/InternalValidation')) \
               and not _shared.parse_bool(self.options.get('//IterativeIV/SessionIsRunning'))
    if iv_requested:
      # validate IV options
      self._read_iv_options(x.shape[0], True, None, None)

    self._log(loggers.LogLevel.INFO, "Analyzing input data...", comment=comment)

    original_options = self.options.values

    try:
      enabledTA = self.refresh_candidates_list(technique_list)

      xy_nan_mode = {'x': self.options.get('GTApprox/InputNanMode').lower(),
                     'y': self.options.get('GTApprox/OutputNanMode').lower(),}
      if requested_technique_name == 'gbrt' and xy_nan_mode['x'] == 'ignore':
        xy_nan_mode['x'] = 'preserve'  # gbrt is the only technique that can handle NaN inputs

      if requested_technique_name == 'tbl':
        categorical_variables = list(range(x.shape[1]))
        self.__datasets = [{'sample': _SampleData(x, y, outputNoiseVariance, weights, categorical_variables, x_tol, xy_nan_mode), 'technique': requested_technique_name}]
        self.__categorical_variables = []
      else:
        # find discrete classes
        self.__categorical_variables = _get_discrete_variables(self.options, x.shape[1], enabledTA)
        n_catvars = len(self.__categorical_variables)

        if n_catvars not in (0, x.shape[1]):
          self._log(loggers.LogLevel.INFO, "Searching encoding for categorical variables...", comment=comment)
          inner_technique_name = self.options.get('GTApprox/MoATechnique').lower() if requested_technique_name == 'moa' else requested_technique_name
          self.__categorical_variables_encoding = self.select_encoding(x, y, inner_technique_name, technique_list, initial_model)

          mentioned_variables = set()
          for encoding in self.__categorical_variables_encoding:
            if isinstance(encoding[-1], string_types):
              idx, name = encoding[:-1], encoding[-1].lower()
            else:
              idx, name = encoding[:], 'none'
            if name != 'none':
              self.__categorical_variables = [_ for _ in self.__categorical_variables if _ not in idx]
            mentioned_variables.update(idx)

          if self.__categorical_variables_encoding and len(mentioned_variables) < x.shape[1]:
            # We need to specify continuous variables as variables without encoding
            self.__categorical_variables_encoding.append([_ for _ in range(x.shape[1]) if _ not in mentioned_variables])

          self._log(loggers.LogLevel.INFO, "Selected encoding " + str(self.__categorical_variables_encoding), comment=comment)
          n_catvars = len(self.__categorical_variables)
          if self.has_encoding:
            enabledTA = False

        if n_catvars in (0, x.shape[1]):
          # neither or all variables are categorical - it's a single dataset case
          requested_technique_name, enabledTA = self._make_single_dataset(_SampleData(x, y, outputNoiseVariance, weights, [], x_tol, xy_nan_mode),
                                                                          ('all input variables are categorical' if n_catvars == x.shape[1] else ''),
                                                                          requested_technique_name, enabledTA, technique_list)
        else:
          self.__datasets = []
          duplicate_indices = _get_unique_elements(x[:, self.__categorical_variables], return_indices=True)
          if not duplicate_indices:
            requested_technique_name, enabledTA = self._make_single_dataset(_SampleData(x, y, outputNoiseVariance, weights, [], x_tol, xy_nan_mode),
                                                                            'every unique combination of the categorical variables is related to a single training dataset point',
                                                                            requested_technique_name, enabledTA, technique_list)
          else:
            for indices in duplicate_indices:
              if indices is not None:
                categorical_signature = (self.__categorical_variables, x[indices[0], self.__categorical_variables])
                categorical_sample = _SampleData(x[indices], y[indices],
                                                 (outputNoiseVariance[indices] if outputNoiseVariance is not None else None),
                                                 (weights[indices] if weights is not None else None),
                                                 self.__categorical_variables, x_tol, xy_nan_mode)
                self.__datasets.append({'sample': categorical_sample,
                                        'categorical_signature': categorical_signature})

      self.options.set('GTApprox/CategoricalVariables')

      local_options = self.options.values
      iv_feasible_count = len(self.__datasets)

      # initialize default options (empty dicts)
      for current_candidate in self.__datasets:
        current_candidate['options'] = [{} for _ in range(1 + current_candidate['sample'].original_shape[2])]

      # check whether NaN values are presented in input
      if self.options.get('GTApprox/InputNanMode').lower() != 'ignore' \
         and any(current_candidate['sample'].nan_info['invalid_x'].any() for current_candidate in self.__datasets):
        raise _ex.NanInfError('Invalid (NaN or Inf) values are found in input part of the training sample.')

      # check whether NaN values are presented in output
      output_nan_mode = self.options.get('GTApprox/OutputNanMode').lower()
      if output_nan_mode != 'ignore' \
         and any(current_candidate['sample'].nan_info['has_invalid_y'][-1] for current_candidate in self.__datasets):
        raise _ex.NanInfError('Invalid (%sInf) values are found in output part of the training sample.' % ('' if 'predict' == output_nan_mode else 'NaN or '))

      if iv_requested:
        # validate IV feasibility
        for current_candidate in self.__datasets:
          iv_impossible = 1
          for output_index in (range(current_candidate['sample'].original_shape[2]) if componentwise else [-1,]):
            current_sample_size = current_candidate['sample'].effective_cardinality(output_index)
            if current_sample_size < 2:
              current_candidate['options'][output_index]['GTApprox/InternalValidation'] = False
            else:
              iv_impossible = 0
              iv_subsets, iv_rounds = self._read_iv_options(current_sample_size, False, x.shape[0], current_candidate['options'][output_index])

          iv_feasible_count -= iv_impossible

      if enabledTA and isinstance(self.options, _options.Options):
        # find cartesian structure if needed w.r.t. componentwise mode and possible output NaN presence
        predefined_structure = _shared.parse_json(self.options.get('GTApprox/TensorFactors'))
        dry_run = _parse_dry_run(self.options) == "quick"

        for current_candidate_index, current_candidate in enumerate(self.__datasets):
          current_sample = current_candidate['sample']
          checked_outputs = []
          candidate_outputs = list(range(current_sample.original_shape[2])) \
                           if (componentwise and current_sample.nan_info['mixed']) \
                           else [-1,]
          for output_index in candidate_outputs:
            current_options = current_candidate['options'][output_index]

            if not predefined_structure:
              # check previously found structures first
              for checked_output_index in checked_outputs:
                if current_sample.same_nan_structure(checked_output_index, output_index):
                  current_options['//Service/CartesianStructureEstimation'] = current_candidate['options'][checked_output_index]['//Service/CartesianStructureEstimation']
                  cartesian_structure = current_candidate['options'][checked_output_index].get('//Service/CartesianStructure')
                  if cartesian_structure is not None:
                    current_options['//Service/CartesianStructure'] = cartesian_structure
                  break

              if '//Service/CartesianStructureEstimation' in current_options:
                continue

            if self.options.get('//Service/CartesianStructureEstimation').lower() != 'unknown':
              continue

            current_unique_sample = current_sample.unique_inputs(filtered=True, output_index=output_index)

            if checked_outputs and not predefined_structure and not dry_run:
              # try to use previously found structure
              c_sample = _shared.py_matrix_2c(current_unique_sample, name="Filtered unique inputs")
              for checked_output_index in checked_outputs:
                cartesian_structure = _shared.parse_json(current_candidate['options'][checked_output_index].get('//Service/CartesianStructure', '[]'))
                if cartesian_structure:
                  # strip factorwise technique specs
                  for factor in cartesian_structure:
                    if isinstance(factor[-1], string_types):
                      del factor[-1]
                  if Utilities.checkTensorStructure(c_sample.array, cartesian_structure)[0]:
                    self.options.set('GTApprox/TensorFactors', cartesian_structure)
                    break

            data_id = sample_id or ('output%04d' % max(0, output_index)) + ('' if len(self.__datasets) == 1 else '_catclass%04d' % current_candidate_index)
            build_manager.submit_data(data_id, current_unique_sample, None)

            job_id = 'find_tensor_structure.' + (sample_id or data_id)
            build_manager.submit_job(data_id, job_id, action='find_tensor_structure', options=self.options.values, comment='')

            code, tensor_structure_estimation, tensor_structure = build_manager.get_tensor_structure()[data_id][job_id]
            self.options.set('//Service/CartesianStructureEstimation', tensor_structure_estimation)
            self.options.set('//Service/CartesianStructure', tensor_structure)

            current_options['//Service/CartesianStructureEstimation'] = self.options.get('//Service/CartesianStructureEstimation')
            if code in [2, 4,]:
              # full factorial of multidimensional factorial
              current_options['//Service/CartesianStructure'] = self.options.get('//Service/CartesianStructure')
            elif predefined_structure:
              self._log(loggers.LogLevel.WARN, 'The input sample%s does not have proposed tensor structure: %s' % ((' for output #%d' % output_index) if output_index >= 0 else '', str(predefined_structure)), comment=comment)
              nan_count = _shared.long_integer(current_sample.nan_info['count'][output_index])
              if nan_count:
                self._log(loggers.LogLevel.WARN, 'It can be caused by %d restricted (NaN) value%s found in input and/or output%s sample.' % (nan_count, ('s' if nan_count > 1 else ''), (' #%d' % output_index) if output_index >= 0 else ''), comment=comment)

            if not predefined_structure:
              checked_outputs.append(output_index)
            self.options.reset()
            self.options.set(local_options)

      def _read_option(options, index, key, defval):
        return options[index].get(key, options[-1].get(key, defval))

      # print dataset info
      ambiguous_exact_fit = False
      ae_degenerated_case = True
      for current_candidate in self.__datasets:
        effective_shape = current_candidate['sample'].effective_shape
        original_shape = current_candidate['sample'].original_shape
        componentwise = componentwise and (effective_shape[2] > 1)

        categorical_signature = current_candidate.get('categorical_signature')
        if categorical_signature:
          self._log(loggers.LogLevel.INFO, 'Subsample for categorical input variables x%s=%s' % categorical_signature, comment=comment)

        self._log(loggers.LogLevel.INFO, '- effective input size: %d' % effective_shape[1], comment=comment)
        if 0 == effective_shape[1]:
          self._log(loggers.LogLevel.WARN, 'All inputs are either categorical or constant.', comment=comment)
        elif effective_shape[1] < original_shape[1]:
          self._log(loggers.LogLevel.INFO, '- input variables (0-based indices): %s' % current_candidate['sample'].variable_columns['x'], comment=comment)

        self._log(loggers.LogLevel.INFO, '- effective output size: %d' % effective_shape[2], comment=comment)
        if 0 == effective_shape[2]:
          self._log(loggers.LogLevel.WARN, 'All outputs are constant.', comment=comment)
        elif effective_shape[2] < original_shape[2]:
          self._log(loggers.LogLevel.INFO, '- output variables (0-based indices): %s' % current_candidate['sample'].variable_columns['y'], comment=comment)
        self._log(loggers.LogLevel.INFO, '- total number of samples: %d' % original_shape[0], comment=comment)

        for output_index in (current_candidate['sample'].variable_columns['y'] if componentwise else [-1,]):
          try:
            self.options.set(current_candidate['options'][-1])
            if output_index != -1:
              self.options.set(current_candidate['options'][output_index])
              self.options.set(self.options._values(output_index))
            self.options.set('//ComponentwiseTraining/ActiveOutput', output_index)

            if componentwise:
              self._log(loggers.LogLevel.INFO, '- output #%d:' % output_index, comment=comment)
            bullet, for_output_name = (' *', ' for output #%d' % output_index) if componentwise else ('-', '')

            duplicate_points = np.array(current_candidate['sample'].duplicate_points)[output_index]
            ambiguous_points = np.array(current_candidate['sample'].ambiguous_points)[output_index]
            nan_output_points = np.array(current_candidate['sample'].nan_info['count'])[output_index]
            effective_cardinality = current_candidate['sample'].effective_cardinality(output_index)

            ae_degenerated_case &= (effective_cardinality <= 1 and _shared.parse_bool(self.options.get('GTApprox/AccuracyEvaluation')))

            self._log(loggers.LogLevel.INFO, '%s duplicate samples: %d' % (bullet, duplicate_points), comment=comment)
            if ambiguous_points > 0:
              self._log(loggers.LogLevel.WARN, 'Dataset%s has ambiguous samples: %d' % (for_output_name, ambiguous_points), comment=comment)
              ambiguous_exact_fit |= _shared.parse_bool(self.options.get('GTApprox/ExactFitRequired'))
            if nan_output_points > 0:
              self._log(loggers.LogLevel.INFO, '%s invalid samples: %d' % (bullet, nan_output_points), comment=comment)
            self._log(loggers.LogLevel.INFO, '%s effective number of samples: %d' % (bullet, effective_cardinality), comment=comment)

            if iv_requested and not _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
              self._log(loggers.LogLevel.WARN, 'Internal Validation is turned off%s because the effective number of samples is too small.' % for_output_name, comment=comment)

            cart_struct = _shared.parse_json(self.options.get('//Service/CartesianStructure'))
            if cart_struct:
              cart_struct = [_[:-1] if isinstance(_[-1], string_types) else _ for _ in cart_struct]
              self._log(loggers.LogLevel.INFO, '%s input points have cartesian structure: %s' % (bullet, str(cart_struct)), comment=comment)
            elif str(self.options.get('//Service/CartesianStructureEstimation')).lower() in ['3', 'incompletefullfactorial']:
              self._log(loggers.LogLevel.INFO, '%s input points have incomplete full factorial structure.' % bullet, comment=comment)
            elif enabledTA:
              self._log(loggers.LogLevel.INFO, '%s no cartesian structure has found.' % bullet, comment=comment)
          finally:
            self.options.reset()
            self.options.set(local_options)

      if ambiguous_exact_fit:
        raise _ex.InvalidOptionsError("Training data set contains ambiguous points. Cannot build model in exact fit mode.")

      if ae_degenerated_case:
        raise _ex.InvalidOptionsError("The 'Accuracy Evaluation' requirement is infeasible because the effective number of samples is too small.")

      if iv_requested and not iv_feasible_count:
        raise _ex.InvalidOptionsError('Internal validation requested while it cannot be performed due to dataset properties.')

      return _get_technique_official_name(requested_technique_name)
    finally:
      self.options.reset()
      self.options.set(original_options)

  def refresh_candidates_list(self, technique_list):
    requested_technique_name = self.options.get('GTApprox/Technique').lower()
    TA_TECHNIQUES_DISABLED = "tensored techniques has been turned off (see %s option)" % \
                             self.options.info('GTApprox/EnableTensorFeature')['OptionDescription']['Name']

    self.candidates = []

    ta_technique_name = self.options.get('GTApprox/MoATechnique').lower() if requested_technique_name == 'moa' else requested_technique_name
    enabledTA = ta_technique_name in ['ita', 'ta', 'tgp'] \
                or (ta_technique_name == 'auto' and _shared.parse_bool(self.options.get('GTApprox/EnableTensorFeature')))

    if technique_list:
      technique_list = [_.lower() for _ in technique_list]

    def _append_technique_info(candidates, technique, status='not checked', reason='', flags=None, base_priority=0):
      if not technique_list or technique.lower() in technique_list:
        candidates.append(CandidateTechniqueInfo(technique=technique, status=status, reason=reason, flags=flags, base_priority=base_priority))

    if not enabledTA:
      _append_technique_info(self.candidates, 'iTA', 'inapplicable', TA_TECHNIQUES_DISABLED)
      _append_technique_info(self.candidates, 'TA', 'inapplicable', TA_TECHNIQUES_DISABLED)
      _append_technique_info(self.candidates, 'TGP', 'inapplicable', TA_TECHNIQUES_DISABLED)
    else:
      # validate_candidates tensor structure
      _append_technique_info(self.candidates, 'iTA', base_priority=10)
      _append_technique_info(self.candidates, 'TA', base_priority=12)
      _append_technique_info(self.candidates, 'TGP', base_priority=11)

    _append_technique_info(self.candidates, 'SPLT', base_priority=6)
    _append_technique_info(self.candidates, 'HDA', base_priority=5)
    _append_technique_info(self.candidates, 'GP', base_priority=4)
    _append_technique_info(self.candidates, 'HDAGP', base_priority=3)
    _append_technique_info(self.candidates, 'SGP', base_priority=2)
    _append_technique_info(self.candidates, 'RSM', base_priority=1)
    _append_technique_info(self.candidates, 'TBL', base_priority=0)

    _append_technique_info(self.candidates, 'GBRT', base_priority=0)
    _append_technique_info(self.candidates, 'PLA', base_priority=0)
    _append_technique_info(self.candidates, 'MoA', base_priority=0)

    return enabledTA

  def refresh_candidates_status(self, sample, initial_model=None):
    originally_requested_technique_name = self.options.get('GTApprox/Technique').lower()

    # validate techniques
    def update_technique_status(requested_technique_name):
      for candidate in self.candidates:
        if 'not checked' == candidate.status and (requested_technique_name == 'auto' or requested_technique_name == candidate.name):
          try:
            if candidate.name not in ['gbrt', 'tbl', 'hdagp', 'gp', 'moa']:
              candidate.flags.set('no_initial_model')
            elif 'no_initial_model' in candidate.flags:
              candidate.flags.clear('no_initial_model')

            candidate.reason = self.checklist[candidate.name](sample, self.options, initial_model)
            candidate.status = 'recommended' if not candidate.reason else 'not recommended'
          except _ex.InvalidOptionsError:
            error_message = sys.exc_info()[1]
            candidate.status = 'wrong options'
            candidate.reason = _shared._safestr(error_message)
          except _ex.InapplicableTechniqueException:
            error_message = sys.exc_info()[1]
            candidate.status = 'inapplicable' if requested_technique_name == 'auto' else 'wrong options'
            candidate.reason = _shared._safestr(error_message)

    update_technique_status(originally_requested_technique_name)
    requested_technique_name = self.options.get('GTApprox/Technique').lower()
    if requested_technique_name != originally_requested_technique_name:
      update_technique_status(requested_technique_name)

    for candidate in self.candidates:
      if originally_requested_technique_name in ('auto', candidate.name):
        reason = (':\n  ' + '\n  '.join([s for s in candidate.reason.splitlines() if s.rstrip()])) if candidate.reason else ''
        if 'recommended' == candidate.status:
          self._log(loggers.LogLevel.DEBUG, '- %s technique can be used for approximation' % candidate.name.upper())
        elif 'not recommended' == candidate.status:
          self._log(loggers.LogLevel.DEBUG, '- %s technique is not recommended%s' % (candidate.name.upper(), reason))
        else:
          self._log(loggers.LogLevel.DEBUG, '- %s technique cannot be used%s' % (candidate.name.upper(), reason))

  def select(self, output_column=None, initial_model=None, comment=None, categorical_outputs_map=None):
    return self._select(output_column, initial_model, comment=comment, categorical_outputs_map=categorical_outputs_map)

  def subsets(self, output_column=None, initial_model=None, technique_list=None, categorical_outputs_map=None):
    original_logger = self.__logger
    try:
      def null_logger(level, message):
        pass
      self.__logger = null_logger
      return self._select(output_column, initial_model, mode='subsets', technique_list=technique_list, categorical_outputs_map=categorical_outputs_map)
    finally:
      self.__logger = original_logger

  def _select(self, output_column=None, initial_model=None, mode='select', comment=None, technique_list=None, categorical_outputs_map=None):
    requested_technique_name = self.options.get('GTApprox/Technique').lower()

    def log_preferred_technique(preferred_technique, categorical_signatures, comment=None):
      preferred_technique_name = _get_technique_official_name(preferred_technique)
      additional_spec = '' if categorical_signatures is None else 'x%s=%s' % categorical_signatures
      if 'auto' == requested_technique_name:
        self._log(loggers.LogLevel.INFO, "Chosen approximation technique: %s" % (preferred_technique_name), output_column, comment or additional_spec)
      elif preferred_technique_name.lower() != requested_technique_name:
        self._log(loggers.LogLevel.INFO, "Chosen approximation technique: %s" % (preferred_technique_name), output_column, comment or additional_spec)
        # report technique switch
        self._log(loggers.LogLevel.WARN, "%s approximation technique was chosen while %s approximation technique was requested." %
                         (preferred_technique_name, _get_technique_official_name(requested_technique_name)), output_column, comment or additional_spec)
      else:
        # report manual selection
        self._log(loggers.LogLevel.INFO, 'Manually selected approximation technique: %s' % (preferred_technique_name), output_column, comment or additional_spec)

    def read_optional_slice(matrix, slice):
      return matrix[slice] if isinstance(matrix, np.ndarray) else None

    def convert_to_train_data(sample, options, initial_model, output_nan_mode):
      # _replace_nan

      if sample.nan_info['count'][-1] > 0:
        valid_points = np.isfinite(sample.original_sample['y']).all(axis=1)
        valid_points[sample.nan_info['invalid_x']] = False

        if 'ignore' == output_nan_mode:
          restricted_points = None
        else:
          restricted_points = np.any(np.isnan(sample.original_sample['y']), axis=1)
          restricted_points[sample.nan_info['invalid_x']] = False
          if not restricted_points.any():
            restricted_points = None

        if not np.any(valid_points):
          # all points are NaN - well, it's a very special case...
          if restricted_points is None:
            raise _ex.InvalidProblemError('All training samples are invalid')
          elif initial_model is None:
            return {'x': np.zeros((1, sample.original_sample['x'].shape[1]), dtype=float)
                    , 'y': np.zeros((1, sample.original_sample['y'].shape[1]), dtype=float)
                    , 'weights': None
                    , 'tol': None
                    , 'initial_model': None
                    , 'options': {}
                    , 'restricted_x': np.zeros((1, sample.original_sample['x'].shape[1]), dtype=float)
                    , 'modified_dataset': True
                    , '_sample': sample
                    }
          else:
            raise _ex.InvalidProblemError('All training samples are invalid while initial model is given')
        elif not np.all(valid_points):
          return {'x': sample.original_sample['x'][valid_points]
                  , 'y': sample.original_sample['y'][valid_points]
                  , 'weights': read_optional_slice(sample.original_sample['w'], valid_points)
                  , 'tol': read_optional_slice(sample.original_sample['tol'], valid_points)
                  , 'initial_model': initial_model
                  , 'options': options
                  , 'restricted_x': None if restricted_points is None else _get_unique_elements(sample.original_sample['x'][restricted_points], return_indices=False)
                  , 'modified_dataset': True
                  , '_sample': sample
                  }

      return {'x': sample.original_sample['x']
              , 'y': sample.original_sample['y']
              , 'weights': sample.original_sample['w']
              , 'tol': sample.original_sample['tol']
              , 'initial_model': initial_model
              , 'options': options
              , 'restricted_x': None
              , 'modified_dataset': False
              , '_sample': sample
              }

    def read_options(dataset, output_column):
      options = dict(dataset['options'][-1].items())
      if self.__categorical_variables_encoding:
        options['//Encoding/InputsEncoding'] = self.__categorical_variables_encoding
        variables_map = _shared.parse_categorical_map(self.options.get('//GTApprox/CategoricalVariablesMap'))
        if variables_map:
          options['//Encoding/InputsEnumerators'] = [variables_map.get(_, (float, [], []))[2] for _ in range(dataset['sample'].original_shape[1])]
      if output_column is not None:
        for key, value in iteritems(dataset['options'][output_column]):
          options[key] = value
      return options

    self._log(loggers.LogLevel.INFO, "Selecting an appropriate approximation technique" + ("." if not initial_model else " from the list of techniques compatible with the initial model: " + str(initial_model._compatible_techniques)), output_column, comment)

    saved_options = self.options.values
    preferred_techniques = []

    if 1 == len(self.__datasets) and self.__datasets[0].get('technique', 'auto').lower() != 'auto':
      try:
        # these techniques have native categorical variables support
        current_dataset = self.__datasets[0]
        current_sample = current_dataset['sample'].slice(output_column)
        current_options = read_options(current_dataset, output_column)
        for key, value in iteritems(current_options):
          self.options.set(key, value)

        self.options.set('GTApprox/Technique', _get_technique_official_name(current_dataset.get('technique', 'auto')))
        self.refresh_candidates_list(technique_list)
        self.refresh_candidates_status(current_sample, initial_model)
        # technique re-assignment can be omitted. The main reason of confirm_technique call is validation of the technique selected
        current_dataset['technique'] = self.confirm_technique(requested_technique_name, comment or '', 'select' == mode, output_column)
        if current_dataset.get('reason') is not None:
          self._log(loggers.LogLevel.INFO, current_dataset['reason'], output_column, comment)
        else:
          log_preferred_technique(current_dataset['technique'], None, comment)
        train_data = convert_to_train_data(current_sample, current_options, initial_model, self.options.get('GTApprox/OutputNanMode').lower())
        train_data['technique'] = current_dataset['technique']

        if categorical_outputs_map:
          output_transform = _shared.parse_output_transformation(self.options.get("GTApprox/OutputTransformation"), output_size=current_sample.original_shape[2])

          options = {}
          if output_column is None:
            if 'select' == mode:
              train_data['technique'] = 'GBRT'
              log_preferred_technique(train_data['technique'], None, comment)
            options['GTApprox/OutputTransformation'] = output_transform
            for i in categorical_outputs_map:
              options['GTApprox/OutputTransformation'][i] = 'none'
            if all(_ == options['GTApprox/OutputTransformation'][0] for _ in options['GTApprox/OutputTransformation']):
              options['GTApprox/OutputTransformation'] = options['GTApprox/OutputTransformation'][0]
            categorical_values = [categorical_outputs_map.get(i, (float, [], []))[1] for i in np.arange(current_sample.original_shape[2])]
            options['//GBRT/CategoricalOutputsCardinality'] = [len(_) for _ in categorical_values]
            options['//GBRT/CategoricalOutputsValues'] = _shared._write_string_vector_list(categorical_values)
            options['GTApprox/CategoricalOutputs'] = sorted([i for i in categorical_outputs_map])

          elif output_column in categorical_outputs_map:
            if 'select' == mode:
              train_data['technique'] = 'GBRT'
              log_preferred_technique(train_data['technique'], None, comment)
            options['GTApprox/OutputTransformation'] = 'none'
            options['//GBRT/CategoricalOutputsCardinality'] = [len(categorical_outputs_map[output_column][1])]
            options['//GBRT/CategoricalOutputsValues'] = _shared._write_string_vector_list([categorical_outputs_map[output_column][1]])
            options['GTApprox/CategoricalOutputs'] = [0]
          else:
            options['GTApprox/CategoricalOutputs'] = []

          train_data['options'].update(options)

        self._review_train_data(train_data, True)
        return [train_data], []
      finally:
        self.options.reset()
        self.options.set(saved_options)

    # for each discrete class choose its own technique
    for current_dataset in self.__datasets:
      try:
        self.options.set('GTApprox/CategoricalVariables')

        current_options = read_options(current_dataset, output_column)
        current_sample = current_dataset['sample'].slice(output_column)

        categorical_signature = current_dataset.get('categorical_signature')
        current_candidate = convert_to_train_data(current_sample, current_options, None, self.options.get('GTApprox/OutputNanMode').lower())
        if categorical_signature is not None:
          current_candidate['comment'] = 'x%s=%s' % categorical_signature
          initial_model_note = "" if not current_candidate['initial_model'] else " from the list of techniques compatible with the initial model: " + str(current_candidate['initial_model']._compatible_techniques)
          self._log(loggers.LogLevel.DEBUG, "Selecting an appropriate approximation technique for categorical input variables x%s=%s%s" % (categorical_signature[0], categorical_signature[1], initial_model_note), output_column, comment)
        else:
          current_candidate['initial_model'] = initial_model

        for key, value in iteritems(current_options):
          self.options.set(key, value)

        if not categorical_outputs_map or output_column is not None and output_column not in categorical_outputs_map:
          # We will switch to GBRT in case of individual categorical output or mixed categorical
          # and continuous outputs. Need to call confirm_technique to ensure GBRT is applicable.
          self.refresh_candidates_list(technique_list)
          self.refresh_candidates_status(current_sample, current_candidate['initial_model'])
          preferred_technique = self.confirm_technique(requested_technique_name,
                                                       comment or (' x%s=%s' % categorical_signature) if categorical_signature else '',
                                                       'select' == mode, output_column)
        else:
          # In subsets mode we ignore the technique specified for categorical outputs, it will be set within smart selection
          preferred_technique = None

        if categorical_outputs_map:
          output_transform = _shared.parse_output_transformation(self.options.get("GTApprox/OutputTransformation"), output_size=current_sample.original_shape[2])

          options = {}
          if output_column is None:
            if 'select' == mode:
              preferred_technique = 'GBRT'
            options['GTApprox/OutputTransformation'] = output_transform
            for i in categorical_outputs_map:
              options['GTApprox/OutputTransformation'][i] = 'none'
            categorical_values = [categorical_outputs_map.get(i, (float, [], []))[1] for i in np.arange(current_sample.original_shape[2])]
            options['//GBRT/CategoricalOutputsCardinality'] = [len(_) for _ in categorical_values]
            options['//GBRT/CategoricalOutputsValues'] = _shared._write_string_vector_list(categorical_values)
            options['GTApprox/CategoricalOutputs'] = sorted([i for i in categorical_outputs_map])

          elif output_column in categorical_outputs_map:
            if 'select' == mode:
              preferred_technique = 'GBRT'
            options['GTApprox/OutputTransformation'] = 'none'
            options['//GBRT/CategoricalOutputsCardinality'] = [len(categorical_outputs_map[output_column][1])]
            options['//GBRT/CategoricalOutputsValues'] = _shared._write_string_vector_list([categorical_outputs_map[output_column][1]])
            options['GTApprox/CategoricalOutputs'] = [0]
          else:
            options['GTApprox/CategoricalOutputs'] = []

          current_candidate['options'].update(options)

        if 'select' == mode or preferred_technique is not None:
          current_candidate['technique'] = preferred_technique
          log_preferred_technique(current_candidate['technique'], categorical_signature, comment)
        self._review_train_data(current_candidate, False, output_column, comment)
        preferred_techniques.append(current_candidate)
      finally:
        self.options.reset()
        self.options.set(saved_options)

    return preferred_techniques, self.__categorical_variables

  def confirm_technique(self, originally_requested_technique_name, comment='', restrictive=True, output_column=None):
    requested_technique_name = self.options.get('GTApprox/Technique').lower()
    preferred_technique = CandidateTechniqueInfo(requested_technique_name, 'inapplicable', '', base_priority=-1)

    # report all techniques availability status (it's required because external techniques like MoA can switch manual technique selection)
    technique_not_found_reasons = ''
    technique_wrong_options = ''

    for candidate in self.candidates:
      if originally_requested_technique_name in ('auto', candidate.name):
        technique_name = _get_technique_official_name(candidate.name)

        if candidate.status == 'wrong options':
          if originally_requested_technique_name == 'auto':
            technique_wrong_options += "%s technique cannot be used %s: %s" % (technique_name, comment.strip(), candidate.reason)
          elif originally_requested_technique_name == candidate.name:
            technique_wrong_options += "Manually selected %s technique cannot be used %s: %s" % (technique_name, comment.strip(), candidate.reason)

        # intentionally going down to write 'not found' message too
        elif candidate.status == 'inapplicable':
          technique_not_found_reasons += "\n* %s cannot be used %s: %s" % (technique_name, comment.strip(), candidate.reason)
        elif candidate.status == 'not recommended':
          technique_not_found_reasons += "\n* %s is not recommended %s: %s" % (technique_name, comment.strip(), candidate.reason)

    if originally_requested_technique_name != requested_technique_name:
      # Note that ('Auto' == requested_technique_name) case also covered by the (originally_requested_technique_name != requested_technique_name) check
      # As well as switching manually selected technique.
      self._log(loggers.LogLevel.INFO, technique_not_found_reasons, output_column, comment)

    if technique_wrong_options:
      raise _ex.InvalidOptionsError(technique_wrong_options)

    applicable_techniques = []

    if 'auto' == requested_technique_name:
      # choose the preferred one
      feasible_techniques = []

      for candidate in self.candidates:
        if 'recommended' == candidate.status:
          applicable_techniques.append(_get_technique_official_name(candidate.name))
        elif 'not recommended' == candidate.status:
          if not restrictive:
            candidate.status = 'recommended'
            applicable_techniques.append(_get_technique_official_name(candidate.name))
          else:
            feasible_techniques.append(_get_technique_official_name(candidate.name))

        if candidate.priority() > preferred_technique.priority():
          preferred_technique = candidate

      self._log(loggers.LogLevel.DEBUG, "Number of approximation techniques matched conditions: %d%s" % (len(applicable_techniques), ((' %s' % str(applicable_techniques)) if applicable_techniques else ''),), output_column, comment)

      if 'recommended' != preferred_technique.status:
        if not feasible_techniques:
          feasible_techniques_list = ''
        elif 1 == len(feasible_techniques):
          feasible_techniques_list = '\nNote %s technique can be manually selected.' % feasible_techniques[0]
        else:
          feasible_techniques_list = '\nNote any of %s techniques can be manually selected.' % feasible_techniques
        preferred_technique.reason = ("Appropriate approximation technique is not found%s. The specific reasons are: %s%s"
                                      % (comment, technique_not_found_reasons, feasible_techniques_list))
    else:
      # ensure that requested technique can be used for training

      # set error status - it will be overriden on success
      preferred_technique.reason = "Unknown technique '%s' requested" % _get_technique_official_name(requested_technique_name)

      for candidate in self.candidates:
        if requested_technique_name == candidate.name:
          preferred_technique = candidate
          break

      if 'recommended' == preferred_technique.status:
        applicable_techniques.append(_get_technique_official_name(candidate.name))
      elif 'not recommended' == preferred_technique.status:
        # emit warning and update status
        self._log(loggers.LogLevel.INFO, "Manually selected '%s' technique is not recommended: %s" % (_get_technique_official_name(requested_technique_name), preferred_technique.reason), output_column, comment)
        preferred_technique.status = 'recommended'

    if 'recommended' != preferred_technique.status:
      raise _ex.InvalidOptionsError(preferred_technique.reason)

    # Note that we wont be able to set that technique for smart selection (restrictive == False)
    # when the list of enabled techniques was specified by hint. These options are mutually exclusive.
    return _get_technique_official_name(preferred_technique.name) if (restrictive or 1 >= len(applicable_techniques)) else None

  def _review_train_data(self, train_data, iv_requirement=True, output_column=None, comment=None):
    technique = str(train_data.get('technique', 'auto')).lower()
    if 'auto' == technique:
      # there is nothing to review
      return

    if technique == 'gbrt':
      x_holes = np.isnan(train_data['x'])
      if x_holes.any():
        x = train_data['x']
        errdesc = _ctypes.c_void_p()
        marker = _api.select_nan_marker(x.shape[0], x.shape[1], x.ctypes.data_as(_api.c_double_ptr), x.strides[0] // x.itemsize, x.strides[1] // x.itemsize, _ctypes.byref(errdesc))
        if not np.isfinite(marker):
          _shared.ModelStatus.checkErrorCode(0, 'The input dataset does not contain finite values.', errdesc)
        x = x.copy()
        x[x_holes] = marker
        train_data['x'] = x
        train_data['options']['//Service/MissingValueMarker'] = marker
      if train_data['_sample'].duplicate_points.size and train_data.get('weights') is None:
        # Suggested weights for duplicate points may interfere incremental training, in fact GBRT supports duplicate points
        train_data['options']['//Service/DuplicatePointsFilteringMode'] = self.options.values.get('//Service/DuplicatePointsFilteringMode', 'Ignore')

    def warn_unsupported(train_data, message):
      prefix = 'Note %s %s' % (_get_technique_official_name(technique), train_data.get('comment', 'technique'),)
      self._log(loggers.LogLevel.WARN, '%s %s' % (prefix, message,), output_column, comment)

    if _shared.parse_bool(self.options.get('GTApprox/InternalValidation')) and technique in ['tbl',]:
      if iv_requirement:
        raise _ex.InvalidOptionsError("The %s %s does not support Internal Validation." % \
          (_get_technique_official_name(technique), train_data.get('comment', 'technique'),))
      else:
        warn_unsupported(train_data, 'does not support Internal Validation')
        train_data['options'] = train_data.get('options', {})
        train_data['options']['GTApprox/InternalValidation'] = False

    if train_data.get('tol') is not None and technique not in ['gp', 'hda', 'hdagp', 'sgp', 'moa',]:
      warn_unsupported(train_data, 'ignores output noise variance')
      train_data['tol'] = None

    if train_data.get('weights') is not None and technique in ['tgp', 'tbl', 'ta', 'splt',]:
      warn_unsupported(train_data, 'ignores points weights')
      train_data['weights'] = None

    if train_data.get('initial_model') is not None and technique not in ['tbl', 'gbrt', 'gp', 'hdagp', 'moa']:
      warn_unsupported(train_data, 'does not support incremental training')
      train_data['initial_model'] = None

class CandidateTechniqueInfo(object):
  """
  Possible status:
    'not checked' == -2: The technique applicability has not been validated yet
    'wrong options' == -1: Invalid options related to the current technique were provided.
    'inapplicable' == 0:  The technique requested is not compatible with the current environment.
    'not recommended' == 1: The technique requested can be used in the current environment, but it's not recommended.
    'recommended' == 2: The technique requested fit to the current environment perfectly.

  Possible flag:
    'componentwise' - If componentwise mode is requested then it should be implemented in out-of-technique-train-driver mode
    'no_initial_model' - Train driver does not supports incremental training
    ''
  """
  def __init__(self, technique, status='not checked', reason='', flags=None, base_priority=0):
    class FlagsList(object):
      def __init__(self, flags):
        self.flags = []
        if flags:
          self.flags = [str(flag).lower() for flag in flags]

      def __contains__(self, item):
        return item.lower() in self.flags

      def __iter__(self):
        return iter(self.flags)

      def set(self, flag):
        flag = str(flag).lower()
        if flag not in self.flags:
          self.flags.append(flag)

      def clear(self, flag):
        flag = str(flag).lower()
        if flag in self.flags:
          self.flags.remove(flag)


    self.name = technique.lower()
    self.reason = reason

    if status not in ['not checked', 'wrong options', 'inapplicable', 'not recommended', 'recommended']:
      raise ValueError('Unknown technique status=%s!' % status)

    self.status = status
    self._priority = {'not checked'    : -2000 + base_priority
                      , 'wrong options'  : -1000 + base_priority
                      , 'inapplicable'   :  0    + base_priority
                      , 'not recommended':  1000 + base_priority
                      , 'recommended'    :  2000 + base_priority
                      }

    self.flags = FlagsList(flags)

  def priority(self):
    return self._priority[self.status]
