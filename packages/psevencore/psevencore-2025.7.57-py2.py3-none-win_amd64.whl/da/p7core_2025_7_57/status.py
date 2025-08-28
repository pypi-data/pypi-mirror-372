#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Status constants.

.. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

*New in version 3.0 Beta 2.*

"""

from . import exceptions as _ex

class Status(object):
  """Status definition.

  Provides integer and string representations of a status, and equality/inequality comparisons.
  This class should never be instantiated by user.

  """
  def __init__(self, id, value):
    self._id = id
    self._value = value

  @property
  def id(self):
    """Status ID.

    :type: ``int``

    This numeric ID is the same as the status integer representation.

    """
    return self._id

  def __hash__(self):
    return hash(self._id)

  def __int__(self):
    return self.id

  def __str__(self):
    return str(self._value)

  def __repr__(self):
    return str(self._value)

  def __eq__(self, other):
    return self._id == other

  def __ne__(self, other):
    return self._id != other

  def __hash__(self):
    return self._id

SUCCESS                = Status(0,  'Success')
IMPROVED               = Status(1,  'Improved')
INFEASIBLE_PROBLEM     = Status(2,  'Infeasible problem')
INVALID_PROBLEM        = Status(3,  'Invalid problem')
NANINF_PROBLEM         = Status(4,  'Nan/Inf problem')
INTERNAL_ERROR         = Status(5,  'Internal error')
INVALID_OPTION         = Status(6,  'Invalid option')
USER_TERMINATED        = Status(7,  'User terminated')
LICENSING_PROBLEM      = Status(8,  'Licensing problem')
IN_PROGRESS            = Status(9,  'In progress')
WRONG_USAGE            = Status(10, 'Wrong usage')
UNSUPPORTED_PROBLEM    = Status(11, 'Unsupported problem')
OUTOFMEMORY_ERROR      = Status(12, 'Out of memory')
FEATURE_NOT_AVAILABLE  = Status(13, 'Feature not available')
INAPPLICABLE_TECHNIQUE = Status(14, 'Inapplicable technique')


_status_map = {
  SUCCESS.id:             SUCCESS,
  IMPROVED.id:            IMPROVED,
  INFEASIBLE_PROBLEM.id:  INFEASIBLE_PROBLEM,
  INVALID_PROBLEM.id:     INVALID_PROBLEM,
  NANINF_PROBLEM.id:      NANINF_PROBLEM,
  INTERNAL_ERROR.id:      INTERNAL_ERROR,
  INVALID_OPTION.id:      INVALID_OPTION,
  USER_TERMINATED.id:     USER_TERMINATED,
  LICENSING_PROBLEM.id:   LICENSING_PROBLEM,
  IN_PROGRESS.id:         IN_PROGRESS,
  WRONG_USAGE.id:         WRONG_USAGE,
  UNSUPPORTED_PROBLEM.id: UNSUPPORTED_PROBLEM,
  OUTOFMEMORY_ERROR.id:   OUTOFMEMORY_ERROR,
  FEATURE_NOT_AVAILABLE.id: FEATURE_NOT_AVAILABLE,
  INAPPLICABLE_TECHNIQUE.id: INAPPLICABLE_TECHNIQUE,}

_ex_types = {
  INVALID_OPTION:      _ex.InvalidOptionsError,
  INFEASIBLE_PROBLEM:  _ex.InfeasibleProblemError,
  INVALID_PROBLEM:     _ex.InvalidProblemError,
  NANINF_PROBLEM:      _ex.NanInfError,
  INTERNAL_ERROR:      _ex.InternalError,
  USER_TERMINATED:     _ex.UserTerminated,
  WRONG_USAGE:         _ex.WrongUsageError,
  LICENSING_PROBLEM:   _ex.LicenseError,
  UNSUPPORTED_PROBLEM: _ex.UnsupportedProblemError,
  OUTOFMEMORY_ERROR:   _ex.OutOfMemoryError,
  FEATURE_NOT_AVAILABLE: _ex.FeatureNotAvailableError,
  INAPPLICABLE_TECHNIQUE: _ex.InapplicableTechniqueException,
}


def exception_by_status_id(status_id):
  return _ex_types.get(_status_map.get(status_id, None), None)

def _select_status(left_status, right_status):
  status_priorities = {
    USER_TERMINATED: 0, # maximal priority
    IMPROVED:        1,
    SUCCESS:         2,
    # all errors have equal priority, 3
    IN_PROGRESS:     4,
  }

  return status_priorities.get(left_status, 3) < status_priorities.get(right_status, 3)
