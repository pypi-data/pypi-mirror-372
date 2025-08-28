#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Utility functions for bit length and log2 for integers"""

from operator import irshift

def get_bit_length(integer):
  """Get the bit length of the given integer."""
  length = 0
  while (integer):
    integer = irshift(integer, 1)
    length = length + 1
  return length

def get_floored_binary_logarithm(integer):
  """Get [log_2(integer)] for a given integer."""
  bit_length = get_bit_length(integer)
  return max(get_bit_length(integer) - 1, 0)
