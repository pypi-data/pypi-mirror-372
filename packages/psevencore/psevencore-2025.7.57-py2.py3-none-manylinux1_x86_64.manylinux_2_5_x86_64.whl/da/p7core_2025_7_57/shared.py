#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Array utilites (with numpy support)."""
from __future__ import with_statement
from __future__ import division

import os as _os
import sys as _sys
import re
import ctypes
import math
import traceback as _traceback
import itertools as _itertools
import numpy as _numpy
import warnings as _warnings
import unicodedata
import weakref as _weakref
import contextlib as _contextlib
import signal as _signal

from .FindNative import _library, _library_welcome_message

from . import six as _six
from . import loggers as _loggers
from . import exceptions as _ex
from . import status as _status

# For backward compatibility, copy _safe_pickle_dump and _safe_pickle_load to this module namespace
from .safe_pickle import _safe_pickle_dump, _safe_pickle_load

try:
  long_integer = long
except NameError:
  long_integer = int

try:
  import pandas as _pandas
except ImportError:
  _pandas = None

try:
  _ = _numpy.array((1,2), copy=False)
  _SHALLOW = False # Old-fashioned Numpy copy mode.
except:
  _SHALLOW = None # Modern Numpy copy mode.

if isinstance((ctypes.c_char*1)().value, str):
  char2str = str
else:
  def char2str(ascii_string):
    return ascii_string if isinstance(ascii_string, str) else str(ascii_string.decode('ascii'))

def _safestr(x):
  if _six.PY2:
    return _six.text_type(x).encode("unicode_escape")
  return str(x)

class _API(object):
  def __init__(self):
    self.__library = _library

    self.get_error_message = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_void_p))(("GTErrorDescriptionGetMessage", self.__library))
    self.get_error_code = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_void_p))(("GTErrorDescriptionGetErrorCode", self.__library))
    self.release_error = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p)(("GTErrorDescriptionFree", self.__library))

    self.get_hole_marker = ctypes.CFUNCTYPE(ctypes.c_double)(("GTOptSolverHoleMarker", self.__library))
    self.is_hole_marker = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_double)(("GTOptSolverCompareHoleMarker", self.__library))
    self.is_batch_hole_marker = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
                                 ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_size_t), ctypes.c_void_p)(("GTOptSolverCompareBatchHoleMarker", self.__library)) # ndim, shape, in_strides, in_pointer, out_strides, out_pointer
    
    self.is_desktop_mode = ctypes.CFUNCTYPE(ctypes.c_short)(("GTOptDesktopCompatibleMode", self.__library))

    self.lexsort = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
                                 ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int32), ctypes.c_size_t)(("GTOptSolverLexSortMatrix2", self.__library)) # ndim, shape, strides, pointer, out_pointer, out_step (in bytes)

  @property
  def _library(self):
    return self.__library

_api = _API()

def _desktop_mode(backend=_api):
  return backend.is_desktop_mode() != 0

def _release_error_message(backend_errdesc, backend=_api):
  exc_type, message = None, ""

  try:
    if backend_errdesc and backend_errdesc.value:
      exc_type = _ex.GTException

      size = ctypes.c_size_t()
      error_code = backend.get_error_message(backend_errdesc, ctypes.c_char_p(), ctypes.byref(size), ctypes.c_void_p())
      if error_code != 0:
        info = (ctypes.c_char * size.value)()
        error_code = backend.get_error_message(backend_errdesc, info, ctypes.byref(size), ctypes.c_void_p())
        if error_code != 0:
          message = _preprocess_utf8(info.value)
      status_id = ctypes.c_short()
      error_code = backend.get_error_code(backend_errdesc, ctypes.byref(status_id), ctypes.c_void_p())
      backend.release_error(backend_errdesc)

      if error_code != 0:
        exc_type = _status.exception_by_status_id(status_id.value)
  except:
    pass

  return exc_type, message

def _raise_on_error(succeeded, message_prefix, backend_errdesc, backend=_api):
  # intentionally assign single shared _api object as default value so we keep backend loaded as long as this method exists
  if succeeded:
    return

  exc_type, message = _release_error_message(backend_errdesc, backend)

  try:
    if message_prefix:
      message = (message_prefix + "\nError details: " + message) if message else message_prefix
  except:
    pass

  if not message:
    message = "Internal algorithmic error occurred: no particular reason given"

  raise (exc_type or ValueError)(message)

class ModelStatus:
  @staticmethod
  def checkErrorCode(err, message, errdesc, backend=_api):
    # intentionally assign single shared _api object as default value so we keep backend loaded as long as this method exists
    if not err:
      exc_type, message = _release_error_message(errdesc, backend)
      if exc_type is None:
        exc_type = _ex.GTException
      raise exc_type(message or 'Internal error')

_has_numpy = True

def is_numpy_array(obj):
  return isinstance(obj, _numpy.ndarray)

try:
  from collections import Iterable as _Iterable
  def is_iterable(obj):
    return isinstance(obj, _Iterable)
except (ImportError, AttributeError):
  def is_iterable(obj):
    try:
      it = iter(obj)
      return True
    except TypeError:
      return False

try:
  from collections import Sized as _Sized
  def is_sized(obj):
    return isinstance(obj, _Sized)
except (ImportError, AttributeError):
  def is_sized(obj):
    return hasattr(obj, '__len__')

try:
  from collections import Mapping as _Mapping
  def is_mapping(obj):
    return isinstance(obj, _Mapping)
except (ImportError, AttributeError):
  def is_mapping(obj):
    for define in ['__getitem__', '__contains__', 'keys', 'items', 'values']:
      if not hasattr(obj, define):
        return False
    return True

try:
  from collections import Set as _Set
  def is_set(obj):
    return isinstance(obj, _Set)
except (ImportError, AttributeError):
  def is_set(obj):
    if not is_iterable(obj):
      return False
    for define in ("__contains__", "__len__", "__le__", "__lt__", "__eq__", "__ne__", "__gt__", "__ge__", "__and__", "__or__", "__sub__", "__xor__", "isdisjoint"):
      if not hasattr(obj, define):
        return False
    return True

def safe_concat(*args):
  """
  for concatenating different iterables
  """
  return list(_itertools.chain(*args))

def _cartesian_product(*args, **kwds):
  pools = [tuple(_) for _ in args] * kwds.get('repeat', 1)
  result = [[]]
  for pool in pools:
    result = [x+[y] for x in result for y in pool]
  for prod in result:
    yield tuple(prod)

def product(*args, **kwds):
  try:
    return _itertools.product(*args, **kwds)
  except AttributeError:
    pass
  return _cartesian_product(*args, **kwds)

def get_size(obj):
  return len(obj) if is_sized(obj) else 1

def get_ndim(obj):
  if isinstance(obj, _numpy.ndarray):
    return obj.ndim
  ndim = 0
  try:
    while is_iterable(obj):
      obj = _six.next(iter(obj))
      ndim = ndim + 1
  except StopIteration:
    pass
  return ndim

def fsum(iterable):
  try:
    return math.fsum(iterable)
  except AttributeError:
    return _numpy.sum(iterable)

def check_args(set_args, unset_args):
  """
  check whether all of set_args is set (i.e. is not None) and all of unset_args is unset (i.e. is None)
  """
  return all(arg is not None for arg in set_args)\
     and all(arg is None for arg in unset_args)

class ArrayPtr:
  """Incapsulates ctypes pointer to array together with its lead dimension / increment."""

  def __init__(self, ptr, ld, array=None):
    """
    ptr - ctypes pointer to array (vector/matrix)
    ld - lead dimension for matrix (or increment for vectors)
    array - optional reference to array object
    """
    self.ptr = ptr
    self.ld = ctypes.c_size_t(ld)
    self.inc = ctypes.c_size_t(ld) # just alias
    self.array = array

  def vector(self, index):
    assert index >= 0, ("Negative index=%s is not allowed!" % (index,))
    address = ctypes.addressof(self.ptr.contents) + self.ld.value * index * ctypes.sizeof(self.ptr.contents)
    return ctypes.pointer(type(self.ptr.contents).from_address(address))

def __check_none(data, index):
  return __check_none(data[index[0]], index[1:]) if index else (data is None)

def as_matrix(array, shape=(None, None), dtype=float, ret_is_vector=False, order=None, detect_none=False, name=None, copy=None):
  """Optionally convert array to the numpy array with requested characteristics.

  :param array: - original data
  :param shape: - tuple of requested array dimensions. Use None or negative integer if the respective axis may have any length.
  :param dtype: - the desired data-type for the array
  :param ret_is_vector: - indicates whether to return array and "array is vector" indicator or array only
  :param order: - {'C', 'F', 'A'} specify the order of the array. Equivalent to the ``order`` property of the ``numpy.ndarray``.
  :param detect_none: - convert None elements of the original array to special ``_NONE`` indicator
  :param name: - array identifier for the exception messages
  :param copy: - force to make a copy of array
  :type array: :term:`array-like`, 1D or 2D
  :type shape: ``tuple``
  :type dtype: data-type
  :type ret_is_vector: ``bool``
  :type order: ``str``
  :type detect_none: ``bool``
  :type name: ``str``
  :type copy: ``bool``
  :return: tuple converted array and boolean vector indicator if ret_is_vector is True, otherwise returns array only.
  :rtype: ``tuple`` or :class:`_numpy.array`

  If the original array meets all requirements then it will be retured as-is.
  """
  if not name:
    name = "input argument"

  if array is None:
    raise TypeError("%s is 'None' and cannot be converted to a matrix" % name)

  n_rows, n_cols = (None, None) if shape is None else shape

  # normalize matrix dimensions
  if n_cols is not None:
    check_concept_int(n_cols, "the number of %s columns" % name)
    n_cols = int(n_cols)
    if n_cols < 0:
      n_cols = None # use numpy reshape syntax

  if n_rows is not None:
    check_concept_int(n_rows, "the number of %s rows" % name)
    n_rows = int(n_rows)
    if n_rows < 0:
      n_rows = None # use numpy reshape syntax

  if order is None:
    order = 'C'

  original_array = array

  try:
    array = _numpy.array(array, dtype=dtype, order=order, copy=(copy or _SHALLOW))
  except:
    exc_info = _sys.exc_info()
    reraise(TypeError, ("%s cannot be interpreted as a matrix of %s values: %s" % (name, dtype, exc_info[1])), exc_info[2])

  is_vector = array.ndim < 2

  def report_invalid_shape(array, m, n):
    raise ValueError("%s is %s-dimensional array and cannot be reshaped into %s-by-%s dimensional matrix!" % \
        (name, str(array.shape), (m if m is not None else "m"), (n if n is not None else "n")))

  if 0 == array.ndim:
    if n_cols is not None and 1 != n_cols:
      report_invalid_shape(array, n_rows, n_cols)
    array = array.reshape((1,1), order=order)
  elif 1 == array.ndim:
    # We've got a vector. May it be treated as a single column or single row matrix?
    if 1 == n_cols or (n_cols is None and n_rows == array.shape[0]):
      # treat as a single column matrix
      array = array.reshape((-1, 1), order=order)
      is_vector = array.shape[0] < 2
    elif 1 == n_rows or (n_rows is None and n_cols == array.shape[0]):
      # treat as a single row matrix
      array = array.reshape((1, -1), order=order)
    elif n_cols is None and n_rows is None:
      # treat as a single column matrix but keep is_vector=True
      array = array.reshape((-1, 1), order=order)
    else:
      # We've got size or vectors number but neither of them match the vector given
      report_invalid_shape(array, n_rows, n_cols)
  elif 2 != array.ndim \
    or (n_rows is not None and array.shape[0] != n_rows) \
    or (n_cols is not None and array.shape[1] != n_cols):
    # Check that we've got a n_rows-by-n_cols dimensional matrix
    report_invalid_shape(array, n_rows, n_cols)

  if detect_none:
    array = __postprocess_holes(original_array, array)

  return (array, is_vector) if ret_is_vector else array

def _emit_names_warn(column_names, variable_names):
  if column_names != variable_names:
    message = ''
    for i, (c_name, v_name) in enumerate(zip(column_names, variable_names)):
      if c_name != v_name:
        message += "\n Inconsistent column name '%s' for variable #%d with name '%s'" % (c_name, i, v_name)
    _warnings.warn(message)


def _test_pandas_dataframe(sample, variable_names):
  column_names = [_ for _ in sample.columns]
  if variable_names and any(a != b for a, b in zip(column_names, range(len(column_names)))):
    _emit_names_warn([_six.text_type(_preprocess_utf8(_)) for _ in column_names], variable_names)

  return sample.index, _pandas.DataFrame


def _test_pandas_series(sample, single_vector, variable_names):
  if single_vector:
    column_names = [_ for _ in sample.index]
  elif sample.name is None:
    return [_ for _ in sample.index], _pandas.Series
  else:
    column_names = [sample.name]

  if variable_names and any(a != b for a, b in zip(column_names, range(len(column_names)))):
    _emit_names_warn([_six.text_type(_preprocess_utf8(_)) for _ in column_names], variable_names)

  return (sample.name if single_vector else [_ for _ in sample.index]), _pandas.Series


def _read_dataframe_names(sample):
  column_names = [_ for _ in sample.columns]
  # Note pd.DataFrame([[7,2,3]]).columns is just a useless range(3)
  if any(a != b for a, b in zip(column_names, range(len(column_names)))):
    return [_six.text_type(_preprocess_utf8(_)) for _ in column_names]
  return None


def _read_series_names(sample):
  if len(_numpy.shape(sample)) == 1 and sample.name is not None:
    return [_six.text_type(_preprocess_utf8(sample.name))]
  return None

def get_pandas_info(sample, single_vector, variable_names=None):
  if _pandas is None:
    return None, None

  try:
    return _test_pandas_dataframe(sample, variable_names)
  except:
    pass

  try:
    return _test_pandas_series(sample, single_vector, variable_names)
  except:
    pass

  return None, None

def make_pandas(sample, single_vector, pandas_type, pandas_index, variable_names):
  if _pandas is None:
    return sample

  try:
    if isinstance(sample, pandas_type) or pandas_type not in [_pandas.Series, _pandas.DataFrame]:
      return sample

    if pandas_type == _pandas.Series:
      if single_vector:
        return _pandas.Series(sample[0], index=variable_names, name=pandas_index)
      elif sample.shape[1] == 1:
        return _pandas.Series(sample[:, 0], index=pandas_index, name=variable_names[0])

    return _pandas.DataFrame(sample, columns=variable_names, index=pandas_index)
  except:
    return sample

def make_pandas_grad(sample, single_vector, pandas_type, pandas_index, major_names, minor_names):
  if _pandas is None:
    return sample

  try:
    if isinstance(sample, pandas_type) or pandas_type not in [_pandas.Series, _pandas.DataFrame]:
      return sample

    if single_vector:
      return _pandas.DataFrame(sample[0], index=major_names, columns=minor_names)

    index = _pandas.MultiIndex.from_product((pandas_index, major_names))
    return _pandas.DataFrame(sample.reshape(-1, sample.shape[-1]), index=index, columns=minor_names)

  except:
    return sample

def make_pandas_pe(sample, single_vector, pandas_type, pandas_index, pe_names):
  if _pandas is None:
    return sample

  try:
    if isinstance(sample, pandas_type) or pandas_type not in [_pandas.Series, _pandas.DataFrame]:
      return sample

    sample = _pandas.DataFrame(sample.reshape(-1, sample.shape[-1]), index=pandas_index, columns=_pandas.MultiIndex.from_tuples(pe_names))
    return sample.iloc[0] if single_vector else sample

  except:
    return sample

def convertToMatrix(array, vectorSize=None, vectorsNumber=None, dataType=_numpy.float64, checkSingleVectorMode=False, allowSparseColumns=False, detect_none=False, name=None):
  return as_matrix(array, shape=(vectorsNumber, vectorSize), dtype=dataType, ret_is_vector=checkSingleVectorMode, order=('A' if allowSparseColumns else 'C'), detect_none=detect_none, name=name)

def py_matrix_2c(vectors, vecSize=None, checkSingleVectorMode=False, datatype=ctypes.c_double, name=None):
  """
  return ArrayPtr encapsulated pointer to matrix data as ctypes.POINTER(ctypes.c_double) and lead dimension as ctypes.c_size_t
  vectors - :term:`array-like` (1d or 2d)
  vecSize - vector size
  """
  matrix, is_vector = as_matrix(vectors, shape=(None, vecSize), dtype=datatype, ret_is_vector=True, name=name)
  arrayPtr = ArrayPtr(matrix.ctypes.data_as(ctypes.POINTER(datatype)), matrix.strides[0] // matrix.itemsize, matrix)
  return (arrayPtr, is_vector) if checkSingleVectorMode else arrayPtr

def py_vector_2c(vector, vecSize=None, datatype=ctypes.c_double, name=None):
  """
  return ArrayPtr encapsulated pointer to vector data as ctypes.POINTER(datatype) and increment as ctypes.c_size_t
  :param vector: - array_like list, or 1d _numpy.array
  :param vecSize: - expected vector size (if known)
  :param datatype: one of ctypes datatype (c_double, c_short, c_size_t, etc.)
  """
  matrix = as_matrix(vector, shape=(None, vecSize), dtype=datatype, ret_is_vector=False, name=name)
  if 1 != matrix.shape[1]:
    if 1 == matrix.shape[0]:
      matrix = matrix.reshape((matrix.shape[1],))
    else:
      raise ValueError("Can't convert to vector the %s-dimensional array given!" % (matrix.shape,))
  return ArrayPtr(matrix.ctypes.data_as(ctypes.POINTER(datatype)), matrix.strides[0] // matrix.itemsize, matrix)

def check_type(value, name, types):
  if not isinstance(value, types):
    if not is_iterable(types):
      typestr = types.__name__
    else:
      typestr = ', '.join([t.__name__ for t in types])
    raise TypeError('Wrong %s type %s! Required: %s' % (name, type(value).__name__, typestr))

def check_concept_sequence(value, name):
  if not (hasattr(value, "__getitem__") and hasattr(value, "__iter__") and hasattr(value, "__len__")):
    raise TypeError('Wrong %s type %s! Required: sequence' % (name, type(value).__name__))
  try:
    value[:]
  except TypeError:
      exc_info = _sys.exc_info()
      reraise(TypeError, 'Wrong %s type %s! Required: sequence' % (name, type(value).__name__), exc_info[2])

def is_numerical(value):
  try:
    # Some strings can be converted to floats but the string is not a numeric type
    if isinstance(value, _six.string_types):
      return False
    _ = float(value)
    return True
  except ValueError:
    pass
  return False

def is_integer(value):
  try:
    if int(value) == float(value):
      return True
  except ValueError:
    pass
  except TypeError:
    pass
  return False

def check_concept_int(value, name):
  if not is_integer(value):
    raise TypeError('Wrong %s type %s! Required: integer' % (name, type(value).__name__))

def check_concept_numeric(value, name):
  if not is_numerical(value):
    raise TypeError('Wrong %s type %s! Required: numeric' % (name, type(value).__name__))

def check_concept_dict(value, name):
  if not (hasattr(value, "__getitem__") and hasattr(value, "__iter__") and hasattr(value, "__len__")):
    raise TypeError('Wrong %s type %s! Required: dict' % (name, type(value).__name__))
  try:
    value[""]
  except KeyError:
    pass
  except:
    exc_info = _sys.exc_info()
    reraise(TypeError, 'Wrong %s type %s! Required: dict' % (name, type(value).__name__), exc_info[2])

def __collect_metainfo(user_meta, direction, size, origin):
  """Collects metainfo according to user-defined descriptions with minimum of checks.

  :param user_meta: - variables description
  :param direction: - "input" or "ouput" variables are described
  :param size: - number of variables
  """
  default_name = 'x[%s]' if direction == 'input' else 'f[%s]'
  metainfo = [{} for i in range(size)]

  if origin and len(origin) == size:
    keys_list = valid_metainfo_keys()
    for i, info in enumerate(origin):
      metainfo[i].update(dict((key, info[key]) for key in info if key in keys_list))
      if 'labels' not in info or 'enumerators' not in info: # both or none
        metainfo[i].pop('labels', None)
        metainfo[i].pop('enumerators', None)

  for i, info in enumerate(metainfo):
    info.setdefault("name", (default_name % i))

  # Check type, if None or empty list return default metainfo
  if user_meta is None:
    return metainfo
  elif is_iterable(user_meta) and not isinstance(user_meta, _six.string_types) \
       and not is_mapping(user_meta) and not is_set(user_meta):
    user_meta = tuple(_ for _ in user_meta)
    if not user_meta:
      return metainfo
    elif len(user_meta) != size:
      raise ValueError('Length of the %ss meta description does not match the number of %ss: %d != %d' %
                       (direction, direction, len(user_meta), size))
    # Update elements of metainfo vector
    for i, var_meta in enumerate(user_meta):
      # Metainfo element can be string, dictionary or none
      if isinstance(var_meta, _six.string_types):
        metainfo[i]['name'] = var_meta
      elif var_meta is not None:
        try:
          var_meta.pop('labels', None)
          metainfo[i].update(var_meta)
        except:
          tb = _sys.exc_info()[2]
          reraise(TypeError, 'Description of the %s component #%d must be None, string or dict: \'%s\' is given' %
                             (direction, i, getattr(type(var_meta), '__name__', str(type(var_meta)))), tb)
    return metainfo
  else:
    raise TypeError('Wrong %ss meta description type \'%s\': iterable over strings or mappings is required.' % (direction, type(user_meta).__name__))

def valid_metainfo_keys():
  return {'name': None,
          'description': None,
          'quantity': None,
          'unit': None,
          'labels': list,
          'enumerators': list,
          'min': float,
          'max': float}

def collect_metainfo_keys(metainfo):
  keys = set()
  for section in ('Input Variables', 'Output Variables'):
    for var_metainfo in metainfo.get(section, []):
      keys.update(k for k in var_metainfo)
  return keys

def _n_columns(sample):
  shape = _numpy.shape(sample)
  return 1 if len(shape) < 2 else shape[-1]

def create_metainfo_template(x, y, model=None, options=None, log=None):
  template, key_x, key_y = {}, "Input Variables", "Output Variables"
  categorical_dtypes = ['category', 'object', 'string', 'bool']

  if log:
    log(_loggers.LogLevel.DEBUG, "Preparing metainfo template...")

  if model is not None:
    for key in (key_x, key_y):
      try:
        template[key] = [_.copy() for _ in model.details[key]] # make deeper copy to avoid modification of the initial model
        if log:
          log(_loggers.LogLevel.DEBUG, "Using as a template metainfo for %s from the initial model: %s" % (key.lower(), template[key]))
      except:
        pass

  if key_x not in template:
    try:
      template[key_x] = [{"name": _safestr(_)} for _ in _read_dataframe_names(x)]
    except:
      pass

  if key_x not in template:
    try:
      template[key_x] = [{"name": _safestr(_)} for _ in _read_series_names(x)]
      # promote series to dataframe to simplify types test
      x = _pandas.DataFrame(x)
    except:
      pass

  if log and key_x in template:
    log(_loggers.LogLevel.DEBUG, "Using column names of the dataframe to set the names of %s: %s"
                                    % (key_x.lower(), ", ".join([_["name"] for _ in template[key_x]])))

  if key_y not in template:
    try:
      template[key_y] = [{"name": _safestr(_)} for _ in _read_dataframe_names(y)]
    except:
      pass

  if key_y not in template:
    try:
      template[key_y] = [{"name": _safestr(_)} for _ in _read_series_names(y)]
      # promote series to dataframe to simplify types test
      y = _pandas.DataFrame(y)
    except:
      pass

  if log and key_y in template:
    log(_loggers.LogLevel.DEBUG, "Using column names of the dataframe to set the names of %s: %s"
                                    % (key_y.lower(), ", ".join([_["name"] for _ in template[key_y]])))


  def ordinal_encoding(labels, initial_enumerators):
    enumerators = [_ for _ in initial_enumerators]
    unique_enumerator = 0
    for new_label in labels[len(initial_enumerators):]:
      while unique_enumerator in enumerators:
        unique_enumerator += 1
      enumerators.append(unique_enumerator)
    return enumerators

  def numerical_encoding(labels, initial_enumerators):
    enumerators = [_ for _ in initial_enumerators]
    unique_enumerator = 0.0
    for new_label in labels[len(initial_enumerators):]:
      try:
        new_enum = float(new_label)
      except ValueError:
        new_enum = None

      if new_enum is None or new_enum in enumerators:
        while unique_enumerator in enumerators:
          unique_enumerator += 1.0
        enumerators.append(unique_enumerator)
      else:
        enumerators.append(new_enum)

    return enumerators

  if options is not None:
    categorical_x_indices = [int(_) for _ in parse_json(options.get('GTApprox/CategoricalVariables', '[]'))]
    try:
      categorical_columns = [_ for _, dtype in enumerate(x.dtypes) if dtype.name in categorical_dtypes and _ not in categorical_x_indices]
      categorical_x_indices += categorical_columns
      if log and categorical_columns:
        log(_loggers.LogLevel.DEBUG, "Setting categorical %s according to the column types of dataframe: %s"
                                                  % (key_x.lower(), ", ".join([_safestr(_) for _ in categorical_columns])))
    except:
      pass

    categorical_y_indices = [int(_) for _ in parse_json(options.get('GTApprox/CategoricalOutputs', '[]'))]
    try:
      categorical_columns = [_ for _, dtype in enumerate(y.dtypes) if dtype.name in categorical_dtypes and _ not in categorical_y_indices]
      categorical_y_indices += categorical_columns
      if log and categorical_columns:
        log(_loggers.LogLevel.DEBUG, "Setting categorical %s according to the column types of pandas dataframe: %s"
                                                  % (key_y.lower(), ", ".join([_safestr(_) for _ in categorical_columns])))
    except:
      pass

    categorical_x_map = collect_categorical_map(x, sorted(categorical_x_indices), 'input', model and model._categorical_x_map)
    for i, (dtype, labels, initial_enumerators) in _six.iteritems(categorical_x_map):
      template.setdefault(key_x, [{} for _ in range(_n_columns(x))])[i].update({
        'variability': 'enumeration',
        'labels': labels,
        'enumerators': labels if _numpy.issubdtype(dtype, _numpy.float64) else numerical_encoding(labels, initial_enumerators),
      })
    if log and not categorical_x_indices and categorical_x_map:
      categorical_x_from_model = [template[key_x][i].get('name', '#'+str(i+1)) for i in categorical_x_map]
      log(_loggers.LogLevel.INFO, "The type of input variable%s %s is set to categorical in accordance with the initial model."
                                                % (("s" if len(categorical_x_from_model) > 1 else ""), ", ".join(categorical_x_from_model)))

    categorical_y_map = collect_categorical_map(y, sorted(categorical_y_indices), 'output', model and model._categorical_f_map)
    for i, (dtype, labels, initial_enumerators) in _six.iteritems(categorical_y_map):
      template.setdefault(key_y, [{} for _ in range(_n_columns(y))])[i].update({
        'variability': 'enumeration',
        'labels': labels,
        'enumerators': ordinal_encoding(labels, initial_enumerators),
      })
    if log and not categorical_y_indices and categorical_y_map:
      categorical_y_from_model = [template[key_y][i].get('name', '#'+str(i+1)) for i in categorical_y_map]
      log(_loggers.LogLevel.INFO, "The type of output%s %s is set to categorical in accordance with the initial model."
                                                % (("s" if len(categorical_y_from_model) > 1 else ""), ", ".join(categorical_y_from_model)))

  return template

def preprocess_metainfo(inputs_meta, outputs_meta, inputs_size, outputs_size, template=None, ignorable_keys=None):
  """Check correctness of user-defined metainfo.

  :param inputs_meta: - input variables description
  :param outputs_meta: - output variables are described
  :param inputs_size: - number of input variables
  :param outputs_size: - number of output variables
  :param template: - model to read meta-info from if related key not in inputs_meta/outputs_meta
  :param ignorable_keys: - list of invalid keys that should be ignored instead of raising exception
  :param categorical_output_labels: - dictionary with categorical output indices as keys and corresponding labels

  """
  meta_keys = valid_metainfo_keys()
  if not ignorable_keys:
    ignorable_keys = tuple()

  try:
    x_origin = [_ for _ in template["Input Variables"]]
  except:
    x_origin = None

  try:
    y_origin = [_ for _ in template["Output Variables"]]
  except:
    y_origin = None


  metainfo = {}
  metainfo['Input Variables'] = __collect_metainfo(inputs_meta, 'input', inputs_size, x_origin)
  metainfo['Output Variables'] = __collect_metainfo(outputs_meta, 'output', outputs_size, y_origin)

  unique_names = {}
  for direction in metainfo:
    for i, var_meta in enumerate(metainfo[direction]):
      direction = direction.split(' ')[0].lower()
      var_spec = '%s component #%d' % (direction, i)

      # Check keys and types of the metainfo dictionary elements
      remove_keys = []
      for key in var_meta:
        if key not in meta_keys:
          if key not in ignorable_keys:
            raise ValueError('Description of the %s contains unknown key: \'%s\'' % (var_spec, key))
          else:
            remove_keys.append(key)
            continue

        if var_meta[key] is None:
          remove_keys.append(key)
          continue

        try:
          if meta_keys[key] is not None:
            var_meta[key] = meta_keys[key](var_meta[key]) # try to convert
          elif not isinstance(var_meta[key], _six.string_types):
            var_meta[key] = _safestr(var_meta[key]) # try to convert

          if isinstance(var_meta[key], str):
            var_meta[key] = _preprocess_utf8(var_meta[key].strip() if key.lower() in ("quantity", "unit") else var_meta[key])
        except:
          tb = _sys.exc_info()[2]
          key_type = 'None' if var_meta[key] is None else getattr(type(var_meta[key]), '__name__', _safestr(type(var_meta[key])))
          reraise(TypeError, ('The \'%s\' parameter of the %s description must be convertable to %s: \'%s\' is given' %
                          (key, var_spec, getattr(meta_keys[key], '__name__', _safestr(meta_keys[key])), key_type)), tb)

      for key in remove_keys:
        var_meta.pop(key, None)

      for label_idx, label in enumerate(var_meta.get('labels', [])):
        if isinstance(label, _six.string_types):
          label = _preprocess_utf8(label)
          # prohibit empty labels
          if not label:
            raise ValueError('Invalid label of %s: label cannot be empty' % var_spec)
          # in Core, label is already Unicode at this point
          for c in label:
            # prohibit Unicode control chars and separators
            if unicodedata.category(c) in ('Cc', 'Cf', 'Cn', 'Co', 'Cs', 'Zl', 'Zp'):
              raise ValueError('Invalid label of %s: label cannot contain control and special characters' % var_spec)
            # prohibit all whitespaces except ASCII space
            #if (c.isspace() or unicodedata.category(c) == 'Zs') and c != ' ':
            #  raise ValueError('Invalid label of %s: label cannot contain whitespace characters except ASCII space' % var_spec)
          var_meta['labels'][label_idx] = label

      # Check name correctness
      name = var_meta['name']
      # prohibit empty names
      if not name:
        raise ValueError('Invalid name of %s: name cannot be empty' % var_spec)
      # in Core, name is already Unicode at this point
      for c in name:
        # prohibit Unicode control chars and separators
        if unicodedata.category(c) in ('Cc', 'Cf', 'Cn', 'Co', 'Cs', 'Zl', 'Zp'):
          raise ValueError('Invalid name of %s: name cannot contain control and special characters' % var_spec)
        # prohibit all whitespaces except ASCII space
        if (c.isspace() or unicodedata.category(c) == 'Zs') and c != ' ':
          raise ValueError('Invalid name of %s: name cannot contain whitespace characters except ASCII space' % var_spec)
        # prohibit chars that are prohibited in Windows file names, but allow < and >
        if c in r':"/\|?*':
          raise ValueError('Invalid name of %s: name cannot contain the "%s" character' % (var_spec, c))
      # check for leading/trailing ASCII space
      if name.strip() != name:
        raise ValueError('Invalid name of %s: name cannot start or end with a space' % var_spec)
      # prohibit leading/trailing dot
      if name[0] == '.' or name[-1] == '.':
        raise ValueError('Invalid name of %s: name cannot start or end with a dot' % var_spec)
      # prohibit 2+ dots, since dot is a name separator
      if '..' in name:
        raise ValueError('Invalid name of %s: name cannot contain consecutive dots' % var_spec)
      # prohibit leading/trailing spaces in parts of a dot-separated name
      if '. ' in name or ' .' in name:
        raise ValueError('Invalid name of %s: space cannot precede or follow a dot' % var_spec)
      # prohibit 2+ spaces just because we can
      if '  ' in name:
        raise ValueError('Invalid name of %s: name cannot contain consecutive spaces' % var_spec)

      # Check uniqueness of the element name
      if name not in unique_names:
        unique_names[name] = var_spec
      else:
        message = 'Duplicate name \"%s\" is detected for the model %s and %s' % (name, unique_names[name], var_spec)
        _raise_unicode_exception(ValueError, message)
  return metainfo

def make_prefix(id):
  return ("%s >>> " % id) if id else ""

def parse_building_issues(build_log, default_key='[general]'):
  if not build_log:
    return {}

  issues = {}
  depth_change = {'[': 1, ']': -1}
  for warn_line in (line for line in build_log.split('\n') if line.strip().startswith('[w]')):
    if " >>> " in warn_line:
      # modern mode
      key, warn_line = warn_line.split(" >>> ", 1)
    else:
      # compatibility mode
      key, warn_line = default_key, warn_line[3:].strip()
      level = 0
      for i, c in enumerate(warn_line):
        level += depth_change.get(c, 0)
        if not level:
          if c == "]":
            key = warn_line[:(i + 1)]
            warn_line = warn_line[(i + 1):]
          break

    key = key.strip()
    if key.startswith('[w]'):
      key = key[3:].strip()
    warn_line = warn_line.strip()
    if warn_line: # and warn_line not in issues.get(key, [])
      issues.setdefault(key, []).append(warn_line)
  return issues

def _raise_unicode_exception(exception, unicode_message):
  """
  Method for raising errors with unicode messages
  ValueError(unicode_message) fails in python 2
  """
  if isinstance(unicode_message, str):
    raise exception(unicode_message)
  else:
    raise exception(unicode_message.encode('utf-8'))


def get_labels_type(labels, direction, variable_index, validate):
  try:
    _numpy.array(labels, dtype=float)
    return float
  except:
    pass

  if validate:
    try:
      valid_types = (_numpy.number, _numpy.bool_, _numpy.str_, _numpy.unicode_)
    except:
      # numpy 2.0 compatibility
      valid_types = (_numpy.number, _numpy.bool_, _numpy.str_)
    for label in labels:
      if not any(_numpy.issubdtype(type(label), _) for _ in valid_types):
        raise ValueError('Categorical %s #%d must be of either string or numeric type, got %s' % (direction, variable_index, type(label)))

  return object

def collect_categorical_map(sample, categorical_variable_indices, direction, existing_categorical_map):
  if existing_categorical_map is None:
    existing_categorical_map = {} # no initial model, no further checks are needed
  elif existing_categorical_map:
    if not categorical_variable_indices:
      categorical_variable_indices = sorted([i for i in existing_categorical_map]) # read categorical variables from the initial model
    elif sorted([i for i in existing_categorical_map]) != sorted(categorical_variable_indices):
      raise ValueError("%s(s) %s are set categorical but the initial model given has different set of categorical %ss: %s."
                       % (direction.title(), ", ".join(str(i) for i in categorical_variable_indices), direction, ", ".join(_safestr(i) for i in existing_categorical_map)))
  elif categorical_variable_indices:
    raise ValueError("%s(s) %s are set categorical but the initial model given has no categorical %ss." % (direction.title(), ", ".join(str(i) for i in categorical_variable_indices), direction))

  if not categorical_variable_indices:
    return {}

  # Even though casting the whole sample to object type is less effective than casting to a type selected automatically by numpy
  # we avoid that way precision loss in case of converting to string types, maximal lengths of which depend on numpy version
  # (e.g. there is a known case of the same sample casting to <U17 in numpy v1.11.2 and <U22 in numpy v1.18.5)
  sample = as_matrix(sample, dtype=object, name="%s part of the train dataset" % direction.title())

  if any((i < 0 or i >= sample.shape[1]) for i in categorical_variable_indices):
    raise ValueError('Invalid categorical %s index encountered out of valid indices range [0, %d]: %s'
                     % (direction, sample.shape[1] - 1, ", ".join(str(i) for i in categorical_variable_indices if (i < 0 or i >= sample.shape[1]))))

  forbidden_labels = [+_numpy.inf, -_numpy.inf, _numpy.nan, None]
  categorical_map = {}

  for variable_index, variable_values in enumerate(sample.T):
    if variable_index not in categorical_variable_indices:
      try:
        variable_values.astype(float)
      except:
        exc_info = _sys.exc_info()
        reraise(ValueError, ('Continuous %s #%d must contain float values: %s' % (direction, variable_index, exc_info[1])), exc_info[2])
    else:
      initial_dtype, initial_labels, initial_enumerators = [_ for _ in existing_categorical_map.get(variable_index, (float, [], []))]
      try:
        test_labels = initial_labels + forbidden_labels
        labels = []
        for unique_value in set(variable_values):
          try:
            unique_value = float(unique_value)
          except:
            pass
          # ugly but this is the only secure way to filter out NaNs
          if unique_value not in (test_labels + labels) and unique_value == unique_value:
            labels.append(unique_value)
      except Exception:
        exc_info = _sys.exc_info()
        reraise(ValueError, ('Error while processing categorical %s #%d values: %s' % (direction, variable_index, exc_info[1])), exc_info[2])

      # try to order labels
      try:
        labels = initial_labels + sorted(labels)
      except:
        labels = initial_labels + labels

      dtype = get_labels_type(labels, direction, variable_index, validate=True)
      categorical_map[variable_index] = dtype, labels, initial_enumerators

  return categorical_map

def read_categorical_maps(metainfo, validate=True):
  if not metainfo:
    return {}, {}

  categorical_inputs_map, categorical_outputs_map = {}, {}

  for var_index, var_meta in enumerate(metainfo.get("Input Variables", [])):
    if "enumeration" == var_meta.get("variability") and "enumerators" in var_meta:
      labels = var_meta.get("labels", var_meta["enumerators"])
      dtype = get_labels_type(labels, "input", var_index, validate)
      enumerators = _numpy.array(var_meta["enumerators"], dtype=float).tolist()
      categorical_inputs_map[var_index] = dtype, labels, enumerators

  for var_index, var_meta in enumerate(metainfo.get("Output Variables", [])):
    if "enumeration" == var_meta.get("variability") and "enumerators" in var_meta:
      labels = var_meta.get("labels", var_meta["enumerators"])
      dtype = get_labels_type(labels, "output", var_index, validate)
      enumerators = _numpy.array(var_meta["enumerators"], dtype=float).tolist()
      categorical_outputs_map[var_index] = dtype, labels, enumerators

  return categorical_inputs_map, categorical_outputs_map

def encode_categorical_map(categorical_map):
  if not categorical_map:
    return ""

  categorical_map = dict(categorical_map) # make a copy
  for key in categorical_map:
    dtype, labels, enumerators = categorical_map[key]
    categorical_map[key] = str(_numpy.dtype(dtype)), labels, enumerators

  return write_json(categorical_map)

def parse_categorical_map(json_string):
  if not json_string:
    return {}

  categorical_map = {}
  for i, (dtype, labels, enumerators) in _six.iteritems(parse_json(json_string)):
    var_index = int(i)
    try:
      dtype = _numpy.dtype(dtype)
    except:
      dtype = None
    if dtype is None:
      dtype = get_labels_type(labels, "", var_index, validate=False)
    enumerators = _numpy.array(enumerators, dtype=float).tolist()
    categorical_map[var_index] = dtype, labels, enumerators
  return categorical_map

def _encode_categorical_variable(dtype, labels, enumerators, values_in, values_out=None, forbidden_labels=None, logger=None, variable_name=None):
  labels = _numpy.array(labels, dtype=dtype)
  values_in = _numpy.array(values_in, dtype=dtype, copy=_SHALLOW, ndmin=1)
  enumerators = _numpy.array(enumerators, dtype=float)

  if values_out is None:
    values_out = _numpy.empty(len(values_in), dtype=float)
    values_out.fill(_NONE)

  if not _numpy.issubdtype(dtype, _numpy.number) or _numpy.any(labels != enumerators):
    if logger is not None:
      logger(_loggers.LogLevel.DEBUG, "Setting the following encoding for categorical %s: [%s] -> [%s]"
                                    % ((variable_name or "variable"), ", ".join([_safestr(_) for _ in labels]),
                                    ", ".join([_safestr(_) for _ in enumerators])))

  known_values = _numpy.zeros(values_in.size, dtype=bool)

  if not _numpy.issubdtype(dtype, _numpy.number):
    for label, enum in zip(labels, enumerators):
      label_type = type(label)
      for j, val in enumerate(values_in):
        try:
          if val == label or label_type(val) == label:
            values_out[j] = enum
            known_values[j] = True
        except:
          pass
  elif _numpy.any(labels != enumerators):
    for label, enum in zip(labels, enumerators):
      label_mask = values_in == label
      values_out[label_mask] = enum
      known_values += label_mask
      if _numpy.all(known_values):
        break
  else:
    # All labels are numerical and coincide with enumerators so leave them as they are
    values_out[:] = values_in
    known_values[:] = True

  if not known_values.all():
    if forbidden_labels is None:
      forbidden_labels = list(_six.itervalues(_REPR_FLOAT)) + [None, ]
    unknown_enum = _numpy.setdiff1d(_numpy.arange(len(enumerators) + 1), enumerators[~_numpy.isnan(enumerators)], assume_unique=True)[0]
    for unknown_value in _numpy.unique(values_in[~known_values]):
      if unknown_value not in forbidden_labels and unknown_value == unknown_value:
        values_out[values_in == unknown_value] = unknown_enum

  return values_out

def encode_categorical_values(sample, categorical_variables_map, direction, log=None):
  if not categorical_variables_map:
    return sample

  forbidden_labels = list(_six.itervalues(_REPR_FLOAT)) + [None, ]

  sample = as_matrix(sample, dtype=object, name="%s part of the decoded dataset" % direction.title())
  encoded_sample = _numpy.empty(sample.shape, dtype=float)
  encoded_sample.fill(_numpy.nan)

  for i, values in enumerate(sample.T):
    if i not in categorical_variables_map:
      try:
        encoded_sample[:, i] = values.astype(float)
      except:
        exc_info = _sys.exc_info()
        reraise(ValueError, ('Continuous %s #%d must contain float values: %s' % (direction, i, exc_info[1])), exc_info[2])
    else:
      dtype, labels, enumerators = categorical_variables_map[i]
      _encode_categorical_variable(dtype=dtype, labels=labels, enumerators=enumerators, values_in=values, values_out=encoded_sample[:, i],
                                   forbidden_labels=forbidden_labels, logger=log, variable_name=("%s #%d" % (direction, i,)))

  return encoded_sample

def decode_categorical_values(sample, categorical_variables_map, inplace=True):
  if not categorical_variables_map:
    return sample

  # considering sample is matrix, so this is just a paranoid transform allowed only because it's light
  sample = _numpy.array(sample, ndmin=2, copy=_SHALLOW)
  decoded_dtype = _numpy.result_type(*(categorical_variables_map[i][0] for i in categorical_variables_map))
  decoded_sample = _numpy.array(sample, copy=_SHALLOW, dtype=decoded_dtype) # no copy op if decoded_dtype equals to sample.dtype
  if not decoded_sample.flags.writeable or (decoded_sample is sample and not inplace):
    decoded_sample = decoded_sample.copy() # copy is required (e.g. training sample is based on internal c++ memory so we do keep it as is)

  for i, (dtype, labels, enumerators) in _six.iteritems(categorical_variables_map):
    labels = as_matrix(labels, shape=(1, None), dtype=dtype)[0]
    enumerators = as_matrix(enumerators, shape=(1, len(labels)), dtype=float)[0]

    mapping_mask = _numpy.array([not (_numpy.can_cast(type(label), float) and code == label) for code, label in zip(enumerators, labels)], dtype=bool)
    if mapping_mask.any(): # do we need to remap
      if mapping_mask.all():
        mapping_mask = slice(None) # it's faster to get all rather than make a copy
      assign_mask = _numpy.nonzero(_numpy.equal(sample[:, i].reshape(-1, 1), enumerators[mapping_mask].reshape(1, -1)))
      # assign_mask[1] is 0-based index of label in labels[mapping_mask]
      # assign_mask[0] is index of element to assign. Note if sample contains NaN's then assign_mask[1] may have leaps
      decoded_sample[:, i][assign_mask[0]] = labels[mapping_mask][assign_mask[1]]

  return decoded_sample


class _JsonParser(object):

  __STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', (re.VERBOSE | re.MULTILINE | re.DOTALL))
  __NUMBER_RE = re.compile(r'(-?(?:0|[1-9]\d*))(\.\d*)?([eE][-+]?\d+)?', (re.VERBOSE | re.MULTILINE | re.DOTALL))
  __WHITESPACE = re.compile(r'[ \t\n\r]*', (re.VERBOSE | re.MULTILINE | re.DOTALL))
  __WHITESPACE_STR = ' \t\n\r'
  __BACKSLASH = {'"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}

  def __init__(self, strict=False):
    """
    If strict is false, then control characters will be allowed inside strings.
    Control characters in this context are those with character codes in the 0-31 range,
    including '\\t', '\\n', '\\r' and '\\0'.
    """
    self.__strict = strict

  def __linecol(self, doc, pos):
    lineno = doc.count('\n', 0, pos) + 1
    if lineno == 1:
      colno = pos + 1
    else:
      colno = pos - doc.rindex('\n', 0, pos)
    return lineno, colno

  def __errmsg(self, msg, doc, pos, end=None):
    lineno, colno = self.__linecol(doc, pos)
    if end is None:
      fmt = '%s: line %d column %d (char %d)'
      return fmt % (msg, lineno, colno, pos)
    endlineno, endcolno = self.__linecol(doc, end)
    fmt = '%s: line %d column %d - line %d column %d (char %d - %d)'
    return fmt % (msg, lineno, colno, endlineno, endcolno, pos, end)

  def __decode_uXXXX(self, s, pos):
    if s[pos] == 'x':
      length = 3
      esc = s[pos + 1:pos + length]
      return int(esc, 16), length
    elif s[pos] == 'u':
      length = 5
      esc = s[pos + 1:pos + length]
      if len(esc) == 4 and esc[1] not in 'xX':
        try:
          return int(esc, 16), length
        except ValueError:
          pass
      raise ValueError(self.__errmsg("Invalid unicode escape", s, pos))

  def parse_string(self, s, end):
    """Scan the string s for a JSON string. End is the index of the
    character in s after the quote that started the JSON string.
    Unescapes all valid JSON string escape sequences and raises ValueError
    on attempt to decode an invalid string. If strict is False then literal
    control characters are allowed in the string.

    Returns a tuple of the decoded string and the index of the character in s
    after the end quote."""
    chunks = []
    chunks_append = chunks.append
    begin = end - 1
    while True:
      chunk = self.__STRINGCHUNK.match(s, end)
      if chunk is None:
        raise ValueError(self.__errmsg("Unterminated string starting at", s, begin))
      end = chunk.end()
      content, terminator = chunk.groups()
      # Content is contains zero or more unescaped string characters
      if content:
        chunks_append(content)
      # Terminator is the end of string, a literal control character,
      # or a backslash denoting that an escape sequence follows
      if terminator == '"':
        break
      elif terminator != '\\':
        if self.__strict:
          raise ValueError(self.__errmsg("Invalid control character %s at" % (repr(terminator)), s, end))
        else:
          chunks_append(terminator)
          continue
      try:
        esc = s[end]
      except IndexError:
        tb = _sys.exc_info()[2]
        reraise(ValueError, self.__errmsg("Unterminated string starting at", s, begin), tb)
      # If not a unicode escape sequence, must be in the lookup table
      if esc != 'u' and esc != 'x':
        try:
          char = self.__BACKSLASH[esc]
        except KeyError:
          tb = _sys.exc_info()[2]
          reraise(ValueError, self.__errmsg("Invalid \\escape: " + repr(esc), s, end), tb)
        end += 1
      else:
        # Unicode escape sequence
        uni, length = self.__decode_uXXXX(s, end)
        end += length
        # Check for surrogate pair on UCS-4 systems
        if _sys.maxunicode > 65535 and 0xd800 <= uni <= 0xdbff and s[end:end + 2] == '\\u':
          uni2 = self.__decode_uXXXX(s, end + 1)
          if 0xdc00 <= uni2 <= 0xdfff:
            uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
            end += 6
        char = _six.unichr(uni)
      # Append the unescaped character
      chunks_append(char)
    return ''.join(chunks), end

  def parse_object(self, s, end):
    _w = self.__WHITESPACE.match
    _ws = self.__WHITESPACE_STR
    pairs = []
    pairs_append = pairs.append
    # Use a slice to prevent IndexError from being raised, the following
    # check will raise a more specific ValueError if the string is empty
    nextchar = s[end:end + 1]
    # Normally we expect nextchar == '"'
    if nextchar != '"':
      if nextchar in _ws:
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
      # Trivial empty object
      if nextchar == '}':
        pairs = {}
        return pairs, end + 1
      elif nextchar != '"':
        raise ValueError(self.__errmsg("Expecting property name enclosed in double quotes", s, end))
    end += 1
    while True:
      key, end = self.parse_string(s, end)
      # To skip some function call overhead we optimize the fast paths where
      # the JSON key separator is ": " or just ":".
      if s[end:end + 1] != ':':
        end = _w(s, end).end()
        if s[end:end + 1] != ':':
          raise ValueError(self.__errmsg("Expecting ':' delimiter", s, end))
      end += 1
      try:
        if s[end] in _ws:
          end += 1
          if s[end] in _ws:
            end = _w(s, end + 1).end()
      except IndexError:
        pass
      try:
        value, end = self.parse_once(s, end)
      except StopIteration:
        tb = _sys.exc_info()[2]
        reraise(ValueError, self.__errmsg("Expecting object", s, end), tb)
      pairs_append((key, value))
      try:
        nextchar = s[end]
        if nextchar in _ws:
          end = _w(s, end + 1).end()
          nextchar = s[end]
      except IndexError:
        nextchar = ''
      end += 1
      if nextchar == '}':
        break
      elif nextchar != ',':
        raise ValueError(self.__errmsg("Expecting ',' delimiter", s, end - 1))
      try:
        nextchar = s[end]
        if nextchar in _ws:
          end += 1
          nextchar = s[end]
          if nextchar in _ws:
            end = _w(s, end + 1).end()
            nextchar = s[end]
      except IndexError:
        nextchar = ''
      end += 1
      if nextchar != '"':
        raise ValueError(self.__errmsg("Expecting property name enclosed in double quotes", s, end - 1))
    pairs = dict(pairs)
    return pairs, end

  def parse_array(self, s, end):
    _w = self.__WHITESPACE.match
    _ws = self.__WHITESPACE_STR
    values = []
    nextchar = s[end:end + 1]
    if nextchar in _ws:
      end = _w(s, end + 1).end()
      nextchar = s[end:end + 1]
    # Look-ahead for trivial empty array
    if nextchar == ']':
      return values, end + 1
    _append = values.append
    while True:
      try:
        value, end = self.parse_once(s, end)
      except StopIteration:
        tb = _sys.exc_info()[2]
        reraise(ValueError, self.__errmsg("Expecting object", s, end), tb)
      _append(value)
      nextchar = s[end:end + 1]
      if nextchar in _ws:
        end = _w(s, end + 1).end()
        nextchar = s[end:end + 1]
      end += 1
      if nextchar == ']':
        break
      elif nextchar != ',':
        raise ValueError(self.__errmsg("Expecting delimiter ',' or the end of array ']', got '%s' " % nextchar, s, end))
      try:
        if s[end] in _ws:
          end += 1
          if s[end] in _ws:
            end = _w(s, end + 1).end()
      except IndexError:
        pass
    return values, end

  def parse_once(self, string, idx):
    try:
      nextchar = string[idx]
    except IndexError:
      reraise(StopIteration, None, _sys.exc_info()[2])
    # Parse character
    if nextchar == '"':
      return self.parse_string(string, idx + 1)
    elif nextchar == '{':
      return self.parse_object(string, idx + 1)
    elif nextchar == '[':
      return self.parse_array(string, idx + 1)
    elif nextchar == 'n' and string[idx:idx + 4] == 'null':
      return None, idx + 4
    elif nextchar == 't' and string[idx:idx + 4] == 'true':
      return True, idx + 4
    elif nextchar == 'f' and string[idx:idx + 5] == 'false':
      return False, idx + 5
    # Parse number
    m = self.__NUMBER_RE.match(string, idx)
    if m is not None:
      integer, frac, exp = m.groups()
      if frac or exp:
        res = float(integer + (frac or '') + (exp or ''))
      else:
        res = int(integer)
      return res, m.end()
    elif nextchar == 'N' and string[idx:idx + 3] == 'NaN':
      return _numpy.nan, idx + 3
    elif nextchar == 'I' and string[idx:idx + 8] == 'Infinity':
      return _numpy.inf, idx + 8
    elif nextchar == '+' and string[idx:idx + 9] == '+Infinity':
      return _numpy.inf, idx + 9
    elif nextchar == '-' and string[idx:idx + 9] == '-Infinity':
      return -_numpy.inf, idx + 9
    else:
      raise StopIteration()

  def parse(self, text):
    if not text:
      return {}
    try:
      obj, end = self.parse_once(text, self.__WHITESPACE.match(text, 0).end())
    except StopIteration:
      reraise(ValueError, "No JSON object could be decoded", _sys.exc_info()[2])
    end = self.__WHITESPACE.match(text, end).end()
    if end != len(text):
      raise ValueError(self.__errmsg("Extra data", text, end, len(text)))
    return obj

def parse_json_deep(text, empty_type=None):
  """Parse string in JSON format.

  :param text: - string or bytearray to parse JSON
  :param empty_type: - optional callable object without parameters to create result if text is empty.
                       If empty_type is None and text is empty then ValueError is raised.

  :rtype: dict of dicts of dicts...
  """
  try:
    import json
    if isinstance(text, (bytes, bytearray)):
      text = _preprocess_json(text)
    if text:
      return json.loads(text)
  except (ImportError, NameError, ValueError):
    pass
    # Go down and try to use in-house parser

  if not text:
    if empty_type:
      return empty_type()
    else:
      raise ValueError('No JSON object could be decoded')

  return _JsonParser(False).parse(text)

def parse_json(text):
  """Parse string in JSON format.

  :rtype: dict of dicts of dicts...
  """
  return parse_json_deep(text, dict)

class _JsonWriter:
  _TTBL = dict((_, (_six.unichr(_) if 32 <= _ < 127 else (u"\\u%04x" % _))) \
               for _ in _six.moves.xrange(0xffff))
  _TTBL.update({ord("\\"): u"\\\\",
                ord("\""): u"\\\"",
                ord("/"): u"\\/",
                ord("\b"): u"\\b",
                ord("\f"): u"\\f",
                ord("\n"): u"\\n",
                ord("\r"): u"\\r",
                ord("\t"): u"\\t",})
  _TTBL_STOP = _six.unichr(0xffff)

  def write_string(self, data):
    data = _six.u(data) if _six.PY2 and isinstance(data, str) else _six.text_type(data)
    json_data = data.translate(self._TTBL)
    if not json_data or max(json_data) < self._TTBL_STOP:
      return '"' + json_data + '"'
    return '"' + ''.join((_ if _ < self._TTBL_STOP else (u"\\u%04x" % ord(_))) for _ in json_data) + '"'

  def write_object(self, data):
    return '{%s}' % ','.join(('%s:%s' % (self.write_string(key), self.write(data[key]))) for key in data)

  def write_array(self, data):
    return '[%s]' % ','.join(self.write(value) for value in data)

  def write_numpy_array(self, data):
    try:
      # 0-dimensional arrays do not support iterator interface while they are converatable to list
      if not data.ndim:
        return self.write(data.tolist())
    except:
      pass
    return self.write_array(data)

  def write_bool(self, data):
    return 'true' if data else 'false'

  def write_float(self, data):
    if _numpy.isnan(data):
      return 'NaN'
    if _numpy.isinf(data):
      return 'Infinity' if data > 0 else '-Infinity'
    return self.fmt_double % data

  def write_none(self, data):
    return 'null'

  def write_long(self, data):
    return str(long_integer(data))

  def __init__(self, custom_types, fmt_double):
    self.fmt_double = fmt_double
    self.handlers = {dict: self.write_object,
                      list: self.write_array,
                      _numpy.ndarray: self.write_numpy_array,
                      tuple: self.write_array,
                      bool: self.write_bool,
                      float: self.write_float,
                      str: self.write_string,
                      type(None): self.write_none,
                    }
    for itype in _six.integer_types:
      self.handlers[itype] = self.write_long

    try:
      self.handlers[unicode] = self.write_string
    except NameError:
      pass

    self.checkers = [ (lambda data: _numpy.issubdtype(data, _numpy.floating), self.write_float)
                    , (lambda data: _numpy.issubdtype(data, _numpy.integer), self.write_long)
                    , (lambda data: _numpy.issubdtype(data, _numpy.bool_), self.write_bool)
                    # the explicit check for string type is required because if data = _numpy.array(['A'], dtype=None)[0]
                    # then list(data) does not raise an exception and we generate ['A']  instead of 'A'
                    , (lambda data: isinstance(data, _six.string_types), self.write_string)
                    # The following checkers are ugly but effective for dict-like objects like pandas dataframe.
                    # Note pandas dataframe does not report itself as collections.Mapping instance while it is!
                    , (lambda data: dict(data), lambda data: self.write_object(dict(data)))
                    , (lambda data: list(data), lambda data: self.write_array(list(data)))]

    if custom_types is not None:
      for custom_type in custom_types:
        self.handlers[custom_type] = self.handlers[custom_types[custom_type]]

  def __check_subclass(self, data):
    for checker, handler in self.checkers:
      try:
        if checker.__call__(data):
          return handler.__call__(data)
      except:
        # do nothing, it's OK
        pass
    return self.write_string(data)

  def write(self, data):
    return self.handlers.get(type(data), self.__check_subclass).__call__(data)


def write_json(data, custom_types={}, fmt_double='%.17g'):
  """
  Writes Python object data as JSON string.

  :param data: - object to write as JSON
  :param custom_types: - optional dict where keys are custom user types and values are
                         one of the standard Python types: dict, list, str, unicode, float, tuple, int, long, bool, type(None)
                         defining JSON representation of the custom user type given.
  :param fmt_double: - format string to write doubles. %.17g representation is accurate enough to convert
                       double to string and back without precision loss, but it generates weird output
                       in cases like 2.5e32 So we use %.15g by default
  :rtype: string
  """
  return _JsonWriter(custom_types, fmt_double).write(data)

def read_traceback():
  """Read the traceback of a caught exception in a logging-friendly format."""

  buf = _six.StringIO()
  exc_type, exc_value = _sys.exc_info()[:2]
  if issubclass(exc_type, Exception):
    buf.write('\n')
    buf.write('=' * 60)
    buf.write('\n')
    _traceback.print_exc(file=buf)
    buf.write('=' * 60)
    buf.write('\n')
  else:
    buf.write(str(exc_value))
  return buf.getvalue()

def reraise(exc_type, exc_value, exc_tb):
  if isinstance(exc_type, Exception):
    exc_type, exc_value = (type(exc_type), exc_type)
  elif not isinstance(exc_value, exc_type):
    try:
      exc_value = exc_type() if exc_value is None \
                  else exc_type(*exc_value) if isinstance(exc_value, tuple) \
                  else exc_type(exc_value)
    except:
      exc_type = _ex.GTException # some exceptions, e.g. UnicodeDecodeError, have uncommon ctors
      exc_value = _ex.GTException("%s: %s" % (exc_type, exc_value))

  if _six.PY3:
    if exc_value.__traceback__ is not exc_tb:
      exc_value = exc_value.with_traceback(exc_tb)
    _six.raise_from(exc_value, None)
  else:
    _six.reraise(exc_type, exc_value, exc_tb)

def wrap_with_exc_handler(f, exc_type):
  if not _six.callable(f) or getattr(f, '_wrapped_with_exc_handler', False):
    return f
  def tmp(*args, **kwargs):
    try:
      return f(*args, **kwargs)
    except Exception:
      exc_value, exc_tb = _sys.exc_info()[1:]
      reraise(exc_type, exc_value, exc_tb)
  # Just to avoid occasional multiple wrappings
  tmp._wrapped_with_exc_handler = True
  return tmp

def isNanInf(x):
  """Return true if only x is NaN or Infinity"""
  return _numpy.isnan(x, casting='unsafe').any() or _numpy.isinf(x, casting='unsafe').any()

__SYNONYMS_TRUE = ("true", "yes", "y", "on")
__SYNONYMS_FALSE = ("false", "no", "n", "off")

def parse_bool(value):
  """Parse value, so one can identify if it is a synonym of logical true and false."""
  try:
    value = bool(float(value))
    return value
  except (TypeError, ValueError): # OK, v is not a number or numeric literal, and we've just handled bool here
    pass

  try:                          # the drawback is that we can't distinguish between ValueErrors due to incorrect float literal and due to the string being one of the true/false synonyms
    value = value.lower()  # only str and unicode have this attribute
  except AttributeError:
    reraise(TypeError, "incorrect value type - only numbers and strings may be converted to Boolean", _sys.exc_info()[2])

  if value in __SYNONYMS_TRUE:
    return True
  elif value in __SYNONYMS_FALSE:
    return False

  raise ValueError("incorrect value - specify a true/false synonym, a number, or a correct float literal")

def parse_auto_bool(value, auto_value):
  return auto_value if isinstance(value, _six.string_types) and value.lower() == 'auto' else parse_bool(value)

def parse_output_transformation(value, output_size=None):
  if not isinstance(value, _six.string_types):
    return [str(_).strip().strip('"') for _ in value]

  try:
    value = parse_json_deep(value, str)  # the empty string is the default value, "use initial model or 'none'"
    if not isinstance(value, _six.string_types):
      return value
    return value.lower() if output_size is None else [value.lower(),]*output_size
  except:
    pass

  value = value.strip()
  if value[0] == '[' and value[-1] == ']':
    return [_.strip().strip('"').lower() for _ in value[1:-1].split(',')]

  value = value.strip('"').lower()
  return value if output_size is None else [value,]*output_size

def _write_string_vector_list(values):
  return [[(item if isinstance(item, _six.string_types) else _safestr(item)) for item in lst] for lst in values]

class Logger(object):
  """Sift message before users logger."""

  def __init__(self, logger=None, log_level_string='info', prefix=None):
    self.logger = logger
    self.log_level = _loggers.LogLevel.from_string(log_level_string)
    self.prefix = prefix or ""

  def __call__(self, level, message):
    self._log_message(level, _preprocess_utf8(message))

  def _log_message(self, message_level, message):
    if (message_level >= self.log_level) and self.logger:
      if self.prefix:
        for s in message.split("\n"):
          self.logger(message_level, (self.prefix + s))
      else:
        self.logger(message_level, message)

  def debug(self, message):
    self._log_message(_loggers.LogLevel.DEBUG, message)

  def info(self, message):
    self._log_message(_loggers.LogLevel.INFO, message)

  def warn(self, message):
    self._log_message(_loggers.LogLevel.WARN, message)

  def error(self, message):
    self._log_message(_loggers.LogLevel.ERROR, message)

  def fatal(self, message):
    self._log_message(_loggers.LogLevel.FATAL, message)

  def __nonzero__(self):
    return bool(self.logger)

  def __bool__(self):
    return bool(self.logger)

class TeeLogger(object):
  def __init__(self, logger, log_level, collect_issues=False):
    self.__public_stream = logger
    self.__public_threshold = log_level
    self.__string_buffer = _six.StringIO()
    self.__private_log_level = min(log_level, _loggers.LogLevel.INFO)
    self.__private_stream = _loggers.StreamLogger(stream=self.__string_buffer, log_level=self.__private_log_level)
    self.__issues = {} if collect_issues else None

  def __call__(self, level, message):
    message = _preprocess_utf8(message)
    if self.__public_stream is not None:
      if level >= self.__public_threshold:
        self.__public_stream(level, message)
    self.__private_stream(level, message)

    if self.__issues is not None and level >= _loggers.LogLevel.WARN:
      try:
        general_key, key_splitter = '[general]', ' >>> '
        for warn_line in message.splitlines(): # messages can be batched to multiline
          if key_splitter in warn_line:
            key, warn_line = warn_line.split(key_splitter, 1)
          else:
            key, warn_line = general_key, warn_line

          warn_line = warn_line.strip()
          if warn_line: # and warn_line not in issues.get(key, [])
            self.__issues.setdefault(key.strip(), []).append(warn_line)
      except:
        pass
      pass

  @property
  def private_log_level(self):
    return self.__private_log_level

  @property
  def log_value(self):
    return self.__string_buffer.getvalue()

  @property
  def issues(self):
    return self.__issues or {}

class TrainingPhasesWatcher(object):

  def __init__(self, watcher):
    self.watcher = watcher
    self._keep_working = True

    self._global_phase = 0
    self._n_global_phases = 0

    self._smart_phase = 0
    self._n_smart_phases = 0

    self._moa_phase = 0
    self._n_moa_phases = 0

    self._smart_phase_technique = tuple()
    self._smart_phase_techniques = tuple()

    self._n_iv_phases = 0

  def __call__(self, userdata=None):
    if self.watcher is None:
      return True # no further processing is needed

    if self._keep_working:
      try:
        # postprocess userdata if userdata is mapping or None
        userdata = self._postprocess({} if userdata is None else dict((k, userdata[k]) for k in userdata))
      except:
        pass

      self._keep_working = bool(self.watcher(userdata))

    return self._keep_working

  def _postprocess(self, userdata):
    if userdata.pop('passed all iv phases', False):
      self._global_phase += self._n_iv_phases

    if userdata.pop('reset moa phase', False):
      self._moa_phase = 0
      self._n_moa_phases = 0

    if userdata.pop('reset smart phase', False):
      self._smart_phase = 0
      self._n_smart_phases = 0
      self._smart_phase_technique = tuple()
      self._smart_phase_techniques = tuple()

    progress_details = {}

    self._n_global_phases = userdata.pop('number of global phases', self._n_global_phases)
    self._global_phase = userdata.pop('current global phase', self._global_phase)
    self._global_phase += userdata.pop('passed global phases', 0)
    if self._n_global_phases > 0:
      progress_details['global'] = self._global_phase, self._n_global_phases

    self._n_moa_phases = userdata.pop('number of moa phases', self._n_moa_phases)
    self._moa_phase = userdata.pop('current moa phase', self._moa_phase)
    self._moa_phase += userdata.pop('passed moa phases', 0)
    if self._n_moa_phases > 0:
      progress_details['moa'] = self._moa_phase, self._n_moa_phases

    self._n_smart_phases = userdata.pop('number of smart phases', self._n_smart_phases)
    self._smart_phase = userdata.pop('current smart phase', self._smart_phase)
    self._smart_phase += userdata.pop('passed smart phases', 0)
    if self._n_smart_phases > 0:
      progress_details['smart selection'] = self._smart_phase, self._n_smart_phases

    self._smart_phase_techniques = tuple(userdata.pop('smart phase techniques', self._smart_phase_techniques))
    self._smart_phase_technique = tuple(userdata.pop('smart phase technique', self._smart_phase_technique))
    technique = userdata.pop('current smart phase technique', None)
    if technique and technique not in self._smart_phase_technique and technique in self._smart_phase_techniques:
      self._smart_phase_technique = self._smart_phase_technique + (technique, )
      self._smart_phase_technique = tuple(sorted(self._smart_phase_technique, key=lambda _: self._smart_phase_techniques.index(_)))
    if self._smart_phase_technique and self._smart_phase_techniques:
      progress_details['smart selection technique'] = self._smart_phase_technique, self._smart_phase_techniques

    # always use global progress, but make smart selection and moa mutually exclusive
    # because moa training in smart selection may be batched with hdagp or something else
    global_progress, global_den = progress_details.get("global", (0., 1.))
    local_progress, local_den = progress_details.get("smart selection", progress_details.get("moa", (0., 1.)))

    userdata["progress"] = min(1., (float(global_progress) + float(local_progress) / max(local_den, local_progress + 1)) / global_den)
    userdata["training phase"] = progress_details

    return userdata

  def count_phases(self, n_outputs, n_discrete_classes, n_tensor_factors, n_iv_training):
    self._n_iv_phases = n_outputs * n_discrete_classes * n_iv_training * max(1, n_tensor_factors)
    self._n_global_phases = n_outputs * n_discrete_classes + self._n_iv_phases

  def add_phases(self, n_outputs, n_discrete_classes, n_tensor_factors, n_iv_training):
    self._n_iv_phases += n_outputs * n_discrete_classes * n_iv_training * max(1, n_tensor_factors)
    self._n_global_phases += n_outputs * n_discrete_classes + self._n_iv_phases


def readStatistics(instance, kind, toolprefix, make_readonly=True, backend=_api, dataset_index=None):
  # intentionally assign single shared _api object as default value so we keep backend loaded as long as this method exists
  kind_code = { "internal validation": ctypes.c_int(0),
                "training dataset": ctypes.c_int(1),
                "input sample": ctypes.c_int(2),
                "output sample": ctypes.c_int(3),
                "points weights": ctypes.c_int(4),
                "output noise variance": ctypes.c_int(5),
                "test input sample": ctypes.c_int(6),
                "test output sample": ctypes.c_int(7),
              }[kind.lower()]

  if dataset_index is not None:
    kind_code = ctypes.c_int(kind_code.value + (int(dataset_index) + 1) * 256)

  def __safe_call(err, errdesc):
    _raise_on_error(err, "Internal implementation function call failed", errdesc, backend=backend)

  ivResultName = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.c_char_p, ctypes.POINTER(ctypes.c_size_t),
                                  ctypes.POINTER(ctypes.c_void_p))((toolprefix + "ModelValidationResultName", backend._library))
  ivResultShape = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
                                   ctypes.POINTER(ctypes.c_void_p))((toolprefix + "ModelValidationResultShape", backend._library))
  ivResultData = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
                                  ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_void_p))((toolprefix + "ModelReadValidationResultData", backend._library))
  ivResultCountType = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_void_p))
  ivResultDataMask = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
                                      ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_void_p))((toolprefix + "ModelReadValidationResultMask", backend._library))

  statData = dict()

  errdesc = ctypes.c_void_p()

  # read the number of IV results
  ivResultsNumber = ctypes.c_size_t()
  __safe_call(ivResultCountType((toolprefix + "ModelValidationResultCount", backend._library))(instance, kind_code, ctypes.byref(ivResultsNumber), ctypes.byref(errdesc)), errdesc)
  ivResultsNumber = ivResultsNumber.value

  for ivResultIndex in _six.moves.range(ivResultsNumber):
    # read result name
    nameSize = ctypes.c_size_t()
    __safe_call(ivResultName(instance, kind_code, ivResultIndex, ctypes.c_char_p(), ctypes.byref(nameSize), ctypes.byref(errdesc)), errdesc)
    name = (ctypes.c_char * nameSize.value)()
    __safe_call(ivResultName(instance, kind_code, ivResultIndex, name, ctypes.byref(nameSize), ctypes.byref(errdesc)), errdesc)

    # read result shape
    ndim = ctypes.c_size_t()
    __safe_call(ivResultShape(instance, kind_code, ivResultIndex, ctypes.byref(ndim), ctypes.POINTER(ctypes.c_size_t)(), ctypes.byref(errdesc)), errdesc)
    shape = (ctypes.c_size_t * ndim.value)()
    __safe_call(ivResultShape(instance, kind_code, ivResultIndex, ctypes.byref(ndim), shape, ctypes.byref(errdesc)), errdesc)

    # allocate buffer and read data
    data = _numpy.ndarray(shape[:], dtype=ctypes.c_double, order='C')
    __safe_call(ivResultData(instance, kind_code, ivResultIndex, data.ndim, \
                            data.ctypes.shape_as(ctypes.c_size_t), data.ctypes.strides_as(ctypes.c_size_t),
                            data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)), ctypes.byref(errdesc)),
               errdesc)
    data.flags['WRITEABLE'] = not make_readonly

    # use colon sign as subdict separator while last element is actual name of data
    path = char2str(name.value).split(':')
    dest = statData
    for node in path[:-1]:
      if node not in dest:
        dest[node] = dict()
      dest = dest[node]
    dest[path[-1]] = data

    # try to read validity mask
    #mask = _numpy.ndarray(shape[:], dtype=bool, order='C')
    #__safe_call(ivResultDataMask(instance, kind_code, ivResultIndex, mask.ndim, \
    #                        mask.ctypes.shape_as(ctypes.c_size_t), mask.ctypes.strides_as(ctypes.c_size_t),
    #                        mask.ctypes.data_as(ctypes.c_void_p), mask.itemsize, ctypes.byref(errdesc)),
    #           errdesc)
    #mask.flags['WRITEABLE'] = not make_readonly
    #if not _numpy.all(mask):
    #  dest[path[-1] + ' Mask'] = mask

  return statData

class _HoleMarker(float):

  def __new__(cls, *args):
    self = super(_HoleMarker, cls).__new__(cls, _api.get_hole_marker())
    self.__vtest = _numpy.vectorize(_HoleMarker._is_hole_marker, otypes=[bool])
    return self

  @staticmethod
  def _is_hole_marker(value):
    if value is None:
      return 1
    try:
      return _api.is_hole_marker(value)
    except:
      return 0

  def __getstate__(self):
    # we must return non-empty dict
    return {"value": float(self)}

  def __setstate__(self, data):
    # assert _HoleMarker._is_hole_marker(data["value"]) # commented for backward compatibility reasons
    self.__vtest = _numpy.vectorize(_HoleMarker._is_hole_marker, otypes=[bool])

  def __repr__(self):
    return "N/A"

  def __str__(self):
    return "N/A"

  def __eq__(self, other):
    try:
      result = self.__vtest(other)
      return result if result.ndim else bool(result)
    except:
      return False

  def __ne__(self, other):
    try:
      result = self.__vtest(other)
      return ~result if result.ndim else not bool(result)
    except:
      return True

  def __neg__(self):
    return self

  def __pos__(self):
    return self

  def __abs__(self):
    return self

  def __invert__(self):
    return self

  def __add__(self, other):
    return self

  def __radd__(self, other):
    return self

  def __sub__(self, other):
    return self

  def __rsub__(self, other):
    return self

  def __mul__(self, other):
    return self

  def __rmul__(self, other):
    return self

  def __mod__(self, other):
    return self

  def __rmod__(self, other):
    return self

  def __div__(self, other):
    return self

  def __rdiv__(self, other):
    return self

  def __truediv__(self, other):
    return self

  def __rtruediv__(self, other):
    return self

  def __floordiv__(self, other):
    return self

  def __rfloordiv__(self, other):
    return self

  def __divmod__(self, other):
    return self, self

  def __rdivmod__(self, other):
    return self, self

  def __pow__(self, other, modulo=None):
    return self

  def __rpow__(self, other):
    return self

def _find_holes(matrix_data):
  try:
    matrix_data = _numpy.array(matrix_data, copy=_SHALLOW)
    hole_markers = _numpy.zeros_like(matrix_data, dtype=bool)

    if not hole_markers.size:
      return hole_markers

    c_size_ptr = ctypes.POINTER(ctypes.c_size_t)
    result = _api.is_batch_hole_marker(matrix_data.ndim, ctypes.cast(matrix_data.ctypes.shape, c_size_ptr),
                                       ctypes.cast(matrix_data.ctypes.strides, c_size_ptr), matrix_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                                       ctypes.cast(hole_markers.ctypes.strides, c_size_ptr), ctypes.c_void_p(hole_markers.ctypes.data))
    if result:
      return hole_markers
  except:
    pass
  return _NONE == matrix_data


_NONE = _HoleMarker()

_REPR_FLOAT = {"nan": _numpy.nan,
               "none": _NONE,
               "+inf": _numpy.inf,
               "inf": _numpy.inf,
               "+infinity": _numpy.inf,
               "infinity": _numpy.inf,
               "-inf": -_numpy.inf,
               "-infinity": -_numpy.inf,}

def __postprocess_holes(original_data, float_array, nan=_NONE):
  if float_array.dtype != float:
    return float_array

  original_ndarray = isinstance(original_data, _numpy.ndarray)
  if original_ndarray and original_data.dtype == float:
    return float_array

  try:
    if 0 == float_array.ndim:
      if original_data is None:
        float_array.flat[0] = nan
    else:
      mask_nan = _numpy.isnan(float_array)
      if not mask_nan.any():
        return float_array

      find_none = _numpy.frompyfunc(lambda x: x is None, 1, 1)
      if original_ndarray and original_data.shape == float_array.shape:
        mask_nan[mask_nan] = find_none(original_data[mask_nan]).astype(bool)
      else:
        mask_nan = find_none(original_data).astype(bool)

      if mask_nan.any():
        float_array[mask_nan] = nan
  except:
    # intentionally do nothing
    pass

  return float_array

def convert_to_1d_array(array, name='array', nan=_NONE):
  """
  Tries to convert the in-object to 1-d numpy ndarray.

  :param array: - object to convert
  :return: converted array
  :rtype: ``ndarray``, 1D
  """

  try:
    #single value
    if not is_iterable(array):
      return _numpy.array((nan if array is None else float(array),), dtype=_numpy.float64)

    #try to convert numpy.array
    try:
      original_array = array
      array = _numpy.array(array, dtype=_numpy.float64, copy=_SHALLOW)
      array = __postprocess_holes(original_array, array, nan)
    except:
      return _numpy.array([(nan if _ is None else float(_)) for _ in array], dtype=_numpy.float64)

    #already numpy
    if max(array.shape) != _numpy.prod(array.shape):
      raise TypeError('Matrix is not a column or a row')
    return _numpy.array([float(_) for _ in array.flat], dtype=_numpy.float64)

  except:
    exc_value, exc_tb = _sys.exc_info()[1:]
    reraise(TypeError, "Can not convert '%s' to 1D array due to: '%s'" % (name, exc_value), exc_tb)

def convert_to_2d_array(array, name='array', order='C', nan=_NONE):
  """
  Tries to convert the in-object to 2-d numpy ndarray.

  :param array: - object to convert
  :param type: iterable
  :return: converted array
  :rtype: ``ndarray``, 2D
  """

  try:
    #single value
    if not is_iterable(array):
      return _numpy.array(((nan if array is None else float(array),),), dtype=_numpy.float64, order=order)


    #try to convert numpy.array (or copy it!)
    try:
      original_array = array
      array = _numpy.array(array, dtype=_numpy.float64, order=order)
      array = __postprocess_holes(original_array, array, nan)
    except:
      return _numpy.array([convert_to_1d_array(_, nan=nan) for _ in array], dtype=_numpy.float64, order=order).T

    #already numpy
    if array.ndim == 1:
      array = array.reshape(array.size, min(1, array.size))  #add fake dim, make it (0,0) is incoming size is zero
    if array.shape[0]*array.shape[1] != _numpy.prod(array.shape):
      raise TypeError('Cannot reduce matrix to 2D')
    return array.reshape(array.shape[:2])

  except:
    exc_value, exc_tb = _sys.exc_info()[1:]
    reraise(TypeError, "Can not convert '%s' to 2D array due to: '%s'" % (name, exc_value), exc_tb)


_JSON_TTBL = dict((_, (_six.unichr(_) if _ < 127 else (u"\\u%04x" % _))) for _ in _six.moves.xrange(256))

def _preprocess_json(data):
  try:
    return data.decode('ascii')
  except AttributeError:
    return data
  except UnicodeError:
    return data.decode('latin1').translate(_JSON_TTBL)

def _preprocess_utf8(data):
  try:
    return unicodedata.normalize("NFKC", data if isinstance(data, _six.text_type) else data.decode('utf8'))
  except AttributeError:
    return data
  except UnicodeError:
    return data.decode('latin1')

def forward_warn(message):
  try:
    _warnings.warn(_preprocess_utf8(message))
    return True
  except:
    return False

def parse_float(value):
  try:
    return float(value)
  except (TypeError, ValueError):
    if value is None:
      return _NONE
    if isinstance(value, _six.string_types):
      float_value = _REPR_FLOAT.get(value.lower())
      if float_value is not None:
        return float_value
    raise

def parse_float_auto(value, auto_value):
  try:
    return float(value)
  except (TypeError, ValueError):
    if value is None:
      return _NONE
    if isinstance(value, _six.string_types):
      if value.lower() == 'auto':
        return auto_value
      float_value = _REPR_FLOAT.get(value.lower())
      if float_value is not None:
        return float_value
    raise

def make_proxy(obj):
  try:
    return _weakref.proxy(obj)
  except TypeError:
    return obj

class _SigIntWatcher(object):
  def __init__(self, builder):
    self._keep_working = True
    self._next_watcher = builder._set_watcher(self)

  def __call__(self, details=None):
    if self._keep_working and self._next_watcher:
      self._keep_working = self._next_watcher(details)
    return self._keep_working

  def sigint_handler(self, signum, frame):
    self._keep_working = False

@_contextlib.contextmanager
def sigint_watcher(builder):
  watcher = _SigIntWatcher(builder)

  old_sigint, old_sigterm = tuple(), tuple()
  try:
    old_sigint = (_signal.signal(_signal.SIGINT, watcher.sigint_handler),)
    old_sigterm = (_signal.signal(_signal.SIGTERM, watcher.sigint_handler),)
  except:
    # intentionally do nothing
    pass

  try:
    yield watcher
  finally:
    if old_sigint:
      _signal.signal(_signal.SIGINT, old_sigint[0])
    if old_sigterm:
      _signal.signal(_signal.SIGTERM, old_sigterm[0])
    builder._set_watcher(watcher._next_watcher)
    watcher._next_watcher = None

def _filled_array(shape, fill_value, dtype=None, order='C'):
  data = _numpy.empty(shape, dtype=dtype, order=order)
  data.fill(fill_value)
  return data

def _make_dataset_keys(dataset, decimals=14):
  if decimals is None or decimals > 17:
    keys = _numpy.array(dataset, dtype=float, copy=True)
  else:
    keys, key_exp = _numpy.frexp(dataset)
    keys = _numpy.ldexp(_numpy.round(keys, decimals), key_exp)

  # I've checked, these None/NaN marks are unique is we are rounding to 17 decimal digits or less.
  # If there is no rounding, then the probability of matching the existing value is negligible.
  keys[_find_holes(dataset)] = 7.0479526562917478e-09 # struct.pack('d', 7.0771706194101364e-09).decode('latin1') == '<<NONE>>'
  keys[_numpy.isnan(dataset)] = 7.0560919075547381e-09 # struct.pack('d', 7.0560919075547381e-09).decode('latin1') == '<<+NAN>>'

  return keys

def _lexsort(matrix_data):
  matrix_data = _numpy.array(matrix_data, copy=_SHALLOW)
  matrix_order = _numpy.zeros(len(matrix_data), dtype=int)

  if not matrix_order.size:
    return matrix_order

  try:
    c_size_ptr = ctypes.POINTER(ctypes.c_size_t)
    result = _api.lexsort(matrix_data.ndim, ctypes.cast(matrix_data.ctypes.shape, c_size_ptr),
                          ctypes.cast(matrix_data.ctypes.strides, c_size_ptr),
                          matrix_data.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
                          matrix_order.ctypes.data, matrix_order.strides[0])
  except:
    result = False
  return matrix_order if result else _numpy.lexsort(matrix_data.T)

def _enumerate_equal_keys(first_set, second_set, decimals=14):
  # WARN: check up Ent. prior to any changes to signature
  if not len(first_set) or not len(second_set):
    return

  first_set = _make_dataset_keys(first_set, decimals=decimals)
  second_set = _make_dataset_keys(second_set, decimals=decimals)

  if first_set.shape[0] == 1:
    for i in _numpy.where((first_set == second_set).all(axis=1))[0]:
      yield 0, i
    return

  if second_set.shape[0] == 1:
    for i in _numpy.where((first_set == second_set).all(axis=1))[0]:
      yield i, 0
    return

  def _series_lengths(ordered_points):
    unique_positions = _numpy.hstack((_numpy.where(~(ordered_points[:-1] == ordered_points[1:]).all(axis=1))[0] + 1, [len(ordered_points)]))
    unique_positions[1:] = unique_positions[1:] - unique_positions[:-1] # never use -= since a bug in numpy
    return unique_positions

  first_order = _lexsort(first_set)
  first_set = first_set[first_order]
  first_series = _series_lengths(first_set)

  second_order = _lexsort(second_set)
  second_set = second_set[second_order]
  second_series = _series_lengths(second_set)

  while len(first_order) and len(second_order):
    first_series_0, second_series_0 = first_series[0], second_series[0]
    difference_position = _numpy.where(first_set[0] != second_set[0])[0]

    if not len(difference_position):
      # we have 2 series of duplicates, enumerate all combinations
      for k in _six.moves.xrange(first_series_0*second_series_0):
        yield first_order[k // second_series_0], second_order[k % second_series_0]

      first_order = first_order[first_series_0:]
      first_set = first_set[first_series_0:]
      first_series = first_series[1:]

      second_order = second_order[second_series_0:]
      second_set = second_set[second_series_0:]
      second_series = second_series[1:]
    elif first_set[0, difference_position[-1]] < second_set[0, difference_position[-1]]:
      # first-set key is less, step first-set (note lexsort uses inverse columns order)
      first_order = first_order[first_series_0:]
      first_set = first_set[first_series_0:]
      first_series = first_series[1:]
    else:
      # second-set key is less, step second-set
      second_order = second_order[second_series_0:]
      second_set = second_set[second_series_0:]
      second_series = second_series[1:]


class _unsafe_allocator(object):
  def __init__(self):
    self._data = ctypes.create_string_buffer(1)

  def __call__(self, size):
    try:
      self._data = ctypes.create_string_buffer(size)
      return ctypes.addressof(self._data)
    except:
      pass
    return None

  @property
  def callback(self):
    return ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_size_t)(self)

  @property
  def value(self):
    return self._data.value

@_contextlib.contextmanager
def _scoped_options(problem, options=None, keep_options='all'):
  original_options = problem.options.values
  try:
    if str(keep_options).lower() != 'all':
      extra_options = dict((k, problem.options.get(k)) for k in (keep_options or []))
      problem.options.reset()
      if extra_options:
        problem.options.set(extra_options)

    if options:
      problem.options.set(options)
    yield original_options
  finally:
    problem.options.reset()
    problem.options.set(original_options)

def _pad_columns(matrix, width, value):
  if width <= 0:
    return matrix
  # Some versions of numpy have a bug that raises an exception if the padding value is NaN.
  matrix = _numpy.pad(matrix, ((0, 0), (0, width)), 'constant')
  matrix[:, -width:].fill(value)
  return matrix

def _normalize_string_list(string_list, default_value=None, name=None, keep_case=False):
  if string_list is None:
    return default_value

  try:
    if isinstance(string_list, _six.string_types):
      string_list = [_.strip() for _ in string_list.split(",")]
    else:
      string_list = [_.strip() for _ in string_list]
    string_list = [_ for _ in string_list if _]
    if not keep_case:
      string_list = [_.lower() for _ in string_list]
  except:
    raise ValueError("Invalid %s: comma-separated string or iterable of strings is required." % ((name or "string list"),))

  return string_list or default_value

def _scalar(value):
  return _numpy.array(value, copy=_SHALLOW).reshape(1)[0]

@_contextlib.contextmanager
def _suppress_history(problem):
  try:
    # Enable in-memory history and clear existing history
    original_history_settings = problem._history_inmemory, problem._history_cache
    problem._history_inmemory, problem._history_cache = True, []
  except:
    # No worry, may be that problem does not support history at all
    original_history_settings = None

  try:
    yield
  finally:
    # restore original settings, preserving new history records if we have to
    if original_history_settings:
      history_inmemory, history_cache = original_history_settings
      problem._history_inmemory = history_inmemory
      if not history_inmemory or not problem._history_cache:
        problem._history_cache = history_cache
      elif history_cache:
        problem._history_cache = history_cache + problem._history_cache

def _format_user_only_exception(exc, value, tb):
  base_path = _os.path.normcase(_os.path.normpath(_os.path.dirname(__file__))) + _os.path.sep

  error_report = []
  original_traceback = _traceback.extract_tb(tb)
  for i, (filename, _, _, _) in enumerate(original_traceback[::-1]):
    if _os.path.normcase(_os.path.normpath(filename)).startswith(base_path):
      # All subsequent stack frames were called from a user script.
      # We keep them all because the user script can call functions from external modules.
      error_report.append('Traceback (most recent call last):\n')
      error_report.extend(_traceback.format_list(original_traceback[-i:]))
      break

  error_report.extend(_traceback.format_exception_only(exc, value))
  return error_report