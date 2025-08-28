#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""pSeven Core result module."""

import sys as _sys
import traceback as _traceback
import ctypes as _ctypes
import weakref as _weakref
from contextlib import contextmanager as _contextmanager

import numpy as _numpy

from . import six as _six
from . import shared as _shared
from . import exceptions as _exceptions
from . import options as _options

GT_SOLUTION_TYPE_DISCARDED = -1
GT_SOLUTION_TYPE_CONVERGED = 0
GT_SOLUTION_TYPE_NOT_DOMINATED = 1
GT_SOLUTION_TYPE_INFEASIBLE = 2
GT_SOLUTION_TYPE_BLACKBOX_NAN = 3
GT_SOLUTION_TYPE_NOT_EVALUATED = 4
GT_SOLUTION_TYPE_FEASIBLE_NAN = 5
GT_SOLUTION_TYPE_INFEASIBLE_NAN = 6
GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE = 7

class _API(object):
  class _Points(_ctypes.Structure):
    pass

  def __init__(self):
    self._backend = _shared._library
    self._c_double_p = _ctypes.POINTER(_ctypes.c_double)
    self._c_size_p = _ctypes.POINTER(_ctypes.c_size_t)
    self._c_short_p = _ctypes.POINTER(_ctypes.c_short)

    self._Points._pack_ = 8
    self._Points._fields_ = [("x", self._c_double_p),
                             ("f", self._c_double_p),
                             ("c", self._c_double_p),
                             ("df", self._c_double_p),
                             ("dc", self._c_double_p),
                             ("n", _ctypes.c_uint)]

    self.solver_filter = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                           , _ctypes.c_uint #nvars
                                           , _ctypes.c_uint #nobj
                                           , _ctypes.c_uint #nconst
                                           , self._c_double_p, self._c_double_p #constr bounds
                                           , _ctypes.c_void_p #option manager
                                           , _ctypes.POINTER(_ctypes.c_int) #out
                                           , self._Points # points (must be the last parameter due to the bug in Python 2.5)
                                           )(("GTOptSolverFilter", self._backend))

    self.d_optimal_design = _ctypes.CFUNCTYPE(_ctypes.c_short # ret. code
                                              , _ctypes.c_size_t # number of points
                                              , _ctypes.c_size_t # points dim.
                                              , self._c_double_p # points buffer
                                              , self._c_size_p # strides (in bytes) of the points buffer
                                              , self._c_short_p # on input: indicates points to preserve in linear design, on output: indicates points to use in linear design.
                                              , _ctypes.c_size_t # stride (in bytes) of the indicators buffer
                                              , _ctypes.POINTER(_ctypes.c_void_p) # optional pointer to
                                              )(("GTUtilsSelectPointsForLinearReconstruction", self._backend))

_api = _API()

def solution_filter(x=None, f=(), c=(), c_bounds=(), df=(), dc=(), options=None):
  """Filters a set of solutions by Pareto optimality.

  :param x: variables
  :type x: ``ndarray``, 2D
  :param f: objectives
  :type f: ``ndarray``, 2D
  :param c: constraints
  :type c: ``ndarray``, 2D
  :param c_bounds: constraint bounds
  :type c_bounds: ``iterable``, 2D-like array
  :param df: objective uncertainties
  :type df: ``ndarray``, 2D
  :param c: constraint uncertainties
  :type dc: ``ndarray``, 2D
  :param options: filter options
  :type options: ``dict``
  :return: solutions
  :rtype: ``ndarray``

  This function labels the set of solutions in the GTOpt way.

  Each solution must be described by coordinates and at least one response (constraint or objective).
  If :arg:`x` is ``None``, it is replaced by a ``range(response.shape[0])``.
  Additionally, a solution may contain uncertainties for responses.
  In :arg:`c_bounds` the NaN and ``None`` values are treated as no bound.
  Prefer ``-inf`` or ``inf`` to set left or right unbounded range.
  NaN and ``None`` uncertainties can be passed, but behavior is undefined.

  The filter

    * discards (labels as GT_SOLUTION_TYPE_DISCARDED) dominated points or strongly infeasible points or NaNs;
    * labels good (depends on GTOpt/OptimalSetRigor) infeasible points as GT_SOLUTION_TYPE_INFEASIBLE (if GTOpt/OptimalSetType = Extended);
    * labels feasible (w.r.t GTOpt/ConstraintsTolerance) non-dominated points as GT_SOLUTION_TYPE_NOT_DOMINATED.


  If the filter encounters swarms of close non-dominated points, it considers only small number of representatives from it, discarding others ((labels as GT_SOLUTION_TYPE_DISCARDED)).

  The filter can use GTOpt options:

    * GTOpt/OptimalSetType
    * GTOpt/ConstraintsTolerance
    * GTOpt/OptimalSetRigor

  """

  if options is None:
    options = {}
  elif not _shared.is_mapping(options):
    raise TypeError('The `options` argument must be a mapping.')

  if (not _shared.is_iterable(x) and x is not None) or \
      not _shared.is_iterable(f) or \
      not _shared.is_iterable(c) or \
      not _shared.is_iterable(c_bounds) or \
      not _shared.is_iterable(dc) or \
      not _shared.is_iterable(df):
    raise TypeError('All inputs must be iterable!')

  f = _shared.convert_to_2d_array(f)
  c = _shared.convert_to_2d_array(c)
  dc = _shared.convert_to_2d_array(dc)
  df = _shared.convert_to_2d_array(df)
  c_bounds = _shared.convert_to_2d_array(c_bounds)

  if not f.size and not c.size:
    raise ValueError('At least one non-empty response (`f` or `c`) must be provided!')

  if x is None:
    x = _numpy.arange(max(f.shape[0], c.shape[0]), dtype=_numpy.float64).reshape(-1, 1)
  x = _shared.convert_to_2d_array(x)

  if not x.size:
    return _numpy.array(())

  number_points = x.shape[0]
  number_vars = x.shape[1]

  if (f.size and (f.shape[0] != number_points)) or (c.size and (c.shape[0] != number_points)):
    raise ValueError('Number of non-empty response (`f` or `c`) must match with number of points `x`!')

  if (df.size and (_numpy.array(df.shape) != f.shape).any()) or \
      (dc.size and (_numpy.array(dc.shape) != c.shape).any()):
    raise ValueError('If provided, errors (`df `and `dc`) must have the same shape as corresponding responses (`f` and `c`)')

  if not c.size:
    if c_bounds.size: raise ValueError('No bounds expected for unconstrained problem')
  else:
    if c.shape[1] != c_bounds.shape[1] or c_bounds.shape[0] != 2:
      raise ValueError('Wrong bounds structure. Shape of bounds must be `(#constraints, 2)`')

    if (c_bounds[1, :] - c_bounds[0, :]).min() < 0:
      raise ValueError('Lower bounds must be not greater than upper bounds!')

  number_cons = c.shape[1]
  number_objs = f.shape[1]
  solutions_types = _numpy.empty(number_points, dtype=_numpy.int32, order="C")
  points = _api._Points()
  points.x = x.ctypes.data_as(_api._c_double_p)
  if number_objs:
    points.f = f.ctypes.data_as(_api._c_double_p)
    if df.size:
      points.df = df.ctypes.data_as(_api._c_double_p)
  lower = upper = _api._c_double_p()
  if number_cons:
    points.c = c.ctypes.data_as(_api._c_double_p)
    if dc.size:
      points.dc = dc.ctypes.data_as(_api._c_double_p)
    lower = c_bounds[0, :].ctypes.data_as(_api._c_double_p)
    upper = c_bounds[1, :].ctypes.data_as(_api._c_double_p)

  points.n = number_points
  option_manager = _options._OptionManager('GTOpt/')
  checker = _options.Options(option_manager.pointer, None)
  checker.set(options)
  checker._checkError(_api.solver_filter( number_vars
                                        , number_objs
                                        , number_cons
                                        , lower, upper
                                        , option_manager.pointer
                                        , solutions_types.ctypes.data_as(_ctypes.POINTER(_ctypes.c_int32))
                                        , points))
  return solutions_types


class _Names(object):
  def __init__(self, problem_ref):
    try:
      object.__setattr__(self, 'x', problem_ref().variables_names())
    except:
      object.__setattr__(self, 'x', [])

    try:
      object.__setattr__(self, 'f', problem_ref().objectives_names())
    except:
      object.__setattr__(self, 'f', [])

    try:
      object.__setattr__(self, 'c', problem_ref().constraints_names())
    except:
      object.__setattr__(self, 'c', [])

  def __setattr__(self, *args):
    raise TypeError('Immutable object!')

  def __delattr__(self, *args):
    raise TypeError('Immutable object!')


class _NamesTransport(object):
  def __init__(self, x, f, c):
    self._x = x
    self._f = f
    self._c = c

  def variables_names(self):
    return self._x

  def objectives_names(self):
    return self._f

  def constraints_names(self):
    return self._c


class _MethodWithProps():
  def __init__(self, callee):
    self.__callee = callee

  def __call__(self, fields=None, filter_type=None):
    return self.__callee(fields, filter_type)

  @property
  def c(self):
    return self('c')

  @property
  def f(self):
    return self('f')

  @property
  def x(self):
    return self('x')


class _MethodWithCustomProps(object):
  def __init__(self, callee, props):
    self.__callee = callee
    self.__props = props

  def __call__(self, *args, **kwargs):
    return self.__callee(*args, **kwargs)

  def __getattr__(self, name):
    return self(name) if name in self.__props else object.__getattribute__(self, name)


class Result(object):
  """General result.

  .. versionadded:: 6.14

  An object of this class is only returned by
  :meth:`~da.p7core.gtdoe.Generator.build_doe()`
  and by :meth:`~da.p7core.gtopt.Solver.solve()` if :arg:`compatibility` is ``False``.
  This class should never be instantiated by user.

  A :class:`~da.p7core.Result` object stores the numerical part of results
  (values of variables and responses) with some additional information.
  It can return all results data or filter it by some fields or point types.

  """

  _known_fields = ("x", "stochastic", "f", "c", "dfdx", "dcdx", "nf", "nc", "v", "psi", "fe", "ce", "ve", "psie", "flag")

  def __init__(self, status, info, solutions, fields, problem=None, diagnostics=None, model=None, designs=None, solutions_subsets=None, finalize=True):
    """
    :param status: returned status of the GT
    :type status: :class:`~da.p7core.status.Status`
    :param info: axualry information
    :type info: dict or str or dictable
    :param fields: description of columns {name: slice},
    :type fields: ``dict``
    :param diagnostics: GT work diagnostics
    :type diagnostics: `array-like` of :class:`~da.p7core.diagnostic.DiagnosticSeverity`
    :param problem: problem reference
    :type problem: `weakref(blackbox)`
    :param solutions: answer produced by GT
    :type solutions: TBA or generator
    :param designs: history of evaluations:
    :type designs: ``tuple``
    """

    #paranoid mode on
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

    if solutions_subsets is not None:
      _shared.check_concept_dict(solutions_subsets, 'c-tor argument')
    _shared.check_concept_dict(fields, 'c-tor argument')
    for field in fields:
      assert field in self._known_fields, "Unknown field."
      assert isinstance(fields[field], slice)
    #paranoid mode off
    self._info = _shared.parse_json_deep(info, dict) if isinstance(info, _six.string_types) else dict(info)
    assert 'Diagnostics' not in self._info
    self._info.update({'Diagnostics': [] if diagnostics is None else diagnostics})
    self._names = _Names(problem)
    self._fields = fields
    self._status = status
    self._solutions_data = _shared.as_matrix(solutions, name="'solutions' argument")
    self._solutions_data.setflags(write=False)
    self._solutions_subsets = dict(solutions_subsets) if solutions_subsets else \
                                {"new": slice(len(self._solutions_data)),
                                 "auto": slice(len(self._solutions_data)),
                                 "initial": slice(0, 0)}
    self._solutions_subsets["all"] = slice(len(self._solutions_data))
    self.solutions = _MethodWithProps(self._solutions)


    self._designs_filters = [[], ("feasible", "infeasible", "undefined", "potentially feasible")]

    self._payload_storage = None
    self._payload_solutions = []
    self._payload_designs = []

    if designs is not None:
      self._designs_data, self._designs_fields, self._designs_samples = designs
      self._designs_data.setflags(write=False)
      self._refine_design_filters()
    else:
      self._designs_data = _numpy.empty((0,0), dtype=float)
      self._designs_fields = ((),(),{})
      self._designs_samples = ((),{})

    self._designs_samples[1].setdefault("all", slice(len(self._designs_data)))
    self._designs_samples[1].setdefault("new", slice(0))
    self._designs_samples[1].setdefault("initial", slice(0))

    self.designs = _MethodWithCustomProps(self._designs, self._designs_fields[0])

    self._extended_fields = {}

    if self._names.x and 'x' in self._fields:
      for shift, var in enumerate(self._names.x):
        self._extended_fields.update({'x' + '.' + var: slice(self._fields['x'].start + shift, self._fields['x'].start + shift + 1)})

    if self._names.f:
      for field in ('f', 'fe'):
        if field in self._fields:
          for shift, var in enumerate(self._names.f):
            self._extended_fields.update({field + '.' + var: slice(self._fields[field].start + shift, self._fields[field].start + shift + 1)})

    if self._names.c:
      for field in ('c', 'ce', 'v', 've'):
        if field in self._fields:
          for shift, var in enumerate(self._names.c):
            self._extended_fields.update({field + '.' + var: slice(self._fields[field].start + shift, self._fields[field].start + shift + 1)})

    self._model = model
    self._default = tuple(field for field in ("x", "f", "c") \
        if (self._solutions_data[:, self._fields.get(field, slice(0))].size \
          or self._designs_data[:, self._designs_fields[2].get(field, slice(0))].size))
    if finalize:
      self._finalized = None

  def _finalize(self, problem, auto_objective_type, options, logger, intermediate_result=False):
    if not problem or hasattr(self, "_finalized"):
      return self

    modified = False

    try:
      self._capture_payload(problem)

      if _numpy.may_share_memory(self._solutions_data, self._designs_data):
        self._designs_data = self._designs_data.copy()

      with _make_writeable(self._solutions_data):
        modified = self._postprocess_solution(problem, auto_objective_type, options, logger, intermediate_result)

      if modified:
        # copy new solutions down to designs w.r.t different fields set
        self._copy_solutions_to_designs(problem, options)

      with _make_writeable(self._designs_data):
        # we don't read the modified state because this method affects flags only and snapshot marks flags itself
        self._mark_undefined_designs(problem, (auto_objective_type or "Minimize"))

      self._refine_design_filters()
      self._adopt_payload()
      self._inplace_sort_solutions()
    except:
      pass
    finally:
      # get a copy of the payload store
      self._finalized = None # finalize class
    return self

  def _inplace_sort_solutions(self):
    # sorting new solutions by designs as designs were aligned with the evaluation history
    try:
      new_solutions = self._solutions_data[self._solutions_subsets["new"], :]

      new_solutions_keys = new_solutions[:, self._fields["x"]]
      designs_keys = self._designs_data[:, self._designs_fields[2]["x"]]

      # Note the solutions is a subset of designs
      solutions_order = [_ for _ in _shared._enumerate_equal_keys(new_solutions_keys, designs_keys)]
      solutions_order = sorted(solutions_order, key=lambda idx: idx[1])

      with _make_writeable(self._solutions_data):
        self._solutions_data[self._solutions_subsets["new"]] = new_solutions[[i for i, _ in solutions_order]]
    except:
      pass # No worry, this is optional

  def _capture_payload(self, problem):
    self._payload_storage = None
    self._payload_solutions = []
    self._payload_designs = []

    try:
      # problem._payload_objectives corresponds to the "f" field only
      if not problem._payload_objectives:
        return

      solutions_base, solutions_last, solutions_stride = self._fields.get("f", slice(0)).indices(self._solutions_data.shape[1])
      self_payload_solutions = [(solutions_base + i * solutions_stride) for i in problem._payload_objectives if (solutions_base + i * solutions_stride) < solutions_last]

      designs_base, designs_last, designs_stride = self._designs_fields[2].get("f", slice(0)).indices(self._designs_data.shape[1])
      self_payload_designs = [(designs_base + i * designs_stride) for i in problem._payload_objectives if (designs_base + i * designs_stride) < designs_last]

      # create an empty storage and translate all codes
      if self_payload_solutions or self_payload_designs:
        self._payload_storage = problem._payload_storage
      self._payload_solutions = self_payload_solutions
      self._payload_designs = self_payload_designs
    except:
      pass

  def _adopt_payload(self):
    if not self._payload_storage:
      return

    try:
      payload_storage = type(self._payload_storage)()

      with _make_writeable(self._solutions_data):
        for i in self._payload_solutions:
          self._solutions_data[:, i] = payload_storage.adopt_encoded_payloads(self._payload_storage, self._solutions_data[:, i])

      with _make_writeable(self._designs_data):
        for i in self._payload_designs:
          self._designs_data[:, i] = payload_storage.adopt_encoded_payloads(self._payload_storage, self._designs_data[:, i])

      self._payload_storage = payload_storage
    except:
      pass

  def _copy_absent_responses(self, source_data, source_fields, source_payloads,\
                             destination_data, destination_fields, destination_payloads):
    if not source_data.size or not destination_data.size or ("stochastic" in source_fields) != ("stochastic" in destination_fields):
      return False

    source_dim, destination_dim = source_data.shape[1], destination_data.shape[1]
    source_column_map = _numpy.empty(destination_dim, dtype=int) # -1 or index of corresponding destination column
    source_column_map.fill(-1)

    for k in source_fields:
      if k in destination_fields:
        source_column_map[destination_fields[k]] = range(*source_fields[k].indices(source_dim))

    undefined_destination = _shared._find_holes(destination_data)
    undefined_destination = _numpy.logical_and(undefined_destination, (source_column_map >= 0).reshape(1, -1))
    for k in (destination_payloads or []):
      undefined_destination[:, k] = False

    if not undefined_destination.any():
      return False

    from .utils.designs import _input_sample_data

    destination_keys = _input_sample_data(destination_fields, destination_data)
    source_keys = _input_sample_data(source_fields, source_data)

    if source_payloads and destination_payloads:
      for source_idx, destination_idx in _shared._enumerate_equal_keys(source_keys, destination_keys):
        destination_mask, destination_vector, source_vector = undefined_destination[destination_idx], destination_data[destination_idx], source_data[source_idx]
        for i, j in zip(source_payloads, destination_payloads):
          destination_vector[j] = self._payload_storage.join_encoded_payloads(source_vector[i], destination_vector[j])
        destination_vector[destination_mask] = source_vector[source_column_map[destination_mask]]
    else:
      for source_idx, destination_idx in _shared._enumerate_equal_keys(source_keys, destination_keys):
        destination_mask, destination_vector, source_vector = undefined_destination[destination_idx], destination_data[destination_idx], source_data[source_idx]
        destination_vector[destination_mask] = source_vector[source_column_map[destination_mask]]

    return True

  def _copy_solutions_to_designs(self, problem, options):
    basic_fields, extra_fields, fields_spec = self._designs_fields

    with _make_writeable(self._designs_data):
      if not self._copy_absent_responses(source_data=self._solutions_data, source_fields=self._fields, source_payloads=self._payload_solutions,
                                destination_data=self._designs_data, destination_fields=fields_spec, destination_payloads=self._payload_designs):
        return

      if "v" in fields_spec and "flag" in fields_spec:
        # keep relative violation of constraints but refine flags
        _, constraints_tolerance = self._read_postprocess_options(options)
        _, deferred_constraints = problem._deferred_responses()
        _, self._designs_data[:, fields_spec["flag"]][:, 0] = problem._violation_coefficients_to_feasibility(constraints_violation=self._designs_data[:, fields_spec["v"]],
                                                                                                             violation_tolerance=constraints_tolerance,
                                                                                                             deferred_constraints=deferred_constraints)

    from .utils.designs import _filter_designs_fields

    basic_fields = sorted([_ for _ in fields_spec if _ not in extra_fields and "." not in _], key=fields_spec.get)
    extra_fields = sorted([_ for _ in fields_spec if _ not in basic_fields], key=fields_spec.get)
    self._designs_fields = _filter_designs_fields(self._designs_data, basic_fields, extra_fields, fields_spec)

  def _mark_undefined_designs(self, problem, auto_objective_type):
    # Quick checks. Note empty auto_objective_type indicates validation mode or optimization.
    if hasattr(self, "_finalized") or not problem or not self._designs_data.size:
      return

    if "flag" not in self._designs_fields[2]:
      invalid_objectives = _numpy.isnan(self._designs_data[:, self._designs_fields[2].get("f", slice(0))]).any(axis=1)
      invalid_constraints = _numpy.isnan(self._designs_data[:, self._designs_fields[2].get("c", slice(0))]).any(axis=1)

      if not invalid_objectives.any() and not invalid_constraints.any():
        return

      self._designs_data = _shared._pad_columns(self._designs_data, 1, GT_SOLUTION_TYPE_CONVERGED)
      self._designs_data[:, -1][(invalid_objectives | invalid_constraints)] = GT_SOLUTION_TYPE_INFEASIBLE

    designs_flags = self._designs_data[:, self._designs_fields[2]["flag"]][:, 0]

    undefined_objectives = _shared._find_holes(self._designs_data[:, self._designs_fields[2].get("f", slice(0))])
    if undefined_objectives.any():
      for kind, undefined in zip(_read_objectives_type(problem, (auto_objective_type or "minimize").lower()), undefined_objectives.T):
        if kind in ("minimize", "maximize") and undefined.any():
          designs_flags[_numpy.logical_and(designs_flags == GT_SOLUTION_TYPE_INFEASIBLE, undefined)] = GT_SOLUTION_TYPE_INFEASIBLE_NAN
          designs_flags[_numpy.logical_and(designs_flags == GT_SOLUTION_TYPE_CONVERGED, undefined)] = GT_SOLUTION_TYPE_FEASIBLE_NAN

  def _refine_design_filters(self):
    active_designs_filters = []

    if "flag" in self._designs_fields[1]:
      flags = self._designs_data[:, self._designs_fields[2]["flag"]][:, 0]

      if (flags == GT_SOLUTION_TYPE_CONVERGED).any():
        active_designs_filters.append("feasible")

      if (flags != GT_SOLUTION_TYPE_CONVERGED).any():
        active_designs_filters.append("infeasible")
        if (flags == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE).any():
          active_designs_filters.append("potentially feasible")
          active_designs_filters.append("undefined")
        elif (flags == GT_SOLUTION_TYPE_NOT_EVALUATED).any():
          active_designs_filters.append("undefined")
    elif len(self._designs_data):
      active_designs_filters.append("feasible")

    self._designs_filters[0] = active_designs_filters

  def _read_postprocess_options(self, options):
    # select which kind of points must be totally evaluated
    total_evaluation_subset, constraints_tolerance = "auto", 1.e-5
    try:
      option_manager = _options._OptionManager('GTOpt/')
      option_reader = _options.Options(option_manager.pointer, None)
      option_reader.set(options)
      total_evaluation_subset = option_reader.get("/GTOpt/EvaluateResultSubset").lower()
      constraints_tolerance = float(option_reader.get("GTOpt/ConstraintsTolerance"))
    except:
      pass
    return total_evaluation_subset, constraints_tolerance

  def _postprocess_solution(self, problem, auto_objective_type, options, logger, intermediate_result=False):
    self._check_extended_fields("x", problem.variables_names())

    if not len(self._solutions_data):
      return False

    if not problem.size_full():
      # no responses - nothing to evaluate or classify, all points are feasible and optimal by default
      if "flag" in self._fields:
        return False

      self._solutions_data, self._fields = _required_solution_field(self._solutions_data, self._fields, "flag", 1)
      self._solutions_data[:, self._fields['flag']][:, 0] = GT_SOLUTION_TYPE_NOT_DOMINATED

      return True

    # In case of space-filling DoE, designs may contain more data than the solutions
    self._copy_absent_responses(source_data=self._designs_data, source_fields=self._designs_fields[2], source_payloads=self._payload_designs,
                                destination_data=self._solutions_data, destination_fields=self._fields, destination_payloads=self._payload_solutions)

    options = options or {}
    if auto_objective_type:
      auto_objective_type = auto_objective_type.lower()

    # enumerate objectives for pareto-optimal solution, do nothing if auto_objective_type is None
    objectives_type = _read_objectives_type(problem, (auto_objective_type or "minimize").lower())
    pareto_optimal_objectives = [] # list of (index, kind) tuples

    # The list of responses that affects "optimality" set. If optimality_responses is empty then all feasible points are optimal
    optimality_responses = [i for i, k in enumerate(objectives_type) if k in ("minimize", "maximize")]

    if auto_objective_type:
      pareto_optimal_objectives = [(i, k) for i, k in enumerate(objectives_type) if k in ("minimize", "maximize")]
      if auto_objective_type != "minimize":
        options = dict(options) # make deep copy before modification
        options["GTOpt/OptimalSetType"] = "Strict" # Don't include infeasible points because we don't have special code for the "infeasible, optimal" solution.

    from .loggers import LogLevel as _LogLevel

    logger = logger or _shared.Logger()

    # select which kind of points must be totally evaluated
    total_evaluation_subset, constraints_tolerance = self._read_postprocess_options(options)

    modified, constraints_violation_ex, feasibility_code = False, None, None
    size_f, size_c = problem.size_f(), problem.size_c()
    responses_evaluation_allowed = not intermediate_result and not problem.size_nf() and not problem.size_nc() # We cannot evaluate responses if the problem uses black box noise.

    if responses_evaluation_allowed:
      try:
        evaluation_mask = _numpy.zeros((self._solutions_data.shape[0], problem.size_full()), dtype=bool)

        # Evaluate deferred responses. Most likely, the space filling DoE has not yet evaluated the responses.
        if total_evaluation_subset in ("all", "new", "initial", "auto"):
          # special evaluation subset - evaluate all objectives and constraints if any
          evaluation_mask[self._solutions_subsets.get(total_evaluation_subset, slice(0))] = True
        elif total_evaluation_subset == "feasible" or (total_evaluation_subset == "optimal" and not pareto_optimal_objectives):
          # The second condition means that all feasible points are optimal if there are no Pareto optimal objectives.
          if not self._solutions_data[:, self._fields.get("c", slice(0))].size:
            # All points are feasible if there are no constraints (or if we don't have constraints values)
            evaluation_mask.fill(True)
          else:
            # Evaluate feasibility
            constraints_violation_ex, feasibility_code, modified = self._refine_feasibility(problem=problem, constraints_tolerance=constraints_tolerance)
            evaluation_mask[feasibility_code == GT_SOLUTION_TYPE_CONVERGED] = True

        if pareto_optimal_objectives and not evaluation_mask.all():
          # We must evaluate pareto-optimal objectives as well
          for i, _ in pareto_optimal_objectives:
            evaluation_mask[:, i] = True

          if feasibility_code is None:
            # We must know feasibility in this case
            constraints_violation_ex, feasibility_code, modified = self._refine_feasibility(problem=problem, constraints_tolerance=constraints_tolerance)
            evaluation_mask[:, size_f:(size_f + size_c)] = False
          if feasibility_code is not None and options.get("GTOpt/OptimalSetType", "").lower() == "strict" \
             and (not auto_objective_type or auto_objective_type == "minimize"):
              # This is an optimization problem or GFO minimization problem.
              # Do not evaluate objectives for infeasible points in strict mode.
              infeasible_mask = (feasibility_code == GT_SOLUTION_TYPE_INFEASIBLE) + (feasibility_code == GT_SOLUTION_TYPE_BLACKBOX_NAN)
              evaluation_mask[infeasible_mask, :size_f] = False

        # Don't evaluate gradients and already known responses
        evaluation_mask = self._normalize_evaluation_mask(problem, evaluation_mask)

        if evaluation_mask.any():
          evaluation_name = ", ".join(name for i, name in enumerate(problem.objectives_names() + problem.constraints_names()) if evaluation_mask[:, i].any())
          logger(_LogLevel.INFO, 'Evaluating undefined ' + evaluation_name + '...')

          restore_mode = _shared.parse_auto_bool(options.get("GTOpt/RestoreAnalyticResponses", "auto"), "auto")
          if restore_mode:
            evaluation_mask, responses_reconstructed = self._refill_linear_responses(problem, evaluation_mask, logger)
            if responses_reconstructed:
              modified = True

          evaluation_mask = self._evaluate_solutions_data(problem, evaluation_mask)
          if evaluation_mask.any():
            modified = True
            if evaluation_mask[:, size_f:(size_f+size_c)].any():
              constraints_violation_ex, feasibility_code = None, None
      except:
        # no drama, just emit a warning
        exc_info = _sys.exc_info()
        logger(_LogLevel.WARN, "Failed to evaluate %s points of design: %s" % (total_evaluation_subset, exc_info[1],))

      self._reset_evaluation_error(problem, logger)

    optimality_marks = self._solutions_data[:, self._fields["flag"]][:, 0] if ("flag" in self._fields and not auto_objective_type) else None

    if pareto_optimal_objectives:
      # Apply SBO Pareto-optimality filter
      failure_prefix = ""
      try:
        failure_prefix = "Failed to classify solutions: "
        target_objective = self._solutions_data[:, self._fields.get("f", slice(0))]
        target_objective = _numpy.hstack([_optional_negative_numbers(target_objective[:, i], (target == "maximize")).reshape(-1, 1) for i, target in pareto_optimal_objectives])

        optimality_marks = solution_filter(x=self._solutions_data[:, self._fields.get("x", slice(0))],
                                          f=target_objective, c=self._solutions_data[:, self._fields.get("c", slice(0))],
                                          c_bounds=problem.constraints_bounds(), df=self._solutions_data[:, self._fields.get("nf", slice(0))],
                                          dc=self._solutions_data[:, self._fields.get("nc", slice(0))], options=options)

        failure_prefix = "Failed to evaluate optimal responses: "
        if total_evaluation_subset == "optimal" and responses_evaluation_allowed:
          # Do it withing the "if pareto_optimal_objectives" block because otherwise we'd evaluated these points
          evaluation_mask = _numpy.zeros((self._solutions_data.shape[0], problem.size_full()), dtype=bool)
          evaluation_mask[:, :(size_f+size_c)][(optimality_marks == GT_SOLUTION_TYPE_CONVERGED)] = True
          evaluation_mask[:, :(size_f+size_c)][(optimality_marks == GT_SOLUTION_TYPE_NOT_DOMINATED)] = True

          # Don't evaluate gradients and already known responses
          evaluation_mask = self._normalize_evaluation_mask(problem, evaluation_mask)

          if evaluation_mask.any():
            logger(_LogLevel.INFO, "Evaluating responses at optimal points...")
            evaluation_mask = self._evaluate_solutions_data(problem, evaluation_mask)
            if evaluation_mask.any():
              modified = True
              if evaluation_mask[:, size_f:(size_f+size_c)].any():
                constraints_violation_ex, feasibility_code = None, None
      except:
        # no drama, just emit a warning
        exc_info = _sys.exc_info()
        logger(_LogLevel.WARN, failure_prefix + str(exc_info[1]))

      self._reset_evaluation_error(problem, logger)

    constraints_values = self._solutions_data[:, self._fields.get("c", slice(0))]
    if constraints_values.size:
      # Setup constraints violations
      if feasibility_code is None:
        constraints_violation_ex, feasibility_code = problem._evaluate_psi(c_values=constraints_values, c_tol=constraints_tolerance)

      # Simplify codes to 4 states: feasible, infeasible, not evaluated, potentially feasible
      feasibility_code[feasibility_code == GT_SOLUTION_TYPE_BLACKBOX_NAN] = GT_SOLUTION_TYPE_INFEASIBLE

      self._solutions_data, self._fields = _required_solution_field(self._solutions_data, self._fields, "v", size_c)
      self._solutions_data, self._fields = _required_solution_field(self._solutions_data, self._fields, "psi", 1)

      self._solutions_data[:, self._fields["v"]] = constraints_violation_ex[:, :-1]
      self._solutions_data[:, self._fields["psi"]] = constraints_violation_ex[:, -1:]

      modified = True # we've just updated relative violations of constraints

    # All filters above do not mark absent objectives evaluations.
    objectives_values = self._solutions_data[:, self._fields.get("f", slice(0))]
    if optimality_responses and objectives_values.size:
      if optimality_marks is None:
        optimality_marks = _numpy.empty(len(self._solutions_data))
        optimality_marks.fill(GT_SOLUTION_TYPE_NOT_DOMINATED)
        if feasibility_code is not None:
          optimality_marks[feasibility_code != GT_SOLUTION_TYPE_CONVERGED] = GT_SOLUTION_TYPE_DISCARDED

      if len(optimality_responses) < len(objectives_type):
        objectives_values = objectives_values[:, optimality_responses]

      undefined_objectives = _shared._find_holes(objectives_values)
      optimality_marks[undefined_objectives.any(axis=1)] = GT_SOLUTION_TYPE_NOT_EVALUATED
      optimality_marks[_numpy.logical_and(_numpy.isnan(objectives_values), ~undefined_objectives).any(axis=1)] = GT_SOLUTION_TYPE_BLACKBOX_NAN

    # Setup flags
    if feasibility_code is not None or optimality_marks is not None:
      self._solutions_data, self._fields = _required_solution_field(self._solutions_data, self._fields, "flag", 1)
      flags_vector = self._solutions_data[:, self._fields['flag']][:, 0]
      modified = True # we are going to update flags

      if feasibility_code is None:
        # All points are feasible by definition
        flags_vector[:] = optimality_marks
        if not pareto_optimal_objectives:
          flags_vector[optimality_marks == GT_SOLUTION_TYPE_DISCARDED] = GT_SOLUTION_TYPE_NOT_DOMINATED
        flags_vector[optimality_marks == GT_SOLUTION_TYPE_NOT_EVALUATED] = GT_SOLUTION_TYPE_FEASIBLE_NAN
        flags_vector[optimality_marks == GT_SOLUTION_TYPE_BLACKBOX_NAN] = GT_SOLUTION_TYPE_DISCARDED
        # the following cases are impossible
        flags_vector[optimality_marks == GT_SOLUTION_TYPE_INFEASIBLE] = GT_SOLUTION_TYPE_DISCARDED
        flags_vector[optimality_marks == GT_SOLUTION_TYPE_INFEASIBLE_NAN] = GT_SOLUTION_TYPE_FEASIBLE_NAN
        flags_vector[optimality_marks == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE] = GT_SOLUTION_TYPE_FEASIBLE_NAN
      elif optimality_marks is None:
        flags_vector[:] = feasibility_code  # Use feasibility markers as a basis
        flags_vector[feasibility_code == GT_SOLUTION_TYPE_CONVERGED] = GT_SOLUTION_TYPE_NOT_DOMINATED
      else:
        # potentially feasible points and those that are undefined due to constraints keep their status
        flags_vector[feasibility_code == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE] = GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE
        flags_vector[feasibility_code == GT_SOLUTION_TYPE_NOT_EVALUATED] = GT_SOLUTION_TYPE_NOT_EVALUATED

        if not pareto_optimal_objectives:
          optimality_marks[optimality_marks == GT_SOLUTION_TYPE_DISCARDED] = GT_SOLUTION_TYPE_NOT_DOMINATED

        # Feasible points can be either
        feasible_points = feasibility_code == GT_SOLUTION_TYPE_CONVERGED
        flags_vector[feasible_points] = optimality_marks[feasible_points]
        #flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_DISCARDED)] = GT_SOLUTION_TYPE_DISCARDED # feasible, not optimal
        #flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_CONVERGED)] = GT_SOLUTION_TYPE_CONVERGED
        #flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_NOT_DOMINATED)] = GT_SOLUTION_TYPE_NOT_DOMINATED
        #flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_INFEASIBLE)] = GT_SOLUTION_TYPE_DISCARDED # cannot be
        flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_BLACKBOX_NAN)] = GT_SOLUTION_TYPE_DISCARDED # feasible, not optimal
        flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_NOT_EVALUATED)] = GT_SOLUTION_TYPE_FEASIBLE_NAN # feasible, undefined
        #flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_FEASIBLE_NAN)] = GT_SOLUTION_TYPE_FEASIBLE_NAN # feasible, undefined
        #flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_INFEASIBLE_NAN)] = GT_SOLUTION_TYPE_FEASIBLE_NAN # cannot be
        #flags_vector[_numpy.logical_and(feasible_points, optimality_marks == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE)] = GT_SOLUTION_TYPE_DISCARDED # cannot be

        infeasible_points = feasibility_code == GT_SOLUTION_TYPE_INFEASIBLE
        flags_vector[infeasible_points] = GT_SOLUTION_TYPE_INFEASIBLE
        #flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_DISCARDED)] = GT_SOLUTION_TYPE_INFEASIBLE # infeasible, not optimal
        #flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_CONVERGED)] = GT_SOLUTION_TYPE_INFEASIBLE # infeasible, we don't have the "optimal infeasible" mark
        #flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_NOT_DOMINATED)] = GT_SOLUTION_TYPE_INFEASIBLE # infeasible, we don't have the "optimal infeasible" mark
        #flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_INFEASIBLE)] = GT_SOLUTION_TYPE_INFEASIBLE
        #flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_BLACKBOX_NAN)] = GT_SOLUTION_TYPE_INFEASIBLE # infeasible, not optimal
        flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_NOT_EVALUATED)] = GT_SOLUTION_TYPE_INFEASIBLE_NAN # infeasible, undefined
        #flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_FEASIBLE_NAN)] = GT_SOLUTION_TYPE_INFEASIBLE # cannot be
        flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_INFEASIBLE_NAN)] = GT_SOLUTION_TYPE_INFEASIBLE_NAN # infeasible, undefined
        #flags_vector[_numpy.logical_and(infeasible_points, optimality_marks == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE)] = GT_SOLUTION_TYPE_INFEASIBLE # cannot be
    elif 'flag' in self._fields and (self._solutions_data[:, self._fields['flag']][:, 0] != GT_SOLUTION_TYPE_NOT_DOMINATED).any():
      # all points must be feasible (because there are no constraints) and optimal (because there are no min/max)
      self._solutions_data[:, self._fields['flag']][:, 0] = GT_SOLUTION_TYPE_NOT_DOMINATED
      modified = True

    if self._reveal_potentially_optimal_solutions(pareto_optimal_objectives=pareto_optimal_objectives,
                                                  deferred_objectives=problem._deferred_responses()[0],
                                                  options=options):
      modified = True

    self._check_extended_fields("f", problem.objectives_names())
    self._check_extended_fields("c", problem.constraints_names())
    self._check_extended_fields("v", problem.constraints_names())

    return modified

  def _reveal_potentially_optimal_solutions(self, pareto_optimal_objectives, deferred_objectives, options):
    flags_vector = self._solutions_data[:, self._fields.get('flag', slice(0))]
    if not flags_vector.size:
      return False
    flags_vector = flags_vector[:, 0]

    # We must not ignore an empty pareto_optimal_objectives because in this case potentially feasible points are potentially optimal

    target_objective = self._solutions_data[:, self._fields.get("f", slice(0))]
    if any(target == "maximize" for _, target in pareto_optimal_objectives):
      target_objective = _numpy.hstack([_optional_negative_numbers(target_objective[:, i], (target == "maximize")).reshape(-1, 1) for i, target in pareto_optimal_objectives])

    # A set of potentially feasible points with known objectives that are not dominated by feasible points with known objectives.
    potentially_optimal = self._non_dominated_potentially_feasible_solutions(flags_vector=flags_vector, target_objective=target_objective, options=options)

    if deferred_objectives.any():
      # Pooling with "feasible" or "potentially feasible" points that have undefined deferred objectives
      deferred_evaluations = _numpy.zeros((len(target_objective),), dtype=bool)
      for i, _ in pareto_optimal_objectives:
        if deferred_objectives[i]:
          deferred_evaluations = _numpy.logical_or(deferred_evaluations, _shared._find_holes(target_objective[:, i]))

      feasible_like_points = (flags_vector == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE) \
                           | (flags_vector == GT_SOLUTION_TYPE_DISCARDED) \
                           | (flags_vector == GT_SOLUTION_TYPE_FEASIBLE_NAN)
      potentially_optimal[_numpy.logical_and(deferred_evaluations, feasible_like_points)] = True

    # Check before pooling with optimal points, we don't want to have two identical sets.
    if not potentially_optimal.any():
      return False

    if pareto_optimal_objectives:
      # Pooling with optimal points.
      potentially_optimal |= (flags_vector == GT_SOLUTION_TYPE_CONVERGED)
      potentially_optimal |= (flags_vector == GT_SOLUTION_TYPE_NOT_DOMINATED)

      # Potentially optimal set is mutually exclusive with optimal set,
      # but only if there are pareto-optimal objectives.
      # Otherwise, optimality is based on the feasibility.
      flags_vector[flags_vector == GT_SOLUTION_TYPE_CONVERGED] = GT_SOLUTION_TYPE_DISCARDED
      flags_vector[flags_vector == GT_SOLUTION_TYPE_NOT_DOMINATED] = GT_SOLUTION_TYPE_DISCARDED

    self._fields["_optimal"] = slice(self._solutions_data.shape[1], self._solutions_data.shape[1] + 1)
    self._solutions_data = _shared._pad_columns(self._solutions_data, 1, GT_SOLUTION_TYPE_DISCARDED)
    self._solutions_data[:, -1][potentially_optimal] = GT_SOLUTION_TYPE_CONVERGED


    return True # we are going to update flags

  def _non_dominated_potentially_feasible_solutions(self, flags_vector, target_objective, options):
    #   0. Let set A is "potentially feasible" points with completely defined objectives
    #   1. Let set B is empty
    #   2. Find the Pareto optimal set S from the pooled sets A and the "optimal"
    #   3. Let set C be the intersection of sets A and S. If C is not empty, move set C from set A to set B and repeat step 2.
    #   4. Set B is a solution — the “optimal” set does not dominate these points.

    potentially_optimal_candidates = (flags_vector == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE)

    failure_prefix = ""
    try:
      failure_prefix = "Failed to classify solutions: "

      inputs = self._solutions_data[:, self._fields.get("x", slice(0))]

      fake_bounds = ((-1.,), (1.,))
      fake_constraints = _numpy.empty(len(flags_vector))
      fake_constraints[:] = -1000. # ignore by default

      fake_constraints[flags_vector == GT_SOLUTION_TYPE_CONVERGED] = 0. # take optimal points
      fake_constraints[flags_vector == GT_SOLUTION_TYPE_NOT_DOMINATED] = 0. # take optimal points too
      fake_constraints[potentially_optimal_candidates] = 0. # take all potentially feasible

      non_dominated_potentially_feasible = potentially_optimal_candidates # initialization
      while non_dominated_potentially_feasible.any():
        optimality_marks = solution_filter(x=inputs, f=target_objective, c=fake_constraints, c_bounds=fake_bounds, options=options)
        non_dominated_potentially_feasible = _numpy.logical_and(_numpy.logical_or((optimality_marks == GT_SOLUTION_TYPE_CONVERGED),
                                                                                  (optimality_marks == GT_SOLUTION_TYPE_NOT_DOMINATED)),
                                                                potentially_optimal_candidates)
        fake_constraints[non_dominated_potentially_feasible] = 1000. # mark non-dominated potentially feasible points and exclude these points from the account
      potentially_optimal_candidates = (fake_constraints > 1.)
    except:
      # no drama, just emit a warning
      pass

    # If error occurred then threat all potentially feasible as potentially optimal
    return potentially_optimal_candidates

  def _check_extended_fields(self, base_field, names_list):
    names_list = names_list[:self._solutions_data[:, self._fields.get(base_field, slice(0))].shape[1]]
    if not names_list:
      return

    field_offset = self._fields[base_field].start or 0
    for name in names_list:
      self._extended_fields[base_field + "." + name] = slice(field_offset, field_offset + 1)
      field_offset += 1

  def _refine_feasibility(self, problem, constraints_tolerance):
    constraints_values = self._solutions_data[:, self._fields.get("c", slice(0))]
    if not constraints_values.size:
      return None, None, False

    constraints_violation_ex, feasibility_code = problem._evaluate_psi(c_values=constraints_values, c_tol=constraints_tolerance)
    defined_points = _numpy.logical_and((feasibility_code != GT_SOLUTION_TYPE_NOT_EVALUATED), (feasibility_code != GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE))
    if defined_points.all():
      return constraints_violation_ex, feasibility_code, False

    size_x, size_f, size_c = problem.size_x(), problem.size_f(), problem.size_c()

    from .gtopt.problem import _backend
    default_cost_type = _backend.default_option_value("@GTOpt/EvaluationCostType")

    active_constraints = _numpy.zeros(problem.size_full(), dtype=bool)
    active_constraints[size_f:(size_f+size_c)] = _numpy.array([str(cost or default_cost_type).lower() == "cheap" for cost in problem.elements_hint(slice((size_x+size_f), (size_x+size_f+size_c)), "@GTOpt/EvaluationCostType")], dtype=bool)

    modified = False
    evaluation_mask = _numpy.empty((len(self._solutions_data), len(active_constraints)), dtype=bool)

    # evaluate cheap constraints first
    if active_constraints.any():
      evaluation_mask.fill(False)
      evaluation_mask[:, active_constraints] = True
      evaluation_mask[defined_points] = False

      evaluation_mask = self._evaluate_solutions_data(problem, evaluation_mask)

      if evaluation_mask.any():
        constraints_values = self._solutions_data[:, self._fields.get("c", slice(0))]
        constraints_violation_ex, feasibility_code = problem._evaluate_psi(c_values=constraints_values, c_tol=constraints_tolerance)
        defined_points = _numpy.logical_and((feasibility_code != GT_SOLUTION_TYPE_NOT_EVALUATED), (feasibility_code != GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE))
        modified = True

    active_constraints[size_f:(size_f+size_c)] = ~active_constraints[size_f:(size_f+size_c)] # switch to expensive constraints

    if defined_points.all() or not active_constraints.any():
      return constraints_violation_ex, feasibility_code, modified

    # evaluate expensive constraints
    evaluation_mask.fill(False)
    evaluation_mask[:, active_constraints] = True
    evaluation_mask[defined_points] = False

    evaluation_mask = self._evaluate_solutions_data(problem, evaluation_mask)

    if evaluation_mask.any():
      constraints_values = self._solutions_data[:, self._fields.get("c", slice(0))]
      constraints_violation_ex, feasibility_code = problem._evaluate_psi(c_values=constraints_values, c_tol=constraints_tolerance)
      modified = True

    return constraints_violation_ex, feasibility_code, modified

  def _normalize_evaluation_mask(self, problem, evaluation_mask):
    size_f = problem.size_f()
    size_fc = size_f + problem.size_c()

    evaluation_mask[:, size_fc:] = False # don't evaluate gradients

    for i in problem._payload_objectives:
      evaluation_mask[:, i] = False # never evaluate payload

    objectives_values = self._solutions_data[:, self._fields.get("f", slice(0))]
    if objectives_values.size:
      evaluation_mask[:, :size_f] = _numpy.logical_and(evaluation_mask[:, :size_f], _shared._find_holes(objectives_values))

    constraints_values = self._solutions_data[:, self._fields.get("c", slice(0))]
    if constraints_values.size:
      evaluation_mask[:, size_f:size_fc] = _numpy.logical_and(evaluation_mask[:, size_f:size_fc], _shared._find_holes(constraints_values))

    return evaluation_mask

  def _refill_linear_responses(self, problem, evaluation_mask, logger):
    if problem.size_s():
      # stochastic problem, cannot reconstruct
      return evaluation_mask, False

    size_x, size_f, size_c = problem.size_x(), problem.size_f(), problem.size_c()
    if not size_f and not size_c:
      return evaluation_mask, False

    if logger:
      from .loggers import LogLevel as _LogLevel

    linearity_type = [(hint or 'generic').lower() == 'linear' for hint in problem.elements_hint(slice(size_x, size_x+size_f+size_c), "@GTOpt/LinearityType")]
    if not any(linearity_type):
      return evaluation_mask, False

    input_data = self._solutions_data[:, self._fields["x"]]

    # preprocessing: filter out fully qualified responses and evaluate responses using weights provided by the user
    for resp_index, weights in enumerate(problem.elements_hint(slice(size_x, size_x+size_f+size_c), "@GTOpt/LinearParameterVector")):
      response, known_points = self._single_response_data(problem, resp_index)
      if known_points.all():
        linearity_type[resp_index] = False
      elif weights is not None and len(weights) in (size_x, size_x+1):
        response[~known_points] = _numpy.dot(input_data[~known_points], weights[:size_x]) + (weights[size_x] if len(weights) > size_x else 0.)
        evaluation_mask[:, resp_index] = False
        linearity_type[resp_index] = False

    if not any(linearity_type):
      return evaluation_mask, False

    categorical_variables = _numpy.array([str(_ or 'continuous').lower() == 'categorical' for _ in problem.elements_hint(slice(problem.size_x()), "@GT/VariableType")], dtype=bool)
    if categorical_variables.all():
      return evaluation_mask, False

    reconstruction_mask = _numpy.empty_like(evaluation_mask)
    _, points_within_problem_bounds = problem._valid_input_points(input_data) # we don't need rounded x
    responses_names = problem.objectives_names() + problem.constraints_names()
    reconstructed = False

    for resp_index, basic_response_name in enumerate(responses_names):
      if not linearity_type[resp_index]:
        continue

      for combination_value, combination_mask, combination_name in self._enumerate_categorical_samples(problem, categorical_variables):
        # Some variables may be fixed withing combination
        active_inputs, active_inputs_eps = _numpy.empty(size_x, dtype=bool), _numpy.finfo(float).eps
        for i, (lb, ub) in enumerate(zip(*problem.variables_bounds())):
          active_inputs[i] = _numpy.ptp(input_data[combination_mask, i]) > abs(ub - lb) * active_inputs_eps
        if active_inputs.all():
          active_inputs = slice(size_x)
        elif not active_inputs.any():
          active_inputs = slice(0)

        response_name = basic_response_name + combination_name
        response, known_points = self._single_response_data(problem, resp_index)
        if not self._reconstructible_response(known_points[combination_mask], response[combination_mask], logger, response_name):
          continue

        err_desc = _ctypes.c_void_p()

        test_input_mask = known_points.copy() # we always can use known points
        test_input_mask[points_within_problem_bounds] = True # points_within_problem_bounds may be slice
        test_input_mask = self._inplace_safe_and(test_input_mask, combination_mask)

        test_input_data = input_data[test_input_mask][:, active_inputs] # input_data now only contains points that are allowed to be evaluated
        selected_points = known_points[test_input_mask].astype(dtype=_ctypes.c_short) # a priory select points with known responses

        if not test_input_data.shape[0]:
          if logger:
            logger(_LogLevel.WARN, "Unable to reconstruct linear response '" + response_name + "': insufficient points may be evaluated.")
          continue
        elif not test_input_data.shape[1]:
          # all inputs are constant
          if not selected_points.any():
            selected_points[0] = 1
        elif not _api.d_optimal_design(test_input_data.shape[0], test_input_data.shape[1],
                                      test_input_data.ctypes.data_as(_api._c_double_p),
                                      _ctypes.cast(test_input_data.ctypes.strides, _api._c_size_p),
                                      selected_points.ctypes.data_as(_api._c_short_p),
                                      selected_points.strides[0], _ctypes.byref(err_desc)):
          _, message = _shared._release_error_message(err_desc)
          if logger:
            logger(_LogLevel.WARN, ": ".join(("Failed to select design for reconstruction of linear response " + response_name, message or "")))
          continue

        selected_points = selected_points != 0
        if not selected_points.any() or selected_points.all():
          # No reconstruction, we cannot save evaluations in this case.
          continue

        reconstruction_mask.fill(False)
        reconstruction_mask[:, resp_index][test_input_mask] = selected_points # len(selected_points) <= len(test_input_mask)
        reconstruction_mask[:, resp_index][known_points] = False

        if reconstruction_mask.any():
          # on input, the reconstruction_mask indicates points to evaluate
          # on output, the reconstruction_mask indicates evaluated points
          reconstruction_mask = self._evaluate_solutions_data(problem, reconstruction_mask)
          _numpy.logical_and(evaluation_mask, ~reconstruction_mask, out=evaluation_mask)
          response, known_points = self._single_response_data(problem, resp_index)
          if not self._reconstructible_response(known_points[combination_mask], response[combination_mask], logger, response_name):
            continue

        known_points = self._inplace_safe_and(known_points, combination_mask)
        weights = self._reconstruct_linear_responses(input_data[known_points], response[known_points], active_inputs, 
                                                     x_bounds=problem.variables_bounds())

        if weights is not None:
          reconstructed = True
          if logger:
            logger(_LogLevel.INFO, "  - using reconstructed " + response_name + "=" + problem._regression_string(weights, "<reconstructed>", 15))
          restore_points = self._inplace_safe_and(~known_points, combination_mask)
          response[restore_points] = _numpy.dot(input_data[restore_points], weights[:-1]) + weights[-1]
          evaluation_mask[restore_points, resp_index] = False
          reconstructed = True # solutions was modified

          # refill corresponding column of designs
          with _make_writeable(self._designs_data):
            designs_response = self._designs_data[:, self._designs_fields[2]["f"]][:, resp_index] if resp_index < size_f else \
                              self._designs_data[:, self._designs_fields[2]["c"]][:, (resp_index - size_f)]
            refill_designs_mask = _shared._find_holes(designs_response)
            if refill_designs_mask.any():
              designs_input = self._designs_data[:, self._designs_fields[2]["x"]]
              if combination_value is not None:
                refill_designs_mask = _numpy.logical_and(refill_designs_mask, (_shared._make_dataset_keys(designs_input[:, categorical_variables]) == combination_value.reshape(1, -1)).all(axis=1))
              if refill_designs_mask.any():
                if refill_designs_mask.all():
                  refill_designs_mask = slice(0, len(designs_response))
                designs_response[refill_designs_mask] = _numpy.dot(designs_input[refill_designs_mask], weights[:-1]) + weights[-1]
        elif logger:
          logger(_LogLevel.WARN, "Unable to reconstruct linear response '" + response_name + "': insufficient points were evaluated.")

    return evaluation_mask, reconstructed

  def _single_response_data(self, problem, resp_index):
    # _refill_linear_responses helper method
    size_f = problem.size_f()
    response = self._solutions_data[:, self._fields['f']][:, resp_index] if resp_index < size_f else \
               self._solutions_data[:, self._fields['c']][:, (resp_index - size_f)]
    return response, ~_shared._find_holes(response)

  def _enumerate_categorical_samples(self, problem, categorical_variables):
    # _refill_linear_responses helper method
    if not categorical_variables.any():
      yield None, slice(len(self._solutions_data)), ""
      return

    categorical_variables_name = [name for categorical, name in zip(categorical_variables, problem.variables_names()) if categorical]
    categorical_inputs = _shared._make_dataset_keys(self._solutions_data[:, self._fields['x']][:, categorical_variables])

    from .utils.designs import _unique_rows_indices

    for unique_combination_index in _unique_rows_indices(categorical_inputs):
      combination_mask = (categorical_inputs == categorical_inputs[unique_combination_index].reshape(1, -1)).all(axis=1)
      combination_name = "|{" + "; ".join(name+"="+str(value) for name, value in zip(categorical_variables_name, categorical_inputs[unique_combination_index])) + "}"
      yield categorical_inputs[unique_combination_index], combination_mask, combination_name

  @staticmethod
  def _reset_evaluation_error(problem, logger):
    last_error = getattr(problem, "_last_error", None)
    if last_error:
      setattr(problem, "_last_error", None)
      if logger:
        from .loggers import LogLevel as _LogLevel
        exception_report = ''.join(_shared._format_user_only_exception(*last_error))
        logger(_LogLevel.WARN, "Failed to evaluate design. {}".format(exception_report))

  @staticmethod
  def _reconstructible_response(known_points, response, logger, response_name):
    # _refill_linear_responses helper method
    if known_points.all():
      return False
    elif not _numpy.isfinite(response[known_points]).all():
      if logger:
        from .loggers import LogLevel as _LogLevel
        logger(_LogLevel.WARN, "Unable to reconstruct linear response '" + response_name + "': NaN or infinite value detected.")
      return False
    return True

  @staticmethod
  def _inplace_safe_and(mask1, mask2):
    # _refill_linear_responses helper method
    if isinstance(mask2, slice):
      first, last, _ = mask2.indices(len(mask1))
      mask1[:first] = False
      mask1[last:] = False
      return mask1
    return _numpy.logical_and(mask1, mask2, out=mask1)

  def _reconstruct_linear_responses(self, x, resp, active_x, x_bounds=None):
    # _refill_linear_responses helper method
    if not len(x):
      return None

    x_recons = x[:, active_x]
    if not x_recons.shape[1]:
      return None if _numpy.ptp(resp) > 1.e-14*_numpy.abs(resp).max() else _numpy.array([0]*x.shape[1] + [_numpy.mean(resp)])
    elif x_recons.shape[0] <= x_recons.shape[1]:
      return None

    from .gtopt import utils as _utils

    try:
      if x_bounds is not None:
        x_bounds = _shared.as_matrix(x_bounds, shape=(2, x.shape[1]))
        x_bounds = x_bounds[:, active_x]
    except:
      x_bounds = None

    if x_recons.shape[0] <= (x_recons.shape[1] + 1):
      weights_recons, _ = _utils._linear_rsm_fit(x_recons, resp[:, _numpy.newaxis], x_bounds=x_bounds)
    else:
      weights_recons, rrms = _utils._linear_rsm_stepwise_fit(x_recons, resp[:, _numpy.newaxis], x_bounds=x_bounds)
      if rrms >= 1.:
        return None

    weights = _numpy.zeros(x.shape[1] + 1)
    weights[:-1][active_x] = weights_recons[:-1, 0]
    weights[-1] = weights_recons[-1, 0]

    return weights

  def _evaluate_solutions_data(self, problem, evaluation_mask):
    if not evaluation_mask.any():
      return evaluation_mask

    solutions_table, fields_map = self._solutions_data, self._fields
    payload_solutions = self._payload_solutions

    size_s = problem.size_s()
    if not size_s:
      input_data = solutions_table[:, fields_map["x"]]
    else:
      input_data = solutions_table[:, fields_map.get("stochastic", slice(0))]
      if input_data.shape[1] != size_s:
        return solutions_table, fields_map # cannot evaluate since stochastic data are missing
      input_data = _numpy.hstack((solutions_table[:, fields_map["x"]], input_data))

    evaluation_data, evaluation_mask = _evaluate_sparse_data(problem, input_data, evaluation_mask)

    size_f, size_c = problem.size_f(), problem.size_c()
    slice_f, slice_c = slice(0, size_f), slice(size_f, size_f + size_c)

    if size_f and evaluation_mask[:, slice_f].any():
      solutions_table, fields_map = _required_solution_field(solutions_table, fields_map, "f", size_f)
      if payload_solutions:
        # we cannot just override payload, we must combine it
        solutions_table_first_f = fields_map["f"].indices(solutions_table.shape[1])[0]
        for k, (current_evaluation_data, current_evaluation_mask) in enumerate(zip(evaluation_data[:, slice_f].T, evaluation_mask[:, slice_f].T)):
          if not current_evaluation_mask.any():
            continue
          elif current_evaluation_mask.all():
            current_evaluation_mask = slice(0, len(current_evaluation_mask))
          current_solutions_table = solutions_table[:, (solutions_table_first_f + k)]
          if (solutions_table_first_f + k) not in payload_solutions:
            current_solutions_table[current_evaluation_mask] = current_evaluation_data[current_evaluation_mask]
          elif self._payload_storage:
            current_solutions_table[current_evaluation_mask] = self._payload_storage.join_encoded_payloads(current_solutions_table[current_evaluation_mask],
                                                                                                           current_evaluation_data[current_evaluation_mask])
      else:
        solutions_table_f = solutions_table[:, fields_map["f"]]
        solutions_table_f[evaluation_mask[:, slice_f]] = evaluation_data[:, slice_f][evaluation_mask[:, slice_f]]

    if size_c and evaluation_mask[:, slice_c].any():
      solutions_table, fields_map = _required_solution_field(solutions_table, fields_map, "c", size_c)
      solutions_table_c = solutions_table[:, fields_map["c"]]
      solutions_table_c[evaluation_mask[:, slice_c]] = evaluation_data[:, slice_c][evaluation_mask[:, slice_c]]

    self._solutions_data, self._fields = solutions_table, fields_map

    return evaluation_mask

  def __setattr__(self, *args):
    """
    Mute direct possibility to write attribute
    """
    if hasattr(self, '_finalized'):
      raise TypeError('Immutable object!')
    super(Result, self).__setattr__(*args)

  def __delattr__(self, *args):
    """
    Mute direct possibility to remove attribute
    """
    if hasattr(self, '_finalized'):
      raise TypeError('Immutable object!')
    super(Result, self).__delattr__(*args)

  @property
  def fields(self):
    """
    Available solution fields.

    :type: ``tuple(list[str], list[str])``

    Available fields (``x``, ``f``, ``c``, and so on) and possible subfields like ``x.x1``, ``f.f1`` and other.

    """
    return sorted([k for k in self._fields if not k.startswith('_')], key=self._fields.get), sorted(self._extended_fields, key=self._extended_fields.get)

  @property
  def solutions_fields(self):
    """
    Available solution fields.

    :type: ``tuple(list[str], list[str])``

    Available fields (``x``, ``f``, ``c``, and so on) and possible subfields like ``x.x1``, ``f.f1`` and other.

    """
    return sorted([k for k in self._fields if not k.startswith('_')], key=self._fields.get), sorted(self._extended_fields, key=self._extended_fields.get)

  def _undefined(self, fields=None):
    """
    Returns undefined points from result if they are available.

    :param fields: fields to output
    :type fields: None or iterable containing str
    :return: feasible points
    :rtype: :class:`_numpy.ndarray`
    """
    return self._solutions(fields, "undefined")

  def feasible(self, fields=None):
    """
    Returns feasible points from the result if they are available.

    :param fields: fields to output
    :type fields: ``list[str]``
    :return: feasible points
    :rtype: ``numpy.ndarray``

    For the available fields, see :attr:`~da.p7core.Result.fields`.

    """
    return self._solutions(fields, "feasible")

  def infeasible(self, fields=None):
    """
    Returns infeasible points from result if they are available.

    :param fields: fields to output
    :type fields: ``list[str]``
    :return: infeasible points
    :rtype: ``numpy.ndarray``

    For the available fields, see :attr:`~da.p7core.Result.fields`.

    """
    return self._solutions(fields, "infeasible")

  def optimal(self, fields=None):
    """
    Returns optimal points from result if they are available.

    :param fields: fields to output
    :type fields: ``None``, ``iterable(str)``
    :return: optimal points
    :rtype: ``numpy.ndarray``
    """
    return self._solutions(fields, "optimal")

  def _converged(self, fields=None):
    """
    Returns converged points from result if they are available

    :param fields: fields to output
    :type fields: ``None``, ``iterable(str)``
    :return: converged points
    :rtype: ``numpy.ndarray``
    """
    return self._solutions(fields, "converged")

  def _undefined_solutions(self):
    return _numpy.logical_or(_shared._find_holes(self._solutions_data[:, self._fields.get("f", slice(0))]).any(axis=1),
                             _shared._find_holes(self._solutions_data[:, self._fields.get("c", slice(0))]).any(axis=1))

  def _simple_solutions_filter(self, points_filters):
    # In a simple case all points are feasible, optimal, converged
    if any(_ in ('feasible', 'optimal', 'converged') for _ in points_filters):
      return None
    # For compatibility with _labeled_solutions_filter, the `undefined` points are OR'ed with the other filters
    return self._undefined_solutions() if 'undefined' in points_filters else slice(0, 0)

  def _labeled_solutions_filter(self, points_filters):
    if not points_filters:
      return None

    active_flags = set()

    if "feasible" in points_filters:
      active_flags.update((GT_SOLUTION_TYPE_DISCARDED, GT_SOLUTION_TYPE_CONVERGED, GT_SOLUTION_TYPE_NOT_DOMINATED, GT_SOLUTION_TYPE_FEASIBLE_NAN,))
    elif "optimal" in points_filters: # "feasible" is a superset of "optimal"
      active_flags.update((GT_SOLUTION_TYPE_CONVERGED, GT_SOLUTION_TYPE_NOT_DOMINATED,))

    if "infeasible" in points_filters:
      active_flags.update((GT_SOLUTION_TYPE_INFEASIBLE, GT_SOLUTION_TYPE_BLACKBOX_NAN, GT_SOLUTION_TYPE_INFEASIBLE_NAN,))
    if "converged" in points_filters:
      active_flags.update((GT_SOLUTION_TYPE_CONVERGED,))
    if "undefined" in points_filters:
      active_flags.update((GT_SOLUTION_TYPE_NOT_EVALUATED, GT_SOLUTION_TYPE_FEASIBLE_NAN, GT_SOLUTION_TYPE_INFEASIBLE_NAN,))
    if "potentially feasible" in points_filters:
      active_flags.update((GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE,))

    if "potentially optimal" in points_filters and "_optimal" in self._fields:
      active_points = self._solutions_data[:, self._fields["_optimal"]][:, 0] == GT_SOLUTION_TYPE_CONVERGED
    else:
      active_points = _numpy.zeros((len(self._solutions_data)), dtype=bool)

    if "flag" in self._fields:
      flags_vector = self._solutions_data[:, self._fields["flag"]][:, 0]
    else:
      flags_vector = _numpy.empty(len(self._solutions_data))
      flags_vector.fill(GT_SOLUTION_TYPE_NOT_DOMINATED)

    for flag in active_flags:
      _numpy.logical_or(active_points, flags_vector == flag, out=active_points)

    if active_points.all():
      return None
    elif not active_points.any():
      return slice(0, 0)

    return active_points

  def _solutions_filter(self, filter_type):
    filter_type = _shared._normalize_string_list(filter_type, name="filters list", keep_case=True)
    if filter_type is None or not self._solutions_data.size:
      return None

    known_subset_filters = ("all", "new", "initial", "auto")
    known_points_filter = ("feasible", "infeasible", "optimal", "undefined", "potentially feasible", "potentially optimal", "converged") # note "converged" must be the last one, so we efficiently hide it
    known_filters = known_subset_filters + known_points_filter

    filter_type, undefined_filters = _validate_fields_names(filter_type, known_filters)
    if undefined_filters:
      raise _exceptions.WrongUsageError("Unknown filter type '%s'. Available filters are '%s'." % ("', '".join(undefined_filters), "', '".join(known_filters[:-1])))

    points_filter = [_ for _ in filter_type if _ in known_points_filter]
    points_filter = None if not points_filter \
                else self._simple_solutions_filter(points_filters=points_filter) if "flag" not in self._fields \
                else self._labeled_solutions_filter(points_filters=points_filter)

    if "all" in filter_type:
      return points_filter
    elif isinstance(points_filter, slice) and (points_filter.start or 0) >= points_filter.stop:
      return points_filter
    elif points_filter is not None and not points_filter.any():
      return slice(0, 0)

    # note "all" is absent since we've checked it above
    subset_filters = [_ for _ in filter_type if _ in known_subset_filters]

    if not subset_filters:
      subset_slice = self._solutions_subsets["all"] # by default its "all" for consistence with filter_type=None
    elif "initial" in subset_filters:
      if "new" in subset_filters or "auto" in subset_filters:
        return points_filter # "initial" + either "new" or "auto" is "all"
      subset_slice = self._solutions_subsets["initial"]
    elif "auto" in subset_filters:
      subset_slice = self._solutions_subsets["auto"] # "auto" is a superset of "new"
    else:
      assert all(_ == "new" for _ in subset_filters)
      subset_slice = self._solutions_subsets["new"]

    if points_filter is None:
      return subset_slice

    subset_slice = subset_slice.indices(len(self._solutions_data))

    if isinstance(points_filter, slice):
      points_filter = points_filter.indices(len(self._solutions_data))
      a, b = max(points_filter[0], subset_slice[0]), min(points_filter[1], subset_slice[1])
      return slice(a, max(a, b))

    points_filter[:subset_slice[0]] = False
    points_filter[subset_slice[1]:] = False
    return points_filter

  def _solutions_size(self, filter_type=None):
    points_filter = self._solutions_filter(filter_type)
    if points_filter is None:
      return len(self._solutions_data)

    # create a dummy array to get the shape of data, but no data
    test_array = _numpy.empty((len(self._solutions_data), 0))
    return len(test_array[points_filter])

  def _unsafe_read_solutions(self, destination_map, destination_data, payload_storage):
    for field in destination_map:
      if field in self._fields:
        source_slice = self._fields[field] if field in self._fields else self._extended_fields[field]
        destination_data[:, destination_map[field]] = self._solutions_data[:, source_slice]

    if payload_storage and self._payload_solutions and "f" in destination_map and "f" in self._fields:
      destination_base, _, destination_stride = destination_map["f"].indices(destination_data.shape[1])
      source_base, _, source_stride = self._fields["f"].indices(self._solutions_data.shape[1])
      for i in self._payload_solutions:
        destination_payload_index = (i - source_base) // source_stride * destination_stride + destination_base
        destination_data[:, destination_payload_index] = payload_storage.adopt_encoded_payloads(self._payload_storage, self._solutions_data[:, i])

  def _postprocess_payload_data(self, dataset, payload_columns):
    if not payload_columns:
      return dataset

    result_dataset = dataset.astype(object)
    for p in payload_columns:
      result_dataset[:, p][_shared._find_holes(dataset[:, p])] = None
      result_dataset[:, p] = self._payload_storage.decode_payload(dataset[:, p])

    return result_dataset

  def _raw_solutions(self, fields=None, filter_type=None):
    fields = _shared._normalize_string_list(fields, name="fields", keep_case=True)
    if fields is not None:
      known_fields = list(self._fields) + list(self._extended_fields)
      fields, invalid_fields = _validate_fields_names(fields, known_fields)
      if invalid_fields:
        raise _exceptions.WrongUsageError("Unexpected fields %s. Available fields are %s." % (invalid_fields, known_fields))

    points_filter = self._solutions_filter(filter_type)
    designs_data = self._solutions_data if points_filter is None else self._solutions_data[points_filter, :]

    if fields is None:
      return (designs_data.copy() if points_filter is None else designs_data), self._payload_solutions # avoid double copy, avoid return pointer to the origin
    elif not fields:
      return designs_data[:, 0:0].copy() if points_filter is None else designs_data[:, 0:0][points_filter], [] # right shape, empty data

    fields_slices = tuple((self._fields[field] if field in self._fields else self._extended_fields[field]) for field in fields)
    fields_collection = [designs_data[:, _] for _ in fields_slices]

    if self._payload_solutions:
      payload_columns = _numpy.zeros(self._solutions_data.shape[1], dtype=bool)
      payload_columns[self._payload_solutions] = True
      payload_columns = _numpy.nonzero(_numpy.hstack([payload_columns[_] for _ in fields_slices]))[0].tolist()
    else:
      payload_columns = []

    if len(fields_collection) == 1:
      return (fields_collection[0].copy() if points_filter is None else fields_collection[0]), payload_columns # avoid double copy, avoid return pointer to the origin
    return _numpy.hstack(fields_collection), payload_columns

  def _solutions(self, fields=None, filter_type=None):
    """
    Returns all solutions if they are available
    Throws an exception otherwise

    :param fields: fields to output
    :type fields: ``None``, ``iterable(str)``
    :param filter_type: filter to use
    :type filter_type: ``str`` or ``None``
    :return: solution points
    :rtype: ``numpy.ndarray``
    """
    return self._postprocess_payload_data(*self._raw_solutions(fields=fields, filter_type=filter_type))

  solutions = None
  """Returns all solutions if they are available.

  (this is a placeholder for the Sphinx autosummary, leave it be)
  """

  @property
  def designs_fields(self):
    """
    Available designs fields.

    :type: ``tuple(list[str], list[str])``

    Available fields (``x``, ``f``, ``c``, and so on) and possible subfields like ``x.x1``, ``f.f1`` and other.

    """
    return ([_ for _ in self._designs_fields[0]], [_ for _ in self._designs_fields[1]])

  @property
  def designs_samples(self):
    """
    Available designs sample type filters.

    :type: ``list[str]``

    Available subsample filters are divided into two groups:

    * Feasibility and optimality filters ---
      filter designs according to values of constraints and objectives.

      * ``"feasible"`` --- get points for which all constraint values are
        known and satisfied (confirmed feasible points), with regard to
        constraint tolerance.
      * ``"infeasible"`` --- get points where at least one of the constraints
        is violated or NaN (confirmed infeasible points).
      * ``"undefined"`` --- get points that are not confirmed feasible or infeasible ---
        for example, some constraints were not evaluated,
        but those that were evaluated are not violated.
      * ``"potentially feasible"`` --- in tasks with deferred constraint evaluations,
        get points to consider when evaluating the deferred responses ---
        those that will resolve into feasible or infeasible after such evaluations,
        and are not yet defined until then; this is different from the undefined points ---
        an undefined point will not resolve even if you complete the deferred evaluations.

    * Data source filters ---
      used to include or exclude the designs from the initial sample.

      * ``"all"`` --- get all designs, new and initial regardless.
      * ``"initial"`` --- get initial sample points, skip new generated points
        unless the ``"new"`` filter is also specified.
      * ``"new"`` --- get new generated points only, skip initial sample points
        unless the ``"initial"`` filter is also specified.

    You can combine the filters to select only the designs you need.
    Filters from different groups are applied using "and" logic, for example:

    * ``["initial", "feasible"]`` gets the points that come from the initial sample *and* are feasible.
    * ``["new", "undefined"]`` gets only the new points where some constraints were not evaluated.

    Filters from the same group are applied using "or" logic, for example:

    * ``["new", "feasible", "potentially feasible"]`` gets the new points that are confirmed feasible, or may yet resolve to feasible.
    """
    return [_ for _ in self._designs_samples[0]] + [_ for _ in self._designs_filters[0]]

  def _designs_filter(self, sample_type):
    if sample_type is None:
      return None # None means "all"

    make_copy = True
    designs_flags = self._designs_data[:, self._designs_fields[2]["flag"]][:, 0] if "flag" in self._designs_fields[1] else None
    designs_data = self._designs_data

    # split sample filters
    point_kind_filters = [_.lower() for _ in sample_type if _.lower() in self._designs_filters[1]]
    point_sample_filter = [_.lower() for _ in sample_type if _.lower() in self._designs_samples[1]]

    if (len(point_kind_filters) + len(point_sample_filter)) < len(sample_type):
      valid_point_filters = [_ for _ in self._designs_filters[1]] + [_ for _ in self._designs_samples[1]]
      invalid_point_filters = [_ for _ in sample_type if _.lower() not in valid_point_filters]
      raise _exceptions.WrongUsageError("Unexpected sample filter '%s'. Available filters are %s." % (invalid_point_filters, valid_point_filters))

    if "all" in point_sample_filter: # all is the excessive default
      point_sample_filter.remove("all")

    points_mask = _numpy.empty(len(self._designs_data), dtype=bool)

    if point_sample_filter:
      points_mask.fill(False)
      for sample_slice in point_sample_filter:
        points_mask[self._designs_samples[1][sample_slice]] = True
    else:
      points_mask.fill(True)

    if point_kind_filters:
      if "flag" in self._designs_fields[1]:
        active_points = _numpy.zeros((designs_data.shape[0],), dtype=bool)
        designs_flags = self._designs_data[:, self._designs_fields[2]["flag"]][:, 0]
        if "feasible" in point_kind_filters and "feasible" in self._designs_filters[0]:
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_CONVERGED)
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_NOT_DOMINATED)
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_FEASIBLE_NAN)
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_DISCARDED)
        if "infeasible" in point_kind_filters and "infeasible" in self._designs_filters[0]:
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_INFEASIBLE)
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_BLACKBOX_NAN)
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_INFEASIBLE_NAN)
        if "undefined" in point_kind_filters and "undefined" in self._designs_filters[0]:
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_NOT_EVALUATED)
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_FEASIBLE_NAN)
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_INFEASIBLE_NAN)
        if "potentially feasible" in point_kind_filters and "potentially feasible" in self._designs_filters[0]:
          active_points = _numpy.logical_or(active_points, designs_flags == GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE)
        points_mask = _numpy.logical_and(points_mask, active_points)
      elif "feasible" not in point_kind_filters:
        # no flags mean all points are feasible and we've just been asked to get points of a different kind
        points_mask.fill(False)

    return None if points_mask.all() else points_mask

  def _raw_designs(self, fields=None, sample_type=None):
    designs_fields = self._designs_fields[2]

    fields = _shared._normalize_string_list(fields, name="fields", keep_case=True)
    if fields is not None:
      valid_fields = self._designs_fields[0] + self._designs_fields[1]
      fields, invalid_fields = _validate_fields_names(fields, valid_fields)
      if invalid_fields:
        raise _exceptions.WrongUsageError("Unexpected fields %s. Available fields are %s." % (invalid_fields, valid_fields))
    else:
      # by default use all top-level fields
      fields = self._designs_fields[0]

    sample_type = _shared._normalize_string_list(sample_type, name="samples list", keep_case=False)
    points_mask = self._designs_filter(sample_type)

    if not fields:
      # avoid double copy, avoid return pointer to the origin
      empty_data = self._designs_data[:, 0:0].copy() if points_mask is None \
              else self._designs_data[:, 0:0][points_mask]
      return empty_data, [] # right shape, empty data

    if self._payload_designs:
      payload_columns = _numpy.zeros(self._designs_data.shape[1], dtype=bool)
      payload_columns[self._payload_designs] = True
      payload_columns = _numpy.nonzero(_numpy.hstack([payload_columns[designs_fields[field]] for field in fields]))[0].tolist()
    else:
      payload_columns = []

    fields_collection = [self._designs_data[:, designs_fields[field]] for field in fields]
    if points_mask is not None:
      fields_collection = [_[points_mask] for _ in fields_collection]

    if len(fields_collection) == 1:
      # avoid double copy, avoid return pointer to the origin
      return (fields_collection[0].copy() if points_mask is None else fields_collection[0]), payload_columns

    return _numpy.hstack(fields_collection), payload_columns

  def _designs(self, fields=None, sample_type=None):
    """
    Returns all solutions if they are available
    Throws an exception otherwise

    :param fields: fields to output
    :type fields: ``None``, ``iterable(str)``
    :param sample_type: filter to use
    :type sample_type: ``str``, ``None``, ``iterable(str)``
    :return: solution points
    :rtype: ``numpy.ndarray``
    """
    return self._postprocess_payload_data(*self._raw_designs(fields=fields, sample_type=sample_type))

  designs = None
  """Returns all designs if they are available.

  (this is a placeholder for the Sphinx autosummary, leave it be)
  """

  @property
  def names(self):
    """Names of variables, objectives, and constraints as they were defined by the problem.
    If some names are not available, corresponding attribute is an empty list.

    * ``names.c`` (``list[str]``) --- names of constraints.
    * ``names.f`` (``list[str]``) --- names of objectives.
    * ``names.x`` (``list[str]``) --- names of variables.

    """
    return self._names


  @property
  def info(self):
    """Result information.

    :type: ``dict``

    """
    return self._info

  @property
  def status(self):
    """Result status.

    :type: :class:`~da.p7core.status.Status`

    For details, see section :ref:`gen_status`.
    """
    return self._status

  @property
  def model(self):
    """Internal model trained by the Adaptive Design of Experiments technique.

    :type: :class:`.gtapprox.Model`

    This attribute is ``None`` in GTOpt results and
    in GTDoE results generated by any GTDoE technique
    other than the Adaptive Design of Experiments.
    May also be ``None`` in an Adaptive Design of Experiments result,
    if the internal model never reached the minimum accuracy specified by the
    :ref:`GTDoE/Adaptive/InitialModelQualityLevel <GTDoE/Adaptive/InitialModelQualityLevel>`
    option.

    """
    return self._model


  def __len__(self):
    return len(self._solutions_data)

  def __str__(self):
    stream = _six.moves.StringIO()

    try:
      data_table = [("Status:", str(self._status)),
                    ("Data fields:", ", ".join(self.fields[0]) or "<no data>"),
                    ("All solutions set:", self.__point_string(len(self._solutions_data))),
                    ("Optimal solutions set:", self.__point_string(self._solutions_size("optimal"))),
                    ("Feasible solutions set:", self.__point_string(self._solutions_size("feasible"))),
                    ("Infeasible solutions set:", self.__point_string(self._solutions_size("infeasible"))),
                    ]

      # Optional fields
      for filter in ("Potentially feasible", "Undefined", "Initial",):
        n_points = self._solutions_size(filter.lower())
        if n_points:
          data_table.append((filter + " set:", self.__point_string(n_points)))
      data_table.append(("All designs set", self.__point_string(len(self._designs_data))))

      data_field_format = "  %%-%ds %%s\n" % (max(len(name) for name, value in data_table),)

      stream.write("Result statistics:\n")
      for _ in data_table:
        stream.write(data_field_format % _)
    except:
      raise # no drama, do nothing

    try:
      diagnostics = self._info.get('Diagnostics')
      if diagnostics:
        stream.write("Details:\n")
        for note in diagnostics:
          stream.write("  " + "\n  ".join(str(note).split("\n")) + "\n")
    except:
      raise # no drama, do nothing

    try:
      n_solutions, print_limit = len(self._solutions_data), 40
      if n_solutions <= print_limit:
        stream.write("All solutions:\n")
        self.pprint(file=stream, designs=False)
        if not n_solutions and len(self._designs_data) <= print_limit:
          stream.write("All designs:\n")
          self.pprint(file=stream, designs=True)
      else:
        stream.write("<The set of all solutions is too long, consider using pprint()>")
    except:
      pass # no drama, do nothing

    return stream.getvalue()

  @staticmethod
  def __point_string(count):
    return str(count) + (" point" if count == 1 else " points")

  @staticmethod
  def _reorder_fields_wrt_payload(fields, payload_indices, fields_location):
    if not payload_indices or "f" not in fields:
      return list(fields), []

    # split "f" to a separate fields and reorder payloads to the end of a row
    regular_fields = []
    payload_fields = []
    for field in fields:
      if field == "f":
        for col in sorted(fields_location, key=fields_location.get):
          if not col.startswith('f.'):
            continue
          elif fields_location[col].start in payload_indices:
            payload_fields.append(col)
          else:
            regular_fields.append(col)
      else:
        regular_fields.append(field)

    return regular_fields, payload_fields

  def pprint(self, fields=None, filter_type=None, file=_sys.stdout, precision=8, designs=False, limit=None):
    """
    Print formatted result data.

    :param fields: fields to output (by default, output all available fields)
    :type fields: ``None`` or ``list[str]``
    :param filter_type: the filter to use
    :type filter_type: ``str``
    :param precision: floating point value precision
    :type precision: ``int``
    :param designs: print all available problem data (``True``) or solutions only (``False``)
    :type designs: ``bool``
    :param file: output facility
    :type file: ``io.TextIOBase``
    :param designs: print designs if True
    :type designs: ``bool``
    :param limit: the maximal number of points to print
    :type limit: ``int``

    Prints the formatted representation of result data to :arg:`file`
    with the specified :arg:`precision` for floating point values.

    By default, prints the solution data only (see :meth:`~da.p7core.Result.solutions()`).
    To print all problem data (see :meth:`~da.p7core.Result.designs()`), set :arg:`designs` to ``True``.

    Similarly to :meth:`~da.p7core.Result.designs()` and :meth:`~da.p7core.Result.solutions()`,
    you can select the fields and subsample types to output
    using the :arg:`fields` and :arg:`filter_type` parameters.
    The fields and filters you specify should be consistent with the type of output
    (all designs or solutions only), set by :arg:`designs`.
    """

    _shared.check_concept_int(precision, '`precision` argument')
    if limit is not None:
      _shared.check_concept_int(limit, '`limit` argument')

    fields = _shared._normalize_string_list(fields, name="fields", keep_case=True)
    filter_type = _shared._normalize_string_list(filter_type, name="filters", keep_case=False)

    if designs:
      if not fields:
        fields = tuple(_ for _ in self._default if _ in self._designs_fields[0]) + (("flag",) if "flag" in self._designs_fields[2] else tuple())
      else:
        valid_fields = tuple(self._designs_fields[0]) + tuple(self._designs_fields[1])
        fields, _ = _validate_fields_names(fields, valid_fields)

      regular_fields, payload_fields = self._reorder_fields_wrt_payload(fields=fields, payload_indices=self._payload_designs, fields_location=self._designs_fields[2])
      fields = regular_fields + payload_fields

      points_filter = self._designs_filter(filter_type)
      fields_collection = [self._designs_data[:, self._designs_fields[2][field]] for field in fields]
    else:
      if not fields:
        fields = tuple(_ for _ in self._default if _ in self._fields) + (("flag",) if "flag" in self._fields else tuple())
      else:
        valid_fields = tuple(self._fields) + tuple(self._extended_fields)
        fields = [_ for _ in fields if _ in valid_fields]

      solution_fields = dict(self._fields)
      solution_fields.update(self._extended_fields)

      regular_fields, payload_fields = self._reorder_fields_wrt_payload(fields=fields, payload_indices=self._payload_solutions, fields_location=solution_fields)
      fields = regular_fields + payload_fields

      points_filter = self._solutions_filter(filter_type)
      fields_collection = [self._solutions_data[:, solution_fields[field]] for field in fields]

    if not fields_collection or not len(fields_collection[0]):
      file.write("<no data>\n")
      return

    if "flag" in regular_fields:
      initial_points = _numpy.zeros(len(fields_collection[0]), dtype=bool)
      potentially_optimal = _numpy.zeros(len(fields_collection[0]), dtype=bool)

      if designs:
        initial_points[self._designs_samples[1]["initial"]] = True
      else:
        initial_points[self._solutions_subsets["initial"]] = True
        if "_optimal" in self._fields:
          potentially_optimal = self._solutions_data[:, self._fields["_optimal"]][:, 0] == GT_SOLUTION_TYPE_CONVERGED

      if points_filter is not None:
        initial_points = initial_points[points_filter]
        potentially_optimal = potentially_optimal[points_filter]

    no_potentially_optimal = ("flag" not in regular_fields) or potentially_optimal.any()

    if points_filter is not None:
      fields_collection = [_[points_filter] for _ in fields_collection]

    post_message = None
    if limit is not None:
      limit, n_points = int(limit), len(fields_collection[0])
      if limit >= 1 and limit < n_points:
        fields_collection = [_[:limit] for _ in fields_collection]
        post_message = '... [ %d more points]\n' % ((n_points - limit),)

    field_width = precision + 6
    format_val = '%- ' + str(field_width) + '.' + str(precision) + 'g'
    hole_marker = ('%-' + str(field_width) + 's') % '<no data>'

    def nptostr(xi):
      return '[' + ' '.join([(hole_marker if _shared._NONE == xij else (format_val % xij)) for xij in xi]) + ']'

    named_flags = {
      GT_SOLUTION_TYPE_DISCARDED:      "feasible", # we use it to mark feasible points in the DoE and discard in optimization result
      GT_SOLUTION_TYPE_CONVERGED:      ("feasible" if designs else "feasible, optimal"),
      GT_SOLUTION_TYPE_NOT_DOMINATED:  ("feasible" if designs else "feasible, optimal"),
      GT_SOLUTION_TYPE_INFEASIBLE:     "infeasible",
      GT_SOLUTION_TYPE_INFEASIBLE_NAN: "infeasible, undefined" if no_potentially_optimal else "infeasible",
      GT_SOLUTION_TYPE_BLACKBOX_NAN:   "infeasible",
      GT_SOLUTION_TYPE_NOT_EVALUATED:  "undefined",
      GT_SOLUTION_TYPE_FEASIBLE_NAN:   "feasible, undefined" if no_potentially_optimal else "feasible",
      GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE: "feasible (?)",
    }

    def stringify_flags(flag_code, initial, potentially_optimal):
      result = named_flags.get(flag_code, "error: " + str(flag_code))
      if initial:
        result = 'initial, ' + result
      if potentially_optimal:
        result = result + ', optimal (?)'
      return result

    for idx, field in enumerate(regular_fields):
      if not len(fields_collection[idx]):
        continue
      elif field.lower() == "flag":
        fields_collection[idx] = [stringify_flags(*_) for _ in zip(fields_collection[idx][:, 0], initial_points, potentially_optimal)]
        width = len(max(fields_collection[idx], key=len))
        fields_collection[idx] = [_.ljust(width) for _ in fields_collection[idx]]
      else:
        fields_collection[idx] = [nptostr(_) for _ in fields_collection[idx]]

    for idx, field in enumerate(payload_fields):
      idx += len(regular_fields)
      if len(fields_collection[idx]):
        fields_collection[idx] = [str(_) for _ in self._payload_storage.decode_payload(fields_collection[idx][:, 0], "<no data>")]
        width = len(max(fields_collection[idx], key=len))
        fields_collection[idx] = [_.ljust(width) for _ in fields_collection[idx]]

    fields = [(name + ": ") for name in fields]
    for values in zip(*fields_collection):
      file.write(" ".join([c + v for c, v in zip(fields, values)]) + '\n')

    if post_message:
      file.write(post_message)

def _batch_evaluate_sparse_data_slice(problem, input_data, input_mask, batch_limit):
  if not batch_limit or len(input_data) < batch_limit:
    return problem._evaluate(input_data, input_mask, None)

  output_data, output_mask = zip(*[problem._evaluate(input_data[_:(_+batch_limit)], input_mask[_:(_+batch_limit)], None) \
                                   for _ in range(0, len(input_data), batch_limit)])

  return _numpy.vstack(output_data), _numpy.vstack(output_mask)

def _evaluate_sparse_data_slice(problem, input_data, mask_in, responses, mask_out, mask_slice, batch_limit=None):
  if not mask_in[:, mask_slice].any():
    return mask_in, responses, mask_out

  mask_call = _numpy.zeros_like(mask_in, dtype=bool)
  mask_call[:, mask_slice] = mask_in[:, mask_slice]

  active_points = mask_call[:, mask_slice].any(axis=1)

  if active_points.all():
    evaluate_data, evaluate_mask = _batch_evaluate_sparse_data_slice(problem=problem, input_data=input_data, input_mask=mask_call, batch_limit=batch_limit)
  else:
    evaluate_mask = _numpy.zeros_like(mask_in, dtype=bool)
    evaluate_data = _shared._filled_array(evaluate_mask.shape, _shared._NONE)
    evaluate_data[active_points], evaluate_mask[active_points] = _batch_evaluate_sparse_data_slice(problem=problem, input_data=input_data[active_points], input_mask=mask_call[active_points], batch_limit=batch_limit)

  if not evaluate_mask.any():
    return mask_in, responses, mask_out

  mask_call[:] = mask_in[:] # copy-on-modify to avoid side effects
  mask_call[evaluate_mask] = False # don't call twice if there were something outside mask_call

  if mask_out is None:
    mask_out = evaluate_mask
  else:
    mask_out[evaluate_mask] = True

  if responses is None:
    responses = evaluate_data
    responses[~evaluate_mask] = _shared._NONE
  else:
    for i in problem._payload_objectives:
      if evaluate_mask[:, i].any():
        evaluate_data_i = evaluate_data[:, i]
        evaluate_mask_i = evaluate_mask[:, i]
        evaluate_data_i[evaluate_mask_i] = problem._payload_storage.join_encoded_payloads(evaluate_data_i[evaluate_mask_i], responses[:, i][evaluate_mask_i])
    responses[evaluate_mask] = evaluate_data[evaluate_mask] # copy only evaluated data

  return mask_call, responses, mask_out

def _evaluate_sparse_data(problem, input_data, mask, batch_limit=None):
  input_data, invalid_points = problem._valid_input_points(input_data, return_invalid=True)
  if mask[invalid_points, :].any():
    mask = mask.copy() # copy on modify
    mask[invalid_points, :] = 0 # don't evaluate invalid points

  if not mask.any():
    return _shared._filled_array(mask.shape, _shared._NONE), _numpy.zeros_like(mask)
  elif (mask.all(axis=0) == mask.any(axis=0)).all():
    return _batch_evaluate_sparse_data_slice(problem=problem, input_data=input_data, input_mask=mask, batch_limit=batch_limit) # simple case

  size_f, size_c = problem.size_f(), problem.size_c()

  # evaluate constraints first, then objectives, and then gradients if any
  mask, responses, mask_out = _evaluate_sparse_data_slice(problem, input_data, mask, None, None, slice(size_f, size_f + size_c), batch_limit=batch_limit)
  mask, responses, mask_out = _evaluate_sparse_data_slice(problem, input_data, mask, responses, mask_out, slice(0, size_f), batch_limit=batch_limit)
  mask, responses, mask_out = _evaluate_sparse_data_slice(problem, input_data, mask, responses, mask_out, slice(size_f + size_c, None), batch_limit=batch_limit)

  if responses is None:
    return _shared._filled_array(mask.shape, _shared._NONE), _numpy.zeros_like(mask)

  return responses, mask_out

@_contextmanager
def _make_writeable(data):
  writeable = data.flags.writeable
  try:
    data.flags.writeable = True
    yield
  finally:
    data.flags.writeable = writeable

def _read_objectives_type(problem, auto_objective):
  try:
    size_x, size_f = problem.size_x(), problem.size_f()
    objectives_type = [(_ or "auto").lower() for _ in problem.elements_hint(slice(size_x, size_x + size_f), "@GT/ObjectiveType")]
    return [(auto_objective if i == "auto" else i) for i in objectives_type]
  except:
    pass
  return []

def _negative_numbers(matrix):
  numbers_mask = ~_numpy.isnan(matrix)
  if numbers_mask.all():
    return _numpy.negative(matrix)
  matrix = _numpy.array(matrix, copy=True)
  matrix[numbers_mask] = -matrix[numbers_mask]
  return matrix

def _optional_negative_numbers(matrix, negate):
  return _negative_numbers(matrix) if negate else matrix

def _slice_width(s, dim):
  s = s.indices(dim)
  return s[1] - s[0]

def _align_datasets(sample_a, fields_a, sample_b, fields_b):
  dim_a, dim_b = sample_a.shape[1], sample_b.shape[1]

  fields_a_map = dict(fields_a)
  fields_b_map = dict(fields_b)

  if dim_a == dim_b and len(fields_a_map) == len(fields_b_map) and\
    all(k in fields_a_map and fields_a_map[k].indices(dim_a) == fields_b_map[k].indices(dim_b) for k in fields_b_map):
    return fields_a, sample_a, sample_b

  # new fields are allowed but existing fields must have the same width
  b_copy_scheme = []

  total_width = dim_a
  for k in fields_b_map: # for all fields in b
    slice_a, slice_b = fields_a_map.get(k), fields_b_map[k]
    if slice_a is None: # if b-field is not in a, then append it
      prev_extra_width, total_width = total_width, total_width + _slice_width(slice_b, dim_b)
      slice_a = slice(prev_extra_width, total_width)
      fields_a_map[k] = slice_a
    assert _slice_width(slice_b, dim_b) == _slice_width(slice_a, dim_a) # cannot be, actually
    b_copy_scheme.append((slice_a, slice_b))

  # append empty fields to sample_a
  sample_a_aligned = _shared._pad_columns(sample_a, (total_width - dim_a), _shared._NONE)
  sample_b_aligned = _shared._filled_array((sample_b.shape[0], sample_a_aligned.shape[1]), _shared._NONE)

  # copy all common a and b fields to their new places in b
  for new_position, original_position in b_copy_scheme: # for all fields in b
    sample_b_aligned[:, new_position] = sample_b[:, original_position]

  # keep type of fields_a on return
  fields_a_type = type(fields_a)
  fields_a = fields_a_map if isinstance(fields_a_map, fields_a_type) else \
    fields_a_type(sorted([(k, fields_a_map[k]) for k in fields_a_map], key=lambda kv: kv[1].start or 0))

  return fields_a, sample_a_aligned, sample_b_aligned

def _required_solution_field(solutions_table, fields_map, field_name, field_width):
  if field_name in fields_map:
    return solutions_table, fields_map
  fields_map[field_name] = slice(solutions_table.shape[1], solutions_table.shape[1] + field_width)
  return _shared._pad_columns(solutions_table, field_width, _shared._NONE), fields_map

def _select_subsample(sample, include_points, exclude_points):
  # this method could be more efficient but now
  # it works with all kinds of include_points/exclude_points indexers
  point_to_get = _numpy.zeros(len(sample), dtype=bool)
  point_to_get[include_points] = True
  point_to_get[exclude_points] = False

  if point_to_get.all():
    return sample
  elif not point_to_get.any():
    return sample[:0] # exclude all: valid shape, no points
  return sample[point_to_get]

def _postprocess_solution_samples(default_solution, default_fields, initial_sample, initial_fields, problem):
  # merge initial and "auto" samples
  has_initial_sample = initial_sample is not None and initial_sample.size
  has_default_solution = default_solution is not None and default_solution.size

  if not has_initial_sample and not has_default_solution:
    return _numpy.empty((0, 0)), {}, {}

  from .utils.designs import _unique_rows_indices, _harmonize_datasets_inplace

  if has_initial_sample and has_default_solution:
    # default_solution and initial_sample must have the same sets of fields
    default_fields, default_solution, initial_sample = _align_datasets(default_solution, default_fields, initial_sample, initial_fields)
    _harmonize_datasets_inplace(problem, default_fields, default_solution, initial_sample)
    initial_fields = default_fields

  general_fields = dict(initial_fields if has_initial_sample else default_fields)
  if "stochastic" in general_fields:
    general_keys_slice = _numpy.zeros((initial_sample if has_initial_sample else default_solution).shape[1], dtype=bool)
    general_keys_slice[general_fields.get("x", slice(0))] = True
    general_keys_slice[general_fields["stochastic"]] = True
    if not general_keys_slice.any():
      general_keys_slice = slice(0, None)
  else:
    general_keys_slice = general_fields.get("x", slice(0, None))

  if has_initial_sample:
    # select indices of unique records in the initial_sample
    initial_sample_keys = _shared._make_dataset_keys(initial_sample[:, general_keys_slice])
    initial_sample_uniques = _unique_rows_indices(initial_sample_keys)

  if has_default_solution:
    # select indices of unique records in the default_solution
    default_solution_keys = _shared._make_dataset_keys(default_solution[:, general_keys_slice])
    default_solution_uniques = _unique_rows_indices(default_solution_keys)

  if not has_initial_sample:
    # no initial sample - the default_solution is "auto" and "new" solution
    solutions_table = _select_subsample(default_solution, default_solution_uniques, slice(0))
    solutions_subsets = {"new": slice(0, len(solutions_table)),
                         "auto": slice(0, len(solutions_table)),
                         "initial": slice(0, 0)}
    return solutions_table, dict(default_fields), solutions_subsets

  if not has_default_solution:
    # no default solution (is it possible?) - the solution is unique points of the initial sample
    solutions_table = _select_subsample(initial_sample, initial_sample_uniques, slice(0))
    solutions_subsets = {"new": slice(0, 0), "auto": slice(0, 0),
                         "initial": slice(0, len(solutions_table))}
    return solutions_table, dict(initial_fields), solutions_subsets

  # split initial_sample and default_solution to three sets of points:
  # - records from the default_solution that are not in the initial_sample
  # - records which are in both default_solution and initial_sample
  # - records from the initial_sample that are not in the default_solution

  final_solution_keys = _numpy.vstack([initial_sample_keys[i] for i in initial_sample_uniques] \
                                    + [default_solution_keys[i] for i in default_solution_uniques])
  final_solution_order = _shared._lexsort(final_solution_keys)

  intersection_default = []
  intersection_initial = []
  n_initial_sample_uniques = len(initial_sample_uniques)

  for i, j in zip(final_solution_order[:-1], final_solution_order[1:]):
    # Since we got subsets of unique default_solution_keys and unique initial_sample_keys,
    # final_solution_keys[i] == final_solution_keys[j] means i and j indicates points
    # from the different sets: default_solution and initial_sample.
    # min(i, j) must be from the initial_sample because the initial_sample precede
    # the default_solution in the final_solution_keys.
    index_initial, index_default = (i, j) if i < j else (j, i)
    if index_initial < n_initial_sample_uniques and index_default >= n_initial_sample_uniques \
      and _numpy.equal(final_solution_keys[i], final_solution_keys[j]).all():
      intersection_initial.append(initial_sample_uniques[index_initial])
      intersection_default.append(default_solution_uniques[index_default - n_initial_sample_uniques])

  initial_only = _select_subsample(initial_sample, initial_sample_uniques, intersection_initial)
  intersection = _select_subsample(initial_sample, intersection_initial, slice(0))
  default_only = _select_subsample(default_solution, default_solution_uniques, intersection_default)

  # in marginal cases we keep order of the initial sample
  solutions_table = _numpy.vstack((initial_only, intersection, default_only))

  n_initial_only = len(initial_only)
  n_default_only = len(default_only)
  n_total        = len(solutions_table)

  #n_default_only = len(default_solution_uniques) - len(intersection_default)
  solutions_subsets = {"new": slice(n_total - n_default_only, n_total),
                        "auto": slice(n_initial_only, n_total),
                        "initial": slice(0, n_total - n_default_only)}

  # note the default_fields equals to the initial_fields
  return solutions_table, dict(default_fields), solutions_subsets

def _snapshot_of_result(problem, result):
  """Converts the result returned by :meth:`~da.p7core.gtdoe.Generator.build_doe()`
  and by :meth:`~da.p7core.gtopt.Solver.solve()` to a snapshot object.

  :param problem: The problem description.
  :type problem: :class:`~da.p7core.gtopt.ProblemGeneric`
  :param result: the result of optimization of DoE to convert to snapshot
  :type result: :class:`~da.p7core.Result`
  :return: snapshot or ``None``
  """
  try:
    from .utils.designs import _SolutionSnapshotFactoryBase
    snapshot_factory = _SolutionSnapshotFactoryBase(generator=object(), watcher=lambda:True,
                                                    problem=problem, auto_objective_type="evaluate")
    return snapshot_factory._modern_result_to_snapshot(result)
  except:
    pass
  return None

def _validate_fields_names(requested_names, known_names):
  known_names = set(known_names)
  return [_ for _ in requested_names if _ in known_names], \
         [_ for _ in requested_names if _ not in known_names]
