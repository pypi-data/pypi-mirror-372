#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

from pprint import pformat
import random
from datetime import datetime
import ctypes as _ctypes
import numpy as np
import numpy.random as rnd

from ..six import string_types
from ..six.moves import range, StringIO

from .. import blackbox as _blackbox
from ..utils import bbconverter as _bbconverter

from .. import shared as _shared
from .. import options as _options
from .. import exceptions as _ex

from . import selector as _selector
from . import ranker as _ranker
from . import checker as _checker
from . import utils as _utils
from ..utils import buildinfo as _buildinfo
from .. import status as _status
from .. import license as _license

from .. import __version__

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.void_ptr_ptr = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)

    self.builder_create = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTSDABuilderAPINew", self.__library))
    self.builder_options_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTSDABuilderAPIGetOptionsManager", self.__library))
    self.builder_license_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTSDABuilderAPIGetLicenseManager", self.__library))
    self.builder_release = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTSDABuilderAPIFree", self.__library))

    self.maxparallel_begin = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_int)(('GTSDASetupParallelization', self.__library))
    self.maxparallel_finish = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTSDACleanupParallelization', self.__library))


_api = _API()

class _Backend(object):
  def __init__(self, api=_api):
    self.__api = api

    # copy attributes from _API
    for _ in dir(self.__api):
      if not _.startswith("_"):
        setattr(self, _, getattr(self.__api, _))

    self.__instance = self.builder_create(_ctypes.c_void_p(), _ctypes.c_void_p())
    if not self.__instance:
      raise Exception("Cannot initialize GT SDA API.")

  def __del__(self):
    if self.__instance:
      self.builder_release(self.__instance)
      self.__instance = None

  @property
  def options_manager(self):
    manager = _ctypes.c_void_p()
    if not self.builder_options_manager(self.__instance, _ctypes.byref(manager)):
      raise _ex.InternalError("Cannot connect to the options manager interface.")
    return manager

  @property
  def license_manager(self):
    manager = _ctypes.c_void_p()
    if not self.builder_license_manager(self.__instance, _ctypes.byref(manager)):
      raise _ex.InternalError("Cannot connect to the license manager interface.")
    return manager


def _pformat_array(prefix, array, max_line_width=60, precision=5, suppress_small=True, separator=","):
  return "%s%s" % (prefix, np.array2string(array, max_line_width=max_line_width, precision=precision,
                                           suppress_small=suppress_small, separator=separator, prefix=prefix))

class RankResult(object):
  r"""SDA Rank final results. An object of this class is only returned by :meth:`Analyzer.rank()` and should never be instantiated by user.

    attribute: info

      type: ``dict``

      SDA procedure information.

    attribute: scores

      type: ``list[list[float]]``

      Resulting scores for the input variables (features).

      The scores matrix contains `dim(Y)` rows and `dim(X)` columns (`dim` is dimensionality).
      Each element of this matrix `s_{ij}` is the sensitivity of the *i*\ -th output component to the *j*\ -th
      component of the input (a feature). In general, `s_{ij}` is a positive ``float`` number, except some special
      cases:

      * In the sample-based mode, if the value of the *j*\ -th feature in the sample is constant (the input sample, contains a constant column),
        all scores of this feature (*j*\ -th score matrix column) will be ``nan`` since there is no way to estimate the sensitivity of the output
        to a constant component.
      * In the sample-based mode, if the value of the *i*\ -th response component in the sample is constant
        (the output sample, contains a constant column), the scores of all features *vs* this output (*i*\ -th score matrix row) will be ``0.0``
        --- it is assumed that this output is insensitive to all features since its value is constant.
      * The first of the above rules has priority: if the sample contains both a constant feature `x_j`
        and a constant output `y_i`, the `s_{ij}` score is ``nan``.
      * In the blackbox-based mode, if the lower and upper bounds of a feature are equal,
        it is interpreted as a constant input, so the resulting score for this feature will be ``nan``,
        similarly to the sample-based mode with a constant column.


    attribute: std

      type: ``list[list[float]]``

      Scores standard deviation.

      Standard deviation matrix is structurally similar to the scores matrix: it also contains
      `dim(Y)` rows and `dim(X)` columns, and each element `\sigma_{ij}` is the standard deviation
      of the `s_{ij}` score. In general, `\sigma_{ij}` is a non-negative ``float`` number, except the following
      special cases:

      * If `s_{ij}` score is ``nan`` (such as the scores of constant features), `\sigma_{ij}` is also set to ``nan``.
      * Estimation of std may fail due to insufficient data. Again, such `\sigma` values are set to ``nan``. This may
        happen even if there is enough data to estimate the corresponding score (so the score is not ``nan``, but its deviation is).
        One of the examples where it is possible is a blackbox-based SDA run with a blackbox that frequently outputs ``nan``
        values: the output data may be sufficient to estimate its score, but insufficient to perform the cross-validation process
        that is used to calculate score deviation.
  """

  def __init__(self, status, info, scores, variances, approx_model=None, generated_sample=None):
    _shared.check_concept_dict(info, 'c-tor argument')
    object.__setattr__(self, 'status', status)
    object.__setattr__(self, 'info', dict((k, info[k]) for k in info))
    object.__setattr__(self, 'scores', _shared.as_matrix(scores, name="Resulting scores for the input variables ('scores' argument)"))
    if approx_model is not None:
      object.__setattr__(self, 'approx_model', approx_model)
    if generated_sample:
      generated_sample['inputs'] = _shared.as_matrix(generated_sample['inputs'], name="Input part of the generated sample")
      generated_sample['outputs'] = _shared.as_matrix(generated_sample['outputs'], name="Output part of the generated sample")
      object.__setattr__(self, 'generated_sample', generated_sample)

    if variances is not None:
      variances = _shared.as_matrix(variances, name="Variance of the resulting scores ('variances' argument)")
      standard_deviations = np.sqrt(variances)
      object.__setattr__(self, 'std', standard_deviations)
      object.__setattr__(self, 'variances', variances)

    str_repr = StringIO()
    try:
      str_repr.write("SDA feature ranking result:\n")
      str_repr.write("  status: %s\n" % str(self.status))
      for output_index in range(self.scores.shape[0]):
        if variances is not None:
          str_repr.write("\n")
        str_repr.write(_pformat_array(("  y[%d] scores:    " % output_index), self.scores[output_index]) + "\n")
        if variances is not None:
          str_repr.write(_pformat_array(("  y[%d] std. dev.: " % output_index), self.std[output_index]) + "\n")
    except:
      pass

    object.__setattr__(self, '_RankResult__str_repr', str_repr.getvalue()[:-1])

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

  def __str__(self):
    return self.__str_repr

class SelectResult(object):
  r"""SDA Select final results. An object of this class is only returned by :meth:`Analyzer.select()` and should never be instantiated by user.

    attribute: info

      type: ``dict``

      SDA Select procedure information.

    attribute: feature_list

      type: ``list[int]``

      List of chosen input variables (features).

    attribute: validation_error

      type: ``float``

      List of chosen input variables (features).
  """

  def __init__(self, status, info, feature_list, validation_error, approx_model):
    _shared.check_concept_dict(info, 'c-tor argument')
    object.__setattr__(self, 'status', status)
    object.__setattr__(self, 'info', info)
    object.__setattr__(self, 'feature_list', _shared.as_matrix(feature_list, dtype=np.int32, name="List of chosen variables ('feature_list' argument)"))
    object.__setattr__(self, 'validation_error', validation_error)
    if approx_model is not None:
      object.__setattr__(self, 'approx_model', approx_model)

    str_repr = StringIO()
    try:
      str_repr.write("SDA feature selection result:\n")
      str_repr.write("  status:           %s\n" % str(self.status))
      str_repr.write("  validation error: %s\n" % str(self.validation_error))
      str_repr.write(_pformat_array("  feature list:     ", self.feature_list, precision=0))
    except:
      pass
    object.__setattr__(self, '_SelectResult__str_repr', str_repr.getvalue())

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

  def __str__(self):
    return self.__str_repr

class CheckResult(object):
  r"""SDA Check final results. An object of this class is only returned by method `Analyzer.check()` and should never be instantiated by user.

    attribute: info

      type: ``dict``

      SDA Check procedure information.

    attribute: scores

     type: ``list[double]``

     List of scores of input variables.

    attribute: p_values

     type: ``list[double]``

     List of p-values of scores

    attribute: decisions

     type: ``list[bool]``

     List of bools of existing dependency.
  """

  def __init__(self, status, info, scores, p_values, decisions):
    _shared.check_concept_dict(info, 'c-tor argument')
    object.__setattr__(self, 'status', status)
    object.__setattr__(self, 'info', dict((k, info[k]) for k in info))
    object.__setattr__(self, 'scores', _shared.as_matrix(scores, name="List of scores of input variables ('scores' argument)"))

    object.__setattr__(self, 'p_values', _shared.as_matrix(p_values, name="List of p-values of scores ('p_values' argument)"))
    object.__setattr__(self, 'decisions', _shared.as_matrix(decisions, name="List of existing dependency indicators ('decisions' argument)"))

    str_repr = StringIO()
    try:
      str_repr.write("SDA correlation check result:\n")
      for output_index in range(self.scores.shape[0]):
        str_repr.write(_pformat_array(("  y[%d] scores:    " % output_index), self.scores[output_index]) + "\n")
        str_repr.write(_pformat_array(("  y[%d] p-values:  " % output_index), self.p_values[output_index]) + "\n")
        str_repr.write(_pformat_array(("  y[%d] decisions: " % output_index), self.decisions[output_index] > 0.) + "\n\n")
    except:
      pass
    object.__setattr__(self, '_CheckResult__str_repr', str_repr.getvalue()[:-2])

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

  def __str__(self):
    return self.__str_repr


class Analyzer(object):
  """GTSDA interface.

  Allows user to perform SDA procedure in two modes:

  - Sample-based SDA.
  - Blackbox-based SDA.

  """
  _SDA2APPROX_OPTIONS = ("MaxParallel",)

  def __init__(self, backend=None):
    """C-tor.
    """
    self._logger = None
    self._watcher = None
    self._backend = backend or _Backend()

  def set_logger(self, logger):
    """Set logger.

    param logger: Logger object
    return: none
    """
    self._logger = _shared.wrap_with_exc_handler(logger, _ex.LoggerException)

  def set_watcher(self, watcher):
    """Set watcher.

    param watcher: Watcher object
    return: none

    """
    self._set_watcher(_shared.wrap_with_exc_handler(watcher, _ex.WatcherException))

  def _set_watcher(self, watcher):
    old_watcher = self._watcher
    self._watcher = watcher
    return old_watcher

  @property
  def options(self):
    """Analyzer options.

    type: class da.p7core.Options

    General options interface for the analyzer. See section :ref:`gen_options` for usage and the GTSDA :ref:`ug_gtsda_options`.
    """
    return _options.Options(self._backend.options_manager, self._backend)

  @property
  def license(self):
    """Analyzer license.

    :type: :class:`~da.p7core.License`

    General license information interface. See section :ref:`gen_license_usage` for details.

    """
    return _license.License(self._backend.license_manager, self._backend)

  def _set_random_generator_state(self, seed=None, states=None):
    '''Set random generator options
    '''
    old_states = {}
    old_states['random'] = random.getstate()
    old_states['numpy.random'] = rnd.get_state()

    if not seed is None and states is None:
      random.seed(seed)
      rnd.seed(seed + 1)

    elif seed is None and not states is None:
      random.setstate(states['random'])
      rnd.set_state(states['numpy.random'])

    else:
      raise Exception("Can't set random generator state: only one of parameters seed or states should be set.")

    return old_states

  def _get_options_subset(self, include=None, exclude=None):
    '''Gets only options satisfying conditions
    '''
    # This call also checks if valid values are set for all options
    try:
      options = self.options._get()
    except:
      self.options.reset()
      self.options.set(self.saved_options)
      raise

    if 2 * int(self.options.get('GTSDA/Ranker/Screening/MorrisGridJump')) > int(self.options.get('GTSDA/Ranker/Screening/MorrisGridLevels')):
      raise _ex.InvalidOptionValueError("'GTSDA/Ranker/Screening/MorrisGridJump' should be smaller or equal then " +
                                        "half of 'GTSDA/Ranker/Screening/MorrisGridLevels' value")

    if not include is None:
      if isinstance(include, list):
        include_keys = [key for key in options if np.array([key.lower().startswith(element.lower()) for element in include]).any()]
      elif isinstance(include, string_types):
        include_keys = [key for key in options if key.lower().startswith(include.lower())]
      else:
        raise Exception('"include" parameter should be list or string')
      options = dict((include_key, options[include_key]) for include_key in include_keys)

    if not exclude is None:
      if isinstance(exclude, list):
        exclude_keys = [key for key in options if not np.array([key.lower().startswith(element.lower()) for element in exclude]).any()]
      elif isinstance(exclude, string_types):
        exclude_keys = [key for key in options if not key.lower().startswith(exclude.lower())]
      else:
        raise Exception('"exclude" parameter should be list or string')
      options = dict((exclude_key, options[exclude_key]) for exclude_key in exclude_keys)

    return options

  def _print_options(self, options, print_function):
    ''' Prints options as alphabetically sorted list
    '''
    for key in sorted(options.keys()):
      print_function('  ' + key + ' : ' + str(options[key]))

  def _translate_options(self, approx_options):
    if approx_options is not None and approx_options:
      # update options
      existing_options = [_.lower() for _ in approx_options]
      for option_name in self._SDA2APPROX_OPTIONS:
        if ("gtapprox/" + option_name.lower()) not in existing_options:
          approx_options["GTApprox/" + option_name] = self.options.get("GTSDA/" + option_name)
      return approx_options

    # new approx_options dict should be created so we'll do it only
    # if there are actual options to translate
    user_options = [_.lower() for _ in self.options.values]
    translated_options = {}
    for option_name in self._SDA2APPROX_OPTIONS:
      if ("gtsda/" + option_name.lower()) in user_options:
        approx_options["GTApprox/" + option_name] = self.options.get("GTSDA/" + option_name)

    return translated_options if translated_options else approx_options

  def score2rank(self, scores, method='average'):
    '''Get ranking based on scores
    '''

    scores = _shared.as_matrix(scores, name="Sensitivity indices ('scores' argument)")

    if method == 'average':
      processed_scores = np.mean(scores, axis=0)
    elif method == 'max':
      processed_scores = np.max(scores, axis=0)
    else:
      raise ValueError(("Unknown method '%s' for rank aggregation!\n Available methods are: 'average' and 'max'" % method))

    ranking = np.argsort(processed_scores)[::-1]

    return ranking

  def rank(self, **kwargs):
    r"""Perform SDA ranking procedure.

    param blackbox: blackbox object
    param budget: maximum number of blackbox evaluations
    type blackbox: class `da.p7core.blackbox.Blackbox`
    type budget: ``int``
    param x: input sample
    param y: output sample
    type x: :term:`array-like`
    type y: :term:`array-like`

    options: a set of options
    type options: ``dict``

    return: SDA RankResult
    rtype: class `da.p7core.gtsda.RankResult`

    There are two ranking modes:

    * Blackbox-based: ranks variables for a class `da.p7core.blackbox.Blackbox` object representing an arbitrary function.
    * Sample-based: ranks variables based on feature/response data samples.

    Valid argument combinations for modes:

    ==================  ================== =================
    Passed arguments    Mode               Ignored arguments
    ==================  ================== =================
    x, y                sample-based       blackbox, budget
    blackbox, budget    blackbox-based     x, y
    ==================  ================== =================

    All other combinations of arguments are invalid.
    """
    with _shared.sigint_watcher(self):
      return self._do_rank(**kwargs)

  def _do_rank(self, **kwargs):
    if not self.license.features().get('DA_MACROS_GTSDA_RANK', True):
      return RankResult(_status.LICENSING_PROBLEM, {'Ranker': 'Required license feature not found.'}, [], None, None)

    # Parsing inputs
    blackbox, budget = None, None
    x, y = None, None
    bounds = None
    options, approx_options, internal_options = None, None, None
    warns, x_meta = None, None

    recognized = ['blackbox', 'budget', 'x', 'y', 'options', 'approx_options', 'model', 'bounds']
    for key, value in kwargs.items():
      if key not in recognized:
        raise TypeError(("Keyword argument '%s' is not recognized!\nAvailable keywords are:\n'"
                         + "', '".join(recognized)  + "'") % key)


      if key in ('blackbox', 'model'):
        if blackbox is not None:
          raise _ex.GTException("Invalid argument set: the 'blackbox' and 'model' arguments are mutually exclusive")
        blackbox, warns, x_meta = _postprocess_blackbox(model=value)
      elif key == 'budget':
        _shared.check_concept_int(value, key)
        budget = value
      elif key == 'x':
        x = _shared.as_matrix(value, name="Input sample ('x' argument)")
        if _shared.isNanInf(x):
          raise _ex.NanInfError('Incorrect (NaN or Inf) value is found in the train inputs!')
      elif key == 'y':
        y = _shared.as_matrix(value, name="Output sample ('y' argument)")
        if _shared.isNanInf(y):
          raise _ex.NanInfError('Incorrect (NaN or Inf) value is found in the train outputs!')
      elif key == 'options':
        _shared.check_concept_dict(value, key)
        options = value
      elif key == 'approx_options':
        _shared.check_concept_dict(value, key)
        approx_options = value
      elif key == 'bounds':
        bounds = _shared.as_matrix(value, shape=(2, None), name="'bounds' argument")
      else:
        assert False, "Algorithmic error encountered: unhandled argument '%s'" % key

    if _shared.check_args((blackbox, budget), (x, y)):
      mode = 'blackbox'
    elif _shared.check_args((x, y), (blackbox, budget)):
      mode = 'sample'
    else:
      raise _ex.GTException("Invalid argument set: valid either pair 'blackbox', 'budget' either pair 'x', 'y'")

    if mode == 'sample':
      sample_size, size_x, size_y = _utils.check_sample(x=x, y=y)

    # If additional options are specified overwrite current options and save backup values
    self.saved_options = self.options.values
    if options is not None:
      # internal_options_keys = [key for key in options.keys() if key[:2] == '//']
      internal_options_keys = [key for key in options if key.lower().startswith('/gtsda/private/')]
      internal_options = dict((internal_options_key, options[internal_options_key]) for internal_options_key in internal_options_keys)
      options = dict((key, options[key]) for key in options if key not in internal_options_keys)

      _shared.check_concept_dict(options, 'options')
      self.options.set(options)

    internal_options = _ranker.fill_private_options_set(internal_options)
    _ranker.fill_options_set(self.options, internal_options, x_meta)

    general_print_options = self._get_options_subset(include=['gtsda/'], exclude=['gtsda/selector/', 'gtsda/checker/', 'gtsda/ranker/'])
    ranker_print_options = self._get_options_subset(include=['gtsda/ranker/'])

    if _shared.parse_bool(self.options.get('GTSDA/Deterministic')):
      states = self._set_random_generator_state(seed=int(self.options.get('GTSDA/Seed')))

    # translate GTSDA/MaxParallel to approx_options
    approx_options = self._translate_options(approx_options)

    # Configure logger
    sift_logger = _shared.Logger(self._logger, self.options.get('GTSDA/LogLevel').lower())

    if warns:
      sift_logger.warn(warns)

    sift_logger.info('Starting Ranker procedure...')
    sift_logger.info('=============================\n')

    start_time = datetime.now()

    # Object that stores all necessary options and objects to control execution
    control = _ranker.RankerParams(mode, self.options, internal_options, approx_options, sift_logger, self._watcher)

    # Form approx_model info
    info = {'Ranker': {}}
    info['Ranker']['General options'] = general_print_options
    info['Ranker']['Ranker options'] = ranker_print_options
    info['Ranker']['GTApprox options'] = approx_options if not approx_options is None else {}
    info['Ranker']['pSeven Core version'] = __version__
    info['BuildInfo'] = _buildinfo.buildinfo()['Build']
    if mode == 'sample':
      info['Ranker']['Sample size'] = sample_size
      info['Ranker']['Input dimension'] = size_x
      info['Ranker']['Output dimension'] = size_y
    if mode == 'blackbox':
      info['Ranker']['Budget'] = budget
      info['Ranker']['Input dimension'] = blackbox.size_x()
      info['Ranker']['Output dimension'] = blackbox.size_f()
      # @todo : report x_meta if presented

    sift_logger.info('Ranking started in %s-based mode.' % mode)

    if not (general_print_options is None and ranker_print_options is None):
      sift_logger.info('The following options were set for ranker:')
      if not general_print_options is None:
        self._print_options(general_print_options, sift_logger.info)
      if not ranker_print_options is None:
        self._print_options(ranker_print_options, sift_logger.info)

    else:
      sift_logger.info('No custom options were set for ranker.\n')

    if not approx_options is None:
      sift_logger.info('The following custom options were set for approximator:')
      self._print_options(approx_options, sift_logger.info)
    else:
      sift_logger.info('No custom options were set for approximator.\n')

    approx_model, generated_sample = None, None

    # Ranking is computed here
    try:
      maxparallel_control = self._backend.maxparallel_begin(int(self.options.get('GTSDA/MaxParallel')))
    except:
      maxparallel_control = None

    try:
      default_invalid_error = np.geterr()['invalid']
      np.seterr(invalid='ignore') #allows to supress incorrect Runtime warnings from numpy

      if mode == 'blackbox':
        info_string, scores, variances, generated_sample = _ranker.blackbox_based_ranker(blackbox=blackbox, budget=budget, control=control, bounds=bounds, x_meta=x_meta)

      elif mode == 'sample':
        info_string, scores, variances, approx_model = _ranker.sample_based_ranker(x=x, y=y, control=control, bounds=bounds)

      info['Ranker']['Detailed info'] = info_string

      if _shared.parse_bool(self.options.get('GTSDA/Deterministic')):
        self._set_random_generator_state(states=states)

      if not _shared.parse_bool(self.options.get('GTSDA/SaveModel')):
        approx_model = None

      if not _shared.parse_bool(self.options.get('GTSDA/SaveBlackboxData')):
        generated_sample = None
    finally:
      # If additional options are specified return to backup value
      if options is not None:
        self.options.reset()
        self.options.set(self.saved_options)

      np.seterr(invalid=default_invalid_error)

      if maxparallel_control is not None:
        self._backend.maxparallel_finish(maxparallel_control)

    sift_logger.info('==================================================================')
    sift_logger.info('Finished ranking. Elapsed time ' + str(datetime.now() - start_time) + '.\n')

    return RankResult(_status.SUCCESS, info, scores, variances, approx_model, generated_sample)

  def select(self, **kwargs):
    r"""Perform SDA selecting procedure.

    keyword x: input sample
    keyword y: output sample
    type x: :term:`array-like`
    type y: :term:`array-like`

    keyword x_test: input sample
    keyword y_test: output sample
    type x_test: :term:`array-like`
    type y_test: :term:`array-like`

    keyword options: a set of options
    type options: ``dict``

    keyword approx_options: a set of options
    type approx_options: ``dict``

    keyword rank_options: a set of options
    type rank_options: ``dict``

    return: SDA SelectResult
    rtype: class `da.p7core.gtsda.SelectResult`

    There are three modes for validation_error computation:

    * IV-based
    * Train sample-based
    * Test sample-based (test sample is needed)

    Valid argument combinations for modes:

    ====================  =================== =================
    Passed arguments      Mode                Ignored arguments
    ====================  =================== =================
    x, y                  IV-based            x_test, y_test
    x, y                  Train sample-based  x_test, y_test
    x, y, x_test, y_test  Test sample-based
    ====================  =================== =================
    """
    with _shared.sigint_watcher(self):
      return self._do_select(**kwargs)

  def _do_select(self, **kwargs):
    if not self.license.features().get('DA_MACROS_GTSDA_SELECT', True):
      return SelectResult(_status.LICENSING_PROBLEM, {'Selector': 'Required license feature not found.'}, [], None, None)

    np.seterr(invalid='ignore') #allows to supress incorrect Runtime warnings from numpy

    x, y = None, None
    x_test, y_test = None, None
    input_select_options, approx_options = None, None
    ranking = None

    # Parse input to detect specific input enities
    recognized = ['x', 'y', 'x_test', 'y_test', 'options', 'approx_options', 'ranking']
    for key, value in kwargs.items():
      if key not in recognized:
        raise TypeError(("Keyword argument '%s' is not recognized!\nAvailable flags are:\n'"
                         + "', '".join(recognized)  + "'") % key)
      elif value is None:
        continue

      if key == recognized[0]:
        x = _shared.as_matrix(value, name="Input part of the train sample ('x' argument)")
        if _shared.isNanInf(x):
          raise _ex.NanInfError('Incorrect (NaN or Inf) value is found in the train inputs!')
      elif key == recognized[1]:
        y = _shared.as_matrix(value, name="Output part of the train sample ('y' argument)")
        if _shared.isNanInf(y):
          raise _ex.NanInfError('Incorrect (NaN or Inf) value is found in the train outputs!')
      elif key == recognized[2]:
        x_test = _shared.as_matrix(value, name="Input part of the test sample ('x_test' argument)")
        if _shared.isNanInf(x_test):
          raise _ex.NanInfError('Incorrect (NaN or Inf) value is found in the test inputs!')
      elif key == recognized[3]:
        y_test = _shared.as_matrix(value, name="Output part of the test sample ('y_test' argument)")
        if _shared.isNanInf(y_test):
          raise _ex.NanInfError('Incorrect (NaN or Inf) value is found in the test outputs!')
      elif key == recognized[4]:
        _shared.check_concept_dict(value, key)
        input_select_options = value
      elif key == recognized[5]:
        _shared.check_concept_dict(value, key)
        approx_options = value
      elif key == recognized[6]:
        ranking = _shared.as_matrix(value, dtype=int, name="List of features indices in order of decreasing importance ('ranking' argument)")[:, 0]

    if not _shared.check_args((x, y), ()):
      raise _ex.GTException("Invalid argument set: 'x' and 'y' should be always set.")

    if not (_shared.check_args((x_test, y_test), ()) or _shared.check_args((), (x_test, y_test))):
      raise _ex.GTException("Invalid argument set: 'x_test' and 'y_test' should be both set or not set.")

    # Check train sample correct size and dimensionality
    sample_size, size_x, size_y = _utils.check_sample(x=x, y=y,
                                                      dif_sizes='Sizes of train inputs and outputs do not match!',
                                                      empty_sample='Train sample is empty!',
                                                      x_dim_is_zero='Train inputs dimensionality should be greater than zero!',
                                                      y_dim_is_zero='Train outputs dimensionality should be greater than zero!')

    # Check test sample correct size and dimensionality
    if x_test is not None and y_test is not None:
      _, size_x_test, size_y_test = _utils.check_sample(x=x_test, y=y_test,
                                                        dif_sizes='Sizes of test inputs and outputs do not match!',
                                                        empty_sample='Test sample is empty!',
                                                        x_dim_is_zero='Test inputs dimensionality should be greater than zero!',
                                                        y_dim_is_zero='Test outputs dimensionality should be greater than zero!')

      if size_x_test != size_x:
        raise ValueError('X dimensionality should coincide for train and test samples!')
      if size_y_test != size_y:
        raise ValueError('Y dimensionality should coincide for train and test samples!')

      #if validation type was not set explicitly by setting option at function call then use test sample for validation
      if input_select_options is not None:
        if all([key.lower() != 'gtsda/selector/validationtype' for key in input_select_options]):
          input_select_options['gtsda/selector/validationtype'] = 'testsample'
      else:
        input_select_options = {'gtsda/selector/validationtype': 'testsample'}

    if ranking is None:
      ranking = list(range(size_x))
    else:
      if (len(ranking) != size_x) or np.any(np.not_equal(np.sort(ranking).flat, range(size_x))):
        raise ValueError('Ranking should coincide with permutation of indices from zero to sample size minus one!')

    # Pass options to class (includes checking default values and ranges)
    self.saved_options = self.options.values
    if input_select_options is not None:
      _shared.check_concept_dict(input_select_options, 'options')
      self.options.set(input_select_options)

    general_print_options = self._get_options_subset(include=['gtsda/'], exclude=['gtsda/selector/', 'gtsda/checker/', 'gtsda/ranker/'])
    selector__print_options = self._get_options_subset(include=['gtsda/selector/'])
    selector_options = self._get_options_subset(include=['gtsda/'], exclude=['gtsda/checker/', 'gtsda/ranker/'])

    # GTApprox options formatting
    approx_options = _selector.set_default_approx_options(approx_options)
    # translate GTSDA/MaxParallel to approx_options
    approx_options = self._translate_options(approx_options)

    sift_logger = _shared.Logger(self._logger, selector_options['GTSDA/LogLevel'].lower())

    sift_logger.info('Starting Selector procedure...')
    sift_logger.info('==============================\n')

    start_time = datetime.now()

    if selector_options['GTSDA/Selector/ValidationType'].lower() == 'internal':
      if sample_size == 1:
        selector_options['GTSDA/Selector/ValidationType'] = 'TrainSample'
        sift_logger.warn('Internal validation couldn\'t be performed for train sample of 1 point. Validation type changed to \'TrainSample\'')

    elif selector_options['GTSDA/Selector/ValidationType'].lower() == 'testsample':
      if _shared.check_args((), (x_test, y_test)):
        raise _ex.GTException("Invalid argument set: 'x_test' and 'y_test' should be set" +
                              "if option 'GTSDA/Selector/ValidationType' value set as 'TestSample'.")

    columns_include_list, columns_exclude_list = _utils.check_for_constant_columns(x)

    if not columns_include_list:
      columns_include_list.append(columns_exclude_list.pop(0))

    if columns_exclude_list:
      ranking = [i for i in ranking if i in columns_include_list]

      sift_logger.info('The following input features were excluded from the consideration as all the feature values were constant: ' +
                       str(columns_exclude_list))

    # Info about method used
    info = {'Selector': {}}
    info['Selector']['General options'] = general_print_options
    info['Selector']['Selector options'] = selector__print_options
    info['Selector']['GTApprox options'] = approx_options
    info['Selector']['Sample size'] = sample_size
    info['Selector']['Input dimension'] = size_x
    info['Selector']['Output dimension'] = size_y
    info['Selector']['pSeven Core version'] = __version__
    info['BuildInfo'] = _buildinfo.buildinfo()['Build']

    if not (general_print_options is None and selector__print_options is None):
      sift_logger.info('The following options were set for selector:')
      if not general_print_options is None:
        self._print_options(general_print_options, sift_logger.info)
      if not selector__print_options is None:
        self._print_options(selector__print_options, sift_logger.info)
    else:
      sift_logger.info('No custom options were set for selector.\n')

    if not approx_options is None:
      sift_logger.info('The following custom options were set for approximator:')
      self._print_options(approx_options, sift_logger.info)
    else:
      sift_logger.info('No custom options were set for approximator.\n')

    if _shared.parse_bool(selector_options['GTSDA/Deterministic']):
      states = self._set_random_generator_state(seed=int(self.options.get('GTSDA/Seed')))

    checker_options = self._get_options_subset(include=['gtsda/'], exclude=['gtsda/selector/', 'gtsda/ranker/'])
    for key, value in checker_options.items():
      selector_options[key] = value

    # Call main algo
    try:
      maxparallel_control = self._backend.maxparallel_begin(int(self.options.get('GTSDA/MaxParallel')))
    except:
      maxparallel_control = None

    try:
      default_invalid_error = np.geterr()['invalid']
      np.seterr(invalid='ignore') #allows to supress incorrect Runtime warnings from numpy

      feature_subset, validation_error, approx_model = _selector.select(x, y, ranking, selector_options, approx_options,
                                                                        x_test, y_test, logger=sift_logger,
                                                                        watcher=self._watcher)

      if _shared.parse_bool(selector_options['GTSDA/Deterministic']):
        self._set_random_generator_state(states=states)

      if not _shared.parse_bool(self.options.get('GTSDA/SaveModel')):
        approx_model = None

    finally:
      if input_select_options is not None:
        self.options.reset()
        self.options.set(self.saved_options)
      np.seterr(invalid=default_invalid_error)
      if maxparallel_control is not None:
        self._backend.maxparallel_finish(maxparallel_control)

    sift_logger.info('=====================================================================')
    sift_logger.info('Finished selecting. Elapsed time ' + str(datetime.now() - start_time) + '.\n')

    return SelectResult(_status.SUCCESS, info, feature_subset, validation_error, approx_model)

  def _check_nans(self, data, name, logger):
    if not _shared.isNanInf(data):
      return

    message = '%s contains incorrect (NaN or Inf) value!' % name
    if self.options.get('GTSDA/NanMode').lower() == 'ignore':
      logger.warn(message)
    else:
      raise _ex.NanInfError(message)

  def check(self, x, y=None, **kwargs):
    r"""Perform SDA checking procedure.

    keyword x: input sample
    keyword y: output sample
    type x: :term:`array-like`
    type y: :term:`array-like`

    keyword options: a set of options
    type options: ``dict``

    keyword z: control sample
    type options: ``matrix``

    return: SDA CheckResult
    rtype: class `da.p7core.gtsda.CheckResult`
    """
    with _shared.sigint_watcher(self):
      return self._do_check(x, y, **kwargs)

  def _do_check(self, x, y=None, **kwargs):
    if not self.license.features().get('DA_MACROS_GTSDA_CHECK', True):
      return CheckResult(_status.LICENSING_PROBLEM, {'Checker': 'Required license feature not found.'}, [], [], [])

    sift_logger = _shared.Logger(self._logger, self.options.get('GTSDA/LogLevel').lower())

    x = _shared.as_matrix(x, name="Input sample ('x' argument)")

    if y is not None:
      y = _shared.as_matrix(y, name="Output sample ('y' argument)")

    # initialize with default values
    options = None
    z = None

    recognized = ['options', 'z']
    for key, value in kwargs.items():
      if key not in recognized:
        raise TypeError(("Keyword argument '%s' is not recognized!\nAvailable flags are:\n'"
                         + "', '".join(recognized)  + "'") % key)
      if value is None:
        continue

      if key == recognized[0]:
        _shared.check_concept_dict(value, key)
        options = value
      elif key == recognized[1]:
        z = _shared.as_matrix(value, name="Explanatory variables sample ('z' argument)")

    only_inputs_mode_flag = True if y is None else False

    self.saved_options = self.options.values
    if options is not None:
      _shared.check_concept_dict(options, key)
      self.options.set(options)

    maxparallel_control = None
    default_invalid_error = np.geterr()['invalid']
    try:
      self.options.set({'/GTSDA/Checker/OnlyInputsMode' : only_inputs_mode_flag})

      self._check_nans(x, "Input sample ('x' argument)", sift_logger)
      if y is not None:
        self._check_nans(y, "Output sample ('y' argument)", sift_logger)
      if z is not None:
        self._check_nans(z, "Explanatory variables sample ('z' argument)", sift_logger)

      if only_inputs_mode_flag:
        sample_size, _ = _utils.check_one_sample(x=x)
      else:
        sample_size, _, _ = _utils.check_sample(x=x, y=y)

      _checker.fill_options_set(self.options)

      checker_print_options = self._get_options_subset(include=['gtsda/checker/'])
      general_print_options = self._get_options_subset(include=['gtsda/'], exclude=['gtsda/checker/', 'gtsda/ranker/', 'gtsda/selector/'])

      sift_logger.info('Starting Checking procedure...')
      sift_logger.info('==============================\n')

      start_time = datetime.now()

      if (self.options.get('gtsda/checker/technique').lower() == 'distancepartialcorrelation') or \
         (self.options.get('gtsda/checker/technique').lower() == 'pearsonpartialcorrelation'):
        if (x.ndim == 1 or (x.ndim > 1 and x.shape[1] == 1)) and (z is None):
          if self.options.get('gtsda/checker/technique').lower() == 'pearsonpartialcorrelation':
            self.options.set('gtsda/checker/technique', 'pearsoncorrelation')
            checker_print_options['GTSDA/Checker/Technique'] = 'PearsonCorrelation'
          elif self.options.get('gtsda/checker/technique').lower() == 'distancepartialcorrelation':
            self.options.set('gtsda/checker/technique', 'distancecorrelation')
            checker_print_options['GTSDA/Checker/Technique'] = 'DistanceCorrelation'

          message = 'Partial techniques are not supported for 1-dimensional input without control variables. ' + \
                    'Checker run with technique replaced by non-partial.\n'

          sift_logger.info(message)

      if self.options.get('gtsda/checker/technique').lower() == 'distancepartialcorrelation':
        message = 'DistancePartialCorrelation supports only unbiased estimation of the score. '
        message += 'Corresponding option \'GTSDA/Checker/DistanceCorrelation/Unbiased\' is automatically changed to \'True\' \n'
        sift_logger.info(message)
        self.options.set('gtsda/checker/distancecorrelation/unbiased', 'true')

      info = {'Checker': {}}
      info['Checker']['General options'] = general_print_options
      info['Checker']['Checker options'] = checker_print_options
      if not (general_print_options is None and checker_print_options is None):
        sift_logger.info('The following options were set for checker:')
        if not general_print_options is None:
          self._print_options(general_print_options, sift_logger.info)
        if not checker_print_options is None:
          self._print_options(checker_print_options, sift_logger.info)

      else:
        sift_logger.info('No custom options were set for checker.\n')

      info['Checker']['Input dimension'] = x.shape[1] if (x is not None and x.ndim > 1) else 1

      if not _shared.parse_bool(self.options.get('/gtsda/checker/onlyinputsmode')):
        info['Checker']['Output dimension'] = y.shape[1] if (y is not None and y.ndim > 1) else 1
      else:
        info['Checker']['Output dimension'] = info['Checker']['Input dimension']
      info['Checker']['Sample size'] = sample_size
      info['Checker']['pSeven Core version'] = __version__
      info['BuildInfo'] = _buildinfo.buildinfo()['Build']

      if _shared.parse_bool(self.options.get('GTSDA/Deterministic')):
        states = self._set_random_generator_state(seed=int(self.options.get('GTSDA/Seed')))

      # calculating
      try:
        maxparallel_control = self._backend.maxparallel_begin(int(self.options.get('GTSDA/MaxParallel')))
      except:
        pass

      np.seterr(invalid='ignore') #allows to supress incorrect Runtime warnings from numpy

      scores, decisions, p_values, checker_info = \
        _checker.check(x, y, z, self.options, logger=sift_logger, watcher=self._watcher)
      for key, value in checker_info.items():
        info[key] = value

      if _shared.parse_bool(self.options.get('GTSDA/Deterministic')):
        self._set_random_generator_state(states=states)
    finally:
      # If additional options are specified return to backup value
      if options is not None:
        self.options.reset()
        self.options.set(self.saved_options)
      np.seterr(invalid=default_invalid_error)
      if maxparallel_control is not None:
        self._backend.maxparallel_finish(maxparallel_control)

    sift_logger.info('===================================================================')
    sift_logger.info('Finished checking. Elapsed time ' + str(datetime.now() - start_time) + '.\n')

    return CheckResult(_status.SUCCESS, info, scores, p_values, decisions)

  def __log(self, level, message):
    """ Logger """
    if self._logger:
      self._logger(level, message)

  def __watch(self, obj):
    """ Watcher """
    if self._watcher:
      retval = self._watcher(obj)
      if not retval:
        raise _ex.UserTerminated()

def _postprocess_blackbox(model, catvars=None):
  blackbox, catvars, warns, vartypes = _bbconverter.preprocess_blackbox(model, "GTSDA Ranking Procedure", (catvars or []))
  x_meta = [{"type": str(kind or "continuous").lower()} for kind in vartypes]
  for i, values in zip(catvars[::2], catvars[1::2]):
    x_meta[i]["enumerators"] = [_ for _ in values]
  return blackbox, warns, x_meta
