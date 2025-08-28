#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
gtdr.Builder - Python DR-model builder interface
------------------------------------------------

.. currentmodule:: da.p7core.gtdr.builder

"""
from __future__ import division

import sys
import ctypes as _ctypes
import numpy as _numpy

from datetime import datetime
from warnings import warn as _warn

from ..six.moves import xrange

from .. import shared as _shared
from .. import options as _options
from .. import license as _license
from .. import exceptions as _ex
from .. import blackbox as _blackbox
from .. import loggers as _loggers

from . import model as _model

from ..utils import bbconverter as _bbconverter

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.void_ptr_ptr = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)

    # Main approx builder API
    self.builder_logger_callback_type = _ctypes.CFUNCTYPE(None, _ctypes.c_int, _ctypes.c_void_p, _ctypes.c_void_p)
    self.builder_watcher_callback_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)
    self.builder_response_callback_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_void_p, # ret. value, points count, [in] x, ldx, opaque (null)
                                                            _ctypes.POINTER(_ctypes.c_short), self.c_double_ptr, _ctypes.c_size_t, # [out] f succeeded, [out] f, ldf,
                                                            _ctypes.POINTER(_ctypes.c_short), self.c_double_ptr, _ctypes.c_size_t, # [out] dfdx succeeded, [out] dfdx, ld_dfdx
                                                            _ctypes.c_size_t, _ctypes.c_size_t) # next_df, next_dx

    self.builder_create = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDRBuilderAPINew", self.__library))
    self.builder_options_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTDRBuilderAPIGetOptionsManager", self.__library))
    self.builder_license_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTDRBuilderAPIGetLicenseManager", self.__library))

    self.builder_build_dim = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. model ptr, builder ptr
                                               _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, # orig. dim, compressed dim., sample size,
                                               self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t, # sample ptr, next vec., next coord,
                                               _ctypes.c_char_p, _ctypes.c_char_p, self.void_ptr_ptr)(("GTDRBuilderAPIBuildByDim", self.__library)) # comment, annotations, err. data

    self.builder_build_err = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. model ptr, builder ptr
                                               _ctypes.c_size_t, _ctypes.c_double, _ctypes.c_char_p, _ctypes.c_char_p, # orig. dim, err threshold, cw err type, agg err type
                                               _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t, # sample size, sample ptr, next vec., next coord,
                                               _ctypes.c_char_p, _ctypes.c_char_p, self.void_ptr_ptr)(("GTDRBuilderAPIBuildByError", self.__library)) # comment, annotations, err. data

    self.builder_build_fe = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. model ptr, builder ptr
                                               _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, # orig. dim, compressed dim., response dim., sample size,
                                               self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t, # x ptr, next x vec., next x coord,
                                               self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t, # f ptr, next f vec., next f coord,
                                               _ctypes.c_char_p, _ctypes.c_char_p, self.void_ptr_ptr)(("GTDRBuilderAPIBuildFEBySample", self.__library)) # comment, annotations, err. data

    self.builder_build_fe_bb = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. model ptr, builder ptr
                                                 _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, # budget, orig. dim, compressed dim., response dim.,
                                                 self.c_double_ptr, _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, # lower bounds ptr, lower bounds inc, upper bounds ptr, upper bounds inc,
                                                 _ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, # gradients enabled, response callback, opaque
                                                 _ctypes.c_char_p, _ctypes.c_char_p, self.void_ptr_ptr)(("GTDRBuilderAPIBuildFEByBlackbox", self.__library)) # comment, annotations, err. data

    self.builder_release = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTDRBuilderAPIFree", self.__library))
    self.builder_logger_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDRBuilderAPISetLogger", self.__library))
    self.builder_watcher_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDRBuilderAPISetWatcher", self.__library))

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
          raise _ex.WrongUsageError("Zero lead dimension parameter allowed only for signle point evaluations (npoints=%s, ldx=%s, ld_resp=%s, ld_grad=%s)." % (npoints, ldx, ld_resp, ld_grad))

        ldx = ldx or self.size_x
        x_mat = _numpy.frombuffer(_ctypes.cast(x, _ctypes.POINTER(_ctypes.c_double * (ldx * npoints))).contents).reshape(npoints, ldx)
        msg_prefix = "an exception is raised inside blackbox 'evaluate(x=numpy.array(%s))' method - " % (x_mat.shape,)
        data = self.blackbox.evaluate(x_mat[:, :self.size_x])
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

    self.__instance = self.builder_create(_ctypes.c_void_p(), _ctypes.c_void_p())
    if not self.__instance:
      raise Exception("Cannot initialize GT DR API.")

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
      raise model_error[0](model_error[1] or "Failed to create GTDR model.")

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

  @staticmethod
  def _encode_message(message):
    if message is not None:
      try:
        return message.encode('utf-8')
      except (AttributeError, UnicodeDecodeError):
        return message
    return _ctypes.c_char_p()

  def build_dim(self, x, dim, comment):
    self._flush_callback_exception(False) # cleanup errors first

    try:
      error_description = _ctypes.c_void_p()
      model_handle = self.builder_build_dim(self.__instance, x.shape[1], dim, x.shape[0],
                                            x.ctypes.data_as(self.c_double_ptr), x.strides[0] // x.itemsize, x.strides[1] // x.itemsize,
                                            self._encode_message(comment), _ctypes.c_char_p(), _ctypes.byref(error_description))
      if not model_handle:
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      return _model.Model(handle=model_handle)
    finally:
      # clean up errors if any occurred
      self._flush_callback_exception(True)

  def build_err(self, x, err, comment):
    self._flush_callback_exception(False) # cleanup errors first

    try:
      error_description = _ctypes.c_void_p()
      model_handle = self.builder_build_err(self.__instance, x.shape[1], err, _ctypes.c_char_p(), _ctypes.c_char_p(), x.shape[0],
                                            x.ctypes.data_as(self.c_double_ptr), x.strides[0] // x.itemsize, x.strides[1] // x.itemsize,
                                            self._encode_message(comment), _ctypes.c_char_p(), _ctypes.byref(error_description))
      if not model_handle:
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      return _model.Model(handle=model_handle)
    finally:
      # clean up errors if any occurred
      self._flush_callback_exception(True)


  def build_fe(self, x, y, dim, comment):
    self._flush_callback_exception(False) # cleanup errors first

    try:
      error_description = _ctypes.c_void_p()
      model_handle = self.builder_build_fe(self.__instance, x.shape[1], dim, y.shape[1], x.shape[0],
                                           x.ctypes.data_as(self.c_double_ptr), x.strides[0] // x.itemsize, x.strides[1] // x.itemsize,
                                           y.ctypes.data_as(self.c_double_ptr), y.strides[0] // y.itemsize, y.strides[1] // y.itemsize,
                                           self._encode_message(comment), _ctypes.c_char_p(), _ctypes.byref(error_description))
      if not model_handle:
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      return _model.Model(handle=model_handle)
    finally:
      # clean up errors if any occurred
      self._flush_callback_exception(True)

  def build_fe_bb(self, budget, bb, dim, comment):
    lb, ub = bb.variables_bounds()
    lb = _shared.py_vector_2c(lb, name="Blackbox variables lower bounds")
    ub = _shared.py_vector_2c(ub, name="Blackbox variables upper bounds")

    self._flush_callback_exception(False) # cleanup errors first

    try:
      magic_sig = _ctypes.c_void_p(0xAACC00FF)
      evaluate_wrapper = self._ResponseCallbackWrapper(self, bb, magic_sig)
      evaluate_callback = self.builder_response_callback_type(evaluate_wrapper)

      error_description = _ctypes.c_void_p()
      model_handle = self.builder_build_fe_bb(self.__instance, budget, bb.size_x(), dim, bb.size_f(),
                                              lb.ptr, lb.inc, ub.ptr, ub.inc, bb.gradients_enabled, evaluate_callback, magic_sig,
                                              self._encode_message(comment), _ctypes.c_char_p(), _ctypes.byref(error_description))
      evaluate_callback.blackbox = None
      if not model_handle:
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      return _model.Model(handle=model_handle)
    finally:
      # clean up errors if any occurred
      self._flush_callback_exception(True)

class Builder(object):
  """Dimension reduction model builder."""
  def __init__(self, backend=None):
    self._backend = backend or _Backend()
    self._logger = None
    self._watcher = None

  def set_logger(self, logger):
    """Set logger.

    :param logger: logger object
    :return: ``None``

    Used to set up a logger for the build process. See section :ref:`gen_loggers` for details.
    """
    self._logger = _shared.wrap_with_exc_handler(logger, _ex.LoggerException)
    self._backend.set_logger(self._logger)

  def set_watcher(self, watcher):
    """Set watcher.

    :param watcher: watcher object
    :return: ``None``

    Used to set up a watcher for the build process. See section :ref:`gen_watchers` for details.
    """
    self._set_watcher(_shared.wrap_with_exc_handler(watcher, _ex.WatcherException))

  def _set_watcher(self, watcher):
    old_watcher = self._watcher
    self._watcher = watcher
    self._backend.set_watcher(self._watcher)
    return old_watcher

  @property
  def options(self):
    """Builder options.

    :type: :class:`~da.p7core.Options`

    General options interface for the builder. See section :ref:`gen_options` for usage and the GTDR :ref:`ug_gtdr_options`.

    """
    return _options.Options(self._backend.options_manager, self._backend)

  @property
  def license(self):
    """Builder license.

    :type: :class:`~da.p7core.License`

    General license information interface. See section :ref:`gen_license_usage` for details.

    """
    return _license.License(self._backend.license_manager, self._backend)

  def build(self, x=None, y=None, dim=None, error=None, blackbox=None, budget=None, options=None, comment=None, annotations=None, x_meta=None):
    r"""Train a dimension reduction model.

    :param x: training sample, input part (values of variables)
    :param y: training sample, optional response part (function values)
    :param dim: output dimension, optional
    :param error: error threshold, optional
    :param blackbox: Feature Extraction blackbox, optional
    :param budget: blackbox budget
    :param options: option settings
    :param comment: text comment
    :param annotations: extended comment and notes
    :param x_meta: descriptions of inputs
    :return: trained model
    :type x: :term:`array-like`, 2D
    :type y: :term:`array-like`, 1D or 2D
    :type dim: ``int``, ``long``
    :type error: ``float``
    :type blackbox: :class:`~da.p7core.blackbox.Blackbox`, :class:`.gtapprox.Model`, or :class:`.gtdf.Model`
    :type budget: ``int``, ``long``
    :type options: ``dict``
    :type comment: ``str``
    :type annotations: ``dict``
    :type x_meta: ``list``
    :rtype: :class:`~da.p7core.gtdr.Model`

    .. versionchanged:: 6.20
       :arg:`blackbox` may be a :class:`.gtapprox.Model` or a :class:`.gtdf.Model`.

    .. versionchanged:: 6.25
       ``pandas.DataFrame`` and ``pandas.Series`` are supported as the :arg:`x`, :arg:`y` training samples.

    Trains a dimension reduction model (codec) which provides vector compression and decompression methods.

    In the sample-based modes, :arg:`x` is always a 2D array because there is no meaningful interpretation of an 1D array.
    However, 1D :arg:`y` is supported as a simplified form for the case of 1D output when using sample-based Feature Extraction.

    Valid argument combinations and mode selection:

    ================== ================== =================== ===========================
    Passed arguments   Technique          Optional arguments  Ignored arguments
    ================== ================== =================== ===========================
    x, dim             dimension-based             \-         y, error, blackbox, budget
    x, error           error-based                 \-         y, dim, blackbox, budget
    x, y               Feature Extraction         dim         error, blackbox, budget
    blackbox, budget   Feature Extraction         dim         x, y, error
    ================== ================== =================== ===========================

    All other combinations of arguments are invalid.

    Example::

      >>> from da.p7core.gtdr import Builder
      >>> sample = [[ 0.1, 0.2, 0.3, 0.4],
                    [ 0.2, 0.3, 0.4, 0.41],
                    [ 0.3, 0.4, 0.5, 0.39]]
      >>> model = Builder().build(sample, dim=1)
      >>> model.original_dim
      4
      >>> model.compressed_dim
      1

    .. versionchanged:: 6.14
       added the :arg:`comment`, :arg:`annotations`, and :arg:`x_meta` parameters.

    The :arg:`comment` and :arg:`annotations` parameters add optional notes to model.
    The :arg:`comment` string is stored to the model's :attr:`~da.p7core.gtdr.Model.comment`.
    The :arg:`annotations` dictionary can contain more notes or other supplementary information;
    all keys and values in :arg:`annotations` must be strings.
    Annotations are stored to the model's :attr:`~da.p7core.gtdr.Model.annotations`.
    After training a model, you can also edit its
    :attr:`~da.p7core.gtdr.Model.comment` and :attr:`~da.p7core.gtdr.Model.annotations`
    using :meth:`~da.p7core.gtdr.Model.modify()`.

    The :arg:`x_meta` parameter adds names and descriptions of model inputs.
    It is a list of length equal to the number of inputs,
    or the number of columns in :arg:`x`.
    List element can be a string (Unicode) or a dictionary.
    A string specifies a name for the respective input.
    It must be a valid identifier according to the FMI standard,
    so there are certain restrictions for names (see below).
    A dictionary describes a single input and can have the following keys
    (all keys are optional, all values must be ``str`` or ``unicode``):

    * ``"name"``:
      contains the name for this input.
      If this key is omitted, a default name will be saved to the model ---
      :samp:`"x[{i}]"` where :samp:`{i}` is the index of the respective column in :arg:`x`.
    * ``"description"``:
      contains a brief description, any text.
    * ``"quantity"``:
      physical quantity, for example ``"Angle"`` or ``"Energy"``.
    * ``"unit"``:
      measurement units used for this input, for example ``"deg"`` or ``"J"``.

    Names of inputs and outputs must satisfy the following rules:

    * Name must not be empty.
    * All names must be unique.
    * The only whitespace character allowed in names is the ASCII space,
      so ``\\t``, ``\\n``, ``\\r``, and various Unicode whitespace characters are prohibited.
    * Name cannot contain leading or trailing spaces, and cannot contain two or more consecutive spaces.
    * Name cannot contain leading or trailing dots, and cannot contain two or more consecutive dots,
      since dots are commonly used as name separators.
    * Parts of the name separated by dots must not begin or end with a space,
      so the name cannot contain ``'. '`` or ``' .'``.
    * Name cannot contain control characters and Unicode separators.
      Prohibited Unicode character categories are:
      ``Cc``, ``Cf``, ``Cn``, ``Co``, ``Cs``, ``Zl``, ``Zp``, ``Zs``.
    * Name cannot contain characters from this set: ``:"/\\|?*``.

    Input descriptions are stored to model :attr:`~da.p7core.gtdr.Model.details`
    (the ``"Input Variables"`` key).
    If you do not specify a name or description for some input,
    its information in :attr:`~da.p7core.gtdr.Model.details` contains only the default name
    (:samp:`"x[{i}]"`).
    When you export a model, input descriptions are found in the comments in the exported code.

    """
    with _shared.sigint_watcher(self):
      return self._do_build(x, y, dim, error, blackbox, budget, options, comment, annotations, x_meta)

  def _do_build(self, x=None, y=None, dim=None, error=None, blackbox=None, budget=None, options=None, comment=None, annotations=None, x_meta=None):
    time_start = datetime.now()

    if _shared.check_args((x, dim), (y, error, blackbox)):
      problem_type = "GT_DR_BY_DIM"
    elif _shared.check_args((x, error), (y, dim, blackbox)):
      problem_type = "GT_DR_BY_ERR"
    elif _shared.check_args((x, y), (error, blackbox)):
      problem_type = "GT_DR_FE"
    elif _shared.check_args((blackbox, budget), (x, y, error)):
      problem_type = "GT_DR_FE_BB"
    else:
      raise _ex.GTException('Inconsistent set of arguments!')

    # save original logger, watcher and options
    saved_logger = self._logger
    saved_watcher = self._watcher
    saved_options = self.options.values

    if options is not None:
      _shared.check_concept_dict(options, 'options')
      self.options.set(options)

    trained_model = None
    try:
      initial_options = self.options.values

      log_level = _loggers.LogLevel.from_string(self.options.get('GTDR/LogLevel').lower())
      local_logger = _shared.TeeLogger(self._logger, log_level)
      self.set_logger(local_logger)
      # now level is handled by the tee logger
      if local_logger.private_log_level != log_level:
        self.options.set('GTDR/LogLevel', str(local_logger.private_log_level))

      local_logger(_loggers.LogLevel.INFO, 'Training started at %s\n' % str(time_start))
      metainfo_template = None

      if problem_type in ("GT_DR_BY_DIM", "GT_DR_BY_ERR", "GT_DR_FE"):
        metainfo_template = _shared.create_metainfo_template(x, None)
        x = _shared.as_matrix(x, name="Input part of the training sample ('x' argument)")

        valid_points = _numpy.isfinite(x, casting='unsafe').all(axis=1)
        if not valid_points.all():
          if 'ignore' == str(self.options.get('GTDR/InputNanMode')).lower():
            x = x[valid_points, :]
            local_logger(_loggers.LogLevel.WARN, '%d out of %d input points are ignored according to \'GTDR/InputNanMode\'=\'ignore\' option value.' % (len(valid_points) - valid_points.sum(), len(valid_points)))
          else:
            raise _ex.NanInfError('The input (\'x\') sample contains at least one NaN or Inf value!')
        else:
          valid_points = None

        if not len(x):
          raise ValueError('Training set is empty!')

        size_x = x.shape[1]
        if size_x <= 0:
          raise ValueError('X dimensionality should be greater than zero!')
        if y is not None:
          expected_size = len(x) if valid_points is None else len(valid_points)
          y = _shared.as_matrix(y, shape=(expected_size, None), name="Output part of the training sample ('y' argument)")
          if valid_points is not None:
            y = y[valid_points, :]
          if _shared.isNanInf(y):
            raise _ex.NanInfError('Output data contains NaN or Inf value!')
          if not y.shape[1]:
            raise ValueError('Y dimensionality should be greater than zero!')
      elif problem_type in ("GT_DR_FE_BB",):
        original_bb = blackbox
        blackbox, _, warns, _ = _bbconverter.preprocess_blackbox(blackbox, "GTDR Feature Extraction", None)
        if warns:
          local_logger(_loggers.LogLevel.WARN, warns)

        lb, ub = blackbox.variables_bounds()
        if len(lb) != blackbox.size_x() or len(ub) != blackbox.size_x():
          raise ValueError('Invalid blackbox generation bounds length: lower %d, upper %d, expected %d' % (len(lb), len(ub), blackbox.size_x()))

        _shared.check_concept_int(budget, 'budget')
        if budget <= 0:
          raise ValueError('Evaluations budget \'budget\'=%d can\'t should be positive!' % budget)
        size_x = blackbox.size_x()

      if problem_type in ("GT_DR_BY_DIM",):
        _shared.check_concept_int(dim, 'dim')
        if dim <= 0:
          raise ValueError('Required output dimensionality \'dim\'=%d should be greater than zero!' % dim)
      elif problem_type in ("GT_DR_BY_ERR",):
        _shared.check_concept_numeric(error, 'error')
        if error <= 0.0:
          raise ValueError('Required error level \'error\'=%f should be greater than zero!' % error)
      elif problem_type in ("GT_DR_FE", "GT_DR_FE_BB"):
        if dim is not None:
          _shared.check_concept_int(dim, 'dim')
          if dim < 0:
            raise ValueError('Required output dimensionality \'dim\'=%d can\'t be less than zero!' % dim)
          dim = _ctypes.c_size_t(dim)
        else:
          dim = _ctypes.c_size_t(_numpy.iinfo(_ctypes.c_size_t(-1)).max)

      metainfo = _shared.preprocess_metainfo(x_meta, None, size_x, 0, template=metainfo_template)
      metainfo.pop('Output Variables', None)
      metainfo['Training Options'] = initial_options

      self._backend.set_logger(local_logger)
      self._backend.set_watcher(self._watcher)

      if problem_type == "GT_DR_BY_DIM":
        trained_model = self._backend.build_dim(x, dim, comment)
      elif problem_type == "GT_DR_BY_ERR":
        trained_model = self._backend.build_err(x, error, comment)
      elif problem_type == "GT_DR_FE":
        trained_model = self._backend.build_fe(x, y, dim, comment)
      elif problem_type == "GT_DR_FE_BB":
        trained_model = self._backend.build_fe_bb(budget, blackbox, dim, comment)

      self._report_train_finished(trained_model, time_start, metainfo, local_logger)

    except Exception:
      exc_type, exc_val, exc_tb = sys.exc_info()
      if isinstance(exc_val, _ex.ExceptionWrapper):
        exc_val.set_prefix("GTDR failed, cause ")
      _shared.reraise(type(exc_val), exc_val, exc_tb)

    finally:
      # restore original logger (avoid set_logger to avoid excessive wrapping)
      self._logger = saved_logger
      self._backend.set_logger(self._logger)

      # restore original watcher (avoid set_watcher to avoid excessive wrapping)
      self._watcher = saved_watcher
      self._backend.set_watcher(self._watcher)

      # restore original options
      self.options.reset()
      self.options.set(saved_options)

    # Reset cached model properties to avoid segfault
    trained_model._Model__cache = {}
    metainfo[u'Issues'] = _shared.parse_building_issues(trained_model.build_log)
    # Save meta-information to annotations and return model
    return trained_model._Model__modify(comment=comment, annotations=annotations, metainfo=metainfo)

  def _report_train_finished(self, model, time_start, metainfo, logger=None):
    try:
      time_finish = datetime.now()
      metainfo["Training Time"] = {"Start": str(time_start),
                                   "Finish": str(time_finish),
                                   "Total": str(time_finish - time_start)}

      log_suffix = ["Training started at %s" % time_start,
                    "Training finished at %s" % time_finish,
                    "Total training time: %s" % (time_finish - time_start)]
      if logger:
        logger(_loggers.LogLevel.INFO, "\n" + "\n".join(log_suffix))

      if model:
        try:
          set_build_log = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p,
                                            _ctypes.POINTER(_ctypes.c_void_p))(('GTDRModelUnsafeSetLog', _shared._library))
          errdesc = _ctypes.c_void_p()

          full_log = logger.log_value if getattr(logger, 'log_value', '') else model.build_log
          set_build_log(model._Model__instance, full_log.encode('utf8'), _ctypes.byref(errdesc))
        except:
          pass

    except:
      pass
