#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
.. currentmodule: da.p7core.parameters

A parameter is a pair (name, value).
"""
import ctypes

from . import six as _six
from . import shared as _shared
from . import exceptions as _exceptions
import numpy as _numpy

_PGETVALUE =     ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p,
                                  ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
                                  ctypes.c_size_t, ctypes.POINTER(ctypes.c_double))
_PGETVALUEINFO = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p,
                                  ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t))
_PGETNAMES =     ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p,
                                  ctypes.POINTER(ctypes.c_size_t), ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t))

class Parameters(object):
  """General parameters interface.
  """

  def __init__(self, obj, parent_impl):
    _shared.check_type(obj, 'constructor argument', ctypes.c_void_p)
    self.__impl = obj
    self.__parent = parent_impl
    self.__cached_list = None
    self.__cached_values = {}

    self.__functionGetParameter = _PGETVALUE(('GTParametersManagerGetParameter', _shared._library))
    self.__functionGetParameterInfo = _PGETVALUEINFO(('GTParametersManagerGetParameterInfo', _shared._library))
    self.__functionGetParametersNames = _PGETNAMES(('GTParametersManagerGetParametersNames', _shared._library))


  def __checkError(self, err):
    if err == 0:
      raise _exceptions.WrongUsageError('parameters operation failed')

  def get(self, name=None):
    """Get parameter(s) value(s).

    :param name: parameter name
    :type name: ``str``
    :return: parameters
    :rtype: :term:`array-like` for single parameter, ``dict`` for all parameters

    Returns the value of the parameter *name*. If *name* is ``None``, returns a dictionary ``{name: value}``. Use :attr:`~da.p7core.Parameters.list` to discover parameter names.

    """
    if name is None:
      return dict((opt, self.get(opt)) for opt in self.list)

    _shared.check_type(name, 'parameter', _six.string_types)

    if name not in self.__cached_values:
      cdim1 = ctypes.c_size_t(0)
      cdim2 = ctypes.c_size_t(0)
      cname = ctypes.c_char_p(name.encode("utf8"))

      self.__checkError(self.__functionGetParameter(self.__impl, cname, ctypes.byref(cdim1), ctypes.byref(cdim2), ctypes.c_size_t(0), ctypes.POINTER(ctypes.c_double)()))
      if cdim1.value * cdim2.value == 0:
        self.__cached_values[name] = None
      else:
        result = _numpy.ndarray((cdim1.value, cdim2.value,), dtype=ctypes.c_double, order='C')
        self.__checkError(self.__functionGetParameter(self.__impl, cname, ctypes.byref(cdim1), ctypes.byref(cdim2),
                           result.strides[0]//result.itemsize, result.ctypes.data_as(ctypes.POINTER(ctypes.c_double))))
        result.flags['WRITEABLE']=False
        self.__cached_values[name] = result

    return self.__cached_values[name]

  def info(self, name=None):
    """Get parameter(s) info.

    :param name: parameter name
    :type name: ``str``
    :return: descriptions dictionary
    :rtype: ``dict``

    Returns a dictionary containing descriptions for parameter *name*. If *name* is ``None``, returns a dictionary for all parameters. Use :attr:`~da.p7core.Parameters.list` to discover parameter names.
    """
    def parameter_info(name):
      cname = ctypes.c_char_p(name.encode("utf8"))
      csize = ctypes.c_size_t(0)
      self.__checkError(self.__functionGetParameterInfo(self.__impl, cname, ctypes.c_char_p(), ctypes.byref(csize)))
      cvalue = (ctypes.c_char * csize.value)()
      self.__checkError(self.__functionGetParameterInfo(self.__impl, cname, ctypes.cast(cvalue, ctypes.c_char_p), ctypes.byref(csize)))
      return _shared.parse_json(_shared._preprocess_json(cvalue.value))

    if name:
      _shared.check_type(name, 'parameter', _six.string_types)
      return parameter_info(name)

    result = {}
    for parameter in self.list:
      result[parameter] = parameter_info(parameter)
    return result

  @property
  def list(self):
    """List of parameter names.

    :Type: ``list[str]``

    """
    if self.__cached_list is None:
      csize = ctypes.c_size_t(0)
      ccount = ctypes.c_size_t(0)
      self.__checkError(self.__functionGetParametersNames(self.__impl, ctypes.byref(ccount), ctypes.c_char_p(), ctypes.byref(csize)))
      cnames = ctypes.create_string_buffer(csize.value)
      self.__checkError(self.__functionGetParametersNames(self.__impl, ctypes.byref(ccount), cnames, ctypes.byref(csize)))
      self.__cached_list = [_shared.char2str(_) for _ in cnames.raw.split(_six.b('\0')) if _]
    return self.__cached_list

  @property
  def is_empty(self):
    ccount = ctypes.c_size_t(0)
    csize_p = ctypes.POINTER(ctypes.c_size_t)()
    self.__checkError(self.__functionGetParametersNames(self.__impl, ctypes.byref(ccount), ctypes.c_char_p(), csize_p))
    return ccount.value == 0

  def __str__(self):
    if _shared.get_size(self.list) > 0:
      tab = max(len('%s' % par) for par in self.list)
    else:
      tab = 1
    return '\n'.join('%%-%ds: %%s' % tab % (par, self.get(par)) for par in self.list)
