#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""pSeven Core blackbox module."""
from __future__ import with_statement

import sys
import ctypes as _ctypes
import struct as _struct
import contextlib as _contextlib
import numpy as _numpy

from warnings import warn as _warn

from .six import string_types, with_metaclass
from .six.moves import range
from . import shared as _shared
from . import options as _options
from . import exceptions as _ex

# Model methods

_PCREATE = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_size_t)
_PFREE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)
_PSIZE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_size_t))

_SINGLE_RESPONSE_CALLBACK_TYPE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.POINTER(_ctypes.c_double), _ctypes.c_size_t, _ctypes.POINTER(_ctypes.c_double), _ctypes.c_void_p, # ret. value, [in] x, incx, [out] f, opaque (null)
                                                   _ctypes.c_size_t, _ctypes.POINTER(_ctypes.c_double), _ctypes.c_size_t, _ctypes.c_size_t) # incf, [out] grad, next_df, next_dx


# Internal enums

(GTIBB_GRADIENT_F_ORDER, GTIBB_GRADIENT_X_ORDER) = range(2)

# Internal classes

class _Response(object):
  """Encapsulates response validation."""
  def __init__(self, name):
    if name:
      _shared.check_type(name, 'response name', string_types)
      self.name = name
    else:
      raise ValueError('Response must have a name!')

class _Variable(object):
  """Encapsulates variable validation."""
  def __init__(self, name, bounds):
    if name:
      _shared.check_type(name, 'variable name', string_types)
      self.name = name
    else:
      raise ValueError('Variable must have a name!')
    if _shared.is_sized(bounds) and len(bounds) == 2:
      _shared.check_concept_numeric(bounds[0], 'lower_bound')
      self.lower_bound = float(bounds[0])
      _shared.check_concept_numeric(bounds[1], 'upper bound')
      self.upper_bound = float(bounds[1])
    else:
      raise ValueError('Variable must define bounds and they must have proper structure!')

class _AbstractMethod(object):
  def __init__(self, *args):
    if args:
      self.args = '(%s)' % (','.join(args))
      self.nargs = len(args)
    else:
      self.args = '()'
      self.nargs = 0

class _BlackboxMetaclass(type):
  """Service metaclass to support blackbox initialization-time check and abstract methods."""
  def __init__(cls, name, bases, *args, **kwargs):
    super(_BlackboxMetaclass, cls).__init__(cls, name, bases)

    cls.__new__ = staticmethod(cls.new)

    def initializer(self, *iargs, **ikwargs):
      cls.__oldinit__(self, *iargs, **ikwargs)
      if cls is type(self):
        self._initialize()

    cls.__oldinit__ = cls.__init__
    cls.__init__ = initializer

    abstractmethods = dict()
    ancestors = list(cls.__mro__)
    ancestors.reverse()  # Start with __builtin__.object
    for ancestor in ancestors:
      for clsname, clst in ancestor.__dict__.items():
        if isinstance(clst, _AbstractMethod):
          abstractmethods[clsname] = clst.args
        else:
          if clsname in abstractmethods and hasattr(clst, '__call__'):
            abstractmethods.pop(clsname)

    setattr(cls, '__abstractmethods__', abstractmethods)

  def new(self, cls, *args, **kwargs):
    if cls.__abstractmethods__:
      method_list = '\n  '.join([meth[0] + meth[1] for meth in cls.__abstractmethods__.items()])
      error_message = 'Can\'t instantiate abstract class `' + cls.__name__ + '\';\n' + 'Abstract methods: \n  ' + method_list
      raise NotImplementedError(error_message)

    obj = object.__new__(cls)
    return obj


class Blackbox(with_metaclass(_BlackboxMetaclass, object)):
  """Base blackbox class.

  To create your own blackbox, inherit from this class and implement two methods:
  :meth:`~da.p7core.blackbox.Blackbox.prepare_blackbox()` and
  :meth:`~da.p7core.blackbox.Blackbox.evaluate()`. Then specify an instance of your class as
  an argument for the blackbox-based method.

  See the :ref:`examples_gtdf_vs_gtapprox` example for a guide on :class:`~da.p7core.blackbox.Blackbox` class usage.

  """
  _NaN = _numpy.nan

  def __init__(self):
    self.nanValue = self._NaN

  # called on metaclass level
  def _initialize(self):
    """Service method to ensure initialization of blackbox."""
    self.__blackboxInitialized = False
    self._variables = []
    self._responses = []

    self._grad_enabled = False
    self._numerical_gradient_step = 1.0e-7

    self._history_cache = []
    self._history_inmemory = True
    self._history_file = None
    self._header_required = False
    try:
      _shared.wrap_with_exc_handler(self.prepare_blackbox, _ex.BBPrepareException)()
      self._validate()
      self.__blackboxInitialized = True
    except _ex.ExceptionWrapper:
      e, tb = sys.exc_info()[1:]
      e.set_prefix("Problem definition error: ")
      _shared.reraise(type(e), e, tb)
    except Exception:
      e, tb = sys.exc_info()[1:]
      _shared.reraise(_ex.InvalidProblemError, "Problem definition error: %s" % e, tb)

  def _validate(self):
    """Service method to ensure validity of blackbox."""
    if self.size_x() == 0:
      raise _ex.InvalidProblemError('User must define at least one input variable!')


  def __str__(self):
    """Blackbox string representation.

    :rtype: str

    """
    result = '''da.p7core blackbox:
    Type: %s
    Number of variables: %d
    Number of functions: %d
    ''' % (type(self).__name__,
           self.size_x(),
           self.size_f())
    result += 'Variables bounds: \n'
    for v in self._variables:
      result += '    '
      result += ' '.join([v.name, str(v.lower_bound), str(v.upper_bound), '\n'])

    return result.strip()


  def variables_bounds(self):
    """
    Check the blackbox bounds.

    :return: blackbox bounds (lower, upper)
    :rtype: ``tuple(list[float], list[float])``

    Returns the bounds for all variables initialized by :meth:`~da.p7core.blackbox.Blackbox.add_variable()`.
    Returned tuple contains two lists, the first is all lower bounds, the second is upper bounds.
    Bounds are listed in the same order in which the variables were initialized.

    Hint: if you want a per-variable output, use

    >>> zip(my_blackbox.variables_bounds())

    to get a list of tuples *(lower, upper)*.

    """
    lower = []
    upper = []
    for x in self._variables:
      lower.append(x.lower_bound)
      upper.append(x.upper_bound)
    return lower, upper

  def size_x(self):
    """
    Check the number of blackbox variables initialized by :meth:`~da.p7core.blackbox.Blackbox.add_variable()`.

    :return: number of variables
    :rtype: ``int``

    """
    return len(self._variables)

  def size_f(self):
    """
    Check the number of blackbox responses initialized by :meth:`~da.p7core.blackbox.Blackbox.add_response()`.

    :return: number of responses
    :rtype: ``int``

    """
    return len(self._responses)

  def size_full(self):
    """
    Check what the evaluation result length should be.

    :return: total number of responses and gradients
    :rtype: ``int``

    .. versionadded:: 1.11.0

    This method returns the required length of a single evaluation result.
    It equals the number of responses plus the number of gradients ---
    that is, for a function with *m* input and *k* output components, length is
    *k + mk* if gradients are enabled (see :meth:`~da.p7core.blackbox.Blackbox.enable_gradients()`);
    otherwise, :meth:`~da.p7core.blackbox.Blackbox.size_full()` is equal to :meth:`~da.p7core.blackbox.Blackbox.size_f()`.

    """

    if self._grad_enabled:
      obj_nnz = self.size_x() * self.size_f()
    else:
      obj_nnz = 0

    return self.size_f() + obj_nnz

  def add_variable(self, bounds, name=None):
    """Initialize a new blackbox variable (input component).

    :param bounds: variable bounds (lower, upper)
    :type bounds: ``tuple(float, float)``
    :param name: variable name (optional)
    :type name: ``str``

    This method should be called from :meth:`~da.p7core.blackbox.Blackbox.prepare_blackbox()`.

    Adds an input component to the blackbox. All variables initialized with :meth:`~da.p7core.blackbox.Blackbox.add_variable()`
    are scalar. To create a blackbox with vector input, call :meth:`~da.p7core.blackbox.Blackbox.add_variable()` several times.

    The *bounds* parameter may be understood (roughly) as specifying the blackbox domain. This is more like a recommendation
    for the methods using this blackbox: evaluations will not be restricted to the domain, but the blackbox will return
    the domain bounds from :meth:`~da.p7core.blackbox.Blackbox.variables_bounds()`. To clarify, allowing evaluations
    outside the domain is needed to support the numerical differentiation on the blackbox bounds.

    """
    if self.__blackboxInitialized:
      raise _ex.IllegalStateError("Can't change initialized blackbox!")
    if not name:
      name = 'x%d' % (len(self._variables) + 1)
    self._variables.append(_Variable(name, bounds))

  def add_response(self, name=None):
    """Initialize a new blackbox response (output component).

    :param name: response name (optional)
    :type name: ``str``

    This method should be called from :meth:`~da.p7core.blackbox.Blackbox.prepare_blackbox()`.

    Adds an output component to the blackbox. All responses initialized with :meth:`~da.p7core.blackbox.Blackbox.add_response()`
    are scalar. To create a blackbox with vector output, call :meth:`~da.p7core.blackbox.Blackbox.add_response()` several times.

    """
    if self.__blackboxInitialized:
      raise _ex.IllegalStateError("Can't change initialized blackbox!")
    if not name:
      name = 'f%d' % (len(self._responses) + 1)
    self._responses.append(_Response(name))


  def enable_gradients(self, order=GTIBB_GRADIENT_F_ORDER):
    """
    Enable using analytical gradients.

    :param order: gradient enumeration order
    :type order: :data:`~da.p7core.blackbox.GTIBB_GRADIENT_F_ORDER`, :data:`~da.p7core.blackbox.GTIBB_GRADIENT_X_ORDER`
    :return: ``None``

    .. versionadded:: 1.11.0

    By default, numerical differentiation is used automatically to provide blackbox gradient values.
    Alternatively, you may provide gradients in :meth:`~da.p7core.blackbox.Blackbox.evaluate()` ---
    see its description for more details. Before that, the blackbox has to be switched to the analytical gradients mode
    by calling :meth:`~da.p7core.blackbox.Blackbox.enable_gradients()` once upon initialization.

    Optional *order* argument sets the order in which gradient values are included into output; default is F-major.

    This method should be called from :meth:`~da.p7core.blackbox.Blackbox.prepare_blackbox()`.

    """
    if self.__blackboxInitialized:
      raise _ex.IllegalStateError("Can't change initialized blackbox!")
    self._grad_order = order
    self._grad_enabled = True

  def disable_gradients(self):
    """
    Disable using analytical gradients.

    .. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

    *New in version 2.0 Release Candidate 1.*

    Disables analytical gradients for the blackbox and switches back to using numerical differentiation
    (see :meth:`~da.p7core.blackbox.Blackbox.enable_gradients()`).

    This method should be called from :meth:`~da.p7core.blackbox.Blackbox.prepare_blackbox()`. It is intended to
    cancel analytical gradients in a new blackbox class inherited from a blackbox with enabled analytical gradients.

    """
    if self.__blackboxInitialized:
      raise _ex.IllegalStateError("Can\'t change initialized blackbox!")
    self._grad_enabled = False

  @property
  def gradients_enabled(self):
    """
    Check if analytical gradients are enabled for the blackbox.

    :Type: ``bool``

    .. versionadded:: 1.11.0

    This attribute is ``True`` if analytical gradients are enabled for the blackbox.
    """
    return self._grad_enabled

  @property
  def gradients_order(self):
    """Check gradient values order.

    :type: constant

    .. versionadded:: 1.11.0

    By default, the gradients are in F-major order, and this attribute is :data:`~da.p7core.blackbox.GTIBB_GRADIENT_F_ORDER`.
    To set the X-major order, use :meth:`~da.p7core.blackbox.Blackbox.enable_gradients()` with argument :data:`~da.p7core.blackbox.GTIBB_GRADIENT_X_ORDER`.

    """
    return getattr(self, "_grad_order", GTIBB_GRADIENT_F_ORDER)

  def set_numerical_gradient_step(self, value):
    """
    Set the numerical differentiation step.

    :param value: step value
    :type value: ``float``
    :return: ``None``

    .. versionadded:: 1.11.0

    This method should be called from :meth:`~da.p7core.blackbox.Blackbox.prepare_blackbox()`.
    """
    self._numerical_gradient_step = value


  @property
  def numerical_gradient_step(self):
    """
    Numerical differentiation step.

    :Type: ``float``

    .. versionadded:: 1.11.0

    Numerical differentiation step value, default is `10^{-7}`. To set a different step, use :meth:`~da.p7core.blackbox.Blackbox.set_numerical_gradient_step()`.

    """
    return self._numerical_gradient_step

  @property
  def _history_fields(self):
    """
    Enumerates data fields in :attr:`~da.p7core.gtopt.ProblemGeneric.history` and :attr:`~da.p7core.gtopt.ProblemGeneric.designs`.

    :type: ``tuple(list[tuple(str, int, int)], list[str])``

    The first element of result enumerates top-level fields name (``x``, ``f``, ``c``, and so on) followed by index of the first and one-past-last field columns.

    The second element of result is a list of columns name.

    """
    variables_names = [v.name for v in self._variables]
    objectives_names = [v.name for v in self._responses]

    current_offset, current_length = 0, len(variables_names)
    basic_fields = [("x", current_offset, current_length)]
    columns_names = variables_names

    if objectives_names:
      current_offset, current_length = current_length, current_length + len(objectives_names)
      basic_fields.append(("f", current_offset, current_length))
      columns_names.extend(objectives_names)

      if self._grad_enabled:
        size_x, size_f = len(variables_names), len(objectives_names)
        dfdx_fields = [(i, j) for i in range(size_f) for j in range(size_x)] \
                      if self._grad_order == GTIBB_GRADIENT_F_ORDER else \
                      [(i, j) for j in range(size_x) for i in range(size_f)]

        current_offset, current_length = current_length, current_length + len(dfdx_fields)
        basic_fields.append(("dfdx", current_offset, current_length))
        columns_names.extend(("d_%s/d_%s" % (objectives_names[i], variables_names[j])) for i, j in dfdx_fields)

    return basic_fields, columns_names

  def _get_header(self):
    return ",".join(self._history_fields[1])

  def set_history(self, **kwargs):
    """
    Configure saving blackbox evaluations.

    :param add_header: add a header to the history file
    :type add_header: ``bool``
    :param file: write history to file
    :type file: ``str``, ``file`` or ``None``
    :param memory: store history in memory
    :type memory: ``bool``

    .. versionadded:: 4.0

    Return values of :meth:`~da.p7core.blackbox.Blackbox.evaluate()` can be saved to memory
    or to a file on disk. History saving modes are independent: both can be enabled simultaneously
    so history is saved in memory while also writing to a file. Default configuration is to save
    history to memory only.

    .. note::

       Default configuration increases memory consumption. If you implement your own way to save
       the history of evaluations, always use :meth:`~da.p7core.blackbox.Blackbox.disable_history()`.
       If there are a lot of evaluations in your problem, consider reconfiguring history to only write
       it to a file.

    If *memory* is ``True``, evaluations are saved to :attr:`~da.p7core.blackbox.Blackbox.history`.
    If ``False``, disables updating :attr:`~da.p7core.blackbox.Blackbox.history` but does not
    clear it. Re-enabling in case :attr:`~da.p7core.blackbox.Blackbox.history` is not empty
    appends to existing history; if it is not wanted, call
    :meth:`~da.p7core.blackbox.Blackbox.clear_history()` first.

    The *file* argument can be a path string or a file-like object (enables writing history to file).
    Note that the file is opened in append mode.
    To disable the file history, set *file* to ``None``.
    Values in a history file are comma-separated.

    If *add_header* is ``True``, the first line appended to file is a header containing
    the names of blackbox variables and responses set by
    :meth:`~da.p7core.blackbox.Blackbox.add_variable()` and
    :meth:`~da.p7core.blackbox.Blackbox.add_response()`.
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
    Enable saving blackbox evaluations.

    :param file_arg: write history to file
    :type file_arg: ``str`` or ``file``
    :param header: add header with the names of variables and responses to the history file
    :type header: ``bool``
    :param inmemory: store history in memory (default on)
    :type inmemory: ``bool``

    .. versionadded:: 1.11.0

    .. deprecated:: 4.0
       use :meth:`~da.p7core.blackbox.Blackbox.set_history()` instead.

    Since version 4.0, replaced by a more convenient
    :meth:`~da.p7core.blackbox.Blackbox.set_history()` method. See also
    :meth:`~da.p7core.blackbox.Blackbox.clear_history()` and
    :meth:`~da.p7core.blackbox.Blackbox.disable_history()`.

    """
    if not inmemory is None:
      self.set_history(memory=inmemory, file=file_arg, add_header=header)
    else:
      self.set_history(file=file_arg, add_header=header)

  def disable_history(self):
    """
    Disable saving blackbox evaluations completely.

    .. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

    *New in version 2.0 Release Candidate 1.*

    Disables both memory and file history. Evaluation results
    will no longer be stored in :attr:`~da.p7core.blackbox.Blackbox.history` or the
    configured history file (see *file* in :meth:`~da.p7core.blackbox.Blackbox.set_history()`).

    Disabling does not clear current contents of :attr:`~da.p7core.blackbox.Blackbox.history`
    (see :meth:`~da.p7core.blackbox.Blackbox.clear_history()`).

    """
    self.set_history(memory=False, file=None)

  def clear_history(self):
    """
    Clear :attr:`~da.p7core.blackbox.Blackbox.history`.

    .. versionadded:: 4.0

    Removes all evaluations currently stored in the memory history, but does not disable it.
    For disabling, see :meth:`~da.p7core.blackbox.Blackbox.disable_history()` or
    :meth:`~da.p7core.blackbox.Blackbox.set_history()`.

    """
    self._history_cache = []

  @property
  def history(self):
    """History of blackbox evaluations stored in memory.

    :Type: ``list[list[float]]``

    .. versionadded:: 1.11.0

    Stores values of variables and evaluation results.
    Each element of the top-level list is one evaluated point.
    Nested list structure is *[variables, responses gradients]*.
    Gradients are added only if analytical gradients are enabled,
    see :meth:`~da.p7core.blackbox.Blackbox.enable_gradients()`).

    .. note::

       Memory history is enabled by default, which increases memory consumption.
       If you implement your own way to save the history of evaluations,
       always use :meth:`~da.p7core.blackbox.Blackbox.disable_history()`.
       If there are a lot of evaluations in your problem, consider reconfiguring history
       to only write it to a file (see :meth:`~da.p7core.blackbox.Blackbox.set_history()`).

    """
    return self._history_cache


  def variables_names(self):
    """Get names of variables.

    :return: list of names
    :rtype: ``list[str]``

    Returns a list containing names of variables.
    All variables are named; if you do not set a name when adding a variable,
    a unique name is generated automatically (``x1``, ``x2`` and so on).
    """
    return [var.name for var in self._variables]

  def objectives_names(self):
    """Get names of responses.

    :return: list of names
    :rtype: ``list[str]``

    Returns a list containing names of responses.
    All responses are named; if you do not set a name when adding a response,
    a unique name is generated automatically (``f1``, ``f2`` and so on).
    """
    return [obj.name for obj in self._responses]

  def constraints_names(self):
    return []

  prepare_blackbox = _AbstractMethod()
  """
  The blackbox initialization method, has to be implemented by user.

  :return: ``None``

  This method is called automatically when creating an instance of the :class:`~da.p7core.blackbox.Blackbox` class, and should never be called directly.
  It is used to initialize blackbox variables and responses (see :meth:`~da.p7core.blackbox.Blackbox.add_variable()` and
  :meth:`~da.p7core.blackbox.Blackbox.add_response()`), enable analytical gradients (see :meth:`~da.p7core.blackbox.Blackbox.enable_gradients()`) and configure saving the history of evaluations (see :meth:`~da.p7core.blackbox.Blackbox.set_history()`).

  """

  evaluate = _AbstractMethod('iterable(iterable(float))')
  r"""
  The evaluation method, has to be implemented by user.

  :param points: points to evaluate
  :type points: ``ndarray``, 2D
  :return: evaluation results
  :rtype: :term:`array-like`, 2D

  .. versionadded:: 1.11.0
     gradients support.

  .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

  *Changed in version 3.0 Release Candidate 1:* :arg:`points` argument is ``ndarray``.

  When a blackbox-based method requests values from the blackbox, it sends a small sample to evaluate (a 2D ``ndarray``).
  The shape of this array is *(n, m)* where *n* is the number of points to evaluate and *m* is the input dimension.
  The blackbox has to initialize a correct number of input components --- see :meth:`~da.p7core.blackbox.Blackbox.add_variable()`.

  Entire :arg:`points` array is passed to :meth:`~da.p7core.blackbox.Blackbox.evaluate()` which has to process it
  and return function values (and gradients, if they were enabled in :meth:`~da.p7core.blackbox.Blackbox.prepare_blackbox()`).

  Return type has to be a 2D :term:`array-like`, ``ndarray`` is preferred.
  The shape of the return array depends on the selected gradient calculation method.

  If analytical gradients are not enabled (default), numerical differentiation is used automatically.
  In this case, for a function with *m* input and *k* output components, and *n* points to evaluate, the input and response structures are:

  * input: `[ [x_1, ..., x_m]_1, ..., [x_1, ..., x_m]_n ]`
  * output: `[ [f_1(\overline{x}_1), ..., f_k(\overline{x}_1)], ..., [f_1(\overline{x}_n), ..., f_k(\overline{x}_n)] ]`

  The blackbox has to initialize a correct number of output components --- see :meth:`~da.p7core.blackbox.Blackbox.add_response()`.
  The return array shape is *(n, k)*, and *k* is checked against :meth:`~da.p7core.blackbox.Blackbox.size_f()`.

  If analytical gradients are enabled (see :meth:`~da.p7core.blackbox.Blackbox.enable_gradients()`), gradient values
  should be appended to each evaluation result, in the selected order, which by default is F-major.
  Hence the output structure becomes (for the default F-major order):

    .. math::

       \begin{array}{c}
       \biggl [ \bigl [f_1(\overline{x}_1), ..., f_k(\overline{x}_1), \frac{\partial{f_1}}{\partial{x_1}}(\overline{x}_1), ..., \frac{\partial{f_1}}{\partial{x_m}}(\overline{x}_1), ..., \frac{\partial{f_k}}{\partial{x_1}}(\overline{x}_1), ..., \frac{\partial{f_k}}{\partial{x_m}}(\overline{x}_1) \bigr], \\
       ..., \\
       \bigl [f_1(\overline{x}_n), ..., f_k(\overline{x}_n), \frac{\partial{f_1}}{\partial{x_1}}(\overline{x}_n), ..., \frac{\partial{f_1}}{\partial{x_m}}(\overline{x}_n), ..., \frac{\partial{f_k}}{\partial{x_1}}(\overline{x}_n), ..., \frac{\partial{f_k}}{\partial{x_m}}(\overline{x}_n) \bigr ] \biggr]
       \end{array}

  In this case, the return array shape is *(n, s)*, where *s = k + mk*, and *s* is checked against :meth:`~da.p7core.blackbox.Blackbox.size_full()`.
  If it is not possible to calculate a gradient value, a NaN value should be added instead to preserve the output structure.
  When a NaN gradient value is encountered in output, gradient calculation falls back to numerical for the current input sample.

  Note that the return array is always 2D, even if there is only one response (scalar output) and gradients are not enabled.
  Never return a 1D :term:`array-like` (such as a flat ``list[float]``) from :meth:`~da.p7core.blackbox.Blackbox.evaluate()`.

  """
  def _evaluate(self, points):
    values = _shared.as_matrix(self.evaluate(points), shape=(len(points), self.size_full()), detect_none=True, name="response")

    if self._history_inmemory or self._history_file is not None:
      with _local_history_file(self._history_file) as hf:
        if self._header_required and not hf is None:
          hf.write(self._get_header() + "\n")
          self._header_required = False
        for points_i, values_i in zip(points, values):
          concat_row = [_ for _ in points_i] + values_i.tolist()
          if self._history_inmemory:
            self._history_cache.append(concat_row)
          if hf is not None:
            hf.write(','.join(('%.17g' % v) for v in concat_row))
            hf.write('\n')

    return values

@_contextlib.contextmanager
def _local_history_file(file_name):
  if file_name is None:
    yield None
  elif isinstance(file_name, string_types):
    fd = open(file_name, 'a+')
    try:
      yield fd
    finally:
      fd.close()
  else:
    yield file_name

class _SingleResponseCallbackWrapper(object):
  def __init__(self, blackbox, magic_sig):
    self.pending_error = None
    self.blackbox = blackbox
    self.size_x = blackbox.size_x()
    self.size_f = blackbox.size_f()
    self.magic_sig = magic_sig.value

  @staticmethod
  def _preprocess_vector(size, inc, name):
    if inc >= 1:
      return inc
    elif size == 1:
      return 1
    raise _ex.WrongUsageError("Invalid distance between elements of the %d-dim. vector %s: %s." % (size, name, inc))

  def __call__(self, x, incx, f, opaque, incf, grad, inc_df, inc_dx):
    msg_prefix = None

    try:
      if _ctypes.cast(opaque, _ctypes.c_void_p).value != self.magic_sig:
        _warn("Evaluation callback: Python stack corruption detected! Results may be unpredictable.", RuntimeWarning)

      if not f and not grad:
        return True

      if not x:
        raise _ex.WrongUsageError("NULL pointer to the x vector is given: %s." % (x,))

      incx = self._preprocess_vector(self.size_x, incx, "x")
      x_buf = _numpy.frombuffer(_ctypes.cast(x, _ctypes.POINTER(_ctypes.c_double * (incx * self.size_x))).contents).reshape(self.size_x, incx)

      msg_prefix = "an exception is raised inside blackbox 'evaluate(x=numpy.array(%s))' method - " % str(x_buf.shape)
      data = self.blackbox._evaluate(x_buf[:, 0].reshape(1, -1))
      msg_prefix = "an error occurred while processing blackbox response - "
      data = _numpy.array(data, copy=_shared._SHALLOW, dtype=_ctypes.c_double).reshape(self.blackbox.size_full())

      if f:
        incf = self._preprocess_vector(self.size_f, incf, "f")
        f_buf = _numpy.frombuffer(_ctypes.cast(f, _ctypes.POINTER(_ctypes.c_double * (incf * self.size_f))).contents).reshape(self.size_f, incf)
        f_buf[:, 0] = data[:self.size_f]

      if grad:
        if not self.blackbox.gradients_enabled:
          data_grad = _numpy.tile(_numpy.nan, (self.size_f, self.size_x))
        elif self.blackbox.gradients_order == GTIBB_GRADIENT_F_ORDER:
          data_grad = data[self.size_f:].reshape(self.size_f, self.size_x)
        else:
          data_grad = data[self.size_f:].reshape(self.size_x, self.size_f).T

        inc_dx = self._preprocess_vector(self.size_x, inc_dx, "dx")
        inc_df = self._preprocess_vector(self.size_f, inc_df, "df")
        lead_df, lead_dx  = inc_df * self.size_f, inc_dx * self.size_x
        grad_buf = _numpy.frombuffer(_ctypes.cast(grad, _ctypes.POINTER(_ctypes.c_double * max(lead_df, lead_dx))).contents)

        if lead_dx == inc_df:
          grad_buf = grad_buf.reshape(self.size_f, lead_dx)
          grad_buf[:,::inc_dx] = data_grad[:]
        elif lead_df == inc_dx:
          grad_buf = grad_buf.reshape(self.size_x, lead_df).T
          grad_buf[::inc_df, :] = data_grad[:]
        else:
          for i, df in enumerate(data_grad):
            grad_buf[i*inc_df:i*inc_df+inc_dx*self.size_x:inc_dx] = df[:]

      return True
    except:
      exc_info = sys.exc_info()
      if msg_prefix:
        exc_info = exc_info[0], exc_info[0](msg_prefix + _shared._safestr(exc_info[1])), exc_info[2]

      if exc_info[1] is not None and (self.pending_error is None or (isinstance(self.pending_error[1], Exception) and not isinstance(exc_info[1], Exception))):
        exc_type = _ex.UserEvaluateException if isinstance(exc_info[1], Exception) else exc_info[0]
        self.pending_error = (exc_type, exc_info[1], exc_info[2])

    return False

  def flush_callback_exception(self):
    if self.pending_error is not None:
      exc_type, exc_val, exc_tb = self.pending_error
      self.pending_error = None
      _shared.reraise(exc_type, exc_val, exc_tb)

@_contextlib.contextmanager
def blackbox_callback(blackbox, response_callback_type):
  magic_sig = _ctypes.c_void_p(0xAACC00FF)
  if blackbox is None:
    yield (response_callback_type(), magic_sig)
  else:
    response_callback = _SingleResponseCallbackWrapper(blackbox, magic_sig)
    yield (response_callback_type(response_callback), magic_sig)
    response_callback.flush_callback_exception()
