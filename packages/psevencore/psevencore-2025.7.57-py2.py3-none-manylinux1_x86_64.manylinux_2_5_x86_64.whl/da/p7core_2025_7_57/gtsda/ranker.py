#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import sys as _sys
import numpy as np
import numpy.random as _random

from .. import shared as _shared
from .. import exceptions as _ex
from . import utils as _utils
from .. import gtdoe as _gtdoe
from ..gtdoe import orthogonal_array as _orthogonal_array
from ..six.moves import xrange, range

from .. import gtapprox as _gtapprox
from ..blackbox import Blackbox

_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
           73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173,
           179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281,
           283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
           419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541,
           547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659,
           661, 673, 677, 683, 691, 701, 709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809,
           811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941,
           947, 953, 967, 971, 977, 983, 991, 997]

class RankerParams(object):
  """RankerParams - structure used to store options and objects needed to control ranker execution
  """

  def __init__(self, mode, options, internal_options, approx_options, logger, watcher):
    object.__setattr__(self, 'mode', mode)
    object.__setattr__(self, 'options', options)
    object.__setattr__(self, 'internal_options', internal_options)
    object.__setattr__(self, 'approx_options', approx_options)
    object.__setattr__(self, 'logger', logger)
    object.__setattr__(self, 'watcher', watcher)

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

def fill_options_set(rank_options, internal_options, x_meta):
  """
  Purpose: Configures low level ranker options according to specified high level options.
    (also it's used to tweak old GT SDA options that are now private)

  Inputs:
    rank_options - da.p7core.Options object connected to corresponding GT SDA
  """
  #GTSDA options formatting
  technique = rank_options.get('GTSDA/Ranker/Technique').lower()
  is_variance_required = _shared.parse_bool(rank_options.get('GTSDA/Ranker/VarianceEstimateRequired'))

  if technique == 'sobol':
    method = rank_options.get('GTSDA/Ranker/Sobol/Method').lower()

    if is_variance_required:
      if method == 'auto':
        method = 'csta'
      elif method in ['fast', 'easi']:
        raise _ex.InvalidOptionValueError('GTSDA/Ranker/Technique=%s is not compatible with GTSDA/Ranker/VarianceEstimateRequired=True'
                                          % method.upper())
    else:
      # 'Fast' method is default but it can only estimate Sobol indices for continuous problem
      if method == 'auto':
        method = 'fast' if all(not _.get("enumerators") for _ in (x_meta or [])) else 'csta'

    if method == 'fast':
      rank_options.set({'GTSDA/Ranker/Sobol/Method': 'FAST'})
    elif method == 'csta':
      rank_options.set({'GTSDA/Ranker/Sobol/Method': 'CSTA'})

  elif technique == 'screening':
    method = rank_options.get('GTSDA/Ranker/Screening/Method').lower()
    if method in ['auto', 'morris']:
      rank_options.set({'GTSDA/Ranker/Screening/Method': 'morris'})

def fill_private_options_set(update_options):
  """
  Purpose: contains "secret" developers options with no C checking for testing and fine tuning.
  Such options start with '/gtsda/private/'
  Return: returns a dict, containing set options values
  """

  internal_options = {}

  internal_options['/GTSDA/Private/ConstantTolerance'.lower()] = 1.e-15
  internal_options['/GTSDA/Private/MinSampleSize'.lower()] = [2, 3]
  internal_options['/GTSDA/Private/RemoveDuplicates'.lower()] = True

  internal_options['/GTSDA/Private/NansAndInfsInBlackbox'.lower()] = 'raise' # 'raise', 'pass'
  internal_options['/GTSDA/Private/NansAndInfsInSample'.lower()] = 'raise' # 'raise', 'pass'

  internal_options['/GTSDA/Private/Ranker/SurrogateModel/TryToSimplify'.lower()] = True
  internal_options['/GTSDA/Private/Ranker/SurrogateModel/SimplificationErrorThreshold'.lower()] = 1.05
  internal_options['/GTSDA/Private/Ranker/SurrogateModel/SimplificationCandidatesList'.lower()] = \
    [{'GTApprox/Technique': 'RSM', 'GTApprox/RSMType': 'purequadratic'},
     {'GTApprox/Technique': 'RSM', 'GTApprox/RSMType': 'quadratic'},
     {'GTApprox/Technique': 'RSM', 'GTApprox/RSMType': 'linear'}
    ]
  internal_options['/GTSDA/Private/Ranker/SurrogateModel/GoodAccuracyThreshold'.lower()] = 0.05

  internal_options['/GTSDA/Private/Ranker/SurrogateModel/QualityErrorType'.lower()] = "Mean RRMS"
  internal_options['/GTSDA/Private/Ranker/SurrogateModel/QualityWarningThreshold'.lower()] = 0.3
  internal_options['/GTSDA/Private/Ranker/SurrogateModel/QualityErrorThreshold'.lower()] = 0.8

  internal_options['/GTSDA/Private/Ranker/Sobol/FAST/sMin'.lower()] = -np.pi
  internal_options['/GTSDA/Private/Ranker/Sobol/FAST/sMax'.lower()] = np.pi

  internal_options['/GTSDA/Private/Ranker/Sobol/CSTA/BootstrapSize'.lower()] = 1000

  internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MaxHarmonicCutoff'.lower()] = 6
  internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MinSampleCheck'.lower()] = True
  internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MinSampleSize'.lower()] = 150
  internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MaxSamplePortionCutoff'.lower()] = 0.001

  internal_options['/GTSDA/Private/Ranker/Sobol/Morris/BootstrapSize'.lower()] = 1000


  if update_options:
    for key in update_options:
      if key.lower() not in internal_options:
        raise Exception('Wrong internal option specified')
      else:
        internal_options[key.lower()] = update_options[key]

  return internal_options

class BoundedBlackbox(Blackbox):
  def __init__(self, blackbox, bounds):
    super(BoundedBlackbox, self).__init__()

    self.blackbox = blackbox
    self.bounds = _shared.as_matrix(bounds, shape=(2, blackbox.size_x()), name="'bounds' argument")

  def prepare_blackbox(self):
    for bounds, name in zip(self.bounds.T, self.blackbox.variables_names()):
      self.add_variable(bounds=bounds, name=name)

    for name in self.blackbox.objectives_names():
      self.add_response(name=name)

    if self.blackbox.gradients_enabled:
      self.enable_gradients(self.blackbox.gradients_order)
    self.set_numerical_gradient_step(self.blackbox.numerical_gradient_step)

  def evaluate(self, x):
    return self.blackbox.evaluate(x)


class NoiseBlackbox(Blackbox):
  r"""
    Purpose: Method creates a wrapper for blackbox which has one additional input which serves to estimate noise

    Inputs:
      blackbox - Blackbox object

    Return:  NoiseBlackbox object
  """
  def __init__(self, blackbox):

    Blackbox.__init__(self)

    self.blackbox = blackbox
    self.dim_x = blackbox.size_x()
    self.dim_f = blackbox.size_f()
    input_bounds = np.zeros((2, self.dim_x + 1))
    input_bounds[:, :self.dim_x] = np.array(blackbox.variables_bounds())
    input_bounds[1, self.dim_x] = 1.0
    self.borders_x = input_bounds

  def prepare_blackbox(self):
    for i in xrange(self.dim_x + 1):
      self.add_variable((self.borders_x[0, i], self.borders_x[1, i]))

    for _ in xrange(self.dim_f):
      self.add_response()

  def evaluate(self, x):
    """Purpose: surrogate model evaluation function

    Input:
      x - set of X-vectors as list(list(float))

    Return: returns set of Y-vectors as list()list(float)). Function Y(X) is the same as in get_data() function
    """

    return self.blackbox.evaluate(x[:, 0:self.dim_x])

class SurrogateModelBlackbox(Blackbox):
  r"""
    Purpose: Method creates GT Approx model from given sample to to be used as a black box by ranker

    Inputs:
      x - input values matrix as list(list(float))
      f - output values matrix as list(list(float))
      options - dict with GT Approx options
      control - dict containing necessary links and parameters (i.e. logger, watcher, options) (formed in analyzer.py)

    Return:  SurrogateModelBlackbox object
  """
  def __init__(self, x, f, control=None):

    Blackbox.__init__(self)

    self.dimx = x.shape[1]

    self.bordersx = [[np.min(x[:, ind]), np.max(x[:, ind])] for ind in xrange(x.shape[1])]

    f = np.array(f)
    if len(f.shape) == 1:
      f = f[:, np.newaxis]

    self.dimf = f.shape[1]

    if not control is None:
      self_logger = control.logger
      options = control.approx_options
      internal_options = control.internal_options
      watcher = control.watcher
    else:
      self_logger, options, internal_options, watcher = None, None, None, None

    builder = _gtapprox.Builder()
    if self_logger:
      self_logger.info('Building of surrogate model to use it as a blackbox...')
      if control.options.get('GTSDA/LogLevel').lower() == 'debug':
        builder.set_logger(self_logger.logger)

    builder.set_watcher(watcher)
    builder.options.set({'gtapprox/internalvalidation': 'on', 'gtapprox/componentwise': 'on'})
    if options:
      builder.options.set(options)

    error_type = internal_options['/GTSDA/Private/Ranker/SurrogateModel/QualityErrorType'.lower()]
    error_threshold = internal_options['/GTSDA/Private/Ranker/SurrogateModel/SimplificationErrorThreshold'.lower()]

    # if user havent specified explicitly the technique he wants to use we try to check if some simple models
    # like linear of quadratic would be accurate enough so that no time would be spent on building more complex models
    if internal_options['/GTSDA/Private/Ranker/SurrogateModel/TryToSimplify'.lower()] and \
      (options is None or _shared.parse_bool(builder.options.get('gtapprox/internalvalidation')) and \
       str(builder.options.get('gtapprox/technique')).lower() == 'auto'):

      current_best_error = np.inf

      candidates_list = internal_options['/GTSDA/Private/Ranker/SurrogateModel/SimplificationCandidatesList'.lower()]

      for candidate_options in candidates_list:

        lower_candidate_options = [key.lower() for key in candidate_options]
        ## Current GT Approx restriction
        if f.shape[1] > 1 and 'GTApprox/RSMFeatureSelection'.lower() in lower_candidate_options \
          and not _shared.parse_bool(builder.options.get('gtapprox/componentwise')):
          continue

        if x.shape[1] > 50 and candidate_options['GTApprox/Technique'].lower() == 'rsm' \
          and candidate_options['GTApprox/RSMType'].lower() in ['quadratic', 'interaction']:
          continue

        candidate = builder.build(x=x, y=f, options=candidate_options)
        candidate_error = candidate.iv_info['Aggregate'][error_type]

        if  error_threshold * current_best_error > candidate_error:
          self.model = candidate
          current_best_error = candidate_error

        if current_best_error <= internal_options['/GTSDA/Private/Ranker/SurrogateModel/GoodAccuracyThreshold'.lower()]:
          break
    else:
      current_best_error = np.inf

    # Try to build model the user wanted if no simplified model was accurate enough
    if current_best_error > internal_options['/GTSDA/Private/Ranker/SurrogateModel/GoodAccuracyThreshold'.lower()]:
      try:
        if str(builder.options.get('gtapprox/technique')).lower() == 'auto' and (50 <= x.shape[0] <= 1000):
          builder.options.set({'gtapprox/technique': 'GP'})
        user_options_model = builder.build(x=x, y=f)

        if _shared.parse_bool(builder.options.get('gtapprox/internalvalidation')):
          user_options_model_error = user_options_model.iv_info['Aggregate'][error_type]

          if current_best_error > error_threshold * user_options_model_error:
            self.model = user_options_model
            current_best_error = user_options_model_error
        else:
          self.model = user_options_model
      except:
        self_logger.warn("Model construction with user provided options failed! Simple default model will be used instead.")


    if not _shared.parse_bool(builder.options.get('gtapprox/internalvalidation')):
      if self_logger:
        self_logger.warn('InternalValidation option was manually disabled so surrogate model accuracy is not checked!')

    else:
      warning_threshold = internal_options['/GTSDA/Private/Ranker/SurrogateModel/QualityWarningThreshold'.lower()]
      error_threshold = internal_options['/GTSDA/Private/Ranker/SurrogateModel/QualityErrorThreshold'.lower()]

      if warning_threshold < current_best_error < error_threshold:
        if self_logger:
          self_logger.warn('Surrogate model is not very accurate so obtained ranking may not be reliable. ' +
                           'Try to increase sample size or tweak GTApprox options to obtain more accurate surrogate model.')
      elif current_best_error >= error_threshold:
        raise _ex.GTException('Surrogate model accuracy is too bad to catch the dependency. ' +
                              'Try to increase sample size or tweak GTApprox options to obtain more accurate surrogate model.')

    if self_logger:
      self_logger.info('Surrogate model was built successfully')

  def prepare_blackbox(self):
    """Purpose: Create surrogate model

    Return: None
    """
    for i in xrange(self.dimx):
      self.add_variable((self.bordersx[i][0], self.bordersx[i][1]))

    for _ in xrange(self.dimf):
      self.add_response()

  def evaluate(self, x):
    """Purpose: surrogate model evaluation function

    Input:
      x - set of X-vectors as list(list(float))

    Return: returns set of Y-vectors as list()list(float)). Function Y(X) is the same as in get_data() function
    """
    return self.model.calc(x)

def form_common_info_string(control):
  """Forms common info string for various indices
  """
  if control is None:
    return {}

  self_options = control.options

  info_string = {}
  info_string['Technique'] = self_options.get('GTSDA/Ranker/Technique')
  if self_options.get('GTSDA/Ranker/Technique').lower() == 'sobol':
    info_string['Method'] = self_options.get('GTSDA/Ranker/Sobol/Method')
  if self_options.get('GTSDA/Ranker/Technique').lower() == 'screening':
    info_string['Method'] = self_options.get('GTSDA/Ranker/Screening/Method')
  if self_options.get('GTSDA/Ranker/Technique').lower() == 'taguchi':
    technique_string = self_options.get('GTSDA/Ranker/Taguchi/Method').lower()
    if technique_string == 'auto':
      technique_string = 'maximum'
    info_string['Method'] = technique_string

  return info_string

def sample_based_ranker(x=None, y=None, control=None, bounds=None):
  """Function calls ranker with sample input
  """
  self_options = control.options
  internal_options = control.internal_options
  info_string = form_common_info_string(control)
  model = None

  if self_options.get('GTSDA/Ranker/Technique').lower() == 'taguchi':
    remove_duplicates = False
  else:
    remove_duplicates = internal_options['/GTSDA/Private/RemoveDuplicates'.lower()]
  min_sample_check = internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MinSampleCheck'.lower()]

  # Check if sample contains duplicate rows or constant columns
  # (currently constant columns are handled on method level, here we only show warning)
  x, constant_columns_x = _utils.preprocess_data(x)
  y, constant_columns_y = _utils.preprocess_data(y)
  number_of_inputs = x.shape[1]
  number_of_outputs = y.shape[1]

  active_columns_x = [dim for dim in xrange(number_of_inputs) if not dim in constant_columns_x]

  unique_idx = _utils.get_unique_rows_idxs(x, y)

  original_sample_size = x.shape[0]
  unique_sample_size = len(unique_idx)
  duplicate_points_size = original_sample_size - unique_sample_size

  # Show warnings if sample contains duplicate rows or constant columns
  if duplicate_points_size > 0:
    if duplicate_points_size == 1:
      control.logger.warn('Sample contains ' + str(duplicate_points_size) + ' duplicate point.')
    else:
      control.logger.warn('Sample contains ' + str(duplicate_points_size) + ' duplicate points.')

    if remove_duplicates:
      x = x[unique_idx, :]
      y = y[unique_idx, :]
      control.logger.warn('These points were removed from the analysis.')


  effective_sample_size = x.shape[0]
  control.logger.info('Effective sample size: ' + str(effective_sample_size) + '\n')

  if len(constant_columns_x) != 0:
    control.logger.warn('Constant columns in X: ' + ', '.join([str(elem) for elem in constant_columns_x]))
    control.logger.warn('Ranker returns nan for these inputs.')

  control.logger.info('Effective input dimensionality: ' + str(number_of_inputs - len(constant_columns_x)) + '\n')

  if len(constant_columns_y) != 0:
    control.logger.warn('Constant columns in Y: ' + ', '.join([str(elem) for elem in constant_columns_y]))
    control.logger.warn('Ranker returns 0 for all inputs for these outputs.')

  control.logger.info('Effective output dimensionality: ' + str(number_of_outputs - len(constant_columns_y)) + '\n')

  __watch(control.watcher, None)

  # Check indices type
  # screening indexes computation
  if self_options.get('GTSDA/Ranker/Technique').lower() == 'screening':
    if self_options.get('GTSDA/Ranker/Screening/Method').lower() == 'morris':
      # Here we throw exception if sample size is too small
      min_sizes = internal_options['/GTSDA/Private/MinSampleSize'.lower()]
      min_sample = min_sizes[0] * len(active_columns_x) + min_sizes[1]

      if (effective_sample_size < min_sample) and min_sample_check:
        if remove_duplicates:
          message = "Morris screening technique needs a sample of at least " + str(min_sample) + \
                    " unique points to work. Please try another technique for the analysis (see Technical reference for sample size requirements)."
        else:
          message = "Morris screening technique needs a sample of size least " + str(min_sample) + \
                    " points to work. Please try another technique for the analysis (see Technical reference for sample size requirements)."

        raise _ex.InvalidProblemError(message)

      # Generate blackbox with GT Approx
      blackbox = SurrogateModelBlackbox(x, y, control=control)
      model = blackbox.model
      budget = int(self_options.get('/GTSDA/Ranker/Screening/SurrogateModelBudget'))

      # Compute Morris screening
      info_string, scores, variances, _ = \
        blackbox_based_ranker(blackbox=blackbox, budget=budget, control=control, printed_constants=True, info_string=info_string, bounds=bounds)

    else:
      raise ValueError('Wrong technique to compute screening indices!')

  # sobol indexes computation
  elif self_options.get('GTSDA/Ranker/Technique').lower() == 'sobol':
    if self_options.get('GTSDA/Ranker/Sobol/Method').lower() in ['fast', 'csta']:
      # Here we throw exception if sample size is too small
      min_sizes = internal_options['/GTSDA/Private/MinSampleSize'.lower()]
      min_sample = min_sizes[0] * len(active_columns_x) + min_sizes[1]

      if effective_sample_size < min_sample and min_sample_check:
        if remove_duplicates:
          message = "Sobol indices (" + self_options.get('GTSDA/Ranker/Sobol/Method') + \
                    ") technique needs a sample of at least " + str(min_sample) + \
                    " unique points to work. Please try another technique for the analysis (see Technical reference for sample size requirements)."
        else:
          message = "Sobol indices (" + \
                    self_options.get('GTSDA/Ranker/Sobol/Method') + ") technique needs a sample of size least " + str(min_sample) + \
                    " points to work. Please try another technique for the analysis (see Technical reference for sample size requirements)."

        raise _ex.InvalidProblemError(message)

      # Generate blackbox with GT Approx
      blackbox = SurrogateModelBlackbox(x, y, control=control)
      model = blackbox.model
      budget = int(self_options.get('/GTSDA/Ranker/Sobol/SurrogateModelBudget'))

      # Compute scores
      info_string, scores, variances, _ = \
        blackbox_based_ranker(blackbox=blackbox, budget=budget, control=control, printed_constants=True, info_string=info_string, bounds=bounds)

    elif self_options.get('GTSDA/Ranker/Sobol/Method').lower() == 'easi':

      # Here we throw exception if sample size is too small
      min_sample = internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MinSampleSize'.lower()]

      x, y = _filter_points(bounds, x, y)
      effective_sample_size = len(x)

      if effective_sample_size < min_sample and min_sample_check:
        message = ("Sobol indices (EASI) technique needs a sample of at least %s %spoints to work." % (str(min_sample), ("unique " if remove_duplicates else "")))
        if bounds is not None:
          message += " %d %spoints are within the bounds given." % (effective_sample_size, ("unique " if remove_duplicates else ""))
        message += " Please try another technique for the analysis (see Technical reference for sample size requirements)."

        raise _ex.InvalidProblemError(message)

      # Compute EASI scores
      info_string, scores, variances = compute_easi_technique(inputs=x, outputs=y, control=control, info_string=info_string)

    else:
      raise ValueError('Wrong technique to compute Sobol indices!')
  # taguchi indexes computation
  elif self_options.get('GTSDA/Ranker/Technique').lower() == 'taguchi':
    x, y = _filter_points(bounds, x, y)
    if not len(x):
      raise _ex.InvalidProblemError("No points are within the bounds given")
    scores = get_taguchi_scores(x, y, self_options.get('GTSDA/Ranker/Taguchi/Method').lower(), control.logger, control.watcher)
    variances = None
  else:
    raise ValueError('Wrong indices type selected!')

  __watch(control.watcher, None)

  return info_string, scores, variances, model


def blackbox_based_ranker(blackbox=None, budget=None, control=None, printed_constants=False, info_string=None, bounds=None, x_meta=None):
  """Function calls ranker with blackbox input
  """
  internal_options = control.internal_options
  self_options = control.options
  self_logger = control.logger

  if info_string is None:
    info_string = form_common_info_string(control)

  if bounds is not None:
    blackbox = BoundedBlackbox(blackbox, bounds)

  input_dimension = blackbox.size_x()
  input_bounds = blackbox.variables_bounds()
  lower_bounds = np.array(input_bounds[0])
  upper_bounds = np.array(input_bounds[1])
  input_ranges = upper_bounds - lower_bounds

  __watch(control.watcher, None)

  control.logger.info('Selected computational budget is ' + str(budget) + ' function runs\n')

  constant_inputs = []
  active_inputs = []
  input_range_tolerance = _shared.parse_float(internal_options['/GTSDA/Private/ConstantTolerance'.lower()])
  for current_input in xrange(input_dimension):
    if input_ranges[current_input] < input_range_tolerance:
      constant_inputs.append(current_input)
    else:
      active_inputs.append(current_input)

  if input_dimension == len(constant_inputs):
    #all inputs are constant
    if self_logger:
      self_logger.warn("All the input columns in the data are constant. All the feature scores will be set to nan.")
    info_string['Variances'] = None
    return info_string, _shared._filled_array((blackbox.size_f(), input_dimension), np.nan), None, None

    control.logger.warn() #  @todo : implement
  elif len(constant_inputs) != 0 and not printed_constants:
    message = ''.join(str(constant_inputs))
    message += ' input columns are constant. Ranker returns nan for these inputs.\n'
    message += 'Effective input size: ' + str(input_dimension - len(constant_inputs)) + '\n'
    control.logger.info(message)

  generated_sample = None

  # screening indexes computation
  if self_options.get('GTSDA/Ranker/Technique').lower() == 'screening':
    if self_options.get('GTSDA/Ranker/Screening/Method').lower() == 'morris':
      if self_logger:
        self_logger.info("Computation of screening indices started...")
      info_string, scores, generated_sample, variances = compute_morris_screening(blackbox=blackbox, budget=budget,
                                                                                  control=control, info_string=info_string, x_meta=x_meta)

    else:
      raise ValueError('Wrong technique to compute screening indices!')

  # sobol indexes computation
  elif self_options.get('GTSDA/Ranker/Technique').lower() == 'sobol':
    is_noise_check_string = control.options.get('GTSDA/Ranker/NoiseCorrection')
    if is_noise_check_string.lower() != 'auto' and _shared.parse_bool(is_noise_check_string):
      is_noise_check = True
      blackbox = NoiseBlackbox(blackbox)
      if x_meta:
        x_meta.append({"type": "Continuous"})
    else:
      is_noise_check = False

    index_type = str(self_options.get('GTSDA/Ranker/Sobol/IndicesType')).lower()
    sobol_method = self_options.get('GTSDA/Ranker/Sobol/Method').lower()

    if sobol_method == 'fast':
      if x_meta is not None and any(_.get("enumerators") for _ in x_meta):
        raise _ex.InvalidProblemError("FAST Method can only estimate Sobol Indices for continuous problems.")
      if self_logger:
        self_logger.info("Computation of Sobol indices started...")
      info_string, generated_sample = compute_fast_technique(blackbox=blackbox, budget=budget, control=control, info_string=info_string)
      variances = None

    elif sobol_method == 'csta':
      if self_logger:
        self_logger.info("Computation of Sobol indices started...")
      info_string, generated_sample = compute_csta_technique(blackbox=blackbox, budget=budget, control=control, info_string=info_string, x_meta=x_meta)

      if _shared.parse_bool(self_options.get('GTSDA/Ranker/VarianceEstimateRequired')):
        if index_type == 'total':
          variances = info_string['Variances']['Total indices']
        elif index_type == 'main':
          variances = info_string['Variances']['Main indices']
        elif index_type == 'interactions':
          variances = info_string['Variances']['Interaction indices']
      else:
        variances = None
    elif sobol_method == 'easi':
      raise ValueError("EASI Method can estimate Sobol Indices only in sample-based mode.")
    else:
      raise ValueError('Wrong technique to compute Sobol indices!')

    if is_noise_check:
      info_string, generated_sample = correct_for_noise_sobol(info_string, generated_sample)

    if index_type == 'total':
      scores = info_string['Total indices']
    if index_type == 'main':
      scores = info_string['Main indices']
    if index_type == 'interactions':
      scores = info_string['Interaction indices']

  # Taguchi indexes computation
  elif self_options.get('GTSDA/Ranker/Technique').lower() == 'taguchi':
    if self_logger:
      self_logger.info("Computation of Taguchi scores started...")
      self_logger.info("  Taguchi: generating Orthogonal array...")
    info_string, blackbox_inputs, blackbox_outputs = get_sample_for_taguchi(blackbox, budget, self_options, info_string, self_logger, x_meta=x_meta)
    generated_sample = {'inputs': blackbox_inputs, 'outputs': blackbox_outputs}
    non_numeric_found, _, _ = check_for_nans_and_infs(blackbox_outputs, control)
    # Nans or infs in sample so we terminate everything
    if non_numeric_found and internal_options['/GTSDA/Private/NansAndInfsInBlackbox'.lower()] == 'raise':
      return info_string, np.nan * np.zeros((len(blackbox_outputs[0]), len(blackbox_inputs[0]))), [], generated_sample

    if self_logger:
      self_logger.debug("Taguchi: Finished computing blackbox outputs.")
    if self_logger:
      self_logger.debug("Taguchi: Calculating scores...")
    scores = get_taguchi_scores(blackbox_inputs, blackbox_outputs,
                                self_options.get('GTSDA/Ranker/Taguchi/Method').lower(),
                                self_logger, control.watcher)
    variances = None
    if self_logger:
      self_logger.debug("Taguchi scores calculation is finished.")

  if constant_inputs:
    if scores is not None:
      try:
        scores = np.array(scores, copy=_shared._SHALLOW)
        scores[:, constant_inputs] = np.nan
      except:
        pass

    if variances is not None:
      try:
        variances = np.array(scores, copy=_shared._SHALLOW)
        variances[:, constant_inputs] = np.nan
      except:
        pass

  __watch(control.watcher, None)
  return info_string, scores, variances, generated_sample

def __watch(watcher, obj):
  if watcher:
    retval = watcher(obj)
    if not retval:
      raise _ex.UserTerminated()

def _form_correct_blackbox_outputs(blackbox=None, inputs=None, size_x=None, size_f=None):
  """Code handles the case when blackbox can't work in batch mode or provides string instead of float output
  """

  inputs = _shared.as_matrix(inputs, shape=(None, size_x), name="Blackbox evaluation input")

  try:
    black_box_output = blackbox(inputs)
    exc_info = None
  except Exception:
    exc_info = _sys.exc_info()

  if exc_info is not None:
    try:
      black_box_output = []
      for i, inputs_row in enumerate(inputs):
        black_box_output.append(_shared.as_matrix(blackbox(inputs_row.reshape(1, -1)), shape=(1, None), name=("Blackbox evaluation result #%d (zero-based)" % i)))
    except:
      _shared.reraise(_ex.UserEvaluateException, ("Can't compute blackbox output: %s" % exc_info[1]), exc_info[2])

  response = _shared.as_matrix(black_box_output, name="Blackbox responses")
  if size_f is not None:
    # note response may include gradients
    response = response[:, :size_f]
  return response

def check_for_nans_and_infs(blackbox_outputs, control):
  """Function checks if nans or infs are present in the outputs.
  If they found function indicates it via 'non_numeric_found' variable. Also it returns indices of infs and nans.
  """
  nan_list = np.isnan(blackbox_outputs)
  inf_list = np.isinf(blackbox_outputs)
  nan_count = nan_list.sum()
  inf_count = inf_list.sum()

  non_numeric_found = False

  if control.internal_options['/GTSDA/Private/NansAndInfsInBlackbox'.lower()] == 'raise':
    if inf_count > 0 or nan_count > 0:
      non_numeric_found = True
      error_string = ''
      if nan_count > 0:
        error_string += '%s nan values were encountered \n' % str(nan_count)

      if inf_count > 0:
        error_string += '%s inf values were encountered \n' % str(inf_count)
      error_string += 'in %s output values computed \n' % str(len(blackbox_outputs))
      error_string += 'No computation of scores would be done!'

      if control.logger:
        control.logger.error(error_string)

  return non_numeric_found, nan_list, inf_list

def correct_for_noise_sobol(info_string, sample):
  sobol_total = info_string['Total indices']
  sobol_main = info_string['Main indices']

  input_dimension = sobol_total.shape[1] - 1

  noise = sobol_total[:, input_dimension]
  noise = np.tile(np.transpose(np.tile(noise, (1, 1))), input_dimension)

  high_noise_indices = noise > 0.99999
  low_noise_indices = noise <= 0.99999

  sobol_total = sobol_total[:, :input_dimension]
  sobol_main = sobol_main[:, :input_dimension]

  sobol_total[low_noise_indices] = (sobol_total[low_noise_indices] - noise[low_noise_indices]) / (1.0 - noise[low_noise_indices])
  sobol_main[low_noise_indices] = sobol_main[low_noise_indices] / (1.0 - noise[low_noise_indices])
  sobol_total[high_noise_indices] = 0.
  sobol_main[high_noise_indices] = 0.

  sobol_interactions = sobol_total - sobol_main

  np.clip(sobol_total, 0., 1., out=sobol_total)
  np.clip(sobol_main, 0., 1., out=sobol_main)
  np.clip(sobol_interactions, 0., 1., out=sobol_interactions)

  info_string['Total indices'] = sobol_total
  info_string['Main indices'] = sobol_main
  info_string['Interaction indices'] = sobol_interactions
  info_string['Noise'] = noise

  sample['inputs'] = sample['inputs'][:, :input_dimension]

  return info_string, sample

def compute_fast_technique(budget=1000, blackbox=None, control=None, info_string=None):
  """Extended Fourier Amplitude Sensitivity Testing Algorithm
  implemented according to
  Saltelli A. 1999 "A Quantitative Model-Independent Method for Global Sensitivity Analysis of Model Output"

  Inputs:
    budget : wanted no. of sample points
    blackbox : p7core.da.Blackbox object
    control : RankerParams object

  Returns:
    info - dict containing main, total and total interactions indices
    sobol_indices - matrix of indices of type selected according to 'GTSDA/Ranker/Sobol/IndicesType' option
    sample - sample generated by the blackbox

  Other used variables/constants:
    number_of_runs : no. of runs on each curve
    input_dimension : no. of input factors
    current_frequences[] : vector of <input_dimension> frequencies
    max_frequency : frequency for the group of interest
    other_frequences[] : set of freq. used for the compl. group
    blackbox_inputs[] : parameter combination rank matrix
    blackbox_outputs[] : model output
    Ac[],Bc[]: Fourier coefficients
    phase_shift[] : random phase shift
    all_variance : total output variance (for each curve)
    part_variance_i : partial var. of par. i (for each curve)
    sobol_indexes : result
  """

  def find_nearest_lesser_prime(n):
    if _PRIMES[-1] >= n:
      return float(_PRIMES[np.searchsorted(_PRIMES, n, 'right') - 1]) if n > 1 else 1

    n_stop = np.searchsorted(_PRIMES, np.sqrt(_PRIMES[-1] + 1), 'right') + 1
    p_stop = _PRIMES[n_stop - 1]**2
    for i in xrange(_PRIMES[-1] + 1, n + 1):
      if i == p_stop:
        p_stop = _PRIMES[n_stop]**2
        n_stop += 1
      elif all([(i % p) for p in _PRIMES[:n_stop]]):
        _PRIMES.append(i)
    return float(_PRIMES[-1])

  if info_string is None:
    info_string = form_common_info_string(control)

  if not control is None:
    internal_options = control.internal_options
    options = control.options
    self_logger = control.logger
  else:
    internal_options, options, self_logger = None, None, None

  seed = int(options.get('GTSDA/Seed')) if options is not None else 0
  rnd = _random.RandomState(seed if _shared.parse_bool(options.get('GTSDA/Deterministic')) else None)

  if self_logger:
    self_logger.debug('Sobol indices computation technique FAST was selected.')

  input_dimension = blackbox.size_x()
  input_bounds = blackbox.variables_bounds()
  lower_bounds = np.array(input_bounds[0])
  upper_bounds = np.array(input_bounds[1])
  input_ranges = upper_bounds - lower_bounds
  output_dimension = blackbox.size_f()

  sobol_main = np.empty((output_dimension, input_dimension))
  sobol_total = np.empty((output_dimension, input_dimension))
  sobol_interactions = np.empty((output_dimension, input_dimension))
  sobol_main.fill(np.nan)
  sobol_total.fill(np.nan)
  sobol_interactions.fill(np.nan)

  number_of_search_curves = int(options.get("GTSDA/Ranker/Sobol/FASTNumberCurves")) # no. of search curves

  # case for 3- or more dimensional task
  if input_dimension > 2:
    # (b/s - d) / (2cd) >= (c-1)(d-2)+1, where b - budget, s - number_of_search_curves, d - input_dimension
    number_of_coeffs = max(1, int((6 * input_dimension - 2 * input_dimension**2 +
                                   (4 * input_dimension**4 - 32 * input_dimension**3 +
                                    (52 + 8 * budget / number_of_search_curves) * input_dimension**2 -
                                    16 * input_dimension * budget / number_of_search_curves)**0.5) /
                                  (4 * input_dimension**2 - 8 * input_dimension))) + 1

    # search for suitable parametres
    while number_of_coeffs != 1:
      #search for prime frequency
      max_frequency = int(np.floor((budget / number_of_search_curves - input_dimension) / (2 * number_of_coeffs) / input_dimension))
      max_frequency = find_nearest_lesser_prime(max_frequency)

      max_complimentary_frequency = max_frequency / (2 * number_of_coeffs)
      if max_complimentary_frequency < (number_of_coeffs - 1) * (input_dimension - 2) + 1:
        number_of_coeffs -= 1
      else:
        break

    #if our budget is small, we try
    if number_of_coeffs == 1:
      number_of_coeffs = 2
      max_frequency = np.floor((budget / number_of_search_curves - input_dimension) / (2 * number_of_coeffs) / input_dimension)
      if max_frequency < 4:
        raise _ex.InvalidProblemError('FAST: Budget is too small for computation of Sobol indices with FAST method (need at least ' + \
                                       str(17 * input_dimension*number_of_search_curves) + ' function calls with current options).')
      else:
        self_logger.warn('FAST: Computation budget is quite small for Sobol indices, computation results may be unreliable.')

    max_complimentary_frequency = np.floor(max_frequency / (2 * number_of_coeffs))

  #case for 2-dimensional task
  else:
    if input_dimension == 1:
      budget = np.min((budget, 10000)) #This is to avoid some bugs in 1d case
    step_size = 0
    need_step = 2.0
    number_of_coeffs = 21
    while step_size < need_step:
      number_of_coeffs -= 1
      if number_of_coeffs == 1 and need_step > 1.0:
        need_step -= 1.0
        number_of_coeffs = 21

      #case for very small budgets: FAST can estimate only big indices
      elif number_of_coeffs == 1 and need_step == 1.0:
        number_of_coeffs = 2
        max_frequency = np.floor((budget / number_of_search_curves - input_dimension) / (2 * number_of_coeffs) / input_dimension)
        if max_frequency / (2 * number_of_coeffs) < 1:
          raise _ex.InvalidProblemError('FAST: Budget is too small for computation of Sobol indices with FAST method (need at least ' +
                                        str(17 * input_dimension * number_of_search_curves) +
                                        ' function calls with current options)' +
                                        ' try Screening indices instead (starts to work at (need at least 3*<input dimension> function calls)')
        else:
          self_logger.warn('Computational budget is quite small for Sobol indices computation. Results may be unreliable')
          break

      max_frequency = int(np.floor((budget / number_of_search_curves - input_dimension) / (2 * number_of_coeffs) / input_dimension))
      max_frequency = find_nearest_lesser_prime(max_frequency)
      max_complimentary_frequency = max_frequency / (2 * number_of_coeffs)

      infd = np.min((max_complimentary_frequency, input_dimension))

      if infd <= 1:
        step_size = 0
      else:
        step_size = round((max_complimentary_frequency - 1) / (infd - 1))

  number_of_runs = int(2 * number_of_coeffs * max_frequency + 1)

  if self_logger:
    self_logger.debug('FAST: %s calls to blackbox function would be performed' % str(number_of_runs))

  sample = {}

  other_frequences = get_other_frequences_fast_technique(input_dimension - 1, max_complimentary_frequency)

  showed_constant_warning = np.zeros(output_dimension)

  input_range_tolerance = _shared.parse_float(internal_options['/GTSDA/Private/ConstantTolerance'.lower()])
  for current_input in xrange(input_dimension):
    if input_ranges[current_input] < input_range_tolerance:
      sobol_total[:, current_input] = np.nan
      sobol_main[:, current_input] = np.nan
      continue

    # Initialize AV,AVi,AVci to zero.
    if self_logger:# and (not is_noise_check or current_input != input_dimension - 1):
      self_logger.info("FAST: Processing input %s" % str(current_input + 1))

    actual_number_of_search_curves = number_of_search_curves

    # Loop over the <number_of_search_curves> search curves.
    for current_curve in xrange(number_of_search_curves):
      __watch(control.watcher, None)

      # Setting the vector of frequencies <current_frequences>
      # for the <input_dimension> factors.

      current_frequences = [0] * input_dimension
      current_frequences[current_input] = max_frequency
      loop_input = (current_input + 1) % input_dimension
      frequences_counter = 0
      while loop_input != current_input:
        current_frequences[loop_input] = other_frequences[frequences_counter]
        frequences_counter += 1
        loop_input = (loop_input+1) % input_dimension

      # Setting the relation between the scalar
      # variable <s> and the coordinates
      # {x_1,x_2,...x_<input_dimension>} of each sample point.
      phase_shift = 2 * np.pi * np.tile(rnd.rand(1, input_dimension), [number_of_runs, 1])  # random phase shift

      s_min = internal_options['/GTSDA/Private/Ranker/Sobol/FAST/sMin'.lower()]
      s_max = internal_options['/GTSDA/Private/Ranker/Sobol/FAST/sMax'.lower()]

      s = np.arange(s_min, s_max, (s_max - s_min) / number_of_runs)[:number_of_runs, np.newaxis]

      current_frequences = np.array(current_frequences)[np.newaxis, :]

      angles = s.dot(current_frequences) + phase_shift
      blackbox_inputs = 0.5 + np.arcsin(np.sin(angles)) / np.pi

      if self_logger:
        self_logger.debug("FAST: Generating input sample...")

      blackbox_inputs = np.tile(lower_bounds, [blackbox_inputs.shape[0], 1]) + \
        blackbox_inputs * np.tile((upper_bounds - lower_bounds), [blackbox_inputs.shape[0], 1])
      if self_logger:
        self_logger.debug("FAST: Computing blackbox outputs...")

      # The code below is needed to handle the case when black box returns input as strings
      blackbox_outputs = _form_correct_blackbox_outputs(blackbox=blackbox._evaluate, inputs=blackbox_inputs, size_x=blackbox.size_x(), size_f=blackbox.size_f())

      if self_logger:
        count_finite = np.count_nonzero(np.isfinite(blackbox_outputs))
        if count_finite < blackbox_outputs.size:
          self_logger.warn('FAST: the method may be inaccurate because %.2f%% of the responses are invalid (NaN or Infinite).' % ((100. * (blackbox_outputs.size - count_finite) / blackbox_outputs.size),))

      if self_logger:
        self_logger.debug("FAST: Finished computing blackbox outputs.")

      if current_curve == 0:
        all_stdev = np.zeros(blackbox_outputs.shape[1])
        part_stdev_ti = np.zeros(blackbox_outputs.shape[1])
        part_stdev_i = np.zeros(blackbox_outputs.shape[1])

      # Save generated samples
      sample['inputs'] = blackbox_inputs
      sample['outputs'] = blackbox_outputs

      if self_logger:
        self_logger.debug("Computing Sobol indices...")
      for current_output in xrange(output_dimension):
        if _utils.is_constant(blackbox_outputs[:, current_output]):
          if showed_constant_warning[current_output] == 0:
            if self_logger:
              self_logger.warn("Data contains a constant output column (index: %s). Any feature score vs these output will be 0." \
                               % str(current_output))
            showed_constant_warning[current_output] = 1
          continue

        __watch(control.watcher, None)

        current_valid_points = np.isfinite(blackbox_outputs[:, current_output])
        if not current_valid_points.any():
          continue

        # Adding part of variance for the given curve
        current_total_variance = compute_portion_of_variance_fast_technique('total', blackbox_outputs[:, current_output],
                                                                            max_frequency, number_of_coeffs, number_of_runs, s)
        current_main_variance = compute_portion_of_variance_fast_technique('main', blackbox_outputs[:, current_output],
                                                                           max_frequency, number_of_coeffs, number_of_runs, s)

        part_stdev_ti[current_output] = np.hypot(part_stdev_ti[current_output], current_total_variance**0.5)
        part_stdev_i[current_output] = np.hypot(part_stdev_i[current_output], current_main_variance**0.5)

        # Computation of the total variance in the time domain.
        if current_valid_points.all():
          current_valid_points = slice(0, None)
        current_blackbox_outputs = blackbox_outputs[current_valid_points, current_output]
        if len(current_blackbox_outputs) > 1:
          all_stdev[current_output] = np.hypot(all_stdev[current_output], np.std(current_blackbox_outputs, ddof=1))
        __watch(control.watcher, None)

    # Computation of sensitivity indicies.
    all_variance = all_stdev**2 / actual_number_of_search_curves
    part_variance_i = part_stdev_i**2 / actual_number_of_search_curves
    part_variance_ti = part_stdev_ti**2 / actual_number_of_search_curves
    input_range_tolerance = _shared.parse_float(internal_options['/GTSDA/Private/ConstantTolerance'.lower()])
    for current_output in xrange(output_dimension):
      if all_variance[current_output] >= input_range_tolerance:
        sobol_total[current_output, current_input] = np.maximum(0.0, 1.0 - part_variance_ti[current_output] / all_variance[current_output])
        sobol_main[current_output, current_input] = np.maximum(0.0, part_variance_i[current_output] / all_variance[current_output])
      else:
        sobol_total[current_output, current_input] = 0.0
        sobol_main[current_output, current_input] = 0.0


  sobol_interactions = np.maximum(0.0, sobol_total - sobol_main)

  info_string['Total indices'] = sobol_total
  info_string['Main indices'] = sobol_main
  info_string['Interaction indices'] = sobol_interactions

  return info_string, sample

def get_other_frequences_fast_technique(number_of_frequences, max_complimentary_frequency):
  '''Algorithm for selection of a frequency
  set for the complementary group. Done
  recursively as described in:
  '''

  if number_of_frequences == 1:
    return np.array([1.0])

  complimentary_frequences = []
  step = np.floor(max(1.0, (max_complimentary_frequency - 0.999999) / (number_of_frequences - 1)))
  max_complimentary_frequency = 1.0 + step * (number_of_frequences - 1)
  current_frequency = max_complimentary_frequency

  counter = 0
  while counter != number_of_frequences:
    complimentary_frequences.append(np.floor(current_frequency))
    current_frequency -= step
    if current_frequency < 1:
      current_frequency = max_complimentary_frequency
    counter += 1

  return np.array(complimentary_frequences)

def compute_portion_of_variance_fast_technique(index_type, blackbox_output, max_frequency, number_of_coeffs, number_of_runs, s):
  '''Computes part of variance for the given curve
  '''
  spectrum_power = 0.

  if index_type == 'total':
    frequences_range = xrange(1, int(max_frequency))
  elif index_type == 'main':
    frequences_range = np.arange(max_frequency, max_frequency*number_of_coeffs+1, max_frequency)
  else:
    raise ValueError('FAST: Wrong Sobol index type!')

  valid_points = np.isfinite(blackbox_output)
  if not valid_points.any():
    return 0.
  elif not valid_points.all():
    mean_value = np.mean(blackbox_output[valid_points])
    blackbox_output = blackbox_output.copy()
    blackbox_output[~valid_points] = mean_value

  for frequency in frequences_range:
    angles = frequency * s
    spectrum_power = np.hypot(spectrum_power, np.dot(blackbox_output, np.cos(angles.reshape(-1))) / number_of_runs)
    spectrum_power = np.hypot(spectrum_power, np.dot(blackbox_output, np.sin(angles.reshape(-1))) / number_of_runs)

  return 2 * float(spectrum_power)**2

def compute_easi_technique(inputs=None, outputs=None, control=None, info_string=None):
  """Purpose: EASI Calculation of Sobol's sensitivity indices from given data (main and second order interactions can be computed this way)

  Implemented according to E. Plischke 2010 "An Effective Algorithm for Computing Global Sensitivity Indices (EASI)",
  Reliability Engineering & Systems Safety, 95(4), 354-360

  Based on matlab code written by Elmar Plischke, elmar.plischke@tu-clausthal.de

  Input:
  input_points - matrix of input vectors
  output_points - matrix of output vectors
  control - RankerParams object

  Returns: sensitivity indices (first order (main) and second order (pairwise interactions)(TODO))
           for input arguments x and output arguments y (per line)
  """

  number_of_points = inputs.shape[0]
  number_of_output_points = outputs.shape[0]

  if not number_of_output_points == number_of_points:
    raise Exception('EASI: Input/output sizes mismatch!')

  if info_string is None:
    info_string = form_common_info_string(control)

  # Divide-and-conquer FFT algorithms work much better the more factors the input length has.
  #Powers of 2 work especially well, whereas primes require slower implementations.
  # It is reasonable to cut off length of sample to a length, which is divisible by power of 2.
  max_sample_portion_cutoff = control.internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MaxSamplePortionCutoff'.lower()]
  power_of_2 = int(2**int(np.log2(len(inputs) * max_sample_portion_cutoff)))
  if power_of_2 > 0:
    inputs = inputs[:len(inputs) - (len(inputs) % power_of_2)]
    outputs = outputs[:len(outputs) - (len(outputs) % power_of_2)]

  number_of_points, input_dimension = inputs.shape
  number_of_output_points, output_dimension = outputs.shape

  active_inputs_idxs, constant_inputs_idxs = _utils.check_for_constant_columns(inputs)
  active_outputs_idxs, constant_outputs_idxs = _utils.check_for_constant_columns(outputs)

  sobol_indices_main = np.empty((output_dimension, input_dimension))
  sobol_indices_main.fill(np.nan)

  sobol_indices_main[constant_outputs_idxs, :] = 0
  sobol_indices_main[:, constant_inputs_idxs] = np.nan

  active_inputs = inputs[:, active_inputs_idxs]
  active_outputs = outputs[:, active_outputs_idxs]

  sorted_index = np.argsort(active_inputs, axis=0)

  sorted_inputs = np.array(active_inputs)
  for dimension in xrange(len(active_inputs_idxs)):
    sorted_inputs[:, dimension] = sorted_inputs[sorted_index[:, dimension], dimension]

  if np.mod(number_of_points, 2) == 0:
    # even no. of samples
    shuffle = list(np.arange(0, number_of_points - 1, 2)) + list(np.arange(number_of_points - 1, 0, -2))
  else:
    # odd no. of samples
    shuffle = list(np.arange(0, number_of_points, 2)) + list(np.arange(number_of_points - 2, 0, -2))

  # create quasi-periodic input of period 1
  # index_quasi_periodic = sorted_index[shuffle, :]

  yr = np.zeros((number_of_points, len(active_inputs_idxs) * len(active_outputs_idxs)))
  for current_output in xrange(len(active_outputs_idxs)):
    __watch(control.watcher, None)
    z = active_outputs[:, current_output]
    for current_input in xrange(len(active_inputs_idxs)):
      yr[:, current_output * len(active_inputs_idxs) + current_input] = z[sorted_index[shuffle, current_input]]

  max_harmonic_cutoff = control.internal_options['/GTSDA/Private/Ranker/Sobol/EASI/MaxHarmonicCutoff'.lower()]

  # look for resonances in the output
  fft_result = np.abs(np.fft.fft(yr, axis=0))

  spectrum = (fft_result * fft_result) / number_of_points

  part_variances_i = 2 * np.sum(spectrum[1:(max_harmonic_cutoff + 1), :], axis=0)
  variances = np.sum(spectrum[1:, :], axis=0)

  active_sobol_indices_main = part_variances_i / variances

  active_sobol_indices_main = np.reshape(active_sobol_indices_main, (len(active_outputs_idxs), len(active_inputs_idxs)))

  for output_dimension in xrange(len(active_outputs_idxs)):
    sobol_indices_main[active_outputs_idxs[output_dimension], active_inputs_idxs] = active_sobol_indices_main[output_dimension, :]

  variances = None

  info_string['Main indices'] = sobol_indices_main

  return info_string, sobol_indices_main, variances

def compute_csta_technique(budget=1000, blackbox=None, control=None, info_string=None, x_meta=None):
  """
  Description:
    Correlation Sensitivity Testing Algorithm
    implemented according to
    Graham Glen 2013 "Estimating Sobol sensitivity indices using correlations"
    Method D1

    Inputs:
      budget : wanted no. of sample points
      blackbox : p7core.da.Blackbox object
      control : RankerParams object

    Returns:
      info - dict containing main, total and total interactions indices
      sobol_indices - matrix of indices of type selected according to 'GTSDA/Ranker/Sobol/IndicesType' option
      sample - sample generated by the blackbox

    Other used variables/constants:
      primed and unprimed : two sets of independent realizations for each input values
      sample_size : number of vectors in primed (or unprimed)
      standardized_outputs : standardized output vectors from blackbox (g_j, g'_j, g_0, g'_0)
      correlation_coefficient_common : double estimate of Sobol main indices (c_dj = 1/2N * sum(g'_0 * g_j + g_0 * g'_j))
      correlation_coefficient_independent : double estimate of Sobol total indices (c_{d-j} = 1/2N * sum(g_0 * g_j + g'_0 * g'_j))
      spurious_correlation : the spurious correlation between primed and unprimed sets (p_j = 1/2N * sum(g_0 * g'_0 + g_j * g'_j))
      step_function : return result, where result[i] = 1 if and only if array[i] > 0, and result[i] = 0 else.
  """

  # define step-funtion
  def step_function(array):
    return 0.5 * (np.sign(array) + 1)

  def standardize(array):
    mean_value = np.mean(array, axis=0)
    standard = np.std(array, axis=0, ddof=1)
    zero_standard = standard >= np.finfo(float).eps

    rstandard = np.zeros_like(standard)
    rstandard[zero_standard] = 1. / standard[zero_standard]

    return np.subtract(array, mean_value[np.newaxis]) * rstandard[np.newaxis]

  if info_string is None:
    info_string = form_common_info_string(control)

  if not control is None:
    internal_options = control.internal_options
    options = control.options
    self_logger = control.logger
  else:
    internal_options, options, self_logger = None, None, None

  seed = int(options.get('GTSDA/Seed')) if options is not None else 0
  rnd = _random.RandomState(seed if _shared.parse_bool(options.get('GTSDA/Deterministic')) else None)

  if self_logger:
    self_logger.debug('Sobol indices computation technique CSTA was selected.')

  input_dimension = blackbox.size_x()
  input_bounds = blackbox.variables_bounds()
  lower_bounds = np.array(input_bounds[0])
  upper_bounds = np.array(input_bounds[1])
  output_dimension = blackbox.size_f()
  sample_size = budget // (2 * input_dimension + 2)

  if sample_size < 2:
    raise _ex.InvalidProblemError('CSTA: Budget is too small for computation of Sobol indices with CSTA method (need at least '+
                                  str(2 * (2 * input_dimension + 2)) + ' function calls with current options)'+
                                  ' try Screening indices instead (starts to work at (need at least '+
                                  str(3 * input_dimension) + ' function calls).')
  if sample_size < 50:
    if self_logger:
      self_logger.warn('CSTA: Computation budget is quite small for Sobol indices, computation results may be unreliable. ' +
                       ('The recommended budget is at least %d evaluations.' % (100 * (input_dimension + 1),)))

  main_indices = np.empty((output_dimension, input_dimension))
  total_indices = np.empty((output_dimension, input_dimension))
  interactions_indices = np.empty((output_dimension, input_dimension))
  main_indices.fill(np.nan)
  total_indices.fill(np.nan)
  interactions_indices.fill(np.nan)

  sample = {}

  if self_logger:
    self_logger.debug('CSTA: %s calls to blackbox function would be performed' % str(sample_size * (2 * input_dimension + 2)))

  # generate blackbox inputs
  if self_logger:
    self_logger.debug("CSTA: Generating input sample...")

  generator = _gtdoe.Generator()

  generator.options.set('GTDoE/Technique', 'LHS')
  generator.options.set('GTDoE/Deterministic', options.get('GTSDA/Deterministic'))
  vars_type, catvars = [], []
  for i, x_meta_i in enumerate(x_meta or []):
    vars_type.append(x_meta_i.get("type", "Continuous"))
    levels = [_ for _ in x_meta_i.get("enumerators", [])]
    if levels:
      catvars.extend((i, levels))
  generator.options.set('GTDoE/CategoricalVariables', catvars)
  generator.options.set('/GTDoE/VariablesType', vars_type)

  # Note seed option is ignored if deterministic is false
  primed = (generator.generate(count=sample_size, bounds=(lower_bounds, upper_bounds), options={'GTDoE/Seed': seed})).points
  unprimed = (generator.generate(count=sample_size, bounds=(lower_bounds, upper_bounds), options={'GTDoE/Seed': seed + 1})).points
  del generator

  original_sample_size, sample_size = sample_size, min(len(primed), len(unprimed)) # in case of a discrete problem, the design size may be less than sample_size

  if sample_size < 2:
    raise _ex.InvalidProblemError('CSTA: Full factorial size of the problem (%d) is too small for computation of Sobol indices with CSTA method (need at least %d unique points).' % (sample_size, 2 * (2 * input_dimension + 2)))
  if sample_size < 50 and original_sample_size > 50 and self_logger:
    self_logger.warn('CSTA: Full factorial size of the problem is quite small for Sobol indices, computation results may be unreliable.')

  primed = primed[:sample_size]
  unprimed = unprimed[:sample_size]

  blackbox_inputs = np.append(primed, unprimed, axis=0)
  for j in xrange(input_dimension):
    blackbox_inputs = np.append(blackbox_inputs, np.concatenate((primed[:, :j], unprimed[:, j:j+1], primed[:, j+1:]), axis=1), axis=0)
    blackbox_inputs = np.append(blackbox_inputs, np.concatenate((unprimed[:, :j], primed[:, j:j+1], unprimed[:, j+1:]), axis=1), axis=0)

  # get outputs from blackbox
  if self_logger:
    self_logger.debug("CSTA: Computing blackbox outputs...")
  blackbox_outputs = _form_correct_blackbox_outputs(blackbox=blackbox._evaluate, inputs=blackbox_inputs, size_x=blackbox.size_x(), size_f=blackbox.size_f())
  if self_logger:
    self_logger.debug("CSTA: Finished computing blackbox outputs.")
  sample['inputs'] = blackbox_inputs
  sample['outputs'] = blackbox_outputs

  # delete realizations with nans or infs
  _, nan_list, inf_list = check_for_nans_and_infs(blackbox_outputs, control)

  # blackbox_outputs are (2 * input_dimension + 2) series of length sample_size.
  # The invalidation of the i-th point in the series must be propagated to all series.
  assert len(blackbox_outputs) == sample_size * (2 * input_dimension + 2)
  valid_points = ~np.logical_or(nan_list, inf_list).any(axis=1).reshape(-1, sample_size).any(axis=0)
  if not valid_points.all():
    blackbox_outputs = blackbox_outputs[np.tile(valid_points, (2 * input_dimension + 2))]
    sample_size = len(blackbox_outputs) // (2 * input_dimension + 2)

  if sample_size < 2:
    raise _ex.InvalidProblemError('CSTA: Number of realizations without Nan and Inf is too small.')

  if sample_size < 50 and self_logger:
    self_logger.warn('CSTA: Number of realizations without Nan and Inf is quite small, computation results may be unreliable.')

  def get_sobol_indices_experiment(blackbox_outputs, input_dimension, output_dimension, constant_to_tolerance):
    # standardize outputs
    standardized_outputs = [standardize(blackbox_outputs[j * sample_size : (j + 1) * sample_size]) for j in xrange(2 * input_dimension + 2)]
    variable_outputs = np.where(np.var(blackbox_outputs, axis=0) > constant_to_tolerance)[0]

    # calculate estimates for correlation coefficient (c_{dj} - correlation_coefficient_common and c_{d-j} - correlation_coefficient_independent)
    correlation_coefficient_common = np.zeros((output_dimension, input_dimension))
    correlation_coefficient_independent = np.zeros((output_dimension, input_dimension))
    for j in xrange(input_dimension):
      for i in variable_outputs:
        correlation_coefficient_common[i, j] = (np.dot(standardized_outputs[1][:, i], standardized_outputs[2 + 2 * j][:, i]) + \
                                                np.dot(standardized_outputs[0][:, i], standardized_outputs[3 + 2 * j][:, i])) / (2 * sample_size)
        correlation_coefficient_independent[i, j] = (np.dot(standardized_outputs[0][:, i], standardized_outputs[2 + 2 * j][:, i]) + \
                                                     np.dot(standardized_outputs[1][:, i], standardized_outputs[3 + 2 * j][:, i])) / (2 * sample_size)
    # calculate spurious correlation (p_j)
    spurious_correlation = np.zeros((output_dimension, input_dimension))
    for i in variable_outputs:
      spurious_correlation[i, :] = np.tile(np.dot(standardized_outputs[0][:, i], standardized_outputs[1][:, i]), (1, input_dimension))
      for j in xrange(input_dimension):
        spurious_correlation[i, j] = (spurious_correlation[i][j] + \
                                      np.dot(standardized_outputs[2 + 2 * j][:, i], standardized_outputs[3 + 2 * j][:, i])) / (2 * sample_size)

    main_indices = np.minimum(1.0, np.maximum(0.0, correlation_coefficient_common -
                                              spurious_correlation * step_function(correlation_coefficient_independent - 1.0 / 2)))
    total_indices = np.zeros((output_dimension, input_dimension))
    total_indices[variable_outputs] = np.minimum(1.0, np.maximum(0.0, 1.0 - correlation_coefficient_independent +
                                                                 spurious_correlation *
                                                                 step_function(correlation_coefficient_common - 1.0 / 2)))[variable_outputs]
    interactions_indices = np.maximum(0.0, total_indices - main_indices)

    # calculate second order indices
    second_main_indices = np.zeros((output_dimension, input_dimension, input_dimension))
    second_total_indices = np.zeros((output_dimension, input_dimension, input_dimension))
    correlation_coefficient_common_second = np.zeros((output_dimension, input_dimension, input_dimension))
    correlation_coefficient_independent_second = np.zeros((output_dimension, input_dimension, input_dimension))
    spurious_correlation_second = np.zeros((output_dimension, input_dimension, input_dimension))

    for i in variable_outputs:
      for j in xrange(input_dimension):
        for k in xrange(input_dimension):
          correlation_coefficient_common_second[i][j][k] = (np.dot(standardized_outputs[3 + 2 * k][:, i],
                                                                   standardized_outputs[2 + 2 * j][:, i]) +
                                                            np.dot(standardized_outputs[2 + 2 * k][:, i],
                                                                   standardized_outputs[3 + 2 * j][:, i])) / (2 * sample_size)
          correlation_coefficient_independent_second[i][j][k] = (np.dot(standardized_outputs[2 + 2* k][:, i],
                                                                        standardized_outputs[2 + 2 * j][:, i]) +
                                                                 np.dot(standardized_outputs[3 + 2 * k][:, i],
                                                                        standardized_outputs[3 + 2 * j][:, i])) / \
                                                                 (2 * sample_size)
          spurious_correlation_second[i][j][k] = (np.dot(standardized_outputs[2 + 2 * j][:, i], standardized_outputs[3 + 2 * j][:, i]) +
                                                  np.dot(standardized_outputs[2 + 2 * k][:, i], standardized_outputs[3 + 2 * k][:, i])) / \
                                                  (2 * sample_size)

    for i in variable_outputs:
      second_main_indices[i] = correlation_coefficient_common_second[i] - \
                               np.ones((input_dimension, 1)).dot(np.array([main_indices[i]])) - \
                               np.array([[ind] for ind in main_indices[i]]).dot(np.ones((1, input_dimension))) - \
                               spurious_correlation_second[i] * step_function(correlation_coefficient_independent_second[i] - 1.0 / 2)
      second_main_indices[i][np.diag_indices(input_dimension)] = main_indices[i]
      second_total_indices[i] = spurious_correlation_second[i] * step_function(correlation_coefficient_common_second[i] - 1.0 / 2) - \
                                correlation_coefficient_independent_second[i] + 1.
      second_total_indices[i][np.diag_indices(input_dimension)] = total_indices[i]
    second_main_indices = np.minimum(1.0, np.maximum(0.0, second_main_indices))
    second_total_indices = np.minimum(1.0, np.maximum(0.0, second_total_indices))

    return [total_indices, main_indices, interactions_indices, second_main_indices, second_total_indices]

  constant_to_tolerance = _shared.parse_float(internal_options['/GTSDA/Private/ConstantTolerance'.lower()])
  indices = get_sobol_indices_experiment(blackbox_outputs, input_dimension, output_dimension, constant_to_tolerance)

  total_indices = indices[0]
  main_indices = indices[1]
  interactions_indices = indices[2]
  second_main_indices = indices[3]
  second_total_indices = indices[4]

  if _shared.parse_bool(control.options.get('GTSDA/Ranker/VarianceEstimateRequired')):
    variances = np.zeros(np.array(indices[:3]).shape)
    bootstrap_size = internal_options['/GTSDA/Private/Ranker/Sobol/CSTA/BootstrapSize'.lower()]
    for i in range(bootstrap_size):
      __watch(control.watcher, None)
      pseudo_outputs_indices = rnd.randint(sample_size, size=sample_size)
      pseudo_outputs_indices = np.tile(pseudo_outputs_indices, (2 * input_dimension + 2))
      for j in range(2 * input_dimension + 2):
        pseudo_outputs_indices[j * sample_size:(j+1) * sample_size] += j * sample_size
      pseudo_outputs = blackbox_outputs[pseudo_outputs_indices, :]
      pseudo_indices = get_sobol_indices_experiment(pseudo_outputs, input_dimension, output_dimension, constant_to_tolerance)
      variances += (np.array(indices[:3]) - pseudo_indices[:3])**2
    variances = (variances / bootstrap_size)**0.5

    info_string['Variances'] = {'Total indices': variances[0], 'Main indices': variances[1], 'Interaction indices': variances[2]}

  info_string['Total indices'] = total_indices
  info_string['Main indices'] = main_indices
  info_string['Interaction indices'] = interactions_indices
  info_string['Second main indices'] = second_main_indices
  info_string['Second total indices'] = second_total_indices

  return info_string, sample

def compute_morris_screening(budget=1000, blackbox=None, control=None, info_string=None, x_meta=None):
  """Python implementation of the Morris screening method, inspired by the SALib implementation.

    Inputs:
      budget : wanted no. of sample points
      blackbox : p7core.da.Blackbox object
      control : required RankerParams object

    Returns:
      info - dict containing mu*, mu and sigma indices
      screening_indices - matrix of mu* screening indices
      sample - sample generated by the blackbox
  """
  if control is None:
    raise _ex.InternalError('Implementation error: compute_morris_screening() method requires valid RankerParams input parameter.')
  if info_string is None:
    info_string = form_common_info_string(control)

  internal_options = control.internal_options
  options = control.options
  self_logger = control.logger

  seed = int(options.get('GTSDA/Seed')) if options is not None else 0
  rnd = _random.RandomState(seed if _shared.parse_bool(options.get('GTSDA/Deterministic')) else None)

  if self_logger:
    self_logger.debug("Screening technique 'Morris screening' was selected.")

  input_dimension = blackbox.size_x()
  input_bounds = np.array(blackbox.variables_bounds())
  lower_bounds = input_bounds[0, :]
  upper_bounds = input_bounds[1, :]
  input_ranges = upper_bounds - lower_bounds
  output_dimension = blackbox.size_f()

  screening_indices = {}
  screening_indices['mu'] = np.empty((output_dimension, input_dimension))
  screening_indices['mu_star'] = np.empty((output_dimension, input_dimension))
  screening_indices['sigma'] = np.empty((output_dimension, input_dimension))
  screening_indices['mu'].fill(np.nan)
  screening_indices['mu_star'].fill(np.nan)
  screening_indices['sigma'].fill(np.nan)

  constant_inputs = []
  active_inputs = []
  input_range_tolerance = _shared.parse_float(internal_options['/GTSDA/Private/ConstantTolerance'.lower()])
  for current_input in xrange(input_dimension):
    if input_ranges[current_input] < input_range_tolerance:
      if self_logger:
        self_logger.warn("Data contains a constant input column (index: %s). It's feature score vs any output will be nan." % str(current_input))
      constant_inputs.append(current_input)
    else:
      active_inputs.append(current_input)

  if budget < len(active_inputs) + 1:
    raise _ex.InvalidProblemError('Morris screening: Budget is too small for computation of screening indices with Morris screening (need at least '+
                                  str(len(active_inputs) + 1) + ' function calls with current options)')

  if len(active_inputs) > 0:
    active_x_meta = [x_meta[i] for i in active_inputs] if x_meta else None
    blackbox_active_inputs = get_oat_sample(budget, input_bounds[:, active_inputs], control, rnd=rnd, x_meta=active_x_meta)
  else:
    #all inputs are constant
    if self_logger:
      self_logger.warn("All the input columns in the data are constant. All the feature scores will be set to nan.")

    return info_string, screening_indices['mu_star'], None, None

  blackbox_inputs = np.empty((blackbox_active_inputs.shape[0], input_dimension))
  blackbox_inputs.fill(np.nan)
  blackbox_inputs[:, active_inputs] = blackbox_active_inputs
  for constant_input in constant_inputs:
    blackbox_inputs[:, constant_input] = lower_bounds[constant_input]

  __watch(control.watcher, None)

  # todo : process deltas in case of categorical and discrete variables
  blackbox_outputs = _form_correct_blackbox_outputs(blackbox=blackbox._evaluate, inputs=blackbox_inputs, size_x=blackbox.size_x(), size_f=blackbox.size_f())

  non_numeric_found, _, _ = check_for_nans_and_infs(blackbox_outputs, control)

  sample = {}
  sample['inputs'] = blackbox_inputs
  sample['outputs'] = blackbox_outputs

  screening_indices = {}
  screening_indices['mu'] = np.empty((output_dimension, input_dimension))
  screening_indices['mu_star'] = np.empty((output_dimension, input_dimension))
  screening_indices['sigma'] = np.empty((output_dimension, input_dimension))

  screening_indices['mu'].fill(np.nan)
  screening_indices['mu_star'].fill(np.nan)
  screening_indices['sigma'].fill(np.nan)

  variances = None
  info_string['Variances'] = None

  # Nans or infs in sample so we throw warning
  if non_numeric_found and internal_options['/GTSDA/Private/NansAndInfsInBlackbox'.lower()] == 'raise':
    self_logger.warn("NaN's or Inf's are detected in the blackbox outputs. Results may be inaccurate!")

  for key in screening_indices:
    screening_indices[key][:, constant_inputs] = np.nan

  elementary_effect_meta = input_ranges[active_inputs]
  if not _shared.parse_bool(control.options.get('GTSDA/Ranker/NormalizeInputs')):
    elementary_effect_meta[:] = 0. # no scale

  if x_meta:
    for i, current_input in enumerate(active_inputs):
      if x_meta[current_input].get("type", "continuous").lower() == 'categorical':
        elementary_effect_meta[i] = -1. # distance is either 0 (no change) or 1 (changed)

  for current_output in xrange(output_dimension):
    if _utils.is_constant(blackbox_outputs[:, current_output]):
      for key in screening_indices:
        for current_input in active_inputs:
          screening_indices[key][current_output, current_input] = 0

    else:
      __watch(control.watcher, None)
      screening_indices_for_output = compute_screening_indices(blackbox_inputs[:, active_inputs], blackbox_outputs[:, current_output], elementary_effect_meta)

      for key in screening_indices:
        for idx, current_input in enumerate(active_inputs):
          screening_indices[key][current_output, current_input] = screening_indices_for_output[key][idx]

  # calculate variances
  if _shared.parse_bool(control.options.get('GTSDA/Ranker/VarianceEstimateRequired')):
    bootstrap_size = internal_options['/GTSDA/Private/Ranker/Sobol/Morris/BootstrapSize'.lower()]
    variances = np.empty((output_dimension, input_dimension, 3))
    variances.fill(np.nan)
    variances[:, active_inputs, :] = 0
    trajectory_length = blackbox_active_inputs.shape[1] + 1
    number_curves = blackbox_active_inputs.shape[0] // trajectory_length

    for _ in xrange(bootstrap_size):
      random_curves = rnd.randint(number_curves, size=number_curves)
      pseudo_outputs_indices = np.repeat(random_curves * trajectory_length, trajectory_length) + \
                               np.tile(np.arange(trajectory_length), number_curves)
      for current_output in xrange(output_dimension):
        __watch(control.watcher, None)
        pseudo_indices = compute_screening_indices(blackbox_inputs[pseudo_outputs_indices, :][:, active_inputs],
                                                   blackbox_outputs[pseudo_outputs_indices, current_output], elementary_effect_meta)
        for i, key in enumerate(('mu', 'mu_star', 'sigma')):
          variances[current_output, :, i][active_inputs] = np.hypot(variances[current_output, active_inputs, i], (screening_indices[key][current_output, active_inputs] - pseudo_indices[key]))
    variances = variances / np.sqrt(bootstrap_size)
    info_string['Variances'] = {'mu': list(list(row) for row in variances[:, :, 0]),
                                'mu_star': list(list(row) for row in variances[:, :, 1]),
                                'sigma': list(list(row) for row in variances[:, :, 2])}
    variances = variances[:, :, 1]

  info_string['mu_star'] = screening_indices['mu_star']
  info_string['mu'] = screening_indices['mu']
  info_string['sigma'] = screening_indices['sigma']

  return info_string, screening_indices['mu_star'], sample, variances

# Generate number_of_trajectories*(input_dimension + 1) x input_dimension matrix of Morris samples (OAT)
def get_oat_sample(budget, bounds, control, rnd=None, x_meta=None):
  input_dimension = bounds.shape[1]

  #grid_jump = int(control.options.get('GTSDA/Ranker/Screening/MorrisGridJump'))
  #number_of_levels = int(control.options.get('GTSDA/Ranker/Screening/MorrisGridLevels'))
  # number of levels can be different for different inputs.

  # number of intervals and grid jump are integer but we use float to avoid excessive type conversions
  number_of_intervals = np.empty((input_dimension,), dtype=float)
  number_of_intervals[:] = int(control.options.get('GTSDA/Ranker/Screening/MorrisGridLevels')) - 1

  for i, x_meta_i in enumerate(x_meta or []):
    enums_i = x_meta_i.get("enumerators")
    if enums_i:
      number_of_intervals[i] = len(enums_i) - 1
    elif str(x_meta_i.get("type", "continuous")).lower() == "integer":
      number_of_intervals[i] = min(number_of_intervals[i], bounds[1, i] - bounds[0, i] - 1)

  grid_jump = np.empty((input_dimension,), dtype=float)
  grid_jump[:] = int(control.options.get('GTSDA/Ranker/Screening/MorrisGridJump'))
  grid_jump = np.clip(np.minimum(grid_jump, np.floor(0.5 * number_of_intervals)) - 1., 0., np.inf)

  trajectory_length = input_dimension + 1
  number_of_trajectories = budget // trajectory_length

  if rnd is None:
    rnd = _random.RandomState()

  # orientation matrix B: lower triangular (1) + upper triangular (-1)
  B = np.ones([trajectory_length, input_dimension], dtype=int)
  B = 0.5 * (np.tril(B, -1) - np.triu(B))

  # grid step delta, and final sample matrix x
  delta_diag = np.diag((grid_jump + 1.) / number_of_intervals)

  x = np.empty([number_of_trajectories * trajectory_length, input_dimension])
  x.fill(np.nan)
  # Create N trajectories. Each trajectory contains D+1 parameter sets.
  # (Starts at a base point, and then changes one parameter at a time)
  for j in xrange(number_of_trajectories):
    # directions matrix DM - diagonal matrix of either +1 or -1
    DM = np.diag((rnd.randint(2, size=input_dimension) - 0.5) * 2.)

    # permutation
    perm = np.random.permutation(input_dimension)

    # starting point for this trajectory
    # random generation interval is half open so floor does not produce (number_of_intervals - grid_jump) value
    x_base = np.floor(rnd.random_sample(size=input_dimension) * (number_of_intervals - grid_jump)) / number_of_intervals

    x[j*trajectory_length:(j+1)*trajectory_length] = np.clip(np.dot((np.dot(B, DM[perm, :]) + 0.5), delta_diag) + x_base[np.newaxis, :], 0., 1.)

  # scale inputs / translate to enumerators or integers
  if x_meta:
    for i, x_meta_i in enumerate(x_meta):
      enums_i = x_meta_i.get("enumerators")
      if enums_i is not None:
        enums_i = np.array(enums_i, copy=_shared._SHALLOW)
        x[:, i] = enums_i[np.round(x[:, i] * (len(enums_i) - 1)).astype(int)]
      else:
        x[:, i] = x[:, i] * (bounds[1, i] - bounds[0, i]) + bounds[0, i]
        if str(x_meta_i.get("type", "continuous")).lower() == "integer":
          x[:, i] = np.round(x[:, i])
  else:
    x = x * (bounds[1] - bounds[0])[np.newaxis] + bounds[0][np.newaxis]

  return x

def compute_screening_indices(x, y, elementary_effect_meta):
  input_dimension = x.shape[1]
  if y.shape[0] != x.shape[0]:
    raise Exception('Wrong sample generated!')

  number_of_points = y.shape[0]
  trajectory_length = input_dimension + 1

  number_of_trajectories = number_of_points // trajectory_length

  y_invalid = np.logical_or(np.isnan(y), np.isinf(y))
  if not y_invalid.all():
    if y_invalid.any():
      # we'll modify y array so we should get its copy
      y = np.array(y, copy=True)
      # now replace invalid y with a last known valid y
      last_valid = y[np.logical_not(y_invalid)][0]
      for i, invalid in enumerate(y_invalid):
        if invalid:
          y[i] = last_valid
        else:
          last_valid = y[i]

    x = x.reshape(number_of_trajectories, trajectory_length, input_dimension)
    y = y.reshape(number_of_trajectories, trajectory_length)

    # The elementary effect is (change in output)/(change in input)
    # Each parameter has one EE per trajectory, because it is only changed once in each trajectory

    delta_x = x[:, 1:, :] - x[:, :-1, :]
    delta_y = y[:, 1:] - y[:, :-1]

    # negative value encodes "no distance", zero value encodes "no scale"
    if elementary_effect_meta is not None:
      for i, ee_scale in enumerate(elementary_effect_meta):
        if ee_scale < 0:
          delta_x[:, :, i] = np.not_equal(delta_x[:, :, i], 0.).astype(float)

    try:
      # We exploit the fact that there is only one non-zero element in each row of each submatrix, so submatrices are orthogonal (not orthonormal)
      a, b, c = np.nonzero(delta_x.swapaxes(1, 2))
      elementary_effect = (delta_y[a,c] / delta_x[a,c,b]).reshape(number_of_trajectories, input_dimension)
    except:
      # Just a safeguard in case there is more than one non-zero element in the string.
      elementary_effect = None

    if elementary_effect is None:
      elementary_effect = np.empty((number_of_trajectories, input_dimension))
      for i in range(number_of_trajectories):
        elementary_effect[i, :] = np.linalg.solve(delta_x[i], delta_y[i])

    # negative value encodes "no distance", zero value encodes "no scale"
    if elementary_effect_meta is not None:
      for i, ee_scale in enumerate(elementary_effect_meta):
        if ee_scale > 0:
          elementary_effect[:, i] *= ee_scale
  else:
    elementary_effect = np.empty([number_of_trajectories, input_dimension])
    elementary_effect.fill(np.nan)

  screening_indices = dict((index, [np.nan] * input_dimension) for index in ['mu', 'mu_star', 'sigma'])

  for j in range(input_dimension):
    screening_indices['mu'][j] = np.average(elementary_effect[:, j])
    screening_indices['mu_star'][j] = np.average(np.abs(elementary_effect[:, j]))
    screening_indices['sigma'][j] = np.std(elementary_effect[:, j])

  return screening_indices

def get_unique_values(points, values, unique_points):
  '''Get values for the given points.
  Input:
    points - matrix (np.array);
    values - matrix (np.array) with values for a given points;
    unique_points - matrix (np.array) with points under interest.
  Output: unique_values - list of values for each row of the unique_points.'''
  return [values[(points == unique_points[i]).all(axis=1)] for i in xrange(len(unique_points))]

def get_taguchi_scores(points, values, criteria='signal_to_noise', self_logger=None, watcher=None):
  '''Get Taguchi scores for a given sample (points, values) and given criteria.
  Input:
    points - matrix (np.array);
    values - matrix (np.array) with values for a given points;
    criteria - string with criteria name.
  Output:
    aggregated_values_range - matrix with scores.
  '''
  unique_points_indices = _utils.get_unique_rows_idxs(points)
  unique_points = points[unique_points_indices, :]

  dim = unique_points.shape[1]
  levels_number = np.array([np.unique(col).size for col in unique_points.T])
  count = unique_points.shape[0]
  level_sum = levels_number.sum()
  last_lower = (count * (dim - 1) * dim + (count - level_sum) * level_sum) * count / 2;

  J2 = 0
  for i in xrange(1, count):
    J2 += (((unique_points[i][np.newaxis] == unique_points[:i, :]) * levels_number[np.newaxis]).sum(axis=1)**2).sum()

  if last_lower < J2:
    self_logger.warn('Design "x" is not orthogonal! The results of Taguchi analysis can be inaccurate.')

  if values.ndim == 1:
    values = values.reshape(-1, 1)

  aggregated_values_range = np.empty((len(values[0]), len(points[0])))
  aggregated_values_range.fill(np.nan)
  for output_index in xrange(len(values[0])):
    __watch(watcher, None)
    if not np.all(values[:, output_index] > 0):
      if self_logger:
        self_logger.warn('All output values should be positive. It is not true for output #%d. ' %(output_index) +
                         'The results of Taguchi analysis can be inaccurate.')

    unique_values = get_unique_values(points, values[:, output_index], unique_points)
    is_multiple_values = [np.any(x != x[0]) for x in unique_values]

    if not np.all(is_multiple_values) and criteria == 'signal_to_noise':
      if not np.any(is_multiple_values):
        raise _ex.InvalidProblemError('There is only one unique measurement for all unique points. ' +
                                      'Taguchi analysis with "Signal_to_noise" method can\'t be performed.')
      unique_values = unique_values[is_multiple_values, :]
      unique_points = unique_points[is_multiple_values, :]
      if self_logger:
        self_logger.warn('There should be more than one measurement (and unique value) for ' + \
                         'each unique point form x for the "GTSDA/Ranker/Taguchi/Technique": "Signal_to_noise" to be accurate. ' + \
                         'It is not true for output #%d.' %output_index)

    aggregated_values = []
    if criteria == 'signal_to_noise':
      for current_values in unique_values:
        current_mean = np.mean(current_values)
        current_variance = np.var(current_values, ddof=1)
        intermediate_score = current_mean**2 / current_variance
        if intermediate_score > 0:
          aggregated_values.append(10 * np.log10(intermediate_score))
        else:
          aggregated_values.append(np.nan)
    elif criteria == 'minimum':
      for current_values in unique_values:
        intermediate_score = np.sum([x**2 for x in current_values]) / len(current_values)
        if intermediate_score > 0:
          aggregated_values.append(-10 * np.log10(intermediate_score))
        else:
          aggregated_values.append(np.nan)
    elif criteria == 'auto' or criteria == 'maximum':
      for current_values in unique_values:
        is_any_zeros = np.any([value == 0 for value in current_values])
        if is_any_zeros:
          intermediate_score = np.nan
        else:
          intermediate_score = np.sum([1 / (x**2) for x in current_values]) / len(current_values)

        if intermediate_score > 0:
          aggregated_values.append(-10 * np.log10(intermediate_score))
        else:
          aggregated_values.append(np.nan)
    aggregated_values = np.array(aggregated_values)

    for input_index, n_levels in enumerate(levels_number):
      if n_levels > 1:
        aggregated_values_range[output_index, input_index] = np.ptp([np.mean(aggregated_values[unique_points[:, input_index] == fixed_input]) for fixed_input in np.unique(unique_points[:, input_index])])

  return aggregated_values_range

def get_sample_for_taguchi(blackbox, budget, self_options, info_string, self_logger=None, x_meta=None):
  '''Generate sample for Taguchi analysis using blackbox.
  '''
  levels_number_option = 'GTSDA/Ranker/Taguchi/LevelsNumber'
  levels_number = _shared.parse_json(self_options.get(levels_number_option))
  if len(levels_number) not in (0, blackbox.size_x()) or any(_ < 0 for _ in levels_number):
    raise _ex.InvalidOptionValueError("Option %s=%s is not correct." % (levels_number_option, self_options.get(levels_number_option),))

  repeats_number = int(self_options.get('GTSDA/Ranker/Taguchi/RepeatsNumber'))
  if repeats_number > budget:
    raise _ex.InvalidOptionValueError("'GTSDA/Ranker/Taguchi/RepeatsNumber' should be not greater than 'budget' (%s > %s)." % (repeats_number, budget))
  elif (budget % repeats_number) != 0:
    self_logger.warn("'GTSDA/Ranker/Taguchi/RepeatsNumber' is not divider of 'budget'. Only %d points will be generated." % (budget // repeats_number))

  try:
    gen = _gtdoe.Generator()

    vars_type, catvars = [], []
    for i, x_meta_i in enumerate(x_meta or []):
      vars_type.append(x_meta_i.get("type", "Continuous"))
      levels = [_ for _ in x_meta_i.get("enumerators", [])]
      if levels:
        catvars.extend((i, levels))

    # We use bounds only because we must not evaluate responses
    result = gen.build_doe(blackbox=blackbox.variables_bounds(), count=(budget // repeats_number),
                           options={'GTDoE/Technique': 'OrthogonalArray',
                                    'GTDoE/OrthogonalArray/ArrayType': 'Orthogonal',
                                    'GTDoE/Seed': self_options.get('GTSDA/seed'),
                                    'GTDoE/Deterministic': self_options.get('GTSDA/Deterministic'),
                                    'GTDoE/MaxParallel': self_options.get('GTSDA/MaxParallel'),
                                    'GTDoE/CategoricalVariables': catvars,
                                    '/GTDoE/VariablesType': vars_type,
                                    'GTDoE/OrthogonalArray/LevelsNumber': levels_number,
                                    })
  except:
    exc_info = _sys.exc_info()
    _shared.reraise(exc_type=_ex.InvalidProblemError, exc_value=exc_info[1], exc_tb=exc_info[2])

  info_string['OrthogonalArraySummary'] = result.info['Generator']['Summary']
  if result.info['Generator']['Summary']['Output type'] != 'Orthogonal':
    _ex.InvalidProblemError("Failed to generate an Orthogonal Array for Taguchi analysis for a specified parameters. " +
                            "Try to precalculate Orthogonal design and use sample-based SDA.")
  blackbox_inputs = np.tile(result.solutions.x, [repeats_number, 1])
  if self_logger:
    self_logger.debug("Taguchi: Computing blackbox outputs...")
  blackbox_outputs = _form_correct_blackbox_outputs(blackbox=blackbox._evaluate, inputs=blackbox_inputs, size_x=blackbox.size_x(), size_f=blackbox.size_f())

  return info_string, blackbox_inputs, blackbox_outputs

def _filter_points(bounds, x, y):
  if bounds is None:
    return x, y

  # filter out points according to custom bounds
  bounds = _shared.as_matrix(bounds, shape=(2, x.shape[1]), name="'bounds' argument")
  active_points = np.logical_and(np.greater_equal(x, bounds[0].reshape(1, -1)).all(axis=1),
                                 np.less_equal(x, bounds[1].reshape(1, -1)).all(axis=1))
  return x[active_points], y[active_points]
