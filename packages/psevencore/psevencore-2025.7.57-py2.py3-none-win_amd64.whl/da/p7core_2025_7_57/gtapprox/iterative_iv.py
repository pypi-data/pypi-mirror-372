#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""GTApprox iterative interface for IV."""
from __future__ import division

import ctypes as _ctypes
import numpy as _np

from .. import shared as _shared
from .. import options as _options
from .. import exceptions as _ex
from .. import loggers as _loggers

class _API(object):
  class _WrappedLogger(object):
    def __init__(self, logger, level=_loggers.LogLevel.INFO):
      self.__logger = logger
      self.__level = level

    def __call__(self, message):
      try:
        if self.__logger is not None:
          self.__logger(self.__level, _shared._preprocess_utf8(message))
      except:
        pass

  def __init__(self):
    self.__library = _shared._library

    self.c_void_p_ptr = _ctypes.POINTER(_ctypes.c_void_p)

    self.logger_callback_t = _ctypes.CFUNCTYPE(None, _ctypes.c_char_p)

    self.create_driver = _ctypes.CFUNCTYPE(_ctypes.c_void_p)(('GTApproxIterativeCrossValidationCreate', self.__library))
    self.delete_driver = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTApproxIterativeCrossValidationDestroy', self.__library))
    self.save_iv = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p, self.c_void_p_ptr)(('GTApproxIterativeCrossValidationLoggedSave', self.__library))
    self.drop_iv = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_ptr)(('GTApproxIterativeCrossValidationDrop', self.__library))
    self.get_options = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_ptr, self.c_void_p_ptr)(('GTApproxIterativeCrossValidationGetOptionsManager', self.__library))
    self.set_sample = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_void_p, _ctypes.c_size_t, self.c_void_p_ptr)(('GTApproxIterativeCrossValidationAddSample', self.__library))
    self.get_sample = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_size_t), _ctypes.POINTER(_ctypes.c_size_t), self.c_void_p_ptr, _ctypes.POINTER(_ctypes.c_size_t), self.c_void_p_ptr)(('GTApproxIterativeCrossValidationGetSample', self.__library))
    self.session_begin = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_short), self.c_void_p_ptr)(('GTApproxIterativeCrossValidationTrainingSessionStart', self.__library))
    self.session_end = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, self.c_void_p_ptr)(('GTApproxIterativeCrossValidationTrainingSessionFinish', self.__library))

_api = _API()

class _IterativeIV(object):
  """
  Iterative IV interface.

  Proposed usage scenario is:

  from da.p7core.gtapprox.iterative_iv import _IterativeIV as _IterativeIV

  builder = gtapprox.Builder()

  ... setup builder log and options here - this code is omitted for simplicity ...

  approximator = builder.build(x, y) # build main approximation

  iv = _IterativeIV(x, y, options=builder.options) # create IV iterator driver

  while iv.session_begin():
    ...  backup builder options here - this code is omitted for simplicity ...
    builder.options.set(iv.options)
    iv.session_end(builder.build(iv.x, iv.y, outputNoiseVariance=iv.outputNoiseVariance, weights=iv.weights))

  # safe IV results to approximator
  iv.save_iv(approximator)
  """

  SAMPLE_INPUT = 1
  SAMPLE_TENSORED_INPUT = 2
  SAMPLE_OUTPUT = 3
  SAMPLE_WEIGHTS = 4
  SAMPLE_OUTPUT_NOISE = 5

  def __init__(self, x, y, options=None, outputNoiseVariance=None, weights=None, tensored=False):
    self.__backend = _api
    self.__driver = self.__backend.create_driver()
    if not self.__driver:
      raise _ex.InternalError('Failed to create iterative IV driver')

    self.__x = _shared.as_matrix(x, name="Input part of the train dataset ('x' argument)")
    self.__y = _shared.as_matrix(y, name="Output part of the train dataset ('y' argument)")

    self._checked_call(self.__backend.set_sample, *self._ndarray_args(_IterativeIV.SAMPLE_TENSORED_INPUT if tensored else _IterativeIV.SAMPLE_INPUT, self.__x))
    self._checked_call(self.__backend.set_sample, *self._ndarray_args(_IterativeIV.SAMPLE_OUTPUT, self.__y))

    if outputNoiseVariance is not None:
      self.__outputNoiseVariance = _shared.as_matrix(outputNoiseVariance, name="Output noise variance of the train dataset ('outputNoiseVariance' argument)")
      self._checked_call(self.__backend.set_sample, *self._ndarray_args(_IterativeIV.SAMPLE_OUTPUT_NOISE, self.__outputNoiseVariance))
    else:
      self.__outputNoiseVariance = None

    if weights is not None:
      self.__weights, single_vector = _shared.as_matrix(weights, ret_is_vector=True, name="Weight of the train dataset points ('weights' argument)")
      if single_vector:
        self.__weights = self.__weights.reshape((weights.size, 1))
      self._checked_call(self.__backend.set_sample, *self._ndarray_args(_IterativeIV.SAMPLE_WEIGHTS, self.__weights))
    else:
      self.__weights = None

    if options is not None:
      self.options.set(options)

  def __del__(self):
    self.__backend.delete_driver(self.__driver)

  def _ndarray_args(self, code, matrix):
    return code, matrix.ctypes.shape[0], matrix.ctypes.shape[1], matrix.ctypes.data_as(_ctypes.c_void_p), \
          matrix.ctypes.strides[0] // matrix.itemsize

  def _read_matrix(self, code):
    m = _ctypes.c_size_t()
    n = _ctypes.c_size_t()
    ld = _ctypes.c_size_t()
    data = _ctypes.c_void_p()
    self._checked_call(self.__backend.get_sample, code, _ctypes.byref(m), _ctypes.byref(n), _ctypes.byref(data), _ctypes.byref(ld))
    if 0 == m.value or 0 == n.value:
      return None

    data = (_ctypes.c_double*(m.value*ld.value)).from_address(data.value)
    result = _np.frombuffer(data).reshape((m.value, ld.value))
    return result[:, 0:n.value]

  def _checked_call(self, function, *args):
    errdesc = _ctypes.c_void_p()
    args = (self.__driver, ) + args + (_ctypes.byref(errdesc),)
    result = function(*args)
    if not result:
      _shared.ModelStatus.checkErrorCode(result, 'Iterative IV error', errdesc)
    return True

  def session_begin(self):
    """ Start training session. Returns True if session has been started or False if no more training sessions is needed. """
    session_started = _ctypes.c_short(0)
    self._checked_call(self.__backend.session_begin, _ctypes.byref(session_started))
    return bool(session_started.value)

  def session_end(self, approximator):
    """ Finished current training session """
    self._checked_call(self.__backend.session_end, approximator._Model__instance if approximator is not None else self.__backend.c_void_p_ptr())

  @property
  def options(self):
    """
    Options manager. Use it to setup IV before first training session starts.
    After this read recommended additional options for training.
    """
    options_manager = _ctypes.c_void_p()
    self._checked_call(self.__backend.get_options, _ctypes.byref(options_manager))
    return _options.Options(options_manager, self.__driver)

  @property
  def x(self):
    """ Input sample for the current training session. The matrix returned is valid during current training session only """
    return self._read_matrix(_IterativeIV.SAMPLE_INPUT)

  @property
  def y(self):
    """ Output sample for the current training session. The matrix returned is valid during current training session only """
    return self._read_matrix(_IterativeIV.SAMPLE_OUTPUT)

  @property
  def outputNoiseVariance(self):
    """
    Output noise variance matrix for the current training session or None if no output noise variance available.
    The matrix returned is valid during current training session only.
    """
    return self._read_matrix(_IterativeIV.SAMPLE_WEIGHTS)

  @property
  def weights(self):
    """
    Points weights vector for the current training session or None if no weights available.
    The vector returned is valid during current training session only.
    """
    return self._read_matrix(_IterativeIV.SAMPLE_OUTPUT_NOISE)

  def save_iv(self, approximator, logger=None):
    """ Updates IV information for the approximator given """
    if approximator is not None:
      if logger is not None:
        wrapped_logger = self.__backend._WrappedLogger(logger)
        logger_ptr = self.__backend.logger_callback_t(wrapped_logger)
      else:
        wrapped_logger = None
        logger_ptr = self.__backend.logger_callback_t()

      self._checked_call(self.__backend.save_iv, approximator._Model__instance, logger_ptr)
      approximator._Model__ivData = None
    else:
      self._checked_call(self.__backend.drop_iv)
