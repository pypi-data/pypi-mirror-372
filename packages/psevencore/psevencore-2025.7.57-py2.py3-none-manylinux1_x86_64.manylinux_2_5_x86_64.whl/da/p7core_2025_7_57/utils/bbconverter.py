#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

import sys as _sys
import weakref as _weakref
import contextlib as _contextlib

import numpy as _numpy

from ..blackbox import Blackbox as _Blackbox
from ..blackbox import GTIBB_GRADIENT_F_ORDER, GTIBB_GRADIENT_X_ORDER
from ..gtopt import ProblemGeneric as _ProblemGeneric
from ..six import string_types
from ..result import _read_objectives_type
from .. import exceptions as _exceptions
from .. import shared as _shared

class _BoxProblem(_ProblemGeneric):
  def __init__(self, limits, levels, size_f=None):
    super(_BoxProblem, self).__init__()
    self._lb, self._ub = limits
    self._levels = levels
    self._size_f = size_f or 0

  def prepare_problem(self):
    for l, u, lv in zip(self._lb, self._ub, self._levels):
      if lv:
        self.add_variable(lv, hints={'@GT/VariableType': 'Categorical'})
      else:
        self.add_variable((l, u))

    for _ in range(self._size_f):
      self.add_objective()

  def evaluate(self, x, mask_in):
    mask_out = _numpy.zeros_like(mask_in)
    return _shared._filled_array(mask_out.shape, _shared._NONE), mask_out

class _WrappedBlackboxAsProblem(_ProblemGeneric):
  def __init__(self, blackbox, levels):
    super(_WrappedBlackboxAsProblem, self).__init__()
    self._blackbox_ref = blackbox
    self._levels = levels

  def prepare_problem(self):
    lb, ub = self._blackbox_ref().variables_bounds()
    for l, u, lv, nm in zip(lb, ub, self._levels, self._blackbox_ref().variables_names()):
      if lv:
        self.add_variable(lv, name=nm, hints={'@GT/VariableType': 'Discrete'})
      else:
        self.add_variable((l, u), name=nm)

    for nm in self._blackbox_ref().objectives_names():
      self.add_objective(name=nm)

    if self._blackbox_ref().gradients_enabled:
      size_x, size_f = self._blackbox_ref().size_x(), self._blackbox_ref().size_f()
      if self._blackbox_ref().gradients_order == GTIBB_GRADIENT_F_ORDER:
        sparse = _numpy.repeat([i for i in range(size_f)], size_x).tolist(), _numpy.tile([i for i in range(size_x)], size_f).tolist()
      else:
        sparse = _numpy.tile([i for i in range(size_f)], size_x).tolist(), _numpy.repeat([i for i in range(size_x)], size_f).tolist()
      self.enable_objectives_gradient(sparse=sparse)

    try:
      # there is no public way to test history mode, so wrap it
      if not self._blackbox_ref()._history_inmemory and self._blackbox_ref()._history_file is None:
        self.disable_history()
    except:
      pass

  def evaluate(self, x, mask):
    problem = self._blackbox_ref()
    resp = problem._evaluate(x)

    last_error = getattr(problem, "_last_error", None)
    if last_error:
      setattr(problem, "_last_error", None)
      setattr(self, "_last_error", last_error)

    return resp, _numpy.ones_like(resp, dtype=bool)

class _WrappedModelAsProblem(_ProblemGeneric):
  def __init__(self, model, x_info, f_info, has_grad):
    super(_WrappedModelAsProblem, self).__init__()

    self._model = model
    self._x_info = x_info
    self._f_info = f_info
    self._has_grad = has_grad

  def prepare_problem(self):
    for info in self._x_info:
      self.add_variable(**info)

    for info in self._f_info:
      self.add_objective(**info)

    if self._has_grad:
      size_x, size_f = self._model.size_x, self._model.size_f

      nonzero_df = [i for i, info in enumerate(self._model.details.get("Output Variables", [{}] * size_f)) if info.get("veriability", "continuous").lower() == "continuous"]
      nonzero_dx = [i for i, info in enumerate(self._model.details.get("Input Variables", [{}] * size_x)) if info.get("veriability", "continuous").lower() == "continuous"]

      if nonzero_df and nonzero_dx:
        sparse = _numpy.repeat(nonzero_df, len(nonzero_dx)).tolist(), _numpy.tile(nonzero_dx, len(nonzero_df)).tolist()
        self.enable_objectives_gradient(sparse=sparse)

  def evaluate(self, x, mask_in):
    resp = _numpy.empty_like(mask_in, dtype=float)
    mask_out = _numpy.zeros_like(mask_in, dtype=bool)

    size_x, size_f = self.size_x(), self.size_f()
    if mask_in[:, :size_f].any():
      resp[:, :size_f] = self._model.calc(x)
      mask_out[:, :size_f] = True

    if mask_in[:, size_f:].any():
      dfdx = self._model.grad(x).reshape(-1, size_x * size_f)
      has_grad, sparse_grad, nonzero_df, nonzero_dx = self.objectives_gradient()
      if sparse_grad:
        for k, (df, dx) in enumerate(zip(nonzero_df, nonzero_dx)):
          resp[:, size_f+k] = dfdx[:, df*size_x+dx]
      else:
        # dense gradients in f-major order
        resp[:, size_f:] = dfdx[:]
      mask_out[:, size_f:] = True

    return resp, mask_out

  @property
  def model(self):
    return self._model

class _WrappedProblemAsBlackbox(_Blackbox):
  def __init__(self, problem, ignore_objectives=None, custom_bounds=None):
    super(_WrappedProblemAsBlackbox, self).__init__()

    if problem().size_s():
      raise _exceptions.InapplicableTechniqueException("Robust optimization problem does not supported.")

    self._problem_ref = problem
    if not ignore_objectives:
      self._active_objectives = None
    else:
      self._active_objectives = [i for i in range(problem().size_f()) if i not in ignore_objectives]
    self._custom_bounds = custom_bounds

  def prepare_blackbox(self):
    lower_bounds, upper_bounds = self._custom_bounds or self._problem_ref().variables_bounds()
    for name, lb, ub in zip(self._problem_ref().variables_names(), lower_bounds, upper_bounds):
      self.add_variable(bounds=(lb, ub), name=name)

    responses_name = list(self._problem_ref().objectives_names())
    if self._active_objectives is not None:
      responses_name = [responses_name[i] for i in self._active_objectives]

    for name in responses_name:
      self.add_response(name=name)

    if self._problem_ref().objectives_gradient()[0]:
      self.enable_gradients()

    try:
      # there is no public way to test history mode, so wrap it
      if not self._problem_ref()._history_inmemory and self._problem_ref()._history_file is None:
        self.disable_history()
    except:
      pass

  def evaluate(self, points):
    problem = self._problem_ref()
    size_x, size_f, size_c = problem.size_x(), problem.size_f(), problem.size_c()


    mask = _numpy.zeros((len(points), problem.size_full()), dtype=bool)
    mask[:, self._active_objectives or slice(size_f)] = 1

    has_grad, sparse_grad, nonzero_df, nonzero_dx = problem.objectives_gradient()
    if has_grad:
      grad_first = size_f + size_c
      grad_last = grad_first + (len(nonzero_df) if sparse_grad else size_f*size_x)

      if self._active_objectives is None:
        mask[:, grad_first:grad_last] = True
      elif sparse_grad:
        for k in nonzero_df:
          if k in self._active_objectives:
            mask[:, grad_first + k] = True
      else:
        for i in self._active_objectives:
          mask[:, grad_first+i*size_x:grad_first+(i+1)*size_x] = True

    if getattr(self, "_last_error", None):
      resp = _numpy.empty(mask.shape)
      resp.fill(_shared._NONE)
      mask.fill(False)
    else:
      resp, mask = problem._evaluate(points, mask, None)
      resp[~mask] = _shared._NONE

      last_error = getattr(problem, "_last_error", None)
      if last_error:
        setattr(problem, "_last_error", None)
        setattr(self, "_last_error", last_error)

    resp_f = resp[:, self._active_objectives or slice(size_f)]

    if not has_grad:
      return resp_f

    resp_dfdx = resp[:, grad_first:grad_last]
    if sparse_grad:
      if self._active_objectives is not None:
        dfdx = _numpy.zeros((resp.shape[0], len(self._active_objectives)*size_x))
        for src, idx_df, idx_dx in zip(resp_dfdx.T, nonzero_df, nonzero_dx):
          if idx_df in self._active_objectives:
            dfdx[:, self._active_objectives.index(idx_df) * size_x + idx_dx] = src[:]
        return _numpy.hstack((resp_f, dfdx))
      else:
        dfdx = _numpy.zeros((resp.shape[0], size_f*size_x))
        for src, idx_df, idx_dx in zip(resp_dfdx.T, nonzero_df, nonzero_dx):
          dfdx[:, idx_df * size_x + idx_dx] = src[:]
        return _numpy.hstack((resp_f, dfdx))
    else:
      if self._active_objectives is not None:
        return _numpy.hstack([resp_f,] + [resp_dfdx[:, i*size_x:(i+1)*size_x] for i in self._active_objectives])
      elif size_c:
        return _numpy.hstack((resp_f, resp_dfdx[:, :size_f*size_x]))

    return resp[:, :size_f*(1+size_x)]

  @property
  def problem_ref(self):
    return self._problem_ref

  def _make_adaptive_only(self, sample_f):
    if self._active_objectives is not None:
      return self, sample_f

    nonadaptive_objectives = [i for i, kind in enumerate(_read_objectives_type(self._problem_ref(), "adaptive")) if kind != "adaptive"]
    if not nonadaptive_objectives:
      return self, sample_f

    other = _WrappedProblemAsBlackbox(problem=self._problem_ref, ignore_objectives=nonadaptive_objectives, custom_bounds=self._custom_bounds)

    if sample_f is not None:
      sample_f = _shared.as_matrix(sample_f, (None, self.size_f()))
      sample_f = sample_f[:, other._active_objectives]

    return other, sample_f

  def _reconstruct_nonadaptive(self, sample_x, sample_f, initial_sample_x, initial_sample_f):
    if sample_f is None or self._active_objectives is None:
      return sample_f

    problem = self._problem_ref()

    sample_x = _shared.as_matrix(sample_x, shape=(None, problem.size_x()))
    sample_f = _shared.as_matrix(sample_f, shape=(None, len(self._active_objectives)))
    full_sample = _numpy.empty((len(sample_f), problem.size_f()))
    full_sample.fill(_shared._NONE)

    for i, values in zip(self._active_objectives, sample_f.T):
      full_sample[:, i] = values[:]

    try:
      history_records = _numpy.vstack(problem._history_cache)
      history_fields = dict((name, slice(start, stop)) for name, start, stop in problem._history_fields[0])

      undefined_sample = _shared._find_holes(full_sample)

      history_x = history_records[:, history_fields["x"]]
      history_f = history_records[:, history_fields["f"]]

      if initial_sample_f is not None:
        history_x = _numpy.vstack((history_x, initial_sample_x))
        history_f = _numpy.vstack((history_f, initial_sample_f))

      known_history = ~_shared._find_holes(history_f)

      if history_x.shape == sample_x.shape and (history_x == sample_x).all():
        undefined_sample = undefined_sample & known_history
        full_sample[undefined_sample] = history_f[undefined_sample]
      elif problem._payload_objectives:
        join_encoded_payloads = problem._payload_storage.join_encoded_payloads

        for k in problem._payload_objectives:
          undefined_sample[:, k] = False
          known_history[:, k] = False

        for i, j in _shared._enumerate_equal_keys(sample_x, history_x):
          undefined_sample_i = undefined_sample[i]
          full_sample[i][undefined_sample_i] = history_f[j, undefined_sample_i]
          undefined_sample_i[known_history[j]] = False
          for k in problem._payload_objectives:
            full_sample[i, k] = join_encoded_payloads(full_sample[i, k], history_f[j, k])
      else:
        for i, j in _shared._enumerate_equal_keys(sample_x, history_x):
          undefined_sample_i = undefined_sample[i]
          full_sample[i][undefined_sample_i] = history_f[j, undefined_sample_i]
          undefined_sample_i[known_history[j]] = False
    except:
      pass

    return full_sample

class _WrappedModelAsBlackbox(_Blackbox):
  def __init__(self, model, x_info, f_info, has_grad):
    super(_WrappedModelAsBlackbox, self).__init__()

    self._model = model
    self._x_info = x_info
    self._f_info = f_info
    self._has_grad = has_grad

  def prepare_blackbox(self):
    for info in self._x_info:
      self.add_variable(**info)

    for info in self._f_info:
      self.add_response(**info)

    if self._has_grad:
      self.enable_gradients()

  def evaluate(self, points):
    resp = self._model.calc(points).reshape(-1, self.size_f())

    if self.gradients_enabled:
      grad = self._model.grad(points).reshape(-1, self.size_f() * self.size_x())
      return _numpy.hstack((resp, grad))

    return resp

  @property
  def model(self):
    return self._model

def preprocess_blackbox(blackbox, location, user_catvars, constraints_supporter=None):
  if blackbox is None:
    raise ValueError(location + " requires blackbox.")

  if isinstance(blackbox, _Blackbox):
    if not user_catvars:
      return blackbox, [], [], ["Continuous"]*blackbox.size_x()
    vartypes = ["Continuous"]*blackbox.size_x()
    for i in user_catvars[::2]:
      vartypes[i] = "Categorical"
    return blackbox, user_catvars, [], vartypes

  if isinstance(blackbox, _ProblemGeneric):
    bounds, problem_catvars, warns, vartypes = _preprocess_problem(blackbox, (user_catvars or []), location, False)
    if user_catvars is None and problem_catvars:
      raise _exceptions.WrongUsageError('Categorical and discrete variables are not supported by ' + location)
    return _WrappedProblemAsBlackbox(_weakref.ref(blackbox), custom_bounds=bounds), problem_catvars, warns, vartypes

  try:
    model, x_info, f_info, _, problem_catvars, has_grad, warns, _ = _preprocess_model(blackbox, None, (user_catvars or []), location, False, False)
    if user_catvars is None and problem_catvars:
      raise _exceptions.WrongUsageError('Categorical and discrete variables are not supported by ' + location)

    var_mapping = {"enumeration": "Categorical", "set": "Discrete"}
    vartypes = [var_mapping.get(input_info.get("variability", "").lower(), "Continuous") \
                for input_info in model.details.get("Input Variables", [])]

    return _WrappedModelAsBlackbox(model, x_info, f_info, has_grad), problem_catvars, warns, vartypes
  except TypeError:
    pass

  raise TypeError(location + " does not support blackbox of type %s" % type(blackbox))

def _classify_regr_model_1D(model, catvars, weights):
  effective_model = model[weights != 0.]

  term_pow = _numpy.zeros(model.shape[0])
  for var_idx, var_spec in enumerate(effective_model.T):
    if var_idx not in catvars:
      term_pow += var_spec # update terms power
    elif not _numpy.isnan(var_spec).all() and _numpy.ptp(var_spec[~_numpy.isnan(var_spec)]) > 0:
      return None # there are more than one active categorical terms, dependency is discontinuous
  return {0.: 'Linear', 1.: 'Linear', 2.: 'Quadratic'}.get(term_pow.max(), None)

def _preprocess_model(model, bounds, catvars, location, strict_categorical, allow_catouts):
  from ..gtapprox import Model as _ApproxModel
  from ..gtdf import Model as _DFModel

  warns = []
  if isinstance(model, _DFModel):
    model = _ApproxModel(string=model.tostring())

  if not isinstance(model, _ApproxModel):
    raise TypeError("The model given must be either %s or %s: %s is given" % (_ApproxModel, _DFModel, (None if model is None else type(model)),))

  size_x = model.size_x

  input_vars = model.details.get("Input Variables", [{}] * size_x)
  output_vars = model.details.get("Output Variables", [{}] * model.size_f)

  if bounds is None:
    bounds = _numpy.empty((2, size_x))
    bounds[0].fill(_numpy.inf)
    bounds[1].fill(-_numpy.inf)

    # Use min/max from the training sample
    for domain in model._training_domains:
      domain = domain.get("Input", {})
      bounds[0] = _numpy.nanmin((bounds[0], domain.get("Min", bounds[0])), axis=0)
      bounds[1] = _numpy.nanmax((bounds[1], domain.get("Max", bounds[0])), axis=0)

    # Basically, use user-defined variable bounds, if any
    for k, var_info in enumerate(input_vars):
      var_min, var_max = var_info.get("min", -_numpy.inf), var_info.get("max", _numpy.inf)
      bounds[0, k] = var_min if _numpy.isfinite(var_min) else bounds[0, k]
      bounds[1, k] = var_max if _numpy.isfinite(var_max) else bounds[1, k]

    try:
      # Try to interpret simple constraints: just box bounds on variables
      input_constraints = model.details.get("Input Constraints", {})

      # No categorical variables, it makes all messy
      box_constraints = input_constraints and not input_constraints['categorical']

      if box_constraints:
        # All terms must be input variables, i.e. input_constraints["model"] must be identity (or permutation) matrix.
        # The weights matrix must be square permutation matrix of size len(input_constraints["model"]) which is the number of conditions.
        terms_model = input_constraints["model"] # alias for simplicity
        terms_weights = input_constraints["weights"] # alias for simplicity
        box_constraints = len(terms_model) == len(terms_weights) # The number of conditions must be equal to the number of terms
        if box_constraints:
          model_term_index, input_index = _numpy.nonzero(terms_model)
          condition_index, condition_term_index = _numpy.nonzero(terms_weights)
          box_constraints = len(model_term_index) == len(terms_model) \
                        and len(condition_index) == len(terms_weights) \
                        and len(model_term_index) == len(_numpy.unique(model_term_index)) \
                        and len(condition_index) == len(_numpy.unique(condition_index)) \
                        and (terms_model[model_term_index, input_index] == 1).all() \
                        and (terms_weights[condition_index, condition_term_index] == 1).all()
          # in general case we must link condition_index and input_index by the model_term_index/condition_term_index key
          inputs_map = _numpy.empty_like(model_term_index) # map buffer
          inputs_map[model_term_index] = input_index # map inputs to terms
          input_index = inputs_map[condition_term_index] # link inputs to conditions

      if box_constraints:
        # RPN formula must be simple conjunction of size_x constraints (one constraint per input variable)
        # Conjunction in RPN form may be performed in any order, so we re-sort actual formula like "push all, then conjugate all"
        box_constraints = sorted(input_constraints["rpn_formula"], key=lambda x: _numpy.inf if x == 'and' else x) \
                       == (sorted(condition_term_index) + ["and"]*(len(condition_term_index) - 1))

      # Now we can read bounds and put these bounds in the proper order
      if box_constraints:
        # Note order of variables in the lower_bound/upper_bound may differ from the variables order
        lower_bound = input_constraints.get('lower_bound', [-_numpy.inf]*model.size_x)
        upper_bound = input_constraints.get('upper_bound', [_numpy.inf]*model.size_x)
        for i, k in zip(condition_index, input_index):
          bounds[0, k] = lower_bound[i] if _numpy.isfinite(lower_bound[i]) else bounds[0, k]
          bounds[1, k] = upper_bound[i] if _numpy.isfinite(upper_bound[i]) else bounds[1, k]
    except:
      pass
  else:
    bounds = _shared.as_matrix(bounds, (2, size_x), name="'bounds' argument", detect_none=True)


  if not allow_catouts and any(info.get("variability", "").lower() == "enumeration" for info in output_vars):
    raise _exceptions.UnsupportedProblemError(location + " does not support categorical outputs.")

  x_info = [{"name": info.get("name", "x[%d]" % i), "bounds": (lb, ub)} for i, (info, lb, ub) in enumerate(zip(input_vars, bounds[0], bounds[1]))]
  f_info = [{"name": info.get("name", "f[%d]" % i)} for i, info in enumerate(output_vars)]

  categorical_kinds = ("enumeration",) if strict_categorical else ("enumeration", "set")
  vartypes = ["Continuous"]*size_x

  if catvars and not any(info.get("variability", "").lower() in categorical_kinds for info in input_vars):
    # if thiere is no categorical inputs then just override, otherwise check compatibility
    for i, user_levels in zip(catvars[::2], catvars[1::2]):
      warns.append("The `GTDoE/CategoricalVariables` option overrides type of model input #%d (%s)." % (i, x_info[i]["name"],))
      vartypes[i] = "Categorical"
  else:
    model_catvars = []
    for i, (info_dst, info_src, user_levels) in enumerate(zip(x_info, input_vars, _convert_catvars_to_levels(catvars, size_x))):
      if info_src.get("variability", "continuous").lower() not in ("continuous", "neglected",):
        try:
          input_levels = [float(_) for _ in info_src.get("enumerators", _numpy.unique(info_dst["bounds"]))]
        except:
          _shared.reraise(_exceptions.UnsupportedProblemError, "The DoE does not support categorical variables with textual labels.", _sys.exc_info[-1])

        if user_levels:
          invalid_levels = [_ for _ in user_levels if _ not in input_levels]
          if invalid_levels:
            raise _exceptions.InvalidOptionValueError("The `GTDoE/CategoricalVariables` option specifies invalid level for model input #%d (%s): %s." % (i, info_dst["name"], invalid_levels))
          elif len(input_levels) != len(user_levels):
            warns.append("The `GTDoE/CategoricalVariables` option overrides levels of model input #%d (%s)." % (i, info_dst["name"],))
            input_levels = user_levels
        model_catvars.extend((i, input_levels))
        vartypes[i] = "Categorical" if info_src.get("variability", "continuous").lower() == "enumeration" else "Stepped"
      elif user_levels:
        # user may override type of continuous input
        warns.append("The `GTDoE/CategoricalVariables` option overrides type of model input #%d (%s)." % (i, info_dst["name"],))
        model_catvars.extend((i, user_levels))
        vartypes[i] = "Categorical"
    catvars = model_catvars

  # Enable gradients only if all inputs and outputs are continuous
  no_grad_techs = ("tbl", "gbrt",)
  has_grad = str(model.details.get("Technique", "auto")).lower() not in no_grad_techs \
           and all(str(info.get("Technique", "auto")).lower() not in no_grad_techs for info in model.details.get("Model Decomposition", [])) \
           and all(info.get("variability", "continuous").lower() in ("continuous", "neglected") for info in input_vars) \
           and all(info.get("variability", "continuous").lower() in ("continuous", "constant") for info in output_vars)

  return model, x_info, f_info, _postprocess_bounds(bounds, catvars), catvars, has_grad, warns, vartypes

def _model_as_problem(model, bounds, catvars, location, allow_catouts=False):
  model, x_info, f_info, bounds, catvars, has_grad, warns, vartypes = _preprocess_model(model, bounds, catvars, location, False, allow_catouts=allow_catouts)

  # Note due to Blackbox compatibility reasons, x_info contains only "name" and 2-value "bounds" fields

  # add hints
  for i, variable_type in enumerate(vartypes):
    x_info[i]["hints"] = {"@GT/VariableType": variable_type}

  # assign proper levels for categorical variables
  for i, user_levels in zip(catvars[::2], catvars[1::2]):
    assert vartypes[i].lower() == "categorical"
    x_info[i]["bounds"] = user_levels

  # Detect linear responses
  try:
    regr_model = model.details.get("Regression Model", {})
    if regr_model:
      for i, weights_i in enumerate(regr_model.get("weights", [])):
        regr_kind = _classify_regr_model_1D(regr_model["model"], regr_model.get("categorical", {}), weights_i)
        if regr_kind:
          f_info[i]["hints"] = {'@GTOpt/LinearityType': regr_kind}
    else:
      model_decomp = model.details.get("Model Decomposition", [])
      for submodel in model_decomp:
        regr_model = model.details.get("Regression Model", {})
        for i, weights_i in enumerate(regr_model.get("weights", [])):
          # test that i-th output explained by this model olny
          if _numpy.count_nonzero(i in _.get("Dependent Outputs", []) for _ in model_decomp) == 1:
            regr_kind = _classify_regr_model_1D(regr_model["model"], regr_model.get("categorical", {}), weights_i)
            if regr_kind:
              f_info[i]["hints"] = {'@GTOpt/LinearityType': regr_kind}
  except:
    pass

  return _WrappedModelAsProblem(model, x_info, f_info, has_grad), warns

def _model_as_blackbox(model, bounds, catvars, location):
  model, x_info, f_info, bounds, catvars, has_grad, warns, vartypes = _preprocess_model(model, bounds, catvars, location, False, False)
  return _WrappedModelAsBlackbox(model, x_info, f_info, has_grad), bounds, catvars, warns, vartypes

def _convert_catvars_to_levels(catvars, nvars):
  levels = [[]]*nvars

  if catvars is None:
    return levels

  catvars = [_ for _ in catvars]
  if (len(catvars) % 1):
    raise ValueError("Invalid categorical variables description")

  for i, vals in zip(catvars[::2], catvars[1::2]):
    try:
      i = int(i)
      vals = [float(x) for x in vals]
    except:
      exc_info = _sys.exc_info()
      _shared.reraise(ValueError, "Invalid categorical variables description (%s): %s" % (exc_info[0], exc_info[1],), exc_info[2])

    if i < 0 or i >= nvars:
      raise ValueError("Invalid categorical variables description: variable index %d is out of valid bounds [0, %d)." % ())
    levels[i] = vals

  return levels

def _preprocess_problem(problem, user_catvars, location, strict_categorical):
  problem._validate()

  if problem.size_s():
    raise _exceptions.UnsupportedProblemError(location + " does not support stochastic problems.")

  if problem.size_nc() or problem.size_nf():
    raise _exceptions.UnsupportedProblemError(location + " does not support blackbox noise.")

  size_x = problem.size_x()

  warns = []
  vartypes = []
  lower_bounds, upper_bounds = problem.variables_bounds()
  categorical_kinds = ("Categorical",) if strict_categorical else ("Discrete", "Categorical", "Stepped")
  problem_catvars, problem_catvars_bounds = {}, {}
  for i, kind in enumerate(problem.elements_hint(slice(size_x), '@GT/VariableType')):
    if isinstance(kind, string_types):
      kind = kind[:1].upper() + kind[1:].lower() # capitalize
    if kind in categorical_kinds:
      problem_catvars_bounds[i] = list(problem.variables_bounds(i))
      problem_catvars[i] = problem_catvars_bounds[i]
    vartypes.append(kind or "Continuous")

  if user_catvars:
    varnames = problem.variables_names()
    for i, user_levels in zip(user_catvars[::2], user_catvars[1::2]):
      problem_levels = problem_catvars_bounds.get(i, [])
      if not problem_levels:
        warns.append("The `GTDoE/CategoricalVariables` option overrides type of variable #%d (%s)." % (i, varnames[i]))
      else:
        invalid_levels = [_ for _ in user_levels if _ not in problem_levels]
        if invalid_levels:
          raise _exceptions.InvalidOptionValueError("The `GTDoE/CategoricalVariables` option specifies invalid level for variable #%d (%s): %s." % (i, varnames[i], invalid_levels))
        elif len(user_levels) != len(problem_levels):
          warns.append("The `GTDoE/CategoricalVariables` option overrides levels of variable #%d (%s)." % (i, varnames[i],))

      if problem.elements_hint(i, '@GT/FixedValue') is not None:
        warns.append("Levels set for fixed variable #%d (%s) in `GTDoE/CategoricalVariables` option are ignored." % (i, varnames[i]))
      else:
        problem_catvars[i] = user_levels
        lower_bounds[i], upper_bounds[i] = min(problem_catvars[i]), max(problem_catvars[i])

      vartypes[i] = "Categorical"

  catvars = []
  for i in problem_catvars:
    catvars.extend((i, problem_catvars[i]))

  return (lower_bounds, upper_bounds), catvars, warns, vartypes

def _problem_as_blackbox(problem, count, user_catvars, location):
  bounds, user_catvars, warns, vartypes = _preprocess_problem(problem, user_catvars, location, False)

  size_x, size_f = problem.size_x(), problem.size_f()

  if not size_f:
    warns = warns + ["The problem given does not specify objectives. Sample-based mode (without blackbox) will be used.",]
    return None, bounds, user_catvars, warns, vartypes

  min_evals = _numpy.iinfo(int).max
  ignore_objectives = [i for i, kind in enumerate(_read_objectives_type(problem, "adaptive")) if kind != "adaptive"]
  for i, (limit_general, limit_expensive) in enumerate(zip(problem.elements_hint(slice(size_x, None), '@GT/EvaluationLimit'), \
                                                           problem.elements_hint(slice(size_x, None), '@GT/ExpensiveEvaluations'))):
    if i in ignore_objectives:
      continue
    limit_general = problem._parse_evaluations_limit(limit_general)
    if limit_general >= 0:
      min_evals = min(min_evals, limit_general)
    limit_expensive = problem._parse_evaluations_limit(limit_expensive)
    if limit_expensive >= 0:
      min_evals = min(min_evals, limit_expensive)

  if min_evals < count:
    warns = warns + [location + " supports only modes with unrestricted blackbox and without blackbox (sample-based mode). " + \
                     "Evaluations for some of objectives is explicitly set less than `count`. Sample-based mode (without blackbox) will be used.",]
    return None, bounds, user_catvars, warns, vartypes

  return _WrappedProblemAsBlackbox(_weakref.ref(problem), custom_bounds=bounds), bounds, user_catvars, warns, vartypes

@_contextlib.contextmanager
def _as_problem_generic(blackbox, catvars, location, logger, init_y=None):
  if blackbox is None:
    raise ValueError(location + " requires blackbox.")

  if isinstance(blackbox, _WrappedProblemAsBlackbox) and blackbox._evaluate is _WrappedProblemAsBlackbox._evaluate:
    problem_generic = blackbox.problem_ref()
  elif isinstance(blackbox, _ProblemGeneric):
    problem_generic = blackbox
  else:
    problem_generic = None

  if problem_generic is not None:
    if not catvars:
      yield problem_generic
      return

    problem_catvars = dict((i, problem_generic.variables_bounds(i)) for i, variable_type in enumerate(problem_generic.elements_hint(slice(problem_generic.size_x()), "@GT/VariableType")) if str(variable_type).lower() == "categorical")

    warns = []
    vars_hints_update = [{}]*problem_generic.size_x()
    vars_name = problem_generic.variables_names() if catvars else []

    for i in catvars[::2]:
      if i not in problem_catvars:
        vars_hints_update[i] = {"@GT/VariableType": "Categorical"}
        warns.append("The `GTDoE/CategoricalVariables` option overrides type of variable #%d (%s)." % (i, vars_name[i],))

    with problem_generic._solve_as_subproblem(vars_hints_update, None, None, doe_mode=True):
      for i, user_levels in zip(catvars[::2], catvars[1::2]):
        if i not in problem_catvars: # override type of variable, just override
          problem_generic.set_variable_bounds(i, user_levels)
        else:
          original_levels = problem_generic.variables_bounds(i)
          invalid_levels = [_ for _ in user_levels if _ not in original_levels]
          if invalid_levels:
            raise _exceptions.InvalidOptionValueError("The `GTDoE/CategoricalVariables` option specifies invalid level for variable #%d (%s): %s." % (i, vars_name[i], invalid_levels))
          elif len(original_levels) != len(user_levels):
            warns.append("The `GTDoE/CategoricalVariables` option overrides levels of variable #%d (%s)." % (i, vars_name[i],))
            problem_generic.set_variable_bounds(i, user_levels)

      _log_warnings(logger, warns)
      yield problem_generic # forward modified problem

    return

  if isinstance(blackbox, _WrappedModelAsBlackbox) and blackbox._evaluate is _WrappedModelAsBlackbox._evaluate:
    problem_generic, warns = _model_as_problem(blackbox.model, None, catvars, location)
  elif _shared.is_sized(blackbox):
    limits = _shared.as_matrix(blackbox, shape=(2, None), detect_none=True, name="design space bounds (lower, upper)")
    problem_generic, warns = _BoxProblem(limits=limits, levels=_convert_catvars_to_levels(catvars, limits.shape[1]),\
                                         size_f=(0 if init_y is None else _numpy.shape(init_y)[1])), []
  elif isinstance(blackbox, _Blackbox):
    problem_generic, warns = _WrappedBlackboxAsProblem(_weakref.ref(blackbox), _convert_catvars_to_levels(catvars, blackbox.size_x())), []
  else:
    try:
      problem_generic, warns = _model_as_problem(blackbox, None, catvars, location)
    except TypeError:
      pass

  if problem_generic is None:
    raise TypeError(location + " does not support blackbox of type %s" % type(blackbox))

  _log_warnings(logger, warns)
  yield problem_generic

def _log_warnings(logger, warnings):
  if not logger or not warnings:
    return

  from ..loggers import LogLevel
  for message in warnings:
    logger(LogLevel.WARN, message)

def _postprocess_bounds(bounds, catvars):
  bounds = _shared.as_matrix(bounds, shape=(2, None), detect_none=True, name="design space bounds (lower, upper)")

  # overwrite categorical variables bounds
  for index, levels in zip(catvars[::2], catvars[1::2]):
    bounds[0, index] = _numpy.nanmin(levels)
    bounds[1, index] = _numpy.nanmax(levels)

  return bounds

def _make_blackbox(blackbox, count, user_catvars, location):
  """
  Returns tuple (blackbox, bounds, catvars, warns, var_types), where
      blackbox is either `da.p7core.blackbox.Blackbox` or `None`
      bounds is a matrix with 2 rows
      catvars is a `list` that specifies categorical variables in the "GTDoE/CategoricalVariables" option format
      warns is a `list` of warnings `str`
      var_types is a `list` with more specific types of variables in the "/GTDoE/VariablesType" option format
  """
  if blackbox is None:
    raise ValueError(location + " requires blackbox.")

  if _shared.is_sized(blackbox):
    # no blackbox, sample-based mode
    bounds = _shared.as_matrix(blackbox, shape=(2, None), detect_none=True, name="design space bounds (lower, upper)")
    return None, _postprocess_bounds(bounds, user_catvars), user_catvars, [], []
  elif isinstance(blackbox, _Blackbox):
    # direct blackbox mode
    return blackbox, blackbox.variables_bounds(), user_catvars, [], []
  elif isinstance(blackbox, _ProblemGeneric):
    return _problem_as_blackbox(blackbox, count, user_catvars, location)

  try:
    return _model_as_blackbox(blackbox, None, user_catvars, location)
  except TypeError:
    pass

  raise TypeError(location + " does not support blackbox of type %s" % type(blackbox))

def _ignore_reponses_message(technique_name):
  return "`%s` is a space-filling DoE technique, which does not analyze behavior of responses." % (technique_name,)

def _make_location(technique_name):
  return "The `%s` DoE technique" % (technique_name,)

def _make_bounds(blackbox, user_catvars, technique_name):
  """
  Returns tuple (bounds, catvars, warns, var_types), where
      bounds is a matrix with 2 rows
      catvars is a `list` that specifies categorical variables in the "GTDoE/CategoricalVariables" option format
      warns is a `list` of warnings `str`
      var_types is a `list` with more specific types of variables in the "/GTDoE/VariablesType" option format
  """
  if blackbox is None:
    raise ValueError("`" + str(technique_name) + "` is a space-filling DoE technique, which requires generation bounds.")

  if _shared.is_sized(blackbox):
    bounds = _shared.as_matrix(blackbox, shape=(2, None), detect_none=True, name="design space bounds (lower, upper)")
    vartypes = ["Continuous",]*bounds.shape[1]
    for i in user_catvars[::2]:
      vartypes[i] = "Categorical"
    return _postprocess_bounds(bounds, user_catvars), user_catvars, [], vartypes
  elif isinstance(blackbox, _Blackbox):
    # direct blackbox mode
    return blackbox.variables_bounds(), user_catvars, ([_ignore_reponses_message(technique_name),] if blackbox.size_f() else []), []
  elif isinstance(blackbox, _ProblemGeneric):
    bounds, user_catvars, warns, vartypes = _preprocess_problem(blackbox, user_catvars, _make_location(technique_name), (technique_name.lower() == "fractionalfactorial"))
    if blackbox.size_f():
      warns.append(_ignore_reponses_message(technique_name))
    return bounds, user_catvars, warns, vartypes

  try:
    _, _, _, bounds, catvars, _, warns, vartypes = _preprocess_model(blackbox, None, user_catvars, _make_location(technique_name), (technique_name.lower() == "fractionalfactorial"), True)
    return bounds, catvars, warns + [_ignore_reponses_message(technique_name),], vartypes
  except TypeError:
    pass

  raise TypeError("`%s` is a space-filling DoE technique, which does not support blackbox of type %s." % (technique_name, type(blackbox)))

def _make_result_compatible(blackbox, catvars=None, location=None, size_f=None):
  # And here we go again: blackbox object must be ProblemGeneric or, at least, have variables_names, objectives_names and constraints_names methods
  if blackbox is None:
    return None

  try:
    if isinstance(blackbox, _WrappedProblemAsBlackbox) and blackbox._evaluate is _WrappedProblemAsBlackbox._evaluate:
      return blackbox.problem_ref()
    elif isinstance(blackbox, _ProblemGeneric):
      return blackbox
    elif isinstance(blackbox, _WrappedModelAsBlackbox) and blackbox._evaluate is _WrappedModelAsBlackbox._evaluate:
      return _model_as_problem(blackbox.model, None, catvars, location, allow_catouts=True)[0]
    elif _shared.is_sized(blackbox):
      limits = _shared.as_matrix(blackbox, shape=(2, None), detect_none=True, name="design space bounds (lower, upper)")
      return _BoxProblem(limits=limits, levels=_convert_catvars_to_levels(catvars, limits.shape[1]), size_f=(size_f or 0))
    elif isinstance(blackbox, _Blackbox):
      return _WrappedBlackboxAsProblem(_weakref.ref(blackbox), _convert_catvars_to_levels(catvars, blackbox.size_x()))
    return _model_as_problem(blackbox, None, catvars, location, allow_catouts=True)[0]
  except:
    pass
  return None

