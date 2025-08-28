#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#


"""Clustering based on Gaussian Mixture Models"""
from __future__ import division

import ctypes as _ctypes
from math import pi
import numpy as np

from ..six.moves import xrange
from ..six import b as _bytes

from .. import shared as _shared
from .. import exceptions as _ex
from ..utils import gmm, distributions
from ..utils import linalg as _linalg
from .utilities import _parse_dry_run

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_size_ptr = _ctypes.POINTER(_ctypes.c_size_t)
    self.c_ushort_ptr = _ctypes.POINTER(_ctypes.c_ushort)
    self.c_double_ptr = _ctypes.POINTER(_ctypes.c_double)
    self.c_byte_ptr = _ctypes.POINTER(_ctypes.c_byte)

    self.clusterize = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, _ctypes.c_size_t,
                                        self.c_double_ptr, self.c_size_ptr,
                                        self.c_ushort_ptr, self.c_double_ptr, self.c_size_ptr,
                                        self.c_ushort_ptr, _ctypes.c_size_t,
                                        _ctypes.c_char_p, _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxUtilitiesClusterize', self.__library))

    self.silhouettes = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_size_t, _ctypes.c_size_t, _ctypes.c_size_t,
                                        self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, self.c_size_ptr,
                                        self.c_double_ptr, self.c_size_ptr, self.c_double_ptr, _ctypes.c_size_t,
                                        _ctypes.c_double, _ctypes.POINTER(_ctypes.c_void_p))(('GTApproxUtilitiesEvaluateSilhouettes', self.__library))

    self.maxparallel_begin = _ctypes.CFUNCTYPE(_ctypes.c_void_p, _ctypes.c_int, _ctypes.c_int, _ctypes.c_char_p)(('GTApproxSetupParallelization', self.__library))

    self.maxparallel_finish = _ctypes.CFUNCTYPE(_ctypes.c_short, _ctypes.c_void_p)(('GTApproxCleanupParallelization', self.__library))


_api = _API()

def build(points, values, possible_number_of_clusters,
          min_sample_size, min_cluster_size,
          options, logger=None, watcher=None):
  """
  Build GMM model.
  possible_number_of_clusters - is a range of possible numbers of clusters.
  the best one will be chosen using BIC.

  :param points: train points
  :param values: train values
  :param options: MoA options
  :type points: :term:`array-like`
  :type values: :term:`array-like`
  :type options: ``dict``
  :return: model: clustering model
  :rtype: :class: ``dict``

  """
  points = _shared.as_matrix(points, name="'points' argument")
  values = _shared.as_matrix(values, name="'values' argument")

  if points.shape[0] != values.shape[0] or not points.size or not values.size:
    raise ValueError('Train points and values samples must be non-empty and have the same number of vectors: points shape is %s while values shape is %s' % (points.shape, values.shape))

  sample_size = len(points)
  size_x = points.shape[1]
  size_y = values.shape[1]

  if _shared.isNanInf(points):
    raise _ex.NanInfError("Train 'points' data contains NaN or Inf value")

  if _shared.isNanInf(values):
    raise _ex.NanInfError("Train 'values' data contains NaN or Inf value")


  quality_metric = None # auto selection according to options and sample size
  covariance_types_set = None # auto selection according to options
  seed = 15313 # default seed
  accelerator = 2 # default accelerator level
  dry_run = False

  if options:
    dry_run = _parse_dry_run(options)
    accelerator = int(options.get('GTApprox/Accelerator'))
    seed = int(options.get("GTApprox/Seed"))

    moa_covariance_type = str(options._get('GTApprox/MoACovarianceType')).lower()
    if moa_covariance_type in ('spherical', 'diag', 'tied', 'full'):
      covariance_types_set = [moa_covariance_type]
    elif moa_covariance_type in ('sil', 'bic'):
      quality_metric = moa_covariance_type

  size_xy = size_x + size_y
  thresh = [1e-3, 1e-3, 5e-3, 1e-2, 5e-2][accelerator - 1]
  n_iter = [min(100 * size_xy, 1000), min(75 * size_xy, 750),
            min(75 * size_xy, 750), min(50 * size_xy, 500),
            min(30 * size_xy, 300)][accelerator - 1]

  if covariance_types_set is None:
    # select kinds of covariance to check according to the accelerator level
    covariance_types_set = [['full', 'tied', 'diag', 'spherical'],
                            ['full', 'diag'],
                            ['full',],
                            ['diag'],
                            ['diag']][accelerator - 1]

  if dry_run:
    possible_number_of_clusters = np.array([1])
    covariance_types_set = ['diag']
    n_iter = 0
  else:
    possible_number_of_clusters = np.unique([int(_) for _ in possible_number_of_clusters])

  if quality_metric is None:
    quality_metric = 'sil' if (len(covariance_types_set) * len([_ for _ in possible_number_of_clusters if _ > 1])) > 1 else 'bic'
  elif quality_metric not in ('sil', 'bic'):
    raise ValueError('Unknown quality metric type: ' + str(quality_metric))

  # concatenate points and values
  data = np.hstack((points, values))

  if not logger:
    logger = _shared.Logger() # null logger

  logger.info('Decomposing design space...')

  try:
    maxparallel_control = _api.maxparallel_begin(int(options.get('GTApprox/MaxParallel')),
                                                 int(options.get('/GTApprox/MaxNestedParallel')),
                                                 options.get('/GTApprox/ParallelizationPenalty').encode("utf8"))
  except:
    maxparallel_control = None

  random_state = np.random.get_state()
  try:
    np.random.seed(seed)

    # Strict ordering for testing purposes
    covariance_types_set.sort()
    # Build optimal clustering model
    if quality_metric == 'bic':
      best_covariance_type, best_gmm = _build_optimal_bic(data,
                                                          possible_number_of_clusters, covariance_types_set,
                                                          n_iter, thresh, logger, watcher)
    else: #if quality_metric == 'sil':
      best_covariance_type, best_gmm = _build_optimal_sil(data,
                                                          possible_number_of_clusters, covariance_types_set,
                                                          min_sample_size, min_cluster_size,
                                                          options, sample_size,
                                                          n_iter, thresh, logger, watcher)
  finally:
    np.random.set_state(random_state)
    if maxparallel_control is not None:
      _api.maxparallel_finish(maxparallel_control)

  clustering_model = {'min_sample_size': min_sample_size,
                      'min_cluster_size': min_cluster_size,
                      'means': best_gmm.means_,
                      'weights': best_gmm.weights_,
                      'number_of_clusters': best_gmm.weights_.shape[0],
                      'covariance_type': best_covariance_type,
                      'covars_cholesky_factor': _covariances(best_gmm, best_covariance_type),
                      }

  _check_abort(watcher)
  return clustering_model

def _parse_json_clusters_model(json_model, raise_on_error):
  try:
    clustering_model = _shared.parse_json(json_model)
    if not clustering_model:
      return None

    absent_fields = [_ for _ in ('min_sample_size',
                                 'min_cluster_size',
                                 'means',
                                 'weights',
                                 'number_of_clusters',
                                 'covariance_type',
                                 'covars_cholesky_factor',) if _ not in clustering_model]

    if absent_fields:
      raise ValueError("Some required fields are absent in clusters model: " + ", ".join(absent_fields))

    number_of_clusters = clustering_model['number_of_clusters']

    clustering_model['means'] = _shared.as_matrix(clustering_model['means'], shape=(number_of_clusters, None))
    clustering_model['weights'] = _shared.as_matrix(clustering_model['weights'], shape=(1, number_of_clusters))[0]

    number_of_features = clustering_model['means'].shape[1]

    clustering_model['covars_cholesky_factor'] = np.array(clustering_model['covars_cholesky_factor'], dtype=float, ndmin=3)
    if clustering_model['covars_cholesky_factor'].shape != (number_of_clusters, number_of_features, number_of_features):
      raise ValueError("Invalid covariance matrices encountered")

    return clustering_model
  except:
    if raise_on_error:
      raise
  return None

def _check_abort(watcher):
  if watcher and not watcher(None):
    raise _ex.UserTerminated()

class _GMMInitCache(object):
  def __init__(self):
    self.cache = {}

  def has(self, clusters_mean, assigned_points):
    eps = np.finfo(float).eps * (np.fabs(clusters_mean) + 1.)
    return any(((np.fabs(c - clusters_mean) < eps).all() and (p == assigned_points).all()) for c, p in self.cache.get(clusters_mean.shape[0], []))

  def put(self, clusters_mean, assigned_points):
    self.cache.setdefault(clusters_mean.shape[0], []).append((clusters_mean, assigned_points))

def _init_clusters_center(data, number_of_clusters):
    assigned_points = np.zeros(data.shape[0], dtype=_ctypes.c_ushort)
    if number_of_clusters == 1:
      return np.mean(data, axis=0)[np.newaxis], assigned_points

    clusters_mean = np.empty((number_of_clusters, data.shape[1]))
    number_of_clusters = _ctypes.c_ushort(number_of_clusters)

    err_desc = _ctypes.c_void_p()
    if not _api.clusterize(data.shape[0], data.shape[1],
                           data.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(data.ctypes.strides, _api.c_size_ptr),
                           _ctypes.byref(number_of_clusters), clusters_mean.ctypes.data_as(_api.c_double_ptr),
                           _ctypes.cast(clusters_mean.ctypes.strides, _api.c_size_ptr),
                           assigned_points.ctypes.data_as(_api.c_ushort_ptr), assigned_points.strides[0] // assigned_points.itemsize,
                           _ctypes.c_char_p(_bytes("cart")), _ctypes.byref(err_desc)):
        _shared.ModelStatus.checkErrorCode(0, 'Clustering has failed.', err_desc)
    return clusters_mean[:number_of_clusters.value], assigned_points

def _enumerate_covariance(n_clusters, data, assigned_points, min_covar):
  n_features = data.shape[1]
  clusters_regul = np.diag([min_covar]*n_features)
  for cluster_idx in xrange(n_clusters):
    cluster_data = data[assigned_points == cluster_idx]
    yield cluster_idx, (np.cov((cluster_data if cluster_data.size else data).T) + clusters_regul)

def _fit_gmm(data, clusters_mean, assigned_points, covariance_type, n_iter, thresh, watcher=None):
  n_clusters, n_features = clusters_mean.shape

  mixture_model = gmm._GMM(n_components=n_clusters, covariance_type=covariance_type, n_iter=n_iter, thresh=thresh, init_params='')

  if covariance_type == 'spherical':
    clusters_cov = np.empty((n_clusters, n_features))
    for cluster_idx, cluster_cov in _enumerate_covariance(n_clusters, data, assigned_points, mixture_model.min_covar):
      clusters_cov[cluster_idx, :] = np.mean(cluster_cov)
  elif covariance_type == 'tied':
    clusters_cov = np.cov(data.T) + np.diag([mixture_model.min_covar]*n_features)
  elif covariance_type == 'diag':
    clusters_cov = np.empty((n_clusters, n_features))
    for cluster_idx, cluster_cov in _enumerate_covariance(n_clusters, data, assigned_points, mixture_model.min_covar):
      clusters_cov[cluster_idx] = np.diag(cluster_cov)
  elif covariance_type == 'full':
    clusters_cov = np.empty((n_clusters, n_features, n_features))
    for cluster_idx, cluster_cov in _enumerate_covariance(n_clusters, data, assigned_points, mixture_model.min_covar):
      clusters_cov[cluster_idx] = cluster_cov
  else:
    raise ValueError("covariance_type must be one of 'spherical', 'tied', 'diag', 'full'")

  mixture_model.means_ = clusters_mean.copy()
  mixture_model._set_covars(clusters_cov)
  mixture_model.weights_ = np.array([np.count_nonzero(assigned_points == c) / float(data.shape[0]) for c in xrange(n_clusters)])
  mixture_model.fit(data, watcher)

  return mixture_model

def _build_optimal_bic(data,
                       possible_number_of_clusters, covariance_types_set,
                       n_iter, thresh, logger, watcher):
  best_bic = np.inf
  cache = _GMMInitCache()
  tests_done, n_tests = 0, len(possible_number_of_clusters) * len(covariance_types_set)

  for number_of_clusters in possible_number_of_clusters:
    clusters_mean, assigned_points = _init_clusters_center(data, number_of_clusters)

    if cache.has(clusters_mean, assigned_points):
      tests_done += len(covariance_types_set)
      logger.info("\tSkipping %d clusters case because effective number of clusters is %d" % (number_of_clusters, clusters_mean.shape[0]))
      continue
    cache.put(clusters_mean, assigned_points)

    for covariance_type in covariance_types_set:
      mixture_model = _fit_gmm(data, clusters_mean, assigned_points, covariance_type, n_iter, thresh, watcher)

      current_bic = mixture_model.bic(data)
      if current_bic < best_bic:
        best_bic = current_bic
        best_gmm = mixture_model
        best_covariance_type = covariance_type

      tests_done += 1
      logger.info("Experiment #%d/%d:" % (tests_done, n_tests))
      logger.info("- number of clusters: %d%s" % (number_of_clusters, ((" (effective %d)" % clusters_mean.shape[0]) if number_of_clusters != clusters_mean.shape[0] else "")))
      logger.info("- covariance type: %s" % covariance_type)
      logger.info("- BIC: %g (optimal %g)" % (current_bic, best_bic))

      _check_abort(watcher)

  logger.info("Final decision:")
  logger.info('- number of clusters: %s' % best_gmm.weights_.shape[0])
  logger.info('- covariance matrix type: %s' % best_covariance_type)
  logger.info('- bayesian information criterion: %s' % best_bic)

  return best_covariance_type, best_gmm

def _build_optimal_sil(data,
                       possible_number_of_clusters, covariance_types_set,
                       min_sample_size, min_cluster_size,
                       options, sample_size,
                       n_iter, thresh, logger, watcher):
  # List of possible settings in (number_of_clusters, covariance_type, mixture_model) format
  settings = []
  cache = _GMMInitCache()

  best_bic, best_sil = np.inf, 0.
  tests_done, n_tests = 0, len(possible_number_of_clusters) * len(covariance_types_set)

  # Silhouettes are equal for all covariance types if number_of_clusters == 1
  if 1 in possible_number_of_clusters:
    possible_number_of_clusters = [_ for _ in possible_number_of_clusters if _ > 1]
    clusters_mean = data.mean(axis=0).reshape(1, -1)
    assigned_points = np.zeros(data.shape[0], dtype=_ctypes.c_ushort)
    cache.put(clusters_mean, assigned_points)

    # Add all covariance types to settings list
    for covariance_type in covariance_types_set:
      mixture_model = _fit_gmm(data, clusters_mean, assigned_points, covariance_type, n_iter, thresh, watcher)
      current_bic = mixture_model.bic(data)
      if current_bic < best_bic:
        best_bic = current_bic
        best_gmm = mixture_model
        best_covariance_type = covariance_type

      tests_done += 1
      logger.info("Experiment #%d/%d:" % (tests_done, n_tests))
      logger.info("- number of clusters: 1")
      logger.info("- covariance type: %s" % covariance_type)
      logger.info("- BIC: %g (optimal %g)" % (current_bic, best_bic))

      _check_abort(watcher)

  # Choose optimal covariance types for all possible number of clusters
  points_assignment_confidence = 0.97 if not options else _shared.parse_float(options.get('GTApprox/MoAPointsAssignmentConfidence'))
  for number_of_clusters in possible_number_of_clusters:
    clusters_mean, assigned_points = _init_clusters_center(data, number_of_clusters)

    if cache.has(clusters_mean, assigned_points):
      tests_done += len(covariance_types_set)
      logger.info("\tSkipping %d clusters case because effective number of clusters is %d" % (number_of_clusters, clusters_mean.shape[0]))
      continue
    cache.put(clusters_mean, assigned_points)

    for covariance_type in covariance_types_set:
      mixture_model = _fit_gmm(data, clusters_mean, assigned_points, covariance_type, n_iter, thresh, watcher)

      clusterwise_sil = _silhouettes(data, mixture_model, points_assignment_confidence)
      #current_sil = np.percentile(clusterwise_sil, 50)
      current_sil = clusterwise_sil.mean()
      current_bic = mixture_model.bic(data)

      if current_sil >= best_sil:
        # current silhouette is better than the optimal meaning clusters
        # are better separated, so we compare BIC to take into account
        # single cluster mode
        best_sil = current_sil
        if current_bic < best_bic:
          best_bic = current_bic
          best_gmm = mixture_model
          best_covariance_type = covariance_type
      elif current_bic < best_bic and best_sil * current_bic < best_bic * current_sil:
        # Current BIC is better while current silhouette is worse.
        # BIC-based improvement can be better than silhouette loss.
        best_sil = current_sil
        best_bic = current_bic
        best_gmm = mixture_model
        best_covariance_type = covariance_type

      tests_done += 1
      logger.info("Experiment #%d/%d:" % (tests_done, n_tests))
      logger.info("- number of clusters: %d%s" % (number_of_clusters, ((" (effective %d)" % clusters_mean.shape[0]) if number_of_clusters != clusters_mean.shape[0] else "")))
      logger.info("- covariance type: %s" % covariance_type)
      logger.info("- silhouette: %g (optimal %g)" % (current_sil, best_sil))
      logger.info("- BIC: %g (optimal %g)" % (current_bic, best_bic))

      _check_abort(watcher)

  logger.info("Final decision:")
  logger.info('- number of clusters: %s' % best_gmm.weights_.shape[0])
  logger.info('- covariance matrix type: %s' % best_covariance_type)
  logger.info('- bayesian information criterion: %s' % best_bic)

  return best_covariance_type, best_gmm


def assign(clustering_model, data, options, mode=None):
  """
  Assign data to clusters.
  Function returns probabililties of each data point to be assigned to each cluster.

  :param clustering_model: gaussian mixture model
  :param data: data to be assigned to clusters
  :param options: MoA options
  :param mode: assignment or weights mode. Possible values are: "assign" and "weights"
  :return probabilities: probabilities of each data point to be assigned to each cluster
  :rtype: :term:`array-like`

  """
  data = _shared.as_matrix(data, name="data")
  number_of_points, dimension = data.shape

  if dimension > clustering_model['means'].shape[1]:
    raise ValueError('Wrong data dimensionality!')

  points_assignment = options.get('GTApprox/MoAPointsAssignment').lower()
  points_assignment_confidence = _shared.parse_float(options.get('GTApprox/MoAPointsAssignmentConfidence'))
  type_of_weights = options.get('GTApprox/MoATypeOfWeights').lower()
  weights_confidence = _shared.parse_float(options.get('GTApprox/MoAWeightsConfidence'))

  number_of_clusters = clustering_model['number_of_clusters']
  distances = np.empty([number_of_points, number_of_clusters], dtype=float)
  if _parse_dry_run(options):
    distances.fill(1.)
    return distances

  # compute posterior probabilities
  for cluster in xrange(number_of_clusters):
    mean = clustering_model['means'][cluster, 0:dimension]
    covariance = clustering_model['covars_cholesky_factor'][cluster, 0:dimension, 0:dimension]
    weight = clustering_model['weights'][cluster]

    if mode == 'assign':
      if points_assignment == 'probability':
        distances[:, cluster] = _probability(data, mean, covariance, weight)
      elif points_assignment == 'mahalanobis':
        distances[:, cluster] = _mahalanobis_dist(data, mean, covariance)

    elif mode == 'weights':
      if type_of_weights == 'probability':
        distances[:, cluster] = _probability(data, mean, covariance, weight)
      elif type_of_weights == 'sigmoid':
        distances[:, cluster] = _weights_sigmoid(data, mean, covariance,
                                                 points_assignment_confidence,
                                                 weights_confidence)

  if mode == "assign":
    if points_assignment == 'mahalanobis':
      chi_squared = distributions._chi2(dimension)
      q_assign_conf = chi_squared.quantile(points_assignment_confidence)
      distances = (distances < q_assign_conf + 1e-34).astype(float)

  # if mode is 'weights':
  #   if type_of_weights is 'sigmoid':
  #     return distances

  distances /= np.tile(np.sum(distances + 1e-34, axis=1).reshape(number_of_points, 1), number_of_clusters)
  return distances


def _indices(probabilities, clustering_model):
  min_cluster_size = int(clustering_model['min_cluster_size'])
  probabilities_max = probabilities.max(axis=1)
  n_points = len(probabilities_max)

  indices = []

  for i in xrange(clustering_model['number_of_clusters']):
    infeasibility_score = probabilities_max - probabilities[:, i]
    cluster_threshold = np.percentile(infeasibility_score, min(100., (100. * max(min_cluster_size, np.count_nonzero(infeasibility_score <= 1.e-5))) / n_points))
    indices.append(np.where(infeasibility_score <= cluster_threshold)[0])

  return indices

def _silhouettes(data, gmm, points_assignment_confidence):
  n_clusters = gmm.weights_.shape[0]
  n_features = gmm.means_.shape[1]
  n_points = data.shape[0]

  if n_features != data.shape[1]:
    raise ValueError("Unconformed number of features: %d (data) != %d (GMM)" % (n_features, data.shape[1]))

  # convert covariances to 3d matrix (array of covariance matrices)
  covariances = np.empty((n_clusters, n_features, n_features), dtype=_ctypes.c_double)
  covariance_type = str(gmm._covariance_type).lower()

  if covariance_type in ('spherical', 'diag'):
    for i in xrange(n_clusters):
      covariances[i] = np.diag(gmm.covars_[i, :])
  elif covariance_type == 'tied':
    for i in xrange(n_clusters):
      covariances[i] = gmm.covars_
  elif covariance_type == 'full':
    for i in xrange(n_clusters):
      covariances[i] = gmm.covars_[i]
  else:
    raise ValueError("Invalid or unsupported covariance type: %s" % covariance_type)

  silhouettes = np.empty(n_clusters, dtype=_ctypes.c_double)

  err_desc = _ctypes.c_void_p()
  if not _api.silhouettes(n_points, n_features, n_clusters,
                         data.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(data.ctypes.strides, _api.c_size_ptr),
                         gmm.means_.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(gmm.means_.ctypes.strides, _api.c_size_ptr),
                         covariances.ctypes.data_as(_api.c_double_ptr), _ctypes.cast(covariances.ctypes.strides, _api.c_size_ptr),
                         silhouettes.ctypes.data_as(_api.c_double_ptr), silhouettes.strides[0] // silhouettes.itemsize,
                         points_assignment_confidence, _ctypes.byref(err_desc)):
    _shared.ModelStatus.checkErrorCode(0, 'Silhouettes evaluation has failed.', err_desc)

  return silhouettes

def _covariances(gmm, covariance_type):
  """ Calculate array of covariance matrices for
  covars_cholesky_factor field of clustering model """
  number_of_clusters = gmm.weights_.shape[0]
  number_of_features = gmm.means_.shape[1]
  # convert covariances to 3d matrix (array of covariance matrices)
  covariances = np.empty((number_of_clusters, number_of_features,
                          number_of_features), dtype=float)
  # we would store only L - lower triangular of cholesky decomposition
  if covariance_type == 'spherical' or covariance_type == 'diag':
    for i in xrange(number_of_clusters):
      covariances[i, :, :] = np.sqrt(np.diag(gmm.covars_[i, :]))
  elif covariance_type == 'tied':
    L = np.linalg.cholesky(gmm.covars_)
    for i in xrange(number_of_clusters):
      covariances[i, :, :] = L
  else:
    for i in xrange(number_of_clusters):
      covariances[i] = np.linalg.cholesky(gmm.covars_[i])
  return covariances


def grad(clustering_model, point, options):
  dim = 1
  if _shared.is_iterable(point):
    dim = len(point)
    if dim == 0:
      raise ValueError('Empty input data!')
    if _shared.is_iterable(point[0]):
      raise ValueError('Point batches are not supported!')

  if dim > clustering_model['means'].shape[1]:
    raise ValueError('Wrong data dimensionality!')

  points_assignment_confidence = _shared.parse_float(options.get('GTApprox/MoAPointsAssignmentConfidence'))
  type_of_weights = options.get('GTApprox/MoATypeOfWeights').lower()
  weights_confidence = _shared.parse_float(options.get('GTApprox/MoAWeightsConfidence'))

  means = clustering_model['means'][:, 0:dim]
  covariances = clustering_model['covars_cholesky_factor'][:, 0:dim, 0:dim]
  weights = clustering_model['weights']
  if type_of_weights == 'probability':
    return _grad_probability(point, means, covariances, weights)
  if type_of_weights == 'sigmoid':
    return _grad_sigmoid(point, means, covariances,
                          points_assignment_confidence, weights_confidence)


def __cho_solve_v(L, b):
  """Solve equation L L' x = b, where L is a lower triangular matrix
  """
  x = _linalg._dtrsv(_linalg.CblasLower, _linalg.CblasNoTrans, _linalg.CblasNonUnit, L, b.copy())
  x = _linalg._dtrsv(_linalg.CblasLower, _linalg.CblasTrans, _linalg.CblasNonUnit, L, x)
  return x


def _mahalanobis_dist(points, mean, cov_chol_factor):
  mean = _shared.as_matrix(mean, shape=(1, None))
  points, single_point = _shared.as_matrix(points, shape=(None, mean.shape[1]), ret_is_vector=True)

  X = np.empty_like(points.T, order='C')
  X = _linalg._dtrsm(_linalg.CblasLeft, _linalg.CblasLower, _linalg.CblasNoTrans, _linalg.CblasNonUnit,
                     1., cov_chol_factor, np.subtract(points.T, mean.T, out=X))
  mahalanobis_distance = np.sum(X**2, axis=0)
  return mahalanobis_distance[0] if single_point else mahalanobis_distance


def _probability(points, mean, covariance, weight):
  mahalanobis_distance = _mahalanobis_dist(points, mean, covariance)
  determinant = np.prod(np.diag(covariance))**2
  return weight / np.sqrt(determinant * (2 * pi) ** points.shape[-1]) * np.exp(-mahalanobis_distance)


def _weights_sigmoid(points, mean, covariance, assign_conf, weights_conf):
  distances = _mahalanobis_dist(points, mean, covariance)

  chi_squared = distributions._chi2(points.shape[-1])
  q_assign_conf = chi_squared.quantile(assign_conf)
  q_weights_conf = chi_squared.quantile(weights_conf)
  distances = ((distances - q_assign_conf) /
               (q_weights_conf - q_assign_conf))
  return 0.5 * (np.tanh(1 - 2 * distances) + 1)


def _grad_probability(point, means, cov_chol_factor, weights):
  """
  dw / dx = || dw_1 / dx; ...; dw_n / dx ||, where
  dw_k / dx - is a column.
  dw_k / dx = -w_k(x) * 2 S^{-1} (x - mu_k) +
              w_k(x) * sum_m (w_m(x) * 2 * S^{-1} * (x - mu_m)) =
              first_term + second_term

  """
  n_clusters = means.shape[0]
  dim = means.shape[1]
  probability = np.empty(shape=(n_clusters), dtype=float)
  first_term = np.empty(shape=(dim, n_clusters), dtype=float)
  for i in xrange(n_clusters):
    X = point - means[i]
    mahalanobis_distance = _mahalanobis_dist(
        X, np.zeros(means[i].shape), cov_chol_factor[i])
    determinant = np.prod(np.diag(cov_chol_factor[i]))**2
    probability[i] = weights[i] / np.sqrt(determinant * (2 * pi) ** dim) * np.exp(-mahalanobis_distance)
    first_term[:, i] = 2 * probability[i] * __cho_solve_v(cov_chol_factor[i], X)

  normalization = np.sum(probability)
  probability /= normalization
  first_term /= normalization
  grad = -first_term + probability * np.sum(first_term, axis=1)[:, np.newaxis]
  return grad


def _grad_sigmoid(point, means, cov_chol_factor, assign_conf, weights_conf):
  """
  dw / dx = || dw_1 / dx; ...; dw_n / dx ||, where
  dw_k / dx - is a column.
  dw_k / dx = 2 S^{-1} (x - mu_k) /
              (ch(1 - 2 * (d_k(x) - chi^2_\alpha_0) / (chi^2_\alpha_1 - chi^2_\alpha_0)) *
              (chi^2_\alpha_1 - chi^2_\alpha_0))

  """
  n_clusters = means.shape[0]
  dim = means.shape[1]
  grad = np.empty(shape=(dim, n_clusters), dtype=float)
  for i in xrange(n_clusters):
    X = point - means[i]
    distance = _mahalanobis_dist(X, np.zeros(means[i].shape),
                                 cov_chol_factor[i])

    chi_squared = distributions._chi2(dim)
    q_assign_conf = chi_squared.quantile(assign_conf)
    q_weights_conf = chi_squared.quantile(weights_conf)
    grad[:, i] = -2 * __cho_solve_v(cov_chol_factor[i], X)
    grad[:, i] /= (np.cosh(1 - (2 * (distance - q_assign_conf) /
                                (q_weights_conf - q_assign_conf)))**2 *
                                (q_weights_conf - q_assign_conf))

  return grad
