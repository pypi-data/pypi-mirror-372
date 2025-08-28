#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
.. currentmodule: da.p7core.license

"""
import ctypes

from . import six as _six
from . import shared as _shared
from . import exceptions as _exceptions

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self._features_name = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.c_char_p,
                                           ctypes.POINTER(ctypes.c_size_t))(('GTLicenseManagerGetFeaturesNames', self.__library))
    self._features_status = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t),
                                             ctypes.POINTER(ctypes.c_int))(('GTLicenseManagerGetFeaturesAvailabilities', self.__library))

_api = _API()

class License(object):
  """License information interface.

  This class only provides license information methods to other classes
  and should never be instantiated by user.
  """
  def __init__(self, obj, parent, api=_api):
    """
    Args:
      obj - pointer to LicenseManager instance
      parent - object owning instance of license manager
    """
    if not obj:
      self.__impl = None
      return
    else:
      _shared.check_type(obj, 'constructor argument', ctypes.c_void_p)
      self.__impl = obj
      self.__parent = parent
      self.__api = api

  def __raise_on_error(self, succeeded):
    if not succeeded:
      raise _exceptions.InternalError("Backend API call failed")

  def features(self):
    """Get information on captured license features.

    :return: license feature names and their state
    :rtype: dict

    Returns a dictionary where keys are names of requested license features
    and values indicate their availability: ``True`` if captured and available,
    ``False`` if not.
    """
    if not self.__impl:
      return {}

    csize = ctypes.c_size_t(0)
    ccount = ctypes.c_size_t(0)
    self.__raise_on_error(self.__api._features_name(self.__impl, ctypes.byref(ccount), ctypes.c_char_p(), ctypes.byref(csize)))

    if not ccount.value:
      # no license features at all
      return {}

    cnames = (ctypes.c_char * csize.value)()
    self.__raise_on_error(self.__api._features_name(self.__impl, ctypes.byref(ccount), cnames, ctypes.byref(csize)))

    names = [_shared.char2str(_) for _ in cnames.raw.split(_six.b('\0')) if _]
    assert len(names) == ccount.value

    cavailabilities = (ctypes.c_int * ccount.value)()
    self.__raise_on_error(self.__api._features_status(self.__impl, ctypes.byref(ccount), cavailabilities))

    return dict((name, (cap != 0)) for name, cap in _six.moves.zip(names, cavailabilities))
