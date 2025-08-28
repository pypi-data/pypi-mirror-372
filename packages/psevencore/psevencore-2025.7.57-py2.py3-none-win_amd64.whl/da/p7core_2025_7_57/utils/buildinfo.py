#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Utility function for generic tools build information"""
from __future__ import division

from .. import shared as _shared

import ctypes

_PGETINFO = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t))


def __checkCall(err):
  if not err:
    msg = ('C call failed! Message: %s')
    raise Exception(msg)

def buildinfo():
  """Build text description.
  :Type: ``dict``
  This info contains technical information about pSeven Core build.
  """
  size = ctypes.c_size_t()
  __checkCall(_PGETINFO (("GTUtilsGetBuildInfo", _shared._library))(ctypes.c_char_p(), ctypes.byref(size)))
  info = (ctypes.c_char * size.value)()
  __checkCall(_PGETINFO (("GTUtilsGetBuildInfo", _shared._library))(info, ctypes.byref(size)))
  return _shared.parse_json_deep(_shared._preprocess_json(info.value), dict)
