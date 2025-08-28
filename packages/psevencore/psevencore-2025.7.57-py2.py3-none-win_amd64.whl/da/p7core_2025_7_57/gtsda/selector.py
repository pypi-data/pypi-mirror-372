#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import numpy as np

from .. import exceptions as _ex
from . import utils as _utils
from .. import shared as _shared
from ..six.moves import xrange, range
from ..utils import distributions as _distributions

from . import checker as _checker
from .. import gtapprox as _gtapprox

_EPS = np.finfo(float).eps

class _SelectorParams(object):
  r"""
    _SelectorParams
  """

  def __init__(self, options, approx_options, logger, watcher):
    object.__setattr__(self, 'options', options)
    object.__setattr__(self, 'approx_options', approx_options)
    object.__setattr__(self, 'logger', logger)
    object.__setattr__(self, 'watcher', watcher)

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

def _log(logger, level, message):
  """Compute feature selection with add algorithm
  """
  if logger:
    logger(level, message)

def _check_for_coinciding_points(x, y):
  """Finds the coinciding points in the train set and excludes them
  """
  excluded_points = np.zeros((0, np.shape(x)[1]))
  excluded_values = np.zeros((0, np.shape(y)[1]))
  x_reduced, y_reduced = _utils.check_coinciding_points(x, y, excluded_points, excluded_values)
  return x_reduced, y_reduced

def set_default_approx_options(input_options):
  """Set default values of GTApprox options
  """
  approx_options = {}
  if input_options is None:
    input_options = {}

  for key in input_options:
    approx_options[key.lower()] = input_options[key]
    if isinstance(approx_options[key.lower()], str):
      approx_options[key.lower()] = approx_options[key.lower()].lower()

  # Set some options to reduce complexity
  approx_options.update({'gtapprox/hdaphasecount': approx_options.get('gtapprox/hdaphasecount', 1)})
  approx_options.update({'gtapprox/hdamultimax': approx_options.get('gtapprox/hdamultimax', 1)})
  approx_options.update({'gtapprox/hdamultimin': approx_options.get('gtapprox/hdamultimin', 1)})
  approx_options['gtapprox/internalvalidation'] = 'off'

  return approx_options

def _compute_averaged_error(errors, averaging_type):
  """Average errors over different outputs
  """
  if averaging_type.lower() == 'mean':
    error = np.mean(errors)
  elif averaging_type.lower() == 'rms':
    error = np.sqrt(np.mean(np.power(errors, 2)))
  elif averaging_type.lower() == 'max':
    error = np.max(errors)

  return error

def _calc_error(x, y, subset, x_test, y_test, selector_params):
  """Calculate errors for given train and test samples and subset of features
  """
  size_y = y.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  if subset is None:
    subset = list(range(int(x[0])))

  approx_options = dict(selector_params.approx_options)
  if len(subset) == 1:
    if len(x) <= 2 * len(subset) + 2:
      approx_options['GTApprox/Technique'] = 'RSM'
    elif len(x) < 125:
      approx_options['GTApprox/Technique'] = 'GP'
    elif len(x) <= 500:
      approx_options['GTApprox/Technique'] = 'HDAGP'
    else:
      approx_options['GTApprox/Technique'] = 'HDA'

  #The following option is set to run GTApprox in silent mode
  approx_options['//IterativeIV/SessionIsRunning'] = True

  builder = _gtapprox.Builder()
  builder.set_watcher(selector_params.watcher)

  if options['GTSDA/LogLevel'].lower() == 'debug':
    builder.set_logger(logger.logger)
  builder.options.set(approx_options)

  x_subset, y_subset = _check_for_coinciding_points(x[:, subset], y)

  error_type = options['GTSDA/Selector/Criteria/ErrorType'].lower()
  averaging_type = options['GTSDA/Selector/Criteria/ErrorAggregationType'].lower()

  if options['GTSDA/Selector/ValidationType'].lower() == 'internal':
    # We can't use internal validation from GTApprox as it uses reduced dimension data
    # during both training and validation. We need full dimension for validation.
    logger.debug('Starting validation using internal validation...')
    errors = _compute_internal_validation(x_subset, y_subset, builder)
    model = builder.build(x_subset, y_subset)
    logger.debug('Model validated.')

  elif options['GTSDA/Selector/ValidationType'].lower() == 'trainsample':
    logger.debug('Starting building GTApprox model...')
    model = builder.build(x_subset, y_subset)
    logger.debug('Model constructed.')

    logger.debug('Starting validation using train sample...')
    errors = model.validate(x_subset, y_subset)
    logger.debug('Model validated.')


  elif options['GTSDA/Selector/ValidationType'].lower() == 'testsample':
    logger.debug('Starting building GTApprox model...')
    model = builder.build(x_subset, y_subset)
    logger.debug('Model constructed.')

    logger.debug('Starting validation using test sample...')
    errors = model.validate(x_test[:, subset], y_test)
    logger.debug('Model validated.')

  errors = dict((key.lower(), value) for key, value in errors.items())

  if error_type == 'rrms':
    if x.shape[0] == 1:
      target_errors = errors['rms']
    else:
      target_errors = []
      for output_index in xrange(size_y):
        if _shared.isNanInf(errors['rrms'][output_index]):
          target_errors.append(errors['rms'][output_index])
        else:
          target_errors.append(errors['rrms'][output_index])
  else:
    target_errors = errors[error_type]

  error = _compute_averaged_error(target_errors, averaging_type)
  logger.info('Subset: ' + str(sorted(list(subset))) + '. ' + 'Error: ' + str(error) + '.\n')

  return error, model

def _compute_internal_validation(x, y, builder):
  """Compute internal validation for given sample.
  """
  size_y = y.shape[1]
  sample_size = x.shape[0]

  options = builder.options.get()

  iv_subset_count, iv_training_count = _gtapprox.technique_selection._read_iv_options_impl(int(options.get('GTApprox/IVSubsetCount')),
                                                                                           int(options.get('GTApprox/IVSubsetSize')),
                                                                                           int(options.get('GTApprox/IVTrainingCount')),
                                                                                           sample_size, True)

  permutation = np.random.permutation(sample_size)

  mean_error = np.empty((iv_training_count, size_y), dtype=float)
  rms = np.empty((iv_training_count, size_y), dtype=float)
  rrms = np.empty((iv_training_count, size_y), dtype=float)
  max_error = np.empty((iv_training_count, size_y), dtype=float)
  median_error = np.empty((iv_training_count, size_y), dtype=float)
  q_95_error = np.empty((iv_training_count, size_y), dtype=float)
  q_99_error = np.empty((iv_training_count, size_y), dtype=float)

  subset_size = sample_size // iv_subset_count
  validation_index = [-1]
  std_errors = np.std(y, ddof=1, axis=0)
  for i in xrange(iv_training_count):
    if i < sample_size % iv_subset_count:
      actual_size = subset_size + 1
    else:
      actual_size = subset_size

    validation_index = np.arange(validation_index[-1] + 1,
                                 validation_index[-1] + 1 + actual_size, dtype=int)
    training_index = np.arange(sample_size)
    training_index = np.delete(training_index, validation_index)

    x_train = x[permutation[training_index]]
    y_train = y[permutation[training_index]]

    x_validation = x[permutation[validation_index]]
    y_validation = y[permutation[validation_index]]

    dummy_options = {'GTApprox/IVSubsetCount': 0, 'GTApprox/IVTrainingCount': 0}
    model = builder.build(x_train, y_train, dummy_options)

    subset_errors = model.validate(x_validation, y_validation)
    mean_error[i] = subset_errors['Mean']
    rms[i] = subset_errors['RMS']
    for j in xrange(size_y):
      if std_errors[j] > 0:
        rrms[i][j] = subset_errors['RMS'][j] / std_errors[j]
      else:
        rrms[i][j] = subset_errors['RMS'][j]

    max_error[i] = subset_errors['Max']
    median_error[i] = subset_errors['Median']
    q_95_error[i] = subset_errors['Q_0.95']
    q_99_error[i] = subset_errors['Q_0.99']

  rrms = np.sort(rrms, axis=0)
  rms = np.sort(rms, axis=0)
  mean_error = np.sort(mean_error, axis=0)
  max_error = np.sort(max_error, axis=0)
  median_error = np.sort(median_error, axis=0)
  q_95_error = np.sort(q_95_error, axis=0)
  q_99_error = np.sort(q_99_error, axis=0)
  median_index = iv_training_count // 2

  errors = {}
  errors['Mean'] = mean_error[median_index]
  errors['RMS'] = rms[median_index]
  errors['RRMS'] = rrms[median_index]
  errors['Max'] = max_error[median_index]
  errors['Median'] = median_error[median_index]
  errors['Q_0.95'] = q_95_error[median_index]
  errors['Q_0.99'] = q_99_error[median_index]

  return errors

def _get_best_subset(subset1, error1, model1, subset2, error2, model2, threshold, min_allowed_error, total_min_error):
  """Compare two subsets of features in terms of error and sample size
  """
  threshold = np.minimum(threshold, 0.5)
  if not model1:
    model1 = model2
  elif not model2:
    model2 = model1

  #in case of dependency search error values are equal to None and are ignored
  is_dependency_search =  (error1 is None) or (error2 is None)

  if is_dependency_search or (max(error1, error2) <= min_allowed_error):
    if len(subset1) < len(subset2):
      best_subset = list(subset1)
      min_error = error1
      best_model = model1
    elif len(subset1) > len(subset2):
      best_subset = list(subset2)
      min_error = error2
      best_model = model2
    else:
      if error1 <= error2:
        best_subset = list(subset1)
        min_error = error1
        best_model = model1
      else:
        best_subset = list(subset2)
        min_error = error2
        best_model = model2

  elif min(error1, error2, total_min_error) / max(error1, error2, total_min_error) < 1. - threshold:
    if error1 < error2:
      best_subset = list(subset1)
      min_error = error1
      best_model = model1

    else:
      best_subset = list(subset2)
      min_error = error2
      best_model = model2

  else:
    if len(subset1) < len(subset2):
      best_subset = list(subset1)
      min_error = error1
      best_model = model1
    elif len(subset1) > len(subset2):
      best_subset = list(subset2)
      min_error = error2
      best_model = model2
    else:
      if error1 <= error2:
        best_subset = list(subset1)
        min_error = error1
        best_model = model1
      else:
        best_subset = list(subset2)
        min_error = error2
        best_model = model2

  total_min_error = min(error1, error2, total_min_error)

  return best_subset, min_error, best_model, total_min_error

def _proceed_subset(x, y, subset, watched_subsets, x_test, y_test, selector_params):
  '''Computes error for specific subset of features and correctly updates list of watched subsets
  '''
  if watched_subsets is None:
    watched_subsets = {'subsets': list(), 'errors': list()}

  sorted_subset = list(subset)
  sorted_subset.sort()
  if sorted_subset in watched_subsets['subsets']:
    index = watched_subsets['subsets'].index(sorted_subset)
    subset_error = watched_subsets['errors'][index]
    subset_model = None
  else:
    subset_error, subset_model = _calc_error(x, y, subset, x_test, y_test, selector_params)
    watched_subsets['subsets'].append(sorted_subset)
    watched_subsets['errors'].append(subset_error)

  return subset_error, watched_subsets, subset_model

def select(x, y, ranking, options, approx_options, x_test, y_test, logger, watcher):
  """Compute feature selection with one of the algorithms (wrapper function)
  """
  if options['GTSDA/Selector/Technique'].lower() == 'add':
    feature_subset, validation_error, model = select_add(x, y, ranking, options, approx_options,
                                                         x_test, y_test, logger, watcher)
  elif options['GTSDA/Selector/Technique'].lower() == 'del':
    feature_subset, validation_error, model = select_del(x, y, ranking, options, approx_options,
                                                         x_test, y_test, logger, watcher)
  elif options['GTSDA/Selector/Technique'].lower() == 'adddel':
    feature_subset, validation_error, model = select_add_del(x, y, ranking, options, approx_options,
                                                             x_test, y_test, logger, watcher)
  elif options['GTSDA/Selector/Technique'].lower() == 'full':
    feature_subset, validation_error, model = select_full(x, y, options, approx_options,
                                                          x_test, y_test, logger, watcher)
  return feature_subset, validation_error, model


def select_add(x, y, ranking, options, approx_options, x_test, y_test, logger, watcher):
  """Compute feature selection with add algorithm (wrapper function)
  """
  number_features = x.shape[1]
  selector_params = _SelectorParams(options, approx_options, logger, watcher)
  string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
  fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
  if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
    raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')

  if options['GTSDA/Selector/QualityMeasure'].lower() == 'dependency':
    best_subset = _select_fast_add(x, y, selector_params, initial_subset=fixed_subset)
    min_error = None
    best_model = None
  elif options['GTSDA/Selector/QualityMeasure'].lower() == 'error':
    if _shared.parse_bool(options['GTSDA/Selector/TryAllFeaturesEveryStep']) == True:
      best_subset, min_error, best_model, _, _ = _select_greedy_add(x, y, x_test, y_test, selector_params, initial_subset=fixed_subset)
    else:
      best_subset, min_error, best_model, _, _ = _select_add(x, y, ranking, x_test, y_test, selector_params, initial_subset=fixed_subset)

  return best_subset, min_error, best_model

def _select_add(x, y, ranking, x_test, y_test, selector_params, initial_subset=None, watched_subsets=None):
  """Compute feature selection with add algorithm
  """
  options = selector_params.options
  logger = selector_params.logger
  logger.info('Starting Add procedure.')
  logger.info('=======================')
  iterations_number = int(options['GTSDA/Selector/Criteria/MaxLookAheadSteps']) # number of iterations allowed without significant error improvement
  threshold = _shared.parse_float(options['GTSDA/Selector/Criteria/MinImprovement']) # relative error improvement, which considered significant
  min_allowed_error = _shared.parse_float(options['GTSDA/Selector/Criteria/TargetError']) # min error, which is not distinguished from zeros
  depth = iterations_number

  if (initial_subset is None) or (len(initial_subset) == 0):
    subset = []
    best_subset = []
    min_error = np.inf
  else:
    subset = list(initial_subset)
    subset_error, watched_subsets, subset_model = _proceed_subset(x, y, subset, watched_subsets, x_test, y_test, selector_params)
    best_subset = list(subset)
    extended_best_subset = list(subset)
    min_error = subset_error
    best_model = subset_model

    if subset_error <= min_allowed_error:
      best_subset.sort()
      extended_best_subset.sort()
      return best_subset, min_error, best_model, extended_best_subset, watched_subsets

  # In this cycle we try to add features as long as it significantly reduces error.
  # Extended best subset is best subset plus some promising but not error improving features.
  for i in xrange(len(ranking)):
    if not ranking[i] in subset:
      subset += [ranking[i]]

      subset_error, watched_subsets, subset_model = _proceed_subset(x, y, subset, watched_subsets, x_test, y_test, selector_params)

      if subset_error <= min_allowed_error:
        min_error = subset_error
        best_subset = list(subset)
        best_model = subset_model
        extended_best_subset = list(subset)
        break
      elif subset_error <= max(1. - threshold, 0.5) * min_error:
        min_error = subset_error
        best_subset = list(subset)
        best_model = subset_model
        extended_best_subset = list(subset)
        depth = iterations_number
      elif subset_error <= min_error:
        depth = iterations_number
        extended_best_subset = list(subset)
      elif subset_error <= min_error * (1. + threshold):
        extended_best_subset = list(subset)
        subset.pop()
        if depth == 0:
          break
        else:
          depth -= 1
      elif subset_error > min_error * (1. + threshold):
        subset.pop()
        if depth == 0:
          break
        else:
          depth -= 1

  best_subset.sort()
  extended_best_subset.sort()

  return best_subset, min_error, best_model, extended_best_subset, watched_subsets

def select_del(x, y, ranking, options, approx_options, x_test, y_test, logger, watcher):
  """Compute feature selection with del algorithm (wrapper function)
  """
  selector_params = _SelectorParams(options, approx_options, logger, watcher)

  if options['GTSDA/Selector/QualityMeasure'].lower() == 'dependency':
    best_subset = _select_fast_del(x, y, selector_params)
    min_error = None
    best_model = None
  elif options['GTSDA/Selector/QualityMeasure'].lower() == 'error':
    if _shared.parse_bool(options['GTSDA/Selector/TryAllFeaturesEveryStep']) == True:
      best_subset, min_error, best_model, _, _ = _select_greedy_del(x, y, x_test, y_test, selector_params)
    else:
      best_subset, min_error, best_model, _, _ = _select_del(x, y, ranking, x_test, y_test, selector_params)

  return best_subset, min_error, best_model

def _select_del(x, y, ranking, x_test, y_test, selector_params, initial_subset=None, watched_subsets=None):
  """Compute feature selection with del algorithm
  """
  number_features = x.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  logger.info('Starting Del procedure.')
  logger.info('=======================')
  iterations_number = int(options['GTSDA/Selector/Criteria/MaxLookAheadSteps']) # number of iterations allowed without significant error improvement
  depth = iterations_number
  threshold = _shared.parse_float(options['GTSDA/Selector/Criteria/MinImprovement']) # relative error improvement, which considered significant
  min_allowed_error = _shared.parse_float(options['GTSDA/Selector/Criteria/TargetError']) # min error, which is not distinguished from zeros
  string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
  fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
  if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
    raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')

  if initial_subset is None:
    initial_subset = sorted(list(ranking))
  else:
    ranking = np.array([i for i in ranking if i in initial_subset])

  subset = list(ranking)
  subset_error, watched_subsets, subset_model = _proceed_subset(x, y, subset, watched_subsets, x_test, y_test, selector_params)
  best_subset = list(subset)
  best_model = subset_model
  best_subset_error = subset_error
  extended_best_subset = list(subset)

  min_error = max(subset_error, min_allowed_error)

  # In this cycle we try to delete features as long as it doesn't significantly increase error.
  # Extended best subset is best subset minus some features which doesn't have major impact on error.
  for i in xrange(len(ranking) - 1, -1, -1):
    if ranking[i] in fixed_subset:
      continue

    subset.remove(ranking[i])

    if len(subset) > 0:
      subset_error, watched_subsets, subset_model = _proceed_subset(x, y, subset, watched_subsets, x_test, y_test, selector_params)

      if max(subset_error * (1. - threshold), 0.5 * subset_error) <= min_error:
        best_subset = list(subset)
        best_subset_error = subset_error
        best_model = subset_model
        extended_best_subset = list(subset)
        depth = iterations_number
        if subset_error < min_error:
          min_error = max(subset_error, min_allowed_error)
      else:
        extended_best_subset.remove(ranking[i])
        subset += [ranking[i]]
        if depth == 0:
          break
        else:
          depth -= 1

  best_subset.sort()
  extended_best_subset.sort()

  return best_subset, best_subset_error, best_model, extended_best_subset, watched_subsets

def select_add_del(x, y, ranking, options, approx_options, x_test, y_test, logger, watcher):
  """Compute feature selection with del algorithm (wrapper function)
  """
  selector_params = _SelectorParams(options, approx_options, logger, watcher)

  if options['GTSDA/Selector/QualityMeasure'].lower() == 'dependency':
    best_subset = _select_fast_add_del(x, y, selector_params)
    min_error = None
    best_model = None
  elif options['GTSDA/Selector/QualityMeasure'].lower() == 'error':
    best_subset, min_error, best_model = _select_add_del(x, y, ranking, x_test, y_test, selector_params)

  return best_subset, min_error, best_model

def _select_add_del(x, y, ranking, x_test, y_test, selector_params):
  """Compute feature selection with add-del algorithm
  """
  number_features = x.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  logger.info('Starting Add-Del procedure.')
  logger.info('===========================')
  threshold = _shared.parse_float(options['GTSDA/Selector/Criteria/MinImprovement']) # relative error improvement, which considered significant
  min_allowed_error = _shared.parse_float(options['GTSDA/Selector/Criteria/TargetError']) # min error, which is not distinguished from zeros

  watched_subsets = None
  # If we want to start with deleting (for data sets with big error on small feature subsets)
  if options['GTSDA/Selector/AddDel/FirstStep'].lower() == 'del':
    initial_subset = list(range(x.shape[1]))

    if options['GTSDA/Selector/QualityMeasure'].lower() == 'dependency':
      best_subset, watched_subsets = _select_fast_del(x, y, selector_params)
      min_error = None
      best_model = None
      last_error = min_error
      last_subset_length = len(best_subset)
      extended_subset = list(best_subset)
    elif options['GTSDA/Selector/QualityMeasure'].lower() == 'error':
      if _shared.parse_bool(options['GTSDA/Selector/TryAllFeaturesEveryStep']) == True:
        best_subset, min_error, best_model, extended_subset, watched_subsets = _select_greedy_del(x, y, x_test, y_test, selector_params,
                                                                                                  initial_subset, watched_subsets)
      else:
        best_subset, min_error, best_model, extended_subset, watched_subsets = _select_del(x, y, ranking, x_test, y_test, selector_params,
                                                                                           initial_subset, watched_subsets)
      if min_error <= min_allowed_error:
        return best_subset, min_error, best_model
      else:
        last_error = min_error
        last_subset_length = len(best_subset)

    total_min_error = min_error
  else:
    string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
    fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
    if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
      raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')

    extended_subset = fixed_subset
    if len(extended_subset) > 0:
      min_error, watched_subsets, best_model = _proceed_subset(x, y, extended_subset, watched_subsets, x_test, y_test, selector_params)
      best_subset = extended_subset
      last_subset_length = len(best_subset)
    else:
      min_error = np.inf
      best_subset = list(range(x.shape[1]))
      best_model = None
      last_subset_length = x.shape[1]

    last_error = min_error
    total_min_error = min_error

  # In this cycle we iterate adding and deleting features trying to reduce error and subset size.
  # We maintain best subset and some promising subset (extended_subset), which is used on further iterations.
  while True:
    initial_subset = list(extended_subset)
    if _shared.parse_bool(options['GTSDA/Selector/TryAllFeaturesEveryStep']) == True:
      add_best_subset, add_error, add_model, extended_subset, watched_subsets = _select_greedy_add(x, y, x_test, y_test, selector_params,
                                                                                                   initial_subset, watched_subsets)
    else:
      add_best_subset, add_error, add_model, extended_subset, watched_subsets = _select_add(x, y, ranking, x_test, y_test, selector_params,
                                                                                            initial_subset, watched_subsets)
    best_subset, min_error, best_model, total_min_error = _get_best_subset(best_subset, min_error, best_model,
                                                                           add_best_subset, add_error, add_model,
                                                                           threshold, min_allowed_error, total_min_error)

    initial_subset = list(extended_subset)
    if _shared.parse_bool(options['GTSDA/Selector/TryAllFeaturesEveryStep']) == True:
      del_best_subset, del_error, del_model, extended_subset, watched_subsets = _select_greedy_del(x, y, x_test, y_test, selector_params,
                                                                                                   initial_subset, watched_subsets)
    else:
      del_best_subset, del_error, del_model, extended_subset, watched_subsets = _select_del(x, y, ranking, x_test, y_test, selector_params,
                                                                                            initial_subset, watched_subsets)
    best_subset, min_error, best_model, total_min_error = _get_best_subset(best_subset, min_error, best_model,
                                                                           del_best_subset, del_error, del_model,
                                                                           threshold, min_allowed_error, total_min_error)

    if min_error <= min_allowed_error:
      break
    elif (min_error >= last_error) and (len(best_subset) >= last_subset_length):
      break
    else:
      last_error = min_error
      last_subset_length = len(best_subset)

  return best_subset, min_error, best_model

def _select_fast_add_del(x, y, selector_params):
  """Compute feature selection with add-del algorithm
  """
  number_features = x.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  logger.info('Starting Add-Del procedure.')
  logger.info('===========================')

  # If we want to start with deleting (for data sets with big error on small feature subsets)
  if options['GTSDA/Selector/AddDel/FirstStep'].lower() == 'del':
    best_subset = _select_fast_del(x, y, selector_params)
    if len(best_subset) == number_features:
      return best_subset
  else:
    string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
    fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
    if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
      raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')

    best_subset = list(fixed_subset)

  # In this cycle we iterate adding and deleting features trying to reduce subset size.
  history = []
  while tuple(_ for _ in best_subset) not in history:
    add_best_subset = _select_fast_add(x, y, selector_params, initial_subset=best_subset)
    if len(add_best_subset) == len(best_subset):
      break
    else:
      best_subset = list(add_best_subset)

    del_best_subset = _select_fast_del(x, y, selector_params, initial_subset=best_subset)
    if len(del_best_subset) == len(best_subset):
      break
    else:
      best_subset = list(del_best_subset)

    history.append(tuple(_ for _ in best_subset))

  return best_subset

def _select_greedy_add(x, y, x_test, y_test, selector_params, initial_subset=None, watched_subsets=None):
  """Compute feature selection with greedy add algorithm
  """
  options = selector_params.options
  logger = selector_params.logger
  logger.info('Starting Add procedure with one step full search.')
  logger.info('=================================================')
  iterations_number = int(options['GTSDA/Selector/Criteria/MaxLookAheadSteps']) # number of iterations allowed without significant error improvement
  threshold = _shared.parse_float(options['GTSDA/Selector/Criteria/MinImprovement']) # relative error improvement, which considered significant
  min_allowed_error = _shared.parse_float(options['GTSDA/Selector/Criteria/TargetError']) # min error, which is not distinguished from zeros
  depth = iterations_number

  if (initial_subset is None) or (len(initial_subset) == 0):
    initial_subset = []
    subset_error = np.inf
    subset_model = None
  else:
    subset_error, watched_subsets, subset_model = _proceed_subset(x, y, initial_subset, watched_subsets, x_test, y_test, selector_params)

  extended_best_subset = list(initial_subset)
  best_subset = list(initial_subset)
  best_model = subset_model
  min_error = subset_error

  iteration_best_subset = list(initial_subset)
  for _ in xrange(x.shape[1] - len(initial_subset)):
    iteration_min_error = np.inf
    previous_iteration_best_subset = list(iteration_best_subset)
    for i in xrange(x.shape[1]):
      if i not in previous_iteration_best_subset:
        subset = list(previous_iteration_best_subset)
        subset.append(i)
        subset_error, watched_subsets, subset_model = _proceed_subset(x, y, subset, watched_subsets, x_test, y_test, selector_params)

        if subset_error <= iteration_min_error:
          iteration_min_error = subset_error
          iteration_best_subset = list(subset)

    if iteration_min_error <= min_allowed_error:
      min_error = iteration_min_error
      best_subset = list(iteration_best_subset)
      best_model = subset_model
      extended_best_subset = list(iteration_best_subset)
      break
    elif iteration_min_error <= max(min_error * (1. - threshold), 0.5 * min_error):
      min_error = iteration_min_error
      best_subset = list(iteration_best_subset)
      best_model = subset_model
      extended_best_subset = list(iteration_best_subset)
      depth = iterations_number
    elif iteration_min_error <= min_error * (1. + threshold):
      extended_best_subset = list(iteration_best_subset)
      if depth == 0:
        break
      else:
        depth -= 1
    elif subset_error > min_error * (1. + threshold):
      if depth == 0:
        break
      else:
        depth -= 1

  best_subset.sort()
  extended_best_subset.sort()

  return best_subset, min_error, best_model, extended_best_subset, watched_subsets

def _select_greedy_del(x, y, x_test, y_test, selector_params, initial_subset=None, watched_subsets=None):
  """Compute feature selection with greedy del algorithm
  """
  number_features = x.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  logger.info('Starting Del procedure with one step full search.')
  logger.info('=================================================')
  iterations_number = int(options['GTSDA/Selector/Criteria/MaxLookAheadSteps']) # number of iterations allowed without significant error improvement
  threshold = _shared.parse_float(options['GTSDA/Selector/Criteria/MinImprovement']) # relative error improvement, which considered significant
  min_allowed_error = _shared.parse_float(options['GTSDA/Selector/Criteria/TargetError']) # min error, which is not distinguished from zeros
  depth = iterations_number
  string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
  fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
  if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
    raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')


  if initial_subset is None:
    initial_subset = list(range(x.shape[1]))

  subset_error, watched_subsets, subset_model = _proceed_subset(x, y, initial_subset, watched_subsets, x_test, y_test, selector_params)
  extended_best_subset = list(initial_subset)
  best_subset = list(initial_subset)
  best_model = subset_model
  min_error = subset_error
  best_subset_error = subset_error

  iteration_best_subset = list(initial_subset)
  for _ in xrange(len(initial_subset) - 1):
    iteration_min_error = np.inf
    previous_iteration_best_subset = list(iteration_best_subset)
    for i in previous_iteration_best_subset:
      if i in fixed_subset:
        continue

      subset = list(previous_iteration_best_subset)
      subset.remove(i)
      subset_error, watched_subsets, subset_model = _proceed_subset(x, y, subset, watched_subsets, x_test, y_test, selector_params)

      if subset_error <= iteration_min_error:
        iteration_min_error = subset_error
        iteration_best_subset = list(subset)

    if max(iteration_min_error * (1. - threshold), 0.5 * iteration_min_error) <= min_error:
      best_subset = list(iteration_best_subset)
      best_subset_error = iteration_min_error
      best_model = subset_model
      extended_best_subset = list(iteration_best_subset)
      depth = iterations_number
      if iteration_min_error < min_error:
        min_error = max(iteration_min_error, min_allowed_error)

    else:
      extended_best_subset = list(iteration_best_subset)
      if depth == 0:
        break
      else:
        depth -= 1

  best_subset.sort()
  extended_best_subset.sort()

  return best_subset, best_subset_error, best_model, extended_best_subset, watched_subsets

def select_full(x, y, options, approx_options, x_test, y_test, logger, watcher):
  """Compute feature selection with full search algorithm
  """
  selector_params = _SelectorParams(options, approx_options, logger, watcher)

  if options['GTSDA/Selector/QualityMeasure'].lower() == 'dependency':
    raise _ex.InvalidOptionsError('Option values GTSDA/Selector/RequiredFeatures=Dependency and ' +
                                  'GTSDA/Selector/Technique=Full are not compatible.')

  elif options['GTSDA/Selector/QualityMeasure'].lower() == 'error':
    best_subset, min_error, best_model = _select_full(x, y, x_test, y_test, selector_params)

  return best_subset, min_error, best_model

def _select_full(x, y, x_test, y_test, selector_params):
  """Compute feature selection with full search algorithm
  """
  number_features = x.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  logger.info('Starting Full search procedure.')
  logger.info('===============================')
  size_x = x.shape[1]
  min_error = np.inf
  total_min_error = min_error
  best_subset = list(range(size_x))
  best_model = None
  threshold = _shared.parse_float(options['GTSDA/Selector/Criteria/MinImprovement']) # relative error improvement, which considered significant
  min_allowed_error = _shared.parse_float(options['GTSDA/Selector/Criteria/TargetError']) # min error, which is not distinguished from zero
  string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
  fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
  if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
    raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')

  basic_indices = (0, 1)
  all_bool_masks = list(_utils.itertools_product(basic_indices, repeat=size_x))

  for i in range(1, len(all_bool_masks)):
    current_subset = np.array(all_bool_masks[i]).nonzero()[0]
    if not np.all(np.isin(fixed_subset, current_subset)):
      continue
    subset_error, subset_model = _calc_error(x, y, current_subset, x_test, y_test, selector_params)

    best_subset, min_error, best_model, total_min_error = _get_best_subset(best_subset, min_error, best_model,
                                                                           current_subset, subset_error, subset_model,
                                                                           threshold, min_allowed_error, total_min_error)

  return best_subset, min_error, best_model

def _select_fast_add(x, y, selector_params, initial_subset=None):
  """Compute dependency-based feature selection with add algorithm
  """
  number_features = x.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  watcher = selector_params.watcher
  logger.info('Starting fast add procedure.')
  logger.info('============================')
  string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
  fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
  if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
    raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')

  selected_features = ([] if (initial_subset is None or not initial_subset) else list(initial_subset)) + fixed_subset
  candidate_features = [_ for _ in range(number_features) if _ not in selected_features]
  checker_options = {'/GTSDA/Checker/OnlyInputsMode': 'false',
                     '/GTSDA/Checker/CorrelationAbsolute': 'on',
                     '/GTSDA/Checker/PearsonPartial/Algo' : 'LinearRegression',
                     'GTSDA/Checker/PValues/Enable': 'on',
                     'GTSDA/Checker/PValues/Method': 'auto',
                     'GTSDA/Checker/PValues/SignificanceLevel': options['GTSDA/Selector/Dependency/SignificanceLevel']}

  for key, value in checker_options.items():
    options[key] = value

  if options['GTSDA/Selector/Dependency/Type'].lower() in ('general', 'linear', 'auto'):
    general_dependency = options['GTSDA/Selector/Dependency/Type'].lower() == 'general'
    options["/GTSDA/Checker/DistanceCorrelation/DependentY"] = general_dependency
  else:
    raise _ex.InvalidOptionsError("Invalid or unsupported GTSDA selector dependency type: %s" % options['GTSDA/Selector/Dependency/Type'])

  # In this cycle we try to add features as long as the added features are statistically significant
  while candidate_features:
    if selected_features:
      options['GTSDA/Checker/Technique'] = 'DistancePartialCorrelation' if general_dependency else 'PearsonPartialCorrelation'
      scores, decisions, _, _ = _checker.check(x[:, candidate_features], y, z=x[:, selected_features], options=options, logger=logger, watcher=watcher)
    else:
      options['GTSDA/Checker/Technique'] = 'DistanceCorrelation' if general_dependency else 'PearsonCorrelation'
      scores, decisions, _, _ = _checker.check(x, y, z=None, options=options, logger=logger, watcher=watcher)

    decisions = _confirm_decision((x.shape[0] * (x.shape[0] + 1) // 2) if general_dependency else x.shape[0], scores, decisions)
    is_feature_found, best_column_index = _get_feature_add(scores, decisions)
    if is_feature_found:
      selected_features.append(candidate_features.pop(best_column_index))
    else:
      break

  return sorted(selected_features)

def _select_fast_del(x, y, selector_params, initial_subset=None):
  """Compute dependency-based feature selection with del algorithm
  """
  number_features = x.shape[1]
  options = selector_params.options
  logger = selector_params.logger
  watcher = selector_params.watcher
  logger.info('Starting fast del procedure.')
  logger.info('============================')
  string_fixed_subset = selector_params.options['GTSDA/Selector/RequiredFeatures']
  fixed_subset = _utils.literal_eval(string_fixed_subset, option_name='GTSDA/Selector/RequiredFeatures')
  if len(fixed_subset) > 0 and np.any([feature_index < 0 or feature_index > number_features - 1 for feature_index in fixed_subset]):
    raise _ex.InvalidOptionValueError('Invalid option value: GTSDA/Selector/RequiredFeatures=' + string_fixed_subset + '.')

  selected_features = list(range(number_features)) if (initial_subset is None or not initial_subset) else [_ for _ in initial_subset]

  checker_options = {'/GTSDA/Checker/OnlyInputsMode': 'false',
                     '/GTSDA/Checker/CorrelationAbsolute': 'on',
                     '/GTSDA/Checker/PearsonPartial/Algo' : 'LinearRegression',
                     'GTSDA/Checker/PValues/Enable': 'on',
                     'GTSDA/Checker/PValues/Method': 'auto',
                     'GTSDA/Checker/PValues/SignificanceLevel': options['GTSDA/Selector/Dependency/SignificanceLevel']}

  for key, value in checker_options.items():
    options[key] = value

  if options['GTSDA/Selector/Dependency/Type'].lower() in ('general', 'linear', 'auto'):
    general_dependency = options['GTSDA/Selector/Dependency/Type'].lower() == 'general'
    options["/GTSDA/Checker/DistanceCorrelation/DependentY"] = general_dependency
  else:
    raise _ex.InvalidOptionsError("Invalid or unsupported GTSDA selector dependency type: %s" % options['GTSDA/Selector/Dependency/Type'])

  # In this cycle we are removing features
  while selected_features:
    if len(selected_features) > 1:

      options['GTSDA/Checker/Technique'] = 'DistancePartialCorrelation' if general_dependency else 'PearsonPartialCorrelation'

      scores = np.empty((y.shape[1], len(selected_features)))
      decisions = np.empty(scores.shape, dtype=_checker._DECISIONS_TYPE)

      z_target = x[:, selected_features[1:]].copy()
      for score_index, x_index in enumerate(selected_features):
        scores[:, score_index:(score_index + 1)], decisions[:, score_index:(score_index + 1)], _, _ = \
          _checker.check(x[:, x_index:(x_index + 1)], y, z=z_target, options=options, logger=logger, watcher=watcher)
        z_target[:, (score_index % z_target.shape[1])] = x[:, x_index]
      del z_target

    else:
      options['GTSDA/Checker/Technique'] = 'DistanceCorrelation' if general_dependency else 'PearsonCorrelation'
      scores, decisions, _, _ = _checker.check(x[:, selected_features], y, z=None, options=options, logger=logger, watcher=watcher)

    decisions = _confirm_decision((x.shape[0] * (x.shape[0] + 1) // 2) if general_dependency else x.shape[0], scores, decisions)
    is_feature_found, del_feature_index = _get_feature_del(decisions, fixed_subset)

    if is_feature_found:
      selected_features.pop(del_feature_index)
    else:
      break

  return sorted(selected_features)

def _confirm_decision(sample_size, scores, decisions, alpha=0.05):
  # Convert decisions indicating score is statistically significant to
  # decisions indicating dependency is statistically significant.
  decisions = decisions.copy()
  active_scores = scores[decisions == 1.]

  t_stat = active_scores / np.clip(np.sqrt(1. - active_scores * active_scores), _EPS, np.inf) * np.sqrt(sample_size - 2.)
  t_crit = _distributions._tdist(sample_size - 2).quantile(1. - 0.5 * alpha)

  decisions[decisions == 1] = t_stat > t_crit
  decisions[decisions != 1] = 0.

  return decisions

def _get_feature_add(scores, decisions):
  "Determines which is the best feature to add based on scores and decisions"
  if decisions.ndim < 2:
    decisions = decisions.reshape(1, -1)

  invalid_decisions = ~np.isfinite(decisions)
  if invalid_decisions.any():
    decisions = decisions.copy()
    decisions[invalid_decisions] = 0.

  columnwise_decisions = (decisions * scores).max(axis=0)
  optimal_column_index = np.argmax(columnwise_decisions)
  return (columnwise_decisions[optimal_column_index] > 0), optimal_column_index

def _get_feature_del(decisions, fixed_subset):
  "Determines which is the best feature to delete based on scores and decisions"
  if decisions.ndim < 2:
    decisions = decisions.reshape(1, -1)

  # Candidates are zero columns. But it can be an empty list and if there are more
  # than one such column then it does not matter which one to select.
  candidates = np.where(~(decisions == 1.).any(axis=0))[0]
  if candidates.size > 0:
    return True, candidates[0]
  return False, 0
