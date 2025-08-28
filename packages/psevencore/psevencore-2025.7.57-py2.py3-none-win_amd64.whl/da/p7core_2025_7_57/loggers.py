#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Log levels and default logger."""

import sys

from . import exceptions as _ex
from . import six as _six

class _LogLevel(object):
  def __init__(self, id, value):
    self._id = id
    self._value = value

  @property
  def id(self):
    return self._id

  def __int__(self):
    return self.id

  def __str__(self):
    return str(self._value)

  def __repr__(self):
    return "_LogLevel(%(_id)r, %(_value)r)" % vars(self)

  def __eq__(self, other):
    return self._id == other

  def __ne__(self, other):
    return self._id != other

  def __lt__(self, other):
    return self._id < other

  def __le__(self, other):
    return self._id <= other

  def __gt__(self, other):
    return self._id > other

  def __ge__(self, other):
    return self._id >= other

  def __hash__(self):
    return self._id

class LogLevel(object):
  """Enumerates log levels.

  :cvar int DEBUG: debug level
  :cvar int INFO: information level
  :cvar int WARN: warnings level
  :cvar int ERROR: errors level
  :cvar int FATAL: fatal errors level

  .. attribute:: DEBUG

     The most verbose log level, includes all errors and warnings, information messages and debug details.

  .. attribute:: INFO

     Includes all errors, warnings, and information messages.
     Does not include detailed debug messages.

     Default log level for :class:`~da.p7core.loggers.StreamLogger`.

  .. attribute:: WARN

     Includes all errors and warning messages.
     Does not include information and debug messages.

  .. attribute:: ERROR

     Includes only general and fatal error messages.

  .. attribute:: FATAL

     Includes only fatal error messages.

  """

  DEBUG, INFO, WARN, ERROR, FATAL = (_LogLevel(k, v) for k, v in enumerate(('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')))
  _level_map = {
      DEBUG.id: '[d]',
      INFO.id:  '   ',
      WARN.id:  '[w]',
      ERROR.id: '[e]',
      FATAL.id: '[f]' }
  _string_map = dict([(str(_).lower(), _) for _ in (DEBUG, INFO, WARN, ERROR, FATAL)])

  @staticmethod
  def to_string(level):
    """Get short string representation of `level`."""
    if isinstance(level, _LogLevel):
      level = level.id
    if isinstance(level, int):
      return LogLevel._level_map.get(level, '[?]')
    return str(level)

  @staticmethod
  def from_string(log_level_string):
    """Get level from its name `log_level_string`."""
    level = LogLevel._string_map.get(str(log_level_string).lower(), None)
    if level is None:
      raise _ex.GTException("Unknown log_level_string value: '" + str(log_level_string) + "'. It should be 'debug', 'info', 'warn', 'error' or 'fatal'.")
    return level

class StreamLogger(object):
  """Default logger.

  Example logger implementation. Outputs to ``sys.stdout`` by default.

  """
  def __init__(self, stream=None, log_level=LogLevel.INFO):
    if stream is not None:
      self.__stream = stream
    else:
      self.__stream = sys.stdout
    self.log_level = log_level if isinstance(log_level, LogLevel) else LogLevel.from_string(log_level)

  def __call__(self, level, message):
    if self.log_level == LogLevel.DEBUG or level >= self.log_level: #later we will develop TRACE, till use DEBUG for trace
      prefix = LogLevel.to_string(level) + " "
      extended_message = "\n".join([(prefix + _) for _ in message.splitlines()]) + "\n"

      try:
        self.__stream.write(extended_message)
        self.__stream.flush()
        return
      except UnicodeError:
        pass

      try:
        self.__stream.write(extended_message.encode(self.__stream.encoding or "utf8"))
        self.__stream.flush()
        return
      except (AttributeError, UnicodeError):
        pass

      self.__stream.write(extended_message.encode("utf8"))
      self.__stream.flush()
