#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import with_statement
from __future__ import division

import sys as _sys
from  datetime import datetime as _datetime
import numpy as _numpy

from ..loggers import LogLevel as _LogLevel
from ..six.moves import xrange
from ..shared import as_matrix as _as_matrix
from ..shared import _SHALLOW

from .. import exceptions as _ex

def find_linear_dependencies(y, rrms_threshold, log=None, y_name=None, weights=None, refine_rrms_threshold=True, seed=None, nan_mode=None, mapping=None, search_groups=None):
  finite_y_mask = _numpy.isfinite(y).all(axis=1)
  if not finite_y_mask.all():
    if nan_mode is None or nan_mode.lower() == 'raise':
      raise _ex.NanInfError('Invalid (NaN or Inf) values are found in output part of the training sample.')
    y = y[finite_y_mask]
    if weights is not None:
      weights = weights[finite_y_mask]

  if y.shape[0] < y.shape[1]:
    if log is not None:
      log(_LogLevel.WARN, "There is not enough points to estimate dependencies between outputs: %d points are given while data are %d-dimensional" % (y.shape[0], y.shape[1]))
    return [_ for _ in xrange(y.shape[1])], None, None

  if mapping is not None:
    mapping = mapping.lower()
    if mapping == "none":
      mapping = None

  if search_groups:
    normalized_groups = []
    for explanatory_outputs in search_groups:
      explanatory_outputs = sorted([_ for _ in explanatory_outputs])
      if explanatory_outputs:
        if any((_ < 0 or _ >= y.shape[1]) for _ in explanatory_outputs):
          raise _ex.InvalidOptionsError("Output index is out of valid [0, %d) range in the dependent outputs search group %s" % (y.shape[1], search_groups))
        normalized_groups.append(explanatory_outputs)
    search_groups = normalized_groups

  analyzer = DependenciesAnalyzer(y, log, y_name, weights, mapping=mapping)
  return analyzer.analyze(rrms_threshold, refine_rrms_threshold, seed, search_groups)

def _linear_regression_string(terms, weights):
  def _linear_regression_addend(term, weight):
    if weight == 0.:
      return ""
    elif term == "1":
      return "%+.16g" % weight
    elif _numpy.fabs(_numpy.fabs(weight) - 1.) < 4.*DependenciesAnalyzer.EPS:
      return ("-%s" % term) if weight < 0. else ("+%s" % term)
    return "%+.16g*%s" % (weight, term)

  model = "".join([_linear_regression_addend(t, w) for t, w in zip(terms, weights)])
  if model.startswith("+"):
    model = model[1:]
  return model if model else "0"

def _batchify(nin, nout, dtype):
  def wrap_batch(func):
    func_batch = _numpy.frompyfunc(func, 2, 1)
    def wrap_dtype(*args, **kwargs):
      result = func_batch(*args, **kwargs)
      try:
        return result.astype(dtype)
      except:
        pass
      return dtype(result)
    return wrap_dtype
  return wrap_batch

@_batchify(2, 1, float)
def _round(x, n_dig, tiny=_numpy.finfo(float).tiny, limit=int(-_numpy.log10(_numpy.finfo(float).tiny))):
  n_dig = n_dig - 1 - int(_numpy.floor(_numpy.log10(_numpy.maximum(_numpy.fabs(x), tiny))))
  return round(x, min(limit, max(-limit, n_dig)))

class _OutputInfo(object):
  VAR_CONSTANT = "constant"
  VAR_EXPLAINED = "explained"
  VAR_INDEPENDENT = "independent"
  VAR_CONSTRAINED = "constrained"

  def __init__(self, rrms, explanatory_vars, explanatory_weights, intercept, variable_type, divergence_ratio, fixed=False):
    explanatory_vars = [] if explanatory_vars is None else [_ for _ in explanatory_vars]
    explanatory_weights = [] if explanatory_weights is None else [float(_) for _ in explanatory_weights]

    assert len(explanatory_vars) == len(explanatory_weights)

    # Sort variables indices and filter out zero weights
    vars_order = _numpy.argsort(explanatory_vars)
    self.explanatory_vars = [explanatory_vars[k] for k in vars_order if explanatory_weights[k] != 0.]
    self.explanatory_weights = [explanatory_weights[k] for k in vars_order if explanatory_weights[k] != 0.]

    # Note if explanatory_vars is not empty while all weights are zero and intercept is None then we must use zero intercept
    self.intercept = float(intercept) if intercept is not None else 0. if self.explanatory_vars else None

    self.rrms = 0. if rrms is None else max(0., _as_matrix(rrms, shape=(1,1), name="rrms")[0,0]) # Conversion of an array with ndim > 0 to a scalar is deprecated since NumPy 1.25
    self.mode = variable_type
    self.divergence_ratio = (1., 1.) if divergence_ratio is None else (float(divergence_ratio[0]), float(divergence_ratio[1]))
    self.fixed = fixed

  def __getstate__(self):
    return {"explanatory_vars": self.explanatory_vars,
            "explanatory_weights": self.explanatory_weights,
            "intercept": self.intercept,
            "rrms": self.rrms,
            "mode": self.mode,
            "divergence_ratio": self.divergence_ratio,
            "fixed": self.fixed}

  def __setstate__(self, state):
    self.explanatory_vars = state.get("explanatory_vars", [])
    self.explanatory_weights = state.get("explanatory_weights", [])
    self.intercept = state.get("intercept", None)
    self.rrms = state.get("rrms", None)
    self.mode = state.get("mode", None)
    self.divergence_ratio = state.get("divergence_ratio", (1., 1.))
    self.fixed = state.get("fixed", self.mode not in (None, self.VAR_CONSTRAINED))

  def __repr__(self):
    if self.is_independent():
      return "<independent>"

    terms, weights = ([], []) if not self.intercept else (["1"], [self.intercept])
    terms.extend(("z[%d]" % i) for i in self.explanatory_vars)
    weights.extend(self.explanatory_weights)

    mode = "[E] "if self.mode in (self.VAR_EXPLAINED, self.VAR_CONSTANT) else "[C] " if self.mode == self.VAR_CONSTRAINED else "[?] "

    divergence = (" div=%g...%g" % self.divergence_ratio) if not all(_ in(0., 1., _numpy.inf) for _ in self.divergence_ratio) else ""
    accuracy = ("(rrms=%g%s) " % (self.rrms, divergence)) if self.rrms else ""
    explanation = _linear_regression_string(terms, weights)

    return "%s%s=%s" % (mode, accuracy, explanation)

  def is_independent(self):
    if self.mode is None:
      return not self.explanatory_vars and self.intercept is None
    return self.mode == self.VAR_INDEPENDENT

  def equal(self, other):
    if self is other:
      return True
    elif other is None:
      return False
    return self.mode == other.mode and self.intercept == other.intercept and self.explanatory_vars == other.explanatory_vars \
        and _numpy.allclose(self.explanatory_weights, other.explanatory_weights, rtol=_numpy.finfo(float).eps**0.5, atol=0.)

  @staticmethod
  def constant(value, rrms=None):
    return _OutputInfo(rrms, [], [], value, _OutputInfo.VAR_CONSTANT, divergence_ratio=(1., 1.), fixed=True)

  @staticmethod
  def independent():
    return _OutputInfo(None, [], [], None, _OutputInfo.VAR_INDEPENDENT, divergence_ratio=(0., 0.), fixed=True)

class _MapTransform(object):
  def __init__(self, y, kind):
    if kind == "mapstd":
      self.bias = _numpy.mean(y, axis=0).reshape(1, -1)
      self.rscale = _numpy.std(y, ddof=1, axis=0).reshape(1, -1)
    elif kind == "mapminmax":
      self.bias = _numpy.min(y, axis=0).reshape(1, -1)
      self.rscale = _numpy.ptp(y, axis=0).reshape(1, -1)
    else:
      raise ValueError("Invalid data mapping algorithm is given: %s." % (kind,))

    self.rscale[self.rscale < _numpy.finfo(float).eps] = 0.
    self.fscale = _numpy.zeros(self.rscale.shape)
    self.fscale[self.rscale > 0.] = 1. / self.rscale[self.rscale > 0.]

  def fwd(self, y, inplace=False):
    y_norm = y if inplace else _numpy.empty(y.shape)
    return _numpy.multiply(_numpy.subtract(y, self.bias, out=y_norm), self.fscale, out=y_norm)

  def rev(self, y, inplace=False):
    y_norm = y if inplace else _numpy.empty(y.shape)
    return _numpy.add(_numpy.multiply(y, self.rscale, out=y_norm), self.bias, out=y_norm)

  def output(self, output_index, output_info):
    if output_info is None:
      return None

    intercept = output_info.intercept if output_info.intercept is not None else 0.

    if output_info.explanatory_weights is not None:
      r_weight = self.rscale[0, output_index]
      explanatory_weights = []
      for e_var, e_weight in zip(output_info.explanatory_vars, output_info.explanatory_weights):
        intercept = intercept - e_weight * self.bias[0, e_var] * self.fscale[0, e_var]
        explanatory_weights.append(e_weight * self.fscale[0, e_var] * r_weight)
    else:
      explanatory_weights = None

    intercept = (intercept * r_weight + self.bias[0, output_index]) if output_info.intercept is not None else None

    return _OutputInfo(rrms=output_info.rrms, explanatory_vars=output_info.explanatory_vars,
                       explanatory_weights=explanatory_weights, intercept=intercept,
                       variable_type=output_info.mode, divergence_ratio=output_info.divergence_ratio,
                       fixed=output_info.fixed)


class DependenciesAnalyzer(object):
  EPS = _numpy.finfo(float).eps

  def __init__(self, y, log, y_name=None, weights=None, mapping=None):
    self.y = _numpy.array(y, ndmin=2, dtype=_numpy.float64, copy=_SHALLOW)

    mapping_kind = "none" if mapping is None else mapping.lower()
    if mapping_kind == "none":
      self.transform = None
    elif mapping_kind in ("mapstd", "mapminmax"):
      self.transform = _MapTransform(self.y, mapping_kind)
      self.y = self.transform.fwd(self.y)
    else:
      raise ValueError("Invalid data mapping algorithm is given: %s." % (mapping,))

    self.n_y = self.y.shape[1]
    self.n_pts = self.y.shape[0]
    self.log = self._null_log if log is None else log
    self.divergence_ratio_threshold = (1, 1.1) # Threshold of the allowed noise divergence ratio in the explained outputs
    self.suppose_correlated_noise = False # Set true if noise would be correlated
    self.minimal_rrms_threshold = _numpy.finfo(_numpy.float32).eps
    self.Y1tWY1 = None
    self.W = None if weights is None else _numpy.array(weights, dtype=_numpy.float64, copy=_SHALLOW).reshape(-1)
    self.std_y = self._stdev(self.y)

    if not y_name:
      self.y_name = [("y[%d]" % i) for i in xrange(self.n_y)]
    else:
      try:
        string_types = basestring
      except:
        string_types = str

      if isinstance(y_name, string_types):
        self.y_name = [("%s[%d]" % (y_name, i)) for i in xrange(self.n_y)]
      else:
        self.y_name = [_ for _ in y_name]
        if len(self.y_name) != self.n_y:
          raise ValueError("The number of features name does not conform features number.")

  def _stdev(self, y):
    if self.W is None:
      return _numpy.std(y, ddof=1, axis=0)
    return _numpy.hypot.reduce(_numpy.multiply(y - _numpy.mean(y, axis=0).reshape(1, -1), self.W.reshape(-1, 1)), axis=0) / self.W.sum()**0.5

  def analyze(self, rrms_threshold, refine_rrms_threshold=True, seed=None, search_groups=None):
    """Search linear dependencies between data columns.

    :param rrms_threshold: RRMS threshold. The i-th data column is explained if RRMS of the linear combination of the other columns is less then the threshold given.
    :param seed: Seed value. Note setting seed value also activates multistart in feature search algorithm (recommended).
    :type rrms_threshold: ``float``
    :type seed: ``int``

    :return: tuple of (explanatory_variables, evaluation_model, constraints)
    :rtype: ``tuple``

    Returns tuple of three elements: explanatory_variables, evaluation_model, constraints

    * explanatory_variables - list of the explanatory variables indices. By definition, contains n_z elements.
    * evaluation_model (A) - 2D numpy array of floats or None. If None then there is no 'explained' columns and order or independent outputs is natural.
      Otherwise it is n_y-by-(n_z + 1) matrix where n_z is the total number of explanatory variables (independent and expanded dependent columns groups).
      The i-th row specifies scheme of i-th column calculation. Let z is the flatten list of explanatory variables,
      then y[i] = dot(A[i, :-1], z) + A[i, -1]
    * constraints - None if there are no constraints otherwise tuple (std_z, std_c, b, R, revR), where
      ** std_z is n_z-dimensional vector of standard deviations of the explanatory variables z;
      ** std_c is n_c-dimensional vector of standard deviations of the constraints equations;
      ** b is n_c-dimensional bias vector (the right part of the constraints)
      ** R is n_c-by-n_z dimensional matrix of the constraints (coefficients of linear equations)
      ** revR is n_c-by-n_z dimensional matrix of the constraints refining
      For a given matrix of explanatory variables Z iterative solution can be Z{i+1} = Z{i} + dot((b - dot(Z{i}, R.T)), revR)
      until some convergence or early stop criteria is met.

    Note one-line code to convert explanatory variables to the flatten list z:
      z = tuple(i for r in ((k if isinstance(k, tuple) else (k,)) for k in explanatory_variables) for i in r)
    """
    time_start = _datetime.now()

    rnd_state = _numpy.random.get_state()
    try:
      _numpy.random.seed(seed)
      fit_multistart = (0 if seed is None else 5)
      outputs_info, rrms_threshold = self._collect_outputs_info(rrms_threshold, refine_rrms_threshold, fit_multistart, search_groups)
      outputs_info = self._postprocess_outputs(outputs_info, rrms_threshold, fit_multistart)
      explanatory_variables, evaluation_model, constraints = self._build_evaluation_scheme(outputs_info)
    finally:
      _numpy.random.set_state(rnd_state)

    if self.log is not self._null_log:
      output_stat = {_OutputInfo.VAR_CONSTANT: 0, _OutputInfo.VAR_EXPLAINED: 0, _OutputInfo.VAR_INDEPENDENT: 0, _OutputInfo.VAR_CONSTRAINED: 0}
      for output in outputs_info:
        output_stat[output.mode] += 1

      time_finish = _datetime.now()
      self._info_log("Analysis done in %s:" % (time_finish - time_start))
      self._info_log("  # of constant outputs:    %d" % output_stat[_OutputInfo.VAR_CONSTANT])
      self._info_log("  # of independent outputs: %d" % output_stat[_OutputInfo.VAR_INDEPENDENT])
      self._info_log("  # of constrained outputs: %d" % output_stat[_OutputInfo.VAR_CONSTRAINED])
      self._info_log("  # of explained outputs:   %d" % output_stat[_OutputInfo.VAR_EXPLAINED])

    return explanatory_variables, evaluation_model, constraints

  def _collect_outputs_info(self, rrms_threshold, refine_rrms_threshold=True, fit_multistart=0, search_groups=None):
    self._info_log("Exploring dependencies using %g RRMS error threshold..." % rrms_threshold)

    self._initialize_regressors()
    outputs_info = [None,]*self.n_y

    fit_multistart = int(fit_multistart) if fit_multistart else 0

    # First stage: collecting constants
    outputs_info = self._collect_constant_outputs(outputs_info)

    if search_groups:
      outputs_info = self._search_withing_groups(outputs_info, search_groups, rrms_threshold, fit_multistart)
    else:
      outputs_info = self._collect_simple_dependencies(outputs_info, rrms_threshold)
      outputs_info, rrms_threshold = self._search_dependencies(outputs_info, rrms_threshold, refine_rrms_threshold, fit_multistart)

    return outputs_info, rrms_threshold

  def _postprocess_outputs(self, outputs_info, rrms_threshold, fit_multistart):
    self._info_log("Postprocessing outputs info...")

    for output_info in outputs_info:
      if output_info.mode is None:
        output_info.mode = _OutputInfo.VAR_CONSTRAINED

    # resolve cross-dependencies and minimize constraints
    outputs_info, group_markers = self._resolve_groups(outputs_info, rrms_threshold, fit_multistart)
    while self._minimize_constraints(outputs_info, group_markers, rrms_threshold):
      outputs_info, group_markers = self._resolve_groups(outputs_info, rrms_threshold, fit_multistart)

    return outputs_info

  def _build_evaluation_scheme(self, outputs_info):
    self._info_log("Building model evaluation scheme...")

    # Simple check: if all variables are independent or constant then say "there is no model"
    if all((output_i.mode in (_OutputInfo.VAR_INDEPENDENT, _OutputInfo.VAR_CONSTANT)) for output_i in outputs_info):
      for i, output_i in enumerate(outputs_info):
        self._info_log(self._stringify_output_info(i, output_i, ignore_accuracy=True, report_constraint=True))
      return [_ for _ in xrange(self.n_y)], None, None

    original_transform = self.transform
    try:
      # apply transform to outputs and temporary mark it as absent
      if self.transform is not None:
        outputs_info = [self.transform.output(i, output_i) for i, output_i in enumerate(outputs_info)]
        self.transform = None

      # Collect sorted list of independent outputs
      explanatory_variables = []
      for i, output_i in enumerate(outputs_info):
        if output_i.mode in (_OutputInfo.VAR_CONSTRAINED, _OutputInfo.VAR_INDEPENDENT):
          explanatory_variables.append(i)
        self._info_log(self._stringify_output_info(i, output_i, ignore_accuracy=True, report_constraint=True))

      constraints = None
      evaluation_model = None

      n_z = len(explanatory_variables)

      mutable_z = [j for j, i in enumerate(explanatory_variables) if outputs_info[i].mode == _OutputInfo.VAR_CONSTRAINED]

      def _print_constraint(constraint_row, mutable_z):
        terms_l, weights_l = [], []
        terms_r, weights_r = [], []
        for z in _numpy.where(constraint_row[:-1] != 0.)[0]:
          if z in mutable_z:
            terms_l.append(self.y_name[explanatory_variables[z]])
            weights_l.append(constraint_row[z])
          else:
            terms_r.append(self.y_name[explanatory_variables[z]])
            weights_r.append(-constraint_row[z])
        if constraint_row[-1] != 0. or not terms_r:
          terms_r.insert(0, "1")
          weights_r.insert(0, constraint_row[-1])
        return "%s = %s" % (_linear_regression_string(terms_l, weights_l), _linear_regression_string(terms_r, weights_r))

      # Build refining matrix based on the constraint only
      constraints_matrix = []
      for z_index in mutable_z:
        constrained_var = explanatory_variables[z_index]
        # mark variable as the mutable one despite the actual constraint could be ignored as duplicated one
        constraint_i = _numpy.zeros(n_z + 1)
        constraint_i[z_index] = 1.
        constraint_i[-1] = 0. if outputs_info[constrained_var].intercept is None else outputs_info[constrained_var].intercept
        for k, w in zip(outputs_info[constrained_var].explanatory_vars, outputs_info[constrained_var].explanatory_weights):
          constraint_i[explanatory_variables.index(k)] = -w
        if (constraint_i[:-1] != 0.).any() and not any((_ == constraint_i).all() for _ in constraints_matrix):
          constraints_matrix.append(constraint_i)

      if constraints_matrix:
        explanatory_std = self.std_y if original_transform is None else self._stdev(original_transform.rev(self.y))
        explanatory_std = explanatory_std[explanatory_variables]

        constraints_matrix = _numpy.vstack(self._cleanup_constraints_matrix(constraints_matrix, explanatory_std))
        constraints_matrix, rev_constraints_matrix = self._initialize_constraint_update(constraints_matrix, mutable_z, explanatory_std)

        for i, constraint_i in enumerate(constraints_matrix):
          self._info_log("constraint %-3s: %s" % (("#%d" % (i + 1)), _print_constraint(constraint_i, _numpy.where(rev_constraints_matrix[i] != 0.)[0].tolist())))

        rev_constraints_mul = _numpy.multiply(rev_constraints_matrix, explanatory_std.reshape(1, -1)) # Rcm = R * std(Y)

        # yes, we still use this workaround for the bug in ancient Numpy
        rev_constraints_norm = _numpy.fabs(_numpy.hypot.reduce(rev_constraints_mul, axis=1)).reshape(-1, 1)
        _numpy.multiply(rev_constraints_norm, rev_constraints_norm, out=rev_constraints_norm) # rcn[i] = norm2(Rcm[i])^2

        _numpy.multiply(rev_constraints_mul, rev_constraints_mul, out=rev_constraints_mul) # Rcm = R^2 * var(Y)
        _numpy.divide(rev_constraints_mul, rev_constraints_norm, out=rev_constraints_mul) # Rcm = R^2 * var(Y) / sum(var(Y))
        del rev_constraints_norm

        accumulated_mutable_variance = rev_constraints_mul.sum(axis=0) # amw[i] = sum(R[:,i]^2 * var(Y[i]))
        _numpy.divide(1., accumulated_mutable_variance[mutable_z], out=accumulated_mutable_variance[mutable_z]) # amw[i] = 1. / sum(R[:,i]^2 * var(Y[i]))
        _numpy.multiply(rev_constraints_mul, accumulated_mutable_variance.reshape(1, -1), out=rev_constraints_mul) # Rcm[:,i] = (R[:,i]^2 * var(Y)) / sum(var(Y)) * (R[:,i]^2 * var(Y[i])) / sum(R[:,i]^2 * var(Y[i]))
        del accumulated_mutable_variance

        # after simplifying: rev_R = 1. / R[:,i] * (R[:,i]^2 * var(Y)) / sum(var(Y)) * (R[:,i]^2 * var(Y[i])) / sum(R[:,i]^2 * var(Y[i]))
        _numpy.sqrt(rev_constraints_mul, out=rev_constraints_mul)
        _numpy.multiply(rev_constraints_mul, rev_constraints_matrix, out=rev_constraints_matrix)
        del rev_constraints_mul

        # According to Jacobi method we update the i-th mutable variable for the k-th equation by delta[k,i] = {k-th residual} / R[k,i]
        # To keep relative error small we'd like to normalize these updates with respect to the variance of i-th variable.
        # Considering mutable variables have uncorrelated noise, we normalize 1./R[k,i] by R[k,i]^2 * var(Z[i]) / sum(R[k]^2 * var(Z[:]))
        # Also, we'd like to take into account correlated noise of the i-th variable in the different equations.
        # It gives us additional multiplier R[k,i]^2*var(Z[i]) / sum(R[:,i]^2*var(Z[i]))
        # Now we can iterate Z{i+1} = Z{i} + dot((vtile(R[:,-1]) - dot(Z{i}, R[:,:-1].T)), revR)
        # w.r.t additional constraints until some convergence or early stop criteria is met.

        constraints_std = _numpy.fabs(_numpy.hypot.reduce(_numpy.multiply(explanatory_std.reshape(1, -1), constraints_matrix[:,:-1]), axis=1))

        constraints = (explanatory_std, constraints_std, constraints_matrix[:,-1], constraints_matrix[:,:-1], rev_constraints_matrix)

      # always build evaluation model because it can be identity in case of constaraints only mode
      evaluation_model = _numpy.zeros((self.n_y, n_z + 1))
      for i, output_i in enumerate(outputs_info):
        if output_i.mode == _OutputInfo.VAR_CONSTANT:
          evaluation_model[i, -1] = output_i.intercept
        elif output_i.mode == _OutputInfo.VAR_EXPLAINED:
          for j, w in zip(output_i.explanatory_vars, output_i.explanatory_weights):
            evaluation_model[i, explanatory_variables.index(j)] = w
          evaluation_model[i, -1] = output_i.intercept
        else:
          evaluation_model[i, explanatory_variables.index(i)] = 1.

      if n_z == self.n_y and constraints is None:
        # check for the degenerated model
        degenerated_model = _numpy.eye(self.n_y + 1)[:self.n_y]
        if (evaluation_model == degenerated_model).all():
          evaluation_model = None
    finally:
      self.transform = original_transform

    return explanatory_variables, evaluation_model, constraints

  def _weighted_hypot(self, x):
    return _numpy.hypot.reduce(x) if self.W is None else _numpy.hypot.reduce(_numpy.multiply(x, self.W))

  def _collect_constant_outputs(self, outputs_info):
    self._info_log("Scanning data for constant outputs...")
    for i, y_i in enumerate(self.y.T):
      if self._is_constant(y_i):
        outputs_info[i] = _OutputInfo.constant(y_i.mean(), _numpy.std(y_i, ddof=1))
        self._debug_log(self._stringify_output_info(i, outputs_info[i]))
    return outputs_info

  def _search_withing_groups(self, outputs_info, search_groups, rrms_threshold, fit_multistart):
    test_outputs = [i for i, output_info in enumerate(outputs_info) if output_info is None]
    if len(test_outputs) <= 1:
      return outputs_info

    self._info_log("Scanning %d out of %d outputs for duplicates and simple dependencies..." % (len(test_outputs), self.n_y))

    work = _numpy.empty((self.n_y + 1, self.n_pts))
    work[0, :] = 1. if self.W is None else self.W

    if self.W is not None:
      _numpy.multiply(self.y.T, _numpy.sqrt(self.W).reshape(1, -1), out=work[1:,:])
    else:
      work[1:,:] = self.y.T

    # ignoring the last independent output because it MUST be independent
    for i in test_outputs[:-1]:
      work[i] = 1. if self.W is None else self.W # actual i-th output is located at work[i + 1]
      Wt, r = _numpy.linalg.lstsq(work[i:i+2].T, work[i+2:].T, rcond=self.EPS*self.n_pts)[:2] # Wt - transposed weights: norm2([1 Y_i]*Wt[:,k] - Y_k) = r[k]**0.5
      if not r.size:
        # the problem is undetermined
        r = _numpy.hypot.reduce(_numpy.dot(Wt.T, work[i:i+2]) - work[i+2:], axis=1)**2
      for w, r_sq, j in zip(Wt.T, r, xrange(i + 1, self.n_y)):
        if outputs_info[j] is None and r_sq**0.5 < rrms_threshold * self.std_y[j]:
          # We've already removed all constant columns so Wt[1, j] cannot be zero-like. But Wt[0, j] (intercept) still can.
          if self._weighted_hypot(w[1] * work[i+1] - work[j + 1]) < rrms_threshold * self.std_y[j]:
            w[0] = 0. # can remove intercept

          if self.transform is None:
            l, u = 0, _numpy.finfo(float).precision
            while (u + l) // 2 > l:
              m = (u + l) // 2
              w0, w1 = _round(w, m)
              if self._weighted_hypot(w1 * work[i+1] + w0 - work[j + 1]) < rrms_threshold * self.std_y[j]:
                w[0], w[1], u = w0, w1, m
              else:
                l = m

          rrms = self._weighted_hypot(w[1] * work[i+1] + w[0] - work[j + 1]) / self.std_y[j]
          outputs_info[j] = _OutputInfo(rrms, [i], [w[1]], w[0], _OutputInfo.VAR_EXPLAINED, self.divergence_ratio_threshold, fixed=True)
          self._debug_log(self._stringify_output_info(j, outputs_info[j]))

    # first pass - replace already explained outputs
    normalized_groups = []
    for search_group in search_groups:
      normalized_group = []
      for output_index in search_group:
        if outputs_info[output_index] is None:
          normalized_group.append(output_index)
        elif outputs_info[output_index].mode == _OutputInfo.VAR_EXPLAINED:
          normalized_group.extend(outputs_info[output_index].explanatory_vars)
      # note normalized_group can be empty if all its components are constant
      normalized_group = _numpy.unique(normalized_group).tolist()
      if len(normalized_group) > 1:
        normalized_groups.append(normalized_group)

    if not normalized_groups:
      for output_index in range(self.n_y):
        if outputs_info[output_index] is None or outputs_info[output_index].rrms >= rrms_threshold:
          outputs_info[output_index] = _OutputInfo.independent()
      return outputs_info

    self._info_log("Scanning %d outputs for the complicated dependencies using %d known groups (RRMS threshold %g)" % (self.n_y, len(normalized_groups), rrms_threshold))

    # second pass - find explanations
    for explanatory_variables in normalized_groups:
      Xt = self.y.T[explanatory_variables]

      group_sum = Xt.sum(axis=0)
      group_mean = group_sum.mean()
      if _numpy.std(group_sum) < max(1., _numpy.fabs(group_mean)) * rrms_threshold:
        outputs_info = self._fill_sum_explanations(explanatory_variables, group_mean, outputs_info, rrms_threshold)
        continue
      del group_sum

      for k, output_index in enumerate(explanatory_variables):
        if outputs_info[output_index] is not None and self._optimal_fit(outputs_info[output_index], rrms_threshold):
          continue

        try:
          Xt[k] = 1. if self.W is None else self.W
          weights_a, sse = _numpy.linalg.lstsq(Xt.T, self.y[:, output_index], rcond=self.EPS*self.n_pts)[:2]
          sse = sse[0] if sse.size else _numpy.hypot.reduce(_numpy.dot(weights_a.reshape(1,-1), Xt).reshape(-1) - self.y[:, output_index])**2
        finally:
          Xt[k] = self.y[:, output_index]

        weights = _numpy.zeros(self.n_y + 1)
        weights[explanatory_variables] = weights_a
        weights[-1] = weights[output_index]
        weights[output_index] = 0.

        rrms = (sse / self.Y1tWY1[-1,-1])**0.5 / self.std_y[output_index]
        if rrms > rrms_threshold:
          outputs_info[output_index] = _OutputInfo.independent()
          self._debug_log("%s cannot be explained: RRMS %g" % (self.y_name[output_index], rrms))
        else:
          weights_new, rrms_new  = self._postprocess_weights(output_index, weights, rrms_threshold)
          if rrms_new <= rrms_threshold:
            weights, rrms = weights_new, rrms_new

          outputs_info[output_index] = self._prepare_output(output_index, weights, rrms)
          outputs_info[output_index].fixed = self._optimal_fit(outputs_info[output_index], rrms_threshold)
          if not outputs_info[output_index].fixed:
            new_explanation = self._fit(output_index, outputs_info[output_index], rrms_threshold, fit_multistart)
            if self._better_fit(outputs_info[output_index], new_explanation, rrms_threshold):
              outputs_info[output_index] = new_explanation
              outputs_info[output_index].fixed = self._optimal_fit(outputs_info[output_index], rrms_threshold)

          self._debug_log(self._stringify_output_info(output_index, outputs_info[output_index]))
          self._generalize_explanation(output_index, outputs_info, explanatory_variables, rrms_threshold)

    for output_index in range(self.n_y):
      if outputs_info[output_index] is None or outputs_info[output_index].rrms >= rrms_threshold:
        outputs_info[output_index] = _OutputInfo.independent()
    return outputs_info

  def _generalize_explanation(self, output_index, outputs_info, explainable_outputs, rrms_threshold):
    if not self._optimal_fit(outputs_info[output_index], rrms_threshold):
      return

    weights = _numpy.zeros(1 + self.n_y)
    weights[outputs_info[output_index].explanatory_vars] = outputs_info[output_index].explanatory_weights
    weights[-1] = outputs_info[output_index].intercept
    weights[output_index] = -1.

    for other_output in outputs_info[output_index].explanatory_vars:
      if other_output not in explainable_outputs or self._optimal_fit(outputs_info[other_output], rrms_threshold):
        continue

      # direct build alternative explanation
      weights_alt = weights / -weights[other_output]
      weights_alt[other_output] = 0.

      weights_alt, rrms_alt = self._postprocess_weights(other_output, weights_alt, rrms_threshold)
      explanation_alt = self._prepare_output(other_output, weights_alt, rrms_alt)
      if outputs_info[other_output] is None:
        outputs_info[other_output] = explanation_alt
        self._debug_log(self._stringify_output_info(other_output, explanation_alt))
      elif self._better_fit(outputs_info[other_output], explanation_alt, rrms_threshold):
        outputs_info[other_output] = explanation_alt
        self._debug_log("reconsidered (better explanation) " + self._stringify_output_info(other_output, explanation_alt))

  def _collect_simple_dependencies(self, outputs_info, rrms_threshold):
    test_outputs = [i for i, output_info in enumerate(outputs_info) if output_info is None]
    if len(test_outputs) <= 1:
      return outputs_info

    self._info_log("Scanning %d out of %d outputs for duplicates and simple dependencies..." % (len(test_outputs), self.n_y))

    work = _numpy.empty((self.n_y + 1, self.n_pts))
    work[0, :] = 1. if self.W is None else self.W

    if self.W is not None:
      _numpy.multiply(self.y.T, _numpy.sqrt(self.W).reshape(1, -1), out=work[1:,:])
    else:
      work[1:,:] = self.y.T

    # ignoring the last independent output because it MUST be independent
    for i in test_outputs[:-1]:
      work[i] = 1. if self.W is None else self.W # actual i-th output is located at work[i + 1]
      Wt, r = _numpy.linalg.lstsq(work[i:i+2].T, work[i+2:].T, rcond=self.EPS*self.n_pts)[:2] # Wt - transposed weights: norm2([1 Y_i]*Wt[:,k] - Y_k) = r[k]**0.5
      if not r.size:
        # the problem is undetermined
        r = _numpy.hypot.reduce(_numpy.dot(Wt.T, work[i:i+2]) - work[i+2:], axis=1)**2
      for w, r_sq, j in zip(Wt.T, r, xrange(i + 1, self.n_y)):
        if outputs_info[j] is None and r_sq**0.5 < rrms_threshold * self.std_y[j]:
          # We've already removed all constant columns so Wt[1, j] cannot be zero-like. But Wt[0, j] (intercept) still can.
          if self._weighted_hypot(w[1] * work[i+1] - work[j + 1]) < rrms_threshold * self.std_y[j]:
            w[0] = 0. # can remove intercept

          if self.transform is None:
            l, u = 0, _numpy.finfo(float).precision
            while (u + l) // 2 > l:
              m = (u + l) // 2
              w0, w1 = _round(w, m)
              if self._weighted_hypot(w1 * work[i+1] + w0 - work[j + 1]) < rrms_threshold * self.std_y[j]:
                w[0], w[1], u = w0, w1, m
              else:
                l = m

          rrms = self._weighted_hypot(w[1] * work[i+1] + w[0] - work[j + 1]) / self.std_y[j]
          outputs_info[j] = _OutputInfo(rrms, [i], [w[1]], w[0], _OutputInfo.VAR_EXPLAINED, self.divergence_ratio_threshold, fixed=True)
          self._debug_log(self._stringify_output_info(j, outputs_info[j]))

    candidate_outputs = [i for i, output_info in enumerate(outputs_info) if (output_info is None or output_info.mode == _OutputInfo.VAR_EXPLAINED)]
    if len(candidate_outputs) > 2:
      work = self.y[:, candidate_outputs]
      active_std = self.std_y[candidate_outputs]
      for i in range(work.shape[1] - 1):
        std_accum = _numpy.std(_numpy.add.accumulate(work[:, i:], axis=1) * (1. if self.W is None else self.W.reshape(-1, 1)), ddof=0, axis=0)
        # ignore expressions like y[i]+y[i+1]=const because these expressions were found on the previous stage
        minimal_std = _numpy.where(std_accum[2:] < _numpy.maximum.accumulate(active_std[i+2:]) * rrms_threshold)[0] + 2
        for j in minimal_std[:1]:
          explained_outputs = sorted([candidate_outputs[k] for k in range(i, i + j + 1)])
          outputs_info = self._fill_sum_explanations(explained_outputs, _numpy.mean(_numpy.sum(work[:, i:(i+j+1)], axis=1)), outputs_info, rrms_threshold)

    return outputs_info

  def _fill_sum_explanations(self, explained_outputs, intercept, outputs_info, rrms_threshold):
    weights = _numpy.zeros(1 + self.n_y)
    weights[explained_outputs] = -1.
    weights[-1] = intercept

    # first pass - replace already explained outputs
    for output_index in explained_outputs:
      if outputs_info[output_index] is not None and outputs_info[output_index].mode == _OutputInfo.VAR_EXPLAINED:
        weights[-1] -= outputs_info[output_index].intercept
        weights[outputs_info[output_index].explanatory_vars] -= outputs_info[output_index].explanatory_weights
        weights[output_index] = 0.

    # second pass - build new explanations
    for output_index in (_ for _ in explained_outputs if weights[_] != 0.):
      weights[output_index] = 0.
      weights_new, rrms_new  = self._postprocess_weights(output_index, weights, rrms_threshold)
      weights[output_index] = -1.
      new_explanation = self._prepare_output(output_index, weights_new, rrms_new, _OutputInfo.VAR_CONSTRAINED)
      if outputs_info[output_index] is None or self._better_fit(outputs_info[output_index], new_explanation, rrms_threshold):
        outputs_info[output_index] = new_explanation
        outputs_info[output_index].fixed = self._optimal_fit(outputs_info[output_index], rrms_threshold)
        self._debug_log(self._stringify_output_info(output_index, outputs_info[output_index]))

    return outputs_info

  def _list_explainable_variables(self, outputs_info, rrms_threshold):
    self._info_log("Scanning data for unexplainable outputs...")

    explainable_outputs = [i for i, output_info in enumerate(outputs_info) if output_info is None]
    explanatory_variables = [i for i, output_info in enumerate(outputs_info) if (output_info is None or output_info.mode in (_OutputInfo.VAR_CONSTRAINED, _OutputInfo.VAR_INDEPENDENT))]
    self._initialize_outputs_ls(outputs_info, rrms_threshold, explanatory_variables, explainable_outputs)
    return [i for i, output_info in enumerate(outputs_info) if output_info.mode is None]

  def _initialize_outputs_ls(self, outputs_info, rrms_threshold, explanatory_variables, explainable_outputs):
    if any((i not in explanatory_variables) for i in explainable_outputs):
      Xt1 = _numpy.vstack((self.y.T[explanatory_variables], _numpy.ones((1, self.y.shape[0]))))
      Xt = Xt1[:-1]
    else:
      Xt = self.y.T[explanatory_variables]

    if self.W is not None:
      _numpy.multiply(Xt, self.W.reshape(1, -1), out=Xt)
    y = _numpy.empty(self.n_pts)
    for output_index in explainable_outputs:
      if output_index in explanatory_variables:
        try:
          k = explanatory_variables.index(output_index)
          y[:] = Xt[k]
          Xt[k] = 1. if self.W is None else self.W

          weights_a, sse = _numpy.linalg.lstsq(Xt.T, y, rcond=self.EPS*self.n_pts)[:2]
          sse = sse[0] if sse.size else _numpy.hypot.reduce(_numpy.dot(weights_a.reshape(1,-1), Xt).reshape(-1) - y)**2 # sse must be scalar
        finally:
          Xt[explanatory_variables.index(output_index)] = y[:]
      else:
        weights_a, sse = _numpy.linalg.lstsq(Xt1.T, self.y[:, output_index], rcond=self.EPS*self.n_pts)[:2]
        sse = sse[0] if sse.size else _numpy.hypot.reduce(_numpy.dot(weights_a.reshape(1,-1), Xt1).reshape(-1) - self.y[:, output_index])**2 # sse must be scalar

      weights = _numpy.zeros(self.n_y + 1)
      weights[explanatory_variables] = weights_a
      weights[-1] = weights[output_index]
      weights[output_index] = 0.

      rrms = (sse / self.Y1tWY1[-1,-1])**0.5 / self.std_y[output_index]
      if rrms > rrms_threshold:
        outputs_info[output_index] = _OutputInfo.independent()
        self._debug_log("%s cannot be explained: RRMS %g" % (self.y_name[output_index], rrms))
      else:
        outputs_info[output_index] = self._prepare_output(output_index, weights, rrms)

  def _search_dependencies(self, outputs_info, rrms_threshold, refine_rrms_threshold, fit_multistart):
    explainable_outputs = self._list_explainable_variables(outputs_info, rrms_threshold)

    if not explainable_outputs:
      return outputs_info, rrms_threshold

    explainable_outputs = sorted(explainable_outputs, key=lambda i: -self.std_y[i])

    dependencies_map = {} # map variable index to a list of possible already known explanations
    next_refit = _numpy.ones(len(explainable_outputs), dtype=bool)
    refit_output = _numpy.empty(len(explainable_outputs), dtype=bool) # indicates whether we should try to re-fit output (because we've got new information)
    initial_rrms_threshold = rrms_threshold

    while next_refit.any():
      refit_output[:] = next_refit[:]
      next_refit.fill(False)

      self._info_log("Scanning %d out of %d outputs for the complicated dependencies (RRMS threshold %g)" % (_numpy.count_nonzero(refit_output), self.n_y, rrms_threshold))

      for k in _numpy.where(refit_output)[0]:
        output_index = explainable_outputs[k]
        if self._optimal_fit(outputs_info[output_index], rrms_threshold):
          continue

        try:
          new_explanation = self._fit(output_index, outputs_info[output_index], rrms_threshold, fit_multistart, dependencies_map.get(output_index))
          if not self._better_fit(outputs_info[output_index], new_explanation, rrms_threshold):
            self._debug_log("%s cannot improve explanation" % self.y_name[output_index])
            continue

          self._debug_log(self._stringify_output_info(output_index, new_explanation))

          # remove old explanations
          for other_output in outputs_info[output_index].explanatory_vars:
            alt_explanatory_vars = [_ for _ in outputs_info[output_index].explanatory_vars]
            alt_explanatory_vars.remove(other_output)
            alt_explanatory_vars.append(output_index)
            alt_explanatory_vars = sorted(alt_explanatory_vars)
            if alt_explanatory_vars in dependencies_map.setdefault(other_output, []):
              dependencies_map[other_output].remove(alt_explanatory_vars)

          if self._optimal_fit(new_explanation, rrms_threshold):
            new_explanation.fixed = True
          outputs_info[output_index] = new_explanation

          weights = _numpy.zeros(1 + self.n_y)
          weights[new_explanation.explanatory_vars] = new_explanation.explanatory_weights
          weights[-1] = new_explanation.intercept
          weights[output_index] = -1.

          for other_output in (new_explanation.explanatory_vars if self._optimal_fit(new_explanation, rrms_threshold) else []):
            if other_output not in explainable_outputs or self._optimal_fit(outputs_info[other_output], rrms_threshold):
              continue

            # direct build alternative explanation
            weights_alt = weights / -weights[other_output]
            weights_alt[other_output] = 0.

            weights_alt, rrms_alt = self._postprocess_weights(other_output, weights_alt, rrms_threshold)
            explanation_alt = self._prepare_output(other_output, weights_alt, rrms_alt)
            if self._better_fit(outputs_info[other_output], explanation_alt, rrms_threshold):
              # rescan cyclic dependencies on success
              for z in (_ for _ in outputs_info[other_output].explanatory_vars if _ in explainable_outputs and other_output in outputs_info[_].explanatory_vars):
                next_refit[explainable_outputs.index(z)] = not self._optimal_fit(outputs_info[z], rrms_threshold)
              outputs_info[other_output] = explanation_alt
              self._debug_log("reconsidered (better explanation) " + self._stringify_output_info(other_output, explanation_alt))

            # add explanation to the list of test explanations for the sake of back propagation
            if not self._optimal_fit(outputs_info[other_output], rrms_threshold):
              alt_explanatory_vars = [_ for _ in new_explanation.explanatory_vars]
              alt_explanatory_vars.remove(other_output)
              alt_explanatory_vars.append(output_index)
              alt_explanatory_vars = sorted(alt_explanatory_vars)
              if not any(_ == alt_explanatory_vars for _ in dependencies_map.get(other_output, [])):
                dependencies_map.setdefault(other_output, []).insert(0, alt_explanatory_vars)
                if other_output < output_index or not refit_output[explainable_outputs.index(other_output)]:
                  next_refit[explainable_outputs.index(other_output)] = True
        except:
          exc_info = _sys.exc_info()
          self._warn_log("%s cannot be explained: %s" % (self.y_name[output_index], exc_info[1]))

      if refine_rrms_threshold and not next_refit.any() and rrms_threshold > self.minimal_rrms_threshold: #is initial_rrms_threshold:
        # check rrms threshold and tune it if needed
        raw_rrms_data = _numpy.array([outputs_info[z].rrms for z in explainable_outputs if outputs_info[z].rrms < rrms_threshold])
        n_bins = int(_numpy.floor(1. + _numpy.log2(len(raw_rrms_data)))) if raw_rrms_data.size else 0
        if n_bins >= 3:
          hist, edges = _numpy.histogram(raw_rrms_data, bins=n_bins)
          edges[-1] = rrms_threshold # expand bound of the last bin

          outlier = _numpy.where(hist > (hist.mean() + 1.5*_numpy.std(hist, ddof=1)))[0]
          proposed_rrms = rrms_threshold if not outlier.size else max(self.minimal_rrms_threshold, edges[min(1 + outlier.min(), edges.shape[0] - 1)])

          if proposed_rrms < rrms_threshold:
            for output_index in explainable_outputs:
              if outputs_info[output_index].rrms >= rrms_threshold and self._optimal_fit(outputs_info[output_index], rrms_threshold):
                # presense of optimal fit means absense of anomaly
                proposed_rrms = outputs_info[output_index].rrms * (1. + 2. * self.EPS)
                break

          if proposed_rrms < rrms_threshold:
            # Some bin contains more than (mean + 1.5*sigma) items! It's really unusual.
            rrms_threshold = proposed_rrms

            anomaly_share = _numpy.count_nonzero(raw_rrms_data <= proposed_rrms) * 100. / raw_rrms_data.size
            self._debug_log("Detected anomaly in the RRMS errors distribution. %d%% explanations have RRMS error less than %g while RRMS threshold is %g:"\
                            % (int(anomaly_share), rrms_threshold, edges[-1]))
            for _ in zip(edges[:-1], edges[1:], hist):
              self._debug_log("  rrms %-12.5g ... %-12.5g : %d explanations" % _)
            self._debug_log("Refined RRMS threshold: %.15g" % rrms_threshold)

            for k, j in enumerate(explainable_outputs):
              next_refit[k] = not self._optimal_fit(outputs_info[j], rrms_threshold)
            self._initialize_outputs_ls(outputs_info, rrms_threshold, explainable_outputs, [explainable_outputs[k] for k in _numpy.where(next_refit)[0]])

    for output_index in explainable_outputs:
      if outputs_info[output_index].rrms >= rrms_threshold:
        outputs_info[output_index] = _OutputInfo.independent()
        self._debug_log("reconsidered (rrms exceeds updated threshold) " + self._stringify_output_info(output_index, outputs_info[output_index]))

    return outputs_info, rrms_threshold

  def _minimize_constraints(self, outputs_info, group_markers, rrms_threshold):
    # Re-check groups: if group is real invariant (i.e. all constraints are the same) and
    # there is variable with minimal noise multiplier then replace this group with explanation
    for group_id in _numpy.unique(group_markers):
      if not group_id:
        continue
      group_elements = [i for i in _numpy.where(group_markers == group_id)[0] if outputs_info[i].mode == _OutputInfo.VAR_CONSTRAINED]
      candidates = [i for i in group_elements if outputs_info[i].divergence_ratio[0] <= self.divergence_ratio_threshold[0]]
      if not candidates:
        continue

      for explained_output in sorted(candidates, key=lambda i: outputs_info[i].divergence_ratio[1]):
        if outputs_info[explained_output].is_independent() or any((outputs_info[k].mode == _OutputInfo.VAR_EXPLAINED and outputs_info[k].fixed) for k in outputs_info[explained_output].explanatory_vars):
          continue
        if self.suppose_correlated_noise and outputs_info[explained_output].divergence_ratio[1] > self.divergence_ratio_threshold[1]:
          continue
        outputs_info[explained_output].mode = _OutputInfo.VAR_EXPLAINED
        outputs_info[explained_output].fixed = True
        self._debug_log("reconsidered (converting constraint to explanation) %s" % self._stringify_output_info(explained_output, outputs_info[explained_output]))

        for k in outputs_info[explained_output].explanatory_vars:
          if not outputs_info[k].is_independent() and explained_output in outputs_info[k].explanatory_vars:
            outputs_info[k] = _OutputInfo.independent()
            self._debug_log("reconsidered (avoiding cyclic dependencies) %s" % self._stringify_output_info(k, outputs_info[k]))

        # Estimate the "true" divergency rato
        if any(outputs_info[k].mode == _OutputInfo.VAR_CONSTRAINED for k in outputs_info[explained_output].explanatory_vars):
          explanatory_vars = outputs_info[explained_output].explanatory_vars
          explanatory_weights = outputs_info[explained_output].explanatory_weights
          S_diag = _numpy.fabs(_numpy.multiply(self.std_y[explanatory_vars], explanatory_weights))
          S = _numpy.diag(S_diag**2)

          constrained_vars = [(k, s) for k, s in zip(explanatory_vars, S_diag) if outputs_info[k].mode == _OutputInfo.VAR_CONSTRAINED]
          for ki, (zi, wsi) in enumerate(constrained_vars[:-1]):
            explanatory_vars_zi = outputs_info[zi].explanatory_vars
            for kj, (zj, wsj) in enumerate(constrained_vars[ki + 1:]):
              if zj in explanatory_vars_zi:
                S[ki, ki + kj + 1] = 2. * wsi * wsj # x2 multiplier is required because we fill only the upper triangle
          divergence_ratio = S.sum()**0.5 / self.std_y[explained_output]

          if divergence_ratio >= self.divergence_ratio_threshold[1]:
            for k, _ in constrained_vars:
              outputs_info[k] = _OutputInfo.independent()
              self._debug_log("reconsidered (avoiding correlated noise) %s" % self._stringify_output_info(k, outputs_info[k]))

        return True # Resolve explanations immediately

    # search degenerated constraints i.e. constraints that depend on the independent variables only
    for i in (j for j, info in enumerate(outputs_info) if info.mode == _OutputInfo.VAR_CONSTRAINED and all(outputs_info[k].is_independent() for k in info.explanatory_vars)):
      if outputs_info[i].divergence_ratio[0] <= self.divergence_ratio_threshold[0]:
        outputs_info[i].mode = _OutputInfo.VAR_EXPLAINED
        outputs_info[i].fixed = True
      else:
        outputs_info[i] = _OutputInfo.independent()
      self._debug_log("reconsidered (degenerated constraint) %s" % self._stringify_output_info(i, outputs_info[i]))
      return True

    return False

  def _resolve_groups(self, outputs_info, rrms_threshold, fit_multistart):
    # Resolve cross-dependencies
    need_restart = True
    while need_restart:
      outputs_info, need_restart = self._resolve_dependencies(outputs_info, rrms_threshold, fit_multistart)

      if not need_restart:
        # remove divergent explanations
        for i in (i for i, info in enumerate(outputs_info) if info.mode == _OutputInfo.VAR_EXPLAINED and info.divergence_ratio[0] > self.divergence_ratio_threshold[0]):
          outputs_info[i] = _OutputInfo.independent()
          self._debug_log("reconsidered (explanation amplifies error) %s" % self._stringify_output_info(i, outputs_info[i]))
          need_restart = True

    dependencies_matrix = self._fill_dependencies(outputs_info)

    # Now find invariant groups
    group_markers = _numpy.zeros(self.n_y, dtype=int)
    next_group_id = 1

    for i in _numpy.where(_numpy.diag(dependencies_matrix))[0]:
      #outputs_info[i].mode = _OutputInfo.VAR_CONSTRAINED
      markers = _numpy.unique(group_markers[dependencies_matrix[i]])
      if markers[0] == 0:
        markers = markers[1:]

      if not markers.shape[0]:
        # got new group
        group_markers[dependencies_matrix[i]] = next_group_id
        next_group_id += 1
      else:
        group_markers[dependencies_matrix[i]] = markers[0]
        # join groups (if any)
        for m in markers[1:]:
          group_markers[group_markers == m] = markers[0]

    return outputs_info, group_markers

  def _fill_dependencies(self, outputs_info):
    dependencies_matrix = _numpy.zeros((self.n_y, self.n_y), dtype=bool)

    test_modes = (None, _OutputInfo.VAR_EXPLAINED, _OutputInfo.VAR_CONSTRAINED)
    for i, explanatory_vars in ((j, info.explanatory_vars) for j, info in enumerate(outputs_info) if info.mode in test_modes):
      dependencies_matrix[i, explanatory_vars] = True

    if not dependencies_matrix.any():
      return dependencies_matrix

    # Resolve all dependencies and find self-dependent variables
    prev_dependencies = _numpy.zeros(dependencies_matrix.shape, dtype=bool)
    while not dependencies_matrix.all() and (prev_dependencies != dependencies_matrix).any():
      prev_dependencies[:] = dependencies_matrix[:]
      for i in _numpy.where(dependencies_matrix.any(axis=1))[0]:
        dependencies_i = dependencies_matrix[i]
        _numpy.logical_or(dependencies_i, dependencies_matrix[dependencies_i].any(axis=0), out=dependencies_i)

    return dependencies_matrix

  def _resolve_dependencies(self, outputs_info, rrms_threshold, fit_multistart):
    dependencies_matrix = self._fill_dependencies(outputs_info)

    explained_variables = _numpy.array([(info.mode == _OutputInfo.VAR_EXPLAINED) for info in outputs_info], dtype=bool)

    reason = "avoiding cyclic dependencies"

    # Check and re-fit if needed explained and grouped variables
    for output_index in _numpy.where(dependencies_matrix.any(axis=1))[0]:
      # output_index-th variable must depends on independent and/or grouped variables only.
      dependencies_i = dependencies_matrix[output_index]
      # The following code is equivalent to
      #   for j in _numpy.where(dependencies_i)[0]:
      #     dependencies_i[j] = not dependencies_matrix[j].any() or dependencies_matrix[j, j]
      dependencies_i[dependencies_i] = _numpy.logical_or(~dependencies_matrix[dependencies_i].any(axis=1), dependencies_matrix[dependencies_i, dependencies_i])

      unresolved_dependency = explained_variables[outputs_info[output_index].explanatory_vars].any()
      if outputs_info[output_index].fixed and not unresolved_dependency:
        continue # intentionally do nothing

      new_explanatory_vars = dependencies_i.copy()
      new_explanatory_vars[output_index] = False
      new_explanatory_vars[explained_variables] = False
      new_explanatory_vars = _numpy.where(new_explanatory_vars)[0].tolist()

      old_explanation = self._stringify_output_info(output_index, outputs_info[output_index])

      if len(new_explanatory_vars) < len(outputs_info[output_index].explanatory_vars) or (unresolved_dependency and new_explanatory_vars != outputs_info[output_index].explanatory_vars):
        # dependency could be changed. The easiest way is re-fit variable
        self._initialize_regressors()
        weights_new, sse_new = self._solve_ls(self.Y1tWY1, self.Y1tWY1[output_index].reshape(-1, 1), self.Y1tWY1[output_index, output_index],\
                                              new_explanatory_vars + [-1,], lambda w: self._calc_sse(output_index, w), self._ridge(rrms_threshold))
        rrms_new = (sse_new / self.Y1tWY1[-1,-1])**0.5 / self.std_y[output_index]
        if rrms_new >= 10. * rrms_threshold: # this is rough check - even _postprocess_weights would decrease error. but not 10x times...
          outputs_info[output_index] = _OutputInfo.independent()
          reason = "explanation without cyclic dependencies is not accurate enough"
        else:
          # refit explanation
          weights_new, rrms_new  = self._postprocess_weights(output_index, weights_new, rrms_threshold)
          new_explanation = self._prepare_output(output_index, weights_new, rrms_new, outputs_info[output_index].mode)
          new_explanation = self._stepwise_fit(output_index, new_explanation, rrms_threshold)
          if new_explanation.mode is None:
            new_explanation.mode = _OutputInfo.VAR_CONSTRAINED

          if not new_explanation.equal(outputs_info[output_index]):
            outputs_info[output_index] = new_explanation
      elif unresolved_dependency:
        # no explanation can be found
        outputs_info[output_index] = _OutputInfo.independent()

      new_explanation = self._stringify_output_info(output_index, outputs_info[output_index])
      if old_explanation != new_explanation:
        self._debug_log("reconsidered (%s) %s" % (reason, new_explanation))
        # restart immediataly becase we must rebuild dependencies matrix
        return outputs_info, True

    return outputs_info, False

  def _initialize_regressors(self):
    if self.Y1tWY1 is not None:
      return

    self.Y1tWY1 = _numpy.empty((self.n_y + 1, self.n_y + 1))

    if self.W is None:
      self.Y1tWY1[:-1,:-1] = _numpy.dot(self.y.T, self.y)
      self.Y1tWY1[-1, -1] = self.n_pts
      self.Y1tWY1[-1, :-1] = self.y.sum(axis=0)
      self.Y1tWY1[:-1, -1] = self.Y1tWY1[-1, :-1]
    else:
      YW = _numpy.multiply(self.y, _numpy.sqrt(self.W).reshape(-1, 1))
      self.Y1tWY1[:-1,:-1] = _numpy.dot(YW.T, YW) # use (sqrt(W)*Y)'(sqrt(W)*Y) to keep symmetry
      self.Y1tWY1[-1, :-1] = _numpy.multiply(self.y, self.W.reshape(-1, 1), out=YW).sum(axis=0)
      self.Y1tWY1[-1, -1] = self.W.sum()
      self.Y1tWY1[:-1, -1] = self.Y1tWY1[-1, :-1]

  def _prepare_output(self, output_index, weights, rrms, mode=None):
    assert len(weights) == (1 + self.n_y)

    explanatory_vars = _numpy.where(weights[:-1] != 0.)[0].tolist()
    explanatory_weights = weights[:-1][explanatory_vars].tolist()
    intercept = weights[-1]

    if not explanatory_vars:
      return _OutputInfo.constant(intercept, rrms)

    weighted_std = _numpy.multiply(explanatory_weights, self.std_y[explanatory_vars])
    _numpy.fabs(weighted_std, out=weighted_std)

    divergence_ratio_min = _numpy.fabs(_numpy.hypot.reduce(weighted_std)) / self.std_y[output_index] # noise multiplier if explanatory variables noise is uncorrelated
    divergence_ratio_max = _numpy.dot(weighted_std.reshape(-1, 1), weighted_std.reshape(1, -1)).sum()**0.5 / self.std_y[output_index] # noise multiplier if explanatory variables noise is correlated in a worst way

    return _OutputInfo(rrms, explanatory_vars, explanatory_weights, intercept, mode, (divergence_ratio_min, divergence_ratio_max))

  def _better_fit(self, old_explanation, new_explanation, rrms_threshold):
    if old_explanation is new_explanation:
      return False

    if new_explanation.mode == _OutputInfo.VAR_CONSTANT:
      return old_explanation.mode != _OutputInfo.VAR_CONSTANT or new_explanation.rrms < old_explanation.rrms
    elif old_explanation.mode == _OutputInfo.VAR_CONSTANT:
      return False

    if old_explanation.is_independent() and new_explanation.rrms < rrms_threshold:
      return True

    if old_explanation.rrms >= rrms_threshold or new_explanation.rrms >= rrms_threshold:
      return new_explanation.rrms < rrms_threshold

    if self._optimal_fit(old_explanation, rrms_threshold) or new_explanation.equal(old_explanation):
      return False

    # prefer compact explanations with integer weights
    abs_weights = _numpy.fabs(old_explanation.explanatory_weights)
    old_int_weights = _numpy.count_nonzero(abs_weights.astype(int).astype(abs_weights.dtype) == abs_weights)

    abs_weights = _numpy.fabs(new_explanation.explanatory_weights)
    new_int_weights = _numpy.count_nonzero(abs_weights.astype(int).astype(abs_weights.dtype) == abs_weights)
    del abs_weights

    old_explanation_len = len(old_explanation.explanatory_vars) - old_int_weights
    new_explanation_len = len(new_explanation.explanatory_vars) - new_int_weights
    if old_explanation_len != new_explanation_len:
      return new_explanation_len < old_explanation_len

    if (old_explanation.divergence_ratio[0] < self.divergence_ratio_threshold[0]) != (new_explanation.divergence_ratio[0] < self.divergence_ratio_threshold[0]):
      return new_explanation.divergence_ratio[0] < self.divergence_ratio_threshold[0]

    if (old_explanation.intercept == 0.) != (new_explanation.intercept == 0.):
      return new_explanation.intercept == 0. # prefer explanations without intercept

    # Both explanations are accurate enough and almost the same in all reasons.
    return old_explanation.divergence_ratio[1] < new_explanation.divergence_ratio[1]

  def _optimal_fit(self, output_explanation, rrms_threshold):
    if output_explanation is None:
      return False

    if output_explanation.fixed or output_explanation.mode == _OutputInfo.VAR_CONSTANT:
      return True

    if output_explanation.mode in (None, _OutputInfo.VAR_CONSTRAINED, _OutputInfo.VAR_EXPLAINED) and output_explanation.rrms >= rrms_threshold:
      return False

    if len(output_explanation.explanatory_vars) < 3:
      return True

    abs_weights = _numpy.fabs(output_explanation.explanatory_weights)
    if (abs_weights.astype(int).astype(abs_weights.dtype) == abs_weights).all():
      return True

    return False

  def _fit(self, output_index, current_explanation, rrms_threshold, fit_multistart, initial_priority=None):
    try:
      initial_priority = [_ for _ in initial_priority] if initial_priority is not None else []

      alt_explanation = self._stepwise_fit(output_index, current_explanation, rrms_threshold)
      if self._better_fit(current_explanation, alt_explanation, rrms_threshold):
        current_explanation = alt_explanation
        if self._optimal_fit(current_explanation, rrms_threshold):
          return current_explanation

      i_left = fit_multistart + len(initial_priority)
      while i_left > 0:
        i_left -= 1

        if initial_priority:
          priorities = initial_priority.pop(0)
          extra_passes = 0
        else:
          priorities = [current_explanation.explanatory_vars[i] for i in _numpy.random.permutation(len(current_explanation.explanatory_vars))]
          extra_passes = (fit_multistart + 2) // 3

        alt_explanation = self._stepwise_fit(output_index, current_explanation, rrms_threshold, priorities=priorities)
        if self._better_fit(current_explanation, alt_explanation, rrms_threshold):
          i_left += extra_passes
          current_explanation = alt_explanation
          if self._optimal_fit(current_explanation, rrms_threshold):
            return current_explanation
    except:
      raise

    return current_explanation

  def _stringify_output_info(self, output_index, info, ignore_accuracy=False, report_constraint=False):
    if info.is_independent():
      return "%s is independent" % self.y_name[output_index]

    if report_constraint and info.mode == _OutputInfo.VAR_CONSTRAINED:
      return "%s is constrained" % self.y_name[output_index]

    if self.transform is not None:
      info = self.transform.output(output_index, info)

    model_weights, model_terms = ([], []) if (not info.intercept and info.explanatory_vars) else ([info.intercept], ["1"])
    model_weights.extend(info.explanatory_weights)
    model_terms.extend(self.y_name[_] for _ in info.explanatory_vars)

    if not ignore_accuracy and info.rrms:
      divergence = (" div.=%g...%g" % info.divergence_ratio) if not all(_ in(0., 1., _numpy.inf) for _ in info.divergence_ratio) else ""
      accuracy = " (rrms=%g%s)" % (info.rrms, divergence)
    else:
      accuracy = ""

    return "%s%s = %s" % (self.y_name[output_index], accuracy, _linear_regression_string(model_terms, model_weights))

  def _debug_log(self, message):
    self.log(_LogLevel.DEBUG, message)

  def _info_log(self, message):
    self.log(_LogLevel.INFO, message)

  def _warn_log(self, message):
    self.log(_LogLevel.WARN, message)

  @staticmethod
  def _null_log(level, message):
    pass

  @staticmethod
  def _is_constant(y):
    return _numpy.ptp(y) <= DependenciesAnalyzer.EPS * _numpy.fabs([y.max(), y.min()]).max()

  def _remove_inner_dependencies(self, output_index, initial_weights, rrms_threshold, ridge=None):
    if ridge is None:
      ridge = self._ridge(rrms_threshold)

    sse_threshold = self.Y1tWY1[-1,-1] * (rrms_threshold * self.std_y[output_index])**2
    initial_explanatory_vars = _numpy.where(initial_weights[:-1])[0].tolist()
    initial_explanatory_vars = sorted(initial_explanatory_vars, key=lambda i: -self.std_y[i])
    for candidate_var in initial_explanatory_vars:
      try:
        test_explanatory_vars = _numpy.where(initial_weights[:-1])[0].tolist()
        if candidate_var not in test_explanatory_vars:
          continue
        test_explanatory_vars.remove(candidate_var)

        test_weights, sse = self._solve_ls(self.Y1tWY1, self.Y1tWY1[candidate_var].reshape(-1, 1), self.Y1tWY1[candidate_var, candidate_var],
                                           test_explanatory_vars, lambda w: self._calc_sse(candidate_var, w), ridge)

        _numpy.multiply(test_weights, initial_weights[candidate_var], out=test_weights)
        _numpy.add(test_weights, initial_weights, out=test_weights)
        test_weights[candidate_var] = 0. # nullify candidate

        # try to remove candidate and its explanation - eliminates a lot of variables
        z_test_explanatory_vars = _numpy.where(test_weights[:-1] * self.std_y > rrms_threshold)[0].tolist()
        z_test_weights, z_sse = self._solve_ls(self.Y1tWY1, self.Y1tWY1[output_index].reshape(-1, 1), self.Y1tWY1[output_index, output_index],
                                               z_test_explanatory_vars, lambda w: self._calc_sse(output_index, w), ridge)
        if z_sse <= sse_threshold:
          initial_weights[:] = z_test_weights
        elif self._calc_rrms(output_index, test_weights) <= rrms_threshold:
          # eliminate single variable (simple way)
          initial_weights[:] = test_weights
        else:
          # eliminate single variable (rebuild weights)
          test_weights, sse = self._solve_ls(self.Y1tWY1, self.Y1tWY1[output_index].reshape(-1, 1), self.Y1tWY1[output_index, output_index],
                                              test_explanatory_vars, lambda w: self._calc_sse(output_index, w), ridge)
          if sse <= sse_threshold:
            initial_weights[:] = test_weights
      except:
        # just ignore
        pass

    return initial_weights

  def _stepwise_fit(self, output_index, initial_explanation, rrms_threshold, priorities=None):
    std_x_add = _numpy.hstack((self.std_y, [0.,]))
    std_x_add[output_index] = 0.
    std_x_del = (std_x_add > 0.).astype(float)

    # small weights of the outputs with huge std looks suspicious, but they are not
    _numpy.multiply(std_x_del[:-1], self.std_y[output_index], out=std_x_del[:-1])
    _numpy.divide(std_x_del[:-1], _numpy.clip(self.std_y, self.std_y[output_index], _numpy.inf), out=std_x_del[:-1])
    _numpy.sqrt(std_x_del, out=std_x_del)

    std_y = self.std_y[output_index]

    improved = True
    first_run = True
    add_step = True
    switch_std = False

    weights = _numpy.zeros(self.n_y + 1)
    weights[initial_explanation.explanatory_vars] = initial_explanation.explanatory_weights
    weights[output_index] = 0. # paranoid assertion
    weights[-1] = initial_explanation.intercept

    ridge = self._ridge(rrms_threshold)

    if priorities is None:
      weights = self._remove_inner_dependencies(output_index, weights, rrms_threshold, ridge)

    Xty = self.Y1tWY1[output_index].reshape(-1, 1)
    yty = self.Y1tWY1[output_index, output_index]

    if priorities is not None:
      priorities = [i for i in priorities]
      if output_index in priorities:
        priorities.remove(output_index) # yet another paranoid assertion

    while improved:
      improved, weights = DependenciesAnalyzer._stepwise_fit_add(weights, self.Y1tWY1, Xty, yty, rrms_threshold * std_y, std_x_add, priorities, lambda w: self._calc_sse(output_index, w), ridge)\
         if add_step else DependenciesAnalyzer._stepwise_fit_del(weights, self.Y1tWY1, Xty, yty, rrms_threshold * std_y, std_x_del, lambda w: self._calc_sse(output_index, w), ridge)

      if improved:
        weights = self._remove_inner_dependencies(output_index, weights, rrms_threshold, ridge)

      add_step = not add_step
      if first_run:
        # Always make additional run after the first one
        improved =True
        first_run = False
        priorities = None

      if not improved and not switch_std:
        std_x_add, std_x_del = std_x_del, std_x_add
        switch_std = not switch_std
        improved = True

    weights, rrms  = self._postprocess_weights(output_index, weights, rrms_threshold)
    explanation = self._prepare_output(output_index, weights, rrms)

    # we've used ridge regression for better generalization, now it's time to avoid ridge for better accuracy
    weights_alt, _ = self._solve_ls(self.Y1tWY1, Xty, yty, _numpy.where(weights != 0.)[0].tolist(), lambda w: self._calc_sse(output_index, w), None)
    weights_alt, rrms_alt  = self._postprocess_weights(output_index, weights_alt, rrms_threshold)
    explanation_alt = self._prepare_output(output_index, weights_alt, rrms_alt)

    if self._better_fit(explanation, explanation_alt, rrms_threshold):
      explanation = explanation_alt

    return explanation

  def _postprocess_weights(self, output_index, weights, rrms_threshold):
    rrms = _numpy.inf

    if weights[-1] != 0.:
      # Try to remove intercept...
      intercept = weights[-1]
      weights[-1] = 0.
      rrms = self._calc_rrms(output_index, weights)
      if rrms >= rrms_threshold:
        weights[-1] = intercept

    if rrms >= rrms_threshold:
      rrms = self._calc_rrms(output_index, weights)

    if rrms < rrms_threshold and self.transform is None:
      try:
        l, u = 0, _numpy.finfo(float).precision
        while (u + l) // 2 > l:
          m = (u + l) // 2
          weights_alt = _round(weights, m)
          rrms_alt = self._calc_rrms(output_index, weights_alt)
          if rrms_alt < rrms_threshold:
            weights, rrms, u = weights_alt, rrms_alt, m
          else:
            l = m
      except:
        pass

    return weights, rrms

  def _calc_rrms(self, output_index, weights):
    sse = (_numpy.dot(weights.reshape(1, -1), _numpy.dot(self.Y1tWY1, weights.reshape(-1, 1) - 2. * self.Y1tWY1[output_index].reshape(-1, 1))) + self.Y1tWY1[output_index, output_index])[0, 0]
    if sse < 0.:
      sse = self._calc_sse(output_index, weights)
    return (sse / self.Y1tWY1[-1, -1])**0.5 / self.std_y[output_index]

  def _calc_sse(self, output_index, weights):
    r = self.y[:, output_index] - weights[-1]
    work = _numpy.empty(r.shape)
    for i in _numpy.where(weights[:-1] != 0.)[0]:
      _numpy.add(r, _numpy.multiply(-weights[i], self.y[:, i], out=work), out=r)
    return self._weighted_hypot(r)**2

  def _ridge(self, rrms_threshold, ridge_scale=0.01):
    return _numpy.hstack((self.std_y, [0.])) * rrms_threshold * ridge_scale + self.Y1tWY1[-1,-1] * _numpy.finfo(float).eps

  @staticmethod
  def _solve_ls(XtX, Xty, yty, explanatory_vars, sse_calculator, ridge):
    XtX_alt = XtX[explanatory_vars][:, explanatory_vars]
    XtY_alt = Xty[explanatory_vars].reshape(-1, 1)

    if ridge is None:
      ridge = _numpy.zeros(XtX_alt.shape)
    else:
      ridge = _numpy.diag(ridge[explanatory_vars])

    try:
      # XtX is expected to be symmetrical positive definite
      L = _numpy.linalg.cholesky(XtX_alt + ridge)
      weights_alt = _numpy.linalg.solve(L.T, _numpy.linalg.solve(L, XtY_alt))
    except:
      weights_alt = None

    if weights_alt is None:
      # if we failed then try to use QR decomposition
      try:
        Q, R = _numpy.linalg.qr(XtX_alt + ridge)
        weights_alt = _numpy.linalg.solve(R, _numpy.dot(Q.T, XtY_alt))
      except:
        weights_alt = _numpy.ones(XtX_alt.shape[1]) # headshot

    weights = _numpy.zeros(XtX.shape[0])
    weights[explanatory_vars] = weights_alt.reshape(-1)

    sse = (_numpy.dot(weights_alt.T, _numpy.dot(XtX_alt, weights_alt) - 2. * XtY_alt) + yty)[0, 0]
    if sse < 0.:
      if sse_calculator is not None:
        sse = sse_calculator(weights)
      else:
        sse = _numpy.inf

    return weights, sse

  @staticmethod
  def _sorted_weights(x_weights, x_stdev):
    weighted_variance = _numpy.fabs(x_weights) * x_stdev**2
    return [i for i in _numpy.argsort(weighted_variance) if x_weights[i] != 0.]

  @staticmethod
  def _stepwise_fit_add(weights, XtX, Xty, yty, rms_threshold, x_std, priorities, sse_calculator, ridge):
    weights = weights.copy()
    test_variables = [i for i in (priorities if priorities else DependenciesAnalyzer._sorted_weights(weights[:-1], x_std[:-1])[::-1])]
    approved_variables = [-1,] # intercept is always approved
    initial_variables = 1 + len(test_variables)
    sse_prev = _numpy.inf

    while test_variables:
      current_test_variable = test_variables.pop(0)
      weights_alt, sse = DependenciesAnalyzer._solve_ls(XtX, Xty, yty, approved_variables + [current_test_variable,], sse_calculator, ridge)

      if sse < sse_prev:
        approved_variables.append(current_test_variable)
        sse_prev = sse

        rms = (sse / XtX[-1,-1])**0.5
        if rms < rms_threshold:
          # approve weights and stop
          weights[:] = weights_alt[:]
          return (len(approved_variables) < initial_variables), weights

    return False, weights

  @staticmethod
  def _stepwise_fit_del(weights, XtX, Xty, yty, rms_threshold, x_std, sse_calculator, ridge):
    weights = weights.copy()
    test_variables = [i for i in DependenciesAnalyzer._sorted_weights(weights[:-1], x_std[:-1])]
    initial_variables = len(test_variables)
    approved_vars = [-1,]

    while test_variables:
      # try to just remove variable
      current_variable = test_variables.pop(0)
      current_weight = weights[current_variable]
      weights[current_variable] = 0.

      sse = (_numpy.dot(weights.reshape(1, -1), _numpy.dot(XtX, weights.reshape(-1, 1)) - 2. * Xty) + yty)[0, 0]
      if sse < 0.:
        if sse_calculator is not None:
          sse = sse_calculator(weights)
        else:
          sse = _numpy.inf

      rms = (sse / XtX[-1,-1])**0.5
      if rms < rms_threshold:
        continue

      # restore weight and try to rebuild LS
      weights[current_variable] = current_weight

      weights_alt, sse = DependenciesAnalyzer._solve_ls(XtX, Xty, yty, approved_vars + test_variables, sse_calculator, ridge)
      rms = (sse / XtX[-1,-1])**0.5

      if rms < rms_threshold:
        weights = weights_alt
        # re-sort test variables...
        test_variables = DependenciesAnalyzer._sorted_weights(weights[:-1], x_std[:-1])

        # approved variables are still in test after sort
        for k in approved_vars[1:]:
          test_variables.remove(k)
      elif len(approved_vars) > 1:
        break
      else:
        approved_vars.append(current_variable)

    improved = _numpy.count_nonzero(weights[:-1]) < initial_variables
    return improved, weights

  @staticmethod
  def _cleanup_constraints_matrix(constraints, explanatory_std, threshold=1.e-8):
    candidates = [(_, _numpy.hypot.reduce(_), _numpy.hypot.reduce(_[:-1] * explanatory_std)) for _ in constraints]

    def cosine_dist(ca, cb):
      return 1. - _numpy.fabs(_numpy.dot(ca[0], cb[0]) / (ca[1] * cb[1]))

    distances = []
    for i, ca in enumerate(candidates):
      for j, cb in enumerate(candidates[(i + 1):]):
        distances.append((i, i + j + 1, cosine_dist(ca, cb)))

    while distances:
      # use some kind of greedy algorithm: remove closest candidates until we have ones
      i, j, distance = min(distances, key=lambda x: x[-1])
      if distance >= threshold:
        break # nothing to merge

      # leave constraint with smaller noise variance
      if candidates[i][2] > candidates[j][2]:
        i, j = j, i

      # just use the first one
      distances = [(((i0 - 1) if i0 > j else i0), ((j0 - 1) if j0 > j else j0), d0) for i0, j0, d0 in distances if j not in (i0, j0)]
      candidates.pop(j)

    return [_[0] for _ in candidates]

  @staticmethod
  def _initialize_constraint_update(constraints_matrix, explanatory_vars, explanatory_std):
    # note last column is intercept
    rev_constraints_matrix = _numpy.zeros((constraints_matrix.shape[0], constraints_matrix.shape[1] - 1), dtype=constraints_matrix.dtype)
    rev_constraints_matrix[:, explanatory_vars] = constraints_matrix[:, explanatory_vars]

    # Don't modify "flowless" constraints
    perfect_constraints = _numpy.where((constraints_matrix[:, :-1].astype(int).astype(constraints_matrix.dtype) == constraints_matrix[:, :-1]).all(axis=1))[0]
    perfect_constraints = sorted(perfect_constraints, key=lambda i:-_numpy.hypot.reduce(rev_constraints_matrix[i]*explanatory_std))

    for i in perfect_constraints:
      # Don't batch it to avoid double removes!
      rev_constraints_matrix[:i, rev_constraints_matrix[i] != 0.] = 0.
      rev_constraints_matrix[(i+1):, rev_constraints_matrix[i] != 0.] = 0.

    constraints_order = perfect_constraints + sorted([i for i in range(constraints_matrix.shape[0]) if i not in perfect_constraints and _numpy.any(rev_constraints_matrix[i])],
                                                     key=lambda i:-_numpy.hypot.reduce(rev_constraints_matrix[i]*explanatory_std))
    constraints_matrix = constraints_matrix[constraints_order]
    rev_constraints_matrix = rev_constraints_matrix[constraints_order]

    return constraints_matrix, rev_constraints_matrix
