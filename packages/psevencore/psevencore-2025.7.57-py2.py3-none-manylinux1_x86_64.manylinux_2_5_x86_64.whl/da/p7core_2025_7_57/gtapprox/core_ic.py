#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import numpy as np

from ..six import next
from ..six.moves import xrange
from ..shared import _SHALLOW
from .moa_preprocessing import Scaler
from .utilities import _distances_table as _build_distance_table


class _MultiRoute(object):
  '''
  +--------+--------+--------+--------+--------+
  |   i/j  | [=]  0 | [-] -2 | [+]  1 | [*] -6 |
  +--------+--------+--------+--------+--------+
  | [=]  0 |    0   |   -2   |    1   |   -6   |
  +--------+--------+--------+--------+--------+
  | [-] -2 |    2   |    0   |    3   |   -4   |
  +--------+--------+--------+--------+--------+
  | [+]  1 |   -1   |   -3   |    0   |   -7   |
  +--------+--------+--------+--------+--------+
  | [*] -6 |    6   |    4   |    7   |    0   |
  +--------+--------+--------+--------+--------+
  '''
  TRANSITION_TYPES = {'negative': -2, 'neutral': 0, 'positive': 1, 'uncaught': -6}
  IMAG_POINTS_WEIGHT = 0.8

  def __init__(self, x, y, w, fronts):
    self.x = np.array(x, dtype=float)
    self.y = np.array(y, dtype=float)

    assert self.x.shape[0] == self.y.shape[0]
    if self.y.ndim == 1:
      self.y = self.y.reshape((-1, 1))

    self.imag_w = _MultiRoute.IMAG_POINTS_WEIGHT
    if w is None:
      self.w = np.ones((self.y.shape[0], 1), dtype=float)
    else:
      self.w = np.array(w, dtype=float).reshape(-1, 1)
      assert self.y.shape[0] == self.w.shape[0]

    if self.w is not None:
      assert self.w.shape[0] == self.y.shape[0]
      if self.w.ndim == 1:
        self.w = self.w.reshape((-1, 1))

    if 1 == self.x.shape[1]:
      norm_x = lambda dx: np.fabs(dx, out=dx).flatten()
    else:
      norm_x = lambda dx: np.hypot.reduce(dx, axis=2)

    self.fronts = fronts
    self.dx_nrm2 = norm_x(np.diff(x[fronts], axis=1)).reshape((-1, 2))

    np.clip(self.dx_nrm2, self.dx_nrm2.max() * np.finfo(float).eps, np.inf, out=self.dx_nrm2)
    self.dydx = np.diff(self.y[fronts], axis=1)
    np.divide(self.dydx, self.dx_nrm2.reshape(-1, 2, 1), out=self.dydx)
    self.dydx[~np.isfinite(self.dydx)] = 0.

    abs_dydx = np.absolute(self.dydx)
    self.eps_min = np.min(abs_dydx)
    self.eps_max = np.max(abs_dydx)

    transitions = [self.TRANSITION_TYPES[i] for i in ['negative', 'neutral', 'positive']]
    self.front_types = np.array([j - i for i in transitions for j in transitions if i != j])
    self.ic_base = np.log(self.front_types.size)

  def extended_copy(self, n_parts, catvars, builder, min_n_parts=3):
    assert n_parts > 1

    max_n_parts = n_parts
    const_weights = {}
    for n_parts in xrange(min_n_parts, max_n_parts + 1):
      linear_weights = np.arange(1, n_parts, dtype=float) / n_parts
      linear_weights = np.vstack((1. - linear_weights, linear_weights))
      # Symlog weights distribution
      nonlinear_weights = 1. / (1. + np.exp(-10. * (linear_weights.T - 0.5)))
      const_weights[n_parts] = (nonlinear_weights, nonlinear_weights.prod(axis=1).reshape(-1, 1))

    x1D = np.zeros(self.fronts.size, dtype=float)
    # Add extra dx values to join all the triples into 1d sequence
    x1D[1:] = np.insert(self.dx_nrm2, np.arange(2, self.dx_nrm2.size, 2), 1.0)
    x1D = np.cumsum(x1D).reshape(self.fronts.shape)
    y1D = self.y[self.fronts]

    original_options = dict(builder.options.values)
    original_watcher = builder.get_watcher()
    original_logger = builder.get_logger()
    try:
      builder.set_watcher(None)
      builder.set_logger(None)

      dry_run = builder.options._get("/GTApprox/DryRun")
      builder.options.reset()

      model = builder.build(x=x1D.reshape(-1, 1), y=y1D.reshape(-1, self.y.shape[1]),
                            options={"GTApprox/Technique": "PLA",
                                     "GTApprox/LogLevel": "error",
                                     "GTApprox/InternalValidation": False,
                                     "/GTApprox/DryRun": dry_run},
                            outputNoiseVariance=None, comment=None, weights=None,
                            initial_model=None, restricted_x=None)
    finally:
      builder.options.reset()
      builder.options.set(original_options)
      builder.set_watcher(original_watcher)
      builder.set_logger(original_logger)

    def _read_weights(n_parts):
      return const_weights.get(n_parts, const_weights[max_n_parts if n_parts > max_n_parts else min_n_parts])

    dx_nrm2_min = self.dx_nrm2.min()
    n_points_dx = (max_n_parts - 2) / max(np.ptp(self.dx_nrm2), np.finfo(float).eps)
    dx_nrm2_limit = np.percentile(self.dx_nrm2, 90) / 2.0

    # first pass - calculate the number of points to add
    n_x_add = 0
    for dx_nrm2 in self.dx_nrm2:
      n_x_add += _read_weights(int(2.5 + (dx_nrm2[0] - dx_nrm2_min) * n_points_dx))[0].shape[0]
      n_x_add += _read_weights(int(2.5 + (dx_nrm2[1] - dx_nrm2_min) * n_points_dx))[0].shape[0]

    new_x = np.empty((self.x.shape[0] + n_x_add, self.x.shape[1]))
    new_y = np.empty((self.y.shape[0] + n_x_add, self.y.shape[1]))
    new_w = np.empty((self.w.shape[0] + n_x_add, self.w.shape[1]))

    fronts = np.empty((len(self.fronts) + n_x_add, 3), dtype=int)

    new_x[:self.x.shape[0]] = self.x
    new_y[:self.y.shape[0]] = self.y
    new_w[:self.w.shape[0]] = self.w

    # Second pass - fill the data
    next_id = self.x.shape[0]
    next_front = 0
    for f_id, (i, j, k) in enumerate(self.fronts):
      path = [i]

      # Split ij front
      wij, wij_prod = _read_weights(int(2.5 + (self.dx_nrm2[f_id][0] - dx_nrm2_min) * n_points_dx))

      prev_id = next_id
      next_id += wij.shape[0]
      path.extend(xrange(prev_id, next_id))

      np.dot(wij, np.vstack((self.x[i], self.x[j])), out=new_x[prev_id:next_id])
      distance_penalty = (self.w[i] + self.w[j]) * self.dx_nrm2[f_id][0] / dx_nrm2_limit
      new_w[prev_id:next_id] = np.dot(wij, np.vstack((self.w[i], self.w[j]))) * self.imag_w - wij_prod * distance_penalty
      new_y[prev_id:next_id, 0] = x1D[f_id][0] + self.dx_nrm2[f_id][0] * wij[:, 1]

      path.append(j)

      # Split jk front
      wij, wij_prod = _read_weights(int(2.5 + (self.dx_nrm2[f_id][1] - dx_nrm2_min) * n_points_dx))

      prev_id = next_id
      next_id += wij.shape[0]
      path.extend(xrange(prev_id, next_id))

      np.dot(wij, np.vstack((self.x[j], self.x[k])), out=new_x[prev_id:next_id])
      distance_penalty = (self.w[j] + self.w[k]) * self.dx_nrm2[f_id][1] / dx_nrm2_limit
      new_w[prev_id:next_id] = np.dot(wij, np.vstack((self.w[j], self.w[k]))) * self.imag_w - wij_prod * distance_penalty
      new_y[prev_id:next_id, 0] = x1D[f_id][1] + self.dx_nrm2[f_id][1] * wij[:, 1]

      path.append(k)

      # Add all the possible fronts
      fronts_update = np.vstack((path[:-2], path[1:-1], path[2:])).T
      fronts[next_front:next_front + fronts_update.shape[0]] = fronts_update
      next_front += fronts_update.shape[0]

    new_y[self.x.shape[0]:] = model.calc(new_y[self.x.shape[0]:,0].reshape(-1, 1))
    np.clip(new_w, 0., np.inf, out=new_w)

    if catvars is not None:
      n_orig = self.x.shape[0]
      last_cat = None
      for i in path:
        if i < n_orig:
          last_cat = self.x[i, catvars]
        else:
          new_x[i, catvars] = last_cat

    return _MultiRoute(new_x, new_y, new_w, fronts[:next_front])

  def copy(self, deep=False):
    obj = self.__new__(_MultiRoute)

    obj.x = self.x.copy() if deep else self.x
    obj.y = self.y.copy() if deep else self.y
    obj.w = self.w.copy() if deep else self.w
    obj.imag_w = self.imag_w
    obj.fronts = [_ for _ in self.fronts] if deep else self.fronts
    obj.dx_nrm2 = self.dx_nrm2.copy() if deep else self.dx_nrm2
    obj.dydx = self.dydx.copy() if deep else self.dydx
    obj.eps_min = self.eps_min
    obj.eps_max = self.eps_max
    obj.front_types = self.front_types
    obj.ic_base = self.ic_base

    return obj

  def update(self, y):
    assert len(y) == len(self.y)
    self.y = np.array(y, dtype=float)
    if self.y.ndim == 1:
      self.y = self.y.reshape((-1, 1))
    self.dydx = np.diff(self.y[self.fronts], axis=1)
    np.divide(self.dydx, self.dx_nrm2.reshape(-1, 2, 1), out=self.dydx)
    return self

  def _analyze_single(self, eps_lb, eps_ub, sequence, front_markers_base, front_markers_ceil):
    icp_marker_a = self.TRANSITION_TYPES['positive'] - self.TRANSITION_TYPES['negative']
    icp_marker_b = self.TRANSITION_TYPES['negative'] - self.TRANSITION_TYPES['positive']

    n_points = float(len(self.dydx))

    ic_list = []
    icp_list = []

    for output_index in range(self.y.shape[1]):
      sequence.fill(self.TRANSITION_TYPES['neutral'])
      sequence[self.dydx[:, :, output_index] > eps_lb] = self.TRANSITION_TYPES['positive']
      sequence[self.dydx[:, :, output_index] < -eps_lb] = self.TRANSITION_TYPES['negative']
      # sequence[self.abs_dydx > eps_ub] = self.TRANSITION_TYPES['uncaught']

      front_markers_count = np.bincount((sequence[:,1] - sequence[:,0]) - front_markers_base, minlength=front_markers_ceil)
      front_prob = front_markers_count[self.front_types - front_markers_base]
      front_prob = front_prob[front_prob != 0] / n_points

      ic_list.append(-(front_prob * np.log(front_prob)).sum() / self.ic_base)

      # Calculate partial information content value (without neutral or repeated transitions)
      icp_list.append((front_markers_count[icp_marker_a - front_markers_base] + front_markers_count[icp_marker_b - front_markers_base]) / (n_points + 1.0))

    return ic_list, icp_list

  def _prepare_for_analyze(self):
    sequence = np.empty_like(self.dx_nrm2, dtype=int)

    icp_marker_a = self.TRANSITION_TYPES['positive'] - self.TRANSITION_TYPES['negative']
    icp_marker_b = self.TRANSITION_TYPES['negative'] - self.TRANSITION_TYPES['positive']

    # Since the sequence contains only 3 markers (neutral, positive and negative),
    # the front_markers.min() must be either icp_marker_a or icp_marker_b.
    # Actually, this is icp_marker_b but we can change markers in the future

    # Calculate information content value
    front_markers_base = min(self.front_types.min(), icp_marker_a, icp_marker_b)
    front_markers_ceil = max(self.front_types.max(), icp_marker_a, icp_marker_b) - front_markers_base + 1

    return sequence, front_markers_base, front_markers_ceil

  def analyze(self, eps_lb=None, eps_ub=None, workbuf=None):
    eps_lb = self.eps_min if eps_lb is None else eps_lb
    eps_ub = self.eps_max if eps_ub is None else eps_ub

    sequence, front_markers_base, front_markers_ceil = self._prepare_for_analyze()
    return self._analyze_single(eps_lb, eps_ub, sequence, front_markers_base, front_markers_ceil)

  def analyze_all(self, eps_lb=None, eps_ub=None, n_points=None):
    eps_lb = self.eps_min if eps_lb is None else eps_lb
    eps_ub = self.eps_max if eps_ub is None else eps_ub
    n_points = np.unique(np.abs(self.dydx)).size if n_points is None else int(n_points)

    eps_points = np.linspace(eps_lb, eps_ub, n_points)

    size_y = self.y.shape[1]
    ic = np.empty((n_points, size_y))
    icp = np.empty((n_points, size_y))

    sequence, front_markers_base, front_markers_ceil = self._prepare_for_analyze()
    for i, eps in enumerate(eps_points):
      ic[i], icp[i] = self._analyze_single(eps_lb, eps_ub, sequence, front_markers_base, front_markers_ceil)

    return eps_points.reshape(-1, 1), ic, icp

def _direct_route(start_idx, stop_idx, points, distances_table, points_usage, stop_list, deep=0):
  # start_idx, stop_idx - integer indices of points to build route from -> to
  # points - n-by-k dimensional ndarray of k-dimensional points in rowwise order
  # distances_table - n-by-n dimensional matrix of euclidean distances between points: distances_table[i][j] is a distance between points i and j
  # stop_list - boolean vector of points that should not be used
  # points_usage - n-dimensional vector of points usage count (i.e. i-th element indicates how many times i-th point is used in different routes)

  stop_list[start_idx] = True
  stop_list[stop_idx] = True

  if start_idx == stop_idx:
    vec_len = 0.
  else:
    try:
      vec_len = distances_table[start_idx][stop_idx]
    except:
      vec_len = np.round(np.fabs(np.hypot.reduce(points[stop_idx] - points[start_idx])), 10)

  if vec_len < np.finfo(float).eps:
    return [start_idx], distances_table

  # find points with minimal angle between vector start_idx->stop_idx and sstart_idx->i-th
  projections = np.dot(points - points[start_idx].reshape(1, -1), (points[stop_idx] - points[start_idx]).reshape(-1, 1)).flatten()
  np.divide(projections, vec_len, out=projections)
  midpoint_idxs = np.logical_and(projections >= 0., projections <= vec_len)
  midpoint_idxs[stop_list] = False

  try:
    np.logical_and(midpoint_idxs, (distances_table[start_idx] < vec_len), out=midpoint_idxs)
  except:
    pass

  try:
    np.logical_and(midpoint_idxs, (distances_table[stop_idx] < vec_len), out=midpoint_idxs)
  except:
    pass

  if not midpoint_idxs.any():
    return [start_idx, stop_idx], distances_table

  midpoint_idxs = np.where(midpoint_idxs)[0]

  if len(midpoint_idxs) > 0:
    try:
      dist_start = distances_table[start_idx]
    except:
      dist_start = np.fabs(points - points[start_idx, :]) if points.shape[1] == 1 else np.hypot.reduce(points - points[start_idx, :], axis=1)
      np.round(dist_start, 10, out=dist_start)

      if distances_table is None:
        distances_table = {}
      distances_table[start_idx] = dist_start

    midpoint_idxs = midpoint_idxs[dist_start[midpoint_idxs] > np.finfo(float).tiny]

  if len(midpoint_idxs) > 1:
    active_cos = np.divide(projections[midpoint_idxs], dist_start[midpoint_idxs])
    midpoint_idxs = midpoint_idxs[active_cos >= max(0.8, active_cos.max())]
    del active_cos

  if len(midpoint_idxs) > 1:
    active_distances = dist_start[midpoint_idxs]
    midpoint_idxs = midpoint_idxs[active_distances <= active_distances.min()]

  if len(midpoint_idxs) > 1:
    # select point according to points_usage statistics
    # convert usage statistics to custom distribution CDF
    point_distrib = points_usage[midpoint_idxs]
    np.subtract(1 + point_distrib.max(), point_distrib, out=point_distrib)
    np.add.accumulate(point_distrib, out=point_distrib)
    np.divide(point_distrib, point_distrib[-1], out=point_distrib)
    midpoint_idxs = [midpoint_idxs[np.where(point_distrib >= np.random.random())[0].min()]]

  if not len(midpoint_idxs):
    # start_idx and stop_idx are closest points for each other
    return [start_idx, stop_idx], distances_table

  midpoint = midpoint_idxs[0]

  # update statistics for the mid point only!
  points_usage[midpoint] += 1.

  if dist_start.min() == dist_start[midpoint]:
    left_path = [start_idx, midpoint]
  else:
    left_path, distances_table = _direct_route(start_idx, midpoint, points, distances_table, points_usage, stop_list, deep + 1)

  try:
    right_path = [midpoint, stop_idx] if distances_table[stop_idx].min() == distances_table[stop_idx, midpoint] else None
  except:
    right_path = None

  if right_path is None:
    right_path, distances_table = _direct_route(midpoint, stop_idx, points, distances_table, points_usage, stop_list, deep + 1)

  return left_path[:-1] + right_path, distances_table


def _continuous_path(n_points, n_routes, distance_table):
  points_chain = np.random.permutation(range(n_points)).tolist()
  routes_left = min(int(n_routes), n_points - 1) if n_routes else (n_points - 1)
  start_idx = points_chain.pop(0)
  while routes_left > 0:
    routes_left -= 1
    if not points_chain:
      points_chain = np.random.permutation(range(n_points)).tolist()
      points_chain.remove(start_idx)
    stop_idx = points_chain.pop(0)
    yield start_idx, stop_idx, False
    start_idx = stop_idx


def _pairwise_path(n_points, n_routes, distance_table):
  if n_routes and int(n_routes) > n_points // 2:
    routes_left = int(n_routes)
    while routes_left > 0:
      routes_left -= 1

      start_idx = np.random.randint(0, n_points)
      stop_idx = start_idx
      while start_idx == stop_idx:
        stop_idx = np.random.randint(0, n_points)

      yield start_idx, stop_idx, True
  else:
    routes_left = int(n_routes) if n_routes else n_points // 2
    routes_list = np.random.permutation(range(n_points))
    for i in xrange(routes_left):
      yield routes_list[i * 2 + 0], routes_list[i * 2 + 1], True


def _furthest_point(n_points, n_routes, distance_table):
  if n_routes is None:
    n_routes = n_points
  for route_idx in xrange(n_routes):
    start_idx = route_idx % distance_table.shape[0]
    stop_idx = np.where(distance_table[start_idx] == np.percentile(distance_table[start_idx], (100. * (distance_table.shape[0] - route_idx // distance_table.shape[0])) / distance_table.shape[0]))[0]
    if stop_idx.size:
      stop_idx = stop_idx[np.random.randint(stop_idx.shape[0])]
      yield start_idx, stop_idx, True


def _enumerate_all(n_points, n_routes, distance_table):
  for start_idx in xrange(n_points):
    for stop_idx in xrange(start_idx + 1, n_points):
      yield start_idx, stop_idx, True


def _cleanup_path(existing_path, new_path, minsize):
  minsize = minsize - 1
  if minsize < 2:
    # just remove already existing pairs
    return [_ for _ in new_path if _ not in existing_path]
  elif minsize >= len(new_path):
    return new_path

  segments = [0]
  for _ in new_path:
    if _ in existing_path:
      if segments[-1] <= 0:
        segments[-1] -= 1
      else:
        segments.append(-1)
    else:
      if segments[-1] >= 0:
        segments[-1] += 1
      else:
        segments.append(1)

  # the whole path already exists or the whole path is not exists
  if len(segments) == 1:
    return [] if segments[0] <= 0 else new_path

  while len(segments) > 1:
    shortest_seg = min(_ for _ in segments if _ > 0)
    if shortest_seg >= minsize:
      break

    if segments[0] == shortest_seg:
      target_idx = 0
      next_idx = 1
    elif segments[-1] == shortest_seg:
      target_idx = -1
      next_idx = -2
    else:
      # the shortes unique segment is the middle one so it have both, left and right neighbors
      target_idx = segments.index(shortest_seg)

      neg_score = int((segments[target_idx] - segments[target_idx - 1]) <= minsize)
      pos_score = int((segments[target_idx] - segments[target_idx + 1]) <= minsize)

      if neg_score == pos_score:
        try:
          if segments[target_idx - 2] < minsize:
            neg_score += 1
        except IndexError:
          pass

        try:
          if segments[target_idx + 2] < minsize:
            pos_score += 1
        except IndexError:
          pass

      if neg_score == pos_score:
        try:
          neg_score -= segments[target_idx - 2]
          pos_score -= segments[target_idx + 2]
        except IndexError:
          pass

      if neg_score >= pos_score:
        # left direction requires right bound based indexing
        target_idx -= len(segments)
        next_idx = target_idx - 1
      else:
        next_idx = target_idx + 1

    if segments[next_idx] < (segments[target_idx] - minsize):
      # non-unique segment is long enough
      segments[next_idx] += minsize - segments[target_idx]
      segments[target_idx] = minsize
    else:
      # merge 3 segments
      try:
        segments[target_idx] -= segments.pop(next_idx)
        segments[target_idx] += segments.pop(next_idx)
      except IndexError:
        pass

  updated_path = []
  i_ofst = 0
  for seg in segments:
    if seg > 0:
      updated_path.extend(new_path[i_ofst:(i_ofst + seg)])
      i_ofst += seg
    else:
      i_ofst -= seg

  return updated_path


def _linearize_path(pairwise_path):
  segments = [0, ]
  linear_path = list(pairwise_path[0]) if pairwise_path else []

  for start_idx, stop_idx in pairwise_path[1:]:
    if start_idx != linear_path[-1]:
      segments.append(len(linear_path))
      linear_path.append(start_idx)
    linear_path.append(stop_idx)

  segments.append(len(linear_path))

  return linear_path, segments


def _limit_gradients(new_path, x, y, x_distances_table):
  if len(new_path) < 2:
    return new_path

  dx = np.array([x[stop_idx] - x[start_idx] for start_idx, stop_idx in new_path])
  if x.shape[1] == 1:
    np.fabs(dx, out=dx)
  else:
    dx = np.hypot.reduce(dx, axis=1)

  dy = np.array([y[stop_idx] - y[start_idx] for start_idx, stop_idx in new_path])
  if dy.shape[1] == 1:
    np.fabs(dy, out=dy)
  else:
    dy = np.hypot.reduce(dy, axis=1)
  dydx = dy.flatten()

  np.divide(dydx, dx.flatten(), out=dydx)
  if np.std(dydx) < np.finfo(float).eps:
    return new_path

  # we are maximizing sum of squared mean values (it's equivalent to minimization of sum of variances) while penalizing for small gap
  slice_pos = np.argmax([(np.mean(dydx[:split_index + 1])**2 + np.mean(dydx[split_index + 1:])**2).sum() * dydx[split_index] for split_index in xrange(dydx.size - 1)])
  slice_mask = dydx <= (0.5 * (dydx[slice_pos] + dydx[slice_pos + 1]))

  if not slice_mask.any() or slice_mask.all() or 2. * np.std(dydx[slice_mask]) >= np.std(dydx):
    return new_path
  return [new_path[_] for _ in np.where(slice_mask)[0]]


def _generate_tensor_fronts(tensor_structure, order, n_fronts):
  # Local group of neighbouring points indices, first element is always central [0, ..., 0]
  group_idx = np.repeat([[0, -1, 1]], len(tensor_structure), axis=0)
  group_idx = np.hstack([_.reshape(-1, 1) for _ in np.meshgrid(*group_idx)])

  # Compose all the possible fronts with central cluster point at the center of all fronts
  candidate_fronts = []
  n_neighbours = 3 ** len(tensor_structure)
  for i in np.arange(1, n_neighbours - 1):
    candidate_fronts_i = np.empty((n_neighbours - i - 1, 3), dtype=int)
    candidate_fronts_i[:, 0] = i
    candidate_fronts_i[:, 1] = 0
    candidate_fronts_i[:, 2] = np.arange(i + 1, n_neighbours)
    # Keep only candidate fronts with reasonable angle
    angles = _calc_angle(group_idx, candidate_fronts_i)
    candidate_fronts.append(candidate_fronts_i[angles > 0.74])
  candidate_fronts = np.vstack(candidate_fronts)

  # Memory inefficient implementation?? It works well for len(tensor_structure) < 7
  # candidate_fronts = np.vstack(np.triu_indices(group_idx.shape[0] - 1, 1)).T + 1
  # candidate_fronts = np.insert(candidate_fronts, 1, 0, axis=1)
  # candidate_fronts = candidate_fronts[_calc_angle(group_idx, candidate_fronts) > 0.74]

  shape = tuple(len(factors) for factors in tensor_structure)
  random_idx = _iterate_randomly(np.prod(shape))
  assert np.prod(shape) == order.size

  fronts = []
  while len(fronts) < n_fronts:
    # Select random point by grid indices
    current_idx = np.unravel_index(next(random_idx)[0], shape, order='F') # The dims argument was renamed shapes in Numpy 1.16 and removed in version 1.21.
    # Apply random shifts to construct one of candidate fronts
    random_shift = group_idx[candidate_fronts[int(np.random.random() * candidate_fronts.shape[0])]]
    # Convert grid indices to flat indices, clip indices if boundary point was shifted in a wrong direction
    front = np.ravel_multi_index((current_idx + random_shift).T, dims=shape, mode='clip', order='F')
    # Check for duplicated points within the front (can be caused by clip mode)
    if np.unique(front).size == front.size:
      fronts.append(front)
  return order[np.array(fronts)]


def _generate_fronts(x, n_fronts):
  scaler = Scaler()
  scaler.fit(x)
  x = scaler.transform(x)

  distances = _build_distance_table(x, 10)
  np.fill_diagonal(distances, np.inf)
  distances[distances < np.finfo(float).eps**0.5] = np.inf # remove duplicates
  # Coeff 1.5 to include distances up to sqrt(2) * max(min(distances))
  threshold = (2.**(1./x.shape[1])) * distances.min(axis=0).max()
  check_point = int(10 * max(x.shape[0], n_fronts))

  fronts = []
  random_idx = _iterate_randomly(x.shape[0])
  while len(fronts) < n_fronts:
    current_idx, step = next(random_idx)
    closest_points = np.nonzero(distances[current_idx] <= threshold)[0]
    if closest_points.size > 1:
      # Form candidate fronts starting from a random point
      np.random.shuffle(closest_points)
      candidate_fronts = np.empty((closest_points.size - 1, 3), dtype=int)
      candidate_fronts[:, 0] = closest_points[0]
      candidate_fronts[:, 1] = current_idx
      candidate_fronts[:, 2] = closest_points[1:]
      # Choose the front having maximum angle assumed by it's 3 points
      front = candidate_fronts[_calc_angle(x, candidate_fronts).argmax()]
      distances[front[0], front[1]] *= 1.5
      distances[front[1], front[0]] *= 1.5
      distances[front[2], front[1]] *= 1.5
      distances[front[1], front[2]] *= 1.5
      fronts.append(front)
    # Increase threshold to avoid infinite loops
    if step % check_point == 0:
      threshold *= 1.5

  return np.vstack(fronts)


def _iterate_randomly(n_values):
  step = 0
  indices = np.arange(n_values)
  while True:
    np.random.shuffle(indices)
    for idx in indices:
      step += 1 # step should start from 1
      yield idx, step


def _calc_angle(x, triples):
  x1 = x[triples[:, 1]]
  v1 = np.array(x1 - x[triples[:, 0]], dtype=float, copy=_SHALLOW)
  v2 = np.array(x1 - x[triples[:, 2]], dtype=float, copy=_SHALLOW)

  dot = (v1 * v2).sum(axis=1)
  #norm = np.hypot.reduce(v1, axis=1) * np.hypot.reduce(v2, axis=1)
  norm = np.sqrt((v1**2).sum(axis=1)*(v2**2).sum(axis=1)) # we don't need this precision here

  # if some of points have same x and different f the angle is assumed 180
  linear_triplets = norm <= 0
  if linear_triplets.any():
    norm[linear_triplets] = -dot[linear_triplets]

    # resolve possible 0/0 issues
    dot[norm == 0] = -1
    norm[norm == 0] = 1

  return np.arccos(np.round(dot / norm, 10)) / np.pi


def _build_route(x, y, w, n_routes=None, max_length=None, n_fronts=None, strategy="segmentation", tensor_structure=None, watcher=None):
  can_continue = watcher if watcher is not None and callable(watcher) else lambda _: True
  n = x.shape[0]

  if n < 2:
    raise ValueError('Not enough points are given')

  distances_table = None

  pairwise_path = []
  points_usage_count = np.zeros((n,), dtype=float)
  stop_list = np.zeros((n,), dtype=bool)

  if n <= 5:
    next_segment = _enumerate_all
  elif strategy == "pairwise":
    next_segment = _pairwise_path
  elif strategy == "furthest" and n <= 2000:
    distances_table = _build_distance_table(x, 10)
    next_segment = _furthest_point
  elif strategy == "clusterization":
    next_segment = _continuous_path
    max_length = None
  elif strategy == "segmentation":
    if tensor_structure is not None:
      fronts = _generate_tensor_fronts(tensor_structure=tensor_structure, order=np.lexsort(x.T), n_fronts=n_fronts)
    else:
      fronts = _generate_fronts(x=x, n_fronts=n_fronts)
    return _MultiRoute(x, y, w, fronts)
  else:
    next_segment = _continuous_path

  usage_table = set()
  for start_idx, stop_idx, new_segment in next_segment(n, n_routes, distances_table):
    # start and stop points counter should be updated outside _direct_route
    points_usage_count[start_idx] += 1.
    points_usage_count[stop_idx] += 1.
    stop_list[:] = False  # reset stop list

    new_path, distances_table = _direct_route(start_idx, stop_idx, x, distances_table, points_usage_count, stop_list)
    new_path = list(zip(new_path[:-1], new_path[1:]))  # convert new path to pairwise mode
    new_path = _cleanup_path(usage_table, new_path, 2)  # remove duplicating segements

    usage_table.update(new_path)
    pairwise_path.extend(new_path)

    if (max_length and len(pairwise_path) >= max_length) or not can_continue(None):
      pairwise_path = pairwise_path[:max_length]
      break

  if strategy == "clusterization" and can_continue(None):
    # check that all points are connected
    singletones = np.where(points_usage_count == 0)[0].tolist()
    if len(singletones) > 0:
      if len(singletones) % 2 == 1:
        start_idx = pairwise_path[-1][1]
      else:
        start_idx = singletones.pop(-1)

      for stop_idx in singletones:
        stop_list[:] = False  # reset stop list
        new_path, distances_table = _direct_route(start_idx, stop_idx, x, distances_table, points_usage_count, stop_list)
        new_path = list(zip(new_path[:-1], new_path[1:]))  # convert new path to pairwise mode
        new_path = _cleanup_path(usage_table, new_path, 2)  # remove duplicating segements

        usage_table.update(new_path)
        pairwise_path.extend(new_path)

        start_idx = stop_idx

  pairwise_path = _limit_gradients(pairwise_path, x, y, distances_table)
  linear_path, segments = _linearize_path(pairwise_path)

  # rearrange segments to minimize cross-segment  derivative change

  def _stat(data):
    mean, std = np.mean(data), np.std(data)
    return std, 0.2 * mean + 0.8 * std

  groups = [linear_path[i:j] for i, j in zip(segments[:-1], segments[1:])]
  group_stat = [_stat(y[segment]) for segment in groups]
  n_groups = len(group_stat)

  rearranged_groups = range(n_groups)

  if n_groups > 100:
    rearranged_groups = sorted(rearranged_groups, key=lambda i: group_stat[i][0])
    rearranged_groups = rearranged_groups[:n_groups - n_groups // 100]

  rearranged_groups = sorted(rearranged_groups, key=lambda i: group_stat[i][1])

  linear_path = []
  segments = [0]
  for i in rearranged_groups:
    linear_path.extend(groups[i])
    segments.append(len(linear_path))

  fronts = np.vstack((linear_path[:-2], linear_path[1:-1], linear_path[2:])).T
  return _MultiRoute(x, y, w, fronts)
