#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

import sys
import ctypes as _ctypes
import numpy as _numpy

from warnings import warn as _warn

from ..six import next, string_types

from .. import shared as _shared
from .. import exceptions as _ex
from .. import blackbox as _blackbox
from .. import loggers as _loggers
from .. import status as _status

class _API(object):
  class BoundsBox(_ctypes.Structure):
    _pack_ = 8
    _fields_ = [("lb", _ctypes.POINTER(_ctypes.c_double)),
                ("inclb", _ctypes.c_size_t),
                ("ub", _ctypes.POINTER(_ctypes.c_double)),
                ("incub", _ctypes.c_size_t),]

    def __init__(self, bounds, copy=False):
      super(_API.BoundsBox, self).__init__()

      assert bounds.ndim == 2 and bounds.shape[0] == 2
      assert bounds.dtype == _ctypes.c_double

      self._bounds = bounds.copy() if copy else bounds

      self.lb = self._bounds[0].ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
      self.ub = self._bounds[1].ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
      self.inclb = self.incub = self._bounds.strides[1] // self._bounds.itemsize

  def __init__(self):
    self.__library = _shared._library

    self.void_ptr_ptr = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)

    # Main DoE generator API
    self.generator_logger_callback_type = _ctypes.CFUNCTYPE(None, _ctypes.c_int, _ctypes.c_void_p, _ctypes.c_void_p)
    self.generator_watcher_callback_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)
    self.generator_response_callback_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_void_p, # ret. value, points count, [in] x, ldx, opaque (null)
                                                              _ctypes.POINTER(_ctypes.c_short), self.c_double_ptr, _ctypes.c_size_t, # [out] f succeeded, [out] f, ldf,
                                                              _ctypes.POINTER(_ctypes.c_short), self.c_double_ptr, _ctypes.c_size_t, # [out] dfdx succeeded, [out] dfdx, ld_dfdx
                                                              _ctypes.c_size_t, _ctypes.c_size_t) # next_df, next_dx


    self.generator_create = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDoEGeneratorAPINew", self.__library))
    self.generator_options_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTDoEGeneratorAPIGetOptionsManager", self.__library))
    self.generator_license_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTDoEGeneratorAPIGetLicenseManager", self.__library))

    self.set_validation_mode = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_short)(("GTDoEGeneratorAPISetValidationMode", self.__library))

    self.generator_build_sample = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. sample object ptr, generator ptr
                                                    _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.POINTER(self.BoundsBox), # budget, dim. x, gen. box
                                                    _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,  # initial sample size, initial X ptr, initial X ld, initial X inc
                                                    _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,  # response (Y) dim, initial Y ptr, initial Y ld, initial Y inc
                                                    self.void_ptr_ptr)(("GTDoEGeneratorAPIBatch", self.__library)) # err. data

    self.generator_start_sequence = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. sample object ptr, generator ptr
                                                      _ctypes.c_size_t, _ctypes.POINTER(self.BoundsBox), # dim. x, gen. box
                                                      self.void_ptr_ptr)(("GTDoEGeneratorAPISequence", self.__library)) # err. data

    self.generator_adaptive_sample = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. sample object ptr, generator ptr
                                                       _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.POINTER(self.BoundsBox), # budget, dim. x, gen. box
                                                       _ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.POINTER(self.BoundsBox), # gradients enabled, response callback, opaque, response callback bounding box
                                                       _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,  # initial sample size, initial X ptr, initial X ld, initial X inc
                                                       _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,  # response (Y) dim, initial Y ptr, initial Y ld, initial Y inc
                                                       self.void_ptr_ptr)(("GTDoEGeneratorAPIAdaptiveBatch", self.__library)) # err. data


    self.generator_release = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTDoEGeneratorAPIFree", self.__library))
    self.generator_logger_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDoEGeneratorAPISetLogger", self.__library))
    self.generator_watcher_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDoEGeneratorAPISetWatcher", self.__library))

    self.sample_read = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_size_ptr,  # succeess indicator, sample object ptr, "response" mode indicator, buffer size ptr
                                         self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t,  # buffer ptr, buffer ld, bufferinc
                                         self.void_ptr_ptr)(("GTDoESampleRead", self.__library)) # err. data
    self.sample_status = _ctypes.CFUNCTYPE(_ctypes.c_int, _ctypes.c_void_p)(("GTDoESampleStatus", self.__library)) # ret. status, design
    self.sample_sequential = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTDoESampleIsSequential", self.__library)) # ret. bool, design
    self.sample_adaptive = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTDoESampleHasResponses", self.__library)) # ret. bool, design
    self.sample_model = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p)(("GTDoESampleModel", self.__library)) # optional model, design
    self.sample_max_size = _ctypes.CFUNCTYPE(_ctypes.c_size_t, _ctypes.c_void_p, _ctypes.c_size_t)(("GTDoESampleMaximalSize", self.__library)) # ret. size, design, is response
    self.sample_get_dim = _ctypes.CFUNCTYPE(_ctypes.c_size_t, _ctypes.c_void_p, _ctypes.c_size_t)(("GTDoESampleDimensionality", self.__library)) # ret. dim, design, is response
    self.sample_read_info = _ctypes.CFUNCTYPE(_ctypes.c_char_p, _ctypes.c_void_p)(("GTDoESampleInfo", self.__library)) # ret. string ptr, design
    self.sample_read_log = _ctypes.CFUNCTYPE(_ctypes.c_char_p, _ctypes.c_void_p)(("GTDoESampleBuildLog", self.__library)) # ret. string ptr, design
    self.sample_release = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTDoESampleRelease", self.__library)) # ret. bool, design

    self.read_default_option_value = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_char_p, _ctypes.c_char_p, self.c_size_ptr,
                                                        self.void_ptr_ptr)(("GTDoEDefaultOptionValue", self.__library)) # ret. bool, option name, option ret. buffer, option ret. buffer size, error descr


_api = _API()

class _Backend(object):
  class _ExternalExceptionWrapper(object):
    def __init__(self, exception_handler, exception_type):
      self.__exception_type = exception_type
      self.__exception_handler = _shared.make_proxy(exception_handler)

    def _process_exception(self, exc_info, msg_prefix=None):
      try:
        if self.__exception_handler:
          if msg_prefix:
            exc_info = exc_info[0], exc_info[0](msg_prefix + _shared._safestr(exc_info[1])), exc_info[2]
          self.__exception_handler._callback_exception(self.__exception_type, exc_info)
      except:
        pass

    def _error_occurred(self):
      return self.__exception_handler and self.__exception_handler._error_occurred()

  class _LoggerCallbackWrapper(_ExternalExceptionWrapper):
    def __init__(self, exception_handler, logger):
      super(_Backend._LoggerCallbackWrapper, self).__init__(exception_handler, _ex.LoggerException)

      self.logger = logger
      self.__ids = dict([(_.id, _) for _ in (_loggers.LogLevel.DEBUG, _loggers.LogLevel.INFO, _loggers.LogLevel.WARN, _loggers.LogLevel.ERROR, _loggers.LogLevel.FATAL)])

    def __call__(self, level, message, userdata):
      try:
        if self.logger is not None:
          self.logger(self.__ids.get(level, level), _shared._preprocess_utf8(_ctypes.string_at(message)))
      except:
        # self._process_exception(sys.exc_info()) # intentionally turned off
        pass

  class _WatcherCallbackWrapper(_ExternalExceptionWrapper):
    def __init__(self, exception_handler, watcher):
      super(_Backend._WatcherCallbackWrapper, self).__init__(exception_handler, _ex.WatcherException)
      self.watcher = watcher

    def __call__(self, userdata):
      try:
        return bool(self.watcher(None)) if self.watcher is not None else True
      except:
        self._process_exception(sys.exc_info())
      return False

  class _ResponseCallbackWrapper(_ExternalExceptionWrapper):
    def __init__(self, exception_handler, blackbox, magic_sig):
      super(_Backend._ResponseCallbackWrapper, self).__init__(exception_handler, _ex.UserEvaluateException)
      self.blackbox = blackbox
      self.size_x = blackbox.size_x()
      self.size_f = blackbox.size_f()
      self.magic_sig = magic_sig.value

    def __call__(self, npoints, x, ldx, opaque, resp_ok, resp, ld_resp, grad_ok, grad, ld_grad, inc_df, inc_dx):
      msg_prefix = None
      try:
        if _ctypes.cast(opaque, _ctypes.c_void_p).value != self.magic_sig:
          _warn("Evaluation callback: Python stack corruption detected! Results may be unpredictable.", RuntimeWarning)

        if npoints > 1 and not (ldx and (not resp or ld_resp) and (not grad or ld_grad)):
          raise _ex.WrongUsageError("Zero lead dimension parameter allowed only for single point evaluations (npoints=%s, ldx=%s, ld_resp=%s, ld_grad=%s)." % (npoints, ldx, ld_resp, ld_grad))

        ldx = ldx or self.size_x
        x_mat = _numpy.frombuffer(_ctypes.cast(x, _ctypes.POINTER(_ctypes.c_double * (ldx * npoints))).contents).reshape(npoints, ldx)
        msg_prefix = "an exception is raised inside blackbox 'evaluate(x=numpy.array(%s))' method - " % (x_mat.shape,)

        if self._error_occurred():
          data = _numpy.empty((npoints, self.blackbox.size_full()))
          data.fill(_shared._NONE)
        else:
          data = self.blackbox._evaluate(x_mat[:, :self.size_x].copy())

          last_error = getattr(self.blackbox, "_last_error", None)
          if last_error:
            setattr(self.blackbox, "_last_error", None)
            self._process_exception(last_error, msg_prefix)
    
          msg_prefix = "an error occurred while processing blackbox response - "
          data = _numpy.array(data, copy=_shared._SHALLOW, dtype=_ctypes.c_double).reshape((npoints, self.blackbox.size_full()))

        if resp:
          resp_ok[0] = 1
          ld_resp = ld_resp or self.size_f
          resp_mat = _numpy.frombuffer(_ctypes.cast(resp, _ctypes.POINTER(_ctypes.c_double * (ld_resp * npoints))).contents).reshape(npoints, ld_resp)
          resp_mat[:, :self.size_f] = data[:, :self.size_f]

        if grad:
          if self.blackbox.gradients_enabled:
            grad_ok[0] = 1
            size_x, size_f = self.size_x, self.size_f
            ld_grad = ld_grad or (size_f * size_x)
            grad_mat = _numpy.frombuffer(_ctypes.cast(grad, _ctypes.POINTER(_ctypes.c_double * (ld_grad * npoints))).contents).reshape(npoints, ld_grad)
            if self.blackbox.gradients_order == _blackbox.GTIBB_GRADIENT_F_ORDER:
              for i in range(size_f):
                grad_mat[:, i*inc_df:(i+1)*inc_df:inc_dx] = data[:, size_f+size_x*i:size_f+(i+1)*size_x]
            else:
              for i in range(size_x):
                grad_mat[:, i*inc_dx:(i+1)*inc_dx:inc_df] = data[:, (i+1)*size_f:(i+2)*size_f]
          else:
            grad_ok[0] = 0

        return True
      except:
        if resp_ok:
          resp_ok[0] = 0
        if grad_ok:
          grad_ok[0] = 0
        self._process_exception(sys.exc_info(), msg_prefix)
      return False

  def __init__(self, api=_api):
    self.__api = api

    # copy attributes from _API
    for _ in dir(self.__api):
      if not _.startswith("_"):
        setattr(self, _, getattr(self.__api, _))

    self.__holded_ptrs = []
    self.__pending_error = None
    self.__logger = self._LoggerCallbackWrapper(self, None)
    self.__watcher = self._WatcherCallbackWrapper(self, None)

    self.__instance = self.generator_create(_ctypes.c_void_p(), _ctypes.c_void_p())
    if not self.__instance:
      raise Exception("Cannot initialize GT DF API.")

    logger_ptr = self.generator_logger_callback_type(self.__logger)
    self.generator_logger_callback(self.__instance, logger_ptr, _ctypes.c_void_p())
    self.__holded_ptrs.append(logger_ptr)

    watcher_ptr = self.generator_watcher_callback_type(self.__watcher)
    self.generator_watcher_callback(self.__instance, watcher_ptr, _ctypes.c_void_p())
    self.__holded_ptrs.append(watcher_ptr)

  def __del__(self):
    if self.__instance:
      self.generator_release(self.__instance)
      self.__instance = None

  def _error_occurred(self):
    return self.__pending_error is not None

  def _callback_exception(self, exc_type, exc_info):
    if exc_info and exc_info[1] is not None and (self.__pending_error is None or \
      (isinstance(self.__pending_error[1], Exception) and not isinstance(exc_info[1], Exception))):
      exc_type = exc_type if isinstance(exc_info[1], Exception) else exc_info[0]
      self.__pending_error = (exc_type, exc_info[1], exc_info[2])

  def _flush_callback_exception(self, ignore_errors, model_error=None):
    if self.__pending_error is not None:
      exc_type, exc_val, exc_tb = self.__pending_error
      self.__pending_error = None
      # logger and watcher exceptions are always ignorable
      if not ignore_errors and exc_type not in (_ex.LoggerException, _ex.WatcherException):
        if model_error is not None and model_error[1]:
          exc_val = ("%s The origin of the exception is: %s" % (_shared._safestr(model_error[1]).strip(), _shared._safestr(exc_val).strip())) if exc_val else model_error[1]
        _shared.reraise(exc_type, exc_val, exc_tb)
      else:
        try:
          if self.__logger.logger is not None:
            self.__logger.logger(_loggers.LogLevel.WARN.id, "Ignorable exception occurred: %s" % exc_val)
        except:
          pass
        finally:
          self.__pending_error = None # clean up to avoid recursive flushes

    if model_error is not None and model_error[0] is not None:
      raise model_error[0](model_error[1] or "Failed to generate DoE.")

  @property
  def options_manager(self):
    manager = _ctypes.c_void_p()
    if not self.generator_options_manager(self.__instance, _ctypes.byref(manager)):
      raise _ex.InternalError("Cannot connect to the options manager interface.")
    return manager

  @property
  def license_manager(self):
    manager = _ctypes.c_void_p()
    if not self.generator_license_manager(self.__instance, _ctypes.byref(manager)):
      raise _ex.InternalError("Cannot connect to the license manager interface.")
    return manager

  def set_logger(self, logger):
    self.__logger.logger = logger

  def set_watcher(self, watcher):
    self.__watcher.watcher = watcher

  @staticmethod
  def _safe_decode_message(message):
    if message:
      try:
        return _ctypes.string_at(message).decode('utf-8', 'replace')
      except:
        pass
    return ""

  @staticmethod
  def _convert_status(status, defres=_status.SUCCESS):
    for item in dir(_status):
      item = getattr(_status, item)
      if isinstance(item, _status.Status) and item.id == status:
        return item
    return defres

  @staticmethod
  def _read_pointer(matrix):
    return matrix.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))

  @staticmethod
  def _read_inc(matrix, dim=0):
    return matrix.strides[dim] // matrix.itemsize

  def _finalize_sample(self, sample_handle, num_points, response=None):
    # In sequential mode we can read any number of points, so we use num_points.
    # Otherwise we must read all available points. It may differ from num_points
    # due to presense of initial sample, full factorial limitations etc.
    num_points_x = _ctypes.c_size_t(num_points if self.sample_sequential(sample_handle) else self.sample_max_size(sample_handle, 0))
    points = _numpy.empty((num_points_x.value, self.sample_get_dim(sample_handle, 0)), dtype=_ctypes.c_double)

    error_description = _ctypes.c_void_p()
    if not self.sample_read(sample_handle, 0, _ctypes.byref(num_points_x), self._read_pointer(points),
                            self._read_inc(points, 0), self._read_inc(points, 1), error_description):
      self._flush_callback_exception(False, _shared._release_error_message(error_description))
    points = points[:num_points_x.value]

    model_handle = self.sample_model(sample_handle)
    if model_handle:
      from ..gtapprox import Model as _ApproxModel
      from ..gtapprox import Builder as _ApproxBuilder
      model = _ApproxModel(handle=model_handle)
      build_log=self._safe_decode_message(self.sample_read_log(sample_handle))

      try:
        x_meta = [{"name": name, "min": lb, "max": ub} for name, lb, ub in zip(response.variables_names(), *response.variables_bounds())]
        y_meta = [{"name": name} for name in response.objectives_names()]
        metainfo = _shared.preprocess_metainfo(x_meta, y_meta, model.size_x, model.size_f)
      except:
        metainfo = None

      model = _ApproxBuilder._postprocess_model(model, build_log, None, None, None, None, metainfo=metainfo)
    else:
      model = None

    if self.sample_adaptive(sample_handle):
      # according to our internal rules (is it time for changes?) we must return numpy array (may be empty) in case of adaptive techniques
      num_points_y = _ctypes.c_size_t(num_points if self.sample_sequential(sample_handle) else self.sample_max_size(sample_handle, 1))
      points_y = _numpy.empty((num_points_y.value, self.sample_get_dim(sample_handle, 1)), dtype=_ctypes.c_double)
      if num_points_y.value:
        if not self.sample_read(sample_handle, 1, _ctypes.byref(num_points_y), self._read_pointer(points_y),
                                                     self._read_inc(points_y, 0), self._read_inc(points_y, 1), error_description):
          self._flush_callback_exception(False, _shared._release_error_message(error_description))
        points_y = points_y[:num_points_y.value]

    else:
      points_y = None

    info = _shared.parse_json(self._safe_decode_message(self.sample_read_info(sample_handle)))
    # log = self._safe_decode_message(self.sample_read_log(sample_handle))
    status = self._convert_status(self.sample_status(sample_handle))

    return info, points, points_y, status, model

  def _finalize_validation(self, sample_handle, num_points):
    # In sequential mode we can read any number of points, so we use num_points.
    # Otherwise we must read all available points. It may differ from num_points
    # due to presense of initial sample, full factorial limitations etc.
    num_points_x = _ctypes.c_size_t(num_points if self.sample_sequential(sample_handle) else self.sample_max_size(sample_handle, 0))
    points = _numpy.empty((num_points_x.value, 0), dtype=_ctypes.c_double) # always create empty matrix with proper length

    info = _shared.parse_json(self._safe_decode_message(self.sample_read_info(sample_handle)))
    status = self._convert_status(self.sample_status(sample_handle))

    return info, points, None, status, None

  @staticmethod
  def _sequence(api, sample_handle):
    try:
      error_description = _ctypes.c_void_p()

      x_buf = _numpy.empty(api.sample_get_dim(sample_handle, 0), dtype=_ctypes.c_double)
      x_ptr = x_buf.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
      x_inc = x_buf.strides[0] // x_buf.itemsize
      num_points = _ctypes.c_size_t(1)

      yield None # the object is not generator until the first yield

      while api.sample_read(sample_handle, 0, _ctypes.byref(num_points), x_ptr, 0, x_inc, error_description) and num_points.value:
        yield x_buf.copy()

      if error_description:
        ex_type, ex_message = _shared._release_error_message(error_description)
        raise ex_type(ex_message)
    finally:
      api.sample_release(sample_handle)

  def start_sequence(self, bounds):
    # We expect all arguments are valid at this point, so no conversions, just paranoid asserts
    box = self.BoundsBox(bounds)

    self._flush_callback_exception(False) # cleanup errors first

    sample_handle = None

    try:
      error_description = _ctypes.c_void_p()
      sample_handle = self.generator_start_sequence(self.__instance, bounds.shape[1], _ctypes.byref(box), _ctypes.byref(error_description))
      if not sample_handle:
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      info = self._safe_decode_message(self.sample_read_info(sample_handle))
      # log = self._safe_decode_message(self.sample_read_log(sample_handle))
      status = self._convert_status(self.sample_status(sample_handle))

      points = self._sequence(self.__api, sample_handle)
      next(points) # the first next() is required, otherwise generator object may be destroyed without any cleanup

      return info, points, None, status, None
    finally:
      # clean up errors if any occurred
      self._flush_callback_exception(True)

  def generate_sample(self, budget, bounds, init_x, init_y, validation_mode=False):
    # We expect all arguments are valid at this point, so no conversions, just paranoid asserts
    box = self.BoundsBox(bounds)

    if init_x is not None:
      assert init_x.shape[1] == bounds.shape[1]
      init_x_size, init_x_ptr = init_x.shape[0], self._read_pointer(init_x)
      init_x_ld, init_x_inc = self._read_inc(init_x, 0), self._read_inc(init_x, 1)
    else:
      init_x_size, init_x_ptr, init_x_ld, init_x_inc = 0, self.c_double_ptr(), 0, 0

    if init_y is not None:
      assert init_x is not None
      assert init_x.shape[0] == init_y.shape[0]
      init_y_dim, init_y_ptr = init_y.shape[1], self._read_pointer(init_y)
      init_y_ld, init_y_inc = self._read_inc(init_y, 0), self._read_inc(init_y, 1)
    else:
      init_y_dim, init_y_ptr, init_y_ld, init_y_inc = 0, self.c_double_ptr(), 0, 0

    self._flush_callback_exception(False) # cleanup errors first

    sample_handle = None

    try:
      self.set_validation_mode(self.__instance, validation_mode)
      error_description = _ctypes.c_void_p()
      sample_handle = self.generator_build_sample(self.__instance, budget, bounds.shape[1], _ctypes.byref(box),
        init_x_size, init_x_ptr, init_x_ld, init_x_inc, init_y_dim, init_y_ptr, init_y_ld, init_y_inc,
        _ctypes.byref(error_description))
      if not sample_handle or _shared._desktop_mode():
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      return self._finalize_validation(sample_handle, budget + init_x_size) if validation_mode\
        else self._finalize_sample(sample_handle, budget + init_x_size)
    finally:
      # clean up errors if any occurred
      self.sample_release(sample_handle)
      self._flush_callback_exception(True)
      self.set_validation_mode(self.__instance, False)

  def adaptive_sample(self, budget, bounds, response, init_x, init_y, validation_mode=False):
    # We expect all arguments are valid at this point, so no conversions, just paranoid asserts
    box = self.BoundsBox(bounds)
    bb_box = self.BoundsBox(_numpy.array(response.variables_bounds(), dtype=_ctypes.c_double), True)

    try:
      problem, sample_y = response._make_adaptive_only(init_y)
    except:
      problem, sample_y = response, init_y

    assert bounds.shape[1] == problem.size_x()

    if init_x is not None:
      assert init_x.shape[1] == bounds.shape[1]
      init_x_size, init_x_ptr = init_x.shape[0], self._read_pointer(init_x)
      init_x_ld, init_x_inc = self._read_inc(init_x, 0), self._read_inc(init_x, 1)
    else:
      init_x_size, init_x_ptr, init_x_ld, init_x_inc = 0, self.c_double_ptr(), 0, 0

    if sample_y is not None:
      assert init_x is not None
      assert init_x.shape[0] == sample_y.shape[0]
      assert sample_y.shape[1] == problem.size_f()
      init_y_ptr = self._read_pointer(sample_y)
      init_y_ld = self._read_inc(sample_y, 0)
      init_y_inc = self._read_inc(sample_y, 1)
    else:
      init_y_ptr, init_y_ld, init_y_inc = self.c_double_ptr(), 0, 0

    self._flush_callback_exception(False) # cleanup errors first

    sample_handle = None

    try:
      self.set_validation_mode(self.__instance, validation_mode)

      magic_sig = _ctypes.c_void_p(0xAACC00FF)
      evaluate_wrapper = self._ResponseCallbackWrapper(self, problem, magic_sig)
      evaluate_callback = self.generator_response_callback_type(evaluate_wrapper)

      error_description = _ctypes.c_void_p()
      sample_handle = self.generator_adaptive_sample(self.__instance, budget, problem.size_x(), _ctypes.byref(box),
                                                     problem.gradients_enabled, evaluate_callback, magic_sig, _ctypes.byref(bb_box),
                                                     init_x_size, init_x_ptr, init_x_ld, init_x_inc,
                                                     problem.size_f(), init_y_ptr, init_y_ld, init_y_inc,
                                                     _ctypes.byref(error_description))
      if not sample_handle:
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      info, points, points_y, status, model = self._finalize_validation(sample_handle, budget + init_x_size) if validation_mode\
                                          else self._finalize_sample(sample_handle, budget + init_x_size, response=problem)

      try:
        points_y = problem._reconstruct_nonadaptive(points, points_y, init_x, init_y)
      except:
        pass

      return info, points, points_y, status, model
    finally:
      # clean up errors if any occurred
      self.sample_release(sample_handle)
      self._flush_callback_exception(True)
      self.set_validation_mode(self.__instance, False)

  def default_option_value(self, name):
    try:
      cname = _ctypes.c_char_p(name.encode("utf8") if isinstance(name, string_types) else name)
    except:
      exc_info = sys.exc_info()
      _shared.reraise(_ex.InvalidOptionNameError, ("Invalid option name is given: %s" % name), exc_info[2])

    errdesc = _ctypes.c_void_p()
    csize = _ctypes.c_size_t(0)
    if not self.read_default_option_value(cname, _ctypes.c_char_p(), _ctypes.byref(csize), _ctypes.byref(errdesc)):
      _shared._raise_on_error(False, "Failed to read default option value", errdesc)
    cvalue = (_ctypes.c_char * csize.value)()
    if not self.read_default_option_value(cname, _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize), _ctypes.byref(errdesc)):
      _shared._raise_on_error(False, "Failed to read default option value", errdesc)
    return _shared._preprocess_utf8(cvalue.value)
