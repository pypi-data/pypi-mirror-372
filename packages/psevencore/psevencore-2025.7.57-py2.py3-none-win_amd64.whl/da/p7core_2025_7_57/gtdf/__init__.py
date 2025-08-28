#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Generic Tool for Data Fusion (GTDF) module."""

class GradMatrixOrder:
  r"""Enumerates available gradient output modes.

  .. py:attribute:: F_MAJOR

      Indexed in function-major order (`grad_{ij} = \frac{df_i}{dx_j}`).

  .. py:attribute:: X_MAJOR

      Indexed in variable-major order (`grad_{ij} = \frac{df_j}{dx_i}`).

  """
  F_MAJOR, X_MAJOR = range(2)

# brings all submodules to package root namespace
from .builder import Builder
from .model import Model, ModelWithBlackbox

__all__ = ['Builder', 'Model', 'ModelWithBlackbox', 'GradMatrixOrder']
