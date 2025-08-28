#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""details function for gtapprox"""
from __future__ import division

import ctypes as _ctypes
import numpy as np

from ..six.moves import xrange, range, reduce
from .. import exceptions as _ex
from .. import shared as _shared

class _API(object):
  def __init__(self):
    self.__library = _shared._library
    self.list_submodels = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.POINTER(_ctypes.c_void_p),
                                            _ctypes.POINTER(_ctypes.c_void_p))(("GTApproxModelUnsafeSubmodelsRange", self.__library))
    self.model_training_details = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p, _ctypes.c_void_p, _ctypes.POINTER(_ctypes.c_void_p))(("GTApproxModelTrainingDetails2", self.__library))

_api = _API()

class DetailsException(_ex.GTException):
  """Special type of exception for details exceptions
  """
  def __init__(self, value):
    super(DetailsException, self).__init__()
    self.value = value

  def __str__(self):
    return repr(self.value)

def _postprocess_varname(name, altname):
  return altname if not name else ("\"%s\"" % name) if name[0].isdigit() or not all((c.isalnum() or c in "[]()_") for c in name) else name

def _get_rsm_terms(regression_model, categorical_variables, input_metainfo):
  if regression_model is None or not regression_model.size:
    return []

  input_size = regression_model.shape[1]
  continuous_model = regression_model[:, [i for i in range(input_size) if i not in categorical_variables]]
  categorical_model = regression_model[:, [i for i in range(input_size) if i in categorical_variables]]

  if not input_metainfo:
    continuous_names = [("x[%d]" % i) for i in range(input_size) if i not in categorical_variables]
    categorical_names = [("x[%d]" % i) for i in range(input_size) if i in categorical_variables]
  else:
    continuous_names = [_postprocess_varname(input_metainfo[i].get("name"), ("x[%d]" % i)) for i in range(input_size) if i not in categorical_variables]
    categorical_names = [_postprocess_varname(input_metainfo[i].get("name"), ("x[%d]" % i)) for i in range(input_size) if i in categorical_variables]

  terms_list = []
  for continuous_term, categorical_term in zip(continuous_model, categorical_model):
    if (continuous_term == 0.).all() and np.isnan(categorical_term).all():
      terms_list.append("1")
    else:
      con_list = ["*".join([varname]*int(varpow)) for varname, varpow in zip(continuous_names, continuous_term) if varpow]
      cat_list = [("I(%s, %g)" % (varname, varval)) for varname, varval in zip(categorical_names, categorical_term) if not np.isnan(varval)]
      terms_list.append("*".join(con_list + cat_list))

  return tuple(terms_list)

def _read_categorical_variables(model, defcatvars=None):
  catvar_list = model.parameters.get("/CategoricalVariables.List") if "/CategoricalVariables.List" in model.parameters.list else None
  if catvar_list is None or catvar_list.shape[0] != 1:
    return {} if defcatvars is None else defcatvars

  categorical_variables = {}
  for catvar in catvar_list[0]:
    catlevels = model.parameters.get("/CategoricalVariables.Levels[%d]" % catvar)
    if catlevels is not None and catlevels.shape[0] == 1:
      categorical_variables[int(catvar)] = tuple(float(_) for _ in catlevels[0])
  return categorical_variables

def _get_regression_model(model, model_code, weights_code, size_in, size_out):
  if any(rsm_code not in model.parameters.list for rsm_code in (model_code, weights_code)):
    return {}

  weights = model.parameters.get(weights_code) if weights_code in model.parameters.list else None
  design_matrix = model.parameters.get(model_code) if model_code in model.parameters.list else None

  if design_matrix is None or not design_matrix.size:
    design_matrix = np.eye(size_in)

  if weights is None or not weights.size:
    weights = np.eye(size_out)

  return {} if design_matrix.shape[0] != weights.shape[1] else {"model": design_matrix, "weights": weights}

def _get_rsm_model_details(model, metainfo, defcatvars=None):
  """
  If the model given is a response surface model then read all information required for model evaluation.
  Returns empty dict if the model given is not RSM one. Otherwise return dict with the following fields:
    "model": design matrix
    "weights": weights for different outputs
    "terms": list of strings of terms in model
    "categorical": dict of categorical variables (may be empty)
  """
  regression_model = _get_regression_model(model, "/RegressionSurface.Model", "/RegressionSurface.Weights", model.size_x, model.size_f)
  if regression_model:
    regression_model["categorical"] = _read_categorical_variables(model, defcatvars)
    regression_model["terms"] = _get_rsm_terms(regression_model["model"], regression_model["categorical"], metainfo["Input Variables"])
  return regression_model

def _convert_rpn_formula(formula):
  codes = {-1: "and", -2: "or", -3: "not"}
  return [codes[_] if _ in codes else int(_) for _ in formula]

def _get_model_input_constraints(model, metainfo, defcatvars=None):
  bounds = model.parameters.get("/InputConstraints.Bounds") if "/InputConstraints.Bounds" in model.parameters.list else None
  if bounds is None or bounds.shape[0] != 2:
    return {} # no constarints

  rpn_formula = model.parameters.get("/InputConstraints.RPNFormula") if "/InputConstraints.RPNFormula" in model.parameters.list else None
  if rpn_formula is None or rpn_formula.shape[0] != 1 or rpn_formula.shape[1] < (bounds.shape[1] * 2 - 1):
    return {} # error

  regression_model = _get_regression_model(model, "/InputConstraints.Model", "/InputConstraints.Weights", model.size_x, bounds.shape[1])
  if regression_model:
    if bounds.shape[1] != regression_model["weights"].shape[0]:
      return {} # error
    regression_model["categorical"] = _read_categorical_variables(model, defcatvars)
    regression_model["terms"] = _get_rsm_terms(regression_model["model"], regression_model["categorical"], metainfo["Input Variables"])
    regression_model["lower_bound"] = bounds[0].copy()
    regression_model["upper_bound"] = bounds[1].copy()
    regression_model["rpn_formula"] = _convert_rpn_formula(rpn_formula[0])
  return regression_model

def _get_model_output_constraints(model, metainfo):
  bounds = model.parameters.get("/OutputConstraints.Bounds") if "/OutputConstraints.Bounds" in model.parameters.list else None
  if bounds is None or bounds.shape[0] != 2:
    return {} # no constarints

  rpn_formula = model.parameters.get("/OutputConstraints.RPNFormula") if "/OutputConstraints.RPNFormula" in model.parameters.list else None
  if rpn_formula is None or rpn_formula.shape[0] != 1 or rpn_formula.shape[1] < (bounds.shape[1] * 2 - 1):
    return {} # error

  regression_model = _get_regression_model(model, "/OutputConstraints.Model", "/OutputConstraints.Weights", model.size_f, bounds.shape[1])
  if regression_model:
    if bounds.shape[1] != regression_model["weights"].shape[0]:
      return {} # error
    #regression_model["categorical"] = {} # there are no categorical variables for outputs
    regression_model["terms"] = _get_rsm_terms(regression_model["model"], {}, metainfo["Output Variables"])
    regression_model["lower_bound"] = bounds[0].copy()
    regression_model["upper_bound"] = bounds[1].copy()
    regression_model["rpn_formula"] = _convert_rpn_formula(rpn_formula[0])
  return regression_model

def _list_submodels(model, first, last):
  from . import model as _model
  instance_list = (_ctypes.c_void_p*(last-first))()
  if not _api.list_submodels(model._Model__instance, first, last, _ctypes.cast(instance_list, _ctypes.POINTER(_ctypes.c_void_p)), _ctypes.POINTER(_ctypes.c_void_p)()):
    return [None]*(last-first)
  return [(None if not instance_found else _model.Model(handle=instance_found)) for instance_found in instance_list]

def _append_nonempty(dest, keys, data):
  if data:
    for k in keys[:-1]:
      dest = dest.setdefault(k, {})
    dest[keys[-1]] = data

def _read_instance_details(instance):
  js_data = _shared._unsafe_allocator()
  err_desc = _ctypes.POINTER(_ctypes.c_void_p)()
  if _api.model_training_details(instance, js_data.callback, err_desc):
    return _shared.parse_json_deep(_shared._preprocess_json(js_data.value), dict)
  return dict()


def _details(model, with_metainfo=False):
  """Get details about model.

  For non-RSM technique provides used technique,
  for RSM technique provides a dict which completely specifies RSM model
  Inputs:
    model - GTApprox model
  Outputs:
    details - dict with model details
  """

  details = {}

  try:
    details = _read_instance_details(model._Model__instance)

    if not details and model.info:
      # old-style model
      details['Technique'] = model.info['ModelInfo']['Builder']['Technique']

    if details['Technique'].lower() == 'lr':
      details['Technique'] = 'RSM' # LR technique is deprecated but it still can be reported by an old models.
    elif details['Technique'].lower() == 'auto':
      details['Technique'] = 'Composite' # 'Auto' is a marker for a composite model built using different techniques

    _append_nonempty(details, ['Training Dataset', 'Accuracy',], _shared.readStatistics(model._Model__instance, "Training Dataset", "GTApprox"))
    _append_nonempty(details, ['Training Dataset', 'Sample Statistics', 'Input'], _shared.readStatistics(model._Model__instance, "Input sample", "GTApprox"))
    _append_nonempty(details, ['Training Dataset', 'Sample Statistics', 'Output'], _shared.readStatistics(model._Model__instance, "Output sample", "GTApprox"))
    _append_nonempty(details, ['Training Dataset', 'Sample Statistics', 'Points Weights'], _shared.readStatistics(model._Model__instance, "Points weights", "GTApprox"))
    _append_nonempty(details, ['Training Dataset', 'Sample Statistics', 'Output Noise Variance'], _shared.readStatistics(model._Model__instance, "Output noise variance", "GTApprox"))
    _append_nonempty(details, ['Training Dataset', 'Test Sample Statistics', 'Input'], _shared.readStatistics(model._Model__instance, "test input sample", "GTApprox"))
    _append_nonempty(details, ['Training Dataset', 'Test Sample Statistics', 'Output'], _shared.readStatistics(model._Model__instance, "test output sample", "GTApprox"))
  except:
    # do nothing
    pass

  def set_optional(details, key, value):
    if value:
      details[key] = value
    pass

  try:
    model_metainfo = model._Model__metainfo()
    set_optional(details, "Regression Model", _get_rsm_model_details(model, model_metainfo))
    set_optional(details, "Input Constraints", _get_model_input_constraints(model, model_metainfo))
    set_optional(details, "Output Constraints", _get_model_output_constraints(model, model_metainfo))
  except:
    model_metainfo = None

  model_decomposition = details.get('Model Decomposition', [])
  block_size, model_decomposition_len = 100, len(model_decomposition) # don't load more than 100 submodels

  for block_start in xrange(0, model_decomposition_len, block_size):
    block_end = min(block_start + block_size, model_decomposition_len)
    submodels_list = _list_submodels(model, block_start, block_end) # load submodels in a single batch - this is the slowest op
    for submodel_index, subdetails, submodel in zip(xrange(block_start, block_start + block_end), model_decomposition[block_start:block_end], submodels_list):
      try:
        if subdetails['Technique'].lower() == 'lr':
          subdetails['Technique'] = 'RSM'

        if submodel:
          catvars = dict((i, (c,)) for i, c in zip(subdetails.get("Categorical Variables", []), subdetails.get("Categorical Signature", [])))
          set_optional(subdetails, "Regression Model", _get_rsm_model_details(submodel, model_metainfo, catvars))
          set_optional(subdetails, "Input Constraints", _get_model_input_constraints(submodel, model_metainfo, catvars))
          set_optional(subdetails, "Output Constraints", _get_model_output_constraints(submodel, model_metainfo))
      except:
        pass

  return details if not with_metainfo else (details, model_metainfo)
