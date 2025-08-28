#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
.. currentmodule:: da.p7core.utils

.. autosummary::
   :nosignatures:

-------------------------------------------------

"""

from .distributions import _chi2, _chi2inv, _tdist, _fdist, _normal
from . import buildinfo

__all__ = ['_chi2', '_chi2inv', '_tdist', '_fdist', '_normal', 'buildinfo']
