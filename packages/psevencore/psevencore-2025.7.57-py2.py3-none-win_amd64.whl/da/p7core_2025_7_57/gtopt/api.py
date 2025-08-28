#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

from __future__ import division

import sys as _sys
import ctypes as _ctypes
import weakref as _weakref
import numpy as _numpy

from .. import result as _result
from .. import shared as _shared
from .. import status as _status
from .. import exceptions as _ex
from .. import six as _six

from ..loggers import LogLevel
from ..utils import designs as _designs

from . import diagnostic as _diagnostic

class _Solution(object):
  def __init__(self, x, f, c, v, fe, ce, ve, psi, psie):
    if len(fe) != len(f) or len(ce) != len(c) or len(ve) != len(v) or len(c) != len(v):
      raise ValueError('Inconsistent solution structure!')

    object.__setattr__(self, 'x', x)
    object.__setattr__(self, 'f', f)
    object.__setattr__(self, 'c', c)
    object.__setattr__(self, 'v', v)
    object.__setattr__(self, 'fe', fe)
    object.__setattr__(self, 'ce', ce)
    object.__setattr__(self, 've', ve)
    object.__setattr__(self, 'psi', psi)
    object.__setattr__(self, 'psie', psie)

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

  def __str__(self):
    l = len(self.x)
    if l == 1:
      return "1 point"
    else:
      return "%d points" % l

  def pprint(self, components=None, limit=None, file=_sys.stdout, precision=8):
    if limit is not None:
      _shared.check_concept_int(limit, '`limit` argument')

    fields = [_ for _ in _shared._normalize_string_list(components, default_value=("x", "f", "c"), name="fields") if _numpy.multiply.reduce(_numpy.shape(getattr(self, _)))]
    fields_collection = [_shared.as_matrix(getattr(self, _), dtype=None, name=_) for _ in fields]

    if not fields_collection or not len(fields_collection[0]):
      file.write("<no data>\n")
      return

    post_message = None
    if limit is not None:
      limit, n_points = int(limit), len(fields_collection[0])
      if limit >= 1 and limit < n_points:
        fields_collection = [_[:limit] for _ in fields_collection]
        post_message = '... [ %d more points]\n' % ((n_points - limit),)

    field_width = precision + 6
    format_val = '%-0' + str(field_width) + '.' + str(precision) + 'g'
    hole_marker = ('%-0' + str(field_width) + 's') % '<no data>'

    def num2str(xi):
      return '[' + ' '.join([(hole_marker if _shared._NONE == xij else (format_val % xij)) for xij in xi]) + ']'

    def obj2str(xi):
      return '[' + ' '.join([(hole_marker if xij is None else str(xij)) for xij in xi]) + ']'

    printers = [num2str]*len(fields_collection)
    for i, (name, data) in enumerate(zip(fields, fields_collection)):
      if name == "f" and not _numpy.issubdtype(data.dtype, float):
        regular = []
        payloads = []

        for vec in data.T:
          try:
            regular.append(_shared.as_matrix(vec, shape=(1,None), detect_none=True))
          except:
            payloads.append(vec.reshape(1, -1))

        if payloads:
          fields[i] = "f[objective]"
          fields_collection[i] = _numpy.hstack(regular)
          fields.append("f[payload]")
          fields_collection.append(_numpy.hstack(payloads))
          printers.append(obj2str)

        break

    for values in zip(*fields_collection):
      file.write(" ".join(["%s: %s" % (c, p(v)) for c, p, v in zip(fields, printers, values)]) + '\n')

    if post_message:
      file.write(post_message)

class Result(object):
  r"""
  Optimization result. An object of this class is only returned by :meth:`~da.p7core.gtopt.Solver.solve()` and should never be instantiated by user.

  .. versionchanged:: 3.0
     removed the converged point set.

  .. py:attribute:: infeasible

     .. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

     *New in version 3.0 Beta 1.*

     Additional Pareto-optimal points from the evaluated set that somehow violate problem constraints
     (see :ref:`ug_gtopt_result_result_sets` for details).
     Note that if :ref:`GTOpt/OptimalSetType<GTOpt/OptimalSetType>` is ``"Strict"``, this attribute contains no data.

     .. py:attribute:: infeasible.c

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Constraint values. Array shape is *(n,* :meth:`~da.p7core.gtopt.ProblemGeneric.size_c()`\ *)* where *n* is the number of found points.

        For robust optimization problems (see :ref:`ug_gtopt_ro`) the interpretation of values in this
        array depends on constraint type (see :ref:`ug_gtopt_ro_formulation`):

        * For expectation constraints, the value is the estimate of the expected constraint value.
        * For chance constraints, the value is the estimated probability of constraint violation.

        Estimation errors are stored in :attr:`infeasible.ce<da.p7core.gtopt.Result.infeasible.ce>`.

     .. py:attribute:: infeasible.ce

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        The errors of constraint estimates for stochastic problems.
        For non-stochastic problems, all errors are considered to be ``0.0``.

        Array shape is the same as of :attr:`infeasible.c<da.p7core.gtopt.Result.infeasible.c>`.

     .. py:attribute:: infeasible.f

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Objective function values. Array shape is *(n,* :meth:`~da.p7core.gtopt.ProblemGeneric.size_f()`\ *)* where *n* is the number of found points.

        For stochastic problems (see :ref:`ug_gtopt_ro`) this array contains
        estimated values of objectives, and estimation errors are stored
        in :attr:`infeasible.fe<da.p7core.gtopt.Result.infeasible.fe>`.

     .. py:attribute:: infeasible.fe

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        The errors of objective function estimates for stochastic problems.
        For non-stochastic problems, all errors are considered to be ``0.0``.

        Array shape is the same as of :attr:`infeasible.f<da.p7core.gtopt.Result.infeasible.f>`.

     .. py:attribute:: infeasible.psi

        :type: ``ndarray``, 1D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        For non-stochastic problems: point feasibility measures
        defined as `\psi(x) = \max_i \psi^i(x)` (see :attr:`infeasible.v<da.p7core.gtopt.Result.infeasible.v>`).
        For stochastic problems: `\psi^*_{N_s}` estimates.

        Array shape is *(n, )* where *n* is the number of points in the result.

     .. py:attribute:: infeasible.psie

        :type: ``ndarray``, 1D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        For stochastic problems: `\psi^*_{N_s}` estimation errors.
        For non-stochastic problems this attribute has no meaning and is filled with zeros.

        Array shape is the same as of :attr:`infeasible.psi<da.p7core.gtopt.Result.infeasible.psi>`.

     .. py:attribute:: infeasible.v

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Normalized constraint violation/satisfaction values defined as
        `\psi^i(x) = \max\left[ \frac{c^i_L - c^i(x)}{\max(1., |c^i_L|)}, \frac{c^i(x) - c^i_U}{\max(1., |c^i_U|)} \right]`.
        Array shape is the same as of :attr:`infeasible.c<da.p7core.gtopt.Result.infeasible.c>`.

        For stochastic problems (see :ref:`ug_gtopt_ro`) this array contains estimated values since it is
        derived from :attr:`infeasible.c<da.p7core.gtopt.Result.infeasible.c>`. The errors of violation/satisfaction estimates
        are stored in :attr:`infeasible.ve<da.p7core.gtopt.Result.infeasible.ve>`.

     .. py:attribute:: infeasible.ve

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        The errors of constraint violation/satisfaction estimates for stochastic problems.
        For non-stochastic problems, all errors are considered to be ``0.0``.

        Array shape is the same as of :attr:`infeasible.v<da.p7core.gtopt.Result.infeasible.v>`.

     .. py:attribute:: infeasible.x

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Values of variables. Array shape is *(n,* :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()`\ *)* where *n* is the number of found points.



  .. py:attribute:: info

     :type: ``dict``

     Human-readable report on the solved problem and optimizer settings used.



  .. py:attribute:: names

     Names of problem variables, objectives and constraints.

     .. py:attribute:: names.c

        :type: ``list[str]``

        The names of constraints set by :meth:`~da.p7core.gtopt.ProblemGeneric.add_constraint()`, listed in order of adding constraints to a problem.

     .. py:attribute:: names.f

        :type: ``list[str]``

        The names of objectives set by :meth:`~da.p7core.gtopt.ProblemGeneric.add_objective()`, listed in order of adding objectives to a problem.

     .. py:attribute:: names.x

        :type: ``list[str]``

        The names of variables set by :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`, listed in order of adding variables to a problem.



  .. py:attribute:: optimal

     All feasible Pareto-optimal points from the evaluated set
     (see :ref:`ug_gtopt_result_result_sets` for details).

     .. py:attribute:: optimal.c

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Constraint values. Array shape is *(n,* :meth:`~da.p7core.gtopt.ProblemGeneric.size_c()`\ *)* where *n* is the number of found points.

        For robust optimization problems (see :ref:`ug_gtopt_ro`) the interpretation of values in this
        array depends on constraint type (see :ref:`ug_gtopt_ro_formulation`):

        * For expectation constraints, the value is the estimate of the expected constraint value.
        * For chance constraints, the value is the estimated probability of constraint violation.

        Estimation errors are stored in :attr:`optimal.ce<da.p7core.gtopt.Result.optimal.ce>`.

     .. py:attribute:: optimal.ce

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        The errors of constraint estimates for stochastic problems.
        For non-stochastic problems, all errors are considered to be ``0.0``.

        Array shape is the same as of :attr:`optimal.c<da.p7core.gtopt.Result.optimal.c>`.

     .. py:attribute:: optimal.f

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Objective function values. Array shape is *(n,* :meth:`~da.p7core.gtopt.ProblemGeneric.size_f()`\ *)* where *n* is the number of found points.

        For stochastic problems (see :ref:`ug_gtopt_ro`) this array contains
        esimetd values of objectives, and estimation errors are stored
        in :attr:`optimal.fe<da.p7core.gtopt.Result.optimal.fe>`.

     .. py:attribute:: optimal.fe

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        The errors of objective function estimates for stochastic problems.
        For non-stochastic problems, all errors are considered to be ``0.0``.

        Array shape is the same as of :attr:`optimal.f<da.p7core.gtopt.Result.optimal.f>`.

     .. py:attribute:: optimal.psi

        :type: ``ndarray``, 1D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        For non-stochastic problems: point feasibility measures
        defined as `\psi(x) = \max_i \psi^i(x)` (see :attr:`optimal.v<da.p7core.gtopt.Result.optimal.v>`).
        For stochastic problems: `\psi^*_{N_s}` estimates.

        Array shape is *(n, )* where *n* is the number of points in the result.

     .. py:attribute:: optimal.psie

        :type: ``ndarray``, 1D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        For stochastic problems: `\psi^*_{N_s}` estimation errors.
        For non-stochastic problems this attribute has no meaning and is filled with zeros.

        Array shape is the same as of :attr:`optimal.psi<da.p7core.gtopt.Result.optimal.psi>`.

     .. py:attribute:: optimal.v

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Normalized constraint violation/satisfaction values defined as
        `\psi^i(x) = \max\left[ \frac{c^i_L - c^i(x)}{\max(1., |c^i_L|)}, \frac{c^i(x) - c^i_U}{\max(1., |c^i_U|)} \right]`.
        Array shape is the same as of :attr:`optimal.c<da.p7core.gtopt.Result.optimal.c>`.

        For stochastic problems (see :ref:`ug_gtopt_ro`) this array contains estimated values since it is
        derived from :attr:`optimal.c<da.p7core.gtopt.Result.optimal.c>`. The errors of violation/satisfaction estimates
        are stored in :attr:`optimal.ve<da.p7core.gtopt.Result.optimal.ve>`.

     .. py:attribute:: optimal.ve

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        The errors of constraint violation/satisfaction estimates for stochastic problems.
        For non-stochastic problems, all errors are considered to be ``0.0``.

        Array shape is the same as of :attr:`optimal.v<da.p7core.gtopt.Result.optimal.v>`.

     .. py:attribute:: optimal.x

        :type: ``ndarray``, 2D

        .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

        *Changed in version 3.0 Release Candidate 1:* attribute type is ``ndarray``.

        Values of variables. Array shape is *(n,* :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()`\ *)* where *n* is the number of found points.



  .. attribute:: status

     Finish status.

     :type: :class:`~da.p7core.status.Status`

     .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

     *Changed in version 3.0 Beta 2:* attribute type is :class:`~da.p7core.status.Status`.

     For details, see section :ref:`gen_status`.

  """
  def __init__(self, info, status, problem_ref, optimal_points, converged_points, infeasible_points, diagnostics):
    _shared.check_type(info, 'c-tor argument', _six.string_types)
    _shared.check_type(status, 'c-tor argument', _status.Status)
    _shared.check_type(optimal_points, 'c-tor argument', _Solution)
    _shared.check_type(infeasible_points, 'c-tor argument', _Solution)
    if optimal_points is not converged_points:
      _shared.check_type(converged_points, 'c-tor argument', _Solution)
    if diagnostics is not None:
      _shared.check_concept_sequence(diagnostics, 'c-tor argument')
      unique_diagnostics, diagnostics_set = [], set()
      for note in diagnostics:
        if note not in diagnostics_set:
          unique_diagnostics.append(note)
          diagnostics_set.add(note)
      diagnostics = unique_diagnostics
      del unique_diagnostics
      del diagnostics_set
    object.__setattr__(self, 'info', _shared.parse_json_deep(info))
    object.__setattr__(self, 'status', status)
    object.__setattr__(self, 'diagnostics', diagnostics)
    object.__setattr__(self, 'names', _result._Names(problem_ref))
    object.__setattr__(self, 'optimal', optimal_points)
    object.__setattr__(self, '_converged', converged_points)
    object.__setattr__(self, 'infeasible', infeasible_points)

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

  def __str__(self):
    stream = _six.moves.StringIO()

    try:
      stream.write('Optimization result:\n')
      stream.write('  Status:                   ' + str(self.status) + "\n")
      stream.write('  Attributes:               ' + (", ".join(field for field in ('x', 'f', 'c', 'v', 'fe', 'ce', 've', 'psi', 'psie') \
                                                               if (_numpy.multiply.reduce(_numpy.shape(getattr(self.optimal, field))) or \
                                                                   _numpy.multiply.reduce(_numpy.shape(getattr(self.infeasible, field))))) \
                                                      or "<no data>") + "\n")
      stream.write('  Optimal solutions set:    ' + str(self.optimal) + "\n")
      stream.write('  Infeasible solutions set: ' + str(self.infeasible) + "\n")
    except:
      pass

    try:
      if self.diagnostics:
        stream.write("Details:\n")
        for note in self.diagnostics:
          stream.write("  " + "\n  ".join(str(note).split("\n")) + "\n")
    except:
      pass # no drama, do nothing

    try:
      n_feasible, n_infeasible = len(self.optimal.x), len(self.infeasible.x)
      if (n_feasible + n_infeasible) < 40:
        stream.write("Optimal solutions:\n")
        self.optimal.pprint(file=stream)
        if n_infeasible:
          stream.write("Infeasible solutions:\n")
          self.infeasible.pprint(file=stream)
      else:
        stream.write("<The set of all solutions is too long, consider using _.optimal.pprint() and _.infeasible.pprint()>")
    except:
      pass

    return stream.getvalue()

class RequestIntermediateResult():
  """The callable object that is given to user to get intermediate result
  """

  def __init__(self, instance):
    """
    C-tor

    :param instance: GTOptAPI
    :type instance: weakref object
    """
    self.__instance = instance

  def __call__(self):
    return self.__instance.intermediate_result()


# C callbacks signatures
_c_double_p = _ctypes.POINTER(_ctypes.c_double)
_c_int_p = _ctypes.POINTER(_ctypes.c_int)

_PEVAL = _ctypes.CFUNCTYPE(_ctypes.c_short, _c_double_p, _c_double_p, _ctypes.POINTER(_ctypes.c_short),
                           _ctypes.c_void_p, #userdata
                           _ctypes.POINTER(_ctypes.c_short),
                          _ctypes.c_uint, _ctypes.c_uint, _ctypes.c_uint)
# typedef short (*evalCallback) (double* x, double* r, short* imask, void* userdata, short* omask, unsigned batch, unsigned variables, unsigned responses);

_PTERMINATE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_short, _ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p)
#typedef short (*terminateCallback) (short external, short optimalSetUpdated, GTOptSolver* optimizer, void* userdata);

_PLOG = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_int, _ctypes.c_char_p, _ctypes.c_void_p)
#typedef short (*loggerCallback) (int level, const char* message, void* userdata);

_PSAMPLE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_uint, _c_double_p, _ctypes.c_uint, _ctypes.c_void_p)
#typedef short (*getSampleCallback) (unsigned sampleSize, double* sample, unsigned numberOfStochastic, void* userdata);

#GTOPT_OPERATION_MODES
(GTOPT_SOLVE, GTOPT_VALIDATE, GTOPT_DOE, GTOPT_VALIDATE_DOE) = range(4)

class GTOptAPI:
  """
  Collection of routines to access c-optimization interface
  """

  # Interface statuses
  SUCCESS                = _status.SUCCESS
  IMPROVED               = _status.IMPROVED
  INFEASIBLE_PROBLEM     = _status.INFEASIBLE_PROBLEM
  INVALID_PROBLEM        = _status.INVALID_PROBLEM
  NANINF_PROBLEM         = _status.NANINF_PROBLEM
  INTERNAL_ERROR         = _status.INTERNAL_ERROR
  INVALID_OPTION         = _status.INVALID_OPTION
  USER_TERMINATED        = _status.USER_TERMINATED
  LICENSING_PROBLEM      = _status.LICENSING_PROBLEM
  IN_PROGRESS            = _status.IN_PROGRESS
  WRONG_USAGE            = _status.WRONG_USAGE
  UNSUPPORTED_PROBLEM    = _status.UNSUPPORTED_PROBLEM
  OUTOFMEMORY_ERROR      = _status.OUTOFMEMORY_ERROR
  FEATURE_NOT_AVAILABLE  = _status.FEATURE_NOT_AVAILABLE
  INAPPLICABLE_TECHNIQUE = _status.INAPPLICABLE_TECHNIQUE

  _status_map = _status._status_map
  _ex_types = _status._ex_types

  _severity_map = { _diagnostic.DIAGNOSTIC_HINT.id: _diagnostic.DIAGNOSTIC_HINT
                  , _diagnostic.DIAGNOSTIC_WARNING.id: _diagnostic.DIAGNOSTIC_WARNING
                  , _diagnostic.DIAGNOSTIC_ERROR.id: _diagnostic.DIAGNOSTIC_ERROR
                  , _diagnostic.DIAGNOSTIC_MISC.id: _diagnostic.DIAGNOSTIC_MISC
                  }

  def __init__(self):
    """Constructor."""
    assert(_shared._library)

    self.__instance = None #we will get opt instance on demand
    self.__library = _shared._library
    self.__current_sample = None
    self.__sample = None
    self.__evaluate = None
    self.__external_logger, self.__logger_callback = None, None
    self.__external_watcher, self.__terminate_callback = None, None
    self.__pending_error = None
    self.__finalize_result = None # optional result postprocessor
    self.__mode = None # mode of operation, undefined at the beginning

    self._evaluations_map = None # c++ backend does not know about collateral evaluations, so we mark effective evaluation() column
    self._maximization_objectives = [] # indicates "maximization" objectives

    self.__GTOptSolverNew = _ctypes.CFUNCTYPE(_ctypes.c_void_p #retval
                                             , _ctypes.c_void_p
                                             )(("GTOptSolverCreate", self.__library))

    self.__GTOptSolverFree = _ctypes.CFUNCTYPE(_ctypes.c_short #retval
                                              , _ctypes.c_void_p
                                              )(("GTOptSolverFree", self.__library))

    self.__GTOptSolverGetOptionsManager = _ctypes.CFUNCTYPE(_ctypes.c_void_p #retval
                                                           , _ctypes.c_void_p
                                                           )(("GTOptSolverGetOptionsManager", self.__library))

    self.__GTOptSolverGetLicenseManager = _ctypes.CFUNCTYPE(_ctypes.c_void_p #retval
                                                           , _ctypes.c_void_p
                                                           )(("GTOptSolverGetLicenseManager", self.__library))

    self.__GTOptSolverSetVariables = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                      , _ctypes.c_void_p
                                                      , _ctypes.c_uint #nvars
                                                      , _c_double_p #ig,
                                                      , _ctypes.POINTER(_ctypes.c_uint), _ctypes.POINTER(_c_double_p) #levels
                                                      , _ctypes.c_uint, _ctypes.POINTER(_ctypes.c_uint), _ctypes.POINTER(_ctypes.c_char_p), _ctypes.POINTER(_ctypes.c_char_p) #hints
                                                      , _ctypes.c_uint, _ctypes.c_void_p #stoh
                                                      , _ctypes.POINTER(_ctypes.c_uint), _ctypes.POINTER(_c_double_p) #admissible
                                                      )(("GTOptSolverSetVariables", self.__library))


    self.__GTOptSolverSetResponses = _ctypes.CFUNCTYPE(_ctypes.c_short # retcode
                                                      , _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_uint # solver callback numberOfObjectives
                                                      , _ctypes.c_uint, _c_double_p, _c_double_p # constraints with bounds
                                                      , _ctypes.c_uint, _ctypes.POINTER(_ctypes.c_uint) #numberOfHints responseHintIndexes
                                                      , _ctypes.POINTER(_ctypes.c_char_p), _ctypes.POINTER(_ctypes.c_char_p) #hintNames hintValues
                                                      , _ctypes.c_short,_ctypes.c_uint, _c_int_p, _c_int_p #objective grads
                                                      , _ctypes.c_short,_ctypes.c_uint, _c_int_p, _c_int_p #constraint grads
                                                      , _ctypes.POINTER(_ctypes.c_uint), _ctypes.POINTER(_ctypes.c_uint) # uncertainties
                                                      )(("GTOptSolverSetResponses", self.__library))

    self.__GTOptSolverSetCallbacks = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                      , _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p
                                                      )(("GTOptSolverSetCallbacks", self.__library))

    self.__GTOptSolverExecute = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                 , _ctypes.c_void_p, _ctypes.c_short, _result._api._Points
                                                 )(("GTOptSolverExecute", self.__library))

    self.__GTOptSolverRequestIntermediateResult = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                                   , _ctypes.c_void_p
                                                                   )(("GTOptSolverRequestIntermediateResult", self.__library))

    self.__GTOptSolverGetResults = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                    , _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_int_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_double_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_double_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_double_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_double_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_double_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_double_p, _ctypes.POINTER(_ctypes.c_long)
                                                    ,_c_double_p, _ctypes.POINTER(_ctypes.c_long)
                                                    )(("GTOptSolverGetResults", self.__library))


    self.__GTOptSolverGetInfo = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                 , _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_size_t)
                                                 )(("GTOptSolverGetInfo", self.__library))

    self.__GTOptSolverGetDiagnostics = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                         , _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_size_t)
                                                         )(("GTOptSolverGetDiagnostics", self.__library))


    self.__GTOptSolverGetStatus = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                   , _ctypes.c_void_p, _c_int_p
                                                   )(("GTOptSolverGetStatus", self.__library))

    self.__GTOptSolverGetLastError = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                      , _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_size_t)
                                                      )(("GTOptSolverGetLastError", self.__library))

    self.__GTOptSolverTimeLimit = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                      , _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_short)
                                                      )(("GTOptSolverCheckTimeLimit", self.__library))

    self.__GTOptGetVariablesIndexes = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                      , _ctypes.c_void_p # solver
                                                      , _ctypes.c_char_p #name
                                                      , _ctypes.POINTER(_ctypes.c_uint) # number out
                                                      , _ctypes.POINTER(_ctypes.c_uint) # index out
                                                      )(("GTOptGetVariablesIndexes", self.__library))

    self.__GTOptEvaluateByCache = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                  , _ctypes.c_void_p # [in] solver
                                                  , _c_double_p # designs
                                                  , _ctypes.c_size_t # batch size
                                                  )(("GTOptEvaluateByCache", self.__library))

    self.__GTOptSolverRequestLicense = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                  , _ctypes.c_void_p # [in] solver
                                                  , _ctypes.c_void_p # [in] companion
                                                  )(("GTOptSolverRequestLicense", self.__library))

  def __del__(self):
    self.reset(False)

  def __init(self):
    """
    Create cpp optimizer instance
    """

    if (not self.__instance):
      self.__instance = _ctypes.c_void_p(self.__GTOptSolverNew(1234)) ##we put a special value to detect stack corruption
    if self.__instance.value is None:
      raise Exception("Cannot initialize optimizer instance!")
    
  def mode(self):
    return self.__mode

  def reset(self, restart=True):
    """
    Clean up. Must be called after optimizer usage.
    """
    if self.__instance:
      self.__current_sample = None
      self.__evaluate = None
      self.__pending_error = None
      self.__sample = None
      self.__finalize_result = None
      self.__mode = None

      if restart: # in restart mode move license to the new instance
        old_instance = self.__instance
        try:
          self.__instance = _ctypes.c_void_p(self.__GTOptSolverNew(1234)) ##we put a special value to detect stack corruption
          if self.__instance:
            self.__GTOptSolverRequestLicense(self.__instance, _ctypes.c_void_p(self.__GTOptSolverGetLicenseManager(old_instance)))
            self.__GTOptSolverSetCallbacks(self.__instance, self.__logger_callback, self.__terminate_callback) # move watcher and logger
        finally:
          self.__GTOptSolverFree(old_instance)
      else:
        self.__GTOptSolverFree(self.__instance)
        self.__instance = None
        self.__external_logger, self.__logger_callback = None, None
        self.__external_watcher, self.__terminate_callback = None, None


  def get_options_manager(self):
    """Get pointer to options manager."""
    self.__init()
    obj = _ctypes.c_void_p(self.__GTOptSolverGetOptionsManager(self.__instance))
    self.__check_error(obj, "GTOptSolverGetOptionsManager")
    return obj

  def get_license_manager(self):
    """Get pointer to license manager."""
    self.__init()
    obj = _ctypes.c_void_p(self.__GTOptSolverGetLicenseManager(self.__instance))
    self.__check_error(obj, "GTOptSolverGetLicenseManager")
    return obj

  def request_license(self, companion=None):
    """Acquire required licenses."""
    self.__init()
    self.__check_error(self.__GTOptSolverRequestLicense(self.__instance, companion), "GTOptSolverRequestLicense")

  def setup_problem(self, problem, postprocess_satellite_objective):
    """ Set variables, responses and other staff from given problem blackbox

      :param problem: problem blackbox
      :type problem: gtopt.ProblemGeneric

    """
    self.__init()
    self.__problem = _weakref.ref(problem) # we have to save problem instance, for a proper callback work
    self.__sample = _PSAMPLE(_SampleCallback(self))

    combined_vars_hints = [dict(var.hints) for var in problem._variables]

    number_of_hins = sum(len(_) for _ in combined_vars_hints)

    variable_hint_indexes = (_ctypes.c_uint * number_of_hins)() #ctypes... sigh... if numberOfHins==0 it won't be a zero pointer. Don't want to fight with
    hint_names  = (_ctypes.c_char_p * number_of_hins)()
    hint_values = (_ctypes.c_char_p * number_of_hins)()
    number_of_level = (_ctypes.c_uint * problem.size_x())()
    levels = (_c_double_p * problem.size_x())()
    idx = 0
    for i, var in enumerate(problem._variables):
      #nan goes quite well here
      levels[i] = var.bounds.ctypes.data_as(_c_double_p)
      number_of_level[i] = var.bounds.size

      var_hints = combined_vars_hints[i]
      for hint in var_hints:
        variable_hint_indexes[idx] = i
        hint_names[idx] = hint.encode("ascii")
        hint_values[idx] = str(var_hints[hint]).encode("ascii")
        idx += 1
    assert idx == number_of_hins

    if problem.initial_guess() is not None:
      initial_guess = _numpy.asarray(problem.initial_guess(), order="C") #NOTE Such operations can not be nested. We need explicit numpy object to get valid pointer on it.
      initial_guess_p = initial_guess.ctypes.data_as(_c_double_p)
    else:
      initial_guess_p = _c_double_p()

    ad_length = len(problem._admissible_values)
    if ad_length:
      admissible_shape = (_ctypes.c_uint * 2)()
      admissible_shape[0] = ad_length
      shape = _six.next(iter(problem._admissible_values)).size
      admissible_shape[1] = shape
      admissible_values = (_c_double_p * ad_length)()
      for i, vals in enumerate(problem._admissible_values):
        admissible_values[i] = vals.ctypes.data_as(_c_double_p)
    else:
      admissible_values = _ctypes.POINTER(_c_double_p)()
      admissible_shape = _ctypes.POINTER(_ctypes.c_uint)()

    response = self.__GTOptSolverSetVariables(self.__instance,
                                                   _ctypes.c_uint(problem.size_x()), initial_guess_p,
                                                   number_of_level, levels,
                                                   _ctypes.c_uint(number_of_hins), variable_hint_indexes, hint_names, hint_values,
                                                   _ctypes.c_uint(problem.size_s()), self.__sample,
                                                   admissible_shape, admissible_values)
    self.__check_error(response, "GTOptSolverSetVariables")

    self.__evaluate = _PEVAL(_EvaluateCallback(self)) #make function object to be persistent

    n_obj, combined_resps = len(problem._objectives), (problem._objectives + problem._constraints)
    combined_resps_hints = [dict(response.hints) for response in combined_resps]

    size_x = problem.size_x()
    size_f = problem.size_f()
    size_c = problem.size_c()

    hint_linear_parameters_vector = problem._normalize_option_name("@GTOpt/LinearParameterVector")
    hint_objective_type = problem._normalize_option_name("@GT/ObjectiveType")
    hint_noise_level = problem._normalize_option_name("@GT/NoiseLevel")

    evaluates_map, collateral_objectives = [], []
    self._maximization_objectives = []
    for obj_index, obj_hints in enumerate(combined_resps_hints[:n_obj]):
      objective_type = str(obj_hints.pop(hint_objective_type, "minimize")).lower()
      evaluates_map.append(objective_type not in  ("evaluate", "payload",))
      if not evaluates_map[-1]:
        collateral_objectives.append(obj_index)
        if postprocess_satellite_objective:
          postprocess_satellite_objective(obj_index, obj_hints)
        if str(obj_hints.get(hint_noise_level, "")).lower() == "fromblackbox":
          raise ValueError('"' + objective_type.capitalize() + '" objective does not support blackbox-based noise level: hints values `@GT/ObjectiveType=' + objective_type.capitalize() + '` and `@GT/NoiseLevel=FromBlackbox` are mutually exclusive.')
      elif objective_type == "maximize":
        self._maximization_objectives.append(obj_index)
        weights = obj_hints.get(hint_linear_parameters_vector)
        if weights:
          obj_hints[hint_linear_parameters_vector] = [-_ for _ in weights]

    if collateral_objectives:
      combined_resps_hints = [combined_resps_hints[i] for i, k in enumerate(evaluates_map) if k] + combined_resps_hints[n_obj:]
      evaluates_map = evaluates_map + [True]*size_c # get all constraints

    number_of_hins = sum(len(_) for _ in combined_resps_hints)

    hint_indexes = (_ctypes.c_uint * number_of_hins)()
    hint_names  = (_ctypes.c_char_p * number_of_hins)()
    hint_values = (_ctypes.c_char_p * number_of_hins)()
    idx = 0
    #finalize hints
    for i, response_hints in enumerate(combined_resps_hints):
      for hint in response_hints:
        hint_indexes[idx] = i
        hint_names[idx] = hint.encode('ascii')
        hint_values[idx] = str(response_hints[hint]).encode('ascii')
        idx += 1
    assert idx == number_of_hins

    obj_grad = problem.objectives_gradient()
    con_grad = problem.constraints_gradient()

    if obj_grad[0]:
      if obj_grad[1]:#user provides sparse format
        obj_nnz = len(obj_grad[2])
        obj_rows = _numpy.array(obj_grad[2], ndmin=1, dtype=_ctypes.c_int).reshape(-1)
        obj_cols = _numpy.array(obj_grad[3], ndmin=1, dtype=_ctypes.c_int).reshape(-1)
      else:
        obj_nnz = size_x * size_f
        obj_rows = _numpy.repeat(_numpy.arange(size_f, dtype=_ctypes.c_int), size_x)
        obj_cols = _numpy.tile(_numpy.arange(size_x, dtype=_ctypes.c_int), size_f)
      assert obj_rows.size == obj_nnz and obj_cols.size == obj_nnz

      if self._maximization_objectives:
        # gradients of objectives follows constraints which follows objectives
        evaluation_offset = size_f + size_c
        self._maximization_objectives += [(evaluation_offset + i) for i, obj_idx in enumerate(obj_rows) if obj_idx in self._maximization_objectives]

      # remove gradients of collateral objectives if any
      if collateral_objectives:
        effective_grads = _numpy.equal(obj_rows.reshape(-1, 1), [collateral_objectives]).any(axis=1)
        if not effective_grads.all():
          obj_rows = obj_rows[effective_grads]
          obj_cols = obj_cols[effective_grads]
          obj_nnz = obj_rows.shape[0]
        evaluates_map = evaluates_map + effective_grads.tolist()
    else:
      obj_nnz, obj_rows, obj_cols = 0, None, None

    if con_grad[0]:
      if con_grad[1]: #user provides sparse format
        con_nnz = len(con_grad[2])
        con_rows = _numpy.array(con_grad[2], ndmin=1, dtype=_ctypes.c_int).reshape(-1)
        con_cols = _numpy.array(con_grad[3], ndmin=1, dtype=_ctypes.c_int).reshape(-1)
      else: #user provides dense format
        con_nnz = size_x * size_c
        con_rows = _numpy.repeat(_numpy.arange(size_c, dtype=_ctypes.c_int), size_x)
        con_cols = _numpy.tile(_numpy.arange(size_x, dtype=_ctypes.c_int), size_c)
      assert con_rows.size == con_nnz and con_cols.size == con_nnz
    else:
      con_nnz, con_rows, con_cols = 0, None, None

    self._evaluations_map = _numpy.array(evaluates_map + [True]*(con_nnz+problem.size_nf()+problem.size_nc()), dtype=bool) if collateral_objectives else None

    lower_bound = _numpy.asarray(problem.constraints_bounds()[0], order="C")
    upper_bound = _numpy.asarray(problem.constraints_bounds()[1], order="C")

    number_objective_uncertainties = _ctypes.c_uint()
    number_constraint_uncertainties = _ctypes.c_uint()

    response = self.__GTOptSolverSetResponses(self.__instance, self.__evaluate, size_f - len(collateral_objectives)
                                             , size_c, lower_bound.ctypes.data_as(_c_double_p), upper_bound.ctypes.data_as(_c_double_p)
                                             , number_of_hins, hint_indexes, hint_names, hint_values
                                             , obj_grad[0], obj_nnz, (obj_rows.ctypes.data_as(_c_int_p) if obj_nnz else _c_int_p()), (obj_cols.ctypes.data_as(_c_int_p) if obj_nnz else _c_int_p())
                                             , con_grad[0], con_nnz, (con_rows.ctypes.data_as(_c_int_p) if con_nnz else _c_int_p()), (con_cols.ctypes.data_as(_c_int_p) if con_nnz else _c_int_p())
                                             ,_ctypes.byref(number_objective_uncertainties), _ctypes.byref(number_constraint_uncertainties))

    self.__check_error(response, "GTOptSolverSetResponses")
    assert(number_objective_uncertainties.value == problem.size_nf()) # after two years we got two tunnels. TODO remove this checks on review
    assert(number_constraint_uncertainties.value == problem.size_nc())

    return number_objective_uncertainties, number_constraint_uncertainties

  def set_callbacks(self, logger=None, watcher=None):
    """Set auxiliary callbacks for logging and interruption

    :param logger: facility to logging, function with two arguments (int (level), str (message))
    :type logger: ``function``
    :param watcher: facility function with one argument (dict (optimizer, update))
    :type watcher: ``function``

    """
    self.__init()
    self.__external_logger, self.__logger_callback = logger, _PLOG(_LoggerCallback(self, logger))
    if _shared._desktop_mode():
      watcher = _SafeDesktopWatcher(watcher)
    self.__external_watcher, self.__terminate_callback = watcher, _PTERMINATE(_TerminateCallback(self, watcher))
    res = self.__GTOptSolverSetCallbacks(self.__instance, self.__logger_callback, self.__terminate_callback)
    self.__check_error(res, "GTOptSolverSetCallbacks")

  def _report(self, level, message):
    try:
      if self.__external_logger:
        self.__external_logger(level, message)
    except:
      pass

  def _test_terminate(self, intermediate_result):
    # intermediate_result is a callable object that returns an old-style result
    if not self.__external_watcher:
      return True
    elif intermediate_result:
      return self.__external_watcher({"RequestIntermediateResult" : intermediate_result, "ResultUpdated" : True})
    return self.__external_watcher({"ResultUpdated": False})

  def _preprocess_initial_objectives(self, objectives):
    if objectives is None:
      return None

    # Some responses could be removed
    active_responses, size_f = None, self.__problem().size_f()
    if self._evaluations_map is not None:
      active_responses = self._evaluations_map[:size_f]
      if not active_responses.any():
        return None
      elif active_responses.all():
        active_responses = None

    # Some objectives must be inverted
    if active_responses is not None:
      maximization_objectives = [i for i in self._maximization_objectives if active_responses[i]]
    else:
      maximization_objectives = [i for i in self._maximization_objectives if i < size_f]

    original_objectives = objectives
    for i in maximization_objectives:
      finite_mask = ~_numpy.isnan(objectives[:, i])
      if finite_mask.any():
        if objectives is original_objectives:
          objectives = objectives.copy() # copy on write
        if finite_mask.all():
          finite_mask = slice(len(objectives))
        objectives[finite_mask, i] = -objectives[finite_mask, i]

    # Return active objectives only
    return objectives[:, active_responses] if active_responses is not None else objectives

  def execute(self, mode, variables, objectives, constraints, objective_uncertainties, constraint_uncertainties, compatibility):
    """Run solver, pass guesses. API does not know the problem, not checks done.

    :param mode: mode to use
    :type mode: int
    :param variables: set of guesses for optimizer
    :type variables: ``ndarray``
    :param objectives: objective values for guesses
    :type objectives: ``ndarray``
    :param constraints: constraint values for guesses
    :type constraints: ``ndarray``
    :param objective_uncertainties: objective value uncertainties for guesses
    :type objective_uncertainties: ``ndarray``
    :param constraint_uncertainties: constraint value uncertainties for guesses
    :type constraint_uncertainties: ``ndarray``
    :type compatibility: bool
    :param compatibility: if ``true`` returns old result


    """

    assert(self.__instance)
    self.__compatibility = compatibility
    self.__mode = mode
    points = _result._api._Points()
    if variables is not None and variables.shape[0] > 0:
      points.n = variables.shape[0]
      variables_c = _numpy.require(variables, requirements=["C"])
      points.x = variables_c.ctypes.data_as(_c_double_p)
      objectives = self._preprocess_initial_objectives(objectives) # invert maximization objectives and remove non-objective responses (like evaluate)
      if objectives is not None:
        assert objectives.shape[0] == points.n
        objectives_c = _numpy.require(objectives, requirements=["C"])
        points.f = objectives_c.ctypes.data_as(_c_double_p)
      if objective_uncertainties is not None:
        assert objective_uncertainties.shape[0] == points.n
        objective_uncertainties_c = _numpy.require(objective_uncertainties, requirements=["C"])
        points.df = objective_uncertainties_c.ctypes.data_as(_c_double_p)
      if constraints is not None:
        assert constraints.shape[0] == points.n
        constraints_c = _numpy.require(constraints, requirements=["C"])
        points.c = constraints_c.ctypes.data_as(_c_double_p)
      if constraint_uncertainties is not None:
        assert constraint_uncertainties.shape[0] == points.n
        constraint_uncertainties_c = _numpy.require(constraint_uncertainties, requirements=["C"])
        points.dc = constraint_uncertainties_c.ctypes.data_as(_c_double_p)

    res = self.__GTOptSolverExecute(self.__instance, _ctypes.c_short(mode), points)
    self.__check_error(res, "GTOptSolverExecute")

  def set_result_postprocessor(self, postprocessor):
    self.__finalize_result = postprocessor

  def intermediate_result(self):
    """
    Ask optimizer to fill internal results values.
    And then gather results ad return to user.

    :return: Solution object
    :rtype: ``obj``
    """
    assert(self.__instance)
    res = self.__GTOptSolverRequestIntermediateResult(self.__instance)
    self.__check_error(res, "GTOptSolverRequestIntermediateResult")
    return self.get_results(in_progress=True)

  def get_results(self, in_progress=False, initial_sample=None, c_tol=None):
    """
    Return optimization result. By default raise exception on empty result.

    :param in_progress: if false request status from opt, if true use IN_PROGRESS status and not raise exception on empty results
    :type in_progress: ``bool``
    :param mode: operation mode (if in validate mode not raise exception on empty results)
    :type mode: ``int``
    :return: Solution object
    :rtype: ``obj``
    """
    assert(self.__instance)
    info_string = self.get_info()
    status = _status.IN_PROGRESS if in_progress else self.get_status()
    diagnostics = self.get_diagnostics()
    mode = self.mode()

    fix_responses = not in_progress and mode in (GTOPT_SOLVE, GTOPT_DOE)
    solutionsType_i32, variablesValue, objectivesValue, constraintsValue, constraintsViolation, objectiveErrors, constraintErrors, constraintsViolationError = self.get_solutions(fix_responses=fix_responses)
    pointsCount = len(solutionsType_i32)

    problem = self.__problem()

    if pointsCount == 0 and mode not in (GTOPT_VALIDATE, GTOPT_VALIDATE_DOE) and not in_progress:
      if status == _status.SUCCESS and self.__compatibility and problem.history:
        self.raise_exception()
      elif _status.exception_by_status_id(status.id) is not None \
        and status not in (_status.INFEASIBLE_PROBLEM, _status.NANINF_PROBLEM, _status.USER_TERMINATED):
        if problem.history and not self.__compatibility:
          # Never raise if we've evaluated something
          self._report(LogLevel.ERROR, self.get_last_error())
        else:
          self.raise_exception() # Empty result and "fatality" status is error.

    designs = None # we are collecting designs only if do need it
    initial_sample, initial_fields = initial_sample if initial_sample is not None else (None, None)

    if not in_progress:
      alternative_csp = self._is_alternative_csp_problem(mode)
      if self._evaluations_map is not None or not self.__compatibility or alternative_csp:
        # new result requires designs (but not in progress mode), collateral evaluations can be read from the designs only
        designs = self._collect_designs(variablesValue, objectivesValue, constraintsValue, initial_sample, c_tol)

      if self._evaluations_map is not None and designs is not None and "f" in designs[1][2]:
        try:
          size_x, size_s = problem.size_x(), problem.size_s()

          _designs._harmonize_datasets_inplace(problem, {"f": slice(0, objectivesValue.shape[1])},
                                               sample_a=objectivesValue, keys_a=_shared._pad_columns(variablesValue, size_s, _shared._NONE),
                                               sample_b=designs[0][:, designs[1][2]["f"]], keys_b=designs[0][:, :(size_x+size_s)])
        except:
          pass

      if alternative_csp:
        try:
          solutionsType_i32, variablesValue, objectivesValue, constraintsValue, \
            constraintsViolation, objectiveErrors, constraintErrors, constraintsViolationError \
              = self._alternative_csp_solution(design_data=designs[0], design_fields=designs[1][2])
        except:
          pass # this is fine

    if not problem.size_c():
      maximalConstraintsViolation = _numpy.empty((pointsCount, 0))
      maximalConstraintsViolationError = _numpy.empty((pointsCount, 0))
    else:
      maximalConstraintsViolation = _safe_nanmax_by_rows(constraintsViolation).reshape(-1, 1)
      maximalConstraintsViolationError = _safe_nanmax_by_rows(constraintsViolationError).reshape(-1, 1)

    if self.__compatibility:
      if pointsCount == 0:
        # kludge for numpy 1.6
        solution_optimal = _Solution([], [], [], [], [], [], [], [], [])
        solution_converged = _Solution([], [], [], [], [], [], [], [], [])
        solution_infeasible = _Solution([], [], [], [], [], [], [], [], [])
      else:
        # All points are Pareto-optimal in the optimization mode and just optimal in the adaptive design mode
        # So, we simply divided these points into feasible and infeasible sets and stated that there are no discarded points (GT_SOLUTION_TYPE_DISCARDED).
        converged_points = (solutionsType_i32 == _result.GT_SOLUTION_TYPE_CONVERGED) # This is the special set of points for which local optimality has been proven.
        optimal_points = converged_points | (solutionsType_i32 == _result.GT_SOLUTION_TYPE_NOT_DOMINATED) | (solutionsType_i32 == _result.GT_SOLUTION_TYPE_FEASIBLE_NAN)
        infeasible_points = ~optimal_points

        def _decode_compatible_payload(objectives):
          try:
            if problem._payload_objectives:
              decoded_objectives = objectives.astype(object)
              for k in problem._payload_objectives:
                decoded_objectives[:, k] = problem._payload_storage.decode_payload(objectives[:, k])
              objectives = decoded_objectives
              return _shared.as_matrix(objectives, detect_none=True) # Try to convert matrix back to floats. Make sense if all payloads are float.
          except:
            pass
          return objectives


        solution_optimal   =  _Solution(variablesValue[optimal_points], _decode_compatible_payload(objectivesValue[optimal_points]),
                                        constraintsValue[optimal_points], constraintsViolation[optimal_points],
                                        objectiveErrors[optimal_points], constraintErrors[optimal_points],
                                        constraintsViolationError[optimal_points], maximalConstraintsViolation[optimal_points],
                                        maximalConstraintsViolationError[optimal_points])
        solution_converged =  _Solution(variablesValue[converged_points], _decode_compatible_payload(objectivesValue[converged_points]),
                                        constraintsValue[converged_points], constraintsViolation[converged_points],
                                        objectiveErrors[converged_points], constraintErrors[converged_points],
                                        constraintsViolationError[converged_points], maximalConstraintsViolation[converged_points],
                                        maximalConstraintsViolationError[converged_points])
        solution_infeasible = _Solution(variablesValue[infeasible_points], _decode_compatible_payload(objectivesValue[infeasible_points]),
                                        constraintsValue[infeasible_points], constraintsViolation[infeasible_points],
                                        objectiveErrors[infeasible_points], constraintErrors[infeasible_points],
                                        constraintsViolationError[infeasible_points], maximalConstraintsViolation[infeasible_points],
                                        maximalConstraintsViolationError[infeasible_points])

      result = Result(info_string, status, self.__problem, solution_optimal, solution_converged, solution_infeasible, diagnostics)
      return self.__finalize_result(result=result, intermediate_result=in_progress) if self.__finalize_result else result

    fields = {"x": slice(0, variablesValue.shape[1])} # x is always present and always the first field
    offset = variablesValue.shape[1]

    def _optional_field(offset, name, values):
      if not values.size:
        return offset
      next_offset = offset + values.shape[1]
      fields[name] = slice(offset, next_offset)
      return next_offset

    offset = _optional_field(offset, "f", objectivesValue)
    offset = _optional_field(offset, "c", constraintsValue)
    offset = _optional_field(offset, "v", constraintsViolation)
    offset = _optional_field(offset, "psi", maximalConstraintsViolation)
    offset = _optional_field(offset, "fe", objectiveErrors)
    offset = _optional_field(offset, "ce", constraintErrors)
    offset = _optional_field(offset, "ve", constraintsViolationError)
    offset = _optional_field(offset, "psie", maximalConstraintsViolationError)

    fields["flag"] = slice(offset, offset + 1) # flags are always the last field

    solutions_table = _numpy.hstack((variablesValue, objectivesValue, constraintsValue, constraintsViolation, maximalConstraintsViolation,
                                      objectiveErrors, constraintErrors, constraintsViolationError, maximalConstraintsViolationError,
                                      solutionsType_i32.reshape(-1, 1)))

    if in_progress or mode in (GTOPT_VALIDATE, GTOPT_VALIDATE_DOE):
      solutions_subsets = None # do nothing, finalize result
    else:
      # promote initial sample to solution only in DoE mode
      solutions_table, fields, solutions_subsets = _result._postprocess_solution_samples(default_solution=solutions_table, default_fields=fields,
                                                                                         initial_sample=(initial_sample if mode == GTOPT_DOE else None),
                                                                                         initial_fields=(initial_fields if mode == GTOPT_DOE else None),
                                                                                         problem=self.__problem)

    if self.__finalize_result:
      return self.__finalize_result(result=_result.Result(status, info_string, solutions_table, fields, self.__problem, diagnostics, designs=designs,
                                                          solutions_subsets=solutions_subsets, finalize=False), intermediate_result=in_progress)
    return _result.Result(status, info_string, solutions_table, fields, self.__problem, diagnostics, designs=designs,
                          solutions_subsets=solutions_subsets, finalize=(solutions_subsets is None))

  def _is_alternative_csp_problem(self, mode):
    if mode not in (GTOPT_SOLVE, GTOPT_VALIDATE):
      return False
    problem = self.__problem()
    try:
      # there are constraints, but no objective, no stochastic, no initial guess
      if not problem.size_c() \
        or problem.size_s() or  problem.size_nf() or problem.size_nc() \
        or problem.initial_guess() is not None:
        return False

      n_objectives = problem.size_f()
      if self._evaluations_map is not None:
        return not self._evaluations_map[:n_objectives].any()
      return not n_objectives
    except:
      pass
    return False # safe path

  def _alternative_csp_solution(self, design_data, design_fields):
    # Any exceptions (like no key) are safe and welcome
    solutionsType_i32 = design_data[:, design_fields["flag"]].reshape(-1).astype(_numpy.int32)

    # Get any feasible point
    optimal_points = (solutionsType_i32 == _result.GT_SOLUTION_TYPE_CONVERGED) \
                   | (solutionsType_i32 == _result.GT_SOLUTION_TYPE_NOT_DOMINATED) \
                   | (solutionsType_i32 == _result.GT_SOLUTION_TYPE_FEASIBLE_NAN) \
                   | (solutionsType_i32 == _result.GT_SOLUTION_TYPE_DISCARDED)

    n_points = _numpy.count_nonzero(optimal_points)

    if n_points < 2:
      raise _ex.InvalidProblemError()

    variablesValue            = design_data[:, design_fields.get("x", slice(0))][optimal_points, :]
    objectivesValue           = _numpy.empty((n_points, 0))
    constraintsValue          = design_data[:, design_fields.get("c", slice(0))][optimal_points, :]
    constraintsViolation      = design_data[:, design_fields.get("v", slice(0))][optimal_points, :]
    objectiveErrors           = _numpy.empty((n_points, 0))
    constraintErrors          = design_data[:, design_fields.get("ce", slice(0))][optimal_points, :]
    constraintsViolationError = design_data[:, design_fields.get("ve", slice(0))][optimal_points, :]
    solutionsType_i32         = solutionsType_i32[optimal_points]

    return solutionsType_i32, variablesValue, objectivesValue, constraintsValue, constraintsViolation, \
            objectiveErrors, constraintErrors, constraintsViolationError

  def _collect_designs(self, variablesValue, objectivesValue, constraintsValue, initial_sample, c_tol):
    problem = self.__problem()
    try:
      input_size = problem.size_x() + problem.size_s()
      n_initial, designs_table = 0, []

      if initial_sample is not None:
        initial_sample = _shared.as_matrix(initial_sample, shape=(None, input_size+problem.size_full()))
        if initial_sample.size:
          n_initial, designs_table = len(initial_sample), [initial_sample]

      designs_table.extend(problem._history_cache)

      solutions_sample = _designs._preprocess_initial_sample(problem, variablesValue, objectivesValue, constraintsValue, None, None)
      if solutions_sample is not None and solutions_sample.size:
        designs_table.append(solutions_sample)

      if designs_table:
        designs_table = _designs._fill_gaps_and_keep_dups(_numpy.vstack(designs_table), slice(0, input_size),
                                                          _designs._typical_problem_payloads_callback(problem))
        designs_table = _designs._select_unique_rows(designs_table, n_initial)

        self.read_backend_reconstructed_responses(designs_table)

        return _designs._postprocess_designs(problem, designs_table, n_initial, c_tol)
    except:
      pass
    return None

  def get_solutions(self, fix_responses=False):
    """
    Copy solution from optimizer buffer to pythonic variables

    :return: solution types, variables, objectives, constraints, feasibilities, objectives errors, constraints errors, feasibilities errors.
    :rtype: ``tuple``
    """
    assert(self.__instance)
    numberOfPoints = _ctypes.c_long()
    solutionsTypeSize = _ctypes.c_long()
    variablesSize = _ctypes.c_long()
    objectivesSize = _ctypes.c_long()
    constraintsSize = _ctypes.c_long()
    feasibilitiesSize = _ctypes.c_long()
    errorObjectivesSize = _ctypes.c_long()
    errorConstraintsSize = _ctypes.c_long()
    errorFeasibilitiesSize = _ctypes.c_long()
    res = self.__GTOptSolverGetResults(self.__instance, _ctypes.byref(numberOfPoints)
                                                , _c_int_p(), _ctypes.byref(solutionsTypeSize)
                                                , _c_double_p(), _ctypes.byref(variablesSize)
                                                , _c_double_p(), _ctypes.byref(objectivesSize)
                                                , _c_double_p(), _ctypes.byref(constraintsSize)
                                                , _c_double_p(), _ctypes.byref(feasibilitiesSize)
                                                , _c_double_p(), _ctypes.byref(errorObjectivesSize)
                                                , _c_double_p(), _ctypes.byref(errorConstraintsSize)
                                                , _c_double_p(), _ctypes.byref(errorFeasibilitiesSize))
    size_c = self.__problem().size_c()
    true_size_f = self.__problem().size_f()
    if self._evaluations_map is not None:
      size_f = _numpy.count_nonzero(self._evaluations_map[:true_size_f]) # the number of c++ backend objectives
    else:
      size_f = true_size_f

    solutionsType = _numpy.empty(numberOfPoints.value, dtype=_numpy.int32, order="C")
    variables = _numpy.empty((numberOfPoints.value, self.__problem().size_x()), order="C")
    objectives = _numpy.empty((numberOfPoints.value, size_f), order="C")
    constraints = _numpy.empty((numberOfPoints.value, size_c), order="C")
    feasibilities = _numpy.empty((numberOfPoints.value, size_c), order="C")
    errorObjectives = _numpy.empty((numberOfPoints.value, size_f), order="C")
    errorConstraints = _numpy.empty((numberOfPoints.value, size_c), order="C")
    errorFeasibilities = _numpy.empty((numberOfPoints.value, size_c), order="C")
    assert variables.size == variablesSize.value
    assert objectives.size == objectivesSize.value
    assert constraints.size == constraintsSize.value
    assert feasibilities.size == feasibilitiesSize.value
    assert errorObjectives.size == errorObjectivesSize.value
    assert errorConstraints.size == errorConstraintsSize.value
    assert errorFeasibilities.size == errorFeasibilitiesSize.value
    res = self.__GTOptSolverGetResults(self.__instance, _ctypes.byref(numberOfPoints)
                                      , solutionsType.ctypes.data_as(_c_int_p), _ctypes.byref(solutionsTypeSize)
                                      , variables.ctypes.data_as(_c_double_p), _ctypes.byref(variablesSize)
                                      , objectives.ctypes.data_as(_c_double_p), _ctypes.byref(objectivesSize)
                                      , constraints.ctypes.data_as(_c_double_p), _ctypes.byref(constraintsSize)
                                      , feasibilities.ctypes.data_as(_c_double_p), _ctypes.byref(feasibilitiesSize)
                                      , errorObjectives.ctypes.data_as(_c_double_p), _ctypes.byref(errorObjectivesSize)
                                      , errorConstraints.ctypes.data_as(_c_double_p), _ctypes.byref(errorConstraintsSize)
                                      , errorFeasibilities.ctypes.data_as(_c_double_p), _ctypes.byref(errorFeasibilitiesSize))
    self.__check_error(res, "GTOptSolverGetResults")

    objectives = self._unpack_objectives(objectives, true_size_f, _shared._NONE)
    errorObjectives = self._unpack_objectives(errorObjectives, true_size_f, 0.)

    for i in self._maximization_objectives:
      if i < objectives.shape[1]: # note self._maximization_objectives may include gradients as well as objectives
        finite_mask = ~_numpy.isnan(objectives[:, i])
        objectives[finite_mask, i] = -objectives[finite_mask, i]

    if fix_responses:
      # The user can return some reconstructed responses even if we did not ask for it.
      # It creates an annoying discrepancy between history and Opt solution.
      # Since Opt does not allow to modify evaluations, the only option is modify the solution here.
      objectives, constraints, feasibilities = self.__problem()._update_analytical_history(variables, objectives, constraints, feasibilities)

    return solutionsType, variables, objectives, constraints, feasibilities, errorObjectives, errorConstraints, errorFeasibilities

  def _unpack_objectives(self, packed_data, size_f, default_value):
    if self._evaluations_map is None:
      return packed_data
    unpacked_data = _shared._filled_array((packed_data.shape[0], size_f), default_value)
    if self._evaluations_map[:size_f].any():
      unpacked_data[:, self._evaluations_map[:size_f]] = packed_data[:]
    return unpacked_data

  def get_info(self):
    """Get info string from optimizer

    :return: info string (build info, problem description etc)
    :rtype: ``str``
    """
    assert(self.__instance)
    size = _ctypes.c_size_t()
    res = self.__GTOptSolverGetInfo(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size))
    data = (_ctypes.c_char * size.value)()
    res = self.__GTOptSolverGetInfo(self.__instance, data, _ctypes.byref(size))
    self.__check_error(res, "GTOptSolverGetInfo")
    return _shared._preprocess_utf8(data.value)

  def get_diagnostics(self):
    assert(self.__instance)
    size = _ctypes.c_size_t()
    res = self.__GTOptSolverGetDiagnostics(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size))
    data = (_ctypes.c_char * size.value)()
    res = self.__GTOptSolverGetDiagnostics(self.__instance, data, _ctypes.byref(size))
    self.__check_error(res, "GTOptSolverGetDiagnostics")

    try:
      return [_diagnostic.DiagnosticRecord(self._severity_map.get(int(severity)), message.strip()) \
              for severity, message in _shared.parse_json_deep(_shared._preprocess_json(data.value), list)]
    except:
      pass # exception here should not be fatal

    return [_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_HINT, _shared._preprocess_utf8(data.value))]

  def get_status(self):
    """
    Get current optimizer status.

    :return: optimizer status
    :rtype: ``int``
    """
    assert(self.__instance)
    status = _ctypes.c_int()
    err = self.__GTOptSolverGetStatus(self.__instance, _ctypes.byref(status))
    self.__check_error(err, "GTOptSolverGetStatus")
    status = self._status_map.get(status.value, self.INTERNAL_ERROR)
    if status == _status.USER_TERMINATED and self._test_terminate(None):
      # This is a termination due to an evaluation error, not user intent.
      status = _status.SUCCESS
    return status

  def get_last_error(self):
    """
    Get last error from GTOpt.

    :return: Error message
    :rtype: ``str``
    """
    assert(self.__instance)
    size = _ctypes.c_size_t()
    res = self.__GTOptSolverGetLastError(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size))
    data = (_ctypes.c_char * size.value)()
    res = self.__GTOptSolverGetLastError(self.__instance, data, _ctypes.byref(size))
    self.__check_error(res, "GTOptSolverGetLastError")
    return _shared._preprocess_utf8(data.value)

  def __check_error(self, succeeded, name):
    """
    Check error and raise exception if needed

    :param succeeded: value to check
    :type succeeded: ``int``
    :param name: Not actually in use, will be seen in traceback
    :type name: ``str``

    """
    if self.__pending_error is not None:
      exc_type, exc_val, exc_tb = self.__pending_error
      self.__pending_error = None
      _shared.reraise(exc_type, exc_val, exc_tb)

    if not succeeded:
      self.raise_exception()

  def _register_callback_exception(self, exc_info):
    try:
      if exc_info and exc_info[1] is not None:
        if self.__pending_error is None or (isinstance(self.__pending_error[1], Exception) and not isinstance(exc_info[1], Exception)):
          exc_type = _ex.UserEvaluateException if isinstance(exc_info[1], Exception) else exc_info[0]
          self.__pending_error = (exc_type, exc_info[1], exc_info[2])
        if self.__external_watcher:
          notify_watcher = getattr(self.__external_watcher, "_exception_occurred", None)
          if notify_watcher:
            notify_watcher()
    except:
      pass

  def _error_occurred(self):
    return self.__pending_error is not None

  def raise_exception(self, status=None, message=None):
    """
    Raise exception depending on status

    :param status: GTOptAPI status, if None status will be obtained from get_status call
    :type status: ``int``
    :param message: GTOptAPI
    :type message: ``str``

    """
    if status is None:
      status = self.get_status() #we believe that instance exits
    if message is None:
      message = self.get_last_error()

    if status in self._ex_types.keys():
      raise self._ex_types[status](message)
    raise _ex.GTException(message)

  def read_backend_reconstructed_responses(self, designs):
    """
    Read linear and quadratic responses reconstructed by backend.
    Since these responses were reconstructed in c++ code,
    they was not evaluated and may be empty.

    Only objectives with linear or quadratic hints are affected.
    """
    assert(self.__instance)
    if not designs.size:
      return

    problem = self.__problem()
    assert (problem and (problem.size_full() + problem.size_x() + problem.size_s()) == designs.shape[1]), "Invalid shape of the designs argument."

    size_x = problem.size_x()
    input_size = size_x + problem.size_s()
    designs_backup = []
    reconstruct = False

    # Internal implementation overrides all linear and quadratic responses, but we'd like to keep already known values

    for k, linearity_type in enumerate(problem.elements_hint(slice(size_x, None), "@GTOpt/LinearityType")):
      if str(linearity_type).lower() in ("linear", "quadratic"):
        original_designs = designs[:, input_size + k]
        keep_mask = ~_shared._find_holes(original_designs)
        negate = k in self._maximization_objectives

        if keep_mask.all():
          designs_backup.append((original_designs, False, original_designs.copy(), slice(0, len(original_designs))))
        else:
          reconstruct = True
          if keep_mask.any():
            designs_backup.append((original_designs, negate, original_designs.copy(), keep_mask))
          elif negate:
            designs_backup.append((original_designs, True, None, None))

    if not reconstruct:
      return

    if self._evaluations_map is None:
      self.__check_error(self.__GTOptEvaluateByCache(self.__instance, designs.ctypes.data_as(_c_double_p), designs.shape[0]), "GTOptEvaluateByCache")
    else:
      # it's complicated...
      effective_designs = _numpy.hstack((designs[:, :input_size], designs[:, input_size:][:, self._evaluations_map])) # get effective responses
      self.__check_error(self.__GTOptEvaluateByCache(self.__instance, effective_designs.ctypes.data_as(_c_double_p), effective_designs.shape[0]), "GTOptEvaluateByCache")
      designs[:, input_size:][:, self._evaluations_map] = effective_designs[:, input_size:] # copy back responses (inputs was not modified)

    for destination, negate, original_designs, copy_mask in designs_backup:
      if negate:
        update_mask = ~_numpy.isnan(destination)
        if update_mask.all():
          destination = -destination
        elif update_mask.any():
          destination[update_mask] = -destination[update_mask]
      if original_designs is not None:
        destination[copy_mask] = original_designs[copy_mask]

  def collect_initial_sample(self, variables, objectives, constraints, objective_uncertainties, constraint_uncertainties, mode):
    if mode not in (GTOPT_SOLVE, GTOPT_DOE) or self.__compatibility:
      return None, None

    try:
      return _designs._preprocess_initial_sample(problem=self.__problem(), sample_x=variables, sample_f=objectives, sample_c=constraints,
                                                 sample_nf=objective_uncertainties, sample_nc=constraint_uncertainties, return_slices=True)
    except:
      pass

    return None, None
  
class _SafeDesktopWatcher(object):
  def __init__(self, watcher):
    self.__watcher = watcher
    self.__keep_running = True

  def __call__(self, *args, **kwargs):
    # Desktop DSE block hangs up if its watcher is called after an exception occurred
    if not self.__keep_running:
      return False
    elif self.__watcher:
      self.__keep_running = self.__watcher(*args, **kwargs)
    return self.__keep_running
  
  def _exception_occurred(self):
    self.__keep_running = False

class _TerminateCallback(object):
  def __init__(self, parent, watcher):
    self.__parent = _shared.make_proxy(parent)
    self.__watcher = watcher

  def __call__(self, external, updated, instance, null):
    """ Napkin between python watcher with 1 argument and 3 argument _PTERMINATE

    :param external: tell if we solver internal or external problem
    :type external: ``boolean (ctypes short int)``
    :param updated: indicates if set is updated since last delivery call
    :type updated : ``boolean (ctypes short int)``
    :param instance: Optimizer instance
    :type instance: ``ctypes.c_void_p``
    :return: True on success, False otherwise
    :rtype: ``bool`` (ctype short int)
    """
    try:
      assert(instance == self.__parent._GTOptAPI__instance.value)
      if not null:
        self.__parent._report(LogLevel.WARN, "Terminate optimization callback: Python stack corruption detected! Results may be unpredictable.")
      return self.__watcher({"RequestIntermediateResult" : RequestIntermediateResult(self.__parent), "ResultUpdated" : updated}) if self.__watcher else True
    except:
      self.__parent._register_callback_exception(_sys.exc_info())
      self.__parent._report(LogLevel.DEBUG, _shared.read_traceback())

    return False

class _LoggerCallback(object):
  def __init__(self, parent, logger):
    self.__parent = _shared.make_proxy(parent)
    self.__logger = logger if logger else None

  def __call__(self, level, message, null):
    """ Napkin between python logger and c logger

    :param level: loglevel
    :type level: ``int``
    :param message: output message
    :type message: ``str``
    :return: True on success, False otherwise
    :rtype: ``bool`` (ctype short int)
    """
    try:
      if self.__logger is not None:
        self.__logger(level, _shared._preprocess_utf8(message))
      return True
    except:
      self.__parent._register_callback_exception(_sys.exc_info())
    return False

class _SampleCallback(object):
  def __init__(self, parent):
    self.__parent = _shared.make_proxy(parent)

  def __call__(self, quantity, realizations, size, null):
    """ Napkin between sophisticated get_stochastic_values and _PSAMPLE

    :param quantity: number of point to generate
    :type quantity: ``uint``
    :param realizations: pointer to ctype double
    :type realizations: ctype double
    :param size: number of elements in each point
    :type size: ``uint``
    """
    try:
      assert realizations
      assert quantity > 0
      assert size > 0
      if not null:
        self.__parent._report(LogLevel.WARN, "Read sample callback: Python stack corruption detected! Results may be unpredictable.")
      _numpy.frombuffer(_ctypes.cast(realizations, _ctypes.POINTER(_ctypes.c_double * (quantity * size))).contents)[:] = \
        self.__parent._GTOptAPI__problem().get_stochastic_values(quantity)
      # we do a dreadful thing above. Inside it holds sample in 2d array. However we push 1d, because we sure about structure of that internal array.
      return True
    except:
      exc_info = _sys.exc_info()
      self.__parent._register_callback_exception((exc_info[0] if issubclass(exc_info[0], BaseException) else _ex.UserEvaluateException, ) + exc_info[1:])
      self.__parent._report(LogLevel.DEBUG, _shared.read_traceback())

    return False

class _EvaluateCallback(object):
  def __init__(self, parent):
    self.__parent = _shared.make_proxy(parent)

  def timecheck(self):
    proceed = _ctypes.c_short(1)
    try:
      self.__parent._GTOptAPI__GTOptSolverTimeLimit(self.__parent._GTOptAPI__instance, _ctypes.byref(proceed))
    except:
      pass
    return proceed.value
  
  def _register_exception(self, exc_info):
    self.__parent._register_callback_exception((exc_info[0] if issubclass(exc_info[0], BaseException) else _ex.UserEvaluateException, ) + exc_info[1:])

  def _error_occurred(self):
    return self.__parent._error_occurred()

  def __call__(self, variables_batch, responses_batch, input_mask_batch, null, output_mask_batch, batch_size, number_variables, number_responses):
    """
    Napkin between sophisticated problem._evaluate and user-friendly c eval

    :param variables_batch: pointer to [input] variables buffer (size batch_size * number_variables)
    :type variables_batch: ``_ctypes.POINTER(_ctypes.c_double)``
    :param responses_batch: pointer to [output] responses buffer (size batch_size * number_responses)
    :type responses_batch: ``_ctypes.POINTER(_ctypes.c_double)``
    :param input_mask_batch: pointer to requested [in] masks buffer
    :type input_mask_batch: ``_ctypes.POINTER(_ctypes.c_short)``
    :param output_mask_batch: pointer to calculated [out] mask buffer
    :type output_mask_batch: ``_ctypes.POINTER(_ctypes.c_short)``
    :param number_variables: problem input dimensionality
    :type number_variables: ``_ctypes.c_uint``
    :param number_responses: problem output dimensionality
    :type number_responses: ``_ctypes.c_uint``

    :return: True on success. False otherwise
    :rtype: ``bool`` (ctype short int)
    """

    # Rake notes
    # There is a copyto since numpy 1.7, however it seems to be only 1% faster and we need to maintain 1.6 anyway
    # There is as_array but it leaks like an elephant (TESTED and confirmed on stackoverflow as known issue, leaks will be on each optimizer iteration that is deadly).
    # So we stick to ugly frombuffer
    try:
      #preventive checks
      assert variables_batch
      assert responses_batch
      assert input_mask_batch
      assert output_mask_batch
      assert batch_size > 0
      assert number_variables > 0
      assert number_responses > 0

      if not null:
        self.__parent._report(LogLevel.WARN, "Evaluation callback: Python stack corruption detected! Results may be unpredictable.")

      buf_responses_batch = _numpy.frombuffer(_ctypes.cast(responses_batch, _ctypes.POINTER(_ctypes.c_double * (batch_size * number_responses))).contents).reshape(batch_size, number_responses)
      buf_output_mask_batch = _numpy.frombuffer(_ctypes.cast(output_mask_batch, _ctypes.POINTER(_ctypes.c_short * (batch_size * number_responses))).contents, dtype=_ctypes.c_short).reshape(batch_size, number_responses)
      buf_variables_batch = _numpy.frombuffer(_ctypes.cast(variables_batch, _ctypes.POINTER(_ctypes.c_double * (batch_size * number_variables))).contents).reshape((batch_size, number_variables))
      buf_input_mask_batch = _numpy.frombuffer(_ctypes.cast(input_mask_batch, _ctypes.POINTER(_ctypes.c_short * (batch_size * number_responses))).contents, dtype=_ctypes.c_short).reshape((batch_size, number_responses))

      problem = self.__parent._GTOptAPI__problem()
      evaluations_map = self.__parent._evaluations_map

      if evaluations_map is None:
        input_mask = buf_input_mask_batch.copy()
      else:
        # expand input mask to the full problem size
        input_mask = _numpy.zeros((batch_size, problem.size_full()), dtype=_ctypes.c_short)
        input_mask[:, evaluations_map] = buf_input_mask_batch[:]

      # use copy of the buf_variables_batch and buf_input_mask_batch for safety
      if self._error_occurred():
        user_mask = _numpy.zeros_like(input_mask)
        user_resp = _numpy.empty_like(user_mask, dtype=float)
        user_resp.fill(_shared._NONE)
      else:
        user_resp, user_mask = problem._evaluate(buf_variables_batch.copy(), input_mask, self.timecheck)

        last_error = getattr(problem, "_last_error", None)
        if last_error:
          setattr(problem, "_last_error", None)
          self._register_exception(last_error)

      maximization_objectives = self.__parent._maximization_objectives
      for i in maximization_objectives:
        if user_mask[:, i].any():
          finite_mask = _numpy.logical_and(~_numpy.isnan(user_resp[:, i]), user_mask[:, i])
          user_resp[finite_mask, i] = -user_resp[finite_mask, i]

      if evaluations_map is None:
        buf_responses_batch[:] = user_resp
        buf_output_mask_batch[:] = user_mask
      else:
        buf_responses_batch[:] = user_resp[:, evaluations_map]
        buf_output_mask_batch[:] = user_mask[:, evaluations_map]

      #It may slightly break the brain down into million pieces but rows here will be columns in Eigen.
      return True
    except:
      self._register_exception(_sys.exc_info())

    return False

def _safe_nanmax_by_rows(matrix):
  any_valid = ~_numpy.isnan(matrix).all(axis=1)
  if any_valid.all():
    return _numpy.nanmax(matrix, axis=1)

  matrix_max = _numpy.empty((len(matrix),))
  matrix_max.fill(_numpy.nan)
  if any_valid.any():
    matrix_max[any_valid] = _numpy.nanmax(matrix[any_valid])
  matrix_max[_shared._find_holes(matrix).all(axis=1)] = _shared._NONE

  return matrix_max
