#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import copy
import time
import numpy as np

from .core_ic import _MultiRoute

from ..six import StringIO
from .. import exceptions as _ex
from .. import shared as _shared

class CaseInsensitiveDict(dict):
  def __init__(self, *args, **kwargs):
    # This is a solution to problem with load_module,
    # details are here https://thingspython.wordpress.com/2010/09/27/another-super-wrinkle-raising-typeerror/
    self.__as_super = super(CaseInsensitiveDict, self)
    self.__as_super.__init__(*args, **kwargs)
    self.__mapping = dict((k.lower(), k) for k in self.__as_super.keys())

  def __setitem__(self, key, value):
    key_lower = key.lower()
    if key_lower in self.__mapping:
      self.__as_super.__delitem__(self.__mapping[key_lower])
    self.__as_super.__setitem__(key, value)
    self.__mapping[key_lower] = key

  def __getitem__(self, key):
    return self.__as_super.__getitem__(self.__mapping[key.lower()])

  def __delitem__(self, key):
    mapped_key = self.__mapping[key.lower()]
    del self.__mapping[key.lower()]
    return self.__as_super.__delitem__(mapped_key)

  def __contains__(self, key):
    return key.lower() in self.__mapping

  def has_key(self, key):
    return key.lower() in self.__mapping

  def get(self, key, default=None):
    return self.__as_super.__getitem__(self.__mapping[key.lower()]) if key.lower() in self.__mapping else default

  def clear(self):
    self.__as_super.clear()
    self.__mapping.clear()

  def setdefault(self, k, d):
    self.__mapping[k.lower()] = k
    return self.__as_super.setdefault(k, d)

  def pop(self, key, *args):
    key_lower = key.lower()
    if key_lower in self.__mapping:
      return self.__as_super.pop(self.__mapping.pop(key_lower))
    return self.__as_super.pop(key, *args)

  def popitem(self):
    k, v = self.__as_super.popitem()
    self.__mapping.pop(k.lower())
    return k, v

  def copy(self):
    return CaseInsensitiveDict(self)

  def update(self, E, **F):
    if hasattr(E, 'keys'):
      for k in E:
        self[k] = E[k]
    else:
      for k, v in E:
        self[k] = v
    for k in F:
      self[k] = F[k]

def _get_ordered_list_of_techniques():
  """
  Return list of techniques. The order of techniques does matter. In this order brute force search must be conducted.
  """
  return ['rsm', 'splt', 'ta', 'tgp', 'ita', 'gp', 'sgp', 'pla', 'gbrt', 'hda', 'hdagp', 'moa', 'tbl']


def _merge_dicts(dictionary, another_dictionary, override=False):
  """
  Add elements from another dictionary to the dictionary.
  If they have the same key with different values, then
    * if values are dictionaries with field 'bounds'
    * raise an exception


  If override is True, then items with the same key and different values will be
  overrided by items from another_dictionary

  """
  if dictionary is None or another_dictionary is None:
    return dictionary if another_dictionary is None else another_dictionary

  merged_dictionary = CaseInsensitiveDict(dictionary)
  if override:
    merged_dictionary.update(another_dictionary)
  else:
    merged_dictionary.update((k, another_dictionary[k]) for k in another_dictionary if k not in dictionary)

  return merged_dictionary


def _guess_init_value(option_name, option_value, default_option_value=None):
  """
  Get initial value for opt_options if not passed: use the lower bound

  Note: opt_options must have bounds
  """
  if 'init_value' in option_value:
    # check that init_value lies in specified bounds
    if _shared.is_numerical(option_value['init_value']) and option_value.get('type', '').lower() != 'enum':
      if option_value['init_value'] > option_value['bounds'][1] or option_value['init_value'] < option_value['bounds'][0]:
        raise _ex.InvalidOptionsError("Initial value of option '%s' lies outside specified bounds!" % option_name)
    elif not option_value['init_value'] in option_value['bounds']:
      raise _ex.InvalidOptionsError("Initial value of option '%s' lies outside specified bounds!" % option_name)

    return option_value['init_value']

  if default_option_value:
    init_value = default_option_value.get('init_value', option_value['bounds'][0])
  else:
    init_value = option_value['bounds'][0]

  # init_value should lie within bounds
  init_value = min(init_value, option_value['bounds'][1])
  init_value = max(init_value, option_value['bounds'][0])
  return init_value

_RANGES_REPLS = (('(', '['), (')', ']'), ('nan', 'NaN'), ('+inf', 'Infinity'), ('-inf', '-Infinity'),)

def _guess_bounds(option_name, option_value, approx_options, default_option_value=None):
  """
  Get bounds for opt_options if not passed use global option bounds
  """
  # obtain global bounds from option info
  # approx_options is needed to obtain bounds from option info
  option_info = approx_options.info(option_name)['OptionDescription']
  trivial_values = []

  if 'Ranges' in option_info: # numerical option
    range_string = option_info['Ranges']
    for key, repl in _RANGES_REPLS:
      range_string = range_string.replace(key, repl)
    bounds = [_shared.parse_float(_) for _ in _shared.parse_json(range_string)]
  elif 'Boolean' in option_info.get('TrueType', ''):
    bounds = [False, True]
  elif 'Values' in option_info: # categorical option
    values = option_info['Values']
    if 'Auto' in values:
      values.remove('Auto')
      trivial_values.append('Auto')
    if 'BIC' in values: # kind of 'Auto'
      values.remove('BIC')
      trivial_values.append('BIC')
    bounds = values
  elif 'unsigned' in option_info['TrueType']: # vector of integers
    bounds = [0, np.inf]
  else: # vector of doubles in range [0, 1]
    bounds = [0, 1]

  if 'bounds' in option_value:
    # In case of enum values that should be in a given range (e.g. if going over certain GPPower values)
    if option_value.get('type', '').lower() == 'enum' and all(_shared.is_numerical(_) for _ in option_value['bounds']):
      for allowed_value in option_value['bounds']:
        if bounds[0] > allowed_value or bounds[1] < allowed_value:
          raise _ex.InvalidOptionsError('Incorrect bounds are specified!')
    # check that specified bounds don't violate bounds from option_info
    elif _shared.is_numerical(option_value['bounds'][0]):
      if bounds[0] > option_value['bounds'][0] or bounds[1] < option_value['bounds'][1]:
        raise _ex.InvalidOptionsError('Incorrect bounds are specified!')
    else:
      # for categorical options check that intersection of global bounds and specified bounds coincides with specified bounds
      lower_case_bounds = set(_lower_case_list(bounds))
      lower_case_options_bounds = _lower_case_list(option_value['bounds'])
      lower_case_bounds.update(_ for _ in _lower_case_list(trivial_values) if _ in lower_case_options_bounds) # restore removed valid option values if they are in the user-defined bounds
      if len(lower_case_bounds.intersection(lower_case_options_bounds)) != len(lower_case_options_bounds):
        raise _ex.InvalidOptionsError('Incorrect bounds are specified for %s: %s not in allowed set %s' % (option_name, [_ for _ in lower_case_options_bounds if _ not in lower_case_bounds], [_ for _ in lower_case_bounds]))

    return option_value['bounds']

  if default_option_value:
    return default_option_value['bounds']

  # bounds are not specified in opt_options, option_name is not in default options
  return bounds


def _guess_option_type(option_name, option_value, approx_options):
  """
  Get option type ('Enum', 'Integer' or 'Continuous'): from default_options
  or from the true type of the option.
  The function also returns true type
  """
  option_type = None
  option_true_type = None

  option_info = approx_options.info(option_name)['OptionDescription']

  types = {'int': 'Integer',
           'unsigned': 'Integer',
           'double': 'Continuous'}

  # guess option type
  if 'type' in option_value:
    if not option_value['type'].lower() in ['continuous', 'integer', 'enum']:
      raise _ex.InvalidOptionsError("Invalid option type '%s' is specified! Possible values are 'Continuous', 'Integer' and 'Enum'." % \
                                    option_value['type'])
    option_type = option_value['type']

  # still None? Parse option_info
  if option_type is None:
    if option_info['Type'] == 'string': # list of doubles or integers
      if 'double' in option_info['TrueType']:
        option_type = 'Continuous'
      else:
        option_type = 'Integer'
    elif 'Values' in option_info: # categorical option
      option_type = 'Enum'
    else:
      option_type = types[option_info['Type']]

  # guess option true type
  option_true_type = option_info.get("TrueType", "").lower()
  if "vector" in option_true_type:
    option_true_type = "vector" if "scalar" not in option_true_type else option_info['Type']
  elif 'Values' in option_info:
    option_true_type = "int"
  else:
    option_true_type = option_info['Type']

  return option_type, option_true_type


def _get_correct_opt_options(opt_options, approx_options, default_options=None):
  if not opt_options:
    return CaseInsensitiveDict()

  opt_options_copy = CaseInsensitiveDict(copy.deepcopy(dict(opt_options)))
  # set correct bounds, type and true_type for opt_options
  for option_name, option_value in opt_options_copy.items():
    if option_value:
      try:
        _shared.check_concept_dict(option_value, "opt_options")
      except TypeError:
        raise _ex.InvalidOptionsError('Invalid opt_options structure!')

    default_option_value = None
    if default_options:
      default_option_value = default_options.get(option_name, None)

    option_value['type'], option_value['true_type'] = _guess_option_type(option_name, option_value, approx_options)
    option_value['bounds'] = _guess_bounds(option_name, option_value, approx_options, default_option_value)
    option_value['init_value'] = _guess_init_value(option_name, option_value, default_option_value)

  return opt_options_copy


def _lower_case_list(list_of_strings):
  return [x.lower() for x in list_of_strings] if list_of_strings is not None else []


class AcceptableLevelWatcher(object):
  """
  Watcher for interrupting GTOpt if acceptable level of objective functino is reached.
  """
  def __init__(self, optimization_problem, acceptable_level, other_watcher=None):
    self.optimization_problem = optimization_problem
    self.acceptable_level = acceptable_level
    self.__other_watcher = other_watcher
    if self.__other_watcher is not None:
      self_props = dir(self)
      for prop_name in dir(self.__other_watcher):
        if not prop_name.startswith('_') and prop_name not in self_props:
          setattr(self, prop_name, getattr(self.__other_watcher, prop_name))

  def __call__(self, reserved=None):
    # call external watcher first (just to report 'reserved' parameter)
    if self.__other_watcher and not self.__other_watcher(reserved):
      return False
    return self.optimization_problem.min_error > self.acceptable_level


class TrainingTimeWatcher(object):
  """
  Watcher for interrupting if training time (in seconds) is larger than predefined value
  """
  def __init__(self, time_limit, other_watcher=None, tolerance=None):
    time_limit = _shared.parse_float(time_limit)
    time_limit = np.ceil(time_limit) if np.isfinite(time_limit) and time_limit > 0. else np.inf

    self.__start_time = time.time()
    self.__last_tick = self.__start_time

    self.__other_watcher = other_watcher
    if self.__other_watcher is not None:
      self_props = dir(self)
      for prop_name in dir(self.__other_watcher):
        if not prop_name.startswith('_') and prop_name not in self_props:
          setattr(self, prop_name, getattr(self.__other_watcher, prop_name))

    if np.isfinite(time_limit):
      self.__time_limit = float(time_limit)

      self.__tolerance = max(0., _shared.parse_float(tolerance)) if tolerance is not None else np.nan
      if not np.isfinite(self.__tolerance):
        self.__tolerance = min(1., 1. / (np.finfo(float).eps + np.log(time_limit + 1.)))
      self.__tolerance *= self.__time_limit

      self.__stop_time = self.__start_time + self.__time_limit
    else:
      self.__time_limit = np.inf
      self.__tolerance = 0.
      self.__stop_time = np.inf

  def __call__(self, reserved=None):
    self.__last_tick = time.time()

    # call external watcher first (just to report 'reserved' parameter)
    if self.__other_watcher and not self.__other_watcher(reserved):
      return False
    return self.__last_tick < self.__stop_time

  def time_left(self):
    return max(self.__stop_time - self.__last_tick, 0.) if np.isfinite(self.__stop_time) else np.inf

  @property
  def time_limit(self):
    return self.__time_limit

  def overhead_allowed(self, overhead):
    if (self.__last_tick + overhead) > (self.__stop_time + self.__tolerance):
      return False
    if self.__other_watcher:
      return self.__other_watcher(None)
    return True

class Hyperparameters(object):
  """
  Hyperparameters of GTApprox.

  :param opt_options: hyperparameters to tune. It is a dict with the following fields
                      <option_name>: dict with keys 'bounds', 'init_value', 'type', 'true_type'
  :
  """
  def __init__(self, gtapprox_options, opt_options=None, default_options=None, is_user_defined=False):
    self.gtapprox_options = gtapprox_options
    self.values = _get_correct_opt_options(opt_options, gtapprox_options, default_options)
    self.values = CaseInsensitiveDict(self.values)
    self.is_user_defined = is_user_defined

  def __contains__(self, key):
    return key in self.values

  def __nonzero__(self):
    return bool(self.values)

  def __bool__(self):
    return self.__nonzero__()

  def __getitem__(self, key):
    return self.values[key]

  def __iter__(self):
    return iter(self.values)

  def __str__(self):
    return self.values.__str__()

  def update(self, new_hyperparameters, override=False):
    if isinstance(new_hyperparameters, Hyperparameters):
      correct_opt_options = new_hyperparameters.values
    else:
      correct_opt_options = _get_correct_opt_options(new_hyperparameters, self.gtapprox_options)

    self.values = _merge_dicts(self.values, correct_opt_options, override=override)

  def remove(self, option_name):
    self.values.pop(option_name, None)

  def get_bounds(self, key, default=None):
    if key in self.values:
      return self.values[key]['bounds']
    return default

  def get_init_value(self, key, default=None):
    if key in self.values:
      return self.values[key]['init_value']
    return default

  def get_true_type(self, key):
    if key in self.values:
      return self.values[key]['true_type']
    return None

  def set_bounds(self, key, bounds, init_value=None):
    if key in self.values:
      self.values[key]['bounds'] = bounds
      self.values[key]['bounds'] = _guess_bounds(key, self.values[key], self.gtapprox_options)
      if init_value is not None:
        self.values[key]['init_value'] = init_value
    else:
      raise ValueError('No such key in Hyperparmaters opt_options!')

  def keys(self):
    return self.values.keys()

  def items(self):
    return self.values.items()

  def difference(self, other_options):
    """
    Remove from self.opt_options all options from other_options
    """
    for option_name in other_options:
      if option_name in self.values:
        self.remove(option_name)
    return self

  def intersection(self, other_options):
    if not isinstance(other_options, Hyperparameters):
      _shared.check_concept_dict(other_options, "hyperparameters")

    intersection = Hyperparameters(self.gtapprox_options)
    intersection_options = dict((key, other_options[key]) for key in other_options if key in self.values)
    intersection.update(intersection_options)

    return intersection

def _pretty_print_options(title, options):
  items = [(key, options[key]) for key in options if not key.startswith('/')]

  stream = StringIO()
  stream.write(title)

  if not items:
    stream.write(' { }')
  else:
    for item in items:
      stream.write('\n  %s = %s' % item)

  return stream.getvalue()

class _LandscapeValidator(object):
  def __init__(self, landscape_analyzer, test_x, test_y, test_w):
    self.landscape_analyzer = landscape_analyzer
    self.validation_dataset = (test_x, test_y, test_w) if test_x is not None and test_y is not None else None

  @staticmethod
  def _cmp_ratio(x, y, eps):
    return 0. if x == y else -abs(y) / (eps + abs(x)) if x < y else abs(x) / (eps + abs(y))

  @staticmethod
  def better_landscape(base_error, base_landscape_err, new_error, new_landscape_err):
    if base_landscape_err is None or base_landscape_err.get("landscape") is None \
     or new_landscape_err is None or new_landscape_err.get("landscape") is None:
      return base_error > new_error

    # Do we need test sample errors here to compare landscapes??
    # err_values = [_LandscapeValidator._cmp_ratio(base_error, new_error, 1.e-5)]
    err_values = []
    for key in base_landscape_err["landscape"].keys():
      err_values.extend(_LandscapeValidator._cmp_ratio(base_landscape_err["landscape"][key][i], new_landscape_err["landscape"][key][i], 1.e-5) for i in range(len(base_landscape_err["landscape"][key])))
    err_pareto = [-1 if ratio <= -1.1 else 1 if ratio >= 1.1 else 0 for ratio in err_values]
    if np.count_nonzero(err_pareto) >= (len(err_pareto) + 1) // 2:
      if all(_ >= 0 for _ in err_pareto):
        return True
      elif all(_ <= 0 for _ in err_pareto):
        return False

    if base_landscape_err.get("validation") is not None and new_landscape_err.get("validation") is not None:
      base_error = (base_error + _get_aggregate_errors(base_landscape_err["validation"]) * _MultiRoute.IMAG_POINTS_WEIGHT) / (1. + _MultiRoute.IMAG_POINTS_WEIGHT)
      new_error = (new_error + _get_aggregate_errors(new_landscape_err["validation"]) * _MultiRoute.IMAG_POINTS_WEIGHT) / (1. + _MultiRoute.IMAG_POINTS_WEIGHT)
    else:
      # np.fabs is workaround for the numpy 1.6 bug: np.hypot.reduce([-1.]) returns -1.
      base_error *= np.fabs(np.hypot.reduce(np.array(list(base_landscape_err["landscape"].values())).flatten()))
      new_error *= np.fabs(np.hypot.reduce(np.array(list(new_landscape_err["landscape"].values())).flatten()))

    return base_error > new_error

  @staticmethod
  def better_solution(base_solution, new_solution):
    if new_solution is None or new_solution.optimal_options is None:
      return False
    elif base_solution is None:
      return True

    return _LandscapeValidator.better_landscape(base_solution.min_error, base_solution.min_la_errors, new_solution.min_error, new_solution.min_la_errors)

  def calc_landscape_errors(self, model, error_types):
    if model is not None and self.landscape_analyzer is not None:
      try:
        aggregate_validation_error = None
        if self.validation_dataset is not None:
          validation_errors = model.validate(*self.validation_dataset)
          if error_types[0] in validation_errors:
            aggregate_validation_error = validation_errors[error_types[0]]
        return {"landscape": self.landscape_analyzer.validate_landscape(model), "validation": aggregate_validation_error}
      except:
        pass
    return None

def _get_aggregate_errors(errors):
  # returns aggregated error for multi-dimensional output mode
  return np.max(errors)
