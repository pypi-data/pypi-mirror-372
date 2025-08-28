#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

from .. import exceptions as _ex
import numpy as np
import math
from .. import shared as _shared
from operator import itemgetter
from numpy import linalg, mean, cov, dot

def _interrupt():
  return False

def _diag_slice(x):
  return x.reshape(-1)[:x.size:x.strides[0]//x.itemsize+1]

def _fast_logdet(A):
  """Compute log(det(A)) for A symmetric

  Equivalent to : np.log(np.linalg.det(A)) but more robust.
  It returns -Inf if det(A) is non positive or is not defined.
  """
  try:
    A_diag = np.diag(A)
    if np.any(A_diag <= 0.):
      return -np.inf
    ld = np.log(A_diag).sum()
    a = np.exp(ld / A.shape[0])
    d = np.linalg.det(A / a)
    if d > 1.e-8:
      ld += np.log(d)
    return ld if np.isfinite(ld) else -np.inf
  except:
    return -np.inf


def _pinvh(a, cond=None, rcond=None, lower=True):
  """Compute the (Moore-Penrose) pseudo-inverse of a hermitian matrix.

  Calculate a generalized inverse of a symmetric matrix using its
  eigenvalue decomposition and including all 'large' eigenvalues.

  Parameters
  ----------
  a : array, shape (N, N)
    Real symmetric or complex hermitian matrix to be pseudo-inverted
  cond, rcond : float or None
    Cutoff for 'small' eigenvalues.
    Singular values smaller than rcond * largest_eigenvalue are considered
    zero.

    If None or -1, suitable machine precision is used.
  lower : boolean
    Whether the pertinent array data is taken from the lower or upper
    triangle of a. (Default: lower)

  Returns
  -------
  B : array, shape (N, N)

  Raises
  ------
  LinAlgError
    If eigenvalue does not converge

  Examples
  --------
  >>> from numpy import *
  >>> a = random.randn(9, 6)
  >>> a = np.dot(a, a.T)
  >>> B = pinvh(a)
  >>> allclose(a, dot(a, dot(B, a)))
  True
  >>> allclose(B, dot(B, dot(a, B)))
  True

  """
  a = np.asarray_chkfinite(a)
  s, u = np.linalg.eigh(a)

  if rcond is not None:
    cond = 1. / rcond if rcond > 0. else None
  if cond in [None, -1] or not np.isfinite(cond):
    t = u.dtype.char.lower()
    factor = {'f': 1E3, 'd': 1E6}
    cond = factor[t] * np.finfo(t).eps

  # unlike svd case, eigh can lead to negative eigenvalues
  above_cutoff = (abs(s) > cond * np.max(abs(s)))
  psigma_diag = np.zeros_like(s)
  psigma_diag[above_cutoff] = 1.0 / s[above_cutoff]

  return np.dot(u * psigma_diag, np.conjugate(u).T)

def _factorize_covariance(covariance_matrix):
  """  Calculates inverse of the lower Cholesky factor of the regularized covariance matrix.

      For example, let
       K is covariance matrix
       X is matrix of rowwise points

       Kinv = np.linag.inv(K)
       L = _factorize_covariance(K) calculation:

      then calcualtion of
         squared_distances = vectorize(lambda x: np.dot(x, np.dot(Kinv, x.T)))(X)
      is equivalent to
         squared_distances = np.hypot.reduce(np.dot(L, X.T), axis=0)**2.
  """
  covariance_matrix = np.atleast_2d(covariance_matrix)
  if covariance_matrix.shape[0] != covariance_matrix.shape[1]:
    raise ValueError("The covariance matrix must be square.")

  # Cholesky decomposition of the regularized covariance matrix
  for regul in range(-16, 0):
    try:
      # regularize main diagonal of the covariance matrix
      regularized_covariance = covariance_matrix.copy()
      regularized_covariance_diag = _diag_slice(regularized_covariance)
      np.multiply(regularized_covariance_diag, 1. + 10.**regul, out=regularized_covariance_diag)
      np.add(regularized_covariance_diag, np.finfo(float).eps, out=regularized_covariance_diag)
      # calculate inverse of the cholesky factor
      return np.linalg.inv(np.linalg.cholesky(regularized_covariance))
    except:
      pass

  raise ValueError("Cholesky decomposition of the regularized covariance matrix cannot be computed")

def _calculate_kurtosis_coefficient(sample, mahalanobis_covariances, factorized_covariances=False):
  """Calculates kurtosis coefficient which is used to check_normality"""
  sample = np.array(sample, dtype=np.float64, ndmin=2)
  mahalanobis_covariances = np.array(mahalanobis_covariances, dtype=np.float64, ndmin=2)
  if mahalanobis_covariances.shape[0] != mahalanobis_covariances.shape[1]:
    raise _ex.GTException("The covariance matrix is not square")
  L = mahalanobis_covariances if factorized_covariances else _factorize_covariance(mahalanobis_covariances)
  return np.hypot.reduce(np.hypot.reduce(np.dot(L, sample.T), axis=0)**2.)**2.

def _calculate_skewness_coefficient(sample, mahalanobis_covariances, factorized_covariances=False):
  sample = np.array(sample, dtype=np.float64, ndmin=2)
  mahalanobis_covariances = np.array(mahalanobis_covariances, dtype=np.float64, ndmin=2)
  if mahalanobis_covariances.shape[0] != mahalanobis_covariances.shape[1]:
    raise _ex.GTException("The covariance matrix is not square")
  S = np.dot(sample, (mahalanobis_covariances if factorized_covariances else _factorize_covariance(mahalanobis_covariances)).T)
  return sum((np.dot(S, x)**3).sum() for x in S)

def _get_positive_erf(input_value):
  if input_value > np.finfo(float).eps:
    lower_count = 0
    values_list = [0.0, 0.0088625012809506066, 0.017726395026678034, 0.026593075234088433, 0.035463938968718675,
                   0.044340387910005531, 0.053223829909766027, 0.062115680568403969, 0.071017364833454805, 0.07993031862520325,
                   0.088855990494257769, 0.09779584331614373, 0.1067513560281845, 0.11572402541417932, 0.12471536794266069,
                   0.13372692166481961, 0.14276024817854743, 0.15181693466541812, 0.16089859600789125, 0.17000687699449396,
                   0.17914345462129161, 0.18831004049856323, 0.19750838337227367, 0.20674027177068635, 0.21600753678729467,
                   0.22531205501217808, 0.23465575162492164, 0.24404060366338221, 0.25346864348386572, 0.26294196242969731,
                   0.27246271472675443, 0.2820331216263019, 0.29165547581744217, 0.3013321461337059, 0.31106558258078482,
                   0.32085832171518158, 0.33071299240667351, 0.34063232202099486, 0.35061914306308917, 0.3606764003257581,
                   0.37080715859355784, 0.38101461095753192, 0.39130208780283199, 0.40167306653867352, 0.41213118214846539,
                   0.42268023864756182, 0.4333242215470679, 0.44406731143474226, 0.45491389879854, 0.46586860023505733,
                   0.47693627620446982, 0.48812205051595875, 0.49943133175366339, 0.51086983688356091, 0.52244361731717892,
                   0.53415908774970233, 0.54602305813905516, 0.55804276925044727, 0.57022593225950968, 0.58258077298879629,
                   0.59511608144999484, 0.60784126748116196, 0.62076642340927002, 0.63390239483887101, 0.64726086087507373,
                   0.6608544253423857, 0.67469672087225308, 0.6888025281165564, 0.7031879128220363, 0.71787038409775472,
                   0.73286907795921696, 0.74820497118498508, 0.76390113173723617, 0.77998301356170252, 0.79647880561170736,
                   0.81341984759761832, 0.83084112847456026, 0.84878188837096069, 0.86728635099387497, 0.88640462220354321,
                   0.90619380243682313, 0.92671937749552846, 0.94805697623234941, 0.97029461851300935, 0.99353562834730391,
                   1.0179024648320278, 1.0435418436397583, 1.0706317121429476, 1.0993909519492191, 1.1300932068852458,
                   1.1630871536766736, 1.1988272177415737, 1.2379219927112441, 1.2812143237490634, 1.3299219143360637,
                   1.3859038243496777, 1.4522197815622464, 1.5344856217777179, 1.6449763571331868, 1.8213863677184492]
    return 0.01 * np.less(values_list, input_value).sum()
  return 0.

class ElementaryStatistics(object):
  """
  Elementary statistics computation results.

  A :class:`~da.p7core.stat.ElementaryStatistics` object is only returned by the
  :func:`~da.p7core.stat.Analyzer.calculate_statistics()` function and must not be instantiated by user.


  .. py:attribute:: min

    A list of minimal values for each dimension of the data sample.

  .. py:attribute:: max

    A list of maximal values for each dimension of the data sample.

  .. py:attribute:: mean

    A list of mean values for each dimension of the data sample.

  .. py:attribute:: median

    A list of median values for each dimension of the data sample.

  .. py:attribute:: range

    .. versionadded:: 1.10.2

    A list of value ranges for each dimension of the data sample.

  .. py:attribute:: quantile_lower

    A list of lower quantiles for the specified confidence level for each dimension of the data sample.

  .. py:attribute:: quantile_upper

    A list of upper quantiles for the specified confidence level for each dimension of the data sample.

  .. py:attribute:: std

    A list of standard deviations for each dimension of the data sample.

  .. py:attribute:: correlation

    A matrix of correlation coefficients  between different dimensions in the data sample.

  """

  def __init__(self, statistics):
    self.__min = statistics['min']
    self.__max = statistics['max']
    self.__mean = statistics['mean']
    self.__median = statistics['median']
    self.__range = statistics['range']
    self.__quantile_lower = statistics['quantile_lower']
    self.__quantile_upper = statistics['quantile_upper']
    self.__std = statistics['std']
    self.__correlation = statistics['correlation']

  @property
  def min(self):
    return self.__min

  @property
  def max(self):
    return self.__max

  @property
  def mean(self):
    return self.__mean

  @property
  def median(self):
    return self.__median

  @property
  def range(self):
    return self.__range

  @property
  def quantile_lower(self):
    return self.__quantile_lower

  @property
  def quantile_upper(self):
    return self.__quantile_upper

  @property
  def std(self):
    return self.__std

  @property
  def correlation(self):
    return self.__correlation

  def __str__(self):
    result = ('Statistics:\n-----\n' +
              '\n\n' + 'Min: ' + str(self.__min) +
              '\n\n' + 'Max: ' + str(self.__max) +
              '\n\n' + 'Mean: ' + str(self.__mean) +
              '\n\n' + 'Median: ' + str(self.__median) +
              '\n\n' + 'Range: ' + str(self.__range) +
              '\n\n' + 'Quantile lower: ' + str(self.__quantile_lower) +
              '\n\n' + 'Quantile upper: ' + str(self.__quantile_upper) +
              '\n\n' + 'Std: ' + str(self.__std) +
              '\n\n' + 'Correlation: ' + str(self.__correlation))

    return result


class DistributionCheckResult(object):
  """
  Distribution tests result.

  A :class:`~da.p7core.stat.DistributionCheckResult` object is only returned by the
  :func:`~da.p7core.stat.Analyzer.check_distribution()` function and must not be instantiated by user.


  .. py:attribute:: uniform

    Boolean result of checking sample on uniform distribution. If test was not performed attribute value will be set to ``None``.

  .. py:attribute:: normal_kurtosis

    Boolean result of checking sample on normal distribution via kurtosis test. If test was not performed attribute value will be set to ``None``.

  .. py:attribute:: normal_skewness

    Boolean result of checking sample on normal distribution via skewness test. If test was not performed attribute value will be set to ``None``.

  """

  def __init__(self, tests):
    if 'uniform' in tests:
      self.__uniform = tests['uniform']
    else:
      self.__uniform = None

    if 'normal_kurtosis' in tests:
      self.__normal_kurtosis = tests['normal_kurtosis']
    else:
      self.__normal_kurtosis = None

    if 'normal_skewness' in tests:
      self.__normal_skewness = tests['normal_skewness']
    else:
      self.__normal_skewness = None

  @property
  def uniform(self):
    return self.__uniform

  @property
  def normal_kurtosis(self):
    return self.__normal_kurtosis

  @property
  def normal_skewness(self):
    return self.__normal_skewness

  def __str__(self):
    result = ('Tests:\n-----\n' +
              '\n\n' + 'Uniformity test:\n-----\n' + str(self.__uniform) +
              '\n\n' + 'Normality kurtosis test:\n-----\n' + str(self.__normal_kurtosis) +
              '\n\n' + 'Normality skewness test:\n-----\n' + str(self.__normal_skewness))
    return result


class OutlierDetectionResult(object):
  """
  Outlier detection result.

  A :class:`~da.p7core.stat.OutlierDetectionResult` object is only returned by the
  :func:`~da.p7core.stat.Analyzer.detect_outliers()` function and must not be instantiated by user.


  .. py:attribute:: scores

    A list containing scores in range [0, 1]. Each value can be interpreted as probability of corresponding object to be an outlier.

  .. py:attribute:: outliers

    A list containing boolean values indicating that corresponding objects are outliers or not.
  """

  def __init__(self, scores, outliers):
    self.__scores = np.array(scores, dtype=float, copy=_shared._SHALLOW)
    self.__outliers = np.array(outliers, dtype=bool, copy=_shared._SHALLOW)

  @property
  def scores(self):
    return self.__scores

  @property
  def outliers(self):
    return self.__outliers

  def __str__(self):
    result = 'Scores:\n-----\n' + str(self.__scores)
    result = result + '\n\n' + 'Outliers mask:\n-----\n' + str(self.__outliers)

    return result

def _get_standard_str_options(options):
  if isinstance(options, list):
    standard_options = np.array([str(option).lower() for option in options])
  else:
    standard_options = str(options).lower()

  return standard_options

def _compute_outliers(scores, confidence_level=0.95):
  number_scores = scores.shape[0]

  number_outliers = int(np.ceil(number_scores * (1. - confidence_level)))

  if number_outliers == 0:
    outlier_mask = [False for _ in scores]
  elif number_outliers == number_scores:
    outlier_mask = [True for _ in scores]
  else:
    outliers_threshold = np.sort(scores)[number_scores - number_outliers]
    outlier_mask = (scores > outliers_threshold)

  return outlier_mask

class _DisjointSet(dict):
  def add(self, item):
    self[item] = item

  def find(self, item):
    parent = self[item]

    while self[parent] != parent:
      parent = self[parent]

    self[item] = parent
    return parent

  def union(self, item1, item2):
    self[item2] = self[item1]

def _find_minimum_spanning_tree(nodes, edges):
  """ find minimum spanning tree (for connected graphs (nodes, edges)) and minimum spanning forest (for disconnected graphs (nodes, edges))

    Returns:
      minimum_spanning_tree:
        data array with minimum spanning tree (or forest) edges. Size: (len(nodes) - 1) for connected graph (nodes, edges), less for disconnected graph.
      is_connected:
        True for connected graph (nodes, edges). False for disconnected graph (nodes, edges).
  """
  forest = _DisjointSet()
  minimum_spanning_tree = []
  for node in nodes:
    forest.add(node)

  edges_to_add = len(nodes) - 1

  for edge in sorted(edges, key=itemgetter(2)):
    first_node, second_node, _ = edge
    first_tree = forest.find(first_node)
    second_tree = forest.find(second_node)
    if first_tree != second_tree:
      minimum_spanning_tree.append(edge)
      edges_to_add -= 1
      if edges_to_add == 0:
        is_connected = True
        return minimum_spanning_tree, is_connected

      forest.union(first_tree, second_tree)

  is_connected = False
  return minimum_spanning_tree, is_connected

def _find_principal_components(sample):
  """ performs principal components analysis
      (PCA) on the n-by-p data matrix sample
      Rows of sample correspond to observations, columns to variables.

   Returns:
    coefficients:
      is a p-by-p matrix, each column containing coefficients
      for one principal component.
    scores:
      the principal component scores; that is, the representation
      of sample in the principal component space. Rows of SCORE
      correspond to observations, columns to components.
    eigenvalues:
      a vector containing the eigenvalues
      of the covariance matrix of sample.
  """
  sample = np.array(sample, dtype=np.float64, ndmin=2)
  centered_sample = (sample - mean(sample.T, axis=1)) # subtract the mean (along columns)
  # not sorted,  np.array needed because cov() function can return scalar in 1-d case
  [eigenvalues, coefficients] = linalg.eig(np.array(cov(centered_sample.T), dtype=np.float64, ndmin=2))
  scores = dot(centered_sample, coefficients) # projection of the data in the new space
  return coefficients, scores, eigenvalues
