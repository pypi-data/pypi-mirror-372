#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Utility functions for linear algebra"""
from __future__ import division

__all__ = ['CblasRowMajor','CblasColMajor','CblasNoTrans',
           'CblasTrans','CblasUpper','CblasLower','CblasNonUnit',
           'CblasUnit','CblasLeft','CblasRight','_dtrsv','_dtrsm']

from .. import shared as _shared
from .. import exceptions as _ex
from ..six.moves import reduce

from ctypes import CFUNCTYPE, POINTER, c_short, c_int, c_double
from numpy import array, float64, ndarray

CblasRowMajor = 101
CblasColMajor = 102

CblasNoTrans  = 111
CblasTrans    = 112

CblasUpper    = 121
CblasLower    = 122

CblasNonUnit  = 131
CblasUnit     = 132

CblasLeft     = 141
CblasRight    = 142

_dtrsvRoutine = CFUNCTYPE(c_short, c_int, c_int, c_int,  c_int, c_int, POINTER(c_double), c_int, POINTER(c_double), c_int)(('GTUtilsDTRSV', _shared._library))
_dtrsmRoutine = CFUNCTYPE(c_short, c_int, c_int, c_int,  c_int, c_int, c_int, c_int, c_double, POINTER(c_double), c_int, POINTER(c_double), c_int)(('GTUtilsDTRSM', _shared._library))

class _CblasMatrix:
  def __init__(self, A):
    if type(A) != ndarray or A.dtype != float64:
      self.origin = array(A, dtype=float64, order='C')
    else:
      self.origin = A

    if self.origin.ndim != 2:
      raise _ex.GTException('The %s-dimensional array given is not a m-by-n dimensional matrix' % self.origin.shape)

    if self.origin.strides[0] != self.origin.itemsize \
       and self.origin.strides[1] != self.origin.itemsize:
      # self.origin isn't C or Fortran-ordered array
      self.origin = array(self.origin, dtype=float64, order='C')
      assert self.origin.strides[1] == self.origin.itemsize, "The array given can't be converted to a C-ordered matrix"

    self.m = self.origin.shape[0]
    self.n = self.origin.shape[1]
    self.ptr = self.origin.ctypes.data_as(POINTER(c_double))
    self.order = CblasRowMajor if self.origin.strides[1] == self.origin.itemsize else CblasColMajor
    self.ld = self.origin.strides[0 if self.order == CblasRowMajor else 1] // self.origin.itemsize

class _CblasVector:
  def __init__(self, x):
    if type(x) != ndarray or x.dtype != float64:
      self.origin = array(x, dtype=float64, order='C')
    else:
      self.origin = x

    if self.origin.ndim != 1:
      n = max(self.origin.shape)
      if reduce(lambda x, y: x * y, self.origin.shape) == n:
        # all dimensions except one are equal to 1 - it's a vector, actually
        self.origin = self.origin.reshape((n))
      else:
        raise _ex.GTException("The %s-dimensional array can't be converted to a n-dimensional matrix" % self.origin.shape)

    self.n = self.origin.shape[0]
    self.ptr = self.origin.ctypes.data_as(POINTER(c_double))
    self.inc = self.origin.strides[0] // self.origin.itemsize

def _dtrsv(uplo, trans, diag, A, x):
  """ Solves a system of linear equations whose coefficients are in a triangular matrix.

  This routine solves one of the systems of equations: A*x = b, or A'*x = b, where:
  - b and x are n-element vectors;
  - A is an n-by-n unit, or non-unit, upper or lower triangular matrix.
  The routine does not test for near-singularity.

  :param uplo: - specifies whether the matrix A is upper or lower triangular.
                 Valid values are CblasUpper or CblasLower.
  :param trans: - specifies the systems of equations: if trans=CblasNoTrans, then A*x=b;
                  if trans=CblasTrans, then A'x=b.
  :param diag: - specifies whether the matrix A is unit triangular.
                 Valid values are CblasUnit or CblasNonUnit.
  :param A: - Before entry with uplo=CblasUpper, the leading n-by-n upper triangular part
              of the array A must contain the upper triangular matrix and the strictly
              lower triangular part of A is not referenced. Before entry with uplo=CblasLower,
              the leading n-by-n lower triangular part of the array A must contain the lower
              triangular matrix and the strictly upper triangular part of a is not referenced.
              When diag=CblasUnit, the diagonal elements of a are not referenced either,
              but are assumed to be unity.
  :param x: - On entry, the array x must contain the n-element right-hand side vector b.
              System of equations will be solved in-place if possible.
  :return: - Vector containing solution of the system of equations. This can be the same object x
             that was passed as the function argument or it can be a new NumPy vector.

  Example:

  import numpy as np
  from da.p7core.utils.linalg import *

  A = np.array([[2,1],[1,2]])
  L = np.linalg.cholesky(A)
  b = np.array([5,6])

  print 'A =', A
  print 'L =', L
  print 'b =', b

  print "solving L*L'*x=b ..."

  # b and x will be different objects because b.dtype.name != 'float64'
  x = dtrsv(CblasLower, CblasNoTrans, CblasNonUnit, L, b.copy())
  x = dtrsv(CblasLower, CblasTrans,   CblasNonUnit, L, x)

  print 'x =', x
  print 'A*x-b = ', (np.dot(A,x)-b)

  print "solving U'*U*x=b ..."
  x = np.array(b, dtype='float64', order='C')
  # now x is a valid array containing right-hand-side vector b
  # so the system of linear equations will be solved in-place
  dtrsv(CblasUpper, CblasTrans,   CblasNonUnit, L.T, x)
  dtrsv(CblasUpper, CblasNoTrans, CblasNonUnit, L.T, x)

  print 'x =', x
  print 'A*x-b = ', (np.dot(A,x)-b)

  """
  if uplo not in (CblasUpper, CblasLower):
    raise _ex.GTException('Invalid uplo marker')

  if trans not in (CblasNoTrans, CblasTrans):
    raise _ex.GTException('Invalid transpose marker')

  if diag not in (CblasNonUnit, CblasUnit):
    raise _ex.GTException('Invalid unit diagonal marker')

  cblasA = _CblasMatrix(A)
  cblasX = _CblasVector(x)

  if cblasA.m != cblasA.n:
    raise _ex.GTException('The array A is not a square matrix')

  if cblasA.m != cblasX.n:
    raise _ex.GTException('The %d-by-%d dimensional matrix A does not conform %d-dimensional vector x' % (cblasA.m, cblasA.n, cblasX.n))

  errorCode = _dtrsvRoutine(cblasA.order, uplo, trans, diag, cblasA.n, cblasA.ptr, cblasA.ld, cblasX.ptr, cblasX.inc)

  if 0 > errorCode:
    raise _ex.GTException('The triangular matrix given is singular')
  elif 0 < errorCode:
    parametersList = ('C/Fortran storage scheme marker',
                      'upper/lower triangle marker',
                      'transpose marker',
                      'diagonal type marker',
                      'matrix order',
                      'pointer to matrix A',
                      'leading dimension of matrix A'
                      'pointer to vector x'
                      'distance between elements of vector x')
    errorMessage = parametersList[errorCode-1] if errorCode <= len(parametersList) else 'can not detect parameter'
    raise _ex.GTException('Invalid parameter #%d: %s' % (errorCode, errorMessage))

  return cblasX.origin

def _dtrsm(side, uplo, transA, diag, alpha, A, B):
  """ Solve one of the following matrix equations: op(A)*X = alpha*B, or X*op(A) = alpha*B,
      where alpha is a scalar, B and X are m-by-n dimensional matrices, A is an unit,
      or non-unit, upper or lower triangular matrix.

  :param side: - specifies whether op(A) appears on the left or right of X in the equation:
                       if side=CblasLeft, then op(A)*X = alpha*B;
                       if side=CblasRight, then X*op(A) = alpha*B.
  :param uplo: - specifies whether the matrix A is upper or lower triangular.
                 Valid values are CblasUpper or CblasLower.
  :param transA: - specifies the form of op(A) used in the matrix multiplication:
                  * if transA==CblasNoTrans, then op(A)=A;
                  * if transA==CblasTrans, then op(A)=A'.
  :param diag: - specifies whether the matrix A is unit triangular.
                 Valid values are CblasUnit or CblasNonUnit.
  :param alpha: - the scalar alpha. When alpha is zero, then matrix A is not referenced.
  :param A: - k-by-k dimensional matrix, where k is m when side=CblasLeft and is n when side=CblasRight
              Before entry with uplo=CblasUpper, the leading k-by-k upper triangular part
              of the array A must contain the upper triangular matrix and the strictly
              lower triangular part of A is not referenced. Before entry with uplo=CblasLower,
              the leading k-by-k lower triangular part of the array A must contain the lower
              triangular matrix and the strictly upper triangular part of A is not referenced.
              When diag=CblasUnit, the diagonal elements of A are not referenced either,
              but are assumed to be unity.
  :param B: - On entry, the m-by-n part of the array B must contain the right-hand side matrix B.
              System of equations will be solved in-place if possible.
  :return: - Matrix containing solution of the system of equations. This can be the same object B
             that was passed as the function argument or it can be a new NumPy array.

  Example:

  import numpy as np
  from da.p7core.utils.linalg import *

  A = np.array([[2,1],[1,2]])
  L = np.linalg.cholesky(A)
  B = np.array([[5,6,7],[8,9,10]])

  print "A =", A
  print "L =", L
  print "B =", B

  print "solving A*X=B..."

  # B and X will be different objects because B.dtype.name != 'float64'
  X = dtrsm(CblasLeft, CblasLower, CblasNoTrans, CblasNonUnit, 1., L, B)
  X = dtrsm(CblasLeft, CblasLower, CblasTrans,   CblasNonUnit, 1., L, X)
  print "X =", X
  print "A*X-B = ", (np.dot(A,X)-B)

  print "solving X*A=0.5*B'..."
  X = np.array(B.T, dtype='float64', order='F')
  # now X is a valid array containing the right-hand-side matrix B,
  # so the system of the linear equations will be solved in-place
  dtrsm(CblasRight, CblasLower, CblasTrans,   CblasNonUnit, 0.5, L, X)
  dtrsm(CblasRight, CblasLower, CblasNoTrans, CblasNonUnit, 1.0, L, X)
  print "X =", X
  print "X*A-0.5*B' = ", (np.dot(X,A)-B.T*0.5)

  """
  if side not in (CblasLeft, CblasRight):
    raise _ex.GTException('Invalid matrix A side marker')

  if uplo not in (CblasUpper, CblasLower):
    raise _ex.GTException('Invalid uplo marker')

  if transA not in (CblasNoTrans, CblasTrans):
    raise _ex.GTException('Invalid transpose marker')

  if diag not in (CblasNonUnit, CblasUnit):
    raise _ex.GTException('Invalid unit diagonal marker')

  cblasA = _CblasMatrix(A)
  cblasB = _CblasMatrix(B)

  k = cblasB.m if side==CblasLeft else cblasB.n

  if cblasA.m != k or cblasA.n != k:
    raise _ex.GTException('The matrix A should be %d-by-%d dimensional (%d-by-%d dimensional matrix given)' % (k, k, cblasA.m, cblasA.n))

  if cblasA.order != cblasB.order:
    # if matrix A has the different order than matrix B, then we just treat A as a transposed matrix
    uplo = CblasUpper if uplo == CblasLower else CblasUpper
    transA = CblasTrans if transA == CblasNoTrans else CblasNoTrans

  errorCode = _dtrsmRoutine(cblasB.order, side, uplo, transA, diag, cblasB.m, cblasB.n, alpha, cblasA.ptr, cblasA.ld, cblasB.ptr, cblasB.ld)

  if 0 > errorCode:
    raise _ex.GTException('The triangular matrix given is singular')
  elif 0 < errorCode:
    parametersList = ('C/Fortran storage scheme marker',
                      'matrix A side marker',
                      'upper/lower triangle marker',
                      'transpose marker',
                      'diagonal type marker',
                      'the number of rows of B',
                      'the number of columns of B',
                      'scalar alpha',
                      'pointer to matrix A',
                      'leading dimension of matrix A'
                      'pointer to matrix B',
                      'leading dimension of matrix B')
    errorMessage = parametersList[errorCode-1] if errorCode <= len(parametersList) else 'can not detect parameter'
    raise _ex.GTException('Invalid parameter #%d: %s' % (errorCode, errorMessage))

  return cblasB.origin
