#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""pSeven Core exceptions."""

class Exception(Exception):
  """Base pSeven Core exception."""
  pass

class GTException(Exception):
  """Base pSeven Core Generic Tools exception class."""
  pass

class XTException(Exception):
  """Base pSeven Core Extras exception."""
  pass

class InvalidOptionsError(GTException):
  """Wrong option has been passed."""
  pass

class InvalidOptionNameError(InvalidOptionsError):
  """Wrong option name has been passed."""
  pass

class InvalidOptionValueError(InvalidOptionsError):
  """Wrong option value has been passed."""
  pass

class InvalidProblemError(GTException):
  """Invalid/inconsistent problem."""
  pass

class FeatureNotAvailableError(GTException):
  """Particular feature not supported."""
  pass

class InfeasibleProblemError(GTException):
  """No feasible points found."""
  pass

class UnsupportedProblemError(GTException):
  """Given problem can not be solved by current version of optimizer."""
  pass

class NanInfError(GTException):
  """Too many NaN/Inf values encountered."""
  pass

class InternalError(GTException):
  """Internal error."""
  pass

class OutOfMemoryError(GTException):
  """The problem given is too big to be solved."""
  pass

class UserTerminated(GTException):
  """Process terminated by user."""
  pass

class WrongUsageError(GTException):
  """Invalid usage of model API."""
  pass

class LicenseError(GTException):
  """Required license feature not found, or other license error. See section :ref:`gen_license_usage` for details."""
  pass

class IllegalStateError(GTException):
  """Attempt to perform action on object with unsuitable state."""
  pass

class InapplicableTechniqueException(GTException):
  """The approximation technique requested is incompatible with the learning dataset and/or options given."""
  pass

class ExceptionWrapper(GTException):
  """Prefixing exception wrapper."""
  _prefix = ""
  _body = "%s: %s"
  __str__ = lambda self: self._prefix + self._body%(type(self.args[0]).__name__, self.args[0])

  def __init__(self, *args):
    super(ExceptionWrapper, self).__init__(*args)
    if len(args) == 1:
      self.message = self.__str__()

  def set_prefix(self, val):
    self._prefix = ("%s" % (val,))
    if len(self.args) == 1:
      self.message = self.__str__()

class BBPrepareException(ExceptionWrapper, InvalidProblemError):
  """Blackbox initialization error."""
  _body = "%s in black box prepare: %s"

class UserEvaluateException(ExceptionWrapper):
  """Blackbox evaluation error."""
  _body = "%s in black box evaluation: %s"

class WatcherException(ExceptionWrapper):
  """Internal watcher error."""
  _body = "%s in watcher: %s"

class LoggerException(ExceptionWrapper):
  """Internal logger error."""
  _body = "%s in logger: %s"
