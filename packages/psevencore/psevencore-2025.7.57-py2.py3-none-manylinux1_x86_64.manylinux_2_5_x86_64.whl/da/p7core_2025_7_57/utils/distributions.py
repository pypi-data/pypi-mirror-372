#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Utility functions for statistical distributions"""
from __future__ import division

from .. import shared as _shared
from .. import exceptions as _ex

import ctypes

class _Distribution:
  def __init__(self, instance, name, **kwargs):
    """Constructor."""
    assert(_shared._library)
    assert(instance)
    self.__library = _shared._library
    self.__instance = instance
    self.name = name

    def _assignPropertyIfDefined(object, property, function):
      value = float(ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p)((function, object.__library))(object.__instance))
      if value == value:
        setattr(object, property, value)

    _assignPropertyIfDefined(self, 'mean',     'GTUtilsDistributionMean')
    _assignPropertyIfDefined(self, 'median',   'GTUtilsDistributionMedian')
    _assignPropertyIfDefined(self, 'mode',     'GTUtilsDistributionMode')
    _assignPropertyIfDefined(self, 'std',      'GTUtilsDistributionStandardDeviation')
    _assignPropertyIfDefined(self, 'var',      'GTUtilsDistributionVariance')
    _assignPropertyIfDefined(self, 'skewness', 'GTUtilsDistributionSkewness')
    _assignPropertyIfDefined(self, 'kurtosis', 'GTUtilsDistributionKurtosis')

    for name in kwargs:
      setattr(self, name, kwargs[name])

  def __del__(self):
    """Destructor."""
    ctypes.CFUNCTYPE(ctypes.c_short, ctypes.c_void_p)(('GTUtilsDeleteDistribution', self.__library))(self.__instance)

  def __str__(self):
    return self.name

  def cdf(self, x, complement=False):
    """ Calculates Cumulative Distribution Function or its complement.

    The Cumulative Distribution Function is the probability that the variable takes a value less than or equal to x.
    It is equivalent to the integral from -infinity to x of the Probability Density Function.
    The complement of the Cumulative Distribution Function is the probability that the variable takes a value greater than x.
    It is equivalent to the integral from x to infinity of the Probability Density Function,
    or 1 minus the Cumulative Distribution Function of x.

    :param x: value to calculate CDF
    :type x: float
    :param complement: False to calculate CDF, or True to calculate complement of the CDF
    :type complement: boolean

    """
    return float(ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p, ctypes.c_double, ctypes.c_short)(('GTUtilsCalculateCDF', self.__library))(self.__instance, x, complement))

  def quantile(self, p, complement=False):
    """ Calculates quantile of the probability p or quantile of the complement of the probability p.

    The quantile of the probability p is a value x such that CDF(x) equals to p.
    The quantile of the complement of the probability p is a value x such that CDF(x) equals to 1-p.

    :param p: probability to calculate quantile
    :type p: float
    :param complement: False to calculate quantile of p, or True to calculate complement of the quantile of p
    :type complement: boolean

    """
    return float(ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p, ctypes.c_double, ctypes.c_short)(('GTUtilsDistributionQuantile', self.__library))(self.__instance, p, complement))

  def pdf(self, x):
    """ Calculates Probability Density Function.

    For a continuous function, the probability density function (pdf) returns the probability
    that the variate has the value x. Since for continuous distributions the probability at
    a single point is actually zero, the probability is better expressed as the integral of
    the pdf between two points: see the Cumulative Distribution Function.
    For a discrete distribution, the pdf is the probability that the variate takes the value x.

    :param x: value to calculate PDF
    :type x: float

    """
    return float(ctypes.CFUNCTYPE(ctypes.c_double, ctypes.c_void_p, ctypes.c_double)(('GTUtilsCalculatePDF', self.__library))(self.__instance, x))

def _chi2(df):
  """Creates Chi-squared distribution with df degrees of freedom

  See http://en.wikipedia.org/wiki/Chi-squared_distribution for details.

  :param df: number of chi-squared degrees of freedom, requires df > 0.
  :type df: ``float``

  Example::

    distr = chi2(3)
    print "Name of the distribution is %s" % distr.name
    print "Distribution has %g degrees of freedom" % distr.df
    print "Mean of the distribution is %g" % distr.mean
    print "Median of the distribution is %g" % distr.median
    print "Mode of the distribution is %g" % distr.mode
    p = 0.98
    q = 1. - p
    x = distr.quantile(p)
    print "p=%g, q=%g, quantile(p)=%g" % (p, q, x)
    print "distr.cdf(x, complement=False)=%.15g" % distr.cdf(x, complement=False)
    print "distr.cdf(x, complement=True)=%.15g" % distr.cdf(x, complement=True)
    print "distr.quantile(p, complement=False)=%.15g" % distr.quantile(p, complement=False)
    print "distr.quantile(q, complement=True)=%.15g" % distr.quantile(q, complement=True)
    print "abs(distr.cdf(x, complement=True) - q)=%.15g" % abs(distr.cdf(x, complement=True) - q)
    assert((distr.cdf(x, False) + distr.cdf(x, True)) == 1.)
    assert(abs(distr.cdf(x) - p) < 2.e-16)
    assert(distr.quantile(p, complement=False) == distr.quantile(q, complement=True))
    assert(abs(distr.cdf(x, complement=True) - q) < 2.e-16)

  """
  df = float(df)
  if df <= 0.:
    raise _ex.GTException('Chi-squared distribution should have positive number of degrees of freedom')
  name = "Chi-squred distribution with %g degrees of freedom" % df
  instance = ctypes.c_void_p(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_double)(('GTUtilsCreateChiSquaredDistribution', _shared._library))(df))
  if not instance:
    raise _ex.GTException("Can't create %s" % name)
  return _Distribution(instance, name, df=df)

def _chi2inv(df, scale=None):
  """Creates a scaled inverse Chi-Squared distribution

  See http://en.wikipedia.org/wiki/Scaled-inverse-chi-squared_distribution for details.

  :param df: number of chi-squared degrees of freedom, requires df > 0.
  :type df: ``float``
  :param scale: scaling parameter. Default is 1./df
  :type scale: ``float``

  Example::

    distr = chi2inv(3., 1./3.)
    print "Name of the distribution is %s" % distr.name
    print "Chi-squared distribution has %g degrees of freedom" % distr.df
    print "Scaling parameter is %g" % distr.scale
    print "Scaling parameter is %g%" % distr.scale
    print "Mean of the distribution is %g" % distr.mean
    print "Median of the distribution is %g" % distr.median
    print "Mode of the distribution is %g" % distr.mode
    p = 0.98
    q = 1. - p
    x = distr.quantile(p)
    print "p=%g, q=%g, quantile(p)=%g" % (p, q, x)
    print "distr.cdf(x, complement=False)=%.15g" % distr.cdf(x, complement=False)
    print "distr.cdf(x, complement=True)=%.15g" % distr.cdf(x, complement=True)
    print "distr.quantile(p, complement=False)=%.15g" % distr.quantile(p, complement=False)
    print "distr.quantile(q, complement=True)=%.15g" % distr.quantile(q, complement=True)
    print "abs(distr.cdf(x, complement=True) - q)=%.15g" % abs(distr.cdf(x, complement=True) - q)
    assert((distr.cdf(x, False) + distr.cdf(x, True)) == 1.)
    assert(abs(distr.cdf(x) - p) < 2.e-16)
    assert(distr.quantile(p, complement=False) == distr.quantile(q, complement=True))
    assert(abs(distr.cdf(x, complement=True) - q) < 2.e-16)
    assert(chi2inv(3).scale == chi2inv(3, 1./3.).scale)

  """
  df = float(df)
  if df <= 0.:
    raise _ex.GTException('Chi-squared distribution should have positive number of degrees of freedom')
  scale = 1./df if scale is None else float(scale)
  name = "Scaled inverse Chi-squred distribution. Chi-squared degrees of freedom is %g, scaling parameter is %g." % (df, scale)
  instance = ctypes.c_void_p(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_double, ctypes.c_double)(('GTUtilsCreateInverseChiSquaredDistribution', _shared._library))(df, scale))
  if not instance:
    raise _ex.GTException("Can't create %s" % name)
  return _Distribution(instance, name, df=df, scale=scale)

def _tdist(df):
  """Creates Student's t-distribution with df degrees of freedom

  See http://en.wikipedia.org/wiki/Student%27s_t-distribution for details.

  Example::

    distr = tdist(3)
    print "Name of the distribution is %s" % distr.name
    print "Distribution has %g degrees of freedom" % distr.df
    print "Mean of the distribution is %g" % distr.mean
    print "Median of the distribution is %g" % distr.median
    print "Mode of the distribution is %g" % distr.mode
    p = 0.98
    q = 1. - p
    x = distr.quantile(p)
    print "p=%g, q=%g, quantile(p)=%g" % (p, q, x)
    print "distr.cdf(x, complement=False)=%.15g" % distr.cdf(x, complement=False)
    print "distr.cdf(x, complement=True)=%.15g" % distr.cdf(x, complement=True)
    print "distr.quantile(p, complement=False)=%.15g" % distr.quantile(p, complement=False)
    print "distr.quantile(q, complement=True)=%.15g" % distr.quantile(q, complement=True)
    print "abs(distr.cdf(x, complement=True) - q)=%.15g" % abs(distr.cdf(x, complement=True) - q)
    assert((distr.cdf(x, False) + distr.cdf(x, True)) == 1.)
    assert(abs(distr.cdf(x) - p) < 2.e-16)
    assert(distr.quantile(p, complement=False) == distr.quantile(q, complement=True))
    assert(abs(distr.cdf(x, complement=True) - q) < 2.e-16)

  """
  df = float(df)
  if df <= 0.:
    raise _ex.GTException("Student's t-distribution should have positive number of degrees of freedom")
  name = "Student\'s t-distribution with %g degrees of freedom" % df
  instance = ctypes.c_void_p(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_double)(('GTUtilsCreateStudentsTDistribution', _shared._library))(df))
  if not instance:
    raise _ex.GTException("Can't create %s" % name)
  return _Distribution(instance, name, df=df)

def _fdist(df1, df2):
  """Creates a Fisher F-distribution with numerator degrees of freedom df1 and denominator degrees of freedom df2.

  See http://en.wikipedia.org/wiki/F-distribution for details.

  :param df1: number of numerator degrees of freedom, requires df1 > 0.
  :type df1: ``float``
  :param df2: number of denomenator degrees of freedom, requires df2 > 0.
  :type df2: ``float``

  Example::

    distr = fdist(3,4)
    print "Name of the distribution is %s" % distr.name
    print "Numerator degrees of freedom is %g" % distr.df1
    print "Denomenator degrees of freedom is %g" % distr.df2
    print "Mean of the distribution is %g" % distr.mean
    print "Median of the distribution is %g" % distr.median
    print "Mode of the distribution is %g" % distr.mode
    p = 0.98
    q = 1. - p
    x = distr.quantile(p)
    print "p=%g, q=%g, quantile(p)=%g" % (p, q, x)
    print "distr.cdf(x, complement=False)=%.15g" % distr.cdf(x, complement=False)
    print "distr.cdf(x, complement=True)=%.15g" % distr.cdf(x, complement=True)
    print "distr.quantile(p, complement=False)=%.15g" % distr.quantile(p, complement=False)
    print "distr.quantile(q, complement=True)=%.15g" % distr.quantile(q, complement=True)
    print "abs(distr.cdf(x, complement=True) - q)=%.15g" % abs(distr.cdf(x, complement=True) - q)
    assert((distr.cdf(x, False) + distr.cdf(x, True)) == 1.)
    assert(abs(distr.cdf(x) - p) < 2.e-16)
    assert(distr.quantile(p, complement=False) == distr.quantile(q, complement=True))
    assert(abs(distr.cdf(x, complement=True) - q) < 2.e-16)

  """
  df1 = float(df1)
  if df1 <= 0.:
    raise _ex.GTException('Fisher F-distribution should have positive number of numerator degrees of freedom')
  df2 = float(df2)
  if df2 <= 0.:
    raise _ex.GTException('Fisher F-distribution should have positive number of denomenator degrees of freedom')
  name = "Fisher F-distribution with numerator degrees of freedom %g and denominator degrees of freedom %g" % (df1, df2)
  instance = ctypes.c_void_p(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_double, ctypes.c_double)(('GTUtilsCreateFisherFDistribution', _shared._library))(df1, df2))
  if not instance:
    raise _ex.GTException("Can't create %s" % name)
  return _Distribution(instance, name, df1=df1, df2=df2)

def _normal(mean = 0., sd = 1.):
  """Constructs a normal (Gaussian) distribution with a given mean and standard deviation.

  See http://en.wikipedia.org/wiki/Normal_distribution for details.

  :param mean: mean value of the distribution.
  :type mean: ``float``
  :param sd: standard deviation of the distribution, requires sd > 0.
  :type sd: ``float``

  Example::

    distr = normal(0., 1.)
    print "Name of the distribution is %s" % distr.name
    print "Numerator degrees of freedom is %g" % distr.df1
    print "Denomenator degrees of freedom is %g" % distr.df2
    print "Mean of the distribution is %g" % distr.mean
    print "Median of the distribution is %g" % distr.median
    print "Mode of the distribution is %g" % distr.mode
    p = 0.98
    q = 1. - p
    x = distr.quantile(p)
    print "p=%g, q=%g, quantile(p)=%g" % (p, q, x)
    print "distr.cdf(x, complement=False)=%.15g" % distr.cdf(x, complement=False)
    print "distr.cdf(x, complement=True)=%.15g" % distr.cdf(x, complement=True)
    print "distr.quantile(p, complement=False)=%.15g" % distr.quantile(p, complement=False)
    print "distr.quantile(q, complement=True)=%.15g" % distr.quantile(q, complement=True)
    print "abs(distr.cdf(x, complement=True) - q)=%.15g" % abs(distr.cdf(x, complement=True) - q)
    assert((distr.cdf(x, False) + distr.cdf(x, True)) == 1.)
    assert(abs(distr.cdf(x) - p) < 2.e-16)
    assert(distr.quantile(p, complement=False) == distr.quantile(q, complement=True))
    assert(abs(distr.cdf(x, complement=True) - q) < 2.e-16)

  """
  mean = float(mean)
  sd = float(sd)
  if sd <= 0.:
    raise _ex.GTException('Normal distribution should have positive standard deviation')
  name = "Normal distribution with mean %g and standard deviation %g" % (mean, sd)
  instance = ctypes.c_void_p(ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_double, ctypes.c_double)(('GTUtilsCreateNormalDistribution', _shared._library))(mean, sd))
  if not instance:
    raise _ex.GTException("Can't create %s" % name)
  return _Distribution(instance, name)
