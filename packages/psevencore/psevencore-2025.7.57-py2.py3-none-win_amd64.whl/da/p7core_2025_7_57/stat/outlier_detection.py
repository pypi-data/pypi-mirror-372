#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import warnings
import numpy as np
from ..six.moves import xrange, range, zip
from .. import exceptions as _ex
from .. import shared as _shared
from .utilities import _get_positive_erf, _fast_logdet, _pinvh, _factorize_covariance, _diag_slice
from ..utils import _chi2

def _mahal_accum_dist(sample_centered, covariances):
  s, u = np.linalg.eigh(covariances)

  cutoff = 1.e6 * np.finfo(float).eps * np.max(s)
  above_cutoff = s > cutoff
  psigma_diag = np.zeros_like(s)
  psigma_diag[above_cutoff] = 1.0 / np.sqrt(s[above_cutoff])
  np.multiply(u, psigma_diag, out=u)
  rcovariances = np.dot(u, np.conjugate(u).T)

  work = np.dot(sample_centered, rcovariances)
  return np.multiply(work, sample_centered, out=work).sum(axis=1)

def _calculate_median_absolute_deviation(train_data):
  train_data = np.array(train_data, dtype=float, copy=_shared._SHALLOW)
  number_points = train_data.shape[0]

  median_value = np.median(train_data, axis=0)
  centered_data = train_data - [median_value] * number_points
  median_absolute_deviation = np.median(np.abs(centered_data), axis=0)

  return median_absolute_deviation

def _get_outlier_probabilities(sample, covariances, lambda_value=3):
  sample = np.array(sample, dtype=float, copy=_shared._SHALLOW)
  covariances = np.atleast_2d(covariances)
  number_points, number_dimensions = sample.shape

  L = _factorize_covariance(covariances)

  distance_standard_deviation = np.vectorize(lambda i: np.hypot.reduce(np.dot(L, (sample - sample[[i]]).T).reshape(-1)), otypes=[np.float64])(xrange(number_points))
  np.divide(distance_standard_deviation, float(max(1, number_points - 1))**0.5, out=distance_standard_deviation)

  pdist_sum = np.zeros(number_points)
  pdist_number = np.zeros(number_points)

  for point in xrange(number_points - 1):
    if number_dimensions > 1:
      # Note dot(L, sample) is number_dimensions-by-number_points dimensional matrix
      other_point_distances = np.hypot.reduce(np.dot(L, (sample[point + 1:] - sample[[point]]).T), axis=0)
    else:
      # Its rather fix for bug in numpy 1.6 implementation of the np.hypot.reduce than optimization of the simple case
      other_point_distances = (sample[point + 1:] - sample[[point]]).reshape(-1)
      np.multiply(other_point_distances, L[0, 0], out=other_point_distances)
      np.fabs(other_point_distances, out=other_point_distances)

    close_to_point = other_point_distances < lambda_value * distance_standard_deviation[point]
    pdist_sum[point] += distance_standard_deviation[point + 1:][close_to_point].sum()
    pdist_number[point] += np.count_nonzero(close_to_point)

    close_to_point = other_point_distances < lambda_value * distance_standard_deviation[point + 1:]
    pdist_sum[point + 1:][close_to_point] += distance_standard_deviation[point]
    pdist_number[point + 1:][close_to_point] += 1

  PLOF = np.multiply(distance_standard_deviation, pdist_number)
  np.subtract(np.divide(PLOF, pdist_sum, out=PLOF), 1., out=PLOF)

  nPLOF = lambda_value * np.hypot.reduce(PLOF) / (number_points * 0.5)**0.5

  if nPLOF < np.finfo(float).tiny:
    return np.zeros(PLOF.shape)

  np.divide(np.fabs(PLOF, out=PLOF), nPLOF, out=PLOF)
  return np.vectorize(_get_positive_erf, otypes=[np.float64])(PLOF)

def _get_deviation_scores(sample, covariances):
  sample = np.array(sample, dtype=float, copy=_shared._SHALLOW)
  covariances = np.atleast_2d(covariances)
  _, number_dimensions = sample.shape

  location = sample.mean(axis=0)
  sample_centered = sample - location
  # get precision matrix in an optimized way

  dist = _mahal_accum_dist(sample_centered, covariances)
  chi2_distribution = _chi2(number_dimensions)
  scores = np.vectorize(chi2_distribution.cdf, otypes=[np.float64])(dist)

  return scores

"""
Robust location and covariance estimators.

Here are implemented estimators that are resistant to outliers.
"""

def _empirical_covariance(X, assume_centered=False, logger=None):
  """Computes the Maximum likelihood covariance estimator

  Parameters
  ----------
  X: 2D ndarray, shape (n_samples, n_features)
    Data from which to compute the covariance estimate

  assume_centered: Boolean
    If True, data are not centered before computation.
    Useful when working with data whose mean is almost, but not exactly
    zero.
    If False, data are centered before computation.

  Returns
  -------
  covariance: 2D ndarray, shape (n_features, n_features)
    Empirical covariance (Maximum Likelihood Estimator)

  """
  X = np.array(X)
  if X.ndim == 1:
    if X.size <= 0:
      raise _ex.GTException("Sample should be nonempty")
    X = X.reshape((X.size, 1))

    if logger:
      logger.warn("Only one sample available. You may want to reshape your data array.")
    else:
      warnings.warn("Only one sample available. You may want to reshape your data array.")

  if assume_centered:
    covariance = np.dot(X.T, X) / len(X)
  else:
    covariance = np.cov(X.T, bias=1)

  # add minimal regularization to the covariance main diagonal
  covariance_diag = _diag_slice(covariance)
  np.maximum(covariance_diag, np.finfo(float).eps, covariance_diag)

  return covariance


###############################################################################
### Minimum Covariance Determinant
#   Implementing of an algorithm by Rousseeuw & Van Driessen described in
#   (A Fast Algorithm for the Minimum Covariance Determinant Estimator,
#   1999, American Statistical Association and the American Society
#   for Quality, TECHNOMETRICS)
###############################################################################
def _c_step(X, n_support, remaining_iterations=30, initial_estimates=None,
            cov_computation_method=_empirical_covariance,
            random_state=None, logger=None):
  """C_step procedure described in [Rouseeuw1984] aiming at computing the MCD

  Parameters
  ----------
  X: array-like, shape (n_samples, n_features)
    Data set in which we look for the n_support observations whose
    scatter matrix has minimum determinant
  n_support: int, > n_samples / 2
    Number of observations to compute the robust estimates of location
    and covariance from.
  remaining_iterations: int
    Number of iterations to perform.
    According to [Rouseeuw1999], two iterations are sufficient to get close
    to the minimum, and we never need more than 30 to reach convergence.
  initial_estimates: 2-tuple
    Initial estimates of location and shape from which to run the _c_step
    procedure:
    - initial_estimates[0]: an initial location estimate
    - initial_estimates[1]: an initial covariance estimate
  random_state: integer or numpy.RandomState, optional
      The random generator used. If an integer is given, it fixes the
      seed. Defaults to the global numpy random number generator.

  Returns
  -------
  location: array-like, shape (n_features,)
    Robust location estimates
  covariance: array-like, shape (n_features, n_features)
    Robust covariance estimates
  support: array-like, shape (n_samples,)
    A mask for the `n_support` observations whose scatter matrix has
    minimum determinant

  References
  ----------

  .. [Rouseeuw1999] A Fast Algorithm for the Minimum Covariance Determinant
    Estimator, 1999, American Statistical Association and the American
    Society for Quality, TECHNOMETRICS

  """
  X = np.array(X, dtype=float, copy=_shared._SHALLOW)

  n_samples, n_features = X.shape

  # Initialisation
  if initial_estimates is None:
    # compute initial robust estimates from a random subset
    support = np.zeros(n_samples, dtype=bool)
    support[random_state.permutation(n_samples)[:n_support]] = True
    location = X[support].mean(0)
    covariance = cov_computation_method(X[support], logger=logger)
  else:
    # get initial robust estimates from the function parameters
    location = initial_estimates[0]
    covariance = initial_estimates[1]
    # run a special iteration for that case (to get an initial support)
    dist = _mahal_accum_dist(X - location, covariance)
    # compute new estimates
    support = np.zeros(n_samples, dtype=bool)
    support[np.argsort(dist)[:n_support]] = True
    location = X[support].mean(0)
    covariance = cov_computation_method(X[support], logger=logger)
  previous_det = np.inf

  # Iterative procedure for Minimum Covariance Determinant computation
  det = _fast_logdet(covariance)
  while remaining_iterations > 0:
    # save old estimates values
    previous_location = location
    previous_covariance = covariance
    previous_det = det
    previous_support = support
    # compute a new support from the full data set mahalanobis distances
    dist = _mahal_accum_dist(X - location, covariance)
    # compute new estimates
    support = np.zeros(n_samples, dtype=bool)
    support[np.argsort(dist)[:n_support]] = True
    location = X[support].mean(axis=0)
    covariance = cov_computation_method(X[support], logger=logger)
    det = _fast_logdet(covariance)

    # check early stopping criteria
    if np.allclose(det, previous_det):
      # optimization converged
      if logger:
        logger.info("Optimal couple (location, covariance) found before"
                    "ending iterations (%d left)" % (remaining_iterations))
      return previous_location, previous_covariance, previous_det, previous_support, dist
    elif det > previous_det:
      # determinant has increased
      return previous_location, previous_covariance, previous_det, previous_support, dist

    # update remaining iterations number
    remaining_iterations -= 1

  if remaining_iterations <= 0 and logger:
    logger.info('Maximum number of iterations reached')

  dist = _mahal_accum_dist(X - location, covariance)
  return location, covariance, det, support, dist

def _select_candidates(X, n_support, n_trials, select=1, n_iter=30,
                       cov_computation_method=_empirical_covariance,
                       random_state=None, logger=None):
  """Finds the best pure subset of observations to compute MCD from it.

  The purpose of this function is to find the best sets of n_support
  observations with respect to a minimization of their covariance
  matrix determinant. Equivalently, it removes n_samples-n_support
  observations to construct what we call a pure data set (i.e. not
  containing outliers). The list of the observations of the pure
  data set is referred to as the `support`.

  Starting from a random support, the pure data set is found by the
  _c_step procedure introduced by Rousseeuw and Van Driessen in
  [Rouseeuw1999].

  Parameters
  ----------
  X: array-like, shape (n_samples, n_features)
    Data (sub)set in which we look for the n_support purest observations
  n_support: int, [(n + p + 1)/2] < n_support < n
    The number of samples the pure data set must contain.
  select: int, int > 0
    Number of best candidates results to return.
  n_trials: int, nb_trials > 0 or 2-tuple
    Number of different initial sets of observations from which to
    run the algorithm.
    Instead of giving a number of trials to perform, one can provide a
    list of initial estimates that will be used to iteratively run
    _c_step procedures. In this case:
    - n_trials[0]: array-like, shape (n_trials, n_features)
      is the list of `n_trials` initial location estimates
    - n_trials[1]: array-like, shape (n_trials, n_features, n_features)
      is the list of `n_trials` initial covariances estimates
  n_iter: int, nb_iter > 0
    Maximum number of iterations for the _c_step procedure.
    (2 is enough to be close to the final solution. "Never" exceeds 20)
  random_state: integer or numpy.RandomState, optional
    The random generator used. If an integer is given, it fixes the
    seed. Defaults to the global numpy random number generator.

  See Also
  ---------
  `_c_step` function

  Returns
  -------
  best_locations: array-like, shape (select, n_features)
    The `select` location estimates computed from the `select` best
    supports found in the data set (`X`)
  best_covariances: array-like, shape (select, n_features, n_features)
    The `select` covariance estimates computed from the `select`
    best supports found in the data set (`X`)
  best_supports: array-like, shape (select, n_samples)
    The `select` best supports found in the data set (`X`)

  References
  ----------
  .. [Rouseeuw1999] A Fast Algorithm for the Minimum Covariance Determinant
    Estimator, 1999, American Statistical Association and the American
    Society for Quality, TECHNOMETRICS

  """
  X = np.array(X, dtype=float, copy=_shared._SHALLOW)

  if _shared.is_integer(n_trials):
    run_from_estimates = False
  elif isinstance(n_trials, tuple):
    run_from_estimates = True
    estimates_list = n_trials
    n_trials = len(estimates_list[0])
  else:
    raise TypeError("Invalid 'n_trials' parameter, expected tuple or "
                    " integer, got %s (%s)" % (n_trials, type(n_trials)))

  # compute `n_trials` location and shape estimates candidates in the subset
  all_estimates = []
  if not run_from_estimates:
    # perform `n_trials` computations from random initial supports
    for j in xrange(n_trials):
      all_estimates.append(
          _c_step(X, n_support, remaining_iterations=n_iter,
                  cov_computation_method=cov_computation_method,
                  random_state=random_state, logger=logger))
  else:
    # perform computations from every given initial estimates
    for j in xrange(n_trials):
      initial_estimates = (estimates_list[0][j], estimates_list[1][j])
      all_estimates.append(_c_step(X, n_support, remaining_iterations=n_iter,
                                   initial_estimates=initial_estimates,
                                   cov_computation_method=cov_computation_method,
                                   random_state=random_state, logger=logger))
  all_locs_sub, all_covs_sub, all_dets_sub, all_supports_sub, all_ds_sub = zip(*all_estimates)
  # find the `n_best` best results among the `n_trials` ones
  index_best = np.argsort(all_dets_sub)[:select]
  best_locations = np.array(all_locs_sub)[index_best]
  best_covariances = np.array(all_covs_sub)[index_best]
  best_supports = np.array(all_supports_sub)[index_best]
  best_ds = np.array(all_ds_sub)[index_best]

  return best_locations, best_covariances, best_supports, best_ds

def _fast_mcd(X, support_fraction=None,
              cov_computation_method=_empirical_covariance,
              random_state=None, logger=None):
  """Estimates the Minimum Covariance Determinant matrix.

  Parameters
  ----------
  X: array-like, shape (n_samples, n_features)
    The data matrix, with p features and n samples.
  support_fraction: float, 0 < support_fraction < 1
      The proportion of points to be included in the support of the raw
      MCD estimate. Default is None, which implies that the minimum
      value of support_fraction will be used within the algorithm:
      [n_sample + n_features + 1] / 2
  random_state: integer or numpy.RandomState, optional
    The generator used to randomly subsample. If an integer is
    given, it fixes the seed. Defaults to the global numpy random
    number generator.

  Notes
  -----
  The FastMCD algorithm has been introduced by Rousseuw and Van Driessen
  in "A Fast Algorithm for the Minimum Covariance Determinant Estimator,
  1999, American Statistical Association and the American Society
  for Quality, TECHNOMETRICS".
  The principle is to compute robust estimates and random subsets before
  pooling them into a larger subsets, and finally into the full data set.
  Depending on the size of the initial sample, we have one, two or three
  such computation levels.

  Note that only raw estimates are returned. If one is interested in
  the correction and reweighting steps described in [Rouseeuw1999],
  see the _MinCovDet object.

  References
  ----------

  .. [Rouseeuw1999] A Fast Algorithm for the Minimum Covariance
     Determinant Estimator, 1999, American Statistical Association
     and the American Society for Quality, TECHNOMETRICS

  .. [Butler1993] R. W. Butler, P. L. Davies and M. Jhun,
     Asymptotics For The Minimum Covariance Determinant Estimator,
     The Annals of Statistics, 1993, Vol. 21, No. 3, 1385-1400

  Returns
  -------
  location: array-like, shape (n_features,)
    Robust location of the data
  covariance: array-like, shape (n_features, n_features)
    Robust covariance of the features
  support: array-like, type boolean, shape (n_samples,)
    a mask of the observations that have been used to compute
    the robust location and covariance estimates of the data set

  """
  X = np.array(X, dtype=float, copy=_shared._SHALLOW)
  if X.size == 0:
    raise _ex.GTException("Empty sample given")

  if X.ndim == 1:
    X = X.reshape((X.size, 1))
    if logger:
      logger.warn("Only one sample available. You may want to reshape your data array.")
    else:
      warnings.warn("Only one sample available. You may want to reshape your data array.")
  n_samples, n_features = X.shape

  # minimum breakdown value
  if support_fraction is None:
    n_support = int(np.ceil(0.5 * (n_samples + n_features + 1)))
  else:
    n_support = int(support_fraction * n_samples)

  # 1-dimensional case quick computation
  # (Rousseeuw, P. J. and Leroy, A. M. (2005) References, in Robust
  #  Regression and Outlier Detection, John Wiley & Sons, chapter 4)
  if n_features == 1:
    if n_support < n_samples:
      # find the sample shortest halves
      flatten_X = X.flatten()
      X_sorted = np.array(sorted(flatten_X))
      diff = X_sorted[n_support:] - X_sorted[:(n_samples - n_support)]

      halves_start = np.where(diff == min(diff))[0]

      # take the middle points' mean to get the robust location estimate
      location = 0.5 * (X_sorted[n_support + halves_start]
                        + X_sorted[halves_start]).mean()
      support = np.zeros(n_samples, dtype=bool)
      support[np.argsort(np.abs(X - location), 0)[:n_support]] = True
      covariance = np.array([[np.var(X[support])]])
      location = np.array([location])
    else:
      support = np.ones(n_samples)
      covariance = np.array([[np.var(X)]])
      location = np.array([np.mean(X)])
    dist = _mahal_accum_dist(X - location, covariance)
  ### Starting FastMCD algorithm for p-dimensional case
  if (n_samples > 500) and (n_features > 1):
    ## 1. Find candidate supports on subsets
    # a. split the set in subsets of size ~ 300
    n_subsets = n_samples // 300
    n_samples_subsets = n_samples // n_subsets
    samples_shuffle = random_state.permutation(n_samples)
    h_subset = int(np.ceil(n_samples_subsets * (n_support / float(n_samples))))
    # b. perform a total of 500 trials
    n_trials_tot = 500
    # c. select 10 best (location, covariance) for each subset
    n_best_sub = 10
    n_trials = max(10, n_trials_tot // n_subsets)
    n_best_tot = n_subsets * n_best_sub
    all_best_locations = np.zeros((n_best_tot, n_features))
    try:
      all_best_covariances = np.zeros((n_best_tot, n_features, n_features))
    except MemoryError:
      # The above is too big. Let's try with something much small
      # (and less optimal)
      n_best_sub = 2
      n_best_tot = n_subsets * n_best_sub
      all_best_locations = np.zeros((n_best_tot, n_features))
      all_best_covariances = np.zeros((n_best_tot, n_features, n_features))
    for i in range(n_subsets):
      low_bound = i * n_samples_subsets
      high_bound = low_bound + n_samples_subsets
      current_subset = X[samples_shuffle[low_bound:high_bound]]
      best_locations_sub, best_covariances_sub, _, _ = _select_candidates(
          current_subset, h_subset, n_trials,
          select=n_best_sub, n_iter=2,
          cov_computation_method=cov_computation_method,
          random_state=random_state, logger=logger)
      subset_slice = np.arange(i * n_best_sub, (i + 1) * n_best_sub)
      all_best_locations[subset_slice] = best_locations_sub
      all_best_covariances[subset_slice] = best_covariances_sub
    ## 2. Pool the candidate supports into a merged set
    ##    (possibly the full dataset)
    n_samples_merged = min(1500, n_samples)
    h_merged = int(np.ceil(n_samples_merged * (n_support / float(n_samples))))
    if n_samples > 1500:
      n_best_merged = 10
    else:
      n_best_merged = 1
    # find the best couples (location, covariance) on the merged set
    selection = random_state.permutation(n_samples)[:n_samples_merged]
    locations_merged, covariances_merged, supports_merged, d = \
      _select_candidates(X[selection], h_merged,
                         n_trials=(all_best_locations, all_best_covariances),
                         select=n_best_merged,
                         cov_computation_method=cov_computation_method,
                         random_state=random_state, logger=logger)
    ## 3. Finally get the overall best (locations, covariance) couple
    if n_samples < 1500:
      # directly get the best couple (location, covariance)
      location = locations_merged[0]
      covariance = covariances_merged[0]
      support = np.zeros(n_samples).astype(bool)
      dist = np.zeros(n_samples)
      support[selection] = supports_merged[0]
      dist[selection] = d[0]
    else:
      # select the best couple on the full dataset
      locations_full, covariances_full, supports_full, d = \
          _select_candidates(X, n_support,
                             n_trials=(locations_merged, covariances_merged),
                             select=1,
                             cov_computation_method=cov_computation_method,
                             random_state=random_state, logger=logger)
      location = locations_full[0]
      covariance = covariances_full[0]
      support = supports_full[0]
      dist = d[0]
  elif n_features > 1:
    ## 1. Find the 10 best couples (location, covariance)
    ## considering two iterations
    n_trials = 30
    n_best = 10
    locations_best, covariances_best, _, _ = \
      _select_candidates(X, n_support, n_trials=n_trials, select=n_best, n_iter=2,
                         cov_computation_method=cov_computation_method,
                         random_state=random_state, logger=logger)
    ## 2. Select the best couple on the full dataset amongst the 10
    locations_full, covariances_full, supports_full, d = \
      _select_candidates(X, n_support, n_trials=(locations_best, covariances_best),
                         select=1, cov_computation_method=cov_computation_method,
                         random_state=random_state, logger=logger)
    location = locations_full[0]
    covariance = covariances_full[0]
    support = supports_full[0]
    dist = d[0]

  return location, covariance, support, dist


class _MinCovDet():
  """Minimum Covariance Determinant (MCD): robust estimator of covariance.

  The Minimum Covariance Determinant covariance estimator is to be applied
  on Gaussian-distributed data, but could still be relevant on data
  drawn from a unimodal, symmetric distribution. It is not meant to be used
  with multimodal data (the algorithm used to fit a _MinCovDet object is
  likely to fail in such a case).
  One should consider projection pursuit methods to deal with multimodal
  datasets.

  Parameters
  ----------
  store_precision: bool
    Specify if the estimated precision is stored
  assume_centered: Boolean
    If True, the support of robust location and covariance estimates
    is computed, and a covariance estimate is recomputed from it,
    without centering the data.
    Useful to work with data whose mean is significantly equal to
    zero but is not exactly zero.
    If False, the robust location and covariance are directly computed
    with the FastMCD algorithm without additional treatment.
  support_fraction: float, 0 < support_fraction < 1
    The proportion of points to be included in the support of the raw
    MCD estimate. Default is None, which implies that the minimum
    value of support_fraction will be used within the algorithm:
    [n_sample + n_features + 1] / 2
  random_state: integer or numpy.RandomState, optional
    The random generator used. If an integer is given, it fixes the
    seed. Defaults to the global numpy random number generator.

  Attributes
  ----------
  `raw_location_`: array-like, shape (n_features,)
    The raw robust estimated location before correction and reweighting

  `raw_covariance_`: array-like, shape (n_features, n_features)
    The raw robust estimated covariance before correction and reweighting

  `raw_support_`: array-like, shape (n_samples,)
    A mask of the observations that have been used to compute
    the raw robust estimates of location and shape, before correction
    and reweighting.

  `location_`: array-like, shape (n_features,)
    Estimated robust location

  `covariance_`: array-like, shape (n_features, n_features)
   Estimated robust covariance matrix

  `precision_`: array-like, shape (n_features, n_features)
    Estimated pseudo inverse matrix.
    (stored only if store_precision is True)

  `support_`: array-like, shape (n_samples,)
    A mask of the observations that have been used to compute
    the robust estimates of location and shape.

  `dist_`: array-like, shape (n_samples,)
    Mahalanobis distances of the training set (on which `fit` is called)
    observations.

  References
  ----------

  .. [Rouseeuw1984] `P. J. Rousseeuw. Least median of squares regression.
     J. Am Stat Ass, 79:871, 1984.`
  .. [Rouseeuw1999] `A Fast Algorithm for the Minimum Covariance Determinant
     Estimator, 1999, American Statistical Association and the American
     Society for Quality, TECHNOMETRICS`
  .. [Butler1993] `R. W. Butler, P. L. Davies and M. Jhun,
     Asymptotics For The Minimum Covariance Determinant Estimator,
     The Annals of Statistics, 1993, Vol. 21, No. 3, 1385-1400`

  """
  _nonrobust_covariance = staticmethod(_empirical_covariance)

  def __init__(self, store_precision=True, assume_centered=False,
               support_fraction=None, random_state=None, logger=None):
    self.store_precision = store_precision
    self.assume_centered = assume_centered
    self.support_fraction = support_fraction
    self.random_state = random_state
    self.logger = logger

  def _set_covariance(self, covariance):
    """Saves the covariance and precision estimates

    Storage is done accordingly to `self.store_precision`.
    Precision stored only if invertible.

    Params
    ------
    covariance: 2D ndarray, shape (n_features, n_features)
      Estimated covariance matrix to be stored, and from which precision
      is computed.

    """
    covariance = np.array(covariance)#array2d(covariance)
    # set covariance
    self.covariance_ = covariance
    # set precision
    if self.store_precision:
      self.precision_ = _pinvh(covariance)
    else:
      self.precision_ = None

  def get_precision(self):
    """Getter for the precision matrix.

    Returns
    -------
    precision_: array-like,
      The precision matrix associated to the current covariance object.

    """
    if self.store_precision:
      precision = self.precision_
    else:
      precision = _pinvh(self.covariance_)
    return precision

  def fit(self, X, y=None):
    """Fits a Minimum Covariance Determinant with the FastMCD algorithm.

    Parameters
    ----------
    X: array-like, shape = [n_samples, n_features]
      Training data, where n_samples is the number of samples
      and n_features is the number of features.
    y: not used, present for API consistence purpose.
    noise_level: add to data normally distributed random noise with level std(X)*noise_level

    Returns
    -------
    self: object
      Returns self.

    """
    X = np.array(X, dtype=float, copy=_shared._SHALLOW)
    n_samples, n_features = X.shape
    # check that the empirical covariance is full rank
    if (np.linalg.eigvalsh(np.dot(X.T, X)) > 1.e-8).sum() != n_features:
      if self.logger:
        self.logger.warn("The covariance matrix associated to your dataset is not full rank")
      else:
        warnings.warn("The covariance matrix associated to your dataset is not full rank")

    X_clean = X

    # It's always worth to add some noise...
    X_noisy = np.random.normal(size=X.shape)
    np.multiply(X_noisy, np.std(X, ddof=1, axis=0).reshape(1, -1), out=X_noisy)
    np.multiply(X_noisy, 1.e-8, out=X_noisy)
    np.add(X, X_noisy, out=X_noisy)
    X = X_noisy

    # compute and store raw estimates
    raw_location, raw_covariance, raw_support, raw_dist = \
      _fast_mcd(X, support_fraction=self.support_fraction,
                cov_computation_method=self._nonrobust_covariance,
                random_state=self.random_state, logger=self.logger)

    if self.assume_centered:
      # recalculate covariances and distances
      raw_location = np.zeros(n_features)
      raw_covariance = self._nonrobust_covariance(X[raw_support],
                                                  assume_centered=True,
                                                  logger=self.logger)
      raw_dist = _mahal_accum_dist(X, raw_covariance)

    self.raw_location_ = raw_location
    self.raw_covariance_ = raw_covariance
    self.raw_support_ = raw_support
    self.location_ = raw_location
    self.support_ = raw_support
    self.dist_ = raw_dist
    # obtain consistency at normal models
    self._correct_covariance(X)
    # reweight estimator
    self._reweight_covariance(X)

    if X_clean is not X:
      # reweight estimator using clean data
      self._reweight_denoised(X_clean)

    return self

  def _correct_covariance(self, data):
    """Apply a correction to raw Minimum Covariance Determinant estimates.

    Correction using the empirical correction factor suggested
    by Rousseeuw and Van Driessen in [Rouseeuw1984]_.

    Parameters
    ----------
    data: array-like, shape (n_samples, n_features)
      The data matrix, with p features and n samples.
      The data set must be the one which was used to compute
      the raw estimates.

    Returns
    -------
    covariance_corrected: array-like, shape (n_features, n_features)
      Corrected robust covariance estimate.

    """
    chi2_distribution = _chi2(_shared.get_size(data[0]))
    correction = np.median(self.dist_) / chi2_distribution.quantile(0.5, complement=True)
    if np.fabs(correction) <= np.finfo(float).tiny:
      return self.raw_covariance_
    covariance_corrected = self.raw_covariance_ * correction
    np.divide(self.dist_, correction, out=self.dist_)
    return covariance_corrected

  def _reweight_covariance(self, data):
    """Reweight raw Minimum Covariance Determinant estimates.

    Reweight observations using Rousseeuw's method (equivalent to
    deleting outlying observations from the data set before
    computing location and covariance estimates). [Rouseeuw1984]_

    Parameters
    ----------
    data: array-like, shape (n_samples, n_features)
      The data matrix, with p features and n samples.
      The data set must be the one which was used to compute
      the raw estimates.

    Returns
    -------
    location_reweighted: array-like, shape (n_features, )
      Reweighted robust location estimate.
    covariance_reweighted: array-like, shape (n_features, n_features)
      Reweighted robust covariance estimate.
    support_reweighted: array-like, type boolean, shape (n_samples,)
      A mask of the observations that have been used to compute
      the reweighted robust location and covariance estimates.

    """
    n_samples, n_features = data.shape
    chi2_distribution = _chi2(n_features)
    mask = (self.dist_ < chi2_distribution.quantile(0.025, complement=True))
    if self.assume_centered:
      location_reweighted = np.zeros(n_features)
    else:
      location_reweighted = data[mask].mean(axis=0)
    covariance_reweighted = self._nonrobust_covariance(data[mask], assume_centered=self.assume_centered, logger=self.logger)
    support_reweighted = np.zeros(n_samples, dtype=bool)
    support_reweighted[mask] = True
    self._set_covariance(covariance_reweighted)
    self.location_ = location_reweighted
    self.support_ = support_reweighted
    self.dist_ = _mahal_accum_dist(data - self.location_, covariance_reweighted)

    return location_reweighted, covariance_reweighted, support_reweighted

  def _reweight_denoised(self, data):
    n_samples, n_features = data.shape
    support_data = data[self.support_]
    location_denoised = np.zeros(n_features) if self.assume_centered else support_data.mean(axis=0)
    covariance_denoised = self._nonrobust_covariance(support_data, assume_centered=self.assume_centered, logger=self.logger)
    dist_denoised = _mahal_accum_dist(data - location_denoised, covariance_denoised)
    support_denoised = (dist_denoised < _chi2(n_features).quantile(0.025, complement=True))

    if (support_denoised != self.support_).any():
      support_data = data[support_denoised]
      if not self.assume_centered:
        location_denoised = support_data.mean(axis=0)
      covariance_denoised = self._nonrobust_covariance(support_data, assume_centered=self.assume_centered, logger=self.logger)
      dist_denoised = _mahal_accum_dist(data - location_denoised, covariance_denoised)

    self._set_covariance(covariance_denoised)
    self.location_ = location_denoised
    self.support_ = support_denoised
    self.dist_ = dist_denoised

    return location_denoised, covariance_denoised, support_denoised

def _calculate_outlier_probabilities(sample, is_robust=True, seed=32771):
  """Calculates robust outlier probabilities
  """
  sample = np.array(sample, dtype=float, copy=_shared._SHALLOW)

  number_points = len(sample)

  if number_points == 0:
    raise _ex.GTException('Sample is empty!')

  number_dimensions = _shared.get_size(sample[0])

  if number_dimensions <= 0:
    raise _ex.GTException('Points dimensionality should be greater than zero!')

  if is_robust:
    rand_gen = np.random.RandomState(seed)

    if _shared.is_iterable(sample[0]) and _shared.get_size(sample[0]) > 1:
      mcd_fit = _MinCovDet(random_state=rand_gen).fit(sample)
      covariances = mcd_fit.covariance_
    else:
      mads = _calculate_median_absolute_deviation(sample)
      covariances = 1.4826 * mads + np.finfo(float).eps
  else:
    covariances = np.cov(sample.T)
  outlier_probabilities = _get_outlier_probabilities(sample, covariances)

  return outlier_probabilities


def _calculate_deviation_scores(sample, is_robust=True):
  """Calculates robust deviation scores
  """
  sample = np.array(sample, dtype=float, copy=_shared._SHALLOW)

  number_points = len(sample)

  if number_points == 0:
    raise _ex.GTException('Sample is empty!')

  number_dimensions = _shared.get_size(sample[0])

  if number_dimensions <= 0:
    raise _ex.GTException('Points dimensionality should be greater than zero!')

  if is_robust:
    rand_gen = np.random.RandomState(0)

    if _shared.is_iterable(sample[0]):
      if len(sample[0]) > 1:
        mcd_fit = _MinCovDet(random_state=rand_gen).fit(sample)
        covariances = mcd_fit.covariance_

      else:
        mads = _calculate_median_absolute_deviation(sample)
        covariances = 1.4826 * mads

    else:
      mads = _calculate_median_absolute_deviation(sample)
      covariances = 1.4826 * mads
  else:
    covariances = np.cov(sample.T)

  deviation_scores = _get_deviation_scores(sample, covariances)

  return deviation_scores
