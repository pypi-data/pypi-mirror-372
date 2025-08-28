#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present

"""
Approximation model builder
---------------------------

.. currentmodule:: da.p7core.gtapprox.builder

"""
from __future__ import with_statement
from __future__ import division

import sys
import ctypes as _ctypes
import time
import re
import numpy as np

from datetime import datetime

from .. import six as _six
from ..six.moves import xrange, StringIO

from .. import shared as _shared
from .. import exceptions as _ex
from .. import loggers

from . import model as _gtamodel
from . import details as _details
from . import build_manager as _build_manager
from . import technique_selection as _technique_selection
from . import utilities as _utilities
from . smart_selection import SmartSelector, _get_default_hints_options
from . sbo_opt_problem import _get_aggregate_errors, _make_job_prefix
from .dependencies import find_linear_dependencies, _linear_regression_string
from .iterative_iv import _IterativeIV

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_void_ptr_ptr = _ctypes.POINTER(_ctypes.c_void_p)

    self.set_build_log = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p,
                                           self.c_void_ptr_ptr)(('GTApproxModelUnsafeSetLog', self.__library))
    self.set_options = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_short, _ctypes.c_char_p,
                                         self.c_void_ptr_ptr)(("GTApproxModelUnsafeSetOptions", self.__library))
    self.update_initial_model_info = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p,
                                                       self.c_void_ptr_ptr)(("GTApproxModelUnsafeSetInitialModelInfo", self.__library))
    self.finalize_iv_statistics = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_short, _ctypes.c_void_p,
                                                    self.c_void_ptr_ptr)(('GTApproxModelUnsafeFinalizeIVStatistics', self.__library))
    self.modify_train_dataset = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_short, _ctypes.c_size_t,
                                                  _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_ptr, self.c_size_ptr,
                                                  self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr,
                                                  self.c_double_ptr, self.c_size_ptr, _ctypes.c_void_p, self.c_void_ptr_ptr)(('GTApproxModelUnsafeSetTrainDataset', self.__library))
    self.modify_test_dataset = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_short, _ctypes.c_size_t,
                                                 _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_ptr, self.c_size_ptr,
                                                 self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr,
                                                 self.c_void_ptr_ptr)(('GTApproxModelUnsafeSetWeightedTestDataset', self.__library))
    self.restrict_validity_domain = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_short, _ctypes.c_size_t,
                                                      self.c_double_ptr, self.c_size_ptr, _ctypes.c_size_t, self.c_double_ptr,
                                                      self.c_size_ptr, self.c_void_ptr_ptr)(('GTApproxModelUnsafeRestrictValidityDomain', self.__library))
    self.set_input_domain = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_char_p, # model, domain op, combine op,
                                              self.c_size_ptr, self.c_double_ptr, self.c_size_ptr, # limits data shape, pointer, strides,
                                              _ctypes.c_size_t, self.c_size_ptr, _ctypes.c_size_t, # categorical variables indices count, pointer, step
                                              self.c_void_ptr_ptr)(('GTApproxModelUnsafeSetInputDomain', self.__library))
    self.merge_input_domains = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, self.c_void_ptr_ptr,
                                                 self.c_void_ptr_ptr)(('GTApproxModelUnsafeMergeInputDomains', self.__library))
    self.read_sys_info = _ctypes.CFUNCTYPE(_ctypes.c_short, self.c_size_ptr, _ctypes.c_char_p,
                                           self.c_size_ptr)(('GTApproxSystemInfo', self.__library))

    self.tolerance_to_weights = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, _ctypes.c_size_t, # ret. code, no. points, point dim,
                                                  self.c_double_ptr, _ctypes.c_size_t, _ctypes.c_size_t, # pointer to tolerance, tolerance lead dimension, tolerance increment,
                                                  self.c_double_ptr, _ctypes.c_size_t, self.c_void_ptr_ptr # pointer to weights, weights step, error pointer
                                                  )(('GTApproxModelToleranceToWeights', self.__library))


    self.filter_callback_type = _ctypes.CFUNCTYPE(None, _ctypes.c_short, _ctypes.c_void_p)
    self.filter_moa = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_void_p, _ctypes.c_char_p, _ctypes.c_size_t,
                                        _ctypes.c_size_t, _ctypes.c_size_t, self.c_double_ptr, self.c_size_ptr,
                                        self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr,
                                        _ctypes.c_void_p, self.c_void_ptr_ptr)(('GTApproxModelUnsafeFilterMoA', self.__library))
    self.outputs_dependencies = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_double, _ctypes.c_void_p, # success, model, threshold, string allocator
                                                  self.c_void_ptr_ptr)(('GTApproxModelReadOutputsDependencies', self.__library)) # err pointer


_api = _API()

class Builder(object):
  """Approximation model builder."""

  def __init__(self):
    self._api = _api
    self.__logger = None
    self.__watcher = None
    self.__build_manager = _build_manager.DefaultBuildManager()

  def set_logger(self, logger):
    """Set logger.

    :param logger: logger object
    :return: ``None``

    Used to set up a logger for the build process. See section :ref:`gen_loggers` for details.
    """
    self.__logger = _shared.wrap_with_exc_handler(logger, _ex.LoggerException)
    self.__build_manager.set_logger(self.__logger)

  def set_watcher(self, watcher):
    """Set watcher.

    :param watcher: watcher object
    :return: ``None``

    Used to set up a watcher for the build process. See section :ref:`gen_watchers` for details.
    """
    self._set_watcher(_shared.wrap_with_exc_handler(watcher, _ex.WatcherException))

  @property
  def options(self):
    """Builder options.

    :type: :class:`~da.p7core.Options`

    General options interface for the builder. See section :ref:`gen_options` for usage and the :ref:`GTApprox option reference <ug_gtapprox_options>`.

    """
    return self.__build_manager.options

  @property
  def license(self):
    """Builder license.

    :type: :class:`~da.p7core.License`

    General license information interface. See section :ref:`gen_license_usage` for details.

    """
    return self.__build_manager.license

  def build(self, x, y, options=None, outputNoiseVariance=None, comment=None, weights=None, initial_model=None, annotations=None, x_meta=None, y_meta=None):
    """Train an approximation model.

    :param x: training sample, input part (values of variables)
    :param y: training sample, response part (function values)
    :param options: option settings
    :param outputNoiseVariance: optional :arg:`y` noise variance, supported by the GP, SGP, HDA, and HDAGP techniques
    :param comment: optional comment added to model :attr:`~da.p7core.gtapprox.Model.info`
    :param weights: optional weights of the training sample points, supported by the RSM, HDA, GP, SGP, HDAGP, iTA, and MoA techniques
    :param initial_model: optional initial model, supported by the GBRT, HDAGP, MoA, and TBL techniques only
    :param annotations: optional extended comment and notes
    :param x_meta: optional input variables information
    :param y_meta: optional output variables information
    :type x: :term:`array-like`, 1D or 2D
    :type y: :term:`array-like`, 1D or 2D
    :type options: ``dict``
    :type outputNoiseVariance: :term:`array-like`, 1D or 2D
    :type comment: ``str``
    :type weights: :term:`array-like`, 1D
    :type initial_model: :class:`~da.p7core.gtapprox.Model`
    :type annotations: ``dict``
    :type x_meta: ``list``
    :type y_meta: ``list``
    :return: trained model
    :rtype: :class:`~da.p7core.gtapprox.Model`

    Train a model using :arg:`x` and :arg:`y` as the training sample.
    1D samples are supported as a simplified form for the case of 1D input and/or response.

    .. versionchanged:: 6.25
       ``pandas.DataFrame`` and ``pandas.Series`` are supported as the :arg:`x`, :arg:`y` training samples.

    If information on the noise level in the response sample :arg:`y` is available, GTApprox accepts it as
    the :arg:`outputNoiseVariance` argument to :meth:`~da.p7core.gtapprox.Builder.build()`. This array should
    specify a noise variance value for each element of the :arg:`y` array (that is, for each response component of every single point).
    Thus :arg:`outputNoiseVariance` has the same shape as :arg:`y`.

    .. versionchanged:: v2024.04
       added the output noise variance support for the HDA technique.

    Output noise variance feature is supported by the following techniques:

    * Gaussian Processes (GP),
    * Sparse Gaussian Processes (SGP),
    * High Dimensional Approximation (HDA), and
    * High Dimensional Approximation combined with Gaussian Processes (HDAGP).

    That is, to use output noise variance meaningfully,
    one of the techniques above has to be selected using :ref:`GTApprox/Technique <GTApprox/Technique>`
    in addition to specifying :arg:`outputNoiseVariance`.
    If any other technique is selected, either manually or automatically,
    the :arg:`outputNoiseVariance` argument is ignored (but see the next note).

    .. note::

       Output noise variance is not compatible with point weighting.
       If both :arg:`outputNoiseVariance` and :arg:`weights` are specified,
       :meth:`~da.p7core.gtapprox.Builder.build()` raises an :exc:`~da.p7core.InvalidProblemError` exception.
       This holds even if you select a technique that does not support output noise variance
       or point weighting and would normally ignore these arguments.

    .. note::

       Output noise variance is not compatible with :ref:`GTApprox/ExactFitRequired <GTApprox/ExactFitRequired>`.
       If :arg:`outputNoiseVariance` is not ``None`` and :ref:`GTApprox/ExactFitRequired <GTApprox/ExactFitRequired>` is on,
       :meth:`~da.p7core.gtapprox.Builder.build()` raises an :exc:`~da.p7core.InvalidOptionsError` exception.

    .. versionchanged // this is just a comment needed to grep the notice below, do not remove it; Sphinx cannot properly render a real versionchanged directive when the version number contains spaces

    *Changed in version 3.0 Release Candidate 1:* elements in :arg:`outputNoiseVariance` can have NaN values in special cases.

    Since 3.0 Release Candidate 1, NaN values can be used in :arg:`outputNoiseVariance` to specify
    that noise variance data is not available. Valid uses are:

    * If noise variance data is not available for some point (a row in :arg:`y`),
      all elements of the corresponding row in :arg:`outputNoiseVariance` should be NaN.
      Note that the row cannot contain any numeric elements in this case.
    * Likewise, if noise variance data is not available for some output component (a column in :arg:`y`),
      the corresponding column in :arg:`outputNoiseVariance` should be filled with NaN values
      and cannot contain any numeric elements.
    * If some element in :arg:`y` is NaN
      (this is valid when :ref:`GTApprox/OutputNanMode<GTApprox/OutputNanMode>` is set to ``"ignore"`` or ``"predict"``),
      the corresponding element in :arg:`outputNoiseVariance` should be NaN.
      A numeric noise value in this case is not an error, but it will be ignored by GTApprox.

    .. versionchanged:: 1.9.5
       added the :arg:`weights` parameter.

    .. versionchanged:: 5.0
       added weights support to the LR, RSM, HDA, GP, SGP, HDAGP, and MoA techniques (previously was available in the iTA technique only).

    .. versionchanged:: 5.0
       point weight is no longer limited to range `[0, 1]` and can be an arbitrary non-negative floating point value or infinity.

    .. versionchanged:: 5.2
       infinite weights are no longer allowed for numerical stability.

    A number of GTApprox techniques support sample point weighting.
    Roughly, point weight is a relative confidence characteristic for this point
    which affects the model fit to the training sample.
    The model will try to fit the points with greater weights better,
    possibly at the cost of decreasing accuracy for the points with lesser weights.
    The points with zero weight may be completely ignored when fitting the model.

    Point weighting is supported in the following techniques:

    * Response Surface Model (RSM).
    * High Dimensional Approximation (HDA).
    * Gaussian Processes (GP).
    * Sparse Gaussian Processes (SGP).
    * High Dimensional Approximation + Gaussian Processes (HDAGP).
    * incomplete Tensor Approximation (iTA).
    * Mixture of Approximators (MoA).

    That is, to use point weights meaningfully,
    one of the techniques above has to be selected using :ref:`GTApprox/Technique<GTApprox/Technique>`
    in addition to specifying :arg:`weights`.
    If any other technique is selected, either manually or automatically,
    :arg:`weights` are ignored (but see the next note).

    .. note::

       Point weighting is not compatible with :ref:`GTApprox/ExactFitRequired <GTApprox/ExactFitRequired>`.
       If :arg:`weights` is not ``None`` and :ref:`GTApprox/ExactFitRequired <GTApprox/ExactFitRequired>` is on,
       :meth:`~da.p7core.gtapprox.Builder.build()` raises an :exc:`~da.p7core.InvalidOptionsError` exception.

    Point weight is an arbitrary non-negative numeric ``float`` value.
    This value has no specific meaning,
    it simply notes the relative "importance" of a point compared to other points in the training sample.

    The :arg:`weights` argument should be a 1D array of point weights,
    and its length has to be equal to the number of training sample points.

    .. note::

       At least one weight has to be non-zero.
       If :arg:`weights` contains only zero values,
       :meth:`~da.p7core.gtapprox.Builder.build()` raises an :exc:`~da.p7core.InvalidProblemError` exception.

    .. note::

       Point weighting is not compatible with output noise variance.
       If both :arg:`outputNoiseVariance` and :arg:`weights` are specified,
       :meth:`~da.p7core.gtapprox.Builder.build()` raises an :exc:`~da.p7core.InvalidProblemError` exception.
       This holds even if you select a technique that does not support output noise variance
       or point weighting and would normally ignore these arguments.

    .. versionchanged:: 5.3
       added the incremental training (model update) support for GBRT models.

    .. versionchanged:: 6.14
       added the initial HDA model support for the HDAGP technique.

    .. versionchanged:: 6.15.1
       added the initial model support for the MoA technique.

    .. versionchanged:: 6.25
       added the incremental training (model update) support for TBL models.

    .. versionchanged:: 6.47
       added the incremental training (model update) support for GP models.

    .. versionchanged:: 6.47
       if you specify :arg:`initial_model` and manually select a technique that does not support model update, :meth:`~da.p7core.gtapprox.Builder.build()` raises an :exc:`~da.p7core.InapplicableTechniqueException`; in earlier versions, the initial model could be ignored in such cases.

    .. versionchanged:: v2024.05
       the GP technique can use HDAGP initial models, and vice versa.

    A GP model can be updated with new data by specifying the existing GP model
    as :arg:`initial_model` and either selecting the GP technique manually
    or enabling the automatic technique selection
    (see :ref:`GTApprox/Technique <GTApprox/Technique>`).
    You can also train a GP model with an initial HDAGP model ---
    for that, you will have to specify the GP technique manually.

    An existing GBRT model, similarly, can be updated with new data
    by specifying it as :arg:`initial_model` and
    selecting the GBRT technique or enabling the automatic technique selection.

    An existing HDAGP model can be updated in the same way as the above.
    You can also train a HDAGP model with an initial GP model
    (specify the HDAGP technique manually).

    Also with the HDAGP technique, you can add an existing HDA model as :arg:`initial_model`
    to use that as a trend, which provides noticeable savings in training time.
    In this case, the HDAGP training sample must be the same one that was used to train the HDA model,
    otherwise the new HDAGP model will be very inaccurate.
    The intent in this case is to speed up the HDAGP model training by skipping the initial step of
    training a trend model internally.

    The MoA technique can use a model trained by any technique as the initial one.
    MoA can improve model accuracy, update the model with new data, or do both.
    See section :ref:`moa_initial_model` for more information.

    The TBL technique can use an existing TBL model as the initial one.
    This technique simply updates the model's internal table with new input-output pairs
    from the training sample.

    Other techniques do not support initial models and raise an exception if
    explicitly selected --- for example, if you set
    :ref:`GTApprox/Technique <GTApprox/Technique>` to ``"RSM"`` and specify :arg:`initial_model`,
    :meth:`~da.p7core.gtapprox.Builder.build()` raises an :exc:`~da.p7core.InapplicableTechniqueException`.

    The MoA technique does not impose any specific limitations on initial models.
    For GBRT, GP, HDAGP, and TBL, if the :arg:`initial_model` does not match the selected technique,
    :meth:`~da.p7core.gtapprox.Builder.build()` raises an exception ---
    for example, if you specify the HDAGP technique but :arg:`initial_model` is not a HDA model.
    Also note the following limitations:

    * If you have trained an GBRT or HDA model with output transformation enabled,
      and you are using that model as an initial one, you must set the
      :ref:`GTApprox/OutputTransformation <GTApprox/OutputTransformation>` option
      when updating the model, as explained in that option description.
    * When updating a GP model, you must get the
      :ref:`GTApprox/GPType <GTApprox/GPType>` and :ref:`GTApprox/GPPower <GTApprox/GPPower>`
      option values from from the initial model :attr:`~da.p7core.gtapprox.Model.details`
      and set those options to the same values in :meth:`~da.p7core.gtapprox.Builder.build()`.
      Additionally, the :ref:`GTApprox/GPInteractionCardinality <GTApprox/GPInteractionCardinality>`
      must be set to ``[]`` or to the value from the initial model.
    * Model update is not supported for GP models with the following features:

      * Model trained with heteroscedastic noise processing
        (:ref:`GTApprox/Heteroscedastic <GTApprox/Heteroscedastic>` set to ``True``).
      * Models with categorical inputs.

    * GP model update is not compatible with point weighting: if :arg:`initial_model`
      is a GP model, and you specify :arg:`weights`,
      :meth:`~da.p7core.gtapprox.Builder.build()` raises an exception.

    .. versionchanged:: 6.14
       added the :arg:`annotations`, :arg:`x_meta`, and :arg:`y_meta` parameters.

    .. versionchanged:: 6.16
       the :arg:`x_meta` parameter can specify input constraints.

    .. versionchanged:: 6.17
       the :arg:`y_meta` parameter can specify output thresholds.

    .. versionchanged:: 6.17
       training reuses the metainformation from an initial model.

    The :arg:`annotations` dictionary adds optional notes or extended comments to model.
    It can contain any number of notes, all keys and values must be strings.
    The :arg:`x_meta` and :arg:`y_meta` parameters provide additional details on model inputs and outputs
    (constraints, names, descriptions, and other) --- see :ref:`ug_gtapprox_details_model_metainfo` for details.
    Note that if you use an initial model that already contains metainformation,
    this metainformation is copied to the trained model.
    In this case, :arg:`x_meta` and :arg:`y_meta` can be used to edit metainformation:
    information specified in :arg:`x_meta`, :arg:`y_meta` overwrites the initial metainformation,
    while information not specified in the arguments is copied from the initial metainformation.

    """
    with _shared.sigint_watcher(self):
      return self._do_build(x, y, options, outputNoiseVariance, comment, weights, initial_model, annotations, x_meta, y_meta)

  def _do_build(self, x, y, options, outputNoiseVariance, comment, weights, initial_model, annotations, x_meta, y_meta):
    time_start = datetime.now()

    # save original logger, watcher and options
    saved_loggers = (self.__logger, self.__build_manager.get_logger())
    saved_watchers = (self.__watcher, self.__build_manager.get_watcher())
    saved_options = self.options.values
    saved_is_batch = None

    try:
      if options is not None:
        _shared.check_concept_dict(options, 'options')
        self.options.set(options)

      quick_dry_run = (_utilities._parse_dry_run(self.options) == 'quick')

      if quick_dry_run:
        self.set_logger(None)

      self.options.set("//Service/SmartSelection", False)

      iv_requested = _shared.parse_bool(self.options.get('GTApprox/InternalValidation'))

      initial_options = dict(self.options.values)
      requested_technique = self.options.get('GTApprox/Technique').lower()

      if iv_requested and requested_technique != 'tbl' and self.options.get("GTApprox/InputDomainType").lower() != 'unbound':
        self.options.set("GTApprox/IVSavePredictions", True) # we have to store IV predictions to calculate IV statistics w.r.t limited domain

      log_level = loggers.LogLevel.from_string(self.options.get('GTApprox/LogLevel').lower())
      tee_logger = _shared.TeeLogger(self.__logger, log_level, collect_issues=True)
      self.set_logger(tee_logger)
      # now level is handled by the tee logger
      if tee_logger.private_log_level != log_level:
        self.options.set('GTApprox/LogLevel', str(tee_logger.private_log_level))

      self._print_sysinfo(time_start)
      self._print_options(options=initial_options, initial_model=initial_model)

      # save and clear store dataset option
      store_dataset = _shared.parse_auto_bool(self.options.get('GTApprox/StoreTrainingSample'), False)
      if store_dataset:
        self.options.set('GTApprox/StoreTrainingSample')

      self.options.set('//GT/ExternalTrainDriverIsWorking', True)

      metainfo_template = _shared.create_metainfo_template(x, y, model=initial_model, options=dict(self.options.values), log=self.__logger)
      categorical_inputs_map, categorical_outputs_map = _shared.read_categorical_maps(metainfo_template)

      if categorical_inputs_map:
        x = _shared.encode_categorical_values(x, categorical_inputs_map, 'input', log=self.__logger)
        self.options.set("GTApprox/CategoricalVariables", sorted([i for i in categorical_inputs_map]))
        self.options.set("//GTApprox/CategoricalVariablesMap", _shared.encode_categorical_map(categorical_inputs_map))

      if categorical_outputs_map:
        y = _shared.encode_categorical_values(y, categorical_outputs_map, 'output', log=self.__logger)
        self.options.set("GTApprox/CategoricalOutputs", sorted([i for i in categorical_outputs_map]))
        self.options.set("//GTApprox/CategoricalOutputsMap", _shared.encode_categorical_map(categorical_outputs_map))

      x, y, outputNoiseVariance, comment, weights, initial_model = self._preprocess_parameters(x, y, outputNoiseVariance, comment, weights, initial_model)
      metainfo = _shared.preprocess_metainfo(x_meta, y_meta, x.shape[1], y.shape[1], template=metainfo_template)
      warn_constraints_violation = self._setup_y_limits(final_metainfo=metainfo, explicit_metainfo=y_meta, y=y)

      class _local_options(object):
        def __init__(self, options):
          self.__options = options
          self.__values = dict(options.values)

        def revert(self):
          self.__options.reset()
          self.__options.set(self.__values)

      has_mixed_nan = _utilities.get_nan_structure(y)[1]
      componentwise_mode, dep_outputs_mode = self._componentwise_train([] if has_mixed_nan else ['splt', 'ta', 'rsm', 'ita', 'pla', 'tbl'],
                                                                       x.shape[1], y.shape[1], categorical_inputs_map, categorical_outputs_map, initial_model)
      if not componentwise_mode and has_mixed_nan:
        raise _ex.InvalidProblemError('Output part of the training dataset contains at least one vector with both NaN and finite float elements. Such kind of problem can be solved in a \'componentwise\' mode only. Please, consider setting GTApprox/DependentOutputs=False.')

      technique_selector = _technique_selection.TechniqueSelector(self.options, tee_logger)
      updated_technique_name = technique_selector.preprocess_sample(x, y, outputNoiseVariance, weights, componentwise_mode, self.__build_manager, initial_model=initial_model)
      self.options.set('GTApprox/Technique', updated_technique_name)

      try:
        saved_is_batch = self.__build_manager.is_batch
        time_limit = int(self.options.get("/GTApprox/TimeLimit"))
        all_outputs_categorical = np.all([i in categorical_outputs_map for i in np.arange(y.shape[1])])
        self.__build_manager.setup_batch_mode(self._read_batch_mode(technique_selector, componentwise_mode, time_limit > 0, all_outputs_categorical))
      except:
        # Build manager does not support dynamic batch mode
        saved_is_batch = None

      outputs_analysis = None
      if dep_outputs_mode == "partiallinear":
        y_name = [_['name'] for _ in metainfo['Output Variables']]

        training_outputs, evaluation_model, constraints = self._read_model_linear_dependencies(model=initial_model)
        if evaluation_model is not None:
          self._report_linear_dependencies(explanatory_outputs=training_outputs, evaluation_model=evaluation_model, constraints=constraints, y=y, y_name=y_name)

        if evaluation_model is None:
          training_outputs, evaluation_model, constraints = find_linear_dependencies(y=y, rrms_threshold=float(self.options.get("/GTApprox/PartialDependentOutputs/RRMSThreshold"))
                                                                                    , log=self.__logger, weights=weights, y_name=y_name
                                                                                    , seed=int(self.options.get("GTApprox/Seed")), nan_mode=self.options.get("GTApprox/OutputNanMode")
                                                                                    , mapping=self.options.get("/GTApprox/PartialDependentOutputs/Mapping")
                                                                                    , search_groups=_shared.parse_json(self.options.get("/GTApprox/DependentOutputsSearchGroups")))

        if evaluation_model is not None:
          outputs_analysis = {"explanatory_variables": [_ for _ in training_outputs],
                              "evaluation_model": evaluation_model,
                              "constraints": constraints}
          self.options.set('//Service/PartialLinearOutputs', True)
          initial_options['//Service/PartialLinearOutputs'] = True # make it global

        del evaluation_model, constraints

      technique_selector, componentwise_mode, training_outputs = self._postprocess_training_outputs(y.shape[1], technique_selector, componentwise_mode,
                                                                                                    (None if outputs_analysis is None else training_outputs))
      initial_models = self._split_initial_model_outputs(initial_model, training_outputs)

      componentwise_models_spec = []
      componentwise_options = _local_options(self.options)

      self.__watcher = _shared.TrainingPhasesWatcher(self.__watcher)
      self.__build_manager.set_watcher(self.__watcher)

      for output_index, actual_initial_model in zip(training_outputs, initial_models):
        actual_y = y if output_index is None else y[:, output_index].reshape(y.shape[0], -1)
        actualOutputNoiseVariance = None if outputNoiseVariance is None else outputNoiseVariance if output_index is None else outputNoiseVariance[:, output_index].reshape(outputNoiseVariance.shape[0], -1)

        if output_index is not None:
          self.options.set(self.options._values(output_index))
          if not componentwise_mode:
            output_index = None # output_index may be None or a list of outputs of interest

        prefix = self._postprocess_comment(output_index, None, metainfo)

        if output_index is not None:
          self.options.set('//ComponentwiseTraining/ActiveOutput', output_index)
          self._log(loggers.LogLevel.INFO, '\nPreprocessing output %s' % metainfo['Output Variables'][output_index]['name'], prefix)

        discrete_classes_data_list, categorical_variables = technique_selector.select(output_column=output_index, initial_model=actual_initial_model, comment=prefix, categorical_outputs_map=categorical_outputs_map)

        if categorical_variables and requested_technique in ['auto', 'rsm'] and len(discrete_classes_data_list) > 1 \
          and all(data.get('technique', 'auto').lower() in ['rsm', 'tbl'] for data in discrete_classes_data_list):
          self._log(loggers.LogLevel.INFO, '\nAll proposed techniques are %s. Switching to RSM with binarized categorical variables.\n' % \
                          ' or '.join(_ for _ in ['RSM', 'TBL'] if any(_.lower() == data.get('technique', 'auto').lower() for data in discrete_classes_data_list)), prefix)

          try:
            self.options.set('GTApprox/Technique', 'RSM')
            rsm_technique_selector = _technique_selection.TechniqueSelector(self.options, tee_logger)
            rsm_updated_technique_name = rsm_technique_selector.preprocess_sample(x, actual_y, actualOutputNoiseVariance, weights, False, self.__build_manager, prefix)
            self.options.set('GTApprox/Technique', rsm_updated_technique_name)
            discrete_classes_data_list, categorical_variables = rsm_technique_selector.select(None, initial_model=actual_initial_model, comment=prefix)
          except Exception:
            e = sys.exc_info()[1]
            self._log(loggers.LogLevel.INFO, '\nFailed to switch to RSM with binarized categorical variables: %s\n' % _shared._safestr(e).strip(), prefix)
          finally:
            rsm_technique_selector = None
            del rsm_technique_selector

        elif categorical_variables and all(i in categorical_outputs_map for i in (np.arange(actual_y.shape[1]) if output_index is None else [output_index])) \
          and len(discrete_classes_data_list) > 1 and all(data.get('technique', 'auto').lower() == 'gbrt' for data in discrete_classes_data_list):
          self._log(loggers.LogLevel.INFO, '\nAll outputs are categorical and all proposed techniques are GBRT. Switching to GBRT with binarized categorical variables.\n', prefix)

          try:
            self.options.set('GTApprox/Technique', 'GBRT')
            gbrt_technique_selector = _technique_selection.TechniqueSelector(self.options, tee_logger)
            gbrt_updated_technique_name = gbrt_technique_selector.preprocess_sample(x, actual_y, actualOutputNoiseVariance, weights, False, self.__build_manager, prefix, initial_model=initial_model)
            self.options.set('GTApprox/Technique', gbrt_updated_technique_name)
            gbrt_categorical_outputs_map = categorical_outputs_map if output_index is None else {0: categorical_outputs_map[output_index]}
            discrete_classes_data_list, categorical_variables = gbrt_technique_selector.select(None, initial_model=actual_initial_model, comment=prefix, categorical_outputs_map=gbrt_categorical_outputs_map)
          except Exception:
            e = sys.exc_info()[1]
            self._log(loggers.LogLevel.INFO, '\nFailed to switch to GBRT with binarized categorical variables: %s\n' % _shared._safestr(e).strip(), prefix)
          finally:
            gbrt_technique_selector = None
            del gbrt_technique_selector

        if not categorical_variables:
          # no categorical variables are given
          assert len(discrete_classes_data_list) == 1
          data = discrete_classes_data_list[0]
          data_comment = self._postprocess_comment(output_index, data.get('comment'), metainfo)
          self.options.set(data.get('options', {}))
          self.options.set('GTApprox/Technique', data['technique'])
          self.options.set('GTApprox/OutputTransformation', self._select_output_transform(data['x'], data['y'],
                           self.options.values, data.get('tol'), data.get('weights'), data.get('initial_model'),
                           comment=data_comment))
          data_id_list = ['output%04d' % (0 if output_index is None else output_index)]
          self._submit(data, data_id_list[-1], data_id_list[-1], comment=data_comment)
          componentwise_models_spec.append({'type': 'standalone', 'output_index': output_index, 'data_id': data_id_list,
                                            'restricted_x': data.get('restricted_x'), 'valid_x': data.get('x')})
        else:
          # Clear categorical variables specification to avoid building of single-categoria models, but keep encoded variables (hence still categorical) for information.
          # This option does not affect inputs encoding - all encoded inputs automatically set categorical in the model built.
          encoded_variables = [_ for _ in _shared.parse_json(self.options.get('GTApprox/CategoricalVariables')) if _ not in categorical_variables]
          self.options.set('GTApprox/CategoricalVariables', encoded_variables)

          # service option indicating composite model is building
          self.options.set('//Service/BuildingCompositeModel', True)

          discrete_class_options = _local_options(self.options)
          data_id_list = []
          cat_data_description = {}
          valid_x, restricted_x = [], []
          for cat_class_id, data in enumerate(discrete_classes_data_list):
            if data.get('x') is not None:
              valid_x.append(data.get('x'))
            if data.get('restricted_x') is not None:
              restricted_x.append(data.get('restricted_x'))
            data_comment = self._postprocess_comment(output_index, data.get('comment'), metainfo)
            self.options.set(data.get('options', {}))
            self.options.set('GTApprox/Technique', data['technique'])
            self.options.set('GTApprox/OutputTransformation', self._select_output_transform(data['x'], data['y'],
                             self.options.values, data.get('tol'), data.get('weights'), data.get('initial_model'),
                             comment=data_comment))
            data_id_list.append('output%04d_catclass%04d' % ((0 if output_index is None else output_index), cat_class_id))
            cat_data_description[data_id_list[-1]] = data.get('comment', "")
            self._submit(data, data_id_list[-1], data_id_list[-1], comment=data_comment)
            discrete_class_options.revert()

          current_sample = {'x': x, 'f': actual_y}
          if weights is not None:
            current_sample['weights'] = weights
          if outputNoiseVariance is not None:
            current_sample['tol'] = actualOutputNoiseVariance

          componentwise_models_spec.append({  'type': 'categorical'
                                            , 'output_index': output_index
                                            , 'sample': current_sample
                                            , 'data_id': data_id_list
                                            , 'cat_data_description': cat_data_description
                                            , 'categorical_variables': categorical_variables
                                            , 'classes_number': len(discrete_classes_data_list)
                                            , 'comment': self._postprocess_comment(output_index, None, metainfo)
                                            , 'restricted_x': np.vstack(restricted_x) if restricted_x else None
                                            , 'valid_x': np.vstack(valid_x) if restricted_x else None
                                            , 'output_spec': '' if output_index is None else (' of output #%d' % output_index)})

        n_iv_training = discrete_classes_data_list[0].get('options', {}).get('GTApprox/IVTrainingCount', 0)
        n_tensor_factors = len(_shared.parse_json(discrete_classes_data_list[0].get('options', {}).get('//Service/CartesianStructure')))
        self.__watcher.add_phases(n_outputs=1,
                                  n_discrete_classes=len(discrete_classes_data_list),
                                  n_iv_training=iv_requested * n_iv_training,
                                  n_tensor_factors=n_tensor_factors - len(categorical_variables))

        componentwise_options.revert()

      models_dict = self.__build_manager.get_models()
      for data_id in models_dict:
        models_dict[data_id] = models_dict[data_id][data_id]
      if any(model is None for model in models_dict.values()):
        raise _ex.UserTerminated()

      componentwise_models = []
      final_model_decomposition = []

      for model_batch in componentwise_models_spec:
        output_index = model_batch['output_index']
        if 'standalone' == model_batch['type']:
          componentwise_models.append(models_dict.get(model_batch['data_id'][-1], None))
          final_model_decomposition.append(('standalone', self._read_build_details(componentwise_models[-1])))
        elif 'categorical' == model_batch['type']:
          if output_index is not None:
            cat_initial_options = dict((key, initial_options[key]) for key in initial_options)
            cat_initial_options['//ComponentwiseTraining/ActiveOutput'] = output_index
          else:
            cat_initial_options = initial_options

          prefix = self._postprocess_comment(output_index, model_batch.get('comment'), metainfo)
          self._log(loggers.LogLevel.INFO, "\nMerging models%s built for different categorical variables combinations..." % model_batch['output_spec'], prefix)
          categorical_models = [models_dict.get(data_id, None) for data_id in model_batch['data_id']]
          cat_data_description = model_batch.get("cat_data_description", {})
          final_model_decomposition.append(('categorical', [self._read_build_details(cat_model, cat_data_description.get(cat_id)) for cat_model, cat_id in zip(categorical_models, model_batch['data_id'])]))
          componentwise_models.append(_utilities.Utilities.join_categorical_models(categorical_models, model_batch['categorical_variables'],
                                                                                   model_batch['sample'], model_batch['comment'],
                                                                                   cat_initial_options, self.__logger))
        else:
          # paranoiac assertion
          assert False, 'Unknown model type %s' % model_batch['type']

        self._restrict_validity_domain(componentwise_models[-1], model_batch.get('valid_x'), model_batch.get('restricted_x'), self.__logger)

      if not componentwise_mode and outputs_analysis is None:
        model = componentwise_models[0]
      else:
        if 1 != len(componentwise_models):
          self._log(loggers.LogLevel.INFO, "\nMerging models built for different outputs...")

        training_dataset = {'x': x, 'f': y}
        if weights is not None:
          training_dataset['weights'] = weights
        if outputNoiseVariance is not None:
          training_dataset['tol'] = outputNoiseVariance

        if outputs_analysis is not None:
          training_dataset['linear_dependencies'] = outputs_analysis

        model = _utilities.Utilities.join_componentwise_models(componentwise_models, training_dataset, "", initial_options, self.__logger, metainfo=metainfo)

      initial_options = self._postprocess_output_transform(model, initial_options, {})
      self._postprocess_domains(model, x, initial_options, metainfo, initial_model)

      if not quick_dry_run:
        self._postprocess_model_train_dataset(model=model, options=initial_options,
                                              dataset={'x': x, 'y': y, 'tol': outputNoiseVariance, 'w': weights, 'store': store_dataset},
                                              warn_always=warn_constraints_violation)
        self._report_model_decomposition(final_model_decomposition, outputs_analysis, metainfo)

      metainfo = self._postprocess_metainfo(model=model, metainfo=metainfo, known_issues=_safe_read_attr(tee_logger, "issues", {}))
      metainfo = self._report_train_finished(model=model, time_start=time_start, metainfo=metainfo)

      return self._postprocess_model(model, _safe_read_attr(tee_logger, "log_value", ""), initial_options, initial_model,
                                      None, self.__logger, comment=comment, annotations=annotations, metainfo=metainfo)

    finally:
      # cleanup queued jobs (in case there was an exception) and data
      self.__build_manager.clean_data()
      self.__build_manager.reset_workdir()

      # restore original logger
      self.__logger = saved_loggers[0]
      self.__build_manager.set_logger(saved_loggers[1])

      # restore original watcher
      self.__watcher = saved_watchers[0]
      self.__build_manager.set_watcher(saved_watchers[1])

      if saved_is_batch is not None:
        self.__build_manager.setup_batch_mode(saved_is_batch)

      # restore original options
      self.options.reset()
      self.options.set(saved_options)

  def build_smart(self, x, y, options=None, outputNoiseVariance=None, comment=None, weights=None, initial_model=None,
                  hints=None, x_test=None, y_test=None, annotations=None, x_meta=None, y_meta=None):
    """Train an approximation model using smart training.

    :param x: training sample, input part (values of variables)
    :param y: training sample, response part (function values)
    :param options: option settings which will be set fixed during parameter search
    :param outputNoiseVariance: optional :arg:`y` noise variance
    :param comment: text comment
    :param weights: training sample point weights
    :param initial_model: initial model for incremental training
    :param hints: user-provided hints on the data behaviour and desirable model properties
    :param x_test: testing sample, input part (values of variables)
    :param y_test: testing sample, response part (function values)
    :param annotations: extended comment and notes
    :param x_meta: descriptions of inputs
    :param y_meta: descriptions of outputs
    :type x: :term:`array-like`, 1D or 2D
    :type y: :term:`array-like`, 1D or 2D
    :type options: ``dict``
    :type hints: ``dict``
    :type x_test: :term:`array-like`, 1D or 2D
    :type y_test: :term:`array-like`, 1D or 2D
    :type outputNoiseVariance: :term:`array-like`, 1D or 2D
    :type comment: ``str``
    :type weights: :term:`array-like`, 1D
    :type initial_model: :class:`~da.p7core.gtapprox.Model`
    :type annotations: ``dict``
    :type x_meta: ``list``
    :type y_meta: ``list``
    :return: trained model
    :rtype: :class:`~da.p7core.gtapprox.Model`

    .. versionadded:: 6.6

    .. versionchanged:: 6.14
       added the :arg:`annotations`, :arg:`x_meta`, and :arg:`y_meta` parameters.

    .. versionchanged:: 6.25
       ``pandas.DataFrame`` and ``pandas.Series`` are supported as the :arg:`x`, :arg:`y` training samples.

    Train a model with :arg:`x` and :arg:`y` as the training sample using the smart training procedure.
    Arguments are the same as :meth:`~da.p7core.gtapprox.Builder.build()`,
    with 3 additional arguments: :arg:`hints`, :arg:`x_test` and :arg:`y_test`.

    * :arg:`hints`:
      additional information about the data set or requirements to the model,
      and optional smart training settings.
      See section :ref:`ug_gtapprox_hints` for details.
    * :arg:`x_test` and :arg:`y_test`:
      test samples which can be used to control model quality during training.

    See section :ref:`ug_gtapprox_smart_training` for details on smart training.

    """
    with _shared.sigint_watcher(self):
      return self._do_build_smart(x, y, options, outputNoiseVariance, comment, weights, initial_model, hints, x_test, y_test, annotations, x_meta, y_meta)

  def _do_build_smart(self, x, y, options=None, outputNoiseVariance=None, comment=None, weights=None, initial_model=None,
                      hints=None, x_test=None, y_test=None, annotations=None, x_meta=None, y_meta=None):
    time_start = datetime.now()
    if hints is not None:
      _shared.check_concept_dict(hints, 'hints')

    # save original logger, watcher and options
    saved_loggers = (self.__logger, self.__build_manager.get_logger())
    saved_watchers = (self.__watcher, self.__build_manager.get_watcher())
    saved_options = self.options.values
    saved_is_batch = None

    try:
      if options is not None:
        _shared.check_concept_dict(options, 'options')
        self.options.set(options)

      quick_dry_run = (_utilities._parse_dry_run(self.options) == 'quick')

      if quick_dry_run:
        self.set_logger(None)

      self.options.set("//Service/SmartSelection", True)

      iv_requested = _shared.parse_bool(self.options.get('GTApprox/InternalValidation'))

      initial_options = dict(self.options.values)
      requested_technique = self.options.get('GTApprox/Technique').lower()

      if iv_requested and requested_technique != 'tbl' and self.options.get("GTApprox/InputDomainType").lower() != 'unbound':
        self.options.set("GTApprox/IVSavePredictions", True) # we have to store IV predictions to calculate IV statistics w.r.t limited domain

      log_level = loggers.LogLevel.from_string(self.options.get('GTApprox/LogLevel').lower())
      tee_logger = _shared.TeeLogger(self.__logger, log_level, collect_issues=True)
      self.set_logger(tee_logger)
      # now level is handled by the tee logger
      if tee_logger.private_log_level != log_level:
        self.options.set('GTApprox/LogLevel', str(tee_logger.private_log_level))

      self._print_sysinfo(time_start)
      self._print_options(options=initial_options, initial_model=initial_model)

      # save and clear store dataset option
      store_dataset = _shared.parse_auto_bool(self.options.get('GTApprox/StoreTrainingSample'), False)
      if store_dataset:
        self.options.set('GTApprox/StoreTrainingSample')

      self.options.set('//GT/ExternalTrainDriverIsWorking', True)

      metainfo_template = _shared.create_metainfo_template(x, y, model=initial_model, options=dict(self.options.values), log=self.__logger)
      categorical_inputs_map, categorical_outputs_map = _shared.read_categorical_maps(metainfo_template)

      if categorical_inputs_map:
        x = _shared.encode_categorical_values(x, categorical_inputs_map, 'input', log=self.__logger)
        self.options.set("GTApprox/CategoricalVariables", sorted([i for i in categorical_inputs_map]))
        self.options.set("//GTApprox/CategoricalVariablesMap", _shared.write_json(categorical_inputs_map))

      if categorical_outputs_map:
        y = _shared.encode_categorical_values(y, categorical_outputs_map, 'output', log=self.__logger)
        self.options.set("GTApprox/CategoricalOutputs", sorted([i for i in categorical_outputs_map]))

      x, y, outputNoiseVariance, comment, weights, initial_model = self._preprocess_parameters(x, y, outputNoiseVariance, comment, weights, initial_model)
      metainfo = _shared.preprocess_metainfo(x_meta, y_meta, x.shape[1], y.shape[1], template=metainfo_template)
      warn_constraints_violation = self._setup_y_limits(final_metainfo=metainfo, explicit_metainfo=y_meta, y=y)

      class _local_options(object):
        def __init__(self, options):
          self.__options = options
          self.__values = dict(options.values)

        def revert(self):
          self.__options.reset()
          self.__options.set(self.__values)

      class _local_time_limit(object):
        def __init__(self, time_limit):
          self.__limits = [(time_limit, None,)]

        @property
        def limited(self):
          return self.__limits[0][0] > 0

        def push(self, time_limit, denominator):
          self.__limits.append((0, None,) if not time_limit else (max(1, float(time_limit) / denominator), time.time() + time_limit,))

        def pop(self):
          self.__limits.pop()

        def current_limit(self, denominator):
          min_time_limit, curr_eta = self.__limits[-1]
          if not min_time_limit or curr_eta is None:
            return min_time_limit
          return max(1, min_time_limit, (curr_eta - time.time()) / denominator)

        def updated_hints(self, hints, denominator):
          new_limit = self.current_limit(denominator)
          if not hints or not new_limit:
            return hints

          hints = dict(hints)
          hints['@GTApprox/TimeLimit'] = int(new_limit + .5)
          return hints

      initial_hints = dict(hints) if hints is not None else {}

      if hints:
        self._log(loggers.LogLevel.INFO, 'The following hints are specified:')
        for hint in hints:
          self._log(loggers.LogLevel.INFO, '  %s: %s' % (hint, hints[hint]))
        self._log(loggers.LogLevel.INFO, ' ')

        # convert hints to options and validate hints vs options
        _, hints_as_options, variable_options, accelerator_options = _get_default_hints_options(hints, self._log, explicit_user_options=initial_options)
        allowed_techniques = [_.lower() for _ in variable_options.get('GTApprox/Technique', {}).get('bounds', [])];
        if len(allowed_techniques) == 1 and self.options.get('GTApprox/Technique').lower() == 'auto':
          self.options.set('GTApprox/Technique', allowed_techniques[0])

        # read time limit requested
        timelimit = _local_time_limit(accelerator_options.get('TimeLimit', 0))

        if hints_as_options:
          self._log(loggers.LogLevel.INFO, 'Hints have been converted to the following options:')
          for option in hints_as_options:
            self._log(loggers.LogLevel.INFO, '  %s: %s' % (option, hints_as_options[option]))
          self._log(loggers.LogLevel.INFO, ' ')

        initial_options_names = [_.lower() for _ in initial_options]
        for option, value in _six.iteritems(hints_as_options):
          initial_value = None
          if option.lower() in initial_options_names:
            initial_value = self.options.get(option)
          self.options.set(option, value)
          # It's a little bit complicated check
          if initial_value is not None:
            actual_value = self.options.get(option)
            if actual_value != initial_value:
              raise _ex.InvalidOptionsError('The \'%s\' option value given differs from the hint based value: %s != %s' % (option, initial_value, actual_value))
      else:
        timelimit = _local_time_limit(0)
        accelerator_options, allowed_techniques = {}, []

      has_mixed_nan = _utilities.get_nan_structure(y)[1]
      try_output_transforms = _shared.parse_bool(accelerator_options.get("TryOutputTransformations", False))
      componentwise_mode, dep_outputs_mode = self._componentwise_train([] if (has_mixed_nan or try_output_transforms) else ['splt', 'ta', 'rsm', 'ita', 'pla', 'tbl'],
                                                                       x.shape[1], y.shape[1], categorical_inputs_map, categorical_outputs_map, initial_model)

      if not componentwise_mode and has_mixed_nan:
        raise _ex.InvalidProblemError('Output part of the training dataset contains at least one vector with both NaN and finite float elements. Such kind of problem can be solved in a \'componentwise\' mode only. Please, consider setting GTApprox/DependentOutputs=False.')

      technique_selector = _technique_selection.TechniqueSelector(self.options, tee_logger)
      default_technique = technique_selector.preprocess_sample(x, y, outputNoiseVariance, weights, componentwise_mode, self.__build_manager, technique_list=allowed_techniques, initial_model=initial_model)
      self.options.set('GTApprox/Technique', default_technique)

      # validate test sample - now we know whether we should preserve or keep nan's
      x_test, y_test, w_test = self._preprocess_test_sample(x.shape[1], y.shape[1], x_test, y_test, None,
                                                            self._read_x_nan_mode(self.options.get("GTApprox/InputNanMode"), (default_technique.lower() == "gbrt")),
                                                            None, self._log)
      has_test_sample = x_test is not None and y_test is not None

      try:
        saved_is_batch = self.__build_manager.is_batch
        all_outputs_categorical = np.all([i in categorical_outputs_map for i in np.arange(y.shape[1])])
        self.__build_manager.setup_batch_mode(self._read_batch_mode(technique_selector, componentwise_mode, timelimit.limited, all_outputs_categorical))
      except:
        # Build manager does not support dynamic batch mode
        saved_is_batch = None

      outputs_analysis = None
      if dep_outputs_mode == "partiallinear":
        y_name = [_['name'] for _ in metainfo['Output Variables']]

        training_outputs, evaluation_model, constraints = self._read_model_linear_dependencies(model=initial_model)
        if evaluation_model is not None:
          self._report_linear_dependencies(explanatory_outputs=training_outputs, evaluation_model=evaluation_model, constraints=constraints, y=y, y_name=y_name)

        if evaluation_model is None:
          training_outputs, evaluation_model, constraints = find_linear_dependencies(y=y, rrms_threshold=float(self.options.get("/GTApprox/PartialDependentOutputs/RRMSThreshold"))
                                                                                    , log=self.__logger, weights=weights, y_name=y_name
                                                                                    , seed=int(self.options.get("GTApprox/Seed")), nan_mode=self.options.get("GTApprox/OutputNanMode")
                                                                                    , mapping=self.options.get("/GTApprox/PartialDependentOutputs/Mapping")
                                                                                    , search_groups=_shared.parse_json(self.options.get("/GTApprox/DependentOutputsSearchGroups")))

        if evaluation_model is not None:
          outputs_analysis = {"explanatory_variables": [_ for _ in training_outputs],
                              "evaluation_model": evaluation_model,
                              "constraints": constraints}
          self.options.set('//Service/PartialLinearOutputs', True)
          initial_options['//Service/PartialLinearOutputs'] = True  # make it global

        del evaluation_model, constraints

      technique_selector, componentwise_mode, training_outputs = self._postprocess_training_outputs(y.shape[1], technique_selector, componentwise_mode,
                                                                                                    (None if outputs_analysis is None else training_outputs))
      initial_models = self._split_initial_model_outputs(initial_model, training_outputs)

      componentwise_models_spec = []
      componentwise_options = _local_options(self.options)
      models_list = []
      timelimit_denominator = len(training_outputs)
      timelimit.push(timelimit.current_limit(1), timelimit_denominator)

      def _activate_output(output_index):
        if output_index is not None:
          self.options.set(self.options._values(output_index))
          if not componentwise_mode:
            output_index = None # output_index may be None or a list of outputs of interest
        if componentwise_mode:
          self.options.set('//ComponentwiseTraining/ActiveOutput', output_index)
        return output_index

      self.__watcher = _shared.TrainingPhasesWatcher(self.__watcher)
      self.__build_manager.set_watcher(self.__watcher)

      # dry run: check up options compatibility issues before we start any time consuming training
      for output_index, actual_initial_model in zip(training_outputs, initial_models):
        output_index = _activate_output(output_index)
        actual_y = y if output_index is None else y[:, output_index].reshape(y.shape[0], -1)
        try:
          discrete_classes_data_list, categorical_variables = technique_selector.subsets(output_column=output_index, initial_model=actual_initial_model, technique_list=allowed_techniques, categorical_outputs_map=categorical_outputs_map)
        except Exception:
          exc_info = sys.exc_info()
          _shared.reraise(exc_info[0], self._report_technique_failure(exc_info[1], self._postprocess_comment(output_index, comment, metainfo), allowed_techniques), exc_info[2])

        if categorical_variables and all(i in categorical_outputs_map for i in (np.arange(actual_y.shape[1]) if output_index is None else [output_index])) \
          and len(discrete_classes_data_list) > 1 and all(data.get('options', {}).get('GTApprox/CategoricalOutputs') for data in discrete_classes_data_list):

          discrete_class_options = _local_options(self.options)
          try:
            self.options.set('GTApprox/Technique', 'GBRT')
            gbrt_technique_selector = _technique_selection.TechniqueSelector(self.options, None)
            self.options.set('GTApprox/Technique', gbrt_technique_selector.preprocess_sample(x, actual_y, None, None, False, self.__build_manager, initial_model=initial_model))
            gbrt_categorical_outputs_map = categorical_outputs_map if output_index is None else {0: categorical_outputs_map[output_index]}
            discrete_classes_data_list, categorical_variables = gbrt_technique_selector.select(None, initial_model=actual_initial_model, categorical_outputs_map=gbrt_categorical_outputs_map)
          except Exception:
            pass
          finally:
            discrete_class_options.revert()
            gbrt_technique_selector = None
            del gbrt_technique_selector

        elif categorical_variables and len(discrete_classes_data_list) > 1 and requested_technique in ['auto', 'rsm'] and output_index not in categorical_outputs_map:
          rsm_applicable = not allowed_techniques or 'rsm' in allowed_techniques
          discrete_class_options = _local_options(self.options)
          for data in discrete_classes_data_list:
            if data.get('technique', 'auto').lower() not in ['rsm', 'tbl']:
              try:
                self.options.set(data.get('options', {}))
                _technique_selection.check_RSM(data['_sample'], self.options, data.get('initial_model'))
              except:
                rsm_applicable = 0
                break
              finally:
                discrete_class_options.revert()

          if rsm_applicable:
            discrete_class_options = _local_options(self.options)
            try:
              if categorical_outputs_map:
                self.options.set('GTApprox/CategoricalOutputs')

              self.options.set('GTApprox/Technique', 'RSM')
              rsm_technique_selector = _technique_selection.TechniqueSelector(self.options, tee_logger)
              self.options.set('GTApprox/Technique', rsm_technique_selector.preprocess_sample(x, actual_y, None, None, False, self.__build_manager))
              rsm_discrete_classes_data_list, rsm_categorical_variables = rsm_technique_selector.select(None, initial_model=actual_initial_model)

              if not rsm_categorical_variables and rsm_discrete_classes_data_list[0].get('technique', default_technique).lower() in ['tbl', 'rsm']:
                n_iv_training = rsm_discrete_classes_data_list[0].get('options', {}).get('GTApprox/IVTrainingCount', 0)
                n_tensor_factors = len(_shared.parse_json(rsm_discrete_classes_data_list[0].get('options', {}).get('//Service/CartesianStructure')))
                self.__watcher.add_phases(n_outputs=1,
                                          n_discrete_classes=len(rsm_discrete_classes_data_list),
                                          n_iv_training=iv_requested * n_iv_training,
                                          n_tensor_factors=n_tensor_factors - len(rsm_categorical_variables))
            except Exception:
              pass
            finally:
              discrete_class_options.revert()
              rsm_technique_selector = None
              del rsm_technique_selector

        n_iv_training = discrete_classes_data_list[0].get('options', {}).get('GTApprox/IVTrainingCount', 0)
        n_tensor_factors = len(_shared.parse_json(discrete_classes_data_list[0].get('options', {}).get('//Service/CartesianStructure')))
        self.__watcher.add_phases(n_outputs=1,
                                  n_discrete_classes=len(discrete_classes_data_list),
                                  n_iv_training=iv_requested * n_iv_training,
                                  n_tensor_factors=n_tensor_factors - len(categorical_variables))

      for output_index, actual_initial_model in zip(training_outputs, initial_models):
        actual_y = y if output_index is None else y[:, output_index].reshape(y.shape[0], -1)
        actualOutputNoiseVariance = None if outputNoiseVariance is None else outputNoiseVariance if output_index is None else outputNoiseVariance[:, output_index].reshape(outputNoiseVariance.shape[0], -1)
        actual_y_test = None if y_test is None else y_test if output_index is None else y_test[:, output_index].reshape(y_test.shape[0], -1)

        output_index = _activate_output(output_index)
        output_data_id = ("training_output%04d" % output_index) if output_index is not None else "training_sample"
        rsm_model = None

        discrete_classes_data_list, categorical_variables = technique_selector.subsets(output_column=output_index, initial_model=actual_initial_model, technique_list=allowed_techniques, categorical_outputs_map=categorical_outputs_map)

        if categorical_variables and all(i in categorical_outputs_map for i in (np.arange(actual_y.shape[1]) if output_index is None else [output_index])) \
          and len(discrete_classes_data_list) > 1 and all(data.get('options', {}).get('GTApprox/CategoricalOutputs') for data in discrete_classes_data_list):
          # We do not check technique == GBRT since the technique is not provided in subsets mode.
          # TODO For now categorical inputs binarization is the only option for GBRT. Training in alternative mode, like its done with RSM,
          # is not suitable for classification problem with many categorical inputs and to be considered later.

          discrete_class_options = _local_options(self.options)
          try:
            prefix = self._postprocess_comment(output_index, ('binarized x%s' % categorical_variables), metainfo)
            self._log(loggers.LogLevel.INFO, '\nPreprocessing data with binarization of categorical variables.\n', prefix)

            self.options.set('GTApprox/Technique', 'GBRT')
            gbrt_technique_selector = _technique_selection.TechniqueSelector(self.options, tee_logger)
            gbrt_updated_technique_name = gbrt_technique_selector.preprocess_sample(x, actual_y, actualOutputNoiseVariance, weights, False, self.__build_manager, prefix, initial_model=initial_model)
            self.options.set('GTApprox/Technique', gbrt_updated_technique_name)
            gbrt_categorical_outputs_map = categorical_outputs_map if output_index is None else {0: categorical_outputs_map[output_index]}
            discrete_classes_data_list, categorical_variables = gbrt_technique_selector.select(None, initial_model=actual_initial_model, comment=prefix, categorical_outputs_map=gbrt_categorical_outputs_map)
            data = discrete_classes_data_list[0]
            if allowed_techniques and 'technique' in data and data['technique'] not in allowed_techniques:
              del data['technique'] # GBRT will be set at smart selection level if categorical output options are specified
          except Exception:
            e = sys.exc_info()[1]
            self._log(loggers.LogLevel.INFO, '\nFailed to switch to GBRT with binarized categorical variables: %s\n' % _shared._safestr(e).strip(), prefix)
          finally:
            discrete_class_options.revert()
            gbrt_technique_selector = None
            del gbrt_technique_selector

        if not categorical_variables:
          # no categorical variables are given
          assert len(discrete_classes_data_list) == 1
          data = discrete_classes_data_list[0]
          data['x_test'], data['y_test'], data['w_test'] = x_test, actual_y_test, w_test
          self.options.set(data.get('options', {}))

          prefix = self._postprocess_comment(output_index, data.get('comment'), metainfo)
          if prefix:
            self._log(loggers.LogLevel.INFO, '\nProcessing %s\n' % prefix, prefix)

          # We can't set the recommended technique if the list of allowed techniques was specified,
          # these options are mutually exclusive at smart selection level.
          self.options.set('GTApprox/Technique', default_technique if allowed_techniques else data.get('technique', default_technique))

          if 'auto' == self.options.get('GTApprox/Technique').lower():
            self.options.set('GTApprox/Technique')

          if self.options.get('GTApprox/Technique').lower() in ['tbl',]:
            current_model = [self._build_simple(data['x'], data['y'], comment=prefix, initial_model=data.get('initial_model')),]
          else:
            data['original_train_data'] = dict((k, data.get(k)) for k in ('x', 'y', 'tol', 'weights', 'initial_model', 'restricted_x'))
            if output_index is None:
              local_categorical_outputs_map = categorical_outputs_map
            elif output_index in categorical_outputs_map:
              local_categorical_outputs_map = {0: categorical_outputs_map[output_index]}
            else:
              local_categorical_outputs_map = {}
            data = self._optional_split(data, accelerator_options, output_data_id, categorical_inputs_map, local_categorical_outputs_map)
            self.options.set(data.get('options', {})) # options could be modified inside _optional_split

            # Turn off IV if dataset was split or we don't have time schedule, note that IV options were set considering whole sample
            if (not timelimit.limited or data.get('modified_dataset', False)) and _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
              self.options.set('GTApprox/InternalValidation', False)
              self.options.set("GTApprox/IVSavePredictions", True)

            current_model = self._build_smart(data['x'], data['y'], options=dict(self.options.values),
                                              outputNoiseVariance=data.get('tol'), weights=data.get('weights'),
                                              comment=prefix, initial_model=data.get('initial_model'),
                                              hints=timelimit.updated_hints(hints, timelimit_denominator),
                                              x_test=data.get('x_test'), y_test=data.get('y_test'), w_test=data.get('w_test'),
                                              restricted_x=data.get('restricted_x'),
                                              categorical_inputs_map=categorical_inputs_map,
                                              categorical_outputs_map=local_categorical_outputs_map)

          if current_model[0] is None:
            raise _ex.UserTerminated()

          self.__watcher({'passed global phases': 1, 'reset smart phase': True})

          # validation data are needed only to select binarization vs categorization mode
          models_list.append({"model": current_model[0], "validation_data": self._read_validation_data(None, None), "comment": data.get('comment'),
                              "iv_dataset": self._collect_internal_validation_data(iv_requested, current_model[0], data, prefix)})

          componentwise_models_spec.append({'type': 'standalone'})
        else:
          if 1 == len(discrete_classes_data_list) or requested_technique not in ['auto', 'rsm'] or output_index in categorical_outputs_map:
            rsm_applicable = 0
          else:
            rsm_applicable = not allowed_techniques or 'rsm' in allowed_techniques

            discrete_class_options = _local_options(self.options)
            for data in discrete_classes_data_list:
              if data.get('technique', 'auto').lower() not in ['rsm', 'tbl']:
                try:
                  self.options.set(data.get('options', {}))
                  _technique_selection.check_RSM(data['_sample'], self.options, data.get('initial_model'))
                except:
                  rsm_applicable = 0
                  break
                finally:
                  discrete_class_options.revert()

          n_discrete_classes = len(discrete_classes_data_list)
          timelimit.push(timelimit.current_limit(timelimit_denominator), n_discrete_classes + rsm_applicable)

          if rsm_applicable:
            # @todo : unify with single dataset build
            discrete_class_options = _local_options(self.options)
            try:
              prefix = self._postprocess_comment(output_index, ('binarized x%s' % categorical_variables), metainfo)
              self._log(loggers.LogLevel.INFO, '\nPreprocessing data with binarization of categorical variables.\n', prefix)

              if categorical_outputs_map:
                self.options.set('GTApprox/CategoricalOutputs')

              self.options.set('GTApprox/Technique', 'RSM')
              rsm_technique_selector = _technique_selection.TechniqueSelector(self.options, tee_logger)
              rsm_updated_technique_name = rsm_technique_selector.preprocess_sample(x, actual_y, actualOutputNoiseVariance, weights, False, self.__build_manager, prefix)
              self.options.set('GTApprox/Technique', rsm_updated_technique_name)
              rsm_discrete_classes_data_list, rsm_categorical_variables = rsm_technique_selector.select(None, initial_model=actual_initial_model, comment=prefix)

              if not rsm_categorical_variables and rsm_discrete_classes_data_list[0].get('technique', default_technique).lower() in ['tbl', 'rsm']:
                data = rsm_discrete_classes_data_list[0]
                data['x_test'], data['y_test'], data['w_test'] = x_test, actual_y_test, w_test
                self.options.set(data.get('options', {}))
                if data.get('x_test') is None or data.get('y_test') is None:
                  self.options.set("GTApprox/IVSavePredictions", True) # required for proper comparison with model based on discrete classes

                self._log(loggers.LogLevel.INFO, '\nProcessing model with binarization of categorical variables\n', prefix)

                self.options.set('GTApprox/Technique', data.get('technique', default_technique))
                if self.options.get('GTApprox/Technique').lower() in ['tbl',]:
                  rsm_model = self._build_simple(data['x'], data['y'], comment=prefix, initial_model=data.get('initial_model'))
                else:
                  data['original_train_data'] = dict((k, data.get(k)) for k in ('x', 'y', 'tol', 'weights', 'initial_model', 'restricted_x'))
                  if output_index is None:
                    local_categorical_outputs_map = categorical_outputs_map
                  elif output_index in categorical_outputs_map:
                    local_categorical_outputs_map = {0: categorical_outputs_map[output_index]}
                  else:
                    local_categorical_outputs_map = {}
                  data = self._optional_split(data, accelerator_options, output_data_id, categorical_inputs_map, local_categorical_outputs_map)
                  self.options.set(data.get('options', {})) # options could be modified inside _optional_split

                  # Turn off IV if dataset was split or we don't have time schedule, note that IV options were set considering whole sample
                  if (not timelimit.limited or data.get('modified_dataset', False)) and _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
                    self.options.set('GTApprox/InternalValidation', False)
                    self.options.set("GTApprox/IVSavePredictions", True)

                  rsm_model, rsm_status, rsm_qmetrics = self._build_smart(data['x'], data['y'], options=dict(self.options.values),
                                                                          outputNoiseVariance=data.get('tol'), weights=data.get('weights'),
                                                                          comment=prefix, initial_model=data.get('initial_model'),
                                                                          hints=timelimit.updated_hints(hints, n_discrete_classes),
                                                                          x_test=data.get('x_test'), y_test=data.get('y_test'), w_test=data.get('w_test'),
                                                                          restricted_x=data.get('restricted_x'),
                                                                          categorical_inputs_map=categorical_inputs_map,
                                                                          categorical_outputs_map=local_categorical_outputs_map)

                if rsm_model is None:
                  raise _ex.UserTerminated()

                self.__watcher({'passed global phases': 1, 'reset smart phase': True})

                models_list.append({"model": rsm_model, "validation_data": self._read_validation_data(rsm_model, data), "comment": None,
                                    "iv_dataset": self._collect_internal_validation_data(iv_requested, rsm_model, data, prefix)})
                componentwise_models_spec.append({'type': 'standalone'})
            except Exception:
              e = sys.exc_info()[1]
              rsm_model = None
              self._log(loggers.LogLevel.INFO, '\nCannot use RSM with binarized categorical variables: %s\n' % _shared._safestr(e).strip(), prefix)
            finally:
              discrete_class_options.revert()
              rsm_technique_selector = None
              del rsm_technique_selector


          # Clear categorical variables specification to avoid building of single-categoria models, but keep encoded variables (hence still categorical) for information.
          # This option does not affect inputs encoding - all encoded inputs automatically set categorical in the model built.
          encoded_variables = [_ for _ in _shared.parse_json(self.options.get('GTApprox/CategoricalVariables')) if _ not in categorical_variables]
          self.options.set('GTApprox/CategoricalVariables', encoded_variables)

          # service option indicating composite model is building
          self.options.set('//Service/BuildingCompositeModel', True)

          discrete_class_options = _local_options(self.options)

          try:
            if rsm_model is not None and 'quality' == rsm_status:
              raise _ex.UserTerminated()

            local_categorical_inputs_map = dict((i, categorical_inputs_map[i]) for i in categorical_inputs_map if i not in categorical_variables)

            if output_index is None:
              local_categorical_outputs_map = categorical_outputs_map
            elif output_index in categorical_outputs_map:
              local_categorical_outputs_map = {0: categorical_outputs_map[output_index]}
            else:
              local_categorical_outputs_map = {}

            categorical_models_list = []
            for class_index, data in enumerate(discrete_classes_data_list):
              prefix = self._postprocess_comment(output_index, data.get('comment'), metainfo)
              self._log(loggers.LogLevel.INFO, '\nProcessing %s\n' % prefix, prefix)

              self.options.set(data.get('options', {}))
              # We can't set the recommended technique if the list of allowed techniques was specified,
              # these options are mutually exclusive at smart selection level.
              self.options.set('GTApprox/Technique', default_technique if allowed_techniques else data.get('technique', default_technique))
              if 'auto' == self.options.get('GTApprox/Technique').lower():
                self.options.set('GTApprox/Technique')

              if 'tbl' == self.options.get('GTApprox/Technique').lower():
                current_model = self._build_simple(data['x'], data['y'], comment=prefix, initial_model=data.get('initial_model'))
              else:
                if has_test_sample:
                  categorical_signature = data['x'][0, categorical_variables]
                  test_indices = np.all(x_test[:, categorical_variables] == categorical_signature, axis=1)
                  if np.any(test_indices):
                    data['x_test'], data['y_test'] = x_test[test_indices, :], actual_y_test[test_indices, :]
                    data['w_test'] = w_test[test_indices] if w_test is not None else None
                  else:
                    data['x_test'], data['y_test'], data['w_test'] = None, None, None
                else:
                  data['original_train_data'] = dict((k, data.get(k)) for k in ('x', 'y', 'tol', 'weights', 'initial_model', 'restricted_x'))
                  data = self._optional_split(data, accelerator_options, ("%s_class%d" % (output_data_id, class_index)), local_categorical_inputs_map, local_categorical_outputs_map)
                  self.options.set(data.get('options', {})) # options could be modified inside _optional_split
                  if rsm_model is not None:
                    self.options.set("GTApprox/IVSavePredictions", True) # required for proper comparison with model based on discrete classes

                # Turn off IV if dataset was split or we don't have time schedule, note that IV options were set considering whole sample
                if (not timelimit.limited or data.get('modified_dataset', False)) and _shared.parse_bool(self.options.get('GTApprox/InternalValidation')):
                  self.options.set('GTApprox/InternalValidation', False)
                  self.options.set("GTApprox/IVSavePredictions", True)

                current_model = self._build_smart(data['x'], data['y'], options=dict(self.options.values),
                                                  outputNoiseVariance=data.get('tol'), weights=data.get('weights'),
                                                  comment=prefix, initial_model=data.get('initial_model'),
                                                  hints=timelimit.updated_hints(hints, n_discrete_classes - class_index),
                                                  x_test=data.get('x_test'), y_test=data.get('y_test'), w_test=data.get('w_test'),
                                                  restricted_x=data.get('restricted_x'),
                                                  categorical_inputs_map=local_categorical_inputs_map,
                                                  categorical_outputs_map=local_categorical_outputs_map)

              if current_model[0] is None:
                raise _ex.UserTerminated()

              self.__watcher({'passed global phases': 1, 'reset smart phase': True})

              # validation data are needed only to select binarization vs categorization mode
              categorical_models_list.append({"model": current_model[0], "validation_data": self._read_validation_data((None if rsm_model is None else current_model[0]), data),
                                              "comment": data.get('comment'), "iv_dataset": self._collect_internal_validation_data(iv_requested, current_model[0], data, prefix)})
              discrete_class_options.revert()

            models_list.extend(categorical_models_list)

            timelimit.pop()

            current_sample = {'x': x, 'f': actual_y}
            if weights is not None:
              current_sample['weights'] = weights
            if outputNoiseVariance is not None:
              current_sample['tol'] = actualOutputNoiseVariance

            if rsm_model is None:
              componentwise_models_spec.append({'type': 'categorical'})
            else:
              componentwise_models_spec[-1]['type'] = 'union'
              componentwise_models_spec[-1]['quality_metrics'] = rsm_qmetrics[0]

            componentwise_models_spec[-1]['sample'] = current_sample
            componentwise_models_spec[-1]['categorical_variables'] = categorical_variables
            componentwise_models_spec[-1]['classes_number'] = len(discrete_classes_data_list)
            componentwise_models_spec[-1]['comment'] = self._postprocess_comment(output_index, None, metainfo)
            componentwise_models_spec[-1]['output_spec'] = (' of output #%d' % output_index) if componentwise_mode else ''
          except:
            if rsm_model is None:
              raise

        componentwise_options.revert()
        timelimit_denominator -= 1

      componentwise_models = []
      final_model_decomposition = []

      # we could select between binarized and categorized RSM first... or just forget it, it's low price for simplicity
      self._perform_internal_validation(models_list)

      for output_index, model_batch in zip(training_outputs, componentwise_models_spec):
        prefix = self._postprocess_comment(output_index, model_batch.get('comment'), metainfo)
        if componentwise_mode:
          cat_initial_options = dict((key, initial_options[key]) for key in initial_options)
          cat_initial_options['//ComponentwiseTraining/ActiveOutput'] = output_index
        else:
          cat_initial_options = initial_options

        if 'standalone' == model_batch['type']:
          componentwise_models.append(models_list.pop(0).get("model"))
          final_model_decomposition.append(('standalone', self._read_build_details(componentwise_models[-1])))
        elif 'categorical' == model_batch['type']:
          self._log(loggers.LogLevel.INFO, "\nMerging models%s built for different categorical variables combinations..." % model_batch['output_spec'], prefix)
          categorical_models, _, categorical_comments = tuple(_ for _ in zip(*tuple(self._unpack_model_validation_comment(models_list.pop(0)) for _ in xrange(model_batch['classes_number']))))
          final_model_decomposition.append(('categorical', [self._read_build_details(*_) for _ in zip(categorical_models, categorical_comments)]))
          componentwise_models.append(_utilities.Utilities.join_categorical_models(categorical_models, model_batch['categorical_variables'],
                                                                                   model_batch['sample'], model_batch['comment'],
                                                                                   cat_initial_options, self.__logger))
          componentwise_models[-1] = self._join_job_ids(componentwise_models[-1], categorical_models)
        elif 'union' == model_batch['type']:
          self._log(loggers.LogLevel.INFO, "\nMerging models%s built for different categorical variables combinations..." % model_batch['output_spec'], prefix)
          rsm_model, (rsm_y_ref, rsm_y_pred, rsm_w), rsm_comment = self._unpack_model_validation_comment(models_list.pop(0))
          rsm_qmetrics = model_batch.get('quality_metrics', 'RRMS')

          categorical_models, categorical_samples, categorical_comments = tuple(_ for _ in zip(*tuple(self._unpack_model_validation_comment(models_list.pop(0)) for _ in xrange(model_batch['classes_number']))))
          discrete_model = _utilities.Utilities.join_categorical_models(categorical_models, model_batch['categorical_variables'],
                                                                        model_batch['sample'], model_batch['comment'],
                                                                        cat_initial_options, self.__logger)
          discrete_model = self._join_job_ids(discrete_model, categorical_models)

          active_cats = [i for i, (cat_y_ref_i, cat_y_pred_i, cat_w_i) in enumerate(categorical_samples) if (cat_y_ref_i is not None and cat_y_pred_i is not None)]
          if rsm_y_ref is None or rsm_y_pred is None or not active_cats:
            better_model = rsm_model if not active_cats else discrete_model
          else:
            cat_y_ref = np.vstack([categorical_samples[i][0] for i in active_cats])
            cat_y_pred = np.vstack([categorical_samples[i][1] for i in active_cats])
            cat_w = tuple(categorical_samples[i][2] for i in active_cats)

            rsm_model_error = _get_aggregate_errors(_utilities.calculate_errors(rsm_y_ref, rsm_y_pred, rsm_w)[rsm_qmetrics])
            discrete_model_error = _get_aggregate_errors(_utilities.calculate_errors(cat_y_ref, cat_y_pred, (None if any(_ is None for _ in cat_w) else np.hstack(cat_w)))[rsm_qmetrics])

            # 1% complexity penalization
            better_model = rsm_model if rsm_model_error <= (1.01 * discrete_model_error) else discrete_model

          if better_model is rsm_model:
            final_model_decomposition.append(('standalone', self._read_build_details(rsm_model)))
          else:
            final_model_decomposition.append(('categorical', [self._read_build_details(*_) for _ in zip(categorical_models, categorical_comments)]))

          componentwise_models.append(better_model)
        else:
          # paranoiac assertion
          assert False, 'Unknown model type %s' % model_batch['type']

      if not componentwise_mode and outputs_analysis is None:
        model = componentwise_models[0]
      else:
        if 1 != len(componentwise_models):
          self._log(loggers.LogLevel.INFO, "\nMerging models built for different outputs...")

        training_dataset = {'x': x, 'f': y}
        if weights is not None:
          training_dataset['weights'] = weights
        if outputNoiseVariance is not None:
          training_dataset['tol'] = outputNoiseVariance
        if outputs_analysis is not None:
          training_dataset['linear_dependencies'] = outputs_analysis

        model = _utilities.Utilities.join_componentwise_models(componentwise_models, training_dataset, "", initial_options, self.__logger, metainfo=metainfo)
        model = self._join_job_ids(model, componentwise_models)

      training_options = initial_options
      if model and 'Model Decomposition' not in model.details:
        training_options.update(model.details['Training Options'])
        # Restore IV option value which was suppressed for smart selection
        if 'GTApprox/InternalValidation' in initial_options:
          training_options['GTApprox/InternalValidation'] = initial_options['GTApprox/InternalValidation']

      training_options = self._postprocess_output_transform(model, training_options, initial_hints)
      self._postprocess_domains(model, x, training_options, metainfo, initial_model)

      if not quick_dry_run:
        self._postprocess_model_train_dataset(model=model, options=training_options,
                                              dataset={'x': x, 'y': y, 'tol': outputNoiseVariance, 'w': weights,
                                                      'x_test': x_test, 'y_test': y_test, 'w_test': w_test,
                                                      'store': store_dataset},
                                              warn_always=warn_constraints_violation)
        self._report_model_decomposition(final_model_decomposition, outputs_analysis, metainfo)

      metainfo = self._postprocess_metainfo(model=model, metainfo=metainfo, known_issues=_safe_read_attr(tee_logger, "issues", {}))
      metainfo = self._report_train_finished(model=model, time_start=time_start, metainfo=metainfo)

      return self._postprocess_model(model, _safe_read_attr(tee_logger, "log_value", ""), training_options, initial_model,
                                      initial_hints, self.__logger, comment=comment,
                                      annotations=annotations, metainfo=metainfo)

    finally:
      # cleanup queued jobs (in case there was an exception) and data
      self.__build_manager.clean_data()
      self.__build_manager.reset_workdir()

      # restore original logger
      self.__logger = saved_loggers[0]
      self.__build_manager.set_logger(saved_loggers[1])

      # restore original watcher
      self.__watcher = saved_watchers[0]
      self.__build_manager.set_watcher(saved_watchers[1])

      if saved_is_batch is not None:
        self.__build_manager.setup_batch_mode(saved_is_batch)

      # restore original options
      self.options.reset()
      self.options.set(saved_options)

  def _log(self, level, msg, prefix=None):
    if self.__logger:
      prefix = _shared.make_prefix(prefix)
      for s in msg.splitlines():
        self.__logger(level, (prefix + s))

  def _postprocess_comment(self, output_index, comment, metainfo):
    if output_index is None:
      return comment or ""

    try:
      output_name = "output #%d" % output_index
    except:
      output_name = None

    if output_name is None:
      output_name = "output %s" % output_index
    elif metainfo:
      try:
        var_name = metainfo['Output Variables'][output_index]['name'].strip()
        if var_name != ("f[%s]" % output_index):
          output_name = "%s (%s)" % (output_name, var_name) # append non-default output name
      except:
        pass

    return ", ".join((output_name, comment)) if comment and comment != output_name else output_name

  def _postprocess_output_transform(self, model, training_options, training_hints):
    if not model:
      return training_options

    ot_name = None
    for option_name in training_options:
      if option_name.lower() == "gtapprox/outputtransformation":
        ot_name = option_name
        break

    if ot_name is None and training_hints:
      # @GTApprox/TryOutputTransformations hint alters default GTApprox/OutputTransformation option value
      for hint_name in training_hints:
        if hint_name.lower() == "@gtapprox/tryoutputtransformations":
          if _shared.parse_bool(training_hints[hint_name]):
            ot_name = "GTApprox/OutputTransformation"
            training_options[ot_name] = "auto"
          break

    if ot_name is not None:
      saved_options = self.options.values
      try:
        self.options.reset()
        self.options.set(training_options)
        ot_value = _shared.parse_output_transformation(self.options.get("GTApprox/OutputTransformation"), output_size=model.size_f)
        if "auto" in ot_value or "" in ot_value:
          ot_value = [(None if (not _ or _ == "auto") else _) for _ in ot_value]
          model_decomposition = model.details.get("Model Decomposition", [])
          if not model_decomposition:
            model_decomposition = [{"Dependent Outputs": list(range(model.size_f)), "Training Options": model.details.get("Training Options", {})}]
          for submodel in model_decomposition:
            self.options.reset()
            self.options.set("GTApprox/OutputTransformation", ["auto"]*len(submodel["Dependent Outputs"]))
            self.options.set(submodel["Training Options"])
            submodel_ot = _shared.parse_output_transformation(self.options.get("GTApprox/OutputTransformation"), len(submodel["Dependent Outputs"]))
            for submodel_ot_value, out_index in zip(submodel_ot, submodel["Dependent Outputs"]):
              if ot_value[out_index] is None:
                ot_value[out_index] = submodel_ot_value
              elif ot_value[out_index] != submodel_ot_value:
                ot_value[out_index] = "auto"
          training_options[ot_name] = ot_value[0] if all(ot_value[0] == _ for _ in ot_value[1:]) else\
                                      "[%s]" % ",".join([("auto" if _ is None else _) for _ in ot_value])
      except:
        # intentionally do nothing
        pass
      finally:
        # restore original options
        self.options.reset()
        self.options.set(saved_options)
    return training_options

  def _postprocess_domains(self, model, x, options, metainfo, initial_model):
    def parse(value, default, spec):
      if value is None:
        return default
      try:
        return float(value)
      except ValueError:
        self._log(loggers.LogLevel.WARN, 'Invalid %s: \'%s\'' % (spec, value))
        return default

    logger = self.__logger

    with _shared._scoped_options(problem=self, options=options, keep_options=_utilities._PERMANENT_OPTIONS):
      catvars = _technique_selection._get_discrete_variables(self.options, model.size_x, True)

      x_domain = self.options.get("GTApprox/InputDomainType").lower()
      if x_domain == "unbound" or len(catvars) == x.shape[1] or model.details.get("Technique", "auto").lower() == "tbl":
        # Reset input domain, keep the model unwrapped
        self._set_input_domain(model, 'reset', None, None, None, self.__logger)
        return

      # Collect max/min values from metainfo
      x_max = np.empty(x.shape[1])
      x_min = np.empty(x.shape[1])
      for i, var in enumerate(metainfo['Input Variables']):
        x_max[i] = parse(var.get('max'), np.inf, 'max value for input #%d' % i)
        x_min[i] = parse(var.get('min'), -np.inf, 'min value for input #%d' % i)

      if x_domain == "manual":
        if np.isfinite(x_max).any() or np.isfinite(x_min).any():
          self._set_input_domain(model, 'box', np.vstack((x_min, x_max)), 'and', catvars, logger)
        else:
          self._set_input_domain(model, 'reset', None, None, None, logger)
      elif x_domain in ("auto", "box"):
        if not np.isfinite(x).all():
          # x contains ignorable (by definition) invalid values.
          x = x[np.isfinite(x).all(axis=1)]
          if not x.size:
            self._log(loggers.LogLevel.WARN, 'Failed to limit input domain of the model: all input points are invalid (each input vector contains at least one invalid value).')
            return

        if x_domain != "box":
          # Set ellipsoid limit
          try:
            if catvars:
              active_var = [i for i in range(x.shape[1]) if i not in catvars]
              Avar, Cvar = _utilities._min_covering_ellipsoid(x[:, active_var])
              A = np.zeros((x.shape[1], x.shape[1]))
              for i, Avar_i in zip(active_var, Avar):
                A[i, active_var] = Avar_i
              center = np.empty(x.shape[1])
              center[active_var] = Cvar
              center[catvars] = np.nan
            else:
              A, center = _utilities._min_covering_ellipsoid(x)
            self._set_input_domain(model, 'ellipsoid', np.vstack((center, A)), 'and', catvars, logger)
          except np.linalg.LinAlgError:
            self._log(loggers.LogLevel.WARN, 'Failed to find minimal covering ellipsoid for the training sample.')

        x_max = np.minimum(x_max, x.max(axis=0))
        x_min = np.maximum(x_min, x.min(axis=0))
        if catvars:
          x_min[catvars] = -np.inf
          x_max[catvars] = np.inf

        self._set_input_domain(model, 'box', np.vstack((x_min, x_max)), 'and', catvars, logger)

        # Merge with initial_model domain
        if initial_model is not None:
          self._merge_input_domains(model, [initial_model], logger)

  def _split_initial_model_outputs(self, initial_model, outputs):
    if initial_model is None:
      return [None,] * len(outputs)
    elif len(outputs) == 1 and outputs[0] is None:
      return [initial_model,]
    else:
      return initial_model._split(outputs=outputs, initial_model_mode=True)

  @staticmethod
  def _postprocess_training_outputs(size_y, technique_selector, componentwise_mode, training_outputs):
    if componentwise_mode:
      return technique_selector, componentwise_mode, ([i for i in xrange(size_y)] if training_outputs is None else training_outputs)

    if training_outputs is None or len(training_outputs) == size_y:
      return technique_selector, False, [None,] # use all outputs as usual

    preserved_options = technique_selector.options.values
    try:
      # try to slice technique selector. If failed then use componentwise mode
      technique_selector.options.set(technique_selector.options._values([i for i in training_outputs]))
      technique_selector.slice_outputs(training_outputs)
      return technique_selector, False, [training_outputs,]
    except:
      return technique_selector, True, training_outputs
    finally:
      technique_selector.options.set(preserved_options)

  @staticmethod
  def _read_x_nan_mode(x_nan_mode, preserve_ignore):
    return "preserve" if preserve_ignore and x_nan_mode.lower() == "ignore" else x_nan_mode

  @staticmethod
  def _preprocess_test_sample(size_x, size_y, x_test, y_test, w_test, x_nan_mode, y_nan_mode, logger=None):
    if (x_test is None) ^ (y_test is None):
      raise ValueError('Both or neither x_test and y_test should be given: %s is None while %s is not!' \
             % (('x_test' if x_test is None else 'y_test'), ('y_test' if x_test is None else 'x_test')))

    if x_test is None:
      return None, None, None

    x_test = _shared.as_matrix(x_test, shape=(None, size_x), name="Input part of the test dataset ('x_test' argument)")
    y_test = _shared.as_matrix(y_test, shape=(None, size_y), name="Output part of the test dataset ('y_test' argument)")

    if x_test.shape[0] != y_test.shape[0]:
      raise ValueError('Sizes of test samples do not match (%d != %d)!' % (x_test.shape[0], y_test.shape[0]))

    if w_test is not None:
      try:
        w_test = np.array(w_test, dtype=float)
        if np.equal(w_test.shape, 1).sum() != (w_test.ndim - 1):
          raise ValueError('vector is expected while %s-dimensional matrix is given' % (w_test.shape,))
        elif w_test.size != x_test.shape[0]:
          raise ValueError('%d-dimensional vector is expected while %d-dimensional vector is given' % (x_test.shape[0], w_test.size))
        else:
          w_test = w_test.flatten()
      except Exception:
        e, tb = sys.exc_info()[1:]
        _shared.reraise(ValueError, ('Test dataset points weights vector (w_test) does not conform input part of the train dataset: %s' % e), tb)

      # raise an exception if w_test contains negative or non-finite values
      if not np.isfinite(w_test).all():
        raise ValueError('Test dataset points weights vector (w_test) contains non-finite values.')
      elif (w_test < 0.).any():
        raise ValueError('Test dataset points weights vector (w_test) contains negative values.')

      if 0 == w_test.ndim or 1 >= w_test.size:
        w_test = None
      else:
        # remove test points with zero weight
        effective_points = w_test > 0.
        if not effective_points.all():
          x_test = x_test[effective_points]
          y_test = y_test[effective_points]
          w_test = w_test[effective_points]

    initial_len = len(x_test)

    # check for NaNs in x_test and handle it according to the GTApprox/InputNanMode
    if x_nan_mode is not None:
      effective_points = np.isfinite(x_test).all(axis=1)
      if not effective_points.all():
        if x_nan_mode.lower() == 'raise':
          raise ValueError('Input (x_test) part of the test dataset contains non-finite values.')
        if x_nan_mode.lower() == 'preserve':
          # nans and finite values are allowed with at least one finite value in a row
          # we could keep "only nans" rows to compare it with what? default value? sounds useless.
          effective_points = np.logical_and(np.logical_or(np.isnan(x_test), np.isfinite(x_test)).all(axis=1), np.isfinite(x_test).any(axis=1))
        x_test = x_test[effective_points]
        y_test = y_test[effective_points]
        if w_test is not None:
          w_test = w_test[effective_points]

    # check for NaNs in y_test and handle it according to the GTApprox/OutputNanMode taking into account componentwise mode
    if y_nan_mode is not None:
      effective_points = np.isfinite(y_test).all(axis=1)
      if not effective_points.all():
        if y_nan_mode.lower() == 'raise':
          raise ValueError('Output (y_test) part of the test dataset contains non-finite values.')
        else:
          x_test = x_test[effective_points]
          y_test = y_test[effective_points]
          if w_test is not None:
            w_test = w_test[effective_points]

    if logger is not None:
      final_len = len(x_test)
      if not final_len:
        logger(loggers.LogLevel.WARN, "All points are excluded from the testing sample.")
      elif final_len < initial_len:
        logger(loggers.LogLevel.WARN, "%d points are excluded from the testing sample. Length of the updated testing sample is %d" % ((initial_len - final_len), final_len))

    return (x_test, y_test, w_test) if x_test.shape[0] > 0 else (None, None, None)

  @staticmethod
  def _preprocess_restricted_points(size_x, valid_points, invalid_points):
    if invalid_points is None:
      return None, None

    if valid_points is None:
      valid_points = np.array((0, size_x), dtype=float)
    else:
      valid_points = _shared.as_matrix(valid_points, shape=(None, size_x), name="NaN prediction error. Valid input points ('valid_points' argument)")

    invalid_points = _shared.as_matrix(invalid_points, shape=(None, size_x), name="NaN prediction error. Inalid input points ('invalid_points' argument)")

    return valid_points, invalid_points

  @staticmethod
  def _preprocess_parameters(x, y, outputNoiseVariance, comment, weights, initial_model):
    x = _shared.as_matrix(x, name="Input part of the train dataset ('x' argument)")
    y = _shared.as_matrix(y, name="Output part of the train dataset ('y' argument)")

    if x.shape[0] != y.shape[0]:
      raise ValueError('Sizes of training samples do not match (%d != %d)!' % (x.shape[0], y.shape[0]))

    sample_size = x.shape[0]

    if sample_size == 0:
      raise ValueError('Training set is empty!')

    size_x = x.shape[1]
    size_y = y.shape[1]

    if size_x <= 0:
      raise _ex.InvalidProblemError('X dimensionality should be greater than zero!')
    if size_y <= 0:
      raise _ex.InvalidProblemError('Y dimensionality should be greater than zero!')

    if initial_model is not None:
      if not isinstance(initial_model, _gtamodel.Model):
        raise ValueError('The initial model given is not instance of the GTApprox Model class')
      elif initial_model.size_x != size_x or initial_model.size_f != size_y:
        raise _ex.InvalidProblemError('The input/output dimensions of the initial model given does not conform training dataset given: (%d, %d) != (%d, %d)' % (initial_model.size_x, initial_model.size_f, size_x, size_y))

    if outputNoiseVariance is not None:
      outputNoiseVariance, outputNoiseVarianceSingleVector = _shared.as_matrix(outputNoiseVariance, ret_is_vector=True, name="Output noise variance of the train dataset ('outputNoiseVariance' argument)")
      if 0 == outputNoiseVariance.size:
        outputNoiseVariance = None
      else:
        if outputNoiseVarianceSingleVector and 1 == sample_size:
          outputNoiseVariance = outputNoiseVariance.reshape(1, outputNoiseVariance.size)
        if outputNoiseVariance.shape[0] != y.shape[0] or outputNoiseVariance.shape[1] != y.shape[1]:
          raise ValueError('Noise variance matrix must have the same size as the output sample matrix: %s != %s' % (outputNoiseVariance.shape, y.shape))
        if np.isnan(outputNoiseVariance).all():
          # all nans means unknown output noise variance
          outputNoiseVariance = None
        else:
          with np.errstate(all='ignore'):
            if np.any(outputNoiseVariance < 0.):
              raise _ex.InvalidProblemError('The output noise variance contains negative values')

    if weights is not None:
      weights = _shared.as_matrix(weights, name="Weight of the train dataset points ('weights' argument)")
      if 0 == weights.size:
        weights = None
      elif (1 != weights.shape[0] and 1 != weights.shape[1]) or sample_size != weights.size:
        raise ValueError('Point weights must be a list of length equal to the number of sample points: %s != (%d)'
                         % (weights.shape, sample_size))
      else:
        weights = weights.reshape((weights.size))
        if np.all(weights == 0.):
          raise _ex.InvalidProblemError('Training sample is empty because zero weights specified for all training sample points.')

    if weights is not None and outputNoiseVariance is not None:
      raise _ex.InvalidProblemError('Both output noise variance and points weights are given.' +
                                    'Please specify either weights or output noise variance.')

    if comment and not isinstance(comment, _six.string_types):
      comment = _shared.write_json(comment)

    return x, y, outputNoiseVariance, comment, weights, initial_model

  @staticmethod
  def _unpack_model_validation_comment(model):
    return model.get("model"), model.get("validation_data"), model.get("comment")

  @staticmethod
  def _collect_internal_validation_data(iv_requested, model, dataset, comment):
    if not iv_requested or model is None or dataset is None:
      return None

    if model.iv_info and not dataset.get('modified_dataset', False):
      # IV was based on the original training dataset, no further processing is needed.
      return None

    iv_dataset = dataset.get('original_train_data', dataset).copy()
    iv_dataset['options'] = model.details.get('Training Options', {})
    iv_dataset['comment'] = comment
    return iv_dataset

  def _perform_internal_validation(self, models_list):
    if not any((model_info.get("model") is not None and model_info.get("iv_dataset")) for model_info in models_list):
      self.__watcher({'passed all iv phases': True})
      return

    saved_options = self.options.values
    try:
      self._log(loggers.LogLevel.INFO, '\nPerforming internal validation with the original training dataset...')

      self._batch_run_internal_validation(models_list, None)

      pulled_models = self.__build_manager.get_models()

      # pulled_models is dict of dicts: {data_id: {job_id: model}}
      # but in our case all data_id are unique and grouped by job_id
      # some models may be absent due to termination request
      # so we must remove other submodels with the same job_id

      models_by_job = {}
      incomplete_jobs = set()
      for data_id in pulled_models:
        for job_id, model in pulled_models[data_id].items():
          models_by_job.setdefault(job_id, []).append(data_id)
          if model is None:
            incomplete_jobs.add(job_id)

      for job_id in incomplete_jobs:
        for data_id in models_by_job[job_id]:
          pulled_models[data_id].pop(job_id, None)

      # and run IV again (note it's OK because IV at this point is deterministic)
      self._batch_run_internal_validation(models_list, pulled_models)
    except:
      exc_info = sys.exc_info()
      self._log(loggers.LogLevel.WARN, 'Failed to perform internal validation with the original training dataset: %s' % exc_info[1])
    finally:
      self.options.reset()
      self.options.set(saved_options)

  def _batch_run_internal_validation(self, models_list, pulled_models):
    for model_index, model_info in enumerate(models_list):
      model, dataset = model_info.get("model"), model_info.get("iv_dataset")
      if model is None or not dataset:
        continue

      self.options.reset()
      self.options.set(dataset.get("options", {}))

      technique = self.options.get("GTApprox/Technique").lower()
      if technique == 'auto':
        continue

      tensor_factors = _shared.parse_json(self.options.get('GTApprox/TensorFactors'))
      if not tensor_factors and technique in ['ta', 'tgp', 'auto']:
        tensor_factors = _shared.parse_json(self.options.get('//Service/CartesianStructure'))

      # @todo : do we really need this filter?
      if any(k.startswith('//') for k in self.options.values):
        training_options = self.options.values
        training_options = dict(((k, training_options[k]) for k in training_options if not k.startswith('//')))
        self.options.reset()
        self.options.set(training_options)

      self.options.set('//GT/ExternalTrainDriverIsWorking', True)
      self.options.set("//Service/SmartSelection", False)
      self.options.set("GTApprox/InternalValidation", False)
      if tensor_factors:
        self.options.set("GTApprox/TensorFactors", tensor_factors)

      # note GTApprox/IVDeterministic is always True at this point with fixed GTApprox/IVSeed if it was False initially

      prefix = dataset.get("comment", "")
      if prefix:
        prefix += ", "

      job_id = "batch_iv_model_%d" % model_index

      iv = _IterativeIV(dataset['x'], dataset['y'], options=self.options.values, outputNoiseVariance=dataset.get('tol'), weights=dataset.get('weights'), tensored=bool(tensor_factors))
      iv_iteration = 0
      while iv.session_begin():
        iv_iteration += 1
        data_id = "batch_iv_model_%d_session_%d" % (model_index, iv_iteration)
        data_comment = prefix + ("IV session %d" % iv_iteration)
        # in our case all data are unique so data_id equals to job_id
        if pulled_models is None:
          self._submit({'x': iv.x.copy() , 'y': iv.y.copy() , 'weights': (iv.weights.copy() if iv.weights is not None else None),
                        'tol': (iv.outputNoiseVariance.copy() if iv.outputNoiseVariance is not None else None),
                        'initial_model': dataset.get('initial_model'), 'options': iv.options.values, 'restricted_x': None},
                        data_id=data_id, job_id=job_id, comment=data_comment)
          iv_model = None
        else:
          iv_model = pulled_models.get(data_id, {}).get(job_id)

        iv.session_end(iv_model)

      if pulled_models is None:
        iv.save_iv(None) # do nothing, just finish
      else:
        model._Model__cache = {} # clear cached values before model modification
        iv.save_iv(model)

  def _postprocess_model_train_dataset(self, model, options, dataset, warn_always):
    if not model or not dataset:
      return model

    x = dataset['x']
    y = dataset['y']
    tol = dataset.get('tol')
    weights = dataset.get('w')

    if self.__logger:
      wrapped_logger = _utilities.Utilities._LogWrapper(self.__logger, "")
      logger_ptr = _ctypes.CFUNCTYPE(None, _ctypes.c_char_p, _ctypes.c_char_p)(wrapped_logger)
    else:
      logger_ptr = _ctypes.c_void_p()

    errdesc = _ctypes.c_void_p()
    if not _api.modify_train_dataset(model._Model__instance, ((1 if dataset.get('store', False) else 0) + 2) # 1 is "store" flag, 2 is "update statistics" flag
                                , x.shape[0], x.shape[1], y.shape[1]
                                , x.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(x.ctypes.strides, _api.c_size_ptr)
                                , y.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(y.ctypes.strides, _api.c_size_ptr)
                                , _api.c_double_ptr() if tol is None else tol.ctypes.data_as(_api.c_double_ptr)
                                , _api.c_size_ptr() if tol is None else _ctypes.cast(tol.ctypes.strides, _api.c_size_ptr)
                                , _api.c_double_ptr() if weights is None else weights.ctypes.data_as(_api.c_double_ptr)
                                , _api.c_size_ptr() if weights is None else _ctypes.cast(weights.ctypes.strides, _api.c_size_ptr)
                                , logger_ptr, _ctypes.byref(errdesc)):
      self.__warn_failure(self.__logger, errdesc, 'Failed to save training dataset with model')

    self._set_model_test_dataset(model, dataset.get('x_test'), dataset.get('y_test'), dataset.get('w_test'), dataset.get('store'), self.__logger)

    # Update IV statistics w.r.t an optional limited input domain. Do it after the final update of the train dataset,
    # so we can use the correct prior statistics.
    with _shared._scoped_options(problem=self, options=options, keep_options=None):
      keep_iv_predictions = _shared.parse_auto_bool(self.options.get('GTApprox/IVSavePredictions'), True)

    errdesc = _ctypes.c_void_p()
    if not _api.finalize_iv_statistics(model._Model__instance, keep_iv_predictions, logger_ptr, _ctypes.byref(errdesc)):
      self.__warn_failure(self.__logger, errdesc, 'Failed to save training dataset with model')

    model._Model__cache = {} # reset cached model properties

    self._warn_constraints_violation(model, warn_always)

    self._print_componentwise_errors(model.iv_info.get("Componentwise"), "Internal validation errors")
    self._print_componentwise_errors(model.details.get("Training Dataset", {}).get("Accuracy", {}).get("Componentwise"), "Training dataset errors")

    return model

  def _warn_constraints_violation(self, model, warn_always):
    if not self.__logger:
      return

    if not warn_always:
      errors = model.details.get("Training Dataset", {}).get("Accuracy", {}).get("Componentwise", {})

      if errors:
        errs = errors.get("False NaN predictions", [])
        mask = errors.get("False NaN predictions Mask", ~_shared._find_holes(errs))

        if (np.isfinite(errs) & mask & np.not_equal(errs, 0)).any():
          warn_always = True

    if warn_always:
      self._log(loggers.LogLevel.INFO, " ")
      self._log(loggers.LogLevel.WARN, "Model errors on the training dataset%s can be biased because the training dataset includes points that violate model constraints." % ((" and internal validation errors" if model.iv_info.get("Componentwise") else ""),))

  def _print_componentwise_errors(self, errors, title):
    if not self.__logger or not errors:
      return

    try:
      self._log(loggers.LogLevel.INFO, "\n%s:\n\n" % title)

      errors_order = ["count", "r^2", "rrms", "rms", "mean", "median", "max", "q_0.99", "q_0.95",
                      "inf count", "nan count", "false nan predictions", "unpredicted nan count", "logloss"]
      optional_errors = ("inf count", "nan count", "false nan predictions", "unpredicted nan count")

      title_width = max(len(kind) for kind in errors if kind.lower() not in optional_errors or np.count_nonzero(errors[kind]))
      report_string_0 = "%%-%ds: [%%s]" % (title_width)
      report_string_1 = "%%%ds [%%s]" % (title_width + 1)

      def compare_error_kind(kind):
        try:
          return errors_order.index(kind.lower())
        except:
          return len(errors_order)

      for kind in sorted([kind for kind in errors if not kind.endswith(" Mask")], key=compare_error_kind):
        errs = errors[kind]
        mask = errors.get(kind + " Mask", ~(_shared._NONE == errs))
        if mask.any() and (kind.lower() not in optional_errors or np.count_nonzero(errs)):
          for i in range(0, len(errs), 5):
            err_line = ", ".join(("  n/a      " if not msk else ("%-11.3g" % err)) for err, msk in zip(errs[i:i+5], mask[i:i+5]))
            if not i:
              self._log(loggers.LogLevel.INFO, report_string_0 % (kind, err_line))
            else:
              self._log(loggers.LogLevel.INFO, report_string_1 % ("...", err_line))
    except:
      pass # ignoreable error occurred

  @staticmethod
  def _postprocess_metainfo(model, metainfo, known_issues):
    if not model:
      return metainfo

    try:
      job_pattern =  re.compile(r"(^|, )(job [^,]+)($|, )")
      if model.annotations.get("__job_id__", []):
        # filter out smart selection jobs
        known_jobs = model.annotations.get("__job_id__", [])
        known_issues = dict((k, known_issues[k]) for k in known_issues if (not job_pattern.search(k) or any((job_id in k) for job_id in known_jobs)))

      if known_issues:
        clean_known_issues = {}
        for section in known_issues:
          found = job_pattern.search(section)
          clean_known_issues.setdefault(((", ".join(chunk for chunk in (section[:found.start()], section[found.end():]) if chunk) or "[general]") if found else section), []).extend(known_issues[section])
        known_issues = clean_known_issues
    except:
      pass

    # Reset cached model properties to avoid segfault
    model._Model__cache = {}
    metainfo = metainfo or {}

    # Do not forget to save variability info if there is any
    try:
      details = _details._details(model)
      for variables_direction in metainfo:
        if details.get(variables_direction):
          for var_meta, var_details in zip(metainfo[variables_direction], details[variables_direction]):
            if var_details.get('variability', 'continuous') == 'enumeration' and 'labels' in var_meta and 'enumerators' in var_meta and 'enumerators' in var_details:
              # reorder labels according to internal enumerators
              try:
                unordered_labels, unordered_enums = var_meta['labels'], [float(k) for k in var_meta['enumerators']]
                var_meta['labels'] = [unordered_labels[unordered_enums.index(v)] for v in var_details['enumerators']]
                var_meta['enumerators'] = var_details['enumerators']
              except:
                pass
            var_meta.update(var_details)
          # Add extra outputs to metainfo if model has more outputs than it was in training sample.
          # May be useful in case of binarization performed by multi:softprob
          if len(details[variables_direction]) > len(metainfo[variables_direction]):
            metainfo[variables_direction].extend(details[variables_direction][len(metainfo[variables_direction]):])
    except:
      pass

    metainfo['Issues'] = known_issues or {}

    return metainfo

  @staticmethod
  def _postprocess_model(model, full_log, initial_options, initial_model, initial_hints, logger, comment=None, annotations=None, metainfo=None):
    if not model:
      return model

    errdesc = _ctypes.c_void_p()

    try:
      if not _api.set_build_log(model._Model__instance, (full_log if full_log else '').encode('utf8'), _ctypes.byref(errdesc)):
        raise _ex.OutOfMemoryError()
    except:
      Builder.__warn_failure(logger, errdesc, 'Failed to save training log with model')

    if initial_options is not None:
      initial_options = dict(((k, initial_options[k]) for k in initial_options if not k.startswith('//')))
      _api.set_options(model._Model__instance, 1, _shared.write_json(initial_options).encode('ascii'), _api.c_void_ptr_ptr())

    if initial_hints is not None:
      _api.set_options(model._Model__instance, 0, _shared.write_json(dict(initial_hints)).encode('ascii'), _api.c_void_ptr_ptr())

    if initial_model is not None:
      _api.update_initial_model_info(model._Model__instance, initial_model._Model__instance, _api.c_void_ptr_ptr())

    if annotations is None and model.annotations:
      annotations = {} # non-None is required to cleanup temporary anotations

    if comment is None and model.comment:
      comment = "" # non-None is required to cleanup temporary comment

    return model._Model__modify(comment=comment if comment is not None else "", annotations=annotations, metainfo=metainfo)

  @staticmethod
  def _join_job_ids(model, origins):
    if model is None:
      return model

    job_ids = []
    for origin in origins:
      if origin is not None:
        job_ids.extend(origin.annotations.get("__job_id__", []))

    if not job_ids:
      return model

    annotations = model.annotations
    annotations = dict((k, annotations[k]) for k in annotations)
    annotations["__job_id__"] = job_ids

    return model.modify(annotations=annotations)

  @staticmethod
  def _set_model_test_dataset(model, x_test, y_test, w_test, store_dataset, logger):
    if not model or x_test is None or y_test is None:
      return

    errdesc = _ctypes.c_void_p()
    if not _api.modify_test_dataset(model._Model__instance, store_dataset
                               , x_test.shape[0], x_test.shape[1], y_test.shape[1]
                               , x_test.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(x_test.ctypes.strides, _api.c_size_ptr)
                               , y_test.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(y_test.ctypes.strides, _api.c_size_ptr)
                               , _api.c_double_ptr() if w_test is None else w_test.ctypes.data_as(_api.c_double_ptr)
                               , _api.c_size_ptr() if w_test is None else _ctypes.cast(w_test.ctypes.strides, _api.c_size_ptr)
                               , _ctypes.byref(errdesc)):
      Builder.__warn_failure(logger, errdesc, 'Failed to save test dataset with model')

  @staticmethod
  def _restrict_validity_domain(model, valid_points, invalid_points, logger):
    if model is None:
      return

    valid_points, invalid_points = Builder._preprocess_restricted_points(model.size_x, valid_points, invalid_points)

    if invalid_points is None:
      return

    errdesc = _ctypes.c_void_p()
    if not _api.restrict_validity_domain(model._Model__instance, 0
                                    , valid_points.shape[0], valid_points.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(valid_points.ctypes.strides, _api.c_size_ptr)
                                    , invalid_points.shape[0], invalid_points.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(invalid_points.ctypes.strides, _api.c_size_ptr)
                                    , _ctypes.byref(errdesc)):
      Builder.__warn_failure(logger, errdesc, 'Failed to restrict model validity domain.')

  @staticmethod
  def _set_input_domain(model, domain_op, data, combine_op, catvars, logger):
    if not model:
      return

    if catvars:
      catvars = np.array([i for i in catvars], _ctypes.c_size_t)
    else:
      catvars = np.array([], _ctypes.c_size_t)

    if data is not None:
      data = np.atleast_2d(data).astype(_ctypes.c_double)
    else:
      data = np.empty((0, model.size_x), dtype=_ctypes.c_double)
    data_shape = data.ctypes.shape_as(_ctypes.c_size_t)
    data_strides = data.ctypes.strides_as(_ctypes.c_size_t)

    errdesc = _ctypes.c_void_p()
    # encode is conventional way to make string compatible with ctypes.c_char_p in Python 2/3
    if not _api.set_input_domain(model._Model__instance,
        (_ctypes.c_char_p() if not domain_op else domain_op.encode("ascii")),
        (_ctypes.c_char_p() if not combine_op else combine_op.encode("ascii")),
        _ctypes.cast(data_shape, _api.c_size_ptr), data.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(data_strides, _api.c_size_ptr),
        catvars.shape[0], catvars.ctypes.data_as(_api.c_size_ptr), catvars.strides[0], _ctypes.byref(errdesc)):
      Builder.__warn_failure(logger, errdesc, 'Failed to add limits for model inputs.')

  @staticmethod
  def _merge_input_domains(model, extending_models, logger):
    if not model or not extending_models:
      return

    errdesc = _ctypes.c_void_p()
    extending_models_array = (_ctypes.c_void_p * len(extending_models))(*(_._Model__instance for _ in extending_models))
    if not _api.merge_input_domains(model._Model__instance, len(extending_models_array),
                                    extending_models_array, _ctypes.byref(errdesc)):
      Builder.__warn_failure(logger, errdesc, 'Failed to merge input domains of models.')

    # Clear cache to refine model parameters
    model._Model__cache = {}

  def _select_output_transform(self, x, y, options, outputNoiseVariance, weights, initial_model, comment=""):
    return self.__build_manager._select_output_transform_local(x, y, options, outputNoiseVariance, weights, comment, initial_model)

  def _read_batch_mode(self, technique_selector, cw_mode, limited_time, all_outputs_categorical):
    mode = self.options.get("GTApprox/SubmodelTraining").lower()
    if mode == "parallel":
      return True
    elif mode == "sequential":
      return False
    elif mode == "fastparallel":
      self._log(loggers.LogLevel.WARN, 'FastParallel mode selected. Some results may become irreproducible.')
      return "fastparallel"

    if technique_selector is not None:
      return technique_selector.batch_recommended(cw_mode, limited_time, all_outputs_categorical)
    return _shared.parse_bool(self.options.get("//Service/SmartSelection"))

  def _build_simple(self, x, y, options=None, outputNoiseVariance=None, comment=None, weights=None, initial_model=None, silent=False):
    x, y, outputNoiseVariance, comment, weights, initial_model = self._preprocess_parameters(x, y, outputNoiseVariance, comment, weights, initial_model)

    if self.__watcher is not None and not self.__watcher(None):
      raise _ex.UserTerminated()

    # save original options
    saved_options = self.options.values
    saved_loggers = (self.__logger, self.__build_manager.get_logger())

    try:
      if options is not None:
        _shared.check_concept_dict(options, 'options')
        self.options.set(options)

      if silent:
        self.set_logger(None)

      return self.__build_manager.build(x, y, options, outputNoiseVariance, comment, weights, initial_model, restricted_x=None)
    finally:
      if silent:
        # restore original logger
        self.__logger = saved_loggers[0]
        self.__build_manager.set_logger(saved_loggers[1])

      # restore original options to avoid posteffects
      self.options.reset()
      self.options.set(saved_options)

  def _build_smart(self, x, y, options=None, outputNoiseVariance=None, comment=None, weights=None, initial_model=None,
                  hints=None, objective_options=None, x_test=None, y_test=None, w_test=None, restricted_x=None,
                  categorical_inputs_map=None, categorical_outputs_map=None):
    if objective_options is not None:
      _shared.check_concept_dict(objective_options, 'options')

    if hints is not None:
      _shared.check_concept_dict(hints, 'options')

    if self.__watcher is not None and not self.__watcher(None):
      raise _ex.UserTerminated()

    with _shared._scoped_options(problem=self, options=options):
      x, y, outputNoiseVariance, comment, weights, initial_model = self._preprocess_parameters(x, y, outputNoiseVariance, comment, weights, initial_model)
      size_x, size_y = x.shape[1], y.shape[1]
      x_test, y_test, w_test = self._preprocess_test_sample(size_x, size_y, x_test, y_test, w_test,
                                                            self._read_x_nan_mode(self.options.get("GTApprox/InputNanMode"), True),
                                                            self.options.get("GTApprox/OutputNanMode"))

      options = dict(self.options.values)
      self.options.reset()

      smart_selector = SmartSelector(options, objective_options, hints=hints, logger=self.__logger,
                                     watcher=self.__watcher, approx_builder=self,
                                     categorical_inputs_map=categorical_inputs_map,
                                     categorical_outputs_map=categorical_outputs_map)

      model, status, qmetrics = smart_selector.build(x, y, x_test, y_test, w_test=w_test, output_noise_variance=outputNoiseVariance,
                                           comment=comment, weights=weights, initial_model=initial_model,
                                           restricted_x=restricted_x)
      if model is not None:
        self._restrict_validity_domain(model, x, restricted_x, self.__logger)
        self._set_model_test_dataset(model, x_test, y_test, w_test, False, self.__logger)

        annotations = model.annotations
        annotations = dict((k, annotations[k]) for k in annotations)
        annotations["__job_id__"] = [_make_job_prefix(comment, job_id) for job_id in model.annotations.get("__job_id__", [])]
        model = model.modify(annotations=annotations)

      return model, status, qmetrics

  def _report_linear_dependencies(self, explanatory_outputs, evaluation_model, constraints, y, y_name):
    if evaluation_model is None:
      return

    if constraints is not None:
      _, _, b, R, revR = constraints

    # report model, test for constants
    eps = np.finfo(float).eps

    model_terms = [y_name[output_index] for output_index in explanatory_outputs] + ["1",]
    self._log(loggers.LogLevel.INFO, "\nLinear dependencies between outputs are set by the initial model.")
    for output_index, output_name in enumerate(y_name):
      if output_index not in explanatory_outputs:
        # explained output
        self._log(loggers.LogLevel.INFO, "%s = %s" % (output_name, _linear_regression_string(model_terms, evaluation_model[output_index])))

        if (evaluation_model[output_index, :-1] == 0.).all() and np.isfinite(y[:, output_index]).any():
          y_min, y_max, y_expected = np.nanmin(y[:, output_index]), np.nanmax(y[:, output_index]), evaluation_model[output_index, -1]
          tol = max(1., abs(y_expected)) * 2. * eps
          if y_min < (y_expected - tol) or y_max > (y_expected + tol):
            raise _ex.InvalidProblemError("The initial model sets the output %s = %g, but this output varies in the range [%g, %g] in the training dataset. GTApprox does not yet support promoting constant output to variable output." % (output_name, y_expected, y_min, y_max))
      elif constraints is not None and (R[:, explanatory_outputs.index(output_index)] != 0.).any():
        # constrained output
        self._log(loggers.LogLevel.INFO, "%s is constrained" % (output_name,))
      else:
        # independent output
        self._log(loggers.LogLevel.INFO, "%s is independent" % (output_name,))

    if constraints is not None:
      weights_model = np.empty((2, len(model_terms))) # the first row is mutable terms, the second row is constant terms
      for i, (b_i, R_i, revR_i) in enumerate(zip(b, R, revR)):
        weights_model.fill(0.)
        weights_model[0, :-1][revR_i != 0.] = R_i[revR_i != 0.]
        weights_model[1, :-1][revR_i == 0.] = -R_i[revR_i == 0.] # move to the right side, so take minus
        weights_model[1, -1] = b_i

        self._log(loggers.LogLevel.INFO, "constraint #%d : %s = %s" % ((i + 1), _linear_regression_string(model_terms, weights_model[0]),
                                                                        _linear_regression_string(model_terms, weights_model[1]),))
    self._log(loggers.LogLevel.INFO, " ")

  def _read_model_linear_dependencies(self, model):
    try:
      if model:
        threshold = _shared.parse_float_auto(self.options.get('/GTApprox/PartialDependentOutputs/ConstraintConvergenceRRMSThreshold'), np.nan)

        err_desc = _ctypes.c_void_p()
        json_data = _shared._unsafe_allocator()
        _shared._raise_on_error(self._api.outputs_dependencies(model._Model__instance, threshold, json_data.callback, _ctypes.byref(err_desc)), "", err_desc)

        outputs_analysis = _shared.parse_json(json_data.value)

        explanatory_outputs = [_ for _ in outputs_analysis.get("explanatory_variables", [])]
        evaluation_model = outputs_analysis.get("evaluation_model")
        constraints = outputs_analysis.get("constraints")

        if evaluation_model is not None:
          n_z = len(explanatory_outputs)

          evaluation_model = _shared.as_matrix(evaluation_model, shape=(model.size_f, n_z + 1), name="outputs dependencies model")

          if constraints is not None:
            std_z, std_c, b, R, revR = constraints

            std_z = _shared.as_matrix(std_z, shape=(1, n_z), name="standard deviations of the explanatory outputs")[0]
            b = _shared.as_matrix(b, shape=(1, None), name="linear constraints bias vector")[0]
            R = _shared.as_matrix(R, shape=(b.shape[0], n_z), name="weights of the linear constraints")
            revR = _shared.as_matrix(revR, shape=R.shape, name="linear constraints refining weights")
            std_c = _shared.as_matrix(std_c, shape=(1, b.shape[0]), name="standard deviations of the constraints equations")[0]

            constraints = std_z, std_c, b, R, revR

          return explanatory_outputs, evaluation_model, constraints
    except:
      exc_info = sys.exc_info()
      self._log(loggers.LogLevel.WARN, "Cannot read information on linear dependencies between outputs in the initial model. " + str(exc_info[1]))

    return [], None, None

  def _componentwise_train(self, native_cw, n_inputs, n_outputs, categorical_inputs_map, categorical_outputs_map, initial_model):
    if n_outputs == 1:
      return False, None

    dep_outs_raw = self.options.get('GTApprox/DependentOutputs')

    try:
      dep_outs = dep_outs_raw.strip().lower()
      if dep_outs not in ('auto', 'partiallinear'):
        dep_outs = None
    except:
      dep_outs = None

    if dep_outs is None:
      dep_outs = 'true' if _shared.parse_bool(dep_outs_raw) else 'false'

    search_groups = _shared.parse_json(self.options.get("/GTApprox/DependentOutputsSearchGroups"))
    if search_groups and any(_ for _ in search_groups):
      if any(output_index in categorical_outputs_map for search_group in search_groups for output_index in search_group):
        raise _ex.InvalidOptionsError("Linearly dependent categorical outputs are not supported.")
      elif dep_outs == "auto":
        dep_outs = "partiallinear"
      elif dep_outs != "partiallinear":
        raise _ex.InvalidOptionsError("Incompatible options combination is given: GTApprox/DependentOutputs is '%s' while 'Auto' or 'PartialLinear' is expected because /GTApprox/DependentOutputsSearchGroups option specifies groups of dependent outputs." % dep_outs_raw)

    if initial_model:
      explanatory_outputs, evaluation_model, constraints = self._read_model_linear_dependencies(model=initial_model)
      if evaluation_model is not None:
        if dep_outs not in ('auto', 'partiallinear'):
          raise _ex.InvalidOptionsError("Incompatible options combination is given: GTApprox/DependentOutputs is '%s' while 'Auto' or 'PartialLinear' is expected because initial model has linear dependencies between outputs." % dep_outs_raw)
        if search_groups and any(_ for _ in search_groups):
          # test compatibility of the existing model and user-defined search groups: all or nothing test
          initial_model_groups = [[explanatory_outputs[i] for i in np.where(equation != 0.)] for equation in evaluation_model[:,:-1]]
          if constraints is not None:
            initial_model_groups += [[explanatory_outputs[i] for i in np.where(equation != 0.)] for equation in constraints[3]]
          initial_model_groups = [set(_) for _ in initial_model_groups if len(_) > 1]
          for user_group in (set(_) for _ in search_groups if _):
            for initial_group in initial_model_groups:
              if user_group.union(initial_group) != user_group:
                raise _ex.InvalidOptionsError("Incompatible option value is given: the initial model has linear dependencies between the outputs %s, which violates constraint %s set by the /GTApprox/DependentOutputsSearchGroups option." % (tuple(initial_group), tuple(user_group)))
        dep_outs = 'partiallinear'

    tech = self.options.get('GTApprox/Technique').lower()
    #all_inputs_are_categorical = np.all([i in categorical_inputs_map for i in np.arange(n_inputs)])
    all_outputs_are_categorical = np.all([i in categorical_outputs_map for i in np.arange(n_outputs)])
    if categorical_outputs_map:
      # we must split categorical and continuous outputs unless all outputs are categorical
      auto_cw = not all_outputs_are_categorical
    #elif all_inputs_are_categorical:
    #  auto_cw = False
    elif tech in [str(_).lower() for _ in native_cw]:
      # All these techniques have effective internal componentwise support, so default CW mode must be False
      # With one exception: stepwisefit mode in RSM requires explicit componentwise training
      auto_cw = (tech == "rsm" and self.options.get("GTApprox/RSMFeatureSelection").lower() == "stepwisefit")
    else:
      auto_cw = True # default implicit mode is componentwise

    if initial_model and not initial_model._has_or:
      auto_cw = False

    cw_train = self.options.get('GTApprox/Componentwise')
    cw_train = 'auto' if (isinstance(cw_train, _six.string_types) and cw_train.lower() == 'auto') \
                    else 'true' if _shared.parse_bool(cw_train) else 'false'

    result = {  'auto' : {'auto': auto_cw, 'true': False, 'false': True, 'partiallinear': True}
              , 'true' : {'auto': True,    'true': None,  'false': True, 'partiallinear': True}
              , 'false': {'auto': False,   'true': False, 'false': None, 'partiallinear': False}
              }.get(cw_train).get(dep_outs)
    if result is None:
      raise _ex.InvalidOptionsError('Incompatible options combination is given: both GTApprox/Componentwise and GTApprox/DependentOutputs options are turned %s' % ('ON' if 'true' == cw_train else 'OFF'))

    if categorical_outputs_map and dep_outs == "partiallinear":
      # TODO we can exclude categorical outputs from dependency analysis and throw it only if all_outputs_are_categorical
      raise _ex.InvalidOptionsError("Linearly dependent categorical outputs are not supported.")
    elif categorical_outputs_map and not all_outputs_are_categorical and result != True:
      raise _ex.InvalidOptionsError("Only componentwise mode is supported for mixed categorical and conituous outputs.")

    return result, dep_outs

  def _print_sysinfo(self, time_start):
    if self.__logger:
      self._log(loggers.LogLevel.INFO, 'Training started at %s\n' % (time_start,))
      omp_threads_num = _ctypes.c_size_t()
      buildstamp_size = _ctypes.c_size_t()
      if self._api.read_sys_info(_ctypes.byref(omp_threads_num), _ctypes.c_char_p(), _ctypes.byref(buildstamp_size)):
        buildstamp_info = (_ctypes.c_char * buildstamp_size.value)()
        if self._api.read_sys_info(self._api.c_size_ptr(), buildstamp_info, _ctypes.byref(buildstamp_size)) and buildstamp_info:
          self._log(loggers.LogLevel.INFO, 'Build stamp information:')
          self._log(loggers.LogLevel.INFO, _shared._preprocess_utf8(buildstamp_info.value))

  def _print_options(self, options, initial_model):
    if self.__logger:
      actual_list = [(name, options[name]) for name in options if not name.startswith('//')]
      if actual_list:
        self._log(loggers.LogLevel.INFO, 'The following options are specified:')
        for option in actual_list:
          self._log(loggers.LogLevel.INFO, '  %s: %s' % option)
      else:
        self._log(loggers.LogLevel.INFO, 'No additional options are specified.')
      self._log(loggers.LogLevel.INFO, ' ')

      if initial_model:
        self._log(loggers.LogLevel.INFO, 'The initial model is given:')
        self._log(loggers.LogLevel.INFO, '  ' + '\n  '.join(_ for _ in str(initial_model).split('\n')))
        self._log(loggers.LogLevel.INFO, ' ')

  @staticmethod
  def _report_technique_failure(error_message, prefix, allowed_techniques):
    if not prefix and not allowed_techniques:
      return error_message

    report_stream = StringIO()

    if prefix:
      report_stream.write(prefix + ", ")

    if allowed_techniques:
      report_stream.write( "approximation techniques are limited by hints and options to ["\
                         + ", ".join([_technique_selection._get_technique_official_name(tech) for tech in allowed_techniques])\
                         + "]\n")

    report_stream.write(_shared._safestr(error_message))

    return report_stream.getvalue()


  @staticmethod
  def _read_build_details(model, desc=None):
    model._Model__cache = {}
    training_options = model.details.get("Training Options", {})
    return { "Technique": model.details.get("Technique", "Auto"),
             "Training Options": dict((k, training_options[k]) for k in training_options if not k.startswith("//")),
             "Description": desc,
             "Output Size": model.size_f }

  def _report_model_decomposition(self, model_decomposition, outputs_analysis, metainfo):
    if not self.__logger:
      return

    try:
      report_stream = StringIO()

      simple_name = re.compile(r"\w+(\[.*\])*$")

      output_names = [_["name"] for _ in metainfo["Output Variables"]]
      output_names = [_ if simple_name.match(_) else repr(_) for _ in output_names]

      independent_outputs = [output_names[_] for _ in outputs_analysis.get("explanatory_variables", [])] if outputs_analysis else []

      def _print_options(options, prefix, title):
        options = [(k, options[k]) for k in options if not k.startswith("//")]
        if options:
          if title:
            report_stream.write(title + "\n")
          for k, v in sorted(options, key=lambda kv: kv[0].lower()):
            report_stream.write("%s%s = %s\n" % (prefix, k, v))

      def _option_hash(k, v):
        return k.lower() + "=" + str(v)

      def _collect_common_options(options_list):
        if not options_list:
          return {}
        first_options = options_list[0]
        common_options = set(_option_hash(k, first_options[k]) for k in first_options)
        for current_options in options_list[1:]:
          common_options = set.intersection(common_options, set(_option_hash(k, current_options[k]) for k in current_options))
        return common_options

      def _read_common_options(common_options, options):
        return dict((k, options[k]) for k in options if _option_hash(k, options[k]) in common_options)

      def _read_uncommon_options(common_options, options):
        return dict((k, options[k]) for k in options if _option_hash(k, options[k]) not in common_options)

      options_collection = []
      for kind, details in model_decomposition:
        if kind == "standalone":
          options_collection.append(details["Training Options"])
        elif kind == "categorical":
          options_collection.extend(cat_details["Training Options"] for cat_details in details)

      common_options = _collect_common_options(options_collection)

      # take into account models may have different output size
      linearized_model_decomposition = []
      for kind, details in model_decomposition:
        output_size = max(_.get("Output Size", 1) for _ in details) if kind == "categorical" else details.get("Output Size", 1)
        linearized_model_decomposition.extend([(kind, details),] * output_size)
      model_decomposition = linearized_model_decomposition

      if common_options:
        # Find GTApprox/OutputTransformation in common options and spread it
        for k in options_collection[0]:
          if str(k).lower() == "gtapprox/outputtransformation":
            original_transform = _shared.parse_output_transformation(options_collection[0][k])
            if isinstance(original_transform, _six.string_types) or all(_ == original_transform[0] for _ in original_transform[1:]):
              break # all transforms are the same or empty

            for f_index, (kind, details) in enumerate(model_decomposition):
              # we must copy details because they can refer to the same object
              if kind != "categorical":
                details = dict(details)
                details["Training Options"] = dict(details.get("Training Options", {}))
                details["Training Options"]["GTApprox/OutputTransformation"] = original_transform[f_index]
              else:
                details = [dict(_) for _ in details]
                for cat_details in details:
                  cat_details["Training Options"] = dict(cat_details.get("Training Options", {}))
                  cat_details["Training Options"]["GTApprox/OutputTransformation"] = original_transform[f_index]
              model_decomposition[f_index] = (kind, details)

            # remove this option from collection but not from the common options hashset
            options_collection[0].pop(k)
            break

      # take into account dependent outputs
      if outputs_analysis and outputs_analysis.get("evaluation_model") is not None:
        remapped_decomposition = [None,]*outputs_analysis["evaluation_model"].shape[0]
        for z_index, f_index in enumerate(outputs_analysis["explanatory_variables"]):
          remapped_decomposition[f_index] = model_decomposition[z_index]

        evaluation_model = outputs_analysis["evaluation_model"]
        for f_index in [i for i, v in enumerate(remapped_decomposition) if v is None]:
          nz_terms = np.where(evaluation_model[f_index, :-1])[0]
          terms = [independent_outputs[k] for k in nz_terms]
          weights = evaluation_model[f_index, nz_terms]
          if not terms or evaluation_model[f_index, -1] != 0.:
            terms = ["1"] + terms
            weights = np.hstack((evaluation_model[f_index, [-1]], weights))
          remapped_decomposition[f_index] = ("explained", _linear_regression_string(terms, weights))
        model_decomposition = remapped_decomposition

      report_stream.write("\n")
      if common_options:
        _print_options(_read_common_options(common_options, options_collection[0]), "  ", "Common training options applied to all outputs:")

      report_stream.write("Output-specific properties and training options:\n")
      for f_index, (kind, details) in enumerate(model_decomposition):
        if kind == "standalone":
          report_stream.write("  Output #%d: %s (technique: %s)\n" % (f_index, output_names[f_index], details["Technique"]))
          _print_options(_read_uncommon_options(common_options, details["Training Options"]), "    ", None)
        elif kind == "explained":
          report_stream.write("  Output #%d: %s = %s (dependent output)\n" % (f_index, output_names[f_index], details))
        else:
          report_stream.write("  Output #%d: %s (composite output)\n" % (f_index, output_names[f_index]))
          cat_options_collection = [cat_details["Training Options"] for cat_details in details]
          cat_common_options = _collect_common_options(cat_options_collection)
          if cat_options_collection:
            _print_options(_read_common_options(cat_common_options.difference(common_options), cat_options_collection[0]), "    ", None)
          for i, cat_details in enumerate(details):
            cat_name = cat_details.get("Description")
            cat_name = ("for " + cat_name) if cat_name else ("#%d" % i)
            report_stream.write("    Submodel %s (technique: %s)\n" % (cat_name, cat_details["Technique"]))
            _print_options(_read_uncommon_options(cat_common_options, cat_details["Training Options"]), "      ", None)

      if outputs_analysis and outputs_analysis.get("constraints") is not None:
        report_stream.write("Output dependency details:\n")
        for b, c in zip(outputs_analysis["constraints"][2], outputs_analysis["constraints"][3]):
          nz = np.where(c)[0]
          report_stream.write("  %s = %s\n" % (b, _linear_regression_string([independent_outputs[k] for k in nz], c[nz])))

      self._log(loggers.LogLevel.INFO, report_stream.getvalue())
    except:
      exc_info = sys.exc_info()
      self._log(loggers.LogLevel.WARN, "Ignorable error occurred: failed to create detailed model report.")
      self._log(loggers.LogLevel.DEBUG, "Error type: %s, Error message: %s" % exc_info[:2])
      self._log(loggers.LogLevel.DEBUG, _shared.read_traceback())

  def _report_train_finished(self, model, time_start, metainfo):
    time_finish = datetime.now()
    if not time_start:
      time_train = None
    else:
      time_train = time_finish - time_start

      metainfo = metainfo or {}
      try:
        metainfo["Training Time"] = {"Start": str(time_start),
                                      "Finish": str(time_finish),
                                      "Total": str(time_train)}
      except:
        pass

    if self.__logger:
      time_report = "\n"
      if time_start:
        time_report += 'Training started at %s\n' % str(time_start)
      time_report += 'Training finished at %s\n' % time_finish
      if time_train:
        time_report += 'Total training time: %s\n' % time_train

      self._log(loggers.LogLevel.INFO, time_report)
      if model:
        self._log(loggers.LogLevel.INFO, '\nModel trained successfully.')

    return metainfo

  def _read_validation_data(self, model, data):
    if model is None or data is None:
      return (None, None, None)

    y_ref, y_pred, weights = None, None, None

    if data.get("x_test") is not None and data.get("y_test") is not None:
      y_ref, y_pred, weights = data.get("y_test"), model.calc(data.get("x_test")), data.get("w_test")
    else:
      iv_dataset = model.iv_info.get("Dataset")
      if iv_dataset is not None:
        y_ref, y_pred, weights = iv_dataset.get("Validation Output"), iv_dataset.get("Predicted Output"), iv_dataset.get("Points Weights")
      elif model.training_sample and model.training_sample[0].get("x_test") is not None and model.training_sample[0].get("f_test") is not None:
        y_ref, y_pred, weights = model.training_sample[0].get("f_test"), model.calc(model.training_sample[0].get("x_test")), None
        if y_ref is not None:
          y_ref = y_ref.copy() # this data are based on the external pointer so we must get copy
        if y_pred is not None:
          y_pred = y_pred.copy() # this data are based on the external pointer so we must get copy

    return (None, None, None) if (y_ref is None or y_pred is None) else (y_ref, y_pred, weights)

  def _optional_split(self, data, accelerator_options, data_id="training_sample", categorical_inputs_map=None, categorical_outputs_map=None):
    if data.get('x_test') is not None and data.get('y_test') is not None:
      return data

    saved_options = self.options.values
    try:
      self.options.set(data.get("options", {}))

      train_test_ratio = accelerator_options.get('TrainingSubsampleRatio', 0.)
      use_iv = train_test_ratio < 0. or train_test_ratio >= 1. or data["x"].shape[0] < 4 * (data["x"].shape[1] + 1)

      if not use_iv and train_test_ratio == 0.:
        if _shared.parse_bool(self.options.get("GTApprox/ExactFitRequired")):
          use_iv = True # if exact fit is required then we must use IV and train final model on the whole dataset
        else:
          iv_subsets, iv_rounds = _technique_selection._read_iv_options_impl(0, 0, 0, data["x"].shape[0], False)
          use_iv = iv_rounds > 1 # by default there are more than 1 round - switch to IV mode

      if use_iv:
        data['x_test'], data['y_test'], data['w_test'] = None, None, None
        self._log(loggers.LogLevel.INFO, 'No sample split performed, using IV for Smart Selection.')
        return data

      seed = None if not _shared.parse_bool(self.options.get('GTApprox/Deterministic')) else int(self.options.get('GTApprox/Seed'))

      cartesian_structure = _shared.parse_json(self.options.get('GTApprox/TensorFactors'))
      fixed_structure = True
      if not cartesian_structure and self.options.get('GTApprox/Technique').lower() in ['ta', 'tgp', 'auto']:
        fixed_structure = self.options.get('GTApprox/Technique').lower() != 'auto'
        cartesian_structure = _shared.parse_json(self.options.get('//Service/CartesianStructure'))

      self.__build_manager.submit_data(data_id, data['x'], data['y'])

      if not _shared.parse_bool(accelerator_options.get('TryOutputTransformations', False)):
        output_transform = _shared.parse_output_transformation(self.options.get("GTApprox/OutputTransformation"))
        if (output_transform.lower() == "auto" if isinstance(output_transform, _six.string_types) else any(_.lower() == "auto" for _ in output_transform)):
          self.options.set("//GTApprox/OutputTransformationPrior")
          self.__build_manager.submit_job(data_id, "select_output_transform", action="select_output_transform",
                                          options=self.options.values, comment=data.get('comment'),
                                          initial_model=data.get("initial_model"))
          output_transform = self.__build_manager.select_output_transform()[data_id]["select_output_transform"]
          data.setdefault("options", {})["//GTApprox/OutputTransformationPrior"] = output_transform

      if cartesian_structure:
        initial_cartesian_factors = sorted([tuple(sorted(_[:-1])) if isinstance(_[-1], _six.string_types) else tuple(sorted(_)) for _ in cartesian_structure])

        self.__build_manager.submit_job(data_id, "split_sample", action='split_sample',
                                        train_test_ratio=train_test_ratio, tensor_structure=cartesian_structure,
                                        fixed_structure=fixed_structure, seed=seed,
                                        categorical_outputs_map=categorical_outputs_map)
        train_indices, test_indices, cartesian_structure = self.__build_manager.get_split_sample()[data_id]["split_sample"]

        new_cartesian_factors = sorted([tuple(sorted(_[:-1])) if isinstance(_[-1], _six.string_types) else tuple(sorted(_)) for _ in cartesian_structure])
        if new_cartesian_factors != initial_cartesian_factors:
          self.options.set('GTApprox/TensorFactors')
          self.options.set('//Service/CartesianStructure', cartesian_structure)
      else:
        if train_test_ratio == 0. and data["x"].shape[0] > 4000:
          train_test_ratio = 0.9 # For huge sample GP and HDAGP are disabled while simple splitting works as good as adaptive one.
                                 # Note 0.9 ratio is used because it is default IV split ratio for such a sample.
        self.__build_manager.submit_job(data_id, "split_sample", action='split_sample',
                                        train_test_ratio=train_test_ratio, seed=seed,
                                        categorical_inputs_map=categorical_inputs_map,
                                        categorical_outputs_map=categorical_outputs_map)
        train_indices, test_indices, _ = self.__build_manager.get_split_sample()[data_id]["split_sample"]

      if not test_indices.any():
        data['x_test'], data['y_test'], data['w_test'] = None, None, None
        self._log(loggers.LogLevel.INFO, 'No sample split performed, using IV for Smart Selection.')
        return data

      data['x_test'] = data['x'][test_indices]
      data['y_test'] = data['y'][test_indices]

      # reconstruct NaNs in the test dataset
      nan_marker = float(self.options.get("//Service/MissingValueMarker"))
      if nan_marker is not None and not np.isnan(nan_marker):
        data['x_test'][data['x_test'] == nan_marker] = np.nan

      if data.get('weights') is not None:
        data['w_test'] = data['weights'][test_indices]
        data['weights'] = data['weights'][train_indices]

      if data.get('tol') is not None:
        data['w_test'] = self._tolerance_to_weights(data['tol'][test_indices])
        data['tol'] = data['tol'][train_indices]

      data['x'] = data['x'][train_indices]
      data['y'] = data['y'][train_indices]

      n_train = data['x'].shape[0]
      if int(self.options.get("GTApprox/IVSubsetCount")) > n_train:
        data.setdefault("options", {})["GTApprox/IVSubsetCount"] = n_train
      if int(self.options.get("GTApprox/IVSubsetSize")) > ((n_train + 1) // 2):
        data.setdefault("options", {})["GTApprox/IVSubsetSize"] = (n_train + 1) // 2
      if int(self.options.get("GTApprox/IVTrainingCount")) > n_train:
        data.setdefault("options", {})["GTApprox/IVTrainingCount"] = n_train

      data['modified_dataset'] = True
    finally:
      # we submitted data and now we must cleanup
      self.__build_manager.clean_data()
      self.options.set(saved_options)

    return data

  def _tolerance_to_weights(self, tol):
    w = np.empty(len(tol))
    err_desc = _ctypes.c_void_p()
    _shared._raise_on_error(self._api.tolerance_to_weights(tol.shape[0], tol.shape[1],
                                                           tol.ctypes.data_as(self._api.c_double_ptr),
                                                           tol.strides[0] // tol.itemsize, tol.strides[1] // tol.itemsize,
                                                           w.ctypes.data_as(self._api.c_double_ptr), w.strides[0] // w.itemsize,
                                                           _ctypes.byref(err_desc)), "", err_desc)
    return w

  def _set_watcher(self, watcher):
    old_watcher = self.__watcher
    self.__watcher = watcher
    self.__build_manager.set_watcher(self.__watcher)
    return old_watcher

  def _set_build_manager(self, build_manager):
    build_manager.options.set(self.options.values)
    build_manager.set_watcher(self.__watcher)
    build_manager.set_logger(self.__logger)
    self.__build_manager = build_manager

  def _reset_build_manager(self):
    bm = _build_manager.DefaultBuildManager()
    bm.options.set(self.options.values)
    bm.set_watcher(self.__watcher)
    bm.set_logger(self.__logger)
    try:
      self.__build_manager.transport.release()
    except AttributeError:
      pass # intentionally do nothing
    self.__build_manager = bm

  def _filter_moa(self, moa_model, x, y, options, weights=None):
    x, y, _, _, weights, moa_model = self._preprocess_parameters(x, y, None, None, weights, moa_model)

    with _shared._scoped_options(problem=self, options=options):
      def wrapped_logger(n_clusters, message):
        try:
          self.__logger(loggers.LogLevel.INFO, _shared._preprocess_utf8(_ctypes.string_at(message)))
          if self.__watcher is not None and not self.__watcher({"n_clusters": n_clusters}):
            return False
          return True
        except:
          return False

      logger_ptr = self._api.filter_callback_type(wrapped_logger) if self.__logger else _ctypes.c_void_p()

      errdesc = _ctypes.c_void_p()
      handle = self._api.filter_moa(moa_model._Model__instance,
                                    _shared.write_json(self.options.values).encode('ascii'),
                                    x.shape[0], x.shape[1], y.shape[1],
                                    x.ctypes.data_as(self._api.c_double_ptr), x.ctypes.strides_as(_ctypes.c_size_t),
                                    y.ctypes.data_as(self._api.c_double_ptr), y.ctypes.strides_as(_ctypes.c_size_t),
                                    self._api.c_double_ptr() if weights is None else weights.ctypes.data_as(self._api.c_double_ptr),
                                    self._api.c_size_ptr() if weights is None else weights.ctypes.strides_as(_ctypes.c_size_t),
                                    logger_ptr, _ctypes.byref(errdesc))

      if not handle:
        _shared.ModelStatus.checkErrorCode(0, 'Failed to filter mixture of approximators.', errdesc)

      return _gtamodel.Model(handle=handle)

  def __submit_moa(self, x, y, options, outputNoiseVariance=None, comment=None, weights=None, initial_model=None, restricted_x=None, logger=None, data_id=0, job_id=0):
    with _shared._scoped_options(problem=self, options=options):
      # check whether user specified technique supports AE
      moa_technique = self.options.get('GTApprox/MoATechnique').upper()
      if (_shared.parse_bool(self.options.get('GTApprox/AccuracyEvaluation')) and
          not moa_technique in ['SPLT', 'GP', 'SGP', 'HDAGP', 'AUTO']):
        raise _ex.InvalidOptionsError("Accuracy Evaluation is not available for %s." % moa_technique)

      if _shared.parse_bool(self.options.get('GTApprox/LinearityRequired')):
        raise _ex.InvalidOptionsError("Linear mode not supported.")
      if _shared.parse_bool(self.options.get('GTApprox/ExactFitRequired')):
        raise _ex.InvalidOptionsError('Exact Fit mode is not available for MoA.')

      categorical_variables = _shared.parse_json(self.options.get('GTApprox/CategoricalVariables'))
      encodings = _shared.parse_json(self.options.get('//Encoding/InputsEncoding'))
      for encoding in encodings:
        if isinstance(encoding[-1], _six.string_types):
          idx, name = encoding[:-1], encoding[-1].lower()
        else:
          idx, name = encoding[:], 'none'
        if name != 'none':
          categorical_variables = [_ for _ in categorical_variables if _ not in idx]

      if categorical_variables:
        raise _ex.InvalidOptionsError('MoA technique does not support categorical variables.')

      points_assignment = self.options.get('GTApprox/MoAPointsAssignment').lower()
      points_assignment_confidence = _shared.parse_float(self.options.get('GTApprox/MoAPointsAssignmentConfidence'))
      if points_assignment == 'mahalanobis' and (points_assignment_confidence <= 0.0 or points_assignment_confidence >= 1.0):
        raise _ex.InvalidOptionsError('Wrong MoAPointsAssignmentConfidence value %s! It must be in (0, 1) interval.' % points_assignment_confidence)

      type_of_weights = self.options.get('GTApprox/MoATypeOfWeights').lower()
      if type_of_weights == 'sigmoid':
        weights_confidence = _shared.parse_float(self.options.get('GTApprox/MoAWeightsConfidence'))
        if weights_confidence <= 0.0 or weights_confidence >= 1.0:
          raise _ex.InvalidOptionsError('Wrong MoAWeightsConfidence value %s! It must be in (0, 1) interval.' % weights_confidence)
        if points_assignment_confidence <= 0.0 or points_assignment_confidence >= 1.0:
          raise _ex.InvalidOptionsError('Wrong MoAPointsAssignmentConfidence value %s! It must be in (0, 1) interval.' % points_assignment_confidence)

        if weights_confidence <= points_assignment_confidence:
          raise _ex.InvalidProblemError('Weights Confidence must be greater than Points Assignment Confidence: %s <= %s'
                                        % (weights_confidence, points_assignment_confidence))

      if logger and _shared.long_integer(self.options.get('GTApprox/MaxExpectedMemory')) > 0:
        logger.warn('GTApprox/MaxExpectedMemory is ignored: supported for the GBRT technique only.')

      self.__build_manager.submit_data(data_id, x, y, outputNoiseVariance, weights, restricted_x)
      self.__build_manager.submit_job(data_id, job_id, options=self.options.values, comment=comment,
                                      initial_model=initial_model, action='build_moa')

  @staticmethod
  def __warn_failure(logger, errdesc, default_message):
    try:
      _shared.ModelStatus.checkErrorCode(0, default_message, errdesc)
    except _ex.GTException:
      e = sys.exc_info()[1]
      if logger:
        logger(loggers.LogLevel.WARN, _shared._safestr(e))

  @staticmethod
  def __process_sample(train_x, train_y):
    if len(train_x) != len(train_y):
      raise ValueError('Sizes of training samples do not match!')
    sample_size = len(train_x)
    if sample_size == 0:
      raise ValueError('Training set is empty!')
    size_x = _shared.get_size(train_x[0])
    size_y = _shared.get_size(train_y[0])
    if size_x <= 0:
      raise ValueError('X dimensionality should be greater than zero!')
    if size_y <= 0:
      raise ValueError('Y dimensionality should be greater than zero!')
    x = train_x
    y = train_y
    if not _shared.is_iterable(train_x[0]):
      x = [[xi] for xi in train_x]
    if not _shared.is_iterable(train_y[0]):
      y = [[fi] for fi in train_y]
    return x, y

  def _submit(self, data, data_id, job_id, comment=None):
    if self.options.get('GTApprox/Technique').lower() == 'moa':
      self.__submit_moa(data['x'], data['y'], self.options.values, data.get('tol'), comment, data.get('weights'),
                        data.get('initial_model'), data.get('restricted_x'), _shared.Logger(self.__logger, 'debug', prefix=comment),
                        data_id=data_id, job_id=job_id)
    else:
      self.__build_manager.submit_data(data_id, data['x'], data['y'], outputNoiseVariance=data.get('tol'),
                                       weights=data.get('weights'), restricted_x=data.get('restricted_x'))
      self.__build_manager.submit_job(data_id, job_id, options=dict(self.options.values), comment=comment,
                                      initial_model=data.get('initial_model'), action='build')

  def _submit_job(self, data_id, job_id, action='build', **kwargs):
    return self.__build_manager.submit_job(data_id, job_id, action=action, **kwargs)

  def _get_models(self, cleanup=True):
    return self.__build_manager.get_models(cleanup=cleanup)

  def _get_build_manager(self):
    return self.__build_manager

  def _setup_y_limits(self, final_metainfo, explicit_metainfo, y):
    report_newline = False

    lower_limit = [_.get("min", -np.inf) for _ in final_metainfo.get("Output Variables", [])]
    if np.greater(lower_limit, -np.inf).any():
      self.options.set("//Service/OutputLowerBound", _shared.write_json(lower_limit))
      report_newline = True
      message = [("%s >= %s" % (info.get("name", "y"+str(i)), info.get("min", -np.inf))) for i, info in enumerate(final_metainfo.get("Output Variables", []))]
      message = ("\n" + "\n- ".join(message)) if len(message) > 1 else message[0]
      if not np.greater([_.get("min", -np.inf) for _ in (explicit_metainfo or [])], -np.inf).any():
        self._log(loggers.LogLevel.WARN, 'Using implicit lower bounds for an outputs: ' + message)
      else:
        self._log(loggers.LogLevel.INFO, 'Using explicit lower bounds for an outputs: ' + message)
    else:
      self.options.set("//Service/OutputLowerBound", None) # reset an option to default

    upper_limit = [_.get("max", np.inf) for _ in final_metainfo.get("Output Variables", [])]
    if np.less(upper_limit, np.inf).any():
      self.options.set("//Service/OutputUpperBound", _shared.write_json(upper_limit))
      report_newline = True
      message = [("%s <= %s" % (info.get("name", "y"+str(i)), info.get("max", np.inf))) for i, info in enumerate(final_metainfo.get("Output Variables", []))]
      message = ("\n" + "\n- ".join(message)) if len(message) > 1 else message[0]
      if not np.less([_.get("max", np.inf) for _ in (explicit_metainfo or [])], np.inf).any():
        self._log(loggers.LogLevel.WARN, 'Using implicit upper bounds for an outputs: ' + message)
      else:
        self._log(loggers.LogLevel.INFO, 'Using explicit upper bounds for an outputs: ' + message)
    else:
      self.options.set("//Service/OutputUpperBound", None)

    if report_newline:
      self._log(loggers.LogLevel.INFO, ' ')

    if not np.isfinite(y).any(axis=0).all():
      # There is at least one output filled with NaNs, this is not OK
      return True

    if lower_limit and np.less(np.nanmin(y, axis=0), lower_limit).any():
      return True

    if upper_limit and np.greater(np.nanmax(y, axis=0), upper_limit).any():
      return True

    return False

  @property
  def is_batch(self):
    return self.__build_manager.is_batch

def _safe_read_attr(obj, attr, ret_on_fail):
  try:
    return getattr(obj, attr)
  except AttributeError:
    raise
  except:
    pass
  return ret_on_fail
