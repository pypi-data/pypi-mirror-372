#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

#
# This module uses code from scikit-learn, the Python machine learning package.
# http://scikit-learn.org

"""K-means clustering"""
from __future__ import division

import warnings

import numpy as np

from ..six import callable
from ..six.moves import xrange, range
from .cluster_utils import _euclidean_distances, _check_random_state, _as_float_array, _atleast2d


###############################################################################
# Initialization heuristic


def _k_init(X, k, n_local_trials=None, random_state=None, x_squared_norms=None):
  """Init k seeds according to k-means++

  Parameters
  -----------
  X: array or sparse matrix, shape (n_samples, n_features)
    The data to pick seeds for. To avoid memory copy, the input data
    should be double precision (dtype=np.float64).

  k: integer
    The number of seeds to choose

  n_local_trials: integer, optional
    The number of seeding trials for each center (except the first),
    of which the one reducing inertia the most is greedily chosen.
    Set to None to make the number of trials depend logarithmically
    on the number of seeds (2+log(k)); this is the default.

  random_state: integer or numpy.RandomState, optional
    The generator used to initialize the centers. If an integer is
    given, it fixes the seed. Defaults to the global numpy random
    number generator.

  x_squared_norms: array, shape (n_samples,), optional
    Squared euclidean norm of each data point. Pass it if you have it at
    hands already to avoid it being recomputed here. Default: None

  Notes
  -----
  Selects initial cluster centers for k-mean clustering in a smart way
  to speed up convergence. see: Arthur, D. and Vassilvitskii, S.
  "k-means++: the advantages of careful seeding". ACM-SIAM symposium
  on Discrete algorithms. 2007

  Version ported from http://www.stanford.edu/~darthur/kMeansppTest.zip,
  which is the implementation used in the aforementioned paper.
  """
  n_samples, n_features = X.shape
  random_state = _check_random_state(random_state)

  centers = np.empty((k, n_features))

  # Set the number of local seeding trials if none is given
  if n_local_trials is None:
    # This is what Arthur/Vassilvitskii tried, but did not report
    # specific results for other than mentioning in the conclusion
    # that it helped.
    n_local_trials = 2 + int(np.log(k))

  # Pick first center randomly
  center_id = random_state.randint(n_samples)
  centers[0] = X[center_id]

  # Initialize list of closest distances and calculate current potential
  if x_squared_norms is None:
    x_squared_norms = _squared_norms(X)
  closest_dist_sq = _euclidean_distances(
    centers[0], X, Y_norm_squared=x_squared_norms, squared=True)
  current_pot = closest_dist_sq.sum()

  # Pick the remaining k-1 points
  for c in xrange(1, k):
    # Choose center candidates by sampling with probability proportional
    # to the squared distance to the closest existing center
    rand_vals = random_state.random_sample(n_local_trials) * current_pot
    candidate_ids = np.searchsorted(closest_dist_sq.cumsum(), rand_vals)

    # Compute distances to center candidates
    distance_to_candidates = _euclidean_distances(
      X[candidate_ids], X, Y_norm_squared=x_squared_norms, squared=True)

    # Decide which candidate is the best
    best_candidate = None
    best_pot = None
    best_dist_sq = None
    for trial in xrange(n_local_trials):
      # Compute potential when including center candidate
      new_dist_sq = np.minimum(closest_dist_sq,
                               distance_to_candidates[trial])
      new_pot = new_dist_sq.sum()

      # Store result if it is the best local trial so far
      if (best_candidate is None) or (new_pot < best_pot):
        best_candidate = candidate_ids[trial]
        best_pot = new_pot
        best_dist_sq = new_dist_sq

    # Permanently add best center candidate found in local tries
    centers[c] = X[best_candidate]
    current_pot = best_pot
    closest_dist_sq = best_dist_sq

  return centers


###############################################################################
# K-means batch estimation by EM (expectation maximization)


def _tolerance(X, tol):
  """Return a tolerance which is independent of the dataset"""
  variances = np.var(X, axis=0)
  return np.mean(variances) * tol


def _k_means(X, k, init='k-means++', n_init=10, max_iter=300, verbose=False,
             tol=1e-4, random_state=None, copy_x=True):
  """K-means clustering algorithm.

  Parameters
  ----------
  X: array-like of floats, shape (n_samples, n_features)
    The observations to cluster.

  k: int
    The number of clusters to form as well as the number of
    centroids to generate.

  max_iter: int, optional, default 300
    Maximum number of iterations of the k-means algorithm to run.

  n_init: int, optional, default: 10
    Number of time the k-means algorithm will be run with different
    centroid seeds. The final results will be the best output of
    n_init consecutive runs in terms of inertia.

  init: {'k-means++', 'random', or ndarray, or a callable}, optional
    Method for initialization, default to 'k-means++':

    'k-means++' : selects initial cluster centers for k-mean
    clustering in a smart way to speed up convergence. See section
    Notes in _k_init for more details.

    'random': generate k centroids from a Gaussian with mean and
    variance estimated from the data.

    If an ndarray is passed, it should be of shape (k, p) and gives
    the initial centers.

    If a callable is passed, it should take arguments X, k and
    and a random state and return an initialization.

  tol: float, optional
    The relative increment in the results before declaring convergence.

  verbose: boolean, optional
    Verbosity mode

  random_state: integer or numpy.RandomState, optional
    The generator used to initialize the centers. If an integer is
    given, it fixes the seed. Defaults to the global numpy random
    number generator.

  copy_x: boolean, optional
    When pre-computing distances it is more numerically accurate to center
    the data first.  If copy_x is True, then the original data is not
    modified.  If False, the original data is modified, and put back before
    the function returns, but small numerical differences may be introduced
    by subtracting and then adding the data mean.

  Returns
  -------
  centroid: float ndarray with shape (k, n_features)
    Centroids found at the last iteration of k-means.

  label: integer ndarray with shape (n_samples,)
    label[i] is the code or index of the centroid the
    i'th observation is closest to.

  inertia: float
    The final value of the inertia criterion (sum of squared distances to
    the closest centroid for all observations in the training set).

  """
  random_state = _check_random_state(random_state)

  best_inertia = np.inf
  X = _as_float_array(X, copy=copy_x)
  tol = _tolerance(X, tol)

  # subtract of mean of x for more accurate distance computations
  X_mean = X.mean(axis=0)
  if copy_x:
    X = X.copy()
  X -= X_mean

  if hasattr(init, '__array__'):
    init = np.asarray(init).copy()
    init -= X_mean
    if not n_init == 1:
      warnings.warn(
        'Explicit initial center position passed: '
        'performing only one init in the k-means instead of %d'
        % n_init, RuntimeWarning, stacklevel=2)
      n_init = 1

  # precompute squared norms of data points
  x_squared_norms = _squared_norms(X)

  best_labels, best_inertia, best_centers = None, None, None

  # For a single thread, less memory is needed if we just store one set
  # of the best results (as opposed to one set per run per thread).
  for it in xrange(n_init):
    # run a k-means once
    labels, inertia, centers = _kmeans_single(
      X, k, max_iter=max_iter, init=init, verbose=verbose,
      tol=tol, x_squared_norms=x_squared_norms, random_state=random_state)
    # determine if these results are the best so far
    if best_inertia is None or inertia < best_inertia:
      best_labels = labels.copy()
      best_centers = centers.copy()
      best_inertia = inertia

  if not copy_x:
    X += X_mean
  best_centers += X_mean

  return best_centers, best_labels, best_inertia


def _kmeans_single(X, k, max_iter=300, init='k-means++', verbose=False,
                   x_squared_norms=None, random_state=None, tol=1e-4):
  """A single run of k-means, assumes preparation completed prior.

  Parameters
  ----------
  X: array-like of floats, shape (n_samples, n_features)
    The observations to cluster.

  k: int
    The number of clusters to form as well as the number of
    centroids to generate.

  max_iter: int, optional, default 300
    Maximum number of iterations of the k-means algorithm to run.

  init: {'k-means++', 'random', or ndarray, or a callable}, optional
    Method for initialization, default to 'k-means++':

    'k-means++' : selects initial cluster centers for k-mean
    clustering in a smart way to speed up convergence. See section
    Notes in _k_init for more details.

    'random': generate k centroids from a Gaussian with mean and
    variance estimated from the data.

    If an ndarray is passed, it should be of shape (k, p) and gives
    the initial centers.

    If a callable is passed, it should take arguments X, k and
    and a random state and return an initialization.

  tol: float, optional
    The relative increment in the results before declaring convergence.

  verbose: boolean, optional
    Verbosity mode

  x_squared_norms: array, optional
    Precomputed x_squared_norms. Calculated if not given.

  random_state: integer or numpy.RandomState, optional
    The generator used to initialize the centers. If an integer is
    given, it fixes the seed. Defaults to the global numpy random
    number generator.

  Returns
  -------
  centroid: float ndarray with shape (k, n_features)
    Centroids found at the last iteration of k-means.

  label: integer ndarray with shape (n_samples,)
    label[i] is the code or index of the centroid the
    i'th observation is closest to.

  inertia: float
    The final value of the inertia criterion (sum of squared distances to
    the closest centroid for all observations in the training set).
  """
  random_state = _check_random_state(random_state)
  if x_squared_norms is None:
    x_squared_norms = _squared_norms(X)
  best_labels, best_inertia, best_centers = None, None, None
  # init
  centers = _init_centroids(X, k, init, random_state=random_state,
                            x_squared_norms=x_squared_norms)
  #if verbose:
  #  print 'Initialization complete'

  # Allocate memory to store the distances for each sample to its
  # closer center for reallocation in case of ties
  distances = np.zeros(shape=(X.shape[0],), dtype=np.float64)

  # iterations
  for i in xrange(max_iter):
    centers_old = centers.copy()
    # labels assignement is also called the E-step of EM
    labels, inertia = _labels_inertia(X, x_squared_norms, centers)

    # computation of the means is also called the M-step of EM
    centers = _centers(X, labels, k, distances)

    #if verbose:
    #  print 'Iteration %i, inertia %s' % (i, inertia)

    if best_inertia is None or inertia < best_inertia:
      best_labels = labels.copy()
      best_centers = centers.copy()
      best_inertia = inertia

    if np.sum((centers_old - centers) ** 2) < tol:
      #if verbose:
      #  print 'Converged to similar centers at iteration', i
      break
  return best_labels, best_inertia, best_centers


def _squared_norms(X):
  """Compute the squared euclidean norms of the rows of X"""
  # TODO: implement a cython version to avoid the memory copy of the
  # input data
  return (X ** 2).sum(axis=1)


def _labels_inertia(X, x_squared_norms, centers):
  n_samples = X.shape[0]
  k = centers.shape[0]
  distances = _euclidean_distances(centers, X, x_squared_norms,
                                   squared=True)
  labels = np.empty(n_samples, dtype=int)
  labels.fill(-1)
  mindist = np.empty(n_samples)
  mindist.fill(np.inf)
  for center_id in range(k):
    dist = distances[center_id]
    labels[dist < mindist] = center_id
    mindist = np.minimum(dist, mindist)
  inertia = mindist.sum()
  return labels, inertia


def _centers(X, labels, n_clusters, distances):
  """M step of the K-means EM algorithm

  Computation of cluster centers / means.

  Parameters
  ----------
  X: array, shape (n_samples, n_features)

  labels: array of integers, shape (n_samples)
    Current label assignment

  n_clusters: int
    Number of desired clusters

  Returns
  -------
  centers: array, shape (n_clusters, n_features)
    The resulting centers
  """
  # TODO: add support for CSR input
  n_features = X.shape[1]

  # TODO: explicit dtype handling
  centers = np.empty((n_clusters, n_features))
  far_from_centers = None
  reallocated_idx = 0

  for center_id in xrange(n_clusters):
    center_mask = labels == center_id
    if not np.any(center_mask):
      # Reassign empty cluster center to sample far from any cluster
      if far_from_centers is None:
        far_from_centers = distances.argsort()[::-1]
      centers[center_id] = X[far_from_centers[reallocated_idx]]
      reallocated_idx += 1
    else:
      centers[center_id] = X[center_mask].mean(axis=0)
  return centers


def _init_centroids(X, k, init, random_state=None, x_squared_norms=None,
                    init_size=None):
  """Compute the initial centroids

  Parameters
  ----------

  X: array, shape (n_samples, n_features)

  k: int
    number of centroids

  init: {'k-means++', 'random' or ndarray or callable} optional
    Method for initialization

  random_state: integer or numpy.RandomState, optional
    The generator used to initialize the centers. If an integer is
    given, it fixes the seed. Defaults to the global numpy random
    number generator.

  x_squared_norms:  array, shape (n_samples,), optional
    Squared euclidean norm of each data point. Pass it if you have it at
    hands already to avoid it being recomputed here. Default: None

  init_size : int, optional
    Number of samples to randomly sample for speeding up the
    initialization (sometimes at the expense of accurracy): the
    only algorithm is initialized by running a batch KMeans on a
    random subset of the data. This needs to be larger than k.

  Returns
  -------
  centers: array, shape(k, n_features)
  """
  random_state = _check_random_state(random_state)
  n_samples = X.shape[0]

  if init_size is not None and init_size < n_samples:
    if init_size < k:
      warnings.warn(
        "init_size=%d should be larger than k=%d. "
        "Setting it to 3*k" % (init_size, k),
        RuntimeWarning, stacklevel=2)
      init_size = 3 * k
    init_indices = random_state.randint(n_samples, size=init_size)
    X = X[init_indices]
    x_squared_norms = x_squared_norms[init_indices]
    n_samples = X.shape[0]
  elif n_samples < k:
      raise ValueError(
        "n_samples=%d should be larger than k=%d" % (init_size, k))

  if init == 'k-means++':
    centers = _k_init(X, k,
            random_state=random_state,
            x_squared_norms=x_squared_norms)
  elif init == 'random':
    seeds = random_state.permutation(n_samples)[:k]
    centers = X[seeds]
  elif hasattr(init, '__array__'):
    centers = init
  elif callable(init):
    centers = init(X, k, random_state=random_state)
  else:
    raise ValueError("the init parameter for the k-means should "
                     "be 'k-means++' or 'random' or an ndarray, "
                     "'%s' (type '%s') was passed." % (init, type(init)))

  return centers


class _KMeans:
  """K-Means clustering

  Parameters
  ----------

  k : int, optional, default: 8
    The number of clusters to form as well as the number of
    centroids to generate.

  max_iter : int
    Maximum number of iterations of the k-means algorithm for a
    single run.

  n_init: int, optional, default: 10
    Number of time the k-means algorithm will be run with different
    centroid seeds. The final results will be the best output of
    n_init consecutive runs in terms of inertia.

  init : {'k-means++', 'random' or an ndarray}
    Method for initialization, defaults to 'k-means++':

    'k-means++' : selects initial cluster centers for k-mean
    clustering in a smart way to speed up convergence. See section
    Notes in _k_init for more details.

    'random': choose k observations (rows) at random from data for
    the initial centroids.

    if init is an 2d array, it is used as a seed for the centroids

  tol: float, optional default: 1e-4
    Relative tolerance w.r.t. inertia to declare convergence

  random_state: integer or numpy.RandomState, optional
    The generator used to initialize the centers. If an integer is
    given, it fixes the seed. Defaults to the global numpy random
    number generator.

  Attributes
  ----------
  `cluster_centers_`: array, [n_clusters, n_features]
    Coordinates of cluster centers

  `labels_`:
    Labels of each point

  `inertia_`: float
    The value of the inertia criterion associated with the chosen
    partition.

  Notes
  ------
  The k-means problem is solved using Lloyd's algorithm.

  The average complexity is given by O(k n T), were n is the number of
  samples and T is the number of iteration.

  The worst case complexity is given by O(n^(k+2/p)) with
  n = n_samples, p = n_features. (D. Arthur and S. Vassilvitskii,
  'How slow is the k-means method?' SoCG2006)

  In practice, the k-means algorithm is very fast (one of the fastest
  clustering algorithms available), but it falls in local minima. That's why
  it can be useful to restart it several times.

  """

  def __init__(self, k=8, init='k-means++', n_init=10, max_iter=300,
               tol=1e-4, verbose=0, random_state=None, copy_x=True):

    if hasattr(init, '__array__'):
      k = init.shape[0]
      init = np.asanyarray(init, dtype=np.float64)

    self.k = k
    self.init = init
    self.max_iter = max_iter
    self.tol = tol
    self.n_init = n_init
    self.verbose = verbose
    self.random_state = random_state
    self.copy_x = copy_x

  def _check_fit_data(self, X):
    """Verify that the number of samples given is larger than k"""
    X = _atleast2d(X, dtype=np.float64)
    if X.shape[0] < self.k:
      raise ValueError("n_samples=%d should be >= k=%d" % (
        X.shape[0], self.k))
    return X

  def _check_test_data(self, X):
    X = _atleast2d(X)
    n_samples, n_features = X.shape
    expected_n_features = self.cluster_centers_.shape[1]
    if not n_features == expected_n_features:
      raise ValueError("Incorrect number of features. "
               "Got %d features, expected %d" % (
                 n_features, expected_n_features))
    if X.dtype.kind != 'f':
      warnings.warn("Got data type %s, converted to float "
              "to avoid overflows" % X.dtype,
              RuntimeWarning, stacklevel=2)
      X = X.astype(np.float64)

    return X

  def _check_fitted(self):
    if not hasattr(self, "cluster_centers_"):
      raise AttributeError("Model has not been trained yet.")

  def fit(self, X, y=None):
    """Compute k-means"""
    self.random_state = _check_random_state(self.random_state)
    X = self._check_fit_data(X)

    self.cluster_centers_, self.labels_, self.inertia_ = _k_means(
      X, k=self.k, init=self.init, n_init=self.n_init,
      max_iter=self.max_iter, verbose=self.verbose,
      tol=self.tol, random_state=self.random_state, copy_x=self.copy_x)
    return self
