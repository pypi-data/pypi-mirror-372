#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Statistical utilities module."""

# brings all submodules to package root namespace
from .analyzer import Analyzer
from .utilities import ElementaryStatistics, OutlierDetectionResult, DistributionCheckResult

__all__ = ['Analyzer', 'ElementaryStatistics', 'OutlierDetectionResult', 'DistributionCheckResult']
