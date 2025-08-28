#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

#
# This module uses code from scikit-learn, the Python machine learning package.
# http://scikit-learn.org

"""
Gaussian Mixture Models.

This implementation corresponds to frequentist (non-Bayesian) formulation
of Gaussian Mixture Models.
"""
from __future__ import division

from datetime import datetime as _datetime
import numpy as np
from numpy import linalg

from ..six.moves import xrange, range, zip
from .. import exceptions as _ex

from .cluster_utils import _logsumexp
from .linalg import _dtrsm, CblasLeft, CblasLower, CblasNoTrans, CblasNonUnit

EPS = np.finfo(float).eps

class _GMM:
  """Gaussian Mixture Model

  Representation of a Gaussian mixture model probability distribution.
  This class allows for easy evaluation of, sampling from, and
  maximum-likelihood estimation of the parameters of a GMM distribution.

  Initializes parameters such that every mixture component has zero
  mean and identity covariance.


  Parameters
  ----------
  n_components : int, optional
      Number of mixture components. Defaults to 1.

  covariance_type : string, optional
      String describing the type of covariance parameters to
      use.  Must be one of 'spherical', 'tied', 'diag', 'full'.
      Defaults to 'diag'.

  random_state: RandomState or an int seed (0 by default)
      A random number generator instance

  min_covar : float, optional
      Floor on the diagonal of the covariance matrix to prevent
      overfitting.  Defaults to 1e-3.

  thresh : float, optional
      Convergence threshold.

  n_iter : int, optional
      Number of EM iterations to perform.

  n_init : int, optional
      Number of initializations to perform. the best results is kept

  params : string, optional
      Controls which parameters are updated in the training
      process.  Can contain any combination of 'w' for weights,
      'm' for means, and 'c' for covars.  Defaults to 'wmc'.

  init_params : string, optional
      Controls which parameters are updated in the initialization
      process.  Can contain any combination of 'w' for weights,
      'm' for means, and 'c' for covars.  Defaults to 'wmc'.

  Attributes
  ----------
  `weights_` : array, shape (`n_components`,)
      This attribute stores the mixing weights for each mixture component.

  `means_` : array, shape (`n_components`, `n_features`)
      Mean parameters for each mixture component.

  `covars_` : array
      Covariance parameters for each mixture component.  The shape
      depends on `covariance_type`::

          (n_components,)                        if 'spherical',
          (n_features, n_features)               if 'tied',
          (n_components, n_features)             if 'diag',
          (n_components, n_features, n_features) if 'full'

  `converged_` : bool
      True when convergence was reached in fit(), False otherwise.


  Examples
  --------

  >>> import numpy as np
  >>> from da.p7core.utils import gmm
  >>> np.random.seed(1)
  >>> g = gmm._GMM(n_components=2)
  >>> # Generate random observations with two modes centered on 0
  >>> # and 10 to use for training.
  >>> obs = np.concatenate((np.random.randn(100, 1),
  ...                       10 + np.random.randn(300, 1)))
  >>> g.fit(obs) # doctest: +NORMALIZE_WHITESPACE
  _GMM(covariance_type=None, init_params='wmc', min_covar=0.001,
          n_components=2, n_init=1, n_iter=100, params='wmc',
          random_state=None, thresh=0.01)
  >>> np.round(g.weights_, 2)
  array([ 0.75,  0.25])
  >>> np.round(g.means_, 2)
  array([[ 10.05],
         [  0.06]])
  >>> np.round(g.covars_, 2) #doctest: +SKIP
  array([[[ 1.02]],
         [[ 0.96]]])
  >>> g.predict([[0], [2], [9], [10]])
  array([1, 1, 0, 0])
  >>> np.round(g.score([[0], [2], [9], [10]]), 2)
  array([-2.19, -4.58, -1.75, -1.21])
  >>> # Refit the model on new data (initial parameters remain the
  >>> # same), this time with an even split between the two modes.
  >>> g.fit(20 * [[0]] +  20 * [[10]]) # doctest: +NORMALIZE_WHITESPACE
  _GMM(covariance_type=None, init_params='wmc', min_covar=0.001,
          n_components=2, n_init=1, n_iter=100, params='wmc',
          random_state=None, thresh=0.01)
  >>> np.round(g.weights_, 2)
  array([ 0.5,  0.5])

  """

  def __init__(self, n_components=1, covariance_type='diag',
               random_state=None, thresh=1e-2, min_covar=1e-3,
               n_iter=100, n_init=1, params='wmc', init_params='wmc'):
    covar_funcs = {
      'spherical': (_log_multivariate_normal_density_spherical, _covar_mstep_spherical),
      'tied': (_log_multivariate_normal_density_tied, _covar_mstep_tied),
      'diag': (_log_multivariate_normal_density_diag, _covar_mstep_diag),
      'full': (_log_multivariate_normal_density_full, _covar_mstep_full),
     }

    if covariance_type not in covar_funcs:
      raise ValueError('Invalid value for covariance_type: %s. Expected values are %s'
                       % (covariance_type, ", ".join(("'%s'" % k) for k in covar_funcs)))

    self.n_components = n_components
    self._log_multivariate_normal_density, self._covar_mstep = covar_funcs[covariance_type]
    self._covariance_type = covariance_type
    self.thresh = thresh
    self.min_covar = min_covar
    self.random_state = random_state
    self.n_iter = n_iter
    self.n_init = n_init
    self.params = params
    self.init_params = init_params

    if n_init < 1:
      raise ValueError('GMM estimation requires at least one run')

    self.weights_ = np.ones(self.n_components) / self.n_components

    # flag to indicate exit status of fit() method: converged (True) or n_iter reached (False)
    self.converged_ = False

  def _get_covars(self):
    """Covariance parameters for each mixture component.
    The shape depends on `cvtype`::

          (`n_states`, 'n_features')                if 'spherical',
          (`n_features`, `n_features`)              if 'tied',
          (`n_states`, `n_features`)                if 'diag',
          (`n_states`, `n_features`, `n_features`)  if 'full'
    """
    if self._covariance_type == 'full':
      return self.covars_
    elif self._covariance_type == 'diag':
      return [np.diag(cov) for cov in self.covars_]
    elif self._covariance_type == 'tied':
      return [self.covars_] * self.n_components
    elif self._covariance_type == 'spherical':
      return [np.diag(cov) for cov in self.covars_]

  def _set_covars(self, covars):
    """Provide values for covariance"""
    covars = np.asarray(covars)
    _validate_covars(covars, self._covariance_type, self.n_components)
    self.covars_ = covars

  def eval(self, X):
    """Evaluate the model on data

    Compute the log probability of X under the model and
    return the posterior distribution (responsibilities) of each
    mixture component for each element of X.

    Parameters
    ----------
    X: array_like, shape (n_samples, n_features)
        List of n_features-dimensional data points.  Each row
        corresponds to a single data point.

    Returns
    -------
    logprob: array_like, shape (n_samples,)
        Log probabilities of each data point in X
    responsibilities: array_like, shape (n_samples, n_components)
        Posterior probabilities of each mixture component for each
        observation
    """
    X = np.asarray(X)
    if X.ndim == 1:
      X = X[:, np.newaxis]
    if X.size == 0:
      return np.array([]), np.empty((0, self.n_components))
    if X.shape[1] != self.means_.shape[1]:
      raise ValueError('the shape of X  is not compatible with self')

    lpr = self._log_multivariate_normal_density(X, self.means_, self.covars_) + np.log(self.weights_ + EPS)
    logprob = _logsumexp(lpr, axis=1)
    responsibilities = np.exp(lpr - logprob[:, np.newaxis])
    return logprob, responsibilities

  def score(self, X):
    """Compute the log probability under the model.

    Parameters
    ----------
    X : array_like, shape (n_samples, n_features)
        List of n_features-dimensional data points.  Each row
        corresponds to a single data point.

    Returns
    -------
    logprob : array_like, shape (n_samples,)
        Log probabilities of each data point in X
    """
    logprob, _ = self.eval(X)
    return logprob

  def predict(self, X):
    """Predict label for data.

    Parameters
    ----------
    X : array-like, shape = [n_samples, n_features]

    Returns
    -------
    C : array, shape = (n_samples,)
    """
    logprob, responsibilities = self.eval(X)
    return responsibilities.argmax(axis=1)

  def predict_proba(self, X):
    """Predict posterior probability of data under each Gaussian
    in the model.

    Parameters
    ----------
    X : array-like, shape = [n_samples, n_features]

    Returns
    -------
    responsibilities : array-like, shape = (n_samples, n_components)
        Returns the probability of the sample for each Gaussian
        (state) in the model.
    """
    logprob, responsibilities = self.eval(X)
    return responsibilities

  def fit(self, X, watcher=None):
    """Estimate model parameters with the expectation-maximization
    algorithm.

    A initialization step is performed before entering the em
    algorithm. If you want to avoid this step, set the keyword
    argument init_params to the empty string '' when creating the
    _GMM object. Likewise, if you would like just to do an
    initialization, set n_iter=0.

    Parameters
    ----------
    X : array_like, shape (n, n_features)
        List of n_features-dimensional data points.  Each row
        corresponds to a single data point.
    """
    ## initialization step
    X = np.asarray(X)
    if X.ndim == 1:
        X = X[:, np.newaxis]
    if X.shape[0] < self.n_components:
        raise ValueError('GMM estimation with %s components, but got only %s samples' % (self.n_components, X.shape[0]))

    max_log_prob = - np.inf

    if watcher:
      checkpoint = _datetime.now()

    for _ in range(self.n_init):
      if 'm' in self.init_params or not hasattr(self, 'means_'):
        self.means_ = X[np.random.permutation(X.shape[0])[:self.n_components]]

      if 'w' in self.init_params or not hasattr(self, 'weights_'):
        self.weights_ = np.tile(1.0 / self.n_components, self.n_components)

      if 'c' in self.init_params or not hasattr(self, 'covars_'):
        cv = np.cov(X.T) + self.min_covar * np.eye(X.shape[1])
        if not cv.size:
          cv = np.array([[1.]])
        self.covars_ = _distribute_covar_matrix_to_match_covariance_type(cv, self._covariance_type, self.n_components)

      # EM algorithms
      log_likelihood = []
      best_params = None

      # reset self.converged_ to False
      self.converged_ = False
      for i in xrange(self.n_iter):
        # Expectation step
        curr_log_likelihood, responsibilities = self.eval(X)
        log_likelihood.append(curr_log_likelihood.sum())

        if log_likelihood[-1] > max_log_prob:
          max_log_prob = log_likelihood[-1]
          best_params = {'weights': self.weights_.copy(),
                         'means': self.means_.copy(),
                         'covars': self.covars_.copy()}

        # Check for convergence.
        if i > 0 and abs(log_likelihood[-1] - log_likelihood[-2]) < self.thresh:
          self.converged_ = True
          break

        if watcher and (_datetime.now() - checkpoint).seconds >= 5: # just ignore days to simplify logic
          if not watcher(None):
            raise _ex.UserTerminated()
          checkpoint = _datetime.now()

        # Maximization step
        self._do_mstep(X, responsibilities, self.params, self.min_covar)

      if best_params:
        self.covars_ = best_params['covars']
        self.means_ = best_params['means']
        self.weights_ = best_params['weights']
      return self

  def _do_mstep(self, X, responsibilities, params, min_covar=0):
    """ Perform the Mstep of the EM algorithm and return the class weihgts.
    """
    weights = responsibilities.sum(axis=0)
    weighted_X_sum = np.dot(responsibilities.T, X)
    inverse_weights = 1.0 / (weights[:, np.newaxis] + 10 * EPS)

    if 'w' in params:
      self.weights_ = (weights / (weights.sum() + 10 * EPS) + EPS)
    if 'm' in params:
      self.means_ = weighted_X_sum * inverse_weights
    if 'c' in params:
      self.covars_ = self._covar_mstep(self, X, responsibilities, weighted_X_sum, inverse_weights, min_covar)
    return weights

  def _n_parameters(self):
    """Return the number of free parameters in the model."""
    ndim = self.means_.shape[1]
    if self._covariance_type == 'full':
      cov_params = self.n_components * ndim * (ndim + 1) / 2.
    elif self._covariance_type == 'diag':
      cov_params = self.n_components * ndim
    elif self._covariance_type == 'tied':
      cov_params = ndim * (ndim + 1) / 2.
    elif self._covariance_type == 'spherical':
      cov_params = self.n_components
    mean_params = ndim * self.n_components
    return  int(cov_params + mean_params + self.n_components - 1)

  def bic(self, X):
    """Bayesian information criterion for the current model fit
    and the proposed data

    Parameters
    ----------
    X : array of shape(n_samples, n_dimensions)

    Returns
    -------
    bic: float (the lower the better)
    """
    return (-2. * self.score(X).sum() +
            self._n_parameters() * np.log(X.shape[0]))


#########################################################################
## some helper routines
#########################################################################

def _log_multivariate_normal_density_diag(X, means=0.0, covars=1.0):
  """Compute Gaussian log-density at X for a diagonal model"""
  n_samples, n_dim = X.shape
  lpr = -0.5 * (n_dim * np.log(2 * np.pi) + np.sum(np.log(covars), 1)
                + np.sum((means ** 2) / covars, 1)
                - 2 * np.dot(X, (means / covars).T)
                + np.dot(X ** 2, (1.0 / covars).T))
  return lpr

def _log_multivariate_normal_density_spherical(X, means=0.0, covars=1.0):
  """Compute Gaussian log-density at X for a spherical model"""
  cv = covars.copy()
  if covars.ndim == 1:
      cv = cv[:, np.newaxis]
  if covars.shape[1] == 1:
      cv = np.tile(cv, (1, X.shape[-1]))
  return _log_multivariate_normal_density_diag(X, means, cv)


def _log_multivariate_normal_density_tied(X, means, covars):
  """Compute Gaussian log-density at X for a tied model"""
  n_samples, n_dim = X.shape
  icv = linalg.pinv(covars)
  lpr = -0.5 * (n_dim * np.log(2 * np.pi) + np.log(linalg.det(covars) + 0.1)
                + np.sum(X * np.dot(X, icv), 1)[:, np.newaxis]
                - 2 * np.dot(np.dot(X, icv), means.T)
                + np.sum(means * np.dot(means, icv), 1))
  return lpr


def _log_multivariate_normal_density_full(X, means, covars, min_covar=1.e-7):
  """Log probability for full covariance matrices.
  """
  n_samples, n_dim = X.shape
  nmix = len(means)
  log_prob = np.empty((n_samples, nmix))
  n_logpi = n_dim * np.log(2 * np.pi)
  for c, (mu, cv) in enumerate(zip(means, covars)):
      try:
          cv_chol = linalg.cholesky(cv)
      except linalg.LinAlgError:
          cv_chol = None

      if cv_chol is None:
          # The model is most probabily stuck in a component with too
          # few observations, we need to reinitialize this components
          cv_chol = linalg.cholesky(cv + min_covar * np.eye(n_dim))

      cv_log_det = n_logpi + 2 * np.sum(np.log(np.diagonal(cv_chol)))
      cv_sol = _dtrsm(CblasLeft, CblasLower, CblasNoTrans, CblasNonUnit, 1.0, cv_chol, (X - mu).T)
      log_prob[:, c] = -0.5 * (np.hypot.reduce(cv_sol, axis=0)**2 + cv_log_det)

  return log_prob

def _covar_mstep_diag(gmm, X, responsibilities, weighted_X_sum, norm, min_covar):
  """Performing the covariance M step for diagonal cases"""
  avg_X2 = np.dot(responsibilities.T, X * X) * norm
  avg_means2 = gmm.means_ ** 2
  avg_X_means = gmm.means_ * weighted_X_sum * norm
  return avg_X2 - 2 * avg_X_means + avg_means2 + min_covar


def _covar_mstep_spherical(gmm, X, responsibilities, weighted_X_sum, norm, min_covar):
  """Performing the covariance M step for spherical cases"""
  cv = _covar_mstep_diag(gmm, X, responsibilities, weighted_X_sum, norm, min_covar)
  return np.tile(cv.mean(axis=1)[:, np.newaxis], (1, cv.shape[1]))


def _covar_mstep_full(gmm, X, responsibilities, weighted_X_sum, norm, min_covar):
  """Performing the covariance M step for full cases"""
  # Eq. 12 from K. Murphy, "Fitting a Conditional Linear Gaussian Distribution"
  n_features = X.shape[1]
  cv = np.empty((gmm.n_components, n_features, n_features))

  if n_features < gmm.n_components:
    # Underflow Errors in doing post * X.T are  not important
    np.seterr(under='ignore')
    responsibilities_norm = 1. / (responsibilities.sum(axis=0) + 10.*EPS).reshape(-1, 1)
    for f in xrange(n_features):
      cv[:, f, f:] = np.dot(responsibilities.T * X[:, f], X[:, f:]) * responsibilities_norm - gmm.means_[:, f].reshape(-1, 1) * gmm.means_[:, f:]
      cv[:, f:, f] = cv[:, f, f:]
    cv += min_covar * np.eye(n_features).reshape((1, n_features, n_features))
  else:
    for c in xrange(gmm.n_components):
      post = responsibilities[:, c]
      # Underflow Errors in doing post * X.T are  not important
      np.seterr(under='ignore')
      avg_cv = np.dot(post * X.T, X) / (post.sum() + 10 * EPS)
      mu = gmm.means_[c][np.newaxis]
      cv[c] = (avg_cv - np.dot(mu.T, mu) + min_covar * np.eye(n_features))

  return cv


def _covar_mstep_tied(gmm, X, responsibilities, weighted_X_sum, norm, min_covar):
  # Eq. 15 from K. Murphy, "Fitting a Conditional Linear Gaussian
  n_features = X.shape[1]
  avg_X2 = np.dot(X.T, X)
  avg_means2 = np.dot(gmm.means_.T, weighted_X_sum)
  return (avg_X2 - avg_means2 + min_covar * np.eye(n_features)) / X.shape[0]


def _validate_covars(covars, covariance_type, n_components):
  """Do basic checks on matrix covariance sizes and values
  """
  if covariance_type == 'spherical':
    if len(covars) != n_components:
      raise ValueError("'spherical' covars have length n_components")
    elif np.any(covars <= 0):
      raise ValueError("'spherical' covars must be non-negative")
  elif covariance_type == 'tied':
    if covars.shape[0] != covars.shape[1]:
      raise ValueError("'tied' covars must have shape (n_dim, n_dim)")
    elif (not np.allclose(covars, covars.T)
          or np.any(linalg.eigvalsh(covars) <= 0)):
      raise ValueError("'tied' covars must be symmetric, "
                       "positive-definite")
  elif covariance_type == 'diag':
    if len(covars.shape) != 2:
      raise ValueError("'diag' covars must have shape"
                       "(n_components, n_dim)")
    elif np.any(covars <= 0):
      raise ValueError("'diag' covars must be non-negative")
  elif covariance_type == 'full':
    if len(covars.shape) != 3:
      raise ValueError("'full' covars must have shape "
                       "(n_components, n_dim, n_dim)")
    elif covars.shape[1] != covars.shape[2]:
      raise ValueError("'full' covars must have shape "
                       "(n_components, n_dim, n_dim)")
    for n, cv in enumerate(covars):
      if (not np.allclose(cv, cv.T)
          or np.any(linalg.eigvalsh(cv) <= 0)):
        raise ValueError("component %d of 'full' covars must be "
                         "symmetric, positive-definite" % n)
  else:
    raise ValueError("covariance_type must be one of " +
                     "'spherical', 'tied', 'diag', 'full'")


def _distribute_covar_matrix_to_match_covariance_type(tied_cv, covariance_type, n_components):
  """Create all the covariance matrices from a given template
  """
  if covariance_type == 'spherical':
    cv = np.tile(tied_cv.mean() * np.ones(tied_cv.shape[1]), (n_components, 1))
  elif covariance_type == 'tied':
    cv = tied_cv
  elif covariance_type == 'diag':
    cv = np.tile(np.diag(tied_cv), (n_components, 1))
  elif covariance_type == 'full':
    cv = np.tile(tied_cv, (n_components, 1, 1))
  else:
    raise ValueError("covariance_type must be one of " +
                     "'spherical', 'tied', 'diag', 'full'")
  return cv
