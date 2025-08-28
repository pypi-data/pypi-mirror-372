#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
#

import numpy as _numpy

from .. import shared as _shared
from ..gtapprox.build_manager import DefaultBuildManager as _DefaultBuildManager
from ..gtapprox.iterative_iv import _IterativeIV

def _rcondh(xtx, regul_min=0., regul_max=0.):
  """
  Calculate reciprocal condition number for the symmetrical,
  positive semi-definite matrix xtx w.r.t optional regularization
  matrix with min/max eigenvalues regul_min/regul_max
  """
  ev = _numpy.linalg.eigvalsh(xtx)
  ev_min = max(0., ev.min())
  ev_max = max(ev.max(), ev_min, 1.e-300)
  # note _numpy.finfo(float).tiny = 2.2250738585072014e-308 so if ev.min() == ev.max() < 1.e-300 then spurious failure is possible

  # For symmetric, positive semi-definite matrices A, B and C = A + B with
  # respective eigenvalues vectors c, a and b: a[i] + max(b) >= c[i] >= a[i] + min(b)
  return min(ev_min / ev_max, (ev_min + regul_min) / (ev_max + regul_max))

def _initialize_x1tx1(xdim, x, xtx):
  xtx[:xdim, :xdim] = _numpy.dot(x.T, x)
  xtx[xdim, :xdim] = _numpy.sum(x, axis=0)
  xtx[:xdim, xdim] = xtx[xdim, :xdim]
  xtx[xdim, xdim] = x.shape[0]

def _min_loocv_rcond(x, regul_min=0., regul_max=0.):
  """
  Calculates minimal reciprocal condition number of matrix (x'x + z)
  and (y_i'y_i+z) where y_i is matrix x with i-th row removed and
  z is additional s.p.d matrix with minimal and maximal eigenvalues
  regul_min and regul_max respectively.
  """
  npoints, xdim = x.shape

  xtx = _numpy.empty((xdim + 1, xdim + 1))
  _initialize_x1tx1(xdim, x, xtx)

  min_rcond = _rcondh(xtx, regul_min, regul_max)
  if not min_rcond or npoints <= (xdim + 1):
    return min_rcond

  xi1 = _numpy.empty((1, xdim + 1))
  xi1[0, xdim] = 1.

  for i in range(npoints):
    xi1[0, :xdim] = x[i]
    min_rcond = min(min_rcond, _rcondh(xtx - _numpy.dot(xi1.T, xi1), regul_min, regul_max))
    if not min_rcond:
      return 0.

  return min_rcond

def _regularize_matrix_inplace(variable_design, rcond_threshold, fixed_design=None, seed=65521, maxiter=100):
  """
  Shuffle variable_design columns while minimal reciprocal condition number of the matrix Z'Z
  and all matrices Zi'Zi is less than `rcond_threshold`, where Z is stacked variable_design and fixed_design
  matrix and Zi is matrix Z with i-th row removed.
  """
  if fixed_design is not None:
    xdim = fixed_design.shape[1]
    xtx = _numpy.empty((xdim + 1, xdim + 1))
    _initialize_x1tx1(xdim, fixed_design, xtx)
    ev = _numpy.linalg.eigvalsh(xtx)
    l_min, l_max = max(0., ev.min()), max(0., ev.max())
    del xtx
  else:
    l_min, l_max = 0., 0.

  best_rcond = _min_loocv_rcond(variable_design, l_min, l_max)

  if best_rcond >= rcond_threshold:
    return best_rcond # the initial matrix is well-conditioned

  gen = _numpy.random.RandomState(seed)

  design = variable_design.copy()
  ndim = design.shape[1]
  maxiter = max(maxiter, ndim * 2)

  for k in range(maxiter):
    gen.shuffle(design[:, (k % ndim)])
    curr_rcond = _min_loocv_rcond(design, l_min, l_max)
    if curr_rcond > best_rcond:
      best_rcond, variable_design[:] = curr_rcond, design
      if best_rcond >= rcond_threshold:
        return best_rcond #instant stop

  return best_rcond

def _collect_vars_levels(ndim, npoints, lower_bounds, upper_bounds, discrete_levels, integer_variables):
  """
  Select the number of levels for each variable w.r.t problem
  dimensionality and optional catagorical-like variables
  """

  def _test_factorial(npoints, levels):
    factorial_size = 1
    for l in levels:
      # l may be equal to _numpy.iinfo(int).max so we must not use something like (npoints + l - 1) due to overflow
      # while factorial_size cannot cause overflow
      if (npoints + factorial_size - 1) // factorial_size <= l:
        return False
      factorial_size *= l
    return True

  maxlevels = _numpy.iinfo(int).max
  integer_variables = integer_variables or [] # convert None to empty list

  levels_limit = [(maxlevels if levels is None else len(levels)) for levels in discrete_levels] if discrete_levels else [maxlevels]*ndim
  for i in integer_variables:
    levels_limit[i] = int(min(levels_limit[i], (upper_bounds[i] - lower_bounds[i] + 1)))

  if _test_factorial(npoints, levels_limit):
    # the only possible case is all variables are discrete or integer with a small range and full factorial size is less than npoints
    npoints = _numpy.prod(levels_limit)
    levels_count = levels_limit
  else:
    dof, next_dof, free_points = 0, ndim, npoints # current degrees of freedom, expected degrees of freedom, required cardinality of free variables
    while dof != next_dof and free_points > 0:
      free_levels = max(2, int((free_points)**(1./next_dof)))
      dof, next_dof, free_points = next_dof, 0, npoints
      for l in levels_limit:
        if l > free_levels:
          next_dof += 1 # variable is free if its limit allows
        else:
          free_points //= l # otherwise it is fixed and reduces cardinality of free variables

    # get no more points than we would need
    levels_count = _numpy.clip(levels_limit, 0, max(2, int(free_points**(1./dof))))

    # inefficient but simple and works good in most cases
    k = 0
    while _test_factorial(npoints, levels_count):
      # increase the number of variable levels if it is allowed and check cardinality
      levels_count[k] = min(levels_limit[k], levels_count[k] + 1)
      k = (k + 1) % ndim

  if discrete_levels:
    levels = [(_numpy.linspace(lb, ub, n).tolist() \
               if not values else \
               [values[k] for k in _numpy.round(_numpy.linspace(0, len(values) - 1, n)).astype(int)]) \
              for lb, ub, n, values in zip(lower_bounds, upper_bounds, levels_count, discrete_levels)]
  else:
    levels = [_numpy.linspace(lb, ub, n).tolist() for lb, ub, n in zip(lower_bounds, upper_bounds, levels_count)]

  for i in integer_variables:
    levels[i] = _numpy.round(levels[i]).tolist()

  return levels, npoints

def _linear_rsm_box(lower_bounds, upper_bounds, discrete_levels=None, integer_variables=None, fixed_design=None, npoints=None, rcond_threshold=1.e-5, seed=65521):
  """
  Plots the DoE for the linear RSM based on the vertices of the bounding box.
  """
  assert len(lower_bounds) == len(upper_bounds)
  ndim = len(lower_bounds)

  # note _collect_vars_levels guarantees the full factorial size is greater than or equal to the npoints
  levels, npoints = _collect_vars_levels(ndim, (npoints or (ndim + 2)), lower_bounds, upper_bounds, discrete_levels, integer_variables)

  rnd = _numpy.random.RandomState(seed)

  # We use float to avoid numerical overflow issue. Accuracy must not be an issue in real life cases
  factorial_size, factorial_dim = float(len(levels[0])), 1
  for axis_levels in levels[1:]:
    if factorial_size >= npoints:
      break
    factorial_size *= len(axis_levels)
    factorial_dim += 1

  design = _numpy.empty((npoints, ndim))

  base_factorial = _numpy.floor(_numpy.linspace(0., factorial_size, num=npoints, endpoint=False)).astype(int)

  for axis_idx, axis_levels in enumerate(levels):
    group_len = len(axis_levels)

    if axis_idx < factorial_dim:
      design[:, axis_idx] = _numpy.array(axis_levels, copy=_shared._SHALLOW)[base_factorial % group_len]
      base_factorial //= group_len
    else:
      work = _numpy.arange((npoints + group_len - 1) // group_len * group_len, dtype=int); rnd.shuffle(work)
      design[:, axis_idx] = _numpy.array(axis_levels, copy=_shared._SHALLOW)[work[:npoints] % group_len]

  design_rcond = _regularize_matrix_inplace(design, fixed_design=fixed_design, rcond_threshold=rcond_threshold, seed=seed)

  return design, design_rcond

def _minimize_design(additional_points, base_points, npoints_threshold, rcond_threshold):
  """
  Remove excessive points from the additional_points while keeping
  at least npoints_threshold  in the stacked additional_points and base_points
  and minimal reciprocal condition number for all LOO matrices
  at least rcond_threshold
  """
  def _test_rcond(x_test, xtx, xi1, rcond_threshold):
    xi1[0, :xdim] = x_test
    return _rcondh(xtx - _numpy.dot(xi1.T, xi1)) >= rcond_threshold

  # Unconditionally remove additional points presented in the base points
  duplicate_extras = _numpy.array([(base_points == xi[_numpy.newaxis]).all(axis=1).any() for i, xi in enumerate(additional_points)], dtype=bool)
  if duplicate_extras.any():
    additional_points = additional_points[~duplicate_extras]
  del duplicate_extras

  extra_points_len, xdim = additional_points.shape
  npoints_threshold = max(0, npoints_threshold - len(base_points))

  if extra_points_len <= npoints_threshold:
    return additional_points # there is nothing to remove

  keep_points = _numpy.arange(extra_points_len).tolist()

  xtx_base = _numpy.zeros((xdim + 1, xdim + 1))
  _initialize_x1tx1(xdim, base_points, xtx_base)

  xtx = _numpy.empty((xdim + 1, xdim + 1))
  _initialize_x1tx1(xdim, additional_points, xtx)
  _numpy.add(xtx, xtx_base, out=xtx)

  xtx_copy = xtx.copy()

  xi1 = _numpy.empty((1, xdim + 1))
  xi1[0, xdim] = 1.

  for candidate in range(extra_points_len):
    xi1[0, :xdim] = additional_points[candidate]
    xtx -= _numpy.dot(xi1.T, xi1)

    if _rcondh(xtx) < rcond_threshold:
      xtx[:] = xtx_copy[:] # instant rollback
    else:
      keep_points.remove(candidate)
      approve = all(_test_rcond(additional_points[i], xtx, xi1, rcond_threshold) for i in keep_points) \
            and all(_test_rcond(x_i, xtx, xi1, rcond_threshold) for x_i in base_points)

      if not approve:
        # rollback remove
        keep_points.append(candidate)
        xtx[:] = xtx_copy[:]
      elif len(keep_points) <= npoints_threshold:
        break # no more points to remove
      else:
        # re-evaluate xtx to avoid numerical reasons
        keep_points = sorted(keep_points)
        _initialize_x1tx1(xdim, additional_points[keep_points], xtx)
        _numpy.add(xtx, xtx_base, out=xtx)
        xtx_copy[:] = xtx[:] # commit remove

  return additional_points[keep_points]

def _insert_const_columns(sample, gripped_bounds, values):
  """
  Insert constant columns into the `sample`
  with values read from the `values` sequence.
  """
  extended_sample = _numpy.empty((len(sample), len(gripped_bounds)))
  extended_sample[:, ~gripped_bounds] = sample
  for i in _numpy.where(gripped_bounds)[0]:
    extended_sample[:, i] = values[i]
  return extended_sample

def _linear_rsm_design(bounds, init_x, npoints=None, catvars=None, intvars=None, resp_scalability=1, rcond_threshold=1.e-5, seed=65521):
  """
  Plots additional points required to fit linear RSM w.r.t optional initial sample.
  Raise an exception on failure.

  :param bounds: design space bounds (lower, upper)
  :type bounds: ``tuple(list[float], list[float])``
  :keyword init_x: optional initial sample, input part (values of variables)
  :type init_x: :term:`array-like`, 1D or 2D
  :param npoints: optional minimal required desing size regardeless of presence and size of ``init_x``
  :type npoints: ``int`` or ``None``
  :param catvars: optional list with indices of categorical variables and their levels.
  :type catvars: ``None`` or ``list[]``
  :param intvars: optional list with indices of integer variables.
  :type intvars: ``None`` or ``list[]``
  :param rcond_threshold: minimal reciprocal condition number of the stacked matrix of
                          generated design and ``init_x`` (if presented) and all matrices
                          cut down from this matrix by removing single row.
  :type rcond_threshold: ``float``
  :param seed: random seed used to initialize the pseudo-random number generator.
  :type seed: ``None, int, array_like``

  If  ``catvars`` parameter is not None then value is a list in the following format:
  ``[id, [lv1, lv2, ...], ...]``, where ``id`` is a zero-based index of the variable,
  and ``lv1``, ``lv2`` and so on are level values. Note categorical variables are not affected
  by bounds — that is, corresponding elements in the bounds tuple are ignored when generating
  a value of a categorical variable. Still, some placeholder numeric values should be present
  in bounds just to keep the order of variables.
  """
  lb, ub = bounds
  if len(lb) != len(ub):
    raise ValueError("Lower and upper bounds have different length: %d != %d" % (len(lb), len(ub)))
  ndim = len(lb)

  if init_x is not None:
    init_x = _numpy.array(init_x, copy=_shared._SHALLOW, dtype=float)
    if init_x.ndim == 1:
      init_x = init_x.reshape(-1, 1) if ndim == 1 else init_x.reshape(1, -1)
    if init_x.shape[1] != ndim:
      raise ValueError("Shape of the initial X sample does not conform dimensionality of the problem: %d != %d" % (init_x.shape[1], ndim))
    if not _numpy.isfinite(init_x).all():
      init_x = init_x[_numpy.isfinite(init_x).all(axis=1)]
    if not len(init_x):
      init_x = None

  # collect levels for categorical-like variables
  if catvars:
    discrete_levels = [None]*ndim
    for i, lvls in zip(catvars[:-1:2], catvars[1::2]):
      discrete_levels[i] = [_ for _ in lvls] # list is required
  else:
    discrete_levels = None

  # enumerate gripped variables
  gripped_vars = _numpy.equal(lb, ub) # variables gripped by bounds
  if discrete_levels:
    gripped_vars[[i for i, lvls in enumerate(discrete_levels) if (lvls is not None and len(lvls) == 1)]] = True

  const_vars = gripped_vars if init_x is None else _numpy.logical_and(gripped_vars, _numpy.ptp(init_x, axis=0) == 0.) # true constants

  npoints = int(npoints) if npoints is not None else -1
  if npoints < 0:
    npoints = ndim - _numpy.count_nonzero(const_vars) + 2
    npoints = (npoints  + resp_scalability - 1) // resp_scalability * resp_scalability

  if init_x is not None and len(init_x) >= npoints and _min_loocv_rcond(init_x[:, ~const_vars]) >= rcond_threshold:
    # initial sample is good enough
    return _numpy.empty((0, ndim)), None

  if not npoints:
    return None, "Evaluation of responses is prohibited, and the initial sample is either absent or too small for linear dependency reconstruction."

  if gripped_vars.any():
    # build reference design based on non-gripped variables
    free_vars = _numpy.where(~gripped_vars)[0]
    if not free_vars.size:
      return None, "No free variables found"
    linear_rsm_design, linear_rsm_design_rcond = _linear_rsm_box([lb[i] for i in free_vars],
                                                                 [ub[i] for i in free_vars],
                                                                 discrete_levels=(None if discrete_levels is None else [discrete_levels[i] for i in free_vars]),
                                                                 integer_variables=intvars, npoints=npoints, rcond_threshold=rcond_threshold,
                                                                 seed=seed, fixed_design=(None if init_x is None else init_x[:, free_vars]))
    # reconstruct gripped variables
    linear_rsm_design = _insert_const_columns(linear_rsm_design, gripped_vars, lb)
  else:
    # build reference design based on all variables
    linear_rsm_design, linear_rsm_design_rcond = _linear_rsm_box(lb, ub, discrete_levels=discrete_levels, integer_variables=intvars,
                                                                 npoints=npoints, rcond_threshold=rcond_threshold,
                                                                 seed=seed, fixed_design=init_x)

  npoints = min(npoints, len(linear_rsm_design)) # if all variables have limited number of levels then full factorial may be less than npoints
  # Note even if all variables have only 2 levels, it is enough for restoring of linear dependency.

  if init_x is not None:
    # remove excessive new points w.r.t initial design
    rcond_threshold = min(rcond_threshold, linear_rsm_design_rcond)

    if const_vars.any():
      linear_rsm_design = _minimize_design(linear_rsm_design[:, ~const_vars], init_x[:, ~const_vars], npoints, rcond_threshold)
      linear_rsm_design = _insert_const_columns(linear_rsm_design, const_vars, lb)
    else:
      linear_rsm_design = _minimize_design(linear_rsm_design, init_x, npoints, rcond_threshold)

  linear_rsm_design_length = len(linear_rsm_design) + (0 if init_x is None else len(init_x))
  if linear_rsm_design_length < npoints:
    return None, "Some variables are gripped, and the initial sample is either absent or too small for linear dependency reconstruction based on %d points (maximum %d points can be used)." % (npoints, linear_rsm_design_length)

  return linear_rsm_design, None

def _round_linear_regresion_weights(weights, x_range, accuracy_threshold=1.e-8):
  # weights is (n_variables + 1) by n_outputs dimensional matrix
  # x_range is n_variables-dimensional vector
  # Variance of the expression, considering inputs are uniformely distributed with the given range
  try:
    inputs_variance = x_range[:, _numpy.newaxis]**2 / 12. # variance of uniformly distributed variables
    original_output_variance = (weights[:-1,:]**2 * inputs_variance).sum(axis=0) # variance of responses

    weights_int = _numpy.round(weights, 0) # integer part of weights and intercept
    weights_frac = weights - weights_int # fractional part of weights and intercept

    # The modulus of variance, which is caused by the presence of a fractional part of the weights.
    # Note that fractional weights can reduce the overall variance, but we want the change in variance 
    # in either direction to be negligible. 
    frac_output_variance = _numpy.fabs((2. * weights_int[:-1] + weights_frac[:-1]) * weights_frac[:-1]) * inputs_variance

    # round weights if the variance of the fractional part is negligible
    negligible_frac_terms = frac_output_variance < original_output_variance * accuracy_threshold

    # round intercept if its fractional value is negligible comparing to the standard deviation of output
    negligible_frac_intercept = _numpy.fabs(weights_frac[-1]) < _numpy.sqrt(original_output_variance) * accuracy_threshold

    weights[:-1][negligible_frac_terms] = weights_int[:-1][negligible_frac_terms]
    weights[-1][negligible_frac_intercept] = weights_int[-1][negligible_frac_intercept]
  except:
    pass

  return weights

def _linear_rsm_stepwise_fit(x, y, x_bounds=None):
  try:
    model = _DefaultBuildManager().build(x, y, {
      'GTApprox/Technique': 'RSM',
      'GTApprox/RSMType': 'Linear',
      'GTApprox/RSMFeatureSelection': 'StepwiseFit',
    }, None, None, None, None, None)

    rsm_model = _numpy.array(model.details['Regression Model']['model'], dtype=float, copy=_shared._SHALLOW) # shape=(n_regressors, x_dim)
    active_terms = _numpy.equal(rsm_model, 1.).any(axis=0)
    if active_terms.all():
      active_terms = None
  except:
    active_terms = None

  return _linear_rsm_fit(x, y, active_terms=active_terms, x_bounds=x_bounds)

def _linear_rsm_fit(x, y, rcond_threshold=None, active_terms=None, x_bounds=None):
  """
  Fit linear regression using OLS. Returns matrix of weights (w)
  and outputwise estimation of relative RMSE based on the LOO CV (rrmse).
    y^hat = [x, 1] * w
    rrmse = std(y - y^hat) / norm(y)
  , where norm(y) is std(y) for variable columns of y and abs(y) for constant columns.
  """

  x = _numpy.array(x, copy=_shared._SHALLOW)
  if x.ndim == 1:
    x = x.reshape(-1, 1)

  y = _numpy.array(y, copy=_shared._SHALLOW)
  if y.ndim == 1:
    y = y.reshape(-1, 1)

  if len(x) != len(y):
    raise Exception("Unconformed length of X and Y samples: %d != %d" % (len(x), len(y)))

  if not _numpy.isfinite(x).all():
    known_x = _numpy.isfinite(x).all(axis=1)
    x = x[known_x]
    y = y[known_x]
    del known_x

  known_y = _numpy.isfinite(y)
  if not known_y.all():
    if not (known_y.any(axis=1) == known_y.all(axis=1)).all():
      # y could be fitted if we consider independent y columns
      weights, rrmse = zip(*tuple([_linear_rsm_fit(x, y_i.reshape(-1, 1), x_bounds=x_bounds) for y_i in y.T]))
      return _numpy.hstack(weights), _numpy.hstack(rrmse)
    # simple case: just filter it out and go down
    known_y = known_y.all(axis=1)
    x = x[known_y]
    y = y[known_y]
  del known_y

  npoints = x.shape[0]

  std_y = _numpy.std(y, axis=0) if npoints > 1 else _numpy.zeros(y.shape[1])

  active_x = _numpy.ptp(x, axis=0) > 0.
  active_y = _numpy.logical_and(_numpy.ptp(y, axis=0) > 0., std_y > _numpy.finfo(float).tiny**0.5)

  if active_terms is not None:
    active_x = _numpy.logical_and(active_x, active_terms)

  if not active_x.any() or not active_y.any():
    mean_y = _numpy.mean(y, axis=0)
    rrmse = std_y / _numpy.maximum(_numpy.fabs(mean_y), 1.) # a little bit of cheating
    rrmse[~active_y] = 1. # RRMS of mean prediction is 1 by definition
    return _numpy.vstack((_numpy.zeros((x.shape[1], y.shape[1])), mean_y.reshape(1, -1))), rrmse

  xdim = _numpy.count_nonzero(active_x)

  x_columns = active_x if not active_x.all() else slice(xdim)
  X1 = _numpy.empty((npoints, xdim + 1))

  X1[:-1, :-1] = x[1:, x_columns]
  X1[:, -1] = 1.

  Y1 = _numpy.empty_like(y)
  Y1[:-1] = y[1:]

  loo_residuals = _numpy.empty_like(y)

  if rcond_threshold is None:
    rcond_threshold = _numpy.finfo(float).eps * xdim

  for i in range(npoints):
    W = _numpy.linalg.lstsq(X1[:-1], Y1[:-1], rcond=rcond_threshold)[0]

    X1[i, :xdim], Y1[i] = x[i, x_columns], y[i]
    loo_residuals[i] = y[i] - _numpy.dot(X1[i], W)

  W = _numpy.linalg.lstsq(X1, Y1, rcond=rcond_threshold)[0]

  if not active_x.all():
    W_ext = _numpy.zeros((x.shape[1] + 1, W.shape[1]))
    W_ext[:-1][active_x] = W[:-1] # the last one is intercept
    W_ext[-1] = W[-1]
    W = W_ext

  W[-1] = _numpy.mean(y-_numpy.dot(x, W[:-1]), axis=0)

  x_range = _numpy.ptp(x, axis=0) if npoints > 1 else _numpy.ones(x.shape[1])
  try:
    if x_bounds is not None:
      x_bounds = _shared.as_matrix(x_bounds, shape=(2, x.shape[1]))
      x_bounds[0][~_numpy.isfinite(x_bounds[0])] = x.min(axis=0)[~_numpy.isfinite(x_bounds[0])]
      x_bounds[1][~_numpy.isfinite(x_bounds[1])] = x.max(axis=0)[~_numpy.isfinite(x_bounds[1])]
      x_range = _numpy.maximum(x_range, _numpy.ptp(x_bounds, axis=0))
  except:
    pass

  W = _round_linear_regresion_weights(W, x_range)

  # calculate componentwise normalized root-mean-squared error

  rrmse = _numpy.std(loo_residuals, axis=0)
  if active_y.all():
    rrmse = rrmse / std_y
  else:
    rrmse[active_y] = rrmse[active_y] / std_y[active_y]
    rrmse[~active_y] = std_y[~active_y] / _numpy.maximum(_numpy.fabs(W[-1, ~active_y]), 1.)

  return W, rrmse
