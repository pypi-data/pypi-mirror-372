#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
.. currentmodule: da.p7core.options

An option is a pair (name, value). Every option have default value.
"""
import sys as _sys
import ctypes as _ctypes
import numpy as _numpy

from . import six as _six

from . import shared as _shared
from . import exceptions as _exceptions

class _API(object):
  def __init__(self):
    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)

    PGETVALUEINFO = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_char_p, self.c_size_ptr)

    self.GTOptionsManagerGetOption = PGETVALUEINFO(('GTOptionsManagerGetOption', _shared._library))
    self.GTOptionsManagerGetValidatedOption = PGETVALUEINFO(('GTOptionsManagerGetValidatedOption', _shared._library))
    self.GTOptionsManagerSetOption = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_char_p)(('GTOptionsManagerSetOptionJSON', _shared._library))
    self.GTOptionsManagerGetOptionInfo = PGETVALUEINFO(('GTOptionsManagerGetOptionInfo', _shared._library))
    self.GTOptionsManagerGetOptionsNames = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_size_ptr, _ctypes.c_char_p,
                                                             self.c_size_ptr)(('GTOptionsManagerGetOptionsNames', _shared._library))
    self.GTOptionsManagerGetOptionsValues = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_ptr)(('GTOptionsManagerGetOptionsValues', _shared._library))
    self.GTOptionsManagerRearrangeComponentwiseOptionsValues = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_size_ptr, _ctypes.c_char_p, \
                                                                           self.c_size_ptr)(('GTOptionsManagerRearrangeComponentwiseOptionsValues', _shared._library))
    self.GTOptionsManagerResetOptions = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTOptionsManagerResetOptions', _shared._library))
    self.GTOptionsManagerGetLastErrorStatus = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_int))(('GTOptionsManagerGetLastErrorStatus', _shared._library))
    self.GTOptionsManagerGetLastError = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, \
                                                          self.c_size_ptr)(('GTOptionsManagerGetLastError', _shared._library))

    self.GTOptionsManagerNew = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_char_p)(('GTOptionsManagerNew', _shared._library))
    self.GTOptionsManagerFree = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTOptionsManagerFree', _shared._library))

_api = _API()

class _OptionManager(object):
  def __init__(self, prefix):
    #NOTE prefix is partially case sensitive. Option set work for any case. Option get requires proper case.
    _shared.check_type(prefix, 'OptionManager c-tor', _six.string_types)
    self.__api = _api
    self.__impl = _ctypes.c_void_p(self.__api.GTOptionsManagerNew(prefix.encode("ascii")))

  @property
  def pointer(self):
    return self.__impl

  def __del__(self):
    if hasattr(self, '_OptionManager__impl') and self.__impl.value is not None:
      self.__api.GTOptionsManagerFree(self.__impl)



class Options(object):
  """General options interface.

  This class only provides option handling methods to other classes
  and should never be instantiated by user.
  """
  def __init__(self, obj, parent_impl):
    _shared.check_type(obj, 'constructor argument', _ctypes.c_void_p)
    self.__impl = obj
    self.__parent = parent_impl
    self.__api = _api

  def _checkError(self, err):
    if err == 0:
      (GT_OPTIONS_MANAGER_STATUS_OK, GT_OPTIONS_MANAGER_STATUS_UNKNOWN_OPTION, GT_OPTIONS_MANAGER_STATUS_INVALID_VALUE,
       GT_OPTIONS_MANAGER_STATUS_WRONG_USAGE, GT_OPTIONS_MANAGER_STATUS_INTERNAL_ERROR) = range(5)

      ret, msg = self.__last_error()
      if ret == 0 or len(msg) == 0:
        msg = 'unable to get last error'
      ret, status = self.__last_error_status()
      if ret != 0:
        if status == GT_OPTIONS_MANAGER_STATUS_UNKNOWN_OPTION:
          raise _exceptions.InvalidOptionNameError(msg)
        if status == GT_OPTIONS_MANAGER_STATUS_INVALID_VALUE:
          raise _exceptions.InvalidOptionValueError(msg)
      raise _exceptions.InvalidOptionsError('options operation failed: ' + msg)

  def set(self, option, value=None):
    """Set option values.

    :param option: option name, or a dictionary of option names and values
    :type option: ``str`` or ``dict``
    :param value: new option value (for a single option)
    :type value: ``str`` or ``None``

    If :arg:`option` type is ``str``, set it to :arg:`value`. If :arg:`value` is omitted or ``None``, the option is reset to its default.

    If :arg:`option` type is ``dict``, set option values by dictionary. The :arg:`value` parameter is ignored,
    and specifying ``None`` as :arg:`value` does not reset the options from dictionary.
    To reset an option using the dictionary form, specify ``None`` as the dictionary value --- see the example.

    Example:

    >>> from da.p7core import gtdr
    >>> builder = gtdr.Builder()
    >>> # The following two lines...
    >>> builder.options.set('GTDR/Normalize', "on")  # normalize input
    >>> builder.options.set('GTDR/Technique')        # use default technique
    >>> # ...are equivalent to this one:
    >>> builder.options.set({'GTDR/Normalize': True, 'GTDR/Technique': None})

    .. note::

       This method does not validate option values (only some type checks are done).
       Options are checked when you call the main processing method,
       for example :meth:`da.p7core.gtapprox.Builder.build()` or :meth:`da.p7core.gtopt.Solver.solve()`.
       If an invalid option value was specified using :meth:`~da.p7core.Options.set()`,
       these methods throw an :exc:`~da.p7core.InvalidOptionsError` exception.
       Check option descriptions for their valid values.

    """
    def set_option(name, value):
      try:
        cname = _ctypes.c_char_p(name.encode("utf8") if isinstance(name, _six.string_types) else name)
      except:
        _shared.reraise(_exceptions.InvalidOptionNameError, ("Invalid option name is given: %s" % name), _sys.exc_info()[2])

      cvalue = _ctypes.c_char_p(_shared.write_json(value, fmt_double='%.17g').encode("ascii")) if value is not None else None
      self._checkError(self.__api.GTOptionsManagerSetOption(self.__impl, cname, cvalue))

    if isinstance(option, type(self)):
      option = option.values

    if _shared.is_mapping(option):
      for key in option:
        set_option(key, option[key])
    else:
      set_option(option, value)

  def get(self, name=None):
    """Get current value of an option or all options.

    :param name: option name
    :type name: str
    :return: current option value
    :rtype: str or dict

    Get the current value of an option as a string.

    If *name* is ``None``, get all current option values as a dictionary
    where keys are option names; all keys and values are strings.

    If an option was not :meth:`~da.p7core.Options.set()`, returns its default value.
    """
    if name is None:
      return dict((opt, self.get(opt)) for opt in self.list)
    try:
      cname = _ctypes.c_char_p(name.encode("utf8") if isinstance(name, _six.string_types) else name)
    except:
      _shared.reraise(_exceptions.InvalidOptionNameError, ("Invalid option name is given: %s" % name), _sys.exc_info()[2])
    csize = _ctypes.c_size_t(0)
    self.__api.GTOptionsManagerGetOption(self.__impl, cname, _ctypes.c_char_p(), _ctypes.byref(csize))
    cvalue = (_ctypes.c_char * csize.value)()
    self._checkError(self.__api.GTOptionsManagerGetOption(self.__impl, cname, _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize)))
    return _shared._preprocess_utf8(cvalue.value)

  def _get(self, name=None):
    """Get validated value of the option `name` (all options if `name` is ``None``).

    If an option was not explicitly set, default option value is returned.

    :param name: option name
    :type name: ``str``
    :return: dictionary containing option(s) value
    :rtype: ``str`` for single option, ``dict`` for all options

    """
    if name is None:
      return dict((opt, self._get(opt)) for opt in self.list)
    try:
      cname = _ctypes.c_char_p(name.encode("utf8") if isinstance(name, _six.string_types) else name)
    except:
      _shared.reraise(_exceptions.InvalidOptionNameError, ("Invalid option name is given: %s" % name), _sys.exc_info()[2])
    csize = _ctypes.c_size_t(0)
    self.__api.GTOptionsManagerGetValidatedOption(self.__impl, cname, _ctypes.c_char_p(), _ctypes.byref(csize))
    cvalue = (_ctypes.c_char * csize.value)()
    self._checkError(self.__api.GTOptionsManagerGetValidatedOption(self.__impl, cname, _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize)))
    return _shared._preprocess_utf8(cvalue.value)

  def info(self, name=None):
    """Get option information.

    :param name: option name
    :type name: str
    :return: option summary
    :rtype: dict

    Get a dictionary containing option default, short description, type and allowed values.
    Example::

      >>> builder.options.info('GTApprox/InternalValidation')
      {'OptionDescription': {'Default': 'False',
                             'Description': 'Enable or disable internal validation.',
                             'Name': 'GTApprox/InternalValidation',
                             'Type': 'bool',
                             'Values': ['False', 'True']}}

    If *name* is ``None``, get information on all available options as a dictionary
    where keys are option names (strings) and values are option summaries (dictionaries).
    """
    def option_info(name):
      cname = _ctypes.c_char_p(name)
      csize = _ctypes.c_size_t(0)
      self.__api.GTOptionsManagerGetOptionInfo(self.__impl, cname, _ctypes.c_char_p(), _ctypes.byref(csize))
      cvalue = (_ctypes.c_char * csize.value)()
      self._checkError(self.__api.GTOptionsManagerGetOptionInfo(self.__impl, cname, _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize)))
      return _shared.parse_json(cvalue.value)

    if name is not None:
      try:
        cname = _ctypes.c_char_p(name.encode("utf8") if isinstance(name, _six.string_types) else name)
      except:
        _shared.reraise(_exceptions.InvalidOptionNameError, ("Invalid option name is given: %s" % name), _sys.exc_info()[2])
      return option_info(cname.value)
    return dict([(option_name, option_info(option_name.encode("utf8"))) for option_name in self.list])

  @property
  def list(self):
    """All options' names.

    :type: list

    List of all valid options' names.

    Example:

    >>> from da.p7core import gtdr
    >>> builder = gtdr.Builder()
    >>> builder.options.list
    ['GTDR/LogLevel', 'GTDR/MinImprove', 'GTDR/Normalize', 'GTDR/UseProjection']

    """
    csize = _ctypes.c_size_t(0)
    ccount = _ctypes.c_size_t(0)
    self.__api.GTOptionsManagerGetOptionsNames(self.__impl, _ctypes.byref(ccount), _ctypes.c_char_p(), _ctypes.byref(csize))
    cnames = (_ctypes.c_char * csize.value)()
    self._checkError(self.__api.GTOptionsManagerGetOptionsNames(self.__impl, _ctypes.byref(ccount), cnames, _ctypes.byref(csize)))
    return [_shared.char2str(_) for _ in cnames.raw.split(_six.b('\0')) if _]

  def __str__(self):
    tab = max(len('%s' % opt) for opt in self.list)
    return '\n'.join('%%-%ds: %%s' % tab % (opt, self.get(opt)) for opt in self.list)

  @property
  def values(self):
    """Non-default option values.

    :type: dict

    A dictionary with option values and option names as keys; all keys and values are strings.

    Contains only those options that were :meth:`~da.p7core.Options.set()` explicitly.
    """
    csize = _ctypes.c_size_t(0)
    self.__api.GTOptionsManagerGetOptionsValues(self.__impl, _ctypes.c_char_p(), _ctypes.byref(csize))
    cvalues = (_ctypes.c_char * csize.value)()
    self._checkError(self.__api.GTOptionsManagerGetOptionsValues(self.__impl, _ctypes.cast(cvalues, _ctypes.c_char_p), _ctypes.byref(csize)))
    return _shared.parse_json(cvalues.value)

  def _values(self, output_index):
    """Non-default option values modified for Python-based componentwise training.

    :param output_index: 0-based index or list of indices of the output(s) to train
    :type output_index: integer, list

    :return: A dictionary with option values and option names as keys.
    :type: dict
    """
    outputs_list = _numpy.array([], dtype=_ctypes.c_size_t) if output_index is None\
              else _numpy.array(output_index, dtype=_ctypes.c_size_t).reshape(-1)

    initial_size = 4096
    csize = _ctypes.c_size_t(initial_size)
    cvalue = (_ctypes.c_char * csize.value)()
    self._checkError(self.__api.GTOptionsManagerRearrangeComponentwiseOptionsValues(self.__impl,
                            outputs_list.shape[0], outputs_list.ctypes.data_as(self.__api.c_size_ptr),
                            _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize)))
    if csize.value > initial_size:
      cvalue = (_ctypes.c_char * csize.value)()
      self._checkError(self.__api.GTOptionsManagerRearrangeComponentwiseOptionsValues(self.__impl,
                              outputs_list.shape[0], outputs_list.ctypes.data_as(self.__api.c_size_ptr),
                              _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize)))

    return _shared.parse_json(cvalue.value)

  def reset(self):
    """Reset all options to their default values."""
    self._checkError(self.__api.GTOptionsManagerResetOptions(self.__impl))

  def __last_error_status(self):
    status = _ctypes.c_int(0)
    return self.__api.GTOptionsManagerGetLastErrorStatus(self.__impl, _ctypes.byref(status)), status.value

  def __last_error(self):
    csize = _ctypes.c_size_t(0)
    self.__api.GTOptionsManagerGetLastError(self.__impl, _ctypes.c_char_p(), _ctypes.byref(csize))
    cvalue = (_ctypes.c_char * csize.value)()
    ret = self.__api.GTOptionsManagerGetLastError(self.__impl, _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize))
    msg = _shared._preprocess_utf8(cvalue.value)
    return ret, msg
