#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import numpy as np

from .. import loggers
from .. import shared as _shared
from .. import exceptions as _ex


def remove_coinciding_points(X, return_index=False, return_sorted=False, logger=None):
  if X.ndim == 1:
    X_sorted, unique_index = np.unique(X, return_index=True)
    unique_index.sort()
    if return_sorted:
      X = X_sorted
  elif X.shape[1] == 1:
    X_sorted, unique_index = np.unique(X[:, 0], return_index=True)
    unique_index.sort()
    if return_sorted:
      X = X_sorted.reshape(-1, 1)
  else:
    order = np.lexsort(X.T)
    sorted_unique_index = np.ones(shape=order.shape, dtype=bool)
    np.diff(X[order], axis=0).any(axis=1, out=sorted_unique_index[1:])

    inverse_order = np.empty(shape=order.shape, dtype=order.dtype)
    inverse_order[order] = np.arange(order.shape[0], dtype=order.dtype)
    unique_index = np.where(sorted_unique_index[inverse_order])[0]
    unique_index.sort()
    if return_sorted:
      X = X[order[sorted_unique_index]]
    del order
    del sorted_unique_index
    del inverse_order

  if logger and len(unique_index) < len(X):
    logger(loggers.LogLevel.INFO, "%d duplicated points were excluded from the training dataset." % (len(X) - len(unique_index)))

  if not return_sorted and len(unique_index) < len(X):
    X = X[unique_index]

  return (X, unique_index) if return_index else X


def check_missed_points(sample, subsample):
  '''
  Test whether each row of sample is also present in subsample (numpy.in1d analogue for 2d arrays).
  Returns a boolean array the same length as sample that is True where an element of sample is in subsample.

  Another implementation:
  dtype = np.dtype((str, sample.dtype.itemsize * sample.shape[1])) # np.void doesn't work in numpy 1.6
  sample_view = np.ascontiguousarray(sample).view(dtype).ravel()
  subsample_view = np.ascontiguousarray(subsample).view(dtype).ravel()
  return ~np.in1d(sample_view, subsample_view, True)

  '''
  missed_points_idx = np.zeros(sample.shape[0], bool)
  sorted_idx = np.lexsort(sample.T[::-1])
  sample = sample[sorted_idx]

  missed_points_count = 0
  subsample = subsample[np.lexsort(subsample.T[::-1])]

  for i, subsample_row in enumerate(subsample):
    while np.any(sample[i + missed_points_count] != subsample_row):
      missed_points_idx[i + missed_points_count] = True
      missed_points_count += 1
  missed_points_idx[subsample.shape[0] + missed_points_count:] = True

  return missed_points_idx[np.argsort(sorted_idx)]


def calc_cluster_size(options, dim_x, sample_size, relaxed_sample_size=False):
  number_of_clusters = np.asarray(_shared.parse_json(options.get('GTApprox/MoANumberOfClusters')), dtype=int)
  number_of_clusters = number_of_clusters.reshape(number_of_clusters.size)
  min_cluster_size = 2 * dim_x + 3
  # [] is 'Auto' for MoANumberOfClusters, i.e. choose automatically from range using BIC
  if 0 == number_of_clusters.size:
    accelerator = max(1, min(5, int(options.get('GTApprox/Accelerator'))))
    n_tries = [5, 4, 3, 2, 2][accelerator - 1]
    max_number_of_clusters = int(np.ceil((2. * sample_size)**0.333)) # kind of Rice rule for the number of histogram bins
    max_number_of_clusters = min(max(1, sample_size // min_cluster_size), max_number_of_clusters)
    number_of_clusters = np.unique(np.linspace(1, max_number_of_clusters, n_tries, True).astype(int))
  elif np.any(number_of_clusters <= 0):
    raise _ex.InvalidOptionsError('The number of clusters should be greater than zero: %s' % str(number_of_clusters))

  number_of_clusters.sort()

  if options.get('GTApprox/MoATechnique').lower() == 'lr':
    min_cluster_size = 1
  elif _shared.parse_bool(options.get('GTApprox/LinearityRequired')):
    min_cluster_size = 1
  min_sample_size = max(number_of_clusters[0] * min_cluster_size, 2)

  if sample_size < min_sample_size:
    if relaxed_sample_size and sample_size >= number_of_clusters[0]:
      # well, let's try.
      min_cluster_size = int(sample_size // number_of_clusters[0])
      return number_of_clusters[0:1], number_of_clusters[0] * min_cluster_size, min_cluster_size
    else:
      raise _ex.InvalidProblemError('Training sample is too small!')

  # remove numbers of clusters for which training sample is too small
  max_number_of_clusters = int(sample_size // min_cluster_size)
  i = len(number_of_clusters)
  while i > 0:
    i -= 1
    if number_of_clusters[i] <= max_number_of_clusters:
      number_of_clusters = number_of_clusters[:i + 1]
      break
  return number_of_clusters, min_sample_size, min_cluster_size


class Scaler(object):
  def __init__(self, with_mean=True, with_std=True, logger=None):
    self.with_mean = with_mean
    self.with_std = with_std
    self.logger = logger

  def fit(self, X, y=None, rm_duplicates=True, weights=None, tol=None, comment=None):
    """
    Compute the mean and std to be used for later scaling

    Parameters
    ----------
    :param X: the data used to compute the mean and standard deviation
    :type X: :term:`array-like`
    :return: One of the following strings identifying supplemenatry data used for fitting: `NoSupplementaryData`, `PointsWeight`, `OutputNoiseVariance`
    """
    if weights is not None and tol is not None:
      raise _ex.InvalidProblemError('Both points weights and output noise variance are given.')

    X = np.array(X, dtype=float, copy=_shared._SHALLOW)
    if 1 == X.ndim:
      X = X.reshape(-1, 1)

    supp_data = 'NoSupplementaryData'

    prefix = _shared.make_prefix(comment)

    if weights is not None:
      tot_weight = weights.sum()
      if tot_weight <= np.finfo(float).tiny:
        self.mean = np.zeros(X.shape[1])
        self.std = np.zeros(X.shape[1]) if self.with_std else np.ones((X.shape[1],), dtype=float)
        if self.logger:
          self.logger(loggers.LogLevel.WARN, prefix + 'Degenerated sample detected: all input points have zero weight.')
        return 'NoSupplementaryData'

      if rm_duplicates:
        # Considering the same points wth different weights are different.
        X = remove_coinciding_points(X=np.hstack((X, weights.reshape(-1, 1))), logger=self.logger)
        weights = X[:, -1]
        X = X[:, :-1]

      if self.with_std or self.with_mean:
        supp_data = 'PointsWeight'
        weighted_mean = np.mean(X * weights.reshape(-1, 1), axis=0) * len(X) / tot_weight

      self.mean = weighted_mean if self.with_mean else np.zeros((X.shape[1],), dtype=float)

      if self.with_std:
        weighted_x = X - weighted_mean.reshape(1, -1)
        np.multiply(weighted_x, weighted_x, out=weighted_x)
        np.multiply(weighted_x, weights.reshape(-1, 1), out=weighted_x)
        self.std = np.sqrt(weighted_x.mean(axis=0) * len(X) / tot_weight)
    elif tol is not None:
      if rm_duplicates:
        # Considering the same points wth different weights are different.
        X = remove_coinciding_points(X=np.hstack((X, tol)), logger=self.logger)
        tol = X[:, -len(tol[0]):]
        X = X[:, :-len(tol[0])]

      if self.with_std or self.with_mean:
        x_mean = X.mean(axis=0)

      self.mean = x_mean if self.with_mean else np.zeros((X.shape[1],), dtype=float)

      if self.with_std:
        X_squared = np.multiply(X, X)
        tol_mask = np.isfinite(tol)
        if tol_mask.all():
          np.add(X_squared, tol, out=X_squared)
          supp_data = 'OutputNoiseVariance'
        elif tol_mask.any():
          tol_mask = tol_mask.flatten()
          X_squared.flat[tol_mask] += tol.flat[tol_mask]
          supp_data = 'OutputNoiseVariance'
        self.std = np.sqrt(np.clip(np.mean(X_squared, axis=0) - x_mean * x_mean, 0., np.inf))
    else:
      if rm_duplicates:
        X = remove_coinciding_points(X=X, logger=self.logger)
      self.mean = X.mean(axis=0) if self.with_mean else np.zeros((X.shape[1],), dtype=float)
      self.std = X.std(axis=0, ddof=0) if self.with_std else np.ones((X.shape[1],), dtype=float)

    if self.with_std:
      const_cols = ~np.logical_and(np.isfinite(self.std), np.ptp(X, axis=0) > np.finfo(float).tiny)
      self.std[const_cols] = 0.0

      # if all columns are constant leave only first column
      if const_cols.all():
        const_cols[0] = False
        self.std[0] = 1.

      if const_cols.any() and self.logger:
        const_cols_list = ", ".join(("x[%d]=%g" % (_, self.mean[_])) for _ in np.where(const_cols)[0])
        self.logger(loggers.LogLevel.WARN, "%sClustering ignores the following constant input variables: %s" % (prefix, const_cols_list))

    return supp_data

  def transform(self, X, y=None):
    """
    Perform normalization by centering and scaling, removing constant columns.

    Parameters
    ----------
    :param X: train points
    :type points: :term:`array-like`
    :return: X_scaled: normalized data
    """
    X = _shared.as_matrix(X, shape=(None, len(self.mean)))

    variable_cols = self.std > np.finfo(float).tiny
    if not variable_cols.any():
      return np.zeros((len(X), 1), dtype=float)
    elif variable_cols.all():
      variable_cols = slice(X.shape[1])

    return (X[:, variable_cols] - self.mean[variable_cols][np.newaxis]) * (1. / self.std[variable_cols][np.newaxis])

class StaticScaler(Scaler):
  def __init__(self, mean, std, payload=None):
    super(StaticScaler, self).__init__(True, True, None)
    self.mean = _shared.as_matrix(mean, (1, None)).reshape(-1)
    self.std = _shared.as_matrix(std, (1, len(self.mean))).reshape(-1)
    self.payload = payload
