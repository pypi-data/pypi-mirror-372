#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Implementation of problem definition for optimizer
--------------------------------------------------

.. currentmodule:: da.p7core.gtopt.problem

"""

from __future__ import with_statement
from __future__ import division

import sys as _sys
import time as _time
import ctypes as _ctypes
import re as _re
import numpy as _numpy
import contextlib as _contextlib
import inspect as _inspect

from decimal import Context as _DecimalContext

from ..six import string_types, with_metaclass, next
from ..six.moves import xrange, range, zip, StringIO
from .. import shared as _shared
from .. import exceptions as _ex
from ..utils import designs as _designs

from . import utils as _utils

from hashlib import sha1 as _sha1

class _Backend(object):
  def __init__(self):
    self.__normal_options_name_cache = {}
    self.__library = _shared._library
    self._c_double_p = _ctypes.POINTER(_ctypes.c_double)

    self._gtopt_positive_infinity = _ctypes.CFUNCTYPE(_ctypes.c_double)(('GTOptPositiveInfinity', self.__library))()
    self._gtopt_negative_infinity = _ctypes.CFUNCTYPE(_ctypes.c_double)(('GTOptNegativeInfinity', self.__library))()

    self._c_normalize_option_name = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                      , _ctypes.c_char_p # [in] user-provided hint name
                                                      , _ctypes.c_void_p # [in] memory allocator for normalized hint name
                                                      , _ctypes.POINTER(_ctypes.c_void_p) # [out] extended error information
                                                      )(("GTOptNormalizeOptionName2", self.__library))

    self._c_validate_options = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                                 , _ctypes.c_char_p # [in] options in JSON format
                                                 , _ctypes.POINTER(_ctypes.c_void_p) # [out] extended error information
                                                 )(("GTOptValidateOptionsValue", self.__library))

    # note this function intentionally refer to GTDoE backend
    self._c_default_option_value = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_char_p, _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_size_t),
                                                        _ctypes.POINTER(_ctypes.c_void_p))(("GTDoEDefaultOptionValue", self.__library)) # ret. bool, option name, option ret. buffer, option ret. buffer size, error descr

    self._c_check_variable = _ctypes.CFUNCTYPE(_ctypes.c_short  #retval
                                              , _ctypes.c_double # initial guess
                                              , _ctypes.c_uint # n.hints
                                              , _ctypes.POINTER(_ctypes.c_char_p), _ctypes.POINTER(_ctypes.c_char_p) #hints
                                              , _ctypes.c_uint, self._c_double_p #levels
                                              , _ctypes.c_char_p # variable name
                                              , _ctypes.POINTER(_ctypes.c_void_p) # [out] extended error information
                                              )(("GTOptSolverCheckVariable2", self.__library))


  def normalize_option_name(self, name):
    if name in self.__normal_options_name_cache:
      return self.__normal_options_name_cache[name]

    try:
      cname = _ctypes.c_char_p(name.encode("ascii") if isinstance(name, string_types) else name)
    except:
      exc_info = _sys.exc_info()
      _shared.reraise(_ex.InvalidOptionNameError, ("Invalid hint name is given: %s" % name), exc_info[2])

    errdesc = _ctypes.c_void_p()
    data = _shared._unsafe_allocator()

    _shared._raise_on_error(self._c_normalize_option_name(cname, data.callback, _ctypes.byref(errdesc)), \
                                                          "Failed to read standard option or hint name.", errdesc)

    norm_name = _shared._preprocess_utf8(data.value)
    self.__normal_options_name_cache[name] = norm_name
    return norm_name

  def check_options_value(self, options):
    if not options:
      return

    _shared.check_concept_dict(options, "options")

    errdesc = _ctypes.c_void_p()
    coptions = _ctypes.c_char_p(_shared.write_json(options, fmt_double='%.17g').encode("ascii"))

    _shared._raise_on_error(self._c_validate_options(coptions, _ctypes.byref(errdesc)), "Invalid option or hint detected.", errdesc)

  def normalize_hints_name(self, hints, target_name):
    if not hints:
      return {}

    if not _shared.is_mapping(hints):
      raise TypeError('Wrong %s hints type %s! Mapping object is required.' % (target_name, type(hints).__name__))

    try:
      return dict((self.normalize_option_name(hint_name), hints[hint_name]) for hint_name in hints)
    except:
      _, exc_val, exc_tb = _sys.exc_info()
      _shared.reraise(ValueError, ("Wrong %s hints: %s" % (target_name, exc_val)), exc_tb)

  def default_option_value(self, name):
    try:
      cname = _ctypes.c_char_p(name.encode("ascii") if isinstance(name, string_types) else name)
    except:
      exc_info = _sys.exc_info()
      _shared.reraise(_ex.InvalidOptionNameError, ("Invalid option name is given: %s" % name), exc_info[2])

    errdesc = _ctypes.c_void_p()
    csize = _ctypes.c_size_t(0)
    if not self._c_default_option_value(cname, _ctypes.c_char_p(), _ctypes.byref(csize), _ctypes.byref(errdesc)):
                                        _shared._raise_on_error(False, "Failed to read default option value", errdesc)
    cvalue = (_ctypes.c_char * csize.value)()
    if not self._c_default_option_value(cname, _ctypes.cast(cvalue, _ctypes.c_char_p), _ctypes.byref(csize), _ctypes.byref(errdesc)):
                                        _shared._raise_on_error(False, "Failed to read default option value", errdesc)
    return _shared._preprocess_utf8(cvalue.value)

  def check_variable(self, initial, hints, levels, name):
    number_of_hins = len(hints)
    hint_names  = (_ctypes.c_char_p * number_of_hins)()
    hint_values = (_ctypes.c_char_p * number_of_hins)()
    for idx, hint in enumerate(hints):
      _shared.check_type(hint, 'hint name', string_types)
      hint_names[idx] = hint.encode("ascii")
      hint_values[idx] = str(hints[hint]).encode("ascii")

    numpy_levels = _numpy.array(levels)
    errdesc = _ctypes.c_void_p()
    status = self._c_check_variable(initial, _ctypes.c_uint(number_of_hins), hint_names, hint_values
                                   , _ctypes.c_uint(numpy_levels.size), numpy_levels.ctypes.data_as(self._c_double_p)
                                   , _ctypes.c_char_p(name.encode("utf-8")), _ctypes.byref(errdesc))
                                   # variable/response name is given by user and may use any unicode symbols, utf-8 is must
    _shared._raise_on_error(status, ("Invalid variable %s" % (name,)), errdesc)

_backend = _Backend()

class _HashableNDArray(_numpy.ndarray):
  def __hash__(self):
    if not hasattr(hasattr, '__hash'):
      self.__hash = int(_sha1(self.view(_numpy.uint8)).hexdigest(), 16)
    return self.__hash

  def __eq__(self, other):
    if not isinstance(other, _HashableNDArray):
      return super(_HashableNDArray, self).__eq__(other)
    return super(_HashableNDArray, self).__eq__(super(_HashableNDArray, other)).all()

class _LRSMReconstructionResult(object):
  def __init__(self, result, points, data):
    self._objectives = tuple(_ for _ in sorted(result["reconstructed"]["objectives"], key=lambda x:x[0]))
    self._constraints = tuple(_ for _ in sorted(result["reconstructed"]["constraints"], key=lambda x:x[0]))
    self._failed_objectives = tuple(_ for _ in sorted(result["failed"]["objectives"], key=lambda x:x[0]))
    self._failed_constraints = tuple(_ for _ in sorted(result["failed"]["constraints"], key=lambda x:x[0]))
    self._evaluations = points, data, ~_shared._find_holes(data)

  @property
  def objectives(self):
    """  List of tuples (`objective index`, `rrms`, `weights`) of reconstructed linear objectives """
    return self._objectives

  @property
  def constraints(self):
    """  List of tuples (`objective index`, `rrms`, `weights`) of reconstructed linear constraints """
    return self._constraints

  @property
  def failed_objectives(self):
    """  List of tuples (`objective index`, `failure reason`, `rrms`, `weights`) of linear objective functions that are considered non-linear.
         Note `rrms`, `weights` may be None if reconstruction failed for reasons other than rejection by leave-one-out cross validation.
    """
    return self._failed_objectives

  @property
  def failed_constraints(self):
    """  List of tuples (`constraint index`, `failure reason`, `rrms`, `weights`) of linear constraints that are considered non-linear
         Note `rrms`, `weights` may be None if reconstruction failed for reasons other than rejection by leave-one-out cross validation.
    """
    return self._failed_constraints

  @property
  def evaluations(self):
    """  Tuple of three (may be empty) matrices: `points`, `data`, `mask`
         `points` is n-by-problem.size_x matrix of points (x) at which were any evaluations, either objective or constraints
         `data` is n-by-problem.size_full() data matrix returned by the problem `evaluate` method
         `mask` is n-by-problem.size_full() boolean mask of evaluated responses at `data`
    """
    return self._evaluations


def _get_gtopt_positive_infinity():
  return _backend._gtopt_positive_infinity

def _get_gtopt_negative_infinity():
  return _backend._gtopt_negative_infinity

def _grad_size(bb):
  """Calc gradient size

  :param bb: problem
  :type bb: ``ProblemGeneric``
  :return: (obj_grad_size, con_grad_size)
  :rtype: ``tuple``

  """
  obj_nnz = con_nnz = 0
  if bb._grad_objectives:
    obj_nnz += len(bb._grad_objectives_rows) if bb._grad_objectives_sparse else bb.size_x() * bb.size_f()
  if bb._grad_constraints:
    con_nnz += len(bb._grad_constraints_rows) if bb._grad_constraints_sparse else bb.size_x() * bb.size_c()
  return obj_nnz, con_nnz

class _Objective(object):
  def __init__(self, name, hints):
    if name:
      _shared.check_type(name, 'objective name', string_types)
      self.name = name
    else:
      raise ValueError('Objective must have a name!')

    self.hints = _backend.normalize_hints_name(hints, ("\"%s\" objective" % self.name))

class _Constraint(object):
  def __init__(self, name, bounds, hints):
    if name:
      _shared.check_type(name, 'constraint name', string_types)
      self.name = name
    else:
      raise ValueError('Constraint must have a name!')

    if _shared.is_sized(bounds) and len(bounds) == 2:
      self.lower_bound = vmin = _get_gtopt_negative_infinity()
      self.upper_bound = vmax = _get_gtopt_positive_infinity()
      if bounds[0] is not None:
        _shared.check_concept_numeric(bounds[0], 'constraint \'%s\' lower bound' % self.name)
        self.lower_bound = _numpy.clip(bounds[0], vmin, vmax)
      if bounds[1] is not None:
        _shared.check_concept_numeric(bounds[1], 'constraint \'%s\' upper bound' % self.name)
        self.upper_bound = _numpy.clip(bounds[1], vmin, vmax)
      if self.lower_bound > self.upper_bound:
        raise ValueError('Invalid constraint bounds %s, lower > upper' % str(bounds))
    else:
      raise ValueError('Wrong constraint bounds structure: a vector of two floating point values is expected.')

    self.hints = _backend.normalize_hints_name(hints, ("\"%s\" constraint" % self.name))

class _Variable(object):
  def __init__(self, name, bounds, initial_guess, hints):
    assert name, 'Variable must have a name!'
    _shared.check_type(name, 'variable name', string_types)

    self.name = name
    if not _shared.is_iterable(bounds):
      raise ValueError('Wrong variable range structure! Variable must define pair for bounds or range of possible values!')

    if (initial_guess is not None):
      _shared.check_concept_numeric(initial_guess, "initial guess of variable '%s'" % self.name)

    if initial_guess is None:
      self.initial_guess = _shared._NONE
    else:
      self.initial_guess = _shared.parse_float(initial_guess)

    self.hints = _backend.normalize_hints_name(hints, ("\"%s\" variable" % self.name))

    self.bounds = _shared.convert_to_1d_array(bounds)
    _backend.check_variable(self.initial_guess, self.hints, self.bounds, self.name) #Check then clamp. Enormous categorical values raise error.
    vmin = _get_gtopt_negative_infinity()
    vmax = _get_gtopt_positive_infinity()
    self.bounds = _numpy.clip(self.bounds, vmin, vmax)#nan seems to be safe

class _Stochastic(object):
  def __init__(self, distribution, name):
    if name:
      _shared.check_type(name, 'Stochastic variables name', string_types)
      self.name = name
    else:
      raise ValueError('Stochastic must have a name!')

    if not distribution:
      raise ValueError('Stochastic must define distribution!')

    self.distribution = distribution
    self.state = []
    self.freeIndex = []

  def get(self, quantity):
    if not self.distribution:
      raise ValueError('Distribution is not set up!')
    ksi = []
    if quantity > 0:
      ksi = self.distribution.getNumericalSample(quantity)
    if not _shared.is_iterable(ksi):
      iterableKsi = []
      for i in xrange(0, ksi.getSize()):
        for j in xrange(0, ksi.getDimension()):
          iterableKsi.append(ksi[i][j])
      ksi = iterableKsi
    return ksi

  def size(self):
    if self.distribution:
      result = self.distribution.getDimension()
    else:
      result = 0
    return result

class _AbstractMethod (object):
  def __init__(self, *args):
    if args:
      self.args = '(%s)' % (','.join(args))
      self.nargs = len(args)
    else:
      self.args = '()'
      self.nargs = 0

class _AbstractMethodBatch(_AbstractMethod):
  def __init__(self, batch_method_name, *args):
    _AbstractMethod.__init__(self, *args)
    self.batch_method_name = batch_method_name

class _OptionalMethod(object):
  def __init__(self, *args):
    if args:
      self.args = '(%s)' % (','.join(args))
      self.nargs = len(args)
    else:
      self.args = '()'
      self.nargs = 0

class _OptionalMethodBatch(_OptionalMethod):
  def __init__(self, opt_method_name, *args):
    _OptionalMethod.__init__(self, *args)
    self.opt_method_name = opt_method_name


class _ProblemMetaclass(type):
  def __init__(cls, name, bases, *args, **kwargs):
    super(_ProblemMetaclass, cls).__init__(cls, name, bases)

    cls.__new__ = staticmethod(cls.new)

    def initializer(self, *iargs, **ikwargs):
      cls.__oldinit__(self, *iargs, **ikwargs)
      if cls is type(self):
        self._initialize()

    cls.__oldinit__ = cls.__init__
    cls.__init__ = initializer

    abstractmethods = dict()
    batchmethods = dict()
    ancestors = list(cls.__mro__)
    ancestors.reverse()  # Start with __builtin__.object
    for ancestor in ancestors:
      for clsname, clst in ancestor.__dict__.items():
        if isinstance(clst, _AbstractMethodBatch):
          batchmethods[clst.batch_method_name] = (clsname, ancestor)
        if isinstance(clst, _AbstractMethod):
          abstractmethods[clsname] = clst.args
        elif hasattr(clst, '__call__'):
          if clsname in abstractmethods:
            abstractmethods.pop(clsname)
          if clsname in batchmethods:
            batchmethod = batchmethods[clsname]
            if batchmethod[1] != ancestor:
              abstractmethods.pop(batchmethod[0], None) #the method may not exist e.g. when the user implements constraint_batch for an unconstrained problem

    setattr(cls, '__abstractmethods__', abstractmethods)

  def new(self, cls, *args, **kwargs):
    if len(cls.__abstractmethods__):
      method_list = '\n  '.join((str(t) for t in cls.__abstractmethods__.items() if (t[0] + t[1])))
      error_message = 'Can\'t instantiate abstract class `' + cls.__name__ + '\';\n' + 'Abstract methods: \n  ' + method_list
      raise NotImplementedError(error_message)

    obj = object.__new__(cls)
    return obj

class ProblemGeneric(with_metaclass(_ProblemMetaclass, object)):
  """Base optimization problem class.

  To define an optimization problem, create your own problem class, inheriting from
  :class:`ProblemGeneric<da.p7core.gtopt.ProblemGeneric>` or its descendants.

  .. _prepare-problem:

  All problem properties are defined in the :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()` method of the derived class.
  Inside :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`, use these inherited methods:

  * Basic problem definition:

    * :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`
    * :meth:`~da.p7core.gtopt.ProblemGeneric.add_objective()`
    * :meth:`~da.p7core.gtopt.ProblemGeneric.add_constraint()`

  * Advanced features:

    * :meth:`~da.p7core.gtopt.ProblemGeneric.enable_objectives_gradient()` --- use analytical gradients of objective functions
    * :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()` --- use analytical gradients of constraint functions
    * :meth:`~da.p7core.gtopt.ProblemGeneric.set_history()` --- configure saving objective and constraint evaluations; note that the memory :attr:`~da.p7core.gtopt.ProblemGeneric.history` is enabled by default, which increases memory consumption
    * :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()` --- essential method for robust optimization problems

  In all classes derived directly from :class:`~da.p7core.gtopt.ProblemGeneric`, you also have to
  implement the :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()` method that calculates values of objectives and
  constraints. This method is the only one that supports all optimizer features, but due to its complexity it may
  be difficult to use (see :ref:`code sample <codesample_gtopt_generic>`). Because of that, GTOpt module includes a number
  of simplified problem classes:

  * :class:`~da.p7core.gtopt.ProblemUnconstrained`
  * :class:`~da.p7core.gtopt.ProblemConstrained`
  * :class:`~da.p7core.gtopt.ProblemCSP`
  * :class:`~da.p7core.gtopt.ProblemMeanVariance`

  A problem object can be converted to a string to obtain a short human-readable problem description, for example::

    >>> import da.p7core.gtopt
    >>> class MyProblem(da.p7core.gtopt.ProblemGeneric):
    >>>   def prepare_problem(self):
    >>>     self.add_variable((0, 1), 0.5)
    >>>     self.add_variable((0, 2), 0.5)
    >>>     self.add_objective()
    >>>   def evaluate(self, xquery, maskquery):
    >>>     return [[x[0]**2] for x in xquery], [[1] for x in xquery]
    >>> problem = MyProblem()
    >>> print problem
    da.p7core GTOpt problem:
        Type: MyProblem
        Number of variables: 2
        Number of objectives: 1
        Number of constraints: 0
        Analytical objectives gradients: False
        Analytical constraints gradients: False
        Variables bounds:
        x1: 0.000000 1.000000
        x2: 0.000000 2.000000
        Initial guess:
        [0.500000,0.500000]
    >>> result = da.p7core.gtopt.Solver().solve(problem)
    >>> print result.optimal.x
    [[7.116129095440896e-07, 0.5050600736179194]]
    >>> print result.optimal.f
    [[5.063929330298047e-13]]

  """


  # called on metaclass level
  def _initialize(self):
    self.__problem_initialized = False

    self._variables = []
    self._objectives = []
    self._constraints = []
    self._stochastic = None

    self._grad_objectives = False
    self._grad_objectives_sparse = False
    self._grad_objectives_rows = tuple()
    self._grad_objectives_cols = tuple()

    self._grad_constraints = False
    self._grad_constraints_sparse = False
    self._grad_constraints_rows = tuple()
    self._grad_constraints_cols = tuple()

    self._admissible_values = set()

    self._history_cache = [] # list of 1D numpy arrays, note a lot of methods access _history_cache directly
    self._history_inmemory = True # note a lot of methods access _history_cache directly
    self._history_file = None
    self._header_required = False
    self._payload_storage = _designs._PayloadStorage() # maps ids of payload objects
    self._payload_objectives = []

    self._timecheck = None
    self._last_error = None # sys.exc_info() for the delayed exception 

    self.__modified = True #tells if we need to validate

    original_validate = self._validate

    try:
      self._validate = lambda: None # avoid accidental self._validate() calls within problem initialization
      _shared.wrap_with_exc_handler(self.prepare_problem, _ex.BBPrepareException)()
      original_validate() # call true validate once
    except Exception:
      e, tb = _sys.exc_info()[1:]
      if not isinstance(e, _ex.ExceptionWrapper):
        e = _ex.InvalidProblemError('Problem definition error: %s' % e)
      else:
        e.set_prefix("Problem definition error: ")
      _shared.reraise(type(e), e, tb)
    finally:
      self._validate = original_validate

  def _check_bound(self, value, lb, ub):
    return not (value < lb or value > ub) # Nan-compatible implementation

  def _read_batch_data(self, queryx, querymask, output, batch_reader, keys, name, regular_responses=None):
    if not output.size:
      return
    elif not querymask.any():
      output.fill(_shared._NONE)
      return

    responses_expected = _numpy.count_nonzero(querymask)
    if querymask.all():
      querymask = slice(0, len(output))

    batch_data = batch_reader(queryx[querymask])
    batch_mask = _numpy.ones(shape=(responses_expected, output.shape[1]), dtype=bool)

    if regular_responses is not None:
      regular_responses = regular_responses[:output.shape[1]]

    try:
      # straightforward matrix (or vector) read
      output[querymask], _ = self._translate_user_response(batch_data, batch_mask, regular_responses, name)
      return
    except:
      pass

    # Well, user may return a mix of lists and mappings
    unpacked_batch = _numpy.empty(shape=batch_mask.shape, dtype=(float if regular_responses is None or regular_responses.all() else object))
    for unpacked_batch_i, batch_data_i in zip(unpacked_batch, batch_data):
      try:
        for j, key in enumerate(keys):
          unpacked_batch_i[j] = batch_data_i[key] if key in batch_data_i else _shared._NONE
        continue
      except:
        pass
      unpacked_batch_i[:] = batch_data_i[:]

    output[querymask], _ = self._translate_user_response(unpacked_batch, batch_mask, regular_responses, name)

  def _evaluate_with_time_check(self, batch_x, size_r, response, timecheck):
    """Evaluate responses for ``batch_x`` checking the time limit.

    :param batch_x: batch of designs
    :param size_r: name of hint
    :param response: caller to evaluate a single designs
    :type batch_x: ``int``
    :type size_r: ``int``
    :type response: callable
    :return: evaluated responses
    :rtype: ``ndarray``

    This function returns loops over batch ``batch_x`` and calls ``response`` for each ``x``.
    Between calls it check time limit and stop if it is reached.

    Returned array always has full size. Not evaluated rows are filled with _shared._NONE

    """
    result = [] #note that result must be a list to be properly passed later if a user provides dicts as result
    keep_evaluating = True
    empty_data = _numpy.array([_shared._NONE]*size_r)
    for x in batch_x:
      result.append(empty_data)
      if keep_evaluating:
        try:
          result[-1] = response(x)
          if timecheck is not None:
            keep_evaluating = timecheck()
        except:
          if len(result) == 1 or _shared._desktop_mode():
            raise # forward exception
          self._last_error = _sys.exc_info()
          keep_evaluating = False

    if size_r == 1 and not keep_evaluating:
      # check if array is homogenous
      for i, _ in enumerate(result):
        if _ is not empty_data:
          try:
            if not _numpy.array(_).ndim:
              for k, _ in enumerate(result):
                if _ is empty_data:
                  result[k] = _shared._NONE
            break
          except:
            pass
    return result
  
  def _check_unique_names(self, names, type_param, autogen):
    names = sorted(names)
    for i, name in enumerate(names[1:]):
      if name == names[i]:
        error_str = '%s name "%s" is used more than once.' % (type_param, name)
        m = _re.match('%s([0-9]+)$' % autogen, name)
        if m and int(m.group(1)) < len(names) + 2:
          error_str += ' It may be automatically generated name.'
        raise _ex.BBPrepareException(error_str)

  def _validate(self):
    if not self.__modified:
      return

    self.__modified = False # mark as unmodified to avoid recursive calls
    try:
      #For DoE (self.size_f() + self.size_c()) == 0 is valid
      if len(self._variables) == 0:
        raise _ex.InvalidProblemError('At least one input variable must be defined!')

      self._check_unique_names(self.variables_names(), 'variable', 'x')
      self._check_unique_names(self.objectives_names(), 'objective', 'f')
      self._check_unique_names(self.constraints_names(), 'constraint', 'c')

      for ivar in self._variables:
        _backend.check_variable(ivar.initial_guess, ivar.hints, ivar.bounds, ivar.name)

      for resp in (self._objectives + self._constraints):
        _backend.check_options_value(resp.hints)

      size_x = self.size_x()

      if self._grad_constraints and self.size_c() == 0:
        raise _ex.InvalidProblemError("Can't use constraints analytical gradients in unconstrained problem!")
      if self._grad_objectives and self.size_f() == 0:
        raise _ex.InvalidProblemError("Can't use objectives analytical gradients in constraint-satisfaction problem!")

      if self._grad_objectives_sparse:
        grad_objectives_nnz = len(self._grad_objectives_rows)
        for i in xrange(grad_objectives_nnz):
          _shared.check_concept_int(self._grad_objectives_rows[i], "gradient element index")
          _shared.check_concept_int(self._grad_objectives_cols[i], "gradient element index")
          if not self._check_bound(self._grad_objectives_rows[i], 0, self.size_f() - 1):
            raise _ex.InvalidProblemError('Wrong non-zero element row index "%d" in objectives gradient!' % self._grad_objectives_rows[i])
          if not self._check_bound(self._grad_objectives_cols[i], 0, size_x - 1):
            raise _ex.InvalidProblemError('Wrong non-zero element column index "%d" in objectives gradient!' % self._grad_objectives_cols[i])

      if self._grad_constraints_sparse:
        grad_constraints_nnz = len(self._grad_constraints_rows)
        for i in xrange(grad_constraints_nnz):
          _shared.check_concept_int(self._grad_constraints_rows[i], "gradient element index")
          _shared.check_concept_int(self._grad_constraints_cols[i], "gradient element index")
          if not self._check_bound(self._grad_constraints_rows[i], 0, self.size_c() - 1):
            raise _ex.InvalidProblemError('Wrong non-zero element row index "%d" in constraints gradient!' % self._grad_constraints_rows[i])
          if not self._check_bound(self._grad_constraints_cols[i], 0, size_x - 1):
            raise _ex.InvalidProblemError('Wrong non-zero element column index "%d" in constraints gradient!' % self._grad_constraints_cols[i])

      noise_level_hint = _backend.normalize_option_name('@GT/NoiseLevel')
      self.__size_nf = sum(str(x.hints.get(noise_level_hint, 0)).lower() == 'fromblackbox' for x in self._objectives)
      self.__size_nc = sum(str(x.hints.get(noise_level_hint, 0)).lower() == 'fromblackbox' for x in self._constraints)

      if (self.__size_nf+self.__size_nc) and not self._stochastic:
        raise _ex.InvalidProblemError("Sample callback cannot be empty for stochastic problems.")

      undefined_ig = _shared._find_holes([_.initial_guess for _ in self._variables])
      if not undefined_ig.all() and undefined_ig.any():
        raise _ex.InvalidProblemError("Partial initial guess is not supported.")

      constraint_type_hint = _backend.normalize_option_name('@GTOpt/ConstraintType')
      constraint_alpha_hint = _backend.normalize_option_name('@GTOpt/ConstraintAlpha')
      for cons in self._constraints:
        if cons.hints.get(constraint_type_hint, "").lower() == "chanceconstraint" and constraint_alpha_hint not in cons.hints:
          raise _ex.InvalidProblemError("Type of the %s constraint is 'ChanceConstraint', %s hint must be set as well." % (cons.name, constraint_alpha_hint))

      linear_parameters_hint = _backend.normalize_option_name('@GTOpt/LinearParameterVector')
      evaluation_limit_hint = _backend.normalize_option_name('@GT/EvaluationLimit')
      expensive_evaluations_hint = _backend.normalize_option_name('@GT/ExpensiveEvaluations')
      objective_type_hint = _backend.normalize_option_name("@GT/ObjectiveType")
      linearity_type_hint = _backend.normalize_option_name("@GTOpt/LinearityType")

      for i, resp in enumerate(self._objectives):
        objective_type = resp.hints.get(objective_type_hint, "").capitalize()
        if objective_type == "Payload":
          linearity_type = (resp.hints.get(linearity_type_hint) or "generic").capitalize()
          if linearity_type != "Generic":
            raise _ex.InvalidProblemError(objective_type + ' objective must be generic: ' + linearity_type_hint + '=' + linearity_type)
          if resp.hints.get(linear_parameters_hint):
            raise _ex.InvalidProblemError('Hint ' + linear_parameters_hint + ' cannot be used for ' + objective_type + ' objective.')
          self._payload_objectives.append(i)

      for resp in (self._objectives + self._constraints):
        linear_parameters = resp.hints.get(linear_parameters_hint)
        if linear_parameters:
          try:
            linear_parameters = _numpy.array(linear_parameters, dtype=float, copy=_shared._SHALLOW)
          except:
            exc_info = _sys.exc_info()
            _shared.reraise(TypeError, ("Value of %s hint of %s cannot be interpreted as a vector of float values: %s"
                                        % (linear_parameters_hint, resp.name, exc_info[1])), exc_info[2])

          if linear_parameters.ndim > 1 and _numpy.count_nonzero(_numpy.equal(linear_parameters.shape, 1)) < (linear_parameters.ndim - 1):
            raise _ex.InvalidOptionValueError("Value of %s hint of %s cannot be interpreted as a vector of float values: %s tensor is given" % (linear_parameters_hint, resp.name, linear_parameters.shape))
          linear_parameters = linear_parameters.reshape(-1)

          if linear_parameters.shape[0] not in (size_x + 1, size_x + self.size_s() + 1):
            raise _ex.InvalidOptionValueError("Value of %s hint of %s has invalid length: %s (%s expected)" % (linear_parameters_hint, resp.name, linear_parameters.shape[0], size_x + 1))
          if not _numpy.isfinite(linear_parameters).all():
            raise _ex.InvalidOptionValueError("Value of %s hint of %s contains invalid (NaN or Infinite) values." % (linear_parameters_hint, resp.name,))

        general_evaluations_limit = self._parse_evaluations_limit(resp.hints.get(evaluation_limit_hint), None)
        expensive_evaluations_limit = self._parse_evaluations_limit(resp.hints.get(expensive_evaluations_hint), None)
        if general_evaluations_limit is not None and expensive_evaluations_limit is not None \
          and general_evaluations_limit != expensive_evaluations_limit:
          raise _ex.InvalidOptionValueError("Values of %s and %s hints of %s contains are set to different values: %s !- %s."
            % (evaluation_limit_hint, expensive_evaluations_hint, resp.name, resp.hints[evaluation_limit_hint], resp.hints[expensive_evaluations_hint]))

      self.__problem_initialized = True
    except:
      # restore modified state and pass exception further
      self.__modified = True
      raise

  @staticmethod
  def _value_string(val):
    vmin = _get_gtopt_negative_infinity()
    vmax = _get_gtopt_positive_infinity()
    if val <= vmin:
      return '-Inf'
    elif val >= vmax:
      return '+Inf'
    elif val is None or _numpy.isnan(val):
      return 'None'
    return '% -12.6g' % val

  @staticmethod
  def _array_string(array, brackets = '[]'):
    return (brackets[0] + '%s' + brackets[1]) % ','.join((ProblemGeneric._value_string(el) for el in array))

  def _regression_string(self, weights, alt_expression, ndig=None):
    try:
      fmt = ("%%.%dg" % ndig) if ndig else "%g"
      terms = [(("+" if weight > 0 else "-"), (fmt % abs(weight)), var.name.replace(' ', '_')) for weight, var in zip(weights[:-1], self._variables) if weight]
      if not terms:
        return fmt % weights[-1]

      terms = [((s+v) if w.rstrip(".") == "1" else (s + w + "*" + v)) for s, w, v in terms]
      if weights[-1]:
        terms = terms + [(("%%+.%dg" % ndig) if ndig else "%+g") % weights[-1],]

      if terms[0].startswith('-') and not all(_.startswith('-') for _ in terms):
        while terms[0].startswith('-'):
          terms = [terms[-1],] + terms[:-1]

      return "".join(terms).lstrip("+")
    except:
      pass
    return alt_expression

  def __str__(self):
    result = '''da.p7core GTOpt problem:
    Type: %s
    Number of variables: %d
    Number of objectives: %d
    Number of constraints: %d
    Analytical objectives gradients: %s
    Analytical constraints gradients: %s
    ''' % (type(self).__name__,
           self.size_x(),
           self.size_f(),
           self.size_c(),
           str(self._grad_objectives),
           str(self._grad_constraints))
    result += 'Variables ranges and hints: \n'

    vartypemap = dict((var_idx, var_type) for var_type in ("Continuous", "Integer", "Stepped", "Discrete", "Categorical") \
                                          for var_idx in self.variable_indexes_by_type(var_type))
    fixed_bound_hint = _backend.normalize_option_name("@GT/FixedValue")
    for idx, v in enumerate(self._variables):
      var_type = vartypemap.get(idx, "Unknown")
      hints = [var_type]
      if v.hints.get(fixed_bound_hint) is not None:
        hints.append(fixed_bound_hint + "=" + str(v.hints.get(fixed_bound_hint)))

      if var_type in ("Continuous", "Integer"):
        brackets = '[]'
        bounds = v.bounds
        if not _numpy.isfinite(bounds[0]):
          bounds[0] = -_numpy.inf;
        if not _numpy.isfinite(bounds[1]):
          bounds[1] = _numpy.inf;
      else:
        brackets = '{}'
        bounds = v.bounds

      result += '    '
      result += ' '.join([v.name + ':', self._array_string(bounds, brackets), ', '.join(hints), '\n'])

    if self.initial_guess():
      result += '    Initial guess:\n    '
      result += self._array_string(self.initial_guess())
      result += '\n'
    else:
      result += '    Initial guess: no\n'

    hint_linearity_type = _backend.normalize_option_name("@GTOpt/LinearityType")
    hint_linear_parameter_vector = _backend.normalize_option_name("@GTOpt/LinearParameterVector")
    hint_constraint_alpha = _backend.normalize_option_name("@GTOpt/ConstraintAlpha")
    hint_constraint_type = _backend.normalize_option_name("@GTOpt/ConstraintType")

    hint_evaluation_cost_type = _backend.normalize_option_name("@GTOpt/EvaluationCostType")
    hint_expensive_evaluations = _backend.normalize_option_name("@GT/ExpensiveEvaluations")
    hint_evaluation_limit = _backend.normalize_option_name("@GT/EvaluationLimit")
    hint_objective_type = _backend.normalize_option_name("@GT/ObjectiveType")

    default_cost_type = _backend.default_option_value(hint_evaluation_cost_type)
    default_linearity_type = _backend.default_option_value(hint_linearity_type)

    if self.size_f():
      result += '    Objectives hints:\n'
      for f in self._objectives:
        hints = [ f.hints.get(hint_linearity_type, default_linearity_type),
                  f.hints.get(hint_evaluation_cost_type, default_cost_type),
                  f.hints.get(hint_objective_type, ""),]
        expr_string = self._regression_string(f.hints.get(hint_linear_parameter_vector, []), "")
        if expr_string:
          hints.append("%s=%s" % (f.name, expr_string))
        result += '    %s: %s\n' % (f.name, ", ".join(_ for _ in hints if _))

    if self.size_c() != 0:
      result += '    Constraints bounds and hints:\n'
      for c in self._constraints:
        hints = [ c.hints.get(hint_linearity_type, default_linearity_type),
                  c.hints.get(hint_evaluation_cost_type, default_cost_type)]

        if hint_expensive_evaluations in c.hints:
          hints.append('ExpensiveEvaluations=%s' % c.hints.get(hint_expensive_evaluations))

        if hint_evaluation_limit in c.hints:
          hints.append('EvaluationLimit=%s' % c.hints.get(hint_evaluation_limit))

        if self._stochastic:
          hints.append(c.hints.get(hint_constraint_type, "ExpectationConstraint"))

        if hint_constraint_alpha in c.hints:
          hints.append('Alpha=%s' % c.hints.get(hint_constraint_alpha))

        hints.append("%s%s%s" % ((("%s <= " % self._value_string(c.lower_bound)) if c.lower_bound > _get_gtopt_negative_infinity() else ""),
                                 self._regression_string(c.hints.get(hint_linear_parameter_vector, []), c.name),
                                 ((" <= %s" % self._value_string(c.upper_bound)) if c.upper_bound < _get_gtopt_positive_infinity() else "")))

        result += '    %s: %s\n' % (c.name, ", ".join(hints))
    return result.strip()

  @staticmethod
  def _calculate_constraint_violation(constraint_values, lower_bound, upper_bound):
    assert constraint_values.ndim == 1

    def __impl(constraint_values):
      if _numpy.isfinite(lower_bound) and lower_bound > _get_gtopt_negative_infinity():
        psi = (lower_bound - constraint_values) / max(_numpy.fabs(lower_bound), 1.)
      else:
        psi = -1.

      if _numpy.isfinite(upper_bound) and upper_bound < _get_gtopt_positive_infinity():
        return _numpy.maximum((constraint_values - upper_bound) / max(_numpy.fabs(upper_bound), 1.), psi)

      return psi

    nan_constraint = _numpy.isnan(constraint_values)
    if nan_constraint.any():
      # Keep invalid (NaN or _shared._NONE) values as psi
      psi = _numpy.array(constraint_values, copy=True)
      psi[~nan_constraint] = __impl(constraint_values[~nan_constraint])
      return psi

    return __impl(constraint_values)

  @staticmethod
  def _violation_coefficients_to_feasibility(constraints_violation, violation_tolerance, deferred_constraints=None):
    """
    constraints_violation - matrix of float, positive values indicates relative constraint violation. A quiet NaN indicates constraint value is NaN.
                            NaN with a hole marker payload indicates constraint that have not been evaluated.
    violation_tolerance - float, the maximum allowed constraint violation
    deferred_constraints - None or any object that can be used to get columns of the matrix constraints_violation,
                           like slice, or list or vector of bools or columns indices.
                           Specifies deferred constraints, that is, a constraint that should not have been evaluated.
                           Although, the values of these constraints may be known.

    Returns a tuple of two vectors: maximum relative constraint violation (a.k.a psi) and classification code.
    The list of possible classification codes:
      GT_SOLUTION_TYPE_CONVERGED (0) - feasible point, all constraints are known and within bounds.
      GT_SOLUTION_TYPE_INFEASIBLE (2) - infeasible point because there is at least one constraint that is out of limits.
      GT_SOLUTION_TYPE_BLACKBOX_NAN (3) - point is infeasible because there is at least one constraint with value NaN.
      GT_SOLUTION_TYPE_NOT_EVALUATED (4) - some constraints that could be evaluated have not been evaluated, but all known constraints are in bounds.
      GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE (7) - there are deferred constraints, but all other constraints are known and within limits.

    Feasible points are those with code GT_SOLUTION_TYPE_CONVERGED (0).
    Potentially feasible points are those with code GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE (7).
    All other points are infeasible.
    """
    constraints_violation = _shared.as_matrix(constraints_violation, detect_none=True)
    violation_tolerance = 1.e-5 if violation_tolerance is None else float(violation_tolerance)

    invalid_points = _numpy.isnan(constraints_violation)

    # now classify points and fill final solution
    feasibility_codes = _numpy.zeros(len(constraints_violation), dtype=_numpy.int32) # by default, all points are feasible (0)

    # simple case: no NaN, no None
    if not invalid_points.any().any():
      maximum_violation = constraints_violation.max(axis=1) # maximum violation
      feasibility_codes[maximum_violation > violation_tolerance] = 2 # GT_SOLUTION_TYPE_INFEASIBLE
      return maximum_violation, feasibility_codes

    test_candidates = ~invalid_points.all(axis=1)
    if not test_candidates.all():
      # let's avoid RuntimeWarning: All-NaN slice encountered
      maximum_violation = _numpy.empty(len(constraints_violation))
      maximum_violation.fill(_shared._NONE) # mark as undefined by default, overwrite by NaNs later
      maximum_violation[test_candidates] = _numpy.nanmax(constraints_violation[test_candidates], axis=1)
    else:
      maximum_violation = _numpy.nanmax(constraints_violation, axis=1)
    del test_candidates

    undefined_points = _shared._find_holes(constraints_violation) # detect holes
    invalid_points[undefined_points] = False # now invalid_points contains only meaningful NaNs

    invalid_points = invalid_points.any(axis=1) # reduce to vector
    undefined_points = _numpy.logical_and(~invalid_points, undefined_points.any(axis=1)) # reduce to vector

    if invalid_points.any():
      feasibility_codes[invalid_points] = 3 # GT_SOLUTION_TYPE_BLACKBOX_NAN
      maximum_violation[invalid_points] = _numpy.nan

    infeasible_points = ~_numpy.logical_or(_numpy.isnan(maximum_violation), invalid_points) # select points that we may check
    # and find points for which known, finite constraint exceeds tolerance
    infeasible_points[infeasible_points] = maximum_violation[infeasible_points] > violation_tolerance
    feasibility_codes[infeasible_points] = 2 # GT_SOLUTION_TYPE_INFEASIBLE

    # clear "undefined" status if point is infeasible because any constraint is either NaN or exceeds tolerance
    undefined_points = _numpy.logical_and(undefined_points, ~_numpy.logical_or(invalid_points, infeasible_points))

    if undefined_points.any():
      feasibility_codes[undefined_points] = 4 # GT_SOLUTION_TYPE_NOT_EVALUATED
      maximum_violation[undefined_points] = _shared._NONE

      if deferred_constraints is not None:
        potentially_feasible = undefined_points # rename variable for the better understanding
        evaluated_constraints = _numpy.ones(constraints_violation.shape[1], dtype=bool)
        evaluated_constraints[deferred_constraints] = False
        if evaluated_constraints.any(): # If all constraints are deferred then all undefined points are potentially feasible
          # Since all undefined_points are not infeasible, points where all not-deferred constraints are known are potentially feasible.
          potentially_feasible[potentially_feasible] = ~_numpy.isnan(constraints_violation[potentially_feasible][:, evaluated_constraints]).any(axis=1)
        feasibility_codes[potentially_feasible] = 7 # GT_SOLUTION_TYPE_POTENTIALLY_FEASIBLE

    return maximum_violation, feasibility_codes

  def _deferred_responses(self):
    deferred_responses = _numpy.equal(self._responses_evaluation_limit(unlimited=-1), 0)
    return deferred_responses[:self.size_f()], deferred_responses[self.size_f():]

  def _evaluate_psi(self, c_values, c_tol):
    constraints_values = _shared.as_matrix(c_values, shape=(None, len(self._constraints)), detect_none=True)

    # estimate bounds violation
    constraints_violation_ext = _numpy.empty((constraints_values.shape[0], constraints_values.shape[1] + 1)) # extra column for the final solution
    for k, constraint_k in enumerate(self._constraints):
      constraints_violation_ext[:, k] = self._calculate_constraint_violation(c_values[:, k], constraint_k.lower_bound, constraint_k.upper_bound)

    _, deferred_constraints = self._deferred_responses()
    constraints_violation_ext[:, -1], feasibility_codes = self._violation_coefficients_to_feasibility(constraints_violation=constraints_violation_ext[:, :-1], violation_tolerance=c_tol, deferred_constraints=deferred_constraints)

    return constraints_violation_ext, feasibility_codes

  #
  # Helper methods used by interface
  #
  def constraints_bounds(self):
    """Get constraints bounds.

    :return: constraints bounds as tuple of two iterable objects
    :rtype: ``tuple``
    """
    # Once a user starts reading we suppose editing is over. Otherwise we cannot guarantee correct result.
    if self.__modified:
      self._validate()

    lower = []
    upper = []
    for c in self._constraints:
      lower.append(c.lower_bound)
      upper.append(c.upper_bound)
    return lower, upper

  def variables_bounds(self, index=None):
    """Get bounds and levels of variables.

    :param index: index of a categorical or discrete variable
    :type index: ``int``
    :return: bounds of variables or levels for a variable specified by :arg:`index`
    :rtype: ``numpy.ndarray``

    .. versionchanged:: 6.14
       added the :arg:`index` parameter

    If :arg:`index` is ``None``, returns a tuple of two lists containing values of the lower and upper bounds
    for all problem variables.
    For continuous and integer variables, these values are the same as those specified by the :arg:`bounds`
    parameter to :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`.
    For discrete and categorical variables, the bounds are the minimum and maximum values from
    the set of their levels specified by the :arg:`bounds` parameter.
    Note that bounds are generally nonsensical for a categorical variable,
    since categorical values cannot be compared by magnitude.

    If :arg:`index` is ``int``, returns a tuple of two values (lower and upper bound)
    if the variable under this :arg:`index` is continuous or integer,
    and a tuple containing all level values
    if this variable is discrete or categorical.
    """

    # Once a user starts reading we suppose editing is over. Otherwise we cannot guarantee correct result.
    if self.__modified:
      self._validate()

    fixed_bound_hint = _backend.normalize_option_name("@GT/FixedValue")
    variable_type_hint = _backend.normalize_option_name("@GT/VariableType")

    def _is_discrete(var):
      return var.hints.get(variable_type_hint, 'Continuous').lower() in ('stepped', 'categorical', 'discrete')

    if index is None:
      lower = []
      upper = []
      for x in self._variables:
        fixed_value = x.hints.get(fixed_bound_hint)
        if fixed_value is not None:
          lower.append(float(fixed_value))
          upper.append(float(fixed_value))
        elif _is_discrete(x):
          lower.append(_numpy.nanmin(x.bounds))
          upper.append(_numpy.nanmax(x.bounds))
        else: # we need to keep None for a bound despite value given for other bound, thus we cannot pass x.bounds through min/max
          lower.append(x.bounds[0])
          upper.append(x.bounds[1])
      return lower, upper

    fixed_value = self._variables[index].hints.get(fixed_bound_hint)
    if fixed_value is None:
      return self._variables[index].bounds
    elif _is_discrete(self._variables[index]):
      return _numpy.array((float(fixed_value),))
    return _numpy.array((float(fixed_value), float(fixed_value),))

  def initial_guess(self):
    """Get initial guess for all variables.

    :return: initial guess iterable (if present)
    :rtype: ``list[float]`` or ``None``
    """
    # Once a user starts reading we suppose editing is over. Otherwise we cannot guarantee correct result.
    if self.__modified:
      self._validate()

    ig = [x.initial_guess for x in self._variables]
    if (_shared._NONE == ig).all():
      return None
    return ig

  def elements_hint(self, indexElement, nameHint):
    """Get current hints for problem element.

    :param indexElement: index of element in order: variables, objectives, constraints
    :param nameHint: name of hint
    :type indexElement: ``int``
    :type nameHint: ``str``
    :return: hint value
    :rtype: ``str`` or ``None``

    This method returns current value of hint *nameHint* for an element of the problem (variable, objective function or constraint) with the given *indexElement* index, or ``None`` if the hint with given name is not available for the element.

    For the list of available hints, see :ref:`ug_gtopt_hints`.
    """
    nameHint = _backend.normalize_option_name(nameHint)

    # Once a user starts reading we suppose editing is over. Otherwise we cannot guarantee correct result.
    if self.__modified:
      self._validate()

    try:
      # get single element
      size_x, size_f, size_c = self.size_x(), self.size_f(), self.size_c()

      if int(indexElement) != indexElement or indexElement < 0 or indexElement >= (size_x + size_f + size_c):
        raise ValueError("Invalid element index: %s. The number in [0, %d) range is required" % (indexElement, (size_x + size_f + size_c)))
      elif indexElement < size_x:
        hints = self._variables[indexElement].hints
      elif indexElement < (size_x + size_f):
        hints = self._objectives[indexElement - size_x].hints
      else:
        hints = self._constraints[indexElement - size_x - size_f].hints

      return hints.get(nameHint, None)
    except TypeError:
      pass

    # get as slice
    hints = [_.hints for _ in self._variables] + [_.hints for _ in self._objectives] + [_.hints for _ in self._constraints]
    return [_.get(nameHint, None) for _ in hints[indexElement]]

  @staticmethod
  def _parse_evaluations_limit(value, default_limit=-1):
    if value is None:
      return default_limit

    try:
      value = int(value)
      return default_limit if value < 0 else value
    except:
      pass

    if str(value).lower() != "auto":
      raise ValueError("Invalid evaluations limit: " + str(value))

    return default_limit

  def _responses_evaluation_limit(self, unlimited=None, ignore_expensive=False,
                                  maximum_iterations=None, maximum_expensive_iterations=None,
                                  sample_x=None, sample_f=None, sample_c=None):
    general_limit_name = _backend.normalize_option_name("@GT/EvaluationLimit")
    expensive_limit_name = _backend.normalize_option_name("@GT/ExpensiveEvaluations")
    cost_type_name = _backend.normalize_option_name("@GTOpt/EvaluationCostType")
    default_cost_type = _backend.default_option_value(cost_type_name)

    def _process_response(resp, n_holes):
      limit = self._parse_evaluations_limit(resp.hints.get(general_limit_name, None), unlimited)
      expensive_response = not ignore_expensive and str(resp.hints.get(cost_type_name, default_cost_type)).lower() == "expensive"
      if limit == unlimited and expensive_response:
        limit = self._parse_evaluations_limit(resp.hints.get(expensive_limit_name, None), unlimited)
      if maximum_iterations:
        limit = maximum_iterations if limit == unlimited else min(maximum_iterations, limit)
      if maximum_expensive_iterations and expensive_response:
        limit = (maximum_expensive_iterations + n_holes) if limit == unlimited else min((maximum_expensive_iterations + n_holes), limit)
      return limit

    def _count_holes(n_default, dim, initial_sample):
      if initial_sample is None:
        return [n_default,]*dim
      initial_sample = _shared.as_matrix(initial_sample, shape=(None, dim))
      if not initial_sample.size:
        return [n_default,]*dim
      return _shared._find_holes(initial_sample).sum(axis=0)

    n_default = 0
    if sample_x is not None:
      sample_x = _shared.as_matrix(sample_x)
      if sample_x.size:
        n_default = sample_x.shape[0]

    return [_process_response(resp, n_holes) for resp, n_holes in zip(self._objectives, _count_holes(n_default, len(self._objectives), sample_f))]\
      + [_process_response(resp, n_holes) for resp, n_holes in zip(self._constraints, _count_holes(n_default, len(self._constraints), sample_c))]

  @_contextlib.contextmanager
  def _solve_as_subproblem(self, vars_hints, objs_hints, cons_hints, doe_mode):
    self._validate()

    init_vars_hints = [_.hints.copy() for _ in self._variables]
    init_objs_hints = [_.hints.copy() for _ in self._objectives]
    init_cons_hints = [_.hints.copy() for _ in self._constraints]

    init_bounds = [_.bounds for _ in self._variables]
    initial_guess = [_.initial_guess for _ in self._variables]
    if _shared._find_holes(initial_guess).all():
      initial_guess = []

    fixed_bound_hint = _backend.normalize_option_name("@GT/FixedValue")
    objective_type_hint = _backend.normalize_option_name("@GT/ObjectiveType")

    try:
      reset_initial_guess = not initial_guess
      for i, h in enumerate(vars_hints or []):
        self.update_variable_hints(i, h)
        if not reset_initial_guess:
          fixed_value = self._variables[i].hints.get(fixed_bound_hint)
          if fixed_value is not None:
            reset_initial_guess = initial_guess[i] != float(fixed_value)

      if reset_initial_guess:
        for var in self._variables:
          var.initial_guess = _shared._NONE

      for i, h in enumerate(objs_hints or []):
        if h:
          self._objectives[i].hints.update(h)
          self.set_objective_hints(i, self._objectives[i].hints)

      for i, h in enumerate(cons_hints or []):
        if h:
          self._constraints[i].hints.update(h)
          self.set_constraint_hints(i, self._constraints[i].hints)

      # now preprocess objective type
      if doe_mode:
        for i, objective in enumerate(self._objectives):
          if objective.hints.pop(objective_type_hint, "Auto").lower() not in ("auto", "adaptive"):
            objective.hints[objective_type_hint] = "Evaluate"
          self.set_objective_hints(i, objective.hints)
      else:
        for i, objective in enumerate(self._objectives):
          original_objective_type = objective.hints.get(objective_type_hint, "").lower()
          if original_objective_type == "adaptive":
            objective.hints[objective_type_hint] = "Evaluate" # switch type to adaptive
          elif original_objective_type == "auto":
            del objective.hints[objective_type_hint] # remove explicit "auto"
          self.set_objective_hints(i, objective.hints)

      # Note we've just remapped DoE 'minimize'/'maximize' to 'evaluate'
      if not self._history_inmemory and any(_.hints.get(objective_type_hint, "").lower() in ("evaluate", "payload",) for _ in self._objectives):
        self._history_inmemory = True # we do need history to put collateral objectives to solution

      self.__modified = False # Discard the modification status, since we assume that we did not make a mistake.

      yield
    finally:
      # avoid excessive checks on restore since we've just read all these values
      for objective, hints in zip(self._objectives, init_objs_hints):
        objective.hints = hints

      for constraint, hints in zip(self._constraints, init_cons_hints):
        constraint.hints = hints

      for variable, hints, bounds in zip(self._variables, init_vars_hints, init_bounds):
        variable.hints = hints
        variable.bounds = bounds

      if initial_guess:
        for variable, guess_value in zip(self._variables, initial_guess):
          variable.initial_guess = guess_value

      self.__modified = False # Discard the modification status, since we restore the valid state.

  def setup_additional_options(self, options):
    pass

  def variables_names(self):
    """Get names of variables.

    :return: name list
    :rtype: ``list[str]``
    """
    return [var.name for var in self._variables]

  def objectives_names(self):
    """Get names of objectives.

    :return: name list
    :rtype: ``list[str]``
    """
    return [obj.name for obj in self._objectives]

  def constraints_names(self):
    """Get names of constraints.

    :return: name list
    :rtype: ``list[str]``
    """
    return [con.name for con in self._constraints]

  def size_x(self):
    """Get number of variables in problem.

    :return: number of variables
    :rtype: ``int``
    """
    return len(self._variables)

  def size_f(self):
    """Get number of objectives in problem.

    :return: number of objectives
    :rtype: ``int``
    """
    return len(self._objectives)

  def size_c(self):
    """Get number of constraints in problem.

    :return: number of constraints
    :rtype: ``int``
    """
    return len(self._constraints)

  def size_nf(self):
    """Get number of blackboxed objective noise in problem.

    :return: dimensionality of the objective noise
    :rtype: ``int``

    .. versionadded:: 6.14
    """
    if self.__modified:
      self._validate()
    return self.__size_nf

  def size_nc(self):
    """Get number of blackboxed constraint noise in problem.

    :return: dimensionality of the constraint noise
    :rtype: ``int``

    .. versionadded:: 6.14
    """
    if self.__modified:
      self._validate()
    return self.__size_nc

  def size_s(self):
    """Get number of stochastic variables in problem.

    :return: number of stochastic variables
    :rtype: ``int``

    For adding stochastic variables, see :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()`.
    """
    stochasticSize = 0
    if self._stochastic:
      stochasticSize = self._stochastic.size()
    return stochasticSize

  def size_full(self):
    """Get full size of evaluated data (including gradients)

    :return: total number of objectives, constraints, gradients, and noise components
    :rtype: ``int``

    If gradients are not enabled (see
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_objectives_gradient()`,
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()`),
    the full size is equal to
    :meth:`~da.p7core.gtopt.ProblemGeneric.size_f()` +
    :meth:`~da.p7core.gtopt.ProblemGeneric.size_c()`.

    If all gradients are enabled and all gradients are dense, full size is
    (:meth:`~da.p7core.gtopt.ProblemGeneric.size_f()` +
    :meth:`~da.p7core.gtopt.ProblemGeneric.size_c()`) ×
    (1 + :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()`).

    In the case of using sparse gradients, full size depends on the number of non-zero
    elements in the gradient (see the *sparse* argument to
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_objectives_gradient()` and
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()`).
    You can also get the number of gradient values from
    :meth:`~da.p7core.gtopt.ProblemGeneric.objectives_gradient()` and
    :meth:`~da.p7core.gtopt.ProblemGeneric.constraints_gradient()`, for example::

      enabled, sparse, rows, columns = problem.objectives_gradient()
      if sparse:
        size_obj_grad = len(rows)  # the number of objective gradient values
                                   # len(rows) and len(columns) are equal

    """
    return self.size_f() + self.size_c() + sum(_grad_size(self)) + self.size_nc() + self.size_nf()

  def objectives_gradient(self):
    """Get objective gradient info.

    :return: objective gradient info
    :rtype: ``tuple(bool, bool, tuple, tuple)``

    This method returns a tuple of four elements (*enabled*, *sparse*, non-zero rows, non-zero columns).

    First boolean element (*enabled*) is ``True`` if analytical objective gradients are enabled in the problem. If *enabled* is ``False``, all other elements should be ignored as meaningless.

    Second boolean (*sparse*) has a meaning only if *enabled* is ``True``. Value of *sparse* is ``True`` if the gradients are sparse. If *sparse* is ``False`` (gradients are dense), all other elements in the returned tuple should be ignored as meaningless.

    Tuple elements provide the lists of non-zero rows and columns for sparse gradients. Naturally, these lists only have a meaning when both *enabled* and *sparse* are ``True``; in all other cases the tuples are empty.

    For an example of using sparse gradients, see
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()`.

    """
    return (self._grad_objectives, self._grad_objectives_sparse, self._grad_objectives_rows, self._grad_objectives_cols)

  def constraints_gradient(self):
    """Get constraint gradient info.

    :return: constraint gradient info
    :rtype: ``tuple(bool, bool, tuple, tuple)``

    This method returns a tuple of four elements (*enabled*, *sparse*, non-zero rows, non-zero columns).

    First boolean element (*enabled*) is ``True`` if analytical constraint gradients are enabled in the problem. If *enabled* is ``False``, all other elements should be ignored as meaningless.

    Second boolean (*sparse*) has a meaning only if *enabled* is ``True``. Value of *sparse* is ``True`` if the gradients are sparse. If *sparse* is ``False`` (gradients are dense), all other elements in the returned tuple should be ignored as meaningless.

    Tuple elements provide the lists of non-zero rows and columns for sparse gradients. Naturally, these lists only have a meaning when both *enabled* and *sparse* are ``True``; in all other cases the tuples are empty.

    """
    return (self._grad_constraints, self._grad_constraints_sparse, self._grad_constraints_rows, self._grad_constraints_cols)

  def get_stochastic_values(self, quantity):
    """Get stochastic values.

    :param quantity: number of values to get
    :type quantity: ``int``
    :return: stochastic values
    :rtype: ``list``

    Returns :arg:`quantity` random values from the stochastic distribution
    added to the problem.
    The distribution must be set before using this method
    (see :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()`).

    """
    return self._stochastic.get(quantity) if self._stochastic else []
  #
  # User problem definition
  #
  def add_variable(self, bounds, initial_guess=None, name=None, hints=None):
    """Add a new problem variable.

    :param bounds: bounds or levels
    :param initial_guess: initial guess
    :param name: the name of the variable
    :param hints: additional hints
    :type bounds: ``tuple(float)``
    :type initial_guess: ``float``
    :type name: ``str``
    :type hints: ``dict``

    .. versionchanged:: 6.14
       added discrete and categorical variables support when using the class with GTDoE only.

    .. versionchanged:: 6.15
       added discrete variables support to GTOpt.

    .. versionchanged:: 6.29
       added stepped variables support.

    .. versionchanged:: 6.33
       added categorical variables support to GTOpt.

    Declares a new variable in the problem.

    For continuous and integer variables, :arg:`bounds` is a tuple of two ``float`` values: ``(lower, upper)``.
    The :arg:`initial_guess`, if specified, must be within :arg:`bounds`.

    For discrete, stepped, and categorical variables, :arg:`bounds` is
    a tuple specifying allowed values (levels) of the variable.
    The sorting order of those values does not matter, the list of levels may be unsorted.
    All values must be ``float`` --- for example, if your problem includes a categorical variable
    with string values, you should denote its categories with arbitrary ``float`` numbers.
    The :arg:`initial_guess`, if specified, must be one of the level values specified by :arg:`bounds`.

    For continuous variables only, ``None`` is valid as the lower or upper bound,
    meaning that the variable is unbound in the respective direction.
    Your problem may declare continuous variables that are unbound in one or both directions,
    given that the problem satisfies the following:

    * All responses are computationally cheap, that is, you do not set
      the *@GTOpt/EvaluationCostType* hint to ``"Expensive"`` for any response.
    * There are no integer or discrete variables in the problem.
    * There are no stochastic variables in the problem.

    In other kinds of problems, each variable requires numeric bounds or levels,
    and using unbound variables leads to an :exc:`~da.p7core.InvalidProblemError` exception when solving.

    The :arg:`name` argument is optional; if you do not provide a name, it is generated automatically.
    Auto names are ``"x1"``, ``"x2"``, ``"x3"``, and so on, in the order of adding variables to a problem.

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* names of variables are no longer required to be valid Python identifiers.

    The *hints* parameter can be used to specify type of the variable --- see :ref:`ug_gtopt_hints` for details.
    It is a dictionary ``{hint name: value}``, for example ``{"@GT/VariableType": "Integer"}``.

    Variables are always indexed in the order of adding them to a problem. This indexing is kept in the *queryx* parameter to :meth:`.ProblemGeneric.evaluate()`, in the *x* parameter to problem definition methods of the simplified problem classes (such as :meth:`.ProblemConstrained.define_objectives()`, :meth:`.ProblemConstrained.define_constraints()` and the like), and in :class:`~da.p7core.gtopt.Result` attributes.

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* name indexing for variables (as in ``x["name"]`` or ``x.name``) is no longer supported.

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")
    if not name:
      name = 'x%d' % (len(self._variables) + 1)
    self._variables.append(_Variable(name, bounds, initial_guess, hints))

  def set_variable_initial_guess(self, index, initial_guess):
    """Set initial guess to a given problem variable.

    :param index: variable index in the list of problem variables.
    :param initial_guess: initial guess for variable
    :type index: ``int``
    :type initial_guess: ``None``, ``float``

    """
    if (index < 0) or (index >= len(self._variables)):
      raise ValueError('Wrong variable index')
    ivar = self._variables[index]
    if (initial_guess is not None):
      _shared.check_concept_numeric(initial_guess, "initial guess of variable '%s'" % ivar.name)
    if initial_guess is not None:
      initial_guess = float(initial_guess)
    else:
      initial_guess = _shared._NONE

    if ivar.initial_guess != initial_guess:
      ivar.initial_guess = initial_guess
      self.__modified = True
    #relax, don't check, allow user to change guesses with check validate on run.

  def set_variable_hints(self, index, hints):
    """Set hints for a variable.

    :param index: index of the variable in the list of problem variables
    :param hints: hint settings
    :type index: ``int``
    :type hints: ``dict``

    Resets all hints previously set for the variable,
    replacing all existing settings with the new settings from :arg:`hints`.
    To update hint settings without resetting them,
    use :meth:`~da.p7core.gtopt.ProblemGeneric.update_variable_hints()`.
    """
    if (index < 0) or (index >= len(self._variables)):
      raise ValueError('Wrong variable index')
    ivar = self._variables[index]
    ivar.hints = _backend.normalize_hints_name(hints, ("\"%s\" variable" % ivar.name))
    self.__modified = True

  def update_variable_hints(self, index, hints):
    """Update hints for a variable.

    :param index: index of the variable in the list of problem variables
    :param hints: hint settings
    :type index: ``int``
    :type hints: ``dict``

    .. versionadded:: 6.35

    Updates hint settings for the variable:
    if :arg:`hints` sets some hint, the new setting replaces the existing one,
    but hints not found in :arg:`hints` keep existing settings.
    To reset all existing hint settings,
    use :meth:`~da.p7core.gtopt.ProblemGeneric.set_variable_hints()`.
    """
    if (index < 0) or (index >= len(self._variables)):
      raise ValueError('Wrong variable index')
    if hints:
      ivar = self._variables[index]
      ivar.hints.update(_backend.normalize_hints_name(hints, ("\"%s\" variable" % ivar.name)))
      self.__modified = True

  def set_objective_hints(self, index, hints):
    """Set hints for an objective.

    :param index: index of the objective in the list of problem objectives
    :param hints: hint settings
    :type index: ``int``
    :type hints: ``dict``

    Resets all hints previously set for the objective,
    replacing all existing settings with the new settings from :arg:`hints`.
    To update hint settings without resetting them,
    use :meth:`~da.p7core.gtopt.ProblemGeneric.update_objective_hints()`.
    """
    if (index < 0) or (index >= len(self._objectives)):
      raise ValueError('Wrong objective index')
    ivar = self._objectives[index]
    ivar.hints = _backend.normalize_hints_name(hints, ("\"%s\" objective" % ivar.name))
    self.__modified = True

  def update_objective_hints(self, index, hints):
    """Update hints for an objective.

    :param index: index of the objective in the list of problem objectives
    :param hints: hint settings
    :type index: ``int``
    :type hints: ``dict``

    .. versionadded:: 6.35

    Updates hint settings for the objective:
    if :arg:`hints` sets some hint, the new setting replaces the existing one,
    but hints not found in :arg:`hints` keep existing settings.
    To reset all existing hint settings,
    use :meth:`~da.p7core.gtopt.ProblemGeneric.set_objective_hints()`.
    """
    if (index < 0) or (index >= len(self._objectives)):
      raise ValueError('Wrong objective index')
    ivar = self._objectives[index]
    ivar.hints.update(_backend.normalize_hints_name(hints, ("\"%s\" objective" % ivar.name)))
    self.__modified = True

  def set_constraint_hints(self, index, hints):
    """Set hints for a constraint.

    :param index: index of the constraint in the list of problem constraints
    :param hints: hint settings
    :type index: ``int``
    :type hints: ``dict``

    Resets all hints previously set for the constraint,
    replacing all existing settings with the new settings from :arg:`hints`.
    To update hint settings without resetting them,
    use :meth:`~da.p7core.gtopt.ProblemGeneric.update_constraint_hints()`.
    """
    if (index < 0) or (index >= len(self._constraints)):
      raise ValueError('Wrong constraint index')
    ivar = self._constraints[index]
    ivar.hints = _backend.normalize_hints_name(hints, ("\"%s\" constraint" % ivar.name))
    self.__modified = True

  def update_constraint_hints(self, index, hints):
    """Update hints for a constraint.

    :param index: index of the constraint in the list of problem constraints
    :param hints: hint settings
    :type index: ``int``
    :type hints: ``dict``

    .. versionadded:: 6.35

    Updates hint settings for the constraint:
    if :arg:`hints` sets some hint, the new setting replaces the existing one,
    but hints not found in :arg:`hints` keep existing settings.
    To reset all existing hint settings,
    use :meth:`~da.p7core.gtopt.ProblemGeneric.set_constraint_hints()`.
    """
    if (index < 0) or (index >= len(self._constraints)):
      raise ValueError('Wrong constraint index')
    ivar = self._constraints[index]
    ivar.hints.update(_backend.normalize_hints_name(hints, ("\"%s\" constraint" % ivar.name)))
    self.__modified = True

  def set_variable_bounds(self, index, bounds):
    """Set bounds for a variable.

    :param index: index of the variable in the list of problem variables
    :param bounds: bounds or levels for the variable
    :type index: ``int``
    :type bounds: :term:`array-like`

    .. versionchanged:: 6.14
       added the support for discrete and categorical variables.

    See :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()` for details on how to use :arg:`bounds` for discrete and categorical variables.

    """
    if (index < 0) or (index >= len(self._variables)):
      raise ValueError('Wrong variable index')
    ivar = self._variables[index]
    if not _shared.is_iterable(bounds):
      raise TypeError('Wrong variable bounds structure!')
    for bound in bounds:
      if bound is not None:
        _shared.check_concept_numeric(bound, 'variable \'%s\' bound values' % ivar.name)

    ivar.bounds = _shared.convert_to_1d_array(bounds)
    if not ivar.bounds.size:
      raise ValueError('Variable must define bounds!')
    vmin = _get_gtopt_negative_infinity()
    vmax = _get_gtopt_positive_infinity()
    ivar.bounds = _numpy.clip(ivar.bounds, vmin, vmax)#nan seems to be safe
    self.__modified = True


  def add_objective(self, name=None, hints=None):
    """Add a new problem objective.

    :param name: the name of the objective
    :param hints: optimization hints
    :type name: ``str``
    :type hints: ``dict``

    Initializes a new objective in the problem.

    The *name* argument is optional; if you do not provide a name, it is generated automatically.
    Auto names are ``"f1"``, ``"f2"``, ``"f3"``, and so on, in the order of adding objectives to a problem.

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* names of objectives are no longer required to be valid Python identifiers.

    The *hints* argument sets objective-specific options that may direct optimizer to use alternative internal algorithms to increase performance
    (see :ref:`ug_gtopt_hints`).
    It is a dictionary ``{hint name: value}``, for example ``{"@GTOpt/LinearityType": "Quadratic"}``.

    If you implement :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()`,
    objectives in *querymask* are indexed in the order of adding them to a problem.
    This indexing order is also kept in :class:`~da.p7core.gtopt.Result` attributes.

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* name indexing for objectives is no longer supported.

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")
    if not name:
      name = 'f%d' % (len(self._objectives) + 1)
    self._objectives.append(_Objective(name, hints))

  def add_constraint(self, bounds, name=None, hints=None):
    """Add a new problem constraint.

    :param bounds: low and high bounds
    :param name: the name of the constraint
    :param hints: optimization hints
    :type bounds: :term:`array-like`
    :type name: ``str``
    :type hints: ``dict``

    Initializes a new constraint in the problem.

    The *bounds* argument is a tuple of two values: ``(lower, upper)``.
    One of the bounds can be ``None``, meaning that there is no respective bound for the constraint.

    The *name* argument is optional; if you do not provide a name, it is generated automatically.
    Auto names are ``"c1"``, ``"c2"``, ``"c3"``, and so on, in the order of adding constraints to a problem.

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* names of constraints are no longer required to be valid Python identifiers.

    The *hints* argument sets constraint-specific options that may direct optimizer to use alternative internal algorithms to increase performance
    (see :ref:`ug_gtopt_hints`).
    It is a dictionary ``{hint name: value}``, for example ``{"@GTOpt/LinearityType": "Quadratic"}``.

    If you implement :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()`,
    constraints in *querymask* are indexed after objectives and in the order of adding constraints to a problem.
    This indexing order is also kept in :class:`~da.p7core.gtopt.Result` attributes.

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* name indexing for constraints is no longer supported.

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")
    if not name:
      name = 'c%d' % (len(self._constraints) + 1)
    self._constraints.append(_Constraint(name, bounds, hints))

  def set_constraint_bounds(self, index, bounds):
    """Set bounds for a constraint.

    :param index: index of the constraint in the list of problem constraints
    :param bounds: lower and upper bounds
    :type index: ``int``
    :type bounds: :term:`array-like`

    """
    if (index < 0) or (index >= len(self._constraints)):
      raise ValueError('Wrong constraint index')
    icon = self._constraints[index]
    lower_bound = vmin = _get_gtopt_negative_infinity()
    upper_bound = vmax = _get_gtopt_positive_infinity()
    if _shared.is_sized(bounds) and len(bounds) == 2:
      if bounds[0] is not None:
        _shared.check_concept_numeric(bounds[0], 'constraint \'%s\' lower bound' % icon.name)
        lower_bound = min(max(vmin, _shared.parse_float(bounds[0])), vmax)
      if bounds[1] is not None:
        _shared.check_concept_numeric(bounds[1], 'constraint \'%s\' upper bound' % icon.name)
        upper_bound = max(min(vmax, _shared.parse_float(bounds[1])), vmin)
      if bounds[0] is not None and bounds[1] is not None:
        if bounds[0] > bounds[1]:
          raise ValueError('Invalid constraint bounds %s, lower > upper' % str(bounds))
    else:
      raise TypeError('Wrong constraint bounds structure!')
    icon.lower_bound = lower_bound
    icon.upper_bound = upper_bound

    self.__modified = True

  def set_stochastic(self, distribution, generator=None, name=None, seed=0):
    """Set stochastic distribution for a robust optimization problem.

    :param distribution: a stochastic distribution object

    .. versionchanged:: 6.15
       the :arg:`generator`, :arg:`name`, and :arg:`seed` arguments are no longer used.

    This method is essential for robust optimization problems.
    It adds stochastic variables `\\xi_i` (see section :ref:`ug_gtopt_ro_formulation`)
    and sets the stochastic distribution used in generating random values for these variables.

    The distribution is implemented by user, see section :ref:`ug_gtopt_stochastic_vars` for details.
    The number of stochastic variables added is equal to the distribution dimension
    (see :meth:`~.Distribution.getDimension`).
    Stochastic variables are always added and indexed after normal variables.
    For example, in :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()` you can do something like:

    .. code-block:: python

       bounds = (0, 1)
       add_variable(bounds)  # indexed 0
       add_variable(bounds)  # indexed 1
       set_stochastic(my_distr)  # assuming the distribution is 2-dimensional,
                                 # adds 2 variables indexed (!) 3 and 4
       add_variable(bounds)  # indexed 2 despite here it is called after set_stochastic()

    Then, when you process :arg:`queryx` in :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()`,
    the variables are indexed as noted above.
    The fact that you call :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()`
    before the final :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()` call does not matter.

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.
    See :ref:`ug_gtopt_stochastic_vars` for a guide.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")
    if not name:
      name = 'sd1'

    self._stochastic = _Stochastic(distribution, name)

  def enable_objectives_gradient(self, sparse=None):
    """Enable using analytical objective gradients.

    :param sparse: non-zero rows and columns
    :type sparse: :term:`array-like`

    By default, the problem automatically uses numerical differentiation to provide objective gradient values to
    :class:`~da.p7core.gtopt.Solver`. Alternatively, you may provide gradients in :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()` ---
    see its description for more details. Before that, the problem has to be switched to analytical objective gradients mode
    by calling :meth:`~da.p7core.gtopt.ProblemGeneric.enable_objectives_gradient()` once upon initialization.

    Gradients may be set sparse using the *sparse* argument. This is a tuple of two integer arrays of same length
    where first array contains indices of non-zero rows in objective gradient, and second array contains indices
    of non-zero columns. ``None`` (default) means that objective gradient is dense.

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.
    Note that not all problem classes support analytical gradients.

    For an example of using sparse gradients, see
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()`.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")

    if sparse is not None:
      _shared.check_concept_sequence(sparse, 'sparse objectives gradient description')
      if not len(sparse):
        sparse = None # empty structure means no structure

    if sparse is not None:
      try:
        if len(sparse) != 2:
          raise IndexError()

        grad_objectives_rows = tuple(_ for _ in sparse[0])
        grad_objectives_cols = tuple(_ for _ in sparse[1])

        if len(grad_objectives_rows) != len(grad_objectives_cols):
          raise ValueError('Wrong sparse gradient description: both index arrays must have the same length!')

        indicesList = list(zip(grad_objectives_rows, grad_objectives_cols))
        indicesSet = frozenset(indicesList)
        if len(indicesList) != len(indicesSet):
          raise ValueError('Wrong sparse gradient description: duplicate indices encountered!')

        self._grad_objectives = True
        self._grad_objectives_sparse = True
        self._grad_objectives_rows = grad_objectives_rows
        self._grad_objectives_cols = grad_objectives_cols
      except IndexError:
        _shared.reraise(ValueError, 'Wrong sparse gradient description: must be either empty or be a tuple of two integer arrays.', _sys.exc_info()[2])
    else:
      self._grad_objectives = True
      self._grad_objectives_sparse = False
      self._grad_objectives_rows = tuple()
      self._grad_objectives_cols = tuple()

  def disable_objectives_gradient(self):
    """Disable using analytical objective gradients.

    .. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

    *New in version 2.0 Release Candidate 1.*

    Disables analytical gradients for objectives and switches back to using numerical differentiation
    (see :meth:`~da.p7core.gtopt.ProblemGeneric.enable_objectives_gradient()`).

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`. It is intended to
    cancel analytical objective gradients in a new problem class inherited from a problem with enabled analytical gradients.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")
    self._grad_objectives = False
    self._grad_objectives_sparse = False

  def enable_constraints_gradient(self, sparse=None):
    r"""Enable using analytical constraint gradients.

    :param sparse: non-zero rows and columns
    :type sparse: :term:`array-like`

    By default, the problem automatically uses numerical differentiation to provide constraint gradient values to
    :class:`~da.p7core.gtopt.Solver`. Alternatively, you may provide gradients in :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()` ---
    see its description for more details. Before that, the problem has to be switched to analytical constraint gradients mode
    by calling :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()` once upon initialization.
    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.
    Note that not all problem classes support analytical gradients.

    Gradients may be set sparse using the *sparse* argument.
    This is a tuple of two lists of the same length
    where the first list contains the indices of non-zero rows in the gradient,
    and the second list contains the indices of non-zero columns.
    ``None`` (default) means that constraint gradient is dense.

    For example, consider a problem with two variables and two constraints:

    .. math::

      \begin{array}{cc}
        (x_1 - 1)^2 &\le 0\\
        x_2 &\le 0
      \end{array}

    The Jacobian matrix for this problem is

    .. math::

      \left(\begin{array}{cc}
        2x_1 - 2 & 0\\
        0  & 1
      \end{array}\right)

    Non-zero elements in the Jacobian are (0, 0) and (1, 1),
    so the *sparse* argument should be ``([0, 1], [0, 1])``.
    The problem can be defined as follows::

      from da.p7core import gtopt

      class MyProblem(gtopt.ProblemGeneric):

        def prepare_problem(self):
          self.add_variable((None,None))
          self.add_variable((None,None))
          self.add_constraint((None, 0))
          self.add_constraint((None, 0))
          self.enable_constraints_gradient(([0, 1], [0, 1]))

        def evaluate(self, x_batch, mask_batch):
          c_batch = []
          # mask_batch is ignored for brevity
          for x in x_batch:
            c_batch.append([(x[0] - 1)**2, x[1], 2*(x[0] - 1), 1])
          # since all responses were calculated, extend the mask to [1, 1, 1, 1]
          mask_batch = [1, 1, 1, 1] * len(mask_batch)
          return c_batch, mask_batch

    There are four elements in the list of evaluations in ``c_batch.append``,
    while in the case of dense gradients it would be
    ``c_batch.append([(x[0] - 1)**2, x[1], 2*(x[0] - 1), 0, 0, 1])``.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")

    if sparse is not None:
      _shared.check_concept_sequence(sparse, 'sparse constraints gradient description')
      if not len(sparse):
        sparse = None # empty structure means no structure

    if sparse is not None:
      try:
        if len(sparse) != 2:
          raise IndexError()

        grad_constraints_rows = tuple(_ for _ in sparse[0])
        grad_constraints_cols = tuple(_ for _ in sparse[1])

        if len(grad_constraints_rows) != len(grad_constraints_cols):
          raise ValueError('Wrong sparse gradient description: index arrays must have the same length!')

        indicesList = list(zip(grad_constraints_rows, grad_constraints_cols))
        indicesSet = frozenset(indicesList)
        if len(indicesList) != len(indicesSet):
          raise ValueError('Wrong sparse gradient description: duplicate indices encountered!')

        self._grad_constraints = True
        self._grad_constraints_sparse = True
        self._grad_constraints_rows = grad_constraints_rows
        self._grad_constraints_cols = grad_constraints_cols
      except IndexError:
        _shared.reraise(ValueError, 'Wrong sparse gradient description: must be either empty or be a tuple of two integer arrays.', _sys.exc_info()[2])
    else:
      self._grad_constraints = True
      self._grad_constraints_sparse = False
      self._grad_constraints_rows = tuple()
      self._grad_constraints_cols = tuple()

  def disable_constraints_gradient(self):
    """Disable using analytical constraint gradients.

    .. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

    *New in version 2.0 Release Candidate 1.*

    Disables analytical gradients for constraints and switches back to using numerical differentiation
    (see :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()`).

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`. It is intended to
    cancel analytical constraint gradients in a new problem class inherited from a problem with enabled analytical gradients.

    """
    if self.__problem_initialized:
      raise _ex.IllegalStateError("Can't change initialized problem!")
    self._grad_constraints = False
    self._grad_constraints_sparse = False

  def _get_admissible_categories(self):
    """Provide current state of admissible combination of categorical variables

    :return: allowed combinations of categorical variables
    :rtype: `list(numpy.ndarray)`

    """
    # @todo : consider setting read-only flag on view
    return [v.view(_numpy.ndarray) for v in self._admissible_values]

  def _set_admissible_categories(self, admissible_values):
    """Set admissible combination of categorical variables.

    By default all combinations of categorical variables are allowed. This method allows setting admissible categories explicitly.

    The parameter `admissible_values` describes allowed categorical variables can be any iterable container contains iterables.
    Size of internal containers must match number of categorical variables. Values of admissible  values must exactly coincidence
    with provided possible categorical levels.

    This method should be set in  :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`. It can be set multiple times.
    If called with non-empty parameters, it appends new combinations to already set.
    If called with `None` argument, it resets all set combinations and makes all combinations allowed.

    :param admissible_values: allowed combinations of categorical variables
    :type admissible_values: ``iterable(iterable)``

    """
    self.__modified = True


    if admissible_values is None:
      self._admissible_values = set()
      return

    if not _shared.is_iterable(admissible_values):
      raise TypeError('Wrong admissible categories structure!')

    if len(self._admissible_values) :
      shape = next(iter(self._admissible_values)).size
    else:
      shape = -1
    for tup in admissible_values:
      if not _shared.is_iterable(tup):
        raise TypeError('Wrong admissible categories entry structure!')
      new_entry = _shared.convert_to_1d_array(tup).view(_HashableNDArray)
      if shape < 0: shape = new_entry.size
      elif new_entry.size != shape: raise TypeError('All admissible categories entries must have the same length as number of categorical variables! Run ProblemGeneric.set_admissible_categories(None) to clean up previously set admissible categories.')
      self._admissible_values.add(new_entry)

  def variable_indexes_by_type(self, var_type):
    """Return list of indexes of variables of the given type.

    :param var_type: type name
    :type var_type: ``str``
    :return: indexes of variables which have the :arg:`var_type` type
    :rtype: ``list``

    .. versionadded:: 6.14

    Types are: ``"continuous"``, ``"integer"``, ``"stepped"``, ``"discrete"``, ``"categorical"``.
    Type names are case-insensitive.

    """
    var_type_key = _backend.normalize_option_name("@GT/VariableType")
    _backend.check_options_value({var_type_key: var_type})
    var_type_default = _backend.default_option_value(var_type_key)
    var_type = str(var_type).lower()

    return [i for i, ivar in enumerate(self._variables) if ivar.hints.get(var_type_key, var_type_default).lower() == var_type]

  prepare_problem = _AbstractMethod()
  """The problem initialization method, has to be implemented by user. Use the following methods for problem definition:

  * Basic problem definition:

    * :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`
    * :meth:`~da.p7core.gtopt.ProblemGeneric.add_objective()`
    * :meth:`~da.p7core.gtopt.ProblemGeneric.add_constraint()`

  * Advanced features:

    * :meth:`~da.p7core.gtopt.ProblemGeneric.enable_objectives_gradient()` --- use analytical gradients of objective functions
    * :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()` --- use analytical gradients of constraint functions
    * :meth:`~da.p7core.gtopt.ProblemGeneric.set_history()` --- configure saving objective and constraint evaluations; note that the memory :attr:`~da.p7core.gtopt.ProblemGeneric.history` is enabled by default, which increases memory consumption
    * :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()` --- essential method for robust optimization problems

  See the usage in :ref:`codesample_gtopt_generic`.
  """


  def _get_header(self):
    return ",".join('"' + field_name.replace('"', '""') + '"' for field_name in self._history_fields[1])

  def set_history(self, **kwargs):
    """
    Configure saving objective and constraint evaluations.

    :param add_header: add a header to the history file
    :type add_header: ``bool``
    :param file: write history to file
    :type file: ``str``, ``file`` or ``None``
    :param memory: store history in memory
    :type memory: ``bool``

    .. versionadded:: 4.0

    Return values of :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()` can be saved to memory
    or to a file on disk. History saving modes are independent: both can be enabled simultaneously
    so history is saved in memory while also writing to a file. Default configuration is to save
    history to memory only.

    .. note::

       Default configuration increases memory consumption. If you implement your own way to save
       the history of evaluations, always use :meth:`~da.p7core.gtopt.ProblemGeneric.disable_history()`.
       If there are a lot of evaluations in your problem, consider reconfiguring history to only write
       it to a file.

    If *memory* is ``True``, evaluations are saved to :attr:`~da.p7core.gtopt.ProblemGeneric.history`.
    If ``False``, disables updating :attr:`~da.p7core.gtopt.ProblemGeneric.history` but does not
    clear it. Re-enabling in case :attr:`~da.p7core.gtopt.ProblemGeneric.history` is not empty
    appends to existing history; if it is not wanted, call
    :meth:`~da.p7core.gtopt.ProblemGeneric.clear_history()` first.

    The *file* argument can be a path string or a file-like object (enables writing history to file).
    Note that the file is opened in append mode.
    To disable the file history, set *file* to ``None``.
    Values in a history file are comma-separated.

    If *add_header* is ``True``, the first line appended to file is a header containing
    the names of problem variables, objectives and constraints set by
    :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`,
    :meth:`~da.p7core.gtopt.ProblemGeneric.add_objective()`, and
    :meth:`~da.p7core.gtopt.ProblemGeneric.add_constraint()`.
    The header is enabled by default, and can be disabled by setting *add_header* to ``False``.

    """
    recognized = ('memory', 'file', 'add_header')
    for keyword, value in kwargs.items():
      if keyword not in recognized:
        raise TypeError(("Keyword argument '%s' is not recognized!\nAvailable flags are:\n'"
                          + "', '".join(recognized)  + "'") % keyword)
      if keyword == recognized[0]:
        _shared.check_type(value, recognized[0], bool)
        self._history_inmemory = value
      if keyword == recognized[1]:
        if isinstance(value, string_types) or hasattr(value, 'write') or value is None:
          if isinstance(value, string_types):
            with open(value, "a+"):
              pass
          self._history_file = value
        else:
          raise ValueError('Wrong file argument passed')
      if keyword == recognized[2]:
        _shared.check_type(value, recognized[2], bool)
        self._header_required = value


  def enable_history(self, inmemory=True, file_arg=None, header=True):
    """
    Enable saving objective and constraint evaluations.

    :param file_arg: write history to file
    :type file_arg: ``str`` or ``file``
    :param header: add a header to the history file
    :type header: ``bool``
    :param inmemory: store history in memory (on by default)
    :type inmemory: ``bool``

    .. versionadded:: 1.11.0

    .. deprecated:: 4.0
       use :meth:`~da.p7core.gtopt.ProblemGeneric.set_history()` instead.

    Since version 4.0, replaced by a more convenient
    :meth:`~da.p7core.gtopt.ProblemGeneric.set_history()` method. See also
    :meth:`~da.p7core.gtopt.ProblemGeneric.clear_history()` and
    :meth:`~da.p7core.gtopt.ProblemGeneric.disable_history()`.

    """
    if not inmemory is None:
      self.set_history(memory=inmemory, file=file_arg, add_header=header)
    else:
      self.set_history(file=file_arg, add_header=header)

  def disable_history(self):
    """
    Disable saving objective and constraint evaluations completely.

    .. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

    *New in version 2.0 Release Candidate 1.*

    Disables both memory and file history. Objective and constraint evaluation results
    will no longer be stored in :attr:`~da.p7core.gtopt.ProblemGeneric.history` or the
    configured history file (see *file* in :meth:`~da.p7core.gtopt.ProblemGeneric.set_history`).

    Disabling does not clear current contents of :attr:`~da.p7core.gtopt.ProblemGeneric.history`
    (see :meth:`~da.p7core.gtopt.ProblemGeneric.clear_history()`).

    """
    self.set_history(memory=False, file=None)

  def clear_history(self):
    """
    Clear :attr:`~da.p7core.gtopt.ProblemGeneric.history`.

    .. versionadded:: 4.0

    Removes all evaluations currently stored in the memory history, but does not disable it.
    For disabling, see :meth:`~da.p7core.gtopt.ProblemGeneric.disable_history()` or
    :meth:`~da.p7core.gtopt.ProblemGeneric.set_history()`.

    """
    self._history_cache = []  # list of 1D numpy arrays, note GTOptAPI.collect_all_designs() method accesses _history_cache directly


  @property
  def _history_fields(self):
    """
    Enumerates data fields in :attr:`~da.p7core.gtopt.ProblemGeneric.history` and :attr:`~da.p7core.gtopt.ProblemGeneric.designs`.

    :type: ``tuple(list[tuple(str, int, int)], list[str])``

    The first element of result enumerates top-level fields name (``x``, ``f``, ``c``, and so on) followed by index of the first and one-past-last field columns.

    The second element of result is a list of columns name.

    """
    names_x = self.variables_names()
    names_f = self.objectives_names()
    names_c = self.constraints_names()

    size_x, size_s, size_f, size_c, size_nf, size_nc = self.size_x(), self.size_s(), self.size_f(), self.size_c(), self.size_nf(), self.size_nc()

    current_offset, current_length = 0, size_x
    basic_fields = [("x", current_offset, current_length)]
    columns_names = names_x

    if size_s:
      current_offset, current_length = current_length, current_length + size_s
      basic_fields.append(("stochastic", current_offset, current_length))
      columns_names.extend(('s%d' % i) for i in range(1, size_s + 1))

    if size_f:
      current_offset, current_length = current_length, current_length + size_f
      basic_fields.append(("f", current_offset, current_length))
      columns_names.extend(names_f)

    if size_c:
      current_offset, current_length = current_length, current_length + size_c
      basic_fields.append(("c", current_offset, current_length))
      columns_names.extend(names_c)


    dfdx_enabled, dfdx_sparse, dfdx_rows, dfdx_cols = self.objectives_gradient()

    if not dfdx_enabled:
      dfdx_fields = []
    elif dfdx_sparse:
      dfdx_fields = [(i, j) for i, j in zip(dfdx_rows, dfdx_cols)]
    else:
      dfdx_fields = [(i, j) for i in range(size_f) for j in range(size_x)]

    if dfdx_fields:
      current_offset, current_length = current_length, current_length + len(dfdx_fields)
      basic_fields.append(("dfdx", current_offset, current_length))
      columns_names.extend(("d_%s/d_%s" % (names_f[i], names_x[j])) for i, j in dfdx_fields)

    dcdx_enabled, dcdx_sparse, dcdx_rows, dcdx_cols = self.constraints_gradient()

    if not dcdx_enabled:
      dcdx_fields = []
    elif dcdx_sparse:
      dcdx_fields = [(i, j) for i, j in zip(dcdx_rows, dcdx_cols)]
    else:
      dcdx_fields = [(i, j) for i in range(size_c) for j in range(size_x)]

    if dcdx_fields:
      current_offset, current_length = current_length, current_length + len(dcdx_fields)
      basic_fields.append(("dcdx", current_offset, current_length))
      columns_names.extend(("d_%s/d_%s" % (names_c[i], names_x[j])) for i, j in dcdx_fields)

    if size_nf:
      current_offset, current_length = current_length, current_length + size_nf
      basic_fields.append(("nf", current_offset, current_length))
      columns_names.extend(("n_%s" % (response.name,)) for response in self._objectives if str(response.hints.get('@GT/NoiseLevel', 0)).lower() == 'fromblackbox')

    if size_nc:
      current_offset, current_length = current_length, current_length + size_nc
      basic_fields.append(("nc", current_offset, current_length))
      columns_names.extend(("n_%s" % (response.name,)) for response in self._constraints if str(response.hints.get('@GT/NoiseLevel', 0)).lower() == 'fromblackbox')

    return basic_fields, columns_names


  @property
  def history(self):
    """Exact history of problem evaluations stored in memory.

    :Type: :term:`array-like`

    .. versionadded:: 1.11.0

    Stores values of variables and evaluation results.
    Each element of the top-level list is one evaluated point.
    Nested list structure is *[variables, objectives, constraints, objective gradients, constraint gradients]*.
    Gradients are added only if analytical gradients are enabled, see
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_objectives_gradient()` and
    :meth:`~da.p7core.gtopt.ProblemGeneric.enable_constraints_gradient()`).

    .. versionchanged:: 5.1
       missing evaluation results are stored as ``None`` values, not NaN (``float``).

    Often :class:`~da.p7core.gtopt.Solver` requests only a partial evaluation of the problem
    (see the *querymask* argument to :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()`).
    For such points, non-evaluated functions (objectives, constraints, gradients)
    are noted with ``None`` values to distinguish them from a ``float`` NaN value.
    NaN in history specifically indicates that a function was evaluated but calculation failed
    (for example, the point to evaluate for was out of the function's domain).

    The history stores all inputs and outputs exactly as they were evaluated, which may be unconvenient
    in some cases. For example, :class:`~da.p7core.gtopt.Solver` can request objective and constraint
    values for the same point on different iterations, and in this case the point will appear
    in history two or more times. This is useful for tracing the optimization process, but when you
    want to re-use evaluation data, a more convenient representation can be found in
    :attr:`~da.p7core.gtopt.ProblemGeneric.designs`.

    .. note::

       Memory history is enabled by default, which increases memory consumption.
       If you implement your own way to save the history of evaluations,
       always use :meth:`~da.p7core.gtopt.ProblemGeneric.disable_history()`.
       If there are a lot of evaluations in your problem, consider reconfiguring history
       to only write it to a file (see :meth:`~da.p7core.gtopt.ProblemGeneric.set_history()`).

    """
    if not self._payload_objectives:
      return [[(None if hole else v) for v, hole in zip(row, _shared._find_holes(row))] for row in self._history_cache]
    regular_responses = [True]*(self.size_x() + self.size_s()) + self._regular_responses_mask().tolist()
    return [[(None if hole else (v if regular else self._payload_storage.decode_payload(v))) \
             for v, hole, regular in zip(row, _shared._find_holes(row), regular_responses)] for row in self._history_cache]

  @property
  def designs(self):
    """Compacted history of problem evaluations.

    :Type: :term:`array-like`

    .. versionadded:: 5.1

    Similar to :attr:`~da.p7core.gtopt.ProblemGeneric.history`, but ensures that each
    evaluated point appears only once by combining all evaluation results available for this point.
    Can still contain ``None`` values (meaning that some function was never evaluated) and NaN
    (meaning that a function was evaluated but calculation failed). For more details on the array
    structure and the meaning of ``None`` and NaN values see
    :attr:`~da.p7core.gtopt.ProblemGeneric.history`.

    """
    if not self._history_cache:
      return []

    key_size = self.size_x() + self.size_s()

    if self._payload_objectives:
      local_storage = _designs._PayloadStorage(self._payload_storage)
      proceed_payloads = _designs._join_payloads_callback(local_storage, tuple((key_size + _) for _ in self._payload_objectives))
    else:
      local_storage = None
      proceed_payloads = None

    compact_design = _designs._fill_gaps_and_keep_dups(_numpy.vstack(self._history_cache), slice(key_size), proceed_payloads)
    compact_design = _designs._select_unique_rows(compact_design, 0)
    compact_design_holes = _shared._find_holes(compact_design)
    if not self._payload_objectives:
      return [[(None if is_hole else value) for value, is_hole in zip(values, holes)] \
              for values, holes in zip(compact_design, compact_design_holes)]
    regular_responses = [True]*(self.size_x() + self.size_s()) + self._regular_responses_mask().tolist()
    return [[(None if hole else (v if regular else local_storage.decode_payload(v))) \
             for v, hole, regular in zip(values, holes, regular_responses)] \
              for values, holes in zip(compact_design, compact_design_holes)]

  evaluate = _AbstractMethod('iterable(iterable(float))', 'iterable(iterable(bool))')
  r"""Calculates values of objective functions and constraints. This method must be implemented by user.

  :param queryx: points to evaluate
  :type queryx: ``ndarray``, 2D ``float``
  :param querymask: evaluation requests mask
  :type querymask: ``ndarray``, 2D ``bool``
  :return: evaluation results (:term:`array-like`, 2D) and masks (:term:`array-like`, 2D, Boolean)
  :rtype: ``tuple(array-like, array-like)``

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* the :arg:`queryx` argument is ``ndarray``.

  .. versionchanged:: 6.19
     it is now possible to skip some evaluations requested by :class:`~da.p7core.gtopt.Solver`.

  .. versionchanged:: 6.24
     skipped evaluations may be indicated with ``None`` response values, regardless of the response flag in the output mask.

  When :class:`~da.p7core.gtopt.Solver` requests values of problem objectives and constraints,
  it sends the *queryx* sample to :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()`.
  The shape of this array is *(n, m)* where *n* is the number of points to evaluate
  (at most :ref:`GTOpt/BatchSize<GTOpt/BatchSize>`)
  and *m* is the input dimension
  (:meth:`~da.p7core.gtopt.ProblemGeneric.size_x()` +
  :meth:`~da.p7core.gtopt.ProblemGeneric.size_s()`).
  For each row, the first :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()` values
  are classic variables (see :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`),
  while the following :meth:`~da.p7core.gtopt.ProblemGeneric.size_s()` values
  are stochastic variables (see :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()`).

  :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()` has to process *queryx*
  and return values of objectives and constraints
  (and gradients, if they are enabled in the problem) according to the *querymask*.

  The *querymask* contains a mask of responses requested by :class:`~da.p7core.gtopt.Solver`
  for each point.
  It is a 2D ``ndarray`` (``bool``) of shape *(n, l)* where *n* is the number of points in *queryx* (a mask for each point; note that each point may have a different mask),
  and *l* is the mask length equal to :meth:`~da.p7core.gtopt.ProblemGeneric.size_full()`.

  Mask order is *[objectives, constraints, objective gradients, constraint gradients]*: for example, if three variables, one objective and
  two constraints were defined in the problem, and all gradients are dense, mask length is 12 (1 + 2 + 1 `\cdot` 3 + 2 `\cdot` 3).
  Masks are used to perform evaluations selectively --- that is, if GTOpt requests only one gradient value, there is
  no need to evaluate all other gradients, as well as objectives and constraints. To take advantage of this feature,
  the evaluation method should be implemented in such a way that supports selective evaluation by mask.

  An implementation of this method must return both evaluation results and evaluation masks as 2D arrays.
  Indexing order for both is the same as in the input *querymask*: *[objectives, constraints, objective gradients, constraint gradients]*,
  and array shape is determined by
  the length of the input batch,
  the number of objectives and constraints, and
  the number of gradient values
  (see :meth:`~da.p7core.gtopt.ProblemGeneric.size_full()` for more details).

  Returned evaluation mask informs :class:`~da.p7core.gtopt.Solver` what responses (objectives, constraints, gradients) were evaluated.
  For mask flags, use either ``bool`` or ``0`` and ``1``.

  * A response flagged ``True`` in the input mask should be evaluated.
    However, :class:`~da.p7core.gtopt.Solver` can handle failed evaluations to some extent,
    so there are several possibilities:

    * Evaluate the response, add its value to results, and flag it ``True`` in the output mask.
      If response evaluation fails, set its value to NaN and flag it ``True``.
    * Skip evaluation, flag the response ``False``, and put any value into results
      (:class:`~da.p7core.gtopt.Solver` discards this value;
      in :attr:`~da.p7core.gtopt.ProblemGeneric.designs` and
      :attr:`~da.p7core.gtopt.ProblemGeneric.history`, the value is replaced with ``None``).
    * Skip evaluation and set the response value to ``None``.
      In this case, the response flag in the returned mask is disregarded
      (you may set it ``True`` for simplicity).

  * A response flagged ``False`` in the input mask is optional.
    You may choose to:

    * Skip evaluation, flag it ``False``, and put any value into results
      (:class:`~da.p7core.gtopt.Solver` discards it;
      in :attr:`~da.p7core.gtopt.ProblemGeneric.designs` and
      :attr:`~da.p7core.gtopt.ProblemGeneric.history`, the value will be ``None``).
    * Skip evaluation and set the response value to ``None``.
      In this case, the response flag in the returned mask is disregarded
      (you may set it ``True`` for simplicity).
    * Evaluate the response, add it to results, and flag it ``True``.
      Despite :class:`~da.p7core.gtopt.Solver` did not request this value,
      it may still be useful in optimization.
      If response evaluation fails, set its value to NaN and flag it ``True``.

  Note that skipped (``None`` or flagged ``False``) and failed (NaN but flagged ``True``)
  evaluations may stop optimization prematurely.

  General advice is to evaluate responses selectively, separating those requested frequently from the ones requested rarely, for example:

  * Cheap and expensive functions (see :ref:`ug_gtopt_hints`).
  * Response values and gradient values.
  * Generic, linear and quadratic response functions (see :ref:`ug_gtopt_hints`).
  * In some cases you may prefer to evaluate objectives and constraints separately.

  Other separations mostly make sense only if they do not complicate the code.

  See the :ref:`codesample_gtopt_generic` code sample for an example implementation of this method.

  """

  def _postprocess_evaluate(self, resp, mask, shape):
    mask = _shared.as_matrix(mask, dtype=bool, shape=shape, name="responses mask")
    return self._translate_user_response(resp, mask, (self._regular_responses_mask() if self._payload_objectives else None), "evaluate")

  def _evaluate_sparse(self, queryx, querymask):
    if not self._last_error and (querymask.any(axis=0) == querymask.all(axis=0)).all():
      resp, mask = self.evaluate(queryx, querymask)
      return self._postprocess_evaluate(resp, mask, querymask.shape)

    querymask = querymask.copy()
    mask = _numpy.zeros_like(querymask)
    resp = _numpy.empty_like(querymask, dtype=float)
    resp.fill(_shared._NONE)

    if self._last_error:
      # no new evaluations while we have not processed an exception
      return resp, mask

    mask_buffer = _numpy.empty_like(querymask)
    resp_buffer = _numpy.empty_like(querymask, dtype=float)

    while querymask.any():
      active_responses = querymask[_numpy.argmax(querymask.sum(axis=1))]
      active_points    = (querymask == active_responses[_numpy.newaxis]).all(axis=1)

      resp_buffer.fill(_shared._NONE)
      mask_buffer.fill(False)
      mask_buffer[active_points] = querymask[active_points]
      querymask[active_points] = False

      current_mask_in = mask_buffer[active_points]
      try:
        current_resp, current_mask_out = self.evaluate(queryx[active_points], current_mask_in)
        resp_buffer[active_points, :], mask_buffer[active_points, :] = self._postprocess_evaluate(current_resp, current_mask_out, current_mask_in.shape)
      except:
        if not mask.any():
          # The user did not retrieved any data, it's safe to rerais an exception
          raise
        # Memorize an exception info, we'll forward it as soon as possible
        self._last_error = _sys.exc_info()
        break

      resp[mask_buffer] = resp_buffer[mask_buffer]
      mask |= mask_buffer

    return resp, mask

  def _evaluate(self, queryx, querymask, timecheck):
    try:
      self._timecheck = timecheck
      # pass a copy to avoid accidentally changing the origin
      queryx = _shared.as_matrix(queryx, dtype=float, copy=True, name="queryx")
      querymask = _shared.as_matrix(querymask, shape=(queryx.shape[0], None), dtype=bool, copy=True, name="querymask")
      resp, mask = self._evaluate_sparse(queryx, querymask)
    finally:
      self._timecheck = None

    if self._history_inmemory:
      history_block = _numpy.hstack((queryx, resp))
      history_block[:, queryx.shape[1]:][~mask] = _shared._NONE
      self._history_cache.extend(history_block)

    with self.open_history_file() as hf:
      if hf is not None:
        regular_responses_mask = self._regular_responses_mask()
        for x_i, resp_i, mask_i in zip(queryx, resp, mask):
          history_line = StringIO()
          history_line.write(','.join(('%.17g' % _) for _ in x_i))
          for resp_ij, mask_ij, regular_resp in zip(resp_i, mask_i, regular_responses_mask):
            history_line.write(',')
            if mask_ij:
              if regular_resp:
                history_line.write('%.17g' % resp_ij)
              else:
                payload_ij = self._payload_storage.decode_payload(resp_ij)
                if payload_ij:
                  history_line.write('"')
                  history_line.write(_shared.write_json(payload_ij).replace('"', '""'))
                  history_line.write('"')
          history_line.write('\n')
          hf.write(history_line.getvalue())

    return resp, mask

  def _regular_responses_mask(self):
    regular_responses_mask = _numpy.ones(self.size_full(), dtype=bool)
    regular_responses_mask[self._payload_objectives] = False
    return regular_responses_mask

  def _translate_user_response(self, resp, mask, regular_responses_mask, name=None):
    if regular_responses_mask is None or regular_responses_mask.all():
      regular_resp = _shared.as_matrix(resp, shape=mask.shape, detect_none=True, name=' '.join((str(name), 'responses')))
    else:
      if not isinstance(resp, _numpy.ndarray):
        resp = _shared.as_matrix(resp, shape=mask.shape, dtype=object, name=' '.join((str(name), 'responses')))

      regular_resp = _numpy.empty(mask.shape, dtype=float)
      regular_resp[:, regular_responses_mask] = resp[:, regular_responses_mask] # copy regular float data

      # proceed payloads
      for j in _numpy.where(~regular_responses_mask)[0]:
        regular_resp[:, j][mask[:, j]] = self._payload_storage.encode_payload(resp[:, j][mask[:, j]])

    regular_resp[~mask] = _shared._NONE
    return regular_resp, ~_shared._find_holes(regular_resp)

  @_contextlib.contextmanager
  def open_history_file(self):
    if self._history_file is None:
      yield None
    elif isinstance(self._history_file, string_types):
      fd = open(self._history_file, 'a+')
      try:
        if self._header_required:
          fd.write(self._get_header() + "\n")
          self._header_required = False
        yield fd
      finally:
        fd.close()
    else:
      if self._header_required:
        self._history_file.write(self._get_header() + "\n")
        self._header_required = False
      yield self._history_file

  @staticmethod
  def _normalize_option_name(name):
    return _backend.normalize_option_name(name)

  def _any_known_responses(self, known_responses, sample, sample_dim, sample_name):
    if sample is None or not sample_dim:
      return
    sample = _shared.as_matrix(sample, shape=(None, sample_dim), name=sample_name)
    if not sample.size:
      return
    known_responses |= ~_shared._find_holes(sample).all(axis=1)

  def _valid_input_points(self, sample_x, sample_f=None, sample_c=None, return_invalid=False, precision=8):
    if sample_x is None:
      return None, slice(0)

    original_sample_x = sample_x

    size_x = self.size_x()
    sample_x = _shared.as_matrix(sample_x, name="Input (x) part of the initial sample")
    if not sample_x.size:
      return original_sample_x, slice(0 if return_invalid else sample_x.shape[0])

    round_context = _DecimalContext(prec=precision) # create rounding context
    round_procedure = _numpy.vectorize(round_context.create_decimal_from_float, otypes=(float,))

    valid_points = ~_numpy.isnan(sample_x).any(axis=1) # +/-Inf is allowed, NaN is always prohibited

    size_f, size_c = self.size_f(), self.size_c()
    known_responses = _numpy.zeros_like(valid_points)

    if size_f or size_c:
      self._any_known_responses(known_responses, sample_f, size_f, "Initial sample of objective function values")
      self._any_known_responses(known_responses, sample_c, size_c, "Initial sample of constraint function values")

    for i, kind in enumerate(self.elements_hint(slice(size_x), "@GT/VariableType")):
      kind = "continuous" if not kind else kind.lower()
      bounds = self.variables_bounds(i)
      if kind == "continuous":
        # continuous variable must be within bounds or the point must have any known response
        valid_points[valid_points] = _numpy.logical_or(known_responses[valid_points],
                                                       _numpy.logical_and(_numpy.less_equal(bounds[0], sample_x[:, i][valid_points]),
                                                                          _numpy.less_equal(sample_x[:, i][valid_points], bounds[1])))
      else:
        rounded_input, rounded_bounds = round_procedure(sample_x[:, i]), round_procedure(bounds)
        if kind == "integer":
          # integer variable must be an integer, yet a small fractional part is allowed
          valid_points[valid_points] = _numpy.equal(_numpy.round(rounded_input[valid_points]), rounded_input[valid_points])
          # integer variable must be within bounds or the point must have any known response
          valid_points[valid_points] = _numpy.logical_or(known_responses[valid_points],
                                                         _numpy.logical_and(_numpy.less_equal(rounded_bounds[0], rounded_input[valid_points]),
                                                                            _numpy.less_equal(rounded_input[valid_points], rounded_bounds[1])))
          # return rounded points if we have to
          if (sample_x[:, i][valid_points] != rounded_input[valid_points]).any():
            if sample_x is original_sample_x:
              sample_x = sample_x.copy() # make a copy if we have not already
            sample_x[:, i] = rounded_input
        else:
          if kind == "stepped":
            # stepped variables must be approximately equal, or the point must have any known response
            valid_points[valid_points] = _numpy.logical_or(known_responses[valid_points],
                                          _numpy.equal(rounded_input[valid_points].reshape(-1, 1), [rounded_bounds]).any(axis=1))
          else:
            # discrete and categorical variables must be approximately equal
            valid_points[valid_points] = _numpy.equal(rounded_input[valid_points].reshape(-1, 1), [rounded_bounds]).any(axis=1)
          # read exact bounds values if we have to
          if _numpy.not_equal(bounds, rounded_bounds).any() or (sample_x[:, i][valid_points] != rounded_input[valid_points]).any():
            point_index, value_index = _numpy.where(_numpy.equal(rounded_input[valid_points].reshape(-1, 1), [rounded_bounds]))
            point_index = _numpy.where(valid_points)[0][point_index] # remap the indices of the valid points to the indices of the original vector
            if sample_x is original_sample_x:
              sample_x = sample_x.copy() # make a copy if we have not already
            sample_x[point_index, i] = _numpy.array(bounds, copy=_shared._SHALLOW)[value_index] # assign original, unmodified values from allowed set

    if valid_points.all():
      return sample_x, slice(0 if return_invalid else sample_x.shape[0])
    elif not valid_points.any():
      return sample_x, slice(sample_x.shape[0] if return_invalid else 0)

    if return_invalid:
      _numpy.invert(valid_points, out=valid_points)

    return sample_x, valid_points

  def _refill_from_history(self, dataset, fields):
    if not self._history_cache:
      return

    undefined_values = _shared._find_holes(dataset)

    if not undefined_values.any() and not self._payload_objectives:
      return

    fields = dict(fields)
    if all(k in ("x", "stochastic") for k in fields):
      return # sample contains keys only

    history_fields = dict((name, slice(start, stop)) for name, start, stop in self._history_fields[0])

    if any(((_ in fields)^(_ in history_fields)) for _ in ("x", "stochastic")):
      return # unconformed keys

    history_data = _numpy.vstack(self._history_cache)

    history_keys = history_data[:, history_fields.get("x", slice(0))]
    dataset_keys = dataset[:, fields.get("x", slice(0))]

    if "stochastic" in history_fields:
      history_keys = _numpy.hstack((history_keys, history_data[:, history_fields["stochastic"]]))
      dataset_keys = _numpy.hstack((dataset_keys, dataset[:, fields["stochastic"]]))

    if self._payload_objectives and "f" in fields and "f" in history_fields:
      dst_f_offset = fields["f"].indices(dataset.shape[1])[0]
      src_f_offset = history_fields["f"].indices(history_data.shape[1])[0]
      payload_objectives = tuple((dst_f_offset + _, src_f_offset + _) for _ in self._payload_objectives)
    else:
      payload_objectives = tuple()

    for p_dst, _ in payload_objectives:
      undefined_values[:, p_dst] = False

    if not undefined_values.any():
      for dst_index, src_index in _shared._enumerate_equal_keys(dataset_keys, history_keys):
        for p_dst, p_src in payload_objectives:
          dataset[dst_index, p_dst] = self._payload_storage.join_encoded_payloads(dataset[dst_index, p_dst], history_data[src_index, p_src])
    elif all(fields[k].indices(dataset.shape[1]) == history_fields[k].indices(history_data.shape[1]) for k in fields if k in history_fields):
      n_mask = min(dataset.shape[1], history_data.shape[1])

      for k in fields:
        if k not in history_fields:
          undefined_values[:, fields[k]] = False

      undefined_values = undefined_values[:, :n_mask]
      if not undefined_values.any() and not payload_objectives:
        return

      known_history = ~_shared._find_holes(history_data[:, :n_mask])

      # simple case: both history and destination are aligned
      for dst_index, src_index in _shared._enumerate_equal_keys(dataset_keys, history_keys):
        dst_value, src_value = dataset[dst_index], history_data[src_index]
        dst_mask, src_mask = undefined_values[dst_index], known_history[src_index]

        dst_value[:n_mask][dst_mask] = src_value[:n_mask][dst_mask]
        dst_mask[src_mask] = False # update mask

        # update payloads
        for p_dst, p_src in payload_objectives:
          dst_value[p_dst] = self._payload_storage.join_encoded_payloads(dst_value[p_dst], src_value[p_src])
    else:
      # not so simple case
      dst_order = []
      src_order = []

      n_dst = dataset.shape[1]
      n_src = history_data.shape[1]

      for k in fields:
        if k in history_fields:
          dst_order.extend(range(*fields[k].indices(n_dst)))
          src_order.extend(range(*history_fields[k].indices(n_src)))

      known_history = ~_shared._find_holes(history_data)

      for dst_index, src_index in _shared._enumerate_equal_keys(dataset_keys, history_keys):
        dst_value, src_value = dataset[dst_index], history_data[src_index]
        dst_mask, src_mask = undefined_values[dst_index], known_history[src_index]

        # source may contain dups which fills destination, so we must update mask every time
        for i, j in zip(dst_order, src_order):
          if dst_mask[i] and src_mask[j]:
            dst_value[i] = src_value[j]
            dst_mask[i] = False

        for p_dst, p_src in payload_objectives:
          dst_value[p_dst] = self._payload_storage.join_encoded_payloads(dst_value[p_dst], src_value[p_src])

  def _update_analytical_history(self, variables, objectives, constraints, feasibilities):
    if self.size_s() or not self._history_cache or not len(variables) or (not objectives.shape[1] and not constraints.shape[1]):
      return objectives, constraints, feasibilities

    size_x = self.size_x()
    size_f = self.size_f()
    size_c = self.size_c()

    linear_objectives = _numpy.array([(w is not None and len(w)) for w in self.elements_hint(slice(size_x, size_x + size_f), "@GTOpt/LinearParameterVector")], dtype=bool)
    linear_constraints = _numpy.array([(w is not None and len(w)) for w in self.elements_hint(slice(size_x + size_f, size_x + size_f + size_c), "@GTOpt/LinearParameterVector")], dtype=bool)

    if not linear_objectives.any() and not linear_constraints.any():
      # there is nothing to update
      return objectives, constraints, feasibilities

    history_fields = dict((name, slice(start, stop)) for name, start, stop in self._history_fields[0])

    slice_x = history_fields["x"]
    slice_f = history_fields.get("f", slice(0))
    slice_c = history_fields.get("c", slice(0))

    update_feasibility = False
    for solution_index, history_index in _shared._enumerate_equal_keys(variables, [record[slice_x] for record in  self._history_cache]):
      known_elements = ~_shared._find_holes(self._history_cache[history_index])

      objectives_mask = _numpy.logical_and(known_elements[slice_f], linear_objectives)
      objectives[solution_index][objectives_mask] = self._history_cache[history_index][slice_f][objectives_mask]

      constraints_mask = _numpy.logical_and(known_elements[slice_c], linear_constraints)
      if constraints_mask.any():
        constraints[solution_index][constraints_mask] = self._history_cache[history_index][slice_c][constraints_mask]
        update_feasibility = True

    if update_feasibility:
      # All linear constraints have been evaluated, so NaN is not expected.
      for k in _numpy.nonzero(linear_constraints)[0]:
        feasibilities[:, k] = self._calculate_constraint_violation(constraints[:, k], self._constraints[k].lower_bound, self._constraints[k].upper_bound)

    return objectives, constraints, feasibilities

  def _refill_analytical_history(self, history_records=None, history_fields=None):
    if history_records is None:
      history_records = self._history_cache

    if not len(history_records):
      return

    size_x = self.size_x()
    size_f = self.size_f()
    size_c = self.size_c()

    linear_weights = self.elements_hint(slice(size_x, None), "@GTOpt/LinearParameterVector")
    linear_weights = [(i, _numpy.array(weights_i, copy=_shared._SHALLOW).reshape(-1)) \
                      for i, weights_i in enumerate(linear_weights) \
                      if weights_i is not None and len(weights_i)]

    if not linear_weights:
      # there is nothing to do
      return

    if history_fields is None:
      history_fields = dict((name, slice(start, stop)) for name, start, stop in self._history_fields[0])
    else:
      history_fields = dict(history_fields)

    dfdx_enabled, dfdx_sparse, dfdx_rows, dfdx_cols = self.objectives_gradient()
    dcdx_enabled, dcdx_sparse, dcdx_rows, dcdx_cols = self.constraints_gradient()

    grad_spec = {}

    n_reponses = len(history_records[0])

    if dfdx_enabled and "dfdx" in history_fields:
      if dfdx_sparse:
        for i, j, k in zip(dfdx_rows, dfdx_cols, range(*history_fields.get("dfdx", slice(0)).indices(n_reponses))):
          grad_spec.setdefault(i, {})[j] = k
      else:
        for (i, j), k in zip(((i, j) for i in range(size_f) for j in range(size_x)), range(*history_fields.get("dfdx", slice(0)).indices(n_reponses))):
          grad_spec.setdefault(i, {})[j] = k

    if dcdx_enabled and "dcdx" in history_fields:
      if dcdx_sparse:
        for i, j, k in zip(dcdx_rows, dcdx_cols, range(*history_fields.get("dcdx", slice(0)).indices(n_reponses))):
          grad_spec.setdefault(size_f + i, {})[j] = k
      else:
        for (i, j), k in zip(((i, j) for i in range(size_c) for j in range(size_x)), range(*history_fields.get("dcdx", slice(0)).indices(n_reponses))):
          grad_spec.setdefault(size_f + i, {})[j] = k

    # note 1. self._history_cache is list of vectors while custom history_records may be a matrix
    # note 2. the hole test is expensive operation unless it's vectorized

    resp_map = dict([(i, j) for i, j in enumerate(range(*history_fields.get("f", slice(0)).indices(n_reponses)))] \
                  + [(size_f+i, j) for i, j in enumerate(range(*history_fields.get("c", slice(0)).indices(n_reponses)))])

    unk_mask = _shared._find_holes(history_records)

    # The history_records may contains data that must be ignored.
    reponses_of_interest = _numpy.zeros_like(unk_mask)
    for field in history_fields:
      reponses_of_interest[:, history_fields[field]] = True

    unk_mask = _numpy.logical_and(unk_mask, reponses_of_interest)
    del reponses_of_interest

    evaluation_idxs = unk_mask.any(axis=1).nonzero()[0]
    if not evaluation_idxs.size:
      return

    # read points of interest into a special buffer
    slice_x = history_fields.get("x", slice(size_x))
    evaluation_x = _numpy.empty(shape=(evaluation_idxs.shape[0], size_x))
    for i, k in enumerate(evaluation_idxs):
      evaluation_x[i] = history_records[k][slice_x] # read points of interest only

    # normalize points of interest
    evaluation_x, valid_mapped_inputs = self._valid_input_points(sample_x=evaluation_x)
    evaluation_idxs = evaluation_idxs[valid_mapped_inputs]
    if not evaluation_idxs.size:
      return
    evaluation_x = evaluation_x[valid_mapped_inputs]

    # each element of evaluation_map is -1 or the index of the corresponding point in the evaluation_x matrix
    evaluation_map = _shared._filled_array(shape=len(history_records), fill_value=-1, dtype=int)
    evaluation_map[evaluation_idxs] = _numpy.arange(evaluation_idxs.shape[0], dtype=int)

    unk_mask[evaluation_map == -1] = False # don't evaluate invalid points

    for i, weights_i in linear_weights:
      intercept = weights_i[-1]
      weights_i = weights_i[:size_x]
      if i in resp_map:
        record_column = resp_map[i]
        for k in unk_mask[:, record_column].nonzero()[0]:
          history_records[k][record_column] = _numpy.dot(evaluation_x[evaluation_map[k]], weights_i) + intercept

      for j in grad_spec.get(i, {}):
        weight_ij = weights_i[j]
        record_column = grad_spec[i][j]
        for k in _numpy.where(unk_mask[:, record_column])[0]:
          history_records[k][record_column] = weight_ij

  def _enumerate_reconstructable_linear_responses(self, mask_only):
    def reconstruct_linearity(index):
      linearity = self.elements_hint(index, "@GTOpt/LinearityType")
      if str(linearity).lower() != "linear":
        return False
      parameters = self.elements_hint(index, "@GTOpt/LinearParameterVector")
      return parameters is None or not len(parameters)

    size_x, size_f, size_c, size_full = self.size_x(), self.size_f(), self.size_c(), self.size_full()
    slice_f, slice_c = slice(0, size_f), slice(size_f, size_f + size_c)

    # detect target objectives and constraints
    lin_mask = _numpy.zeros(size_full, dtype=bool)
    for k in xrange(size_f + size_c):
      lin_mask[k] = reconstruct_linearity(k + size_x)

    result = {"reconstructed": {"constraints": [], "objectives": []},
              "failed": {"constraints": [], "objectives": []}}

    # don't reconstruct linear responses if gradients are enabled - good chances to caught MILP

    if self._grad_objectives and lin_mask[slice_f].any():
      result["failed"]["objectives"].extend((idx, "Reconstruction of linear dependencies disabled if gradients are enabled.", None, None) for idx in _numpy.where(lin_mask[slice_f])[0])
      lin_mask[slice_f].fill(False)

    if self._grad_constraints and lin_mask[slice_c].any():
      result["failed"]["constraints"].extend((idx - size_f, "Reconstruction of linear dependencies disabled if gradients are enabled.", None, None) for idx in _numpy.where(lin_mask[slice_c])[0])
      lin_mask[slice_c].fill(False)

    if self.size_nf() or self.size_nc() or self.size_s():
      raise _ex.UnsupportedProblemError("Noisy problems does not support linear dependencies reconstruction")

    catvars = self.variable_indexes_by_type("Categorical")
    if any(len(self.variables_bounds(i)) > 1 for i in catvars):
      raise _ex.UnsupportedProblemError("Cannot restore linear dependencies with categorical variables (%s)." % (", ".join(self._variables[i].name for i in catvars),))

    return lin_mask if mask_only else (lin_mask, result)

  def _validate_linear_responses(self, sample_x, sample_f, sample_c, l1_threshold=0.1):
    if sample_x is None or not len(sample_x):
      return

    #ignore variables type because we check predefined parameters vectors

    size_x, size_f, size_c = self.size_x(), self.size_f(), self.size_c()

    def check_linearity(response_kind, response_name, linear_weights, observed_responses):
      if linear_weights is None or not len(linear_weights):
        return

      known_responces = ~_shared._find_holes(observed_responses)
      if not known_responces.any():
        return
      elif known_responces.all():
        known_responces = slice(0, len(sample_x))

      linear_weights = _numpy.array(linear_weights, copy=_shared._SHALLOW).reshape(-1)
      intercept = 0 if len(linear_weights) == size_x else linear_weights[size_x]

      expected_responses = _numpy.empty_like(observed_responses)
      expected_responses[known_responces] = _numpy.dot(sample_x[known_responces], linear_weights[:size_x]) + intercept

      residuals = _numpy.zeros_like(observed_responses)
      residuals[known_responces] = _numpy.fabs(expected_responses[known_responces] - observed_responses[known_responces])
      threshold = l1_threshold * _numpy.maximum(1., _numpy.fabs(expected_responses))
      invalid_points = _numpy.where(residuals > threshold)[0]
      if len(invalid_points):
        # This must be a rare issue, so we throw an exception immediately, for simplicity.
        error_message = "The values ​​of the initial sample of %s %s do not correspond to the given expression %s=%s." % \
                            (response_kind, response_name, response_name, self._regression_string(linear_weights, ""))
        for k, i in enumerate(invalid_points):
          error_message += "\n    [%d] x=%s, %s(given)=[% -12.6g], %s(expected)=[% -12.6g], residual=[% -12.6g]" % \
                                    (i, self._array_string(sample_x[i]), response_name, observed_responses[i], \
                                      response_name, expected_responses[i], abs(observed_responses[i] - expected_responses[i]))
          if len(error_message) > 1024:
            n_left = len(invalid_points) - k - 1
            if n_left > 2:
              error_message += "\n    ... %d more points" % (n_left,)
              break
        raise ValueError(error_message)

    linear_weights = self.elements_hint(slice(size_x, size_x + size_f + size_c), "@GTOpt/LinearParameterVector")

    if sample_f is not None:
      names_f = self.objectives_names()
      for name_i, weights_i, resp_i in zip(names_f, linear_weights[:size_f], sample_f.T):
        check_linearity("objective", name_i, weights_i, resp_i)

    if sample_c is not None:
      names_c = self.constraints_names()
      for name_i, weights_i, resp_i in zip(names_c, linear_weights[size_f:], sample_c.T):
        check_linearity("constraint", name_i, weights_i, resp_i)

  def _reconstruct_linear_dependencies(self, **kwargs):
    """
    Reconstruct linear dependencies if any.

    :keyword sample_x: optional initial sample containing values of variables. Note this sample may contain data for gripped variables, not presented in the problem.
    :type sample_x: :term:`array-like`, 1D or 2D
    :keyword sample_f: optional initial sample of objective function values, ignored if :arg:`sample_x` is absent
    :type sample_f: :term:`array-like`, 1D or 2D
    :keyword sample_c: optional initial sample of constraint function values, ignored if :arg:`sample_x` is absent
    :type sample_c: :term:`array-like`, 1D or 2D
    :keyword gripped_x: optional list of pairs (variable index ``int``, variable value ``float``) indicating variables in :arg:`sample_x` that were removed in problem definition
    :type gripped_x: ``list``
    :keyword immutable: dont modify hints, just return reconstruction result, default is False
    :type immutable: ``bool``

    :keyword evaluation_limit: default number of allowed evaluations if individual budget is not set
    :type evaluation_limit: ``int`` or ``None``
    :keyword expensive_evaluation_limit: default number of allowed evaluations if individual budget is not set and response is hinted as expensive
    :type expensive_evaluation_limit: ``int`` or ``None``
    :keyword seed: random seed used to initialize the pseudo-random number generator
    :type seed: ``int`` or ``None``
    :keyword rcond: optional minimal allowed reciprocal conditionality number for linear dependency reconstruction designs, default is 1.e-5
    :type rcond: ``float`` or ``None``
    :keyword batch_size: maximal number of points that can be evaluated at once
    :type batch_size: ``int`` or ``None``
    :keyword rrms_threshold: maximal allowed RRMS error on LOO CV
    :type rrms_threshold: ``float`` or ``None``
    :keyword responses_scalability: the maximum number of concurrent response evaluations supported by the problem.
    :type responses_scalability: ``int`` or ``None``
    :keyword validation_mode: specifies validation mode.
    :type validation_mode: ``bool`` or ``None``

    :rtype: :class:`.gtopt.problem._LRSMReconstructionResult`
    """
    def read_nonempty_matrix(input_data, length, size_x, detect_none, name):
      if input_data is not None and len(input_data) > 0:
        output_matrix = _shared.as_matrix(input_data, shape=(length, size_x), detect_none=detect_none, name=name)
        if output_matrix.size > 0:
          return output_matrix
      return None

    def _read_nonnegative_argument(name, default_value, conversion):
      try:
        value = kwargs.get(name)
        if value is None:
          return default_value
        value = conversion(value)
      except:
        exc_info = _sys.exc_info()
        _shared.reraise(TypeError, ("Invalid value of the '%s' argument is given: %s" % (name, str(exc_info[1]) or "no particular reason given",)), exc_info[2]);

      if value < 0:
        raise ValueError("Invalid value of the '%s' argument is given: %s (%s must be non-negative)." % (name, value, name))

      return value

    # read and validate arguments

    size_x, size_f, size_c, size_full = self.size_x(), self.size_f(), self.size_c(), self.size_full()
    slice_f, slice_c = slice(0, size_f), slice(size_f, size_f + size_c)

    known_arguments = ("sample_x", "sample_f", "sample_c", "seed", "rcond", "batch_size",
                       "rrms_threshold", "gripped_x", "evaluation_limit",
                       "expensive_evaluation_limit", "immutable", "responses_scalability",
                       "validation_mode",)
    invalid_arguments = [_ for _ in kwargs if _ not in known_arguments]
    if invalid_arguments:
      raise TypeError("Keyword argument %s is not recognized. Valid arguments are: %s"
                      % (", ".join("'%s'" % _ for _ in invalid_arguments), ", ".join("'%s'" % _ for _ in known_arguments)))

    lin_mask, result = self._enumerate_reconstructable_linear_responses(False)
    if not lin_mask.any():
      return _LRSMReconstructionResult(result, _numpy.empty((0, size_x)), _numpy.empty((0, size_full)))

    resp_scalability = max(1, _read_nonnegative_argument("responses_scalability", 1, int))
    # -1 means default budget: number of variables plus intercept plus one point for LOO CV
    # Intentionally ignore GTOpt/ExpensiveEvaluations hint for expensive evaluations.
    requested_design_size = _numpy.array(self._responses_evaluation_limit(-1, ignore_expensive=True), dtype=int)
    requested_design_size[~lin_mask[:(size_f + size_c)]] = -1 # ignore non-linear limits, size_full may be greater than size_f+size_c due to gradients
    requested_design_size[requested_design_size > 0] *= resp_scalability # convert the number of batches to the number of points since we use single batch

    # read list of gripped variables first

    try:
      gripped_x = sorted([(int(i), float(v)) for i, v in kwargs.get("gripped_x", [])], key=lambda k: k[0])
    except:
      exc_info = _sys.exc_info()
      _shared.reraise(TypeError, ("Invalid value of the 'gripped_x' argument is given: %s" % str(exc_info[1])), exc_info[2]);

    # read initial samples

    sample_x = read_nonempty_matrix(kwargs.get("sample_x"), None, size_x + len(gripped_x), False, name="Initial sample containing values of variables ('sample_x' argument)")
    if sample_x is not None:
      sample_f = read_nonempty_matrix(kwargs.get("sample_f"), sample_x.shape[0], size_f, True, name="Initial sample of objective function values ('sample_f' argument)")
      sample_c = read_nonempty_matrix(kwargs.get("sample_c"), sample_x.shape[0], size_c, True, name="Initial sample of constraint function values ('sample_c' argument)")

      valid_x = _numpy.isfinite(sample_x).all(axis=1)
      if not valid_x.any():
        sample_x, sample_f, sample_c = None, None, None
      elif not valid_x.all():
        sample_x = sample_x[valid_x]
        if sample_f is not None:
          sample_f = sample_f[valid_x]
        if sample_c is not None:
          sample_c = sample_c[valid_x]
        del valid_x
    else:
      sample_f, sample_c = None, None

    if sample_x is None:
      gripped_x = [] # just ignore it
    elif gripped_x:
      # Move gripped variables to the end. The order does matter only for evaluations.
      rcols = [i for i, v in gripped_x]
      lcols = [i for i in range(sample_x.shape[1]) if i not in rcols]
      sample_x = _numpy.hstack((sample_x[:, lcols], sample_x[:, rcols]))

    evaluation_limit = _read_nonnegative_argument("evaluation_limit", _numpy.iinfo(int).max, int)
    expensive_evaluation_limit = _read_nonnegative_argument("expensive_evaluation_limit", _numpy.iinfo(int).max, int)

    resp_evaluation_limit = requested_design_size.copy() # read individual limits
    for resp_idx, limit in enumerate(resp_evaluation_limit):
      if limit < 0:
        resp_cost = self.elements_hint(size_x+resp_idx, "@GTOpt/EvaluationCostType")
        if isinstance(resp_cost, string_types) and resp_cost.lower() == "expensive":
          resp_evaluation_limit[resp_idx] = min(expensive_evaluation_limit, evaluation_limit)
        else:
          resp_evaluation_limit[resp_idx] = evaluation_limit

    batch_size = _read_nonnegative_argument("batch_size", 0, int)
    validation_mode = bool(kwargs.get("validation_mode", False))

    def _batch_evaluate(query_x, query_mask):
      if validation_mode:
        # fake evaluations
        return _numpy.zeros(query_mask.shape), _numpy.array(query_mask, copy=True)
      if not batch_size or len(query_x) <= batch_size:
        return self._evaluate(query_x, query_mask, self._timecheck)
      response_batches = []
      for ofst in range(0, len(query_x), batch_size):
        response_batches.append(self._evaluate(query_x[ofst:ofst+batch_size], query_mask[ofst:ofst+batch_size], self._timecheck))
        if self._last_error:
          last_error, self._last_error = self._last_error, None
          _shared.reraise(*last_error)
      response_data, response_mask = zip(*response_batches)
      response_data, response_mask = _numpy.vstack(response_data), _numpy.vstack(response_mask)
      response_data[~response_mask] = _shared._NONE
      return response_data, response_mask

    try:
      seed = kwargs.get("seed", 65521)
      _numpy.random.RandomState(seed)
    except:
      exc_info = _sys.exc_info()
      _shared.reraise(TypeError, ("Invalid value of the 'seed' argument is given: %s" % str(exc_info[1])), exc_info[2]);

    rcond = _read_nonnegative_argument("rcond", 1.e-5, float)
    rrms_threshold = _read_nonnegative_argument("rrms_threshold", None, float)

    if sample_f is not None and lin_mask[slice_f].any():
      # any non-finite value in initial sample makes linear responce invalid unless it's the "hole" mark
      valid_f = _numpy.logical_or(_numpy.isfinite(sample_f), _shared._find_holes(sample_f)).all(axis=0)
      result["failed"]["objectives"].extend((k, "Non-finite value encountered in the initial sample.", None, None) for k in _numpy.where(_numpy.logical_and(~valid_f, lin_mask[slice_f]))[0])
      _numpy.logical_and(lin_mask[slice_f], valid_f, out=lin_mask[slice_f])
      del valid_f

    if sample_c is not None and lin_mask[slice_c].any():
      # any non-finite value in initial sample makes linear constraint invalid unless it's the "hole" mark
      valid_c = _numpy.logical_or(_numpy.isfinite(sample_c), _shared._find_holes(sample_c)).all(axis=0)
      result["failed"]["constraints"].extend((k, "Non-finite value encountered in the initial sample.", None, None) for k in _numpy.where(_numpy.logical_and(~valid_c, lin_mask[slice_c]))[0])
      _numpy.logical_and(lin_mask[slice_c], valid_c, out=lin_mask[slice_c])
      del valid_c

    if not lin_mask.any():
      return _LRSMReconstructionResult(result, _numpy.empty((0, size_x)), _numpy.empty((0, size_full)))

    # We need initial points only if they have associated responses.
    # In other words, sample_x is usless if we have to evaluate it.

    if sample_f is not None and (not lin_mask[slice_f].any() or (_shared._find_holes(sample_f)[:, lin_mask[slice_f]]).all()):
      sample_f = None

    if sample_c is not None and (not lin_mask[slice_c].any() or (_shared._find_holes(sample_c)[:, lin_mask[slice_c]]).all()):
      sample_c = None

    if sample_f is None and sample_c is None:
      sample_x, gripped_x = None, []

    # collect categorical variables
    catvars = []
    intvars = []
    for var_idx in xrange(size_x):
      var_type = self.elements_hint(var_idx, "@GT/VariableType")
      var_type = var_type.lower() if isinstance(var_type, string_types) else var_type
      if var_type in ("categorical", "discrete", "stepped"):
        catvars.extend((var_idx, self.variables_bounds(var_idx)))
      elif var_type == "integer":
        intvars.append(var_idx)

    # reconstruct design bounds w.r.t gripped variables not presented in the problem but presented in the initial sample
    lower_bounds, upper_bounds = self.variables_bounds()
    if gripped_x:
      lower_bounds = [_ for _ in lower_bounds] + [val for idx, val in gripped_x]
      upper_bounds = [_ for _ in upper_bounds] + [val for idx, val in gripped_x]

    def _read_known_points(idx):
      responses = sample_f if idx < size_f else sample_c
      if responses is None:
        return _numpy.zeros(len(sample_x), dtype=bool)
      return ~_shared._find_holes(responses[:, (idx if idx < size_f else (idx - size_f))])

    def _enumerate_initial_samples(mask):
      if not mask[slice_f].any() and not mask[slice_c].any():
        # strange case: there is nothing to reconstruct
        return

      if sample_x is None:
        # simple case: no initial data, reconstruct all at once
        yield None, mask
        return

      active_responses = _numpy.where(mask)[0]

      # batchify known responses
      responses_mask = _numpy.zeros_like(mask)
      responses_mask[active_responses[0]] = True
      initial_points_mask = _read_known_points(active_responses[0])

      for idx in active_responses[1:]:
        known_responses_mask = _read_known_points(idx)
        if not (known_responses_mask == initial_points_mask).all():
          # mask has changed, flush it
          yield initial_points_mask, responses_mask
          responses_mask.fill(False)
          initial_points_mask = known_responses_mask
        responses_mask[idx] = True

      # flush the last batch
      yield initial_points_mask, responses_mask

      # end of _enumerate_initial_samples

    evaluated_inputs = _numpy.empty((0, size_x + len(gripped_x)))
    evaluated_responses = _numpy.empty((0, size_full))
    evaluated_queue_mask = _numpy.empty((0, size_full), dtype=bool)

    # evaluate as much as we can and allowed
    for subproblem_budget in _numpy.unique(requested_design_size):
      for initial_points_mask, responses_mask in _enumerate_initial_samples(_numpy.logical_and(lin_mask, requested_design_size == subproblem_budget)):
        if not responses_mask.any():
          continue

        # get known points from sample_x
        subproblem_variables = [sample_x[initial_points_mask]] if initial_points_mask is not None and initial_points_mask.any() else []

        if subproblem_budget >= 0:
          # in case of explicit individual budget we must not use partially evaluated points in order to avoid accidental budget violation
          evaluated_points_mask = evaluated_queue_mask[:, responses_mask].all(axis=1)
        else:
          # get known points from evaluated so far points: exploiting the fact that the user can return more responses than requested
          evaluated_points_mask = evaluated_queue_mask[:, responses_mask].any(axis=1)

        if evaluated_points_mask.any():
          # try to reuse some points
          subproblem_variables.append(evaluated_inputs[evaluated_points_mask])

        subproblem_variables = _numpy.vstack(subproblem_variables) if subproblem_variables else None

        lrsm_doe, failure_reason = _utils._linear_rsm_design((lower_bounds, upper_bounds), catvars=catvars, intvars=intvars, init_x=subproblem_variables,
                                                             npoints=subproblem_budget, resp_scalability=resp_scalability, seed=seed, rcond_threshold=rcond)
        if lrsm_doe is None:
          result["failed"]["objectives"].extend((k, failure_reason, None, None) for k in _numpy.where(responses_mask[slice_f])[0])
          result["failed"]["constraints"].extend((k, failure_reason, None, None) for k in _numpy.where(responses_mask[slice_c])[0])
          continue # cannot be solved

        if evaluated_points_mask.any():
          # Re-evaluate incomplete points. Note we won't break evaluation limit here because we've already asked these points with different mask so we counted these evaluation.
          reevaluation_points_mask = _numpy.logical_and(evaluated_points_mask, ~evaluated_queue_mask[:, responses_mask].all(axis=1))
          if reevaluation_points_mask.any():
            query_mask = ~evaluated_queue_mask[reevaluation_points_mask, :]
            query_mask[:, ~responses_mask] = False
            query_mask[:, query_mask.any(axis=0)] = True # chess-like evaluations are prohibited by backward compatibility reasons
            new_response_data, new_response_mask = _batch_evaluate(evaluated_inputs[reevaluation_points_mask, :size_x], query_mask)
            evaluated_queue_mask[reevaluation_points_mask, :] = _numpy.logical_or(new_response_mask, evaluated_queue_mask[reevaluation_points_mask])
            for j, i in enumerate(_numpy.where(reevaluation_points_mask)[0]):
              evaluated_responses[i, new_response_mask[j]] = new_response_data[j, new_response_mask[j]]

        if lrsm_doe.shape[0] and subproblem_budget < 0:
          # limit evaluations by general evaluations budget
          lrsm_doe = lrsm_doe[:min(lrsm_doe.shape[0], resp_evaluation_limit[responses_mask].max())]
          resp_evaluation_limit[responses_mask] = _numpy.clip(resp_evaluation_limit[responses_mask] - len(lrsm_doe), 0, _numpy.iinfo(int).max)

        if lrsm_doe.shape[0]:
          # Note lrsm_doe[:, :size_x] is required because problem does not know about gripped variables
          new_response_data, new_response_mask = _batch_evaluate(lrsm_doe[:, :size_x], _numpy.tile(responses_mask, (len(lrsm_doe), 1)))

          new_response_data = _shared.as_matrix(new_response_data, detect_none=True, name="responses")
          new_response_mask = _shared.as_matrix(new_response_mask, shape=new_response_data.shape, detect_none=False, dtype=bool, name="mask")
          new_response_data[~new_response_mask] = _shared._NONE

          if not evaluated_inputs.size:
            evaluated_inputs = lrsm_doe
            evaluated_responses = new_response_data
            evaluated_queue_mask = new_response_mask
          else:
            evaluated_inputs_list = [evaluated_inputs]
            evaluated_responses_list = [evaluated_responses]
            evaluated_queue_mask_list = [evaluated_queue_mask]

            # search points in evaluated_inputs
            for x, resp, mask in zip(lrsm_doe, new_response_data, new_response_mask):
              found = _numpy.where((evaluated_inputs == x[_numpy.newaxis, :]).all(axis=1))[0][:1]
              if found.size:
                evaluated_responses[found[0], mask] = resp[mask]
                evaluated_queue_mask[found[0], mask] = True
              else:
                evaluated_inputs_list.append(x)
                evaluated_responses_list.append(resp)
                evaluated_queue_mask_list.append(mask)

            evaluated_inputs = _numpy.vstack(evaluated_inputs_list)
            evaluated_responses = _numpy.vstack(evaluated_responses_list)
            evaluated_queue_mask = _numpy.vstack(evaluated_queue_mask_list)

    # collect joined inputs
    if sample_f is None:
      sample_xf = evaluated_inputs
      sample_xc = evaluated_inputs if sample_c is None else _numpy.vstack((sample_x, evaluated_inputs))
    else:
      sample_xf = _numpy.vstack((sample_x, evaluated_inputs))
      sample_xc = evaluated_inputs if sample_c is None else sample_xf

    # and now reconstruct, at last
    intercept_regressors = _numpy.array([v for i, v in gripped_x] + [1.])
    for idx in _numpy.where(lin_mask)[0]:
      norm_idx, key = (idx, "objectives") if idx < size_f else (idx - size_f, "constraints")
      if any(_[0] == norm_idx for _ in result["failed"][key]):
        continue # already failed

      # now we must fit it
      if idx < size_f:
        x, resp = sample_xf, evaluated_responses[:, idx] if sample_f is None else _numpy.hstack((sample_f[:, idx], evaluated_responses[:, idx]))
      else:
        x, resp = sample_xc, evaluated_responses[:, idx] if sample_c is None else _numpy.hstack((sample_c[:, idx - size_f], evaluated_responses[:, idx]))

      known_points = ~_shared._find_holes(resp)
      if not known_points.all():
        x, resp = x[known_points], resp[known_points]

      if x.shape[0] <= x.shape[1]:
        result["failed"][key].append((norm_idx, "Failed to reconstruct due to evaluations limit: %d < %d." % (x.shape[0], x.shape[1] + 1), None, None))
        continue

      if not _numpy.isfinite(resp).all():
        result["failed"][key].append((norm_idx, "NaN or Infinity value encountered.", None, None))
        continue

      try:
        n_consts = sum(_numpy.ptp(x, axis=0) == 0.)  # true constants
        if x.shape[0] <= (x.shape[1] + 1 - n_consts):
          # not enough points for LOO CV
          weights, _ = _utils._linear_rsm_fit(x, resp[:, _numpy.newaxis], x_bounds=(lower_bounds, upper_bounds))
          #rrmse[0] = _numpy.nan
          rrmse = None
        else:
          weights, rrmse = _utils._linear_rsm_stepwise_fit(x, resp[:, _numpy.newaxis], x_bounds=(lower_bounds, upper_bounds))

        weights = weights[:, 0]

        if gripped_x:
          # project gripped variables to intercept
          weights[size_x] = _numpy.dot(intercept_regressors, weights[size_x:])
          weights = weights[:(size_x + 1)]

        if rrms_threshold is not None and rrmse is not None and rrmse[0] > rrms_threshold:
          reason = "The relative root mean square error estimated by leave-one-out cross validation procedure exceeds allowed level: %g > %g." % (rrmse[0], rrms_threshold)
          result["failed"][key].append((norm_idx, reason, rrmse, weights))
        else:
          # succeeded
          initial_hints = self._objectives[norm_idx].hints if idx < size_f else self._constraints[norm_idx].hints
          updated_hints = dict((k, initial_hints[k]) for k in initial_hints) # make a copy

          updated_hints["@GTOpt/LinearParameterVector"] = weights.tolist()
          updated_hints["@GTOpt/LinearityType"] = "Linear"
          updated_hints["@GTOpt/EvaluationCostType"] = "Cheap"

          if not kwargs.get("immutable", False):
            if idx < size_f:
              self.set_objective_hints(norm_idx, updated_hints)
            else:
              self.set_constraint_hints(norm_idx, updated_hints)

          result["reconstructed"][key].append((norm_idx, rrmse, weights))
      except:
        result["failed"][key].append((norm_idx, "Failed to reconstruct: " + str(_sys.exc_info()[1]), None, None))

    # slice removes gripped variables
    return _LRSMReconstructionResult(result, evaluated_inputs[:, :size_x], evaluated_responses)


class ProblemConstrained(ProblemGeneric):
  """
  Simplified problem class for constrained problems. Inherits from :class:`~da.p7core.gtopt.ProblemGeneric`.

  This class does not support the usage of analytical objective and constraint gradients.

  To define a constrained optimization problem, create your own problem class, inheriting from :class:`~da.p7core.gtopt.ProblemConstrained`.
  This class must implement the following methods:

  * :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()` inherited from :class:`~da.p7core.gtopt.ProblemGeneric`
  * :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives()` (or :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`)
  * :meth:`~da.p7core.gtopt.ProblemConstrained.define_constraints()` (or :meth:`~da.p7core.gtopt.ProblemConstrained.define_constraints_batch()`)

  """

  def _validate(self):
    ProblemGeneric._validate(self)
    if self.size_nc() > 0 or self.size_nf() > 0:
      raise _ex.InvalidProblemError('Blackbox noise is supported only in ProblemGeneric!')
    if self.size_c() == 0 or self.size_f() == 0:
      raise _ex.InvalidProblemError('Constrained problem must define both constraints and objectives!')
    if self._grad_constraints or self._grad_objectives:
      raise _ex.InvalidProblemError('Analytical gradients are not supported in plain problems!')

  def _check_len(self, iter, target, name):
    if len(iter) != target:
      raise ValueError('Wrong number of %s evaluated: %d != %d' % (name, len(iter), target))

  def evaluate(self, queryx, querymask):
    """
    Default implementation of the :func:`~da.p7core.gtopt.ProblemGeneric.evaluate()` method
    inherited from the base class :class:`~da.p7core.gtopt.ProblemGeneric`.
    Should not be reimplemented; use
    :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives()` and
    :meth:`~da.p7core.gtopt.ProblemConstrained.define_constraints()`.
    """
    queryx = _numpy.array(queryx, dtype=float, ndmin=2, copy=_shared._SHALLOW)
    querymask = _numpy.array(querymask, dtype=bool, ndmin=2, copy=_shared._SHALLOW)
    size_f = self.size_f()
    size_cf = size_f + self.size_c()
    assert queryx.shape[0] == querymask.shape[0], "The number of points to evaluate does not conform the number of the evaluation requests masks."
    assert size_cf == querymask.shape[1], "The number of responses in requests masks does match number of responses in the problem."

    points = _numpy.empty(querymask.shape, dtype=float)
    points.fill(_shared._NONE)

    if size_f:#can be zero in CSP
      self._read_batch_data(queryx, querymask[:, :size_f].any(axis=1), points[:, :size_f],
                            self.define_objectives_batch, self.objectives_names(),
                            'objective', regular_responses=self._regular_responses_mask())

    if size_cf > size_f: #we may come here from ProblemUnconstrained
      self._read_batch_data(queryx, querymask[:, size_f:size_cf].any(axis=1), points[:, size_f:size_cf],
                            self.define_constraints_batch, self.constraints_names(),
                            'constraints')

    return points, ~_shared._find_holes(points)

  define_objectives = _AbstractMethodBatch('define_objectives_batch', 'iterable(float)')
  """An abstract method to define problem objectives.

  :param x: point to evaluate
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: ``ndarray``, 1D

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``.

  .. versionchanged:: 6.24
     evaluation results may contain ``None`` values to indicate skipped evaluations.

  This method does not support the batch mode (evaluates single point only). May be implemented by user instead of
  :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch` (which uses this method by default).

  The shape of :arg:`x` is *(1, m)* where *m* is the input dimension (:meth:`~da.p7core.gtopt.ProblemGeneric.size_x()` + :meth:`~da.p7core.gtopt.ProblemGeneric.size_s()`).
  The first :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()` values are classic variables (see :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`),
  while the following :meth:`~da.p7core.gtopt.ProblemGeneric.size_s()` values
  are stochastic variables (see :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()`).

  The returned array may contain NaN and ``None`` values, which have the following meaning:

  * NaN value of some objective indicates that evaluation of an objective failed.
  * ``None`` value indicates that evaluation of an objective was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """

  define_constraints = _AbstractMethodBatch('define_constraints_batch', 'iterable(float)')
  """An abstract method to define problem constraints.

  :param x: point to evaluate
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: :term:`array-like`, 1D

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``.

  .. versionchanged:: 6.24
     evaluation results may contain ``None`` values to indicate skipped evaluations.

  This method does not support the batch mode (evaluates single point only). May be implemented by user instead of
  :meth:`~da.p7core.gtopt.ProblemConstrained.define_constraints_batch` (which uses this method by default).

  The shape of :arg:`x` is the same as in :meth:`~ProblemConstrained.define_objectives()`.

  The returned array may contain NaN and ``None`` values, which have the following meaning:

  * NaN value of some constraint indicates that evaluation of a constraint failed.
  * ``None`` value indicates that evaluation of a constraint was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """

  def define_objectives_batch(self, x):
    """Default implementation of the method defining problem objectives. Supports non-batch and batch modes.

    :param x: points batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``; default implementation also returns ``ndarray``.

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :meth:`.ProblemConstrained.evaluate` to calculate objectives.
    Default implementation simply loops over the points batch *x*, calling
    :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives()` for each point.
    May be reimplemented to support parallel calculations.
    Such implementation may return any 2D :term:`array-like`.

    The shape of :arg:`x` is *(n, m)* where *n* is the number of points to evaluate (at most :ref:`GTOpt/BatchSize<GTOpt/BatchSize>`) and *m*
    is the input dimension ( :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()` + :meth:`~da.p7core.gtopt.ProblemGeneric.size_s()` ).
    For each row, the first :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()` values are classic variables
    (see :meth:`~da.p7core.gtopt.ProblemGeneric.add_variable()`),
    while the following :meth:`~da.p7core.gtopt.ProblemGeneric.size_s()` values
    are stochastic variables (see :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()`).

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value of some constraint indicates that evaluation of an objective failed.
    * ``None`` value indicates that evaluation of an objective was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return self._evaluate_with_time_check(x, self.size_f(), self.define_objectives, self._timecheck)

  def define_constraints_batch(self, x):
    """Default implementation of the method defining problem constraints. Supports non-batch and batch modes.

    :param x: points batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``; default implementation also returns ``ndarray``.

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :meth:`.ProblemConstrained.evaluate` to calculate constraints.
    Default implementation simply loops over the points batch *x*, calling
    :meth:`~da.p7core.gtopt.ProblemConstrained.define_constraints()` for each point.
    May be reimplemented by user to support parallel calculations.
    Such implementation may return any 2D :term:`array-like`.

    The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`.

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value of some constraint indicates that evaluation of a constraint failed.
    * ``None`` value indicates that evaluation of a constraint was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return self._evaluate_with_time_check(x, self.size_c(), self.define_constraints, self._timecheck)


class ProblemUnconstrained(ProblemConstrained):
  """
  Simplified problem class for unconstrained problems. Inherits from :class:`~da.p7core.gtopt.ProblemConstrained`.

  This class does not support the usage of analytical objective gradients, and should not add any problem constraints.

  To define an unconstrained optimization problem, create your own problem class, inheriting from :class:`~da.p7core.gtopt.ProblemUnconstrained`.
  This class must implement the following methods:

  * :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()` inherited from :class:`~da.p7core.gtopt.ProblemGeneric`
  * :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives()` (or :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`) inherited from :class:`~da.p7core.gtopt.ProblemConstrained`

  Note that this class should not implement :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()`.
  """

  def _validate(self):
    ProblemGeneric._validate(self)
    if self.size_nc() > 0 or self.size_nf() > 0:
      raise _ex.InvalidProblemError('Blackbox noise is supported only in ProblemGeneric!')
    if self.size_c() > 0:
      raise _ex.InvalidProblemError("Unconstrained problem can't have constraints!")
    if self._grad_constraints or self._grad_objectives:
      raise _ex.InvalidProblemError('Analytical gradients are not supported in plain problems!')

  def define_constraints(self, x):
    """Empty definition of constraints for an unconstrained problem. Does nothing. Should not be reimplemented
    (an unconstrained problem must not define any constraints)."""
    pass

class ProblemCSP(ProblemConstrained):
  """
  Simplified problem class for constraint satisfaction problems (CSP). Inherits from :class:`~da.p7core.gtopt.ProblemConstrained`.

  This class does not support the usage of analytical constraint gradients, and should not add any problem objectives.

  To define a constraint satisfaction problem, create your own problem class, inheriting from :class:`~da.p7core.gtopt.ProblemCSP`.
  This class must implement the following methods:

  * :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()` inherited from :class:`~da.p7core.gtopt.ProblemGeneric`
  * :meth:`~da.p7core.gtopt.ProblemConstrained.define_constraints()` (or :meth:`~da.p7core.gtopt.ProblemConstrained.define_constraints_batch()`) inherited from :class:`~da.p7core.gtopt.ProblemConstrained`

  Note that this class should not implement :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate()`.

  """

  def _validate(self):
    ProblemGeneric._validate(self)
    if self.size_nc() > 0 or self.size_nf() > 0:
      raise _ex.InvalidProblemError('Blackbox noise is supported only in ProblemGeneric!')
    if self.size_f() > 0:
      raise _ex.InvalidProblemError("CSP problem can't have objectives!")
    if self._grad_constraints or self._grad_objectives:
      raise _ex.InvalidProblemError('Analytical gradients are not supported in plain problems!')

  def define_objectives(self, x):
    """Empty definition of objectives. Does nothing. Should not be reimplemented
    (CSP must not define any objectives)."""
    pass

class ProblemMeanVariance(ProblemGeneric):
  """
  Simplified problem class for mean variance problems. Inherits from :class:`~da.p7core.gtopt.ProblemGeneric`.

  To define a mean variance problem, create your own problem class, inheriting from :class:`~da.p7core.gtopt.ProblemMeanVariance`.
  This class must implement the following methods:

  * :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()` inherited from :class:`~da.p7core.gtopt.ProblemGeneric`
  * :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_objective()` (or :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_objective_batch()`)
  * :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_objective_gradient()` (or :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_objective_gradient_batch()`)
  * :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints()` (or :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_batch()`)
  * :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_gradient()` (or :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_gradient_batch()`)

  A mean variance problem must also add stochastic variables.
  See :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()`
  and section :ref:`ug_gtopt_stochastic_vars` for details.

  .. note::

     Mean variance problem defines only one objective, hence the name of the
     :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_objective` method.

  To add an objective to a mean variance problem, use :meth:`~da.p7core.gtopt.ProblemMeanVariance.set_objective()`
  instead of the inherited :meth:`~da.p7core.gtopt.ProblemMeanVariance.add_objective()` method.
  The :meth:`~da.p7core.gtopt.ProblemMeanVariance.set_objective()` method adds both the objective function
  and its mean variance. This method should be used only once. Its main purpose is to support optimization
  hints in mean variance problems (see the *hints* argument in method description).

  Example::

    class MyProblem(da.p7core.gtopt.ProblemMeanVariance):
      def prepare_problem(self):
        self.add_variable((0, 1), 0.5)
        self.add_variable((0, 2), 0.5)
        self.add_constraint()
        self.set_objective()
        self.set_stochastic(distribution)

      def define_objective(self, x):
        #f = x0**2 + x1**2
        return x[0]**2 + x[1]**2

      def define_constraints(self, x):
        #c = x0 + x1
        return [x[0] + x[1]]

      def define_objective_gradient(self, x):
        #return [ df/dx0 ... df/dxn ]

      def define_constraints_gradient(self, x):
        #return [ dc0/dx0 ... dc0/dxn ... dcm/dxn ]

    problem = MyProblem()

  """

  def _validate(self):
    ProblemGeneric._validate(self)
    if self.size_nc() > 0 or self.size_nf() > 0:
      raise _ex.InvalidProblemError('Blackbox noise is supported only in ProblemGeneric!')
    if self.size_f() != 2:
      raise _ex.InvalidProblemError('Mean variance problem must define objectives using set_objective() function!')
    if self.size_s() == 0:
      raise _ex.InvalidProblemError('Mean variance problem must define stochastic variables!')
    enabled, sparse, rows, columns = self.objectives_gradient()
    if enabled and sparse:
      for r in rows:
        if r != 0:
          raise _ex.InvalidProblemError('The gradient for the second function is not allowed!')

  def add_objective(self, name=None, hints=None):
    """
    A prohibiting implementation of the :meth:`~da.p7core.gtopt.ProblemGeneric.add_objective()` method
    inherited from :class:`~da.p7core.gtopt.ProblemGeneric`. Will simply raise an exception if you attempt to use this method;
    use :meth:`~da.p7core.gtopt.ProblemMeanVariance.set_objective()` instead.

    """
    raise _ex.InvalidProblemError('Mean variance problem must define its objective in set_objective()!')

  def set_objective(self, name=None, hints=None):
    r"""
    Set mean variance problem objective.

    :param name: the name of the objective
    :param hints: optimization hints
    :type name: ``str``
    :type hints: ``dict``

    Adds an objective function and its mean variance.

    Let `f(x, \xi)` be the objective function, then its mean is

    .. math::

       \langle f \rangle (x) ~=~ \int f(x,\xi) \rho (\xi) \, \mathrm{d}\xi,

    and mean variance

    .. math::

      V = \sqrt{\langle f^2 \rangle ~-~ {\langle f \rangle}^2}

    To simplify problem implementation, :meth:`~da.p7core.gtopt.ProblemMeanVariance.set_objective()` allows you to simply define `f(x, \\xi)`,
    and its mean and variance are added automatically.

    The *name* argument is optional; if you do not provide a name, the objective is automatically named ``"f1"``.

    The *hints* argument sets objective-specific options that may direct optimizer to use alternative internal algorithms to increase performance
    (see :ref:`ug_gtopt_hints`).
    It is a dictionary ``{hint name: value}``, for example ``{"@GTOpt/LinearityType": "Quadratic"}``.

    This method should be used only once, from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.

    """
    if self._objectives:
      raise _ex.InvalidProblemError("The mean variance problem allows only one call of the set_objective() method.")
    ProblemGeneric.add_objective(self, name, hints)
    ProblemGeneric.add_objective(self)
    if self._objectives[0].hints.get("@GT/ObjectiveType", "Auto").lower() in ("evaluate", "adaptive", "payload"):
      raise _ex.InvalidOptionValueError('The mean variance problem prohibits the use of "Evaluate", or "Adaptive", or "Payload" objective.')

  def _check_len(self, iter, target, name):
    if len(iter) != target:
      raise ValueError('Wrong number of %s evaluated: %d != %d' % (name, len(iter), target))

  def setup_additional_options(self, options):
    options.set("/OptimizationManager/stochastic_problem_type", "STOCHASTIC_PROBLEM_MEAN_VARIANCE")

  def evaluate(self, queryx, querymask):
    """
    Default implementation of the :meth:`~da.p7core.gtopt.ProblemGeneric.evaluate` method inherited from the base class
    :class:`~da.p7core.gtopt.ProblemGeneric`. Should not be reimplemented; use
    :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_objective()`,
    :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_objective_gradient()`,
    :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints()`,
    :meth:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_gradient()`,
    or their batch counterparts.

    """
    size_x, size_f, size_c = self.size_x(), self.size_f(), self.size_c()

    dfdx_enabled, dfdx_sparse, dfdx_rows, dfdx_cols = self.objectives_gradient()
    size_dfdx = 0 if not dfdx_enabled else len(dfdx_rows) if dfdx_sparse else size_x * size_f

    dcdx_enabled, dcdx_sparse, dcdx_rows, dcdx_cols = self.constraints_gradient()
    size_dcdx = 0 if not dcdx_enabled else len(dcdx_rows) if dcdx_sparse else size_x * size_c

    points = _numpy.zeros(querymask.shape, dtype=float)
    outmask = _numpy.zeros(querymask.shape, dtype=bool)

    # note 1. we need only vector-column of the outmask[:, 0] because actually we need outmask[:, :size_f].any(axis=1)
    # note 2. we evaluate only half of objectives because the second half is complementary one and should not be evaluated
    outmask[:, :size_f] = querymask[:, :size_f].any(axis=1).reshape((-1, 1))
    self._read_batch_data(queryx, outmask[:, 0], points[:, :(size_f // 2)], self.define_objective_batch,
                          self.objectives_names(), 'objective', regular_responses=self._regular_responses_mask())

    if size_c:
      slice_c = slice(size_f, size_f + size_c)
      outmask[:, slice_c] = querymask[:, slice_c].any(axis=1).reshape((-1, 1))
      self._read_batch_data(queryx, outmask[:, size_f], points[:, slice_c], self.define_constraints_batch, self.constraints_names(), 'constraints')

    if size_dfdx:
      first_dfdx = size_f + size_c
      slice_dfdx = slice(first_dfdx, first_dfdx + size_dfdx)
      outmask[:, slice_dfdx] = querymask[:, slice_dfdx].any(axis=1).reshape((-1, 1))

      if outmask[:, first_dfdx].any():
        name_dfdx = [("d%s/d%s" % (name_f, name_x)) for name_f in self.objectives_names()[:1] for name_x in self.variables_names()]
        if not dfdx_sparse:
          slice_dfdx = slice(first_dfdx, first_dfdx + size_dfdx // 2) # evaluate objective gradient for the first objective only
        self._read_batch_data(queryx, outmask[:, first_dfdx], points[:, slice_dfdx], self.define_objective_gradient_batch, name_dfdx, 'objective gradient')

    if size_dcdx:
      first_dcdx = size_f + size_c + size_dfdx
      slice_dcdx = slice(first_dcdx, first_dcdx + size_dcdx)
      outmask[:, slice_dcdx] = querymask[:, slice_dcdx].any(axis=1).reshape((-1, 1))

      if outmask[:, first_dcdx].any():
        name_dcdx = [("d%s/d%s" % (name_c, name_x)) for name_c in self.constraints_names() for name_x in self.variables_names()]
        self._read_batch_data(queryx, outmask[:, first_dcdx], points[:, slice_dcdx], self.define_constraints_gradient_batch, name_dcdx, 'constraints gradient')

    return points, outmask

  define_objective = _AbstractMethodBatch('define_objective_batch', 'iterable(float)')
  """An abstract method to define mean variance problem objective.

  :param x: point to evaluate
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: :term:`array-like`, 1D

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``.

  .. versionchanged:: 6.24
     objective value may be ``None`` to indicate skipped evaluation.

  Defines the problem objective (mean variance problem includes only one objective).
  This method does not support the batch mode (evaluates single point only).
  May be implemented by user instead of :func:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_batch`,
  default implementation of which uses this method.

  The returned objective value may be NaN or ``None`` with the following meaning:

  * NaN value indicates that objective evaluation failed.
  * ``None`` value indicates that objective evaluation was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """

  define_objective_gradient = _AbstractMethodBatch('define_objective_gradient_batch', 'iterable(float)')

  """An abstract method to define mean variance problem objective gradient.

  :param x: point to evaluate
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: :term:`array-like`, 1D

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``.

  .. versionchanged:: 6.24
     evaluation results may contain ``None`` values to indicate skipped evaluations.

  Defines the objective gradient (mean variance problem includes only one objective).
  This method does not support the batch mode (evaluates single point only).
  May be implemented by user instead of :func:`~da.p7core.gtopt.ProblemMeanVariance.define_objective_gradient_batch`,
  default implementation of which uses this method.

  The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`.

  The returned array may contain NaN and ``None`` values, which have the following meaning:

  * NaN value of some gradient indicates that evaluation of a gradient failed.
  * ``None`` value indicates that evaluation of a gradient was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """

  define_constraints = _AbstractMethodBatch('define_constraints_batch', 'iterable(float)')

  """An abstract method to define mean variance problem constraints.

  :param x: point to evaluate
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: :term:`array-like`, 1D

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``.

  .. versionchanged:: 6.24
     evaluation results may contain ``None`` values to indicate skipped evaluations.

  This method does not support the batch mode (evaluates single point only).
  May be implemented by user instead of :func:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_batch`,
  default implementation of which uses this method.

  The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives()`.

  The returned array may contain NaN and ``None`` values, which have the following meaning:

  * NaN value of some constraint indicates that evaluation of a constraint failed.
  * ``None`` value indicates that evaluation of a constraint was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """


  define_constraints_gradient = _AbstractMethodBatch('define_constraints_gradient_batch', 'iterable(float)')

  """An abstract method to define gradients for mean variance problem constraints.

  :param x: point to evaluate
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: :term:`array-like`, 1D

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``.

  .. versionchanged:: 6.24
     evaluation results may contain ``None`` values to indicate skipped evaluations.

  This method does not support the batch mode (evaluates single point only).
  May be implemented by user instead of :func:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_gradient_batch`,
  default implementation of which uses this method.

  The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives()`.

  The returned array may contain NaN and ``None`` values, which have the following meaning:

  * NaN value of some gradient indicates that evaluation of a gradient failed.
  * ``None`` value indicates that evaluation of a gradient was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """


  def define_objective_batch(self, x):
    """Default implementation of the method defining mean variance problem objective. Supports non-batch and batch modes.

    :param x: points batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``; default implementation also returns ``ndarray``.

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :func:`~da.p7core.gtopt.ProblemMeanVariance.evaluate` to calculate the objective value
    (mean variance problem includes only one objective). Default implementation simply loops over the points
    batch `x`, calling :func:`~da.p7core.gtopt.ProblemMeanVariance.define_objective()` for each point.
    May be reimplemented by user to support parallel calculations.
    Such implementation may return any 2D :term:`array-like`.

    The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`.

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value indicates that objective evaluation failed.
    * ``None`` value indicates that objective evaluation was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return self._evaluate_with_time_check(x, self.size_f(), self.define_objective, self._timecheck)

  def define_constraints_batch(self, x):
    """Default implementation of the method defining mean variance problem constraints. Supports non-batch and batch modes.

    :param x: points batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``; default implementation also returns ``ndarray``.

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :func:`~da.p7core.gtopt.ProblemMeanVariance.evaluate` to calculate constraints.
    Default implementation simply loops over the points batch `x`, calling
    :func:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints()` for each point.
    May be reimplemented by user to support parallel calculations.
    Such implementation may return any 2D :term:`array-like`.

    The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`.

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value of some constraint indicates that evaluation of a constraint failed.
    * ``None`` value indicates that evaluation of a constraint was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return self._evaluate_with_time_check(x, self.size_c(), self.define_constraints, self._timecheck)

  def define_objective_gradient_batch(self, x):
    """Default implementation of the method defining mean variance problem objective gradient.
    Supports non-batch and batch modes.

    :param x: points batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``; default implementation also returns ``ndarray``.

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :func:`~da.p7core.gtopt.ProblemMeanVariance.evaluate` to calculate the objective gradient
    (mean variance problem includes only one objective). Default implementation simply loops over the points
    batch `x`, calling :func:`~da.p7core.gtopt.ProblemMeanVariance.define_objective_gradient()` for each point.
    May be reimplemented by user to support parallel calculations.
    Such implementation may return any 2D :term:`array-like`.

    The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`.

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value of some gradient indicates that evaluation of a gradient failed.
    * ``None`` value indicates that evaluation of a gradient was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return self._evaluate_with_time_check(x, _grad_size(self)[0], self.define_objective_gradient, self._timecheck)


  def define_constraints_gradient_batch(self, x):
    """Default implementation of the method defining gradients for mean variance problem constraints.
    Supports non-batch and batch modes.

    :param x: points batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* the :arg:`x` argument is ``ndarray``; default implementation also returns ``ndarray``.

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :func:`~da.p7core.gtopt.ProblemMeanVariance.evaluate` to calculate gradients for constraints.
    Default implementation simply loops over the points batch `x`, calling
    :func:`~da.p7core.gtopt.ProblemMeanVariance.define_constraints_gradient()` for each point.
    May be reimplemented by user to support parallel calculations.
    Such implementation may return any 2D :term:`array-like`.

    The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemConstrained.define_objectives_batch()`.

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value of some gradient indicates that evaluation of a gradient failed.
    * ``None`` value indicates that evaluation of a gradient was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return self._evaluate_with_time_check(x, _grad_size(self)[1], self.define_constraints_gradient, self._timecheck)


class ProblemFitting(ProblemGeneric):
  r"""
  Specialized problem class for fitting problems (see :ref:`ug_gtopt_fitting` for details).
  Inherits from :class:`~da.p7core.gtopt.ProblemGeneric`.
  A fitting problem requires to define
  a model (`f`), variables (`x`) and the data to fit (`model_x`, `model_y`).

  The problem statement is to find `x` (parameters of the model) minimizing RMS:

  .. math::

    \sqrt{N^{-1} \sum_{i=1}^N w^2_i (f(model_x^i, x) - model_y^i)^2 }

  where `w_i` are given weights. Multiple models and constraints on `x` are supported.

  .. note::

    Stochastic variables are not supported in fitting problems.

  .. note::

    History and designs do not contain model evaluations. They contain residuals and parameters and can be used to
    depict convergence or resume optimization within SBO framework.

  To define a fitting problem, create your own problem class, inheriting from :class:`~da.p7core.gtopt.ProblemFitting`.
  This class must implement the following methods:

  * :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()` inherited from :class:`~da.p7core.gtopt.ProblemGeneric`
  * :meth:`~da.p7core.gtopt.ProblemFitting.define_models()` (or :meth:`~da.p7core.gtopt.ProblemFitting.define_models_batch()`)
  * :meth:`~da.p7core.gtopt.ProblemFitting.define_constraints()` (or :meth:`~da.p7core.gtopt.ProblemFitting.define_constraints_batch()`)

  """


  def _validate(self):
    self._check_unique_names(self.objectives_names(), 'model', 'm') # intentionally perform this check PRIOR to ProblemGeneric._validate call
    self._check_unique_names(self.model_x_names(), 'model variable', 'model_x')

    ProblemGeneric._validate(self)
    if self.size_nc() > 0 or self.size_nf() > 0:
      raise _ex.InvalidProblemError('Blackbox noise is supported only in ProblemGeneric!')
    if self.size_f() == 0:
      raise _ex.InvalidProblemError("Fitting problem must define at least one model!")
    if self._grad_constraints or self._grad_objectives:
      raise _ex.InvalidProblemError("Analytical gradients are not supported in plain problems!")
    if self.size_c() > 0:
      ancestors = list(type(self).__mro__)
      ancestors.reverse()  # Start with __builtin__.object
      passed = False
      for ancestor in ancestors[3:]:
        passed = "define_constraints_batch" in ancestor.__dict__ or "define_constraints" in ancestor.__dict__
        if passed:
          break
      if not passed:
        raise _ex.InvalidProblemError("Constraint fitting problem must define 'define_constraints' or 'define_constraints_batch'")
    if self.size_c() == 0 and ("define_constraints_batch" in self.__class__.__dict__ or  "define_constraints" in self.__class__.__dict__):
      pass #we could warn here if we had logger
    if not hasattr(self, "_model_x"):
      raise _ex.InvalidProblemError("Fitting problem must define a sample using 'add_model_x'!")

    if self._sample_f.shape[0] != self._model_x['sample'].shape[0]: #check only one, other were checked in add_model_y
      raise _ex.InvalidProblemError("Number of points in 'model_x' data and 'model_y' data must be the same! 'model_x' has length %d. 'model_y' has length %d" % (self._model_x['sample'].shape[0], self._sample_f.shape[0]))

    # self._sample_f, self._model_x['sample'], self._weights
    # all these entities can be constructed as dim by dim or as multidim
    # The store and multidim in-out rule:
    # for, map, go through points, len gives number of points, and v[i] - gives a point.
    # so shape[0] is also number of points. shape[1] is dim. Dixi

  def _check_len(self, iter, target, name):
    if len(iter) != target:
      raise ValueError('Wrong number of %s evaluated: %d != %d' % (name, len(iter), target))

  def add_objective(self, name=None, hints=None):
    """
    A prohibiting implementation of the :meth:`~da.p7core.gtopt.ProblemGeneric.add_objective()` method
    inherited from :class:`~da.p7core.gtopt.ProblemGeneric`. Will simply raise an exception if you attempt to use this method;
    use :meth:`~da.p7core.gtopt.ProblemFitting.add_model_y()` instead.

    """

    raise _ex.InvalidProblemError("Fitting problem cannot have explicit objectives. Implicit objectives must be defined using add_model_y()!")

  def set_stochastic(self, distribution, generator=None, name=None, seed=0):
    """
    A prohibiting implementation of the :meth:`~da.p7core.gtopt.ProblemGeneric.set_stochastic()` method
    inherited from :class:`~da.p7core.gtopt.ProblemGeneric`.
    The fitting problem is incompatible with stochastic variables,
    so this method simply raises an :exc:`~da.p7core.InvalidProblemError` exception when used.
    """
    raise _ex.InvalidProblemError("Fitting problem is incompatible with stochastic!")

  def add_model_x(self, sample, name=None):
    """Set model_x values of fitting data.

    :param sample: sample in model_x space
    :type sample: ``ndarray``, 1D or 2D
    :param name: name of model input
    :type name: ``str``

    Initializes model_x values of fitted data (points, in which value of model is known). The length of this sample must match the length of observables data set with :meth:`~da.p7core.gtopt.ProblemFitting.add_model_y()`.

    If :arg:`sample` is a 2D array then multidimensional sample is added. The first dimension is number of points, the second is dimensionality.

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.

    """
    if self._ProblemGeneric__problem_initialized:
      raise _ex.IllegalStateError("Can not add samples to initialized problem!")

    if not hasattr(self, "_model_x"):
      self._model_x = {'name': [], 'sample': None}

    if not name:
      name = 'model_x%d' % len(self._model_x['name'])
    self._model_x['name'].append(name)

    sample = _shared.convert_to_2d_array(sample, 'sample')
    if self._model_x['sample'] is None:
      self._model_x['sample'] = sample
    else:
      if sample.shape[0]  != self._model_x['sample'].shape[0]:
        raise _ex.InvalidProblemError("All components of 'model_x' must have the same length. \
                                      Data for the model x '%s' has length %d, but %d is expected." % (name, sample.shape[0], self._model_x['sample'].shape[0]))

      self._model_x['sample'] = _numpy.hstack((self._model_x['sample'], sample))


  def model_x_names(self):
    """Get names of model variables.

    :return: name list
    :rtype: ``list[str]``
    """
    return getattr(self, '_model_x', {}).get('name', [])

  def model_info(self):
    """Provide accumulated information about all added models.

    :return: list of dicts with models properties
    :rtype: ``list`` of ``dict``
    """

    # @todo : cache model info w.r.t possible modifications of the self._groups, self._sample_f, etc
    model_info_result = [{'name': obj_name, 'sample': [], 'in_dim': 0, 'out_dim' : 0, 'weights': []} for obj_name in self.objectives_names()]
    for idx, i in enumerate(self._groups):
      if not model_info_result[i]['out_dim']: #fisrt in
        model_info_result[i]['sample'] = self._sample_f[:,idx:idx+1]
        model_info_result[i]['weights'] = self._weights[:,idx:idx+1]
      else:
        model_info_result[i]['sample'] = _numpy.hstack((model_info_result[i]['sample'], self._sample_f[:,idx:idx+1]))
        model_info_result[i]['weights'] = _numpy.hstack((model_info_result[i]['weights'], self._weights[:,idx:idx+1]))

      model_info_result[i]['in_dim'] = self.size_model_x()
      model_info_result[i]['out_dim'] += 1

    return model_info_result


  def size_model_x(self):
    """Get dimensionality of points in sample.

    :return: dimensionality
    :rtype: ``int``
    """

    if not self._ProblemGeneric__problem_initialized:
      raise _ex.IllegalStateError("Can not get dimensionality from uninitialized problem!")

    return self._model_x['sample'].shape[1]

  def get_sample(self):
    """Get fitting data.

    :return: design and observables of fitting data as a pair (designs, observables)
    :rtype: ``tuple(ndarray, ndarray)``
    """

    if not self._ProblemGeneric__problem_initialized:
      raise _ex.IllegalStateError("Can not get sample from uninitialized problem!")

    return self._model_x['sample'], self._sample_f

  def add_model_y(self, sample, weights=None, name=None, hints=None):
    """Add a new model to fit.

    :param sample: fitted observables
    :param weights: aggregation weights
    :param name: the name of the model
    :param hints: optimization hints
    :type sample: ``ndarray``, 1D or 2D
    :type weights: ``ndarray``, 1D or 2D
    :type name: ``str``
    :type hints: ``dict``

    Initializes a new model in the problem.

    The length of the *sample* and *weights* (if set) must match the length of design data set with :meth:`~da.p7core.gtopt.ProblemFitting.add_model_x()`

    The *weights* argument is optional; if it is not provided, unit weights is used.

    The *name* argument is optional; if you do not provide a name, it is generated automatically.
    Auto names are ``"f1"``, ``"f2"``, ``"f3"``, and so on, in the order of adding models to a problem.

    The *hints* argument sets objective-specific options that may direct optimizer to use alternative internal algorithms to increase performance
    (see :ref:`ug_gtopt_hints`).
    It is a dictionary ``{hint name: value}``, for example ``{"@GTOpt/EvaluationCostType": "Expensive"}``. Please, note that "@GTOpt/LinearityType" can be ignored
    and setting different computational cost type for different models may lead to undesirable results.

    If `sample` is 2D array then multidimensional model is added. The first dimension is number of points, the second is number of models.

    This method should be called from :meth:`~da.p7core.gtopt.ProblemGeneric.prepare_problem()`.
    """
    if self._ProblemGeneric__problem_initialized:
      raise _ex.IllegalStateError("Can not add models to initialized problem!")

    if hints is not None: #drop analytical hint
      _shared.check_concept_dict(hints, 'model hints')
      for key in list(hints):
        if isinstance(key, str) and key.lower() == "@GTOpt/LinearityType".lower():
          hints.pop(key, None)

    if not name:
      name = 'm%d' % (len(self._objectives) + 1)
    self._objectives.append(_Objective(name, hints))


    sample = _shared.convert_to_2d_array(sample, 'sample')

    if not hasattr(self, "_sample_f"):
      self._sample_f = sample
    else:
      if sample.shape[0] != self._sample_f.shape[0]:
        raise _ex.InvalidProblemError("All `model_y` samples must have the same length. \
                                      Data for the model '%s' has length %d, but %d is expected." % (name, sample.shape[0], self._sample_f.shape[0]))
      self._sample_f = _numpy.hstack((self._sample_f, sample))

    if not hasattr(self, "_groups"):
      self._groups = []
    self._groups += [len(self._objectives) - 1] * sample.shape[1]

    if weights is not None:
      weights = _shared.convert_to_2d_array(weights, 'weights')
      if weights.shape[0] != sample.shape[0]:
        raise _ex.InvalidProblemError("Weights must be 'None' or their length must much number of points in sample! Weights have length %d. \
                                      Data for the model '%s' has length %d" % (weights.shape[0], name, sample.shape[0]))
      if weights.shape[1] == 1:
        weights = _numpy.repeat(weights, sample.shape[1], axis=1)
      else:
        if weights.shape[1] != sample.shape[1]:
          raise _ex.InvalidProblemError("Weights must have a single dimensionlity or the same dimensionlity as sample! Weights have dimensionlity %d. \
                                         Data for the model '%s' has dimensionlity %d" % (weights.shape[0], name, sample.shape[0]))
    else:
      weights  = _numpy.ones(sample.shape)

    if not hasattr(self, "_weights"):
      self._weights = weights
    else:
      self._weights = _numpy.hstack((self._weights, weights))

    if not _numpy.isfinite(self._weights[:, -weights.shape[1]:]).all():
      raise ValueError("Weights must be finite. Got 'NaN/Inf' for the model '%s'" % name)

  define_models  = _AbstractMethodBatch("define_models_batch", "iterable(float)", "iterable(float)")
  """An abstract method to define fitted models.

  :param t: point from sample to evaluate
  :type t: ``ndarray``, 1D
  :param x: parameters of models to evaluate
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: ``ndarray``, 1D

  .. versionchanged:: 6.24
     evaluation results may contain ``None`` values to indicate skipped evaluations.

  This method does not support the batch mode (evaluates single point only). May be implemented by user instead of
  :meth:`~da.p7core.gtopt.ProblemFitting.define_models_batch()` (which uses this method by default).

  The shape of :arg:`x` is *(1, m)* where *m* is the input dimension (:meth:`~da.p7core.gtopt.ProblemGeneric.size_x()`).

  The shape of *t* is *(1, n)* where *n* is the sample dimension (:meth:`~da.p7core.gtopt.ProblemFitting.size_model_x()`).

  The returned array may contain NaN and ``None`` values, which have the following meaning:

  * NaN value indicates that evaluation failed.
  * ``None`` value indicates that evaluation was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """


  def define_models_batch(self, t, x):
    """Default implementation of the method defining fit models. Supports non-batch and batch modes.

    :param t: design sample
    :type t: ``ndarray``, 2D
    :param x: parameters batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 3D

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :meth:`.ProblemFitting.evaluate` to calculate fitting error
    Default implementation simply loops over the points batch *x* for each *t*, calling
    :meth:`~da.p7core.gtopt.ProblemFitting.define_models()` for each point.
    May be reimplemented by user to support parallel calculations.
    Such implementation must return any 3D :term:`array-like`.

    The shape of :arg:`x` is *(n, m)* where *n* is the number of points to evaluate (at most :ref:`GTOpt/BatchSize<GTOpt/BatchSize>`) and *m*
    is the input dimension ( :meth:`~da.p7core.gtopt.ProblemGeneric.size_x()`).

    The shape of *t* is *(p, q)* where *p* is the sample length number of points to evaluate (at most :ref:`GTOpt/BatchSize<GTOpt/BatchSize>`) and *q*
    is the its dimension ( :meth:`~da.p7core.gtopt.ProblemFitting.size_model_x()`).

    The implementation of method must return values for each design in design sample (*t*) for each set of parameters in batch (*x*) for each model.
    The results must be a 3D ``ndarray`` with the shape (len(x), :meth:`~da.p7core.gtopt.ProblemFitting.size_model_x()`, :meth:`~da.p7core.gtopt.ProblemGeneric.size_f()`)

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value indicates that evaluation failed.
    * ``None`` value indicates that evaluation was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return _numpy.array([self.define_models(i, p) for p in x for i in t ]).reshape((len(x), len(t), self._sample_f.shape[1]))

  def define_constraints_batch(self, x):
    """Default implementation of the method defining problem constraints. Supports non-batch and batch modes.

    :param x: x batch
    :type x: ``ndarray``, 2D
    :return: evaluation results
    :rtype: ``ndarray``, 2D

    .. versionchanged:: 6.24
       evaluation results may contain ``None`` values to indicate skipped evaluations.

    This method is used by :meth:`.ProblemFitting.evaluate` to calculate constraints.
    Default implementation simply loops over the points batch *parameters*, calling
    :meth:`~da.p7core.gtopt.ProblemFitting.define_constraints()` for each point.
    May be reimplemented by user to support parallel calculations.
    Such implementation may return any 2D :term:`array-like`.

    The shape of :arg:`x` is the same as in :meth:`~da.p7core.gtopt.ProblemFitting.define_models_batch()` .

    The returned array may contain NaN and ``None`` values, which have the following meaning:

    * NaN value of some constraint indicates that evaluation of a constraint failed.
    * ``None`` value indicates that evaluation of a constraint was skipped.

    Note that skipped and failed evaluations may stop optimization prematurely.
    """
    return _numpy.array([self.define_constraints(_) for _ in x])


  define_constraints        = _OptionalMethodBatch("define_constraints_batch", "iterable(float)")
  """An optional method to define problem constraints.

  :param x: combination of parameter values to test against constraints
  :type x: ``ndarray``, 1D
  :return: evaluation results
  :rtype: :term:`array-like`, 1D

  .. versionchanged:: 6.24
     evaluation results may contain ``None`` values to indicate skipped evaluations.

  This method does not support the batch mode (evaluates single point only). May be implemented by user instead of
  :meth:`~da.p7core.gtopt.ProblemFitting.define_constraints_batch` (which uses this method by default).

  The shape of *parameters* is the same as in :meth:`~ProblemFitting.define_models()`.

  The returned array may contain NaN and ``None`` values, which have the following meaning:

  * NaN value of some constraint indicates that evaluation of a constraint failed.
  * ``None`` value indicates that evaluation of a constraint was skipped.

  Note that skipped and failed evaluations may stop optimization prematurely.
  """

  def evaluate(self, queryx, querymask):
    """
    Default implementation of the :func:`~da.p7core.gtopt.ProblemGeneric.evaluate()` method
    inherited from the base class :class:`~da.p7core.gtopt.ProblemGeneric`.
    Should not be reimplemented; use
    :meth:`~da.p7core.gtopt.ProblemFitting.define_models()` and
    :meth:`~da.p7core.gtopt.ProblemFitting.define_constraints()`.
    """

    queryx = _numpy.array(queryx, dtype=float, ndmin=2, copy=_shared._SHALLOW)
    querymask = _numpy.array(querymask, dtype=bool, ndmin=2, copy=_shared._SHALLOW)
    size_f = self.size_f()
    size_cf = size_f + self.size_c()
    assert queryx.shape[0] == querymask.shape[0], "The number of points to evaluate does not conform the number of the evaluation requests masks."
    assert size_cf == querymask.shape[1], "The number of responses in requests masks does match number of responses in the problem."

    points = _numpy.empty(querymask.shape, dtype=float)
    masks = _numpy.empty(querymask.shape, dtype=bool)

    masks[:, :size_f] = querymask[:, :size_f].any(axis=1).reshape((-1, 1))
    masks[:, size_f:] = querymask[:, size_f:].any(axis=1).reshape((-1, 1))

    if querymask[:, :size_f].any():
      obj_vars_mask = masks[:,0]

      if obj_vars_mask.all():
        n_points = len(obj_vars_mask)
        values = _numpy.array(self.define_models_batch(self._model_x['sample'], queryx))#no reshape here!, expect proper shape from user side.
        obj_result = points[:, 0:size_f]
      else:
        n_points = _numpy.count_nonzero(obj_vars_mask)
        values = _numpy.array(self.define_models_batch(self._model_x['sample'], queryx[obj_vars_mask]))#no reshape here!, expect proper shape from user side.
        obj_result = _numpy.zeros((n_points, size_f))

      proper_shape = (n_points, self._model_x['sample'].shape[0], self._sample_f.shape[1])
      if values.shape != proper_shape:
        raise ValueError("wrong number of components in blackbox response for the evaluated objective batch: the response shape for point should be %s (problem returned %s)" % (proper_shape, values.shape))

      nontrivial_groups = self._groups and not _numpy.equal(self._groups, list(range(self._sample_f.shape[1]))).all()
      f_result = _numpy.empty((n_points, self._sample_f.shape[1])) if nontrivial_groups else obj_result

      nan_index = ~_numpy.isfinite(self._sample_f)
      has_nan_index = nan_index.any()

      old_settings = _numpy.seterr(all='ignore')
      try:
        for obj_idx, value_f in enumerate(values):
          err = (value_f - self._sample_f) * self._weights
          if has_nan_index:
            err[nan_index] = 0. #suppress nans in y sample
          # calculate columnwise sqrt(sum(err*err)) with workaround for the numpy hypot.reduce bug
          _numpy.fabs(_numpy.hypot.reduce(err, axis=0), out=f_result[obj_idx])

        if nontrivial_groups:
          group_weight = _numpy.zeros((size_f,))
          obj_result[:] = 0.

          for f_idx, obj_idx in enumerate(self._groups):
            group_weight[obj_idx] += 1.
            _numpy.hypot(obj_result[:, obj_idx], f_result[:, f_idx], out=obj_result[:, obj_idx])
        else:
          group_weight = _numpy.ones((size_f,))

        # normalize obj_result w.r.t the number of outputs in group
        _numpy.multiply(group_weight, float(self._model_x['sample'].shape[0]), out=group_weight)
        _numpy.sqrt(group_weight, out=group_weight)
        _numpy.divide(obj_result, group_weight.reshape(1, -1), out=obj_result)
      finally:
        _numpy.seterr(**old_settings)

      if not obj_vars_mask.all():
        # copy sparse result back to points
        points[obj_vars_mask, 0:size_f] = obj_result

    if size_cf > size_f:
      self._read_batch_data(queryx, masks[:, size_f], points[:, size_f:size_cf],
                            self.define_constraints_batch, self.constraints_names(),
                            'constraints')
      _numpy.logical_and(masks[:, size_f:size_cf], ~_shared._find_holes(points[:, size_f:size_cf]), out=masks[:, size_f:size_cf])

    return points, masks

class _LimitedEvaluations(object):
  def __init__(self, problem, limits, scalability):
    self._evaluate = problem._evaluate
    self._limits = limits
    self._scalability = scalability or 1

  def __call__(self, queryx, querymask, *args, **kwargs):
    original_querymask = querymask
    for i, limit in enumerate(self._limits):
      if limit < 0:
        continue
      requested = _numpy.count_nonzero(querymask[:, i])
      #self._limits[i] = max(0, limit - (requested + self._scalability - 1) // self._scalability) # pre-limit is now post-limit
      limit *= self._scalability
      if requested <= limit:
        continue
      if querymask is original_querymask:
        querymask = querymask.copy()
      # get only first `limit` evaluations
      querymask[(_numpy.nonzero(querymask[:, i])[0][limit] if limit else 0):,i] = 0

    if querymask is not original_querymask:
      if not querymask.any():
        # don't call if nothing to call
        return _shared._filled_array(querymask.shape, _shared._NONE), querymask
      # call only limited set of points
      active_points = querymask.any(axis=1)
      if not active_points.all():
        responses_buffer = _shared._filled_array(querymask.shape, _shared._NONE)
        responses_buffer[active_points], querymask[active_points] = self._evaluate(queryx[active_points], querymask[active_points], *args, **kwargs)
        return self._update_limits(responses_buffer, querymask)

    # forward evaluation
    return self._update_limits(*self._evaluate(queryx, querymask, *args, **kwargs))

  def _update_limits(self, calcs, masks):
    try:
      # update limits according to the real number of evaluations
      obtained = (_numpy.array(masks, dtype=bool, copy=_shared._SHALLOW).sum(axis=0)[:len(self._limits)] + self._scalability - 1) // self._scalability
      # note the length of the obtained vector can be greater than the length of the limits vector because of gradients and blackbox noise
      self._limits = _numpy.subtract(self._limits, _numpy.minimum(obtained, _numpy.maximum(self._limits, 0)))
    except:
      # It's better to ignore limits than to fail AFTER a succeeded evaluation.
      pass

    return calcs, masks

class _SlicedEvaluationsBlackbox(object):
  def __init__(self, evaluate, input_size, response_size, batch_size, watcher, exception_handler=None):
    self._evaluate = evaluate
    self._input_size = input_size
    self._response_size = response_size
    self._batch_size = batch_size or _numpy.iinfo(int).max
    self._watcher = watcher
    self._exception_handler = exception_handler

  def __call__(self, points, *args, **kwargs):
    points = _shared.as_matrix(points, shape=(None, self._input_size), dtype=float)
    n_points = len(points)

    response_data = _numpy.empty((n_points, self._response_size), dtype=float)
    response_data.fill(_shared._NONE)

    last_point = 0
    while last_point < n_points:
      if self._watcher and not self._watcher():
        return response_data
      
      first_point, last_point = last_point, min(n_points, last_point + self._batch_size)
      try:
        response_data[first_point:last_point] = self._evaluate(points[first_point:last_point], *args, **kwargs)
      except:
        if _shared._find_holes(response_data).all():
          raise
        # we must keep these values
        if self._exception_handler:
          self._exception_handler(_sys.exc_info())
        break

    if self._watcher:
      self._watcher() # post-call watcher to deliver a new snapshot

    return response_data

class _SlicedEvaluationsProblemGeneric(object):
  def __init__(self, evaluate, input_size, response_size, batch_size, watcher, exception_handler=None):
    self._evaluate = evaluate
    self._input_size = input_size
    self._response_size = response_size
    self._batch_size = batch_size or _numpy.iinfo(int).max
    self._watcher = watcher
    self._exception_handler = exception_handler

  def __call__(self, queryx, querymask, *args, **kwargs):
    queryx = _shared.as_matrix(queryx, shape=(None, self._input_size), dtype=float)
    n_points = len(queryx)

    querymask = _shared.as_matrix(querymask, shape=(n_points, self._response_size), dtype=bool)

    response_mask = _numpy.zeros_like(querymask)
    response_data = _numpy.empty(querymask.shape, dtype=float)
    response_data.fill(_shared._NONE)

    last_point = 0
    while last_point < n_points:
      if self._watcher and not self._watcher():
        return response_data, response_mask
      first_point, last_point = last_point, min(n_points, last_point + self._batch_size)
      try:
        response_data[first_point:last_point], response_mask[first_point:last_point] = self._evaluate(queryx[first_point:last_point], querymask[first_point:last_point], *args, **kwargs)
      except:
        if not response_mask.any():
          raise
        # we must keep these values
        if self._exception_handler:
          self._exception_handler(_sys.exc_info())
        break

    if self._watcher and response_mask.any():
      self._watcher() # post-call watcher to deliver a new snapshot

    return response_data, response_mask

class _PeriodicWatcherWrapper(object):
  def __init__(self, watcher_ref, request_timeout_ms):
    try:
      self._now = _time.monotonic # This method is the best, but absent in 2.7
    except:
      self._now = _time.time # Python 2.7 fallback: time.clock() would be better, but on Linux it's the perfect UB.

    self._watcher_ref = watcher_ref
    self._request_timeout = 0.001 * float(request_timeout_ms)
    self._watcher_wall = self._now() + self._request_timeout
    self._keep_working = True

  def __call__(self, *args, **kwargs):
    watcher = self._watcher_ref() if self._watcher_ref else None
    if not watcher:
      return True
    elif not self._request_timeout:
      if not watcher():
        self._keep_working = False
    elif self._now() >= self._watcher_wall:
      if not watcher():
        self._keep_working = False
      self._watcher_wall = self._now() + self._request_timeout

    return self._keep_working

def _overloaded_method(obj, method_name):
  impl = None
  for cls in _inspect.getmro(type(obj)):
    method = getattr(cls, method_name, None)
    if callable(method):
      if impl is None:
        impl = method
      elif impl != method:
        return True
  return False

def _small_batches_heuristic(problem):
  if not problem:
    return False

  # We'd like to keep both: backwards compatibility and the benefits of interruptible small batches.
  try:
    # These methods get one point per call. Also, there are default implementation of batch version of these methods.
    # We can use small batch if user provided custom implementation of a single-point method and has not provided custom batch version,
    sequential_methods = ("define_objectives", "define_constraints", "define_objective_gradient", "define_constraints_gradient", "define_models",)
    for method_name in sequential_methods:
      method = getattr(problem, method_name, None)
      if callable(method) and not isinstance(method, _AbstractMethodBatch) and not _overloaded_method(problem, method_name + "_batch"):
        return True

    # Discrete problems are a special kind of problems
    for i, variable_type in enumerate(problem.elements_hint(slice(0, problem.size_x()), "@GT/VariableType")):
      variable_type = str(variable_type or "continuous").lower()
      if variable_type != "categorical":
        variable_bounds = problem.variables_bounds(i)
        if variable_type in ("discrete", "stepped"):
          if len(variable_bounds) > 1:
            return False
        elif _numpy.isnan(variable_bounds).any() or variable_bounds[0] < variable_bounds[1]:
          return False

    return True
  except:
    pass

  return False

@_contextlib.contextmanager
def _limited_evaluations(problem, maximum_iterations=None, maximum_expensive_iterations=None, \
                         sample_x=None, sample_f=None, sample_c=None, responses_scalability=None,
                         watcher_ref=None, configuration=None):
  try:
    original_evaluate = problem._evaluate
  except:
    original_evaluate = None

  original_calc = None
  configuration = configuration or {}
  responses_scalability = configuration.get('responses_scalability', responses_scalability) or 1

  if original_evaluate is not None:
    try:
      evaluations_limit = configuration.get('evaluations_limit')
      if evaluations_limit is None or len(evaluations_limit) > problem.size_full():
        evaluations_limit = problem._responses_evaluation_limit(-1, maximum_iterations=maximum_iterations,
                                                                maximum_expensive_iterations=maximum_expensive_iterations,
                                                                sample_x=sample_x, sample_f=sample_f, sample_c=sample_c)
      if not all(_ < 0 for _ in evaluations_limit):
        problem._evaluate = _LimitedEvaluations(problem, evaluations_limit, responses_scalability)
    except:
      pass

  batch_size = configuration.get('batch_size', 0)
  if batch_size:
    batch_size = max(1, batch_size // responses_scalability) * responses_scalability
  elif watcher_ref:
    if original_evaluate is not None and _small_batches_heuristic(problem):
      batch_size = responses_scalability
    else:
      # Dummy batch size to avoid evaluations after termination
      batch_size = _numpy.iinfo(int).max

  if batch_size:
    try:
      watcher = _PeriodicWatcherWrapper(watcher_ref, configuration.get('watcher_timeout_ms', 1000))
    except:
      watcher = None

    def exception_handler(exc_info):
      try:
        setattr(problem, "_last_error", exc_info)
      except:
        pass

    if original_evaluate is not None:
      try:
        if isinstance(problem, ProblemGeneric):
          problem._evaluate = _SlicedEvaluationsProblemGeneric(evaluate=problem._evaluate, input_size=(problem.size_x() + problem.size_s()),
                                                               response_size=problem.size_full(), batch_size=batch_size,
                                                               watcher=watcher, exception_handler=exception_handler)
        else:
          problem._evaluate = _SlicedEvaluationsBlackbox(evaluate=problem._evaluate, input_size=problem.size_x(),
                                                         response_size=problem.size_full(), batch_size=batch_size,
                                                         watcher=watcher, exception_handler=exception_handler)
      except:
        pass
    else:
      try:
        original_calc = problem.calc
        problem.calc = _SlicedEvaluationsBlackbox(evaluate=problem.calc, input_size=problem.size_x,
                                                  response_size=problem.size_f, batch_size=batch_size,
                                                  watcher=watcher, exception_handler=exception_handler)
      except:
        pass

  try:
    yield problem
  finally:
    if original_evaluate is not None and problem._evaluate is not original_evaluate:
      problem._evaluate = original_evaluate
    if original_calc is not None and problem.calc is not original_calc:
      problem.calc = original_calc
