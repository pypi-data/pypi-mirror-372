#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Sample metrics."""
from __future__ import division

import sys as _sys
import ctypes as _ctypes
import numpy as _numpy

from .. import shared as _shared
from .. import exceptions as _ex
from .. import six as _six

class _API(object):
  def __init__(self):
    self.__library = _shared._library

    self.c_double_p = _ctypes.POINTER(_ctypes.c_double)
    self.c_void_p_p = _ctypes.POINTER(_ctypes.c_void_p)
    self.c_size_t_p = _ctypes.POINTER(_ctypes.c_size_t)

    self.minimax_distance = _ctypes.CFUNCTYPE(_ctypes.c_double, _ctypes.c_size_t, self.c_double_p, self.c_size_t_p, # ret, dim, bounds pointer, bounds strides
                                              _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # points count, pointer and strides
                                              _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # opt. initial sample count, pointer and strides
                                              _ctypes.c_short, self.c_void_p_p)(('GTDoEMeasureMinimaxInterpoint2', self.__library)) # normalize, err. descr.
    self.potential = _ctypes.CFUNCTYPE(_ctypes.c_double, _ctypes.c_size_t, self.c_double_p, self.c_size_t_p, # ret, dim, bounds pointer, bounds strides
                                       _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # points count, pointer and strides
                                       _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # opt. initial sample count, pointer and strides
                                       _ctypes.c_short, self.c_void_p_p)(('GTDoEMeasurePotential2', self.__library)) # normalize, err. descr.
    self.phi_p = _ctypes.CFUNCTYPE(_ctypes.c_double, _ctypes.c_double, _ctypes.c_size_t, self.c_double_p, self.c_size_t_p, # ret, p, dim, bounds pointer, bounds strides
                                   _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # points count, pointer and strides
                                   _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # opt. initial sample count, pointer and strides
                                   _ctypes.c_short, self.c_void_p_p)(('GTDoEMeasurePhiP2', self.__library)) # normalize, err. descr.
    self.discrepancy = _ctypes.CFUNCTYPE(_ctypes.c_double, _ctypes.c_size_t, self.c_double_p, self.c_size_t_p, # ret, dim, bounds pointer, bounds strides
                                       _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # points count, pointer and strides
                                       _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # opt. initial sample count, pointer and strides
                                       self.c_void_p_p)(('GTDoEMeasureDiscrepancy2', self.__library)) # normalize, err. descr.

    self.explore_discrepancy = _ctypes.CFUNCTYPE(_ctypes.c_double, _ctypes.c_size_t, self.c_double_p, self.c_size_t_p, # ret, dim, bounds pointer, bounds strides
                                                 _ctypes.c_size_t,  self.c_double_p, self.c_size_t_p, # points count, pointer and strides
                                                 _ctypes.c_char_p, self.c_size_t_p, # mode, opt. num. of points in result
                                                 self.c_double_p, self.c_size_t_p, # opt. result bounds pointer, opt. result bounds strides
                                                 _ctypes.POINTER(_ctypes.c_short), self.c_void_p_p)(('GTDoEExploreDiscrepancy', self.__library)) # opt. "include points on bounds", err. descr.


_api = _API()

def __preprocess_input(bounds, points):
  if len(points) < 2:
    raise ValueError('Not enough points to calculate measure!')
  size_x = _shared.get_size(points[0])

  bounds = _shared.as_matrix(bounds, shape=(2, None), name="design space bounds")
  points = _shared.as_matrix(points, shape=(None, size_x), name="input points")

  if not _numpy.isfinite(bounds).all():
    raise _ex.NanInfError('Incorrect (NaN or Inf or denormalized zero) value is found in the design space bounds.')

  if not _numpy.isfinite(points).all():
    raise _ex.NanInfError('Incorrect (NaN or Inf or denormalized zero) value is found in the input points.')

  if bounds.shape[1] != size_x:
    if bounds.shape[1] == 1:
      bounds = _numpy.repeat(bounds, size_x, axis=1)
    else:
      raise ValueError('Design space bounds have invalid length: %d (%d expected)' % (bounds.shape[1], size_x))

  if _numpy.greater(bounds[0], bounds[1]).any():
    raise ValueError('Some of the lower design space bounds are greater than the upper bounds: %s > %s.' % (bounds[0], bounds[1]))

  outliers_count = _numpy.count_nonzero(_numpy.less(points, bounds[0].reshape(1, -1)))\
                 + _numpy.count_nonzero(_numpy.greater(points, bounds[1].reshape(1, -1)))
  if outliers_count:
    raise ValueError('%d of %d points are out of the design space bounds.' % (outliers_count, points.shape[0]))

  return bounds, points

def minimax_distance(bounds, points, normalize=True, backend=_api):
  r"""Evaluate the minimax interpoint distance.

  :param bounds: design space bounds (lower, upper)
  :type bounds: ``tuple(list[float], list[float])``
  :param points: sample
  :type points: :term:`array-like`, 2D
  :param normalize: indicates coordinate transform into a unit hypercube
  :type normalize: ``bool``
  :return: minimax distance in the original or normalized space
  :rtype: ``float``
  :raise: :exc:`ValueError` if *points* contain a point out of *bounds*

  Evaluates the minimax interpoint distance `d = \max _i \min _j d_{ij}`
  (the maximum distance to the nearest neighbor in the array),
  where `d_{ij}` is the Euclidean distance between two points.

  If :arg:`normalize` is ``True`` (default), the design space (point coordinates and bounds)
  is normalized before calculation:

  * Normalization applies a linear coordinate transform,
    so that all points are contained into a unit hypercube.
  * Return value becomes the minimax distance in this normalized space (in the unit hypercube),
    not in the original design space (the bounding box specified by :arg:`bounds`).

  Note that the bounds should be equal to the bounds of the DoE generator that was used to obtain the *points* set
  (see *bounds* in :meth:`~da.p7core.gtdoe.Generator.generate()`). Setting different bounds makes the normalization
  incorrect; this issue can not be resolved automatically, so this function only checks that all points are within bounds.

  """
  bounds, points = __preprocess_input(bounds, points)
  return _minimax_distance(bounds, points, normalize=normalize, initial_points=None, backend=backend)

def phi_p(bounds, points, p=50, normalize=True, backend=_api):
  r"""Evaluate the `\phi_p` metric.

  :param bounds: design space bounds (lower, upper)
  :type bounds: ``tuple(list[float], list[float])``
  :param points: sample
  :type points: :term:`array-like`, 2D
  :param p: metric parameter
  :type p: ``int``, ``long``, or ``float``
  :param normalize: indicates coordinate transform into a unit hypercube
  :type normalize: ``bool``
  :return: `\phi_p` value in the original or normalized space
  :rtype: ``float``
  :raise: :exc:`ValueError` if the *points* array contains a point out of *bounds*

  Evaluates the `\phi_p = \sqrt[p]{\sum_{i=1}^N \sum_{j=1}^{i-1} \frac{1}{d_{ij}^p}}` metric,
  where `d_{ij}` is the Euclidean distance between two points.

  If :arg:`normalize` is ``True`` (default), the design space (point coordinates and bounds)
  is normalized before calculation:

  * Normalization applies a linear coordinate transform,
    so that all points are contained into a unit hypercube.
  * Return value becomes the metric value in this normalized space (in the unit hypercube),
    not in the original design space (the bounding box specified by :arg:`bounds`).

  Note that the bounds should be equal to the bounds of the DoE generator that was used to obtain the *points* set
  (see *bounds* in :meth:`~da.p7core.gtdoe.Generator.generate()`). Setting different bounds makes the normalization
  incorrect; this issue can not be resolved automatically, so this function only checks if all points are within bounds.
  """
  bounds, points = __preprocess_input(bounds, points)
  return _phi_p(bounds, points, p=p, normalize=normalize, initial_points=None, backend=backend)

def potential(bounds, points, normalize=True, backend=_api):
  r"""Evaluate the potential metric.

  :param bounds: design space bounds (lower, upper)
  :type bounds: ``tuple(list[float], list[float])``
  :param points: point set
  :type points: :term:`array-like`
  :param normalize: indicates coordinate transform into a unit hypercube
  :type normalize: ``bool``
  :return: potential value in the original or normalized space
  :rtype: ``float``
  :raise: :exc:`ValueError` if the *points* array contains a point out of *bounds*

  Evaluates the `U = \sum_{i=1}^N \sum_{j=1}^{i-1} \frac{1}{d_{ij}^2}` metric,
  where `d_{ij}` is the Euclidean distance between two points.

  If :arg:`normalize` is ``True`` (default), the design space (point coordinates and bounds)
  is normalized before calculation:

  * Normalization applies a linear coordinate transform,
    so that all points are contained into a unit hypercube.
  * Return value becomes the metric value in this normalized space (in the unit hypercube),
    not in the original design space (the bounding box specified by :arg:`bounds`).

  Note that the bounds should be equal to the bounds of the DoE generator that was used to obtain the *points* set
  (see *bounds* in :meth:`~da.p7core.gtdoe.Generator.generate()`). Setting different bounds makes the normalization
  incorrect; this issue can not be resolved automatically, so this function only checks if all points are within bounds.
  """
  bounds, points = __preprocess_input(bounds, points)
  return _potential(bounds, points, normalize=normalize, initial_points=None, backend=backend)

def discrepancy(bounds, points, backend=_api):
  """Evaluate the discrepancy metric.

  :param bounds: design space bounds (lower, upper)
  :type bounds: ``tuple(list[float], list[float])``
  :param points: point set
  :type points: :term:`array-like`
  :return: normalized discrepancy value
  :rtype: ``float``
  :raise: :exc:`ValueError` if the *points* array contains a point out of *bounds*

  .. versionadded:: 6.18

  Evaluates the discrepancy metric (see section :ref:`ug_gtdoe_general_properties_uniformity`).

  The design space (both point coordinates and bounds) is normalized before calculation:
  the function applies a linear transform so that all points are contained into a unit hypercube.

  Note that the bounds should be equal to the bounds of the DoE generator that was used to obtain the *points* set
  (see *bounds* in :meth:`~da.p7core.gtdoe.Generator.generate()`). Setting different bounds makes the normalization
  incorrect; this issue can not be resolved automatically, so this function only checks if all points are within bounds.

  .. note::

     Return value is the discrepancy metric in the normalized space,
     not in the original design space.

  """

  bounds, points = __preprocess_input(bounds, points)
  return _discrepancy(bounds, points, initial_points=None, backend=backend)


def _minimax_distance(bounds, points, normalize=True, initial_points=None, backend=_api):
  errdesc = _ctypes.c_void_p()
  value = backend.minimax_distance( points.shape[1], bounds.ctypes.data_as(backend.c_double_p), bounds.ctypes.strides_as(_ctypes.c_size_t),
                                    points.shape[0], points.ctypes.data_as(backend.c_double_p), points.ctypes.strides_as(_ctypes.c_size_t),
                                    0 if initial_points is None else initial_points.shape[0],
                                    backend.c_double_p() if initial_points is None else initial_points.ctypes.data_as(backend.c_double_p),
                                    backend.c_size_t_p() if initial_points is None else initial_points.ctypes.strides_as(_ctypes.c_size_t),
                                    (1 if normalize else 0), _ctypes.byref(errdesc))
  _shared._raise_on_error(not _numpy.isnan(value), "Failed to evaluate minimax interpoint distance.", errdesc)
  return value

def _phi_p(bounds, points, p=50, normalize=True, initial_points=None, backend=_api):
  errdesc = _ctypes.c_void_p()
  value = backend.phi_p(float(p), points.shape[1], bounds.ctypes.data_as(backend.c_double_p), bounds.ctypes.strides_as(_ctypes.c_size_t),
                        points.shape[0], points.ctypes.data_as(backend.c_double_p), points.ctypes.strides_as(_ctypes.c_size_t),
                        0 if initial_points is None else initial_points.shape[0],
                        backend.c_double_p() if initial_points is None else initial_points.ctypes.data_as(backend.c_double_p),
                        backend.c_size_t_p() if initial_points is None else initial_points.ctypes.strides_as(_ctypes.c_size_t),
                        (1 if normalize else 0), _ctypes.byref(errdesc))
  _shared._raise_on_error(not _numpy.isnan(value), "Failed to evaluate minimax interpoint distance.", errdesc)
  return value

def _potential(bounds, points, normalize=True, initial_points=None, backend=_api):
  errdesc = _ctypes.c_void_p()
  value = backend.potential(points.shape[1], bounds.ctypes.data_as(backend.c_double_p), bounds.ctypes.strides_as(_ctypes.c_size_t),
                            points.shape[0], points.ctypes.data_as(backend.c_double_p), points.ctypes.strides_as(_ctypes.c_size_t),
                            0 if initial_points is None else initial_points.shape[0],
                            backend.c_double_p() if initial_points is None else initial_points.ctypes.data_as(backend.c_double_p),
                            backend.c_size_t_p() if initial_points is None else initial_points.ctypes.strides_as(_ctypes.c_size_t),
                            (1 if normalize else 0), _ctypes.byref(errdesc))
  _shared._raise_on_error(not _numpy.isnan(value), "Failed to evaluate minimax interpoint distance.", errdesc)
  return value

def _discrepancy(bounds, points, initial_points=None, backend=_api):
  errdesc = _ctypes.c_void_p()
  value = backend.discrepancy(points.shape[1], bounds.ctypes.data_as(backend.c_double_p), bounds.ctypes.strides_as(_ctypes.c_size_t),
                              points.shape[0], points.ctypes.data_as(backend.c_double_p), points.ctypes.strides_as(_ctypes.c_size_t),
                              0 if initial_points is None else initial_points.shape[0],
                              backend.c_double_p() if initial_points is None else initial_points.ctypes.data_as(backend.c_double_p),
                              backend.c_size_t_p() if initial_points is None else initial_points.ctypes.strides_as(_ctypes.c_size_t),
                              _ctypes.byref(errdesc))
  _shared._raise_on_error(not _numpy.isnan(value), "Failed to evaluate sample discrepancy.", errdesc)
  return value

def _explore_discrepancy(bounds, points, mode=None, backend=_api):
  errdesc = _ctypes.c_void_p()
  bounds, points = __preprocess_input(bounds, points)
  result_bounds = bounds.copy()
  result_npoints = _ctypes.c_size_t()
  result_incbounds = _ctypes.c_short()

  try:
    cmode = _ctypes.c_char_p("normal".encode("utf8") if mode is None else \
                             mode.encode("utf8") if isinstance(mode, _six.string_types) else \
                             mode)
  except:
    _shared.reraise(_ex.InvalidOptionNameError, ("Invalid discrepancy mode is given: %s" % mode), _sys.exc_info()[2])


  value = backend.explore_discrepancy(points.shape[1], bounds.ctypes.data_as(backend.c_double_p), bounds.ctypes.strides_as(_ctypes.c_size_t),
                                      points.shape[0], points.ctypes.data_as(backend.c_double_p), points.ctypes.strides_as(_ctypes.c_size_t),
                                      cmode, _ctypes.byref(result_npoints), result_bounds.ctypes.data_as(backend.c_double_p),
                                      result_bounds.ctypes.strides_as(_ctypes.c_size_t), _ctypes.byref(result_incbounds), _ctypes.byref(errdesc))
  _shared._raise_on_error(not _numpy.isnan(value), "Failed to explore sample discrepancy.", errdesc)
  return value, result_npoints.value, result_bounds, result_incbounds.value

