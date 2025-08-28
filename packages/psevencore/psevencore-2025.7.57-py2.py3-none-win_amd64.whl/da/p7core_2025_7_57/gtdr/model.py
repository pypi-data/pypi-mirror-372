#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Model - Python DR-model interface
---------------------------------

.. currentmodule:: da.p7core.gtdr.model

"""

from __future__ import with_statement
from __future__ import division

import os as _os
import warnings as _warn
from pprint import pformat
import codecs
import ctypes as _ctypes
import base64 as _base64
import numpy as _numpy
import zipfile as _zipfile
import tarfile as _tarfile

from .. import six as _six
from ..six import string_types

from .. import shared as _shared
from .. import archives as _archives
from .. import exceptions as _ex
from . import ExportedFormat
from . import GradMatrixOrder
from .. import license as _license


class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_double_p = _ctypes.POINTER(_ctypes.c_double)
    self.c_void_p_p = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_size_t_p = _ctypes.POINTER(_ctypes.c_size_t)

    _PGETSTR  = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_t_p, self.c_void_p_p)
    _PGETSIZE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_size_t_p, self.c_void_p_p)

    self._BATCH_COMPRESS = "compress".encode("ascii")
    self._BATCH_DECOMPRESS = "decompress".encode("ascii")
    self._BATCH_GRAD_COMPRESS = "grad_compress".encode("ascii")
    self._BATCH_GRAD_DECOMPRESS = "grad_decompress".encode("ascii")

    self.create_loader = _ctypes.CFUNCTYPE(_ctypes.c_void_p)(("GTDRModelLoaderNew", self.__library))
    self.delete_loader = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTDRModelLoaderFree', self.__library))
    self.last_loader_error = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_t_p)(("GTDRModelLoaderGetLastError", self.__library))
    self.load_model = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_size_t)(('GTDRModelLoaderLoad', self.__library))

    self.delete_model = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_p)(('GTDRModelFree', self.__library))

    self.read_metainfo = _PGETSTR(("GTDRModelGetMetainfo", self.__library))
    self.read_comment = _PGETSTR(("GTDRModelGetComment", self.__library))
    self.read_license = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_p, self.c_void_p_p)(("GTDRModelGetLicenseManager", self.__library))
    self.batch_calc = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_size_t, _ctypes.c_size_t,
                                        self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t,
                                        self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t,
                                        self.c_void_p_p)(("GTDRModelBatchCalc", self.__library))
    self.has_feature = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_short),
                                         self.c_void_p_p)(("GTDRModelHasFeature", self.__library))

    self.callback_single_file = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_char_p, _ctypes.c_char_p); # ret.code, archive file name, file data
    self.callback_warning = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_char_p)

    self.export_multiple_file = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.c_char_p, _ctypes.c_int, _ctypes.c_size_t, # ret. code, pointer to model, export format code, basename for archived files, model type (compress/decompress), compressed dim.
                                                  _ctypes.c_char_p, _ctypes.c_char_p, _ctypes.c_void_p, _ctypes.c_size_t, # model name, model description, file write callback (self.callback_single_file), single file size limit
                                                  _ctypes.c_void_p, self.c_void_p_p)(('GTDRModelExportToMultipleFiles', self.__library)) # warnings callback (self.callback_warning), err. data


    self.read_info = _PGETSTR(("GTDRModelGetInfo", self.__library))
    self.read_annotations = _PGETSTR(("GTDRModelGetAnnotations", self.__library))
    self.modify = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_char_p,
                                    _ctypes.c_char_p, self.c_void_p_p)(("GTDRModelModify", self.__library))
    self.read_log = _PGETSTR(("GTDRModelGetLog", self.__library))
    self.original_dim = _PGETSIZE(("GTDRModelOriginalDimension", self.__library))
    self.compressed_dim = _PGETSIZE(("GTDRModelCompressedDimension", self.__library))
    self.save = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, self.c_size_t_p, self.c_void_p_p)(('GTDRModelSave', self.__library))

    self.GT_DR_FUNCTION_TYPE_COMPRESS = 0
    self.GT_DR_FUNCTION_TYPE_DECOMPRESS = 1

    self.GTDR_MODEL_FEATURE_VARIABLE_COMPRESSION = 0

_api = _API()

class Model(object):
  """Dimension reduction model.

  Can be created by :class:`~da.p7core.gtdr.Builder` or
  loaded from a file via the :class:`~da.p7core.gtdr.Model` constructor.

  :class:`~da.p7core.gtdr.Model` objects are immutable.
  All methods which are meant to change the model return a new :class:`~da.p7core.gtdr.Model` instance.
  """
  @property
  def info(self):
    """Model description.

    :Type: ``dict``

    Contains all technical information which can be gathered from the model.

    """
    if self.__cache.get('info') is None:
      errdesc = _ctypes.c_void_p()
      size = _ctypes.c_size_t()
      self.__checkCall(self._backend.read_info(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      info = (_ctypes.c_char * size.value)()
      self.__checkCall(self._backend.read_info(self.__instance, info, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      self.__cache['info'] = _shared.parse_json_deep(_shared._preprocess_json(info.value), dict)
    return self.__cache['info']

  @property
  def details(self):
    r"""Detailed model information.

    :Type: ``dict``

    .. versionadded:: 6.14

    .. versionchanged:: 6.14.3
       added training time.

    .. versionchanged:: 6.16
       added training warnings.

    Contains training information
    and descriptions of model inputs specified when training the model
    or added using :meth:`~da.p7core.gtdr.Model.modify()`.

    The :attr:`~da.p7core.gtdr.Model.details` dictionary has the following keys:

    * ``"Input Variables"`` --- model input descriptions.
    * ``"Issues"`` ---
      training warnings extracted from :attr:`~da.p7core.gtdr.Model.build_log`.
    * ``"Training Time"`` --- time statistics.

    The value under the ``"Input Variables"`` key is a list of descriptions for original model inputs,
    list length is :attr:`~da.p7core.gtdr.Model.original_dim`.
    List order follows the order of columns in the training data sample.
    Each list element is a dictionary describing a single input.
    This dictionary has the following keys:

    * ``"name"`` (``str``) ---
      contains the name of respective input.
      This key always exists.
      If a name for this input was never specified,
      a default name (:samp:`x[{i}]`) is stored here.
    * ``"description"`` (``str``) ---
      contains a brief description for the input.
      This key exists only if the description was specified by user.
    * ``"quantity"`` (``str``) ---
      physical quantity of this input.
      This key exists only if variable's quantity was specified by user.
    * ``"unit"`` (``str``) ---
      measurement units used for this input.
      This key exists only if measurement units were specified by user.

    The value under the ``"Issues"`` key is a dictionary where
    a key is a string identifying the source of a warning,
    and value is a list containing all warnings (as strings) collected from this source.

    The value under the ``"Training Time"`` key is a dictionary with the following keys:

    * ``"Start"`` (``str``) ---
      training start time.
    * ``"Finish"`` (``str``) ---
      finish time.
    * ``"Total"`` (``str``) ---
      the difference between the start and finish times.

    Note that the total is wall time, which may be different from the real time spent in training.
    For example, if you run training on a laptop and it enters the suspend mode (sleeps)
    during training, the suspend period is included in the total time,
    while training was actually paused during suspend.

    """
    if self.__cache.get('details') is None:
      self.__cache['details'] = self.__metainfo()
    return self.__cache['details']

  def __metainfo(self):
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.read_metainfo(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    metainfo = (_ctypes.c_char * size.value)()
    self.__checkCall(self._backend.read_metainfo(self.__instance, metainfo, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    metainfo = _shared.parse_json_deep(_shared._preprocess_json(metainfo.value), dict)

    # Back compatibility
    if metainfo == {}:
      metainfo = _shared.preprocess_metainfo(None, None, self.original_dim, 0)
      metainfo.pop('Output Variables', None)
    metainfo.setdefault(u'Issues', _shared.parse_building_issues(self.build_log))
    return metainfo

  @property
  def _names_x(self):
    if self.__cache.get('_names_x') is None:
      self.__cache['_names_x'] = [_['name'] for _ in self.__metainfo().get("Input Variables", [])]
    return self.__cache['_names_x']

  @property
  def comment(self):
    """
    Text comment to the model.

    :Type: ``str``

    .. versionadded:: 6.14

    Optional plain text comment to the model.
    You can add the comment when training a model
    and edit it using :meth:`~da.p7core.gtdr.Model.modify()`.

    """
    if self.__cache.get('comment') is None:
      errdesc = _ctypes.c_void_p()
      size = _ctypes.c_size_t()
      self.__checkCall(self._backend.read_comment(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      comment = (_ctypes.c_char * size.value)()
      self.__checkCall(self._backend.read_comment(self.__instance, comment, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      self.__cache['comment'] = _shared._preprocess_utf8(comment.value)
    return self.__cache['comment']

  @property
  def annotations(self):
    """
    Extended comment or supplementary information.

    :Type: ``dict``

    .. versionadded:: 6.14

    The annotations dictionary can optionally contain any number of notes.
    All dictionary keys and values are strings.
    You can add annotations when training a model
    and edit them using :meth:`~da.p7core.gtdr.Model.modify()`.

    """
    if self.__cache.get('annotations') is None:
      errdesc = _ctypes.c_void_p()
      size = _ctypes.c_size_t()
      self.__checkCall(self._backend.read_annotations(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      annotations = (_ctypes.c_char * size.value)()
      self.__checkCall(self._backend.read_annotations(self.__instance, annotations, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      self.__cache['annotations'] = _shared.parse_json_deep(_shared._preprocess_json(annotations.value), dict)
    return self.__cache['annotations']

  def modify(self, comment=None, annotations=None, x_meta=None):
    """Create a copy of the model with modified metainformation.

    :param comment: new comment
    :param annotations: new annotations
    :param x_meta: descriptions of inputs
    :type comment: ``str``
    :type annotations: ``dict``
    :type x_meta: ``list``
    :return: model copy with modified information
    :rtype: :class:`~da.p7core.gtdr.Model`

    .. versionadded:: 6.14

    This method is intended to edit model
    :attr:`~da.p7core.gtdr.Model.annotations`,
    :attr:`~da.p7core.gtdr.Model.comment`, and
    input descriptions found in :attr:`~da.p7core.gtdr.Model.details`.
    Parameters are similar to :meth:`~da.p7core.gtdr.Builder.build()` --- see the full description there.
    If a parameter is ``None``, corresponding information in the modified model remains unchanged.
    If you specify a parameter, corresponding information in the modified model is fully replaced.

    Note that :meth:`~da.p7core.gtdr.Model.modify()`
    returns a new modified model, which is identical to the original
    except your edits to the model metainformation.

    """
    metainfo = self.__metainfo()

    if x_meta is not None:
      new_metainfo = _shared.preprocess_metainfo(x_meta, None, self.original_dim, 0, ignorable_keys=_shared.collect_metainfo_keys(metainfo))
      metainfo.update({'Input Variables': new_metainfo['Input Variables']})

    return self.__modify(comment=comment, annotations=annotations, metainfo=metainfo)

  def __modify(self, comment=None, annotations=None, metainfo=None):
    """
    Create a copy of the model with modified additional information.
    """
    if comment is None and annotations is None and metainfo is None:
      return self

    # Prepare comment pointer
    if comment is not None:
      if not isinstance(comment, string_types):
        comment = _shared.write_json(comment)
      else:
        comment = comment.strip()

      try:
        comment_ptr = comment.encode('utf-8')
      except (AttributeError, UnicodeDecodeError):
        comment_ptr = comment
    else:
      comment_ptr = _ctypes.c_char_p()

    # Prepare annotations pointer
    annotations_ptr = _shared.write_json(annotations).encode('ascii') if annotations is not None else _ctypes.c_char_p()

    # Prepare metainfo pointer
    metainfo_ptr = _shared.write_json(metainfo).encode('ascii') if metainfo is not None else _ctypes.c_char_p()

    # Modify model
    errdesc = _ctypes.c_void_p()
    handle = self._backend.modify(self.__instance, comment_ptr, annotations_ptr, metainfo_ptr, _ctypes.byref(errdesc))
    if not handle:
      _shared.ModelStatus.checkErrorCode(0, 'Failed to modify model.', errdesc)
    return Model(handle=handle)

  @property
  def license(self):
    """Model license.

    :type: :class:`~da.p7core.License`

    General license information interface. See section :ref:`gen_license_usage` for details.

    """
    errdesc = _ctypes.c_void_p()
    obj = _ctypes.c_void_p()
    self.__checkCall(self._backend.read_license(self.__instance, _ctypes.byref(obj), _ctypes.byref(errdesc)), errdesc)
    return _license.License(obj, self.__instance)

  @property
  def build_log(self):
    """
    Model building log.

    :Type: ``str``

    """
    if self.__cache.get('log') is None:
      errdesc = _ctypes.c_void_p()
      size = _ctypes.c_size_t()
      self.__checkCall(self._backend.read_log(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      log = (_ctypes.c_char * size.value)()
      self.__checkCall(self._backend.read_log(self.__instance, log, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      self.__cache['log'] = _shared._preprocess_utf8(log.value)
    return self.__cache['log']

  @property
  def original_dim(self):
    """
    Original (uncompressed) vector dimension.

    :Type: ``long``

    """
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.original_dim(self.__instance, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    return size.value

  @property
  def compressed_dim(self):
    """Compressed vector dimension.

    :Type: ``long`` or ``None``

    This attribute is ``None`` if the model supports variable-dimension compression.

    """
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.compressed_dim(self.__instance, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    if size.value == _ctypes.c_size_t(-1).value:
      return None
    return size.value

  def __str__(self):
    info = _six.StringIO()
    if self.comment:
      info.write(_shared._safestr(self.comment).rstrip(" \n") + "\n")

    info_list = []
    if self.annotations:
      info_list.append("annotations")

    compressed_dim = "variable" if not self.compressed_dim else (str(self.compressed_dim) \
                   + (" (variable)" if self.has_variable_compression else " (fixed)"))

    info.write("Original dimension:   %d\n" % self.original_dim)
    info.write("Compressed dimension: %s\n" % compressed_dim)
    info.write("Attachments:          %s\n" % (", ".join(info_list) if info_list else "-"))
    info.write("Training Time:        %s\n" % self.details.get("Training Time", {}).get("Total", "-"))

    return info.getvalue()

  def __actualDim(self, dim):
    if self.__variable_compression:
      if dim is None:
        if self.compressed_dim is None:
          raise ValueError('You must choose desired compressed vector dimensionality!')
        else:
          dim = self.compressed_dim
      else:
        _shared.check_concept_int(dim, "desired compressed vector dimensionality")
      if dim <= 0 or dim > self.original_dim:
        raise ValueError('Wrong desired compressed vector dimensionality!')
    elif dim is None or dim == self.compressed_dim:
      dim = self.compressed_dim
    else:
      raise ValueError('Model does not support variable compressed vector dimensionality!')
    return dim

  def compress(self, vec, dim=None):
    """Compression method.

    :param vec: vector(s) to compress
    :keyword dim: required dimension
    :type vec: :term:`array-like`, 2D or 1D
    :type dim: ``int``, ``long``
    :return: compressed vectors
    :rtype: ``pandas.DataFrame`` or ``pandas.Series`` if :arg:`vec` is a pandas type; otherwise ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`vec` is a pandas data type.

    Compresses a vector (1D) or each of vectors in a batch (2D).
    Vector length must be equal to :attr:`~da.p7core.gtdr.Model.original_dim`.

    When using pandas, the return type is the same as the :arg:`vec` type.
    Also in this case the returned array keeps indexing of :arg:`vec`.

    """
    input, single_vector = _shared.as_matrix(vec, shape=(None, self.original_dim), ret_is_vector=True, order='A', name="Vector(s) to compress ('vec' argument)")
    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')

    compressed_size = self.__actualDim(dim)
    output = _numpy.ndarray((input.shape[0], compressed_size), dtype=float, order='C')
    errdesc = _ctypes.c_void_p()

    if not self._backend.batch_calc(self.__instance, self._backend._BATCH_COMPRESS, len(input), compressed_size, \
                                    input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    output.ctypes.data_as(self._backend.c_double_p), \
                                    output.strides[0] // output.itemsize, output.strides[1] // output.itemsize, 1, \
                                    _ctypes.byref(errdesc)):
      _shared.ModelStatus.checkErrorCode(0, 'Failed to compress input data.', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(vec, single_vector, self._names_x)
    if pandas_index is not None:
      return _shared.make_pandas(output, single_vector, pandas_type, pandas_index, None)
    else:
      return output[0] if single_vector else output

  def _check_compressed_size(self, vec_size):
    if self.__variable_compression:
      if vec_size <= 0 or vec_size > self.original_dim:
        raise ValueError('Wrong input vector dimensionality!')
    elif vec_size != self.compressed_dim:
      raise ValueError('Wrong input vector dimensionality, technique does not support variable compressed vector size!')

  def decompress(self, vec):
    """Decompression method.

    :param vec: vector(s) to decompress
    :type vec: :term:`array-like`, 2D or 1D
    :return: decompressed vectors
    :rtype: ``pandas.DataFrame`` or ``pandas.Series`` if :arg:`vec` is a pandas type; otherwise ``ndarray``, 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`vec` is a pandas data type.

    Decompresses a vector (1D) or each of the vectors in a batch (2D).
    The vector length should be equal to :attr:`~da.p7core.gtdr.Model.compressed_dim` for a model with fixed-dimension compression,
    and no more than :attr:`~da.p7core.gtdr.Model.original_dim` for a model with variable-dimension compression.

    When using pandas, the return type is the same as the :arg:`vec` type.
    Also in this case the returned array keeps indexing of :arg:`vec`.
    """
    if not self.__variable_compression:
      input, single_vector = _shared.as_matrix(vec, shape=(None, self.compressed_dim), ret_is_vector=True, order='A', name="Vector(s) to decompress ('vec' argument)")
    else:
      input, single_vector = _shared.as_matrix(vec, ret_is_vector=True, order='A', name="Vector(s) to decompress ('vec' argument)")
      if single_vector and input.shape[0] > 1:
        input = input.reshape((1, input.shape[0]))

    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')

    compressed_size = input.shape[1]
    self._check_compressed_size(compressed_size)

    output = _numpy.ndarray((input.shape[0], self.original_dim), dtype=float, order='C')
    errdesc = _ctypes.c_void_p()

    if not self._backend.batch_calc(self.__instance, self._backend._BATCH_DECOMPRESS, len(input), compressed_size, \
                                    input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    output.ctypes.data_as(self._backend.c_double_p), \
                                    output.strides[0] // output.itemsize, output.strides[1] // output.itemsize, 1, \
                                    _ctypes.byref(errdesc)):
      _shared.ModelStatus.checkErrorCode(0, 'Failed to decompress input data.', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(vec, single_vector, None) # Do not check column names
    if pandas_index is not None:
      return _shared.make_pandas(output, single_vector, pandas_type, pandas_index,  self._names_x)
    else:
      return output[0] if single_vector else output

  @property
  def has_variable_compression(self):
    """Variable-dimension compression support.

    :Type: ``bool``

    If ``True``, the model supports variable-dimension compression.

    """
    return self.__hasFeature(self._backend.GTDR_MODEL_FEATURE_VARIABLE_COMPRESSION)

  def gradCompress(self, vec, dim=None, order=GradMatrixOrder.F_MAJOR):
    """Evaluate compression transformation gradient.

    :param vec: vector(s) to evaluate
    :keyword dim: required dimension
    :keyword order: gradient matrix order
    :type vec: :term:`array-like`, 2D or 1D
    :type dim: ``int``, ``long``
    :type order: :class:`GradMatrixOrder`
    :return: gradients
    :rtype: ``pandas.DataFrame`` if :arg:`vec` is a pandas type; otherwise ``ndarray``, 3D or 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`vec` is a pandas data type.

    Evaluates compression transformation gradients for a data sample
    (if :arg:`vec` is a 2D array-like) or a single vector (if :arg:`vec` is 1D).
    The returned array is 3D if :arg:`vec` is a sample, and 2D if :arg:`vec` is a single vector.

    When using pandas data samples (:arg:`vec` is a ``pandas.DataFrame``),
    a 3D array in return value is represented by a ``pandas.DataFrame`` with multi-indexing (``pandas.MultiIndex``).
    In this case, the first element of the multi-index is the index of a vector from the input sample.
    The second element of the multi-index is:

    * the index or name of a model's output,
      if :arg:`order` is :attr:`~da.p7core.gtdr.GradMatrixOrder.F_MAJOR` (default)
    * the index or name of a model's input,
      if :arg:`order` is :attr:`~da.p7core.gtdr.GradMatrixOrder.X_MAJOR`

    When :arg:`vec` is a ``pandas.Series``,
    its index becomes the row index of the returned ``pandas.DataFrame``.

    """
    input, single_vector = _shared.as_matrix(vec, shape=(None, self.original_dim), ret_is_vector=True, order='A', name="Point(s) to evaluate compression transformation gradient ('vec' argument)")
    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')
    dim = self.__actualDim(dim)
    result = self.__grad(input, order, False, dim)

    pandas_index, pandas_type = _shared.get_pandas_info(vec, single_vector, self._names_x)
    if pandas_index is not None:
      major_names = _numpy.arange(dim) if order == GradMatrixOrder.F_MAJOR else self._names_x
      minor_names = self._names_x if order == GradMatrixOrder.F_MAJOR else _numpy.arange(dim)
      return _shared.make_pandas_grad(result, single_vector, pandas_type, pandas_index, major_names, minor_names)
    else:
      return result[0] if single_vector else result

  def gradDecompress(self, vec, order=GradMatrixOrder.F_MAJOR):
    """Evaluate decompression transformation gradient.

    :param vec: vector(s) to evaluate
    :keyword order: gradient matrix order
    :type vec: :term:`array-like`, 2D or 1D
    :type order: :class:`GradMatrixOrder`
    :return: gradients
    :rtype: ``pandas.DataFrame`` if :arg:`vec` is a pandas type; otherwise ``ndarray``, 3D or 2D

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`vec` is a pandas data type.

    Evaluates decompression transformation gradients for a data sample
    (if :arg:`vec` is a 2D array-like) or a single vector (if :arg:`vec` is 1D).
    The returned array is 3D if :arg:`vec` is a sample, and 2D if :arg:`vec` is a single vector.

    When using pandas data samples (:arg:`vec` is a ``pandas.DataFrame``),
    a 3D array in return value is represented by a ``pandas.DataFrame`` with multi-indexing (``pandas.MultiIndex``).
    In this case, the first element of the multi-index is the index of a vector from the input sample.
    The second element of the multi-index is:

    * the index or name of a model's output,
      if :arg:`order` is :attr:`~da.p7core.gtdr.GradMatrixOrder.F_MAJOR` (default)
    * the index or name of a model's input,
      if :arg:`order` is :attr:`~da.p7core.gtdr.GradMatrixOrder.X_MAJOR`

    When :arg:`vec` is a ``pandas.Series``,
    its index becomes the row index of the returned ``pandas.DataFrame``.

    """
    if not self.__variable_compression:
      input, single_vector = _shared.as_matrix(vec, shape=(None, self.compressed_dim), ret_is_vector=True, order='A', name="Point(s) to evaluate decompression transformation gradient ('vec' argument)")
    else:
      input, single_vector = _shared.as_matrix(vec, ret_is_vector=True, order='A', name="Point(s) to evaluate decompression transformation gradient ('vec' argument)")
      if single_vector and input.shape[0] > 1:
        input = input.reshape((1, input.shape[0]))
    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')
    self._check_compressed_size(input.shape[1])
    result = self.__grad(input, order, True, input.shape[1])

    pandas_index, pandas_type = _shared.get_pandas_info(vec, single_vector, self._names_x)
    if pandas_index is not None:
      major_names = self._names_x if order == GradMatrixOrder.F_MAJOR else _numpy.arange(input.shape[1])
      minor_names = _numpy.arange(input.shape[1]) if order == GradMatrixOrder.F_MAJOR else self._names_x
      return _shared.make_pandas_grad(result, single_vector, pandas_type, pandas_index, major_names, minor_names)
    else:
      return result[0] if single_vector else result

  def __grad(self, input, order, is_decompress, compressed_dim):

    if is_decompress:
      mode = self._backend._BATCH_GRAD_DECOMPRESS
      size_arg = compressed_dim
      size_func = self.original_dim
    else:
      mode = self._backend._BATCH_GRAD_COMPRESS
      size_arg = self.original_dim
      size_func = compressed_dim

    vectorsNumber = input.shape[0]
    if order == GradMatrixOrder.X_MAJOR:
      output = _numpy.ndarray((vectorsNumber, size_arg, size_func), dtype=_numpy.float64, order='C')
      df_axis, dx_axis = 2, 1
    elif order == GradMatrixOrder.F_MAJOR:
      output = _numpy.ndarray((vectorsNumber, size_func, size_arg), dtype=_numpy.float64, order='C')
      df_axis, dx_axis = 1, 2
    else:
      raise ValueError('Wrong "order" value!')

    errdesc = _ctypes.c_void_p()
    if not self._backend.batch_calc(self.__instance, mode, len(input), compressed_dim, \
                                    input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    output.ctypes.data_as(self._backend.c_double_p), output.strides[0] // output.itemsize, \
                                    output.strides[df_axis] // output.itemsize, output.strides[dx_axis] // output.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared.ModelStatus.checkErrorCode(0, 'Gradient evaluation error', errdesc)

    return output

  def compress_export_to(self, format, name, description, file, dim=None, single_file=None):
    """Export the compression procedure to a source file in specified format.

    :param format: source code format
    :param name: exported function name
    :param description: additional comment
    :param file: export file or path
    :param dim: required compressed dimension
    :param single_file: export sources as a single file (default) or multiple files (``False``)
    :type format: :class:`ExportedFormat` or ``str``
    :type name: ``str``
    :type description: ``str``
    :type file: file-like, ``str``, ``zipfile.ZipFile``, ``tarfile.TarFile``
    :type dim: ``int`` or ``long``
    :type single_file: ``bool``
    :return: ``None``
    :raise: :exc:`~da.p7core.GTException` if :arg:`name` is empty and :arg:`format` is not :attr:`~da.p7core.gtdr.ExportedFormat.C99_PROGRAM`

    .. versionadded:: 6.10
       added ``str`` aliases for export formats.

    .. versionchanged:: 6.24
       added the support for exporting sources to archives; added the :arg:`single_file` parameter.

    Generates the model source code in the specified :arg:`format` and saves it
    to a file or a set of source files.
    Supports packing the source code to various archive file formats.

    The source code format can be specified using an enumeration or a string alias
    --- see :class:`ExportedFormat` for details.

    By default, all source code is exported to a single file.
    This mode is not recommended for large models,
    since large source files can cause problems during compilation.
    To split the source code into multiple files, set :arg:`single_file` to ``False``.
    In this case, the filename from :arg:`file` serves as a basename,
    and additional source files have names with an added suffix.
    In the multi-file mode, all exported files are required to compile the model.

    To pack source files into an archive, you can pass a ``zipfile.ZipFile`` or ``tarfile.TarFile``
    object as :arg:`file`, or specify a path to the file wit an archive type extension.
    Recognized extensions are: ``.zip``, ``.tar``, ``.tgz``, ``.tar.gz``, ``.taz``, ``.tbz``, ``.tbz2``, ``.tar.bz2``.

    The :arg:`name` argument is optional if :arg:`format` is :attr:`~da.p7core.gtdr.ExportedFormat.C99_PROGRAM`.
    For other source code formats, an empty name raises an exception.

    The :arg:`description` provides an additional comment,
    which is added on top of the generated source file.

    """
    self.__export_to(format, self._backend.GT_DR_FUNCTION_TYPE_COMPRESS, dim, name, description, file, single_file)

  def decompress_export_to(self, format, name, description, file, dim=None, single_file=None):
    """Export the decompression procedure to a source file in specified format.

    :param format: source code format
    :param name: exported function name
    :param description: additional comment
    :param file: export file or path
    :keyword dim: required compressed dimension
    :param single_file: export sources as a single file (default) or multiple files (``False``)
    :type format: :class:`ExportedFormat` or ``str``
    :type name: ``str``
    :type description: ``str``
    :type file: file-like, ``str``, ``zipfile.ZipFile``, ``tarfile.TarFile``
    :type dim: ``int`` or ``long``
    :type single_file: ``bool``
    :return: ``None``
    :raise: :exc:`~da.p7core.GTException` if *name* is empty and :arg:`format` is not :attr:`~da.p7core.gtdr.ExportedFormat.C99_PROGRAM`

    .. versionadded:: 6.10
       added ``str`` aliases for export formats.

    .. versionchanged:: 6.24
       added the support for exporting sources to archives; added the :arg:`single_file` parameter.

    Generates the model source code in the specified :arg:`format` and saves it
    to a file or a set of source files.
    Supports packing the source code to various archive file formats.

    The source code format can be specified using an enumeration or a string alias
    --- see :class:`ExportedFormat` for details.

    By default, all source code is exported to a single file.
    This mode is not recommended for large models,
    since large source files can cause problems during compilation.
    To split the source code into multiple files, set :arg:`single_file` to ``False``.
    In this case, the filename from :arg:`file` serves as a basename,
    and additional source files have names with an added suffix.
    In the multi-file mode, all exported files are required to compile the model.

    To pack source files into an archive, you can pass a ``zipfile.ZipFile`` or ``tarfile.TarFile``
    object as :arg:`file`, or specify a path to the file wit an archive type extension.
    Recognized extensions are: ``.zip``, ``.tar``, ``.tgz``, ``.tar.gz``, ``.taz``, ``.tbz``, ``.tbz2``, ``.tar.bz2``.

    The :arg:`name` argument is optional if :arg:`format` is :attr:`~da.p7core.gtdr.ExportedFormat.C99_PROGRAM`.
    For other source code formats, an empty name raises an exception.

    The :arg:`description` provides an additional comment,
    which is added on top of the generated source file.

    """
    self.__export_to(format, self._backend.GT_DR_FUNCTION_TYPE_DECOMPRESS, dim, name, description, file, single_file)

  def __export_to(self, format, ftype, dim, name, description, file, single_file):
    dim = self.__actualDim(dim)
    format = ExportedFormat.from_string(format)

    _shared.check_type(name, 'function name argument', string_types)
    _shared.check_type(description, 'exported function description argument', string_types)

    def _validate_function(name, allow_empty, defname):
      if len(name) == 0:
        if format in allow_empty and defname:
          return defname
        raise _ex.GTException('The name of function must be not empty!')
      return name

    description = _ctypes.c_char_p(description.encode("utf8"))

    if single_file is None:
      single_file = True # backward compatibility mode
    file_size = _ctypes.c_size_t(_numpy.iinfo(_ctypes.c_size_t).max if single_file else _debug_export_file_size(format)*1024)

    errdesc = _ctypes.c_void_p()
    warnings_callback = self._backend.callback_warning(_shared.forward_warn)

    if isinstance(file, _six.string_types):
      file_path, file_base = _os.path.split(file)
      file_base, tar_mode = _archives._detect_tar_mode(file_base)

      name = _validate_function(name, (ExportedFormat.C99_PROGRAM, ExportedFormat.OCTAVE), file_base.split('.')[0])

      with open(file, 'w') as fid:
        pass # test file open

      if tar_mode is not None:
        # tar file export
        with _archives._with_tarfile(file, tar_mode) as fobj:
          file_writer = _archives._TarArchiveWriter(fobj)
          #err = self._backend.export_to_file(self.__instance, format, ftype, dim, name, description, codecs.encode(file, 'utf8'), logger, _ctypes.byref(errdesc))

          succeeded =  self._backend.export_multiple_file(self.__instance, format, file_base.encode("utf8"),
                                                          ftype, dim, _ctypes.c_char_p(name.encode("utf8")), description,
                                                          self._backend.callback_single_file(file_writer), file_size,
                                                          warnings_callback, _ctypes.byref(errdesc))
          file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))
      elif file_base[-4:].lower() == ".zip":
        # zip file export
        with _archives._with_zipfile(file, "w") as fobj:
          file_writer = _archives._ZipArchiveWriter(fobj)
          succeeded =  self._backend.export_multiple_file(self.__instance, format, file_base[:-4].encode("utf8"),
                                                          ftype, dim, _ctypes.c_char_p(name.encode("utf8")), description,
                                                          self._backend.callback_single_file(file_writer), file_size,
                                                          warnings_callback, _ctypes.byref(errdesc))
          file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))
      else:
        if format == ExportedFormat.OCTAVE and name != _os.path.splitext(file_base)[0]:
          #raise ValueError("Octave requires match of the function name (%s) and base name of the file (%s)." % (name, _os.path.splitext(file_base)[0]))
          _warn.warn("Octave requires match of the function name (%s) and base name of the file (%s)." % (name, _os.path.splitext(file_base)[0]))
        file_writer = _archives._DirectoryWriter(file_path or _six.moves.getcwd(), (file if single_file else None))
        succeeded =  self._backend.export_multiple_file(self.__instance, format, _os.path.splitext(file_base)[0].encode("utf8"),
                                                        ftype, dim, _ctypes.c_char_p(name.encode("utf8")), description,
                                                        self._backend.callback_single_file(file_writer), file_size,
                                                        warnings_callback, _ctypes.byref(errdesc))
        file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))
    else:
      _validate_function(name, (ExportedFormat.C99_PROGRAM,), None)

      postprocess = False
      if isinstance(file, _zipfile.ZipFile):
        file_writer = _archives._ZipArchiveWriter(file)
      elif isinstance(file, _tarfile.TarFile):
        file_writer = _archives._TarArchiveWriter(file)
      else:
        file_writer = _archives._MemoryFileWriter()
        file_size = _ctypes.c_size_t(_numpy.iinfo(_ctypes.c_size_t).max) # force single file mode
        postprocess = True

      succeeded =  self._backend.export_multiple_file(self.__instance, format, name,
                                                      ftype, dim, _ctypes.c_char_p(name.encode("utf8")), description,
                                                      self._backend.callback_single_file(file_writer), file_size,
                                                      warnings_callback, _ctypes.byref(errdesc))
      file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))

      if postprocess:
        try:
          for fname, source_code in file_writer.files:
            file.write(source_code)
            file.write("\n")
          return
        except AttributeError:
          pass

        with open(file, 'w') as fid:
          for fname, source_code in file_writer.files:
            file.write(source_code)
            file.write("\n")

  def save(self, file):
    """Save the model to file.

    :param file: file object or path
    :type file: ``file`` or ``str``
    :return: ``None``

    """
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.save(self.__instance, _ctypes.c_void_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    data = _ctypes.create_string_buffer(size.value)
    self.__checkCall(self._backend.save(self.__instance, data, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)

    try:
      file.write(data.raw)
      return
    except AttributeError:
      pass

    with open(file, 'wb') as fid:
      fid.write(data.raw)

  def tostring(self):
    """Serialize the model.

    :return: serialized model
    :rtype: ``str``

    """
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.save(self.__instance, _ctypes.c_void_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    data = _ctypes.create_string_buffer(size.value)
    self.__checkCall(self._backend.save(self.__instance, data, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    return _base64.b64encode(data.raw)

  def load(self, file):
    """Load a model from file.

    :param file: file object or path
    :type file: ``file`` or ``str``
    :return: ``None``

    .. deprecated:: 6.29
       use :class:`~da.p7core.gtdr.Model` constructor instead.

    """
    try:
      data = file.read(-1)
    except AttributeError:
      data = None

    if data is None:
      with open(file, 'rb') as fid:
        data = fid.read(-1)

    self.__reload_model(data)

  def fromstring(self, modelString):
    """Deserialize a model from string.

    :param modelString: serialized model
    :type modelString: ``str``
    :return: ``None``

    """
    binary_data = _shared.wrap_with_exc_handler(_base64.b64decode, _ex.GTException)(modelString)
    self.__reload_model(binary_data)

  # Constructor
  def __init__(self, file=None, **kwargs):
    self.__init_self()
    handle = kwargs.get('handle')
    if not handle:
      modelString = kwargs.get('string')
      if modelString and file:
        raise ValueError("Only one argument 'file' or 'string' must be set")
      if modelString:
        self.fromstring(modelString)
      elif file:
        self.load(file)
      else:
        raise ValueError("'file' argument must be file object or file name")
    else:
      self.__instance = handle
    self.__variable_compression = self.__hasFeature(self._backend.GTDR_MODEL_FEATURE_VARIABLE_COMPRESSION)

  def __getstate__(self):
    # version 1 has the following keys:
    #   'version' - version number, integer 1
    #   'model_data' - binary model data returned by tostring() method
    return {'version': 1,
            'model_data': self.tostring(),}

  def __setstate__(self, dict):
    self.__init_self()
    if 1 == dict['version']:
      self.fromstring(dict['model_data'])
    else:
      raise ValueError("Invalid or unsupported model data given.")

  def __init_self(self):
    self._backend = self._default_backend()
    self.__instance = None
    self.__cache = {}

  @staticmethod
  def _default_backend(backend=_api):
    # intentionally assign single shared _api object as default value so we keep backend loaded as long as this method exists
    return _api if backend is None else backend

  def __reload_model(self, binary_data):
    if self.__instance is not None:
      self._backend.delete_model(self.__instance, _ctypes.c_void_p())
      self.__instance = None
      self.__cache = {}

    loader = _ctypes.c_void_p(self._backend.create_loader())
    if not loader:
      raise _ex.GTException('Failed to initialize model loader!')

    try:
      self.__instance = _ctypes.c_void_p(self._backend.load_model(loader, binary_data, len(binary_data)))
      # lastError support
      errorInfoMessage = 'Failed to load model!'
      if not self.__instance:
        errorSize = _ctypes.c_size_t()
        self._backend.last_loader_error(loader, _ctypes.c_char_p(), _ctypes.byref(errorSize))
        errorInfo = (_ctypes.c_char * errorSize.value)()
        self._backend.last_loader_error(loader, errorInfo, _ctypes.byref(errorSize))
        if errorInfo:
          errorInfoMessage = _shared._preprocess_utf8(errorInfo.value)
    finally:
      self._backend.delete_loader(loader)

      if not self.__instance:
        raise _ex.GTException(errorInfoMessage)
      self.__variable_compression = self.__hasFeature(self._backend.GTDR_MODEL_FEATURE_VARIABLE_COMPRESSION)

  def __hasFeature(self, feature):
    errdesc = _ctypes.c_void_p()
    result = _ctypes.c_short()
    err = self._backend.has_feature(self.__instance, _ctypes.c_int(feature), _ctypes.byref(result), _ctypes.byref(errdesc))
    _shared.ModelStatus.checkErrorCode(err, 'Failed to get model feature state!', errdesc)
    return result.value > 0

  def __checkCall(self, err, errdesc):
    _shared.ModelStatus.checkErrorCode(err, 'C call failed!', errdesc)

  # Destructor.
  def __del__(self):
    self._backend.delete_model(self.__instance, self._backend.c_void_p_p())

_FILE_SIZE_THRESHOLD = {}

def _debug_export_file_size(format, file_size=None):
  if file_size is not None:
    file_size = int(file_size)
    if file_size < 0:
      raise ValueError("File size threshold must be non-negative")

  norm_format = ExportedFormat.from_string(format)

  if file_size is not None:
    _FILE_SIZE_THRESHOLD[norm_format] = file_size

  return _FILE_SIZE_THRESHOLD.get(norm_format, 0)
