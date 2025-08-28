#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

#
# This module uses code from scipy, the Python library for scientific computing.
# https://www.scipy.org
#
# SciPy license
#
# Copyright © 2001, 2002 Enthought, Inc.
# All rights reserved.
#
# Copyright © 2003-2013 SciPy Developers.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of Enthought nor the names of the SciPy Developers may be used
#   to endorse or promote products derived from this software without specific prior
#   written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
from __future__ import division

import numpy as np
from numpy.ma import nomask
import itertools

from ..six.moves import xrange, range, zip
from .. import exceptions as _ex
from .. import shared as _shared
from .outlier_detection import _MinCovDet, _calculate_median_absolute_deviation


def __watch(watcher, obj):
  if watcher:
    retval = watcher(obj)
    if not retval:
      raise _ex.UserTerminated()

def _calculate_elementary_statistics(train_data, confidence_level=0.95, is_robust=False, is_rank=False):
  """Implements calculation of elementary statistics.
  """
  # calculate elementary statistics
  medians = np.median(train_data, axis=0)
  means = train_data.mean(axis=0)
  minimums = train_data.min(axis=0)
  maximums = train_data.max(axis=0)
  ranges = maximums - minimums

  number_points, data_dimension = train_data.shape

  quantile_lower = np.empty(0)
  quantile_upper = np.empty(0)
  if confidence_level == 0.5:
    quantile_lower = medians
    quantile_upper = medians
  else:
    target_index = max(0, int(float(number_points) * (1. - confidence_level)) - 1)
    sort_column = lambda column_data: np.sort(column_data.conj()).conj()
    sorted_columns = np.apply_along_axis(sort_column, axis=0, arr=train_data)

    quantile_lower = sorted_columns[target_index,:]
    quantile_upper = sorted_columns[number_points - 1 - target_index,:]

  # calculate stds and correlations
  stds = np.std(train_data, axis=0, ddof=1)
  nonconstant_indexes = np.nonzero(stds)[0]
  constant_indexes = [i for i in range(data_dimension) if i not in nonconstant_indexes]
  correlations = np.zeros((data_dimension, data_dimension))

  for i in constant_indexes:
    for j in constant_indexes:
      correlations[i, j] = np.nan

  if nonconstant_indexes.size > 0:
    if is_robust:
      rand_gen = np.random.RandomState(0)

      if number_points > 1:
        if data_dimension > 1:
          mcd_fit = _MinCovDet(random_state=rand_gen).fit(train_data)

          covariances = mcd_fit.covariance_

          stds = [np.sqrt(covariances[i][i]) for i in range(data_dimension)]
          for i in nonconstant_indexes:
            for j in nonconstant_indexes:
              correlations[i][j] = covariances[i][j] / stds[i] / stds[j]
        else:
          mads = _calculate_median_absolute_deviation(train_data)
          stds = [1.4826 * mad for mad in mads]
          correlations = [1]
      else:
        correlations = [1] * data_dimension
        stds = [0] * data_dimension
    else:
      correlations[np.ix_(nonconstant_indexes, nonconstant_indexes)] = np.corrcoef(train_data[:, nonconstant_indexes].T)

  if any(is_rank):
    rank_indexes = np.nonzero(is_rank)[0]
    rank_train_data = train_data[:, rank_indexes]
    rank_correlation_matrix = _kendall_correlation(rank_train_data)

    for first_index in xrange(rank_indexes.shape[0]):
      for second_index in xrange(rank_indexes.shape[0]):
        correlations[rank_indexes[first_index]][rank_indexes[second_index]] = rank_correlation_matrix[first_index, second_index]

  elementary_statistics = {'min': np.array(minimums),
                           'max': np.array(maximums),
                           'mean': np.array(means),
                           'median': np.array(medians),
                           'range': np.array(ranges),
                           'quantile_lower': np.array(quantile_lower),
                           'quantile_upper': np.array(quantile_upper),
                           'std': np.array(stds),
                           'correlation': np.array(correlations)}

  return elementary_statistics


def _find_repeats(arr):
  arr = np.array(arr, dtype=float, copy=_shared._SHALLOW)

  # This function assumes it may clobber its input.
  if not len(arr):
    return np.array(0, dtype=float), np.array(0, dtype=int)

  arr = arr.ravel()
  arr.sort()

  # Taken from NumPy 1.9's np.unique.
  change = np.concatenate(([True], arr[1:] != arr[:-1]))
  unique = arr[change]
  change_idx = np.concatenate(np.nonzero(change) + ([arr.size],))
  freq = np.diff(change_idx)
  atleast2 = freq > 1
  return unique[atleast2], freq[atleast2]


def find_repeats(arr):
  """Find repeats in arr and return a tuple (repeats, repeat_count).
  The input is cast to float64. Masked values are discarded.
  Parameters
  ----------
  arr : sequence
      Input array. The array is flattened if it is not 1D.
  Returns
  -------
  repeats : ndarray
      Array of repeated values.
  counts : ndarray
      Array of counts.
  """
  # Make sure we get a copy. ma.compressed promises a "new array", but can
  # actually return a reference.
  compr = np.asarray(np.ma.compressed(arr), dtype=np.float64)
  if compr is arr or compr.base is arr:
    compr = compr.copy()
  return _find_repeats(compr)


def count_tied_groups(x, use_missing=False):
  """
  Counts the number of tied values.
  Parameters
  ----------
  x : sequence
      Sequence of data on which to counts the ties
  use_missing : bool, optional
      Whether to consider missing values as tied.
  Returns
  -------
  count_tied_groups : dict
      Returns a dictionary (nb of ties: nb of groups).
  Examples
  --------
  >>> from scipy.stats import mstats
  >>> z = [0, 0, 0, 2, 2, 2, 3, 3, 4, 5, 6]
  >>> mstats.count_tied_groups(z)
  {2: 1, 3: 2}
  In the above example, the ties were 0 (3x), 2 (3x) and 3 (2x).
  >>> z = np.ma.array([0, 0, 1, 2, 2, 2, 3, 3, 4, 5, 6])
  >>> mstats.count_tied_groups(z)
  {2: 2, 3: 1}
  >>> z[[1,-1]] = np.ma.masked
  >>> mstats.count_tied_groups(z, use_missing=True)
  {2: 2, 3: 1}
  """
  nmasked = np.ma.getmask(x).sum()
  # We need the copy as find_repeats will overwrite the initial data
  data = np.ma.compressed(x).copy()
  (ties, counts) = find_repeats(data)
  nties = {}
  if len(ties):
    nties = dict(zip(np.unique(counts), itertools.repeat(1)))
    nties.update(dict(zip(*find_repeats(counts))))

  if nmasked and use_missing:
    try:
      nties[nmasked] += 1
    except KeyError:
      nties[nmasked] = 1

  return nties


def rankdata(data, axis=None, use_missing=False):
  """Returns the rank (also known as order statistics) of each data point
  along the given axis.
  If some values are tied, their rank is averaged.
  If some values are masked, their rank is set to 0 if use_missing is False,
  or set to the average rank of the unmasked values if use_missing is True.
  Parameters
  ----------
  data : sequence
      Input data. The data is transformed to a masked array
  axis : {None,int}, optional
      Axis along which to perform the ranking.
      If None, the array is first flattened. An exception is raised if
      the axis is specified for arrays with a dimension larger than 2
  use_missing : bool, optional
      Whether the masked values have a rank of 0 (False) or equal to the
      average rank of the unmasked values (True).
  """
  def _rank1d(data, use_missing=False):
    n = data.count()
    rk = np.empty(data.size, dtype=float)
    idx = data.argsort()
    rk[idx[:n]] = np.arange(1, n+1)

    if use_missing:
      rk[idx[n:]] = (n+1)/2.
    else:
      rk[idx[n:]] = 0

    repeats = find_repeats(data.copy())
    for r in repeats[0]:
      condition = (data == r).filled(False)
      rk[condition] = rk[condition].mean()
    return rk

  data = np.ma.array(data)
  if axis is None:
    if data.ndim > 1:
      return _rank1d(data.ravel(), use_missing).reshape(data.shape)
    else:
      return _rank1d(data, use_missing)
  else:
    return np.ma.apply_along_axis(_rank1d, axis,data, use_missing).view(np.ndarray)


def _kendall_num(x, y=None, watcher=None):
  """
  Computes values of Kendall’s tau-b numerator
  Parameters
  ----------
  x : sequence
      Input sample (for example, time).
  y : sequence
      Output sample.
  Returns
  -------
  numerator : 2d ndarray, float
      Kendall’s tau-b numerators matrix
  """
  n = x.shape[0]

  __watch(watcher, None)
  next_watch = max(2, 1000 // n) # some kind of complexity threshold

  if y is not None and y is not x:
    tau = np.zeros((y.shape[1], x.shape[1]), dtype=float)
    for i in xrange(n - 1):
      if i >= next_watch:
        __watch(watcher, None)
        next_watch *= 2 # we are in cycle with decreasing complexity
      sign_x = np.sign(x[i+1:,:] - x[i,:])
      sign_y = np.sign(y[i+1:,:] - y[i,:])
      np.add(tau, np.dot(sign_x.T, sign_y).T, out=tau)
  else:
    tau = np.zeros((x.shape[1], x.shape[1]), dtype=float)
    for i in xrange(n - 1):
      if i >= next_watch:
        __watch(watcher, None)
        next_watch *= 2 # we are in cycle with decreasing complexity
      sign_x = np.sign(x[i+1:,:] - x[i,:])
      np.add(tau, np.dot(sign_x.T, sign_x).T, out=tau)

  return tau


def _kendall_denom(x, y=None):
  '''
  Computes values of Kendall’s tau-b denominator sqrt((Np + Tx) * (Np + Ty)),
  where Np is the number of all pairs pairs, Tx the number of ties only in x, and Ty the number of ties only in y.
  Parameters
  ----------
  x : sequence
      Input sample (for example, time).
  y : sequence
      Output sample.
  Returns
  -------
  denominator : 2d ndarray, float
      Kendall’s tau-b denominators matrix
  '''
  n = x.shape[0]
  Np = n * (n - 1) / 2.0

  dim_x = x.shape[1]
  Tx = np.zeros(dim_x)
  for x_feature in xrange(dim_x):
    xties = count_tied_groups(x[:, x_feature])
    Tx[x_feature] = np.sum([xties[k]*k*(k-1) for k in xties], dtype=np.float64) / 2.0

  if y is not None:
    dim_y = y.shape[1]
    Ty = np.zeros(dim_y)
    denom = np.ndarray((dim_y, dim_x), dtype=np.float64)
    for y_feature in xrange(dim_y):
      yties = count_tied_groups(y[:, y_feature])
      Ty[y_feature] = np.sum([yties[k]*k*(k-1) for k in yties], dtype=np.float64) / 2.0
      for x_feature in xrange(dim_x):
        denom[y_feature, x_feature] = np.ma.sqrt((Np - Tx[x_feature]) * (Np - Ty[y_feature]))
  else:
    denom = np.ndarray((dim_x, dim_x), dtype=np.float64)
    for x_feature in xrange(dim_x):
      denom[x_feature, x_feature] = Np - Tx[x_feature]
      for y_feature in xrange(x_feature + 1, dim_x):
        denom[y_feature, x_feature] = np.ma.sqrt((Np - Tx[x_feature]) * (Np - Tx[y_feature]))
        denom[x_feature, y_feature] = denom[y_feature, x_feature]

  return denom


def _kendall_correlation(x, y=None, denom=None, watcher=None):
  '''
  Main function for calculating kendall correlation for samples.
  The case when y=None is supported
  Parameters
  ----------
  x : sequence
      Input sample (for example, time).
  y : sequence
      Output sample.
  denominator : 2d ndarray, float
      Calculated values of Kendall’s tau-b denominator sqrt((Np + Tx) * (Np + Ty)),
      where Np is the number of all pairs pairs, Tx the number of ties only in x, and Ty the number of ties only in y.
      If 0, tau-a statistic will be calculated without making any adjustment for ties (denom = Np).
  '''
  x = np.asarray(x)
  if x.ndim == 2:
    dim_x = x.shape[1]
  else:
    dim_x = 1
    x = x.reshape(-1, 1)

  if y is not None and y is not x:
    y = np.asarray(y)
    if y.ndim == 2:
      dim_y = y.shape[1]
    else:
      dim_y = 1
      y = y.reshape(-1, 1)

  if denom is None:
    denom = _kendall_denom(x, y)
  scores = _kendall_num(x, y, watcher=watcher) / denom

  return scores


def _update_incremental_statistics(train_case, elementary_statistics):
  """Updates elementary statistics for new point.

  Parameters
  train_case: array-like, shape (1, n_features)
    The data string, with n_features features.
  elementary_statistics: dictionary with elementary statistics
    * 'mean'
    * 'min'
    * 'max'

  Returns

  elementary_statistics: dictionary with elementary statistics

  """
  for dimension in xrange(0, train_case.shape[1]):
    elementary_statistics['minimums'][0, dimension] = min(train_case[0, dimension], elementary_statistics['minimums'][0, dimension])
    elementary_statistics['maximums'][0, dimension] = max(train_case[0, dimension], elementary_statistics['maximums'][0, dimension])
    elementary_statistics['means'][0, dimension] = elementary_statistics['means'][0, dimension] + train_case[0, dimension]

  return dict(elementary_statistics)


def _calculate_incremental_statistics(train_points, train_values):
  """Calculates incremental statistics such as mean and maximum value for a given sample.
  """
  train_points = np.array(train_points, dtype=np.float64)
  train_values = np.array(train_values, dtype=np.float64)

  if train_points.shape[0] != train_values.shape[0]:
    raise _ex.GTException('The number of train points is not equal to the number of train values')

  number_points = train_points.shape[0]

  if number_points <= 1:
    raise _ex.GTException('Train points must have at least two points')

  input_dimension = _shared.get_size(train_points[0])

  if input_dimension <= 0:
    raise _ex.GTException('Points dimensionality should be greater than zero!')

  output_dimension = _shared.get_size(train_values[0])

  if output_dimension <= 0:
    raise _ex.GTException('Values dimensionality should be greater than zero!')

  train_data = np.hstack((train_points, train_values))

  elementary_statistics = {'minimums': train_data.min(axis=0), 'maximums': train_data.max(axis=0), 'means': train_data.mean(axis=0)}
  return elementary_statistics
