#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import sys as _sys
from datetime import datetime as _datetime

import numpy as np

from .. import exceptions as _ex
from .. import shared as _shared
from .. import loggers
from ..six import string_types
from .sbo_opt_problem import SmartSelectionOptimizer
from .smart_selection_utilities import CaseInsensitiveDict, _get_ordered_list_of_techniques, _lower_case_list, _merge_dicts
from . import technique_selection

def _check_hints_compatibility(hints, incompatible_hints_pairs):
  """
  hints --- user provided hints
  incompatible_hints_pairs --- dictionary, (key: value), key is a possible hint value,
                         value is a list of hints values incompatible with key.
  """
  hint_values = set(_lower_case_list(hints.get('@GTApprox/DataFeatures', []) + hints.get('@GTApprox/ModelFeatures', [])))
  for value in hint_values:
    incompatible_candidates = incompatible_hints_pairs.get(value, set())
    incompatible_hints_intersection = hint_values.intersection(incompatible_candidates)
    if incompatible_hints_intersection:
      raise _ex.InvalidOptionsError('Incompatible hint values: "%s" and "%s"!' % (value, list(incompatible_hints_intersection)[0]))

def _check_supported_hint(hint_name, hint_value, supported_hints):
  if not hint_name in supported_hints:
    raise _ex.InvalidOptionsError('Hint %s is not supported!' % hint_name)

  type_converter, type_name, valid_values = supported_hints[hint_name]

  try:
    checked_hint_value, valid_value, error_desc = type_converter(hint_value, valid_values)
  except:
    _shared.reraise(_ex.InvalidOptionsError, ('Invalid type of hint %s value: %s expected (got %s).' % (hint_name, type_name, type(hint_value))), _sys.exc_info()[2])

  if not valid_value:
    raise _ex.InvalidOptionsError('Invalid value of hint %s is given: %s. %s' % (hint_name, hint_value, error_desc))

  return checked_hint_value

def _get_default_accelerator_options():
  return CaseInsensitiveDict({'GTOpt/GlobalPhaseIntensity': 0.2,
                              'AcceptableQualityLevel': 1.e-3,
                              'LandscapeAnalysis': False,
                              'LandscapeAnalysisThreshold': 10000,
                              'TimeLimit': 0,
                              'TrainingSubsampleRatio': 0.,
                              'TryOutputTransformations': False})

def _get_default_hints_options(hints, logger=None, explicit_user_options=None):
  """
  Map hints to options
  """
  if hints is None:
    hints = {}

  def _valid_range_repr(valid_range):
    return '%s%g, %g%s' % (('[' if valid_range[0][1] else '('), valid_range[0][0], valid_range[1][0], (']' if valid_range[1][1] else ')'))

  def _err_not_in_list(valid_values, alt_reason):
    return alt_reason if valid_values is None else 'Expected one of the following values: %s' % valid_values

  def _err_not_in_range(valid_range, alt_reason):
    return alt_reason if valid_range is None else 'The value given is out of the valid range %s' % _valid_range_repr(valid_range)

  def _err_not_subset(valid_values, alt_reason):
    return alt_reason if valid_values is None else 'Expected nonempty subset of the following values: %s' % valid_values

  def _validate_int(value, valid_values):
    int_value = int(value)
    try:
      if float(value) != int_value:
        # improper float value could be converted to int
        return value, False, 'Integer value is expected.'
      return int_value, (valid_values is None or int_value in valid_values), _err_not_in_list(valid_values, '')
    except:
      return value, False, 'Integer value is expected.'

  def _validate_unsigned(value, valid_values):
    uint_value = int(value)
    try:
      if float(value) != uint_value:
        # improper float value could be converted to int
        return value, False, 'Integer value is expected.'
      return uint_value, (uint_value >= 0 and (valid_values is None or uint_value in valid_values)), \
                           _err_not_in_list(valid_values, 'Non-negative value is expected.')
    except:
      return value, False, 'Integer value is expected.'

  def _validate_float(value, valid_values):
    value = float(value)
    try:
      return value, (not np.isnan(value) and (valid_values is None or value in valid_values)), \
              _err_not_in_list(valid_values, 'Finite float value is expected.')
    except:
      return value, False, 'Finite float value is expected.'

  def _validate_ranged_float(value, valid_range):
    value = float(value)
    try:
      check_ok = not np.isnan(value)
      if check_ok and valid_range is not None:
        check_ok = ((value >= valid_range[0][0]) if valid_range[0][1] else (value > valid_range[0][0])) \
                and ((value <= valid_range[1][0]) if valid_range[1][1] else (value < valid_range[1][0]))
      return value, check_ok, _err_not_in_range(valid_range, 'Finite float value is expected.')
    except:
      return value, False, 'The float value in %s range is expected.' % _valid_range_repr(valid_range)

  def _validate_string(value, valid_values):
    value = str(value)
    try:
      if valid_values is None or value in valid_values:
        return value, True, ''
      # case insensitive check
      value = value.lower()
      for valid_value in valid_values:
        if value == valid_value.lower():
          return valid_value, True, ''
    except:
      pass
    return value, False, _err_not_in_list(valid_values, '')

  def _list_of_strings(value, valid_values):
    listed_value = None
    if not isinstance(value, string_types):
      try:
        if not hasattr(value, 'keys'):
          listed_value = [str(_) for _ in value]
      except:
        pass
    value = [str(value),] if listed_value is None else listed_value

    if valid_values is None or not value:
      return value, True, ''

    checked_values = []
    test_passed = True
    for unchecked_value in value:
      if unchecked_value in valid_values:
        checked_values.append(unchecked_value)
      else:
        unchecked_value_lc = unchecked_value.lower()
        for valid_value in valid_values:
          if unchecked_value_lc == valid_value.lower():
            checked_values.append(valid_value)
            break
        else:
          checked_values.append(unchecked_value)
          test_passed = False

    return checked_values, test_passed, _err_not_subset(valid_values, '')

  def _validate_bool(value, valid_values):
    try:
      return _shared.parse_bool(value), (valid_values is None or _shared.parse_bool(value) in valid_values), _err_not_in_list(valid_values, '')
    except:
      return value, False, 'Boolean value is expected.'

  supported_hints = CaseInsensitiveDict({'@GTApprox/Accelerator': (_validate_int, 'integer', [1, 2, 3, 4, 5],),
                                         '@GTApprox/AcceptableQualityLevel': (_validate_float, 'float', None),
                                         '@GTApprox/TimeLimit': (_validate_unsigned, 'unsigned', None),
                                         '@GTApprox/Tolerance': (_validate_float, 'float', None),
                                         '@GTApprox/TrainingSubsampleRatio': (_validate_ranged_float, 'float', ((0., True), (1., True))),
                                         '@GTApprox/QualityMetrics': (_validate_string, 'string', ['RRMS', 'RMS', 'Mean', 'Median', 'Q_0.95', 'Q_0.99', 'Max', 'R^2'],),
                                         '@GTApprox/DataFeatures': (_list_of_strings, 'list of strings', ['Discontinuous', 'Linear', 'Quadratic', 'DependentOutputs', 'TensorStructure'],),
                                         '@GTApprox/ModelFeatures': (_list_of_strings, 'list of strings', ['AccuracyEvaluation', 'Smooth', 'ExactFit', 'Gradient'],),
                                         '@GTApprox/TryOutputTransformations': (_validate_bool, 'boolean', None,),
                                         '@GTApprox/EnabledTechniques': (_list_of_strings, 'list of strings', _get_ordered_list_of_techniques(),),
                                         })
  incompatible_hints_pairs = {'discontinuous': ['linear', 'quadratic', 'accuracyevaluation'],
                              'linear': ['quadratic', 'exactfit', 'accuracyevaluation'],
                              'quadratic': ['exactfit', 'accuracyevaluation'],
                             }

  hints = CaseInsensitiveDict(hints)
  opt_options = CaseInsensitiveDict()
  fixed_options = CaseInsensitiveDict()
  implicit_accelerator_options = _get_default_accelerator_options()
  accelerator_options = CaseInsensitiveDict({})
  quality_metric = 'RRMS'
  explicit_user_options = CaseInsensitiveDict() if not explicit_user_options else CaseInsensitiveDict(explicit_user_options)
  user_tech = explicit_user_options.get("GTApprox/Technique", "Auto")

  _check_hints_compatibility(hints, incompatible_hints_pairs)

  opt_options['GTApprox/Technique'] = {'type': 'Enum', 'true_type': 'int'}

  # separate read techniques list
  for hint_name in hints:
    hint_name = hint_name.lower()
    if hint_name == "@gtapprox/enabledtechniques":
      hint_value = _check_supported_hint(hint_name, hints[hint_name], supported_hints)
      if hint_value:
        opt_options['GTApprox/Technique']['bounds'] = set(_lower_case_list(hint_value))
        if user_tech.lower() != 'auto':
          if user_tech.lower() not in opt_options['GTApprox/Technique']['bounds']:
            raise _ex.InvalidOptionsError('The selected technique (%s) is not listed in the @GTApprox/EnabledTechniques hint (%s).' % (user_tech, hints[hint_name]))
          elif len(opt_options['GTApprox/Technique']['bounds']) > 1:
            # if GTApprox/Technique option value is set to non-auto technique X then the only valid @GTApprox/EnabledTechniques hint value is "[X]"
            raise _ex.InvalidOptionsError('The GTApprox/Technique option (%s) and the @GTApprox/EnabledTechniques hint (%s) are mutually exclusive.' % (user_tech, hints[hint_name]))
      break

  user_tech = user_tech.lower()
  if not opt_options['GTApprox/Technique'].get("bounds"):
    opt_options['GTApprox/Technique']['bounds'] = set([user_tech] if user_tech != 'auto' else ['splt', 'ta', 'ita', 'tgp', 'rsm', 'gbrt', 'gp', 'sgp', 'hda', 'hdagp', 'moa'])

  for original_hint_name in hints:
    # check that correct hints are provided
    original_hint_value = hints[original_hint_name]
    hint_value = _check_supported_hint(original_hint_name, original_hint_value, supported_hints)
    hint_name = original_hint_name.lower()

    if hint_name == '@gtapprox/timelimit' and hint_value:
      accelerator_options['TimeLimit'] = int(hint_value)

    if  hint_name == '@gtapprox/tryoutputtransformations':
      accelerator_options['TryOutputTransformations'] = hint_value
      if hint_value:
        explicit_output_transform = explicit_user_options.get("GTApprox/OutputTransformation", None)
        if explicit_output_transform is None:
          fixed_options["GTApprox/OutputTransformation"] = "auto"
        else:
          explicit_output_transform = _shared.parse_output_transformation(explicit_output_transform)
          if not (explicit_output_transform.lower() == "auto" if isinstance(explicit_output_transform, string_types) else any(_.lower() == "auto" for _ in explicit_output_transform)):
            if logger:
              logger(loggers.LogLevel.WARN, 'The %s=%s hint is ignored because transformations for all outputs are fixed by the GTApprox/OutputTransformation option.' % (original_hint_name, original_hint_value,))
            accelerator_options['TryOutputTransformations'] = False


    elif hint_name == '@gtapprox/accelerator':
      global_phase_intensities = [0.2, 0.1, 0.05, 0.05, 0.05]
      accelerator_options['GTOpt/GlobalPhaseIntensity'] = global_phase_intensities[hint_value - 1]
      fixed_options['GTApprox/Accelerator'] = hint_value

      max_iterations = [0, 0, 50, 30, 20]
      accelerator_options['GTOpt/MaximumExpensiveIterations'] = max_iterations[hint_value - 1]

    elif hint_name == '@gtapprox/trainingsubsampleratio':
      accelerator_options['TrainingSubsampleRatio'] = hint_value

    elif hint_name == '@gtapprox/acceptablequalitylevel':
      accelerator_options['AcceptableQualityLevel'] = hint_value

    elif hint_name == '@gtapprox/tolerance':
      accelerator_options['GTOpt/ObjectiveTolerance'] = hint_value

    elif hint_name == '@gtapprox/qualitymetrics':
      quality_metric = hint_value

      if 'r^2' == quality_metric.lower():
        implicit_accelerator_options['AcceptableQualityLevel'] = 1. - _get_default_accelerator_options()['AcceptableQualityLevel']**2
      elif 'rrms' != quality_metric.lower():
        implicit_accelerator_options['AcceptableQualityLevel'] = 0.

    elif hint_name == '@gtapprox/datafeatures':
      hint_value = _lower_case_list(hint_value)

      incompatible_features = [('Quadratic', ['Linear']),
                               ('Linear', ['Discontinuous', 'TensorStructure']),
                               ('Quadratic', ['Discontinuous', 'TensorStructure']),
                               ('Discontinuous', ['TensorStructure']), ]
      for preferred_feature, submissive_features in incompatible_features:
        if preferred_feature.lower() in hint_value:
          for submissive_feature in submissive_features:
            if submissive_feature.lower() in hint_value:
              if logger:
                logger(loggers.LogLevel.WARN, '\'%s\' and \'%s\' data features are mutually exclusive: ignoring \'%s\'.' % (preferred_feature, submissive_feature, submissive_feature,))
              hint_value.remove(submissive_feature.lower())

      if 'discontinuous' in hint_value:
        techniques = opt_options['GTApprox/Technique']['bounds'].intersection(['hda', 'moa'])
        if not 'smooth' in _lower_case_list(hints.get('@GTApprox/ModelFeatures', [])):
          for tech_name in ['gbrt', 'pla', 'tbl']:
            if tech_name in opt_options['GTApprox/Technique']['bounds']:
              techniques.add(tech_name)
        opt_options['GTApprox/Technique']['bounds'] = techniques

      if 'linear' in hint_value:
        del opt_options['GTApprox/Technique']
        fixed_options['GTApprox/Technique'] = 'RSM'
        fixed_options['GTApprox/RSMType'] = 'Linear'

      if 'quadratic' in hint_value:
        del opt_options['GTApprox/Technique']
        fixed_options['GTApprox/Technique'] = 'RSM'
        opt_options['GTApprox/RSMType'] = {'bounds': ['Interaction', 'PureQuadratic', 'Quadratic'], 'init_value': 'PureQuadratic'}

      if 'dependentoutputs' in hint_value:
        fixed_options['GTApprox/DependentOutputs'] = True

      if 'tensorstructure' in hint_value:
        techniques = opt_options['GTApprox/Technique']['bounds'].intersection(['ta', 'ita', 'tgp'])
        opt_options['GTApprox/Technique']['bounds'] = techniques

    elif hint_name == '@gtapprox/modelfeatures':
      hint_value = _lower_case_list(hint_value)

      if 'accuracyevaluation' in hint_value:
        fixed_options['GTApprox/AccuracyEvaluation'] = True

      if 'smooth' in hint_value:
        accelerator_options['LandscapeAnalysis'] = True
        if 'GTApprox/Technique' in opt_options: # can be missing if 'Linear' or 'Quadratic' hint is set
          techniques = \
            opt_options['GTApprox/Technique']['bounds'].intersection(['splt', 'ta', 'tgp', 'ita', 'rsm', 'gp', 'sgp', 'hda', 'hdagp', 'moa'])
          opt_options['GTApprox/Technique']['bounds'] = techniques

      if 'exactfit' in hint_value:
        fixed_options['GTApprox/ExactFitRequired'] = True

      if 'gradient' in hint_value:
        if 'GTApprox/Technique' in opt_options: # can be missing if 'Linear' or 'Quadratic' hint is set
          techniques = opt_options['GTApprox/Technique']['bounds'].difference({'gbrt', 'tbl'})
          opt_options['GTApprox/Technique']['bounds'] = techniques


  for key in implicit_accelerator_options:
    if key not in accelerator_options:
      accelerator_options[key] = implicit_accelerator_options[key]

  if 'r^2' == quality_metric.lower():
    if accelerator_options['AcceptableQualityLevel'] > 1.:
      raise _ex.InvalidOptionsError('The @GTApprox/AcceptableQualityLevel=%s value is invalid R^2 metric value.' % accelerator_options['AcceptableQualityLevel'])
    else:
      r2_quality_level = accelerator_options['AcceptableQualityLevel']
      rrms_quality_level = np.sqrt(1. - r2_quality_level)
      if logger:
        logger(loggers.LogLevel.INFO, 'The acceptable R^2 level %g has been converted to equivalent RRMS level %g\n' % (r2_quality_level, rrms_quality_level))
      quality_metric = 'RRMS'
      accelerator_options['AcceptableQualityLevel'] = rrms_quality_level
  elif accelerator_options['AcceptableQualityLevel'] < 0.:
    raise _ex.InvalidOptionsError('The @GTApprox/AcceptableQualityLevel=%s value is invalid %s metric value.' % (accelerator_options['AcceptableQualityLevel'], quality_metric))

  if 'gtapprox/technique' in opt_options:
    if opt_options['GTApprox/Technique']['bounds']:
      techniques_order = _get_ordered_list_of_techniques()
      ordered_bounds = sorted([_.lower() for _ in opt_options['GTApprox/Technique']['bounds']], key=lambda x: techniques_order.index(x))
      opt_options['GTApprox/Technique']['bounds'] = ordered_bounds
      opt_options['GTApprox/Technique']['init_value'] = ordered_bounds[0]
    else:
      del opt_options['gtapprox/technique']

  if 'gtapprox/technique' not in opt_options and 'gtapprox/technique' not in fixed_options:
    raise _ex.InvalidOptionsError('There is no technique satisfying requirements of options and/or hints given.')

  if accelerator_options.get('LandscapeAnalysis', False):
    final_techniques_list = [_.lower() for _ in opt_options.get('GTApprox/Technique', {}).get('bounds', [user_tech])]
    if not any(_ in final_techniques_list for _ in ['ta', 'tgp', 'ita', 'gp', 'sgp', 'hda', 'moa', 'hdagp']):
      accelerator_options['LandscapeAnalysis'] = False

  # ATTENTION! If return tuple order will ever be changed then builder.Builder.build_smart method should be updated as well!
  return [quality_metric,], fixed_options, opt_options, accelerator_options

def _get_options_relevant_techniques(options):
  """
  Return list of techniques which are affected by options
  """
  all_techniques = _get_ordered_list_of_techniques()
  option_names_list = list(options.keys())
  relevant_techniques = []
  for technique in all_techniques:
    for option_name in option_names_list:
      if technique in option_name[9:].lower():
        relevant_techniques.append(technique)

  return relevant_techniques


class SmartSelector(object):
  "This class provides a simple interface for smart selection of technique for GTApprox"
  def __init__(self, fixed_options=None, opt_options=None, hints=None, logger=None, watcher=None,
               approx_builder=None, initial_model=None, categorical_inputs_map=None, categorical_outputs_map=None):
    self.fixed_options = fixed_options
    self.opt_options = opt_options
    self.hints = hints
    self.__logger = logger
    self.__watcher = watcher
    self.approx_builder = approx_builder
    self.initial_model = initial_model
    self.techniques = ["RSM", "SPLT", "HDA", "SGP", "HDAGP",
                       "TGP", "GP", "iTA", "TA", "MoA", "GBRT"]
    self.optimization_problem = None
    self.accelerator_options = {}
    self.quality_metrics = ['RRMS']
    self.categorical_inputs_map = categorical_inputs_map
    self.categorical_outputs_map = categorical_outputs_map

  def _remove_auto_options(self, options):
    ignorable_string = ("GTApprox/Technique", "GTApprox/Componentwise", "GTApprox/SubmodelTraining", "GTApprox/DependentOutputs",
                        "GTApprox/SPLTContinuity", "GTApprox/HDAFDLinear", "GTApprox/HDAFDSigmoid", "GTApprox/HDAFDGauss", "GTApprox/GPType",
                        "GTApprox/GPLinearTrend", "GTApprox/GPTrendType", "GTApprox/Heteroscedastic", "GTApprox/GPLearningMode",
                        "GTApprox/TensorFactors", "GTApprox/TAReducedBSPLModel", "GTApprox/TALinearBSPLExtrapolation", "GTApprox/RSMType",
                        "GTApprox/RSMFeatureSelection", "GTApprox/RSMStepwiseFit/inmodel", "GTApprox/MoATechnique", "GTApprox/MoACovarianceType",)

    ignorable_float_auto = ("GTApprox/GPPower",)

    ignorable_float_0 = ("GTApprox/MaxAxisRotations", "GTApprox/HDAPhaseCount", "GTApprox/HDAPMin", "GTApprox/HDAPMax", "GTApprox/HDAMultiMin",
                         "GTApprox/HDAMultiMax", "GTApprox/SGPNumberOfBasePoints", "GTApprox/TAModelReductionRatio", "GTApprox/GBRTMaxDepth",
                         "GTApprox/GBRTNumberOfTrees",)

    for k in ignorable_string:
      if k in options and str(options[k]).lower() == 'auto':
        options.pop(k)

    for k in ignorable_float_0:
      if k in options and not _shared.parse_float(options[k]):
        options.pop(k)

    for k in ignorable_float_auto:
      if k in options and np.isnan(_shared.parse_float_auto(options[k], np.nan)):
        options.pop(k)

    return options

  def _process_options(self, fixed_options, opt_options, hints, size_y):
    if not opt_options is None and not hints is None:
      raise _ex.InvalidOptionsError('Hints and opt_options are both provided! Please specify either hints or opt_options!')

    fixed_options = CaseInsensitiveDict() if not fixed_options else self._remove_auto_options(CaseInsensitiveDict(fixed_options))
    user_technique = self._read_option_value(fixed_options, 'GTApprox/Technique', 'auto')

    # if hints are not provided this will return empty quality_metrics and hints options and default accelerator_options
    error_types, hints_fixed_options, hints_opt_options, accelerator_options = _get_default_hints_options(hints, explicit_user_options=fixed_options)

    if opt_options is not None:
      opt_options = CaseInsensitiveDict(opt_options)
      opt_options['//SmartSelection/HintsBasedOptions'] = False
    else:
      opt_options = hints_opt_options
      opt_options['//SmartSelection/HintsBasedOptions'] = True

    fixed_options = _merge_dicts(hints_fixed_options, fixed_options, override=True)

    # Get list of techniques to optimize
    if 'GTApprox/Technique' in hints_fixed_options:
      opt_techniques = [hints_fixed_options['GTApprox/Technique'].lower()]
    else:
      opt_techniques = opt_options.get('GTApprox/Technique', {}).get('bounds', [])

    # Remove techniques from options to avoid possible conflicts
    opt_options.pop('GTApprox/Technique', None)

    if _shared.parse_json(fixed_options.get('GTApprox/CategoricalVariables', [])):
      # At this point the remaining categorical variables are encoded, which is not directly supported for tensor techniques.
      # The training sample have to be decomposed inside, however we were not able to validate the decomposition (e.g. to detect empty classes).
      opt_techniques = [_ for _ in opt_techniques if _.lower() not in ['ta', 'ita', 'tgp']]
      if not opt_techniques:
        # It can be fixed by disabling categorical variables encoding.
        # Try using the private option or passing setting EnabledTechniques hint with only tensor techniques.
        raise _ex.InvalidOptionsError('Unable to apply tensor techniques to categorical variables with encoding!')

    if self.categorical_outputs_map:
      opt_techniques = ['gbrt']
      if user_technique.lower() != "auto":
        fixed_options['GTApprox/Technique'] = user_technique = 'gbrt'
      if fixed_options.get('//ComponentwiseTraining/ActiveOutput') is not None or \
            np.all([i in self.categorical_outputs_map for i in np.arange(size_y)]):
        # Options for active categorical output were specified before
        error_types = ['LogLoss']
        accelerator_options['TryOutputTransformations'] = False
        accelerator_options['LandscapeAnalysis'] = False

    if user_technique.lower() != "auto": # technique was specified by user
      # check that techniques defined by hints contains technique specified by user
      if opt_techniques and user_technique.lower() not in _lower_case_list(opt_techniques):
        raise _ex.InvalidOptionsError('Specified technique is not compatible with provided hints!')
      opt_techniques = [user_technique]
    elif not opt_techniques:
      opt_techniques = _get_options_relevant_techniques(opt_options)

    if accelerator_options.get('LandscapeAnalysis', False) and _shared.parse_bool(self._read_option_value(fixed_options, 'GTApprox/ExactFitRequired', False)):
      raise _ex.InvalidOptionsError("The 'exact fit' requirement is incompatible with the 'smooth' model requirement.")

    time_limit = accelerator_options.get('TimeLimit', 0)
    if time_limit:
      fixed_options["/GTApprox/TimeLimit"] = time_limit
      if not _shared.parse_bool(fixed_options.get("//GTApprox/AdaptiveAccelerator", True)):
        fixed_options['GTApprox/Accelerator'] = int(fixed_options.get('GTApprox/Accelerator', 3))
    else:
      fixed_options['GTApprox/Accelerator'] = int(fixed_options.get('GTApprox/Accelerator', 3))

    if "GTApprox/TensorFactors" in fixed_options:
      # if any tensor factor has explicit technique (except "DV" marker) then TA is the only technique to use
      for tensor_factor in _shared.parse_json(self._read_option_value(fixed_options, 'GTApprox/TensorFactors', [])):
        if tensor_factor and isinstance(tensor_factor[-1], string_types) and tensor_factor[-1].lower() in ("bspl", "gp", "hda", "lr0", "lr", "pla", "sgp"):
          opt_techniques = ["ta"]
          break

    return fixed_options, opt_options, accelerator_options, error_types, opt_techniques

  def _read_option_value(self, options_collection, option_name, emergency_default):
    try:
      if option_name in options_collection:
        return options_collection[option_name]
      return self.approx_builder.options.info(option_name)['OptionDescription']['Default']
    except:
      pass
    return emergency_default

  def _prepare_optimizer(self, x, y, x_test, y_test, w_test, output_noise_variance, comment, weights, initial_model, restricted_x, landscape_analyzer=None):
    fixed_options, opt_options, self.accelerator_options, self.quality_metrics, techniques = self._process_options(self.fixed_options, self.opt_options, self.hints, y.shape[1])

    optimizer = SmartSelectionOptimizer(x, y,
                                        x_test=x_test, y_test=y_test, w_test=w_test,
                                        techniques=techniques,
                                        fixed_options=fixed_options,
                                        opt_options=opt_options,
                                        accelerator_options=self.accelerator_options,
                                        error_types=self.quality_metrics,
                                        approx_builder=self.approx_builder,
                                        output_noise_variance=output_noise_variance,
                                        comment=comment, weights=weights, landscape_analyzer=landscape_analyzer,
                                        initial_model=initial_model, restricted_x=restricted_x,
                                        logger=self.__logger, watcher=self.__watcher,
                                        categorical_inputs_map=self.categorical_inputs_map,
                                        categorical_outputs_map=self.categorical_outputs_map)
    return optimizer

  def build(self, x, y, x_test=None, y_test=None, w_test=None, output_noise_variance=None, comment=None, weights=None, initial_model=None, restricted_x=None, landscape_analyzer=None):
    if self.fixed_options is not None:
      self.approx_builder.options.set(self.fixed_options)

    optimizer = self._prepare_optimizer(x, y, x_test, y_test, w_test, output_noise_variance, comment, weights, initial_model, restricted_x, landscape_analyzer)

    smart_phases = {'current smart phase': 0,
                    'number of smart phases': 0,
                    'smart phase technique': [],
                    'smart phase techniques': [_.lower() for _ in optimizer.techniques]}

    for problem in optimizer.optimization_problems:
      smart_phases['number of smart phases'] += max(1, problem.number_of_phases_estimate)

      if x_test is None or y_test is None:
        # Estimate number of IV rounds
        smart_phases['number of smart phases'] *= technique_selection._read_iv_options_impl(
                                                    int(self._read_option_value(self.fixed_options, 'GTApprox/IVSubsetCount', 0)),
                                                    int(self._read_option_value(self.fixed_options, 'GTApprox/IVSubsetSize', 0)),
                                                    int(self._read_option_value(self.fixed_options, 'GTApprox/IVTrainingCount', 0)),
                                                    x.shape[0], False)[1]

    if self.__watcher and not self.__watcher(smart_phases):
      raise _ex.UserTerminated()

    return optimizer.solve() + (self.quality_metrics,)
