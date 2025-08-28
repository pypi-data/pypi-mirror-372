#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
gtopt.Optimizer - Python Optimization interface
------------------------------------------------

.. currentmodule:: da.p7core.gtopt.optimizer

"""

import sys as _sys
import weakref as _weakref
import contextlib as _contextlib

import numpy as _numpy

from .. import shared as _shared
from .. import status as _status
from .. import exceptions as _ex
from .. import options as _options
from .. import license as _license
from .. import six as _six

from ..utils import designs as _designs
from ..loggers import LogLevel

from . import problem as _problem
from . import diagnostic as _diagnostic
from . import api as _api

class ValidationResult(object):
  """Validation result and details. An object of this class is only returned by
  :meth:`~da.p7core.gtopt.Solver.validate()` and should never be instantiated by user.
  """
  def __init__(self, status, details):
    if not _shared.is_iterable(details):
      raise TypeError('Wrong c-tor argument type %s! Iterable is required' % (type(details).__name__,))
    for i, rec in enumerate(details):
      _shared.check_type(rec, 'c-tor argument details[%d]' % i, _diagnostic.DiagnosticRecord)

    if isinstance(status, Exception):
      object.__setattr__(self, 'status', False)
    else:
      _shared.check_type(status, 'c-tor argument', _status.Status)
      object.__setattr__(self, 'status', (status in (_status.SUCCESS, _status.IMPROVED,)))

    object.__setattr__(self, 'details', [_ for _ in details if _.severity != _diagnostic.DIAGNOSTIC_MISC])

    for misc_payload in details:
      if misc_payload.severity == _diagnostic.DIAGNOSTIC_MISC:
        try:
          misc_payload = _shared.parse_json(misc_payload.message)
          for key in misc_payload:
            object.__setattr__(self, key, misc_payload[key])
        except:
          pass

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')

  def __nonzero__(self):
    return self.status

  def __bool__(self):
    return self.status

  def __str__(self):
    stream = _six.StringIO()
    stream.write('Optimization problem validation result:\nStatus: ' + ("SUCCESS" if self.status else "ERROR"))
    if self.details:
      stream.write('\nStatus details:')
      for note in self.details:
        stream.write('\n  [%s] %s' % (note.severity, note.message))
    result = stream.getvalue()
    stream.close()
    return result

class Solver(object):
  """Optimizer interface."""

  def __init__(self):
    self.__logger  = None
    self.__watcher = None
    self.__impl = _api.GTOptAPI()
    self.__impl.request_license()
    self.__invalid_category_mark = object() # special mark for invalid combination of categorical variables in an initial sample

  def set_logger(self, logger):
    """Set logger.

    :param logger: logger object
    :return: ``None``

    Used to set up a logger for the optimization process. See section :ref:`gen_loggers` for details.
    """
    self.__logger = _shared.wrap_with_exc_handler(logger, _ex.LoggerException)

  def _get_logger(self):
    return self.__logger

  def set_watcher(self, watcher):
    """Set watcher.

    :param watcher: watcher object
    :return: ``None``

    Used to set up a watcher that can interrupt or monitor the optimization process.
    See section :ref:`gen_watchers` for details and the :ref:`example_intermediate_result` example for usage.
    """
    self._set_watcher(_shared.wrap_with_exc_handler(watcher, _ex.WatcherException))

  def _set_watcher(self, watcher):
    old_watcher = self.__watcher
    self.__watcher = watcher
    return old_watcher

  def _get_watcher(self):
    return self.__watcher

  @property
  def options(self):
    """Optimizer options.

    :type: :class:`~da.p7core.Options`

    General options interface for the optimizer. See section :ref:`gen_options` for usage and the :ref:`GTOpt option reference <ug_gtopt_options>`.

    """
    return _options.Options(self.__impl.get_options_manager(), self.__impl)

  @property
  def license(self):
    """Optimizer license.

    :type: :class:`~da.p7core.License`

    General license information interface. See section :ref:`gen_license_usage` for details.

    """
    return _license.License(self.__impl.get_license_manager(), self.__impl)

  def _solve_nevergrad(self, problem, options=None, sample_x=None, sample_f=None, sample_c=None, **kwargs):
    saved_options = self.options.values
    try:
      from .nevergrad_wrapper import solve as ng_solve

      if options is not None:
        _shared.check_concept_dict(options, 'options')
        self.options.set(options)

      return ng_solve(self, problem, sample_x, sample_f, sample_c)
    finally:
      self.options.set(saved_options)

  def _validate_nevergrad(self, problem, options=None, sample_x=None, sample_f=None, sample_c=None, **kwargs):
    saved_options = self.options.values
    try:
      from .nevergrad_wrapper import validate as ng_validate

      if options is not None:
        _shared.check_concept_dict(options, 'options')
        self.options.set(options)

      return ng_validate(self, problem, sample_x, sample_f, sample_c)
    except Exception:
      e = _sys.exc_info()[1]
      return ValidationResult(e, [_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_ERROR, str(e))])
    finally:
      self.options.set(saved_options)

  def solve(self, problem, **kwargs):
    """Solve an optimization problem.

    :param problem: optimization problem
    :keyword options: solver options; not required, overrides the options set through the :attr:`~da.p7core.gtopt.Solver.options` interface
    :type options: ``dict``
    :keyword sample_x: optional initial sample containing values of variables (*added in 2.0 Release Candidate 1*)
    :type sample_x: :term:`array-like`, 1D or 2D
    :keyword sample_f: optional initial sample of objective function values, requires :arg:`sample_x` (*added in 2.0 Release Candidate 1*)
    :type sample_f: :term:`array-like`, 1D or 2D
    :keyword sample_c: optional initial sample of constraint function values, requires :arg:`sample_x` (*added in 2.0 Release Candidate 1*)
    :type sample_c: :term:`array-like`, 1D or 2D
    :keyword compatibility: produces old style results (*added in 6.14*)
    :type compatibility: ``bool``
    :return: solution
    :rtype: :class:`.gtopt.Result` by default, or :class:`.p7core.Result` if :arg:`compatibility` is ``False``

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

    *Changed in version 2.0 Release Candidate 1:* added the initial sample support (:arg:`sample_x`, :arg:`sample_f`, :arg:`sample_c`).

    The :arg:`problem` should be an instance of a user problem class inherited from
    :class:`~da.p7core.gtopt.ProblemGeneric` or one of its descendants (simplified classes :class:`~da.p7core.gtopt.ProblemConstrained`,
    :class:`~da.p7core.gtopt.ProblemUnconstrained`, :class:`~da.p7core.gtopt.ProblemCSP`, or :class:`~da.p7core.gtopt.ProblemMeanVariance`).
    See the :class:`~da.p7core.gtopt.ProblemGeneric` class documentation for details on how to define an optimization problem.

    Validate your problem with :meth:`~da.p7core.gtopt.Solver.validate()` before solving
    to avoid errors caused by incorrect problem definition.

    Alternatively to using the :attr:`~da.p7core.gtopt.Solver.options` interface, solver options may be specified in
    :meth:`~da.p7core.gtopt.Solver.solve()` as the :arg:`options` argument, which is a dictionary with option names as keys, for example::

      solver.solve(my_problem, options={"GTOpt/LogLevel": "Debug"})

    If :arg:`options` contain an option previously set through the :attr:`~da.p7core.gtopt.Solver.options` interface, then the value from
    :arg:`options` overrides the one stored in solver configuration, but does not replace it (that is, the :arg:`options` argument has higher
    priority, but it works only in the :meth:`~da.p7core.gtopt.Solver.solve()` scope).

    Since version 2.0 Release Candidate 1, GTOpt supports initial sample given as :arg:`sample_x`, :arg:`sample_f`, and :arg:`sample_c` arguments. If only :arg:`sample_x`
    is specified, it may be considered as an extended initial guess for variables --- the solver always evaluates points from :arg:`sample_x` (the initial guess point, if it was specified when adding variables, is also evaluated). If :arg:`sample_f` and/or :arg:`sample_c` is specified in addition to :arg:`sample_x`, the solver does not call
    :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()` for these points, but takes objective and/or constraint function values from the
    respective samples. Naturally, specifying either of :arg:`sample_f`, :arg:`sample_c` requires :arg:`sample_x`, and all samples have to be of the
    same size. 1D samples are supported as a simplified form for the case of 1D input and/or response.

    .. versionchanged:: 6.16.3
       invalid values of discrete or integer variables in :arg:`sample_x` now cause :exc:`~da.p7core.InvalidProblemError`

    Note that if the problem defines discrete or integer variables,
    :arg:`sample_x` must contain only valid values of such variables.
    For a discrete variable, each its value in :arg:`sample_x` must match one of the level values
    specified by the :arg:`bounds` argument to :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`.
    For integer variables, all their values in :arg:`sample_x` must be integers.
    Otherwise, :meth:`~da.p7core.gtopt.Solver.solve()` raises an :exc:`~da.p7core.InvalidProblemError` exception.
    """
    with _shared.sigint_watcher(self):
      with _shared._suppress_history(problem=problem):
        configuration = self._read_limited_evaluations_configuration(options=kwargs.get("options"))
        with _problem._limited_evaluations(problem=problem, watcher_ref=self._get_watcher, configuration=configuration) as problem:
          return self._run_solver(problem, _api.GTOPT_SOLVE, **kwargs)

  def validate(self, problem, **kwargs):
    """Validate an optimization problem definition.

    :param problem: optimization problem
    :keyword options: solver options
    :type options: ``dict``
    :keyword sample_x: optional initial sample of variables
    :type sample_x: :term:`array-like`, 1D or 2D
    :keyword sample_f: optional initial sample of objectives
    :type sample_f: :term:`array-like`, 1D or 2D
    :keyword sample_c: optional initial sample of constraints
    :type sample_c: :term:`array-like`, 1D or 2D
    :keyword compatibility: unused, recognized for compatibility with :meth:`~da.p7core.gtopt.Solver.solve()`
    :type compatibility: ``bool``
    :return: validation outcome
    :rtype: :class:`.gtopt.ValidationResult`

    .. versionadded:: 6.33

    Validates your :arg:`problem` definition and returns
    a :class:`~da.p7core.gtopt.ValidationResult` object providing general validation status
    (:attr:`~da.p7core.gtopt.ValidationResult.status`, ``True`` if validation passed, ``False`` otherwise)
    and details, if any (:attr:`~da.p7core.gtopt.ValidationResult.details`).

    Test your problem before running :meth:`~da.p7core.gtopt.Solver.solve()`
    to avoid errors caused by incorrect problem definition.
    When calling :meth:`~da.p7core.gtopt.Solver.validate()`, pass the same arguments
    as you would pass to :meth:`~da.p7core.gtopt.Solver.solve()`,
    including option settings and initial samples.
    All :meth:`~da.p7core.gtopt.Solver.validate()` parameters
    have the same meaning as :meth:`~da.p7core.gtopt.Solver.solve()` parameters.
    """
    logger = self.__logger
    try:
      # mute solver for a validation time, keep watcher - validation may take a long time
      self.__logger = None
      status, diagnostics = self._run_solver(problem, _api.GTOPT_VALIDATE, **kwargs)
      return ValidationResult(status, diagnostics)
    except Exception:
      e = _sys.exc_info()[1]
      return ValidationResult(e, [_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_ERROR, str(e))])
    finally:
      self.__logger = logger

  def _run_solver(self, problem, mode, **kwargs):

    if not isinstance(problem, _problem.ProblemGeneric):
      raise ValueError("Wrong type of problem provided ('%s')!" % type(problem).__name__)

    problem.setup_additional_options(self.options)
    problem._validate()

    sample_x, sample_f, sample_c, sample_nf, sample_nc = None, None, None, None, None

    options = None
    compatibility = True
    recognized = ["enableIntermediate", "options", "sample_x", "sample_f", "sample_c", "sample_nf", "sample_nc", "compatibility"]
    for k, v in kwargs.items():
      if k not in recognized:
        raise TypeError(("Keyword argument '%s' is not recognized!\nAvailable flags are:\n'" + "', '".join(recognized)  + "'") % k)

      if k == recognized[0]:
        self._log(LogLevel.WARN, "Option 'enableIntermediate' is deprecated")
        _shared.check_type(v, recognized[0], bool)
      elif k == recognized[1]:
        _shared.check_concept_dict(v, recognized[1])
        options = v
      elif k == recognized[2]:
        sample_x = self._read_nonempty_matrix(v, problem.size_x(), False, sample_x, name="Initial sample containing values of variables ('sample_x' argument)")
      elif k == recognized[3]:
        sample_f = self._read_nonempty_matrix(_designs._preprocess_initial_objectives(problem, v), problem.size_f(), True, sample_f,
                                              name="Initial sample of objective function values ('sample_f' argument)")
      elif k == recognized[4]:
        sample_c = self._read_nonempty_matrix(v, problem.size_c(), True, sample_c, name="Initial sample of constraint function values ('sample_c' argument)")
      elif k == recognized[5]:
        sample_nf = v # temporary will do read later
      elif k == recognized[6]:
        sample_nc = v
      elif k == recognized[7]:
        _shared.check_type(v, recognized[7], bool)
        compatibility = v

    if sample_x is not None and _shared.isNanInf(sample_x):
      raise _ex.NanInfError('Incorrect (NaN or Inf) value is found in the initial guesses inputs!')
    self._check_required_sample(sample_f, sample_x, "sample_f", "sample_x")
    self._check_required_sample(sample_c, sample_x, "sample_c", "sample_x")

    saved_options = self.options.values
    solution_snapshot_watcher = None
    original_watcher = None
    try:
      if options is not None:
        _shared.check_concept_dict(options, 'options')
        self.options.set(options)
      local_options = self.options.values

      problem._validate_linear_responses(sample_x, sample_f, sample_c)

      solution_snapshot_watcher = self._create_snapshot_watcher(problem=problem, mode=mode)
      original_watcher = self._set_watcher(solution_snapshot_watcher.watcher)

      subproblems_result = []
      subproblems_name = []
      subproblems_spec = []

      size_f = problem.size_f()
      validation_mode = mode in (_api.GTOPT_VALIDATE, _api.GTOPT_VALIDATE_DOE)
      doe_mode = mode in (_api.GTOPT_DOE, _api.GTOPT_VALIDATE_DOE)
      complete_designs, expose_analytic_cache = [], False if validation_mode else _shared.parse_bool(self.options.get('/GTOpt/ExposeAnalyticCache'))
      catvars = self._read_categorical_combinations(problem)

      if catvars:
        if compatibility and (problem.size_nf() or problem.size_nc()):
          raise _ex.FeatureNotAvailableError("The problem with categorical variables and blackbox tolerances does not support the old result format. Please, consider using `compatibility=False` argument.")
        if problem.size_s():
          raise _ex.FeatureNotAvailableError("The problem with categorical variables does not support robust optimization problems.")
        if isinstance(problem, (_problem.ProblemMeanVariance, _problem.ProblemFitting)):
          raise _ex.FeatureNotAvailableError('The problem with categorical variables does not support "mean-variance" and "data fitting" problems.')

      self.__impl.set_callbacks(self.__logger, solution_snapshot_watcher.watcher)

      # Note we replace sample_x with rounded data to avoid incoherence if some initial points are a solution
      # Intentionally ignore invalid points, solver can handle it
      sample_x, invalid_initial_points = problem._valid_input_points(sample_x, sample_f=sample_f, sample_c=sample_c, return_invalid=True)
      invalid_initial_sample = None

      alternative_solver = None
      if self._test_categorical_only_problem(problem, doe_mode):
        alternative_solver = self._build_full_factorial
      elif self._is_alternative_csp(problem, mode, sample_c):
        alternative_solver = self._solve_alternative_csp

      if alternative_solver is not None:
        solution_snapshot_watcher.initial_sample(sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, sample_nf=sample_nf, sample_nc=sample_nc)
        with _shared._suppress_history(problem):
          result = alternative_solver(problem=problem, mode=mode, sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, compatibility=compatibility)
          if expose_analytic_cache:
            complete_designs = self._expose_analytic_cache(problem)
        solution_snapshot_watcher.report_final_result(result=result, sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, sample_nf=sample_nf, sample_nc=sample_nc)
        if expose_analytic_cache:
          problem._complete_designs = complete_designs
        return result

      for subproblem_name, vars_hints, resp_hints, subsample_x, subsample_f, subsample_c, subsample_nf, subsample_nc in self._enumerate_categorical_combinations(problem, mode, invalid_initial_points, sample_x, sample_f, sample_c, sample_nf, sample_nc):
        solution_snapshot_watcher.initial_sample(sample_x=subsample_x, sample_f=subsample_f, sample_c=subsample_c, sample_nf=subsample_nf, sample_nc=subsample_nc)

        if subproblem_name is self.__invalid_category_mark:
          # this is a very special case: subsample_* are points with invalid combination of categorical variables. We must append these points to the final result.
          invalid_initial_sample = dict((field_name, field_data) for field_data, field_name in ((subsample_x, "x"), (subsample_f, "f"), (subsample_c, "c"), (subsample_nf, "nf"), (subsample_nc, "nc")) if field_data is not None)
          solution_snapshot_watcher.commit_subproblem(None)
          continue

        try:
          subproblems_name.append(subproblem_name)
          # We must temporary limit history by current category
          with _shared._suppress_history(problem): # we must keep history within single
            with problem._solve_as_subproblem(vars_hints, (resp_hints[:size_f] if resp_hints else None), (resp_hints[size_f:] if resp_hints else None), doe_mode=doe_mode):
              updated_resp_hints = self._preprocess_linear_response(problem, mode, subsample_x, subsample_f, subsample_c)
              if validation_mode:
                linear_response_diagnostics, updated_resp_hints = updated_resp_hints, None
              with problem._solve_as_subproblem(None, (updated_resp_hints[:size_f] if updated_resp_hints else None), (updated_resp_hints[size_f:] if updated_resp_hints else None), doe_mode=doe_mode):
                subproblems_spec.append(dict((var_index, problem.elements_hint(var_index, "@GT/FixedValue")) for var_index, _ in catvars) if catvars else {})

                with self._analyze_satellite_objectives(mode=mode, problem=problem, sample_f=subsample_f) as objectives_postprocessor:
                  size_df, size_dc = self.__impl.setup_problem(problem=problem, postprocess_satellite_objective=objectives_postprocessor) # read problem data into the backend GTOptSolverImpl object, held by the self.__impl

                subsample_nf = self._read_nonempty_matrix(subsample_nf, size_df, True, name="Initial sample of objective function value noise ('sample_nf' argument)")
                subsample_nc = self._read_nonempty_matrix(subsample_nc, size_dc, True, name="Initial sample of constraint function value noise  ('sample_nc' argument)")
                self._check_required_sample(subsample_nf, subsample_x, "sample_nf", "sample_x")
                self._check_required_sample(subsample_nc, subsample_x, "sample_nc", "sample_x")

                problem._complete_designs = None

                last_error = None
                with self._postprocess_intermediate_result(problem=problem, mode=mode, subproblems_result=subproblems_result, compatibility=compatibility):
                  try:
                    self.__impl.execute(mode, subsample_x, subsample_f, subsample_c, subsample_nf, subsample_nc, compatibility)
                  except:
                    if _shared._desktop_mode():
                      raise
                    last_error = _sys.exc_info()

                if validation_mode:
                  subproblem_diagnostics = self.__impl.get_status(), self.__impl.get_diagnostics()
                  if linear_response_diagnostics:
                      subproblem_diagnostics = self._combine_validation((subproblem_name, subproblem_name), (subproblems_spec, subproblems_spec), 
                                                                        (subproblem_diagnostics, linear_response_diagnostics))
                  subproblems_result.append(subproblem_diagnostics)
                else:
                  problem._refill_analytical_history()
                  initial_sample = self.__impl.collect_initial_sample(subsample_x, subsample_f, subsample_c, subsample_nf, subsample_nc, mode=mode)

                  if expose_analytic_cache:
                    complete_designs.append(self._expose_analytic_cache(problem))

                  try:
                    subproblems_result.append(self.__impl.get_results(initial_sample=initial_sample, c_tol=float(self.options._get("GTOpt/ConstraintsTolerance"))))
                  except:
                    if not last_error:
                      raise
                    _shared.reraise(*last_error) # this is the original reason

                  with self._lazy_intermediate_result_callback(problem=problem, mode=mode, subproblems_result=subproblems_result, compatibility=compatibility) as intermediate_result_callback:
                    if not self.__impl._test_terminate(intermediate_result_callback):
                      break

                  # we must commit the last solution AFTER _test_terminate,
                  # otherwise we have an unreliable duplicates in a snapshot
                  solution_snapshot_watcher.commit_subproblem(subproblems_result[-1])
                
                if last_error:
                  if not validation_mode and not len(getattr(problem, "_history_cache", [])):
                    # No evaluations performed, it's legit to discard the result in case of error
                    subproblems_result = subproblems_result[:-1] 
                  _shared.reraise(*last_error)
        except:
          if not subproblems_result or _shared._desktop_mode():
            # No result or Desktop DSE compatibility mode
            raise
          exception_report = ''.join(_shared._format_user_only_exception(*_sys.exc_info()))
          if not subproblem_name or (subproblem_name is self.__invalid_category_mark):
            subproblem_title = ""
          elif subproblem_name:
            subproblem_title = " Cannot proceed {}.".format(subproblem_name)
          self._log(LogLevel.ERROR, "{} stopped due to an error.{} {}".format(("DoE" if doe_mode else "Optimization"), 
                                                                              subproblem_title, exception_report))
        finally:
          self.__impl.reset(restart=True) # restart after use
          self.options.set(local_options) # we must re-assign options after restart

      if validation_mode:
        return self._combine_validation(subproblems_name, subproblems_spec, subproblems_result)

      if expose_analytic_cache:
        problem._complete_designs = _numpy.vstack(complete_designs) #for platform

      result = self._combine_legacy_results(problem, mode, subproblems_result) if compatibility else \
                self._combine_solutions(problem, mode, subproblems_result, invalid_initial_sample=invalid_initial_sample)

      solution_snapshot_watcher.report_final_result(result=result, sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, sample_nf=sample_nf, sample_nc=sample_nc)
      return result
    finally:
      self.__impl.reset()
      if solution_snapshot_watcher:
        solution_snapshot_watcher.reset()
        self._set_watcher(original_watcher)
      self.options.set(saved_options)

  @_contextlib.contextmanager
  def _analyze_satellite_objectives(self, mode, problem, sample_f):
    if mode in (_api.GTOPT_SOLVE, _api.GTOPT_VALIDATE):
      yield None
      return

    maximum_iterations = int(self.options.get("GTOpt/MaximumIterations"))
    maximum_expensive_iterations = int(self.options.get("GTOpt/MaximumExpensiveIterations"))
    evaluation_scalability = int(self.options.get("GTOpt/ResponsesScalability"))

    hint_linear_parameters_vector = problem._normalize_option_name("@GTOpt/LinearParameterVector")
    hint_evaluation_cost_type = problem._normalize_option_name("@GTOpt/EvaluationCostType")
    hint_expensive_evaluations = problem._normalize_option_name("@GT/ExpensiveEvaluations")
    hint_evaluation_limit = problem._normalize_option_name("@GT/EvaluationLimit")

    satellite_evaluations = []

    def proceed(obj_index, obj_hints):
      if obj_hints.get(hint_linear_parameters_vector):
        # reconstructed linear response, no limits
        return


      evaluations_limit = int(_shared.parse_float_auto(obj_hints.get(hint_evaluation_limit, -1), -1))
      deprecated_evaluations_limit = int(_shared.parse_float_auto(obj_hints.get(hint_expensive_evaluations, -1), -1))
      expensive_objective = str(obj_hints.get(hint_evaluation_cost_type, "cheap")).lower() == "expensive"

      if deprecated_evaluations_limit >= 0:
        # c++ code emits warning here:
        self._log(LogLevel.WARN, "The %s hint is deprecated and will be removed in future versions. Use %s instead." % (hint_expensive_evaluations, hint_evaluation_limit))
        if evaluations_limit < 0:
          if expensive_objective:
            evaluations_limit = deprecated_evaluations_limit
        elif evaluations_limit != deprecated_evaluations_limit:
          raise _ex.InvalidOptionsError("The %s and %s hints are set to different values: %d != %d."
                                        % (hint_evaluation_limit, hint_expensive_evaluations,
                                            evaluations_limit, deprecated_evaluations_limit))
      if evaluations_limit < 0:
        if maximum_expensive_iterations and expensive_objective:
          evaluations_limit = maximum_expensive_iterations # use expensive default, increment by the number of holes in the initial sample, if any
          if sample_f is not None:
            # maximum_expensive_iterations excludes evaluations of the initial sample, round it up to evaluations scalability
            evaluations_limit += (_numpy.count_nonzero(_shared._find_holes(sample_f[:, obj_index])) + evaluation_scalability - 1) // evaluation_scalability * evaluation_scalability
        elif maximum_iterations:
          evaluations_limit = maximum_iterations # use general default

      if evaluations_limit > 0:
        satellite_evaluations.append(evaluations_limit)

    yield proceed

    self.options.set("/GTOpt/MaximumExternalIterations", (0 if not satellite_evaluations else max(satellite_evaluations)))

  def _expose_analytic_cache(self, problem):
    input_size = problem.size_x() + problem.size_s()

    def _wipe_payloads(dataset, dup_rows_indices):
      for k in problem._payload_objectives:
        dataset[:, (input_size + k)][dup_rows_indices] = _shared._NONE

    if problem._history_cache:
      try:
        wipe_payloads = _wipe_payloads if problem._payload_objectives else None
      except:
        wipe_payloads = None

      try:
        designs = _numpy.vstack(problem._history_cache)
        designs = _designs._fill_gaps_and_keep_dups(designs, slice(input_size), wipe_payloads) # fill holes in history, remove payloads if any
        designs = _designs._select_unique_rows(designs, 0) # remove dups
        problem._refill_analytical_history(designs)
        self.__impl.read_backend_reconstructed_responses(designs)
        # We must convert the marker if there are any holes left because 6.x expects -NaN as the hole marker.
        designs[_shared._find_holes(designs)] = _numpy.copysign(_numpy.nan, -1.)
        return designs
      except:
        pass
    return _numpy.empty((0, input_size + problem.size_full())) # no data, right shape

  def _combine_validation(self, subproblems_name, subproblems_spec, subproblems_result):
    status, diagnostics, misc_payload = None, [], {}
    for subproblem_name, subproblem_spec, (subproblem_status, subproblem_diagnostics) in zip(subproblems_name, subproblems_spec, subproblems_result):
      if status is None or _status._select_status(subproblem_status, status):
        status = subproblem_status

      for current_diagnostics in subproblem_diagnostics:
        if current_diagnostics.severity == _diagnostic.DIAGNOSTIC_MISC:
          current_diagnostics = _shared.parse_json_deep(current_diagnostics.message, dict)
          if "_details" in current_diagnostics and "_subproblems" not in current_diagnostics:
            local_details = dict(current_diagnostics.get("_details", {}))
            local_details["CategoricalSignature"] = subproblem_spec
            local_details["CategoricalName"] = subproblem_name or ""
            current_diagnostics["_subproblems"] = [local_details] # make a shallow copy
          _recursive_update_diagnostics(misc_payload, current_diagnostics)
        elif subproblem_name:
          diagnostics.append(_diagnostic.DiagnosticRecord(current_diagnostics.severity, subproblem_name + ": " + current_diagnostics.message))
        else:
          diagnostics.append(current_diagnostics)

    if misc_payload:
      diagnostics.append(_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_MISC, _shared.write_json(misc_payload)))

    return (status or _status.SUCCESS), diagnostics

  def _combine_solutions(self, problem, mode, subproblems_result, invalid_initial_sample, intermediate_result=False):
    from .. import result as _result

    assert mode in (_api.GTOPT_SOLVE, _api.GTOPT_DOE)

    def _update_fields(fields_map, total_width, new_fields_map):
      for field_name in sorted(new_fields_map, key=new_fields_map.get):
        if field_name not in fields_map:
          field_start, field_end, field_step = new_fields_map[field_name].indices(n_columns)
          field_width = (field_end - field_start + field_step - 1) // field_step
          fields_map[field_name] = slice(total_width, total_width + field_width)
          total_width += field_width
      return fields_map, total_width

    def _write_solutions_data(destination_data, destination_fields, source_data, source_fields):
      source_length = len(source_data)
      if not source_length:
        return 0
      for field_name in destination_fields:
        if field_name in source_fields: # copy non-empty data
          destination_data[:source_length, destination_fields[field_name]] = source_data[:, source_fields[field_name]]
      return source_length

    if len(subproblems_result) == 1 and not invalid_initial_sample:
      sift_logger = None if intermediate_result else _shared.Logger(logger=self.__logger, log_level_string=self.options._get('GTOpt/LogLevel').lower())
      # None means "do nothing" and this is what we are going to do in case of single enumerator class
      return subproblems_result[0]._finalize(problem=problem, auto_objective_type=(None if mode == _api.GTOPT_SOLVE else "Adaptive"),
                                             options=self.options.values, logger=sift_logger, intermediate_result=intermediate_result)

    # collect joined fields and subsets spec
    total_points, total_width, fields_map, subsets_list = 0, 0, {}, []
    for result in subproblems_result:
      n_points, n_columns = result._solutions_data.shape
      total_points += n_points

      # update fields list
      fields_map, total_width = _update_fields(fields_map, total_width, result._fields)

      # update slices for each result
      auto_start, auto_end, _ = result._solutions_subsets.get("auto", slice(0,0)).indices(n_points)
      initial_start, initial_end, _ = result._solutions_subsets.get("initial", slice(0,0)).indices(n_points)

      if auto_start <= initial_end:
        slice_initial_only = slice(initial_start, min(initial_end, auto_start))
        slice_overlapped = slice(auto_start, initial_end)
      else:
        slice_initial_only = slice(max(auto_end, initial_start), initial_end)
        slice_overlapped = slice(initial_start, auto_end)

      subsets_list.append((slice_initial_only, slice_overlapped, result._solutions_subsets.get("new", slice(0,0))))

    if invalid_initial_sample:
      designs = _designs._preprocess_initial_sample(problem=problem, sample_x=invalid_initial_sample["x"],
                                                    sample_f=invalid_initial_sample.get("f"), sample_c=invalid_initial_sample.get("c"),
                                                    sample_nf=invalid_initial_sample.get("nf"), sample_nc=invalid_initial_sample.get("nc"))
      designs = _designs._postprocess_designs(problem, designs, len(designs), float(self.options.get("GTOpt/ConstraintsTolerance")))
      if designs is not None and mode == _api.GTOPT_DOE:
        total_points += len(designs[0])
        fields_map, total_width = _update_fields(fields_map, total_width, dict((k, designs[1][2][k]) for k in designs[1][0]))
    else:
      designs = None

    # collect final solutions data
    subsets_slices, block_last, solutions_data = [], 0, _shared._filled_array((total_points, total_width), _shared._NONE)

    if designs is not None and mode == _api.GTOPT_DOE:
      block_last += _write_solutions_data(solutions_data[block_last:], fields_map, designs[0], designs[1][2])

    for points_slices in zip(*subsets_list): # for each kind of vertical slices (initial only, overlapped, new only)
      for points_slice, result in zip(points_slices, subproblems_result): # for each result and vertical slice
        block_last += _write_solutions_data(solutions_data[block_last:], fields_map, result._solutions_data[points_slice, :], result._fields)
      subsets_slices.append(block_last) # accumulate total heights of vertical slices

    if mode == _api.GTOPT_SOLVE:
      # Note we can ignore constraints satisfaction problems
      pareto_optimal_objectives = [(i, k) for i, k in enumerate(_result._read_objectives_type(problem, "minimize")) if k in ("minimize", "maximize")]
      target_objective = solutions_data[:, fields_map.get("f", slice(0))]
      if pareto_optimal_objectives and target_objective.size:
        if len(pareto_optimal_objectives) != problem.size_f() or any((i != j or target != "minimize") for j, (i, target) in enumerate(pareto_optimal_objectives)):
          target_objective = _numpy.hstack([_result._optional_negative_numbers(target_objective[:, i], (target == "maximize")).reshape(-1, 1) for i, target in pareto_optimal_objectives])

        solutions_type = _result.solution_filter(x=solutions_data[:, fields_map.get("x", slice(0))],
                                          f=target_objective, c=solutions_data[:, fields_map.get("c", slice(0))],
                                          c_bounds=problem.constraints_bounds(), df=solutions_data[:, fields_map.get("nf", slice(0))],
                                          dc=solutions_data[:, fields_map.get("nc", slice(0))], options=self.options.values)
        if "flag" in fields_map:
          solutions_data[:, fields_map["flag"]][:, 0] = solutions_type[:]

        discarded_points = solutions_type == _result.GT_SOLUTION_TYPE_DISCARDED
        if discarded_points.any():
          solutions_data = solutions_data[~discarded_points]
          subsets_slices = [(k - _numpy.count_nonzero(discarded_points[:k])) for k in subsets_slices]

    # finalize subset slices
    solutions_subsets = {"initial": slice(0, subsets_slices[1]), # starts from the beginning and ended after overlapped block
                         "auto": slice(subsets_slices[0], subsets_slices[2]), # start after "initial only" and finished after "new"
                         "new": slice(subsets_slices[1], subsets_slices[2]), # starts from the end of overlapped  and finished after "new"
                         }

    # update diagnostics, info and status
    status = subproblems_result[0].status
    info = subproblems_result[0].info # note subproblems_result[0].info is dict
    diagnostics = subproblems_result[0].info.get("Diagnostics", [])

    for result in subproblems_result:
      # combine designs
      designs = _designs._combine_designs(problem, designs, (result._designs_data, result._designs_fields, result._designs_samples))

      # update diagnostics
      for diag_record in result.info.get("Diagnostics", []):
        if diag_record not in diagnostics:
          diagnostics.append(diag_record)

      if _status._select_status(result.status, status):
        status = result.status
        info = result.info # @todo : check it out and do something special

    info = dict(info)
    info.pop("Diagnostics", None)
    result = _result.Result(status=status, info=info, solutions=solutions_data, fields=fields_map,
                            problem=_weakref.ref(problem), diagnostics=diagnostics, designs=designs,
                            solutions_subsets=solutions_subsets, finalize=False)

    sift_logger = None if intermediate_result else _shared.Logger(logger=self.__logger, log_level_string=self.options._get('GTOpt/LogLevel').lower())
    return result._finalize(problem=problem, auto_objective_type=(None if mode == _api.GTOPT_SOLVE else "Adaptive"),
                            options=self.options.values, logger=sift_logger, intermediate_result=intermediate_result)

  @staticmethod
  def _find_points(global_data, search_keys):
    dst_keys = _shared._make_dataset_keys(global_data)
    src_keys = _shared._make_dataset_keys(search_keys)

    dst_order = _shared._lexsort(dst_keys)
    src_order = _shared._lexsort(src_keys)

    global_indices, search_indices = [], []

    while len(dst_order) and len(src_order):
      d_key, s_key = dst_keys[dst_order[0]], src_keys[src_order[0]]
      i = _numpy.where(d_key != s_key)[0]
      if not len(i):
        global_indices.append(dst_order[0])
        search_indices.append(src_order[0])

        # global_data may contain dups but search_keys must be unique because it's solution, so proceed both
        dst_order = dst_order[1:]
        src_order = src_order[1:]
      elif d_key[i[-1]] < s_key[i[-1]]:
        dst_order = dst_order[1:] # destination key is less, step destination (not lexsort uses inverse columns order)
      else:
        src_order = src_order[1:] # source key is less, step source

    return global_indices, search_indices

  @staticmethod
  def _combine_legacy_solutions(solutions):
    return _api._Solution(x=_optional_vstack([_.x for _ in solutions]),
                          f=_optional_vstack([_.f for _ in solutions]),
                          c=_optional_vstack([_.c for _ in solutions]),
                          v=_optional_vstack([_.v for _ in solutions]),
                          fe=_optional_vstack([_.fe for _ in solutions]),
                          ce=_optional_vstack([_.ce for _ in solutions]),
                          ve=_optional_vstack([_.ve for _ in solutions]),
                          psi=_optional_vstack([_.psi for _ in solutions]),
                          psie=_optional_vstack([_.psie for _ in solutions]))

  def _combine_legacy_results(self, problem, mode, subproblems_result, intermediate_result=False):
    if len(subproblems_result) == 1:
      return subproblems_result[0]

    assert mode in (_api.GTOPT_SOLVE, _api.GTOPT_DOE)

    status = subproblems_result[0].status
    info = subproblems_result[0].info # note subproblems_result[0].info is dict
    diagnostics = subproblems_result[0].diagnostics

    for result in subproblems_result[1:]:
      diagnostics.extend([diag_record for diag_record in result.diagnostics if diag_record not in diagnostics]) # update diagnostics

      if _status._select_status(result.status, status):
        status = result.status
        info = result.info # @todo : check it out and do something special

    def _make_result(optimal_points, converged_points, infeasible_points):
      return _api.Result(info=_shared.write_json(info), status=status, problem_ref=_weakref.ref(problem),
                        optimal_points=optimal_points, converged_points=converged_points,
                        infeasible_points=infeasible_points, diagnostics=diagnostics)

    if not any(len(_.optimal.x) or len(_.infeasible.x) for _ in subproblems_result):
      return _make_result(optimal_points=_api._Solution([], [], [], [], [], [], [], [], []),
                          converged_points=_api._Solution([], [], [], [], [], [], [], [], []),
                          infeasible_points=_api._Solution([], [], [], [], [], [], [], [], []))

    from .. import result as _result

    size_x, size_f, size_c = problem.size_x(), problem.size_f(), problem.size_c()

    def _combine_by_field(field, empty_shape):
      return _optional_vstack([getattr(_.optimal, field) for _ in subproblems_result] + \
                              [getattr(_.infeasible, field) for _ in subproblems_result], \
                                empty_shape=empty_shape)

    solution_x = _combine_by_field("x", empty_shape=(0, size_x))
    solution_f = _combine_by_field("f", empty_shape=(0, size_f))
    solution_c = _combine_by_field("c", empty_shape=(0, size_c))
    solution_v = _combine_by_field("v", empty_shape=(0, size_c))
    solution_fe = _combine_by_field("fe", empty_shape=(0, size_f))
    solution_ce = _combine_by_field("ce", empty_shape=(0, size_c))
    solution_ve = _combine_by_field("ve", empty_shape=(0, size_c))
    solution_psi = _combine_by_field("psi", empty_shape=(0, 1))
    solution_psie = _combine_by_field("psie", empty_shape=(0, 1))

    # Converged points are points from the optimal set with proven local optimality. We can identify and keep these points
    converged_points = _numpy.zeros(len(solution_x), dtype=bool)

    if not intermediate_result:
      current_offset, next_offset = 0, 0

      for subproblem in subproblems_result:
        current_offset, next_offset = next_offset, next_offset + len(subproblem.optimal.x) + len(subproblem.infeasible.x)
        converged_x = subproblem._converged.x
        if len(converged_x): # this implies a non-empty optimal set
          subproblem_x = solution_x[current_offset:next_offset]
          converged_x = _shared.as_matrix(converged_x, shape=(None, solution_x.shape[1]))
          converged_points[current_offset:next_offset] = (subproblem_x[:,_numpy.newaxis,:] == converged_x[_numpy.newaxis,:,:]).all(axis=-1).any(axis=-1)

    problem_objectives_type = _result._read_objectives_type(problem=problem, auto_objective=("minimize" if mode == _api.GTOPT_SOLVE else "adaptive"))
    pareto_optimal_objectives = [(i, k) for i, k in enumerate(problem_objectives_type) if k in ("minimize", "maximize")]
    evaluation_objectives = [] if intermediate_result else [i for i, k in enumerate(problem_objectives_type) if k in ("evaluate",)]

    if not pareto_optimal_objectives and not solution_c.size:
      self._update_target_objectives(problem=problem, target_objectives=evaluation_objectives,
                                     x=solution_x, f=solution_f, c=solution_c, v=solution_v, psi=solution_psi)

      # All points are feasible (because there is no constraints) and optimal
      return _make_result(optimal_points=_api._Solution(x=solution_x, f=solution_f, c=solution_c, v=solution_v,
                                                        fe=solution_fe, ce=solution_ce, ve=solution_ve,
                                                        psi=solution_psi, psie=solution_psie),
                          converged_points=_api._Solution([], [], [], [], [], [], [], [], []),
                          infeasible_points=_api._Solution([], [], [], [], [], [], [], [], []))

    if not pareto_optimal_objectives:
      target_objective = [] # no objectives, feasible points will be marked as "not dominated"
    else:
      # Some of these objectives could have not been evaluated yet
      if not intermediate_result:
        self._update_target_objectives(problem=problem, target_objectives=[i for i, _ in pareto_optimal_objectives],
                                       x=solution_x, f=solution_f, c=solution_c, v=solution_v, psi=solution_psi)

      if len(pareto_optimal_objectives) == size_f and all((i == j and target == "minimize") for j, (i, target) in enumerate(pareto_optimal_objectives)):
        target_objective = solution_f
      else:
        target_objective = _numpy.hstack([_result._optional_negative_numbers(solution_f[:, i], (target == "maximize")).reshape(-1, 1) for i, target in pareto_optimal_objectives])

    solutions_type = _result.solution_filter(solution_x, target_objective, solution_c, problem.constraints_bounds(), [], [], self.options.values)

    converged_points = _numpy.logical_and(converged_points, (solutions_type == _result.GT_SOLUTION_TYPE_NOT_DOMINATED)) # we are combining
    optimal_points = converged_points | (solutions_type == _result.GT_SOLUTION_TYPE_NOT_DOMINATED) | (solutions_type == _result.GT_SOLUTION_TYPE_FEASIBLE_NAN)
    infeasible_points = ~optimal_points

    self._update_target_objectives(problem=problem, target_objectives=evaluation_objectives,
                                    x=solution_x, f=solution_f, c=solution_c, v=solution_v, psi=solution_psi,
                                    discarded_points=(solutions_type == _result.GT_SOLUTION_TYPE_DISCARDED))

    if mode == _api.GTOPT_SOLVE:
      # In optimization mode discard points that are too dominated or too infeasible. Keep these points in DoE mode
      infeasible_points = _numpy.logical_and(infeasible_points, (solutions_type != _result.GT_SOLUTION_TYPE_DISCARDED))

    optimal_set = _api._Solution(x=solution_x[optimal_points], f=solution_f[optimal_points],
                                 c=solution_c[optimal_points], v=solution_v[optimal_points],
                                 fe=solution_fe[optimal_points], ce=solution_ce[optimal_points],
                                 ve=solution_ve[optimal_points], psi=solution_psi[optimal_points],
                                 psie=solution_psie[optimal_points])

    converged_set = _api._Solution(x=solution_x[converged_points], f=solution_f[converged_points],
                                   c=solution_c[converged_points], v=solution_v[converged_points],
                                   fe=solution_fe[converged_points], ce=solution_ce[converged_points],
                                   ve=solution_ve[converged_points], psi=solution_psi[converged_points],
                                   psie=solution_psie[converged_points])

    infeasible_set = _api._Solution(x=solution_x[infeasible_points], f=solution_f[infeasible_points],
                                    c=solution_c[infeasible_points], v=solution_v[infeasible_points],
                                    fe=solution_fe[infeasible_points], ce=solution_ce[infeasible_points],
                                    ve=solution_ve[infeasible_points], psi=solution_psi[infeasible_points],
                                    psie=solution_psie[infeasible_points])

    return _make_result(optimal_points=optimal_set, converged_points=converged_set, infeasible_points=infeasible_set)

  def _update_target_objectives(self, problem, target_objectives, x, f, c, v, psi, discarded_points=None):
    if problem is None or problem.size_s() or not target_objectives or not len(x):
      return

    logger = _shared.Logger(logger=self.__logger, log_level_string=self.options._get('GTOpt/LogLevel').lower())

    try:
      size_f, size_c = problem.size_f(), problem.size_c()

      undefined_objectives = _shared._find_holes(f)

      evaluation_mask_in = _numpy.zeros((len(x), problem.size_full()), dtype=bool)
      evaluation_mask_in[:, target_objectives] = undefined_objectives[:, target_objectives]
      if discarded_points is not None:
        evaluation_mask_in[discarded_points] = False

      if not evaluation_mask_in.any():
        return

      objectives_names = problem.objectives_names()
      logger(LogLevel.INFO, "Evaluating %s..." % (", ".join(objectives_names[i] for i in target_objectives)))

      from ..result import _evaluate_sparse_data

      evaluation_data, evaluation_mask_out = _evaluate_sparse_data(problem, x, evaluation_mask_in, batch_limit=int(self.options.get("GTOpt/BatchSize")))

      # update only undefined responses
      evaluation_mask_out[:, :size_f] = _numpy.logical_and(evaluation_mask_out[:, :size_f], undefined_objectives)
      if evaluation_mask_out[:, :size_f].any():
        f[evaluation_mask_out[:, :size_f]] = evaluation_data[:, :size_f][evaluation_mask_out[:, :size_f]]

      if not c.size:
        return

      constraints_evaluation_mask = evaluation_mask_out[:, size_f:(size_f+size_c)]
      if not constraints_evaluation_mask.any():
        return

      constraints_evaluation_mask = _numpy.logical_and(constraints_evaluation_mask, _shared._find_holes(c))
      if not constraints_evaluation_mask.any():
        return

      c[constraints_evaluation_mask] = evaluation_data[:, size_f:(size_f+size_c)][constraints_evaluation_mask]

      if not v.size and not psi.size:
        return

      v_psi, _ = problem._evaluate_psi(c, float(self.options.get("GTOpt/ConstraintsTolerance")))

      if v.size:
        # intentionally update mask and reuse it later
        constraints_evaluation_mask = _numpy.logical_and(constraints_evaluation_mask, _shared._find_holes(v))
        v[constraints_evaluation_mask] = v_psi[:, :-1][constraints_evaluation_mask]

      if psi.size:
        update_psi_mask = constraints_evaluation_mask.any(axis=1)
        psi[:, 0][update_psi_mask] = v_psi[:, -1][update_psi_mask]
    except:
      # no drama, just emit a warning
      exc_info = _sys.exc_info()
      logger(LogLevel.WARN, "Failed to evaluate objectives function: %s" % (exc_info[1],))

  def _is_alternative_csp(self, problem, mode, sample_c):
    if mode not in (_api.GTOPT_SOLVE, _api.GTOPT_VALIDATE) or sample_c is None:
      return False

    try:
      # there are constraints, but no objective, no stochastic, no initial guess
      if not problem.size_c() \
        or problem.size_s() or  problem.size_nf() or problem.size_nc() \
        or problem.initial_guess() is not None:
        return False

      size_x, size_f = problem.size_x(), problem.size_f()
      for objective_kind in problem.elements_hint(slice(size_x, size_x + size_f), "@GT/ObjectiveType"):
        if not objective_kind or objective_kind.lower() in ("minimize", "maximize"):
          return False

      c_tol = float(self.options._get("GTOpt/ConstraintsTolerance"))
      _, feasibility_code = problem._evaluate_psi(c_values=sample_c, c_tol=c_tol)
      return (feasibility_code == 0).any() # GT_SOLUTION_TYPE_CONVERGED = 0
    except:
      pass
    return False # safe path

  def _solve_alternative_csp(self, problem, mode, sample_x, sample_f, sample_c, compatibility):
    warn_message = "The initial sample contains at least one feasible point. No further exploration is needed."
    diagnostics = [_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_WARNING, warn_message)]

    if mode in (_api.GTOPT_VALIDATE, _api.GTOPT_VALIDATE_DOE):
      return _status.SUCCESS, diagnostics

    designs_table = _designs._preprocess_initial_sample(problem=problem, sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, sample_nf=None, sample_nc=None)
    return self._make_alternative_result(problem=problem, designs_table=designs_table, n_initial=len(designs_table),
                                         compatibility=compatibility, diagnostics=diagnostics)

  @staticmethod
  def _read_categorical_combinations(problem):
    categorical_variables = []
    variables_type = problem.elements_hint(slice(0, problem.size_x()), "@GT/VariableType")
    for i, variable_type in enumerate(variables_type):
      variable_type = str(variable_type or "Continuous").lower()
      if variable_type == "categorical":
        variable_bounds = problem.variables_bounds(i)
        if len(variable_bounds) > 1:
          categorical_variables.append((i, variable_bounds))
    return categorical_variables

  @staticmethod
  def _test_categorical_only_problem(problem, doe_mode):
    n_combinations, size_x = 1, problem.size_x()
    n_infinite = 1024 * 1024 * 128 // size_x # No more than 1G in memory

    variables_type = problem.elements_hint(slice(0, size_x), "@GT/VariableType")
    for i, variable_type in enumerate(variables_type):
      variable_type = str(variable_type or "continuous").lower()
      variable_bounds = problem.variables_bounds(i)
      if variable_type == "categorical":
        n_levels = len(variable_bounds)
        if n_levels > 1:
          n_combinations = (n_levels * n_combinations) if (n_infinite // n_combinations) >= n_levels else n_infinite
      elif variable_type in ("discrete", "stepped"):
        if len(variable_bounds) > 1:
          return False # the problem can be solved, somehow...
      elif _numpy.isnan(variable_bounds).any() or variable_bounds[0] < variable_bounds[1]:
        return False # the problem can be solved, somehow...

    if n_combinations == n_infinite or problem.size_s():
      fatality = True
    else:
      fatality = any(str(_).lower() == "fromblackbox" for _ in problem.elements_hint(slice(size_x, size_x + problem.size_f() + problem.size_c()), "@GT/NoiseLevel"))

    if fatality:
      # pure categorical problem with noise or stochastic
      error_message = "Cannot apply " + \
                      ("the Adaptive Design technique " if doe_mode else "optimization techniques ") + \
                      "because all problem variables are categorical or have a fixed value. " + \
                      ("\nThe number of combinations of categorical variables is%s %d." % (" more than" if (n_combinations == n_infinite) else "", n_combinations))
      #if n_combinations < n_infinite:
      #  error_message += " Consider using the Full Factorial DoE technique, as it can cover the entire design space of this problem."
      raise _ex.UnsupportedProblemError(error_message)

    return True

  @staticmethod
  def _generate_full_factorial(problem, validation_mode, factor_types=("categorical",)):
    if problem.size_s():
      raise _ex.InvalidProblemError("Cannot solve robust optimization problem because all problem variables are categorical or have a fixed value.")

    # The first pass: count the total number of combinations
    variables_levels, n_combinations, size_x  = [], 1, problem.size_x()
    n_infinite = 1024 * 1024 * 128 // size_x # No more than 1G in memory

    variables_type = problem.elements_hint(slice(0, size_x), "@GT/VariableType")
    for i, variable_type in enumerate(variables_type):
      variable_type = str(variable_type or "continuous").lower()
      variable_bounds = problem.variables_bounds(i)
      if variable_type in factor_types:
        n_levels = len(variable_bounds)
        if n_levels > 1:
          if (n_infinite // n_combinations) >= n_levels:
            n_combinations *= n_levels
          else:
            raise _ex.InvalidProblemError("Cannot solve optimization problem because all problem variables are categorical or have a fixed value, " +\
                                          "and the cardinality of the full factorial design exceeds " + str(n_infinite) + " points.")
        variables_levels.append(variable_bounds)
      else:
        variables_levels.append((variable_bounds[0],))

    if validation_mode:
      return n_combinations

    design = _numpy.empty((n_combinations, size_x))
    n_repeat, n_tile = 1, n_combinations
    for i, levels in enumerate(variables_levels):
      n_levels = len(levels)
      if n_levels == 1:
        design[:, i] = levels[0]
      else:
        n_tile //= n_levels
        design[:, i] = _numpy.tile(_numpy.repeat(levels, n_repeat), n_tile)
        n_repeat *= n_levels

    return design

  @staticmethod
  def _count_known_full_factorial(problem, sample_x, sample_f, sample_c):
    if sample_x is None:
      return 0
    elif sample_c is not None:
      mask_known = _numpy.isfinite(sample_c).all(axis=1)
      if not mask_known.any():
        return 0
    elif problem.size_c():
      return 0
    else:
      mask_known = _numpy.ones(len(sample_x), dtype=bool)

    size_x = problem.size_x()
    if sample_f is not None:
      objectives_type = [(_ or "minimize").lower() for _ in problem.elements_hint(slice(size_x, size_x + problem.size_f()), "@GT/ObjectiveType")]
      for i, kind in enumerate(objectives_type):
        if kind in ("minimize", "maximize"):
          mask_known &= _numpy.isfinite(sample_f[:, i])
    elif problem.size_f():
      return 0

    if not mask_known.any():
      return 0

    # now check variables values
    variables_type = problem.elements_hint(slice(0, size_x), "@GT/VariableType")
    for i, variable_type in enumerate(variables_type):
      variable_type = str(variable_type or "continuous").lower()
      variable_bounds = problem.variables_bounds(i)
      if variable_type == "categorical":
        mask_known &= _numpy.equal(sample_x[:, i].reshape(-1, 1), [variable_bounds]).any(axis=1)
      else:
        mask_known &= _numpy.isfinite(sample_x[:, i] == variable_bounds[0])
      if not mask_known.any():
        return 0

    return _numpy.count_nonzero(mask_known)

  def _make_alternative_result(self, problem, designs_table, n_initial, compatibility, diagnostics):
    from ..utils import buildinfo as _buildinfo
    from .. import __version__

    buildstamp = _buildinfo.buildinfo().get("Build", {}).get("Stamp", 'version=' + str(__version__) + ';')

    sift_logger = _shared.Logger(logger=self.__logger, log_level_string=self.options._get('GTOpt/LogLevel').lower())

    sift_logger.info(buildstamp)
    sift_logger.info(str(problem))

    for diag_record in diagnostics:
      if diag_record.severity == _diagnostic.DIAGNOSTIC_WARNING:
        sift_logger.warn(diag_record.message)

    from .. import result as _result

    c_tol = float(self.options._get("GTOpt/ConstraintsTolerance"))
    designs = _designs._postprocess_designs(problem, designs_table, n_initial, c_tol)

    solutions_subsets = {"new": slice(n_initial, len(designs[0])),
                         "auto": slice(0, len(designs[0])),
                         "initial": slice(0, n_initial)}

    designs_slices = designs[1][2]
    solutions_fields = dict((k, designs_slices[k]) for k in _result.Result._known_fields if k in designs_slices)

    objectives_gradient, _, _, _ = problem.objectives_gradient()
    constraints_gradient, _, _, _ = problem.constraints_gradient()

    solution_info = {
      "Solver" : {
        "Buildstamp": buildstamp,
        "Number of variables": problem.size_x(),
        "Number of stochastic variables": problem.size_s(),
        "Number of objectives": problem.size_f(),
        "Number of constraints": problem.size_c(),
        "Objectives gradients": objectives_gradient,
        "Constraints gradients": constraints_gradient,
        "Objectives gradients analytical": objectives_gradient,
        "Constraints gradients analytical": constraints_gradient,
        "Options": self.options.values,
      }
    }

    doe_result = _result.Result(status=_status.SUCCESS, info=solution_info, solutions=designs[0], fields=solutions_fields,
                                problem=_weakref.ref(problem), diagnostics=diagnostics, designs=designs,
                                solutions_subsets=solutions_subsets, finalize=False)
    doe_result._finalize(problem=problem, auto_objective_type="Minimize", options=self.options.values, logger=sift_logger)

    if compatibility:
        solution_optimal = {"x": doe_result.solutions("x", "optimal")}
        for field in ("f", "c", "v", "psi"):
          field_e = field + "e"
          if field in doe_result._fields:
            solution_optimal[field] = doe_result.solutions(field, "optimal")
            solution_optimal[field_e] = doe_result.solutions(field_e, "optimal") \
                                      if field_e in doe_result._fields else \
                                        _numpy.zeros_like(solution_optimal[field])
          else:
            solution_optimal[field] = []
            solution_optimal[field_e] = []

        solution_optimal    = _api._Solution(**solution_optimal)
        solution_converged  = _api._Solution([], [], [], [], [], [], [], [], [])
        solution_infeasible = _api._Solution([], [], [], [], [], [], [], [], [])

        return _api.Result(_shared.write_json(solution_info), _status.SUCCESS, _weakref.ref(problem),
                           solution_optimal, solution_converged, solution_infeasible, diagnostics)

    initial_solutions, _ = doe_result._raw_solutions(None, ("optimal", "initial"))
    new_solutions, _ = doe_result._raw_solutions(None, ("optimal", "new"))
    solutions_data = _numpy.vstack((initial_solutions, new_solutions))
    solutions_data.setflags(write=False)

    n_all, n_initial = len(solutions_data), len(initial_solutions)
    solutions_subsets = {"new": slice(n_initial, n_all),
                         "auto": slice(0, n_all),
                         "initial": slice(0, n_initial),
                         "all": slice(0, n_all)}

    super(_result.Result, doe_result).__setattr__("_solutions_data", solutions_data)
    super(_result.Result, doe_result).__setattr__("_solutions_subsets", solutions_subsets)

    return doe_result

  def _build_full_factorial(self, problem, mode, sample_x, sample_f, sample_c, compatibility, factor_types=("categorical",)):
    warn_message = "All problem variables are %s or have a fixed value. The solution will be selected from a full factorial design." % ", ".join(factor_types)
    diagnostics = [_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_WARNING, warn_message)]

    if mode in (_api.GTOPT_VALIDATE, _api.GTOPT_VALIDATE_DOE):
      n_points = self._generate_full_factorial(problem, True, factor_types)
      n_archive = self._count_known_full_factorial(problem, sample_x, sample_f, sample_c)

      diagnostics.append(_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_MISC, _shared.write_json({
        "_details": {"Optimization": {
          "N_archive": n_archive,
          "N_eval": (n_points - n_archive),
          }}
      })))

      return _status.SUCCESS, diagnostics

    points_x = self._generate_full_factorial(problem, False, factor_types)

    designs_table = _designs._preprocess_initial_sample(problem=problem, sample_x=points_x, sample_f=None, sample_c=None, sample_nf=None, sample_nc=None)
    initial_sample = _designs._preprocess_initial_sample(problem=problem, sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, sample_nf=None, sample_nc=None)
    n_initial = len(initial_sample) if initial_sample is not None else 0

    if n_initial:
      designs_table = _designs._fill_gaps_and_keep_dups(_numpy.vstack((initial_sample, designs_table)), slice(0, problem.size_x()),
                                                        _designs._typical_problem_payloads_callback(problem))
      designs_table = _designs._select_unique_rows(designs_table, n_initial)

    return self._make_alternative_result(problem=problem, designs_table=designs_table, n_initial=n_initial,
                                         compatibility=compatibility, diagnostics=diagnostics)

  def _enumerate_categorical_combinations(self, problem, mode, invalid_initial_points, sample_x, sample_f, sample_c, sample_nf, sample_nc):
    def _optional_sample(index):
      if sample_x is not None:
        subsample_x = sample_x[index]
        if len(subsample_x):
          subsample_f = sample_f[index] if sample_f is not None else None
          subsample_c = sample_c[index] if sample_c is not None else None
          subsample_nf = sample_nf[index] if sample_nf is not None else None
          subsample_nc = sample_nc[index] if sample_nc is not None else None
          return subsample_x, subsample_f, subsample_c, subsample_nf, subsample_nc
      return None, None, None, None, None

    catvars = self._read_categorical_combinations(problem)
    if not catvars:
      if sample_x is not None:
        valid_initial_points = _numpy.ones((len(sample_x),), dtype=bool)
        valid_initial_points[invalid_initial_points] = False

        if not valid_initial_points.all():
          yield (None, None, None,) + _optional_sample(valid_initial_points)
          yield (self.__invalid_category_mark, None, None,) + _optional_sample(invalid_initial_points)
          return

      yield None, None, None, sample_x, sample_f, sample_c, sample_nf, sample_nc
      return

    size_x, size_f, size_c = problem.size_x(), problem.size_f(), problem.size_c()

    variables_name = problem.variables_names()
    responses_name = problem.objectives_names() + problem.constraints_names()

    categorical_cardinality = 1
    max_categorical_cardinality = _numpy.iinfo(int).max
    for _, levels in catvars:
      n_levels = len(levels)
      if max_categorical_cardinality // categorical_cardinality > n_levels:
        categorical_cardinality *= n_levels
      else:
        raise _ex.InvalidProblemError("The cardinality of the cartesian product of categorical variables %s is too large" % (", ".join(variables_name[i] for i, levels in catvars),))

    doe_mode = mode in (_api.GTOPT_DOE, _api.GTOPT_VALIDATE_DOE)

    if doe_mode:
      point_count = int(self.options.get("/GTOpt/DesignPointsCount"))
      if point_count and categorical_cardinality > point_count:
        raise _ex.InvalidProblemError("The cardinality of the cartesian product of categorical variables %s is greater than the target number of feasible designs: %d > %d" % (", ".join(variables_name[i] for i, levels in catvars), categorical_cardinality, point_count))

    maximum_expensive_iterations = int(self.options.get('GTOpt/MaximumExpensiveIterations'))
    maximum_iterations = int(self.options.get('GTOpt/MaximumIterations'))

    # Intentionally ignore initial sample because these samples may be different for different combinations
    evaluations_budget = problem._responses_evaluation_limit(maximum_iterations=maximum_iterations, maximum_expensive_iterations=maximum_expensive_iterations)

    default_cost_type = _problem._backend.default_option_value("@GTOpt/EvaluationCostType")
    expensive_responses = [i for i, _ in enumerate(problem.elements_hint(slice(size_x, None), "@GTOpt/EvaluationCostType")) if str(_ or default_cost_type).lower() == "expensive"]

    maximum_expensive_iterations = int(self.options.get("GTOpt/MaximumExpensiveIterations"))
    if maximum_expensive_iterations and maximum_expensive_iterations < categorical_cardinality \
       and any(evaluations_budget[i] is None for i in expensive_responses):
      raise _ex.InvalidOptionsError("The maximum number of evaluations for expensive responses [%s] is less than the cardinality of the cartesian product of categorical variables [%s]: GTOpt/MaximumExpensiveIterations=%d is less than %d." \
        % (", ".join(name for i, name in enumerate(responses_name) if i in expensive_responses), ", ".join(variables_name[i] for i, levels in catvars), maximum_expensive_iterations, categorical_cardinality))

    maximum_iterations = int(self.options.get("GTOpt/MaximumIterations"))
    if maximum_iterations and maximum_iterations < categorical_cardinality and (None in evaluations_budget):
      raise _ex.InvalidOptionsError("The maximum number of evaluations for responses [%s] is less than the cardinality of the cartesian product of categorical variables [%s]: GTOpt/MaximumExpensiveIterations=%d is less than %d." \
        % (", ".join(name for i, name in enumerate(responses_name) if evaluations_budget[i] is None), ", ".join(variables_name[i] for i, levels in catvars), maximum_iterations, categorical_cardinality))

    invalid_individual_budget = [i for i, budget in enumerate(evaluations_budget) if budget and budget > 0 and budget < categorical_cardinality]
    if invalid_individual_budget:
      raise _ex.InvalidOptionsError("The individual maximum number of evaluations for responses [%s] is less than the cardinality of the cartesian product of categorical variables [%s]: %d." \
        % (", ".join(responses_name[i] for i in invalid_individual_budget), ", ".join(variables_name[i] for i, levels in catvars), categorical_cardinality))

    if sample_x is not None:
      invalid_initial_sample = []
      for catvar_index, catvar_levels in catvars:
        unknown_levels = _numpy.setdiff1d(sample_x[:, catvar_index], catvar_levels)
        n_unknown_levels = len(unknown_levels)
        if n_unknown_levels:
          invalid_initial_sample.append("- categorical variable %s takes %s" % (variables_name[catvar_index], \
            ("unknown values " + str(unknown_levels) if n_unknown_levels <= 3 else \
              (str(n_unknown_levels) + " unknown values"))))
      if invalid_initial_sample:
        self._log(LogLevel.WARN, "Invalid values encountered in the initial sample:\n" + "\n".join(invalid_initial_sample))

    mode_name = { _api.GTOPT_SOLVE: "optimization",
                  _api.GTOPT_VALIDATE: "validation",
                  _api.GTOPT_DOE: "adaptive design",
                  _api.GTOPT_VALIDATE_DOE: "adaptive design validation"}.get(mode, "")

    maximum_expensive_iterations_left = maximum_expensive_iterations
    maximum_iterations_left = maximum_iterations
    evaluations_budget_left = [_ for _ in evaluations_budget]
    var_hints = [{} for i in _six.moves.xrange(size_x)] # don't multiply to avoid references to the same object
    active_points = None if sample_x is None else _numpy.zeros((len(sample_x),), dtype=bool)
    used_initial_points = None if sample_x is None else active_points.copy()
    combination_first = 0

    initial_guess = problem.initial_guess()
    if initial_guess is not None:
      # find indices of the initial guess values and make it the first combination w.r.t levels rounding
      n_levels = 1
      for catvar_index, catvar_levels in catvars[::-1]:
        combination_first *= n_levels
        if initial_guess[catvar_index] != _shared._NONE:
          initial_guess_index = _numpy.nonzero(_numpy.equal(catvar_levels, initial_guess[catvar_index]))[0]
          if len(initial_guess_index):
            combination_first += initial_guess_index[0]
          # Intentionally do nothing because initial guess has been checked already.
          # If we didn't find a value, then it's a rounding problem.
        n_levels = len(catvar_levels)
      del n_levels

    for combination_index in _six.moves.xrange(categorical_cardinality):
      folds_number = categorical_cardinality - combination_index

      if doe_mode:
        self.options.set("/GTOpt/DesignPointsCount", point_count // folds_number)
        point_count -= point_count // folds_number

      self.options.set("GTOpt/MaximumExpensiveIterations", maximum_expensive_iterations_left // folds_number)
      maximum_expensive_iterations_left -= maximum_expensive_iterations_left // folds_number

      self.options.set("GTOpt/MaximumIterations", maximum_iterations_left // folds_number)
      maximum_iterations_left -= maximum_iterations_left // folds_number

      resp_hints = [({} if budget is None else {"@GT/EvaluationLimit": (budget // folds_number)}) for budget in evaluations_budget_left]
      evaluations_budget_left = [None if budget is None else (budget - (budget // folds_number)) for budget in evaluations_budget_left]

      combination_code = (combination_first + combination_index) % categorical_cardinality
      combination_name = []
      for catvar_index, catvar_levels in catvars:
        n_levels = len(catvar_levels)
        catvar_value = catvar_levels[combination_code % n_levels]
        var_hints[catvar_index]["@GT/FixedValue"] = catvar_value
        combination_code //= n_levels
        combination_name.append("%s=%s" % (variables_name[catvar_index], catvar_value))

      current_sample_x, current_sample_f, current_sample_c, current_sample_nf, current_sample_nc = None, None, None, None, None

      if sample_x is not None:
        active_points.fill(True)
        for catvar_index, catvar_levels in catvars:
          active_points = _numpy.logical_and(active_points, sample_x[:, catvar_index] == var_hints[catvar_index]["@GT/FixedValue"])
        active_points[invalid_initial_points] = False

        if active_points.any():
          current_sample_x = sample_x[active_points]
          current_sample_f = sample_f[active_points] if sample_f is not None else None
          current_sample_c = sample_c[active_points] if sample_c is not None else None
          current_sample_nf = sample_nf[active_points] if sample_nf is not None else None
          current_sample_nc = sample_nc[active_points] if sample_nc is not None else None

          _numpy.logical_or(used_initial_points, active_points, out=used_initial_points)

      combination_name = "subproblem #%d/%d [%s]" % (combination_index + 1, categorical_cardinality, ", ".join(combination_name),)
      self._log(LogLevel.INFO, "\nStarting %s of subproblem %s\n" % (mode_name, combination_name,))
      yield combination_name, var_hints, resp_hints, current_sample_x, current_sample_f, current_sample_c, current_sample_nf, current_sample_nc

    if used_initial_points is not None and not used_initial_points.all():
      yield (self.__invalid_category_mark, None, None,) + _optional_sample(~used_initial_points)

  @staticmethod
  def _update_integer_share(count, n_splits):
    delta = count // n_splits
    return (count - delta), delta

  def _read_limited_evaluations_configuration(self, options):
    settings = {}
    with _shared._scoped_options(self, options):
      settings['responses_scalability'] = int(self.options._get("GTOpt/ResponsesScalability"))
      settings['batch_size'] = int(self.options._get("GTOpt/BatchSize"))
      settings['watcher_timeout_ms'] = int(self.options._get("/GTOpt/WatcherCallGap"))
    return settings

  def _preprocess_linear_response(self, problem, mode, sample_x, sample_f, sample_c, return_evaluations=False):
    empty_return = (None, None) if return_evaluations else None
    validation_mode = mode in (_api.GTOPT_VALIDATE, _api.GTOPT_VALIDATE_DOE)
    if not _shared.parse_bool(self.options._get("/GTOpt/PreprocessLinearResponses")):
      return empty_return

    restore_mode = _shared.parse_auto_bool(self.options._get("GTOpt/RestoreAnalyticResponses"), "auto")
    if not restore_mode:
      return empty_return

    try:
      if not problem._enumerate_reconstructable_linear_responses(True).any():
        return empty_return

      self._log(LogLevel.INFO, "Trying to restore analytic forms of problem objectives and constraints hinted as linear...")

      seed = int(self.options.get("GTOpt/Seed")) if _shared.parse_auto_bool(self.options.get("GTOpt/Deterministic"), False) else _numpy.random.randint(1, 65535)
      resp_scalability = int(self.options._get("GTOpt/ResponsesScalability")) # read scalability first
      rrms_threshold = float(self.options._get("/GTOpt/RestoreAnalyticResponsesThreshold"))

      lin_deps = problem._reconstruct_linear_dependencies(sample_x=sample_x, sample_f=sample_f, sample_c=sample_c,
                                                          evaluation_limit=(int(self.options._get("GTOpt/MaximumIterations")) or None),
                                                          expensive_evaluation_limit=(int(self.options._get("GTOpt/MaximumExpensiveIterations")) or None),
                                                          seed=seed, immutable=True, rrms_threshold=rrms_threshold,
                                                          responses_scalability=resp_scalability,
                                                          validation_mode=validation_mode)
      
      failures = [("  - cannot restore linear objective #%d (%s): %s" % (i, problem._objectives[i].name, reason)) for i, reason, rrmse, weights in lin_deps.failed_objectives]\
               + [("  - cannot restore linear constraint #%d (%s): %s" % (i, problem._constraints[i].name, reason)) for i, reason, rrmse, weights in lin_deps.failed_constraints]

      if validation_mode:
        severity = _diagnostic.DIAGNOSTIC_WARNING if restore_mode == "auto" else _diagnostic.DIAGNOSTIC_ERROR
        diagnostics = [_diagnostic.DiagnosticRecord(severity, message) for message in failures]
        evaluations_commited = len(lin_deps.evaluations[0])
        if evaluations_commited:
          diagnostics.append(_diagnostic.DiagnosticRecord(_diagnostic.DIAGNOSTIC_MISC, 
                                                          _shared.write_json({"_details": {'LinearResponses': {
                                                              'N_doe': evaluations_commited }
                                                              }})))
        elif not diagnostics:
          return None # nothing special
        status = _status.SUCCESS if (not failures or restore_mode == "auto") else _status.INVALID_PROBLEM
        return status, diagnostics

      if failures:
        if restore_mode == "auto":
          self._log(LogLevel.INFO, "\n".join(failures))
        else:
          raise _ex.InvalidProblemError("Failed to restore analytic forms of problem objectives and constraints hinted as linear:\n" + "\n".join(failures))

      size_f, size_c = problem.size_f(), problem.size_c()
      resp_hints = [{} for _ in range(size_f + size_c)] # use long form otherwise we've got list of the same object

      for i, _, _, _ in lin_deps.failed_objectives:
        resp_hints[i].update(self._failed_linear_response_hints())

      for i, _, _, _ in lin_deps.failed_constraints:
        resp_hints[i+size_f].update(self._failed_linear_response_hints())

      for i, rrmse, weights in lin_deps.objectives:
        rrmse_report = "" if rrmse is None else (" (leave-one-out cross-validation R^2=%g)" % max(0., 1. - _shared._scalar(rrmse)**2))
        self._log(LogLevel.INFO, "  - objective #%d: %s = %s%s" % (i, problem._objectives[i].name, problem._regression_string(weights, "<reconstructed>", 15), rrmse_report))
        resp_hints[i].update(self._reconstructed_linear_response_hints(weights))

      for i, rrmse, weights in lin_deps.constraints:
        rrmse_report = "" if rrmse is None else (" (leave-one-out cross-validation R^2=%g)" % max(0., 1. - _shared._scalar(rrmse)**2))
        self._log(LogLevel.INFO, "  - constraint #%d: %s = %s%s" % (i, problem._constraints[i].name, problem._regression_string(weights, "<reconstructed>", 15), rrmse_report))
        resp_hints[i+size_f].update(self._reconstructed_linear_response_hints(weights))

      if any((rrmse is None or _shared._scalar(rrmse) >= 1.) for i, rrmse, weights in (lin_deps.objectives + lin_deps.constraints)):
        self._log(LogLevel.WARN, "Cross validation indicates that restored analytic forms of problem objectives and constraints hinted as linear may be inaccurate.")

      if not any(_ for _ in resp_hints):
        resp_hints = None

      return (resp_hints, lin_deps.evaluations) if return_evaluations else resp_hints
    except:
      # ignore exception in 'auto' mode but reraise it in the explicit mode
      if restore_mode != "auto":
        raise
      exc_info = _sys.exc_info()
      self._log(LogLevel.WARN, "Failed to restore analytic forms of problem objectives and constraints hinted as linear: %s." % ((str(exc_info[1]) or "no particular reason given"),))

    return empty_return

  def _fill_reconstructed_responses(self, responses):
    self.__impl.read_backend_reconstructed_responses(responses)

  def _create_snapshot_watcher(self, problem, mode):
    if mode in (_api.GTOPT_SOLVE, _api.GTOPT_DOE) and self.__watcher and not problem.size_s():
      auto_objective_type = "minimize" if mode == _api.GTOPT_SOLVE else "adaptive"
      return _SolutionSnapshotFactory(generator=self, watcher=self.__watcher, problem=problem, auto_objective_type=auto_objective_type)
    return _SolutionSnapshotFactory(generator=None, watcher=self.__watcher, problem=None, auto_objective_type=None)

  @staticmethod
  def _read_nonempty_matrix(input_data, size_x, detect_none, default_output=None, name=None):
    if input_data is not None and len(input_data) > 0:
      output_matrix = _shared.as_matrix(input_data, shape=(None, size_x), detect_none=detect_none, name=name)
      if output_matrix.size > 0:
        return output_matrix
    return default_output

  @staticmethod
  def _check_required_sample(sample_test, sample_req, name_test, name_req):
    if sample_test is None:
      return
    if sample_req is None:
      raise ValueError("The non-empty argument %s requires non-empty %s argument" % (name_test, name_req))
    if sample_test.shape[0] != sample_req.shape[0]:
      raise ValueError("The matrix %s has different number of points than matrix %s: %d != %d" % (name_test, name_req, sample_test.shape[0], sample_req.shape[0]))

  @staticmethod
  def _reconstructed_linear_response_hints(weights):
    return {"@GTOpt/LinearParameterVector": weights.tolist(), "@GTOpt/LinearityType": "Linear"}

  @staticmethod
  def _failed_linear_response_hints():
    return {"@GTOpt/LinearParameterVector": [], "@GTOpt/LinearityType": "Generic"}

  def _log(self, level, message):
    if self.__logger:
      self.__logger(level, message)

  @_contextlib.contextmanager
  def _lazy_intermediate_result_callback(self, problem, mode, subproblems_result, compatibility):
    intermediate_result_callback = None

    try:
      if subproblems_result and mode not in (_api.GTOPT_VALIDATE, _api.GTOPT_VALIDATE_DOE):
        intermediate_result_callback = _DeferredIntermediateResult(parent=self, problem=problem, mode=mode,
                                                                   subproblems_result=subproblems_result,
                                                                   compatibility=compatibility)
      yield intermediate_result_callback
    finally:
      if intermediate_result_callback is not None:
        intermediate_result_callback.reset()

  @_contextlib.contextmanager
  def _postprocess_intermediate_result(self, problem, mode, subproblems_result, compatibility):
    postprocessor = None

    try:
      if subproblems_result and mode not in (_api.GTOPT_VALIDATE, _api.GTOPT_VALIDATE_DOE):
        postprocessor = _IntermediateResultPostprocessor(parent=self, problem=problem, mode=mode,
                                                         subproblems_result=subproblems_result,
                                                         compatibility=compatibility)

      self.__impl.set_result_postprocessor(postprocessor)

      yield
    finally:
      self.__impl.set_result_postprocessor(None)
      if postprocessor is not None:
        postprocessor.reset()

def _recursive_update_diagnostics(base_dict, update_dict):
  for k in update_dict:
    if k in base_dict:
      if isinstance(update_dict[k], dict):
        _recursive_update_diagnostics(base_dict[k], update_dict[k])
      elif isinstance(update_dict[k], list):
        base_dict[k] += update_dict[k]
      elif isinstance(update_dict[k], bool):
        base_dict[k] &= update_dict[k]
      elif isinstance(update_dict[k], int):
        base_dict[k] += update_dict[k]
      elif isinstance(update_dict[k], float):
        base_dict[k] = (base_dict[k] + update_dict[k]) * 0.5
      else:
        base_dict[k] = update_dict[k]
    else:
      base_dict[k] = update_dict[k]

def _optional_vstack(data, empty_shape=None):
  data = [_ for _ in data if len(_)]
  if not data:
    return [] if empty_shape is None else _numpy.empty(shape=empty_shape, dtype=float)
  return data[0] if len(data) == 1 else _numpy.vstack(data)

class _IntermediateResultCombinator(object):
  def __init__(self, parent, problem, mode, subproblems_result, compatibility):
    self._parent             = parent # solver that generated this intermediate result
    self._problem            = problem # current (not the original) problem
    self._mode               = mode # mode of operation
    self._subproblems_result = [_ for _ in subproblems_result] # list of results obtained
    self._compatibility      = bool(compatibility) # indicates format of results in the subproblems_result.

  def reset(self):
    # indicates the lifetime of the intermediate result is over
    self._parent             = None
    self._problem            = None
    self._subproblems_result = []

  def proceed(self, result):
    if not self._parent or not self._subproblems_result:
      return result

    subproblems_result = self._subproblems_result
    if result:
      subproblems_result.append(result)

    if len(subproblems_result) == 1:
      return subproblems_result[0]

    if self._compatibility:
      return self._parent._combine_legacy_results(problem=self._problem, mode=self._mode,
                                                  subproblems_result=subproblems_result,
                                                  intermediate_result=True)
    return self._parent._combine_solutions(problem=self._problem, mode=self._mode,
                                           subproblems_result=subproblems_result,
                                           invalid_initial_sample=None, intermediate_result=True)

  def _make_legacy_solution(self, fields_dict, points):
    if not len(points):
      return _api._Solution([], [], [], [], [], [], [], [], [])
    return _api._Solution(**dict((k, points[:, fields_dict.get(k, slice(0))]) for k in ("x", "f", "c", "v", "fe", "ce", "ve", "psi", "psie")))

  def _make_legacy_result(self, result):
    solution_fields = dict(result._fields)
    optimal_points = self._make_legacy_solution(solution_fields, result.solutions(filter_type="optimal"))
    converged_points = self._make_legacy_solution(solution_fields, result.solutions(filter_type="converged"))
    infeasible_points = self._make_legacy_solution(solution_fields, result.solutions(filter_type="infeasible"))

    new_info = dict((k, result.info[k]) for k in result.info)
    new_diagnostics = new_info.pop("Diagnostics", None)
    return _api.Result(info=_shared.write_json(new_info), status=result.status, problem_ref=_weakref.ref(self._problem),
                        optimal_points=optimal_points, converged_points=converged_points,
                        infeasible_points=infeasible_points, diagnostics=new_diagnostics)

class _DeferredIntermediateResult(_IntermediateResultCombinator):
  def __init__(self, parent, problem, mode, subproblems_result, compatibility):
    super(_DeferredIntermediateResult, self).__init__(parent=parent, problem=problem, mode=mode,
                                                      subproblems_result=subproblems_result,
                                                      compatibility=compatibility)

  def __call__(self):
    return self.proceed(None)

class _IntermediateResultPostprocessor(_IntermediateResultCombinator):
  def __init__(self, parent, problem, mode, subproblems_result, compatibility):
    super(_IntermediateResultPostprocessor, self).__init__(parent=parent, problem=problem, mode=mode,
                                                      subproblems_result=subproblems_result,
                                                      compatibility=compatibility)

  def __call__(self, result, intermediate_result):
    return result if not intermediate_result else self.proceed(result)

class _SolutionSnapshotFactory(_designs._SolutionSnapshotFactoryBase):
  def __call__(self, data=None):
    if not self._user_watcher:
      return True
    elif not self._generator:
      return self._user_watcher(data)
    return self._proceed(payload=data, result_kind=None)

  def report_final_result(self, result, sample_x, sample_f, sample_c, sample_nf, sample_nc):
    if not self._user_watcher or not self._generator:
      return
    self._prepare_final_result(sample_x=sample_x, sample_f=sample_f, sample_c=sample_c, sample_nf=sample_nf, sample_nc=sample_nc)
    payload = {'ResultUpdated': True, 'RequestIntermediateResult': _weakref.ref(result)} if result else None
    self._proceed(payload=payload, result_kind="final")

  def _proceed(self, payload, result_kind):
    lazy_snapshot = None
    try:
      payload = payload or {}
      result_kind = result_kind or ("new" if payload.get("ResultUpdated", False) else "same")
      lazy_snapshot = _designs._DetachableSingleCallableRef(callable=self.snapshot,
                                                      result_ref=payload.get("RequestIntermediateResult"),
                                                      result_kind=result_kind)
      payload["RequestIntermediateSnapshot"] = lazy_snapshot
      return self._user_watcher(payload)
    finally:
      if lazy_snapshot is not None:
        lazy_snapshot._reset()

  def snapshot(self, result_ref, result_kind):
    if self._last_snapshot is not None and result_kind == 'same' and self._history_length == len(self._problem._history_cache):
      return self._last_snapshot

    try:
      final_result = result_kind == 'final'
      if final_result:
        final_snapshot = self._modern_result_to_snapshot(result_ref() if result_ref else None)
        if final_snapshot:
          return final_snapshot

      # Get known designs and convert history to designs table.
      # Ignore the new intermediate result because it may contain points from self._subproblems_design.
      # We must not fill absent linear responses for these points.
      designs_table = self._subproblems_design + [self._collect_designs(extra_designs=None)]

      # convert result to snapshot designs or use cached value if we can
      if self._last_result_designs is not None and result_kind == 'same':
        result_designs = self._last_result_designs
      else:
        self._last_result_designs = None # reset last result
        result_designs = self._result_to_designs(result_ref()) if result_ref else None

      if result_designs is None and len(designs_table) == 1:
        designs_table = _numpy.vstack(designs_table) # simple case, no dups
      else:
        # the intermediate result may contain points from the previous subproblems
        if result_designs is not None:
          designs_table.append(result_designs)
        designs_table = _numpy.vstack(designs_table)
        designs_table = _designs._fill_gaps_and_keep_dups(designs_table, self._fields_mapping["x"][1],
                                                          _designs._typical_problem_payloads_callback(self._problem))
        designs_table = _designs._select_unique_rows(designs_table, 0)

      if not designs_table.size:
        # This must be the first call
        empty_status = _numpy.zeros((0,), dtype=int)
        return self._make_snapshot(designs=designs_table[:, :-1], status_initial=empty_status,
                                   status_feasibility=empty_status, status_optimality=empty_status)

      # Note "status" is the last column. Must be.
      designs_table, status_initial = designs_table[:, :-1], designs_table[:, -1]
      status_initial[_shared._find_holes(status_initial)] = _designs._SolutionSnapshot._UNDEFINED
      status_initial = status_initial.astype(int)
      status_feasibility = self._status_feasibility(design=designs_table, final_result=final_result)
      status_optimality = self._status_optimality(design=designs_table, status_feasibility=status_feasibility, final_result=final_result)

      return self._make_snapshot(designs=designs_table,
                                 status_initial=status_initial,
                                 status_feasibility=status_feasibility,
                                 status_optimality=status_optimality)
    except:
      pass

    return None
