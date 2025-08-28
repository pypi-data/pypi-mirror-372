#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present

"""
Approximation model builder
---------------------------

.. currentmodule:: da.p7core.gtapprox.build_manager

"""
from __future__ import division, with_statement

import sys
import ctypes as _ctypes
from textwrap import dedent
from datetime import datetime
import contextlib as _contextlib
import time

import numpy as np

from . import cluster as _cluster
from . import moa_preprocessing as _moa_preprocessing
from . import model as _gtamodel
from . import split_sample as _split_sample
from . import utilities as _utilities
from .. import exceptions as _ex
from .. import license as _license
from .. import options as _options
from .. import shared as _shared
from .. import loggers
from ..batch import BatchJobSpecification, BatchJobStatus, test_ssh_connection
from ..batch.batch_manager import getFullPath
from ..six import BytesIO, StringIO, iteritems, string_types
from ..six.moves import range, reduce, xrange
from ..utils.abc import abstractmethod, abstractproperty
from .features_ic import build_landscape_analyzer as _build_landscape_analyzer
from .iterative_iv import _IterativeIV
from .technique_selection import TechniqueSelector, _SampleData, _build_inputs_encoding_model


N_BUILD = 0

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.void_ptr_ptr = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)

    # Main approx builder API
    self.builder_logger_callback_type = _ctypes.CFUNCTYPE(None, _ctypes.c_int, _ctypes.c_void_p, _ctypes.c_void_p)
    self.builder_watcher_callback_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)
    self.builder_pull_callback_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int)

    self.builder_create = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTApproxBuilderAPINew", self.__library))
    self.builder_options_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTApproxBuilderAPIGetOptionsManager", self.__library))
    self.builder_license_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTApproxBuilderAPIGetLicenseManager", self.__library))
    self.builder_build = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p,
                                           _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t,
                                           self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                           self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                           self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                           self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_void_p,
                                           _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                           _ctypes.c_char_p, _ctypes.c_char_p, self.void_ptr_ptr)(("GTApproxBuilderAPIBuild", self.__library))
    self.builder_submit = _ctypes.CFUNCTYPE(_ctypes.c_int, _ctypes.c_void_p,
                                            _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t,
                                            self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                            self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                            self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                            self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_void_p,
                                            _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,
                                            _ctypes.c_char_p, _ctypes.c_short, self.void_ptr_ptr)(("GTApproxBuilderAPISubmit", self.__library))
    self.builder_pull = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTApproxBuilderAPIPull", self.__library))
    self.builder_purge = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTApproxBuilderAPIPurge", self.__library))
    self.builder_submit_transaction = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int)(("GTApproxBuilderAPISubmitTransaction", self.__library))
    self.builder_release = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTApproxBuilderAPIFree", self.__library))
    self.builder_logger_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTApproxBuilderAPISetLogger", self.__library))
    self.builder_watcher_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTApproxBuilderAPISetWatcher", self.__library))

    # MoA API
    self.moa_create_builder = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_int, _ctypes.c_size_t, _ctypes.c_size_t,
                                                _ctypes.c_size_t, _ctypes.c_void_p)(("GTApproxMixtureOfApproximatorsCreateBuilder", self.__library))
    self.moa_set_input_properties = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p,
                                                      _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t,
                                                      _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t)(("GTApproxMixtureOfApproximatorsSetInputProperties", self.__library))
    self.moa_set_log = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p)(("GTApproxMixtureOfApproximatorsSetLog", self.__library))
    self.moa_set_options = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p)(("GTApproxMixtureOfApproximatorsSetOptions", self.__library))
    self.moa_set_info = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p)(("GTApproxMixtureOfApproximatorsSetInfo", self.__library))
    self.moa_set_approximator = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_void_p)(("GTApproxMixtureOfApproximatorsSetApproximator", self.__library))
    self.moa_set_mean = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t)(("GTApproxMixtureOfApproximatorsSetMean", self.__library))
    self.moa_set_covariance = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_int)(("GTApproxMixtureOfApproximatorsSetCovariance", self.__library))
    self.moa_set_weight = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_double)(("GTApproxMixtureOfApproximatorsSetWeight", self.__library))
    self.moa_set_confidence = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_double, _ctypes.c_double)(("GTApproxMixtureOfApproximatorsSetConfidence", self.__library))
    self.moa_get_last_error = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_size_t))(("GTApproxMixtureOfApproximatorsGetLastError", self.__library))
    self.moa_create = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_char_p)(("GTApproxMixtureOfApproximatorsCreate", self.__library))
    self.moa_set_sample = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_int), self.c_double_ptr, _ctypes.POINTER(_ctypes.c_int))(("GTApproxMixtureOfApproximatorsSetTrainingSample", self.__library))
    self.moa_set_lf_model = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p)(("GTApproxMixtureOfApproximatorsSetLowFidelityApproximator", self.__library))
    self.moa_set_encoding_model = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p)(("GTApproxMixtureOfApproximatorsSetInputsEncodingModel", self.__library))
    self.moa_free_builder = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTApproxMixtureOfApproximatorsFreeBuilder", self.__library))

    # Aux functions
    self.check_tensor_structure = _ctypes.CFUNCTYPE(_ctypes.c_int, _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t,
                                                    _ctypes.c_void_p)(('GTApproxUtilitiesFullCheckTensorStructure', self.__library))
    self.resolve_output_transform = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t
                                                      , self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr
                                                      , self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr
                                                      , _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxUtilitiesSelectOutputTransform', _shared._library))
    self.apply_output_transform = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t
                                                    , self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr
                                                    , self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr
                                                    , _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxUtilitiesApplyOutputTransform', _shared._library))
    self.wrap_output_transform = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_short
                                                  , _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxModelUnsafeWrapOutputTransform', _shared._library))

_api = _API()

class BuildManager(object):
  """Model builder manager"""

  @abstractmethod
  def set_logger(self, logger):
    """Set build logger"""
    pass

  @abstractmethod
  def get_logger(self):
    """Get current build logger"""
    pass

  @abstractmethod
  def set_watcher(self, watcher):
    """Set build watcher"""
    pass

  @abstractmethod
  def get_watcher(self):
    """Get current build watcher"""
    pass

  @abstractproperty
  def options(self):
    """Builder options.

    :type: :class:`~da.p7core.Options`

    General options interface for the builder. See section :ref:`Options<options/gtapprox>` for details.

    """
    pass

  @property
  def license(self):
    """Builder licenses.

    :type: :class:`~da.p7core.Licenses`

    General licenses interface for the builder.

    """
    pass

  @abstractmethod
  def get_models(self, cleanup=True):
    """Build models by previously submitted data and return list containing build models"""
    pass

  @abstractproperty
  def is_batch(self):
    """Indicates whether get_models() method can parallelize models training"""
    pass

  @abstractmethod
  def build(self, x, y, options=None, outputNoiseVariance=None, comment=None, weights=None, initial_model=None, restricted_x=None):
    """Train single model. All sanity checks on input data are supposed to have been performed outside."""
    pass

  def clean_data(self):
    pass

  def reset_workdir(self):
    pass

class _JobData(object):
  def __init__(self, data):
    self.data = data # data is kwargs dictionary of the BuildManager.submit_job() method
    self.uploaded = False # indicates whether the self.data are uploaded

class _Backend(object):
  _PYTHON_TECHNIQUES = ("moa",) # list of the Python-based techniques
  _RANDOMIZED_TECHNIQUES = ("gbrt",) # list of techniques than must not be trained in parallel with something else

  class _ExternalExceptionWrapper(object):
    def __init__(self, exception_handler, exception_type):
      self.__exception_type = exception_type
      self.__exception_handler = _shared.make_proxy(exception_handler)

    def _process_exception(self, exc_info):
      try:
        if self.__exception_handler:
          self.__exception_handler._callback_exception(self.__exception_type, exc_info)
      except:
        pass

  class LoggerCallbackWrapper(_ExternalExceptionWrapper):
    def __init__(self, exception_handler, logger):
      super(_Backend.LoggerCallbackWrapper, self).__init__(exception_handler, _ex.LoggerException)

      self.logger = logger
      self.__ids = dict([(_.id, _) for _ in (loggers.LogLevel.DEBUG, loggers.LogLevel.INFO, loggers.LogLevel.WARN, loggers.LogLevel.ERROR, loggers.LogLevel.FATAL)])

    def __call__(self, level, message, userdata):
      try:
        if self.logger is not None:
          self.logger(self.__ids.get(level, level), _shared._preprocess_utf8(_ctypes.string_at(message)))
      except:
        # self._process_exception(sys.exc_info()) # intentionally turned off
        pass

  class WatcherCallbackWrapper(_ExternalExceptionWrapper):
    def __init__(self, exception_handler, watcher):
      super(_Backend.WatcherCallbackWrapper, self).__init__(exception_handler, _ex.WatcherException)
      self.watcher = watcher

    def __call__(self, userdata):
      try:
        return bool(self.watcher(userdata)) if self.watcher is not None else True
      except:
        self._process_exception(sys.exc_info())
      return False

  class PullCallbackWrapper(_ExternalExceptionWrapper):
    def __init__(self, exception_handler, on_model):
      super(_Backend.PullCallbackWrapper, self).__init__(exception_handler, _ex.InternalError)
      self.on_model = on_model

    def __call__(self, model_handle, job_id):
      try:
        if self.on_model is not None:
          return self.on_model(job_id, _gtamodel.Model(handle=model_handle) if model_handle else None)
      except:
        self._process_exception(sys.exc_info())
      return False

  def __init__(self, api=_api):
    # intentionally use "volatile singleton" default value (we know about drawbacks)
    # so we preload and keep backend API
    self.__api = api
    self._sequential_techniques = self._PYTHON_TECHNIQUES + self._RANDOMIZED_TECHNIQUES

    # copy attributes from _API
    for _ in dir(self.__api):
      if not _.startswith("_"):
        setattr(self, _, getattr(self.__api, _))

    self.__holded_ptrs = []
    self.__pending_error = None
    self.__logger = self.LoggerCallbackWrapper(self, None)
    self.__watcher = self.WatcherCallbackWrapper(self, None)
    self.__pull_wrapper = self.PullCallbackWrapper(self, None)
    self.__pull_callback = self.builder_pull_callback_type(self.__pull_wrapper)

    self.__submit_transaction_actions = {"begin": 1, "commit": 2, "rollback": 0}

    self.__instance = self.builder_create(_ctypes.c_void_p(), _ctypes.c_void_p())
    if not self.__instance:
      raise Exception("Cannot initialize GT Approx API.")

    logger_ptr = self.builder_logger_callback_type(self.__logger)
    self.builder_logger_callback(self.__instance, logger_ptr, _ctypes.c_void_p())
    self.__holded_ptrs.append(logger_ptr)

    watcher_ptr = self.builder_watcher_callback_type(self.__watcher)
    self.builder_watcher_callback(self.__instance, watcher_ptr, _ctypes.c_void_p())
    self.__holded_ptrs.append(watcher_ptr)

  def __del__(self):
    if self.__instance:
      self.builder_release(self.__instance)
      self.__instance = None

  def _callback_exception(self, exc_type, exc_info):
    if exc_info and exc_info[1] is not None and (self.__pending_error is None or \
      (isinstance(self.__pending_error[1], Exception) and not isinstance(exc_info[1], Exception))):
      exc_type = exc_type if isinstance(exc_info[1], Exception) else exc_info[0]
      self.__pending_error = (exc_type, exc_info[1], exc_info[2])

  def _flush_callback_exception(self, ignore_errors):
    if self.__pending_error is not None:
      exc_type, exc_val, exc_tb = self.__pending_error
      self.__pending_error = None
      # logger and watcher exceptions are always ignorable
      if not ignore_errors and exc_type not in (_ex.LoggerException, _ex.WatcherException):
        _shared.reraise(exc_type, exc_val, exc_tb)
      else:
        try:
          if self.__logger.logger is not None:
            self.__logger.logger(loggers.LogLevel.WARN.id, "Ignorable exception occurred: %s" % exc_val)
        except:
          pass
        finally:
          self.__pending_error = None # clean up to avoid recursive flushes

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

  def set_logger(self, logger):
    self.__logger.logger = logger

  def set_watcher(self, watcher):
    self.__watcher.watcher = watcher

  @_contextlib.contextmanager
  def _scoped_callbacks(self, logger, watcher):
    original_logger = self.__logger.logger
    original_watcher = self.__watcher.watcher
    try:
      self.set_logger(logger)
      self.set_watcher(watcher)

      yield
    finally:
      self.set_logger(original_logger)
      self.set_watcher(original_watcher)

  @staticmethod
  def _encode_message(message):
    if message is not None:
      try:
        return message.encode('utf-8')
      except (AttributeError, UnicodeDecodeError):
        return message
    return _ctypes.c_char_p()

  def build(self, x, y, y_tol, w, initial_model, restricted_x, comment, annotations):
    self._flush_callback_exception(False) # cleanup errors first

    try:
      if y_tol is None:
        y_tol = np.empty((0, y.shape[1]), dtype=float)

      if w is None:
        w = np.empty(0, dtype=float)

      if restricted_x is None:
        restricted_x = np.empty((0, x.shape[1]), dtype=float)

      error_description = _ctypes.c_void_p()
      model_handle = self.builder_build(self.__instance, x.shape[0], x.shape[1], y.shape[1],
                                        x.ctypes.data_as(self.c_double_ptr), x.strides[0] // x.itemsize, x.strides[1] // x.itemsize,
                                        y.ctypes.data_as(self.c_double_ptr), y.strides[0] // y.itemsize, y.strides[1] // y.itemsize,
                                        y_tol.ctypes.data_as(self.c_double_ptr) if y_tol.size else self.c_double_ptr(),
                                        y_tol.strides[0] // y_tol.itemsize, y_tol.strides[1] // y_tol.itemsize,
                                        w.ctypes.data_as(self.c_double_ptr) if w.size else self.c_double_ptr(), w.strides[0] // w.itemsize,
                                        initial_model._Model__instance if initial_model else _ctypes.c_void_p(),
                                        restricted_x.shape[0] if restricted_x.size else 0,
                                        restricted_x.ctypes.data_as(self.c_double_ptr),
                                        restricted_x.strides[0] // restricted_x.itemsize,
                                        restricted_x.strides[1] // restricted_x.itemsize,
                                        self._encode_message(comment), self._encode_message(annotations), _ctypes.byref(error_description))
      if not model_handle:
        _shared.ModelStatus.checkErrorCode(0, 'Failed to train model.', error_description)

      return _gtamodel.Model(handle=model_handle)
    finally:
      # clean up errors if any occurred
      self._flush_callback_exception(True)

  def submit_transaction(self, action):
    self.builder_submit_transaction(self.__instance, self.__submit_transaction_actions[action])

  def submit(self, x, y, y_tol, w, initial_model, restricted_x, comment, copy_data, ignorable):
    if y_tol is None:
      y_tol = np.empty((0, y.shape[1]), dtype=float)

    if w is None:
      w = np.empty(0, dtype=float)

    if restricted_x is None:
      restricted_x = np.empty((0, x.shape[1]), dtype=float)

    flags = (1 if copy_data else 0) + (2 if ignorable else 0)

    error_description = _ctypes.c_void_p()
    job_id = self.builder_submit(self.__instance, x.shape[0], x.shape[1], y.shape[1],
                                 x.ctypes.data_as(self.c_double_ptr), x.strides[0] // x.itemsize, x.strides[1] // x.itemsize,
                                 y.ctypes.data_as(self.c_double_ptr), y.strides[0] // y.itemsize, y.strides[1] // y.itemsize,
                                 y_tol.ctypes.data_as(self.c_double_ptr) if y_tol.size else self.c_double_ptr(),
                                 y_tol.strides[0] // y_tol.itemsize, y_tol.strides[1] // y_tol.itemsize,
                                 w.ctypes.data_as(self.c_double_ptr) if w.size else self.c_double_ptr(), w.strides[0] // w.itemsize,
                                 initial_model._Model__instance if initial_model else _ctypes.c_void_p(),
                                 restricted_x.shape[0] if restricted_x.size else 0,
                                 restricted_x.ctypes.data_as(self.c_double_ptr),
                                 restricted_x.strides[0] // restricted_x.itemsize,
                                 restricted_x.strides[1] // restricted_x.itemsize,
                                 self._encode_message(comment), flags, _ctypes.byref(error_description))
    if not job_id or error_description:
      _shared.ModelStatus.checkErrorCode(0, 'Failed to train model.', error_description)
    return job_id

  def pull(self, raise_on_failure=True, is_smart_selection=False, is_moa_building=False):
    self._flush_callback_exception(False) # cleanup errors first

    try:
      models = []

      def on_model(job_id, model):
        if not model:
          return not raise_on_failure
        else:
          models.append((job_id, model))

        if is_smart_selection:
          self.__watcher({'passed smart phases': 1, 'current smart phase technique': model.details['Technique'].lower()})
        elif is_moa_building:
          self.__watcher({'passed moa phases': 1})
        else:
          self.__watcher({'passed global phases': 1})
        return True

      self.__pull_wrapper.on_model = on_model
      error_description = _ctypes.c_void_p()
      if not self.builder_pull(self.__instance, self.__pull_callback, _ctypes.byref(error_description)):
        _shared.ModelStatus.checkErrorCode(0, 'Failed to batch train models.', error_description)

      return models
    finally:
      self.__pull_wrapper.on_model = None
      # clean up errors if any occurred
      self._flush_callback_exception(True)

  def purge(self):
    return bool(self.builder_purge(self.__instance))

class DefaultBuildManager(BuildManager):
  """Build manager used by gtapprox.Builder by default"""

  def __init__(self, handle=None):
    self._logger = None
    self._watcher = None
    self._datasets = {}
    self._clustering_jobs = [] # [(data_id, job_id, options, comment, initial_model)]
    self._build_moa_jobs = [] # [(data_id, job_id, options, comment, initial_model)]
    self._building_jobs = []
    self._landscape_analysis_jobs = []
    self._find_tensor_structure_jobs = [] # {data_id: {job_id: (options, comment)}}
    self._split_sample_jobs = [] # {data_id: {job_id: (comment, train_test_ratio, tensor_structure, fixed_structure, min_factor_size, seed)}}  # @todo : implement
    self._make_iv_split_jobs = [] # {data_id: {job_id: (options, tensored_iv)}}
    self._select_output_transform_jobs = []
    self._job_data = {} # key is job_id, value is _JobData object
    self._backend = handle or _Backend()
    self._batch_mode = False

  def set_logger(self, logger):
    self._logger = logger

  def get_logger(self):
    return self._logger

  def _log(self, level, msg, prefix=None):
    if self._logger:
      prefix = _shared.make_prefix(prefix)
      for s in msg.splitlines():
        self._logger(level, prefix + s)

  def set_watcher(self, watcher):
    self._watcher = watcher

  def get_watcher(self):
    return self._watcher

  @property
  def options(self):
    return _options.Options(self._backend.options_manager, self._backend)

  @property
  def license(self):
    return _license.License(self._backend.license_manager, self._backend)

  def submit_data(self, data_id, x, y, outputNoiseVariance=None, weights=None, restricted_x=None):
    if x is not None and y is not None:
      from . builder import Builder
      x, y, outputNoiseVariance, _, weights, _ = Builder._preprocess_parameters(x, y, outputNoiseVariance, None, weights, None)

    self._datasets.setdefault(data_id, {}).update({'x': x, 'y': y, 'tol': outputNoiseVariance,
                                                   'weights': weights, 'restricted_x': restricted_x,
                                                   'is_uploaded': {}})

  def submit_job(self, data_id, job_id, action='build', **kwargs):
    """
    possible actions: 'build', 'find_tensor_structure', 'build_moa', 'make_iv_split', 'landscape_analysis', 'split_sample', 'select_output_transform', 'clusterize_moa'
    Action will be performed using a subsample defined by subsample_indices
    If data with 'data_id' was not submitted, then it is assumed that dataset with 'data_id' is already uploaded to server.
    """

    with _shared._scoped_options(self, kwargs.get('options')):
      actual_options = self.options.values

    if not data_id in self._datasets:
      self._datasets[data_id] = {}

    tested_actions = []
    def _test_action(action, expected_action):
      tested_actions.append(expected_action)
      return action == expected_action

    if _test_action(action, 'build_moa'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._build_moa_jobs):
        raise ValueError('MoA build job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      job_args = ("options", "comment", "initial_model")
      job_data = (actual_options, kwargs.get("comment"), kwargs.get("initial_model"))
      self._build_moa_jobs.append((data_id, job_id) + job_data)
    elif _test_action(action, 'clusterize_moa'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._clustering_jobs):
        raise ValueError('Clustering job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      job_args = ("options", "comment", "initial_model")
      job_data = (actual_options, kwargs.get("comment"), kwargs.get("initial_model"))
      self._clustering_jobs.append((data_id, job_id) + job_data)
    elif _test_action(action, 'build'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._building_jobs):
        raise ValueError('Model construction job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      job_args = ("options", "comment", "initial_model")
      job_data = (actual_options, kwargs.get("comment"), kwargs.get("initial_model"))
      self._building_jobs.append((data_id, job_id) + job_data)
    elif _test_action(action, 'find_tensor_structure'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._find_tensor_structure_jobs):
        raise ValueError('Searching for tensor structure job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      job_args = ("options", "comment")
      job_data = (actual_options, kwargs.get("comment"))
      self._find_tensor_structure_jobs.append((data_id, job_id) + job_data)
    elif _test_action(action, 'make_iv_split'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._make_iv_split_jobs):
        raise ValueError('Make IV split job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      job_args = ("options", "tensored_iv")
      job_data = (actual_options, kwargs.get("tensored_iv", False))
      self._make_iv_split_jobs.append((data_id, job_id) + job_data)
    elif _test_action(action, 'landscape_analysis'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._landscape_analysis_jobs):
        raise ValueError('Landscape analysis job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      default_la_options = (("catvars", None), ("seed", 15313), ("n_parts", 5), ("n_routes", None), ("n_fronts", None), ("strategy", "segmentation"), ("landscape_analyzer", None), ("extra_points_number", 0), ("extra_points_strategy", "dx"))
      job_args = ("options",) + tuple(k for k, v in default_la_options)
      job_data = (actual_options,) + (tuple(v for k, v in default_la_options) if kwargs is None else tuple(kwargs.get(k, v) for k, v in default_la_options))
      self._landscape_analysis_jobs.append((data_id, job_id) + job_data)
    elif _test_action(action, 'split_sample'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._split_sample_jobs):
        raise ValueError('Landscape analysis job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      default_split_options = (("tensor_structure", None), ("fixed_structure", False), ("min_factor_size", 5), ("seed", None), ("categorical_inputs_map", None), ("categorical_outputs_map", None))
      job_args = ("comment", "train_test_ratio",) + tuple(k for k, v in default_split_options)
      job_data = (kwargs.get("comment"), kwargs["train_test_ratio"],) + (tuple(v for k, v in default_split_options) if kwargs is None else tuple(kwargs.get(k, v) for k, v in default_split_options))
      self._split_sample_jobs.append((data_id, job_id) + job_data)
    elif _test_action(action, 'select_output_transform'):
      if any(_[0] == data_id and _[1] == job_id for _ in self._select_output_transform_jobs):
        raise ValueError('Select output transform job %s for data with %s data_id has already been submitted.' % (job_id, data_id))
      job_args = ("options", "comment", "initial_model")
      job_data = (actual_options, kwargs.get("comment"), kwargs.get("initial_model"))
      self._select_output_transform_jobs.append((data_id, job_id) + job_data)
    else:
      raise ValueError('Unknown action: %s! Valid actions are: "%s".' % (action, '", "'.join(tested_actions)))

    self._job_data.setdefault(job_id, {})[data_id] = _JobData(dict(zip(job_args, job_data)))

  def _normalize_moa_lf_mode(self, initial_model, feasible_forward=True, feasible_boost=True, raise_on_error=False):
    if initial_model is None:
      return []

    lf_mode = [_ for _ in _shared.parse_json(self.options.get("/GTApprox/MoALowFidelityModel"))]

    feasible_forward = feasible_forward and not _shared.parse_bool(self.options.get('GTApprox/ExactFitRequired'))
    feasible_boost = feasible_boost and not _shared.parse_bool(self.options.get('GTApprox/AccuracyEvaluation')) or initial_model.has_ae

    if raise_on_error:
      error_msg = []
      if not feasible_forward and "forward" in lf_mode:
        error_msg.append('the "forward" mode is incompatible with the "exact fit" requirement')
      if not feasible_boost and "boost" in lf_mode:
        error_msg.append('the "boost" mode cannot be used because initial model does not support accuracy evaluation')
      if error_msg:
        raise _ex.InvalidOptionValueError("Invalid /GTApprox/MoALowFidelityModel=%s option value:\n- %s." % (self.options.get("/GTApprox/MoALowFidelityModel"), ";\n- ".join(error_msg)))
      del error_msg

    if "auto" in lf_mode:
      lf_mode.remove("auto")
      if feasible_forward and "forward" not in lf_mode:
        lf_mode.append("forward")
      if feasible_boost and "boost" not in lf_mode:
        lf_mode.append("boost")

    if not feasible_forward and "forward" in lf_mode:
      lf_mode.remove("forward")
    if not feasible_boost and "boost" in lf_mode:
      lf_mode.remove("boost")

    return lf_mode

  def _make_clustering_local(self, x, y, options, weights=None, tol=None, initial_model=None, comment=None, cluster_model=None):
    sample_size = x.shape[0] if weights is None else (weights > 0).sum()
    boosting_mode = False

    cluster_model_scalers = cluster_model.get("scalers", {}) if cluster_model else {}

    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
      encoding_model = cluster_model.get('encoding_model') if cluster_model else None
      if not encoding_model:
        # Note the initial model is a "low fidelity" model and its internal properties must be ignored
        encoding_model = _build_inputs_encoding_model(x, y, self.options, weights=weights, tol=tol, initial_model=None)
      x_encoded = encoding_model.calc(x) if encoding_model else x
      size_x_encoded = x_encoded.shape[1]

      lf_mode = self._normalize_moa_lf_mode(initial_model)
      number_of_clusters, min_sample_size, min_cluster_size = _moa_preprocessing.calc_cluster_size(self.options, ((size_x_encoded + initial_model.size_f) if "forward" in lf_mode else size_x_encoded), sample_size, True)

      if initial_model is not None:
        if "boost" in lf_mode:
          boosting_mode = True
          # we need original norm because low fidelity model may be degenerated
          if "original_y_scaler" in cluster_model_scalers:
            original_y_scaler = _moa_preprocessing.StaticScaler(**cluster_model_scalers["original_y_scaler"])
          else:
            original_y_scaler = _moa_preprocessing.Scaler(logger=self._logger)
            original_y_scaler.fit(y, rm_duplicates=False, weights=weights, tol=tol)
            cluster_model_scalers["original_y_scaler"] = {"mean": original_y_scaler.mean.tolist(), "std": original_y_scaler.std.tolist()}
          variable_cols = original_y_scaler.std > np.finfo(float).tiny
          original_y_norm = original_y_scaler.std.copy()[variable_cols]
          original_y_norm = 1. / original_y_norm

          if "ignore_clustering" not in lf_mode:
            x_encoded = np.hstack((x_encoded, initial_model.calc(x)))
            y = (y - x_encoded[:, size_x_encoded:]) # use residuals for clustering
          else:
            y = (y - initial_model.calc(x))

          # exclude the "exact fit" points
          points_of_interest = np.hypot.reduce(np.fabs(original_y_scaler.transform(np.fabs(y)) + original_y_scaler.mean[variable_cols].reshape(1, -1)) * (original_y_norm *  original_y_scaler.std[variable_cols]).reshape(1, -1), axis=1)
          # keep at least number_of_clusters * (1 + min_cluster_size) points
          clustering_threshold = min(_shared.parse_float(self.options.get("/GTApprox/MoAClusteringThreshold")),
            np.percentile(points_of_interest, max(0., points_of_interest.shape[0] - np.max(number_of_clusters) * (min_cluster_size + 1)) * 100. / points_of_interest.shape[0]))
          points_of_interest = points_of_interest > (clustering_threshold * float(original_y_scaler.mean.size)**0.5)
          tol = None # tol is redundant because we are now in residuals space
        elif "ignore_clustering" not in lf_mode:
          y = initial_model.calc(x)

      # normalization for GMM clustering
      if "points_scaler" in cluster_model_scalers and size_x_encoded == len(cluster_model_scalers["points_scaler"]["mean"]):
        points_scaler = _moa_preprocessing.StaticScaler(**cluster_model_scalers["points_scaler"])
      else:
        points_scaler = _moa_preprocessing.Scaler(logger=self._logger)
        points_scaler.fit(x_encoded, rm_duplicates=False, weights=weights, comment=comment)
        cluster_model_scalers["points_scaler"] = {"mean": points_scaler.mean.tolist(), "std": points_scaler.std.tolist()}

      if "values_scaler" in cluster_model_scalers:
        values_scaler = _moa_preprocessing.StaticScaler(**cluster_model_scalers["values_scaler"])
        supp_data = values_scaler.payload
      else:
        values_scaler = _moa_preprocessing.Scaler(logger=self._logger)
        # values_scaler supersedes supplementary data usage for points_scaler
        supp_data = values_scaler.fit(y, rm_duplicates=False, weights=weights, tol=tol, comment=comment)
        cluster_model_scalers["values_scaler"] = {"mean": values_scaler.mean.tolist(), "std": values_scaler.std.tolist(), "payload": supp_data}

      normalized_x = points_scaler.transform(x_encoded)
      normalized_y = values_scaler.transform(y)

      active_points = (weights > 0) if weights is not None else None

      if boosting_mode:
        if active_points is not None:
          np.logical_and(active_points, points_of_interest, out=active_points)
        elif not np.all(points_of_interest):
          active_points = points_of_interest

      if active_points is None or not np.any(active_points):
        active_points = True

      if not np.all(active_points):
        normalized_x = normalized_x[active_points]
        normalized_y = normalized_y[active_points]

      if not cluster_model:
        if _shared.parse_bool(self.options.get('GTApprox/AccuracyEvaluation')):
          cluster_model = self._moa_clustering_for_ae(normalized_x, normalized_y, number_of_clusters,
                                                      min_sample_size, min_cluster_size, comment)
        else:
          cluster_model = _cluster.build(normalized_x, normalized_y, number_of_clusters, min_sample_size, min_cluster_size,
                                         self.options, _shared.Logger(self._logger, 'debug', prefix=_shared.make_prefix(comment)),
                                         self._watcher)

      # assign training points to clusters
      probabilities = _cluster.assign(cluster_model, np.hstack((normalized_x, normalized_y)), self.options, mode="assign")

      if not np.all(active_points):
        active_probabilities = probabilities
        probabilities = np.zeros((len(x), probabilities.shape[1]))
        probabilities[active_points] = active_probabilities


      if initial_model is None or boosting_mode or ("ignore_clustering" in lf_mode):
        x_mean, x_std = points_scaler.mean, points_scaler.std
      else:
        x_mean = np.hstack((points_scaler.mean, values_scaler.mean))
        x_std = np.hstack((points_scaler.std, values_scaler.std))

      cluster_model["scalers"] = cluster_model_scalers
      cluster_model["encoding_model"] = encoding_model
      return cluster_model, probabilities, {'mean': x_mean, 'std': x_std, 'supp_data': supp_data}

  def _make_iv_split_local(self, data_id, job_id, options, tensored_iv, dry_run=False):
    data = self._datasets[data_id]
    actual_options = dict(options.items())
    actual_options['GTApprox/IVDeterministic'] = True
    actual_options['GTApprox/Technique'] = 'TA' if tensored_iv else 'RSM' # 'Auto' technique is not allowed
    iv = _IterativeIV(data['x'], data['y'], options=actual_options, outputNoiseVariance=data.get('tol'),
                      weights=data.get('weights'), tensored=tensored_iv)
    session_data_ids = []
    while iv.session_begin():
      session_data_ids.append('%s_%s_iv_split_%d' % (data_id, job_id, len(session_data_ids)))
      if not dry_run:
        self.submit_data(session_data_ids[-1], np.array(iv.x), np.array(iv.y),
                         outputNoiseVariance=np.array(iv.outputNoiseVariance, copy=True) if iv.outputNoiseVariance is not None else None,
                         weights=np.array(iv.weights, copy=True) if iv.weights is not None else None)
      iv.session_end(None)

    return session_data_ids

  def _clusterize_moa_local(self, x, y, options, y_tol, weights, comment, initial_model, restricted_x):
    self._log(loggers.LogLevel.INFO, 'Performing clusterization for MoA models...\n', comment)

    moa_metainfo, x, y, weights, y_tol, initial_model = self._preprocess_moa_output_transform(x=x, y=y, options=options, y_tol=y_tol, weights=weights,
                                                                                              comment=comment, initial_model=initial_model,
                                                                                              restricted_x=restricted_x)

    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
      self.options.set(moa_metainfo.get("initial_options", options))
      self.options.set({"GTApprox/OutputTransformation": "none"})

      cluster_model, _, _ = self._make_clustering_local(x, y, self.options.values, weights, y_tol, initial_model, comment)
      return cluster_model


  def _moa_clustering_for_ae(self, x, y, number_of_clusters, min_sample_size, min_cluster_size, comment):
    sample_size = x.shape[0]
    # Average cluster size is about 1000 so, that in each cluster we can build GP model with AE
    average_cluster_size = 1000
    # AE is now available for sample sizes less than 10 000 (SGP)
    max_cluster_size = 10000
    if self.options.get('GTApprox/MoANumberOfClusters') == '[]' and (sample_size > max_cluster_size):
      number_of_clusters = [sample_size // average_cluster_size + 1]

    cluster_model = _cluster.build(x, y, number_of_clusters, min_sample_size, min_cluster_size, self.options,
                                   _shared.Logger(self._logger, 'debug', prefix=_shared.make_prefix(comment)),
                                   self._watcher)

    # find cluster which has more than 10k points
    i = 0
    while i < cluster_model['number_of_clusters']:
      xy = np.append(x, y, axis=1)
      probabilities = _cluster.assign(cluster_model, xy, self.options, mode="assign")
      labels = np.argmax(probabilities, axis=1)
      cluster_size = np.sum(labels == i)
      if cluster_size > max_cluster_size:
        cluster_comment = 'cluster #%d' % (i + 1)
        if comment:
          cluster_comment = '%s, %s' % (cluster_comment, comment)

        weight = cluster_model['weights'][i]
        this_cluster_x = x[labels == i]
        this_cluster_y = y[labels == i]
        this_cluster_number_of_clusters = [cluster_size // average_cluster_size + 1]
        this_cluster_model = _cluster.build(this_cluster_x, this_cluster_y, this_cluster_number_of_clusters,
                                            min_sample_size, min_cluster_size, self.options,
                                            _shared.Logger(self._logger, 'debug', prefix=_shared.make_prefix(cluster_comment)),
                                            self._watcher)
        this_cluster_model['weights'] *= weight

        # update cluster_model model: replace mean, covariance matrix and weight
        cluster_model['means'] = np.delete(cluster_model['means'], (i), axis=0)
        cluster_model['means'] = np.vstack((cluster_model['means'], this_cluster_model['means']))

        cluster_model['covars_cholesky_factor'] = np.delete(cluster_model['covars_cholesky_factor'], (i), axis=0)
        cluster_model['covars_cholesky_factor'] = np.vstack((cluster_model['covars_cholesky_factor'],
                                                             this_cluster_model['covars_cholesky_factor']))

        cluster_model['weights'] = np.delete(cluster_model['weights'], (i), axis=0)
        cluster_model['weights'] = np.hstack((cluster_model['weights'], this_cluster_model['weights']))
        cluster_model['number_of_clusters'] = cluster_model['number_of_clusters'] - 1 + this_cluster_model['number_of_clusters']
      else:
        i += 1

    return cluster_model

  def _get_cluster_data_local(self, x, y, options, weights, outputNoiseVariance, probabilities, cluster_model, initial_model, comment):
    forward_lf = False
    boost_lf = False
    cluster_mean = []
    base_cluster_options = {}
    dry_run = _utilities._parse_dry_run(self.options)

    # Check if sample structure should be kept full-factorial
    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
      cluster_mean = _shared.parse_json(self.options.get("GTApprox/GPMeanValue"))

      # Check training sample structure, keep it full-factorial if 'ta' or 'tgp' is selected.
      moa_tech = self.options.get('GTApprox/MoATechnique').lower()
      keep_full_factorial = (moa_tech in ('ta', 'tgp', 'auto')) and not dry_run
      if keep_full_factorial:
        structure, _, tensor_factors = self._find_tensor_structure_local(x, self.options.values, comment)
        if structure not in (2, 4,):
          tensor_factors = None
          if moa_tech == 'auto':
            keep_full_factorial = False
          else:
            raise _ex.InvalidOptionValueError("MoA cluster technique %s is not applicable because input part of the dataset does not have tensor structure." % self.options.get('GTApprox/MoATechnique'))

      lf_mode = self._normalize_moa_lf_mode(initial_model, feasible_forward=(not keep_full_factorial))
      base_cluster_options["/GTApprox/MoALowFidelityModel"] = lf_mode
      forward_lf = "forward" in lf_mode
      boost_lf = "boost" in lf_mode

    # Prepare grid representation for full-factorial data if necessary
    if keep_full_factorial:
      # Get input dimensions set as factors
      factor_dims = _shared.parse_json(tensor_factors)
      factor_dims = [_[: -1] for _ in factor_dims]

    for i, indices in enumerate(_cluster._indices(probabilities, cluster_model)):
      x_cluster = x[indices]
      y_cluster = y[indices]
      n_cluster = outputNoiseVariance[indices] if outputNoiseVariance is not None else None
      w_cluster = weights[indices] if weights is not None else None
      options_cluster = dict((k, base_cluster_options[k]) for k in base_cluster_options)

      tensor_cluster = keep_full_factorial

      if tensor_cluster:
        cluster_idxs = np.ones(x.shape[0], dtype=bool) # cluster points complemented to tensor
        factor_points = np.empty(x.shape[0], dtype=bool) # temporary buffer
        grid_shape_c = []
        for dims in factor_dims:
          factor_points.fill(True)
          for axis in dims:
            np.logical_and(factor_points, (x[:, axis].reshape(-1, 1) == np.unique(x_cluster[:, axis]).reshape(1, -1)).any(axis=1), out=factor_points)
          grid_shape_c.append(len(_moa_preprocessing.remove_coinciding_points(x[factor_points][:, dims], return_index=False, return_sorted=False, logger=None)))
          np.logical_and(cluster_idxs, factor_points, out=cluster_idxs)
        del factor_points
        grid_size_c = np.count_nonzero(cluster_idxs)

        if np.max(grid_shape_c) == grid_size_c:
          # TA and TGP do not support samples with effective dimensionality 1
          options_cluster['GTApprox/Technique'] = 'Auto'
          options_cluster['GTApprox/TensorFactors'] = []
          options_cluster['//Service/CartesianStructure'] = []
          options_cluster['//Service/CartesianStructureEstimation'] = 'NoCartesianProduct'
          tensor_cluster = False
        else:
          # We must set tensor factors manually to avoid accidental splitting of n-dimensional factors
          options_cluster['GTApprox/TensorFactors'] = tensor_factors
          options_cluster['//Service/CartesianStructure'] = tensor_factors
          options_cluster['//Service/CartesianStructureEstimation'] = "MultidimensionalFactorial" if any(len(_) > 1 for _ in factor_dims) else "FullFactorial"

          # Set weight to 0 for added points (or outputs noise variance to max if specified)
          added_points_idx = cluster_idxs.copy()
          added_points_idx[indices] = False

          if added_points_idx.any():
            added_points_idx = added_points_idx[cluster_idxs]

            # Extend training data to full-factorial DoE for current cluster
            x_cluster = x[cluster_idxs]
            y_cluster = y[cluster_idxs]
            n_cluster = outputNoiseVariance[cluster_idxs] if outputNoiseVariance is not None else None
            w_cluster = weights[cluster_idxs] if weights is not None else None

            if n_cluster is not None:
              n_cluster[added_points_idx] = [10 * np.var(y)] * n_cluster.shape[1]
            elif w_cluster is not None:
              w_cluster[added_points_idx] = 0.
            else:
              w_cluster = np.ones((grid_size_c,))
              w_cluster[added_points_idx] = 0.

      lfy_cluster = initial_model.calc(x_cluster) if (initial_model and (boost_lf or forward_lf)) else None

      if not tensor_cluster:
        # Check cluster sample
        x_tol = _shared.parse_json(self.options.get('GTApprox/InputsTolerance'))
        if len(x_tol) != 0:
          x_tol = np.array(x_tol, dtype=float).reshape((-1,))

        sample = _SampleData((x_cluster if lfy_cluster is None else np.hstack((x_cluster, lfy_cluster))),
                             y_cluster, n_cluster, w_cluster, [], x_tol,
                             {'x': self.options.get('GTApprox/InputNanMode'),
                              'y': self.options.get('GTApprox/OutputNanMode')})
        # Reset technique if cluster sample lost the original sample properties
        with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
          try:
            self.options.set('//Service/CartesianStructureEstimation', 'Unknown' if not dry_run else 'NoCartesianProduct')
            TechniqueSelector(self.options).checklist[moa_tech](sample, self.options, None)
          except (_ex.InapplicableTechniqueException, KeyError):
            # For 'GTApprox/MoATechnique'=Auto also falls here
            options_cluster['GTApprox/Technique'] = 'Auto'
            options_cluster['GTApprox/TensorFactors'] = []
            options_cluster['//Service/CartesianStructure'] = []
            options_cluster['//Service/CartesianStructureEstimation'] = 'Unknown' if not dry_run else 'NoCartesianProduct'

      if lfy_cluster is not None:
        if boost_lf:
          if not cluster_mean:
            cluster_mean = y_cluster.mean(axis=0).tolist()
            options_cluster['GTApprox/GPMeanValue'] = cluster_mean
          np.multiply(y_cluster, 2., out=y_cluster)
          np.subtract(y_cluster, lfy_cluster, out=y_cluster)
        if forward_lf:
          x_cluster = np.hstack((x_cluster, lfy_cluster))

      yield x_cluster, y_cluster, n_cluster, w_cluster, options_cluster

  def _select_technique_local(self, x, y, weights, tol, initial_model, logger, comment=None, sample_id=None):
    technique_selector = TechniqueSelector(self.options, logger)
    if sample_id:
      technique_selector.preprocess_sample(x, y, tol, weights, False, self, comment, sample_id=sample_id)
    else:
      build_manager = DefaultBuildManager()
      build_manager.options.set(self.options.values)
      build_manager.set_watcher(self._watcher)
      technique_selector.preprocess_sample(x, y, tol, weights, False, build_manager, comment)
    preferred_technique, _ = technique_selector.select(output_column=None, initial_model=initial_model, comment=comment)
    return preferred_technique[0]['technique']

  def _build_default_moa_initial_model(self, x, y, options, outputNoiseVariance, weights, comment, restricted_x):
    trained_model = None

    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
      with self._backend._scoped_callbacks(self._logger, self._watcher):
        try:
          self.options.set({'GTApprox/InternalValidation': False,
                            'GTApprox/AccuracyEvaluation': False,
                            'GTApprox/ExactFitRequired': False,
                            'GTApprox/Technique': 'RSM',
                            'GTApprox/RSMFeatureSelection': 'MultipleRidgeLS',
                            'GTApprox/DependentOutputs': True,
                            'GTApprox/Componentwise': False,
                            'GTApprox/LinearityRequired': False,
                            'GTApprox/RSMMapping': 'None',
                            'GTApprox/RSMType': 'PureQuadratic',
                            })

          trained_model = self._backend.build(x, y, outputNoiseVariance, weights, None, restricted_x, comment, None)
        except Exception:
          exc_val = sys.exc_info()[1]
          self._log(loggers.LogLevel.WARN, 'Failed to build default MoA initial model: %s' % (exc_val,))
          trained_model = None

    return trained_model or None

  def _preprocess_moa_output_transform(self, x, y, options, y_tol, weights, comment, initial_model, restricted_x):
    saved_options = self.options.values
    saved_logger = self._logger
    output_transform = None

    self._log(loggers.LogLevel.INFO, '\nPreparing data for MoA approximation...')

    try:
      if initial_model is not None and not (np.isfinite(initial_model.calc(x)) == np.isfinite(y)).all():
        self._log(loggers.LogLevel.WARN, '\nInitial model cannot be used with MoA technique%s: initial model predicts non-finite values at the finite training dataset points\n'
            % ((" for %s" % comment) if comment else ""))
        initial_model = None
    except:
      initial_model = None
      self._log(loggers.LogLevel.WARN, '\nInitial model cannot be used with MoA technique%s: model evaluation has failed at the training dataset' % ((" for %s" % comment) if comment else ""))

    try:
      self._logger = None # mute output transform selection

      output_transform = self._select_output_transform_local(x, y, options, y_tol, weights, comment, None) # note MoA does not need initial model for transform selection
      if all((_ == "none") for _ in output_transform):
        output_transform = None

      self.options.reset()
      self.options.set(options)

      if output_transform is not None:
        self.options.set({"GTApprox/OutputTransformation": output_transform});

      if initial_model is not None:
        moa_tech = self.options.get('GTApprox/MoATechnique').lower()
        keep_full_factorial = moa_tech in ['ta', 'tgp', 'auto']
        if keep_full_factorial:
          structure, _, tensor_factors = self._find_tensor_structure_local(x, self.options.values, comment)
          if structure not in (2, 4,):
            tensor_factors = None
            if moa_tech == 'auto':
              keep_full_factorial = False
            else:
              self._log(loggers.LogLevel.ERROR, ("MoA cluster technique %s is not applicable because input part of the dataset does not have tensor structure." % self.options.get('GTApprox/MoATechnique')))
              raise _ex.InvalidOptionValueError("MoA cluster technique %s is not applicable because input part of the dataset does not have tensor structure." % self.options.get('GTApprox/MoATechnique'))
      else:
        initial_model = self._build_default_moa_initial_model(x, y, self.options.values, y_tol, weights, (comment + (": " if comment else "") + "MoA linear trend"), restricted_x)
        self.options.set('/GTApprox/MoALowFidelityModel', '[]') # no boosting, no forward, use linear model only for clustering
        keep_full_factorial = False

      self.options.set("/GTApprox/MoALowFidelityModel", self._normalize_moa_lf_mode(initial_model, feasible_forward=(not keep_full_factorial), raise_on_error=True))

      moa_metainfo = {'x': x, 'y': y, 'w': weights, 'tol': y_tol,
                      'initial_options': self.options.values, 'initial_model': initial_model,
                      'restricted_x': restricted_x}

      if output_transform is not None:
        wrapped_initial_model = None
        if initial_model is not None:
          current_options = self.options.values
          current_options["GTApprox/OutputTransformation"] = output_transform
          err_desc = _ctypes.c_void_p()
          wrapped_initial_model = self._backend.wrap_output_transform(initial_model._Model__instance, 0, \
                          _shared.write_json(current_options).encode('ascii'), _ctypes.byref(err_desc))
          if not wrapped_initial_model:
            _, message = _shared._release_error_message(err_desc)
            self._log(loggers.LogLevel.WARN, ("Cannot apply '%s' transform: %s" % (output_transform, message,)))
            output_transform = None # keep calm and ignore output transformation
          else:
            wrapped_initial_model = _gtamodel.Model(handle=wrapped_initial_model)

        if output_transform is not None:
          x, y = x.copy(), y.copy()
          if weights is not None:
            weights = weights.copy()
          if y_tol is not None:
            y_tol = y_tol.copy()

          if not self._backend.apply_output_transform(x.shape[0], x.shape[1], y.shape[1]
                                                      , x.ctypes.data_as(self._backend.c_double_ptr), _ctypes.cast(x.ctypes.strides, self._backend.c_size_ptr)
                                                      , y.ctypes.data_as(self._backend.c_double_ptr), _ctypes.cast(y.ctypes.strides, self._backend.c_size_ptr)
                                                      , self._backend.c_double_ptr() if y_tol is None else y_tol.ctypes.data_as(self._backend.c_double_ptr)
                                                      , self._backend.c_size_ptr() if y_tol is None else _ctypes.cast(y_tol.ctypes.strides, self._backend.c_size_ptr)
                                                      , self._backend.c_double_ptr() if weights is None else weights.ctypes.data_as(self._backend.c_double_ptr)
                                                      , self._backend.c_size_ptr() if weights is None else _ctypes.cast(weights.ctypes.strides, self._backend.c_size_ptr)
                                                      , self.options._Options__impl, _ctypes.c_void_p(), self._backend.void_ptr_ptr()):
            x, y, weights, y_tol = moa_metainfo['x'], moa_metainfo['y'], moa_metainfo['w'], moa_metainfo['tol']
            output_transform = None
            wrapped_initial_model = None

        if wrapped_initial_model is not None and output_transform is not None:
          initial_model = wrapped_initial_model
          moa_metainfo["initial_model"] = initial_model

      moa_metainfo["output_transform"] = output_transform
      return moa_metainfo, x, y, weights, y_tol, initial_model
    finally:
      self.options.reset()
      self.options.set(saved_options)
      self._logger = saved_logger

  def _get_moa_model(self, x, y, options, y_tol, weights, comment, initial_model, restricted_x, iv_mode, cluster_model=None):
    saved_options = self.options.values
    saved_logger = self._logger
    tensor_factors = None

    moa_metainfo, x, y, weights, y_tol, initial_model = self._preprocess_moa_output_transform(x, y, options, y_tol, weights, comment, initial_model, restricted_x)

    with self._backend._scoped_callbacks(self._logger, self._watcher):
      try:
        self.options.reset()
        self.options.set(moa_metainfo.get("initial_options", options))
        self.options.set({"GTApprox/OutputTransformation": "none", "//GT/SkipLicenseRequest": True})
        initial_options = self.options.values

        log_level = loggers.LogLevel.from_string(self.options.get('GTApprox/LogLevel').lower())
        tee_logger = _shared.TeeLogger(self._logger, log_level)
        self.set_logger(tee_logger)
        if tee_logger.private_log_level != log_level:
          self.options.set('GTApprox/LogLevel', str(tee_logger.private_log_level))

        self._log(loggers.LogLevel.INFO, 'Creating MoA approximation...\n', comment)
        if not cluster_model:
          cluster_model = _cluster._parse_json_clusters_model(self.options.get("//GTApprox/MoAClustersModel"), False)
          if cluster_model and 'encoding_model' in cluster_model and cluster_model['encoding_model'] \
            and not isinstance(cluster_model['encoding_model'], _gtamodel.Model):
            cluster_model['encoding_model'] = _gtamodel.Model(string=cluster_model['encoding_model'])
        cluster_model, probabilities, points_scaler = self._make_clustering_local(x, y, self.options.values, weights, y_tol, initial_model, comment, cluster_model=cluster_model)
        cluster_data_generator = self._get_cluster_data_local(x, y, self.options.values, weights, y_tol, probabilities, cluster_model, initial_model, comment)
        cluster_comment_suffix = ("/%d" % (cluster_model['number_of_clusters'],)) if 'number_of_clusters' in cluster_model else ""

        if self._watcher:
          self._watcher({'number of moa phases': cluster_model['number_of_clusters']})

        local_models = []
        for i, (x_cluster, y_cluster, n_cluster, w_cluster, options_cluster) in enumerate(cluster_data_generator):
          self.options.reset()
          self.options.set(initial_options)

          cluster_comment = ('cluster #%d' % (i + 1)) + cluster_comment_suffix
          if comment:
            cluster_comment = '%s, %s' % (cluster_comment, comment)

          self._log(loggers.LogLevel.INFO, '%d points assigned to %s...' % (x_cluster.shape[0], cluster_comment))

          self.options.set('GTApprox/InternalValidation', False)
          self.options.set('GTApprox/Technique', self.options.get('GTApprox/MoATechnique'))
          verb = self.options.get('GTApprox/Technique')
          verb = "Selecting" if verb.lower() == "auto" else ("Reconsidering %s" % verb)
          # service option indicating composite model is building
          self.options.set('//Service/BuildingCompositeModel', True)
          self.options.set(options_cluster)

          cluster_tech = self.options.get('GTApprox/Technique')
          if cluster_tech.lower() == 'auto':
            self._log(loggers.LogLevel.INFO, ('\n%s approximation technique...' % verb), cluster_comment)
            # Note we don't pass initial model to the technique selection because this is technique selection for the particular MoA cluster
            cluster_tech = self._select_technique_local(x_cluster, y_cluster, w_cluster, n_cluster, None, self._logger, cluster_comment, sample_id=cluster_comment)
            self.options.set('GTApprox/Technique', cluster_tech)
            self._log(loggers.LogLevel.INFO, " ")

          cluster_tensor_factors = _shared.parse_json(self.options.get('GTApprox/TensorFactors'))
          if tensor_factors is None:
            tensor_factors = cluster_tensor_factors
          elif tensor_factors and tensor_factors != cluster_tensor_factors:
            tensor_factors = []

          submitted_job = False
          if self.is_batch and cluster_tech.lower() not in self._backend._sequential_techniques:
            try:
              self._backend.submit_transaction("begin")
              local_models.append((True, self._backend.submit(x_cluster, y_cluster, n_cluster, w_cluster, None, # note there is no initial_model here
                                                              None, cluster_comment, copy_data=True,
                                                              ignorable=iv_mode)))
              submitted_job = True
              self._backend.submit_transaction("commit")
            except (MemoryError, _ex.OutOfMemoryError):
              self._backend.submit_transaction("rollback")

          if not submitted_job:
            try:
              local_models.append((False, self._backend.build(x_cluster, y_cluster, n_cluster, w_cluster, None, # note there is no initial_model here
                                                              None, cluster_comment, None)))

              if self._watcher:
                self._watcher({'passed moa phases': 1})
            except:
              exc_info = sys.exc_info()
              _shared.reraise(_ex.InvalidProblemError, "Failed to build approximation for %s: %s" % (cluster_comment, exc_info[1]), exc_info[2])

        self.options.reset()
        self.options.set(moa_metainfo.get("initial_options", options))

        if self.is_batch and any(_[0] for _ in local_models):
          models_built = dict(_ for _ in self._backend.pull(is_moa_building=True))
          self._backend._flush_callback_exception(False)
        else:
          models_built = dict()

        local_models = [(models_built[job_data] if is_job_id else job_data) for is_job_id, job_data in local_models]
        if any(_ is None for _ in local_models):
          raise _ex.InvalidProblemError("Failed to build model for MoA cluster")

        moa_metainfo["full_log"] = tee_logger.log_value
        logger = _shared.Logger(self._logger, 'debug', prefix=_shared.make_prefix(comment))
        model = self._collect_moa(local_models, cluster_model, points_scaler, moa_metainfo, logger)

        if self._watcher:
          self._watcher({'reset moa phase': True})
          if _shared.parse_bool(self.options.get("//Service/SmartSelection")):
            self._watcher({'passed smart phases': 1, 'current smart phase technique': model.details['Technique'].lower()})
          else:
            self._watcher({'passed global phases': 1})

        if model:
          self._log(loggers.LogLevel.INFO, '\n\nDone. %d approximation models for clusters are built.' % len(local_models), comment)

        return model, tensor_factors, cluster_model
      except:
        if iv_mode:
          return None, tensor_factors
        else:
          raise
      finally:
        self._backend.purge()

        self.options.reset()
        self.options.set(saved_options)
        self.set_logger(saved_logger)

  def _build_moa(self, x, y, options, y_tol, weights, comment, initial_model, restricted_x):
    model, tensor_factors, cluster_model = self._get_moa_model(x, y, options, y_tol, weights, comment, initial_model, restricted_x, iv_mode=False)
    if not model:
      return model

    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
      try:
        if _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
          self.options.set('GTApprox/InternalValidation', False)
          self.options.set('GTApprox/Technique', 'MoA')
          if tensor_factors:
            self.options.set('GTApprox/TensorFactors', tensor_factors)
          iv = _IterativeIV(x, y, options=self.options.values, outputNoiseVariance=y_tol, weights=weights, tensored=bool(tensor_factors))
          iv_iteration = 0
          while iv.session_begin():
            iv_comment = ("%s, IV session #%d" % (comment, iv_iteration)) if comment else ("IV training session #%d" % iv_iteration)
            iv_model, _, _ = self._get_moa_model(iv.x, iv.y, self.options.values, comment=iv_comment, initial_model=initial_model,
                                                y_tol=iv.outputNoiseVariance, weights=iv.weights, restricted_x=None, iv_mode=True,
                                                cluster_model=cluster_model)
            iv.session_end(iv_model)
            iv_iteration += 1
          iv.save_iv(model)
      except:
        # do not care, we've got model, so emit warning and return it
        exc_info = sys.exc_info()
        self._log(loggers.LogLevel.WARN, 'Failed to perform internal validation of the MoA model: %s' % exc_info[1], comment)

    return model

  def _find_tensor_structure_local(self, x, options, comment):
    self._log(loggers.LogLevel.INFO, 'Analyzing cartesian structure...', comment)

    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS_TA):
      c_options = self.options._Options__impl
      c_sample = _shared.py_matrix_2c(x, name="'x' argument")
      code = self._backend.check_tensor_structure(c_sample.array.shape[0], c_sample.array.shape[1], c_sample.ptr, c_sample.ld, c_options)
      return code, self.options.get('//Service/CartesianStructureEstimation'), self.options.get('//Service/CartesianStructure')

  def _split_sample_local(self, x, y, train_test_ratio, tensor_structure, fixed_structure, min_factor_size, seed, comment, categorical_inputs_map, categorical_outputs_map):
    self._log(loggers.LogLevel.INFO, 'Splitting %d samples%s to train and validation datasets%s...'
                % (len(x), ('' if not comment else (' [%s]' % comment)),
                  (" w.r.t cartesian structure of the dataset" if tensor_structure else "")))
    train_indices, test_indices, tensor_structure = _split_sample._train_test_split(x, y, train_test_ratio, tensor_structure, fixed_structure, min_factor_size,
                                                                                    (None if seed is None else np.random.RandomState(seed)),
                                                                                    categorical_inputs_map, categorical_outputs_map,
                                                                                    dry_run=_utilities._parse_dry_run(self.options))
    self._log(loggers.LogLevel.INFO, 'Splitting%s%s complete:' % (('' if not comment else (' [%s]' % comment)),
                            (" w.r.t cartesian structure of the dataset" if tensor_structure else "")))
    self._log(loggers.LogLevel.INFO, '- samples assigned to the train dataset: %d' % np.count_nonzero(train_indices))
    self._log(loggers.LogLevel.INFO, '- samples assigned to the validation dataset: %d' % np.count_nonzero(test_indices))
    return train_indices, test_indices, tensor_structure

  def _landscape_analysis_local(self, x, y, w, tol, options, catvars, seed, n_parts, n_routes, n_fronts, strategy, landscape_analyzer, extra_points_number, extra_points_strategy):
    self._log(loggers.LogLevel.INFO, 'Performing landscape analysis...')

    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
      try:
        # @todo : convert tolerances to weights somehow
        if landscape_analyzer is None:
          time_start = datetime.now()
          landscape_analyzer = _build_landscape_analyzer(x, y, w, catvars, seed, n_parts, self, n_routes, n_fronts, strategy, accelerator=int(self.options.get('GTApprox/Accelerator')))
          time_finish = datetime.now()
          self._log(loggers.LogLevel.DEBUG, 'Landscape analysis performed in %s' % str(time_finish - time_start))
        if landscape_analyzer is None or not extra_points_number:
          return landscape_analyzer, None
        self._log(loggers.LogLevel.DEBUG, 'Generating %d image points...' % extra_points_number)
        time_start = datetime.now()
        extra_dataset = dict(zip(["x", "y", "w"], landscape_analyzer.random_subsample(extra_points_number, mode=extra_points_strategy, seed=seed)))
        time_finish = datetime.now()
        self._log(loggers.LogLevel.DEBUG, '%d points done in %s' % (extra_points_number, str(time_finish - time_start)))
        return landscape_analyzer, extra_dataset
      except:
        return None, None

  def _select_output_transform_local(self, x, y, options, outputNoiseVariance, weights, comment, initial_model):
    self._log(loggers.LogLevel.INFO, 'Selecting output transformation...', comment)

    with _shared._scoped_options(self, options, keep_options=_utilities._PERMANENT_OPTIONS):
      errdesc = _ctypes.c_void_p()
      if not self._backend.resolve_output_transform(x.shape[0], x.shape[1], y.shape[1]
                                , x.ctypes.data_as(self._backend.c_double_ptr), _ctypes.cast(x.ctypes.strides, self._backend.c_size_ptr)
                                , y.ctypes.data_as(self._backend.c_double_ptr), _ctypes.cast(y.ctypes.strides, self._backend.c_size_ptr)
                                , self._backend.c_double_ptr() if outputNoiseVariance is None else outputNoiseVariance.ctypes.data_as(self._backend.c_double_ptr)
                                , self._backend.c_size_ptr() if outputNoiseVariance is None else _ctypes.cast(outputNoiseVariance.ctypes.strides, self._backend.c_size_ptr)
                                , self._backend.c_double_ptr() if weights is None else weights.ctypes.data_as(self._backend.c_double_ptr)
                                , self._backend.c_size_ptr() if weights is None else _ctypes.cast(weights.ctypes.strides, self._backend.c_size_ptr)
                                , self.options._Options__impl, (initial_model._Model__instance if initial_model else _ctypes.c_void_p()), _ctypes.byref(errdesc)):
        _shared.ModelStatus.checkErrorCode(0, 'Failed to resolve output transformation type.', errdesc)


      result = _shared.parse_output_transformation(self.options.get("GTApprox/OutputTransformation"))
      if not isinstance(result, string_types) and int(self.options.get("//ComponentwiseTraining/ActiveOutput")) >= 0:
        result = result[0]

      result_repr = result if isinstance(result, string_types) else ("[%s]" % ", ".join([_shared._safestr(_) for _ in result]))
      self._log(loggers.LogLevel.INFO, 'Output transformation: %s' % (result_repr), comment)

      return result

  def get_landscape_analyzer(self):
    # create landscape analyzers
    landscape_analyzers = {}
    job_queue = self._pull_job_queue(job_action='landscape_analysis')
    for data_id, job_id, options, catvars, seed, n_parts, n_routes, n_fronts, strategy, landscape_analyzer, extra_points_number, extra_points_strategy in job_queue:
      data = self._datasets[data_id]
      landscape_analyzers.setdefault(data_id, {})[job_id] = self._landscape_analysis_local(data['x'], data['y'], data.get("weights"), data.get("tol"), \
                                                                                           options, catvars, seed, n_parts, n_routes, n_fronts, strategy, \
                                                                                           landscape_analyzer, extra_points_number, extra_points_strategy)
    return landscape_analyzers

  def get_tensor_structure(self):
    # find tensor structure
    tensor_structures = {}
    job_queue = self._pull_job_queue(job_action='find_tensor_structure')
    for data_id, job_id, options, comment in job_queue:
      tensor_structures.setdefault(data_id, {})[job_id] = self._find_tensor_structure_local(self._datasets[data_id]['x'], options, comment)
    return tensor_structures

  def get_split_sample(self):
    # split sample to train and test subsamples
    split_results = {}
    job_queue = self._pull_job_queue(job_action='split_sample')
    for data_id, job_id, comment, train_test_ratio, tensor_structure, fixed_structure, min_factor_size, seed, categorical_inputs_map, categorical_outputs_map in job_queue:
      data = self._datasets[data_id]
      split_results.setdefault(data_id, {})[job_id] = self._split_sample_local(data['x'], data['y'], train_test_ratio,
                                                                               tensor_structure, fixed_structure, min_factor_size,
                                                                               seed, comment, categorical_inputs_map, categorical_outputs_map)
    return split_results

  def select_output_transform(self):
    # split sample to train and test subsamples
    output_transform = {}
    job_queue = self._pull_job_queue(job_action='select_output_transform')
    for data_id, job_id, options, comment, initial_model in job_queue:
      data = self._datasets[data_id]
      output_transform.setdefault(data_id, {})[job_id] = self._select_output_transform_local(x=data['x'], y=data['y'], options=options, outputNoiseVariance=data.get("tol"),
                                                                                             weights=data.get("weights"), comment=comment, initial_model=initial_model)
    return output_transform

  def get_moa_clusters(self):
    clusters_model = {}
    job_queue = self._pull_job_queue(job_action='clusterize_moa')
    for data_id, job_id, options, comment, initial_model in job_queue:
      data = self._datasets[data_id]
      clusters_model.setdefault(data_id, {})[job_id] = self._clusterize_moa_local(x=data['x'], y=data['y'], options=options, y_tol=data.get('tol'), weights=data.get('weights'),
                                                                                  comment=comment, initial_model=initial_model, restricted_x=data.get('restricted_x'))
    return clusters_model

  class _IVComment(object):
    def __init__(self, comment):
      self.comment = _shared._safestr(comment) if comment else ""
      self.format = "[%s, IV session #%d]" if comment else "[%sIV training session #%d]"
      self.iteration = 0

    def next(self):
      self.iteration += 1
      return self.format % (self.comment, self.iteration)

  def get_models(self, cleanup=True):
    models = {}

    saved_options = self.options.values
    ignore_exceptions = False
    with self._backend._scoped_callbacks(self._logger, self._watcher):
      try:

        # make IV split
        job_queue = self._pull_job_queue(job_action='make_iv_split')
        for data_id, job_id, options, tensored_iv in job_queue:
          self._make_iv_split_local(data_id, job_id, options, tensored_iv)
          self._backend._flush_callback_exception(False)

        # first make clustering
        job_queue = self._pull_job_queue(job_action='build_moa')
        for data_id, job_id, options, comment, initial_model in job_queue:
          data = self._datasets[data_id]
          self.options.reset()
          self.options.set(options)
          models.setdefault(data_id, {})[job_id] = self._build_moa(data['x'], data['y'], self.options.values, y_tol=data.get('tol'),
                                                                  weights=data.get('weights'), comment=comment, initial_model=initial_model,
                                                                  restricted_x=data.get('restricted_x'))
          self._backend._flush_callback_exception(False)

        # build models (batch)
        job_queue = self._pull_job_queue(job_action='build')

        # First pass - build or submit non-MoA models
        submit_queue = []
        for data_id, job_id, options, comment, initial_model in job_queue:
          data = self._datasets[data_id]

          self.options.reset()
          self.options.set(options)

          technique = self.options.get('GTApprox/Technique').lower()
          if technique == "moa" and self._batch_mode:
            # We must use separate queue for MoA in batch mode to avoid interference of MoA with current submit queue
            submit_queue.append((data_id, job_id, None, None, self.options.values, initial_model))
            continue

          if technique == "auto" or not _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
            iv_status = None
          else:
            self.options.set('GTApprox/InternalValidation', False)
            iv_status = { "options": { "x": data["x"],
                                      "y": data["y"],
                                      "options": self.options.values,
                                      "outputNoiseVariance": data.get('tol'),
                                      "weights": data.get('weights'),
                                      "tensored": (technique in ["ta", "tgp"]) },
                          "job_ids": []}


          if self._batch_mode and technique not in self._backend._sequential_techniques:
            ignorable_models = _shared.parse_bool(self.options.get("//Service/SmartSelection"))
            api_job_id = self._backend.submit(data['x'], data['y'], data.get('tol'), data.get('weights'), initial_model,
                                              data.get('restricted_x'), comment, copy_data=False, ignorable=ignorable_models)
          else:
            api_job_id = None

          if api_job_id is None:
            models.setdefault(data_id, {})[job_id] = self.build(data['x'], data['y'], self.options.values, data.get('tol'), comment, data.get('weights'), initial_model, data.get('restricted_x'))
          elif iv_status is not None:
            self._backend.submit_transaction("begin")
            iv = None
            try:
              iv = _IterativeIV(**iv_status["options"])
              iv_comment = self._IVComment(comment)
              while iv.session_begin():
                self.options.reset()
                self.options.set(iv.options.values)
                api_iv_job_id = self._backend.submit(iv.x, iv.y, iv.outputNoiseVariance, iv.weights, initial_model, None, iv_comment.next(), copy_data=True, ignorable=True)
                submit_queue.append((None, None, None, api_iv_job_id, None, None))
                iv_status["job_ids"].append(api_iv_job_id)
                iv.session_end(None)
              iv.save_iv(None)
              self._backend.submit_transaction("commit")
            except (MemoryError, _ex.OutOfMemoryError):
              self._backend.submit_transaction("rollback")
              submit_queue = submit_queue[:-len(iv_status["job_ids"])]
              iv_status["job_ids"] = []
            finally:
              del iv
              self.options.reset()
              self.options.set(options)

          submit_queue.append((data_id, job_id, iv_status, api_job_id, None, initial_model))
          self._backend._flush_callback_exception(False)

        # Pull submitted models (if any)
        if any(api_job_id is not None for _, _, _, api_job_id, _, _ in submit_queue):
          models_built = dict(_ for _ in self._backend.pull(is_smart_selection=_shared.parse_bool(self.options.get("//Service/SmartSelection"))))
          for data_id, job_id, iv_status, api_job_id, options, initial_model in submit_queue:
            if data_id is not None and api_job_id is not None:
              models.setdefault(data_id, {})[job_id] = models_built.get(api_job_id)

        # Second pass - separate build MoA to avoid interference of submitted/pulled jobs
        for data_id, job_id, iv_status, api_job_id, options, initial_model in submit_queue:
          if data_id is not None and options is not None:
            data = self._datasets[data_id]
            self.options.reset()
            models.setdefault(data_id, {})[job_id] = self._build_moa(data['x'], data['y'], options, y_tol=data.get('tol'),
                                                                    weights=data.get('weights'), comment=comment, initial_model=initial_model,
                                                                    restricted_x=data.get('restricted_x'))
            self._backend._flush_callback_exception(False)


        # perform IV. Note any exception is safe since this point
        ignore_exceptions = True

        for data_id, job_id, iv_status, api_job_id, options, initial_model in submit_queue:
          # if data_id is None then model should be ignored (it will be used later)
          if data_id is not None and iv_status is not None:
            # if iv_status is not None then it specifies IV process
            iv = _IterativeIV(**iv_status["options"])
            if iv_status["job_ids"]:
              for api_iv_job_id in iv_status["job_ids"]:
                if iv.session_begin():
                  iv.session_end(models_built.get(api_iv_job_id))
                else:
                  break
            else:
              iv_comment = self._IVComment(comment)
              while iv.session_begin():
                iv_model = self.build(iv.x, iv.y, iv.options.values, iv.outputNoiseVariance,
                                      iv_comment.next(), iv.weights, initial_model, None)
                iv.session_end(iv_model)
                del iv_model
            iv.save_iv(models[data_id][job_id], _shared.Logger(self._logger, "debug", prefix=_shared.make_prefix(comment)))
            del iv

      except Exception:
        exc_type, exc_val, exc_tb = sys.exc_info()
        if isinstance(exc_val, _ex.ExceptionWrapper):
          exc_val.set_prefix("Approximation failed, cause ")
        if not isinstance(exc_val, _ex.GTException):
          exc_val = _ex.GTException('Approximation failed, cause: %s' % (exc_val,))

        if not ignore_exceptions:
          _shared.reraise(type(exc_val), exc_val, exc_tb)
        else:
          self._backend._callback_exception(type(exc_val), (exc_type, exc_val, exc_tb))
          self._backend._flush_callback_exception(False)
      finally:
        self._backend.purge()
        self.options.reset()
        self.options.set(saved_options)

    models = self._postprocess_models(models, {}, {}, {})
    if cleanup:
      self.clean_data()

    return models

  def clean_data(self):
    self._datasets = {}
    self._job_data = {}
    self._building_jobs = []
    self._build_moa_jobs = []
    self._clustering_jobs = []
    self._find_tensor_structure_jobs = []
    self._split_sample_jobs = []
    self._make_iv_split_jobs = []
    self._landscape_analysis_jobs = []
    self._select_output_transform_jobs = []

  @property
  def is_batch(self):
    return self._batch_mode

  def setup_batch_mode(self, batch_mode):
    if str(batch_mode).lower() == 'fastparallel':
      self._batch_mode = 'fastparallel' # this is True
      self._backend._sequential_techniques = self._backend._PYTHON_TECHNIQUES
    else:
      self._batch_mode = bool(batch_mode)
      self._backend._sequential_techniques = self._backend._PYTHON_TECHNIQUES + self._backend._RANDOMIZED_TECHNIQUES

  def build(self, x, y, options, outputNoiseVariance, comment, weights, initial_model, restricted_x):
    sample_size = x.shape[0]
    size_x = x.shape[1]
    size_y = y.shape[1]

    trained_model = None
    saved_options = self.options.values if options else None

    with self._backend._scoped_callbacks(self._logger, self._watcher):
      try:
        if options:
          self.options.reset()
          self.options.set(options)

        if self.options.get("GTApprox/Technique").lower() == "moa":
          return self._build_moa(x, y, options=self.options.values, y_tol=outputNoiseVariance,
                                weights=weights, comment=comment, initial_model=initial_model, restricted_x=restricted_x)

        iv_technique = None

        if _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
          iv_technique = self.options.get('GTApprox/Technique').lower()
          if iv_technique == 'auto':
            iv_technique = None
          else:
            self.options.set('GTApprox/InternalValidation', False)

        trained_model = self._backend.build(x, y, outputNoiseVariance, weights, initial_model, restricted_x, comment, None)

        if self._watcher:
          if _shared.parse_bool(self.options.get("//Service/SmartSelection")):
            self._watcher({'passed smart phases': 1, 'current smart phase technique': trained_model.details['Technique'].lower()})
          else:
            self._watcher({'passed global phases': 1})

        if trained_model is not None and iv_technique is not None:
          iv = _IterativeIV(x, y, self.options.values, outputNoiseVariance, weights, tensored=(iv_technique in ["ta", "tgp"]))
          iv_comment_generator = self._IVComment(comment)
          while iv.session_begin():
            self.options.reset()
            self.options.set(iv.options.values)
            iv_model = self._backend.build(iv.x, iv.y, iv.outputNoiseVariance, iv.weights, initial_model, None, iv_comment_generator.next(), None)
            iv.session_end(iv_model)
          iv.save_iv(trained_model, _shared.Logger(self._logger, "debug", prefix=_shared.make_prefix(comment)))
          del iv

      except Exception:
        exc_val, exc_tb = sys.exc_info()[1:]
        if isinstance(exc_val, _ex.ExceptionWrapper):
          exc_val.set_prefix("Approximation failed, cause ")
        if not isinstance(exc_val, _ex.GTException):
          exc_val = _ex.GTException('Approximation failed, cause: %s' % (exc_val,))
        _shared.reraise(type(exc_val), exc_val, exc_tb)
      finally:
        if saved_options is not None:
          self.options.reset()
          self.options.set(saved_options)

    if not trained_model:
      raise _ex.GTException("Approximation failed.")
    return trained_model

  def _pull_job_queue(self, job_action='build', cleanup_queue=True):
    actions_map = {
      'build':                   '_building_jobs',
      'build_moa':               '_build_moa_jobs',
      'clusterize_moa':          '_clustering_jobs',
      'find_tensor_structure':   '_find_tensor_structure_jobs',
      'make_iv_split':           '_make_iv_split_jobs',
      'landscape_analysis':      '_landscape_analysis_jobs',
      'split_sample':            '_split_sample_jobs',
      'select_output_transform': '_select_output_transform_jobs',
    }

    queue_name = actions_map.get(job_action)
    if not queue_name:
      raise ValueError('Unknown action: %s. Valid actions are: "".' % (job_action, '", "'.join(_ for _ in actions_map)))

    job_source = getattr(self, queue_name)

    if cleanup_queue:
      setattr(self, queue_name, [])
    else:
      job_source = [_ for _ in job_source]

    return job_source

  def _collect_moa(self, approximators, cluster_model, points_scaler, meta_info, logger):
    """
    meta_info has the following fields:
        {'x': input part of the whole training sample (including all clusters),
         'y': output part of the whole training sample (including all clusters),
         'w': points weight of the whole training sample (including all clusters),
         'tol': output noise variance of the whole training sample (including all clusters),
         'initial_options': options to store with the model created. If not set then the current self.options are stored,
         'initial_model': initial_model,
         'full_log': the whole training log to store with the model}
    """
    model = None
    saved_options = self.options.values
    moa_builder = None

    try:
      self.options.reset()
      self.options.set(meta_info.get('initial_options', {}))

      info = {'ClusteringInfo': {'Number of clusters': cluster_model['number_of_clusters'],
                                 'Type of covariance matrix': cluster_model['covariance_type'],
                                 'Options': {'GTApprox/MoACovarianceType': cluster_model['covariance_type'],
                                             'GTApprox/MoANumberOfClusters': cluster_model['number_of_clusters'],
                                             'GTApprox/MoAPointsAssignment': self.options.get('GTApprox/MoAPointsAssignment'),
                                             'GTApprox/MoATypeOfWeights': self.options.get('GTApprox/MoATypeOfWeights'),
                                            },
                                 'Details': {'/GTApprox/SupplementaryDataUsed': points_scaler.get('supp_data', 'NoSupplementaryData'),},
                                 'Clusters': [],
                                },
             }

      if self.options.get('GTApprox/MoAPointsAssignment').lower() != 'probability':
        info['ClusteringInfo']['Options']['GTApprox/MoAPointsAssignmentConfidence'] = self.options.get('GTApprox/MoAPointsAssignmentConfidence')
      if self.options.get('GTApprox/MoATypeOfWeights').lower() != 'probability':
        info['ClusteringInfo']['Options']['GTApprox/MoAWeightsConfidence'] = self.options.get('GTApprox/MoAWeightsConfidence')

      if logger:
        logger.debug('The following options are really used for clustering:')
        for key, val in iteritems(info['ClusteringInfo']['Options']):
          logger.debug('  %s: %s' % (key, val,))



      moa_builder = self._create_moa_model_ctor(self.options.get('GTApprox/MoATypeOfWeights'),
                                                cluster_model['number_of_clusters'],
                                                len(meta_info.get("x", np.empty((1, approximators[0].size_x)))[0]),
                                                len(meta_info.get("y", np.empty((1, approximators[0].size_f)))[0]),
                                                logger, backend=self._backend)
      moa_builder.set_options(self.options.values)
      moa_builder.set_lf_model(meta_info.get("initial_model"))

      moa_builder.set_encoding_model(cluster_model.get("encoding_model"))
      moa_builder.set_input_norm(points_scaler['mean'], points_scaler['std'])
      size_x_norm = np.count_nonzero(points_scaler['std'])

      for i in xrange(cluster_model['number_of_clusters']):
        moa_builder.set_cluster(i, approximators[i],
                                center=cluster_model['means'][i, :size_x_norm],
                                covariance=cluster_model['covars_cholesky_factor'][i, :size_x_norm, :size_x_norm],
                                weight=cluster_model['weights'][i],
                                points_confidence=_shared.parse_float(self.options.get('GTApprox/MoAPointsAssignmentConfidence')),
                                weights_confidence=_shared.parse_float(self.options.get('GTApprox/MoAWeightsConfidence')))
        info['Local model #%d' % (i + 1)] = approximators[i].info

        orig_center = np.array(points_scaler['std'], copy=True, dtype=float)
        orig_center[orig_center != 0.] *= cluster_model['means'][i, :size_x_norm]
        np.add(orig_center, points_scaler['mean'], out=orig_center)
        info['ClusteringInfo']['Clusters'].append({'Center': orig_center.tolist()})

      moa_builder.set_info(info)

      if 'x' in meta_info and 'y' in meta_info:
        moa_builder.set_train_dataset(meta_info['x'], meta_info['y'], meta_info.get('w'), meta_info.get('tol'))

      with _shared._scoped_options(self, {"GTApprox/OutputTransformation": meta_info.get('output_transform', 'none')}):
        model = moa_builder.get_model(self.options.values)

      if meta_info:
        from . builder import Builder

        Builder._restrict_validity_domain(model, meta_info.get('x'), meta_info.get('restricted_x'), logger)

        dataset = dict((k, meta_info[k]) for k in ('x', 'y', 'tol', 'w', 'x_test', 'y_test', 'w_test') if k in meta_info)
        if dataset:
          dataset['update_stat'] = False # there is no need to update stat because we've already done it by moa_builder.set_train_dataset()
          dataset['store'] = _shared.parse_auto_bool(self.options.get('GTApprox/StoreTrainingSample'), False)
        return Builder._postprocess_model(model=model, full_log=meta_info.get('full_log', ''), initial_options=self.options.values,
                                          initial_model=meta_info.get('initial_model', None), initial_hints=None, logger=logger)
    except:
      pass
    finally:
      if moa_builder is not None:
        moa_builder.cleanup()

      self.options.reset()
      self.options.set(saved_options)

    return model

  @staticmethod
  def _create_moa_model_ctor(weights_type, n_clusters, size_x, size_f, logger, backend=None):
    class MoaCreator(object):
      def __init__(self, backend, weights_type, n_clusters, size_x, size_f, logger):
        weights_type_code = {'probability': 0, 'sigmoid': 1}[weights_type.lower()]

        self._backend = backend
        self.__wrapped_logger0 = self._backend.LoggerCallbackWrapper(None, logger)
        self.__wrapped_logger1 = self._backend.builder_logger_callback_type(self.__wrapped_logger0)
        self.__instance = self._backend.moa_create_builder(weights_type_code, n_clusters, size_x, size_f, self.__wrapped_logger1)
        if not self.__instance:
          raise _ex.GTException('Failed to create Mixture of Approximators builder')

        self.weights_type = weights_type.lower()
        self.size_x = size_x
        self.size_f = size_f

      def cleanup(self):
        if self.__instance is not None:
          self._backend.moa_free_builder(self.__instance)
          self.__instance = None
        self.__wrapped_logger1 = None # remove it explicitly to avoid cross-refs
        self.__wrapped_logger0 = None

      def __throw_last_error(self, success):
        if not success:
          messageSize = _ctypes.c_size_t(0)
          self._backend.moa_get_last_error(self.__instance, _ctypes.c_char_p(), _ctypes.byref(messageSize))
          messageBuffer = _ctypes.create_string_buffer(messageSize.value)
          if self._backend.moa_get_last_error(self.__instance, messageBuffer, _ctypes.byref(messageSize)):
            raise _ex.GTException(_shared._preprocess_utf8(messageBuffer.value))
          else:
            raise _ex.GTException('No particular error description given')

      def set_input_norm(self, mean_x, std_x):
        mean_x = _shared.py_vector_2c(mean_x, name="'mean_x' argument")
        std_x = _shared.py_vector_2c(std_x, name="'std_x' argument")
        self.cluster_dim = np.count_nonzero(std_x.array)
        self.__throw_last_error(self._backend.moa_set_input_properties(self.__instance, mean_x.array.shape[0], mean_x.ptr, mean_x.inc, std_x.array.shape[0], std_x.ptr, std_x.inc))

      def set_cluster(self, cluster_idx, approximator, center, covariance, covariance_kind='L', \
                      weight=None, points_confidence=None, weights_confidence=None):
        # Getting approximator._Model__instance is unsafe and breaks incapsulation but who cares?
        if approximator is None:
          raise _ex.GTException("Approximation for the cluster #%d is invalid." % cluster_idx)
        self.__throw_last_error(self._backend.moa_set_approximator(self.__instance, cluster_idx, approximator._Model__instance))

        if len(center) != self.cluster_dim:
          raise _ex.GTException('The cluster center vector should be %d dimensional (the %d-dimensional vector given for cluster #%d)'\
                                              % (self.cluster_dim, len(center), cluster_idx))

        center = _shared.py_vector_2c(center, vecSize=self.cluster_dim, name="'center' argument")

        self.__throw_last_error(self._backend.moa_set_mean(self.__instance, cluster_idx, center.ptr, center.inc))

        covariance_kind_codes = {'L': 1, 'U': 2, 'O': 0}
        covariance_kind = str(covariance_kind).upper()
        if covariance_kind not in covariance_kind_codes:
          raise _ex.GTException('Invalid or unknown covariance matrix kind: %s (one of %s is expected)' \
                                % (covariance_kind, str([_ for _ in covariance_kind_codes])))

        covariance = _shared.py_matrix_2c(covariance, vecSize=self.cluster_dim, name="'covariance' argument")
        if covariance.array.shape[0] != self.cluster_dim \
          or covariance.array.shape[1] != self.cluster_dim:
          raise _ex.GTException('The covariance matrix should be %d-by-%d dimensional (the %s-dimensional matrix given for cluster #%d)'\
                                              % (self.cluster_dim, self.cluster_dim, str(covariance.array.shape), cluster_idx))
        self.__throw_last_error(self._backend.moa_set_covariance(self.__instance, cluster_idx, covariance.ptr, covariance.ld, covariance_kind_codes[covariance_kind]))

        if self.weights_type == 'probability':
          if weight is None:
            raise _ex.GTException("Cluster weight should be provided in 'probability' mode")
          else:
            self.__throw_last_error(self._backend.moa_set_weight(self.__instance, cluster_idx, weight))
        elif self.weights_type == 'sigmoid':
          if points_confidence is None or weights_confidence is None:
            raise _ex.GTException("Confidence should be provided in 'sigmoid' mode")
          else:
            self.__throw_last_error(self._backend.moa_set_confidence(self.__instance, cluster_idx, points_confidence, weights_confidence))

      def set_log(self, message):
        self.__throw_last_error(self._backend.moa_set_log(self.__instance, message.encode('utf8')))

      def set_train_dataset(self, x, y, w=None, tol=None):
        self._set_train_dataset(0, x)
        self._set_train_dataset(1, y)
        self._set_train_dataset(2, w)
        self._set_train_dataset(3, tol)

      def _set_train_dataset(self, sample_code, data):
        if data is not None:
          shape = (_ctypes.c_int * data.ndim)()
          shape[:] = data.shape[:]

          strides = (_ctypes.c_int * data.ndim)()
          strides[:] = [_ // data.itemsize for _ in data.strides]

          data_ptr = (_ctypes.c_double * (strides[0] * shape[0])).from_address(data.ctypes.data)

          self.__throw_last_error(self._backend.moa_set_sample(self.__instance, sample_code, data.ndim, shape, data_ptr, strides))

      def set_info(self, info):
        self.__throw_last_error(self._backend.moa_set_info(self.__instance, _shared.write_json(info).encode('ascii')))

      def set_options(self, options):
        self.__throw_last_error(self._backend.moa_set_options(self.__instance, _shared.write_json(dict(options)).encode('ascii')))

      def set_lf_model(self, model):
        if model is not None:
          self.__throw_last_error(self._backend.moa_set_lf_model(self.__instance, model._Model__instance))

      def set_encoding_model(self, model):
        if model is not None:
          self.__throw_last_error(self._backend.moa_set_encoding_model(self.__instance, model._Model__instance))

      def get_model(self, options):
        options_str = _shared.write_json(options).encode('ascii') if options else _ctypes.c_char_p()
        approximator_inst = _ctypes.c_void_p(self._backend.moa_create(self.__instance, options_str))
        self.__throw_last_error(approximator_inst)
        return _gtamodel.Model(handle=approximator_inst)

    return MoaCreator((backend if backend is not None else _Backend()), weights_type, n_clusters, size_x, size_f, logger)

  def _postprocess_models(self, models, cluster_models, points_scalers, moas_metainfo):
    # join local moa model into one model
    for data_id in cluster_models:
      for job_id in cluster_models[data_id]:
        local_moa_models = []
        n_clusters = cluster_models[data_id][job_id]['number_of_clusters']
        for i in xrange(n_clusters):
          cluster_data_id = '%s_%s_cluster%d' % (data_id, job_id, i)
          cluster_job_id = "%s_cluster%d" % (job_id, i)
          local_moa_models.append(models[cluster_data_id].pop(cluster_job_id))

        comment = None
        if self._datasets[data_id]:
          data = self._datasets[data_id]
          job_data = self._job_data[data_id][job_id]
          comment = job_data.data.get("comment")

          meta_info = {'x': data['x'], 'y': data['y'], 'w': data.get('weights'), 'tol': data.get('tol'),
                        'restricted_x': data.get('restricted_x'), 'initial_options': job_data.data.get('options'),
                        'initial_model': job_data.data.get('initial_model'),
                        'full_log': '\n'.join([local_model.build_log for local_model in local_moa_models])}
          meta_info.update(moas_metainfo[data_id][job_id])
        else:
          # Usually it is IV session model. It does not need meta info like training dataset.
          meta_info = {}

        logger = _shared.Logger(self._logger, 'debug', prefix=_shared.make_prefix(comment))
        models.setdefault(data_id, {})[job_id] = self._collect_moa(local_moa_models, cluster_models[data_id][job_id],
                                                                    points_scalers[data_id][job_id], meta_info, logger)

    # remove empty dicts from models
    for data_id in list(models.keys()):
      if not models[data_id]:
        del models[data_id]

    # save results of IV models into one model constructed using full sample
    for data_id in list(models.keys()):
      if 'iv_iteration' in data_id:
        continue

      # find models with the same full data id and catclass but different iv iterations
      iv_models = {}
      for other_id in models:
        if other_id.startswith(data_id) and 'iv_iteration' in other_id:
          iv_models[other_id] = models[other_id]

      if iv_models:
        data = self._datasets[data_id]

        current_job_iv_models = {}
        for job_id in models[data_id]:
          # check that for given job_id IV was requested
          for iv_data_id in iv_models:
            for iv_job_id in iv_models[iv_data_id]:
              if job_id in iv_job_id:
                current_job_iv_models[iv_data_id + '_' + iv_job_id] = iv_models[iv_data_id][iv_job_id]

          current_job_data = self._job_data[job_id][data_id].data

          with _shared._scoped_options(self, current_job_data.get('options', {}), keep_options=_utilities._PERMANENT_OPTIONS):
            technique = self.options.get('GTApprox/Technique').lower()

            if technique == 'auto':
              technique = self._select_technique_local(data['x'], data['y'], data.get('weights'), data.get('tol'), current_job_data.get('initial_model'),
                                                       _shared.TeeLogger(self._logger, loggers.LogLevel.ERROR), sample_id=data_id).lower()

            self.options.set('GTApprox/Technique', technique)

            iv = _IterativeIV(data['x'], data['y'], options=self.options.values,
                              outputNoiseVariance=data.get('tol'), weights=data.get('weights'),
                              tensored=technique in ['ta', 'tgp'])
            iv_iteration = 0
            while iv.session_begin():
              iv_model_id = None
              for current_iv_model_id in current_job_iv_models:
                if ('iv_iteration%d' % iv_iteration) in current_iv_model_id:
                  iv_model_id = current_iv_model_id
                  break
              iv.session_end(current_job_iv_models.pop(iv_model_id, None))
              iv_iteration += 1

            iv.save_iv(models[data_id][job_id])

      for model_id in iv_models:
        del models[model_id]

    return models

class SSHBuildManager(DefaultBuildManager):
  """Build models on remote host via SSH"""

  def __init__(self,
               host='localhost',
               port=22,
               username=None,
               password=None,
               workdir=None,
               environment=None,
               private_key_path=''):

    super(SSHBuildManager, self).__init__()

    self.host = host
    self.port = port
    self.username = username
    self.password = password
    self.workdir = workdir
    self.environment = dict(environment) if environment else {}
    self.is_temporary_workdir = False

    self.status_check_interval = 10

    self.omp_thread_limit = 0

    self.private_key = None
    if private_key_path:
      with open(private_key_path, 'rt') as f:
        self.private_key = f.read()

    self._cancelled = False

    self._init_transport()
    self._init_manager()

  # to be overloaded in subclass
  def _init_manager(self):
    from ..batch.batch_manager import SSHBatchManager
    self.manager = SSHBatchManager(self.transport, self)

  # to be overloaded in subclass
  def _init_transport(self):
    from ..batch.command import SSHTransport
    self.transport = SSHTransport(self.host, self.port, self.username, self.password, self.private_key, self)

  def __del__(self):
    try:
      self.transport.release()
    except:
      pass

  def dbg(self, message):
    if self._logger:
      self._logger(loggers.LogLevel.DEBUG, message)

  def info(self, message):
    if self._logger:
      self._logger(loggers.LogLevel.INFO, message)

  def warn(self, message):
    if self._logger:
      self._logger(loggers.LogLevel.WARN, message)

  def error(self, message):
    if self._logger:
      self._logger(loggers.LogLevel.INFO, message)

  def fatal(self, message):
    if self._logger:
      self._logger(loggers.LogLevel.FATAL, message)

  def test_connection(self):
    ## @todo implement for local cluster usage
    if self.host:
      test_ssh_connection(self.host, self.port, self.username, self.password, self.private_key)

  def is_cancel_work_requested(self):
    return self._watcher and not self._watcher()

  def _retry(self, func, handle_errors=()):
    """
    Call function retrying on error of type `TransportException`, `paramiko.SSHException` or enlisted in `handle_errors`
    Note: `handle_errors` must be tuple
    """
    from ..batch.command import SSHException, TransportException, TransportAuthenticationException
    ## @todo to instance consts
    retry_count = 10
    retry_interval = 5

    errors_to_handle = (TransportException, SSHException) + handle_errors
    if not retry_count:
      retry_count = 0
    if not retry_interval:
      retry_interval = 0

    retry_left = max(retry_count, 1)

    while retry_count == 0 or retry_left > 0:
      try:
        return func()
      except TransportAuthenticationException:
        exc_info = sys.exc_info()
        self.error('TransportAuthenticationException: %s' % exc_info[1])
        _shared.reraise(*exc_info)
      except errors_to_handle:
        exc_info = sys.exc_info()
        retry_left = max(retry_left - 1, 0)
        if self.is_cancel_work_requested():
          # give additional retry attempt to perform operation - may be useful to get script output files due to lags in NFS
          if retry_count == 0:
            retry_left = 1
          else:
            retry_left = min(1, retry_left)
        self.error('Error: <%s> %s' % (exc_info[0], exc_info[1]))
        if retry_count == 0 and not self.is_cancel_work_requested():
          self.info('Retrying...')
        else:
          self.info(str(retry_left) + ' retries left')
          if retry_left == 0:
            self.info('Break')
            _shared.reraise(*exc_info)

        if retry_interval is not None:
          time.sleep(retry_interval)

  def _log_std_stream(self, prefix, message):
    if message:
      self.info(prefix + ('\n' + prefix).join(message.splitlines()))

  def _std_script_prefix(self, job_title, id_var, core_imports):
    pkg_name = DefaultBuildManager.__module__.split('.')[:2]
    pkg_version = __import__('.'.join(pkg_name), {}, {}, pkg_name[-1:], level=0).__version__.split('.')
    import_name = '%s_%s' % ('.'.join(pkg_name), '_'.join(pkg_version))
    import_title = '%s version %s' % ('.'.join(pkg_name), '.'.join(pkg_version))

    stream = StringIO()
    stream.write("# coding: utf-8\n")
    stream.write(dedent("""
                  from __future__ import with_statement
                  from __future__ import division

                  import os
                  import sys
                  import signal
                  import platform

                  if len(sys.argv) != 2:
                    raise Exception('Exactly one argument is required')

                  try:
                    %s = int(sys.argv[1])
                  except:
                    %s = None

                  if %s is None:
                    raise Exception('Invalid argument value "%%s" - number is expected' %% sys.argv[1])
                  """ % (id_var, id_var, id_var)))

    stream.write(dedent("""

                  try:
                    import %s
                    exc_info = None
                  except:
                    exc_info = sys.exc_info()[1]

                  if exc_info is not None:
                    raise Exception('Package %s is not found on the remote node %%s: %%s' %% ('; '.join(str(_) for _ in platform.uname()), exc_info))

                  print('=' * 50)
                  print('Job type: %s')
                  print('Host: %%s' %% '; '.join(str(_) for _ in platform.uname()))
                  print('Python: %%s' %% sys.version)
                  print('PATH: %%s' %% os.getenv('PATH'))
                  print('PYTHONPATH: %%s' %% os.getenv('PYTHONPATH'))
                  print('pSeven Core version: %%s' %% %s.__version__)
                  print('DATADVD_LICENSE_FILE: %%s' %% os.getenv('DATADVD_LICENSE_FILE'))
                  print('=' * 50)

                  """ % (import_name, import_title, job_title, import_name)))

    for pkg_name, imp_name, imp_as in core_imports:
      stream.write("from %s%s import %s%s\n" % (import_name, (('.%s' % pkg_name) if pkg_name else ''), imp_name, ((' as %s' % imp_as) if imp_as else '')))

    stream.write("from %s.shared import _safe_pickle_dump, _safe_pickle_load\n" % import_name)

    stream.write(dedent("""

    class SignalWatcher(object):
      def __init__(self, logger, log_level, signals=[signal.SIGTERM, signal.SIGINT]):
        self.logger = logger
        self.log_level = log_level
        self.keep_walking = True
        for sig in signals:
          signal.signal(sig, self.sighandler)

      def sighandler(self, signum, frame):
        if self.logger:
          self.logger(self.log_level, 'SignalWatcher: signum = %s' % (signum))
        print('\\n*** Training Terminated ***\\n')
        self.keep_walking = False

      def __call__(self, reserved=None):
        return self.keep_walking

    """))

    return stream.getvalue()

  def _get_build_moa_script(self):
    return self._std_script_prefix("decomposing design space", "id",
                                   [("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    ("gtapprox", "Builder", None)]) +\
           dedent("""
    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    builder._set_build_manager(DefaultBuildManager())

    with open('clustering_data_ids', 'r') as f:
      for i in range(id):
        data_job_id = f.readline()

    data_id, job_id = data_job_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)


    x = data['x']
    y = data['y']
    tol = data['tol'] if data.get('tol') is not None else None
    weights = data['weights'] if data.get('weights') is not None else None
    options = job_data['options']
    initial_model = job_data.get('initial_model')
    comment = job_data.get('comment')

    moa_metainfo, x, y, weights, tol, initial_model = builder._get_build_manager()._preprocess_moa_output_transform(x, y, options, tol, weights, comment, initial_model, None)

    builder._Builder__logger(LogLevel.INFO, '\\nCreating MoA approximation%s...\\n' % ((" for %s" % comment) if comment else ""))

    builder.options.reset()
    builder.options.set(moa_metainfo.get("initial_options", options))
    builder.options.set({"GTApprox/OutputTransformation": "none"});
    initial_options = builder.options.values

    cluster_model, probabilities, points_scaler = builder._get_build_manager()._make_clustering_local(x, y, initial_options, weights, tol, initial_model, comment)
    cluster_data_generator = builder._get_build_manager()._get_cluster_data_local(x, y, initial_options, weights, tol, probabilities, cluster_model, initial_model, comment)

    for i, (x_cluster, y_cluster, n_cluster, w_cluster, options_cluster) in enumerate(cluster_data_generator):
      input_filename = 'input_data_%s_%s_cluster%d.dat' % (data_id, job_id, i)

      builder.options.reset()
      builder.options.set(initial_options)
      builder.options.set('GTApprox/InternalValidation', False)
      builder.options.set('GTApprox/Technique', builder.options.get('GTApprox/MoATechnique'))
      verb = builder.options.get('GTApprox/Technique')
      verb = "Selecting" if verb.lower() == "auto" else ("Reconsidering %s" % verb)
      builder.options.set('//Service/BuildingCompositeModel', True)
      builder.options.set(options_cluster)

      cluster_comment = 'cluster #%d' % (i + 1)
      if comment:
        cluster_comment = '%s, %s' % (cluster_comment, comment)

      builder._Builder__logger(LogLevel.INFO, '%d points assigned to %s...' % (x_cluster.shape[0], cluster_comment))

      if builder.options.get('GTApprox/Technique').lower() == 'auto':
        builder._Builder__logger(LogLevel.INFO, '\\n%s approximation technique for %s...' % (verb, cluster_comment))
        builder.options.set('GTApprox/Technique', builder._get_build_manager()._select_technique_local(x_cluster, y_cluster, w_cluster, n_cluster, None, builder._Builder__logger, cluster_comment))
        builder._Builder__logger(LogLevel.INFO, ' ')

      cluster_data = {
                      'x': x_cluster,
                      'y': y_cluster,
                      'tol': n_cluster,
                      'weights': w_cluster,
                      'comment': cluster_comment,
                      'options': builder.options.values,
                      'initial_model': None
                     }
      with open(input_filename, 'wb') as f:
        _safe_pickle_dump(cluster_data, f)

    with open('cluster_model_%s %s.pkl' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump({'cluster_model': cluster_model, 'points_scaler': points_scaler,
                         'output_transform': moa_metainfo.get('output_transform'),
                         'initial_model': moa_metainfo.get('initial_model')}, f)
    """)

  def _get_build_script(self):
    return self._std_script_prefix("build model", "id",
                                   [("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    ("gtapprox", "Builder", None)]) +\
           dedent("""
    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    builder._set_build_manager(DefaultBuildManager())

    with open('build_data_ids', 'r') as f:
      for i in range(id):
        data_job_id = f.readline()

    data_id, job_id = data_job_id.rstrip().split(' ')

    # This file contains job_data options that might be updated after tensor samples clustering!!!
    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    model_filename = 'model_%s %s.gtapprox' % (data_id, job_id)
    try:
      os.remove(model_filename)
    except:
      pass

    builder.options.set(job_data.get('options', {}))
    model = builder._build_simple(x=data['x'], y=data['y'], options=data.get('options'), \\
                                  outputNoiseVariance=data.get('tol'), comment=job_data.get('comment'), \\
                                  weights=data.get('weights'), initial_model=job_data.get('initial_model'))


    if model is not None:
      if data.get('restricted_x') is not None:
        builder._restrict_validity_domain(model, data['x'], data.get('restricted_x'), builder._Builder__logger)
      model.save(model_filename)
      print('\\n*** Model successfully built ***\\n')
    else:
      print('\\n*** Failed to build model ***\\n')
    """)

  def _get_prepare_iv_data_script(self):
    return self._std_script_prefix("prepare data for internal validation", "id",
                                   [("gtapprox", "Builder", None),
                                    ("gtapprox", "technique_selection", "_technique_selection"),
                                    ("gtapprox", "utilities", "_utilities"),
                                    ("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("gtapprox.iterative_iv", "_IterativeIV", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    (None, "shared", "_shared")]) +\
           dedent("""
    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    build_manager = DefaultBuildManager()
    builder._set_build_manager(build_manager)

    with open('prepare_iv_data_ids', 'r') as f:
      for i in range(id):
        data_id = f.readline()

    data_id, job_id = data_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    builder.options.set(job_data['options'])

    technique = builder.options.get('GTApprox/Technique').lower()

    if technique == 'auto':
      log_level = LogLevel.from_string(builder.options.get('GTApprox/LogLevel').lower())
      tee_logger = _shared.TeeLogger(logger, log_level)
      technique_selector = _technique_selection.TechniqueSelector(builder.options, tee_logger)
      technique_selector.preprocess_sample(data['x'], data['y'], data.get('tol'), data.get('weights'), True, build_manager)
      preferred_technique, _ = technique_selector.select(output_column=None, initial_model=job_data.get('initial_model'))
      technique = preferred_technique[0]['technique'].lower()

    builder.options.set('GTApprox/Technique', technique)

    iv = _IterativeIV(data['x'], data['y'], options=builder.options.values,
                      outputNoiseVariance=data.get('tol'), weights=data.get('weights'),
                      tensored=technique in ['ta', 'tgp'])
    iv_iteration = 0
    data_id_list = []
    while iv.session_begin():
      current_iteration_data_id = "%s_iv_iteration%d" % (data_id, iv_iteration)
      with open("input_data_%s.dat" % current_iteration_data_id, 'wb') as f:
        iv_comment = job_data['comment'] + ', ' if job_data.get('comment') else ''
        iv_comment += 'IV training session #%d' % iv_iteration
        iv_data = {'x': iv.x, 'y': iv.y, 'tol': iv.outputNoiseVariance, 'weights': iv.weights,
                   'options': iv.options.values, 'initial_model': job_data.get('initial_model'),
                   'comment': iv_comment, 'restricted_x': None}
        data_id_list.append((current_iteration_data_id, iv_comment))
        _safe_pickle_dump(iv_data, f)
        iv.session_end(None)
        iv_iteration += 1

    # write to file newly added data_id's
    with open('iv_data_id_list_%s %s' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump(data_id_list, f)
    """)

  def _get_find_tensor_structure_script(self):
    return self._std_script_prefix("cartesian decomposition", "id",
                                   [("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    ("gtapprox", "Builder", None)]) +\
           dedent("""
    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    builder._set_build_manager(DefaultBuildManager())

    with open('tensor_structure_data_ids', 'r') as f:
      for i in range(id):
        data_id = f.readline()

    data_id, job_id = data_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    tensor_structure = builder._get_build_manager()._find_tensor_structure_local(data['x'], **job_data)

    with open('tensor_structure_%s %s.pkl' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump(tensor_structure, f)
    """)

  def _get_make_iv_split_script(self):
    return self._std_script_prefix("split data for internal validation", "id",
                                   [("gtapprox", "Builder", None),
                                    ("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("gtapprox.iterative_iv", "_IterativeIV", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    (None, "shared", None)]) +\
           dedent("""
    import numpy as np

    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    builder._set_build_manager(DefaultBuildManager())

    with open('make_iv_split_data_ids', 'r') as f:
      for i in range(id):
        data_id = f.readline()

    data_id, job_id = data_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    job_data['options']['GTApprox/IVDeterministic'] = True
    job_data['options']['GTApprox/Technique'] = 'TA' if job_data['tensored_iv'] else 'RSM' # 'Auto' technique is not allowed

    iv = _IterativeIV(data['x'], data['y'], options=job_data['options'], outputNoiseVariance=data.get('tol'),
                      weights=data.get('weights'), tensored=job_data['tensored_iv'])
    session_data_ids = []
    while iv.session_begin():
      session_data_ids.append('%s_%s_iv_split_%d' % (data_id, job_id, len(session_data_ids)))
      filename = 'input_data_%s.dat' % session_data_ids[-1]
      iv_data = {'x': np.array(iv.x), 'y': np.array(iv.y),
                 'tol': np.array(iv.outputNoiseVariance) if iv.outputNoiseVariance is not None else None,
                 'weights': np.array(iv.weights) if iv.weights is not None else None}
      with open(filename, 'wb') as f:
        _safe_pickle_dump(iv_data, f)
      iv.session_end(None)

    with open('iv_split_%s %s.pkl' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump(session_data_ids, f)
    """)

  def _get_landscape_analysis_script(self):
    return self._std_script_prefix("perform data landscape analysis", "id",
                                   [("gtapprox", "Builder", None),
                                    ("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    (None, "shared", None)]) +\
           dedent("""
    import numpy as np

    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    builder._set_build_manager(DefaultBuildManager())

    with open('landscape_analysis_data_ids', 'r') as f:
      for i in range(id):
        data_id = f.readline()

    data_id, job_id = data_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    landscape_analysis_data = builder._get_build_manager()._landscape_analysis_local(data['x'], data['y'], data.get('weights'), data.get('tol'), **job_data)

    with open('landscape_analysis_%s %s.pkl' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump(landscape_analysis_data, f)
    """)

  def _get_clusterize_moa_script(self):
    return self._std_script_prefix("perform clusterization", "id",
                                   [("gtapprox", "Builder", None),
                                    ("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    (None, "shared", None)]) +\
           dedent("""
    import numpy as np

    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    builder._set_build_manager(DefaultBuildManager())

    with open('clusterize_moa_data_ids', 'r') as f:
      for i in range(id):
        data_id = f.readline()

    data_id, job_id = data_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    clusters_model = builder._get_build_manager()._clusterize_moa_local(x=data['x'], y=data['y'], options=job_data['options'], y_tol=data.get('tol'), weights=data.get('weights'),
                                                                        comment=job_data.get('comment'), initial_model=job_data.get('initial_model'), restricted_x=data.get('restricted_x'))

    with open('clusters_models_%s %s.pkl' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump(clusters_model, f)
    """)

  def _get_split_sample_script(self):
    return self._std_script_prefix("split sample to train/test subsamples", "id",
                                   [("gtapprox", "Builder", None)]) +\
           dedent("""
    import numpy as np

    with open('split_sample_data_ids', 'r') as f:
      for i in range(id):
        data_id = f.readline()

    data_id, job_id = data_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    split_data = Builder()._get_build_manager()._split_sample_local(data['x'], data['y'], job_data["train_test_ratio"], job_data.get("tensor_structure"),
                                                                    job_data.get("fixed_structure", False), job_data.get("min_factor_size", 5),
                                                                    job_data.get("seed"), job_data.get("comment"),
                                                                    job_data.get("categorical_inputs_map"),
                                                                    job_data.get("categorical_outputs_map"))

    with open('split_sample_%s %s.pkl' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump(split_data, f)
    """)

  def _select_output_transform_script(self):
    return self._std_script_prefix("select output transformation", "id",
                                   [("gtapprox", "Builder", None),
                                    ("gtapprox.build_manager", "DefaultBuildManager", None),
                                    ("loggers", "StreamLogger, LogLevel", None),
                                    (None, "shared", None)]) +\
           dedent("""
    import numpy as np

    log_level = LogLevel.INFO
    logger = StreamLogger(sys.stdout, log_level)
    watcher = SignalWatcher(logger, log_level)

    builder = Builder()
    builder.set_logger(logger)
    builder.set_watcher(watcher)
    builder._set_build_manager(DefaultBuildManager())

    with open('select_output_transform_data_ids', 'r') as f:
      for i in range(id):
        data_id = f.readline()

    data_id, job_id = data_id.rstrip().split(' ')

    with open("input_data_%s.dat" % data_id, "rb") as f:
      data = _safe_pickle_load(f)

    with open("input_job_data_%s.dat" % job_id, "rb") as f:
      job_data = _safe_pickle_load(f)

    output_transform_data = builder._get_build_manager()._select_output_transform_local(x=data['x'], y=data['y'], weights=data.get('weights'), outputNoiseVariance=data.get('tol'), **job_data)

    with open('select_output_transform_%s %s.pkl' % (data_id, job_id), 'wb') as f:
      _safe_pickle_dump(output_transform_data, f)
    """)

  def set_omp_thread_limit(self, thread_limit):
    self.omp_thread_limit = thread_limit

  def get_omp_thread_limit(self):
    return self.omp_thread_limit

  def _get_omp_thread_limit_str(self):
    omp_thread_limit = self.get_omp_thread_limit()
    if not omp_thread_limit:
      return ''
    return 'export OMP_NUM_THREADS=%d' % omp_thread_limit

  def _prepare_job(self, workdir, data_id_list, script_name, data_id_filename):
    shell = self.environment.get('SHELL', '/bin/sh')
    N = len(data_id_list)
    script_runner = dedent("""
    %s
    %s
    for i in %s
    do
      python %s $i
    done
    """ % ('\n'.join(['    export %s=%s' % (key, value) for key, value in self.environment.items() if key != 'SHELL']),
           self._get_omp_thread_limit_str(), ' '.join([str(_ + 1) for _ in xrange(N)]), script_name))
    self._retry(lambda: self.transport.writeFile(workdir + '/%s' % data_id_filename, BytesIO('\n'.join(data_id_list).encode('utf8'))))

    job_spec = BatchJobSpecification(shell=shell)
    job_spec.command = script_runner
    return job_spec

  @property
  def is_batch(self):
    return True

  def _upload_data(self, data_id, workdir):
    data = self._datasets[data_id]
    if not data:
      return
    if data['is_uploaded'].get(workdir):
      return

    f = BytesIO()
    _shared._safe_pickle_dump(data, f)
    f.seek(0)
    self._retry(lambda: self.transport.writeFile(workdir + '/input_data_%s.dat' % (data_id), f))
    data['is_uploaded'][workdir] = True

  def _upload_job_data(self, job_id, data_id, workdir):
    job_data = self._job_data.get(job_id, {}).get(data_id, _JobData({}))
    # check whether job data are already uploaded
    if job_data.uploaded:
      return

    f = BytesIO()
    _shared._safe_pickle_dump(job_data.data, f)
    f.seek(0)
    self._retry(lambda: self.transport.writeFile(workdir + '/input_job_data_%s.dat' % (job_id), f))
    job_data.uploaded = True

  def _run_jobs(self, job_spec, comments_list, job_comment):
    job_id = self._retry(lambda: self.manager.submit(job_spec))
    self.info('Submitted job id: %s' % job_id)
    self.info('Submitted job commentaries:')
    for index, comment in enumerate(comments_list):
      self.info('* ' + comment if comment else '* %s #%d' % (job_comment, 1+index))
    job_spec.job_id = job_id

    if job_id:
      outPos, errPos = 0, 0
      out_wait_retries = 5
      status = BatchJobStatus.PENDING
      while True:
        if self.is_cancel_work_requested() and not self._cancelled:
          self._cancelled = True
          self.warn('Job execution cancelled')
          self.manager.cancel(job_id)
        status, status_info = self._retry(lambda: self.manager.getStatus(job_id, array_summary=bool(job_spec.array)))
        self.info('Job status: ' + status + ((': %s' % status_info) if status_info else ''))
        [out, outPos, err, errPos] = self.manager.getOutput(job_spec, outPos, errPos, False)
        self._log_std_stream('[stdout] ', out)
        self._log_std_stream('[stderr] ', err)
        if status == BatchJobStatus.PENDING or status == BatchJobStatus.RUNNING:
          time.sleep(self.status_check_interval)
        else:
          break

      if status == BatchJobStatus.ERROR:
        raise Exception('Job %s status: %s%s' % (job_id, status, ((': %s' % status_info) if status_info else '')))
      elif status == BatchJobStatus.FINISHED:
        if not outPos and not errPos:
          # our scripts are always generate some output
          time.sleep(self.status_check_interval)
          [out, outPos, err, errPos] = self.manager.getOutput(job_spec, outPos, errPos, False)
          self._log_std_stream('[stdout] ', out)
          self._log_std_stream('[stderr] ', err)

        exit_code = self.manager.get_exit_code(job_id)
        if exit_code is not None and exit_code != 0:
          raise Exception('Job %s has finished with the exit code %d' % (job_id, exit_code))
    else:
      raise Exception("Can't start job")

    return job_spec

  def _cleanup_temporary_files(self, workdir, files_to_remove=None, job_spec=None):
    if self.workdir is None:
      self._retry(lambda: self.manager._transport.removeDirectory(workdir))
      return
    if files_to_remove:
      for filename in files_to_remove:
        self._retry(lambda: self.manager._transport.deleteFile(getFullPath(workdir, filename)))
    if job_spec:
      self._retry(lambda: self.manager.cleanup(job_spec))

  def _find_tensor_structure_remote(self, workdir):
    location = ''
    if self.host:
      location = 'at %s@%s' % (self.username, self.host)

    job_queue = self._pull_job_queue(job_action='find_tensor_structure')
    if not job_queue:
      return None

    self.info('\nStarted searching for tensor structure %s' % location)

    id_list = []
    comments_list = []

    # transport data
    self.info('Uploading data for searching for tensor structure.\n')
    for data_id, job_id, options, comment in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      id_list.append((data_id, job_id))
      comments_list.append(comment if isinstance(comment, string_types) else _shared._safestr(comment) if comment else '')

    self._retry(lambda: self.transport.writeFile(workdir + '/tensor_structure_script.py',
                                                 BytesIO(self._get_find_tensor_structure_script().encode('utf8'))))

    job_spec = self._prepare_job(workdir, [('%s %s' % id) for id in id_list], 'tensor_structure_script.py', 'tensor_structure_data_ids')
    files_to_remove = ['tensor_structure_data_ids', 'tensor_structure_script.py']

    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, comments_list, job_comment='queued for searching for tensor structure')

    # Download found tensor structures
    self.info('\nDownloading found tensor structures...\n')
    tensor_structures = {}
    for data_id, job_id in id_list:
      try:
        f = BytesIO()
        files_to_remove.append('tensor_structure_%s %s.pkl' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0) # rewind binary data to the beginning
        tensor_structures.setdefault(data_id, {})[job_id] = _shared._safe_pickle_load(f)
      except Exception:
        exc_info = sys.exc_info()
        self.warn('Failed to download tensor structure for %s: %s' % (data_id, exc_info[1]))
        import traceback as tb
        exc_data = StringIO()
        tb.print_exception(exc_info[0], exc_info[1], exc_info[2], file=exc_data)
        self.warn(_shared._safestr(exc_data.getvalue()))
        tensor_structures.setdefault(data_id, {})[job_id] = None

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

    return tensor_structures

  def _make_clustering_remote(self, workdir):
    location = ''
    if self.host:
      location = 'at %s@%s' % (self.username, self.host)

    job_queue = self._pull_job_queue(job_action='build_moa')

    if not job_queue:
      return {}, {}, {}

    self.info('\nClustering for MoA started %s' % location)

    id_list = []
    comments_list = []

    # transport data
    self.info('Uploading data for clustering\n')
    for data_id, job_id, options, comment, initial_model in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      id_list.append((data_id, job_id))
      comments_list.append(comment if isinstance(comment, string_types) else _shared._safestr(comment) if comment else 'Clustering')

    self._retry(lambda: self.transport.writeFile(workdir + '/clustering_script.py', BytesIO(self._get_build_moa_script().encode('utf8'))))
    job_spec = self._prepare_job(workdir, [('%s %s' % id) for id in id_list], 'clustering_script.py', 'clustering_data_ids')
    files_to_remove = ['clustering_data_ids', 'clustering_script.py']

    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, comments_list, 'queued for clustering')

    # download cluster models and points scalers
    self.info('Downloading clustering models\n')
    cluster_models = {}
    points_scalers = {}
    moas_metainfo = {}
    for data_id, job_id in id_list:
      try:
        f = BytesIO()
        files_to_remove.append('cluster_model_%s %s.pkl' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0) # rewind binary data to the beginning
        result = _shared._safe_pickle_load(f)
        cluster_models.setdefault(data_id, {})[job_id] = result['cluster_model']
        points_scalers.setdefault(data_id, {})[job_id] = result['points_scaler']
        moas_metainfo.setdefault(data_id, {})[job_id] = {"output_transform": result.get("output_transform"),
                                                         "initial_model": result.get("initial_model")}
      except Exception:
        e = sys.exc_info()[1]
        self.warn('Failed to download cluster model %s' % data_id)
        self.warn(_shared._safestr(e))
        cluster_models.setdefault(data_id, {})[job_id] = None
        points_scalers.setdefault(data_id, {})[job_id] = None
        moas_metainfo.setdefault(data_id, {})[job_id] = None

    # add data files to build job queue
    saved_options = self.options.values
    try:
      for data_id, job_id, options, comment, initial_model in job_queue:
        cluster_model = cluster_models[data_id][job_id]
        n_clusters = cluster_model['number_of_clusters']
        for i in xrange(n_clusters):
          cluster_comment = 'cluster #%d/%d' % (i + 1, n_clusters)
          if comment:
            cluster_comment = '%s of %s' % (cluster_comment, comment)
          self.options.reset()
          self.options.set(options)
          self.options.set('//Service/BuildingCompositeModel', True)
          self.options.set('GTApprox/InternalValidation', False)
          self.options.set('GTApprox/Technique', self.options.get('GTApprox/MoATechnique'))
          cluster_data_id = '%s_%s_cluster%d' % (data_id, job_id, i)
          cluster_job_id = "%s_cluster%d" % (job_id, i)
          self.submit_job(cluster_data_id, cluster_job_id, options=self.options.values, comment=cluster_comment,
                          initial_model=initial_model, action='build')
          self._upload_job_data(cluster_job_id, cluster_data_id, workdir)
    finally:
      self.options.reset()
      self.options.set(saved_options)

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

    return cluster_models, points_scalers, moas_metainfo

  def _make_iv_split_remote(self, workdir):
    job_queue = self._pull_job_queue(job_action='make_iv_split')
    if not job_queue:
      return None

    id_list = []

    # transport data
    self.info('Uploading data for making IV split.\n')
    for data_id, job_id, options, tensored_iv in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      id_list.append((data_id, job_id))

    self._retry(lambda: self.transport.writeFile(workdir + '/make_iv_split_script.py', BytesIO(self._get_make_iv_split_script().encode('utf8'))))

    job_spec = self._prepare_job(workdir, [('%s %s' % id) for id in id_list], 'make_iv_split_script.py', 'make_iv_split_data_ids')
    files_to_remove = ['make_iv_split_data_ids', 'make_iv_split_script.py']
    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, [], job_comment='queued for making IV split')

    # Download found tensor structures
    self.info('\nDownloading list of splitted IV datasets...\n')
    for data_id, job_id in id_list:
      try:
        f = BytesIO()
        files_to_remove.append('iv_split_%s %s.pkl' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0) # rewind binary data to the beginning
        data_id_list = _shared._safe_pickle_load(f)
        for id in data_id_list:
          self.submit_data(id, None, None)
          self._datasets[id]['is_uploaded'][workdir] = True
      except Exception:
        e = sys.exc_info()[1]
        self.warn('Failed to download list of splitted IV datasets #%s %s' % (data_id, job_id))
        self.warn(_shared._safestr(e))

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

  def _landscape_analysis_remote(self, workdir):
    location = ''
    if self.host:
      location = 'at %s@%s' % (self.username, self.host)

    job_queue = self._pull_job_queue(job_action='landscape_analysis')
    if not job_queue:
      return None

    self.info('\nStarted landscape analysis %s' % location)

    id_list = []

    # transport data
    self.info('Uploading data for landscape analysis.\n')
    for data_id, job_id, options, catvars, seed, n_parts, n_routes, n_fronts, strategy, landscape_analyzer, extra_points_number, extra_points_strategy in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      id_list.append((data_id, job_id))

    self._retry(lambda: self.transport.writeFile(workdir + '/landscape_analysis_script.py',
                                                 BytesIO(self._get_landscape_analysis_script().encode('utf8'))))

    job_spec = self._prepare_job(workdir, [('%s %s' % id) for id in id_list], 'landscape_analysis_script.py', 'landscape_analysis_data_ids')
    files_to_remove = ['landscape_analysis_data_ids', 'landscape_analysis_script.py']

    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, [], job_comment='queued for landscape analysis')

    # Download found tensor structures
    self.info('\nDownloading landscape analysis data...\n')
    landscape_data = {}
    for data_id, job_id in id_list:
      try:
        f = BytesIO()
        files_to_remove.append('landscape_analysis_%s %s.pkl' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0) # rewind binary data to the beginning
        landscape_data.setdefault(data_id, {})[job_id] = _shared._safe_pickle_load(f)
      except Exception:
        e = sys.exc_info()[1]
        self.warn('Failed to download tensor structure #%s' % data_id)
        self.warn(_shared._safestr(e))
        landscape_data.setdefault(data_id, {})[job_id] = None

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

    return landscape_data

  def _clusterize_moa_remote(self, workdir):
    location = ''
    if self.host:
      location = 'at %s@%s' % (self.username, self.host)

    job_queue = self._pull_job_queue(job_action='clusterize_moa')
    if not job_queue:
      return None

    self.info('\nStarted clusterisation for MoA models %s' % location)

    id_list = []

    # transport data
    self.info('Uploading data for clusterization.\n')
    for data_id, job_id, options, comment, initial_model in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      id_list.append((data_id, job_id))

    self._retry(lambda: self.transport.writeFile(workdir + '/clusterize_moa_script.py',
                                                 BytesIO(self._get_clusterize_moa_script().encode('utf8'))))

    job_spec = self._prepare_job(workdir, [('%s %s' % id) for id in id_list], 'clusterize_moa_script.py', 'clusterize_moa_data_ids')
    files_to_remove = ['clusterize_moa_data_ids', 'clusterize_moa_script.py']

    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, [], job_comment='queued for clustering')

    # Download found tensor structures
    self.info('\nDownloading clusterization data...\n')
    clusters_models = {}
    for data_id, job_id in id_list:
      try:
        f = BytesIO()
        files_to_remove.append('clusters_models_%s %s.pkl' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0) # rewind binary data to the beginning
        clusters_models.setdefault(data_id, {})[job_id] = _shared._safe_pickle_load(f)
      except Exception:
        e = sys.exc_info()[1]
        self.warn('Failed to download clusterization data #%s' % data_id)
        self.warn(_shared._safestr(e))
        clusters_models.setdefault(data_id, {})[job_id] = None

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

    return clusters_models

  def _split_sample_remote(self, workdir):
    location = ''
    if self.host:
      location = 'at %s@%s' % (self.username, self.host)

    job_queue = self._pull_job_queue(job_action='split_sample')
    if not job_queue:
      return None

    self.info('\nStarted sample splitting %s' % location)

    id_list = []

    # transport data
    self.info('Uploading data for sample splitting.\n')
    for data_id, job_id, comment, train_test_ratio, tensor_structure, fixed_structure, min_factor_size, seed in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      id_list.append((data_id, job_id))

    self._retry(lambda: self.transport.writeFile(workdir + '/split_sample_script.py',
                                                 BytesIO(self._get_split_sample_script().encode('utf8'))))

    job_spec = self._prepare_job(workdir, [('%s %s' % id) for id in id_list], 'split_sample_script.py', 'split_sample_data_ids')
    files_to_remove = ['split_sample_data_ids', 'split_sample_script.py']

    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, [], job_comment='queued for searching for tensor structure')

    # Download found tensor structures
    self.info('\nDownloading splitted sample...\n')
    split_sample_data = {}
    for data_id, job_id in id_list:
      try:
        f = BytesIO()
        files_to_remove.append('split_sample_%s %s.pkl' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0) # rewind binary data to the beginning
        split_sample_data.setdefault(data_id, {})[job_id] = _shared._safe_pickle_load(f)
      except Exception:
        e = sys.exc_info()[1]
        self.warn('Failed to download splitted sample for %s' % data_id)
        self.warn(_shared._safestr(e))
        split_sample_data.setdefault(data_id, {})[job_id] = None

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

    return split_sample_data

  def _select_output_transform_remote(self, workdir):
    location = ''
    if self.host:
      location = 'at %s@%s' % (self.username, self.host)

    job_queue = self._pull_job_queue(job_action='select_output_transform')
    if not job_queue:
      return None

    self.info('\nStarted output transform selection %s' % location)

    id_list = []

    # transport data
    self.info('Uploading data for the output transform selection.\n')
    for data_id, job_id, options, comment, initial_model in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      id_list.append((data_id, job_id))

    self._retry(lambda: self.transport.writeFile(workdir + '/select_output_transform_script.py',
                                                 BytesIO(self._select_output_transform_script().encode('utf8'))))

    job_spec = self._prepare_job(workdir, [('%s %s' % id) for id in id_list], 'select_output_transform_script.py', 'select_output_transform_data_ids')
    files_to_remove = ['select_output_transform_data_ids', 'select_output_transform_script.py']

    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, [], job_comment='queued for selecting of the output transformation')

    # Download found tensor structures
    self.info('\nDownloading selected output transformation...\n')
    output_transform_data = {}
    for data_id, job_id in id_list:
      try:
        f = BytesIO()
        files_to_remove.append('select_output_transform_%s %s.pkl' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0) # rewind binary data to the beginning
        output_transform_data.setdefault(data_id, {})[job_id] = _shared._safe_pickle_load(f)
      except Exception:
        e = sys.exc_info()[1]
        self.warn('Failed to download selected output transformation for %s' % data_id)
        self.warn(_shared._safestr(e))
        output_transform_data.setdefault(data_id, {})[job_id] = None

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

    return output_transform_data

  def get_tensor_structure(self):
    workdir = self._retry(lambda: self.transport.makeDirectory(self.workdir) if self.workdir else self.transport.makeTempDirectory('p7core.XXXXXX'))
    self.info('\nWorking directory: %s' % workdir)
    return self._find_tensor_structure_remote(workdir)

  def get_landscape_analyzer(self):
    workdir = self._retry(lambda: self.transport.makeDirectory(self.workdir) if self.workdir else self.transport.makeTempDirectory('p7core.XXXXXX'))
    self.info('\nWorking directory: %s' % workdir)
    return self._landscape_analysis_remote(workdir)

  def get_split_sample(self):
    workdir = self._retry(lambda: self.transport.makeDirectory(self.workdir) if self.workdir else self.transport.makeTempDirectory('p7core.XXXXXX'))
    self.info('\nWorking directory: %s' % workdir)
    return self._split_sample_remote(workdir)

  def select_output_transform(self):
    workdir = self._retry(lambda: self.transport.makeDirectory(self.workdir) if self.workdir else self.transport.makeTempDirectory('p7core.XXXXXX'))
    self.info('\nWorking directory: %s' % workdir)
    return self._select_output_transform_remote(workdir)

  def get_moa_clusters(self):
    workdir = self._retry(lambda: self.transport.makeDirectory(self.workdir) if self.workdir else self.transport.makeTempDirectory('p7core.XXXXXX'))
    self.info('\nWorking directory: %s' % workdir)
    return self._clusterize_moa_remote(workdir)

  def get_models(self, cleanup=True):
    location = ''
    if self.host:
      location = 'at %s@%s' % (self.username, self.host)

    self.info('\nModel building started %s' % location)

    if self.workdir:
      workdir = self._retry(lambda: self.transport.makeDirectory(self.workdir))
      self.is_temporary_workdir = False
    else:
      workdir = self._retry(lambda: self.transport.makeTempDirectory('p7core.XXXXXX'))
      self.is_temporary_workdir = True
      self.workdir = workdir

    self.info('\nWorking directory: %s' % workdir)

    # make IV splits first
    self._make_iv_split_remote(workdir)

    # prepare data: split to iv subsets
    saved_options = self.options.values
    try:
      iv_ids_list = []
      files_to_remove = []
      random_seed = np.random.randint(1, np.iinfo(np.int32).max)

      for action in ['build_moa', 'build']:
        # First pass: checking whether IV jobs are needed and modifying its options
        job_queue = self._pull_job_queue(job_action=action)
        for data_id, job_id, options, comment, initial_model in job_queue:
          self.options.reset()
          self.options.set(options)
          if self._datasets[data_id] and _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
            if not _shared.parse_bool(self.options.get('GTApprox/IVDeterministic')):
              self.options.set('GTApprox/IVDeterministic', True)
              self.options.set('GTApprox/IVSeed', random_seed)
            self.options.set('GTApprox/InternalValidation', False)

            iv_ids_list.append((data_id, job_id))

          # resubmit job with possibly updated options
          self.submit_job(data_id, job_id, options=self.options.values, comment=comment, initial_model=initial_model, action=action)

          self._upload_data(data_id, workdir)
          self._upload_job_data(job_id, data_id, workdir)

      if iv_ids_list:
        self._retry(lambda: self.transport.writeFile(workdir + '/prepare_iv_data_script.py', BytesIO(self._get_prepare_iv_data_script().encode('utf8'))))
        job_spec = self._prepare_job(workdir, ['%s %s' % id for id in iv_ids_list], 'prepare_iv_data_script.py', 'prepare_iv_data_ids')
        files_to_remove.append('prepare_iv_data_ids')
        files_to_remove.append('prepare_iv_data_script.py')
        job_spec.workingDirectory = workdir
        job_spec = self._run_jobs(job_spec, '', 'queued IV training session')

        for action in ['build_moa', 'build']:
          # here we are actually sending IV jobs
          job_queue = self._pull_job_queue(job_action=action, cleanup_queue=False)
          for data_id, job_id, options, comment, initial_model in job_queue:
            if (data_id, job_id) in iv_ids_list:
              try:
                f = BytesIO()
                files_to_remove.append('iv_data_id_list_%s %s' % (data_id, job_id))
                self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
                f.seek(0) # rewind binary data to the beginning
                iv_data_id = _shared._safe_pickle_load(f)
              except Exception:
                e = sys.exc_info()[1]
                self.warn('Failed to download data_id_list #%s' % data_id)
                self.warn(_shared._safestr(e))
                iv_data_id = []

              for id, iv_comment in iv_data_id:
                self.options.reset()
                self.options.set(options)
                self.submit_job(id, job_id, action=action, options=self.options.values, comment=iv_comment, initial_model=initial_model)
                self._upload_job_data(job_id, id, workdir)

        self._cleanup_temporary_files(workdir, job_spec=job_spec)
    finally:
      self.options.reset()
      self.options.set(saved_options)

    # make clustering and find tensor structures
    cluster_models, points_scalers, moas_metainfo = self._make_clustering_remote(workdir)

    # build models
    ids_list = []
    comments_list = []

    # first upload all data
    self.info('Uploading data for models construction.\n')

    job_queue = self._pull_job_queue(job_action='build')
    for data_id, job_id, options, comment, initial_model in job_queue:
      self._upload_data(data_id, workdir)
      self._upload_job_data(job_id, data_id, workdir)
      ids_list.append((data_id, job_id))
      comments_list.append(comment if isinstance(comment, string_types) else _shared._safestr(comment) if comment else '')

    self._retry(lambda: self.transport.writeFile(workdir + '/script.py', BytesIO(self._get_build_script().encode('utf8'))))
    job_spec = self._prepare_job(workdir, ['%s %s' % id for id in ids_list], 'script.py', 'build_data_ids')
    files_to_remove.append('build_data_ids')
    files_to_remove.append('script.py')
    job_spec.workingDirectory = workdir

    job_spec = self._run_jobs(job_spec, comments_list, 'queued for building')

    # download models
    self.info('\nDownloading models...\n')
    models = {}
    for data_id, job_id in ids_list:
      try:
        f = BytesIO()
        files_to_remove.append('model_%s %s.gtapprox' % (data_id, job_id))
        self._retry(lambda: self.transport.readFile(workdir + '/' + files_to_remove[-1], targetFile=f))
        f.seek(0)
        models.setdefault(data_id, {})[job_id] = _gtamodel.Model(file=f)
      except Exception:
        e = sys.exc_info()[1]
        self.warn('Failed to download model "%s %s"' % (data_id, job_id))
        self.warn(_shared._safestr(e))
        models.setdefault(data_id, {})[job_id] = None

    # postprocess IV models
    models = self._postprocess_models(models, cluster_models, points_scalers, moas_metainfo)

    self.info('\nModel building finished %s\n' % location)

    self._cleanup_temporary_files(workdir, files_to_remove, job_spec)

    if cleanup:
      self.clean_data()

    return models

  def clean_data(self):
    self.dbg('\nCleaning up working directory')

    try:
      if self.is_temporary_workdir:
        self.transport.removeDirectory(self.workdir)
      else:
        for data_id in self._datasets:
          self.transport.deleteFile(getFullPath(self.workdir, 'input_data_%s.dat' % data_id))
        for job_id in self._job_data:
          self.transport.deleteFile(getFullPath(self.workdir, 'input_job_data_%s.dat' % job_id))
    finally:
      self._datasets = {}
      self._job_data = {}

  def reset_workdir(self):
    if self.is_temporary_workdir:
      self.dbg('\nRemoving working directory')
      self.transport.removeDirectory(self.workdir)

    self.workdir = None
    self.is_temporary_workdir = False


class BatchBuildManager(SSHBuildManager):
  """Build manager to build approx bunch on LSF cluster"""
  def __init__(self,
               host='localhost',
               port=22,
               username=None,
               password=None,
               workdir=None,
               environment=None,
               private_key_path='',
               cluster_options={}):
    self._use_ssh = bool(host)
    super(BatchBuildManager, self).__init__(host, port, username, password, workdir, environment, private_key_path)
    for k in cluster_options:
      if not k in ['exclusive', 'queue', 'array_slot_limit', 'job_name', 'custom_options']:
        raise ValueError("Unknown option '%s' in cluster_options" % k)
    self._cluster_options = cluster_options


  def _init_manager(self):
    from ..batch.batch_manager import LSFBatchManager
    self.manager = LSFBatchManager(self.transport, self)

  # to be overloaded in subclass
  def _init_transport(self):
    from ..batch.command import SSHTransport, LocalTransport
    if self._use_ssh:
      self.transport = SSHTransport(self.host, self.port, self.username, self.password, self.private_key, self)
    else:
      self.transport = LocalTransport(self)


  def get_omp_thread_limit(self):
    if self.omp_thread_limit:
      if self.omp_thread_limit > 1 and not self._cluster_options.get('exclusive'):
        self.warn('Exclusive flag is not set and OMP_NUM_THREADS=%d this may cause perfomance problems' % self.omp_thread_limit)
      return self.omp_thread_limit
    if not self._cluster_options.get('exclusive'):
      self.warn("OMP_NUM_THREADS is limited to 1 because 'exclusive' flag is not set\n")
      return 1
    return 0


  def _prepare_job(self, workdir, data_id_list, script_name, data_id_filename):
    shell = self.environment.get('SHELL', '/bin/sh')
    script_runner = dedent("""
    %s
    %s
    python %s $LSB_JOBINDEX
    """ % ('\n'.join(['    export %s=%s' % (key, value) for key, value in self.environment.items() if key != 'SHELL']),
           self._get_omp_thread_limit_str(), script_name))

    exclusive = self._cluster_options.get('exclusive')
    queue = self._cluster_options.get('queue')
    job_name = self._cluster_options.get('job_name')
    array_slot_limit = self._cluster_options.get('array_slot_limit')
    custom_options = self._cluster_options.get('custom_options')

    N = len(data_id_list)
    self._retry(lambda: self.transport.writeFile(workdir + '/%s' % data_id_filename, BytesIO('\n'.join(data_id_list).encode('utf8'))))

    job_spec = BatchJobSpecification(shell=shell)
    job_spec.task_list = list(range(N))
    job_spec.command = script_runner
    job_spec.name = job_name or 'gtapprox'
    job_spec.array = '1-%d' % N
    if exclusive:
      job_spec.exclusive = True
    if queue:
      job_spec.destination = queue
    if array_slot_limit:
      job_spec.array_slot_limit = array_slot_limit
    if custom_options:
      job_spec.opt_custom_options = custom_options

    return job_spec
