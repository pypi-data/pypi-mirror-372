#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import sys as _sys
import ctypes as _ctypes
from time import time
import numpy as np
import numpy.linalg as alg

from .. import stat as _stat
from ..utils import distributions as _distributions
from ..six.moves import xrange, range, zip
from . import utils as _utils
from .. import exceptions as _ex
from .. import shared as _shared
from .. import options as _options
from ..stat import outlier_detection as _outlier_detection

_DECISIONS_TYPE = np.float32

class CheckerParams(object):
  """CheckerParams - structure used to store options and objects needed to control checker execution
  """

  def __init__(self, backend, logger, watcher):
    object.__setattr__(self, 'backend', backend)
    object.__setattr__(self, 'logger', logger)
    object.__setattr__(self, 'watcher', watcher)

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

def _log(logger, level, message):
  """Send message to logger
  """
  if logger:
    logger(level, message)

def _rank_data(vector):
  """Rank data for Spearman correlation
  """
  vector = np.array(vector, dtype=float, copy=_shared._SHALLOW)
  vector_mask = np.isfinite(vector)
  n_valid = np.count_nonzero(vector_mask)
  n_orig = vector_mask.size

  if n_valid == n_orig:
    vector_mask = None
  elif not n_valid:
    ranks = np.empty(n_orig)
    ranks.fill(np.nan)
    return ranks
  else:
    vector = vector[vector_mask]

  vector_order = np.argsort(vector)
  ordered_ranks = vector[vector_order]
  i_start = 0
  for i_curr, r_curr, r_next in zip(xrange(n_valid - 1), ordered_ranks[:-1], ordered_ranks[1:]):
    if r_curr != r_next:
      ordered_ranks[i_start:(i_curr + 1)] = 0.5 * (i_curr + i_start)
      i_start = i_curr + 1
  ordered_ranks[i_start:n_valid] = 0.5 * (n_valid - 1 + i_start)

  ranks = np.empty(n_valid)
  ranks[vector_order] = ordered_ranks

  if vector_mask is None:
    return ranks

  ranks_and_nans = np.empty(n_orig)
  ranks_and_nans.fill(np.nan)
  ranks_and_nans[vector_mask] = ranks
  return ranks_and_nans

def fill_options_set(options):
  """Purpose: Configures low level checker options according to specified high level options.
    (also it's used to tweak old GT SDA options that are now private)

  Inputs:
    options - da.p7core.Options object connected to corresponding GT SDA backend
  """
  #GTSDA options formatting
  technique = options.get('GTSDA/Checker/Technique').lower()

  if technique == 'mutualinformation':
    options.set({'/GTSDA/Ranker/VarianceEstimateRequired': False})

def _get_pvalues_correction(number_experiments, p_values, options):
  """Calculate correction for p_values computed with permutation test
  """
  normal_distribution = _distributions._normal()
  significance_level = _shared.parse_float(options.get('GTSDA/Checker/PValues/SignificanceLevel'))
  p_quantile = normal_distribution.quantile(1 - 0.5 * significance_level)
  p_values_correction_method = options.get('/GTSDA/Checker/PValues/CorrectionMethod').lower()

  if p_values_correction_method == 'nocorrection':
    pass
  elif p_values_correction_method == 'wald':
    confidence_width = p_quantile * np.sqrt(p_values * (1. - p_values) / number_experiments)
    p_values = p_values + confidence_width
  elif p_values_correction_method == 'wilson':
    confidence_width = p_quantile * np.sqrt(p_values * (1. - p_values) / number_experiments + 0.25 * p_quantile**2 / number_experiments**2)
    p_values = 1 / (1 + p_quantile**2 / number_experiments) * (p_values + 0.5 * p_quantile**2 / number_experiments + confidence_width)
  elif p_values_correction_method == 'wilsoncc':
    tmp_upper = np.sqrt(p_quantile**2 - 1 / number_experiments + 4 * number_experiments * p_values * (1 - p_values) - (4 * p_values - 2))
    confidence_width_u = np.round(p_quantile * tmp_upper + 1)
    p_values = 0.5 * (2 * number_experiments * p_values + p_quantile**2 + confidence_width_u) / (number_experiments + p_quantile**2)

  return np.clip(p_values, 0., 1.)

def check(x, y, z, options, logger, watcher):
  """Main procedure for checking
  """
  if not isinstance(options, _options.Options):
    from .analyzer import Analyzer as _Analyzer
    fake_analyzer = _Analyzer()
    if options is not None and options:
      for k in options:
        fake_analyzer.options.set(k, options[k])
    options = fake_analyzer.options

  x = np.array(x, copy=_shared._SHALLOW, dtype=float)
  if x.ndim == 1:
    x = x.reshape(-1, 1)

  if y is not None:
    y = np.array(y, copy=_shared._SHALLOW, dtype=float)
    if y.ndim == 1:
      y = y.reshape(-1, 1)

  if z is not None:
    z = np.array(z, copy=_shared._SHALLOW, dtype=float)
    if z.ndim == 1:
      z = z.reshape(-1, 1)

  only_inputs_mode = y is None or _shared.parse_bool(options.get('/GTSDA/Checker/OnlyInputsMode'))

  logger.info("Length of the series: %d" % x.shape[0])
  logger.info("Number of the variables: %d (x) vs %d (y)" % (x.shape[1], x.shape[1] if only_inputs_mode else y.shape[1]))
  if z is not None:
    logger.info("Number of the explanatory variables: %d (z)" % z.shape[1])

  if z is not None:
    z_finite = np.isfinite(z).all(axis=1)
    if not z_finite.all():
      z = z[z_finite]
      x = x[z_finite]
      if y is not None:
        y = y[z_finite]
      logger.info("%d points are excluded due to non-finite explanatory variables values" % (z_finite.shape[0] - z.shape[0]))
    del z_finite

  calculate_pvalue = _shared.parse_bool(options.get('GTSDA/Checker/PValues/Enable'))
  pvalues_method = options.get('GTSDA/Checker/PValues/Method').lower()
  if pvalues_method != 'auto':
    use_permutations = (pvalues_method == 'permutations')
  else:
    permutations_threshold = 100 if options.get('GTSDA/Checker/Technique').lower() in ['kendallcorrelation'] else 1000
    use_permutations = len(x) < permutations_threshold

  if only_inputs_mode:
    y = x
  scores_scheme = [(_ScoresCalculator(x[points_slice, x_slice], None if y_slice is None else y[points_slice, y_slice],
                                      None if z is None else z[points_slice], options, logger, watcher, not (calculate_pvalue and use_permutations)), \
                    (x_slice if y_slice is None else y_slice), x_slice, (None if (not calculate_pvalue or use_permutations) else points_slice)) for y_slice, x_slice, points_slice in \
                   _enumerate_finite_blocks(x, y)]

  n_y, n_x = y.shape[1], x.shape[1]
  scores = np.empty((n_y, n_x))
  p_values = np.empty((n_y, n_x))
  decisions = np.empty((n_y, n_x), dtype=_DECISIONS_TYPE)

  p_values.fill(np.nan)
  decisions.fill(np.nan)

  try:
    for scores_calc, y_slice, x_slice, points_slice in scores_scheme:
      scores[y_slice, x_slice] = scores_calc.scores(watcher, False)

      if calculate_pvalue:
        if not scores_calc.variable_yx and not any(_[-1] is None for _ in scores_calc.precalculated_yx):
          block_p_values = p_values[y_slice, x_slice]
          block_decisions = decisions[y_slice, x_slice]

          # for the degenerated cases we use a priory known p-value
          for output_index, input_index, apriory_corr, apriory_pvalue in scores_calc.precalculated_yx:
            if np.isnan(apriory_corr):
              block_p_values[output_index, input_index] = np.nan
              block_decisions[output_index, input_index] = 0
            else:
              block_p_values[output_index, input_index] = 0.
              block_decisions[output_index, input_index] = (apriory_corr > 0)
        elif use_permutations:
          p_values[y_slice, x_slice], decisions[y_slice, x_slice] = _estimate_p_values_permutations(scores_calc, scores[y_slice, x_slice], options, logger, watcher)
        else:
          # p-values estimation method is "Asymptotic" or "Auto"
          p_values[y_slice, x_slice], decisions[y_slice, x_slice] = _estimate_p_values_approximate(scores_calc, x[points_slice, x_slice], \
                                                                                                   (None if scores_calc.inputs_only else y[points_slice, y_slice]), \
                                                                                                   scores[y_slice, x_slice], options, logger, watcher)
    if only_inputs_mode:
      for i in xrange(1, n_x):
        scores[i - 1, i:] = scores[i:, i - 1]
        p_values[i - 1, i:] = p_values[i:, i - 1]
        decisions[i - 1, i:] = decisions[i:, i - 1]
  finally:
    for _ in scores_scheme:
      _[0].release()

  return scores, decisions, p_values, scores_calc.outlier_info.get("Info", {})

def _read_slice(x, d0, d1):
  if x is None:
    return None
  y = x[(slice(x.shape[0]) if d0 is None else d0), (slice(x.shape[1]) if d1 is None else d1)]
  return y.reshape(-1, 1) if y.ndim < 2 else y

def _enumerate_general_subfinite_blocks(x_start, y_start, nnan, mask):
  # select leftmost h-slice
  h_slice = nnan.shape[1]
  for j in xrange(1, nnan.shape[1]):
    if nnan[0, j] != nnan[0, 0] or not (mask[0, j] == mask[0, 0]).all():
      h_slice = j
      break

  # select topmost v_slice
  v_slice = nnan.shape[0]
  for i in xrange(1, nnan.shape[0]):
    if nnan[i, 0] != nnan[0, 0] or not (mask[i, 0] == mask[0, 0]).all():
      v_slice = i
      break

  # Note it's crucial to return explicit slices!
  result = [] if nnan[0, 0] == mask[0, 0].size else [(slice(y_start, y_start + v_slice), slice(x_start, x_start + h_slice),
                                                     (slice(mask.shape[-1]) if not nnan[0, 0] else mask[0, 0].copy())),]

  if v_slice < nnan.shape[0]:
    result.extend(_enumerate_general_subfinite_blocks(x_start, y_start + v_slice, nnan[v_slice:,:h_slice], mask[v_slice:,:h_slice]))
  if h_slice < nnan.shape[1]:
    result.extend(_enumerate_general_subfinite_blocks(x_start + h_slice, y_start, nnan[:,h_slice:], mask[:,h_slice:]))

  return result

def _enumerate_symmetrical_subfinite_blocks(x_start, nnan, mask):
  # select diagonal slice
  slice_pos = nnan.shape[0]
  for i in xrange(1, nnan.shape[0]):
    if not all((nnan[i, j] == nnan[0, 0] and (mask[i, j] == mask[0, 0]).all()) for j in xrange(i + 1)):
      slice_pos = i
      break

  # Note it's crucial to return explicit slices!
  result = [] if nnan[0, 0] == mask[0, 0].size else [(None, slice(x_start, x_start + slice_pos),
                                                      (slice(mask.shape[-1]) if not nnan[0, 0] else mask[0, 0].copy())),]

  if slice_pos < nnan.shape[0]:
    result.extend(_enumerate_symmetrical_subfinite_blocks(x_start + slice_pos, nnan[slice_pos:,slice_pos:], mask[slice_pos:,slice_pos:]))
    # use lower triangle only
    result.extend(_enumerate_general_subfinite_blocks(x_start, x_start + slice_pos, nnan[slice_pos:,:slice_pos], mask[slice_pos:,:slice_pos]))

  return result

def _enumerate_finite_blocks(x, y):
  x_finite = np.isfinite(x.T)
  y_finite = x_finite if y is None or y is x else np.isfinite(y.T)
  n_y, n_x, n_pts = y_finite.shape[0], x_finite.shape[0], x_finite.shape[1]

  result = []

  if x_finite.all() and (x_finite is y_finite or y_finite.all()):
    return [(slice(n_y), slice(n_x), slice(n_pts)),]

  nnan = np.empty((n_y, n_x), dtype=np.int64)
  mask = np.empty((n_y, n_x, n_pts), dtype=bool)

  for i, y_fin_i in enumerate(y_finite):
    for j, x_fin_j in enumerate(x_finite):
      np.logical_and(y_fin_i, x_fin_j, out=mask[i, j])
      nnan[i, j] = n_pts - np.count_nonzero(mask[i, j])

  return _enumerate_symmetrical_subfinite_blocks(0, nnan, mask) if y is None or y is x \
    else _enumerate_general_subfinite_blocks(0, 0, nnan, mask)

def _watch(watcher, obj):
  if watcher:
    retval = watcher(obj)
    if not retval:
      raise _ex.UserTerminated()

def _get_dependence_type(technique):
  dep_type = ''
  if technique.lower() in ['pearsoncorrelation', 'pearsonpartialcorrelation', 'robustpearsoncorrelation']:
    dep_type = 'linear'
  elif technique.lower() in ['spearmancorrelation', 'kendallcorrelation']:
    dep_type = 'rank'
  elif technique.lower() in ['distancecorrelation', 'distancepartialcorrelation', 'mutualinformation']:
    dep_type = 'general'

  return dep_type

def _estimate_p_values_permutations(scores_calc, scores, options, logger, watcher):
  """Estimate p_values using permutation test
  """
  try:
    only_inputs_mode = scores_calc.inputs_only
    number_outputs, number_inputs = scores_calc.scores_shape[:2]

    technique = scores_calc.technique
    critical_p_value = _shared.parse_float(options.get('GTSDA/Checker/PValues/SignificanceLevel'))
    number_permutations = int(options.get('/GTSDA/Checker/Permutations/NumberPermutations'))

    logger.info('Computing permutations...')

    start_time = time()

    p_values = scores_calc.estimate_pvalues(scores, number_permutations, watcher)

    finite_pvalues = np.isfinite(p_values)
    p_values[finite_pvalues] = _get_pvalues_correction(number_permutations, p_values[finite_pvalues], options)
    decisions = (p_values <= critical_p_value).astype(_DECISIONS_TYPE)

    # for degenerated cases no correction is needed
    for output_index, input_index, apriory_corr, apriory_pvalue in scores_calc.precalculated_yx:
      # None marks pre-calculated values rather than degenerated cases
      if apriory_pvalue is not None:
        p_values[output_index, input_index] = apriory_pvalue
        decisions[output_index, input_index] = float(apriory_corr > 0) if not np.isnan(apriory_pvalue) else np.nan

    logger.info('Finished computing permutations. Elapsed time ' + str(time() - start_time) + '.\n')
    exc_info = None
  except:
    exc_info = _sys.exc_info()

  if exc_info is not None:
    try:
      logger.error("Failed to estimate p-values using permutations: %s" % exc_info[1])

      p_values = np.empty((number_outputs, number_inputs))
      p_values.fill(np.nan)

      decisions = np.zeros((number_outputs, number_inputs), dtype=_DECISIONS_TYPE)
    except:
      _shared.reraise(*exc_info)

  return p_values, decisions

def _estimate_p_values_approximate(scores_calc, x, y, scores, options, logger, watcher):
  technique = scores_calc.technique

  variable_yx = [(output_index, input_index) for output_index, input_index in scores_calc.variable_yx]
  variable_yx.extend([(output_index, input_index) for output_index, input_index, apriory_corr, apriory_pvalue in scores_calc.precalculated_yx if apriory_pvalue is None])

  number_outputs, number_inputs, number_points = scores_calc.scores_shape
  critical_p_value = _shared.parse_float(options.get('GTSDA/Checker/PValues/SignificanceLevel'))
  p_values = np.zeros((number_outputs, number_inputs), dtype=float)
  test_statistic = np.zeros((number_outputs, number_inputs), dtype=float)

  # Collect test statistics
  if _get_dependence_type(technique) == 'linear' or technique == 'spearmancorrelation':
    for output_index, input_index in variable_yx:
      if np.isnan(scores[output_index, input_index]):
        test_statistic[output_index, input_index] = np.nan
      elif np.abs(scores[output_index, input_index]) < 0.99999999:
        if technique == 'robustpearsoncorrelation':
          number_support_points = scores_calc.outlier_info.get("SupportVectorsCount", {}).get((output_index, input_index), 0)
          test_statistic[output_index, input_index] = \
            np.sqrt(number_support_points - 3) * np.fabs(np.arctanh(scores[output_index, input_index]))
        else:
          test_statistic[output_index, input_index] = np.sqrt(number_points - 3) * np.fabs(np.arctanh(scores[output_index, input_index]))
      else:
        test_statistic[output_index, input_index] = np.inf

  elif technique == 'kendallcorrelation':
    variance = np.sqrt(2 * (2 * number_points + 5.) / (9 * number_points * (number_points - 1)))
    for output_index, input_index in variable_yx:
      test_statistic[output_index, input_index] = np.nan if np.isnan(scores[output_index, input_index]) \
                                                  else np.fabs(scores[output_index, input_index]) / variance

  elif technique == 'distancecorrelation':
    is_calculate_unbiased = _shared.parse_bool(options.get('GTSDA/Checker/DistanceCorrelation/Unbiased'))
    if not is_calculate_unbiased:
      for output_index, input_index in variable_yx:
        test_statistic[output_index, input_index] = scores_calc.distance_test_stat[output_index, input_index]
    else:
      normalizing_constant = np.sqrt(0.5 * number_points * (number_points - 3.) - 1)
      for output_index, input_index in variable_yx:
        test_statistic[output_index, input_index] = np.nan if np.isnan(scores[output_index, input_index]) \
                                                    else normalizing_constant * scores[output_index, input_index]

  elif technique == 'distancepartialcorrelation':
    # this technique always calculates unbiased distances
    normalizing_constant = np.sqrt(0.5 * number_points * (number_points - 3.) - 1.)
    for output_index, input_index in variable_yx:
      test_statistic[output_index, input_index] = np.nan if np.isnan(scores[output_index, input_index]) \
                                                  else normalizing_constant * scores[output_index, input_index]

  elif technique == 'mutualinformation':
    for output_index, input_index in variable_yx:
      test_statistic[output_index, input_index] = scores_calc.mi_test_stat[output_index, input_index]

  # Calculate p-values based on the test statistics
  if technique == 'mutualinformation':
    for output_index, input_index in variable_yx:
      if np.isnan(test_statistic[output_index, input_index]):
        p_values[output_index, input_index] = np.nan
      else:
        p_values[output_index, input_index] = 1. - _distributions._chi2(scores_calc.mi_k_freedom[output_index, input_index]).cdf(test_statistic[output_index, input_index])
  else:
    for output_index, input_index in variable_yx:
      # workaround for bug in the boost library
      curr_stat = test_statistic[output_index, input_index]
      p_values[output_index, input_index] = 2. * _distributions._normal().cdf(-curr_stat) if np.isfinite(curr_stat) \
                                            else np.nan if np.isnan(curr_stat) else 0.

  valid_pvalues = ~np.isnan(p_values)
  p_values[valid_pvalues] = np.clip(p_values[valid_pvalues], 0., 1.)

  decisions = np.empty(p_values.shape, dtype=_DECISIONS_TYPE)
  decisions[~valid_pvalues] = np.nan
  decisions[valid_pvalues] = (p_values[valid_pvalues] < critical_p_value)

  # for the degenerated cases we use a priory known p-value
  for output_index, input_index, apriory_corr, apriory_pvalue in scores_calc.precalculated_yx:
    # None marks pre-calculated values rather than degenerated cases
    if apriory_pvalue is not None:
      if np.isnan(apriory_corr):
        p_values[output_index, input_index] = np.nan
        decisions[output_index, input_index] = np.nan
      else:
        p_values[output_index, input_index] = 0.
        decisions[output_index, input_index] = (apriory_corr > 0)

  return p_values, decisions

class _ScoresCalculator(object):
  """Calculate score for given sample.
  """
  def __init__(self, x, y, z, options, logger, watcher, single_calc):
    self.inputs_only = y is None or y is x or (y.shape == x.shape and (y == x).all())
    self.options = options
    self.technique = self.options.get('GTSDA/Checker/Technique').lower()
    self.scores_shape = ((x.shape[1] if self.inputs_only else y.shape[1]), x.shape[1], x.shape[0])
    self.outlier_info = {}
    self.single_calc = single_calc

    variable_columns_x, constant_columns_x = _utils.check_for_constant_columns(x)
    variable_columns_y, constant_columns_y = (variable_columns_x, constant_columns_x) if self.inputs_only \
                                             else _utils.check_for_constant_columns(y)

    self.variable_yx = []

    # List of a priory known correlations (output index, input index, corr. value, p-value or None)
    self.precalculated_yx = []
    for input_index in variable_columns_x:
      for output_index in constant_columns_y:
        self.precalculated_yx.append((output_index, input_index, 0., 0.))
    for input_index in constant_columns_x:
      for output_index in variable_columns_y:
        self.precalculated_yx.append((output_index, input_index, 0., 0.))

    if self.inputs_only:
      y = x # explicitly assign x to y
      for input_index in xrange(x.shape[1]):
        self.precalculated_yx.append((input_index, input_index, (1. if input_index in variable_columns_x else np.nan), (0. if input_index in variable_columns_x else np.nan)))

      for input_index in constant_columns_x:
        for output_index in constant_columns_x[:input_index]:
          self.precalculated_yx.append((output_index, input_index, np.nan, np.nan))
          self.precalculated_yx.append((input_index, output_index, np.nan, np.nan))

      if len(variable_columns_x) == 1:
        # there are no non-degenerated correlations
        return
    else:
      for input_index in constant_columns_x:
        for output_index in constant_columns_y:
          self.precalculated_yx.append((output_index, input_index, np.nan, np.nan))

      if not variable_columns_x or not variable_columns_y:
        # there are no non-degenerated correlations
        return

    if not variable_columns_x or not variable_columns_y:
      # all correlations are pre-calculated
      return
    if self.technique == 'pearsonpartialcorrelation':
      if z is None or not z.size:
        raise _ex.GTException("Partial Pearson correlation requires matrix of the explanatory variables (z).")

      algo = self.options.get('/GTSDA/Checker/PearsonPartial/Algo').lower()
      if algo == 'linearregression':
        self._prepare_partial_pearson_linear_regression(x, y, z, variable_columns_x, constant_columns_x, variable_columns_y, constant_columns_y)
      elif algo == 'matrix':
        self._prepare_partial_pearson_matrix(x, y, z, variable_columns_x, constant_columns_x, variable_columns_y, constant_columns_y)
      else:
        raise _ex.GTException("Invalid or unsupported algorithm of partial Pearson correlation is specified: ")
    elif self.technique == 'robustpearsoncorrelation':
      self._prepare_robust_pearson(x, y, variable_columns_x, constant_columns_x, variable_columns_y, constant_columns_y, logger, watcher)
    else:
      # the order MUST be output-major
      for i in variable_columns_y:
        self.variable_yx.extend([(i, j) for j in variable_columns_x])

      if self.technique == 'spearmancorrelation':
        self._prepare_spearman(x, y, variable_columns_x, variable_columns_y)
      elif self.technique == 'mutualinformation':
        self._prepare_mi(x, y, variable_columns_x, variable_columns_y, options)
      else:
        variable_x = x[:, variable_columns_x] if constant_columns_x else x
        variable_y = variable_x if self.inputs_only else y[:, variable_columns_y] if constant_columns_y else y

        if self.technique == 'pearsoncorrelation':
          self._prepare_pearson(variable_x, variable_y)
        elif self.technique == 'distancecorrelation':
          self._prepare_distance_corr(variable_x, variable_y, variable_columns_x, variable_columns_y, options)
        else:
          self.norm_x, self.norm_y = variable_x, variable_y

          if self.technique == 'kendallcorrelation':
            # denominator is irrelevant to the x order
            self.kendall_denom = _stat.statistics._kendall_denom(self.norm_x, (self.norm_y if not self.inputs_only else None))
          elif self.technique == 'distancepartialcorrelation':
            if z is None or not z.size:
              raise _ex.GTException("Partial distance correlation requires matrix of the explanatory variables (z).")

            variable_columns_z, const_columns_z = _utils.check_for_constant_columns(z)
            if not variable_columns_z:
              raise _ex.GTException("Cannot calculate partial distance correlation because all explanatory variables (z) are constant.")

            self.norm_z = z[:, variable_columns_z] if const_columns_z else z
            self._prepare_distance_corr(variable_x, variable_y, variable_columns_x, variable_columns_y, options, z=self.norm_z)

  def release(self):
    distance_corr = getattr(self, "distance_corr", None)
    if distance_corr is not None:
      self.distance_corr.release()

  def estimate_pvalues(self, base_scores, n_permutations, watcher):
    p_values = np.zeros(self.scores_shape[:2], dtype=float)

    if self.variable_yx:
      flat_scores = np.array([base_scores[output_index, input_index] for output_index, input_index in self.variable_yx], dtype=float)
      if self.technique in ('distancecorrelation', 'distancepartialcorrelation') and hasattr(self, "distance_corr"):
        # first we should reverse transform base_scores to the internal representation
        var_pvalues = self.distance_corr.estimate_pvalues(flat_scores.reshape(self.distance_corr.scores_shape), n_permutations, watcher)
        for (output_index, input_index), p_value in zip(self.variable_yx, var_pvalues.flat):
          p_values[output_index, input_index] = p_value
      else:
        np.fabs(flat_scores, out=flat_scores)
        flat_count = np.zeros(len(self.variable_yx), dtype=int)
        for permutations_pass in range(n_permutations):
          _watch(watcher, None)

          x_order = np.random.permutation(self.scores_shape[-1])
          variable_scores = np.fabs(self._scores(watcher, x_order))

          # convert list of (output index, input index) pairs to the flattened scores array indices
          np.add((variable_scores > flat_scores), flat_count, out=flat_count)

        for (output_index, input_index), count in zip(self.variable_yx, flat_count):
          p_values[output_index, input_index] = float(count) / n_permutations

    for i, j, val, pval in self.precalculated_yx:
      p_values[i, j] = pval

    return p_values

  def scores(self, watcher, shuffle=False):
    scores = np.empty(self.scores_shape[:2])

    if self.variable_yx:
      x_order = np.random.permutation(self.scores_shape[-1]) if shuffle else None

      variable_scores = self._scores(watcher, x_order)

      # convert list of (output index, input index) pairs to the flattened scores array indices
      for (output_index, input_index), cov_value in zip(self.variable_yx, variable_scores):
        scores[output_index, input_index] = cov_value

    if self.precalculated_yx:
      for i, j, val, pval in self.precalculated_yx:
        scores[i, j] = _shared._scalar(val)

    if _shared.parse_bool(self.options.get('/GTSDA/Checker/CorrelationAbsolute')):
      np.fabs(scores, out=scores)

    return scores

  def _scores(self, watcher, x_order):
    if self.technique in ('pearsoncorrelation', 'spearmancorrelation'):
      variable_scores = self.pearson_corr.calc(x_order)
    elif self.technique in ('distancecorrelation', 'distancepartialcorrelation'):
      variable_scores = self.distance_corr.calc(x_order)
    elif self.technique == 'mutualinformation':
      variable_scores = self.mi_calc.calc(x_order)
    elif self.technique == 'pearsonpartialcorrelation':
      # a very special, may be non-square case
      variable_scores = np.empty((len(self.variable_yx),))
      prev_corr = np.nan
      for output_index, input_index, corr_calc in self.partial_pearson:
        # self.partial_pearson elements are harmonized with the self.variable_yx but it would change
        i = self.variable_yx.index((output_index, input_index))
        variable_scores[i] = prev_corr if corr_calc is None else _shared._scalar(corr_calc.calc(x_order))
        prev_corr = variable_scores[i]
    elif self.technique == 'robustpearsoncorrelation':
      variable_scores = np.empty((len(self.variable_yx),))
      prev_corr = np.nan
      for output_index, input_index, pearson_corr in self.outlier_info.get("Data", []):
        # self.outlier_info["Data"] elements are harmonized with the self.variable_yx but it would change
        i = self.variable_yx.index((output_index, input_index))
        if pearson_corr is None:
          variable_scores[i] = prev_corr
        else:
          variable_scores[i] = _shared._scalar(pearson_corr.calc(x_order))
        prev_corr = variable_scores[i]
    elif self.technique == 'kendallcorrelation':
      norm_x = self.norm_x if x_order is None else self.norm_x[x_order]
      variable_scores = _stat.statistics._kendall_correlation(x=norm_x, y=self.norm_y, denom=self.kendall_denom, watcher=watcher)

    return variable_scores.flat

  def _prepare_mi(self, variable_x, variable_y, variable_columns_x, variable_columns_y, options):
    mi_calc = _MutualInformation(variable_x, variable_y, variable_columns_x, variable_columns_y, options)

    #must be called BEFORE _flush_precalculated
    self.mi_test_stat = np.zeros((self.scores_shape[:2]))
    self.mi_k_freedom = np.zeros((self.scores_shape[:2]), dtype=int)
    for (output_index, input_index), test_stat, k_freedom in zip(self.variable_yx, mi_calc.test_statistics.flat, mi_calc.k_freedom.flat):
      self.mi_test_stat[output_index, input_index] = test_stat
      self.mi_k_freedom[output_index, input_index] = k_freedom

    if self.single_calc:
      self._flush_precalculated(mi_calc.calc())
    else:
      self.mi_calc = mi_calc

  def _prepare_distance_corr(self, variable_x, variable_y, variable_columns_x, variable_columns_y, options, **kwargs):
    corr_calc = _CDistanceCorrelation(variable_x, variable_y, kwargs.get("z"), options)

    try:
      for output_index, input_index, corr_val, p_val in corr_calc.precalculated_yx:
        self.precalculated_yx.append((variable_columns_y[output_index], variable_columns_x[input_index], corr_val, p_val))

      self.variable_yx = [(variable_columns_y[output_index], variable_columns_x[input_index]) for output_index, input_index, recalc_flag in corr_calc.variable_yx]

      if not corr_calc.is_constant:
        if self.single_calc:
          scores = corr_calc.calc()

          #must be called BEFORE _flush_precalculated
          self.distance_test_stat = np.zeros((self.scores_shape[:2]))
          for (output_index, input_index), test_stat in zip(self.variable_yx, corr_calc.test_statistics(scores).flat):
            self.distance_test_stat[output_index, input_index] = test_stat

          self._flush_precalculated(scores)

        else:
          self.distance_corr = corr_calc
          corr_calc = None
    finally:
      if corr_calc is not None:
        corr_calc.release()

  def _prepare_spearman(self, x, y, variable_columns_x, variable_columns_y):
    variable_x = np.empty((x.shape[0], len(variable_columns_x)))
    for dst_index, input_index in enumerate(variable_columns_x):
      variable_x[:, dst_index] = _rank_data(x[:, input_index])

    if self.inputs_only:
      variable_y = variable_x
    else:
      variable_y = np.empty((y.shape[0], len(variable_columns_y)))
      for dst_index, output_index in enumerate(variable_columns_y):
        variable_y[:, dst_index] = _rank_data(y[:, output_index])

    self._prepare_pearson(variable_x, variable_y)

  def _prepare_pearson(self, x, y):
    pearson_corr = _PearsonCorrData(x, y)
    if self.single_calc:
      self._flush_precalculated(pearson_corr.calc())
    else:
      self.pearson_corr = pearson_corr

  def _flush_precalculated(self, value):
    for (output_index, input_index), cov_value in zip(self.variable_yx, value.flat):
      self.precalculated_yx.append((output_index, input_index, cov_value, None))
    self.variable_yx = []

  def _prepare_robust_pearson(self, x, y, variable_columns_x, constant_columns_x, variable_columns_y, constant_columns_y, logger, watcher):
    seed = int(self.options.get('GTSDA/Seed')) if _shared.parse_bool(self.options.get('GTSDA/Deterministic')) else None

    support_data = []
    outliers = {}
    n_support_vectors = {}
    observations = np.empty((2, len(x)))

    for i, input_index in enumerate(variable_columns_x):
      observations[0] = x[:, input_index]
      for output_index in (variable_columns_y[:i] if self.inputs_only else variable_columns_y):
        _watch(watcher, None)

        observations[1] = y[:, output_index]
        support_indices = _outlier_detection._MinCovDet(random_state=np.random.RandomState(seed)).fit(observations.T).support_
        outlier_indices = np.where(~support_indices)[0].tolist()

        support_observations = observations[:, support_indices]
        const_support_observations = [_utils.is_constant(_) for _ in support_observations]

        if any(const_support_observations):
          self.precalculated_yx.append((output_index, input_index, np.nan if all(const_support_observations) else 0., 0))
        else:
          pearson_calc = _PearsonCorrData(support_observations[0], support_observations[1])
          if self.single_calc:
            self.precalculated_yx.append((output_index, input_index, pearson_calc.calc(), None))
          else:
            self.variable_yx.append((output_index, input_index))
            support_data.append((output_index, input_index, pearson_calc))

        n_support_vectors[(output_index, input_index)] = np.count_nonzero(support_indices)
        outliers['input%s;output%s' % (input_index, output_index)] = outlier_indices

        if self.inputs_only:
          if (output_index, input_index) in self.variable_yx:
            self.variable_yx.append((input_index, output_index))
            support_data.append((input_index, output_index, None))
          else:
            self.precalculated_yx.append((input_index, output_index) + self.precalculated_yx[-1][2:])
          n_support_vectors[(input_index, output_index)] = n_support_vectors[(output_index, input_index)]
          outliers['input%s;output%s' % (output_index, input_index)] = outlier_indices

        if logger:
          logger.info("- %d support observations selected to calculate Pearson correlation between x{%d} and y{%d}" % (n_support_vectors[(output_index, input_index)], input_index, output_index))

    self.outlier_info = {"SupportVectorsCount": n_support_vectors, "Info": {'Outliers': outliers}, "Data": support_data}

  def _prepare_partial_pearson_linear_regression(self, x, y, z, variable_columns_x, constant_columns_x, variable_columns_y, constant_columns_y):
    assert z is not None and z.size

    self.partial_pearson = []

    if not variable_columns_x or not variable_columns_y:
      return

    variable_columns_z, const_columns_z = _utils.check_for_constant_columns(z)
    if not variable_columns_z:
      raise _ex.GTException("Cannot calculate partial Pearson correlation because all explanatory variables (z) are constant.")

    # buld linear model of variable z columns with intercept
    norm_z = np.hstack(((z if not const_columns_z else z[:, variable_columns_z]), np.ones((z.shape[0], 1))))
    residuals_x = x - np.dot(norm_z, alg.lstsq(norm_z, x, rcond=np.finfo(float).eps*max(1,norm_z.size))[0])

    if self.inputs_only:
      def enumerate_residuals():
        for i, input_index in enumerate(variable_columns_x):
          for output_index in variable_columns_x[:i]:
            yield (input_index, output_index, residuals_x[:, input_index], residuals_x[:, output_index])
    else:
      residuals_y = y - np.dot(norm_z, alg.lstsq(norm_z, y, rcond=np.finfo(float).eps*max(1,norm_z.size))[0])
      def enumerate_residuals():
        for input_index in variable_columns_x:
          for output_index in variable_columns_y:
            yield (input_index, output_index, residuals_x[:, input_index], residuals_y[:, output_index])

    # initialize self.variable_yx, self.precalculated_yx and self.partial_pearson
    for input_index, output_index, residuals_x_i, residuals_y_j in enumerate_residuals():
      if not _utils.is_constant(residuals_x_i) and not _utils.is_constant(residuals_y_j):
        # residual of the both input and output columns are variable
        if self.single_calc:
          # no permutations would be used so just pre-calculate correlation value
          value = _PearsonCorrData(residuals_x_i, residuals_y_j).calc()
          self.precalculated_yx.append((output_index, input_index, value, None))
          if self.inputs_only:
            self.precalculated_yx.append((input_index, output_index, value, None))
        else:
          self.variable_yx.append((output_index, input_index))
          self.partial_pearson.append((output_index, input_index, _PearsonCorrData(residuals_x_i, residuals_y_j)))
          if self.inputs_only:
            self.variable_yx.append((input_index, output_index))
            self.partial_pearson.append((input_index, output_index, None)) # mark use previous calculation
      else:
        # Either x or y or both are completely explained by z, so no dependencie is presented
        self.precalculated_yx.append((output_index, input_index, 0., 0.))
        if self.inputs_only:
          self.precalculated_yx.append((input_index, output_index, 0., 0.))

    del enumerate_residuals

  def _prepare_partial_pearson_matrix(self, x, y, z, variable_columns_x, constant_columns_x, variable_columns_y, constant_columns_y):
    self.partial_pearson = []

    if not variable_columns_x or not variable_columns_y:
      return

    variable_columns_z = _utils.check_for_constant_columns(z)[0] if (z is not None and z.size) else []

    dim_norm_x = len(variable_columns_x)
    dim_norm_z = len(variable_columns_z) if z is not None and z.size else 0
    dim_norm_y = 0 if self.inputs_only else len(variable_columns_y)

    merged_data = np.empty((x.shape[0], dim_norm_x + dim_norm_z + dim_norm_y))
    for i, input_index in enumerate(variable_columns_x):
      merged_data[:, i] = x[:, input_index]

    if dim_norm_z:
      for i, input_index in enumerate(variable_columns_z):
        merged_data[:, dim_norm_x + i] = z[:, input_index]
      z_indices = list(range(dim_norm_x, dim_norm_x + dim_norm_z))

    if dim_norm_y:
      for i, input_index in enumerate(variable_columns_y):
        merged_data[:, dim_norm_x + dim_norm_z + i] = y[:, input_index]

    parent = _PearsonPartialCorrMatrix(merged_data, 0, 0, [])
    calculators_list = []

    if self.inputs_only:
      for i, input_index in enumerate(variable_columns_x):
        for j, output_index in enumerate(variable_columns_x[:i]):
          if not dim_norm_z:
            z_indices = [_ for _ in range(dim_norm_x) if _ != i and _ != j]
          curr_calc = _PearsonPartialCorrMatrix(parent, i, j, z_indices)
          calculators_list.append((input_index, output_index, curr_calc))
    else:
      for i, input_index in enumerate(variable_columns_x):
        if not dim_norm_z:
          z_indices = [_ for _ in range(dim_norm_x) if _ != i]
        for j, output_index in enumerate(variable_columns_y):
          curr_calc = _PearsonPartialCorrMatrix(parent, i, dim_norm_x + j, z_indices)
          calculators_list.append((input_index, output_index, curr_calc))

    # initialize self.variable_yx, self.precalculated_yx and self.partial_pearson
    for input_index, output_index, corr_calc in calculators_list:
      if not corr_calc.is_constant:
        # residual of the both input and output columns are variable
        if self.single_calc:
          # no permutations would be used so just pre-calculate correlation value
          value = corr_calc.calc()
          self.precalculated_yx.append((output_index, input_index, value, None))
          if self.inputs_only:
            self.precalculated_yx.append((input_index, output_index, value, None))
        else:
          self.variable_yx.append((output_index, input_index))
          self.partial_pearson.append((output_index, input_index, corr_calc))
          if self.inputs_only:
            self.variable_yx.append((input_index, output_index))
            self.partial_pearson.append((input_index, output_index, None)) # mark use previous calculation
      else:
        # Either x or y or both are completely explained by z, so no dependencie is presented
        self.precalculated_yx.append((output_index, input_index, 0., 0.))
        if self.inputs_only:
          self.precalculated_yx.append((input_index, output_index, 0., 0.))

class _PearsonCorrData(object):
  def __init__(self, x, y):
    self.norm_x, sigma_x = self.normalize(x)
    self.norm_y, sigma_y = (self.norm_x, sigma_x) if (y is None or y is x) else self.normalize(y)

    self.scale = sigma_y.T * sigma_x
    nonzero_denom = self.scale >= np.finfo(float).eps
    self.scale[nonzero_denom] = 1. / self.scale[nonzero_denom]
    self.scale[~nonzero_denom] = 0.

  @staticmethod
  def normalize(x):
    norm_x = x - np.mean(x, axis=0)
    return norm_x, np.fabs(np.hypot.reduce(norm_x)).reshape(1, -1)

  def calc(self, x_order=None):
    if x_order is None:
      cov_xy = np.dot(self.norm_y.T, self.norm_x)
    elif x_order.shape[0] > self.norm_y.shape[0]:
      cov_xy = np.dot(self.norm_y.T, self.norm_x[x_order[x_order < self.norm_y.shape[0]]])
    else:
      cov_xy = np.dot(self.norm_y.T, self.norm_x[x_order])
    return np.clip(cov_xy * self.scale, -1., 1.)


class _WatcherCallback(object):
  def __init__(self, watcher):
    self.__watcher = watcher

  def __call__(self, progress):
    return self.__watcher(None)


class _CDistanceCorrelation(object):
  _PWATCH = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_int)
  #typedef short (*watcher) (int);

  def __init__(self, x, y, z, options):
    self.__impl = None

    try:
      c_int_p = _ctypes.POINTER(_ctypes.c_int)
      c_double_p = _ctypes.POINTER(_ctypes.c_double)

      self.__library = _shared._library

      ciface_create = _ctypes.CFUNCTYPE(_ctypes.c_void_p, # result
                        _ctypes.c_int, c_int_p, c_double_p, c_int_p, # X: ndim, shape, data, strides
                        _ctypes.c_int, c_int_p, c_double_p, c_int_p, # Y: ndim, shape, data, strides
                        _ctypes.c_int, c_int_p, c_double_p, c_int_p, # Z: ndim, shape, data, strides
                        _ctypes.c_char_p, c_int_p, _ctypes.POINTER(_ctypes.c_void_p) # JSON-enveloped options, [out] scores shape, [out] error description
                        )(("GTSDACheckerDistanceCorrelationNew", self.__library))

      ciface_aux_data = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, # result, iface pointer
                                          c_int_p, _ctypes.POINTER(_ctypes.c_short), c_int_p, # const markers: shape, data, strides
                                          c_int_p, c_double_p, c_int_p, # aux data: shape, data, strides
                                          _ctypes.POINTER(_ctypes.c_void_p))\
                                        (("GTSDACheckerDistanceCorrelationAuxData", self.__library))

      self.__pvalues = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, # result, iface pointer, n_permutations
                                          c_int_p, c_double_p, c_int_p, # [in] pre-calculated corr(X, Y): shape, data, strides
                                          c_int_p, c_double_p, c_int_p, # [out] estimated p-values: shape, data, strides
                                          _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_void_p))\
                                        (("GTSDACheckerDistanceCorrelationPValue", self.__library))

      self.__calc = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, # result, iface pointer
                        c_int_p, c_double_p, c_int_p, # corr(X, Y): shape, data, strides
                        c_int_p, _ctypes.c_int, # permutations: data, step
                        _ctypes.POINTER(_ctypes.c_void_p))\
                      (("GTSDACheckerDistanceCorrelationCalc", self.__library))

      x_ndim, x_shape, x_ptr, x_strides = self._preprocess_matrix(x)
      y_ndim, y_shape, y_ptr, y_strides = self._preprocess_matrix(y if x is not y else None)
      z_ndim, z_shape, z_ptr, z_strides = self._preprocess_matrix(z)

      safe_options = _shared.write_json(options.values).encode('ascii')

      errdesc = _ctypes.c_void_p()
      scores_shape = (_ctypes.c_int * 2)()
      impl = ciface_create(x_ndim, x_shape, x_ptr, x_strides,
                           y_ndim, y_shape, y_ptr, y_strides,
                           z_ndim, z_shape, z_ptr, z_strides,
                           safe_options, scores_shape, _ctypes.byref(errdesc))

      if not impl:
        _shared.ModelStatus.checkErrorCode(0, 'Distance correlation error', errdesc)

      self.__impl = impl
      self.__shape = (scores_shape[0], scores_shape[1])
      self.__data = (x, y, z) # required because internal implementation stores weak pointers

      const_marker = np.zeros(self.__shape, dtype=_ctypes.c_short)
      cm_ndim, cm_shape, cm_ptr, cm_strides = self._preprocess_matrix(const_marker, _ctypes.c_short)

      self.__aux_data = np.zeros(self.__shape, dtype=_ctypes.c_double)
      aux_ndim, aux_shape, aux_ptr, aux_strides = self._preprocess_matrix(self.__aux_data)

      if not ciface_aux_data(self.__impl, cm_shape, cm_ptr, cm_strides,
                             aux_shape, aux_ptr, aux_strides, _ctypes.byref(errdesc)):
        _shared.ModelStatus.checkErrorCode(0, 'Distance correlation error', errdesc)

      self.variable_yx = [(i, j, True) for i, j in np.vstack(np.where(~const_marker)).T]
      self.precalculated_yx = [(i, j, self.__aux_data[i, j], (np.nan if np.isnan(self.__aux_data[i, j]) else 0.)) for i, j in np.vstack(np.where(const_marker)).T]

    except:
      exc_info = _sys.exc_info()
      self.release()
      _shared.reraise(*exc_info)

  @staticmethod
  def _preprocess_matrix(data, data_type=_ctypes.c_double):
    if data is None or not data.size:
      c_int_p = _ctypes.POINTER(_ctypes.c_int)
      return 0, c_int_p(), _ctypes.POINTER(data_type)(), c_int_p()
    else:
      shape = (_ctypes.c_int * data.ndim)()
      shape[:] = data.shape[:]

      strides = (_ctypes.c_int * data.ndim)()
      strides[:] = data.strides[:]

      data_ptr = (data_type * (strides[0] // data.itemsize * shape[0])).from_address(data.ctypes.data)

      return data.ndim, shape, data_ptr, strides

  def __del__(self):
    self.release()

  def release(self):
    if self.__impl is not None:
      _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTSDACheckerDistanceCorrelationFree", _shared._library))(self.__impl)
      self.__impl = None
      self.__data = None
      self.__calc = None

  @property
  def scores_shape(self):
    return self.__shape

  def calc(self, x_order=None):
    corr_yx = np.zeros(self.__shape, dtype=_ctypes.c_double)
    corr_ndim, corr_shape, corr_ptr, corr_strides = self._preprocess_matrix(corr_yx)

    if x_order is not None:
      x_order = np.array(x_order, dtype=_ctypes.c_int, copy=_shared._SHALLOW).reshape(-1)
      ord_ptr = (_ctypes.c_int * (x_order.strides[0] // x_order.itemsize * x_order.shape[0])).from_address(x_order.ctypes.data)
      ord_inc = x_order.strides[0]
    else:
      ord_ptr = _ctypes.POINTER(_ctypes.c_int)()
      ord_inc = 0

    errdesc = _ctypes.c_void_p()
    if not self.__calc(self.__impl, corr_shape, corr_ptr, corr_strides, ord_ptr, ord_inc, _ctypes.byref(errdesc)):
      _shared.ModelStatus.checkErrorCode(0, 'Distance correlation error', errdesc)

    return np.clip([corr_yx[i, j] for i, j, _ in self.variable_yx], -1., 1.)

  def estimate_pvalues(self, base_scores, n_permutations, watcher):
    base_scores = _shared.as_matrix(base_scores, shape=self.__shape, name="(base_scores) argument")
    corr_ndim, corr_shape, corr_ptr, corr_strides = self._preprocess_matrix(base_scores)

    pvalues = np.zeros(self.__shape, dtype=_ctypes.c_double)
    pvalues_ndim, pvalues_shape, pvalues_ptr, pvalues_strides = self._preprocess_matrix(pvalues)

    errdesc = _ctypes.c_void_p()
    watcher_ptr = self._PWATCH(_WatcherCallback(watcher)) if watcher is not None else _ctypes.c_void_p()
    if not self.__pvalues(self.__impl, n_permutations, corr_shape, corr_ptr, corr_strides, \
                          pvalues_shape, pvalues_ptr, pvalues_strides, watcher_ptr, \
                          _ctypes.byref(errdesc)):
      _shared.ModelStatus.checkErrorCode(0, 'Distance correlation error', errdesc)

    return pvalues

  def test_statistics(self, raw_scores):
    # raw_scores is scores vector returned by the calc() method
    test_stat_yx = np.array(raw_scores, copy=True)
    for dst_index, (output_index, input_index, _) in enumerate(self.variable_yx):
      test_stat_yx[dst_index] *= self.__aux_data[output_index, input_index]
    return test_stat_yx

  @property
  def is_constant(self):
    return not self.variable_yx

class _PearsonPartialCorrMatrix(object):
  """
  Calculator for the partial Pearson correlation using "Matrix" algorithm
  """
  def __init__(self, data, input_index, output_index, z_indices):
    self.input_index = input_index
    self.output_index = output_index
    self.z_indices = z_indices

    if isinstance(data, _PearsonPartialCorrMatrix):
      self.data = data.data
      self.corrcoef = data.corrcoef
    else:
      self.data = _PearsonCorrData(data, data)
      self.corrcoef = self.data.calc()

  @property
  def is_constant(self):
    return self.data.scale[self.output_index, self.input_index] == 0.

  def calc(self, x_order=None):
    if self.data.scale[self.output_index, self.input_index] == 0.:
      return 0.

    actual_indices = [self.input_index, self.output_index,] + self.z_indices
    corrcoef = self.corrcoef[actual_indices, :][:, actual_indices]

    if x_order is not None:
      norm_x = self.data.norm_x[:, self.input_index][x_order].reshape(1, -1)

      for dst_index, test_index in enumerate(actual_indices[1:]):
        curr_cov = np.clip(np.dot(norm_x, self.data.norm_x[:, test_index]) * self.data.scale[self.input_index, test_index], -1., 1.)
        corrcoef[0, 1 + dst_index] = curr_cov
        corrcoef[1 + dst_index, 0] = curr_cov

    corrcoef[np.diag_indices(corrcoef.shape[0])] += 1.e-5 # silly regularization
    pinv_corrcoef = alg.pinv(corrcoef)

    return -pinv_corrcoef[0, 1] / np.sqrt(pinv_corrcoef[0, 0] * pinv_corrcoef[1, 1])

class _MutualInformation(object):
  _FULL_SEARCH_BIN_SIZES = np.array([2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 48, 64, 88, 100], dtype=int)

  def __init__(self, x, y, variable_columns_x, variable_columns_y, options):
    self._normalize_method = None if not _shared.parse_bool(options.get('GTSDA/Checker/MutualInformation/Normalize')) \
                             else options.get('/GTSDA/Checker/MutualInformation/NormalizeMethod').lower()

    bins_method = options.get("GTSDA/Checker/MutualInformation/BinsMethod").lower()

    c_int_p = _ctypes.POINTER(_ctypes.c_int)
    c_double_p = _ctypes.POINTER(_ctypes.c_double)

    self.__library = _shared._library
    self.__entropy = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_int, # result, n_points
                                         _ctypes.c_int, c_double_p, _ctypes.c_int, # n_bins_x, x, incx
                                         _ctypes.c_int, c_double_p, _ctypes.c_int, # n_bins_y, y, incy
                                         c_double_p, c_double_p, c_double_p, c_double_p, # [out, optional] entropy_xy, entropy_x, entropy_y, bins_objective
                                         _ctypes.POINTER(_ctypes.c_void_p))(("GTSDACheckerEntropy", self.__library))


    self._inputs_only = y is None or y is x
    self._variable_x = [(x[:, i], self._available_bins_sizes(x[:, i], bins_method)) for i in variable_columns_x]
    self._variable_y = self._variable_x if self._inputs_only else [(y[:, i], self._available_bins_sizes(y[:, i], bins_method)) for i in variable_columns_y]

    self._setup_mi()

  def _available_bins_sizes(self, x, bins_method):
    bins_method = bins_method.lower()
    if bins_method == 'fullsearch':
      return self._FULL_SEARCH_BIN_SIZES[self._FULL_SEARCH_BIN_SIZES < np.sqrt(x.shape[0])]

    if bins_method == 'scott':
      h = 3.5 * np.std(x) / x.shape[0]**0.3333
      proposed_bins_size = np.ptp(x) / h
    elif bins_method == 'sqrt':
      proposed_bins_size = np.sqrt(x.shape[0])
    elif bins_method == 'sturges':
      proposed_bins_size = 1. + np.log2(float(x.shape[0]))
    elif bins_method == 'doane':
      mx = np.mean(x)
      g1 = np.mean((x - mx)**3) / np.std(x)**3
      sigma = np.sqrt(6. * (x.shape[0] - 2.) / (x.shape[0] + 1.) / (x.shape[0] + 3.))
      proposed_bins_size = 1. + np.log2(float(x.shape[0])) + np.log2(1. + g1 / sigma)
    elif bins_method == 'rice':
      proposed_bins_size = 2. * x.shape[0]**0.3333
    elif bins_method == 'freedman':
      iqr = np.percentile(x, 75.) -  np.percentile(x, 25.)
      h = 2. * iqr / x.shape[0]**0.3333
      proposed_bins_size = np.ptp(x) / h
    else:
      raise _ex.GTException('Invalid or usupported method to calculate optimal bins sizes for histogram MI estimation: %s' % bins_method)

    return np.array(max(2, int(np.ceil(proposed_bins_size))), dtype=int, ndmin=1)

  def _entropy(self, x_bins, y_bins, x, y, evaluate_obj):
    x_ptr = (_ctypes.c_double * (x.strides[0] // x.itemsize)).from_address(x.ctypes.data)
    y_ptr = (_ctypes.c_double * (y.strides[0] // y.itemsize)).from_address(y.ctypes.data)

    mi = _ctypes.c_double()
    entropy_x = _ctypes.c_double()
    entropy_y = _ctypes.c_double()
    obj = _ctypes.c_double()

    errdesc = _ctypes.c_void_p()
    if not self.__entropy(x.shape[0], x_bins, x_ptr, x.strides[0], y_bins, y_ptr, y.strides[0],
                          _ctypes.byref(mi), _ctypes.byref(entropy_x), _ctypes.byref(entropy_y),
                          (_ctypes.byref(obj) if evaluate_obj else None), _ctypes.byref(errdesc)):
      _shared.ModelStatus.checkErrorCode(0, 'Mutual information error', errdesc)

    return mi.value, entropy_x.value, entropy_y.value, obj.value

  def _setup_mi(self):
    dim_x = len(self._variable_x)
    dim_y = len(self._variable_y)
    points_number = self._variable_x[0][0].shape[0] if self._variable_x else 0

    mi = np.zeros((dim_y, dim_x), dtype=float)
    entropy_x = np.zeros((dim_y, dim_x), dtype=float)
    entropy_y = np.zeros((dim_y, dim_x), dtype=float)
    optimal_bins_sizes = np.empty((dim_x, dim_y), dtype=object)

    for input_index, (x_i, x_bins_candidates) in enumerate(self._variable_x):
      variable_y = self._variable_x[:input_index] if self._inputs_only else self._variable_y
      for output_index, (y_j, y_bins_candidates) in enumerate(variable_y):
        simplified_search = len(x_bins_candidates) * len(y_bins_candidates) > 4 and points_number > 20000

        optimal_bins_sizes[input_index, output_index] = []
        goal_values = np.zeros((x_bins_candidates.shape[0], y_bins_candidates.shape[0]), dtype=float)
        estimated_entropy = np.empty((x_bins_candidates.shape[0], y_bins_candidates.shape[0]), dtype=object)

        for ix, x_bins in enumerate(x_bins_candidates):
          if simplified_search:
            y_bins_candidates = [x_bins]
          for iy, y_bins in enumerate(y_bins_candidates):
            mi_ij, ex_ij, ey_ij, goal_values[ix, iy] = self._entropy(x_bins, y_bins, x_i, y_j, True)
            estimated_entropy[ix, iy] = (mi_ij, ex_ij, ey_ij)

        opt_value = np.min(goal_values)

        count = 0
        for ix, x_bins in enumerate(x_bins_candidates):
          if simplified_search:
            y_bins_candidates = [x_bins]
          for iy, y_bins in enumerate(y_bins_candidates):
            if np.fabs(goal_values[ix, iy] - opt_value) < 1.e-8:
              optimal_bins_sizes[input_index, output_index].append((x_bins, y_bins))

              mi_ij, ex_ij, ey_ij = estimated_entropy[ix, iy]
              mi[output_index, input_index] += mi_ij
              entropy_x[output_index, input_index] += ex_ij
              entropy_y[output_index, input_index] += ey_ij

              count += 1

        mi[output_index, input_index] /= count
        entropy_x[output_index, input_index] /= count
        entropy_y[output_index, input_index] /= count

        if self._inputs_only:
          mi[input_index, output_index] = mi[output_index, input_index]
          entropy_x[input_index, output_index] = entropy_x[output_index, input_index]
          entropy_y[input_index, output_index] = entropy_y[output_index, input_index]

    self._optimal_bins_sizes = optimal_bins_sizes
    self._entropy_x = entropy_x
    self._entropy_y = entropy_y
    self._mi = mi

  def _reordered_mi(self, x_order):
    dim_x = len(self._variable_x)
    dim_y = len(self._variable_y)

    mi = np.zeros((dim_y, dim_x), dtype=float)
    entropy_x = np.zeros((dim_y, dim_x), dtype=float)
    entropy_y = np.zeros((dim_y, dim_x), dtype=float)

    for input_index, (x_i, x_bins_candidates) in enumerate(self._variable_x):
      x_i = x_i[x_order]
      variable_y = self._variable_x[:input_index] if self._inputs_only else self._variable_y
      for output_index, (y_j, y_bins_candidates) in enumerate(variable_y):
        points_number = y_j.shape[0]
        optimal_bins_sizes = self._optimal_bins_sizes[input_index, output_index]
        for x_bins, y_bins in optimal_bins_sizes:
          mi_ij, ex_ij, ey_ij, _ = self._entropy(x_bins, y_bins, x_i, y_j, False)

          mi[output_index, input_index] += mi_ij
          entropy_x[output_index, input_index] += ex_ij
          entropy_y[output_index, input_index] += ey_ij

        count = len(optimal_bins_sizes)
        mi[output_index, input_index] /= count
        entropy_x[output_index, input_index] /= count
        entropy_y[output_index, input_index] /= count

        if self._inputs_only:
          mi[input_index, output_index] = mi[output_index, input_index]
          entropy_x[input_index, output_index] = entropy_x[output_index, input_index]
          entropy_y[input_index, output_index] = entropy_y[output_index, input_index]

    return mi, entropy_x, self._entropy_y

  def calc(self, x_order=None):
    if x_order is None:
      scores = self._mi.copy()
      entropy_x = self._entropy_x
      entropy_y = self._entropy_y
    else:
      scores, entropy_x, entropy_y = self._reordered_mi(x_order)

    if self._normalize_method is None:
      return scores

    valid_scores = scores > 1.e-8
    if self._normalize_method == 'averagemi':
      scores[valid_scores] *= 2. / (entropy_x[valid_scores] + entropy_y[valid_scores])
    elif self._normalize_method == 'geometricmeanmi':
      scores[valid_scores] /= np.sqrt(entropy_x[valid_scores] * entropy_y[valid_scores])
    elif self._normalize_method == 'minmi':
      scores[valid_scores] /= np.minimum(entropy_x[valid_scores], entropy_y[valid_scores])
    else:
      raise _ex.GTException('Invalid or unsupported MI scores normalization method: %s' % self._normalize_method)

    if self._inputs_only:
      np.fill_diagonal(scores, 1.)

    return scores

  @property
  def test_statistics(self):
    points_number = self._variable_x[0][0].shape[0] if self._variable_x else 0
    test_stat = 2. * points_number * self._mi
    if self._inputs_only:
      np.fill_diagonal(test_stat, np.nan)
    return test_stat

  @property
  def k_freedom(self):
    dim_x = len(self._variable_x)
    dim_y = len(self._variable_y)

    k = np.zeros((dim_y, dim_x), dtype=int)
    if self._inputs_only:
      for input_index in range(dim_x):
        k[input_index, input_index] = 1
        for output_index in range(input_index):
          k[input_index, output_index] = k[output_index, input_index] = sum(n_x * n_y for n_x, n_y in self._optimal_bins_sizes[input_index, output_index])
    else:
      for input_index in range(dim_x):
        for output_index in range(dim_y):
          k[output_index, input_index] = sum(n_x * n_y for n_x, n_y in self._optimal_bins_sizes[input_index, output_index])

    return k
