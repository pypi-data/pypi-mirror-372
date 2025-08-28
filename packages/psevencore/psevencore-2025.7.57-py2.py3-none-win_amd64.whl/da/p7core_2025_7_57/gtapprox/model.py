#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Approximation model.

.. currentmodule:: da.p7core.gtapprox.model

"""

from __future__ import with_statement
from __future__ import division

import sys as _sys
import os as _os
import warnings as _warn
from pprint import pformat
import codecs as _codecs
import ctypes as _ctypes
import base64 as _base64
import numpy as _numpy
import zipfile as _zipfile
import tarfile as _tarfile

from .. import six as _six
from .. import shared as _shared
from .. import archives as _archives
from .. import exceptions as _ex
from . import GradMatrixOrder
from . import ExportedFormat
from . import details as _details
from .. import parameters as _parameters
from . import smoothing as _smoothing
from .. import license as _license

class _API(object):
  @staticmethod
  def read_str(instance, reader):
    errdesc = _ctypes.c_void_p()
    data = _shared._unsafe_allocator()
    _shared._raise_on_error(reader(instance, data.callback, _ctypes.byref(errdesc)), \
                            "Failed to read string data from the backend.", errdesc)
    return data.value

  def __init__(self):
    self.__library = _shared._library

    self.c_double_p = _ctypes.POINTER(_ctypes.c_double)
    self.c_void_p_p = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_size_t_p = _ctypes.POINTER(_ctypes.c_size_t)

    PGETSTR = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_t_p, self.c_void_p_p)
    PGETSIZE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_size_t_p, self.c_void_p_p)
    PGETSTR2 = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, self.c_void_p_p)

    # deprecated methods. keep for backward compatibility only
    self.get_info = PGETSTR(("GTApproxModelGetInfo", self.__library))
    self.get_comment = PGETSTR(("GTApproxModelGetComment", self.__library))
    self.get_log = PGETSTR(("GTApproxModelGetLog", self.__library))
    self.get_annotations = PGETSTR(("GTApproxModelGetAnnotations", self.__library))
    self.get_metainfo = PGETSTR(("GTApproxModelGetMetainfo", self.__library))
    self.get_variables_info = PGETSTR(("GTApproxModelVariablesInfo", self.__library))
    # end of depreceted methods

    self._get_info = PGETSTR2(("GTApproxModelGetInfo2", self.__library))
    self._get_comment = PGETSTR2(("GTApproxModelGetComment2", self.__library))
    self._get_log = PGETSTR2(("GTApproxModelGetLog2", self.__library))
    self._get_annotations = PGETSTR2(("GTApproxModelGetAnnotations2", self.__library))
    self._get_metainfo = PGETSTR2(("GTApproxModelGetMetainfo2", self.__library))
    self._get_variables_info = PGETSTR2(("GTApproxModelVariablesInfo2", self.__library))

    self.get_size_x = PGETSIZE(("GTApproxModelGetSizeX", self.__library))
    self.get_size_f = PGETSIZE(("GTApproxModelGetSizeF", self.__library))
    self.get_size_p = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_size_t_p, self.c_void_p_p)(("GTApproxModelGetSizeP", self.__library))
    self.model_training_domains = PGETSTR(('GTApproxModelTrainingDomains', self.__library))
    self.read_license = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_p, self.c_void_p_p)(("GTApproxModelGetLicenseManager", self.__library))
    self.get_parameters = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_p, self.c_void_p_p)(("GTApproxModelGetParameters", self.__library))
    self.delete_model = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_p)(('GTApproxModelFree', self.__library))
    self.split_model_outputs = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_size_t, self.c_size_t_p,
                                                 _ctypes.c_size_t, self.c_void_p_p, self.c_void_p_p)(('GTApproxModelSplitOutputs2', self.__library))

    self.batch_calc = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, self.c_void_p_p)(("GTApproxModelBatchCalc", self.__library))
    self.batch_calc_pe = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_short, _ctypes.c_size_t, _ctypes.c_char_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, self.c_void_p_p)(("GTApproxModelBatchCalcP", self.__library))

    self.callback_single_file = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_char_p, _ctypes.c_char_p); # ret.code, archive file name, file data
    self.callback_warning = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_char_p)

    self.check_input = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, self.c_void_p_p)(("GTApproxModelValidateInput", self.__library))
    self.export_multiple_file = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.c_char_p, _ctypes.c_char_p, # ret. code, pointer to model, export format code, basename for archived files, model name
                                                  _ctypes.c_char_p, _ctypes.c_void_p, _ctypes.c_size_t, # model description, file write callback (self.callback_single_file), single file size limit
                                                  _ctypes.c_void_p, self.c_void_p_p)(('GTApproxModelExportToMultipleFiles', self.__library)) # warnings callback (self.callback_warning), err. data
    self.validation_errors_list = PGETSTR(("GTApproxModelValidationErrorsList", self.__library))
    self.validate_weighted = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, self.c_void_p_p)(("GTApproxModelValidateWeighted", self.__library))
    self.save_model = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, self.c_size_t_p,  _ctypes.c_uint, self.c_void_p_p)(('GTApproxModelSelectiveSave', self.__library))
    self.has_feature = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_short), self.c_void_p_p)(("GTApproxModelHasFeature", self.__library))
    self.train_sample_count = PGETSIZE(("GTApproxModelGetTrainSampleCount", self.__library))
    self.get_train_sample = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_int, self.c_size_t_p, self.c_size_t_p, self.c_size_t_p, self.c_void_p_p, self.c_void_p_p)(("GTApproxModelGetTrainSample", self.__library))
    self.modify_model = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_char_p, _ctypes.c_char_p, _ctypes.c_char_p, self.c_void_p_p)(("GTApproxModelModify", self.__library))
    self.enum_load_sections = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_short, _ctypes.POINTER(_ctypes.c_uint), self.c_void_p_p)(("GTApproxModelAvailableLoadSections", self.__library))
    self.enum_save_sections = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_uint), self.c_void_p_p)(("GTApproxModelAvailableSaveSections", self.__library))
    self.create_loader = _ctypes.CFUNCTYPE(_ctypes.c_void_p)(("GTApproxModelLoaderNew", self.__library))
    self.selective_load = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_uint)(('GTApproxModelLoaderSelectiveLoad', self.__library))
    self.last_loader_error = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_t_p)(("GTApproxModelLoaderGetLastError", self.__library))
    self.delete_loader = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTApproxModelLoaderFree', self.__library))
    self.shapley_value = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_size_t, # ret.code, model, mode, n vectors
                                           self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, # [in] x, next x vector, next x vector element
                                           _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, # [in, optional] n bkgnd vectors, bkgnd, next bkgnd vector, next bkgnd vector element
                                           self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t, # [out] shap., next shap vector, next f, next shap value
                                           _ctypes.c_void_p, self.c_void_p_p)(("GTApproxModelShapleyValue", self.__library)) # err. data

    self.find_extrema = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, # ret.code, model,
                                           self.c_double_p, self.c_size_t_p, # [in] values: flatten list of lists representing search bounds, row_index: values[row_index[i]:row_index[i+1]] is i-th list in values,
                                           self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, # [out] output data, output inc row, output inc col,
                                           self.c_void_p_p)(("GTApproxFindModelExtrema", self.__library)) # err. data

    self.enum_compatible_tech_list = PGETSTR2(("GTApproxModelCompatibleIncrementalTrainingTechniques", self.__library))

    self.FEATURE_ACCURACY_EVALUATION = 0
    self.FEATURE_STATIC_SMOOTHNESS = 1
    self.FEATURE_SMOOTHED = 2
    self.FEATURE_CALC_LOADED = 3
    self.FEATURE_PROBABILITY_ESTIMATION = 4
    self.FEATURE_OUTPUTS_REARRANGEMENT = 5

_api = _API()

class _PropertiesTransport(object):
  def __init__(self, **kwargs):
    for k in kwargs:
      object.__setattr__(self, k, kwargs[k])

  def __setattr__(self, *args):
    raise TypeError('Immutable object.')

  def __delattr__(self, *args):
    raise TypeError('Immutable object.')

class _CallbackMatrixReader(object):
  def __init__(self, default_data=None):
    self._data = default_data
    self._callback_type = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_void_p, _ctypes.c_size_t)
    self._pending_error = None

  @property
  def data(self):
    return self._data

  @property
  def callback(self):
    return self._callback_type(self)

  def process_exception(self):
    if self._pending_error is not None:
      _shared.reraise(*self._pending_error)

  def __call__(self, m, n, data_ptr, ld):
    try:
      self._data = _numpy.frombuffer((_ctypes.c_double * (m*ld)).from_address(data_ptr)).reshape((m, ld))[:,:n].copy()
      return True
    except:
      self._pending_error = _sys.exc_info()
      return False

class Model(object):
  """Approximation model.

  Can be created by :class:`~da.p7core.gtapprox.Builder` or
  loaded from a file via the :class:`~da.p7core.gtapprox.Model` constructor.

  .. versionchanged:: 6.16
    the file to load may also be a GTDF model saved with :meth:`.gtdf.Model.save()`. Note that loading a GTDF model converts it into a GTApprox model, but the backward conversion is not supported.

  :class:`~da.p7core.gtapprox.Model` objects are immutable.
  All methods which are meant to change the model return a new :class:`~da.p7core.gtapprox.Model` instance.
  """

  __MODEL_SECTIONS = {"all":  0x7fffffff,
                      "none": 0x80000000,
                      "model": 0x00000001,
                      "info": 0x00000002,
                      "build_log": 0x00000004,
                      "iv_info": 0x00000008,
                      "comment": 0x00000010,
                      "training_sample": 0x00000020,
                      "annotations": 0x00000040,
                      }

  __BATCH_F = 'F'.encode('ascii')
  __BATCH_dFdX = 'dF/dX'.encode('ascii')
  __BATCH_AE = 'AE'.encode('ascii')
  __BATCH_dAEdX = 'dAE/dX'.encode('ascii')

  @property
  def info(self):
    """Model description.

    :Type: ``dict``

    Contains all technical information which can be gathered from the model.

    """
    if self.__cache.get('info') is None:
      info = self._backend.read_str(self.__instance, self._backend._get_info)
      self.__cache['info'] = _shared.parse_json_deep(_shared._preprocess_json(info), dict)
    return self.__cache['info']

  @property
  def license(self):
    """Model license.

    :type: :class:`~da.p7core.License`

    General license information interface. See section :ref:`gen_license_usage` for details.

    """
    errdesc = _ctypes.c_void_p()
    obj = _ctypes.c_void_p()
    self.__checkCall(self._backend.read_license(self.__instance, _ctypes.byref(obj), _ctypes.byref(errdesc)), errdesc)
    return _license.License(obj, self)

  @property
  def parameters(self):
    """Model parameters.

    :Type: :class:`~da.p7core.Parameters`

    General parameters interface for the model. See :ref:`Parameters` for details.

    """
    if self.__cache.get('parameters') is None:
      errdesc = _ctypes.c_void_p()
      obj = _ctypes.c_void_p()
      self.__checkCall(self._backend.get_parameters(self.__instance, _ctypes.byref(obj), _ctypes.byref(errdesc)), errdesc)
      self.__cache['parameters'] = _parameters.Parameters(obj, self.__instance)
    return self.__cache['parameters']

  @property
  def details(self):
    r"""Detailed model information.

    :Type: ``dict``

    .. versionadded:: 5.2

    A detailed description of the model. Includes model metainformation, accuracy data, training sample statistics,
    regression coefficients for RSM models, and other data.

    See sections :ref:`ug_gtapprox_details_model_information` and :ref:`ug_gtapprox_details_model_metainfo`.
    """

    if self.__cache.get('details') is None:
      details, metainfo = _details._details(self, with_metainfo=True)
      if metainfo is None:
        metainfo = self.__metainfo()
      for key in metainfo:
        if key in ("Input Variables", "Output Variables") and key in details:
          for details_data, metainfo_data in zip(details[key], metainfo[key]):
            for k in metainfo_data:
              if k not in details_data:
                details_data[k] = metainfo_data[k]
            if details_data.get("variability", "continuous") == "enumeration" and "labels" in details_data and "enumerators" in details_data:
              # Since enumerators can only store floats we use labels field at python level that supports any type (like string, bool)
              details_data["enumerators"] = details_data.pop("labels")
        else:
          details[key] = metainfo[key]
      self.__cache['details'] = details
    return self.__cache['details']

  @property
  def _categorical_x_map(self):
    # The property is used to encode/decode categorical inputs in train and test samples
    # Note the property returns "type, labels and enumerators by input index" dict.
    if self.__cache.get('_labels') is None:
      self.__cache['_labels'] = _shared.read_categorical_maps(self.__metainfo(), validate=False)
    return self.__cache['_labels'][0]

  @property
  def _categorical_f_map(self):
    # The property is used to encode/decode categorical outputs in train and test samples
    # Note the property returns "type, labels and enumerators by output index" dict.
    if self.__cache.get('_labels') is None:
      self.__cache['_labels'] = _shared.read_categorical_maps(self.__metainfo(), validate=False)
    return self.__cache['_labels'][1]

  @property
  def _names_x(self):
    if self.__cache.get('_names_x') is None:
      self.__cache['_names_x'] = [_['name'] for _ in self.__metainfo().get("Input Variables", [])]
    return self.__cache['_names_x']

  @property
  def _names_f(self):
    if self.__cache.get('_names_f') is None:
      self.__cache['_names_f'] = [_['name'] for _ in self.__metainfo().get("Output Variables", [])]
    return self.__cache['_names_f']

  def __metainfo(self):
    metainfo = self._backend.read_str(self.__instance, self._backend._get_metainfo)
    metainfo = _shared.parse_json_deep(_shared._preprocess_json(metainfo), dict)

    # Backward compatibility
    if not metainfo:
      try:
        # Try to load metainfo from annotations for old models built in platform
        # Old metainfo might be invalid in terms of currently specified rules, set default metainfo in such cases
        deprecated_metainfo = self.annotations.get('training_sample', {}) if isinstance(self.annotations, dict) else {}
        # Fix encoding issues
        for variables_direction in ['x', 'f']:
          for i, var_meta in enumerate(deprecated_metainfo[variables_direction]):
            try:
              deprecated_metainfo[variables_direction][i] = var_meta.encode('latin1').decode('utf-8')
            except:
              pass
        metainfo = _shared.preprocess_metainfo(deprecated_metainfo.get('x'), deprecated_metainfo.get('f'), self.size_x, self.size_f)
      except:
        metainfo = _shared.preprocess_metainfo(None, None, self.size_x, self.size_f)

      cached_details = self.__cache.get('details', {})
      # Do not forget to load variability info if there is any
      for variables_direction in metainfo:
        if cached_details.get(variables_direction):
          for var_meta, var_details in zip(metainfo[variables_direction], cached_details[variables_direction]):
            var_meta.update(var_details)

    # read variables info based on natural properties of the model
    varsinfo = self._backend.read_str(self.__instance, self._backend._get_variables_info)
    varsinfo = _shared.parse_json_deep(_shared._preprocess_json(varsinfo), dict)

    # extend metainfo with variables info in a raw way
    for key in ("Input Variables", "Output Variables"):
      if key in varsinfo and key in metainfo:
        for metainfo_data, varsinfo_data in zip(metainfo[key], varsinfo[key]):
          metainfo_data.update(varsinfo_data)

    if 'Issues' not in metainfo:
      metainfo.setdefault(u'Issues', _shared.parse_building_issues(self.build_log))

    return metainfo

  @property
  def build_log(self):
    """
    Model building log.

    :Type: ``str``

    """
    if self.__cache.get('log') is None:
      log = self._backend.read_str(self.__instance, self._backend._get_log)
      self.__cache['log'] = _shared._preprocess_utf8(log)
    return self.__cache['log']

  @property
  def comment(self):
    """
    Text comment to the model.

    :Type: ``str``

    .. versionadded:: 6.6

    Optional plain text comment to the model.
    You can add the comment when training a model
    and edit it using :meth:`~da.p7core.gtapprox.Model.modify()`.

    See also :ref:`ug_gtapprox_details_model_metainfo`.

    """
    if self.__cache.get('comment') is None:
      comment = self._backend.read_str(self.__instance, self._backend._get_comment)
      self.__cache['comment'] = _shared._preprocess_utf8(comment)
    return self.__cache['comment']

  @property
  def annotations(self):
    """
    Extended comment or supplementary information.

    :Type: ``dict``

    .. versionadded:: 6.6

    The annotations dictionary can optionally contain any number of notes.
    All dictionary keys and values are strings.
    You can add annotations when training a model
    and edit them using :meth:`~da.p7core.gtapprox.Model.modify()`.

    See also :ref:`ug_gtapprox_details_model_metainfo`.

    """
    if self.__cache.get('annotations') is None:
      annotations = self._backend.read_str(self.__instance, self._backend._get_annotations)
      self.__cache['annotations'] = _shared.parse_json_deep(_shared._preprocess_json(annotations), dict)
    return self.__cache['annotations']

  @property
  def training_sample(self):
    """
    Model training sample optionally stored with the model.

    :Type: ``list``

    .. versionadded:: 6.6

    If :ref:`GTApprox/StoreTrainingSample<GTApprox/StoreTrainingSample>` was enabled when training the model, this attribute contains a copy of training data. Otherwise it will be an empty list.

    Training data is a single ``dict`` element contained in the list. This dictionary has the following keys:

    * ``"x"`` --- the input part of the training sample (values of variables).
    * ``"f"`` --- the response part of the training sample (function values).
    * ``"tol"`` --- response noise variance. This key is present only if output noise variance was specified when training.
    * ``"weights"`` --- sample point weights. This key is present only if point weights were specified when training.
    * ``"x_test"`` --- the input part of the test sample (*added in 6.8*). This key is present only if a test sample was used when training.
    * ``"f_test"`` --- the response part of the test sample (*added in 6.8*). This key is present only if a test sample was used when training.

    Note that in case of GBRT incremental training (see :ref:`gbrt_configuration_incremental_training`) only the last (most recent) training sample can be saved.

    .. note::

       Training sample data is stored in lightweight NumPy arrays that have
       limited lifetime, which cannot exceed the lifetime of the model object.
       It means that you should avoid assigning these arrays to new variables.
       Either use them directly, or if you want to read this data without
       keeping the model object, create copies of arrays:
       ``train_x = my_model.training_sample["x"].copy``.

    """
    if self.__cache.get('training_sample') is None:
      training_sample_list = []

      null_size_t = self._backend.c_size_t_p()
      null_void_p = self._backend.c_void_p_p()

      ndim = _ctypes.c_size_t()
      nsamples = _ctypes.c_size_t()

      if not self._backend.train_sample_count(self.__instance, _ctypes.byref(nsamples), null_void_p):
        nsamples = 0

      for sample_idx in _six.moves.range(nsamples.value):
        training_sample = dict()

        for name, code in [('x', 1), ('f', 2), ('weights', 3), ('tol', 4), ('x_test', 5), ('f_test', 6)]:
          err = self._backend.get_train_sample(self.__instance, sample_idx, code, _ctypes.byref(ndim), null_size_t, null_size_t, null_void_p, null_void_p)
          if 0 == err or 0 == ndim.value or ndim.value > 2:
            continue

          shape = (_ctypes.c_size_t * ndim.value)()
          strides = (_ctypes.c_size_t * ndim.value)()
          data_ptr = _ctypes.c_void_p()

          err = self._backend.get_train_sample(self.__instance, sample_idx, code, _ctypes.byref(ndim), shape, strides, _ctypes.byref(data_ptr), null_void_p)
          if 0 == err or 0 == shape[0] or 0 == shape[ndim.value - 1]:
            continue

          data = _numpy.frombuffer((_ctypes.c_double * (shape[0]*strides[0])).from_address(data_ptr.value)).reshape((shape[0], strides[0]))
          data.flags.writeable = False

          if name == 'x':
            data = _shared.decode_categorical_values(data, self._categorical_x_map, inplace=False)
          elif name == 'f':
            data = _shared.decode_categorical_values(data, self._categorical_f_map, inplace=False)

          training_sample[name] = data[:, 0] if 1 == ndim.value else data[:, :shape[1]]

        if training_sample:
          training_sample_list.append(training_sample)

      self.__cache['training_sample'] = training_sample_list

    return self.__cache['training_sample']

  @property
  def iv_info(self):
    """Internal validation results.

    :Type: ``dict``

    .. versionadded // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionadded directive when the version number contains spaces

    *New in version 2.0 Release Candidate 1.*

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 2.0 Release Candidate 2:* also stores raw validation data.

    A dictionary containing error values calculated during :term:`internal validation`.
    Has the same structure as the ``details["Training Dataset"]["Accuracy"]``
    dictionary in :attr:`~da.p7core.gtapprox.Model.details` ---
    see section :ref:`ug_gtapprox_details_model_information_training_dataset_info_accuracy`
    in :ref:`ug_gtapprox_details_model_information` for a full description.

    Additionally, if the model was trained with
    :ref:`GTApprox/IVSavePredictions <GTApprox/IVSavePredictions>` on,
    :attr:`~da.p7core.gtapprox.Model.iv_info` also contains raw validation
    data: model values calculated during internal validation, reference
    inputs, and reference outputs. This data is stored under the ``"Dataset"`` key.

    If internal validation was not required when training the model
    (see :ref:`GTApprox/InternalValidation <GTApprox/InternalValidation>`),
    :attr:`~da.p7core.gtapprox.Model.iv_info` is an empty dictionary.

    """
    if self.__cache.get('iv_info') is None:
      iv_data = _shared.readStatistics(self.__instance, "Internal Validation", "GTApprox")
      iv_dataset = iv_data.get('Dataset')
      if iv_dataset:
        if 'Validation Input' in iv_dataset:
          iv_dataset['Validation Input'] = _shared.decode_categorical_values(iv_dataset['Validation Input'], self._categorical_x_map, inplace=False)
        if 'Validation Output' in iv_dataset:
          iv_dataset['Validation Output'] = _shared.decode_categorical_values(iv_dataset['Validation Output'], self._categorical_f_map, inplace=False)
        if 'Predicted Output' in iv_dataset:
          iv_dataset['Predicted Output'] = _shared.decode_categorical_values(iv_dataset['Predicted Output'], self._categorical_f_map, inplace=False)
        if 'Predicted Probabilities' in iv_dataset:
          predicted_prob = iv_dataset['Predicted Probabilities']
          iv_dataset['Predicted Probabilities'] = [predicted_prob[:, (last-size):last] for last, size in zip(_numpy.add.accumulate(self._size_pe), self._size_pe)]
      self.__cache['iv_info'] = iv_data
    return self.__cache['iv_info']

  @property
  def size_x(self):
    """
    Model input dimension.

    :Type: ``long``

    """
    if self.__cache.get('size_x') is None:
      errdesc = _ctypes.c_void_p()
      size_x = _ctypes.c_size_t()
      self.__checkCall(self._backend.get_size_x(self.__instance, _ctypes.byref(size_x), _ctypes.byref(errdesc)), errdesc)
      self.__cache['size_x'] = _shared.long_integer(size_x.value)
    return self.__cache['size_x']

  @property
  def size_f(self):
    """
    Model output dimension.

    :Type: ``long``

    """
    if self.__cache.get('size_f') is None:
      errdesc = _ctypes.c_void_p()
      size_f = _ctypes.c_size_t()
      self.__checkCall(self._backend.get_size_f(self.__instance, _ctypes.byref(size_f), _ctypes.byref(errdesc)), errdesc)
      self.__cache['size_f'] = _shared.long_integer(size_f.value)
    return self.__cache['size_f']

  @property
  def _size_pe(self):
    """
    Model probabilistic output dimension.

    :Type: ``long``

    """
    if self.__cache.get('size_p') is None:
      self.__cache['size_p'] = []
      for output_index in range(self.size_f):
        errdesc = _ctypes.c_void_p()
        size_p = _ctypes.c_size_t()
        self.__checkCall(self._backend.get_size_p(self.__instance, output_index ,_ctypes.byref(size_p), _ctypes.byref(errdesc)), errdesc)
        self.__cache['size_p'].append(_shared.long_integer(size_p.value))
    return self.__cache['size_p']

  @property
  def _has_pe(self):
    """Probability estimation support.

    :Type: ``bool``

    .. versionadded:: 6.22

    Check this attribute before using :meth:`~da.p7core.gtapprox.Model.calc_p()`.
    If ``True``, the model supports probability estimation.
    If ``False``, then probability estimation is not available, and the methods above raise an exception.
    """
    return self.__hasFeature(self._backend.FEATURE_PROBABILITY_ESTIMATION)

  @property
  def has_ae(self):
    """:term:`Accuracy evaluation` support.

    :Type: ``bool``

    Check this attribute before using :meth:`~da.p7core.gtapprox.Model.calc_ae()` or :meth:`~da.p7core.gtapprox.Model.grad_ae()`.
    If ``True``, the model supports accuracy evaluation.
    If ``False``, then accuracy evaluation is not available, and the methods above raise an exception.
    """
    return self.__hasFeature(self._backend.FEATURE_ACCURACY_EVALUATION)

  @property
  def has_smoothing(self):
    """Smoothing support.

    :Type: ``bool``

    .. versionadded:: 1.9.0

    Check this attribute before using :meth:`~da.p7core.gtapprox.Model.smooth()`,
    :meth:`~da.p7core.gtapprox.Model.smooth_anisotropic()`, or
    :meth:`~da.p7core.gtapprox.Model.smooth_errbased()`.
    If ``True``, the model supports smoothing. If ``False``, then smoothing is not available,
    and smoothing methods raise an exception.
    """
    return self.__hasFeature(self._backend.FEATURE_STATIC_SMOOTHNESS)

  @property
  def _has_or(self):
    """Outputs rearrangement support.

    :Type: ``bool``

    .. versionadded:: 6.31

    Check this attribute before splitting the model's outputs.
    If ``True``, the model supports outputs rearrangement.
    If ``False``, outputs rearrangement is not available, and the methods above raise an exception.
    """
    return self.__hasFeature(self._backend.FEATURE_OUTPUTS_REARRANGEMENT)

  @property
  def is_smoothed(self):
    """Smoothed model.

    :Type: ``bool``

    .. versionadded:: 1.9.0

    Check this attribute to see if the model is already smoothed.
    It is ``True`` for models returned by :meth:`~da.p7core.gtapprox.Model.smooth()`,
    :meth:`~da.p7core.gtapprox.Model.smooth_errbased()`, and :meth:`~da.p7core.gtapprox.Model.smooth_anisotropic()`
    methods, and ``False`` for other models.
    """
    return self.__hasFeature(self._backend.FEATURE_SMOOTHED)

  def calc(self, point):
    """Evaluate the model.

    :param point: the sample or point to evaluate
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :return: model values
    :rtype: ``pandas.DataFrame`` or ``pandas.Series`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 2D or 1D

    .. versionchanged:: 1.9.0
       *smoothness* parameter is no longer supported (see :ref:`support_vci`).

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.22
       returns ``ndarray`` with ``dtype=object`` if the model has string categorical outputs.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Evaluates a data sample or a single point.
    In general form, :arg:`point` is a 2D array-like (a data sample).
    Several simplified argument forms are also supported.

    The returned array is 2D if :arg:`point` is a sample, and 1D if :arg:`point` is a single point.
    When :arg:`point` is a ``pandas.DataFrame`` or ``pandas.Series``,
    the returned array keeps indexing of the :arg:`point` array.

    * In the case of 1D model input, a single ``float`` value is interpreted as a single point.
      A 1D array-like with a single element is also one point; other 1D array-likes are interpreted as a sample.
      A 2D array-like is always interpreted as a sample, even if it contains a single point actually.
      For example::

        model_1d.calc(0.0)             # a 1D point
        model_1d.calc([0.0])           # a 1D point
        model_1d.calc([[0.0]])         # a sample, one 1D point
        model_1d.calc([0.0, 1.0])      # a sample, two 1D points
        model_1d.calc([[0.0], [1.0]])  # a sample, two 1D points
        model_1d.calc([[0.0, 1.0]])    # incorrect: a sample with a single 2D point (model input is 1D)

    * If model input is multidimensional, a 1D array-like is interpreted as a single point,
      and 2D array-likes are interpreted as data samples.
      For example, if model input is 2D::

        model_2d.calc(0.0)                       # incorrect: point is 1D
        model_2d.calc([0.0])                     # incorrect: point is 1D
        model_2d.calc([[0.0]])                   # incorrect: sample contains one 1D point
        model_2d.calc([0.0, 0.0])                # a 2D point
        model_2d.calc([[0.0, 0.0]])              # a sample, one 2D point
        model_2d.calc([[0.0, 0.0], [1.0, 1.0]])  # a sample, two 2D points

    """
    self.__requireModelSection()

    if self._categorical_x_map:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument", dtype=object)
      input = _shared.encode_categorical_values(input, self._categorical_x_map, "input")
    else:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")

    errdesc = _ctypes.c_void_p()
    if not self._backend.check_input(self.__instance, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Input data contains NaN or Inf value', errdesc)

    output = _numpy.ndarray((input.shape[0], self.size_f), dtype=float, order='C')

    if not self._backend.batch_calc(self.__instance, self.__BATCH_F, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    output.ctypes.data_as(self._backend.c_double_p), \
                                    output.strides[0] // output.itemsize, output.strides[1] // output.itemsize, 1, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Model evaluation error', errdesc)

    output = _shared.decode_categorical_values(output, self._categorical_f_map)
    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      return _shared.make_pandas(output, single_vector, pandas_type, pandas_index, self._names_f)
    else:
      return output[0] if single_vector else output

  def grad(self, point, order=GradMatrixOrder.F_MAJOR):
    """Evaluate :term:`model gradient`.

    :param point: the sample or point to evaluate
    :keyword order: gradient matrix order
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :type order: :class:`GradMatrixOrder`
    :return: model gradients
    :rtype: ``pandas.DataFrame`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 3D or 2D

    .. versionchanged:: 1.9.0
       *smoothness* parameter is no longer supported (see :ref:`support_vci`).

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Evaluates model gradients for a data sample or a single point.
    In general form, :arg:`point` is a 2D array-like (a data sample).
    Several simplified argument forms are also supported, similar to :meth:`~da.p7core.gtapprox.Model.calc()`.

    The returned array is 3D if :arg:`point` is a sample, and 2D if :arg:`point` is a single point.

    When using pandas data samples (:arg:`point` is a ``pandas.DataFrame``),
    a 3D array in return value is represented by a ``pandas.DataFrame`` with multi-indexing (``pandas.MultiIndex``).
    In this case, the first element of the multi-index is the point index from the input sample.
    The second element of the multi-index is:

    * the index or name of a model's output,
      if :arg:`order` is :attr:`~da.p7core.gtapprox.GradMatrixOrder.F_MAJOR` (default)
    * the index or name of a model's input,
      if :arg:`order` is :attr:`~da.p7core.gtapprox.GradMatrixOrder.X_MAJOR`

    When :arg:`point` is a ``pandas.Series``,
    its index becomes the row index of the returned ``pandas.DataFrame``.
    """
    self.__requireModelSection()

    size_x = self.size_x
    if self._categorical_x_map:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument", dtype=object)
      input = _shared.encode_categorical_values(input, self._categorical_x_map, 'input')
    else:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")

    errdesc = _ctypes.c_void_p()
    if not self._backend.check_input(self.__instance, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Input data contains NaN or Inf value', errdesc)

    vectorsNumber = input.shape[0]
    if order == GradMatrixOrder.F_MAJOR:
      output = _numpy.ndarray((vectorsNumber, self.size_f, size_x), dtype=float, order='C')
      df_axis, dx_axis = 1, 2
    elif order == GradMatrixOrder.X_MAJOR:
      output = _numpy.ndarray((vectorsNumber, size_x, self.size_f), dtype=float, order='C')
      df_axis, dx_axis = 2, 1
    else:
      raise ValueError('Wrong "order" value!')

    if not self._backend.batch_calc(self.__instance, self.__BATCH_dFdX, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    output.ctypes.data_as(self._backend.c_double_p), output.strides[0] // output.itemsize, \
                                    output.strides[df_axis] // output.itemsize, output.strides[dx_axis] // output.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Gradient evaluation error', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      major_names = self._names_f if order == GradMatrixOrder.F_MAJOR else self._names_x
      minor_names = self._names_x if order == GradMatrixOrder.F_MAJOR else self._names_f
      return _shared.make_pandas_grad(output, single_vector, pandas_type, pandas_index, major_names, minor_names)
    else:
      return output[0] if single_vector else output

  def calc_ae(self, point):
    """Calculate the :term:`accuracy evaluation` estimate.

    :param point: the sample or point to evaluate
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :return: estimates
    :rtype: ``pandas.DataFrame`` or ``pandas.Series`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 2D or 1D
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not provide :term:`accuracy evaluation`

    .. versionchanged:: 1.9.0
       *smoothness* parameter is no longer supported (see :ref:`support_vci`).

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Check :attr:`~da.p7core.gtapprox.Model.has_ae` before using this method.
    It is available only if the model was trained with
    :ref:`GTApprox/AccuracyEvaluation <GTApprox/AccuracyEvaluation>` on.

    Performs accuracy evaluation for a data sample or a single point.
    In general form, :arg:`point` is a 2D array-like (a data sample).
    Several simplified argument forms are also supported, similar to :meth:`~da.p7core.gtapprox.Model.calc()`.

    The returned array is 2D if :arg:`point` is a sample, and 1D if :arg:`point` is a single point.
    When :arg:`point` is a ``pandas.DataFrame`` or ``pandas.Series``,
    the returned array keeps indexing of the :arg:`point` array.

    """
    self.__requireModelSection()
    self.__requireAE()

    if self._categorical_x_map:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument", dtype=object)
      input = _shared.encode_categorical_values(input, self._categorical_x_map, 'input')
    else:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")

    errdesc = _ctypes.c_void_p()
    if not self._backend.check_input(self.__instance, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Input data contains NaN or Inf value', errdesc)

    output = _numpy.ndarray((input.shape[0], self.size_f), dtype=float, order='C')

    if not self._backend.batch_calc(self.__instance, self.__BATCH_AE, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    output.ctypes.data_as(self._backend.c_double_p), \
                                    output.strides[0] // output.itemsize, output.strides[1] // output.itemsize, 1, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Accuracy estimation error', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      return _shared.make_pandas(output, single_vector, pandas_type, pandas_index, self._names_f)
    else:
      return output[0] if single_vector else output

  def grad_ae(self, point, order=GradMatrixOrder.F_MAJOR):
    """Calculate gradients of the :term:`accuracy evaluation` function.

    :param point: the sample or point to evaluate
    :keyword order: gradient matrix order
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :type order: :class:`GradMatrixOrder`
    :return: accuracy evaluation gradients
    :rtype: ``pandas.DataFrame`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 3D or 2D
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not provide :term:`accuracy evaluation`

    .. versionchanged:: 1.9.0
       the :arg:`smoothness` argument is no longer supported (see :ref:`support_vci`).

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Check :attr:`~da.p7core.gtapprox.Model.has_ae` before using this method.
    It is available only if the model was trained with
    :ref:`GTApprox/AccuracyEvaluation <GTApprox/AccuracyEvaluation>` on.

    Evaluates gradients of the accuracy evaluation function for a data sample or a single point.
    In general form, :arg:`point` is a 2D array (a data sample).
    Several simplified argument forms are also supported, similar to :meth:`~da.p7core.gtapprox.Model.calc()`.

    The returned array is 3D if :arg:`point` is a sample, and 2D if :arg:`point` is a single point.

    When using pandas data samples (:arg:`point` is a ``pandas.DataFrame``),
    a 3D array in return value is represented by a ``pandas.DataFrame`` with multi-indexing (``pandas.MultiIndex``).
    In this case, the first element of the multi-index is the point index from the input sample.
    The second element of the multi-index is:

    * the index or name of a model's output,
      if :arg:`order` is :attr:`~da.p7core.gtapprox.GradMatrixOrder.F_MAJOR` (default)
    * the index or name of a model's input,
      if :arg:`order` is :attr:`~da.p7core.gtapprox.GradMatrixOrder.X_MAJOR`

    When :arg:`point` is a ``pandas.Series``,
    its index becomes the row index of the returned ``pandas.DataFrame``.
    """
    self.__requireModelSection()
    self.__requireAE()

    size_x = self.size_x
    if self._categorical_x_map:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument", dtype=object)
      input = _shared.encode_categorical_values(input, self._categorical_x_map, 'input')
    else:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")

    errdesc = _ctypes.c_void_p()
    if not self._backend.check_input(self.__instance, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Input data contains NaN or Inf value', errdesc)

    vectorsNumber = input.shape[0]
    if order == GradMatrixOrder.F_MAJOR:
      output = _numpy.ndarray((vectorsNumber, self.size_f, size_x), dtype=float, order='C')
      df_axis, dx_axis = 1, 2
    elif order == GradMatrixOrder.X_MAJOR:
      output = _numpy.ndarray((vectorsNumber, size_x, self.size_f), dtype=float, order='C')
      df_axis, dx_axis = 2, 1
    else:
      raise ValueError('Wrong "order" value!')

    if not self._backend.batch_calc(self.__instance, self.__BATCH_dAEdX, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    output.ctypes.data_as(self._backend.c_double_p), output.strides[0] // output.itemsize, \
                                    output.strides[df_axis] // output.itemsize, output.strides[dx_axis] // output.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'AE gradient evaluation error', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      major_names = self._names_f if order == GradMatrixOrder.F_MAJOR else self._names_x
      minor_names = self._names_x if order == GradMatrixOrder.F_MAJOR else self._names_f
      return _shared.make_pandas_grad(output, single_vector, pandas_type, pandas_index, major_names, minor_names)
    else:
      return output[0] if single_vector else output

  def _calc_pe(self, point, output_index=None):
    """Evaluate the model.

    :param point: point(s) to evaluate
    :type point: ``float`` or :term:`array-like`, 1D or 2D
    :return: model values
    :rtype: ``ndarray``, 1D or 2D

    .. versionchanged:: 6.22

    Evaluates a point or a sample.
    In general form, *point* is a 2D array.
    Several simplified argument forms are also supported.

    Returned array is 1D if *point* is a point, and 2D if *point* is a sample.

    * In case of 1D model input, a single ``float`` value is seen as a single point. A 1D array with a single element is also one point; other 1D arrays are seen as a sample. A 2D array is always seen as a sample, even if it contains a single point actually. For example::

        model_1d.calc(0.0)             # a point
        model_1d.calc([0.0])           # a point
        model_1d.calc([[0.0]])         # a sample, one point
        model_1d.calc([0.0, 1.0])      # a sample, two points
        model_1d.calc([[0.0], [1.0]])  # a sample, two points
        model_1d.calc([[0.0, 1.0]])    # incorrect: a sample with a single 2D point

    * In other cases (multidimensional input), 1D array is seen as a single point, and 2D array as a sample. For example::

        model_2d.calc(0.0)                       # incorrect: point is 1D
        model_2d.calc([0.0])                     # incorrect: point is 1D
        model_2d.calc([[0.0]])                   # incorrect: sample contains one 1D point
        model_2d.calc([0.0, 0.0])                # a point
        model_2d.calc([[0.0, 0.0]])              # a sample, one 2D point
        model_2d.calc([[0.0, 0.0], [1.0, 1.0]])  # a sample, two 2D points

    """
    self.__requireModelSection()
    self.__requirePE()

    if self._categorical_x_map:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument", dtype=object)
      input = _shared.encode_categorical_values(input, self._categorical_x_map, 'input')
    else:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")

    errdesc = _ctypes.c_void_p()
    if not self._backend.check_input(self.__instance, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                    input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                    _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Input data contains NaN or Inf value', errdesc)

    if output_index is None:
      output_index = 0
      estimate_for_all_outputs = 1
      output = _numpy.ndarray((input.shape[0], sum(self._size_pe)), dtype=float, order='C')
    elif output_index in _numpy.arange(self.size_f):
      estimate_for_all_outputs = 0
      output = _numpy.ndarray((input.shape[0], self._size_pe[output_index]), dtype=float, order='C')
    else:
      raise ValueError('Categorical output index %s is out of valid output indices range [0, %d]' % (str(output_index), self.size_f - 1))

    if not self._backend.batch_calc_pe(self.__instance, estimate_for_all_outputs, output_index, \
                                       self.__BATCH_F, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                       input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                       output.ctypes.data_as(self._backend.c_double_p), \
                                       output.strides[0] // output.itemsize, output.strides[1] // output.itemsize, 1, \
                                      _ctypes.byref(errdesc)):
      _shared._raise_on_error(0, 'Model evaluation error', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      pe_names = []
      for i, name in enumerate(self._names_f):
        if i in self._categorical_f_map:
          pe_names.extend((name, label) for label in self._categorical_f_map[i][1])
      return _shared.make_pandas_pe(output, single_vector, pandas_type, pandas_index, pe_names)
    else:
      return output[0] if single_vector else output

  def validate(self, pointsX, pointsY, weights=None):
    """Validate the model using a reference inputs-responses array.

    :param pointsX: reference inputs
    :param pointsY: reference responses
    :param weights: optional weights of the reference points
    :type pointsX: ``float`` or :term:`array-like`, 1D or 2D
    :type pointsY: ``float`` or :term:`array-like`, 1D or 2D
    :type weights: :term:`array-like`, 1D
    :return: accuracy data
    :rtype: ``dict``

    Validates the model against the reference array, evaluating model
    responses to :arg:`pointsX` and comparing them to :arg:`pointsY`.

    Generally, :arg:`pointsX` and :arg:`pointsY` should be 2D arrays.
    Several simplified argument forms are also supported,
    similar to :meth:`~da.p7core.gtapprox.Model.calc()`.

    Returns a dictionary containing lists of error values calculated
    componentwise, with names of errors as keys. The returned dictionary
    has the same structure as the ``details["Training Dataset"]["Accuracy"]["Componentwise"]``
    dictionary in :attr:`~da.p7core.gtapprox.Model.details` ---
    see section :ref:`ug_gtapprox_details_model_information_training_dataset_info_accuracy`
    in :ref:`ug_gtapprox_details_model_information` for a full description.

    """
    return self._validate(pointsX, pointsY, weights)

  def export_to(self, format, function, description, file, single_file=None):
    """Export the model to a source file in specified format.

    :param format: source code format
    :param function: exported function name
    :param description: additional comment
    :param file: export file or path
    :param single_file: export sources as a single file (default) or multiple files (``False``)
    :type format: :class:`ExportedFormat` or ``str``
    :type function: ``str``
    :type description: ``str``
    :type file: file-like, ``str``, ``zipfile.ZipFile``, ``tarfile.TarFile``
    :type single_file: ``bool``
    :return: ``None``
    :raise: :exc:`~da.p7core.GTException` if :arg:`function` is empty and :arg:`format` is not :attr:`~da.p7core.gtapprox.ExportedFormat.C99_PROGRAM`

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

    The :arg:`function` argument is optional if :arg:`format` is :attr:`~da.p7core.gtapprox.ExportedFormat.C99_PROGRAM`
    For other source code formats, an empty :arg:`function` name raises an exception.

    For the C# source format (:attr:`~da.p7core.gtapprox.ExportedFormat.CSHARP_SOURCE`),
    the :arg:`function` argument sets the name of the model class and its namespace.
    There are two ways to use it:

    * If you specify a name without dots ``.``, it becomes the namespace,
      and the class name remains default (``Model``).
      For example, if :arg:`function` is "myGTAmodel":

      .. code-block:: none

         namespace myGTAmodel {
           public sealed class Model {
             // attributes and methods
           }
         }

    * If you specify a name with dots ``.``, it is split by dots
      and the last part becomes the class name,
      while the remaining parts become a namespace hierarchy.
      For example, if :arg:`function` is "ns1.ns2.MyExportedModel":

      .. code-block:: none

         namespace ns1 {
           namespace ns2 {
             public sealed class MyExportedModel {
               // attributes and methods
             }
           }
         }

    The :arg:`description` provides an additional comment,
    which is added on top of the generated source file.

    See also the :ref:`examples_gtapprox_model_export` example.
    """
    self.__requireModelSection()
    format = ExportedFormat.from_string(format)

    _shared.check_type(function, 'function name argument', _six.string_types)
    _shared.check_type(description, 'exported function description argument', _six.string_types)

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

      function = _validate_function(function, (ExportedFormat.C99_PROGRAM, ExportedFormat.OCTAVE), file_base.split('.')[0])

      with open(file, 'w') as fid:
        pass # test file open

      if tar_mode is not None:
        # tar file export
        with _archives._with_tarfile(file, tar_mode) as fobj:
          file_writer = _archives._TarArchiveWriter(fobj)
          succeeded =  self._backend.export_multiple_file(self.__instance, format, file_base.encode("utf8"),
                                                          _ctypes.c_char_p(function.encode("utf8")), description,
                                                          self._backend.callback_single_file(file_writer), file_size,
                                                          warnings_callback, _ctypes.byref(errdesc))
          file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))
      elif file_base[-4:].lower() == ".zip":
        # zip file export
        with _archives._with_zipfile(file, "w") as fobj:
          file_writer = _archives._ZipArchiveWriter(fobj)
          succeeded =  self._backend.export_multiple_file(self.__instance, format, file_base[:-4].encode("utf8"),
                                                          _ctypes.c_char_p(function.encode("utf8")), description,
                                                          self._backend.callback_single_file(file_writer), file_size,
                                                          warnings_callback, _ctypes.byref(errdesc))
          file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))
      else:
        if format == ExportedFormat.OCTAVE and function != _os.path.splitext(file_base)[0]:
          #raise ValueError("Octave requires match of the function name (%s) and base name of the file (%s)." % (function, _os.path.splitext(file_base)[0]))
          _warn.warn("Octave requires match of the function name (%s) and base name of the file (%s)." % (function, _os.path.splitext(file_base)[0]))
        file_writer = _archives._DirectoryWriter(file_path or _six.moves.getcwd(), (file if single_file else None))
        succeeded =  self._backend.export_multiple_file(self.__instance, format, _os.path.splitext(file_base)[0].encode("utf8"),
                                                        _ctypes.c_char_p(function.encode("utf8")), description,
                                                        self._backend.callback_single_file(file_writer), file_size,
                                                        warnings_callback, _ctypes.byref(errdesc))
        file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))
    else:
      _validate_function(function, (ExportedFormat.C99_PROGRAM,), None)

      postprocess = False
      if isinstance(file, _zipfile.ZipFile):
        file_writer = _archives._ZipArchiveWriter(file)
      elif isinstance(file, _tarfile.TarFile):
        file_writer = _archives._TarArchiveWriter(file)
      else:
        file_writer = _archives._MemoryFileWriter()
        file_size = _ctypes.c_size_t(_numpy.iinfo(_ctypes.c_size_t).max) # force single file mode
        postprocess = True

      succeeded =  self._backend.export_multiple_file(self.__instance, format, function.encode("utf8"),
                                                      _ctypes.c_char_p(function.encode("utf8")), description,
                                                      self._backend.callback_single_file(file_writer), file_size,
                                                      warnings_callback, _ctypes.byref(errdesc))
      file_writer.flush_callback_exceptions(succeeded, _shared._release_error_message(errdesc))

      if postprocess:
        try:
          for fname, source_code in file_writer.files:
            file.write(source_code)
          return
        except AttributeError:
          pass

        with open(file, 'w') as fid:
          for fname, source_code in file_writer.files:
            file.write(source_code)

  def save(self, file, sections='all'):
    """Save the model to file.

    :param file: file object or path
    :type file: ``file`` or ``str``
    :param sections: model sections to save
    :type sections: ``list`` or ``str``
    :return: ``None``

    .. versionchanged:: 6.6
       *sections* argument added.

    When saving, certain sections of the model can be skipped to reduce the model file size
    (see :ref:`special_model_structure` for details).
    The *sections* argument can be a string or a list of strings specifying which sections to save:

    * ``"all"``: all sections (default).
    * ``"model"``: main model section, required for model evaluation.
      This section is always saved even if not specified.
      For some models, the size of this section can be additionally reduced by removing
      the accuracy evaluation or smoothing information with :meth:`~da.p7core.gtapprox.Model.modify()`.
    * ``"info"``: model information, :attr:`~da.p7core.gtapprox.Model.info`.
    * ``"comment"``: comment section, :attr:`~da.p7core.gtapprox.Model.comment`.
    * ``"annotations"``: annotations section, :attr:`~da.p7core.gtapprox.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, :attr:`~da.p7core.gtapprox.Model.training_sample`.
    * ``"iv_info"``: internal validation data, :attr:`~da.p7core.gtapprox.Model.iv_info`.
    * ``"build_log"``: model training log, :attr:`~da.p7core.gtapprox.Model.build_log`.

    Note that the main model section is always saved, so
    ``sections="model"`` and ``sections=[]`` are equivalent.

    """
    self.__requireModelSection()

    sections_code = self.__sections_code(sections) | self.__MODEL_SECTIONS['model'] # always save model section
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.save_model(self.__instance, _ctypes.c_void_p(), _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)
    data = _ctypes.create_string_buffer(size.value)
    self.__checkCall(self._backend.save_model(self.__instance, data, _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)

    try:
      file.write(data.raw)
      return
    except AttributeError:
      pass

    with open(file, 'wb') as fid:
      fid.write(data.raw)

  def tostring(self, sections='all'):
    """Serialize the model.

    :param sections: model sections to save
    :type sections: ``list`` or ``str``
    :return: serialized model
    :rtype: ``str``

    .. versionchanged:: 6.6
       *sections* argument added.

    When serializing, certain sections of the model can be skipped to reduce the model size
    (see :ref:`special_model_structure` for details).
    The *sections* argument can be a string or a list of strings specifying which sections to include:

    * ``"all"``: all sections (default).
    * ``"model"``: main model section, required for model evaluation.
      This section is always saved even if not specified.
      For some models, the size of this section can be additionally reduced by removing
      the accuracy evaluation or smoothing information with :meth:`~da.p7core.gtapprox.Model.modify()`.
    * ``"info"``: model information, :attr:`~da.p7core.gtapprox.Model.info`.
    * ``"comment"``: comment section, :attr:`~da.p7core.gtapprox.Model.comment`.
    * ``"annotations"``: annotations section, :attr:`~da.p7core.gtapprox.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, :attr:`~da.p7core.gtapprox.Model.training_sample`.
    * ``"iv_info"``: internal validation data, :attr:`~da.p7core.gtapprox.Model.iv_info`.
    * ``"build_log"``: model training log, :attr:`~da.p7core.gtapprox.Model.build_log`.

    Note that the main model section is always included, so
    ``sections="model"`` and ``sections=[]`` are equivalent.

    """
    self.__requireModelSection()

    sections_code = self.__sections_code(sections) | self.__MODEL_SECTIONS['model'] # always save model section
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.save_model(self.__instance, _ctypes.c_void_p(), _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)
    data = _ctypes.create_string_buffer(size.value)
    self.__checkCall(self._backend.save_model(self.__instance, data, _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)
    return _base64.b64encode(data.raw)

  def modify(self, comment=None, annotations=None, x_meta=None, y_meta=None, strip=None):
    """Create a copy of the model with modified features or metainformation.

    :param comment: new comment
    :param annotations: new annotations
    :param x_meta: descriptions of inputs
    :param y_meta: descriptions of outputs
    :param strip: optional list of features to strip from the model
    :type comment: ``str``
    :type annotations: ``dict``
    :type x_meta: ``list``
    :type y_meta: ``list``
    :type strip: ``list`` or ``str``
    :return: copy of this model with modifications
    :rtype: :class:`~da.p7core.gtapprox.Model`

    .. versionadded:: 6.6

    .. versionchanged:: 6.14
       can edit descriptions of inputs and outputs.

    .. versionchanged:: 6.14.3
       can remove the accuracy evaluation and smoothing features.

    .. versionchanged:: 6.17
       can disable the model output thresholds.

    This method is intended to edit model
    :attr:`~da.p7core.gtapprox.Model.annotations`,
    :attr:`~da.p7core.gtapprox.Model.comment`,
    metainformation,
    and can be used to reduce model size by removing certain features.
    If a parameter is ``None``, corresponding information in the modified model remains unchanged.
    If you specify a parameter, corresponding information in the modified model is fully replaced.

    The :arg:`x_meta` and :arg:`y_meta` parameters that edit metainformation
    are similar to :meth:`~da.p7core.gtapprox.Builder.build()`
    and are described in section :ref:`ug_gtapprox_details_model_metainfo` ---
    however note that specifying any new input constraints or output thresholds in :arg:`x_meta` or :arg:`y_meta`
    does not change the effective (current) model constraints:
    changes in :arg:`x_meta` and :arg:`y_meta` only apply to model information
    stored in :attr:`~da.p7core.gtapprox.Model.details`.
    For example, if you set a new, more restrictive input constraint
    in :arg:`x_meta` in :meth:`~da.p7core.gtapprox.Model.modify()`,
    the model will still evaluate outputs for any input that is within the range
    previously set by :arg:`x_meta` in :meth:`~da.p7core.gtapprox.Builder.build()`.
    Generally, it is not recommended to edit the model constraints information
    with :meth:`~da.p7core.gtapprox.Model.modify()` to avoid confusion.

    The :arg:`strip` argument can be used to remove accuracy evaluation (AE) and smoothing features
    from the model.
    It can be a string or a list of strings specifying which features to remove:

    * ``"ae"`` --- remove accuracy evaluation.
    * ``"smoothing"`` --- remove smoothing.
    * ``"output_bounds"`` --- disable the output bounds (thresholds), which were previously set
      with the :arg:`y_meta` parameter when training the model or using :meth:`~da.p7core.gtapprox.Model.modify()`.

    Removing AE may be useful for models trained with the GP, HDAGP, SGP, or TGP techniques
    (other techniques do not support AE).
    It reduces the size of the of the main model section (see :ref:`special_model_structure`),
    thus decreasing the model size in memory.
    Also it significantly reduces volume of the C code generated by :meth:`~da.p7core.gtapprox.Model.export_to()`.
    The :attr:`~da.p7core.gtapprox.Model.has_ae` property of the modified model will be ``False``.

    Removing the smoothing feature reduces the size of the of the main model section only.
    It decreases the model size, but not the volume of exported code.
    The size reduction is most noticeable for models trained with the RSM and HDA techniques
    (up to 10 times for HDA).
    If the model was smoothed before :meth:`~da.p7core.gtapprox.Model.modify()`,
    the modified model remains smoothed.
    However, smoothing methods will no longer be available from the modified model
    (:attr:`~da.p7core.gtapprox.Model.has_smoothing` will be ``False``).

    Note that :meth:`~da.p7core.gtapprox.Model.modify()`
    returns a new modified model, which is identical to the original
    except your modifications.

    See also :ref:`ug_gtapprox_details_model_metainfo`.

    """
    metainfo = self.__metainfo()
    new_metainfo = _shared.preprocess_metainfo(x_meta, y_meta, self.size_x, self.size_f, ignorable_keys=_shared.collect_metainfo_keys(metainfo))

    if x_meta is not None:
      # Do not loose variability info for new models!!
      for var_new_meta, var_meta in zip(new_metainfo['Input Variables'], metainfo['Input Variables']):
        for key in var_meta:
          if key not in var_new_meta:
            var_new_meta[key] = var_meta[key]
      metainfo.update({'Input Variables': new_metainfo['Input Variables']})
    if y_meta is not None:
      for var_new_meta, var_meta in zip(new_metainfo['Output Variables'], metainfo['Output Variables']):
        # if user modified enumerators then we store it as labels because we hide labels from user
        if var_meta.get("variability", "continuous") == "enumeration" and "enumerators" in var_new_meta:
          var_new_meta["labels"] = var_new_meta.pop("enumerators")

        for key in var_meta:
          if key not in var_new_meta:
            var_new_meta[key] = var_meta[key]
      metainfo.update({'Output Variables':  new_metainfo['Output Variables']})

    return self.__modify(comment=comment, annotations=annotations, metainfo=metainfo, strip=strip)

  def __modify(self, comment=None, annotations=None, metainfo=None, strip=None):
    """
    Create a copy of the model with modified additional information.
    """
    if comment is None and annotations is None and metainfo is None and not strip:
      return self

    # Prepare comment pointer
    if comment is not None:
      if not isinstance(comment, _six.string_types):
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

    # additional flags
    if not strip:
      strip_ptr = _ctypes.c_char_p()
    elif not _shared.is_iterable(strip):
      raise ValueError("Invalid \"strip\" parameter is given: string or iterable of strings is expected.")
    else:
      if not isinstance(strip, _six.string_types):
        try:
          strip = [(feature if isinstance(feature, _six.string_types) else str(feature)) for feature in strip]
        except:
          tb = _sys.exc_info()[2]
          _six.reraise(ValueError, "Invalid \"strip\" parameter is given: string or iterable of strings is expected.", tb)
      strip_ptr = _shared.write_json(strip).encode('ascii')

    # Modify model
    errdesc = _ctypes.c_void_p()
    handle = self._backend.modify_model(self.__instance, comment_ptr, annotations_ptr, metainfo_ptr, strip_ptr, _ctypes.byref(errdesc))

    if not handle:
      _shared._raise_on_error(0, 'Failed to modify model.', errdesc)
    return Model(handle=handle)

  def _split(self, outputs, concatenate=False, initial_model_mode=False):
    self.__requireOR()
    if not outputs:
      return [self,]

    n_models = 1 if concatenate else len(outputs)
    split_models = (_ctypes.c_void_p * n_models)()
    outputs_of_interest = _numpy.array(outputs, dtype=_ctypes.c_size_t).reshape(-1)

    error_description = _ctypes.c_void_p()
    _shared._raise_on_error(self._backend.split_model_outputs(self._Model__instance, (1 if initial_model_mode else 0),
                                                              outputs_of_interest.shape[0], outputs_of_interest.ctypes.data_as(self._backend.c_size_t_p),
                                                              n_models, _ctypes.cast(split_models, self._backend.c_void_p_p),
                                                              _ctypes.byref(error_description)),
                            "The model was trained in the incompatible componentwise mode.", error_description)

    original_metainfo = self._Model__metainfo()['Output Variables']
    if concatenate:
      model = Model(handle=split_models[0])
      metainfo = model._Model__metainfo()
      metainfo['Output Variables'] = [original_metainfo[output] for output in outputs]
      return [model._Model__modify(comment=self.comment, annotations=self.annotations, metainfo=metainfo)]
    else:
      models = []
      for model_instance, output in zip(split_models, outputs):
        model = Model(handle=model_instance)
        metainfo = model._Model__metainfo()
        metainfo['Output Variables'] = [original_metainfo[output]]
        models.append(model._Model__modify(comment=self.comment, annotations=self.annotations, metainfo=metainfo))
      return models

  @staticmethod
  def available_sections(**kwargs):
    """Get a list of available model sections.

    :keyword file: file object or path to load model from
    :keyword string: serialized model
    :keyword model: model object
    :type file: ``file`` or ``str``
    :type string: ``str``
    :type model: :class:`~da.p7core.gtapprox.Model`
    :return: available model sections
    :rtype: ``list``

    .. versionadded:: 6.11

    Returns a list of strings specifying which sections can be loaded from the model:

    * ``"model"``: main model section, required for model evaluation and smoothing methods.
    * ``"info"``: model information, required for :attr:`~da.p7core.gtapprox.Model.info`.
    * ``"comment"``: comment section, required for :attr:`~da.p7core.gtapprox.Model.comment`.
    * ``"annotations"``: annotations section, required for :attr:`~da.p7core.gtapprox.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, required for :attr:`~da.p7core.gtapprox.Model.training_sample`.
    * ``"iv_info"``: internal validation data, required for :attr:`~da.p7core.gtapprox.Model.iv_info`.
    * ``"build_log"``: model training log, required for :attr:`~da.p7core.gtapprox.Model.build_log`.

    See :ref:`special_model_structure` for details.

    """
    if sum(bool(kwargs.get(_)) for _ in ['file', 'string', 'model']) != 1:
      raise ValueError("Exact one input argument must be set: either 'file' or 'string' or 'model'.")

    binary_data = None
    model = None

    if 'file' in kwargs:
      try:
        binary_data = kwargs['file'].read(-1)
      except AttributeError:
        binary_data = None

      if binary_data is None:
        with open(kwargs['file'], 'rb') as f:
          binary_data = f.read(-1)
    elif 'string' in kwargs:
      binary_data = _shared.wrap_with_exc_handler(_base64.b64decode, _ex.GTException)(kwargs['string'])
    elif 'model' in kwargs:
      model = kwargs['model']
      if not isinstance(model, Model):
        raise ValueError("Value of the 'model' argument must have type %s" % Model)
    else:
      raise ValueError("Neither 'file' nor 'string' nor 'model' argument is given.")

    errdesc = _ctypes.c_void_p()
    sec_flags = _ctypes.c_uint(0)

    if binary_data is not None:
      succeeded = Model._default_backend().enum_load_sections(binary_data, len(binary_data), 0, _ctypes.byref(sec_flags), _ctypes.byref(errdesc))
    elif model is not None:
      succeeded = Model._default_backend().enum_save_sections(model.__instance, _ctypes.byref(sec_flags), _ctypes.byref(errdesc))
    else:
      raise ValueError("Failed to interpret input arguments.")

    _shared._raise_on_error(succeeded, 'Failed to read available model sections list.', errdesc)

    return Model.__sections_list(sec_flags.value)

  def load(self, file, sections='all'):
    """Load a model from file.

    :param file: file object or path
    :type file: ``file`` or ``str``
    :param sections: model sections to load
    :type sections: ``list`` or ``str``
    :return: ``None``

    .. versionchanged:: 6.6
       added the :arg:`sections` argument.

    .. deprecated:: 6.29
       use :class:`~da.p7core.gtdf.Model` constructor instead.

    A model can be loaded partially, omitting certain sections to reduce memory usage and load time.
    Note that availability of :class:`~da.p7core.gtapprox.Model` methods and attributes depends on which sections are loaded.
    This dependency is described in more detail in section :ref:`special_model_structure`.

    The :arg:`sections` argument can be a string or a list of strings specifying which sections to load:

    * ``"all"``: all sections (default).
    * ``"none"``: minimum model information, does not load any other section (the minimum load).
    * ``"model"``: main model section, required for model evaluation and smoothing methods.
    * ``"info"``: model information, required for :attr:`~da.p7core.gtapprox.Model.info`.
    * ``"comment"``: comment section, required for :attr:`~da.p7core.gtapprox.Model.comment`.
    * ``"annotations"``: annotations section, required for :attr:`~da.p7core.gtapprox.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, required for :attr:`~da.p7core.gtapprox.Model.training_sample`.
    * ``"iv_info"``: internal validation data, required for :attr:`~da.p7core.gtapprox.Model.iv_info`.
    * ``"build_log"``: model training log, required for :attr:`~da.p7core.gtapprox.Model.build_log`.

    To get a list of sections available for load, use :meth:`~da.p7core.gtapprox.Model.available_sections()`.

    """
    try:
      data = file.read(-1)
    except AttributeError:
      data = None

    if data is None:
      with open(file, 'rb') as fid:
        data = fid.read(-1)

    self.__reload_model(data, sections)

  def fromstring(self, modelString, sections='all'):
    """Deserialize a model from string.

    :param modelString: serialized model
    :type modelString: ``str``
    :param sections: model sections to load
    :type sections: ``list`` or ``str``
    :return: ``None``

    .. versionchanged:: 6.6
       added the :arg:`sections` argument.

    A model can be loaded (deserialized) partially, omitting certain sections to reduce memory usage.
    Note that availability of :class:`~da.p7core.gtapprox.Model` methods and attributes depends on which sections are loaded.
    This dependency is described in more detail in section :ref:`special_model_structure`.

    The :arg:`sections` argument can be a string or a list of strings specifying which sections to load:

    * ``"all"``: all sections (default).
    * ``"none"``: minimum model information, does not load any other section (the minimum load).
    * ``"model"``: main model section, required for model evaluation and smoothing methods.
    * ``"info"``: model information, required for :attr:`~da.p7core.gtapprox.Model.info`.
    * ``"comment"``: comment section, required for :attr:`~da.p7core.gtapprox.Model.comment`.
    * ``"annotations"``: annotations section, required for :attr:`~da.p7core.gtapprox.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, required for :attr:`~da.p7core.gtapprox.Model.training_sample`.
    * ``"iv_info"``: internal validation data, required for :attr:`~da.p7core.gtapprox.Model.iv_info`.
    * ``"build_log"``: model training log, required for :attr:`~da.p7core.gtapprox.Model.build_log`.

    To get a list of sections available for load, use :meth:`~da.p7core.gtapprox.Model.available_sections()`.
    """
    binary_data = _shared.wrap_with_exc_handler(_base64.b64decode, _ex.GTException)(modelString)
    self.__reload_model(binary_data, sections)

  def smooth(self, f_smoothness):
    """Apply smoothing to model.

    :param f_smoothness: output smoothing factors
    :type f_smoothness: ``float`` or :term:`array-like`, 1D
    :return: smoothed model
    :rtype: :class:`~da.p7core.gtapprox.Model`
    :raise: :exc:`~da.p7core.GTException` if the model does not support smoothing

    .. versionadded:: 1.9.0

    Check :attr:`~da.p7core.gtapprox.Model.has_smoothing` before using this method.

    This method creates and returns a new smoothed model. The amount of smoothing is specified by the
    ``f_smoothness`` argument. Details on model smoothing can be found in section :ref:`special_smoothing`.
    """
    self.__requireModelSection()

    if not self.has_smoothing:
      raise _ex.FeatureNotAvailableError('Smoothing is not available for this model')

    return _smoothing._smooth(f_smoothness, self)


  def smooth_anisotropic(self, f_smoothness, x_weights):
    """Apply anisotropic smoothing to model.

    :param f_smoothness: output smoothing factors
    :type f_smoothness: ``float`` or :term:`array-like`, 1D
    :param x_weights: the amount of smoothing by different input components
    :type x_weights: :term:`array-like`, 1D or 2D
    :return: smoothed model
    :rtype: :class:`~da.p7core.gtapprox.Model`
    :raise: :exc:`~da.p7core.GTException` if the model does not support smoothing

    .. versionadded:: 1.9.0

    Check :attr:`~da.p7core.gtapprox.Model.has_smoothing` before using this method.

    This method extends the simple smoothing functionality (see :meth:`smooth()`) by allowing anisotropic smoothing:
    ``x_weights`` specify relative smoothing by different components of the input.

    Details on anisotropic smoothing can be found in section :ref:`special_anisotropic_smooth`.

    """
    self.__requireModelSection()

    if not self.has_smoothing:
      raise _ex.FeatureNotAvailableError('Smoothing is not available for this model')

    return _smoothing._smooth_anisotropic(f_smoothness, x_weights, self)

  def smooth_errbased(self, x_sample, f_sample, error_type, error_thresholds, x_weights=None):
    """Apply error based smoothing to model, controlling model errors over a reference inputs-responses array.

    :param x_sample: reference inputs
    :type x_sample: ``float`` or :term:`array-like`, 1D or 2D
    :param f_sample: reference responses
    :type f_sample: ``float`` or :term:`array-like`, 1D or 2D
    :param error_type: error types to calculate
    :type error_type: ``str`` or ``list[str]``
    :param error_thresholds: error thresholds
    :type error_thresholds: ``float`` or :term:`array-like`, 1D
    :param x_weights: the amount of smoothing for different input components
    :type x_weights: :term:`array-like`, 1D or 2D
    :return: smoothed model
    :rtype: :class:`~da.p7core.gtapprox.Model`
    :raise: :exc:`~da.p7core.GTException` if the model does not support smoothing

    .. versionadded:: 1.9.0

    Check :attr:`~da.p7core.gtapprox.Model.has_smoothing` before using this method.

    This method creates and returns a model which has maximum smoothness while
    preserving approximation errors of the model below specified threshold.

    Details on error-based smoothing can be found in section :ref:`special_error_based_smooth`.
    """
    self.__requireModelSection()

    if not self.has_smoothing:
      raise _ex.FeatureNotAvailableError('Smoothing is not available for this model')

    if self._categorical_x_map:
      x_sample = _shared.as_matrix(x_sample, shape=(None, self.size_x), order='A', name="'x_sample' argument", dtype=None)
      x_sample = _shared.encode_categorical_values(x_sample, self._categorical_x_map, "'x_sample' argument")
    else:
      x_sample = _shared.as_matrix(x_sample, shape=(None, self.size_x), order='A', name="'x_sample' argument")

    if self._categorical_f_map:
      f_sample = _shared.as_matrix(f_sample, shape=(None, self.size_f), order='A', name="'f_sample' argument", dtype=None)
      f_sample = _shared.encode_categorical_values(f_sample, self._categorical_f_map, "'f_sample' argument")
    else:
      f_sample = _shared.as_matrix(f_sample, shape=(None, self.size_f), order='A', name="'f_sample' argument")

    return _smoothing._smooth_errbased(x_sample, f_sample, error_type, error_thresholds, x_weights, self)

  def __init__(self, file=None, **kwargs):
    """Constructor."""
    self.__init_self()

    handle = kwargs.get('handle')
    if not handle:
      modelString = kwargs.get('string')
      modelSections = kwargs.get('sections', 'all')
      if modelString and file:
        raise ValueError("Only one argument 'file' or 'string' must be set")
      if modelString:
        self.fromstring(modelString, sections=modelSections)
      elif file:
        self.load(file, sections=modelSections)
      else:
        raise ValueError("'file' argument must be file object or file name")
    else:
      self.__instance = handle
      self.__weak_reference = bool(kwargs.get('weak_handle'))

  def __del__(self):
    """Destructor."""
    if self.__instance and not self.__weak_reference:
      self._backend.delete_model(self.__instance, self._backend.c_void_p_p())

  @staticmethod
  def __str_var_info(data):
    vars_stat = dict((k, 0) for k in set(str(v["variability"]) for v in data))
    for v in data:
      vars_stat[v["variability"]] += 1
    return ", ".join("%d %s" % (vars_stat[k], k) for k in vars_stat)

  @staticmethod
  def __str_details_key(details, key, output):
    if key in details:
      output.append("'%s' (global)" % key)
    else:
      count = sum(key in data for data in details.get("Model Decomposition", []))
      if count:
        output.append("'%s' (%d submodels)" % (key, count))

  @staticmethod
  def __str_dict(details, key, out):
    data = details.get(key)
    if not data:
      return
    out.write(key + "\n")
    fmt = "  '%%-%ds' : '%%s'\n" % max(len(k) for k in data)
    for k in data:
      out.write(fmt % (k, data[k]))

  def __str__(self):
    info = _six.StringIO()
    if self.comment:
      info.write(_shared._safestr(self.comment).rstrip(" \n") + "\n")

    feature_list = []
    if self.has_ae:
      feature_list.append("AE")
    if self.has_smoothing:
      feature_list.append("smoothed" if self.is_smoothed else "smoothable")

    info_list = []
    if self.iv_info:
      info_list.append("iv_info")
    if self.training_sample:
      info_list.append("training_sample")
    if self.annotations:
      info_list.append("annotations")

    details_keys = []
    if self.details.get("Model Decomposition"):
      details_keys.append("'Model Decomposition' (%d)" % len(self.details["Model Decomposition"]))

    self.__str_details_key(self.details, "Regression Model", details_keys)
    self.__str_details_key(self.details, "Input Constraints", details_keys)
    self.__str_details_key(self.details, "Output Constraints", details_keys)

    info.write("Input Size:    %s (%s)\n" % (self.size_x, self.__str_var_info(self.details["Input Variables"])))
    info.write("Output Size:   %s (%s)\n" % (self.size_f, self.__str_var_info(self.details["Output Variables"])))
    info.write("Technique:     %s\n" % self.details.get("Technique", "<not set>"))
    info.write("Features:      %s\n" % (", ".join(feature_list) if feature_list else "-"))
    info.write("Attachments:   %s\n" % (", ".join(info_list) if info_list else "-"))
    info.write("Model Details: %s\n" % (",\n               ".join(details_keys) if details_keys else "-"))
    info.write("Training Time: %s\n" % self.details.get("Training Time", {}).get("Total", "-"))
    self.__str_dict(self.details, "Training Options", info)
    self.__str_dict(self.details, "Training Hints", info)

    return info.getvalue()

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
    self.__weak_reference = False
    self.__cache = {}

  @staticmethod
  def _default_backend(backend=_api):
    # intentionally assign single shared _api object as default value so we keep backend loaded as long as this method exists
    return _api if backend is None else backend

  def __requireAE(self):
    if not self.has_ae:
      raise _ex.FeatureNotAvailableError('Accuracy Evaluation is not available for this model')

  def __requirePE(self):
    if not self._has_pe:
      raise _ex.FeatureNotAvailableError('Probability Estimation is not available for this model')

  def __requireOR(self):
    if not self._has_or:
      raise _ex.FeatureNotAvailableError('The model was trained in the incompatible componentwise mode, outputs rearrangement is not available')

  def __requireModelSection(self):
    if not self.__hasFeature(self._backend.FEATURE_CALC_LOADED):
      raise _ex.FeatureNotAvailableError('The required "model" section has not been loaded.')

  def __hasFeature(self, feature_id):
    if not self.__instance:
      return False

    errdesc = _ctypes.c_void_p()
    result = _ctypes.c_short()
    _shared._raise_on_error(self._backend.has_feature(self.__instance, _ctypes.c_int(feature_id),
                                                      _ctypes.byref(result), _ctypes.byref(errdesc)),
                            'Failed to get model feature state!', errdesc)
    return result.value != 0

  def __checkCall(self, susseeded, errdesc):
    _shared._raise_on_error(susseeded, "Backend call failed.", errdesc)

  def __sections_code(self, sections):
    if isinstance(sections, _six.string_types):
      code = self.__MODEL_SECTIONS.get(sections, None)
      if code is None:
        raise ValueError('Unknown section name "%s" is given' % sections)
    else:
      code = self.__MODEL_SECTIONS.get('none', 0)
      for section in sections:
        curr_code = self.__MODEL_SECTIONS.get(section, None)
        if curr_code is None:
          raise ValueError('Unknown section name "%s" is given' % section)
        code |= curr_code

    return code

  @staticmethod
  def __sections_list(code):
    sections = []
    for name, flag in _six.iteritems(Model.__MODEL_SECTIONS):
      if (code & flag) == flag:
        sections.append(name)
    return sections

  def __reload_model(self, binary_data, sections):
    if self.__instance is not None:
      if not self.__weak_reference:
        self._backend.delete_model(self.__instance, self._backend.c_void_p_p())
      self.__instance = None
      self.__weak_reference = False
      self.__cache = {}

    loader = _ctypes.c_void_p(self._backend.create_loader())
    if not loader:
      raise _ex.GTException('Failed to initialize model loader!')

    try:
      sections_code = self.__sections_code(sections)
      self.__instance = _ctypes.c_void_p(self._backend.selective_load(loader, binary_data, len(binary_data), sections_code))
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

  def _validate(self, pointsX, pointsY, weights):
    self.__requireModelSection()

    # read errors list first
    errdesc = _ctypes.c_void_p()
    errorsListSize = _ctypes.c_size_t()
    self.__checkCall(self._backend.validation_errors_list(self.__instance, _ctypes.c_char_p(), _ctypes.byref(errorsListSize), _ctypes.byref(errdesc)), errdesc)
    errorsList = (_ctypes.c_char * errorsListSize.value)()
    self.__checkCall(self._backend.validation_errors_list(self.__instance, errorsList, _ctypes.byref(errorsListSize), _ctypes.byref(errdesc)), errdesc)
    errorsList = _shared.parse_json_deep(_shared._preprocess_json(errorsList.value), list)

    pointsX = _shared.encode_categorical_values(pointsX, self._categorical_x_map, "input")
    pointsY = _shared.encode_categorical_values(pointsY, self._categorical_f_map, "output")

    # perform validation
    size_x = self.size_x
    size_f = self.size_f
    cpointsX = _shared.py_matrix_2c(pointsX, size_x, name="'pointsX' argument")
    cpointsY = _shared.py_matrix_2c(pointsY, size_f, name="'pointsY' argument")
    if cpointsX.array.shape[0] != cpointsY.array.shape[0]:
      raise ValueError('Sizes of reference samples do not match (%d != %d)!' % (cpointsX.array.shape[0], cpointsY.array.shape[0]))

    sample_size = cpointsX.array.shape[0]

    if not self._backend.check_input(self.__instance, sample_size, cpointsX.ptr, cpointsX.ld, 1, _ctypes.byref(errdesc)):
      _warn.warn(_shared._release_error_message(errdesc)[1])
      #_shared._raise_on_error(0, 'Input data contains NaN or Inf value', errdesc)

    cpointsW = _shared.py_vector_2c(weights, sample_size, name="'weights' argument") if weights is not None and sample_size > 1 \
          else _shared.ArrayPtr(self._backend.c_double_p(), 0)

    ince = len(errorsList)
    result = (_ctypes.c_double * (size_f * ince))()
    _shared._raise_on_error(self._backend.validate_weighted(self.__instance, _ctypes.c_size_t(sample_size),
                                          cpointsX.ptr, cpointsX.ld, cpointsY.ptr, cpointsY.ld,
                                          cpointsW.ptr, cpointsW.inc,
                                          result, _ctypes.c_size_t(ince), _ctypes.byref(errdesc)),
                            'Model validation error', errdesc)

    validationResult = {}
    result = list(result[:])
    for err_index, err_name in enumerate(errorsList):
      validationResult[err_name] = result[err_index::ince]
    return validationResult

  @property
  def _training_domains(self):
    if self.__cache.get('model_training_domains') is None:
      errdesc = _ctypes.c_void_p()
      size = _ctypes.c_size_t()
      self.__checkCall(self._backend.model_training_domains(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      model_training_domains = (_ctypes.c_char * size.value)()
      self.__checkCall(self._backend.model_training_domains(self.__instance, model_training_domains, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      self.__cache['model_training_domains'] = _shared.parse_json_deep(_shared._preprocess_json(model_training_domains.value), dict)
    return self.__cache['model_training_domains']

  def _find_extrema(self, bounds=None):
    self.__requireModelSection()

    size_x, size_f = self.size_x, self.size_f

    if bounds is not None:
      values = [] # flatten list of lists
      range_index = _numpy.zeros((size_x + 1,), dtype=_ctypes.c_size_t) # i-th element indicates the beginning of i-th list in values

      categorical_variables_map = self._categorical_x_map or {}

      for i, bounds_i in enumerate(bounds):
        if i > size_x:
          raise ValueError("Invalid length of bounds: %d elements are expected" % (size_x,))

        if i in categorical_variables_map:
          dtype, labels, enumerators = categorical_variables_map[i]
          values.extend(_shared._encode_categorical_variable(dtype=dtype, labels=labels, enumerators=enumerators, values_in=bounds_i))
        else:
          values.extend(_shared.as_matrix(bounds_i, (1, None))[0])
        range_index[(i+1):] = len(values) # always extend forward, so incomplete bounds are allowed

      values = _numpy.array(values, dtype=float)
      values_ptr = values.ctypes.data_as(self._backend.c_double_p)
      range_index_ptr = range_index.ctypes.data_as(self._backend.c_size_t_p)
    else:
      values_ptr, range_index_ptr = self._backend.c_double_p(), self._backend.c_size_t_p()

    errdesc = _ctypes.c_void_p()
    extrema_data = _numpy.empty((2 * size_f, size_x + 1))
    self.__checkCall(self._backend.find_extrema(self.__instance,
                                                values_ptr, range_index_ptr, # compressed list of lists
                                                extrema_data.ctypes.data_as(self._backend.c_double_p),
                                                extrema_data.strides[0] // extrema_data.itemsize,
                                                extrema_data.strides[1] // extrema_data.itemsize,
                                                _ctypes.byref(errdesc)), errdesc)

    return _PropertiesTransport(argmin=extrema_data[:size_f, :-1].copy(), valmin=extrema_data[:size_f, -1].copy(),
                                argmax=extrema_data[size_f:, :-1].copy(), valmax=extrema_data[size_f:, -1].copy())

  def shap_value(self, point, data=None, interactions=False, approximate=False, shap_compatible=True):
    """Compute SHAP (SHapley Additive exPlanations) values.

    :param point: a point or sample to evaluate
    :type point: ``float`` or :term:`array-like`, 1D or 2D
    :param data: optional background data sample
    :type data: ``float`` or :term:`array-like`, 1D or 2D
    :param interactions: if ``True``, evaluate pairwise interactions (supported by GBRT models only)
    :type interactions: ``bool``
    :param approximate: if ``True``, compute approximate SHAP values (fast but less accurate)
    :type approximate: ``bool``
    :param shap_compatible: if ``True``, return ``shap.Explanation`` (requires :mod:`shap`)
    :type shap_compatible: ``bool``
    :return: explanations
    :rtype: ``shap.Explanation`` or ``tuple`` (elements depend on the :arg:`point` type)

    .. versionadded:: 6.20

    Evaluates `SHAP <https://pypi.org/project/shap/>`_,
    using an optimized internal implementation when possible.
    The following models support the internal method
    and do not require the :mod:`shap` module,
    if you set :arg:`shap_compatible` to ``False``:

    * All models trained with the GBRT technique.
    * All differentiable models --- that is,
      all models without categorical variables.

    Other models use ``shap.PermutationExplainer`` and require :mod:`shap`.

    The :arg:`point` syntax is the same as in :meth:`~da.p7core.gtapprox.Model.calc()`:
    general form is a 2D array, and several simplified forms are supported.
    When :arg:`shap_compatible` is ``False``, the return value is a pair (tuple)
    where elements depend on the :arg:`point` type:

    * If :arg:`point` is a single point, the return pair is
      a scalar base value and
      an ``ndarray`` --- 1D or 2D, depending on :arg:`interactions`.
    * If :arg:`point` is a sample, the return pair is
      a list of base values for each output and
      an ``ndarray`` --- 2D or 3D, also depending on :arg:`interactions`.
      In this case, a base value for an output is the average of this output
      over the training dataset.

    Array structure in results is:

    * If :arg:`interactions` is ``False`` (default),
      resulting SHAP values form an `n \\times m` matrix, where
      `n` in the number of points in :arg:`point`, and `m` is the model's input dimension.
      Each matrix row contains contributions of model inputs
      to push the model output from the base value.
    * If :arg:`interactions` is ``True``,
      contributions for each input point form an `m \\times m` matrix,
      where main effects are on the diagonal and interaction effects are off-diagonal.
      Resulting SHAP values form an `n \\times m \\times m` array.
      Note that only GBRT models support pairwise interactions.

    For more convenience, if you have :mod:`shap` installed,
    set :arg:`shap_compatible` to ``True`` to return a ``shap.Explanation`` object.

    GBRT models estimate SHAP values by a fast and exact method for tree models and ensembles of trees.
    Differentiable models (without categorical variables) approximate SHAP values
    using expected gradients (*Sundararajan et al. 2017*) ---
    an extension of integrated gradients, a feature attribution method designed for
    differentiable models based on an extension of Shapley values
    to infinite player games (Aumann-Shapley values).
    """

    self.__requireModelSection()

    if shap_compatible:
      try:
        import shap as _shap
      except:
        exc_info = _sys.exc_info()
        _shared.reraise(ValueError, "Cannot import the shap module required in the SHAP compatibility mode. %s" % (exc_info[1],), exc_info[2])

    if self._categorical_x_map:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument", dtype=object)
      input = _shared.encode_categorical_values(input, self._categorical_x_map, 'input')
    else:
      input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")

    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or infinity values')

    mode = []
    shap_vec_size = self.size_x + 1
    if interactions:
      shap_vec_size *= shap_vec_size
      mode.append("interactions")
    if approximate:
      mode.append("fast")

    if data is not None:
      data = _shared.as_matrix(data, shape=(None, self.size_x), order='A', name="'data' argument")
    else:
      # try to read training sample as data
      data = [sample['x'] for sample in self.training_sample if 'x' in sample]
      data = _numpy.empty((0, self.size_x)) if not data else _numpy.vstack(data)

    # output-major order for compatibility with old SHAP format
    output = _numpy.ndarray((self.size_f, input.shape[0], shap_vec_size), dtype=float, order='C')
    errdesc = _ctypes.c_void_p()

    data_matrix = _CallbackMatrixReader(data) if shap_compatible else None
    try_permutations = False

    mode = ",".join(mode)
    if not self._backend.shapley_value(self.__instance, mode.encode('ascii'), len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                       input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                       len(data), data.ctypes.data_as(self._backend.c_double_p), \
                                       data.strides[0] // data.itemsize, data.strides[1] // data.itemsize, \
                                       output.ctypes.data_as(self._backend.c_double_p), \
                                       output.strides[1] // output.itemsize, output.strides[0] // output.itemsize, output.strides[2] // output.itemsize, \
                                       (data_matrix.callback if data_matrix is not None else _ctypes.c_void_p()), _ctypes.byref(errdesc)):
      exc_type, message = _shared._release_error_message(errdesc) # release error message first
      if data_matrix is not None:
        data_matrix.process_exception() # reraise an internal data reader exception if any

      if exc_type == _ex.FeatureNotAvailableError and shap_compatible:
        try_permutations = True
      else:
        raise exc_type("SHAP evaluation error: " + (message if message else "no particular reason given"))

    feature_names = [info.get("name", ("x[%d]" % i)) for i, info in enumerate(self.details["Input Variables"])]

    if try_permutations:
      # @todo : if model contains multiple categorical variables and only known combinations of cat. variables
      #         is allowed then custom masker must be used. Implementation is delayed until request.
      try:
        explainer = _shap.explainers.Permutation(self.calc, data_matrix.data, features_names=feature_names)
      except TypeError:
        explainer = None

      if explainer is None:
        # workaround for features_names absence
        try:
          import pandas as _pandas
          featured_data = _pandas.DataFrame(data_matrix.data, columns=feature_names)
        except:
          featured_data = data_matrix.data
        explainer = _shap.explainers.Permutation(self.calc, featured_data)

      return explainer(input, silent=True)

    if interactions:
      output = output.reshape(output.shape[0], output.shape[1], (self.size_x + 1), (self.size_x + 1))

    if not shap_compatible:
      if interactions:
        base_values = [_numpy.mean(_[:, -1, -1]) for _ in output]
        shap_values = [_[:, :-1, :-1] for _ in output]
      else:
        base_values = [_numpy.mean(_[:, -1]) for _ in output]
        shap_values = [_[:, :-1] for _ in output]

      return (base_values[0], shap_values[0]) if output.shape[0] == 1 else (base_values, shap_values)

    if interactions:
      base_values = output[:, :, -1, -1].T # n points, size_f
      shap_values = _numpy.rollaxis(output[:, :, :-1, :-1], 0, 4) # n points, size_x, size_x, size_f
    else:
      base_values = output[:, :, -1].T # n points, size_f
      shap_values = _numpy.rollaxis(output[:, :, :-1], 0, 3) # n points, size_x, size_f

    if self.size_f == 1:
      shap_values = shap_values.reshape(shap_values.shape[:-1])
      base_values = base_values.reshape(base_values.shape[:-1])

    if single_vector:
      shap_values = shap_values[0]
      base_values = base_values[0]

    return _shap.Explanation(shap_values, base_values=base_values, data=input, feature_names=feature_names)

  @property
  def _compatible_techniques(self):
    """
    Returns a list of techniques that can be used to incrementally train this model.
    """
    if self.__cache.get('_compatible_techniques') is None:
      compatible_techniques = self._backend.read_str(self.__instance, self._backend.enum_compatible_tech_list)
      self.__cache['_compatible_techniques'] = _shared.parse_json_deep(compatible_techniques, list)
    return self.__cache['_compatible_techniques']

_FILE_SIZE_THRESHOLD = {}

def _debug_export_file_size(format, file_size=None):
  if file_size is not None:
    file_size = int(file_size)
    if file_size < 0:
      raise ValueError("File size threshold must be non-negative")

  try:
    norm_format = str(format).lower()
    if norm_format not in ("me10", "cs10", "fmi20"):
      norm_format = None
  except:
    norm_format = None

  if norm_format is None:
    norm_format = ExportedFormat.from_string(format)

  if file_size is not None:
    _FILE_SIZE_THRESHOLD[norm_format] = file_size

  return _FILE_SIZE_THRESHOLD.get(norm_format, 0)
