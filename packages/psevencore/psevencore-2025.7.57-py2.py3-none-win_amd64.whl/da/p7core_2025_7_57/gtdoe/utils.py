#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
#

import numpy as _numpy
import warnings as _warn

from . import generator
from .. import shared as _shared
from .. import exceptions as _ex
from ..utils import bbconverter as _bbconverter

def orthogonal_array_minimal_count(problem_or_bounds, categorical_vars=None):
  """
  This helper determines orthogonal array minimal count.

  The function simply reads Summary field of the result generate by

    result = Generator().build_doe(problem, count=1, options={'GTDoE/Technique': 'OrthogonalArray', 'GTDoE/OrthogonalArray/ArrayType': 'Irregular'})

  :param problem_or_bounds: design space bounds or problem definition
  :type bounds: ``tuple(list(float), list(float))`` or gtdoe.ProblemGeneric
  :param categorical_vars: used only if bounds are provided, specify categorical_variables
  either in 'GTDoE/OrthogonalArray/LevelsNumber' or ' GTDoE/CategoricalVariables' in format.
  :type options: ``dict``
  :return: orthogonal array minimal count, balanced near orthogonal array minimal count
  :rtype: int, int

  """

  gen = generator.Generator()
  if categorical_vars:
    gen.options.set(dict((k, categorical_vars[k]) for k in categorical_vars))
  gen.options.set('GTDoE/Technique', 'OrthogonalArray')
  gen.options.set('GTDoE/OrthogonalArray/ArrayType', 'Irregular')
  gen.options.set('/GTDoE/SuppressResultWarning', True) #suppress an old warning

  catvars = _shared.parse_json(gen.options._get('GTDoE/CategoricalVariables'))
  bounds, catvars, _, var_types = _bbconverter._make_bounds(problem_or_bounds, catvars, "OrthogonalArray")

  gen.options.set('GTDoE/CategoricalVariables', catvars)
  gen.options.set('/GTDoE/VariablesType', var_types)

  info, _, _, _, _ = gen._backend.generate_sample(budget=1, bounds=gen._preprocess_bounds(bounds),
                                                  init_x=None, init_y=None, validation_mode=False)

  info = info.get("Generator", {}).get("Summary", {})
  return info.get("First Orthogonal"), info.get("First Balanced")
