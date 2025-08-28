#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""GTOpt optimizer diagnostic record."""

from .. import shared as _shared

class DiagnosticSeverity(object):
  def __init__(self, id, name):
    self.__id = id
    self.__name = str(name)

  @property
  def id(self):
    """Severity level ID.

    :type: ``int``

    This numeric ID is the same as the severity level integer representation.
    """
    return self.__id

  def __int__(self):
    return self.__id

  def __str__(self):
    return self.__name

  def __repr__(self):
    return self.__name

  def __eq__(self, other):
    return self.__id == other

  def __ne__(self, other):
    return self.__id != other

  def __hash__(self):
    return self.__id

(DIAGNOSTIC_MISC, DIAGNOSTIC_HINT, DIAGNOSTIC_WARNING, DIAGNOSTIC_ERROR) = (DiagnosticSeverity(k-1, v) for k, v in enumerate(('Misc', 'Hint', 'Warning', 'Error')))

class DiagnosticRecord(object):
  """Diagnostic record definition.

  Provides integer and string representations of a severity level, and textual message.
  This class should never be instantiated by user.

  """
  def __init__(self, severity, message):
    _shared.check_type(severity, 'c-tor argument', DiagnosticSeverity)
    self.__severity = severity
    self.__message = str(message)

  @property
  def severity(self):
    """Severity level.

    :type: ``DiagnosticSeverity``
    """
    return self.__severity

  @property
  def message(self):
    """Diagnostic message.

    :type: ``str``
    """
    return self.__message

  def __str__(self):
    return "%-7s: %s" % (str(self.__severity), "\n         ".join(self.__message.split("\n")),)

  def __repr__(self):
    return repr((self.__severity, self.__message, ))

  def __eq__(self, other):
    return self.severity == other.severity and self.message == other.message

  def __hash__(self):
    return hash((self.__severity.id, self.__message))
