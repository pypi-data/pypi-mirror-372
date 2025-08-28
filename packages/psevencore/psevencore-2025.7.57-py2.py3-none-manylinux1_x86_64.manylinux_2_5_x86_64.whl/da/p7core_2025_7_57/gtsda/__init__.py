#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Generic Tool for Sensitivity and Dependency Analysis (GTSDA) module."""

GTSDA_PROBLEM_SAMPLE, GTSDA_PROBLEM_BLACKBOX = range(2)

# brings all submodules to package root namespace
from .analyzer import RankResult, SelectResult, CheckResult, Analyzer

__all__ = ['Analyzer', 'RankResult', 'SelectResult', 'CheckResult']
