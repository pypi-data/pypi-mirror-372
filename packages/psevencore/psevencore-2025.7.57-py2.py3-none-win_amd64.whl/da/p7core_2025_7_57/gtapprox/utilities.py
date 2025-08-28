#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Utilities for usage Approximation.

.. currentmodule:: da.p7core.gtapprox.utilities

"""

from __future__ import with_statement
from __future__ import division

import sys
import ctypes
import uuid
import warnings as _warn
import zipfile as _zipfile
from os import path
import datetime as _datetime
import numpy as np

from .. import six as _six
from ..six.moves import xrange, range
from .. import shared as _shared
from .. import options as _options
from .. import exceptions as _ex
from .. import loggers as _loggers
from .. import archives as _archives

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_size_ptr = ctypes.POINTER(ctypes.c_size_t)
    self.c_double_ptr = ctypes.POINTER(ctypes.c_double)
    self.c_error_ptr = ctypes.POINTER(ctypes.c_void_p)

    self.check_tensor_structure = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_size_t, ctypes.c_size_t, self.c_double_ptr, ctypes.c_size_t,
                                                    ctypes.c_void_p)(('GTApproxUtilitiesFullCheckTensorStructure', _shared._library))

    # composer API
    self.composer_log = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_char_p)
    self.composer_create_cat = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, self.c_size_ptr, ctypes.c_void_p)(("GTApproxCreateCategoricalModelComposer", _shared._library))
    self.composer_create_cw = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_short)(("GTApproxCreateComponentwiseModelComposer", _shared._library))
    self.composer_free = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p)(("GTApproxFreeModelComposer", _shared._library))
    self.composer_lasterr = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p, self.c_size_ptr)(("GTApproxComposerGetLastError", _shared._library))
    self.composer_training_sample = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int), self.c_double_ptr, ctypes.POINTER(ctypes.c_int))(("GTApproxComposerTrainingSample", _shared._library))
    self.composer_set_comment = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p)(("GTApproxComposerComment", _shared._library))
    self.composer_set_options = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p)(("GTApproxComposerOptions", _shared._library))
    self.composer_append = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_void_p)(("GTApproxComposerAppendModel", _shared._library))
    self.composer_evaluation_model = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p,
                                                      ctypes.c_size_t, ctypes.c_size_t, self.c_size_ptr, ctypes.c_size_t,
                                                      self.c_double_ptr, ctypes.c_size_t, ctypes.c_size_t
                                                      )(("GTApproxComposerSetEvaluationModel", _shared._library))
    self.composer_constraints = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_size_t, # retcode, composer, n_z
                                                  self.c_double_ptr, ctypes.c_size_t, ctypes.c_size_t, # z_clip
                                                  ctypes.c_size_t, self.c_double_ptr, ctypes.c_size_t, # n_c, std_c
                                                  self.c_double_ptr, ctypes.c_size_t, ctypes.c_size_t, # left side
                                                  self.c_double_ptr, ctypes.c_size_t, # right side
                                                  self.c_double_ptr, ctypes.c_size_t, ctypes.c_size_t # update
                                                  )(("GTApproxComposerSetConstraints", _shared._library))
    self.composer_flush = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)(("GTApproxComposerFlush", _shared._library))

    # calculate errors API
    self.read_errors_list = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_char_p, self.c_size_ptr, self.c_size_ptr,
                                             self.c_error_ptr)(("GTApproxErrorStatisticsList", _shared._library))
    self.calc_statistics = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_size_t, ctypes.c_size_t,
                                            self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr,
                                            self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr,
                                            self.c_error_ptr)(('GTApproxCalculateWeightedErrorStatistics', _shared._library))

    # FMI API
    self.callback_single_file = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_char_p, ctypes.c_char_p); # ret.code, archive file name, file data

    self.fmi_update_metainfo = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p,
                                                ctypes.c_size_t, self.c_error_ptr)(("GTApproxModelExportFMIInfo", _shared._library))
    self.fmi_do_export_cs = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, # ret. code, model, metainfo, base archive file name
                                             ctypes.c_void_p, ctypes.c_size_t, self.c_error_ptr)(("GTApproxModelExportFMICSCode", _shared._library)) # file write callback (self.callback_single_file), single file size limit, err. data
    self.fmi_do_export_me = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, # ret. code, model, metainfo, base archive file name
                                             ctypes.c_void_p, ctypes.c_size_t, self.c_error_ptr)(("GTApproxModelExportFMIMECode", _shared._library)) # file write callback (self.callback_single_file), single file size limit, err. data
    self.fmi_do_export_fmu20 = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p, # ret. code, model, metainfo, base archive file name
                                                ctypes.c_void_p, ctypes.c_size_t, self.c_error_ptr)(("GTApproxModelExportFMI20Code", _shared._library)) # file write callback (self.callback_single_file), single file size limit, err. data

    self.kdtree_create = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, self.c_double_ptr, # ret. pointer, n points, point dim, pointer to points
                                          self.c_size_ptr, self.c_error_ptr)(("GTApproxKDTreeCreate", _shared._library)) # pointer to strides, error data

    self.kdtree_delete = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, self.c_error_ptr)(("GTApproxKDTreeDelete", _shared._library)) # ret code, pointer to kd-tree, error data

    self.kdtree_neighborhood = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, self.c_double_ptr, ctypes.c_size_t, # ret. code, pointer to kd-tree, pointer to test point, test point step,
                                                ctypes.c_double, ctypes.c_double, ctypes.c_char_p, ctypes.c_size_t, # min. search radius (l2-norm), max. search radius (l2-norm), pointer to mask, mask step
                                                self.c_error_ptr)(("GTApproxKDTreeNeighborhood", _shared._library)) # error data

    self.kdtree_equal_points = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p, self.c_double_ptr, ctypes.c_size_t, # ret. code, pointer to kd-tree, pointer to test point, test point step,
                                                ctypes.c_double, ctypes.c_char_p, ctypes.c_size_t, # max relative radius of equality (inf-norm), pointer to mask, mask step
                                                self.c_error_ptr)(("GTApproxKDTreeEqualPoints", _shared._library)) # error data

    self.kdtree_minimax = ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p, ctypes.c_double, self.c_error_ptr)(("GTApproxKDTreeMinimaxDistance", _shared._library)) # distance, pointer to kd-tree, minimal distinguishable distance, error data

    self.build_distance_table = ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_size_t, ctypes.c_size_t, # ret. code, m, n,
                                                 self.c_double_ptr, self.c_size_ptr, # x data, x strides,
                                                 self.c_double_ptr, self.c_size_ptr, # dist. data, dist. strides
                                                 ctypes.c_short, self.c_error_ptr)(("GTApproxUtilitiesFillDistanceTable", _shared._library)) # precision (digits), err. data

  def composer_raise_lasterr(self, composer, message):
    err_size = ctypes.c_size_t()
    if self.composer_lasterr(composer, ctypes.c_char_p(), ctypes.byref(err_size)):
      err_msg = (ctypes.c_char * err_size.value)()
      if self.composer_lasterr(composer, err_msg, ctypes.byref(err_size)):
        message = ': '.join((message, _shared._preprocess_utf8(err_msg.value)))
    raise _ex.GTException(message)

  def composer_set_sample(self, composer, sample_code, sample, data_name, vec_size, raise_if_absent):
    data = sample.get(data_name)
    if data is None:
      if raise_if_absent:
        raise _ex.GTException('The required "%s" sample is absent' % data_name)
      else:
        return None

    data = _shared.as_matrix(data, shape=(None, vec_size), order='A', name=("'%s' sample" % data_name))

    shape = (ctypes.c_int * data.ndim)()
    shape[:] = data.shape[:]

    strides = (ctypes.c_int * data.ndim)()
    strides[:] = [_ // data.itemsize for _ in data.strides]

    data_ptr = (ctypes.c_double * (strides[0] * shape[0])).from_address(data.ctypes.data)

    if not self.composer_training_sample(composer, sample_code, data.ndim, shape, data_ptr, strides):
      self.composer_raise_lasterr(composer, 'Failed to setup "%s" sample' % data_name)

    return data

_api = _API() # All backend functions must be preloaded for Python 2.5 compatibility. You'd better do not know WHY.

def _distances_table(x, precision=None):
  x = _shared.as_matrix(x)
  d = np.empty((x.shape[0], x.shape[0]))
  err_desc = ctypes.c_void_p()

  precision = int(precision) if precision else 0

  _shared._raise_on_error(_api.build_distance_table(x.shape[0], x.shape[1],
                            x.ctypes.data_as(_api.c_double_ptr), ctypes.cast(x.ctypes.strides, _api.c_size_ptr),
                            d.ctypes.data_as(_api.c_double_ptr), ctypes.cast(d.ctypes.strides, _api.c_size_ptr),
                            precision, ctypes.byref(err_desc)),
                          "Failed to build distances table.", err_desc)

  return d

_PERMANENT_OPTIONS = ('/GTApprox/DryRun', '/TA/TensorDecompositionTimeout')
_PERMANENT_OPTIONS_TA = _PERMANENT_OPTIONS + ('GTApprox/Technique', 'GTApprox/MoATechnique')

def _parse_dry_run(options):
  value = options._get("/GTApprox/DryRun")
  if value == "False":
    return False
  elif value == "Quick":
    return "quick"
  elif value == "True":
    return True
  return _shared.parse_bool(value)

class _KDTree(object):
  def __init__(self, data):
    data = _shared.as_matrix(data)
    err_desc = ctypes.c_void_p()
    self._shape = data.shape
    self._tree = _api.kdtree_create(data.shape[0], data.shape[1], data.ctypes.data_as(_api.c_double_ptr),
                                    ctypes.cast(data.ctypes.strides, _api.c_size_ptr), ctypes.byref(err_desc))
    _shared._raise_on_error(self._tree, "Failed to create K-D tree", err_desc)

  def __del__(self):
    self.reset()

  def reset(self):
    err_desc = ctypes.c_void_p()
    tree_pointer, self._tree = self._tree, None
    if not _api.kdtree_delete(tree_pointer, ctypes.byref(err_desc)):
      _shared._raise_on_error(0, "Failed to destroy K-D tree", err_desc)

  def search(self, point, min_distance, max_distance):
    point = _shared.as_matrix(point, shape=(1, self._shape[1]), name="test point")
    mask = np.zeros((self._shape[0]), dtype=bool)
    err_desc = ctypes.c_void_p()

    if not _api.kdtree_neighborhood(self._tree, point.ctypes.data_as(_api.c_double_ptr),
                                    point.strides[-1] // point.itemsize, min_distance, max_distance,
                                    ctypes.c_char_p(mask.ctypes.data), mask.strides[0], ctypes.byref(err_desc)):
      _shared._raise_on_error(0, "K-D tree search failed", err_desc)

    return mask

  def equal_points(self, point, max_rel_radius):
    point = _shared.as_matrix(point, shape=(1, self._shape[1]), name="test point")
    mask = np.zeros((self._shape[0]), dtype=bool)
    err_desc = ctypes.c_void_p()

    if not _api.kdtree_equal_points(self._tree, point.ctypes.data_as(_api.c_double_ptr), point.strides[-1] // point.itemsize,
                                    max_rel_radius, ctypes.c_char_p(mask.ctypes.data), mask.strides[0], ctypes.byref(err_desc)):
      _shared._raise_on_error(0, "K-D tree search failed", err_desc)

    return mask

  def minimax_distance(self, min_distance):
    err_desc = ctypes.c_void_p()
    dist = _api.kdtree_minimax(self._tree, min_distance, ctypes.byref(err_desc))
    _shared._raise_on_error(np.isfinite(dist), "K-D tree search failed", err_desc)
    return dist

class _ZipArchiveWriterEx(_archives._BasicArchveWriter):
  def __init__(self, file_obj):
    super(_ZipArchiveWriterEx, self).__init__(file_obj)
    self.files = []

  def __call__(self, archname, bytes):
    try:
      archname = _shared._preprocess_utf8(archname)
      self.file_obj.writestr(archname, bytes, _zipfile.ZIP_DEFLATED)
      self.files.append((archname, _shared._preprocess_utf8(bytes)))
      return True
    except:
      self.process_exception()
    return False


class Utilities(object):
  """Utility functions.

  """
  class _LogWrapper(object):
    def __init__(self, logger, prefix=None):
      self.__logger = logger
      self.__prefix = _shared.make_prefix(prefix)

    def __call__(self, level, message):
      try:
        if self.__logger is not None:
          level = _loggers.LogLevel.from_string(_shared._preprocess_utf8(level))
          message = _shared._preprocess_utf8(message)
          for s in message.splitlines():
            self.__logger(level, (self.__prefix + s))
      except:
        pass
      return False

  @staticmethod
  def checkTensorStructure(trainPoints, userDefinedFactors=tuple()):
    """Check if the source data has proper structure so the Tensor Approximation technique may be used.

    :param trainPoints: training sample (variables only)
    :param userDefinedFactors: optional user-defined tensor factors, as in :ref:`GTApprox/TensorFactors<GTApprox/TensorFactors>`
    :type trainPoints: :term:`array-like`
    :type userDefinedFactors: :term:`array-like`
    :return: check result and (if no user-defined factors are given) calculated tensor factors, as a tuple
    :rtype: ``tuple(bool, list[list])``

    The Tensor Approximation technique requires specific design of an experiment type to be used (the so-called gridded data).
    This function may be used to check if sample data structure allows TA usage. User shall supply the training sample and,
    optionally, a list of proposed tensor factors. Return value is a tuple of Boolean check result (``True`` means sample is
    TA-compatible) and a list of tensor factors which are either user-defined or calculated automatically if **userDefinedFactors**
    is an empty list.

    """
    c_sample = _shared.py_matrix_2c(trainPoints, name="Training sample ('trainPoints' argument)")

    options_manager = _options._OptionManager('GTApprox/')
    options_impl = _options.Options(options_manager.pointer, None)
    if userDefinedFactors:
      options_impl.set("GTApprox/TensorFactors", userDefinedFactors)

    code = _api.check_tensor_structure(c_sample.array.shape[0], c_sample.array.shape[1], c_sample.ptr, c_sample.ld, options_manager.pointer)
    return (code in (2, 4)), (userDefinedFactors or _shared.parse_json(options_impl.get('//Service/CartesianStructure')))

  @staticmethod
  def join_categorical_models(models, catvars, sample, comment, initial_options, logger):
    """
    Creates model based on the models for different discrete categorical classes

    :param models: list of a simple models to join
    :type models: iterable returning :class:`~da.p7core.gtapprox.Model` instances
    :param catvars: list of categorical variables indices
    :type catvars: ``list`` or any iterable of integers
    :param sample: dictionary describing training sample
    :type sample: ``dict``
    :param comment: user-defined commentary string for the model created
    :type comment: ``str``
    :param initial_options: dictionary describing initial options set by user
    :type initial_options: ``dict``

    The *sample* argument is a dictionary with the following keys:

    * ``"x"`` --- the input part of the training sample (values of variables).
    * ``"f"`` --- the response part of the training sample (function values).
    * ``"tol"`` --- response noise variance.
      Optional: the key may be omitted, or its value may be an explicit ``None``.
      Incompatible with sample point weights.
    * ``"weights"`` --- sample point weights.
      Optional: may be omitted or set to ``None``.
      Incompatible with response noise variance.

    """
    models = [_ for _ in models]
    if not models:
      raise _ex.GTException('Failed to compose model: no submodels are given.')

    catvars_c = (ctypes.c_size_t * len(catvars))()
    catvars_c[:] = catvars[:]

    wrapped_logger0 = Utilities._LogWrapper(logger, comment)
    wrapped_logger1 = _api.composer_log(wrapped_logger0)
    composer = _api.composer_create_cat(models[0].size_x, len(catvars_c), catvars_c, wrapped_logger1)
    if not composer:
      raise _ex.GTException('Failed to create model composer')

    try:
      # additional variables are needed because composer_set_sample could replace original data
      data_x = _api.composer_set_sample(composer, 0, sample, 'x', models[0].size_x, True)
      data_f = _api.composer_set_sample(composer, 1, sample, 'f', models[0].size_f, True)
      data_w = _api.composer_set_sample(composer, 2, sample, 'weights', 1, False)
      data_tol = _api.composer_set_sample(composer, 3, sample, 'tol', models[0].size_f, False)

      _api.composer_set_comment(composer, Utilities._encode_comment(comment))
      _api.composer_set_options(composer, _shared.write_json(dict(initial_options)).encode('ascii'))

      for index, model in enumerate(models):
        if not _api.composer_append(composer, model._Model__instance):
          _api.composer_raise_lasterr(composer, 'Failed to append model #%d' % index)

      instance = _api.composer_flush(composer)
      if not instance:
        _api.composer_raise_lasterr(composer, 'Failed to compose model')

      from . import model as _model
      return _model.Model(handle=instance)
    finally:
      _api.composer_free(composer)

  @staticmethod
  def join_componentwise_models(models, sample, comment, initial_options, logger, metainfo=None):
    """
    Creates model based on the models for different output components

    :param models: list of a simple models to join outputs
    :type models: iterable returning :class:`~da.p7core.gtapprox.Model` instances
    :param sample: dictionary describing training sample
    :type sample: ``dict``
    :param comment: user-defined commentary string for the model created
    :type comment: ``str``
    :param initial_options: dictionary describing initial options set by user
    :type initial_options: ``dict``

    The *sample* argument is a dictionary with the following keys:

    * ``"x"`` --- the input part of the training sample (values of variables).
    * ``"f"`` --- the response part of the training sample (function values).
    * ``"tol"`` --- response noise variance.
      Optional: the key may be omitted, or its value may be an explicit ``None``.
      Incompatible with sample point weights.
    * ``"weights"`` --- sample point weights.
      Optional: may be omitted or set to ``None``.
      Incompatible with response noise variance.

    """
    models = [_ for _ in models]
    if not models:
      raise _ex.GTException('Failed to compose model: no submodels are given.')

    wrapped_logger0 = Utilities._LogWrapper(logger, comment)
    wrapped_logger1 = _api.composer_log(wrapped_logger0)
    composer = _api.composer_create_cw(models[0].size_x, wrapped_logger1, ctypes.c_short(sample.get("linear_dependencies") is not None))
    if not composer:
      raise _ex.GTException('Failed to create model composer')

    try:
      linear_dependencies = sample.get("linear_dependencies")
      if linear_dependencies is None:
        expected_size_f = sum([_.size_f for _ in models])
      else:
        lindep_model = np.array(linear_dependencies.get("evaluation_model", [[]]), copy=_shared._SHALLOW, dtype=float, ndmin=2)
        if not lindep_model.size or lindep_model.shape[1] != (sum([_.size_f for _ in models]) + 1):
          raise _ex.GTException('Invalid model of the linear dependencies between outputs is given.')
        expected_size_f = lindep_model.shape[0]

      # additional variables are needed because composer_set_sample could replace original data
      data_x = _api.composer_set_sample(composer, 0, sample, 'x', models[0].size_x, True)
      data_f = _api.composer_set_sample(composer, 1, sample, 'f', expected_size_f, True)
      data_w = _api.composer_set_sample(composer, 2, sample, 'weights', 1, False)
      data_tol = _api.composer_set_sample(composer, 3, sample, 'tol', expected_size_f, False)

      _api.composer_set_comment(composer, Utilities._encode_comment(comment))
      _api.composer_set_options(composer, _shared.write_json(dict(initial_options)).encode('ascii'))

      for index, model in enumerate(models):
        if not _api.composer_append(composer, model._Model__instance):
          _api.composer_raise_lasterr(composer, 'Failed to append model #%d' % index)

      if linear_dependencies is not None:
        explanatory_vars = np.array(linear_dependencies["explanatory_variables"], dtype=ctypes.c_size_t)

        if not _api.composer_evaluation_model(composer, lindep_model.shape[0], lindep_model.shape[1] - 1
                                              , explanatory_vars.ctypes.data_as(_api.c_size_ptr), explanatory_vars.strides[0] // explanatory_vars.itemsize
                                              , lindep_model.ctypes.data_as(_api.c_double_ptr), lindep_model.strides[0] // lindep_model.itemsize
                                              , lindep_model.strides[1] // lindep_model.itemsize):
          _api.composer_raise_lasterr(composer, 'Failed to setup model of linear dependencies between outputs')

        if linear_dependencies.get("constraints") is not None:
          std_z, std_c, b, R, revR = tuple(np.array(_, copy=_shared._SHALLOW, dtype=float) for _ in linear_dependencies["constraints"])

          z_clip = np.empty((2, len(explanatory_vars)))

          if metainfo is not None:
            outputs_info = metainfo.get('Output Variables', [{}]*expected_size_f)
            for i, z in enumerate(explanatory_vars):
              z_clip[0, i] = outputs_info[z].get("min", -np.inf)
              z_clip[1, i] = outputs_info[z].get("max", np.inf)
          else:
            z_clip[0] = -np.inf
            z_clip[1] = np.inf


          if not _api.composer_constraints(composer, std_z.shape[0]
                                          , z_clip.ctypes.data_as(_api.c_double_ptr), z_clip.strides[0] // z_clip.itemsize, z_clip.strides[1] // z_clip.itemsize
                                          , std_c.shape[0], std_c.ctypes.data_as(_api.c_double_ptr), std_c.strides[0] // std_c.itemsize
                                          , R.ctypes.data_as(_api.c_double_ptr), R.strides[0] // R.itemsize, R.strides[1] // R.itemsize
                                          , b.ctypes.data_as(_api.c_double_ptr), b.strides[0] // b.itemsize
                                          , revR.ctypes.data_as(_api.c_double_ptr), revR.strides[0] // revR.itemsize, revR.strides[1] // revR.itemsize):
            _api.composer_raise_lasterr(composer, 'Failed to setup model of linear dependencies between outputs')

      instance = _api.composer_flush(composer)
      if not instance:
        _api.composer_raise_lasterr(composer, 'Failed to compose model')

      from . import model as _model
      return _model.Model(handle=instance)
    finally:
      _api.composer_free(composer)

  @staticmethod
  def _encode_comment(comment):
    if not comment:
      comment = ''
    elif not isinstance(comment, _six.string_types):
      comment = _shared.write_json(comment)

    try:
      return comment.encode('utf8')
    except (AttributeError, UnicodeDecodeError):
      pass
    return comment

def set_remote_build(builder, options={}, config_file=None):
  """Configure a GTApprox builder to run on a remote host over SSH or to use a HPC cluster.

  :param builder: model builder
  :param options: configuration options
  :param config_file: optional path to a configuration file
  :type builder: :class:`~da.p7core.gtapprox.Builder`
  :type options: ``dict``
  :type config_file: ``str``

  .. versionadded:: 4.3
     initial support for remote model training and distributed training of MoA models on a cluster.

  .. versionadded:: 5.3
     distributed training now supported for all componentwise models.

  .. versionchanged:: 6.3
     GTApprox now enables componentwise training by default, hence distributed training also becomes default when using a cluster.

  .. versionadded:: 6.6
     for models with categorical variables, distributed training now supports parallelization over all unique combinations of their values found in the training sample.

  .. deprecated:: 6.35
     this method is no longer updated and may be behind :meth:`~da.p7core.gtapprox.Builder.build()` and :meth:`~da.p7core.gtapprox.Builder.build_smart()` with regard to certain features or training techniques; using it is not recommended as it may get removed in future versions.

  Allows to configure a model builder to run remotely or to perform distributed model training on a cluster. Distributed training on a cluster means that a model is divided into several sub-models which become separate cluster jobs, allowing high degree of parallelization.

  .. note:: The same version of pSeven Core has to be installed on the local and remote hosts or, in case of distributed training, on the local host and all cluster nodes.

  .. note:: Remote training requires the ``paramiko`` module and its dependencies (``pycrypto`` and ``ecdsa``). These modules are not required for pSeven Core in general and hence are not listed in section :ref:`install_sysreq`.

  Distributed training is effective in the following cases:

  #. When using the Mixture of Approximators (MoA) technique (set :ref:`GTApprox/Technique<GTApprox/Technique>` to ``"MoA"``).
     This technique automatically partitions the training sample and trains several sub-models which are then combined in the final model.
     Naturally it can support distributed training for its sub-models.
  #. When a model has multidimensional output and componentwise training is enabled.
     The componentwise mode is default since 6.3 (see :ref:`GTApprox/DependentOutputs<GTApprox/DependentOutputs>`).
     Componentwise models can be trained in parallel since each model component is trained independently.
  #. When you define one or more categorical variables (see :ref:`GTApprox/CategoricalVariables<GTApprox/CategoricalVariables>`) and the training sample contains two or more unique combinations of their values.
     In this case, an independent model can be trained for each of such combinations.

  Note that a combination of the above cases is also supported --- that is, GTApprox tries to achieve as high parallelization ratio as possible. For example, if you train a componentwise model with categorical variables, the ratio can be higher than the number of model outputs.

  If none of the above cases apply, cluster training is still available but will simply submit a single job to the cluster.

  The *options* argument is a dictionary with the following recognized keys (all keys are ``str``, value types are noted below):

  * ``"ssh-hostname"`` (``str``) --- remote SSH host name.
  * ``"ssh-username"`` (``str``) --- SSH username.
  * ``"ssh-password"`` (``str``) --- SSH password (warning: unsafe).
  * ``"ssh-keyfile"`` (``str``) --- path to an SSH private key file.
  * ``"environment"`` (``dict``) --- dictionary of environment variables.
  * ``"workdir"`` (``str``) --- path to the working directory (local or remote, depending on SSH configuration).
  * ``"cluster"`` (``str``) --- cluster type. Currently the only supported type is LSF (``"lsf"``).
    If cluster type is ``None`` the model is trained on a remote host without using a HPC cluster.
  * ``"cluster-queue"`` (``str``) ---  name of the destination cluster queue.
  * ``"cluster-job-name"`` (``str``) --- cluster job name.
  * ``"cluster-exclusive"`` (``bool``) --- if ``True``, cluster nodes are used exclusively by jobs (the destination queue must support exclusive jobs).
    Note that if exclusive jobs are disabled (``False``), it is recommended to set :ref:`GTApprox/MaxParallel<GTApprox/MaxParallel>` to 1 or 2 (in *builder* options) to avoid performance degradation in case of two or more jobs being allocated to the same node by a cluster manager.
    See section :ref:`special_scalability` for details.
  * ``"cluster-slot-limit"`` (``int``) --- maximum number of jobs that can run simultaneously.

  .. ``"omp_num_threads"`` is not documented because #12111 is going to introduce the ability to set remote host envvars by a dict in *options*

  .. "cluster-custom-options" - ?

  To train a model remotely over SSH, you have to specify ``"ssh-hostname"`` and either:

  * ``"ssh-username"`` and ``"ssh-password"``, or
  * ``"ssh-keyfile"`` (``"ssh-username"`` may also be required when using a key file).

  Using a key file is recommended since storing SSH password in your script is unsafe.
  If you have no key file, you can use the standard ``getpass`` module as a workaround.
  For example::

    builder = gtapprox.Builder()
    # will prompt for password, getpass() requires interactive input
    gtapprox.set_remote_build(builder, {"ssh-hostname": "theserver", "ssh-username": "user", "ssh-password": getpass.getpass()})

  To use a cluster, you have to specify ``"cluster"``; ``"cluster-queue"`` and ``"cluster-job-name"`` may also be required, depending on your cluster manager configuration.
  If you connect to the cluster submit node over SSH, also specify ``"ssh-username"`` and ``"ssh-password"`` or ``"ssh-keyfile"``.
  For example::

    builder = gtapprox.Builder()
    # will prompt for password, getpass() requires interactive input
    gtapprox.set_remote_build(builder, {"ssh-hostname": "submit-node", "ssh-username": "user", "ssh-password": getpass.getpass(), "cluster": "lsf"})

  Instead of *options* you can specify the path to a configuration file in *config_file*.
  Also you can combine both --- in this case option values are read from file first, then from *options*.
  If a conflict occurs, values set by *options* override those specified in the configuration file.

  The configuration file should contain options and values in JSON format, for example::

    {
        "ssh-hostname": "submit-node",
        "ssh-username": "user",
        "ssh-password": "password",

        "environment": {"OMP_NUM_THREADS": 8, "SHELL": "/bin/bash -i"},

        "cluster": "lsf",
        "cluster-queue": "normal",
        "cluster-exclusive": True
    }

  """
  from . import builder as _builder
  # use a 'public class name' in exception message (not actual ...builder.Builder)
  if not isinstance(builder, _builder.Builder):
    raise TypeError("builder argument must be an instance of da.p7core.gtapprox.Builder")
  try:
    import paramiko
    import Crypto
    import ecdsa
  except ImportError:
    _shared.reraise(ImportError, "paramiko module and its dependecies are required to use remote build", sys.exc_info()[2])

  # Undocumented options for now:
  # * ``"omp-num-threads"`` --- limit the maximum number of threads (OMP_NUM_THREADS) (only if ssh or cluster is used)
  # * ``"cluster-custom-options"`` ---  custom string to pass to the resource manager
  from . import train
  hostname, username, password, private_key_path, workdir, omp_num_threads, cluster, cluster_options, environment = train.parse_config_options(config_file, options)

  if cluster:
    bm = train.BatchBuildManager(host=hostname, username=username, password=password, private_key_path=private_key_path,
                                 workdir=workdir, cluster_options=cluster_options, environment=environment)
  else:
    bm = train.SSHBuildManager(host=hostname, username=username, password=password, private_key_path=private_key_path, workdir=workdir,
                               environment=environment)
  if omp_num_threads:
    bm.set_omp_thread_limit(omp_num_threads)
  builder._set_build_manager(bm)

def disable_remote_build(builder):
  """Reset builder configuration to run on the local host only.

  :param builder: model builder
  :type builder: :class:`~da.p7core.gtapprox.Builder`

  Used to cancel the :meth:`~da.p7core.gtapprox.set_remote_build()` configuration.
  """
  from . import builder as _builder
  # use a 'public class name' in exception message (not actual ...builder.Builder)
  if not isinstance(builder, _builder.Builder):
    raise TypeError("builder argument must be an instance of %s" % _builder.Builder)
  builder._reset_build_manager()

def calculate_errors(reference, predicted, weights=None):
  """Calculates the prediction errors using a reference responses array.

  :param reference: reference responses
  :type reference: ``float`` or :term:`array-like`, 1D or 2D
  :param predicted: predicted responses
  :type predicted: ``float`` or :term:`array-like`, 1D or 2D
  :return: error values
  :rtype: ``dict``

  In general form, *reference* and *predicted* are 2D arrays.
  Several simplified forms are also supported, similar to :meth:`~da.p7core.gtapprox.Model.calc()`.
  Note *reference* and *predicted* arrays should have the same dimensionality.

  Returns a dictionary containing lists of error values calculated componentwise,
  with names of errors as keys:
  ``"Max"``, ``"Mean"``, ``"Median"``, ``"Q_0.95"``, ``"Q_0.99"``, ``"RMS"``, ``"RRMS"``, and ``"R^2"``.

  """

  reference = _shared.as_matrix(reference, name="Reference responses ('reference' argument)")
  predicted = _shared.as_matrix(predicted, name="Predicted responses ('predicted' argument)")

  if reference.shape != predicted.shape:
    raise ValueError('Sizes of reference and predicted samples do not match: %s != %s' % (reference.shape, predicted.shape))

  if weights is not None:
    try:
      weights = np.array(weights, dtype=float)
      if 0 == weights.ndim or 1 >= weights.size:
        weights = None
      elif np.equal(weights.shape, 1).sum() != (weights.ndim - 1):
        raise ValueError('Weights vector is expected while %s-dimensional matrix is given' % (weights.shape,))
      elif weights.size != reference.shape[0]:
        raise ValueError('Weights vector size does not conform the number of responses: %d != %d' % (weights.size, reference.shape[0]))
      else:
        weights = weights.flatten()
    except Exception:
      e, tb = sys.exc_info()[1:]
      _shared.reraise(ValueError, ('Weights vector does not conform reference responses: %s!' % (e,)), tb)

  err_desc = ctypes.c_void_p()
  names_len = ctypes.c_size_t()
  n_errors = ctypes.c_size_t()

  if not _api.read_errors_list(ctypes.c_char_p(), ctypes.byref(names_len), ctypes.byref(n_errors), ctypes.byref(err_desc)):
    _shared.ModelStatus.checkErrorCode(0, 'Failed to read errors names', err_desc)

  names = (ctypes.c_char * names_len.value)()
  if not _api.read_errors_list(names, ctypes.byref(names_len), _api.c_size_ptr(), ctypes.byref(err_desc)):
    _shared.ModelStatus.checkErrorCode(0, 'Failed to read errors names', err_desc)
  names = _shared.parse_json(_shared._preprocess_json(names.value))

  assert len(names) == n_errors.value, 'Unrecoverable internal error detected: inconsistent number of errors and its\' names.'

  errors = np.zeros((n_errors.value, reference.shape[1]), dtype=float)

  if not _api.calc_statistics(reference.shape[0], reference.shape[1],
                         reference.ctypes.data_as(_api.c_double_ptr), ctypes.cast(reference.ctypes.strides, _api.c_size_ptr),
                         predicted.ctypes.data_as(_api.c_double_ptr), ctypes.cast(predicted.ctypes.strides, _api.c_size_ptr),
                         _api.c_double_ptr() if weights is None else weights.ctypes.data_as(_api.c_double_ptr),
                         _api.c_size_ptr() if weights is None else ctypes.cast(weights.ctypes.strides, _api.c_size_ptr),
                         errors.ctypes.data_as(_api.c_double_ptr), ctypes.cast(errors.ctypes.strides, _api.c_size_ptr),
                         ctypes.byref(err_desc)):
    _shared.ModelStatus.checkErrorCode(0, 'Failed to calculate errors statistics', err_desc)

  return dict((name, errors[index].tolist()) for index, name in enumerate(names))

def _min_covering_ellipsoid(x, tol=1e-2, rcond=1.e-3):
  """
  Find the minimum covering ellipsoid
  https://people.orie.cornell.edu/miketodd/TYKhach.pdf
  """
  x = np.atleast_2d(x)
  Q = np.vstack((x.T, np.ones(x.shape[0])))
  p = (1.0 / x.shape[0]) * np.ones(x.shape[0])
  dim = x.shape[1]

  err = np.inf
  while err > tol:
    q = np.dot(Q, p.reshape(-1, 1) * Q.T)
    K = (Q * np.dot(np.linalg.pinv(q), Q)).sum(0)
    i_max = np.argmax(K)
    step = (K[i_max] - dim - 1.0) / ((dim + 1.0) * (K[i_max] - 1.0))
    next_p = (1.0 - step) * p
    next_p[i_max] += step
    err = np.linalg.norm(next_p - p)
    p = next_p

  center = np.dot(x.T, p)
  A = (np.dot(x.T, p.reshape(-1, 1) * x) - np.multiply.outer(center, center)) / dim
  eigA = np.linalg.eigh(A)[0]
  regul = np.finfo(float).eps
  while regul < 1. and rcond * eigA.max() > eigA.min():
    A.reshape(-1)[::A.shape[0]+1] += max(eigA.max(), 1.) * regul
    eigA = np.linalg.eigh(A)[0]
    regul *= 8.

  A = np.linalg.pinv(A)

  xc = x - center
  radii = np.einsum('ij,jk,ik->i', xc, A, xc)
  uncovered_count = np.count_nonzero(radii > 0.999)
  while uncovered_count:
    u, s, v = np.linalg.svd(A)
    s /= max(radii.max(), 1. + 1e-12)
    A = np.dot(u * s, v)
    radii = np.einsum('ij,jk,ik->i', xc, A, xc)
    prev_uncovered = uncovered_count
    uncovered_count = np.count_nonzero(radii > 0.999)
    if prev_uncovered <= uncovered_count:
      break # cannot improve, just stop
  return A, center

def get_nan_structure(y):
  '''Function detects whether we have NaN in output and any sample with different NaN structure
  '''
  nan_indices = np.isnan(_shared.as_matrix(y, name="'y' sample"))
  has_output_nan = np.any(nan_indices)

  if has_output_nan and nan_indices.shape[1] > 1:
    # for boolean vector z, all(z) == any(z) if all elements of z are the same
    has_mixed_nan = np.any(np.any(nan_indices, axis=1) != np.all(nan_indices, axis=1))
  else:
    has_mixed_nan = False

  return has_output_nan, has_mixed_nan

def _optional_assign(name, src, dst):
  if src.get(name) is not None:
    dst[name] = src[name]

def _read_vars_info(info_in, direction, info_out, model):
  if not _shared.is_iterable(info_in) or isinstance(info_in, _six.string_types):
    raise ValueError('The %s variables description must be a vector-like object' % direction)
  info_in = [_ for _ in info_in]
  if len(info_in) != len(info_out):
    raise ValueError('Length of the %s variables description vector does not match the number of %s variables: %d != %d' % (direction, direction, len(info_in), len(info_out),))

  options_list = ['name', 'description', 'quantity', 'unit', 'min', 'max']
  for i, desc in enumerate(info_in):
    if desc:
      if not _shared.is_mapping(desc):
        param_type = type(desc)
        raise ValueError('Description of the %s component #%d must be None or dict object: \'%s\' is given' % (direction, i, getattr(param_type, '__name__', param_type)))

      for name in options_list:
        _optional_assign(name, desc, info_out[i])

      for name in desc:
        if name not in options_list:
          raise ValueError('Description of the %s component #%d contains unknown key: \'%s\'' % (direction, i, name))

      sample_stat = model.details.get('Training Dataset', {}).get('Sample Statistics', {}).get(direction.capitalize())
      for param_name in ['min', 'max']:
        if param_name in info_out[i]:
          param_val = info_out[i][param_name]
          try:
            info_out[i][param_name] = float(param_val)
          except:
            if not isinstance(param_val, _six.string_types) or 'training' != param_val.lower():
              _shared.reraise(ValueError, ('Invalid \"%s\" property of the %s component #%d is given: %s.' % (param_name, direction, i, param_val)), sys.exc_info()[2])
            elif sample_stat is None:
              _shared.reraise(ValueError, ('Value of the \"%s\" property of the %s component #%d cannot be auto-selected. The model does not contains training dataset statistics.' % (param_name, direction, i)), sys.exc_info()[2])
            else:
              info_out[i][param_name] = sample_stat[param_name.capitalize()][i]

  return info_out

def _read_variability_me(variable):
  if variable["causality"].lower() == "output" and variable["variability"].lower() == "continuous":
    return "discrete"
  return variable["variability"]

def _read_variability_cs(variable):
  return variable["variability"]

def _make_identifier(float_label):
  # OpenModelica compatibility mode
  return "cat_" + "".join((_ if _.isalnum() else '_') for _ in ("%.15g" % (float_label,)).replace('+', 'p').replace('-', 'm'))

def _postprocess_enumerators(model, variable_info, return_identifiers):
  input_index, output_index = variable_info['origin']

  if input_index == -1:
    categorical_data = (model._categorical_f_map or {}).get(input_index)
  elif output_index == -1:
    categorical_data = (model._categorical_x_map or {}).get(output_index)
  else:
    # impossible case: partial derivative of either categorical output, or w.r.t categorical input or both
    categorical_data = None

  if not categorical_data:
    public_labels = variable_info.get('enumerators', variable_info.get('value'))
    if not return_identifiers:
      return [_six.text_type(_) for _ in public_labels]
    labels_dtype, inner_codes = float, public_labels
  else:
    labels_dtype, public_labels, inner_codes = categorical_data

  inner_codes = np.array(inner_codes, dtype=float, copy=_shared._SHALLOW).reshape(-1, 1)
  enumerators = np.array(variable_info.get('enumerators', variable_info.get('value')), dtype=float, copy=_shared._SHALLOW).reshape(1, -1)
  return [_make_identifier(float(public_labels[k])) for k in np.where(inner_codes == enumerators)[0]] \
      if (return_identifiers and np.issubdtype(labels_dtype, np.number)) \
    else [_six.text_type(public_labels[k]) for k in np.where(inner_codes == enumerators)[0]]

def _generate_fmi10_xml(mode, model, metainfo):
  import xml.etree.ElementTree as ET
  from xml.dom.minidom import parseString as parseXmlString

  pkg_name = _ex.GTException.__module__.split('.')[:2]
  pkg_version = __import__('.'.join(pkg_name), globals(), locals(), pkg_name[-1:]).__version__

  if mode not in ("cs10", "me10"):
    raise ValueError("Invalid or unsupporeted FMU generation mode: %s" % mode)

  xml_root = ET.Element('fmiModelDescription', {
      'fmiVersion': '1.0',
      'modelName': metainfo['model']['name'],
      'modelIdentifier': metainfo['model']['id'],
      'guid': metainfo['model']['guid'],
      'description': metainfo['model']['description'],
      'generationTool': 'pSeven Core ' + str(pkg_version),
      'generationDateAndTime': metainfo['model']['date'],
      'variableNamingConvention': metainfo['model']['naming_convention'],
      'numberOfContinuousStates': ('1' if mode == "me10" else '0'),
      'numberOfEventIndicators': '0',
    }
    )

  for dst_attr, src_attr in [('author', 'author'), ('version', 'version')]:
    if src_attr in metainfo['model']:
      xml_root.attrib[dst_attr] = metainfo['model'][src_attr]

  xml_typedefs = ET.Element('TypeDefinitions', {})
  xml_variables = ET.Element('ModelVariables', {})

  # All output dependencies are the same for all outputs
  xml_dependencies = ET.Element('DirectDependency', {})

  if 'output_dependencies' in metainfo:
    for var_name in metainfo['output_dependencies']:
      ET.SubElement(xml_dependencies, 'Name')
      xml_dependencies[-1].text = var_name

  read_variability = _read_variability_me if mode == "me10" else _read_variability_cs
  for variable in metainfo['variables']:
    xml_variable = ET.Element('ScalarVariable', {'valueReference': str(variable['refid']),
                                                 'name': variable['name'],
                                                 'causality': variable['causality'],
                                                 'variability': read_variability(variable),
                                                 })
    if variable.get('description'):
      xml_variable.attrib['description'] = variable['description']

    assert variable['type'] in ['real', 'enum']

    if 'real' == variable['type']:
      xml_real = ET.Element('Real')
      if 'start' in variable:
        xml_real.attrib['start'] = '%.17g' % float(variable['start'])
        if 'constant' == variable['variability']:
          xml_real.attrib['fixed'] = 'true'

      for attr_name in ['quantity', 'unit', 'min', 'max']:
        if attr_name in variable:
          xml_real.attrib[attr_name] = str(variable[attr_name])

      xml_variable.append(xml_real)
    elif 'enum' == variable['type']:
      type_name = u'categories_' + variable['name']
      xml_type = ET.SubElement(xml_typedefs, 'Type', {'name': type_name})
      xml_type = ET.SubElement(xml_type, 'EnumerationType')
      for value in _postprocess_enumerators(model, variable, True):
        ET.SubElement(xml_type, 'Item', {'name': value})

      xml_enum = ET.Element('Enumeration', {'declaredType': type_name})
      for attr_name in ['start', 'quantity', 'min', 'max']:
        if attr_name in variable:
          xml_enum.attrib[attr_name] = str(variable[attr_name])

      xml_variable.append(xml_enum)

    if len(xml_dependencies) and 'output' == variable['causality'] and 'constant' != variable["variability"]:
      xml_variable.append(xml_dependencies)

    xml_variables.append(xml_variable)

  if len(xml_typedefs):
    xml_root.append(xml_typedefs)

  if mode == "me10":
    xml_root.append(ET.Element('DefaultExperiment', {"startTime": "0.0",
                                                     "stopTime": "1.0",
                                                     "tolerance": "0.1"}))

  xml_root.append(xml_variables)

  if mode == "cs10":
    xml_impl = ET.Element('Implementation', {})
    ET.SubElement(ET.SubElement(xml_impl, 'CoSimulation_StandAlone'),
                 'Capabilities', {"canHandleVariableCommunicationStepSize":"true",
                                  "canHandleEvents":"true",
                                  "canRejectSteps":"false",
                                  "canInterpolateInputs":"false",
                                  "maxOutputDerivativeOrder":"0",
                                  "canRunAsynchronuously":"false",
                                  "canSignalEvents":"false",
                                  "canBeInstantiatedOnlyOncePerProcess":"false",
                                  "canNotUseMemoryManagementFunctions":"false",})
    xml_root.append(xml_impl)


  return parseXmlString(ET.tostring(xml_root)).toprettyxml('  ', encoding='utf-8')

def _generate_fmi20_xml(model, metainfo, sources):
  import xml.etree.ElementTree as ET
  from xml.dom.minidom import parseString as parseXmlString
  from hashlib import sha1

  pkg_name = _ex.GTException.__module__.split('.')[:2]
  pkg_version = __import__('.'.join(pkg_name), globals(), locals(), pkg_name[-1:]).__version__

  xml_root = ET.Element('fmiModelDescription', {
      'fmiVersion': '2.0',
      'modelName': metainfo['model']['name'],
      'guid': metainfo['model']['guid'],
      'description': metainfo['model']['description'],
      'generationTool': 'pSeven Core ' + str(pkg_version),
      'generationDateAndTime': metainfo['model']['date'],
      'variableNamingConvention': metainfo['model']['naming_convention'],
      #'numberOfContinuousStates': '1',
      'numberOfEventIndicators': '0',
    }
    )

  # optional top-level attributes
  for attr in ('author', 'version',  'copyright', 'license'):
    if attr in metainfo['model']:
      xml_root.attrib[attr] = metainfo['model'][attr]

  xml_me = ET.Element('ModelExchange', {
    'modelIdentifier': metainfo['model']['id'],
    'completedIntegratorStepNotNeeded': 'true',
    'canGetAndSetFMUstate': 'true',
    'canSerializeFMUstate': 'true',
    'providesDirectionalDerivative': 'true',
    })

  xml_cs = ET.Element('CoSimulation', {
    'modelIdentifier': metainfo['model']['id'],
    'canHandleVariableCommunicationStepSize': 'true',
    'canGetAndSetFMUstate': 'true',
    'canSerializeFMUstate': 'true',
    'providesDirectionalDerivative': 'true',
    })

  xml_source_files = ET.Element("SourceFiles")

  for source_file in sources:
    source_file = "/".join(path.relpath(source_file, "sources").split(path.sep)) # normilize separators
    xml_source_files.append(ET.Element("File", {"name": source_file}))

  xml_me.append(xml_source_files)
  xml_cs.append(xml_source_files)

  xml_root.append(xml_me)
  xml_root.append(xml_cs)

  xml_typedefs = ET.Element('TypeDefinitions', {})
  xml_variables = ET.Element('ModelVariables', {})
  xml_log_categories = ET.Element('LogCategories', {})
  xml_model_outputs = ET.Element('Outputs', {})
  xml_initial_unknowns = ET.Element('InitialUnknowns', {})

  # convert dependencies from names to indices
  effective_inputs_name = metainfo.get('output_dependencies')
  effective_inputs_index = []
  if effective_inputs_name:
    for index, variable in enumerate(metainfo['variables']):
      if variable['name'] in effective_inputs_name:
        effective_inputs_index.append(index + 1)
  effective_inputs_index = ' '.join(str(_) for _ in effective_inputs_index)

  local_name = sha1("local".encode("utf8"))
  for index, variable in enumerate(metainfo['variables']):
    local_name.update(variable['name'].encode("utf8"))
    xml_variable = ET.Element('ScalarVariable', {'valueReference': str(variable['refid']),
                                                 'name': variable['name'],
                                                 'causality': variable['causality'],
                                                 'variability': _read_variability_me(variable),
                                                 })
    if variable.get('description'):
      xml_variable.attrib['description'] = variable['description']
    xml_variable.append(ET.Comment(' index="%d" ' % (index + 1,)))

    assert variable['type'] in ['real', 'enum']

    if variable['variability'] == 'constant':
      xml_variable.attrib['initial'] = 'exact'

    if 'real' == variable['type']:
      xml_real = ET.Element('Real')
      if 'start' in variable:
        xml_real.attrib['start'] = '%.17g' % float(variable['start'])

      for attr_name in ['quantity', 'unit', 'min', 'max']:
        if attr_name in variable:
          xml_real.attrib[attr_name] = str(variable[attr_name])

      xml_variable.append(xml_real)
    elif 'enum' == variable['type']:
      type_name = u'categories_' + variable['name']
      xml_type = ET.SubElement(xml_typedefs, 'SimpleType', {'name': type_name})
      xml_type = ET.SubElement(xml_type, 'Enumeration')
      if 'enumerators' in variable:
        # mapped mode, use names from variable if any!
        for item_index, item_name in enumerate(_postprocess_enumerators(model, variable, False)):
          ET.SubElement(xml_type, 'Item', {'name': item_name, 'value': str(item_index+1)})
      elif 'value' in variable:
        # direct integer values mode
        for item_value, item_name in zip(variable['value'], _postprocess_enumerators(model, variable, False)):
          ET.SubElement(xml_type, 'Item', {'name': item_name, 'value': str(item_value)})
      else:
        raise _ex.InternalError('Invalid categorical variable %s: no enumerators.' % variable['name'])

      xml_enum = ET.Element('Enumeration', {'declaredType': type_name})
      for attr_name in ['start', 'quantity', 'min', 'max']:
        if attr_name in variable:
          xml_enum.attrib[attr_name] = str(variable[attr_name])
      xml_variable.append(xml_enum)

    if 'input' == variable['causality']:
      xml_variable.attrib['canHandleMultipleSetPerTimeInstant'] = 'true'
    else:
      unknown_attrs = {'index': str(index + 1)} # indices are one-based
      if effective_inputs_index:
        unknown_attrs['dependencies'] = effective_inputs_index
      xml_model_outputs.append(ET.Element("Unknown", unknown_attrs))
      if variable['variability'] != 'constant':
        xml_initial_unknowns.append(ET.Element("Unknown", unknown_attrs))
    xml_variables.append(xml_variable)

  # dummy continuous state
  dummy_idx, dummy_name = (1 + len(metainfo['variables'])), ('_'+local_name.hexdigest()[:8])
  xml_variable = ET.Element('ScalarVariable', {'valueReference': '1073741822', 'name': dummy_name,
                                               'causality': 'local', 'variability': 'continuous'})
  xml_variable.append(ET.Comment(' index="%d" ' % (dummy_idx,)))
  xml_variable.append(ET.Element('Real'))
  xml_variables.append(xml_variable)
  xml_variable = ET.Element('ScalarVariable', {'valueReference': '1073741823', 'name': 'der(_'+local_name.hexdigest()[:8] + ")",
                                               'causality': 'local', 'variability': 'constant',})
  xml_variable.append(ET.Comment(' index="%d" ' % (dummy_idx + 1,)))
  xml_variable.append(ET.Element('Real', {'derivative': str(dummy_idx), 'start': '0.0'}))
  xml_variables.append(xml_variable)

  # the order is matter

  if len(xml_typedefs):
    xml_root.append(xml_typedefs)

  # enumerate supported log categories
  xml_log_categories = ET.Element('LogCategories', {})
  for log_category_name in ('logAll', 'logFmiCall', 'logStatusWarning', 'logStatusDiscard', 'logStatusError', 'logDebugTrace',):
    xml_log_categories.append(ET.Element('Category', {'name': log_category_name}))
  xml_root.append(xml_log_categories)


  xml_root.append(ET.Element('DefaultExperiment', {"startTime": "0.0",
                                                   "stopTime": "1.0",
                                                   "tolerance": "0.1"}))

  xml_root.append(xml_variables)

  xml_model_structure = ET.Element('ModelStructure', {})
  xml_model_structure.append(xml_model_outputs)
  xml_model_derivatives = ET.Element('Derivatives', {})
  xml_model_derivatives.append(ET.Element("Unknown", {'index': str(dummy_idx + 1), 'dependencies': ''}))
  xml_model_structure.append(xml_model_derivatives)
  xml_initial_unknowns.append(ET.Element("Unknown", {'index': str(dummy_idx), 'dependencies': ''}))
  xml_model_structure.append(xml_initial_unknowns)

  xml_root.append(xml_model_structure)

  return parseXmlString(ET.tostring(xml_root)).toprettyxml('  ', encoding='utf-8')


_VALID_C_ID_FRONT = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_VALID_C_ID_CHARS = _VALID_C_ID_FRONT + "0123456789"

def _normalize_id(original_id):
  #normalized_id = ''.join((_ if _ == '_' or _.isalnum() else hex(ord(_))) for _ in original_id)
  normalized_id = ''.join((_ if _ in _VALID_C_ID_CHARS else hex(ord(_))) for _ in original_id)
  if not normalized_id or normalized_id[0] not in _VALID_C_ID_FRONT:
    normalized_id = "_" + normalized_id
  return normalized_id

def _read_timestamp(meta):
  utcdate = meta.get('date')
  if utcdate is not None:
    return str(utcdate)

  try:
    utcdate = _datetime.datetime.now(tz=_datetime.timezone.utc)
  except:
    pass

  if utcdate is None:
    utcdate = _datetime.datetime.utcnow()

  return '%04d-%02d-%02dT%02d:%02d:%02dZ' % utcdate.utctimetuple()[:6]

def _export_fmi(mode, model, file, id=None, der_outputs=False, meta=None, inputs_meta=None, outputs_meta=None, compilers=None, single_file=False):
  from .model import _debug_export_file_size

  if not model:
    raise ValueError('The model is not initialized.')

  if meta is None:
    meta = {}
  elif not _shared.is_mapping(meta):
    raise ValueError('The \'meta\' argument must be a dictionary (got %s)' % getattr(type(meta), '__name__', str(type(meta))))
  else:
    meta = dict((k, meta[k]) for k in meta)

  if compilers is None:
    compilers = {}
  elif not _shared.is_mapping(compilers):
    raise ValueError('The \'compilers\' argument must be a dictionary (got %s)' % getattr(type(compilers), '__name__', str(type(compilers))))
  else:
    compilers = dict((k, compilers[k]) for k in compilers)

  if single_file is None:
    single_file = True # default is single file mode for backward compatibility
  file_size = ctypes.c_size_t(np.iinfo(ctypes.c_size_t).max if single_file else _debug_export_file_size(mode)*1024)

  known_model_parameters = ['name', 'description', 'naming_convention', 'author', 'version'] + (['copyright', 'license'] if mode == "fmi20" else [])
  known_platforms = {'win32': '.dll', 'win64': '.dll', 'linux32': '.so', 'linux64': '.so'}

  for param_name in meta:
    if param_name not in known_model_parameters:
      raise ValueError('Unknown key in \'meta\': \'%s\'' % param_name)

  for platform in compilers:
    if platform not in known_platforms:
      raise ValueError('Unknown key in \'compilers\': \'%s\'' % platform)

  # collect and validate input parameters
  id = id if isinstance(id, _six.string_types) else ''

  metainfo = {'model': {},
              'der_outputs': bool(der_outputs),}

  if id:
    model_id = _normalize_id(id)
    if model_id != id:
      _warn.warn("Some C compilers may consider '%s' to be an invalid name prefix, changing the model id and filename to '%s' to avoid compilation issues." % (id, model_id))
  elif isinstance(file, _six.string_types):
    # use file name as model id, but in this case we should not alter name
    id = path.splitext(path.basename(file))[0]
    model_id = _normalize_id(id)
    if model_id != id:
      raise ValueError("Cannot use the filename-based model id '%s' because some C compilers may consider it to be an invalid name prefix." % id)
  else:
    raise ValueError('Cannot determine model id: either the file path or the id string is required.')

  if isinstance(file, _six.string_types) and model_id != path.splitext(path.basename(file))[0]:
    raise ValueError('The FMI standard requires that model id and filename are the same, but "%s" and "%s" are not.' % (model_id, path.splitext(path.basename(file))[0]))

  metainfo['model']['id'] = model_id
  metainfo['model']['name'] = meta.get('name', id)
  metainfo['model']['guid'] = str(uuid.uuid1())
  metainfo['model']['description'] = meta.get('description', model.comment)
  metainfo['model']['date'] = _read_timestamp(meta)
  metainfo['model']['naming_convention'] = str(meta.get('naming_convention', 'flat')).lower()
  _optional_assign('author', meta, metainfo['model'])
  _optional_assign('version', meta, metainfo['model'])
  _optional_assign('copyright', meta, metainfo['model'])
  _optional_assign('license', meta, metainfo['model'])

  metainfo['input'] = model.details['Input Variables']
  if inputs_meta:
    metainfo['input'] = _read_vars_info(inputs_meta, 'input', metainfo['input'], model)

  metainfo['output'] = model.details['Output Variables']
  if outputs_meta:
    metainfo['output'] = _read_vars_info(outputs_meta, 'output', metainfo['output'], model)

  # validate parameters types
  for param_name in known_model_parameters:
    if param_name in metainfo['model'] and not isinstance(metainfo['model'][param_name], _six.string_types):
      param_type = type(metainfo['model'][param_name])
      raise ValueError('The model \'%s\' parameter must be string: \'%s\' is given' % (param_name, getattr(param_type, '__name__', str(param_type))))

  unique_names = {}
  for direction in ['input', 'output']:
    for var_index, var_info in enumerate(metainfo[direction]):
      # check name
      var_spec = '%s component #%d' % (direction, var_index)
      if var_info['name'] in unique_names:
        raise ValueError('Duplicate name \"%s\" is detected for the model %s and %s' % (var_info['name'], unique_names[var_info['name']], var_spec))
      else:
        unique_names[var_info['name']] = var_spec

      # check parameters
      for param_name in ['name', 'description', 'quantity', 'unit']:
        if param_name in var_info and not isinstance(var_info[param_name], _six.string_types):
          param_type = type(var_info[param_name])
          raise ValueError('The \'%s\' parameter of the model %s must be string: \'%s\' is given' % (param_name, var_spec, getattr(param_type, '__name__', str(param_type))))

  if metainfo['model']['naming_convention'] not in ['flat', 'structured']:
    raise ValueError('Invalid naming convention is given: "%s" ("flat" or "structured" is expected)' % metainfo['model']['naming_convention'])

  # generate model source code
  if mode == "me10":
    fmi_do_export, fmi_standard = _api.fmi_do_export_me, 1
  elif mode == "cs10":
    fmi_do_export, fmi_standard = _api.fmi_do_export_cs, 1
  elif mode == "fmi20":
    fmi_do_export, fmi_standard = _api.fmi_do_export_fmu20, 2
  else:
    raise ValueError("Invalid or unsupported FMI export mode: %s" % mode)

  # update metainfo
  info_js = ctypes.c_char_p(_shared.write_json(metainfo).encode("utf8"))
  err_desc = ctypes.c_void_p()

  c_metainfo = _shared._unsafe_allocator()
  _shared._raise_on_error(_api.fmi_update_metainfo(model._Model__instance, info_js, c_metainfo.callback, fmi_standard, ctypes.byref(err_desc)), \
                          'Failed to export model to the FMI format', err_desc)

  metainfo = _shared.parse_json(c_metainfo.value)

  # assemble model zip file
  with _archives._with_zipfile(file, "w", _zipfile.ZIP_DEFLATED) as zip:
    file_writer = _ZipArchiveWriterEx(zip) if (compilers or mode == "fmi20") else _archives._ZipArchiveWriter(zip)

    if not fmi_do_export(model._Model__instance, c_metainfo.value, path.join('sources', model_id).encode("utf8"),\
                         _api.callback_single_file(file_writer), file_size, ctypes.byref(err_desc)):
      _shared.ModelStatus.checkErrorCode(0, 'Failed to export model to the FMI format', err_desc)

    if mode == "fmi20":
      module_prefix = "#define DISABLE_FMI2_FUNCTION_PREFIX\n\n"
      zip.writestr('modelDescription.xml', _generate_fmi20_xml(model, metainfo, [_[0] for _ in file_writer.files]))
    else:
      module_prefix = ""
      zip.writestr('modelDescription.xml', _generate_fmi10_xml(mode, model, metainfo))

    for platform in known_platforms:
      if platform in compilers:
        binary_data = compilers[platform](((module_prefix + "\n\n".join(_[1] for _ in file_writer.files)) if single_file else \
                                            [(path.basename(_[0]), module_prefix + _[1]) for _ in file_writer.files]), model_id, platform)
        if binary_data:
          zip.writestr(path.join('binaries', platform, model_id + known_platforms[platform]), binary_data)

  fmu_variables = []
  for variable in metainfo['variables']:
    fmu_variables.append({'name'        : variable['name'],
                          'causality'   : variable['causality'],
                          'variability' : variable['variability'],
                          'type'        : variable['type'],
                          'origin'      : variable['origin'],
                          })
    if 'value' in variable:
      fmu_variables[-1]['value'] = variable['value']
    if 'enumerators' in variable:
      fmu_variables[-1]['enumerators'] = variable['enumerators']

  return fmu_variables


def export_fmi_cs(model, file, id=None, der_outputs=False, meta=None, inputs_meta=None, outputs_meta=None, compilers=None, single_file=None):
  """Export the model to a Functional Mock-up Unit for Co-Simulation 1.0.

  :param model: exported model
  :param file: file object or path where to export
  :param id: a string used in model and function names
  :param der_outputs: if ``True``, include partial derivatives of model outputs in the list of FMI model outputs
  :param meta: model information
  :param inputs_meta: input variable information
  :param outputs_meta: output variable information
  :param compilers: compiler settings to export an FMU with binary
  :param single_file: pass sources to compilers as a single file (default) or multiple files (``False``)
  :return: description of model variables
  :type model: :class:`~da.p7core.gtapprox.Model`
  :type file: ``file`` or ``str``
  :type id: ``str``
  :type der_outputs: ``bool``
  :type meta: ``dict``
  :type inputs_meta: ``list``
  :type outputs_meta: ``list``
  :type compilers: ``dict``
  :type single_file: ``bool``
  :rtype: ``list``

  .. versionadded:: 6.9

  .. versionchanged:: 6.24
     added the :arg:`single_file` parameter.

  According to the FMI standard, in an FMU with source code
  the same string (:arg:`id`) is used as the model name and as a prefix in function names in the model code.
  If :arg:`file` is a path, omit :arg:`id` as it will be generated from the filename in the path.
  In this case, the filename must be a valid C identifier.
  If :arg:`file` is a file object, :arg:`id` is required and must be a valid C identifier.
  If you specify both :arg:`file` and :arg:`id`, the filename and :arg:`id` must be identical.
  The file extension should be ``.fmu`` by standard.

  For the general model description, use :arg:`meta`.
  This argument is a dictionary that may contain the following keys:

  * ``"name"``: a string with the name of the model that will be shown in the modeling environment.
  * ``"description"``: a string with a brief model description; if omitted, the model's :attr:`~da.p7core.gtapprox.Model.comment` is used.
  * ``"naming_convention"``: name convention used for names of variables. For details, see the FMI documentation. Currently included in the standard are:

    * ``"flat"``: a list of strings (default).
    * ``"structured"``: hierarchical names using dot separator, with array elements and derivative characterization.

  * ``"author"``: an string containing author's name and organization.
  * ``"version"``: model version string.

  For variable description, use :arg:`inputs_meta` and :arg:`outputs_meta`.
  If specified, variable description must be a list with length :attr:`~da.p7core.gtapprox.Model.size_x` (or :attr:`~da.p7core.gtapprox.Model.size_f` respectively).
  List element is a dictionary with the following keys (all keys are optional):

  * ``"name"``: name of the variable (string), optional.
    Default is :samp:`"x[{i}]"` for inputs, :samp:`"f[{i}]"` for outputs,
    where :samp:`{i}` is the index of this input or output in the training sample.
  * ``"description"``: a string containing brief variable description.
  * ``"quantity"``: physical quantity of the variable, for example ``"Angle"`` or ``"Energy"``.
  * ``"unit"``: measurement units used for this variable in model equations, for example ``"deg"`` or ``"J"``.
  * ``"min"``: the minimum value of the variable (``float``) or ``"training"`` to use the minimum value from the model's training sample. If omitted, the minimum is the largest negative number that can be represented on the machine.
  * ``"max"``: the maximum value of the variable (``float``) or ``"training"`` to use the training sample value. If omitted, the maximum is the largest positive number that can be represented on the machine.

  If some or all details for a variable are not specified, GTApprox also tries to get them from model's
  :attr:`~da.p7core.gtapprox.Model.details`.
  If some details are specified both in :attr:`~da.p7core.gtapprox.Model.details` and as parameters to
  :func:`~da.p7core.gtapprox.export_fmi_cs()`, information from parameters takes priority.

  By default, an FMU is exported with source code only.
  To export an FMU with binaries for one or more of the standard FMI platforms, specify :arg:`compilers`.

  * A key in :arg:`compilers` is a string identifying the target platform.
    Recognized platform names are: ``"win32"``, ``"win64"``, ``"linux32"``, ``"linux64"``.
    You can add compilers for different platforms to export an FMU with cross-platform support.
  * A value in :arg:`compilers` is a Python callable object that implements an FMU compiler
    for the platform specified by key.

  Each callable in :arg:`compilers` should support three input parameters:

  * :arg:`source_code` - the source code to compile.

    * If :arg:`single_file` is ``True`` or not specified, :arg:`source_code` is a string.
    * If :arg:`single_file` is ``False``, :arg:`source_code` is a list of string pairs ``(file_name, source_code)``.
      The ``file_name`` and ``source_code`` strings are the name and source code of a C translation unit.
      Together, these translation units form the FMU source code.

  * :arg:`model_id` is the model identifier and the name of the shared library (a ``.dll`` or ``.so`` file).
  * :arg:`platform` is the platform identifier, one of the following strings:
    ``"win32"``, ``"win64"``, ``"linux32"``, ``"linux64"``.

  Each callable in :arg:`compilers` must return a string containing the binary code of the compiled shared library.
  Note that any exception raised by the callable is re-raised by :func:`~da.p7core.gtapprox.export_fmi_cs()`.

  On successful export, :func:`~da.p7core.gtapprox.export_fmi_cs()` returns
  a description of the exported model variables in terms of FMI standard.
  The description is a list of dictionaries with the following keys:

  * ``"name"``: the name of the variable.
  * ``"causality"``: ``"input"`` or ``"output"``; indicates how the variable is visible from the outside of the model.
  * ``"variability"``: ``"constant"`` or ``"parameter"``; indicates when the value of the variable changes.
  * ``"type"``: ``"real"`` or ``"enum"``; indicates type of the variable.
  * ``"value"``: ``"real"`` or ``"constant"``; omitted for other types of variables.
  * ``"enumerators"``: list of enumerators if variable type is ``"enum"``; omitted for other types of variables.
  * ``"origin"``: a tuple of two integers that are 0-based indices of the original model input and output components related to this FMU parameter:

    * ``(j, -1)`` is the j-th component of the original model input.
    * ``(-1, i)`` is the i-th component of the original model output.
    * ``(j, i)`` is the partial derivative of the i-th model output with respect to j-th input.

  """
  return _export_fmi(mode="cs10", model=model, file=file, id=id, der_outputs=der_outputs, meta=meta, inputs_meta=inputs_meta, outputs_meta=outputs_meta, compilers=compilers, single_file=single_file)

def export_fmi_me(model, file, id=None, der_outputs=False, meta=None, inputs_meta=None, outputs_meta=None, compilers=None, single_file=None):
  """Export the model to a Functional Mock-up Unit for Model Exchange 1.0.

  :param model: exported model
  :param file: file object or path where to export
  :param id: a string used in model and function names
  :param der_outputs: if ``True``, include partial derivatives of model outputs in the list of FMI model outputs
  :param meta: model information
  :param inputs_meta: input variable information
  :param outputs_meta: output variable information
  :param compilers: compiler settings to export an FMU with binary
  :param single_file: pass sources to compilers as a single file (default) or multiple files (``False``)
  :return: description of model variables
  :type model: :class:`~da.p7core.gtapprox.Model`
  :type file: ``file`` or ``str``
  :type id: ``str``
  :type der_outputs: ``bool``
  :type meta: ``dict``
  :type inputs_meta: ``list``
  :type outputs_meta: ``list``
  :type compilers: ``dict``
  :type single_file: ``bool``
  :rtype: ``list``

  .. versionadded:: 6.14.3

  .. versionchanged:: 6.24
     added the :arg:`single_file` parameter.

  According to the FMI standard, in an FMU with source code
  the same string (:arg:`id`) is used as the model name and as a prefix in function names in the model code.
  If :arg:`file` is a path, omit :arg:`id` as it will be generated from the filename in the path.
  In this case, the filename must be a valid C identifier.
  If :arg:`file` is a file object, :arg:`id` is required and must be a valid C identifier.
  If you specify both :arg:`file` and :arg:`id`, the filename and :arg:`id` must be identical.
  The file extension should be ``.fmu`` by standard.

  For the general model description, use :arg:`meta`.
  This argument is a dictionary that may contain the following keys:

  * ``"name"``: a string with the name of the model that will be shown in the modeling environment.
  * ``"description"``: a string with a brief model description; if omitted, the model's :attr:`~da.p7core.gtapprox.Model.comment` is used.
  * ``"naming_convention"``: name convention used for names of variables. For details, see the FMI documentation. Currently included in the standard are:

    * ``"flat"``: a list of strings (default).
    * ``"structured"``: hierarchical names using dot separator, with array elements and derivative characterization.

  * ``"author"``: an string containing author's name and organization.
  * ``"version"``: model version string.

  For variable description, use :arg:`inputs_meta` and :arg:`outputs_meta`.
  If specified, variable description must be a list with length :attr:`~da.p7core.gtapprox.Model.size_x` (or :attr:`~da.p7core.gtapprox.Model.size_f` respectively).
  List element is a dictionary with the following keys (all keys are optional):

  * ``"name"``: name of the variable (string), optional.
    Default is :samp:`"x[{i}]"` for inputs, :samp:`"f[{i}]"` for outputs,
    where :samp:`{i}` is the index of this input or output in the training sample.
  * ``"description"``: a string containing brief variable description.
  * ``"quantity"``: physical quantity of the variable, for example ``"Angle"`` or ``"Energy"``.
  * ``"unit"``: measurement units used for this variable in model equations, for example ``"deg"`` or ``"J"``.
  * ``"min"``: the minimum value of the variable (``float``) or ``"training"`` to use the minimum value from the model's training sample. If omitted, the minimum is the largest negative number that can be represented on the machine.
  * ``"max"``: the maximum value of the variable (``float``) or ``"training"`` to use the training sample value. If omitted, the maximum is the largest positive number that can be represented on the machine.

  If some or all details for a variable are not specified, GTApprox also tries to get them from model's
  :attr:`~da.p7core.gtapprox.Model.details`.
  If some details are specified both in :attr:`~da.p7core.gtapprox.Model.details` and as parameters to
  :func:`~da.p7core.gtapprox.export_fmi_me()`, information from parameters takes priority.

  By default, an FMU is exported with source code only.
  To export an FMU with binaries for one or more of the standard FMI platforms, specify :arg:`compilers`.

  * A key in :arg:`compilers` is a string identifying the target platform.
    Recognized platform names are: ``"win32"``, ``"win64"``, ``"linux32"``, ``"linux64"``.
    You can add compilers for different platforms to export an FMU with cross-platform support.
  * A value in :arg:`compilers` is a Python callable object that implements an FMU compiler
    for the platform specified by key.

  Each callable in :arg:`compilers` should support three input parameters:

  * :arg:`source_code` - the source code to compile.

    * If :arg:`single_file` is ``True`` or not specified, :arg:`source_code` is a string.
    * If :arg:`single_file` is ``False``, :arg:`source_code` is a list of string pairs ``(file_name, source_code)``.
      The ``file_name`` and ``source_code`` strings are the name and source code of a C translation unit.
      Together, these translation units form the FMU source code.

  * :arg:`model_id` is the model identifier and the name of the shared library (a ``.dll`` or ``.so`` file).
  * :arg:`platform` is the platform identifier, one of the following strings:
    ``"win32"``, ``"win64"``, ``"linux32"``, ``"linux64"``.

  Each callable in :arg:`compilers` must return a string containing the binary code of the compiled shared library.
  Note that any exception raised by the callable is re-raised by :func:`~da.p7core.gtapprox.export_fmi_me()`.

  On successful export, :func:`~da.p7core.gtapprox.export_fmi_me()` returns
  a description of the exported model variables in terms of FMI standard.
  The description is a list of dictionaries with the following keys:

  * ``"name"``: the name of the variable.
  * ``"causality"``: ``"input"`` or ``"output"``; indicates how the variable is visible from the outside of the model.
  * ``"variability"``: ``"constant"`` or ``"parameter"``; indicates when the value of the variable changes.
  * ``"type"``: ``"real"`` or ``"enum"``; indicates type of the variable.
  * ``"value"``: ``"real"`` or ``"constant"``; omitted for other types of variables.
  * ``"enumerators"``: list of enumerators if variable type is ``"enum"``; omitted for other types of variables.
  * ``"origin"``: a tuple of two integers that are 0-based indices of the original model input and output components related to this FMU parameter:

    * ``(j, -1)`` is the j-th component of the original model input.
    * ``(-1, i)`` is the i-th component of the original model output.
    * ``(j, i)`` is the partial derivative of the i-th model output with respect to j-th input.

  """
  return _export_fmi(mode="me10", model=model, file=file, id=id, der_outputs=der_outputs, meta=meta, inputs_meta=inputs_meta, outputs_meta=outputs_meta, compilers=compilers, single_file=single_file)

def export_fmi_20(model, file, id=None, der_outputs=False, meta=None, inputs_meta=None, outputs_meta=None, compilers=None, single_file=None):
  """Export the model to a Functional Mock-up Unit for Model Exchange and Co-Simulation 2.0.

  :param model: exported model
  :param file: file object or path where to export
  :param id: a string used in model and function names
  :param der_outputs: if ``True``, include partial derivatives of model outputs in the list of FMI model outputs
  :param meta: model information
  :param inputs_meta: input variable information
  :param outputs_meta: output variable information
  :param compilers: compiler settings to export an FMU with binary
  :param single_file: pass sources to compilers as a single file (default) or multiple files (``False``)
  :return: description of model variables
  :type model: :class:`~da.p7core.gtapprox.Model`
  :type file: ``file`` or ``str``
  :type id: ``str``
  :type der_outputs: ``bool``
  :type meta: ``dict``
  :type inputs_meta: ``list``
  :type outputs_meta: ``list``
  :type compilers: ``dict``
  :type single_file: ``bool``
  :rtype: ``list``

  .. versionadded:: 6.31

  According to the FMI standard, in an FMU with source code
  the same string (:arg:`id`) is used as the model name and as a prefix in function names in the model code.
  If :arg:`file` is a path, omit :arg:`id` as it will be generated from the filename in the path.
  In this case, the filename must be a valid C identifier.
  If :arg:`file` is a file object, :arg:`id` is required and must be a valid C identifier.
  If you specify both :arg:`file` and :arg:`id`, the filename and :arg:`id` must be identical.
  The file extension should be ``.fmu`` by standard.

  For the general model description, use :arg:`meta`.
  This argument is a dictionary that may contain the following keys:

  * ``"name"``: a string with the name of the model that will be shown in the modeling environment.
  * ``"description"``: a string with a brief model description; if omitted, the model's :attr:`~da.p7core.gtapprox.Model.comment` is used.
  * ``"naming_convention"``: name convention used for names of variables. For details, see the FMI documentation. Currently included in the standard are:

    * ``"flat"``: a list of strings (default).
    * ``"structured"``: hierarchical names using dot separator, with array elements and derivative characterization.

  * ``"author"``: an string containing author's name and organization.
  * ``"version"``: model version string.
  * ``"copyright"``: optional information on the intellectual property copyright for this FMU.
  * ``"license"``: optional information on the intellectual property licensing for this FMU.

  For variable description, use :arg:`inputs_meta` and :arg:`outputs_meta`.
  If specified, variable description must be a list with length :attr:`~da.p7core.gtapprox.Model.size_x` (or :attr:`~da.p7core.gtapprox.Model.size_f` respectively).
  List element is a dictionary with the following keys (all keys are optional):

  * ``"name"``: name of the variable (string), optional.
    Default is :samp:`"x[{i}]"` for inputs, :samp:`"f[{i}]"` for outputs,
    where :samp:`{i}` is the index of this input or output in the training sample.
  * ``"description"``: a string containing brief variable description.
  * ``"quantity"``: physical quantity of the variable, for example ``"Angle"`` or ``"Energy"``.
  * ``"unit"``: measurement units used for this variable in model equations, for example ``"deg"`` or ``"J"``.
  * ``"min"``: the minimum value of the variable (``float``) or ``"training"`` to use the minimum value from the model's training sample. If omitted, the minimum is the largest negative number that can be represented on the machine.
  * ``"max"``: the maximum value of the variable (``float``) or ``"training"`` to use the training sample value. If omitted, the maximum is the largest positive number that can be represented on the machine.

  If some or all details for a variable are not specified, GTApprox also tries to get them from model's
  :attr:`~da.p7core.gtapprox.Model.details`.
  If some details are specified both in :attr:`~da.p7core.gtapprox.Model.details` and as parameters to
  :func:`~da.p7core.gtapprox.export_fmi_20()`, information from parameters takes priority.

  By default, an FMU is exported with source code only.
  To export an FMU with binaries for one or more of the standard FMI platforms, specify :arg:`compilers`.

  * A key in :arg:`compilers` is a string identifying the target platform.
    Recognized platform names are: ``"win32"``, ``"win64"``, ``"linux32"``, ``"linux64"``.
    You can add compilers for different platforms to export an FMU with cross-platform support.
  * A value in :arg:`compilers` is a Python callable object that implements an FMU compiler
    for the platform specified by key.

  Each callable in :arg:`compilers` should support three input parameters:

  * :arg:`source_code` - the source code to compile.

    * If :arg:`single_file` is ``True`` or not specified, :arg:`source_code` is a string.
    * If :arg:`single_file` is ``False``, :arg:`source_code` is a list of string pairs ``(file_name, source_code)``.
      The ``file_name`` and ``source_code`` strings are the name and source code of a C translation unit.
      Together, these translation units form the FMU source code.

  * :arg:`model_id` is the model identifier and the name of the shared library (a ``.dll`` or ``.so`` file).
  * :arg:`platform` is the platform identifier, one of the following strings:
    ``"win32"``, ``"win64"``, ``"linux32"``, ``"linux64"``.

  Each callable in :arg:`compilers` must return a string containing the binary code of the compiled shared library.
  Note that any exception raised by the callable is re-raised by :func:`~da.p7core.gtapprox.export_fmi_20()`.

  On successful export, :func:`~da.p7core.gtapprox.export_fmi_20()` returns
  a description of the exported model variables in terms of FMI standard.
  The description is a list of dictionaries with the following keys:

  * ``"name"``: the name of the variable.
  * ``"causality"``: ``"input"`` or ``"output"``; indicates how the variable is visible from the outside of the model.
  * ``"variability"``: ``"constant"`` or ``"parameter"``; indicates when the value of the variable changes.
  * ``"type"``: ``"real"`` or ``"enum"``; indicates type of the variable.
  * ``"value"``: ``"real"`` or ``"constant"``; omitted for other types of variables.
  * ``"enumerators"``: list of enumerators if variable type is ``"enum"``; omitted for other types of variables.
  * ``"origin"``: a tuple of two integers that are 0-based indices of the original model input and output components related to this FMU parameter:

    * ``(j, -1)`` is the j-th component of the original model input.
    * ``(-1, i)`` is the i-th component of the original model output.
    * ``(j, i)`` is the partial derivative of the i-th model output with respect to j-th input.

  """
  return _export_fmi(mode="fmi20", model=model, file=file, id=id, der_outputs=der_outputs, meta=meta, inputs_meta=inputs_meta, outputs_meta=outputs_meta, compilers=compilers, single_file=single_file)
