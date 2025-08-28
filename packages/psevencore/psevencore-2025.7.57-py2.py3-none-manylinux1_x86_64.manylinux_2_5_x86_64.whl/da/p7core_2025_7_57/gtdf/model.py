#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


"""
Data fusion model.

.. currentmodule:: da.p7core.gtdf.model
"""

from __future__ import with_statement
from __future__ import division

import sys as _sys
from pprint import pformat
from warnings import warn as _warn
import ctypes as _ctypes
import base64 as _base64
import numpy as _numpy

from .. import six as _six
from ..six.moves import xrange
from .. import shared as _shared
from .. import exceptions as _ex
from . import GradMatrixOrder
from .. import blackbox as _blackbox
from .. import license as _license

from ..utils import bbconverter as _bbconverter

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_double_p = _ctypes.POINTER(_ctypes.c_double)
    self.c_void_p_p = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_size_t_p = _ctypes.POINTER(_ctypes.c_size_t)

    _PGETSTR = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_t_p, self.c_void_p_p)
    _PGETSIZE = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_size_t_p, self.c_void_p_p)
    _INTERACTIVE_MODEL = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p)

    self.delete_model = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_p)(('GTDFModelFree', self.__library))
    self.batch_calc_bb = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_double, _ctypes.c_char_p, # ret. value, model, blackbox callback, blackbox opaque, blackbox num. gradient step (nan if blackbox supports gradients), evaluation mode
                                        _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, # points number, x, ldx, incx, f, ldf
                                        _ctypes.c_size_t, _ctypes.c_size_t, self.c_void_p_p)(("GTDFModelBatchCalcBB", self.__library)) # inc_df, inc_dx, err. data
    self.validation_errors_list = _PGETSTR(("GTDFModelValidationErrorsList", self.__library))
    self.validate_bb = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_double,  # ret. value, model, blackbox callback, blackbox opaque, blackbox num. gradient step (nan if blackbox supports gradients)
                                         _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, # points num., x (inputs), ldx, f (reference outputs), ldf,
                                         self.c_double_p, _ctypes.c_size_t, self.c_double_p, _ctypes.c_size_t, # w (weights), incw, e (linearized error metrics), ince (distance between i-th and (i+1)-th model output for the same kind of error)
                                         self.c_void_p_p)(("GTDFModelValidateWeightedBB", self.__library))
    self.save = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, self.c_size_t_p, _ctypes.c_uint,
                                  self.c_void_p_p)(('GTDFModelSelectiveSave', self.__library))
    self.has_feature = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_int, _ctypes.POINTER(_ctypes.c_short),
                                         self.c_void_p_p)(("GTDFModelHasFeature", self.__library))
    self.train_sample_count = _PGETSIZE(("GTDFModelGetTrainSampleCount", self.__library))
    self.train_sample = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_int, self.c_size_t_p, self.c_size_t_p,
                                          self.c_size_t_p, self.c_void_p_p, self.c_void_p_p)(("GTDFModelGetTrainSample", self.__library))
    self.modify = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_char_p,
                                    _ctypes.c_char_p, self.c_void_p_p)(("GTDFModelModify", self.__library))
    self.read_license = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, self.c_void_p_p, self.c_void_p_p)(("GTDFModelGetLicenseManager", self.__library))
    self.enum_load_sections = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_short, _ctypes.POINTER(_ctypes.c_uint),
                                                self.c_void_p_p)(("GTDFModelAvailableLoadSections", self.__library))
    self.enum_save_sections = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_uint),
                                                self.c_void_p_p)(("GTDFModelAvailableSaveSections", self.__library))
    self.create_loader = _ctypes.CFUNCTYPE(_ctypes.c_void_p)(("GTDFModelLoaderNew", self.__library))
    self.selective_loader = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_size_t,
                                              _ctypes.c_uint)(('GTDFModelLoaderSelectiveLoad', self.__library))
    self.last_loader_error = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_t_p)(("GTDFModelLoaderGetLastError", self.__library))
    self.delete_loader = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTDFModelLoaderFree', self.__library))
    self.read_info = _PGETSTR(("GTDFModelGetInfo", self.__library))
    self.read_metainfo = _PGETSTR(("GTDFModelGetMetainfo", self.__library))
    self.read_log = _PGETSTR(("GTDFModelGetLog", self.__library))
    self.read_comment = _PGETSTR(("GTDFModelGetComment", self.__library))
    self.read_annotations = _PGETSTR(("GTDFModelGetAnnotations", self.__library))
    self.get_size_x = _PGETSIZE(("GTDFModelGetSizeX", self.__library))
    self.get_size_f = _PGETSIZE(("GTDFModelGetSizeF", self.__library))
    self.model_training_details = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, self.c_size_t_p,
                                                    _ctypes.POINTER(_ctypes.c_void_p))(("GTDFModelTrainingDetails", self.__library))

    self.GT_DF_MODEL_FEATURE_ACCURACY_EVALUATION = 0
    self.GT_DF_MODEL_FEATURE_BLACKBOX_CALCULATION = 1
    self.GT_DF_MODEL_FEATURE_SAMPLE_ACCURACY_EVALUATION = 2
    self.GT_DF_MODEL_FEATURE_BLACKBOX_ACCURACY_EVALUATION = 3
    self.GT_DF_MODEL_FEATURE_CALC_LOADED = 4

    self.BATCH_CALC_F = 'F'.encode('ascii')
    self.BATCH_CALC_dFdX = 'dF/dX'.encode('ascii')
    self.BATCH_CALC_AE = 'AE'.encode('ascii')
    self.BATCH_CALC_dAEdX = 'dAE/dX'.encode('ascii')

_api = _API()

class Model(object):
  """Data fusion model.

  Can be created by :class:`~da.p7core.gtdf.Builder` or
  loaded from a file via the :class:`~da.p7core.gtdf.Model` constructor.

  :class:`~da.p7core.gtdf.Model` objects are immutable.
  All methods which are meant to change the model return a new :class:`~da.p7core.gtdf.Model` instance.
  """

  __MODEL_SECTIONS = {"all":  0x7fffffff,
                      "none": 0x80000000,
                      "model": 0x00000001,
                      "info": 0x00000002,
                      "build_log": 0x00000004,
                      "iv_info": 0x00000008,
                      "comment": 0x00000010,
                      "training_sample": 0x00000020,
                      "annotations": 0x00000040,}

  @property
  def info(self):
    """Model description.

    :Type: ``dict``

    Contains all technical information which can be gathered from the model, including error evaluation.

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
  def details(self):
    r"""Detailed model information.

    :Type: ``dict``

    .. versionadded:: 6.14

    A detailed description of the model. Includes model metainformation,
    accuracy data, training sample statistics, and other data.

    The :attr:`.gtdf.Model.details` dictionary structure is generally
    the same as the :attr:`.gtapprox.Model.details` structure (described
    in section :ref:`ug_gtapprox_details_model_information`), with the
    following exceptions:

    * Training dataset information (the structure under ``details["Training Dataset"]``,
      see :ref:`ug_gtapprox_details_model_information_training_dataset_info`)
      for GTDF models is a list of dictionaries. Each of these dictionaries
      describes one of the training samples, in the order of increasing fidelity ---
      so the highest fidelity sample is the last (``details["Training Dataset"][-1]``).
    * GTDF model accuracy data (see :ref:`ug_gtapprox_details_model_information_training_dataset_info_accuracy`)
      is available only for the highest fidelity sample.
    * Regression model information and model decomposition are not applicable
      GTDF models, so the ``details["Regression Model"]`` and
      ``details["Model Decomposition"]`` keys never exist in :attr:`.gtdf.Model.details`.

    Also, in GTDF models from deprecated pSeven Core versions that were
    trained with the DA or DA_BB technique, the sample statistics
    dictionaries may omit the ``"Output"`` key as this information
    is not available from the model.

    """
    if self.__cache.get('details') is None:
      details = {}
      try:
        details = self.__read_details()
        metainfo = self.__metainfo()

        for key in metainfo: # user-defined metainfo must not overrite internal model details
          if key in ("Input Variables", "Output Variables") and key in details:
            for details_data, metainfo_data in zip(details[key], metainfo[key]):
              for k in metainfo_data:
                if k not in details_data:
                  details_data[k] = metainfo_data[k]
          else:
            details[key] = metainfo[key]

        for dataset_index, dataset_stat in enumerate(details.get("Training Dataset", [])):
          self.__append_nonempty(dataset_stat, ['Accuracy',], _shared.readStatistics(self.__instance, "Training Dataset", "GTDF", dataset_index=dataset_index))
          self.__append_nonempty(dataset_stat, ['Sample Statistics', 'Input'], _shared.readStatistics(self.__instance, "Input sample", "GTDF", dataset_index=dataset_index))
          self.__append_nonempty(dataset_stat, ['Sample Statistics', 'Output'], _shared.readStatistics(self.__instance, "Output sample", "GTDF", dataset_index=dataset_index))
          self.__append_nonempty(dataset_stat, ['Sample Statistics', 'Points Weights'], _shared.readStatistics(self.__instance, "Points weights", "GTDF", dataset_index=dataset_index))
          self.__append_nonempty(dataset_stat, ['Sample Statistics', 'Output Noise Variance'], _shared.readStatistics(self.__instance, "Output noise variance", "GTDF", dataset_index=dataset_index))

        if "Training Options" not in details and "Options" in self.info:
          details["Training Options"] = dict((k, v) for k, v in self.info.items() if not k.startswith("//"))
      finally:
        self.__cache['details'] = details
    return self.__cache['details']

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

  def __read_details(self):
    js_size = _ctypes.c_size_t()
    err_desc = self._backend.c_void_p_p()
    if self._backend.model_training_details(self.__instance, _ctypes.c_char_p(), _ctypes.byref(js_size), err_desc):
      js_data = (_ctypes.c_char * js_size.value)()
      if self._backend.model_training_details(self.__instance, js_data, _ctypes.byref(js_size), err_desc):
        return _shared.parse_json_deep(_shared._preprocess_json(js_data.value), dict)
    return dict()

  @staticmethod
  def __append_nonempty(dest, keys, data):
    if data:
      for k in keys[:-1]:
        dest = dest.setdefault(k, {})
      dest[keys[-1]] = data

  def __metainfo(self):
    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.read_metainfo(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    metainfo = (_ctypes.c_char * size.value)()
    self.__checkCall(self._backend.read_metainfo(self.__instance, metainfo, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
    metainfo = _shared.parse_json_deep(_shared._preprocess_json(metainfo.value), dict)

    # Backward compatibility
    if metainfo == {}:
      metainfo = _shared.preprocess_metainfo(None, None, self.size_x, self.size_f)
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
      errdesc = _ctypes.c_void_p()
      size = _ctypes.c_size_t()
      self.__checkCall(self._backend.read_log(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      log = (_ctypes.c_char * size.value)()
      self.__checkCall(self._backend.read_log(self.__instance, log, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      self.__cache['log'] = _shared._preprocess_utf8(log.value)
    return self.__cache['log']


  @property
  def comment(self):
    """
    Text comment to the model.

    :Type: ``str``

    .. versionadded:: 6.6

    Optional plain text comment to the model.
    You can add the comment when training a model
    and edit it using :meth:`~da.p7core.gtdf.Model.modify()`.

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

    .. versionadded:: 6.6

    The annotations dictionary can optionally contain any number of notes.
    All dictionary keys and values are strings.
    You can add annotations when training a model
    and edit them using :meth:`~da.p7core.gtdf.Model.modify()`.

    """
    if self.__cache.get('annotations') is None:
      errdesc = _ctypes.c_void_p()
      size = _ctypes.c_size_t()
      self.__checkCall(self._backend.read_annotations(self.__instance, _ctypes.c_char_p(), _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      annotations = (_ctypes.c_char * size.value)()
      self.__checkCall(self._backend.read_annotations(self.__instance, annotations, _ctypes.byref(size), _ctypes.byref(errdesc)), errdesc)
      self.__cache['annotations'] = _shared.parse_json_deep(_shared._preprocess_json(annotations.value), dict)
    return self.__cache['annotations']

  @property
  def training_sample(self):
    """
    Model training samples, in order of increasing fidelity, optionally stored with the model.

    :Type: ``list``

    .. versionadded:: 6.6

    If :ref:`GTDF/StoreTrainingSample<GTDF/StoreTrainingSample>` was on when training the model, this attribute contains a copy of training data. Otherwise it will be an empty list.

    Training data (list contents) is one or more ``dict`` elements sorted in order of increasing fidelity.
    Each dictionary has the following keys:

    * ``"x"`` --- the input part of the training sample (values of variables).
    * ``"f"`` --- the response part of the training sample (function values).
    * ``"tol"`` --- response noise variance. This key is optional and may be absent.
    * ``"weights"`` --- sample point weights. This key is optional and may be absent.

    .. note::

       Training sample data is stored in lightweight NumPy arrays that have limited lifetime which cannot exceed the lifetime of the model object.
       It means that you should avoid assigning these arrays to new variables.
       Either use them directly, or if you want to read this data without keeping the model object, create copies of arrays: ``train_x = my_model.training_sample["x"].copy``.

    """
    if self.__cache.get('training_sample') is None:
      training_sample_list = []

      null_size_t = self._backend.c_size_t_p()
      null_void_p = self._backend.c_void_p_p()

      ndim = _ctypes.c_size_t()
      nsamples = _ctypes.c_size_t()

      if not self._backend.train_sample_count(self.__instance, _ctypes.byref(nsamples), null_void_p):
        nsamples = 0

      for sample_idx in xrange(nsamples.value):
        training_sample = dict()

        for name, code in [('x', 1), ('f', 2), ('weights', 3), ('tol', 4)]:
          err = self._backend.train_sample(self.__instance, sample_idx, code, _ctypes.byref(ndim), null_size_t, null_size_t, null_void_p, null_void_p)
          if 0 == err or 0 == ndim.value or ndim.value > 2:
            continue

          shape = (_ctypes.c_size_t * ndim.value)()
          strides = (_ctypes.c_size_t * ndim.value)()
          data_ptr = _ctypes.c_void_p()

          err = self._backend.train_sample(self.__instance, sample_idx, code, _ctypes.byref(ndim), shape, strides, _ctypes.byref(data_ptr), null_void_p)
          if 0 == err or 0 == shape[0] or 0 == shape[ndim.value - 1]:
            continue

          data = _numpy.frombuffer((_ctypes.c_double * (shape[0]*strides[0])).from_address(data_ptr.value)).reshape((shape[0], strides[0]))
          data.flags['WRITEABLE'] = False

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

    *New in version 3.0 Beta 1.*

    A dictionary containing error values calculated during :term:`internal validation`.
    Has the same structure as the ``details["Training Dataset"]["Accuracy"]``
    dictionary in GTApprox model details --- see section
    :ref:`ug_gtapprox_details_model_information_training_dataset_info_accuracy`
    in :ref:`ug_gtapprox_details_model_information` for a full description.

    Additionally, if the model was trained with
    :ref:`GTDF/IVSavePredictions <GTDF/IVSavePredictions>` on,
    :attr:`~da.p7core.gtdf.Model.iv_info` also contains raw validation
    data: model values calculated during internal validation, reference
    inputs, and reference outputs. This data is stored under the ``"Dataset"`` key.

    If internal validation was not required when training the model
    (see :ref:`GTDF/InternalValidation <GTDF/InternalValidation>`),
    :attr:`~da.p7core.gtdf.Model.iv_info` is an empty dictionary.

    """
    if self.__cache.get('iv_info') is None:
      self.__cache['iv_info'] = _shared .readStatistics(self.__instance, "Internal Validation", "GTDF")
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
  def has_bb(self):
    """Blackbox-based model evaluation support.

    :Type: ``bool``

    .. versionadded:: 5.1

    Check this attribute before using :meth:`~da.p7core.gtdf.Model.calc()` or :meth:`~da.p7core.gtdf.Model.grad()` with the *blackbox* argument.
    If ``True``, the model supports blackbox-based evaluation and gradient calculation.
    If ``False``, then blackbox-based calculations are not available. In this case :meth:`~da.p7core.gtdf.Model.calc()` and :meth:`~da.p7core.gtdf.Model.grad()` raise an exception if *blackbox* is not ``None``.

    """
    return self.__hasFeature(self._backend.GT_DF_MODEL_FEATURE_BLACKBOX_CALCULATION)

  @property
  def has_ae(self):
    """:term:`Accuracy evaluation` support.

    :Type: ``bool``

    Check this attribute before using :meth:`~da.p7core.gtdf.Model.calc_ae()`.
    If ``True``, the model supports accuracy evaluation.
    If ``False``, then accuracy evaluation is not available, and :meth:`~da.p7core.gtdf.Model.calc_ae()` raises an exception.
    """
    return self.__hasFeature(self._backend.GT_DF_MODEL_FEATURE_ACCURACY_EVALUATION)

  @property
  def has_ae_bb(self):
    """Blackbox-based :term:`accuracy evaluation` support.

    :Type: ``bool``

    .. versionadded:: 5.1

    Check this attribute before using :meth:`~da.p7core.gtdf.Model.calc_ae()` with the *blackbox* argument.
    If ``True``, the model supports blackbox-based accuracy evaluation.
    If ``False``, then blackbox-based accuracy evaluation is not available, and :meth:`~da.p7core.gtdf.Model.calc_ae()` raises an exception if *blackbox* is not ``None``.
    """
    return self.__hasFeature(self._backend.GT_DF_MODEL_FEATURE_BLACKBOX_ACCURACY_EVALUATION)

  def calc(self, point, blackbox=None):
    """Evaluate the model.

    :param point: the sample or point to evaluate
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :param blackbox: optional low fidelity blackbox
    :type blackbox: :class:`~da.p7core.blackbox.Blackbox`, :class:`.gtapprox.Model`, or :class:`.gtdf.Model`
    :return: model values
    :rtype: ``pandas.DataFrame`` or ``pandas.Series`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 2D or 1D
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not support blackbox-based calculations but *blackbox* is not ``None``

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 5.1
       blackbox support added.

    .. versionchanged:: 6.20
       :arg:`blackbox` may be a :class:`.gtapprox.Model` or a :class:`.gtdf.Model`.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Evaluates a data sample or a single point, optionally requesting low fidelity data from the :arg:`blackbox`
    (check :attr:`~da.p7core.gtdf.Model.has_bb` before performing blackbox-based calculations).
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

    Using a low-fidelity blackbox in model evaluations increases accuracy,
    but at the same time effectively limits the model domain to the blackbox domain:
    if the point to evaluate is outside the blackbox variable bounds
    (see :arg:`bounds` in :meth:`da.p7core.blackbox.Blackbox.add_variable()`),
    blackbox-based :meth:`~da.p7core.gtdf.Model.calc()` returns NaN values of responses
    since it receives NaN responses from the blackbox.

    """
    self.__requireModelSection()

    original_bb = blackbox # store it to keep reference
    blackbox = self.__preprocess_blackbox(blackbox, False)
    numgrad_tol = float(blackbox.numerical_gradient_step) if blackbox is not None and not blackbox.gradients_enabled else _numpy.nan

    input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")
    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')
    output = _numpy.ndarray((input.shape[0], self.size_f), dtype=float, order='C')
    succeeded, errdesc = 0, _ctypes.c_void_p()

    try:
      with _blackbox.blackbox_callback(blackbox, _blackbox._SINGLE_RESPONSE_CALLBACK_TYPE) as (callback, magic_sig):
        succeeded = self._backend.batch_calc_bb(self.__instance, callback, magic_sig, numgrad_tol, self._backend.BATCH_CALC_F, \
                                                len(input), input.ctypes.data_as(self._backend.c_double_p),\
                                                input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                                output.ctypes.data_as(self._backend.c_double_p), \
                                                output.strides[0] // output.itemsize, output.strides[1] // output.itemsize, 1, \
                                                _ctypes.byref(errdesc))
    except:
      exc_type, exc_val, exc_tb = _sys.exc_info()
      model_error = _shared._release_error_message(errdesc)
      if model_error is not None and model_error[1]:
        exc_val = ("%s The origin of the exception is: %s" % (_shared._safestr(model_error[1]).strip(), _shared._safestr(exc_val).strip())) if exc_val else model_error[1]
      _shared.reraise(exc_type, exc_val, exc_tb)

    _shared._raise_on_error(succeeded, 'Model evaluation error', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      return _shared.make_pandas(output, single_vector, pandas_type, pandas_index, self._names_f)
    else:
      return output[0] if single_vector else output

  def calc_bb(self, blackbox, point):
    """Evaluate the model, requesting low fidelity data from the *blackbox*.

    .. deprecated:: 5.1
       use :meth:`~da.p7core.gtdf.Model.calc()` instead.

    This method is deprecated since the blackbox support was added
    to :meth:`~da.p7core.gtdf.Model.calc()`, and is kept for compatibility only.
    It is recommended to use :meth:`~da.p7core.gtdf.Model.calc()`
    with the *blackbox* argument to perform blackbox-based model evaluations.

    """
    return self.calc(point, blackbox=blackbox)

  def grad(self, point, order=GradMatrixOrder.F_MAJOR, blackbox=None):
    """Evaluate :term:`model gradient`.

    :param point: the sample or point to evaluate
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :param order: gradient matrix order
    :type order: :class:`GradMatrixOrder`
    :param blackbox: optional low fidelity blackbox
    :type blackbox: :class:`~da.p7core.blackbox.Blackbox`, :class:`.gtapprox.Model`, or :class:`.gtdf.Model`
    :return: model gradients
    :rtype: ``pandas.DataFrame`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 3D or 2D
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not support blackbox-based gradient calculation but *blackbox* is not ``None``

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 5.1
       blackbox support added.

    .. versionchanged:: 6.20
       :arg:`blackbox` may be a :class:`.gtapprox.Model` or a :class:`.gtdf.Model`.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Evaluates model gradients for a data sample or a single point,
    optionally requesting low fidelity data from the :arg:`blackbox`
    (check :attr:`~da.p7core.gtdf.Model.has_bb` before performing blackbox-based gradient calculation).
    In general form, :arg:`point` is a 2D array-like (a data sample).
    Several simplified argument forms are also supported, similar to :meth:`~da.p7core.gtdf.Model.calc()`.

    The returned array is 3D if :arg:`point` is a sample, and 2D if :arg:`point` is a single point.

    When using pandas data samples (:arg:`point` is a ``pandas.DataFrame``),
    a 3D array in return value is represented by a ``pandas.DataFrame`` with multi-indexing (``pandas.MultiIndex``).
    In this case, the first element of the multi-index is the point index from the input sample.
    The second element of the multi-index is:

    * the index or name of a model's output,
      if :arg:`order` is :attr:`~da.p7core.gtdf.GradMatrixOrder.F_MAJOR` (default)
    * the index or name of a model's input,
      if :arg:`order` is :attr:`~da.p7core.gtdf.GradMatrixOrder.X_MAJOR`

    When :arg:`point` is a ``pandas.Series``,
    its index becomes the row index of the returned ``pandas.DataFrame``.

    Using a low-fidelity blackbox in model gradient evaluations increases accuracy,
    but at the same time effectively limits the model domain to the blackbox domain:
    if the point to evaluate is outside the blackbox variable bounds
    (see :arg:`bounds` in :meth:`da.p7core.blackbox.Blackbox.add_variable()`),
    blackbox-based :meth:`~da.p7core.gtdf.Model.grad()` returns NaN values of gradients
    since it receives NaN responses from the blackbox.

    """
    self.__requireModelSection()

    original_bb = blackbox # store it to keep reference
    blackbox = self.__preprocess_blackbox(blackbox, False)
    numgrad_tol = float(blackbox.numerical_gradient_step) if blackbox is not None and not blackbox.gradients_enabled else _numpy.nan

    size_x = self.size_x
    input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")
    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')

    vectorsNumber = input.shape[0]
    if order == GradMatrixOrder.F_MAJOR:
      output = _numpy.ndarray((vectorsNumber, self.size_f, size_x), dtype=float, order='C')
      df_axis, dx_axis = 1, 2
    elif order == GradMatrixOrder.X_MAJOR:
      output = _numpy.ndarray((vectorsNumber, size_x, self.size_f), dtype=float, order='C')
      df_axis, dx_axis = 2, 1
    else:
      raise ValueError('Wrong "order" value!')
    succeeded, errdesc = 0, _ctypes.c_void_p()

    try:
      with _blackbox.blackbox_callback(blackbox, _blackbox._SINGLE_RESPONSE_CALLBACK_TYPE) as (callback, magic_sig):
        succeeded = self._backend.batch_calc_bb(self.__instance, callback, magic_sig, numgrad_tol,
                                                self._backend.BATCH_CALC_dFdX, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                                input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                                output.ctypes.data_as(self._backend.c_double_p), output.strides[0] // output.itemsize, \
                                                output.strides[df_axis] // output.itemsize, output.strides[dx_axis] // output.itemsize, \
                                                _ctypes.byref(errdesc))
    except:
      exc_type, exc_val, exc_tb = _sys.exc_info()
      model_error = _shared._release_error_message(errdesc)
      if model_error is not None and model_error[1]:
        exc_val = ("%s The origin of the exception is: %s" % (_shared._safestr(model_error[1]).strip(), _shared._safestr(exc_val).strip())) if exc_val else model_error[1]
      _shared.reraise(exc_type, exc_val, exc_tb)

    _shared._raise_on_error(succeeded, 'Gradient evaluation error', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      major_names = self._names_f if order == GradMatrixOrder.F_MAJOR else self._names_x
      minor_names = self._names_x if order == GradMatrixOrder.F_MAJOR else self._names_f
      return _shared.make_pandas_grad(output, single_vector, pandas_type, pandas_index, major_names, minor_names)
    else:
      return output[0] if single_vector else output

  def grad_bb(self, blackbox, point, order=GradMatrixOrder.F_MAJOR):
    """Evaluate :term:`model gradient`, requesting low fidelity data from the *blackbox*.

    .. deprecated:: 5.1
       use :meth:`~da.p7core.gtdf.Model.grad()` instead.

    This method is deprecated since the blackbox support was added
    to :meth:`~da.p7core.gtdf.Model.grad()`, and is kept for compatibility only.
    It is recommended to use :meth:`~da.p7core.gtdf.Model.grad()`
    with the :arg:`blackbox` argument to perform blackbox-based model gradient evaluation.

    """
    return self.grad(point, order=order, blackbox=blackbox)

  def calc_ae(self, point, blackbox=None):
    """Calculate the :term:`accuracy evaluation` estimate.

    :param point: the sample or point to evaluate
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :param blackbox: optional low fidelity blackbox
    :type blackbox: :class:`~da.p7core.blackbox.Blackbox`, :class:`.gtapprox.Model`, or :class:`.gtdf.Model`
    :return: estimates
    :rtype: ``pandas.DataFrame`` or ``pandas.Series`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 2D or 1D
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not provide :term:`accuracy evaluation`
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not support blackbox-based accuracy evaluation but *blackbox* is not ``None``

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* returns ``ndarray``.

    .. versionchanged:: 5.1
       blackbox support added.

    .. versionchanged:: 6.20
       :arg:`blackbox` may be a :class:`.gtapprox.Model` or a :class:`.gtdf.Model`.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Check :attr:`~da.p7core.gtdf.Model.has_ae` before using this method.
    It is available only if the model was trained with
    :ref:`GTDF/AccuracyEvaluation <GTDF/AccuracyEvaluation>` on.

    Performs accuracy evaluation for a data sample or a single point,
    optionally requesting low fidelity data from the :arg:`blackbox`
    (check :attr:`~da.p7core.gtdf.Model.has_ae_bb` before performing blackbox-based accuracy evaluation).
    In general form, :arg:`point` is a 2D array-like (a data sample).
    Several simplified argument forms are also supported, similar to :meth:`~da.p7core.gtdf.Model.calc()`.

    The returned array is 2D if :arg:`point` is a sample, and 1D if :arg:`point` is a single point.
    When :arg:`point` is a ``pandas.DataFrame`` or ``pandas.Series``,
    the returned array keeps indexing of the :arg:`point` array.

    Using a low-fidelity blackbox in accuracy evaluation improves its quality,
    but at the same time effectively limits the model domain to the blackbox domain:
    if the point to evaluate is outside the blackbox variable bounds
    (see :arg:`bounds` in :meth:`da.p7core.blackbox.Blackbox.add_variable()`),
    blackbox-based :meth:`~da.p7core.gtdf.Model.calc_ae()` returns NaN values of estimates
    since it receives NaN responses from the blackbox.

    """
    self.__requireModelSection()

    original_bb = blackbox # store it to keep reference
    blackbox = self.__preprocess_blackbox(blackbox, True)
    numgrad_tol = float(blackbox.numerical_gradient_step) if blackbox is not None and not blackbox.gradients_enabled else _numpy.nan

    input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")
    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')
    output = _numpy.ndarray((input.shape[0], self.size_f), dtype=float, order='C')
    succeeded, errdesc = 0, _ctypes.c_void_p()

    try:
      with _blackbox.blackbox_callback(blackbox, _blackbox._SINGLE_RESPONSE_CALLBACK_TYPE) as (callback, magic_sig):
        succeeded = self._backend.batch_calc_bb(self.__instance, callback, magic_sig, numgrad_tol, self._backend.BATCH_CALC_AE, \
                                                len(input), input.ctypes.data_as(self._backend.c_double_p),\
                                                input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                                output.ctypes.data_as(self._backend.c_double_p), \
                                                output.strides[0] // output.itemsize, output.strides[1] // output.itemsize, 1, \
                                                _ctypes.byref(errdesc))
    except:
      exc_type, exc_val, exc_tb = _sys.exc_info()
      model_error = _shared._release_error_message(errdesc)
      if model_error is not None and model_error[1]:
        exc_val = ("%s The origin of the exception is: %s" % (_shared._safestr(model_error[1]).strip(), _shared._safestr(exc_val).strip())) if exc_val else model_error[1]
      _shared.reraise(exc_type, exc_val, exc_tb)

    _shared._raise_on_error(succeeded, 'Model evaluation error', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      return _shared.make_pandas(output, single_vector, pandas_type, pandas_index, self._names_f)
    else:
      return output[0] if single_vector else output

  def grad_ae(self, point, order=GradMatrixOrder.F_MAJOR, blackbox=None):
    """Calculate gradients of the :term:`accuracy evaluation` function.

    :param point: the sample or point to evaluate
    :param order: gradient matrix order
    :param blackbox: optional low fidelity blackbox
    :type point: ``float`` or :term:`array-like`, 2D or 1D
    :type order: :class:`GradMatrixOrder`
    :type blackbox: :class:`~da.p7core.blackbox.Blackbox`, :class:`.gtapprox.Model`, or :class:`.gtdf.Model`
    :return: accuracy evaluation gradients
    :rtype: ``pandas.DataFrame`` if :arg:`point` is a pandas type; otherwise ``ndarray``, 3D or 2D
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not provide :term:`accuracy evaluation`

    .. versionadded:: 6.18

    .. versionchanged:: 6.20
       :arg:`blackbox` may be a :class:`.gtapprox.Model` or a :class:`.gtdf.Model`.

    .. versionchanged:: 6.25
       supports ``pandas.DataFrame`` and ``pandas.Series`` as 2D and 1D array-likes, respectively; returns a pandas data type if :arg:`point` is a pandas data type.

    Check :attr:`~da.p7core.gtdf.Model.has_ae` before using this method.
    It is available only if the model was trained with
    :ref:`GTDF/AccuracyEvaluation <GTDF/AccuracyEvaluation>` on.

    Evaluates gradients of the accuracy evaluation function for a data sample or a single point,
    optionally requesting low fidelity data from the :arg:`blackbox`
    (check :attr:`~da.p7core.gtdf.Model.has_ae_bb` before performing blackbox-based calculation of accuracy evaluation gradients).
    In general form, :arg:`point` is a 2D array (a data sample).
    Several simplified argument forms are also supported, similar to :meth:`~da.p7core.gtdf.Model.calc()`.

    The returned array is 3D if :arg:`point` is a sample, and 2D if :arg:`point` is a single point.

    When using pandas data samples (:arg:`point` is a ``pandas.DataFrame``),
    a 3D array in return value is represented by a ``pandas.DataFrame`` with multi-indexing (``pandas.MultiIndex``).
    In this case, the first element of the multi-index is the point index from the input sample.
    The second element of the multi-index is:

    * the index or name of a model's output,
      if :arg:`order` is :attr:`~da.p7core.gtdf.GradMatrixOrder.F_MAJOR` (default)
    * the index or name of a model's input,
      if :arg:`order` is :attr:`~da.p7core.gtdf.GradMatrixOrder.X_MAJOR`

    When :arg:`point` is a ``pandas.Series``,
    its index becomes the row index of the returned ``pandas.DataFrame``.

    """
    self.__requireModelSection()

    original_bb = blackbox # store it to keep reference
    blackbox = self.__preprocess_blackbox(blackbox, True)
    numgrad_tol = float(blackbox.numerical_gradient_step) if blackbox is not None and not blackbox.gradients_enabled else _numpy.nan

    size_x = self.size_x
    input, single_vector = _shared.as_matrix(point, shape=(None, self.size_x), ret_is_vector=True, order='A', name="'point' argument")
    if _shared.isNanInf(input):
      raise _ex.NanInfError('Input data contains NaN or Inf value')

    vectorsNumber = input.shape[0]
    if order == GradMatrixOrder.F_MAJOR:
      output = _numpy.ndarray((vectorsNumber, self.size_f, size_x), dtype=float, order='C')
      df_axis, dx_axis = 1, 2
    elif order == GradMatrixOrder.X_MAJOR:
      output = _numpy.ndarray((vectorsNumber, size_x, self.size_f), dtype=float, order='C')
      df_axis, dx_axis = 2, 1
    else:
      raise ValueError('Wrong "order" value!')
    succeeded, errdesc = 0, _ctypes.c_void_p()

    try:
      with _blackbox.blackbox_callback(blackbox, _blackbox._SINGLE_RESPONSE_CALLBACK_TYPE) as (callback, magic_sig):
        succeeded = self._backend.batch_calc_bb(self.__instance, callback, magic_sig, numgrad_tol,
                                                self._backend.BATCH_CALC_dAEdX, len(input), input.ctypes.data_as(self._backend.c_double_p), \
                                                input.strides[0] // input.itemsize, input.strides[1] // input.itemsize, \
                                                output.ctypes.data_as(self._backend.c_double_p), output.strides[0] // output.itemsize, \
                                                output.strides[df_axis] // output.itemsize, output.strides[dx_axis] // output.itemsize, \
                                                _ctypes.byref(errdesc))
    except:
      exc_type, exc_val, exc_tb = _sys.exc_info()
      model_error = _shared._release_error_message(errdesc)
      if model_error is not None and model_error[1]:
        exc_val = ("%s The origin of the exception is: %s" % (_shared._safestr(model_error[1]).strip(), _shared._safestr(exc_val).strip())) if exc_val else model_error[1]
      _shared.reraise(exc_type, exc_val, exc_tb)

    _shared._raise_on_error(succeeded, 'Failed to calculate gradient of the accuracy evaluation.', errdesc)

    pandas_index, pandas_type = _shared.get_pandas_info(point, single_vector, self._names_x)
    if pandas_index is not None:
      major_names = self._names_f if order == GradMatrixOrder.F_MAJOR else self._names_x
      minor_names = self._names_x if order == GradMatrixOrder.F_MAJOR else self._names_f
      return _shared.make_pandas_grad(output, single_vector, pandas_type, pandas_index, major_names, minor_names)
    else:
      return output[0] if single_vector else output

  def calc_ae_bb(self, blackbox, point):
    """Calculate the :term:`accuracy evaluation` estimate, requesting low fidelity data from the *blackbox*.

    .. deprecated:: 5.1
       use :meth:`~da.p7core.gtdf.Model.calc_ae()` instead.

    This method is deprecated since the blackbox support was added
    to :meth:`~da.p7core.gtdf.Model.calc_ae()`, and is kept for compatibility only.
    It is recommended to use :meth:`~da.p7core.gtdf.Model.calc_ae()`
    with the *blackbox* argument to perform blackbox-based accuracy evaluation.

    """
    return self.calc_ae(point, blackbox=blackbox)

  def validate(self, pointsX, pointsY, blackbox=None, weights=None):
    """Validate the model using a reference inputs-responses array.

    :param pointsX: reference inputs
    :type pointsX: ``float`` or :term:`array-like`, 1D or 2D
    :param pointsY: reference responses
    :type pointsY: ``float`` or :term:`array-like`, 1D or 2D
    :param blackbox: optional low fidelity blackbox
    :type blackbox: :class:`~da.p7core.blackbox.Blackbox`
    :param weights: optional weights of the reference points
    :type weights: :term:`array-like`, 1D
    :return: accuracy data
    :rtype: ``dict``
    :raise: :exc:`~da.p7core.FeatureNotAvailableError` if the model does not support blackbox-based calculations but :arg:`blackbox` is not ``None``

    .. versionchanged:: 5.1
       blackbox support added.

    .. versionchanged:: 6.17
       added the :arg:`weights` argument.

    Validates the model against the reference array,  evaluating model
    responses to :arg:`pointsX` and comparing them to :arg:`pointsY`.
    Optionally can request low fidelity data from the :arg:`blackbox`
    (check :attr:`~da.p7core.gtdf.Model.has_bb` before running
    blackbox-based validation).

    Generally, :arg:`pointsX` and :arg:`pointsY` should be 2D arrays.
    Several simplified argument forms are also supported,
    similar to :meth:`~da.p7core.gtdf.Model.calc()`.

    Returns a dictionary containing lists of error values calculated
    componentwise, with names of errors as keys. The returned dictionary
    has the same structure as the ``details["Training Dataset"]["Accuracy"]["Componentwise"]``
    dictionary in GTApprox model details ---
    see section :ref:`ug_gtapprox_details_model_information_training_dataset_info_accuracy`
    in :ref:`ug_gtapprox_details_model_information` for a full description.

    Using a blackbox in validation increases accuracy, but at the same
    time effectively limits the model domain to the blackbox domain. Due
    to this, points in the reference array have to satisfy the blackbox
    variable bounds (see :arg:`bounds` in :meth:`da.p7core.blackbox.Blackbox.add_variable()`).
    Otherwise :meth:`validate()` returns NaN error values since it
    receives NaN responses from the blackbox.

    """
    self.__requireModelSection()

    original_bb = blackbox # store it to keep reference
    blackbox = self.__preprocess_blackbox(blackbox, False)
    numgrad_tol = float(blackbox.numerical_gradient_step) if blackbox is not None and not blackbox.gradients_enabled else _numpy.nan

    # read errors list first
    errdesc = _ctypes.c_void_p()
    errorsListSize = _ctypes.c_size_t()
    self.__checkCall(self._backend.validation_errors_list(self.__instance, _ctypes.c_char_p(), _ctypes.byref(errorsListSize), _ctypes.byref(errdesc)), errdesc)
    errorsList = (_ctypes.c_char * errorsListSize.value)()
    self.__checkCall(self._backend.validation_errors_list(self.__instance, errorsList, _ctypes.byref(errorsListSize), _ctypes.byref(errdesc)), errdesc)
    errorsList = _shared.parse_json_deep(_shared._preprocess_json(errorsList.value), list)

    # perform validation
    size_x = self.size_x
    size_f = self.size_f
    pointsX = _shared.as_matrix(pointsX, shape=(None, size_x), name="Reference inputs ('pointsX' argument)")
    pointsY = _shared.as_matrix(pointsY, shape=(None, size_f), name="Reference responses ('pointsY' argument)")
    if not (len(pointsX) == len(pointsY)):
      raise ValueError('Sizes of reference samples do not match!')
    sample_size = len(pointsX)
    if sample_size == 0:
      raise ValueError('Reference set is empty!')
    if _shared.isNanInf(pointsX) or _shared.isNanInf(pointsY):
      raise _ex.NanInfError('Reference data contains NaN or Inf value')

    cpointsW = _shared.py_vector_2c(weights, sample_size, name="'weights' argument") if weights is not None and sample_size > 1 \
          else _shared.ArrayPtr(self._backend.c_double_p(), 0)

    ince = len(errorsList)
    result = (_ctypes.c_double * (size_f * ince))()

    cpointsY = _shared.py_matrix_2c(pointsY, size_f)
    cpointsX = _shared.py_matrix_2c(pointsX, size_x)

    succeeded = 0

    try:
      with _blackbox.blackbox_callback(blackbox, _blackbox._SINGLE_RESPONSE_CALLBACK_TYPE) as (callback, magic_sig):
        succeeded = self._backend.validate_bb(self.__instance, callback, magic_sig, numgrad_tol, sample_size, \
                                              cpointsX.ptr, cpointsX.ld, cpointsY.ptr, cpointsY.ld, cpointsW.ptr, cpointsW.inc, \
                                              result, ince, _ctypes.byref(errdesc))
    except:
      exc_type, exc_val, exc_tb = _sys.exc_info()
      model_error = _shared._release_error_message(errdesc)
      if model_error is not None and model_error[1]:
        exc_val = ("%s The origin of the exception is: %s" % (_shared._safestr(model_error[1]).strip(), _shared._safestr(exc_val).strip())) if exc_val else model_error[1]
      _shared.reraise(exc_type, exc_val, exc_tb)

    _shared._raise_on_error(succeeded, 'Model validation error', errdesc)

    return dict((err_name, list(result[:])[err_index::ince]) for err_index, err_name in enumerate(errorsList))

  def validate_bb(self, blackbox, pointsX, pointsY):
    """Validate the model using a reference inputs-responses array and requesting low fidelity data from the *blackbox*.

    .. deprecated:: 5.1
       use :meth:`~da.p7core.gtdf.Model.validate()` instead.

    This method is deprecated since the blackbox support was added
    to :meth:`~da.p7core.gtdf.Model.validate()`, and is kept for compatibility only.
    It is recommended to use :meth:`~da.p7core.gtdf.Model.validate()`
    with the *blackbox* argument to perform blackbox-based model validation.

    """
    return self.validate(pointsX, pointsY, blackbox=blackbox)

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
    (see :ref:`ug_gtdf_model_structure` for details).
    The *sections* argument can be a string or a list of strings specifying which sections to save:

    * ``"all"``: all sections (default).
    * ``"model"``: main model section, required for model evaluation. This section is always saved even if not specified.
    * ``"info"``: model information, :attr:`~da.p7core.gtdf.Model.info`.
    * ``"comment"``: comment section, :attr:`~da.p7core.gtdf.Model.comment`.
    * ``"annotations"``: annotations section, :attr:`~da.p7core.gtdf.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, :attr:`~da.p7core.gtdf.Model.training_sample`.
    * ``"iv_info"``: internal validation data, :attr:`~da.p7core.gtdf.Model.iv_info`.
    * ``"build_log"``: model training log, :attr:`~da.p7core.gtdf.Model.build_log`.

    Note that the main model section is always saved, so
    ``sections="model"`` and ``sections=[]`` are equivalent.

    """
    self.__requireModelSection()

    sections_code = self.__sections_code(sections) | self.__MODEL_SECTIONS['model'] # always save model section

    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.save(self.__instance, _ctypes.c_void_p(), _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)
    data = _ctypes.create_string_buffer(size.value)
    self.__checkCall(self._backend.save(self.__instance, data, _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)

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
    (see :ref:`ug_gtdf_model_structure` for details).
    The *sections* argument can be a string or a list of strings specifying which sections to include:

    * ``"all"``: all sections (default).
    * ``"model"``: main model section, required for model evaluation. This section is always included even if not specified.
    * ``"info"``: model information, :attr:`~da.p7core.gtdf.Model.info`.
    * ``"comment"``: comment section, :attr:`~da.p7core.gtdf.Model.comment`.
    * ``"annotations"``: annotations section, :attr:`~da.p7core.gtdf.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, :attr:`~da.p7core.gtdf.Model.training_sample`.
    * ``"iv_info"``: internal validation data, :attr:`~da.p7core.gtdf.Model.iv_info`.
    * ``"build_log"``: model training log, :attr:`~da.p7core.gtdf.Model.build_log`.

    Note that the main model section is always included, so
    ``sections="model"`` and ``sections=[]`` are equivalent.

    """
    self.__requireModelSection()

    sections_code = self.__sections_code(sections) | self.__MODEL_SECTIONS['model'] # always save model section

    errdesc = _ctypes.c_void_p()
    size = _ctypes.c_size_t()
    self.__checkCall(self._backend.save(self.__instance, _ctypes.c_void_p(), _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)
    data = _ctypes.create_string_buffer(size.value)
    self.__checkCall(self._backend.save(self.__instance, data, _ctypes.byref(size), sections_code, _ctypes.byref(errdesc)), errdesc)
    return _base64.b64encode(data.raw)

  def modify(self, comment=None, annotations=None, x_meta=None, f_meta=None):
    """Create a copy of the model with modified metainformation.

    :param comment: new comment
    :param annotations: new annotations
    :param x_meta: descriptions of inputs
    :param f_meta: descriptions of outputs
    :type comment: ``str``
    :type annotations: ``dict``
    :type x_meta: ``list``
    :type f_meta: ``list``
    :return: copy of this model with modifications
    :rtype: :class:`~da.p7core.gtdf.Model`

    .. versionadded:: 6.6

    .. versionchanged:: 6.14
       can edit descriptions of inputs and outputs.

    This method is intended to edit model
    :attr:`~da.p7core.gtdf.Model.annotations`,
    :attr:`~da.p7core.gtdf.Model.comment`, and
    input and output descriptions found in :attr:`~da.p7core.gtdf.Model.details`.
    Parameters are similar to :meth:`~da.p7core.gtdf.Builder.build()` --- see the full description there.
    If a parameter is ``None``, corresponding information in the modified model remains unchanged.
    If you specify a parameter, corresponding information in the modified model is fully replaced.

    Note that :meth:`~da.p7core.gtdf.Model.modify()`
    returns a new modified model, which is identical to the original
    except your edits to the model metainformation.

    """
    metainfo = self.__metainfo()
    new_metainfo = _shared.preprocess_metainfo(x_meta, f_meta, self.size_x, self.size_f, ignorable_keys=_shared.collect_metainfo_keys(metainfo))

    if x_meta is not None:
      metainfo.update({'Input Variables': new_metainfo['Input Variables']})
    if f_meta is not None:
      metainfo.update({'Output Variables':  new_metainfo['Output Variables']})

    return self.__modify(comment=comment, annotations=annotations, metainfo=metainfo)

  def __modify(self, comment=None, annotations=None, metainfo=None):
    """
    Create a copy of the model with modified additional information.
    """
    if comment is None and annotations is None and metainfo is None:
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

    # Modify model
    errdesc = _ctypes.c_void_p()
    handle = self._backend.modify(self.__instance, comment_ptr, annotations_ptr, metainfo_ptr, _ctypes.byref(errdesc))
    if not handle:
      _shared.ModelStatus.checkErrorCode(0, 'Failed to modify model.', errdesc)
    return Model(handle=handle)

  @staticmethod
  def available_sections(**kwargs):
    """Get a list of available model sections.

    :keyword file: file object or path to load model from
    :keyword string: serialized model
    :keyword model: model object
    :type file: ``file`` or ``str``
    :type string: ``str``
    :type model: :class:`~da.p7core.gtdf.Model`
    :return: available model sections
    :rtype: ``list``

    .. versionadded:: 6.11

    Returns a list of strings specifying which sections can be loaded from the model:

    * ``"model"``: main model section, required for model evaluation.
    * ``"info"``: model information, required for :attr:`~da.p7core.gtdf.Model.info`.
    * ``"comment"``: comment section, required for :attr:`~da.p7core.gtdf.Model.comment`.
    * ``"annotations"``: annotations section, required for :attr:`~da.p7core.gtdf.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, required for :attr:`~da.p7core.gtdf.Model.training_sample`.
    * ``"iv_info"``: internal validation data, required for :attr:`~da.p7core.gtdf.Model.iv_info`.
    * ``"build_log"``: model training log, required for :attr:`~da.p7core.gtdf.Model.build_log`.

    See :ref:`ug_gtdf_model_structure` for details.

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
      errcode = Model._default_backend().enum_load_sections(binary_data, len(binary_data), 0, _ctypes.byref(sec_flags), _ctypes.byref(errdesc))
    elif model is not None:
      errcode = Model._default_backend().enum_save_sections(model.__instance, _ctypes.byref(sec_flags), _ctypes.byref(errdesc))
    else:
      raise ValueError("Failed to interpret input arguments.")

    _shared.ModelStatus.checkErrorCode(errcode, 'Failed to read available model sections list.', errdesc)

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
    Note that availability of :class:`~da.p7core.gtdf.Model` methods and attributes depends on which sections are loaded.
    This dependency is described in more detail in section :ref:`ug_gtdf_model_structure`.

    The :arg:`sections` argument can be a string or a list of strings specifying which sections to load:

    * ``"all"``: all sections (default).
    * ``"none"``: minimum model information, does not load any other section (the minimum load).
    * ``"model"``: main model section, required for model evaluation and smoothing methods.
    * ``"info"``: model information, required for :attr:`~da.p7core.gtdf.Model.info`.
    * ``"comment"``: comment section, required for :attr:`~da.p7core.gtdf.Model.comment`.
    * ``"annotations"``: annotations section, required for :attr:`~da.p7core.gtdf.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, required for :attr:`~da.p7core.gtdf.Model.training_sample`.
    * ``"iv_info"``: internal validation data, required for :attr:`~da.p7core.gtdf.Model.iv_info`.
    * ``"build_log"``: model training log, required for :attr:`~da.p7core.gtdf.Model.build_log`.

    To get a list of sections available for load, use :meth:`~da.p7core.gtdf.Model.available_sections()`.
    """
    try:
      data = file.read(-1)
    except AttributeError:
      data = None

    if data is None:
      with open(file, 'rb') as f:
        data = f.read(-1)

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
    Note that availability of :class:`~da.p7core.gtdf.Model` methods and attributes depends on which sections are loaded.
    This dependency is described in more detail in section :ref:`ug_gtdf_model_structure`.

    The :arg:`sections` argument can be a string or a list of strings specifying which sections to load:

    * ``"all"``: all sections (default).
    * ``"none"``: minimum model information, does not load any other section (the minimum load).
    * ``"model"``: main model section, required for model evaluation and smoothing methods.
    * ``"info"``: model information, required for :attr:`~da.p7core.gtdf.Model.info`.
    * ``"comment"``: comment section, required for :attr:`~da.p7core.gtdf.Model.comment`.
    * ``"annotations"``: annotations section, required for :attr:`~da.p7core.gtdf.Model.annotations`.
    * ``"training_sample"``: a copy of training sample data, required for :attr:`~da.p7core.gtdf.Model.training_sample`.
    * ``"iv_info"``: internal validation data, required for :attr:`~da.p7core.gtdf.Model.iv_info`.
    * ``"build_log"``: model training log, required for :attr:`~da.p7core.gtdf.Model.build_log`.

    To get a list of sections available for load, use :meth:`~da.p7core.gtdf.Model.available_sections()`.
    """
    binary_data = _shared.wrap_with_exc_handler(_base64.b64decode, _ex.GTException)(modelString)
    self.__reload_model(binary_data, sections)

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

  def __del__(self):
    """Destructor."""
    self._backend.delete_model(self.__instance, self._backend.c_void_p_p())


  @staticmethod
  def __str_var_info(data):
    vars_stat = dict((k, 0) for k in set(str(v["variability"]) for v in data))
    for v in data:
      vars_stat[v["variability"]] += 1
    return ", ".join("%d %s" % (vars_stat[k], k) for k in vars_stat)

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
    if self.has_bb:
      feature_list.append("blackbox (AE)" if self.has_ae_bb else "blackbox")
    if self.has_ae:
      feature_list.append("AE")

    info_list = []
    if self.iv_info:
      info_list.append("iv_info")
    if self.training_sample:
      info_list.append("training_sample (%d)" % len(self.training_sample))
    if self.annotations:
      info_list.append("annotations")

    info.write("Input Size:    %s (%s)\n" % (self.size_x, self.__str_var_info(self.details["Input Variables"])))
    info.write("Output Size:   %s (%s)\n" % (self.size_f, self.__str_var_info(self.details["Output Variables"])))
    info.write("Technique:     %s\n" % self.details.get("Technique", "<not set>"))
    info.write("Features:      %s\n" % (", ".join(feature_list) if feature_list else "-"))
    info.write("Attachments:   %s\n" % (", ".join(info_list) if info_list else "-"))
    info.write("Training Time: %s\n" % self.details.get("Training Time", {}).get("Total", "-"))
    self.__str_dict(self.details, "Training Options", info)

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
    self.__cache = {}

  @staticmethod
  def _default_backend(backend=_api):
    # intentionally assign single shared _api object as default value so we keep backend loaded as long as this method exists
    return _api if backend is None else backend

  def __requireModelSection(self):
    if not self.__hasFeature(self._backend.GT_DF_MODEL_FEATURE_CALC_LOADED):
      raise _ex.FeatureNotAvailableError('The required "model" section has not been loaded.')

  def __hasFeature(self, feature_id):
    errdesc = _ctypes.c_void_p()
    result = _ctypes.c_short()
    err = self._backend.has_feature(self.__instance, _ctypes.c_int(feature_id), _ctypes.byref(result), _ctypes.byref(errdesc))
    if not err:
      _shared.ModelStatus.checkErrorCode(err, 'Failed to get model feature state!', errdesc)
    return result.value != 0

  def __checkCall(self, err, errdesc):
    _shared.ModelStatus.checkErrorCode(err, 'C call failed!', errdesc)

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
      self._backend.delete_model(self.__instance, _ctypes.c_void_p())
      self.__instance = None
      self.__cache = {}

    loader = _ctypes.c_void_p(self._backend.create_loader())
    if not loader:
      raise _ex.GTException('Failed to initialize model loader!')

    try:
      sections_code = self.__sections_code(sections)
      self.__instance = _ctypes.c_void_p(self._backend.selective_loader(loader, binary_data, len(binary_data), sections_code))
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

  def __preprocess_blackbox(self, blackbox, mode_ae):
    if blackbox is None:
      return None

    if not (self.has_ae_bb if mode_ae else self.has_bb):
      raise _ex.FeatureNotAvailableError('Blackbox-based %sevaluations is not available for this model.' % ("accuracy " if mode_ae else ""))

    blackbox, _, warns, _ = _bbconverter.preprocess_blackbox(blackbox, "GTDF Model", None)
    if warns:
      _warn(_shared._safestr(warns), RuntimeWarning)

    return blackbox

# ModelWithBlackbox is deprecated and aliased to Model
ModelWithBlackbox = Model
