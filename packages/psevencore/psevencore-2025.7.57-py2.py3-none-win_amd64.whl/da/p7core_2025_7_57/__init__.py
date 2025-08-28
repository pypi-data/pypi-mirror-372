#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""pSeven Core package."""

__version__ = "2025.7.57"

import numpy
import ctypes as _ctypes
import atexit as _atexit

def _distutils_loose_version(vstring):
  import re
  vlist = []
  for c in re.split(r'(\d+ | [a-z]+ | \.)', str(vstring), flags=re.VERBOSE):
    if c and c != '.':
      try:
        c = int(c)
      except:
        pass
      vlist.append(c)
  return tuple(vlist)

if _distutils_loose_version(numpy.version.version) < (1,6,0):
  raise Exception('The detected version of numpy is %s. NumPy version 1.6.0 or newer is required to run pSeven Core.' % (numpy.version.version))

from . import FindNative as _FindNative
_FindNative._library, _FindNative._library_welcome_message = _FindNative.loadNativeLib('generic_tools')
if not _FindNative._library:
  raise RuntimeError('Failed to load "generic_tools" backend library.')

_ctypes.CFUNCTYPE(_ctypes.c_void_p)(("GTWarmUp", _FindNative._library))()

_shutdown = _ctypes.CFUNCTYPE(_ctypes.c_void_p)(("GTShutDown", _FindNative._library))
_atexit.register(_shutdown)

from . import shared as _shared
from .options import Options
from .license import License
from .parameters import Parameters
from .exceptions import Exception, GTException, XTException, InvalidOptionsError, InvalidOptionNameError,\
                        InvalidOptionValueError, InvalidProblemError, FeatureNotAvailableError, InfeasibleProblemError,\
                        UnsupportedProblemError, NanInfError, InternalError, OutOfMemoryError, UserTerminated, WrongUsageError,\
                        LicenseError, IllegalStateError, InapplicableTechniqueException, ExceptionWrapper, BBPrepareException,\
                        UserEvaluateException, WatcherException, LoggerException
from . import gtapprox
from . import gtdf
from . import gtdoe
from . import gtdr
from . import gtsda
from . import gtopt
from . import stat
from .result import Result

_NONE = _shared._NONE

__all__ = ['gtapprox', 'gtdf', 'gtdoe', 'gtdr', 'gtsda', 'gtopt', 'stat']
