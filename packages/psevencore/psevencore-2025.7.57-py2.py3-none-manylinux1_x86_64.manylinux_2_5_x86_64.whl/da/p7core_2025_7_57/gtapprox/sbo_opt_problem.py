#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division, with_statement

import sys
import re
import time
import datetime
import ctypes as _ctypes
from contextlib import contextmanager
import numpy as np

from ..six import string_types, next, iterkeys
from ..six.moves import zip, range

from .smart_selection_utilities import CaseInsensitiveDict, AcceptableLevelWatcher, TrainingTimeWatcher, Hyperparameters, _merge_dicts, _lower_case_list, _get_ordered_list_of_techniques, _pretty_print_options, _LandscapeValidator, _get_aggregate_errors
from . import tpe
from .. import gtopt as _gtopt
from .. import exceptions as _ex
from .iterative_iv import _IterativeIV
from ..loggers import LogLevel
from .. import shared as _shared
from . import technique_selection
from . import build_manager as _build_manager
from .model import Model as _Model
from .utilities import _parse_dry_run


class _API(object):
  def __init__(self):
    self.__library = _shared._library
    self.copy_iv_info = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p,
                                          _ctypes.POINTER(_ctypes.c_void_p))(("GTApproxModelUnsafeCopyInternalValidationInfo", self.__library))
    self.extract_trend = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_void_p))(("GTApproxModelUnsafeExtractHDA", self.__library))


_api = _API()

@contextmanager
def _scoped_options(options):
  initial_options = dict((key, options[key]) for key in options)
  try:
    yield
  finally:
    remove_keys = [key for key in options if key not in initial_options]
    for key in remove_keys:
      del options[key]
    for key in initial_options:
      options[key] = initial_options[key]

def _get_default_options():
  default_options = CaseInsensitiveDict({
      # Make sure the initial values, which optimization starts with, are appropriate for all the cases, e.g.
      # do not set inititals GTApprox/GPType=Additive, GTApprox/GPPower=1 (combination has no sense and may be removed)

      # GBRT
      'GTApprox/GBRTMaxDepth': {'bounds': (1, 10), 'init_value': 5},
      'GTApprox/GBRTMinChildWeight': {'bounds': (1, 10), 'init_value': 2, 'type': 'Integer'},
      #'GTApprox/GBRTMinLossReduction': {'bounds': (0, 1), 'init_value': 0},
      #'GTApprox/GBRTNumberOfTrees': {'bounds': (1, 500), 'init_value': 50},
      #'GTApprox/GBRTShrinkage': {'bounds': (0.001, 0.5), 'init_value': 0.3},
      'GTApprox/GBRTSubsampleRatio': {'bounds': (0.1, 1), 'init_value': 0.8},
      'GTApprox/GBRTColsampleRatio': {'bounds': (0.1, 1), 'init_value': 0.8},

      # MoA
      'GTApprox/MoATechnique': {'bounds': ['RSM', 'GBRT', 'HDA'], 'init_value': 'RSM', 'type': 'Enum'},

      # RSM
      'GTApprox/RSMFeatureSelection': {'bounds': ['LS', 'RidgeLS', 'MultipleRidgeLS', 'StepwiseFit', 'ElasticNet'], 'init_value': 'LS', 'type': 'Enum'},
      # 'Interaction' is intentionally removed
      'GTApprox/RSMType': {'bounds': ['Linear', 'PureQuadratic', 'Quadratic'], 'init_value': 'Linear', 'type': 'Enum'},

      # GP, SGP, TGP
      'GTApprox/GPType': {'bounds': ['Additive', 'Wlp', 'Mahalanobis'], 'init_value': 'Wlp', 'type': 'Enum'},
      'GTApprox/GPLearningMode': {'bounds': ['Accurate', 'Robust'], 'init_value': 'Accurate', 'type': 'Enum'},
      'GTApprox/GPTrendType': {'bounds': ['None', 'Linear', 'Quadratic'], 'init_value': 'None', 'type': 'Enum'},
      'GTApprox/GPPower': {'bounds': [1.4, 1.7, 2.0], 'init_value': 2.0, 'type': 'Enum'},

      # SPLT
      'GTApprox/SPLTContinuity': {'bounds': ['C2', 'C1'], 'init_value': 'C2', 'type': 'Enum'},

      # It is optimizable option for all techniques in case of enum problem
      'GTApprox/OutputTransformation': {'bounds': ['none', 'lnp1'], 'init_value': 'none', 'type': 'Enum'},
  })

  return default_options

def _technique_objective_options(technique):
  ns = lambda x: 'GTApprox/' + x

  options_list = {
    'splt': [ns('SPLTContinuity')],
    'hda': [ns("HDAPhaseCount"), ns("HDAPMin"), ns("HDAPMax"), ns("HDAMultiMin"), ns("HDAMultiMax"),
            ns("HDAFDLinear"), ns("HDAFDSigmoid"), ns("HDAFDGauss"), ],
    'gp': [ns("GPTrendType"), ns('GPPower'), ns('GPType'), # ns('Heteroscedastic'),
           ns('GPLearningMode'), ],
    'sgp': [ns('GPPower'), ns('SGPNumberOfBasePoints'), ns('GPType'), # ns('Heteroscedastic'),
            ns('GPLearningMode'),],
    'tgp': [ns('GPPower'), ns('GPLearningMode')],
    'hdagp': [ns('GPPower'), ns('GPType'), # ns('Heteroscedastic'),
              ns('GPLearningMode'), ns("HDAPhaseCount"), ns("HDAPMin"), ns("HDAPMax"),
              ns("HDAMultiMin"), ns("HDAMultiMax"), ns("HDAFDLinear"), ns("HDAFDSigmoid"),
              ns("HDAFDGauss"), ],
    'ta': [ns('SGPNumberOfBasePoints'), # ns('TALinearBSPLExtrapolationRange'),
           ns('TALinearBSPLExtrapolation'), ns('TAModelReductionRatio')],
    'rsm': [ns('RSMType'), ns('RSMFeatureSelection'), # ns("RSMStepwiseFit/inmodel"),
            #ns("RSMStepwiseFit/penter"), ns("RSMStepwiseFit/premove"),
            ns("RSMElasticNet/L1_ratio"),],
    'ita': [ns('TALinearBSPLExtrapolation'), #ns("TALinearBSPLExtrapolationRange"),
            ns('TAModelReductionRatio'), ],
    'moa': re.compile(r'GTApprox/MoA.+', re.I),
    'gbrt': [ns("GBRTNumberOfTrees"), ns("GBRTMaxDepth"), ns("GBRTShrinkage"), ns("GBRTMinLossReduction"),
             ns("GBRTSubsampleRatio"), ns("GBRTColsampleRatio"), ns("GBRTMinChildWeight"), ],
    #'pla': [],
    #'tbl': [],
  }
  return options_list.get(technique.lower(), [])

def _technique_adaptive_accelerator(n_models_magnitude, technique, opt_options):
  # Here for each technique we set 5 values corresponding to accelerator levels from 1 to 5.
  # Each value is a magnitude of roughly estimated maximum number of elementary models that can be built
  # for the training sample on the given computational system within the specified time frame.
  n_models_magnitudes = {
    # Long-time techniques (considering options optimization)
    'moa':   [6, 5, 4, 3, 2],
    'hdagp': [6, 5, 4, 3, 2],
    'gp':    [6, 5, 4, 3, 2],
    # Moderate-time techniques
    'sgp':  [5, 4, 3, 2, 1],
    'gbrt': [5, 4, 3, 2, 1],
    'hda':  [5, 4, 3, 2, 1],
    # Fast techniques
    'rsm': [3, 2.5, 2, 1.5, 1],
    'tgp': [3, 2.5, 2, 1.5, 1],
    'ta':  [3, 2.5, 2, 1.5, 1],
    'ita': [3, 2.5, 2, 1.5, 1],
    # Instantaneous techniques
    'splt': [0],
    'pla':  [0],
    'tbl':  [0],
  }.get(technique, [0]) # by default set accelerator=1
  return np.abs(np.array(n_models_magnitudes) - n_models_magnitude).argmin() + 1

def _read_gtapprox_option(options_collection, option_name, emergency_default, gtapprox_options):
    try:
      if option_name in options_collection:
        return options_collection[option_name]
      return gtapprox_options.info(option_name)['OptionDescription']['Default']
    except:
      pass
    return emergency_default

def _prepare_technique_options(technique, fixed_options, opt_options, default_options, gtapprox_options):
  """
  Get correct opt_option and fixed_options, i.e.

      * Return default opt_options if None passed and remove fixed_options from opt_options
      * Raise exception if fixed_options and opt_options are conflicted
      * Set bounds for opt_options if not passed: use default from default_options or
        if option is not in default_options list use global option bounds
      * Set initial value for opt_options if not passed: use default from default_options
        (if it doesn't fit the bounds, then choose the closest bound) or mean of the bounds
      * Set option type ('Enum', 'Integer' or 'Continuous'): from default_options
        or from the true type of the option
  """

  def remove_technique_irrelevant_options(technique, options):
    relevant_options = _technique_objective_options(technique)

    if hasattr(relevant_options, 'match'):
      for option_name in list(options.keys()):
        if not relevant_options.match(option_name):
          options.remove(option_name)
    else:
      relevant_options = set(_.lower() for _ in relevant_options)
      for option_name in list(options.keys()):
        # Remove options which don't influence model (options of other techniques)
        if option_name.lower() not in relevant_options:
          options.remove(option_name)

  fixed_options = CaseInsensitiveDict(fixed_options if fixed_options is not None else {})
  if _shared.parse_bool(_read_gtapprox_option(fixed_options, "GTApprox/ExactFitRequired", False, gtapprox_options)) \
     and _read_gtapprox_option(fixed_options, "GTApprox/GPLearningMode", "auto", gtapprox_options).lower() == "auto":
    fixed_options["GTApprox/GPLearningMode"] = "Accurate"

  if fixed_options.get("GTApprox/RSMFeatureSelection", "auto").lower() == "auto":
    fixed_options.pop("GTApprox/RSMFeatureSelection", "auto")

  if 'GTApprox/Technique' not in fixed_options:
    fixed_options['GTApprox/Technique'] = technique

  # use default opt options if they are not provided
  if opt_options is None:
    opt_options = Hyperparameters(gtapprox_options, opt_options=default_options)
    remove_technique_irrelevant_options(technique, opt_options)
    opt_options = opt_options.difference(fixed_options)
    return fixed_options, opt_options

  # make copy of opt_options
  opt_options = Hyperparameters(gtapprox_options, opt_options.values, default_options, opt_options.is_user_defined)

  # find intersection between fixed options and options to be optimized. Raise an error
  intersection = opt_options.intersection(fixed_options)
  if intersection:
    if opt_options.is_user_defined:
      raise _ex.InvalidOptionsError('The same options are found in fixed_options and opt_options!')
    else:
      for option in intersection:
        opt_options.remove(option)

  remove_technique_irrelevant_options(technique, opt_options)

  return fixed_options, opt_options

def _is_init_value(values, problem):
  for key, value in zip(problem.variables_names(), values):
    value = ('[' + str(value) + ']') if problem.opt_options.get_true_type(key) == 'vector' else str(value)
    if str(problem.opt_options.get_init_value(key)).lower() != value.lower():
      return False
  return True

def _convert_variable_to_dict(values, keys, fixed_options, opt_options):
  """
  Convert array-like x to approx options
  """
  approx_options = CaseInsensitiveDict(fixed_options.copy())

  is_init_value = True
  for key, value in zip(keys, values):
    # option value can be list
    if opt_options.get_true_type(key) == 'vector':
      approx_options[key] = '[' + str(value) + ']'
      if str(opt_options.get_init_value(key)).lower() != approx_options[key].lower():
        is_init_value = False
    else:
      approx_options[key] = value
      if str(opt_options.get_init_value(key)).lower() != str(value).lower():
        is_init_value = False


  if 'GTApprox/HDAPmax' in approx_options:
    if 'GTApprox/HDAPmin' not in approx_options:
      approx_options['GTApprox/HDAPmin'] = approx_options['GTApprox/HDAPmax']
  elif 'GTApprox/HDAPmin' in approx_options:
    approx_options['GTApprox/HDAPmax'] = approx_options['GTApprox/HDAPmin']

  return approx_options, is_init_value


def _sort_techniques(techniques):
  """
  Sort techniques in the following order SPLT, TA, iTA, TGP, RSM, GP/SGP, GBRT, HDA, HDAGP, MoA.
  """
  correct_order = _get_ordered_list_of_techniques()
  return [_.lower() for _ in sorted(techniques, key=lambda x: correct_order.index(x.lower()))]


def _copy_iv_info(model_src, model_dst, logger, prefix=None):
  if not model_src or not model_dst:
    return

  errdesc = _ctypes.c_void_p()
  if not _api.copy_iv_info(model_dst._Model__instance, model_src._Model__instance, _ctypes.byref(errdesc)):
    try:
      _shared.ModelStatus.checkErrorCode(0, 'Failed to save Internal Validation info to the optimal model found.', errdesc)
    except _ex.GTException:
      e = sys.exc_info()[1]
      if logger:
        logger(LogLevel.WARN, _shared._safestr(e), prefix)
  else:
    model_dst._Model__cache = {}

class _IVModelComplexity(object):
  def __init__(self):
    self._complexity = []
    self._errors = []

  def update(self, new_complexity, new_error):
    if new_complexity is not None:
      self._complexity.append(new_complexity)
      self._errors.append(new_error)

  @property
  def complexity(self):
    if not self._complexity:
      return None
    elif len(self._complexity) == 1:
      return self._complexity[0]
    # transform errors to weight keeping it linear
    weights = np.array(self._errors)
    weights = weights.max() - weights + weights.min()
    weights = weights / (weights.min() + np.finfo(float).eps)
    weighted_complexity = np.dot(weights, self._complexity) / weights.sum()
    return int(np.round(weighted_complexity, 0))

def _extract_trend(model, logger, prefix=None):
  if not model:
    return None

  errdesc = _ctypes.c_void_p()
  model_handle = _api.extract_trend(model._Model__instance, _ctypes.byref(errdesc))
  if not model_handle:
    # note extract_trend may return null pointer even in normal (not an error) case
    exc_type, message = _shared._release_error_message(errdesc)
    if exc_type is not None and logger:
      logger(LogLevel.WARN, message, prefix)
    return None
  return _Model(handle=model_handle)

def _postprocess_single_model(model, job_id):
  if model is None:
    return None
  annotations = model.annotations
  annotations = dict((k, annotations[k]) for k in annotations)
  annotations["__job_id__"] = [job_id]
  return model.modify(annotations=annotations)

def _postprocess_models_dict(models):
  for data_id in models:
    for job_id in models[data_id]:
      models[data_id][job_id] = _postprocess_single_model(models[data_id][job_id], job_id)
  return models

def _make_job_prefix(comment, job_id, iv_round=None):
  items = []

  if comment:
    items.append(comment)

  if job_id:
    items.append("job %s" % job_id)

  if iv_round is not None:
    items.append("IV session %d" % iv_round)

  return ", ".join(items)

def _get_models(builder, logger, cleanup, prefix=None):
  fail_reason = None
  training_start = time.time()
  try:
    models = _postprocess_models_dict(builder._get_models(cleanup=cleanup))
  except _ex.UserTerminated:
    raise
  except BaseException:
    e = sys.exc_info()[1]
    fail_reason = _shared._safestr(e)
    models = None

    if logger:
      logger(LogLevel.WARN, 'Approximation failure: %s' % e, prefix)
  return models, fail_reason, training_start


def _get_iv_options(approx_options, approx_builder, sample_size, uploaded_samples_number=None):
  with _shared._scoped_options(problem=approx_builder, options=approx_options):
    options_manager = approx_builder.options
    iv_subsets, iv_rounds = technique_selection._read_iv_options_impl(iv_subsets=int(options_manager.get('GTApprox/IVSubsetCount')),
                                                                      iv_subset_size=int(options_manager.get('GTApprox/IVSubsetSize')),
                                                                      iv_rounds=int(options_manager.get('GTApprox/IVTrainingCount')),
                                                                      sample_size=sample_size, validate=True)

    if (uploaded_samples_number or 0) > 1:
      # We want to keep the same number of IV subsets for the existing subsamples
      # if the training sample has already been split (when call it from calc method).
      iv_subsets = uploaded_samples_number
      iv_rounds = min(iv_subsets, iv_rounds)

    return {'GTApprox/IVSeed': int(options_manager.get('GTApprox/IVSeed')),
            'GTApprox/IVSubsetCount': iv_subsets,
            'GTApprox/IVTrainingCount': iv_rounds,
            'GTApprox/IVSubsetSize': 0, # set the value to 'auto' explicitly to avoid possible conflicts with approx_options
            }

class SmartSelectionOptimizationProblemGeneric(object):
  def __init__(self, error_types=('RRMS',),
               opt_options=None, fixed_options=None, approx_builder=None,
               comment=None, logger=None, watcher=None):
    self.error_types = error_types
    self.errors = {}.fromkeys(error_types)
    self.opt_options = opt_options
    self.fixed_options = fixed_options
    self.approx_builder = approx_builder
    self.comment = comment
    self.__logger = logger
    self.__watcher = watcher

    self.__cache = []

    # set defaults
    self.evaluation_count = 0
    self.min_error = np.inf
    self.optimal_options = None
    self.optimal_model = None
    self.fail_reason = []
    self.data_id_list = []
    self._dry_run = None

    self.min_la_errors = None
    self.landscape_validator = None

    # information about IV session with the minimal objective error achieved
    self.optimal_iv_session = {'error': np.inf, # objective error
                               'model': None,  # model obtained on the training session
                               'la_errors': None, # optional landscape errors
                               'iv_model': None} # dummy model holding global IV info to save
    self.optimal_dummy_model = None

    self.external_objective_min = np.inf
    self.external_optimal_options = None
    self.objectives_defined = 0

    self.__mean_training_time = {'model': (0., 0), 'objective': (0., 0)}

    self.submitted_jobs = {} # dict containing job_id and data_ids of different IV rounds of the same model.

  def update_fixed_options(self, fixed_options):
    self.fixed_options = _merge_dicts(self.fixed_options, fixed_options, override=True)
    self._dry_run = None # clear cached value

  def set_absolute_minima(self, optimal_solution):
    if optimal_solution is None:
      self.external_objective_min = np.inf
      self.external_optimal_options = None
    else:
      self.external_objective_min = optimal_solution.min_error
      self.external_optimal_options = optimal_solution.optimal_options

  def set_acceptable_quality_level(self, acceptable_quality_level, call_watcher=False):
    if isinstance(self.__watcher, AcceptableLevelWatcher):
      self.__watcher.acceptable_level = acceptable_quality_level if acceptable_quality_level is not None else 0.
    elif acceptable_quality_level is not None:
      self.__watcher = AcceptableLevelWatcher(self, acceptable_quality_level, self.__watcher)
    if call_watcher and self.__watcher and not self.__watcher():
      raise _ex.UserTerminated()

  def set_dataset(self, x, y, weights, output_noise_variance, x_test, y_test, w_test, initial_model):
    self.x = x
    self.y = y
    self.x_test = _shared.as_matrix(x_test, name="'x_test' argument") if x_test is not None else None
    self.y_test = _shared.as_matrix(y_test, name="'y_test' argument") if y_test is not None else None
    self.w_test = _shared.as_matrix(w_test, shape=(1, self.x_test.shape[0]), name="'w_test' argument").reshape(-1) if w_test is not None and x_test is not None else None
    self.output_noise_variance = output_noise_variance
    self.weights = weights
    self.initial_model = initial_model

  def set_data_id_list(self, data_id_list):
    self.data_id_list = data_id_list

  @property
  def acceptable_quality_level(self):
    return self.__watcher.acceptable_level if isinstance(self.__watcher, AcceptableLevelWatcher) else None

  def update_training_time_estimate(self, last_training_time, training_type):
    mean_time, count = self.__mean_training_time[training_type]
    count += 1
    mean_time += (last_training_time - mean_time) / count
    self.__mean_training_time[training_type] = (mean_time, count,)

  @property
  def training_time_estimate(self):
    return self.__mean_training_time['model'][0]

  @property
  def objective_time_estimate(self):
    return self.__mean_training_time['objective'][0]

  @property
  def number_of_phases_estimate(self):
    return 0

  def cache_get(self, x):
    x = np.array(x)
    for key, value in self.__cache:
      if np.all(key == x):
        return value
    return None

  def cache_add(self, x, errors):
    self.__cache.append((np.array(x).copy(), errors))

  def cache_clear(self):
    self.__cache = []

  def get_logger(self):
    return self.__logger

  def _log(self, level, msg, prefix=None):
    if self.__logger:
      prefix = _shared.make_prefix(prefix)
      for s in msg.splitlines():
        self.__logger(level, prefix + s)

  @property
  def _technique(self):
    return self._read_fixed_option('GTApprox/Technique', 'auto').lower()

  @property
  def dry_run(self):
    if self._dry_run is None:
      with _shared._scoped_options(self.approx_builder, self.fixed_options):
        self._dry_run = _parse_dry_run(self.approx_builder.options)
    return self._dry_run

  def _read_fixed_option(self, option_name, emergency_default=None):
    return _read_gtapprox_option(self.fixed_options, option_name, emergency_default, self.approx_builder.options)

  def _read_estimated_p(self, model):
    if model.details.get('Technique', 'auto').lower() not in ("hda", "hdagp"):
      return None
    estimated_p = model.info.get('ModelInfo', {}).get('Builder', {}).get('Details', {}).get('/GTApprox/HDAEstimatedP', None)
    return None if estimated_p is None else int(estimated_p)

  def _update_parameters(self, model, target_error, iv_dummy_model, training_start, la_errors):
    # todo : should we scale training time by O( len(self.x)/len(iv.x) ) ?
    self.update_training_time_estimate(time.time() - training_start, 'model')

    if model:
      # save IV model for possible further use...
      errors = model.validate(self.x, self.y)
      target_error = _get_aggregate_errors(errors[self.error_types[0]])

      # We always store optimal IV solution for the 'terminated by user' case
      if _LandscapeValidator.better_landscape(self.optimal_iv_session['error'], self.optimal_iv_session['la_errors'], target_error, la_errors):
        self.optimal_iv_session['error'] = target_error
        self.optimal_iv_session['model'] = model
        self.optimal_iv_session['la_errors'] = la_errors
        self.optimal_iv_session['iv_model'] = iv_dummy_model # iv_dummy_model WILL have proper IV info after iv.save_iv(iv_dummy_model) will be executed

    return target_error

  def _calc_penalty(self, model):
    return 1.

  def calc(self, x, just_submit=False, alt_initial_model=None):
    error  = self._build_model_and_estimate_error(x=x, just_submit=just_submit, alt_initial_model=alt_initial_model)
    return None if isinstance(error, string_types) else error

  def _quick_validate_model_options(self, x, alt_initial_model):
    initial_options = self.approx_builder.options.values
    result, approx_options = False, None
    try:
      approx_options, _ = _convert_variable_to_dict(x, self.variables_names(), self.fixed_options, self.opt_options)

      has_test_sample = not self.x_test is None and not self.y_test is None
      technique = approx_options.get('GTApprox/Technique', 'Auto').lower()
      tensored_iv = technique in ['ta', 'tgp']

      tensor_factors = approx_options.get('GTApprox/TensorFactors', '[]')
      if isinstance(tensor_factors, string_types) and not _shared.parse_json(tensor_factors):
        if tensored_iv:
          approx_options['GTApprox/TensorFactors'] = _shared.parse_json(approx_options.get('//Service/CartesianStructure', '[]'))
        else:
          approx_options.pop('GTApprox/TensorFactors', None)
          approx_options['GTApprox/EnableTensorFeature'] = False

      self.approx_builder.options.reset()
      for key in initial_options:
        if key.startswith('/'):
          self.approx_builder.options.set(key, initial_options[key])
      self.approx_builder.options.set("/GTApprox/DryRun", "Quick")

      if alt_initial_model is None:
        alt_initial_model = None, tuple()
      initial_model = alt_initial_model[0] or self.initial_model

      # Use cross-validation error if no test data is provided
      if not has_test_sample:
        iv_dummy_model = _build_manager.DefaultBuildManager().build(self.x[:1], self.y[:1], {'GTApprox/Technique': 'TBL'}, None, None, None, None, None)
        iv_options = _get_iv_options(approx_options, self.approx_builder, len(self.x), len(self.data_id_list))
        with _shared._scoped_options(problem=self.approx_builder, options=approx_options):
          self.approx_builder.options.set(iv_options)
          iv = _IterativeIV(self.x, self.y, options=self.approx_builder.options.values,
                            outputNoiseVariance=self.output_noise_variance, weights=self.weights,
                            tensored=tensored_iv) # create IV iterator driver

        iv_initial_model = (_ for _ in (alt_initial_model[1] if initial_model is None else []))

        iv_models = []
        while iv.session_begin():
          try:
            model = self.approx_builder._build_simple(iv.x, iv.y, outputNoiseVariance=iv.outputNoiseVariance, weights=iv.weights,
                                                      options=iv.options.values, initial_model=next(iv_initial_model, initial_model),
                                                      silent=True)
            iv_models.append(model)
          except:
            model = None
          iv.session_end(model)
        iv.save_iv(iv_dummy_model)

        if iv_models:
          return True
      else:
        model = self.approx_builder._build_simple(self.x, self.y, options=approx_options, outputNoiseVariance=self.output_noise_variance,
                                                  weights=self.weights, initial_model=(initial_model or alt_initial_model[0]), silent=True)
        if model is not None:
          return True
    except:
      pass
    finally:
      # reset options in order to keep in model.info only those options related to the optimal technique
      self.approx_builder.options.reset()
      self.approx_builder.options.set(initial_options)

    if approx_options and self.__logger:
      prefix_message = 'Ignoring a set of parameters that are incompatible with a given initial model:' if initial_model else 'Ignoring an incompatible set of parameters:'
      self._log(LogLevel.INFO, prefix_message + "\n    " + ("\n    ".join(("%s=%s" % (a, b)) for a, b in zip(self.variables_names(), x)) or "<no variable parameters>"), self.comment)

    return False

  def _build_model_and_estimate_error(self, x, just_submit, alt_initial_model):
    if self.__watcher is not None and not self.__watcher():
      raise _ex.UserTerminated()

    initial_options = self.approx_builder.options.values
    force_terminate = False

    approx_options, is_init_value = _convert_variable_to_dict(x, self.variables_names(), self.fixed_options, self.opt_options)
    iv_requested = _shared.parse_bool(approx_options.pop('GTApprox/InternalValidation', False))

    target_error = None
    errors = self.cache_get(x)
    if errors is not None:
      # Returns target error
      return errors[0]

    if alt_initial_model is None:
      alt_initial_model = None, tuple()
    initial_model = alt_initial_model[0] or self.initial_model

    self.evaluation_count += 1 # increment evaluations number

    has_test_sample = not self.x_test is None and not self.y_test is None
    technique = approx_options.get('GTApprox/Technique', 'Auto').lower()
    estimated_p = None

    job_id = '%s_%d' % (technique, self.evaluation_count)

    if just_submit:
      self.submitted_jobs[job_id] = {'technique': technique, 'x': x, 'approx_options': approx_options,
                                      'is_init_value': is_init_value, 'has_test_sample': has_test_sample}

    fast_tech = len(self.x) < 10 or (int(approx_options.get('GTApprox/Accelerator', 1)) > 3 if technique in ['gp', 'sgp'] else technique not in ['auto', 'hda', 'hdagp', 'moa'])

    tensor_factors = approx_options.get('GTApprox/TensorFactors', '[]')
    if isinstance(tensor_factors, string_types) and not _shared.parse_json(tensor_factors):
      if technique in ['ta', 'tgp']:
        approx_options['GTApprox/TensorFactors'] = _shared.parse_json(approx_options.get('//Service/CartesianStructure', '[]'))
      else:
        approx_options.pop('GTApprox/TensorFactors', None)
        approx_options['GTApprox/EnableTensorFeature'] = False

    self._log(LogLevel.DEBUG, _pretty_print_options('Trying to build model with the following parameters:', approx_options))

    approx_options["//GTApprox/JobID"] = job_id
    approx_options["//GTApprox/JobVariables"] = _shared.write_json([[a, b] for a, b in zip(self.variables_names(), x)])

    try:
      self.approx_builder.options.reset()
      for key in initial_options:
        if key.startswith('/'):
          self.approx_builder.options.set(key, initial_options[key])

      # Use cross-validation error if no test data is provided
      objective_start = time.time()
      iv_dummy_model = None
      iv_models_list = []
      if not has_test_sample:
        iv_dummy_model = _build_manager.DefaultBuildManager().build(self.x[:1], self.y[:1], {'GTApprox/Technique': 'TBL'}, None, None, None, None, None)
        iv_dummy_model = _postprocess_single_model(iv_dummy_model, job_id)

        tensored_iv = technique in ['ta', 'tgp']

        iv_options = _get_iv_options(approx_options, self.approx_builder, len(self.x), len(self.data_id_list))

        if self.__logger and not fast_tech:
          if just_submit:
            self._log(LogLevel.INFO, 'Preparing job #%d for calculation of %s approximation error using internal validation...' %
                          (self.evaluation_count, self.error_types[0]), self.comment)
          else:
            self._log(LogLevel.INFO, 'Calculating %s approximation error using internal validation...' % self.error_types[0], self.comment)

        with _shared._scoped_options(problem=self.approx_builder, options=approx_options):
          self.approx_builder.options.set(iv_options)
          iv = _IterativeIV(self.x, self.y, options=self.approx_builder.options.values,
                            outputNoiseVariance=self.output_noise_variance, weights=self.weights,
                            tensored=tensored_iv) # create IV iterator driver
        if just_submit:
          self.submitted_jobs[job_id]['iv_options'] = iv.options.values

        round_index = 0
        report_session = False
        la_errors = []
        limited_time = np.isfinite(getattr(self.__watcher, 'time_limit', np.inf))
        iv_initial_model = (_ for _ in (alt_initial_model[1] if initial_model is None else []))
        iv_complexity_estimator = _IVModelComplexity()

        while not force_terminate and iv.session_begin():
          round_index += 1
          try:
            if not just_submit and self.__watcher is not None and (not self.__watcher() # avoid watcher calls if we are sending requests
                or getattr(self.__watcher, 'time_left', lambda: np.inf)() < self.training_time_estimate):
              # well, we are going to exceed time limit, so let's stop...
              raise _ex.UserTerminated()

            if self.__logger:
              if fast_tech and not report_session and self.training_time_estimate*round_index > 5:
                self._log(LogLevel.INFO, 'Calculating %s approximation error using internal validation (%d training sessions done so far)...' % (self.error_types[0], round_index - 1), self.comment)
                fast_tech = self.training_time_estimate < 5
                report_session = True
              elif not fast_tech and round_index > 1 and self.training_time_estimate < 2:
                self._log(LogLevel.INFO, 'Turning off training log because training is fast enough.', self.comment)
                fast_tech = True
                report_session = True

              if not fast_tech or report_session:
                ett_message = '' if not self.training_time_estimate else (' (estimated training time %s)' % datetime.timedelta(seconds=self.training_time_estimate))
                if not just_submit:
                  self._log(LogLevel.INFO, '\nThe cross validation training session #%d is started%s' % (round_index, ett_message), self.comment)

            job_comment = _make_job_prefix(self.comment, job_id, round_index)

            # submit job
            if just_submit:
              self.approx_builder.options.reset()
              self.approx_builder.options.set(approx_options)
              self.approx_builder._submit_job(self.data_id_list[round_index - 1], job_id, action='build',
                                              options=iv.options.values, comment=job_comment, initial_model=next(iv_initial_model, initial_model))
              self.submitted_jobs[job_id].setdefault('data_id_list', []).append(self.data_id_list[round_index - 1])
              model = None
            else:
              training_start = time.time()
              model = self.approx_builder._build_simple(iv.x, iv.y, outputNoiseVariance=iv.outputNoiseVariance, weights=iv.weights, comment=job_comment,
                                                        options=iv.options.values, initial_model=next(iv_initial_model, initial_model), silent=fast_tech)
              model = _postprocess_single_model(model, job_id)
              iv_models_list.append(model)

              la_errors.append(self.landscape_validator.calc_landscape_errors(model, self.error_types) if self.landscape_validator is not None else None)
              target_error = self._update_parameters(model, target_error, iv_dummy_model, training_start, la_errors[-1])
              iv_complexity_estimator.update(self._read_estimated_p(model), target_error)

          except _ex.UserTerminated:
            force_terminate = True
            model = None
          except BaseException:
            # I've got exception here because already there is job with the same data id and job id (ta_1)
            # Why all data ids are the same?!!! It's handled by the self.data_id_list list
            e = sys.exc_info()[1]
            self.fail_reason.append(_shared._safestr(e))

            model = None
          if self.__logger and (not fast_tech or report_session):
            if not fast_tech and not just_submit:
              self._log(LogLevel.INFO, '\n', self.comment)
            if not self.approx_builder.is_batch:
              self._log(LogLevel.INFO, 'The cross validation training session #%d is finished\n' % round_index, self.comment)
          iv.session_end(model)

        # safe IV results to approximator
        if not just_submit:
          errors, la_errors = self._save_iv_results(iv, iv_dummy_model, la_errors)
          estimated_p = iv_complexity_estimator.complexity
      else:
        if iv_requested:
          # if IV was requested then we should reserve some time for the final model IV
          iv_rounds = technique_selection._read_iv_options_impl(int(approx_options.get('GTApprox/IVSubsetCount', 0)),
                                                                int(approx_options.get('GTApprox/IVSubsetSize', 0)),
                                                                int(approx_options.get('GTApprox/IVTrainingCount', 0)),
                                                                self.x.shape[0], False)[1]
        else:
          iv_rounds = 0

        job_comment = _make_job_prefix(self.comment, job_id, None)

        if just_submit:
          self.approx_builder._submit_job(self.data_id_list[0], job_id, action='build',
                                          options=approx_options, comment=job_comment,
                                          initial_model=(initial_model or alt_initial_model[0]))
          self.submitted_jobs[job_id].setdefault('data_id_list', []).append(self.data_id_list[0])
          model = None
        else:
          training_start = time.time()
          model = self.approx_builder._build_simple(self.x, self.y, options=approx_options, outputNoiseVariance=self.output_noise_variance,
                                                    comment=job_comment, weights=self.weights, initial_model=(initial_model or alt_initial_model[0]),
                                                    silent=fast_tech)
          model = _postprocess_single_model(model, job_id)
          self.update_training_time_estimate((time.time() - training_start) * (1 + iv_rounds), 'model')
          la_errors = self.landscape_validator.calc_landscape_errors(model, self.error_types) if self.landscape_validator is not None else None
          if model is not None:
            errors = model._validate(self.x_test, self.y_test, self.w_test)
            estimated_p = self._read_estimated_p(model)
          elif self.__watcher is not None and not self.__watcher():
            raise _ex.UserTerminated()
          else:
            raise _ex.GTException("cannot build approximation")

      if not just_submit:
        target_error = self._update_results(x, approx_options, is_init_value, errors, technique, estimated_p,
                                              _postprocess_single_model(iv_dummy_model, job_id), objective_start,
                                              model, la_errors, iv_models_list)
    except _ex.UserTerminated:
      raise
    except BaseException:
      e = sys.exc_info()[1]
      self.fail_reason.append(_shared._safestr(e))
      self._log(LogLevel.WARN, 'Failed to calculate approximation error: %s' % e, self.comment if self.comment else '')
      return np.nan
    finally:
      # reset options in order to keep in model.info only those options related to the optimal technique
      self.approx_builder.options.reset()
      self.approx_builder.options.set(initial_options)

    if just_submit:
      return job_id

    self._postprocess(target_error, approx_options, force_terminate)
    return target_error

  def define_objectives(self, x, just_submit=False, alt_initial_model=None):
    return self.calc(x, just_submit, alt_initial_model=alt_initial_model)

  def define_objectives_immediate(self, x, just_submit=False, alt_initial_model=None):
    target_error = self._build_model_and_estimate_error(x, just_submit, alt_initial_model)
    if isinstance(target_error, string_types):
      models, fail_reason, training_start = _get_models(self.approx_builder, self._log, False, self.comment)
      target_error = self.pull_solution(models, fail_reason, training_start, target_errors_list=(target_error,))[0]
    return target_error

  def _save_iv_results(self, iv, iv_dummy_model, la_errors):
    iv.save_iv(iv_dummy_model)
    errors = iv_dummy_model.iv_info.get('Componentwise', None)
    if errors is None:
      nan_array = np.empty(self.y.shape[-1])
      nan_array[:] = np.nan
      errors = dict((error_type, nan_array.copy()) for error_type in self.error_types)

    landscape_errors  = [_.get("landscape") for _ in la_errors if _ is not None]
    landscape_errors  = [_ for _ in landscape_errors if _ is not None]
    if landscape_errors:
      aggregated_landscape_errors = {}
      for key in landscape_errors[0].keys():
        aggregated_landscape_errors[key] = np.mean(np.vstack([_[key] for _ in landscape_errors]), axis=0)
    else:
      aggregated_landscape_errors = None

    validation_errors = [_.get("validation") for _ in la_errors if _ is not None]
    validation_errors  = [_ for _ in validation_errors if _ is not None]
    if validation_errors:
      aggregated_validation_errors = np.mean(validation_errors, axis=0)
    else:
      aggregated_validation_errors = None

    return errors, ({"landscape": aggregated_landscape_errors, "validation": aggregated_validation_errors} if aggregated_landscape_errors or aggregated_validation_errors else None)

  def _update_results(self, x, approx_options, is_init_value, errors, technique, estimated_p, iv_dummy_model, objective_start, model, la_errors, iv_models_list):
    self.update_training_time_estimate(time.time() - objective_start, 'objective')

    errors = dict((error_type, errors[error_type]) for error_type in self.error_types)
    target_error = _get_aggregate_errors(errors[self.error_types[0]])

    self.cache_add(x, (target_error, la_errors))

    output_transform = approx_options.get('GTApprox/OutputTransformation', 'none')
    if not isinstance(output_transform, string_types):
      output_transform = output_transform[0]
    output_transform = output_transform.lower()

    if estimated_p is not None:
      if getattr(self, 'estimated_p', None) is None:
        self.estimated_p = {}
      if self.estimated_p.get(output_transform) is None:
        self.estimated_p[output_transform] = estimated_p

    if technique in ('hda', 'hdagp'):
      if getattr(self, 'hda_trend_model', None) is None:
        self.hda_trend_model = {}
      if self.hda_trend_model.get(output_transform) is None:
        trend_model = _extract_trend(model, self.get_logger())
        if trend_model is not None:
          self.hda_trend_model[output_transform] = trend_model, [_extract_trend(_, self.get_logger()) for _ in iv_models_list]

    if np.isfinite(target_error) and ((is_init_value and not np.isfinite(self.min_error)) or _LandscapeValidator.better_landscape(self.min_error, self.min_la_errors, target_error, la_errors)):
      # if something will go wrong we store initial option values as optimal
      self.min_error = target_error if np.isfinite(target_error) else np.inf
      self.min_la_errors = la_errors
      self.optimal_options = approx_options
      if estimated_p is not None:
        self.optimal_options['GTApprox/HDAPMin'] = estimated_p
        self.optimal_options['GTApprox/HDAPMax'] = estimated_p
      self.min_errors_all = dict((error_type, _get_aggregate_errors(errors[error_type])) for error_type in self.error_types)
      if not self.x_test is None and not self.y_test is None:
        self.optimal_model = model
      self.optimal_dummy_model = None if not iv_dummy_model or not iv_dummy_model.iv_info else iv_dummy_model

    return target_error

  def _postprocess(self, target_error, approx_options, force_terminate):
    if self.external_objective_min <= self.min_error:
      ui_report_min_error = self.external_objective_min
      ui_report_optimal_options = self.external_optimal_options
    else:
      ui_report_min_error = self.min_error
      ui_report_optimal_options = self.optimal_options

    ui_report_optimal_options = {} if ui_report_optimal_options is None else dict(((key, ui_report_optimal_options[key]) for key in ui_report_optimal_options if not key.startswith('//')))

    if np.isfinite(self.min_error):
      if self.__logger:
        self.__logger(LogLevel.DEBUG, 'New optimal set of parameters found:')
        for key in ui_report_optimal_options:
          self.__logger(LogLevel.DEBUG, '  %s = %s' % (key, ui_report_optimal_options[key],))

    if self.__logger:
      optimal_error = '' if not np.isfinite(self.min_error) else (' (optimal %.8g)' % ui_report_min_error)
      this_job_id = approx_options.get("//GTApprox/JobID", "Current")
      this_job_descr = _shared.parse_json(approx_options.get("//GTApprox/JobVariables"))
      if this_job_descr:
        prefix = "%s variables: " % this_job_id
        self._log(LogLevel.INFO, prefix + ("\n" + " "*len(prefix)).join(("%s=%s" % (a, b)) for a, b in this_job_descr), self.comment)
      self._log(LogLevel.INFO, '%s objective: %.8g%s' % (this_job_id, target_error, optimal_error), self.comment)

    watcher_argument = {'current error': target_error,
                        'current options': dict(((key, approx_options[key]) for key in approx_options if not key.startswith('//'))),
                        'optimal error': ui_report_min_error,
                        'optimal options': ui_report_optimal_options,
                        'error type': self.error_types[0],
                        'model': ('' if self.comment is None else self.comment)}
    if (self.__watcher is not None and not self.__watcher(watcher_argument)) or force_terminate:
      raise _ex.UserTerminated()

  @staticmethod
  def _job_id_key(job_id):
    try:
      return int(job_id.split('_')[-1])
    except:
      pass
    return job_id

  def pull_solution(self, models, fail_reason, objective_start, target_errors_list=None):
    limited_time = np.isfinite(getattr(self.__watcher, 'time_limit', np.inf))

    if fail_reason:
      self.fail_reason.append(fail_reason)

    if not models:
      models = {}

    received_target_errors = {}
    user_terminated = False
    submitted_jobs = self.submitted_jobs
    self.submitted_jobs = {}
    for job_id, job_data in submitted_jobs.items():
      try:
        iv_complexity_estimator = _IVModelComplexity()
        iv_dummy_model = None
        iv_models_list = []

        if not job_data['has_test_sample']:
          iv_dummy_model = _build_manager.DefaultBuildManager().build(self.x[:1], self.y[:1], {'GTApprox/Technique': 'TBL'}, None, None, None, None, None)
          iv_dummy_model = _postprocess_single_model(iv_dummy_model, job_id)

          iv = _IterativeIV(self.x, self.y, options=job_data['iv_options'],
                            outputNoiseVariance=self.output_noise_variance, weights=self.weights,
                            tensored=job_data['technique'] in ['ta', 'tgp']) # create IV iterator driver
          round_index = 0
          target_error = np.inf

          la_errors = []
          while iv.session_begin():
            data_id = job_data['data_id_list'][round_index]
            curr_model = models.get(data_id, {}).get(job_id)
            iv_models_list.append(curr_model)
            iv.session_end(curr_model)
            round_index += 1

            if curr_model is not None:
              # @todo : should I perform landscape analysis outside?
              la_errors.append(self.landscape_validator.calc_landscape_errors(curr_model, self.error_types) if self.landscape_validator is not None else None)
              target_error = self._update_parameters(curr_model, target_error, iv_dummy_model, objective_start, la_errors[-1])
              iv_complexity_estimator.update(self._read_estimated_p(curr_model), target_error)

          errors, la_errors = self._save_iv_results(iv, iv_dummy_model, la_errors)
          estimated_p = iv_complexity_estimator.complexity
          curr_model = None
        else:
          data_id = job_data['data_id_list'][0]
          curr_model = models.get(data_id, {}).get(job_id)
          if curr_model is None:
            # One of the models was not built. May be other models succeeded, so keep working but replace curr_model by dummy model for the consistency of errors.
            received_target_errors[job_id] = np.nan
            continue
          errors = curr_model._validate(self.x_test, self.y_test, self.w_test)
          la_errors = self.landscape_validator.calc_landscape_errors(curr_model, self.error_types) if self.landscape_validator is not None else None
          estimated_p = self._read_estimated_p(curr_model)

        target_error = self._update_results(job_data['x'], job_data['approx_options'], job_data['is_init_value'], errors, job_data['technique'],
                                            estimated_p, _postprocess_single_model(iv_dummy_model, job_id), objective_start, curr_model, la_errors, iv_models_list)
        self._postprocess(target_error, job_data['approx_options'], False)
        received_target_errors[job_id] = target_error
      except _ex.UserTerminated:
        # All hard jobs are already done so there is no reason to abort postprocessing.
        # Even if we've found good solution we could already have better solution
        user_terminated = True

    if user_terminated:
      # forward user terminated exception
      raise _ex.UserTerminated()

    if target_errors_list:
      return [received_target_errors.get(_, np.nan) if isinstance(_, string_types) else _ for _ in target_errors_list]
    return [received_target_errors.get(_, np.nan) for _ in sorted([_ for _ in received_target_errors], key=self._job_id_key)]


class SmartSelectionSBO(SmartSelectionOptimizationProblemGeneric, _gtopt.ProblemUnconstrained):
  def prepare_problem(self):
    self.init_x = []
    for option_name, option_value in self.opt_options.items():
      if option_value['type'] == 'Enum':
        continue

      self.init_x += [option_value['init_value']]
      self.add_variable(option_value['bounds'], name=option_name,
                        hints={'@GTOpt/VariableType': option_value['type']})

    self.add_objective(name=self.error_types[0], hints={'@GTOpt/EvaluationCostType': 'Expensive'})

  def define_objectives(self, x, just_submit=False, alt_initial_model=None):
    x = np.array(x, copy=_shared._SHALLOW)
    return self.define_objectives_batch((x[np.newaxis] if x.ndim == 1 else x), alt_initial_model=alt_initial_model)[0]

  def define_objectives_batch(self, x, alt_initial_model=None):
    errors = [None]*len(x)

    try:
      # In sequential mode calc() returns an error value.
      # In batch mode calc() can return cached error value or None if error evaluation has been delayed.
      errors = [self._build_model_and_estimate_error(point, just_submit=self.approx_builder.is_batch, alt_initial_model=alt_initial_model) for point in x]

      if not any(isinstance(_, string_types) for _ in errors):
        return errors

      # There are deferred evaluations. Build models and pull errors.
      models, fail_reason, training_start = _get_models(self.approx_builder, self._log, False, self.comment)
      return self.pull_solution(models, fail_reason, training_start, target_errors_list=errors)
    except _ex.UserTerminated:
      pass
    return [(None if isinstance(_, string_types) else _) for _ in errors]

  @property
  def number_of_phases_estimate(self):
    # Since training samples are not set yet we estimate the upper bound of number of phases
    _, max_n_evaluations = tpe.get_optimizer(self, np.inf, None, estimate_objective_time=False)
    return max_n_evaluations

class SmartSelectionEnum(SmartSelectionOptimizationProblemGeneric):
  def __init__(self, error_types=('RRMS',),
               opt_options=None, fixed_options=None, approx_builder=None,
               comment=None, logger=None, watcher=None):

    super(SmartSelectionEnum, self).__init__(fixed_options=fixed_options,
                                             opt_options=opt_options,
                                             error_types=error_types,
                                             approx_builder=approx_builder,
                                             comment=comment, logger=logger,
                                             watcher=watcher)

    # remove non-Enum options from opt_options
    for option_name in list(self.opt_options.keys()):
      if self.opt_options[option_name]['type'] != 'Enum':
        self.opt_options.remove(option_name)

    self.__variables_names = tuple([option_name for option_name in self.opt_options])
    self.options_grid = self.get_options_grid(*[self.opt_options.get_bounds(option_name) for option_name in self.opt_options])
    self.init_x = [self.opt_options.get_init_value(key) for key in self.opt_options]

  @staticmethod
  def get_options_grid(*levels_list):
    options_grid = np.array([levels_list[0] if levels_list else []], dtype=object)
    for factors in levels_list[1:]:
      options_grid = np.vstack((np.tile(options_grid, len(factors)), np.repeat(factors, options_grid.shape[1])))
    # convert to list to avoid errors with numpy arrays
    return options_grid.T.tolist()

  def variables_names(self):
    return self.__variables_names

  def get_opt_option_index(self, name, default=-1):
    for i, option_name in enumerate(self.__variables_names):
      if option_name.lower() == name.lower():
        return i
    return default

  def get_optimal_x(self):
    optimal_x = self.init_x
    if self.optimal_options is not None:
      optimal_x = [self.optimal_options.get(key) for key in self.opt_options]
    return [_.lower() if isinstance(_, string_types) else _ for _ in optimal_x]

  @property
  def number_of_phases_estimate(self):
    return len(self.options_grid)


class SmartSelectionMixed(SmartSelectionEnum):
  def __init__(self, error_types=('RRMS',),
               opt_options=None, fixed_options=None, approx_builder=None,
               comment=None, logger=None, watcher=None):

    # separate 'Enum' options from 'SBO' options
    self.sbo_options = CaseInsensitiveDict()
    sbo_init_values = []
    for option_name in opt_options:
      if opt_options[option_name]['type'] != 'Enum':
        self.sbo_options[option_name] = opt_options[option_name]
        sbo_init_values.append(opt_options[option_name]['init_value'])
    self.sbo_options = Hyperparameters(approx_builder.options, self.sbo_options)

    super(SmartSelectionMixed, self).__init__(fixed_options=fixed_options,
                                              opt_options=opt_options,
                                              error_types=error_types,
                                              approx_builder=approx_builder,
                                              comment=comment, logger=logger,
                                              watcher=watcher)
    self.init_x += sbo_init_values

    self.dependen_options_values = CaseInsensitiveDict({'ElasticNet': 'GTApprox/RSMElasticNet/L1_ratio'})

  @property
  def number_of_phases_estimate(self):
    return len(self.options_grid)

class SmartSelectionOptimizer(object):
  "This class provides a simple interface for optimizing hyperparameters of specific GTApprox technique"
  def __init__(self, x, y, x_test=None, y_test=None, w_test=None, error_types=('RRMS',),
               techniques=('auto',), opt_options=None, fixed_options=None, accelerator_options=None,
               approx_builder=None, output_noise_variance=None, comment=None, weights=None, initial_model=None,
               landscape_analyzer=None, restricted_x=None, logger=None, watcher=None,
               categorical_inputs_map=None, categorical_outputs_map=None):
    from .builder import Builder as _Builder
    x, y, output_noise_variance, comment, weights, initial_model = _Builder._preprocess_parameters(x, y, output_noise_variance, comment, weights, initial_model)
    _, restricted_x = _Builder._preprocess_restricted_points(x.shape[1], None, restricted_x)

    if accelerator_options is None:
      from .smart_selection import _get_default_accelerator_options
      accelerator_options = _get_default_accelerator_options()

    self.accelerator_options = accelerator_options
    self.techniques = [str(_).lower() for _ in techniques]
    self.__logger = logger
    self.__watcher = TrainingTimeWatcher(self.accelerator_options.get('TimeLimit', 0), watcher)
    self.fixed_options = []
    self.opt_options = []
    self.iv = False
    self.fail_reasons = []
    self.resolve_output_transform = False
    self.comment = comment
    self.elementary_model_time = 0

    self.categorical_inputs_map = categorical_inputs_map
    self.categorical_outputs_map = categorical_outputs_map

    if approx_builder is not None:
      x_nan_mode, y_nan_mode = None, None
    else:
      keep_x_nan = approx_builder.options.get("GTApprox/Technique").lower() == "gbrt" or self.techniques == ["gbrt"]
      x_nan_mode = _Builder._read_x_nan_mode(approx_builder.options.get("GTApprox/InputNanMode"), keep_x_nan)
      y_nan_mode = approx_builder.options.get("GTApprox/OutputNanMode")

    x_test, y_test, w_test = _Builder._preprocess_test_sample(x.shape[1], y.shape[1], x_test, y_test, w_test, x_nan_mode, y_nan_mode)

    self.sample = {'x': x, 'y': y, 'weights': weights, 'tol': output_noise_variance,
                   'x_test': x_test, 'y_test': y_test, 'w_test': w_test,
                   'restricted_x': restricted_x,}
    self.initial_model = initial_model
    self.landscape_analyzer = landscape_analyzer

    self.__external_watcher = watcher
    self.__approx_builder = approx_builder

    self._process_options(fixed_options, opt_options, approx_builder.options)
    has_test_sample = not x_test is None and not y_test is None

    tensor_structure = approx_builder.options.get('GTApprox/TensorFactors')
    approx_builder.options.set('GTApprox/TensorFactors', self.fixed_options[0].get('GTApprox/TensorFactors', []))

    for options in self.fixed_options:
      options.setdefault('GTApprox/TensorFactors', approx_builder.options.get('GTApprox/TensorFactors'))
      options.setdefault('//Service/CartesianStructure', approx_builder.options.get('//Service/CartesianStructure'))
    approx_builder.options.set('GTApprox/TensorFactors', tensor_structure)

    effective_shape = self._truncate_options_bounds(approx_builder.options, x, y, has_test_sample, output_noise_variance, weights, initial_model)

    if error_types[0].lower() == 'rrms':
      rrms_issue = ""
      if effective_shape[2] < y.shape[1]:
        rrms_issue = "Constant output columns detected"
      elif has_test_sample:
        y_test_max = np.max(y_test, axis=0)
        y_test_min = np.min(y_test, axis=0)
        y_test_eps = np.fabs(np.vstack((y_test_max, y_test_min))).max(axis=0) * np.finfo(float).eps
        if not ((y_test_max - y_test_min) > y_test_eps).all():
          rrms_issue = 'Constant output columns detected in the test sample'

      if rrms_issue:
        error_types = ['RMS'] + error_types[1:]
        self._log(LogLevel.WARN, '%s: switching objective error type from RRMS to %s' % (rrms_issue, error_types[0]), comment)

        if 'AcceptableQualityLevel' in self.accelerator_options:
          # update acceptable quality level
          level_scale = np.std(y, axis=0)
          if np.any(level_scale == 0.):
            # for constant columns set epsilon-based error level
            y_min_abs = np.abs(np.min(y, axis=0))
            y_max_abs = np.abs(np.max(y, axis=0))
            level_scale[level_scale == 0.] = np.max((y_min_abs, y_max_abs, np.ones(np.shape(y_max_abs))), axis=0)[level_scale == 0.] * np.sqrt(np.finfo(float).eps)

          old_quality_level = self.accelerator_options['AcceptableQualityLevel']
          new_quality_level = np.median(level_scale * old_quality_level)

          self.accelerator_options = CaseInsensitiveDict(self.accelerator_options) # make a copy for safe modifications
          self.accelerator_options['AcceptableQualityLevel'] = new_quality_level
          self._log(LogLevel.WARN, 'Acceptable quality level is changed to [%s]<=%g (was [RRMS]<=%g)' % (error_types[0], new_quality_level, old_quality_level), comment)

    self.optimization_problems = []
    for i, technique in enumerate(self.techniques):
      if np.any(np.equal(effective_shape, (1, 0, 0))):
        # Degenerated sample detected - there is no need in any kind of optimization
        self.opt_options[i] = Hyperparameters(self.opt_options[i].gtapprox_options)
      if technique == 'gbrt' and self.opt_options[i]:
        optimization_problem = SmartSelectionSBO
      elif technique == 'rsm' and 'GTApprox/RSMElasticNet/L1_ratio' in self.opt_options[i]:
        optimization_problem = SmartSelectionMixed
      else:
        optimization_problem = SmartSelectionEnum

      problem = optimization_problem(fixed_options=self.fixed_options[i],
                                     opt_options=self.opt_options[i], error_types=error_types,
                                     approx_builder=approx_builder,
                                     comment=comment, logger=self.__logger, watcher=self.__watcher)
      problem.set_acceptable_quality_level(self.accelerator_options['AcceptableQualityLevel'])
      self.optimization_problems.append(problem)

  def _log(self, level, msg, prefix=None):
    if self.__logger:
      prefix = _shared.make_prefix(prefix)
      for s in msg.splitlines():
        self.__logger(level, prefix + s)

  def _process_options(self, fixed_options, opt_options, gtapprox_options):
    default_options = {}
    default_options.update(_get_default_options())
    default_options = CaseInsensitiveDict(default_options)

    if opt_options is not None:
      opt_options = CaseInsensitiveDict(opt_options) # make copy and modify it
      is_user_defined = not opt_options.pop('//SmartSelection/HintsBasedOptions', True)
    else:
      is_user_defined = False

    if opt_options:
      opt_options = Hyperparameters(gtapprox_options, opt_options, default_options, is_user_defined)
    else:
      opt_options = None

    # Techniques must appear in the following order SPLT, TA, iTA, TGP, RSM, GP/SGP, GBRT, HDA, HDAGP, MoA.
    self.techniques = _sort_techniques(self.techniques)
    self.iv = False

    # Select pseudo-random seed in 'randomized' mode
    with _shared._scoped_options(self.__approx_builder, fixed_options):
      if not _shared.parse_bool(self.__approx_builder.options.get('GTApprox/Deterministic')):
        fixed_options['GTApprox/Deterministic'] = True
        fixed_options['GTApprox/Seed'] = np.random.randint(1, np.iinfo(np.int32).max)
      if not _shared.parse_bool(self.__approx_builder.options.get('GTApprox/IVDeterministic')):
        fixed_options['GTApprox/IVDeterministic'] = True
        fixed_options['GTApprox/IVSeed'] = np.random.randint(1, np.iinfo(np.int32).max)

      output_transform = _shared.parse_output_transformation(self.__approx_builder.options.get("GTApprox/OutputTransformation"))
      self.resolve_output_transform = (output_transform.lower() == "auto" if isinstance(output_transform, string_types) else any(_.lower() == "auto" for _ in output_transform))

      # Vary OutputTransformation value if the corresponding hint is set True
      try_output_transformations = self.resolve_output_transform and self.accelerator_options.get('TryOutputTransformations', False)
      if try_output_transformations and not isinstance(output_transform, string_types):
        active_output = self.__approx_builder.options.values.get("//ComponentwiseTraining/ActiveOutput", None)
        if active_output is not None:
          try_output_transformations = (output_transform[int(active_output)].lower() == "auto")
      self.accelerator_options['TryOutputTransformations'] = try_output_transformations

    # process technique specific options
    for technique in self.techniques:
      fixed_options_technique, opt_options_technique = _prepare_technique_options(technique, fixed_options, opt_options,
                                                                                  default_options, gtapprox_options)
      # It is optimizable option for all techniques in case of enum problem
      if self.accelerator_options.get('TryOutputTransformations', False):
        option_name = 'GTApprox/OutputTransformation'
        opt_options_technique.update({option_name: default_options[option_name]})
      self.fixed_options += [fixed_options_technique]
      self.opt_options += [opt_options_technique]
      self.iv |= _shared.parse_bool(fixed_options_technique.get('GTApprox/InternalValidation', False))

  def _get_adaptive_accelerator(self, time_limit, techniques, opt_options):
    if self.elementary_model_time == 0:
      return [{} for _ in techniques]

    n_models_magnitude = np.log10((np.finfo(float).eps + time_limit) / self.elementary_model_time)
    accelerators = [_technique_adaptive_accelerator(n_models_magnitude, technique, opt_options) for technique in techniques]
    self._log(LogLevel.DEBUG, 'Setting accelerator values for candidate techniques to fit the time limit (%d sec) ...' % time_limit)

    options_list = []
    for technique, accelerator in zip(techniques, accelerators):
      options_list.append({
        'GTApprox/Accelerator': int(accelerator),
        '//Service/ElementaryModelTime': self.elementary_model_time,
        '//Service/IndividualTimeLimit': np.ceil(time_limit * int(accelerator) / sum(accelerators)),
      })
      self._log(LogLevel.DEBUG, ' - %s technique accelerator set to %d with time limit %d sec' % (technique, accelerator, options_list[-1]['//Service/IndividualTimeLimit']))

    return options_list

  def _truncate_options_bounds(self, gtapprox_options, x, y, has_test_sample=False,
                               output_noise_variance=None, weights=None,
                               initial_model=None):
    """
    Truncate options bounds (set of possible values) according to sample size and input dimension
    """

    self._log(LogLevel.DEBUG, 'Preprocessing optimization parameters')

    def remove_technique(index, reason):
      self._log(LogLevel.DEBUG, '  %s technique will not be used: %s' % (technique_selection._get_technique_official_name(self.techniques[index]), reason))
      del self.techniques[index]
      del self.opt_options[index]
      del self.fixed_options[index]

    # remove inapplicable techniques
    x_tol = _shared.parse_json(self.fixed_options[0].get('GTApprox/InputsTolerance', "[]"))
    if len(x_tol) != 0:
      x_tol = np.array(x_tol, dtype=float).reshape((-1,))

    time_limit = getattr(self.__watcher, 'time_limit', np.inf)
    accelerator = int(self.fixed_options[0].get('GTApprox/Accelerator', 1))

    # read whether technique was set manually by user
    manual_technique = [_.get('GTApprox/Technique', 'auto').lower() for _ in self.fixed_options]
    manual_technique = manual_technique[0] if (manual_technique and manual_technique[0] != 'auto' and all(_ == manual_technique[0] for _ in manual_technique[1:])) else None

    if manual_technique == 'gbrt':
      x_nan_mode = self.fixed_options[0].get('GTApprox/InputNanMode', "ignore")
      if x_nan_mode == "ignore":
        x_nan_mode = "preserve"
    else:
      x_nan_mode = self.fixed_options[0].get('GTApprox/InputNanMode', "raise")

    sample = technique_selection._SampleData(x, y, output_noise_variance, weights, [], x_tol,
                          {'x': x_nan_mode,
                           'y': self.fixed_options[0].get('GTApprox/OutputNanMode', "raise")})
    sample_size, x_dim, f_dim = sample.effective_shape

    if self.opt_options[0].is_user_defined:
      return sample.effective_shape

    checklist = technique_selection.TechniqueSelector(gtapprox_options).checklist

    i = 0
    while i < len(self.techniques):
      gtapprox_options.reset()
      gtapprox_options.set(self.fixed_options[i])
      if not has_test_sample:
        # IV feasibility is required if no test sample is given
        gtapprox_options.set('GTApprox/InternalValidation', True)
      try:
        current_technique = self.techniques[i].lower()
        checklist[current_technique](sample, gtapprox_options, initial_model)
        i += 1
      except BaseException:
        e = sys.exc_info()[1]
        self.fail_reasons.append('- %s technique cannot be used: %s' %
                                 (technique_selection._get_technique_official_name(self.techniques[i].lower()), e))
        remove_technique(i, e)

    if not self.techniques:
      raise _ex.InvalidOptionsError('There are no approximation techniques compatible with the specified options and/or hints.')

    if self.initial_model is not None:
      compatible_techniques = [_.lower() for _ in self.initial_model._compatible_techniques]

      for i in range(len(self.techniques), 0, -1):
        if self.techniques[i-1] not in compatible_techniques:
          remove_technique(i-1, 'the initial model is incompatible')
      if not self.techniques:
        raise _ex.InvalidOptionsError('There are no approximation techniques compatible with the initial model and specified options and/or hints.')

    if 1 == sample_size or 0 == x_dim:
      # Highly degenerated dataset - just use RSM or remove all optimization parameters if technique is user-defined.
      if not manual_technique:
        # remove all techniques and use linear RSM
        for i in range(len(self.techniques), 0, -1):
          remove_technique(i - 1, 'degenerated dataset detected')

        self.techniques.append('rsm')
        self.opt_options.append(Hyperparameters(gtapprox_options))
        # All service options are gone by now but we need smart selection flag for proper progress counting
        self.fixed_options.append(CaseInsensitiveDict({'GTApprox/Technique': 'RSM', '//Service/SmartSelection': True}))
      else:
        for i in range(len(self.opt_options)):
          self.opt_options[i] = Hyperparameters(self.opt_options[i].gtapprox_options)

      if 'rsm' in self.techniques:
        rsm_idx = self.techniques.index('rsm')
        self.fixed_options[rsm_idx]['GTApprox/RSMType'] = 'Linear'
        self.fixed_options[rsm_idx]['GTApprox/RSMFeatureSelection'] = 'LS'
        self.fixed_options[rsm_idx]['GTApprox/RSMMapping'] = 'None'

    elif sample_size <= (2*(x_dim+f_dim)+1):
      # Don't use highly nonlinear techniques if sample size is less or equal input dimension
      message = 'sample size is too small: %d <= %d' % (sample_size, (2*x_dim+1))
      # remove techniques only if they were not set manually
      if not manual_technique:
        for current_technique in [_ for _ in ['hda', 'hdagp', 'gp', 'sgp', 'moa', 'ta', 'ita', 'tgp'] if _ in self.techniques]:
          remove_technique(self.techniques.index(current_technique), message)

      # If sample_size <= x_dim use linear RSM with elastic_net
      if sample_size <= x_dim:
        message = 'sample size is too small: %d <= %d' % (sample_size, x_dim)

        # remove techniques only if they were not set manually
        if not manual_technique:
          for current_technique in (_ for _ in ['splt', 'pla'] if _ in self.techniques):
            remove_technique(self.techniques.index(current_technique), message)

        if 'rsm' in self.techniques:
          if not manual_technique and 'gbrt' in self.techniques:
            # dont use gbrt if we can use rsm
            remove_technique(self.techniques.index('gbrt'), message)
          rsm_idx = self.techniques.index('rsm')
          self.opt_options[rsm_idx] = Hyperparameters(self.opt_options[rsm_idx].gtapprox_options)
          self.fixed_options[rsm_idx]['GTApprox/RSMType'] = 'Linear'
          self.fixed_options[rsm_idx]['GTApprox/RSMFeatureSelection'] = 'ElasticNet'
          self.fixed_options[rsm_idx]['GTApprox/RSMElasticNet/L1_ratio'] = [0, 0.1, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0]

    # remove TGP technique if techniques for factors are proposed
    if 'tgp' in self.techniques and not manual_technique:
      tgp_idx = self.techniques.index('tgp')

      gtapprox_options.reset()
      gtapprox_options.set(self.fixed_options[tgp_idx])
      proposed_tensor_factors = _shared.parse_json(gtapprox_options.get('GTApprox/TensorFactors'))

      for i, factor in enumerate(proposed_tensor_factors):
        if isinstance(factor[-1], string_types) and factor[-1].lower() != 'auto':
          remove_technique(tgp_idx, '\'%s\' technique is proposed for tensor factor %s' % (factor[-1], factor[:-1]))
          break

    # remove iTA if sample has tensor stucture with 1d factors, use TA in this case
    if 'ita' in self.techniques and 'ta' in self.techniques and not manual_technique:
      ita_idx = self.techniques.index('ita')
      actual_tensor_factors = _shared.parse_json(self.fixed_options[ita_idx].get('//Service/CartesianStructure', []))
      if len(actual_tensor_factors) == x.shape[1]:
        remove_technique(ita_idx, 'full factorial structure is detected')

    # for TGP remove TrendType from opt_options
    if 'tgp' in self.techniques:
      tgp_idx = self.techniques.index('tgp')
      self.opt_options[tgp_idx].remove('GTApprox/GPTrendType')

      if 'gp' in self.techniques and not manual_technique:
        remove_technique(self.techniques.index('gp'), 'TGP is preferred technique')
      if 'sgp' in self.techniques and not manual_technique:
        remove_technique(self.techniques.index('sgp'), 'TGP is preferred technique')

    max_sgp_points_number = {4: 4000, 5: 2000}.get(accelerator, 8000)

    # only one GP technique will survive. And it should be recommended one
    if 'sgp' in self.techniques and not manual_technique:
      sgp_index = self.techniques.index('sgp')
      gtapprox_options.reset()
      gtapprox_options.set(self.fixed_options[sgp_index])
      base_points_number = int(gtapprox_options.get('GTApprox/SGPNumberOfBasePoints'))
      if sample_size < base_points_number:
        # sgp is not recommended. Switch it to GP somehow
        if 'gp' in self.techniques:
          remove_technique(sgp_index, 'SGP is not recommended because sample is too small: %d < %d' % (sample_size, base_points_number))
        else:
          self.techniques[sgp_index] = 'gp'

    if 'gp' in self.techniques and not manual_technique:
      gp_index = self.techniques.index('gp')
      gtapprox_options.reset()
      gtapprox_options.set(self.fixed_options[gp_index])
      base_points_number = int(gtapprox_options.get('GTApprox/SGPNumberOfBasePoints'))
      if sample_size >= base_points_number:
        # gp is not recommended. Switch it to SGP somehow
        if 'sgp' in self.techniques:
          remove_technique(gp_index, 'GP is not recommended because sample is too big: %d >= %d' % (sample_size, base_points_number))
        else:
          self.techniques[gp_index] = 'sgp'

    # remove sgp after all checks
    if 'sgp' in self.techniques and not manual_technique and sample_size > max_sgp_points_number:
      remove_technique(self.techniques.index('sgp'), 'SGP is not recommended because sample is too big: %d > %d' % (sample_size, max_sgp_points_number))

    if 'hdagp' in self.techniques and not manual_technique:
      hdagp_index = self.techniques.index('hdagp')
      gtapprox_options.reset()
      gtapprox_options.set(self.fixed_options[hdagp_index])
      max_sample_size_hdagp = int(gtapprox_options.get('/GTApprox/MaxSampleSizeForHDAGP'))
      min_sample_size_hda = int(gtapprox_options.get('/GTApprox/MinSampleSizeForHDA'))
      if sample_size > max_sample_size_hdagp:
        remove_technique(hdagp_index, 'HDAGP is not recommended because sample is too big: %d >= %d' % (sample_size, max_sample_size_hdagp))
      elif accelerator >= 5 and sample_size < min_sample_size_hda:
        remove_technique(hdagp_index, 'HDAGP is not recommended because sample is too small (%d < %d) while acceleration level is %d' % (sample_size, min_sample_size_hda, accelerator))

    if 'moa' in self.techniques:
      if (accelerator > 3 and len(self.techniques) >= 3 and sample_size < 200):
        if not manual_technique:
          remove_technique(self.techniques.index('moa'), 'too slow while sample is reasonably small')

      if 'moa' in self.techniques:
        # set maximum number of clusters for MoA depending on sample size
        moa_idx = self.techniques.index('moa')
        gtapprox_options.reset()
        gtapprox_options.set(self.fixed_options[moa_idx])

        if 'GTApprox/MoATechnique' not in self.fixed_options[moa_idx]:
          moa_techniques = _lower_case_list(self.opt_options[moa_idx].get_bounds('GTApprox/MoATechnique'))
          speed_limits = {4: 1000, 5: 10000}
          valid_moa_techniques = []

          for moa_tech in moa_techniques:
            try:
              if moa_tech != 'auto':
                checklist[moa_tech](sample, gtapprox_options, None) # ignore initial model for MoA clusters
              if moa_tech == 'hda' and sample_size < speed_limits.get(accelerator, 100):
                continue # exclude 'hda' for small samples or high speed techs
              valid_moa_techniques.append(moa_tech)
            except BaseException:
              pass

          if valid_moa_techniques:
            self.opt_options[moa_idx].set_bounds('GTApprox/MoATechnique', valid_moa_techniques)
          elif not manual_technique:
            remove_technique(moa_idx, 'all internal MoA techniques are inapplicable')
          else:
            self.opt_options[moa_idx] = Hyperparameters(self.opt_options[moa_idx].gtapprox_options)
            self.fixed_options[moa_idx]['GTApprox/MoATechnique'] = 'Auto'

    # scale GBRTMinLossReduction to std of outputs
    if 'gbrt' in self.techniques:
      gbrt_idx = self.techniques.index('gbrt')
      if 'GTApprox/GBRTMinLossReduction' not in self.fixed_options[gbrt_idx]:
        self.fixed_options[gbrt_idx]['GTApprox/GBRTMinLossReduction'] = 1.e-5 * np.std(y)

      if 'GTApprox/GBRTColsampleRatio' in self.opt_options[gbrt_idx]:
        # Note we ignore binarization for simplicity reasons
        gbrt_col_ratio_min, gbrt_col_ratio_max = self.opt_options[gbrt_idx].get_bounds('GTApprox/GBRTColsampleRatio')
        gbrt_col_ratio_min = max(gbrt_col_ratio_min, 1. / np.shape(x)[1])
        gbrt_col_ratio_init = max(self.opt_options[gbrt_idx].get_init_value('GTApprox/GBRTColsampleRatio'), gbrt_col_ratio_min)
        self.opt_options[gbrt_idx].set_bounds('GTApprox/GBRTColsampleRatio', (gbrt_col_ratio_min, gbrt_col_ratio_max), init_value=gbrt_col_ratio_init)

      if 'GTApprox/GBRTSubsampleRatio' in self.opt_options[gbrt_idx]:
        gbrt_row_ratio_min, gbrt_row_ratio_max = self.opt_options[gbrt_idx].get_bounds('GTApprox/GBRTSubsampleRatio')
        gbrt_row_ratio_min = max(gbrt_row_ratio_min, 1. / sample_size)
        gbrt_row_ratio_init = max(self.opt_options[gbrt_idx].get_init_value('GTApprox/GBRTSubsampleRatio'), gbrt_row_ratio_min)
        self.opt_options[gbrt_idx].set_bounds('GTApprox/GBRTSubsampleRatio', (gbrt_row_ratio_min, gbrt_row_ratio_max), init_value=gbrt_row_ratio_init)

    # Don't use 'Interaction' and 'Quadratic' for RSM in high dimensional space
    if x_dim > 50:
      for i in range(len(self.techniques)):
        if 'GTApprox/RSMType' in self.opt_options[i]:
          rsm_type = _lower_case_list(self.opt_options[i].get_bounds('GTApprox/RSMType'))
          if 'interaction' in rsm_type:
            rsm_type.remove('interaction')
          if 'quadratic' in rsm_type:
            rsm_type.remove('quadratic')

          self.opt_options[i].set_bounds('GTApprox/RSMType', rsm_type)
    else:
      for i, curr_options in enumerate(self.opt_options):
        if 'GTApprox/RSMFeatureSelection' in curr_options and 'GTApprox/RSMElasticNet/L1_ratio' in curr_options:
          # if there are expensive techniques then remove L1_ratio from optimization
          if accelerator >= 3 and ('moa' in self.techniques or 'gbrt' in self.techniques):
            curr_options.remove('GTApprox/RSMElasticNet/L1_ratio')
          if accelerator >= 4:
            curr_options.remove('GTApprox/RSMElasticNet/L1_ratio')

    if np.isfinite(time_limit) and 'GTApprox/Accelerator' not in self.fixed_options[0]:
      try:
        options = dict(((k, self.fixed_options[0].get(k)) for k in self.fixed_options[0] if not k.startswith('/')))
        options['GTApprox/Technique'] = 'RSM'
        options['GTApprox/RSMType'] = 'Linear'
        elementary_model_time = time.time()
        self.__approx_builder._build_simple(x, y, options=options,
                                            outputNoiseVariance=output_noise_variance, weights=weights,
                                            comment=self.comment, initial_model=None, silent=True)
        self.elementary_model_time = time.time() - elementary_model_time
        self._log(LogLevel.DEBUG, 'Elementary model for the training sample given was built in %g seconds' % self.elementary_model_time)

        accelerator_options = self._get_adaptive_accelerator(time_limit, self.techniques, self.opt_options)
        for options, fixed_options in zip(accelerator_options, self.fixed_options):
          fixed_options.update(options)

      except:
        self._log(LogLevel.DEBUG, 'Failed to adjust accelerator: %s' % sys.exc_info()[1])

    return sample.effective_shape

  def _upload_original_data(self, original_data_id):
    uploaded_data_ids = {
      "original": {
        "train": original_data_id,
        "ordinal_iv": [],
      },
      "rsm": {
        "train": original_data_id,
        "iv": [],
        "optimization_step": [original_data_id],
      },
      "gbrt": {
        "train": original_data_id,
        "iv": [],
        "optimization_step": [original_data_id],
      },
    }

    build_manager = self.__approx_builder._get_build_manager()
    build_manager.submit_data(original_data_id, self.sample['x'], self.sample['y'],
                              outputNoiseVariance=self.sample['tol'], weights=self.sample['weights'],
                              restricted_x=self.sample['restricted_x'])

    optimize_iv = self.sample["x_test"] is None or self.sample["y_test"] is None

    if (self.iv or optimize_iv):
      if 'rsm' in self.techniques:
        # Since RSM is fast and smooth and robust it requires original data only
        rsm_options = self.fixed_options[self.techniques.index('rsm')]
        iv_options = _get_iv_options(rsm_options, self.__approx_builder, len(self.sample['x']))
        build_manager.submit_job(original_data_id, "make_iv_split", options=iv_options, tensored_iv=False, action='make_iv_split')
        uploaded_data_ids["rsm"]["iv"] = build_manager._make_iv_split_local(original_data_id, "make_iv_split", options=iv_options, tensored_iv=False, dry_run=True)
        uploaded_data_ids["rsm"]["optimization_step"] = uploaded_data_ids["rsm"]["iv"]
        uploaded_data_ids["original"]["ordinal_iv"] = uploaded_data_ids["rsm"]["iv"]
      if 'gbrt' in self.techniques:
        gbrt_options = self.fixed_options[self.techniques.index('gbrt')]
        iv_options = _get_iv_options(gbrt_options, self.__approx_builder, len(self.sample['x']))
        build_manager.submit_job(original_data_id, "make_iv_split_gbrt", options=iv_options, tensored_iv=False, action='make_iv_split')
        uploaded_data_ids["gbrt"]["iv"] = build_manager._make_iv_split_local(original_data_id, "make_iv_split_gbrt", options=iv_options, tensored_iv=False, dry_run=True)
        uploaded_data_ids["gbrt"]["optimization_step"] = uploaded_data_ids["gbrt"]["iv"]

    return {"rsm": self.sample, "gbrt": self.sample}, uploaded_data_ids

  def _upload_additional_data(self, training_samples, uploaded_data_ids):
    # note uploaded_data_ids are actually used only in batch mode
    build_manager = self.__approx_builder._get_build_manager()

    optimize_iv = self.sample["x_test"] is None or self.sample["y_test"] is None

    uploaded_data_ids["tensored"]= {"train": uploaded_data_ids["original"]["train"], "iv": []}
    uploaded_data_ids["mixed"] = {"train": uploaded_data_ids["original"]["train"], "iv": uploaded_data_ids["original"].get("ordinal_iv", [])}
    uploaded_data_ids["ordinary"] = {"train": uploaded_data_ids["original"]["train"], "iv": uploaded_data_ids["original"].get("ordinal_iv", [])}

    landscape_validator = None
    training_samples["tensored"] = self.sample
    training_samples["mixed"] = self.sample
    training_samples["ordinary"] = self.sample

    if self.sample['x'].shape[1] > 1 and self.accelerator_options.get('LandscapeAnalysis', False) \
       and self.sample['x'].shape[0] <= self.accelerator_options.get('LandscapeAnalysisThreshold', np.iinfo(int).max):
      # estimate effective x shape
      local_x = self.sample['x']
      local_eps = np.fabs(np.vstack((np.max(local_x, axis=0).reshape(1, -1), np.min(local_x, axis=0).reshape(1, -1)))).max(axis=0) * 2. * np.finfo(float).eps
      create_landscape_validator = np.count_nonzero(np.ptp(local_x, axis=0) > local_eps) > 1
    else:
      create_landscape_validator = False

    if create_landscape_validator:
      train_points_number = self.sample['x'].shape[0]
      test_points_number = train_points_number if optimize_iv else self.sample['x_test'].shape[0]
      # TODO take into account categorical inputs and outputs when analysing landscape and generating new points
      original_data_id = uploaded_data_ids["original"]["train"]
      build_manager.submit_job(original_data_id, 'landscape_analysis', action='landscape_analysis', \
                               extra_points_number=(train_points_number + test_points_number),
                               catvars=_shared.parse_json(self.fixed_options[0].get('GTApprox/CategoricalVariables', '[]')),
                               landscape_analyzer=self.landscape_analyzer)
      landscape_analyzer, imag_points = build_manager.get_landscape_analyzer()[original_data_id]['landscape_analysis']

      if imag_points is not None:
        xtra_x, xtra_y, xtra_w = imag_points["x"], imag_points["y"], imag_points["w"].flatten()
        training_samples["tensored"] = dict(self.sample.items())
        training_samples["ordinary"] = dict(self.sample.items())
        training_samples["mixed"] = dict(self.sample.items())
        uploaded_data_ids["ordinary"]["iv"] = []
        uploaded_data_ids["mixed"]["iv"] = []

        # additional landscape validator is not needed because it will be a part of test sample
        landscape_validator = _LandscapeValidator(landscape_analyzer, None, None, None) if not optimize_iv \
                         else _LandscapeValidator(landscape_analyzer, xtra_x, xtra_y, xtra_w)

        if any(_ not in ('ta', 'tgp', 'rsm') for _ in self.techniques):
          # split extra dataset to train and test part
          split_data_id = original_data_id + "_imag"
          build_manager.submit_data(split_data_id, xtra_x, xtra_y)
          build_manager.submit_job(split_data_id, 'split_sample', action='split_sample', train_test_ratio=0.5, seed=15313,
                                   categorical_inputs_map=self.categorical_inputs_map, categorical_outputs_map=self.categorical_outputs_map)
          train_indices, test_indices, _ = build_manager.get_split_sample()[split_data_id]["split_sample"]

          # Append train data to the train sample and upload it
          training_samples["mixed"] = {"x": np.vstack((self.sample["x"], xtra_x[train_indices])),
                                       "y": np.vstack((self.sample["y"], xtra_y[train_indices])),
                                       "weights": None, "tol": None, "x_test": None, "y_test": None, "w_test": None,
                                       "restricted_x": self.sample["restricted_x"]}

          if self.sample["tol"] is not None:
            training_samples["mixed"]["tol"] = np.empty(training_samples["mixed"]["y"].shape, dtype=float)
            training_samples["mixed"]["tol"][:] = np.nan
            training_samples["mixed"]["tol"][:self.sample["tol"].shape[0]] = self.sample["tol"]
          else:
            training_samples["mixed"]["weights"] = np.hstack(((self.sample["weights"].flatten() if self.sample["weights"] is not None else np.ones(self.sample["y"].shape[0])), xtra_w[train_indices]))

          if not optimize_iv:
            # Append test data to test sample (note tensored sample should use the same test dataset)
            training_samples["tensored"]["x_test"] = np.vstack((self.sample["x_test"], xtra_x[test_indices]))
            training_samples["tensored"]["y_test"] = np.vstack((self.sample["y_test"], xtra_y[test_indices]))
            training_samples["tensored"]["w_test"] = np.hstack(((self.sample["w_test"].flatten() if self.sample["w_test"] is not None else np.ones(self.sample["y_test"].shape[0])), xtra_w[test_indices]))
            training_samples["mixed"]["x_test"] = training_samples["ordinary"]["x_test"] = training_samples["tensored"]["x_test"]
            training_samples["mixed"]["y_test"] = training_samples["ordinary"]["y_test"] = training_samples["tensored"]["y_test"]
            training_samples["mixed"]["w_test"] = training_samples["ordinary"]["w_test"] = training_samples["tensored"]["w_test"]
          else:
            # _LandscapeValidator ctor is simple so just re-create it
            landscape_validator = _LandscapeValidator(landscape_analyzer, xtra_x[test_indices], xtra_y[test_indices], xtra_w[test_indices])

          uploaded_data_ids["mixed"]["train"] = original_data_id + "_ext"
          build_manager.submit_data(uploaded_data_ids["mixed"]["train"], training_samples["mixed"]['x'], training_samples["mixed"]['y'],
                                    outputNoiseVariance=training_samples["mixed"]['tol'], weights=training_samples["mixed"]['weights'],
                                    restricted_x=training_samples["mixed"]['restricted_x'])
        elif not optimize_iv:
          # Append xtra_x, xtra_y, xtra_w to the tensored test sample. Test sample is not uploaded so train data id is not modified
          training_samples["tensored"]["x_test"] = np.vstack((self.sample["x_test"], xtra_x))
          training_samples["tensored"]["y_test"] = np.vstack((self.sample["y_test"], xtra_y))
          training_samples["tensored"]["w_test"] = np.hstack(((self.sample["w_test"].flatten() if self.sample["w_test"] is not None else np.ones(self.sample["y_test"].shape[0])), xtra_w))
          training_samples["mixed"]["x_test"] = training_samples["ordinary"]["x_test"] = training_samples["tensored"]["x_test"]
          training_samples["mixed"]["y_test"] = training_samples["ordinary"]["y_test"] = training_samples["tensored"]["y_test"]
          training_samples["mixed"]["w_test"] = training_samples["ordinary"]["w_test"] = training_samples["tensored"]["w_test"]
      elif landscape_analyzer is not None:
        landscape_validator = _LandscapeValidator(landscape_analyzer, None, None, None)

    if build_manager.is_batch:
      if self.iv or optimize_iv:
        if any(_ not in ('ta', 'tgp') for _ in self.techniques) and not uploaded_data_ids["mixed"]["iv"]:
          iv_options = _get_iv_options(self.fixed_options[0], self.__approx_builder, len(training_samples["mixed"]["x"]))
          build_manager.submit_job(uploaded_data_ids["mixed"]["train"], "make_iv_split", options=iv_options, tensored_iv=False, action='make_iv_split')
          uploaded_data_ids["mixed"]["iv"] = build_manager._make_iv_split_local(uploaded_data_ids["mixed"]["train"], "make_iv_split", options=iv_options, tensored_iv=False, dry_run=True)
          if uploaded_data_ids["ordinary"]["train"] == uploaded_data_ids["mixed"]["train"]:
            uploaded_data_ids["ordinary"]["iv"] = uploaded_data_ids["mixed"]["iv"]

        if any(_ in ('gp', 'sgp', 'hdagp') for _ in self.techniques) and not uploaded_data_ids["ordinary"]["iv"]:
          iv_options = _get_iv_options(self.fixed_options[0], self.__approx_builder, len(training_samples["ordinary"]["x"]))
          build_manager.submit_job(uploaded_data_ids["ordinary"]["train"], "make_iv_split", options=iv_options, tensored_iv=False, action='make_iv_split')
          uploaded_data_ids["ordinary"]["iv"] = build_manager._make_iv_split_local(uploaded_data_ids["ordinary"]["train"], "make_iv_split", options=iv_options, tensored_iv=False, dry_run=True)

        if any(_ in self.techniques for _ in ('ta', 'tgp')):
          iv_options = _get_iv_options(self.fixed_options[0], self.__approx_builder, len(training_samples["tensored"]["x"]))
          build_manager.submit_job(uploaded_data_ids["tensored"]["train"], "make_iv_split_tensored", options=iv_options, tensored_iv=True, action='make_iv_split')
          uploaded_data_ids["tensored"]["iv"] = build_manager._make_iv_split_local(uploaded_data_ids["tensored"]["train"], "make_iv_split_tensored", options=iv_options, tensored_iv=True, dry_run=True)


      if optimize_iv:
        uploaded_data_ids["ordinary"]["optimization_step"] = uploaded_data_ids["ordinary"]["iv"]
        uploaded_data_ids["tensored"]["optimization_step"] = uploaded_data_ids["tensored"]["iv"]
        uploaded_data_ids["mixed"]["optimization_step"] = uploaded_data_ids["mixed"]["iv"]
      else:
        uploaded_data_ids["ordinary"]["optimization_step"] = [uploaded_data_ids["ordinary"]["train"]]
        uploaded_data_ids["tensored"]["optimization_step"] = [uploaded_data_ids["tensored"]["train"]]
        uploaded_data_ids["mixed"]["optimization_step"] = [uploaded_data_ids["mixed"]["train"]]

    return training_samples, uploaded_data_ids, landscape_validator

  def _flush_problems_queue(self, opt_data):
    if not opt_data.problems_queue:
      return False

    models, fail_reason, training_start = _get_models(self.__approx_builder, self._log, False, self.comment)

    user_terminated = False
    while opt_data.problems_queue:
      optimization_problem = opt_data.problems_queue.pop(0)
      try:
        optimization_problem.set_absolute_minima(opt_data.best_problem)
        optimization_problem.pull_solution(models, fail_reason, training_start)
      except _ex.UserTerminated:
        user_terminated = True
      finally:
        if opt_data.update_best(optimization_problem):
          if user_terminated and opt_data.best_problem.min_error < self.accelerator_options['AcceptableQualityLevel']:
            # Models are sorted in the complexity increasing order. So we implement early stop in case of target error achievement to avoid overtraining
            break

    return user_terminated

  def _select_output_transform(self, uploaded_data_ids):
    build_manager = self.__approx_builder._get_build_manager()

    data_id = uploaded_data_ids["original"]["train"]
    job_ids = []


    for i, optimization_problem in enumerate(self.optimization_problems):
      job_ids.append('select_output_transform_' + str(i))
      self._log(LogLevel.INFO, "Considering technique %s" % self.techniques[i], optimization_problem.comment)
      build_manager.submit_job(data_id, job_ids[-1], action='select_output_transform', options=optimization_problem.fixed_options, comment=optimization_problem.comment)

    output_transforms = build_manager.select_output_transform()[data_id]

    for job_id, optimization_problem in zip(job_ids, self.optimization_problems):
      optimization_problem.fixed_options["GTApprox/OutputTransformation"] = output_transforms[job_id]

  @staticmethod
  def get_tech_kind(technique):
    if technique in ('rsm', 'gbrt'):
      # These techniques use original data uploaded preliminarily
      return technique, False
    elif technique in ('ta', 'tgp'):
      return "tensored", True
    elif technique in ('hda', 'pla') or 'gp' in technique:
      return "ordinary", True
    else:
      return "mixed", True

  def solve(self):
    if not self.techniques:
      raise _ex.InvalidOptionsError('Cannot build model for the specified options and hints:\n%s' % '\n'.join(self.fail_reasons))

    opt_data = _OptimizationData()
    has_test_sample = self.sample['x_test'] is not None and self.sample['y_test'] is not None
    training_samples, uploaded_data_ids = self._upload_original_data("original_dataset")

    original_watcher = self.__approx_builder._set_watcher(self.__watcher)

    if self.resolve_output_transform:
      self._select_output_transform(uploaded_data_ids)

    try:
      prefer_linear_trend = True
      user_terminated = False
      tech_kind = None

      for i, optimization_problem in enumerate(self.optimization_problems):
        prev_tech_kind = tech_kind
        tech_kind, upload_additional_data = self.get_tech_kind(self.techniques[i])

        if upload_additional_data:
          if "landscape_validator" not in locals():
            training_samples, uploaded_data_ids, landscape_validator = self._upload_additional_data(training_samples, uploaded_data_ids)

            if opt_data.best_problem is not None:
              if has_test_sample and opt_data.best_problem.optimal_model is not None:
                updated_optimal_error = opt_data.best_problem.optimal_model._validate(training_samples["mixed"]["x_test"], training_samples["mixed"]["y_test"], training_samples["mixed"]["w_test"])
                opt_data.best_problem.min_error = _get_aggregate_errors(updated_optimal_error[opt_data.best_problem.error_types[0]])
                del updated_optimal_error

              if landscape_validator is not None:
                # try to calculate landscape errors for the optimal solution found
                opt_data.best_problem.landscape_validator = landscape_validator
                if opt_data.best_problem.optimal_model is not None:
                  opt_data.best_problem.min_la_errors = opt_data.best_problem.landscape_validator.calc_landscape_errors(opt_data.best_problem.optimal_model, opt_data.best_problem.error_types)
                elif opt_data.best_problem.optimal_iv_session['model'] is not None:
                  # minimal landscape errors cannot be calculated here because IV models are already lost
                  opt_data.best_problem.optimal_iv_session['la_errors'] = opt_data.best_problem.landscape_validator.calc_landscape_errors(opt_data.best_problem.optimal_iv_session['model'], opt_data.best_problem.error_types)
          optimization_problem.landscape_validator = landscape_validator

        sample = training_samples[tech_kind]
        optimization_problem.set_dataset(sample["x"], sample["y"], sample["weights"], sample["tol"],
                                         sample["x_test"], sample["y_test"], sample["w_test"], self.initial_model)
        if self.__approx_builder.is_batch:
          optimization_problem.set_data_id_list(uploaded_data_ids[tech_kind]["optimization_step"])

        if opt_data.problems_queue and (self.techniques[i] in ("moa",) or (self.techniques[i] == "hdagp" and not opt_data.hda_estimated_p) or prev_tech_kind != tech_kind):
          # Two major cases are here:
          # 1. HDAGP requres prior complexity estimation;
          # 2. In batch mode we can detect early abortion of training caused by target error achievement only at flushpoint. Otherwise training would not be deterministic.
          #    So we have to keep some trade off to detect target error achievement as soon as possible but keeping batch size large enough for efficient utilization of
          #    computational resources. Switching from tensor techniques to the ordinary ones is a good point because tensor techniques are fast. MoA is a good point because
          #    it always creates a lot of models so it keeps resources utilization at high level. Also there is some limitations considering MoA in local batch mode.
          #    Actually, we should not combine MoA with something else.
          user_terminated = self._flush_problems_queue(opt_data)
          if user_terminated:
            raise _ex.UserTerminated()

          remaining_techniques = self.techniques[i:]
          opt_options = [_.opt_options for _ in self.optimization_problems[i:]]
          time_limit = getattr(self.__watcher, 'time_left', lambda: np.inf)()
          accelerator_options = self._get_adaptive_accelerator(time_limit, remaining_techniques, opt_options)
          for options, problem in zip(accelerator_options, self.optimization_problems[i:]):
            problem.update_fixed_options(options)

        self._log(LogLevel.INFO, 'Trying to use %s technique\n' % self.techniques[i].upper(), optimization_problem.comment)

        optimization_problem.set_absolute_minima(opt_data.best_problem)

        batch_mode = bool(self.__approx_builder.is_batch) and self.techniques[i] not in ("rsm", "moa")

        if isinstance(optimization_problem, SmartSelectionSBO):
          seed = None
          if 'GTApprox/Deterministic' in self.fixed_options:
            deterministic = self.fixed_options['GTApprox/Deterministic']
          else:
            deterministic = _shared.parse_bool(optimization_problem.approx_builder.options.get('GTApprox/Deterministic'))

          if deterministic:
            seed = int(optimization_problem.approx_builder.options.get('GTApprox/Seed'))

          if 'GTApprox/OutputTransformation' in optimization_problem.opt_options:
            # Enum opt_options (like 'GTApprox/OutputTransformation') are ignored when solving SBO problem
            # Since init_x values are already filtered, use fixed_options to specify required OutputTransformation
            default_transform = optimization_problem.approx_builder.options.get('GTApprox/OutputTransformation')
            original_transform = optimization_problem.fixed_options.get('GTApprox/OutputTransformation', default_transform)
            original_transform = original_transform.lower() if isinstance(original_transform, string_types) else [_.lower() for _ in original_transform]
            test_transforms = [_ for _ in ("lnp1", "none") if _ not in original_transform]
          else:
            test_transforms = []

          time_limit = int(optimization_problem._read_fixed_option('//Service/IndividualTimeLimit', 0)) or getattr(self.__watcher, 'time_left', lambda: np.inf)()
          time_limit /= len(test_transforms) + 1
          optimizer, max_n_evaluations = tpe.get_optimizer(optimization_problem, time_limit, seed)
          if not optimizer:
            self.accelerator_options['GTOpt/MaximumExpensiveIterations'] = max_n_evaluations
            optimizer = self._solve_sbo

          optimizer(optimization_problem)
          if test_transforms:
            with _scoped_options(optimization_problem.fixed_options):
              for current_transform in test_transforms:
                optimization_problem.cache_clear()
                optimization_problem.fixed_options['GTApprox/OutputTransformation'] = current_transform
                optimizer(optimization_problem)
          batch_mode = False


        elif self.techniques[i] == 'rsm':
          prefer_linear_trend = self._solve_rsm(optimization_problem)
          if 'GTApprox/OutputTransformation' in optimization_problem.opt_options:
            original_transform = optimization_problem.opt_options.get_init_value('GTApprox/OutputTransformation')
            original_transform = original_transform.lower() if isinstance(original_transform, string_types) else [_.lower() for _ in original_transform]
            test_transforms = [_ for _ in ("lnp1", "none") if _ not in original_transform]
            index = [_ for _ in optimization_problem.opt_options].index('GTApprox/OutputTransformation')
            for current_transform in test_transforms:
              optimization_problem.cache_clear()
              optimization_problem.init_x[index] = current_transform
              self._solve_rsm(optimization_problem)

        elif self.techniques[i] == 'hdagp':
          self._solve_hdagp(optimization_problem, opt_data, just_submit=batch_mode)

        elif self.techniques[i] == 'moa':
          self._solve_moa(optimization_problem, uploaded_data_ids, opt_data.optimal_model)

        elif isinstance(optimization_problem, SmartSelectionMixed): # descendant of the SmartSelectionEnum, must be checked prior to SmartSelectionEnum
          self._solve_mixed(optimization_problem, just_submit=batch_mode)

        elif isinstance(optimization_problem, SmartSelectionEnum):
          self._solve_enum(optimization_problem, opt_data, just_submit=batch_mode)

        if batch_mode:
          opt_data.problems_queue.append(optimization_problem)
        else:
          opt_data.update_best(optimization_problem)

          remaining_techniques = self.techniques[i + 1:]
          opt_options = [_.opt_options for _ in self.optimization_problems[i + 1:]]
          time_limit = getattr(self.__watcher, 'time_left', lambda: np.inf)()
          accelerator_options = self._get_adaptive_accelerator(time_limit, remaining_techniques, opt_options)
          for options, problem in zip(accelerator_options, self.optimization_problems[i + 1:]):
            problem.update_fixed_options(options)

        optimization_problem = None

      if self.resolve_output_transform and opt_data.problems_queue:
        user_terminated = self._flush_problems_queue(opt_data)

      if self.resolve_output_transform and not user_terminated and not 'GTApprox/OutputTransformation' in opt_data.best_problem.opt_options:
        with _scoped_options(opt_data.best_problem.fixed_options):
          original_transform = opt_data.best_problem.fixed_options["GTApprox/OutputTransformation"]
          original_transform = original_transform.lower() if isinstance(original_transform, string_types) else [_.lower() for _ in original_transform]
          test_transforms = [_ for _ in ("lnp1", "none") if _ not in original_transform]

          if test_transforms:
            self._log(LogLevel.INFO, "\nTrying to apply %s output transformation to the optimal set of parameters found." % ", ".join(test_transforms), opt_data.best_problem.comment)

          optimal_key = []
          for opt_name in opt_data.best_problem.variables_names():
            opt_value = opt_data.best_problem.optimal_options[opt_name]
            if opt_data.best_problem.opt_options.get_true_type(opt_name) == 'vector' and isinstance(opt_value, string_types):
              opt_value = opt_value.strip().lstrip("[").rstrip("]")
            optimal_key.append(opt_value)

          # some optimal options may override fixed options (e.g. HDAPMin/HDAPMax)
          for opt_name in opt_data.best_problem.optimal_options:
            opt_data.best_problem.fixed_options[opt_name] = opt_data.best_problem.optimal_options[opt_name]

          optimal_tech = opt_data.best_problem.optimal_options.get("GTApprox/Technique")
          batch_mode = bool(self.__approx_builder.is_batch) and optimal_tech.lower() not in ("rsm", "moa")

          for current_transform in test_transforms:
            try:
              opt_data.best_problem.cache_clear()
              opt_data.best_problem.fixed_options["GTApprox/OutputTransformation"] = current_transform
              opt_data.best_problem.set_absolute_minima(opt_data.best_problem)
              opt_data.best_problem.define_objectives_immediate(optimal_key, batch_mode)
            except _ex.UserTerminated:
              user_terminated = True
            finally:
              opt_data.optimal_model = opt_data.best_problem.optimal_model
    except _ex.UserTerminated:
      user_terminated = True
    except:
      # intentionally do nothing
      pass
    finally:
      # Restore builder watcher because further training (if any will occure) should ignore time limit.
      # Use the protected set method to avoid additional wrappings - the watcher has probably already
      # been wrapped with the exception handler.
      self.__approx_builder._set_watcher(original_watcher)

    if opt_data.problems_queue and not user_terminated:
      # flush problems queue
      user_terminated = self._flush_problems_queue(opt_data)

    self.fail_reasons = np.unique(sum([problem.fail_reason for problem in self.optimization_problems], []))

    optimal_model = opt_data.optimal_model
    best_optimization_problem = opt_data.best_problem
    status = 'timeout' if user_terminated else 'ok'

    try:
      if optimization_problem is not None and _LandscapeValidator.better_solution(best_optimization_problem, optimization_problem) \
         and (optimal_model is None or optimization_problem.optimal_model is not None):
        # reassign optimal problem only if it have or may have valid model
        best_optimization_problem = optimization_problem
        optimal_model = optimization_problem.optimal_model

      if best_optimization_problem is None or best_optimization_problem.optimal_options is None:
        aborted_externally = self.__external_watcher and not self.__external_watcher()
        if aborted_externally:
          raise _ex.UserTerminated('Training had been aborted before the model was created.')
        elif not aborted_externally and user_terminated and np.isfinite(getattr(self.__watcher, 'time_limit', np.inf)):
          raise _ex.InvalidOptionsError('Cannot build model for the specified options and hints. Please, consider increase time limit.')
        else:
          raise _ex.InvalidOptionsError('Cannot build model for the specified options and hints:\n%s' %
                                        ('\n'.join(['- ' + reason for reason in self.fail_reasons]) or '- failed to build or validate any model tried.'))

      if best_optimization_problem.min_error < self.accelerator_options['AcceptableQualityLevel']:
        status = 'quality'
        self._log(LogLevel.INFO, 'Acceptable quality level reached. Quality criterion value: %g' % best_optimization_problem.min_error, best_optimization_problem.comment)

      self._log(LogLevel.INFO, _pretty_print_options('Optimal set of options found:', best_optimization_problem.optimal_options), best_optimization_problem.comment)
      self._log(LogLevel.INFO, 'Best errors: %s' % best_optimization_problem.min_errors_all, best_optimization_problem.comment)

      if user_terminated and self.__watcher.overhead_allowed(best_optimization_problem.training_time_estimate):
        user_terminated = False # clear user terminated state

      if user_terminated and not optimal_model:
        optimal_iv_session = getattr(best_optimization_problem, 'optimal_iv_session', {})
        optimal_model = optimal_iv_session.get('model', None)
        if optimal_model:
          _copy_iv_info(optimal_iv_session.get('iv_model', None), optimal_model, self._log, self.comment)

        if optimal_model:
          self._log(LogLevel.WARN, _pretty_print_options('Model was created on a subset of the training set using the following options:', best_optimization_problem.optimal_options), best_optimization_problem.comment)
        return optimal_model, status

      fast_tech = best_optimization_problem.optimal_options.get('GTApprox/Technique', 'auto') not in ['auto', 'gp', 'sgp', 'hda', 'hdagp']
      technique = best_optimization_problem.optimal_options.get('GTApprox/Technique', 'auto').lower()
      tech_kind, _ = self.get_tech_kind(technique)

      if not optimal_model:
        # Finally build model with optimal values
        self._log(LogLevel.INFO, _pretty_print_options('Building the final model with the following parameters:', best_optimization_problem.optimal_options), best_optimization_problem.comment)

        best_optimization_problem.optimal_options['GTApprox/InternalValidation'] = self.iv and (has_test_sample or best_optimization_problem.optimal_dummy_model is None)

        optimal_job_id = best_optimization_problem.optimal_dummy_model.annotations.get("__job_id__", ["optimal"])[0] if best_optimization_problem.optimal_dummy_model is not None else "optimal"
        if self.__approx_builder.is_batch:
          self.__approx_builder._submit_job(uploaded_data_ids[tech_kind]["train"], optimal_job_id, action='build', options=best_optimization_problem.optimal_options,
                                            comment=best_optimization_problem.comment, initial_model=best_optimization_problem.initial_model)
          optimal_model = self.__approx_builder._get_models(cleanup=False)[uploaded_data_ids[tech_kind]["train"]][optimal_job_id]
        else:
          optimal_model = self.__approx_builder._build_simple(best_optimization_problem.x, best_optimization_problem.y, options=best_optimization_problem.optimal_options,
                                                              weights=best_optimization_problem.weights, outputNoiseVariance=best_optimization_problem.output_noise_variance,
                                                              initial_model=best_optimization_problem.initial_model, comment=best_optimization_problem.comment, silent=fast_tech)
        optimal_model = _postprocess_single_model(optimal_model, optimal_job_id)
        if optimal_model is not None and not optimal_model.iv_info:
          # copy IV info from optimal_dummy_model to optimal_model
          _copy_iv_info(best_optimization_problem.optimal_dummy_model, optimal_model, self._log, self.comment)

      elif self.iv:
        # manually perform IV
        tensored_iv = technique in ['ta', 'tgp']
        iv = _IterativeIV(best_optimization_problem.x, best_optimization_problem.y, options=best_optimization_problem.optimal_options,
                          outputNoiseVariance=best_optimization_problem.output_noise_variance, weights=best_optimization_problem.weights,
                          tensored=tensored_iv) # create IV iterator driver

        if self.__approx_builder.is_batch:
          data_id_list = uploaded_data_ids[tech_kind]["iv"]

          # first pass - submit jobs
          round_index = 0
          while iv.session_begin():
            job_comment = _make_job_prefix(best_optimization_problem.comment, None, round_index + 1)
            self.__approx_builder._submit_job(data_id_list[round_index], 'optimal_model', action='build', options=iv.options.values,
                                              comment=job_comment, initial_model=best_optimization_problem.initial_model)
            iv.session_end(None)
            round_index += 1

          # second pass - pull models and overwrite IV data
          models = _postprocess_models_dict(self.__approx_builder._get_models(cleanup=False))
          iv = _IterativeIV(best_optimization_problem.x, best_optimization_problem.y, options=best_optimization_problem.optimal_options,
                            outputNoiseVariance=best_optimization_problem.output_noise_variance, weights=best_optimization_problem.weights,
                            tensored=tensored_iv) # create IV iterator driver
          round_index = 0
          while iv.session_begin():
            iv.session_end(models[data_id_list[round_index]]['optimal_model'])
            round_index += 1
        else:
          round_index = 1
          while iv.session_begin():
            if not fast_tech:
              self._log(LogLevel.INFO, '\nThe cross validation training session #%d is started.' % round_index, best_optimization_problem.comment)

            job_comment = _make_job_prefix(best_optimization_problem.comment, None, round_index)
            model = self.__approx_builder._build_simple(iv.x, iv.y, outputNoiseVariance=iv.outputNoiseVariance, weights=iv.weights,
                                                        options=iv.options.values, initial_model=best_optimization_problem.initial_model,
                                                        comment=job_comment, silent=fast_tech)

            if not fast_tech:
              self._log(LogLevel.INFO, '\n', best_optimization_problem.comment)
              self._log(LogLevel.INFO, 'The cross validation training session #%d is finished\n' % round_index, best_optimization_problem.comment)

            iv.session_end(model)
            round_index += 1

        # safe IV results to approximator
        iv.save_iv(optimal_model)
    finally:
      self.__approx_builder._get_build_manager().clean_data()
    return optimal_model, status

  def _solve_sbo(self, problem):
    optimizer = _gtopt.Solver()
    optimizer.set_logger(self.__logger)

    # remove non-GT options from accelerator options
    gtopt_options = self.accelerator_options.copy()
    for option_name in [_ for _ in gtopt_options.keys() if not _.lower().startswith(("/", "gtopt/", "gtdoe/", "gtapprox/"))]:
      del gtopt_options[option_name]

    gtopt_options['GTOpt/BatchSize'] = 65535 if self.__approx_builder.is_batch else 1
    gtopt_options['GTOpt/MaxParallel'] = problem.approx_builder.options.get('GTApprox/MaxParallel')
    gtopt_options['GTOpt/LogLevel'] = problem.approx_builder.options.get('GTApprox/LogLevel')

    try:
      problem.disable_history()
      # Do not call optimizer.solve(...) method to keep current SIGINT watcher
      _ = optimizer._run_solver(problem, (_gtopt.api.GTOPT_VALIDATE if problem.dry_run else _gtopt.api.GTOPT_SOLVE), sample_x=problem.init_x, options=gtopt_options)
    except (_ex.UserTerminated, _ex.UserEvaluateException):
      _shared.reraise(_ex.UserTerminated, None, sys.exc_info()[2])
    except:
      pass

  def _solve_rsm(self, problem):
    acceptable_quality_level = problem.acceptable_quality_level
    surface_objective = {} # RSM errors by surface type for GP trend type selection

    init_x = [_.lower() if isinstance(_, string_types) else _ for _ in problem.init_x]
    batch_mode = self.__approx_builder.is_batch and problem.dry_run != 'quick'

    x_encoded_shape = [_ for _ in np.shape(problem.x)]
    if len(x_encoded_shape) == 1:
      x_encoded_shape = x_encoded_shape[0], 1

    catvars = _shared.parse_json(problem._read_fixed_option('GTApprox/CategoricalVariables'))
    encodings = _shared.parse_json(problem._read_fixed_option('//Encoding/InputsEncoding'))
    for encoding_idx in encodings:
      if isinstance(encoding_idx[-1], string_types):
        encoding_idx, encoding_type = encoding_idx[:-1], encoding_idx[-1]
      else:
        encoding_type = 'none'
      if all([_ in catvars for _ in encoding_idx]):
        n_unique_values = len(technique_selection._get_unique_elements(problem.x[:, encoding_idx], return_indices=False))
        x_encoded_shape[1] += technique_selection.encoded_dims_number(encoding_type, n_unique_values) - 1

    y_shape = np.shape(problem.y)
    if len(y_shape) == 1:
      y_shape = y_shape[0], 1

    problem_grid = {tuple(_ for _ in init_x): None}
    rt_index, fs_index = -1, -1

    def _remove(option_index, option_value):
      if option_index > -1:
        for key in list(problem_grid):
          if key[option_index] == option_value:
            del problem_grid[key]

    def _unique(option_index):
      if option_index == -1:
        return []
      return list(set(key[option_index] for key in problem_grid))

    def _min_error(option_index, option_value, default_min_error):
      min_error = None
      if option_index > -1:
        for key in problem_grid:
          if key[option_index] != option_value or problem_grid[key] is None:
            continue
          elif min_error is None or problem_grid[key] < min_error:
            min_error = problem_grid[key]
      return default_min_error if min_error is None else min_error

    def _calc_terms(rsm_type, nvar):
      if rsm_type == 'linear':
        return 1 + nvar  # intercept + linear
      elif rsm_type == 'interaction':
        return 1 + nvar + nvar * (nvar - 1) // 2  # intercept + linear + interactions
      elif rsm_type == 'quadratic':
        return 1 + 2 * nvar + nvar * (nvar - 1) // 2  # intercept + linear + quadratic + interactions
      elif rsm_type == 'purequadratic':
        return 1 + 2 * nvar  # intercept + linear + quadratic
      return 1 + nvar

    def _apply_stepwisefit(rsm_type, nvar, npoints):
      return _calc_terms(rsm_type, nvar) * npoints <= 20000

    try:
      for i, option_name in enumerate(problem.opt_options):
        if option_name.lower() == 'gtapprox/rsmtype':
          rt_index = i
          rt_values = _lower_case_list(problem.opt_options.get_bounds('gtapprox/rsmtype', []))
          for rt, test_x in _shared.product(rt_values, iterkeys(problem_grid)):
            problem_grid[tuple(rt if _ == i else v for _, v in enumerate(test_x))] = None
        elif option_name.lower() == 'gtapprox/rsmfeatureselection':
          fs_index = i
          fs_values = _lower_case_list(problem.opt_options.get_bounds('gtapprox/rsmfeatureselection', []))
          fs_priority = ['ls', 'ridgels', 'multipleridgels', 'elasticnet', 'stepwisefit']
          for fs, test_x in _shared.product(sorted(fs_values, key=lambda fs: fs_priority.index(fs)), iterkeys(problem_grid)):
            problem_grid[tuple(fs if _ == i else v for _, v in enumerate(test_x))] = None

      acceleration_level = int(problem._read_fixed_option('GTApprox/Accelerator', 1))
      fs_unique = _unique(fs_index)
      # Apply additional constraints on feature selection algorithms:
      #  level 1, 2: quality level disabled, check all feature selection algorithms
      #  level 3: check all feature selection algorithms with instant death if quality level achivied
      #  level 4: same as level 3 but don't use StepwiseFit and ElasticNet
      #  level 5: same as level 4 but don't use MultipleRidgeLS
      if len(fs_unique) > 1:
        if 1 != y_shape[1]:
          _remove(fs_index, 'stepwisefit')
        if acceleration_level > 3:
          _remove(fs_index, 'stepwisefit')
          _remove(fs_index, 'elasticnet')
          if acceleration_level > 4:
            _remove(fs_index, 'multipleridgels')

        fs_unique = _unique(fs_index)
        if len(fs_unique) > 1 and ('stepwisefit' in fs_unique or 'elasticnet' in fs_unique):
          for key in list(problem_grid):
            rsm_type = key[rt_index] if rt_index > -1 else problem._read_fixed_option('GTApprox/RSMType').lower()
            if key[fs_index] == 'stepwisefit' and not _apply_stepwisefit(rsm_type, x_encoded_shape[1], x_encoded_shape[0]):
              # it's too slow for a moment
              del problem_grid[key]
            elif not batch_mode and key[fs_index] in ['ridgels', 'multipleridgels'] and _calc_terms(rsm_type, x_encoded_shape[1]) > x_encoded_shape[0]:
              # remove ridgels and multiple ridgels if there are too many terms
              del problem_grid[key]

      # End up filtering here, ensure problem grid is not empty
      problem_grid = problem_grid or {(_ for _ in init_x): None}
      untested_x = list(problem_grid)
      # Update init_x since we might filter out the original one
      init_x = untested_x[0]
      fs_error_best = np.inf
      fs_optimal = init_x[fs_index] if fs_index > -1 else problem._read_fixed_option('GTApprox/RSMFeatureSelection').lower()
      rt_error_best = np.inf
      rt_optimal = init_x[rt_index] if rt_index > -1 else problem._read_fixed_option('GTApprox/RSMType').lower()

      def define_objectives(test_x):
        if test_x in untested_x:
          untested_x.remove(test_x)
          if problem.dry_run == 'quick':
            # All models are the same in dry run mode.
            for k in problem_grid:
              if problem_grid[k] is not None:
                return problem_grid[k]
          # Note _build_model_and_estimate_error returns either error (float) or job id (string)
          return problem._build_model_and_estimate_error(list(test_x), just_submit=batch_mode, alt_initial_model=None)
        else:
          return problem_grid[test_x]

      # Two phases mode: first try LS and ElasticNet, then perform feature selection if LS is a winner
      if fs_index > -1 and 'ls' in fs_unique:
        # don't stop on first minimal error, we'd like to run feature selection on the second stage
        problem.set_acceptable_quality_level(-np.inf)

      if batch_mode or 'GTApprox/OutputTransformation' in problem.opt_options:
        # First check LS and ElasticNet for all RSM types
        tested_x_list = []

        # run all acceptable evaluations
        for test_x in untested_x:
          if fs_index == -1 or test_x[fs_index] in ['ls', 'elasticnet']:
            problem_grid[test_x] = define_objectives(test_x)
            tested_x_list.append(test_x)

        if batch_mode:
          models, fail_reason, training_start = _get_models(self.__approx_builder, self._log, False, self.comment)
          # The pull_solution keeps known errors and replaces job ids (strings) by evaluated error or NaN
          errors = problem.pull_solution(models, fail_reason, training_start, target_errors_list=[problem_grid[_] for _ in tested_x_list])
          # Now copy the errors back, hoping that the problem_grid keys are listed in the same order.
          for test_x, error in zip(tested_x_list, errors):
            problem_grid[test_x] = error

        if fs_index > -1:
          for test_x in untested_x:
            if problem_grid[test_x] is not None and problem_grid[test_x] < fs_error_best:
              fs_error_best = problem_grid[test_x]
              fs_optimal = init_x[fs_index]

        # Now check other LS-based feature selection algorithms if LS was better than ElasticNet
        if fs_optimal == 'ls' and fs_index > -1:
          tested_x_list = []
          for test_x in untested_x:
            if test_x[fs_index] in ['ridgels', 'multipleridgels', 'stepwisefit']:
              problem_grid[test_x] = define_objectives(test_x)
              tested_x_list.append(test_x)
          if batch_mode:
            models, fail_reason, training_start = _get_models(self.__approx_builder, self._log, False, self.comment)
            errors = problem.pull_solution(models, fail_reason, training_start, target_errors_list=[problem_grid[_] for _ in tested_x_list])
            for test_x, error in zip(tested_x_list, errors):
              problem_grid[test_x] = error

      else:
        if rt_index > -1:
          # First select RSM type, do not vary feature selection
          for test_x in untested_x:
            if fs_index == -1 or test_x[fs_index] == init_x[fs_index]:
              problem_grid[test_x] = define_objectives(test_x)
              if problem_grid[test_x] < rt_error_best:
                rt_error_best = problem_grid[test_x]
                rt_optimal = test_x[rt_index]

        if fs_index > -1:
          # First check LS and ElasticNet feature selection algorithms for optimal RSM type
          error_best = rt_error_best
          if acceptable_quality_level is not None and error_best > acceptable_quality_level:
            # restore acceptable quality level so we'll abort at the first successfull feature selection
            # otherwise let's first try all feature selection algorithms
            problem.set_acceptable_quality_level(acceptable_quality_level, call_watcher=False)
            acceptable_quality_level = None
          for test_x in untested_x:
            if rt_index == -1 or test_x[rt_index] == rt_optimal:
              if test_x[fs_index] in ['ls', 'elasticnet']:
                problem_grid[test_x] = define_objectives(test_x)
                if problem_grid[test_x] < error_best:
                  error_best = problem_grid[test_x]
                  fs_optimal = test_x[fs_index]
          # Now check other LS-based feature selection algorithms if LS was better than ElasticNet
          if fs_optimal == 'ls':
            for test_x in untested_x:
              if rt_index == -1 or test_x[rt_index] == rt_optimal:
                if test_x[fs_index] in ['ridgels', 'multipleridgels', 'stepwisefit']:
                  problem_grid[test_x] = define_objectives(test_x)

    finally:
      if acceptable_quality_level is not None:
        problem.set_acceptable_quality_level(acceptable_quality_level, call_watcher=True)

    # if either linear or purequadratic surface has not been checked then linear is prefered trend
    return surface_objective.get('linear', 0.) <= surface_objective.get('purequadratic', np.inf)

  def _get_valid_problems_grid(self, problem, opt_data, just_submit):
    if not problem.initial_model:
      # Simple case.
      options_grid = [problem.init_x]
      if problem.dry_run != 'quick':
        options_grid.extend(x for x in problem.options_grid if not _is_init_value(x, problem))
      return options_grid

    # There is an initial model: some options may be incompatible, alternative initial model must not be used
    # Flush problem queue prior to any checks that involve approx builder
    if just_submit and self._flush_problems_queue(opt_data):
      raise _ex.UserTerminated()

    max_grid_length = 1 if problem.dry_run == 'quick' else np.iinfo(int).max
    options_grid = [problem.init_x] if problem._quick_validate_model_options(problem.init_x, alt_initial_model=None) else []
    for x in problem.options_grid:
      if len(options_grid) >= max_grid_length:
        break
      elif not _is_init_value(x, problem) and problem._quick_validate_model_options(x, alt_initial_model=None):
        options_grid.append(x)

    return options_grid

  def _solve_hdagp(self, problem, opt_data, just_submit):
    self._filter_options_grid(problem)

    # If there is global initial model (problem.initial_model) then we MUST use this model.

    output_transform_i = problem.get_opt_option_index("GTApprox/OutputTransformation")
    fixed_output_transform = problem._read_fixed_option('GTApprox/OutputTransformation', 'none')
    if not isinstance(fixed_output_transform, string_types):
      fixed_output_transform = fixed_output_transform[0]

    def define_objectives(x):
      output_transform = (x[output_transform_i] if output_transform_i > -1 else fixed_output_transform).lower()
      estimated_p = opt_data.hda_estimated_p.get(output_transform)
      # Never send an alternative initial model if we have the real one
      trend_model = opt_data.hda_trend_model.get(output_transform) if not problem.initial_model else None
      if estimated_p is not None or trend_model is not None:
        with _scoped_options(problem.fixed_options):
          if estimated_p is not None:
            problem.fixed_options['GTApprox/HDAPMin'] = estimated_p
            problem.fixed_options['GTApprox/HDAPMax'] = estimated_p
          problem.define_objectives(x, just_submit, alt_initial_model=trend_model)
      else:
        # flush problem queue first
        if just_submit and self._flush_problems_queue(opt_data):
          raise _ex.UserTerminated()
        problem.define_objectives_immediate(x, just_submit, alt_initial_model=trend_model)
        estimated_p = getattr(problem, 'estimated_p', {}).get(output_transform, None)
        trend_model = None if problem.initial_model else getattr(problem, 'hda_trend_model', {}).get(output_transform, None)
        opt_data.update_hda_parameters(output_transform, estimated_p, trend_model)

    for x in self._get_valid_problems_grid(problem, opt_data, just_submit):
      if not just_submit and self._termination_criteria(problem):
        break
      define_objectives(x)

  def _solve_moa(self, problem, uploaded_data_ids, optimal_model=None):
    self._filter_options_grid(problem)

    if optimal_model is not None and problem.initial_model is None:
      decompose_initial_model = optimal_model # model to use for problem decomposition
      alt_initial_model = optimal_model, [] # alternative initial model
      low_fidelity_model_mode = [] # no boosting, no forward, use best existing model only for clustering
      try:
        self._log(LogLevel.INFO, "\nMoA technique is using %s model for clustering purpose" % (optimal_model.details.get("Technique", optimal_model.comment)))
        optimal_model_options = optimal_model.details.get("Training Options", {})
        for k in sorted([_ for _ in optimal_model_options]):
          self._log(LogLevel.INFO, "    %s=%s" % (k, optimal_model_options[k]))
      except:
        pass
    else:
      decompose_initial_model = problem.initial_model
      alt_initial_model, low_fidelity_model_mode = None, None

    manual_clusters = _shared.parse_json(problem._read_fixed_option("//GTApprox/MoAClustersModel"))
    output_transform_i = problem.get_opt_option_index("GTApprox/OutputTransformation")
    clusters_models = {}

    def decompose_space(codename):
      build_manager = problem.approx_builder._get_build_manager()
      data_id, job_id = uploaded_data_ids["original"]["train"], "cluster" + codename


      if low_fidelity_model_mode is not None:
        clusterize_moa_options = CaseInsensitiveDict(problem.fixed_options)
        clusterize_moa_options["/GTApprox/MoALowFidelityModel"] = low_fidelity_model_mode
      else:
        clusterize_moa_options = problem.fixed_options

      build_manager.submit_job(data_id, job_id, action="clusterize_moa", options=clusterize_moa_options,
                               comment=_make_job_prefix(problem.comment, job_id),
                               initial_model=decompose_initial_model)
      return build_manager.get_moa_clusters().get(data_id, {}).get(job_id)

    def define_objectives(x):
      codename = ("_transform_" + x[output_transform_i]) if output_transform_i >= 0 else "_space"
      current_clusters = manual_clusters or clusters_models.get(codename)

      # in the worst case (manual_clusters is not empty) the following code is just useless but safe
      if not current_clusters:
        with _scoped_options(problem.fixed_options):
          problem.fixed_options['GTApprox/Accelerator'] = min(5, problem._read_fixed_option('GTApprox/AcceLerator', 1) + 1)
          if output_transform_i >= 0:
            problem.fixed_options["GTApprox/OutputTransformation"] = x[output_transform_i]
          current_clusters = decompose_space(codename)
        if 'encoding_model' in current_clusters and current_clusters['encoding_model']:
          current_clusters['encoding_model'] = current_clusters['encoding_model'].tostring(sections='none').decode("ascii") # convert model to string
        clusters_models[codename] = current_clusters

      with _scoped_options(problem.fixed_options):
        problem.fixed_options["//GTApprox/MoAClustersModel"] = _shared.write_json(current_clusters)
        problem.fixed_options["GTApprox/MoANumberOfClusters"] = [int(current_clusters.get("number_of_clusters"))]
        problem.fixed_options["GTApprox/MoACovarianceType"] = current_clusters.get("covariance_type")
        if low_fidelity_model_mode is not None:
          problem.fixed_options["/GTApprox/MoALowFidelityModel"] = low_fidelity_model_mode
        problem.define_objectives(x, False, alt_initial_model=alt_initial_model)

    # sort grid in the increasing complexity order
    options_grid = [x for x in problem.options_grid]
    moa_technique_i = problem.get_opt_option_index("GTApprox/MoATechnique")
    if moa_technique_i >= 0:
      techniques_order = ["splt", "rsm", "ta", "tgp", "gbrt", "ita", "pla", "sgp", "gp", "hda", "hdagp", "auto"]
      options_grid = sorted(options_grid, key=lambda x: techniques_order.index(str(x[moa_technique_i]).lower()))

    # build model with initial value first
    define_objectives(problem.init_x)

    if problem.dry_run == 'quick':
      return

    for x in options_grid:
      if self._termination_criteria(problem):
        break
      elif not _is_init_value(x, problem):
        define_objectives(x)

  def _solve_enum(self, problem, opt_data, just_submit):
    self._filter_options_grid(problem)
    for x in self._get_valid_problems_grid(problem, opt_data, just_submit):
      if not just_submit and self._termination_criteria(problem):
        break
      problem.define_objectives(x, just_submit)

  def _solve_mixed(self, problem, just_submit):
    # build model with initial value first
    _ = problem.define_objectives(problem.init_x, just_submit)

    if problem.dry_run == 'quick':
      return

    for x in problem.options_grid:
      # calculate objective for non init value
      categorical_options, is_init_value = _convert_variable_to_dict(x, problem.variables_names(), problem.fixed_options,
                                                                     problem.opt_options)
      if not is_init_value:
        solve_enum_problem = True
        # solve SBO problem only if numerical option is enable (e.g. L1_ratio is enabled only if RSMFeatureSelection=='ElasticNet')
        for dependent_value in problem.dependen_options_values:
          if dependent_value.lower() in [value.lower() for value in categorical_options.values() if isinstance(value, str)]:
            solve_enum_problem = False

        if solve_enum_problem:
          _ = problem.define_objectives(x, just_submit)
        else:
          if just_submit:
            models, fail_reason, training_start = _get_models(problem.approx_builder, problem._log, False, self.comment)
            problem.pull_solution(models, fail_reason, training_start)

          problem.update_fixed_options(categorical_options)
          sbo_problem = SmartSelectionSBO(problem.x, problem.y,
                                          x_test=problem.x_test, y_test=problem.y_test,
                                          fixed_options=problem.fixed_options,
                                          opt_options=problem.sbo_options,
                                          error_types=problem.error_types,
                                          approx_builder=problem.approx_builder,
                                          output_noise_variance=problem.output_noise_variance,
                                          comment=problem.comment, weights=problem.weights,
                                          initial_model=problem.initial_model)

          self._solve_sbo(sbo_problem)
          problem.evaluation_count += sbo_problem.evaluation_count

      if not just_submit and self._termination_criteria(problem):
        break

  def _filter_options_grid(self, problem):
    n_points, dim = problem.x.shape
    technique = problem._technique
    smooth_mode = self.accelerator_options.get('LandscapeAnalysis', False)
    full_search = _shared.parse_bool(problem._read_fixed_option('/GTApprox/SmartSelection/BruteforceGP', False))

    if self.__logger and full_search:
      self.__logger(LogLevel.DEBUG, '\nBruteforce search is activated for Smart Selection.\n')

    if 'gp' in technique:
      i_learning_mode = problem.get_opt_option_index('GTApprox/GPLearningMode')
      i_trend = problem.get_opt_option_index('GTApprox/GPTrendType')
      i_type = problem.get_opt_option_index('GTApprox/GPType')
      i_power = problem.get_opt_option_index('GTApprox/GPPower')

      def is_valid(options):
        # Save initial options values anyway
        if options == problem.init_x:
          return True
        # For 1D sample and TGP technique only Wlp is allowed
        if (dim == 1 or technique == 'tgp') and i_type > -1 and str(options[i_type]).lower() != 'wlp':
          return False
        if i_type > -1 and options[i_type].lower() == "mahalanobis":
          # Mahalanobis covariance is quadratic by definition
          if i_power > -1 and np.abs(float(options[i_power]) - 2) > 1e-10:
            return False
          # Mahalanobis covariance function doesn't support heteroscedasticity
          if _shared.parse_auto_bool(problem._read_fixed_option('GTApprox/Heteroscedastic', 'auto'), False):
            return False
          # Mahalanobis covariance have dim * (dim + 1) // 2 internal parameters. Let's require n_points >= (2 * n_params + 3)
          if (dim * (dim + 1) + 3) > n_points:
            return False
          # Mahalanobis is slow
          if (dim * (dim + 1) // 2) >= 50:
            return False
        # The Robust learning mode is incompatible with the 'Exact Fit' requirement (was also checked before)
        if _shared.parse_bool(problem._read_fixed_option('GTApprox/ExactFitRequired', False)):
          if i_learning_mode > -1 and options[i_learning_mode].lower() == 'robust':
            return False

        # Try to reasonably reduce the size of options grid if full search is not required
        if full_search or dim == 1 or technique == 'tgp':
          return True
        # Vary gppower and fix robust learning mode in smooth mode with landscape validation
        if smooth_mode and i_learning_mode > -1 and options[i_learning_mode].lower() != 'robust':
          return False
        # Mahalanobis is usually less smooth than WLP in case of varying GP Power
        if smooth_mode and i_type > -1 and options[i_type].lower() != 'wlp':
          return False
        # Do not vary gppower if smooth mode is not active
        if not smooth_mode and i_power > -1 and np.abs(float(options[i_power]) - 2) > 1e-10:
          return False
        # Build model in robust mode if the sample is big enough
        if n_points * dim ** 2 > 512 and i_learning_mode > -1 and options[i_learning_mode].lower() != 'robust':
          return False

        if i_learning_mode > -1 and options[i_learning_mode].lower() == 'robust':
          if i_trend > -1 and options[i_trend].lower() not in ['linear', 'quadratic']:
            return False

        if i_learning_mode > -1 and options[i_learning_mode].lower() == 'accurate':
          if i_trend > -1 and options[i_trend].lower() not in ['none', 'linear']:
            return False

        return True

      problem.options_grid = [_ for _ in problem.options_grid if is_valid(_)]

  def _termination_criteria(self, problem, ignore_error=False):
    # it's deprecated and buried...
    #if isinstance(problem, SmartSelectionEnum):
    #  max_count = len(problem.options_grid) / ((int(problem.fixed_options['GTApprox/Accelerator']) + 1) // 2)
    #  if problem.evaluation_count >= max_count:
    #    return True

    if not ignore_error and problem.min_error <= self.accelerator_options.get('AcceptableQualityLevel', 1.e-8):
      return True

    return False


class _OptimizationData(object):

  def __init__(self, ):
    self.optimal_model = None # optimal model built (could be built using not the optimal options set)
    self.best_problem = None

    self.problems_queue = []
    self.hda_estimated_p = {}
    self.hda_trend_model = {}

  def update_hda_parameters(self, transform, estimated_p, trend_model):
    if estimated_p is not None:
      self.hda_estimated_p[transform] = estimated_p
    if trend_model is not None:
      self.hda_trend_model[transform] = trend_model

  def update_best(self, optimization_problem):
    if optimization_problem._technique in ('hda', 'hdagp'):
      if not self.hda_estimated_p:
        self.hda_estimated_p = getattr(optimization_problem, 'estimated_p', {})
      if not self.hda_trend_model:
        self.hda_trend_model = getattr(optimization_problem, 'hda_trend_model', {})
    if _LandscapeValidator.better_solution(self.best_problem, optimization_problem): #optimization_problem.min_error < min_error:
      self.best_problem = optimization_problem
      if optimization_problem.optimal_model is not None:
        self.optimal_model = optimization_problem.optimal_model
      return True
    else:
      return False
