#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
gtdf.Builder - Python DP-model builder interface
------------------------------------------------

.. currentmodule:: da.p7core.gtdf.builder

"""

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
  class SampleData(_ctypes.Structure):
    _pack_ = 8
    _fields_ = [("n", _ctypes.c_size_t),
                ("x", _ctypes.POINTER(_ctypes.c_double)),
                ("ldx", _ctypes.c_size_t),
                ("incx", _ctypes.c_size_t),
                ("f", _ctypes.POINTER(_ctypes.c_double)),
                ("ldf", _ctypes.c_size_t),
                ("incf", _ctypes.c_size_t),
                ("w", _ctypes.POINTER(_ctypes.c_double)),
                ("incw", _ctypes.c_size_t),
                ("tol", _ctypes.POINTER(_ctypes.c_double)),
                ("ldtol", _ctypes.c_size_t),
                ("inctol", _ctypes.c_size_t),]

    def __init__(self, x, f, tol, weights):
      super(_API.SampleData, self).__init__()

      assert x.ndim == 2 and f.ndim == 2 and x.shape[0] == f.shape[0]

      self.n = x.shape[0]
      self.x = x.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
      self.ldx = x.strides[0] // x.itemsize
      self.incx = x.strides[1] // x.itemsize
      self.f = f.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
      self.ldf = f.strides[0] // f.itemsize
      self.incf = f.strides[1] // f.itemsize

      if weights is not None and weights.size:
        assert weights.ndim == 1 and weights.shape[0] == self.n
        self.w = weights.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
        self.incw = weights.strides[0] // weights.itemsize

      if tol is not None and tol.size:
        assert tol.shape == f.shape
        self.tol = tol.ctypes.data_as(_ctypes.POINTER(_ctypes.c_double))
        self.ldtol = tol.strides[0] // tol.itemsize
        self.inctol = tol.strides[1] // tol.itemsize

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


    self.builder_create = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDFBuilderAPINew", self.__library))
    self.builder_options_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTDFBuilderAPIGetOptionsManager", self.__library))
    self.builder_license_manager = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.void_ptr_ptr)(("GTDFBuilderAPIGetLicenseManager", self.__library))

    self.builder_build_sample = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. model ptr, builder ptr
                                                  _ctypes.c_size_t, _ctypes.c_size_t, # dim. x, dim. f
                                                  _ctypes.c_size_t, _ctypes.POINTER(self.SampleData), # num. of datasets, datasets array
                                                  _ctypes.c_char_p, _ctypes.c_char_p, self.void_ptr_ptr)(("GTDFBuilderAPIBuildBySample", self.__library)) # comment, annotations, err. data

    self.builder_build_bb = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, # ret. model ptr, builder ptr
                                              _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.POINTER(self.SampleData), # dim. x, dim. f, high fidelity dataset
                                              self.c_double_ptr, _ctypes.c_size_t, self.c_double_ptr, _ctypes.c_size_t, # lower bounds ptr, lower bounds inc, upper bounds ptr, upper bounds inc,
                                              _ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, # gradients enabled, response callback, opaque
                                              _ctypes.c_char_p, _ctypes.c_char_p, self.void_ptr_ptr)(("GTDFBuilderAPIBuildByBlackbox", self.__library)) # comment, annotations, err. data

    self.builder_release = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(("GTDFBuilderAPIFree", self.__library))
    self.builder_logger_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDFBuilderAPISetLogger", self.__library))
    self.builder_watcher_callback = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p)(("GTDFBuilderAPISetWatcher", self.__library))

    self.set_model_options = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p,
                                                self.void_ptr_ptr)(("GTDFModelUnsafeSetOptions", self.__library))

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
        msg_prefix = "an exception is raised inside blackbox 'evaluate(x=numpy.array(%s))' method - " % str(x_mat.shape)
        data = self.blackbox._evaluate(x_mat[:, :self.size_x])
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
      raise Exception("Cannot initialize GT DF API.")

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
      raise model_error[0](model_error[1] or "Failed to create GTDF model.")

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

  def build_sample(self, size_x, size_f, datasets, comment):
    samples = (self.SampleData * len(datasets))()
    for i, sample in enumerate(datasets):
      samples[i] = self.SampleData(**sample)

    self._flush_callback_exception(False) # cleanup errors first

    try:
      error_description = _ctypes.c_void_p()
      model_handle = self.builder_build_sample(self.__instance, size_x, size_f, len(samples), samples,
                                               self._encode_message(comment), _ctypes.c_char_p(),
                                               _ctypes.byref(error_description))
      if not model_handle:
        self._flush_callback_exception(False, _shared._release_error_message(error_description))

      return _model.Model(handle=model_handle)
    finally:
      # clean up errors if any occurred
      self._flush_callback_exception(True)

  def build_bb(self, sample_hf, bb, comment):
    lb, ub = bb.variables_bounds()
    lb = _shared.py_vector_2c(lb, name="Blackbox variables lower bounds")
    ub = _shared.py_vector_2c(ub, name="Blackbox variables upper bounds")

    sample = self.SampleData(**sample_hf)

    self._flush_callback_exception(False) # cleanup errors first

    try:
      magic_sig = _ctypes.c_void_p(0xAACC00FF)
      evaluate_wrapper = self._ResponseCallbackWrapper(self, bb, magic_sig)
      evaluate_callback = self.builder_response_callback_type(evaluate_wrapper)

      error_description = _ctypes.c_void_p()
      model_handle = self.builder_build_bb(self.__instance, sample_hf["x"].shape[1], sample_hf["f"].shape[1], _ctypes.byref(sample),
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
  """Data fusion model builder."""

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

    General options interface for the builder. See section :ref:`gen_options` for usage and the :ref:`GTDF option reference <ug_gtapprox_options>`.

    """
    return _options.Options(self._backend.options_manager, self._backend)

  @property
  def license(self):
    """Builder license.

    :type: :class:`~da.p7core.License`

    General license information interface. See section :ref:`gen_license_usage` for details.

    """
    return _license.License(self._backend.license_manager, self._backend)

  def build(self, x_hf, f_hf, x_lf, f_lf, options=None, weights_hf=None, weights_lf=None, comment=None, annotations=None, x_meta=None, f_meta=None):
    """Train a sample-based data fusion model.

    :param x_hf: high fidelity training sample, input part (values of variables)
    :param f_hf: high fidelity training sample, response part (function values)
    :param x_lf: low fidelity training sample, input part (values of variables)
    :param f_lf: low fidelity training sample, response part (function values)
    :param options: option settings
    :param weights_hf: optional weights of the high fidelity training sample points
    :param weights_lf: optional weights of the low fidelity training sample points
    :param comment: text comment
    :param annotations: extended comment and notes
    :param x_meta: descriptions of inputs
    :param f_meta: descriptions of outputs
    :type x_hf: :term:`array-like`, 1D or 2D
    :type f_hf: :term:`array-like`, 1D or 2D
    :type x_lf: :term:`array-like`, 1D or 2D
    :type f_lf: :term:`array-like`, 1D or 2D
    :type options: ``dict``
    :type weights_hf: :term:`array-like`, 1D
    :type weights_lf: :term:`array-like`, 1D
    :type comment: ``str``
    :type annotations: ``dict``
    :type x_meta: ``list``
    :type f_meta: ``list``
    :return: trained model
    :rtype: :class:`~da.p7core.gtdf.Model`

    Train a data fusion model using :arg:`x_hf`, :arg:`f_hf` and :arg:`x_lf`, :arg:`f_lf` as the high and low fidelity training samples, respectively.
    1D samples are supported as a simplified form for the case of 1D input and/or response.

    .. versionadded:: 5.0
       sample point weighting support.

    .. versionchanged:: 6.25
       ``pandas.DataFrame`` and ``pandas.Series`` are supported as training samples.

    Some of the sample-based GTDF techniques support sample point weighting (:arg:`weights_hf`, :arg:`weights_lf`).
    Roughly, point weight is a relative confidence characteristic for this point
    which affects the model fit to the training sample.
    The model will try to fit the points with greater weights better,
    possibly at the cost of decreasing accuracy for the points with lesser weights.
    The points with zero weight may be completely ignored when fitting the model.

    Point weighting is supported in the following techniques:

    * Difference Approximation (DA).
    * High Fidelity Approximation (HFA). Note that HFA ignores :arg:`weights_lf` because it does not use the low fidelity sample.
    * Multiple Fidelity Gaussian Process (MFGP), both in :meth:`~da.p7core.gtdf.Builder.build()` and :meth:`~da.p7core.gtdf.Builder.build_MF()`.

    That is, to use point weights meaningfully,
    one of the techniques above has to be selected using :ref:`GTDF/Technique<GTDF/Technique>`.
    If any other technique is selected, either manually or automatically, all weights are ignored.

    Point weight is an arbitrary non-negative ``float`` value.
    This value has no specific meaning,
    it simply notes the relative "importance" of a point compared to other points in the training sample.

    The :arg:`weights_hf` and :arg:`weights_lf` arguments are independent, so it is possible to specify only one of them.
    If specified, it should be a 1D array of point weights,
    and its length has to be equal to the number of points in the respective training sample.

    .. note::

       At least one weight has to be non-zero.
       If :arg:`weights_hf` or :arg:`weights_lf` is specified but contains only zero values,
       :meth:`~da.p7core.gtdf.Builder.build()` raises an :exc:`~da.p7core.InvalidProblemError` exception.

    .. versionchanged:: 6.14
       added the :arg:`comment`, :arg:`annotations`, :arg:`x_meta`, and :arg:`f_meta` parameters.

    The :arg:`comment` and :arg:`annotations` parameters add optional notes to model.
    The :arg:`comment` string is stored to the model's :attr:`~da.p7core.gtdf.Model.comment`.
    The :arg:`annotations` dictionary can contain more notes or other supplementary information;
    all keys and values in :arg:`annotations` must be strings.
    Annotations are stored to the model's :attr:`~da.p7core.gtdf.Model.annotations`.
    After training a model, you can also edit its
    :attr:`~da.p7core.gtdf.Model.comment` and :attr:`~da.p7core.gtdf.Model.annotations`
    using :meth:`~da.p7core.gtdf.Model.modify()`.

    The :arg:`x_meta` and :arg:`f_meta` parameters add names and descriptions of model inputs and outputs.
    These parameters are lists of length equal to the number of inputs and outputs respectively,
    or the number of columns in the input and response parts of the training sample.
    List element can be a string (Unicode) or a dictionary.
    A string specifies a name for the respective input or output.
    It must be a valid identifier according to the FMI standard,
    so there are certain restrictions for names (see below).
    A dictionary describes a single input or output and can have the following keys
    (all keys are optional, all values must be ``str`` or ``unicode``):

    * ``"name"``:
      contains the name for this input or output.
      If this key is omitted, default names will be saved to the model:
      :samp:`"x[{i}]"` for inputs, :samp:`"f[{i}]"` for outputs,
      where :samp:`{i}` is the index of the respective column in the training samples.
    * ``"description"``:
      contains a brief description, any text.
    * ``"quantity"``:
      physical quantity, for example ``"Angle"`` or ``"Energy"``.
    * ``"unit"``:
      measurement units used for this input or output, for example ``"deg"`` or ``"J"``.

    Names of inputs and outputs must satisfy the following rules:

    * Name must not be empty.
    * All names must be unique. The same name for an input and an output is also prohibited.
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

    Input and output descriptions are stored to model :attr:`~da.p7core.gtdf.Model.details`
    (the ``"Input Variables"`` and ``"Output Variables"`` keys).
    If you do not specify a name or description for some input or output,
    its information in :attr:`~da.p7core.gtdf.Model.details` contains only the default name
    (:samp:`"x[{i}]"` for inputs, :samp:`"f[{i}]"` for outputs).

    """
    with _shared.sigint_watcher(self):
      return self._do_build(x_hf, f_hf, x_lf, f_lf, options, weights_hf, weights_lf, comment, annotations, x_meta, f_meta)

  def _do_build(self, x_hf, f_hf, x_lf, f_lf, options=None, weights_hf=None, weights_lf=None, comment=None, annotations=None, x_meta=None, f_meta=None):
    time_start = datetime.now()

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

      log_level = _loggers.LogLevel.from_string(self.options.get('GTDF/LogLevel').lower())
      local_logger = _shared.TeeLogger(self._logger, log_level)
      self.set_logger(local_logger)
      # now level is handled by the tee logger
      if local_logger.private_log_level != log_level:
        self.options.set('GTDF/LogLevel', str(local_logger.private_log_level))

      local_logger(_loggers.LogLevel.INFO, 'Training started at %s\n' % str(time_start))

      metainfo_template = _shared.create_metainfo_template(x_hf, f_hf)

      sample_hf = self._validate_dataset(x_hf, f_hf, None, weights_hf, 'training dataset with high fidelity level', local_logger)
      if not sample_hf["x"].size:
        raise ValueError('The high fidelity sample is empty!')
      samples = [sample_hf]
      size_x, size_f = sample_hf["x"].shape[1], sample_hf["f"].shape[1]

      if _shared.get_size(x_lf) != 0 or _shared.get_size(f_lf) != 0:
        sample_lf = self._validate_dataset(x_lf, f_lf, None, weights_lf, 'training dataset with low fidelity level', local_logger)
        if sample_lf["x"].size:
          if size_x != sample_lf["x"].shape[1] or size_f != sample_lf["f"].shape[1]:
            raise ValueError('Dimensionality of the high and low fidelity samples are different: (x=%d, f=%d) != (x=%d, f=%d)' \
                               % (size_x, size_f, sample_lf["x"].shape[1], sample_lf["f"].shape[1]))
          samples.insert(0, sample_lf)

      metainfo = _shared.preprocess_metainfo(x_meta, f_meta, size_x, size_f, template=metainfo_template)
      #metainfo['Training Options'] = initial_options # @todo - do we?

      self._backend.set_logger(local_logger)
      self._backend.set_watcher(self._watcher)

      trained_model = self._backend.build_sample(size_x, size_f, samples, comment)

      self._report_train_finished(trained_model, time_start, metainfo, local_logger)

    except Exception:
      exc_type, exc_val, exc_tb = sys.exc_info()
      if isinstance(exc_val, _ex.ExceptionWrapper):
        exc_val.set_prefix("GTDF failed, cause ")
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

    # Save meta-information to annotations and return model
    return self._postprocess_model(trained_model, comment=comment, annotations=annotations, metainfo=metainfo, initial_options=initial_options)

  def build_BB(self, x_hf, f_hf, blackbox, options=None, comment=None, annotations=None, x_meta=None, f_meta=None):
    """Train a blackbox-based data fusion model.

    :param x_hf: high fidelity training sample, input part (values of variables)
    :param f_hf: high fidelity training sample, response part (function values)
    :param blackbox: low fidelity blackbox
    :param options: option settings
    :param comment: text comment
    :param annotations: extended comment and notes
    :param x_meta: descriptions of inputs
    :param f_meta: descriptions of outputs
    :type x_hf: :term:`array-like`, 1D or 2D
    :type f_hf: :term:`array-like`, 1D or 2D
    :type blackbox: :class:`~da.p7core.blackbox.Blackbox`, :class:`.gtapprox.Model`, or :class:`.gtdf.Model`
    :type options: ``dict``
    :type comment: ``str``
    :type annotations: ``dict``
    :type x_meta: ``list``
    :type f_meta: ``list``
    :return: trained model
    :rtype: :class:`~da.p7core.gtdf.Model`

    Train a data fusion model using :arg:`x_hf`, :arg:`f_hf` as the high fidelity training sample and obtaining low-fidelity training points from the :arg:`blackbox`.
    1D samples are supported as a simplified form for the case of 1D input and/or response.

    .. versionchanged:: 6.14
       added the :arg:`comment`, :arg:`annotations`, :arg:`x_meta`, and :arg:`f_meta` parameters.

    .. versionchanged:: 6.20
       :arg:`blackbox` may be a :class:`.gtapprox.Model` or a :class:`.gtdf.Model`.

    .. versionchanged:: 6.25
       ``pandas.DataFrame`` and ``pandas.Series`` are supported as training samples.

    The :arg:`comment` and :arg:`annotations` parameters add optional notes to model.
    The :arg:`x_meta` and :arg:`f_meta` parameters add names and descriptions to model inputs and outputs.
    See full descriptions of these parameters in :meth:`~da.p7core.gtdf.Builder.build()`.

    """
    with _shared.sigint_watcher(self):
      return self._do_build_BB(x_hf, f_hf, blackbox, options, comment, annotations, x_meta, f_meta)

  def _do_build_BB(self, x_hf, f_hf, blackbox, options=None, comment=None, annotations=None, x_meta=None, f_meta=None):
    time_start = datetime.now()

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

      log_level = _loggers.LogLevel.from_string(self.options.get('GTDF/LogLevel').lower())
      local_logger = _shared.TeeLogger(self._logger, log_level)
      self.set_logger(local_logger)
      # now level is handled by the tee logger
      if local_logger.private_log_level != log_level:
        self.options.set('GTDF/LogLevel', str(local_logger.private_log_level))

      local_logger(_loggers.LogLevel.INFO, 'Training started at %s\n' % str(time_start))

      metainfo_template = _shared.create_metainfo_template(x_hf, f_hf)
      sample_hf = self._validate_dataset(x_hf, f_hf, None, None, 'training dataset with high fidelity level', local_logger)
      if not sample_hf["x"].size:
        raise ValueError('The high fidelity sample is empty!')

      original_bb = blackbox
      blackbox, _, warns, _ = _bbconverter.preprocess_blackbox(original_bb, "GTDF", None)
      if warns:
        local_logger(_loggers.LogLevel.WARN, warns)

      lb, ub = blackbox.variables_bounds()
      if len(lb) != blackbox.size_x() or len(ub) != blackbox.size_x():
        raise ValueError('Invalid blackbox generation bounds length: lower %d, upper %d, expected %d' % (len(lb), len(ub), blackbox.size_x()))

      size_x, size_f = sample_hf["x"].shape[1], sample_hf["f"].shape[1]

      if size_x != blackbox.size_x() or size_f != blackbox.size_f():
        raise ValueError('Dimensionality of the high fidelity sample and blackbox are different: (x=%d, f=%d) != (x=%d, f=%d)' \
                           % (size_x, size_f, blackbox.size_x(), blackbox.size_f()))

      metainfo = _shared.preprocess_metainfo(x_meta, f_meta, size_x, size_f, template=metainfo_template)
      # metainfo['Training Options'] = initial_options # @todo : do we need it?

      self._backend.set_logger(local_logger)
      self._backend.set_watcher(self._watcher)

      trained_model = self._backend.build_bb(sample_hf, blackbox, comment)

      self._report_train_finished(trained_model, time_start, metainfo, local_logger)

    except Exception:
      exc_type, exc_val, exc_tb = sys.exc_info()
      if isinstance(exc_val, _ex.ExceptionWrapper):
        exc_val.set_prefix("GTDF failed, cause ")
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

    # Save meta-information to annotations and return model
    return self._postprocess_model(trained_model, comment=comment, annotations=annotations, metainfo=metainfo, initial_options=initial_options)

  def build_MF(self, samples, options=None, comment=None, annotations=None, x_meta=None, f_meta=None):
    """Train a data fusion model using multiple training samples of different fidelity.

    :param samples: training samples, in order of increasing fidelity
    :param options: option settings
    :param comment: text comment
    :param annotations: extended comment and notes
    :param x_meta: descriptions of inputs
    :param f_meta: descriptions of outputs
    :type samples: ``list[dict]``
    :type options: ``dict``
    :type comment: ``str``
    :type annotations: ``dict``
    :type x_meta: ``list``
    :type f_meta: ``list``
    :return: trained model
    :rtype: :class:`~da.p7core.gtdf.Model`

    .. versionadded:: 4.0

    .. versionchanged:: 6.25
       ``pandas.DataFrame`` and ``pandas.Series`` are supported as training samples in :arg:`samples`.

    This is a dedicated method for the Multiple Fidelity Gaussian Processes (MFGP) technique.
    It allows using more than two samples of different fidelity to train the model;
    internally this technique is a version of the Variable Fidelity Gaussian Processes
    technique (VFGP) updated to support more than one low-fidelity data set.

    The :arg:`samples` argument is a list of training samples sorted in order of increasing fidelity,
    so the sample with maximum fidelity is the last. Each element is a dictionary with the following keys:

    * ``"x"`` --- the input part of the training sample (values of variables).
    * ``"f"`` --- the response part of the training sample (function values).
    * ``"tol"`` --- response noise variance.
      Optional: the key may be omitted, or its value may be an explicit ``None``.
      Incompatible with sample point weights.
    * ``"weights"`` --- sample point weights.
      Optional: may be omitted or set to ``None``.
      Incompatible with response noise variance.

    For example::

      s_low = {"x": x_low, "f": f_low, "tol": None}
      s_higher = {"x": x_higher, "f": f_higher, "weights": pt_weights}
      s_highest = {"x": x_highest, "f": f_highest, "tol": f_var}
      samples = [s_low, s_higher, s_highest]

    All dictionary values are :term:`array-like`.
    Arrays in ``"x"``, ``"f"``, ``"tol"`` can be 1D or 2D,
    with 1D samples supported as a simplified form for the case of 1D input and/or response.
    The array in ``"weights"`` is always 1D.

    If information on the noise level in the response sample (key ``"f"``) is available,
    it can be added to the sample dictionary under the ``"tol"`` key.
    The ``"tol"`` array should specify a noise variance value for each element of the ``"f"`` array
    (that is, for each response component of every single point).
    Thus the ``"tol"`` and ``"f"`` arrays are of the same shape.
    If noise variance data is not available for some points or output components, corresponding values
    in ``"tol"`` should be replaced with NaN.

    .. note::

       The response noise variance in :meth:`~da.p7core.gtdf.Builder.build_MF()` is similar
       to the :arg:`outputNoiseVariance` argument in :meth:`da.p7core.gtapprox.Builder.build()`.

    .. versionadded:: 5.0
       sample point weighting support.

    MFGP supports sample point weighting.
    Roughly, point weight is a relative confidence characteristic for this point
    which affects the model fit to the training sample.
    The model will try to fit the points with greater weights better,
    possibly at the cost of decreasing accuracy for the points with lesser weights.
    The points with zero weight may be completely ignored when fitting the model.

    Point weight is an arbitrary non-negative ``float`` value.
    This value has no specific meaning,
    it simply notes the relative "importance" of a point compared to other points in the training sample.

    If weights for a sample are available,
    they can be added to this sample dictionary under the ``"weights"`` key.
    The value should be a 1D array of point weights,
    and its length has to be equal to the number of points in this sample.

    .. note::

       At least one weight has to be non-zero.
       If there is a sample with all weights set to zero,
       :meth:`~da.p7core.gtdf.Builder.build_MF()` raises an :exc:`~da.p7core.InvalidProblemError` exception.

    .. note::

       Point weighting is not compatible with output noise variance.
       If there is a sample with both ``"tol"`` and ``"weights"`` specified,
       :meth:`~da.p7core.gtdf.Builder.build_MF()` raises an :exc:`~da.p7core.InvalidProblemError` exception.

    .. versionchanged:: 6.14
       added the :arg:`comment`, :arg:`annotations`, :arg:`x_meta`, and :arg:`f_meta` parameters.

    The :arg:`comment` and :arg:`annotations` parameters add optional notes to model.
    The :arg:`x_meta` and :arg:`f_meta` parameters add names and descriptions to model inputs and outputs.
    See full descriptions of these parameters in :meth:`~da.p7core.gtdf.Builder.build()`.

    """
    with _shared.sigint_watcher(self):
      return self._do_build_MF(samples, options, comment, annotations, x_meta, f_meta)

  def _do_build_MF(self, samples, options=None, comment=None, annotations=None, x_meta=None, f_meta=None):
    time_start = datetime.now()
    samples = [dict(_) for _ in samples] # get a shallow copy of samples

    if not samples:
      raise ValueError('No training sample given')

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

      log_level = _loggers.LogLevel.from_string(self.options.get('GTDF/LogLevel').lower())
      local_logger = _shared.TeeLogger(self._logger, log_level)
      self.set_logger(local_logger)
      # now level is handled by the tee logger
      if local_logger.private_log_level != log_level:
        self.options.set('GTDF/LogLevel', str(local_logger.private_log_level))

      local_logger(_loggers.LogLevel.INFO, 'Training started at %s\n' % str(time_start))

      # convert samples to numpy arrays and validate conformance of the x/f samples size
      for i, sample in enumerate(tuple(_ for _ in samples)):
        metainfo_template = _shared.create_metainfo_template(sample.get('x'), sample.get('f'))
        samples[i] = self._validate_dataset(sample.get('x'), sample.get('f'), sample.get('tol'), sample.get('weights'), \
                                              ('training dataset with fidelity level %d' % i), local_logger)


      if not samples[-1]['x'].shape[0]:
        raise ValueError('No high fidelity training sample given')

      if not sum(sample['x'].shape[0] for sample in samples[:-1]):
        raise ValueError('No low fidelity training sample given')

      # get input and output dimensionality from the first sample
      size_x = samples[0]['x'].shape[1]
      size_f = samples[0]['f'].shape[1]

      # check that all x/f samples have the same vector dimensionality
      for i, sample in enumerate(samples):
        if sample['x'].shape[1] != size_x:
          raise ValueError('Dimensionality of the fidelity levels 0 and %d input samples do not match: %d != %d' % (i, sample['x'].shape[1], size_x))
        if sample['f'].shape[1] != size_f:
          raise ValueError('Dimensionality of the fidelity levels 0 and %d output samples do not match: %d != %d' % (i, sample['f'].shape[1], size_f))

      metainfo = _shared.preprocess_metainfo(x_meta, f_meta, size_x, size_f, template=metainfo_template)
      #metainfo['Training Options'] = initial_options # @todo - do we?

      self._backend.set_logger(local_logger)
      self._backend.set_watcher(self._watcher)

      trained_model = self._backend.build_sample(size_x, size_f, samples, comment)

      self._report_train_finished(trained_model, time_start, metainfo, local_logger)

    except Exception:
      exc_type, exc_val, exc_tb = sys.exc_info()
      if isinstance(exc_val, _ex.ExceptionWrapper):
        exc_val.set_prefix("GTDF failed, cause ")
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

    # Save meta-information to annotations and return model
    return self._postprocess_model(trained_model, comment=comment, annotations=annotations, metainfo=metainfo, initial_options=initial_options)

  @staticmethod
  def _postprocess_model(model, comment=None, annotations=None, metainfo=None, initial_options=None):
    if not model:
      return model

    errdesc = _ctypes.c_void_p()

    known_issues = _shared.parse_building_issues(model.build_log)

    if initial_options is not None:
      initial_options = dict(((k, initial_options[k]) for k in initial_options if not k.startswith('//')))
      _api.set_model_options(model._Model__instance, _shared.write_json(initial_options).encode('ascii'), _api.void_ptr_ptr())

    if annotations is None and model.annotations:
      annotations = {} # non-None is required to cleanup temporary anotations

    if comment is None and model.comment:
      comment = "" # non-None is required to cleanup temporary comment

    # Reset cached model properties to avoid segfault
    model._Model__cache = {}

    # Do not forget to save variability info if there is any
    if metainfo is not None:
      details = model._Model__read_details()
      for variables_direction in metainfo:
        if details.get(variables_direction):
          for var_meta, var_details in zip(metainfo[variables_direction], details[variables_direction]):
            var_meta.update(var_details)
      metainfo['Issues'] = known_issues
    elif known_issues:
      metainfo = {'Issues': known_issues}

    return model._Model__modify(comment=comment if comment is not None else "", annotations=annotations, metainfo=metainfo)

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
                                            _ctypes.POINTER(_ctypes.c_void_p))(('GTDFModelUnsafeSetLog', _shared._library))
          errdesc = _ctypes.c_void_p()

          full_log = logger.log_value if getattr(logger, 'log_value', '') else model.build_log
          set_build_log(model._Model__instance, full_log.encode('utf8'), _ctypes.byref(errdesc))
        except:
          pass

    except:
      pass

  def _validate_dataset(self, x, f, tol, weights, title, logger=None):
    def _wrappedConvertToMatrix(data, title, vectorSize=None):
      try:
        return _shared.as_matrix(data, shape=(None, vectorSize), name=title)
      except ValueError:
        e, tb = sys.exc_info()[1:]
        _shared.reraise(ValueError, ('Failed to read %s: %s' % (title, str(e))), tb)

    x = _wrappedConvertToMatrix(x, 'input part of %s' % title)
    f = _wrappedConvertToMatrix(f, 'output part of %s' % title)

    if x.shape[0] != f.shape[0]:
      raise ValueError('Size of the input (\'x\') and output (\'f\') samples of %s do not match: %d != %d' % (title, x.shape[0], f.shape[0]))

    if x.shape[1] <= 0:
      raise ValueError('The input (\'x\') sample of %s is zero-dimensional!' % title)
    if f.shape[1] <= 0:
      raise ValueError('The output (\'f\') sample of %s is zero-dimensional!' % title)

    if tol is not None:
      tol = _wrappedConvertToMatrix(tol, 'output noise variance of %s' % title)
      if 0 == tol.size:
        tol = None
      elif f.shape != tol.shape:
        raise ValueError('Dimensionality of the output (\'f\') and output noise variance (\'tol\') samples of %s do not match: %s != %s' % (title, f.shape, tol.shape))

    if weights is not None:
      weights = _wrappedConvertToMatrix(weights, 'points weights of %s' % title, vectorSize=1)
      if 0 == weights.size:
        weights = None
      elif f.shape[0] != weights.shape[0]:
        raise ValueError('The number of points weights does not match the length of the output (\'f\') sample of %s: %s != %s' % (title, len(f), len(weights.shape)))
      weights = weights.reshape(-1)
    else:
      weights = None

    nan_inputs = _numpy.isfinite(x, casting='unsafe').all(axis=1)
    _numpy.logical_not(nan_inputs, out=nan_inputs)
    if nan_inputs.any():
      if 'ignore' == str(self.options.get('GTDF/InputNanMode')).lower():
        valid_points = ~nan_inputs
        x = x[valid_points]
        f = f[valid_points]
        if tol is not None:
          tol = tol[valid_points]
        if weights is not None:
          weights = weights[valid_points]
        if logger:
          n_nan, n_valid = nan_inputs.sum(), valid_points.sum()
          logger(_loggers.LogLevel.WARN, '%d out of %d input points of %s are ignored according to \'GTDF/InputNanMode\'=\'ignore\' option value.' % (n_nan, (n_nan + n_valid), title))
      else:
        raise _ex.NanInfError('The input (\'x\') sample of %s contains at least one NaN or Inf value!' % title)

    if _shared.isNanInf(f):
      raise _ex.NanInfError('The output (\'f\') sample of %s contains NaN or Inf value!' % title)

    return {"x": x, "f": f, "tol": tol, "weights": weights}
