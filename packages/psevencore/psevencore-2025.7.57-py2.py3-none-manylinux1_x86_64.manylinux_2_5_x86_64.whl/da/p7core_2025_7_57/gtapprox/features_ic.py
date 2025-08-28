#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import sys as _sys
import numpy as np

from .. import six as _six
from .. import loggers
from ..shared import parse_json, parse_bool
from .core_ic import _build_route
from .moa_preprocessing import remove_coinciding_points
from .utilities import _parse_dry_run


def build_landscape_analyzer(x, y, w=None, catvars=None, seed=None, n_parts=3, builder=None, n_routes=None, n_fronts=None, strategy=None, accelerator=1):
  """
  Build landscape analyzer.
  strategy - fronts generation strategy: segmentation, pairwise, continuous, furthest, clusterization
  n_routes - number of fronts per points for segmentation strategy (0, inf), recommended 0.5 ... 3
  """
  from .builder import Builder as _Builder
  x, y, _, _, w, _ = _Builder._preprocess_parameters(x, y, None, None, w, None)

  if builder is None:
    builder = _Builder()._get_build_manager()

  if w is not None:
    valid_points = w > (w.max() * 1.e-5)
    if np.count_nonzero(valid_points) < w.size:
      x = x[valid_points]
      y = y[valid_points]
      w = w[valid_points]

  if x.size == 0:
    return None

  dry_run = _parse_dry_run(builder.options)
  if dry_run == 'quick':
    return None

  rnd_state = np.random.get_state()
  try:
    if seed is not None:
      np.random.seed(seed)

    n_points = len(x)

    # filter and merge duplicate points
    x_order = np.lexsort(x.T)
    x_dups = np.array([False] + [(x[i] == x[j]).all() for i, j in zip(x_order[:-1], x_order[1:])], dtype=bool)
    if x_dups.any():
      blck_start = -1
      blck_size = 0
      for i_curr in np.where(x_dups)[0]:
        if (blck_start + blck_size + 1) != i_curr:
          blck_start = i_curr - 1
          blck_size = 1
        else:
          pass

        blck_size += 1
        y[x_order[blck_start]] += (y[x_order[i_curr]] - y[x_order[blck_start]]) / blck_size

      x_order = x_order[np.logical_not(x_dups, out=x_dups)]
      x = x[x_order]
      y = y[x_order]
    del x_dups
    del x_order

    # Check tensor structure
    structure, _, tensor_factors = builder._find_tensor_structure_local(x, {}, None)
    factor_vals = None
    if structure in (2, 4,):
      strategy = "segmentation"
      factor_dims = [_[: -1] for _ in parse_json(tensor_factors)]
      factor_vals = tuple(remove_coinciding_points(x[:, dims], return_sorted=True, logger=None) for dims in factor_dims)

    if strategy == "segmentation":
      if n_fronts is None:
        n_fronts = min(10000, int(np.round(float(x.size) / (np.log(accelerator) + 1))))
      else:
        n_fronts *= n_points
    elif n_points > 100:
      if n_routes is None:
        n_routes = min(1000, int(np.round(float(x.size) / (2. * (np.log(accelerator) + 1.)))))
      if strategy is None:
        strategy = "pairwise"
    else:
      if n_routes is None:
        n_routes = n_points * 2
      if strategy is None:
        strategy = "continuous"

    if dry_run:
      if n_fronts:
        n_fronts = (n_fronts + 49) // 50
      if n_routes:
        n_routes = (n_routes + 49) // 50

    base_route = _build_route(x, y, w, n_routes=n_routes, n_fronts=n_fronts, strategy=strategy, tensor_structure=factor_vals, watcher=builder.get_watcher())
    sample_route = base_route.extended_copy(n_parts, catvars, builder)
    n_eps_points = 100 if dry_run else 1000

    analyzer = _FeaturesIC(base_route, sample_route)
    analyzer.cached_sample_stat[n_eps_points] = analyzer.sample_route.analyze_all(n_points=n_eps_points)

    return analyzer
  except:
    exc_info = _sys.exc_info()
    if builder._logger:
      builder._logger(loggers.LogLevel.WARN, 'Failed to perform landscape analysis: %s' % exc_info[1])
    return None
  finally:
    np.random.set_state(rnd_state)


class _FeaturesIC(object):

  def __init__(self, base_route, sample_route):
    self.route = base_route
    self.sample_route = sample_route
    self.model_route = self.sample_route.copy(False)
    self.cached_sample_stat = {}

  @staticmethod
  def _calc_cos_dist(v1, v2):
    # np.dot for each row
    dot = np.einsum('ij..., ij...->i...', v1, v2)
    norm = np.hypot.reduce(v1, axis=1) * np.hypot.reduce(v2, axis=1)

    valid_values = norm > 0.
    if not valid_values.all():
      cos_dist = np.ones_like(dot) # if both points are at 0 angle is assumed 0
      cos_dist[valid_values] = dot[valid_values] / norm[valid_values]
    else:
      cos_dist = dot / norm

    return np.round(cos_dist, 10, out=cos_dist)

  def _calc_errors(self, sample_stat, model_stat):
    eps, ic1, icp1 = sample_stat
    eps, ic2, icp2 = model_stat
    ic_error = np.mean(np.abs(ic1 - ic2), axis=0) / (np.std(ic1, ddof=1) + np.finfo(float).eps) # The constant model can produce zero-variance statistics

    # Find sin of angle between vector from sample VM point to center of VM and vector from sample VM point to model VM point
    # sin(arccos(cosine_dist)) == np.sqrt(1 - cosine_dist ** 2)
    angles = np.sqrt(1. - self._calc_cos_dist(-self.sample_route.dydx, self.model_route.dydx-self.sample_route.dydx)**2)
    if np.all(angles == 0):  # degenerated landscape, angles are useless
      angles[:] = 1.0

    errors = np.abs(self.sample_route.y - self.model_route.y)
    error_training_sample = np.sqrt(np.mean(errors[:len(self.route.x)] ** 2, axis=0)) / np.std(self.sample_route.y, ddof=1, axis=0)
    errors[:len(self.route.x)] = 0

    front_angle_errors = angles * errors[self.sample_route.fronts].sum(axis=1) # SUM along y values
    front_angle_errors = np.sqrt(np.mean(front_angle_errors ** 2, axis=0)) / np.std(self.sample_route.y, ddof=1, axis=0)

    la_errors = {
      # Information content error (combines both curvature and residuals)
      'mean_ic': ic_error,
      # Angle shifts of dxdy values (depends on curvature errors, ignores residuals)
      'mean_angle': np.mean(angles, axis=0),
      # Output values errors calculated by linear interpolation of training sample points (ignores curvature errors)
      'mean_error': np.mean(errors, axis=0),
      # Output values errors calculated by linear interpolation of training sample points with front angles as weights
      'mean_front_angle': front_angle_errors,

      # Output values errors in training sample points
      'mean_error_training_sample': error_training_sample,

      # Combines angles and residuals
      'mean_angle_error': np.mean(angles, axis=0) * np.mean(errors, axis=0),
      # Combines angles and ic
      'mean_angle_ic': np.mean(angles, axis=0) * ic_error,
      # Combines residuals and ic
      'mean_error_ic': np.mean(errors, axis=0) * ic_error,
      # Combines front errors, angles and ic
      'mean_front_angle_ic': front_angle_errors * ic_error,
    }
    return {'la_error': la_errors['mean_front_angle_ic']}

  def validate_landscape(self, model, n_points=1000):
    # Build route along model landscape
    self.model_route.update(model.calc(self.model_route.x))

    # General route properties errors
    if n_points not in self.cached_sample_stat:
      self.cached_sample_stat[n_points] = self.sample_route.analyze_all(n_points=n_points)

    model_stat = self.model_route.analyze_all(eps_lb=self.sample_route.eps_min, eps_ub=self.sample_route.eps_max, n_points=n_points)
    return self._calc_errors(self.cached_sample_stat[n_points], model_stat)

  def _select_subsample(self, n_points, mode, seed):
    max_points = self.sample_route.x.shape[0] - self.route.x.shape[0]
    if n_points >= max_points:
      return np.ones(max_points, dtype=bool)

    # create CDF according to x segments distances
    segments_weight = np.zeros(self.route.dx_nrm2.shape)

    modes_list = {}
    for current_mode in str(mode).lower().split("+"):
      current_mode = current_mode.strip()
      modes_list[current_mode] = modes_list.get(current_mode, 0) + 1

    for current_mode, mode_multiplier in modes_list.items():
      current_mode = current_mode.strip()
      if current_mode.lower() == "dy/dx":
        abs_dydx = np.fabs(self.route.dydx).sum(axis=2)
        np.add(abs_dydx * (mode_multiplier / self.route.dydx.sum()), segments_weight, out=segments_weight)
      elif current_mode.lower() == "d2y/dx2":
        d2ydx2 = (self.route.dydx[:, 0] - self.route.dydx[:, 1]) / (self.route.dx_nrm2[:, [0]] + self.route.dx_nrm2[:, [1]])
        d2ydx2 = np.fabs(d2ydx2).sum(axis=1).reshape(-1, 1)
        np.add(d2ydx2 * (mode_multiplier / d2ydx2.sum()), segments_weight, out=segments_weight)
      elif current_mode.lower() == "dx":
        np.add(self.route.dx_nrm2 * (mode_multiplier / self.route.dx_nrm2.sum()), segments_weight, out=segments_weight)

    if segments_weight.sum() <= np.finfo(float).eps:
      segments_weight[:] = 1.

    candidate_cdf = np.zeros((self.sample_route.x.shape[0],), dtype=float)

    extra_id = 0
    assert self.route.fronts[0][0] == self.sample_route.fronts[0][0]
    for orig_id, (i1, i2, i3) in enumerate(self.route.fronts):
      # Find extra points added within current original front
      extra_fronts = self.sample_route.fronts[extra_id]
      extra_id += 1
      while self.sample_route.fronts[extra_id - 1][-1] != i3:
        extra_fronts = np.append(extra_fronts, self.sample_route.fronts[extra_id])
        extra_id += 1
      idx = remove_coinciding_points(extra_fronts)
      # Split extra points by central element of original front
      cut_id = np.argwhere(idx == i2)[0][0]
      # Assign weights
      w_ij, w_jk = np.fabs(segments_weight[orig_id])
      candidate_cdf[idx[:cut_id]] = w_ij
      candidate_cdf[idx[cut_id:]] = w_jk

    # take into account only 'extra' points and get one extra point from the left
    n_orig = self.route.x.shape[0]
    candidate_cdf = candidate_cdf[n_orig - 1:]
    candidate_cdf[0] = 0.

    n_active = np.count_nonzero(candidate_cdf)

    if n_points >= n_active:
      # get all points
      candidates = candidate_cdf > 0.
    else:
      # select points to get
      n_select = n_points

      # now select points w.r.t the distribution generated?
      candidates = np.zeros((1 + max_points,), dtype=bool)

      if isinstance(seed, _six.string_types) and seed.lower() == "deterministic":
        # deterministic mode
        min_nonzero = candidate_cdf[1:].min()
        max_nonzero = candidate_cdf[1:].max()
        if 0. == min_nonzero:
          min_nonzero = candidate_cdf[np.nonzero(candidate_cdf)].min()

        if (max_nonzero - min_nonzero) <= np.finfo(float).eps * max_nonzero * 2.:
          # distribution is pretty uniform, so just select first n_select elements with nonzero CDF
          candidates[np.nonzero(candidate_cdf)[:n_select]] = True
        else:
          # make all values unique...
          if min_nonzero < max_points:
            np.multiply(candidate_cdf, max_points / min_nonzero, out=candidate_cdf)
          np.add(candidate_cdf[1:], np.arange(max_points), out=candidate_cdf[1:])

          cdf_threshold = np.percentile(candidate_cdf[1:], (max_points - n_select) * 100. / max_points)
          candidates[candidate_cdf >= cdf_threshold] = True
      else:
        # random mode with random state preserving
        random_state = np.random.get_state()
        try:
          # accumulate probabilities to CDF (it's not an actual CDF because it's not normalized but it's easer to re-scale random probabilities)
          np.add.accumulate(candidate_cdf, out=candidate_cdf)

          if seed is not None:
            np.random.seed(seed)
          for candidate_prob in np.random.random(n_select):
            candidate_idx = np.searchsorted(candidate_cdf, candidate_prob * candidate_cdf[-1])
            candidates[candidate_idx] = True  # select candidate
            # update CDF
            delta = candidate_cdf[candidate_idx] - candidate_cdf[candidate_idx - 1]
            np.subtract(candidate_cdf[candidate_idx + 1:], candidate_cdf[candidate_idx] - candidate_cdf[candidate_idx - 1], out=candidate_cdf[candidate_idx + 1:])
            candidate_cdf[candidate_idx] = candidate_cdf[candidate_idx - 1]  # just to avoid numerical issues
        finally:
          if seed is not None:
            np.random.set_state(random_state)

    # don't forget to skip first point
    return candidates[1:]

  def random_subsample(self, n_points, mode="dx", seed=None):
    """
    Selects random subsample from the extra (non training dataset) points.
    n_points - the number of points to select
    mode - points prioritization mode: one of the "dx", "dy/dx", "d2y/dx2" or "+"-delimited combination of these modes, where
        "dx" - priority is segment distance;
        "dy/dx" and "d2y/dx2" - priorities are first and second numerical derivatives respectively.
    """
    extra_x = self.sample_route.x[self.route.x.shape[0]:]
    extra_y = self.sample_route.y[self.route.x.shape[0]:]
    extra_w = self.sample_route.w[self.route.w.shape[0]:]

    if n_points >= len(extra_x):
      return extra_x, extra_y, extra_w

    random_state = np.random.get_state()
    try:
      candidates = self._select_subsample(n_points, mode, seed)
    finally:
      np.random.set_state(random_state)
    return extra_x[candidates], extra_y[candidates], extra_w[candidates].flatten()

  def random_split(self, n_points, mode="dx", seed=None):
    """
    Almost the same as random_subsample but also returns unselected points
    """

    extra_x = self.sample_route.x[self.route.x.shape[0]:]
    extra_y = self.sample_route.y[self.route.x.shape[0]:]
    extra_w = self.sample_route.w[self.route.w.shape[0]:]

    if n_points >= len(extra_x):
      return extra_x, extra_y, extra_w, np.array((0, extra_x.shape[1])), np.array((0, extra_y.shape[1])), np.array((0, extra_w.shape[1]))

    selected_candidates = self._select_subsample(n_points, mode, seed)
    other_candidates = ~selected_candidates

    return extra_x[selected_candidates], extra_y[selected_candidates], extra_w[selected_candidates].flatten(), \
        extra_x[other_candidates], extra_y[other_candidates], extra_w[other_candidates].flatten()
