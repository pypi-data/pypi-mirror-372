#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Generic Tool for Dimension Reduction (GTDR) module."""

class GradMatrixOrder:
  r"""Enumerates available gradient output modes.

  .. py:attribute:: F_MAJOR

      Indexed in function-major order (`grad_{ij} = \frac{df_i}{dx_j}`).

  .. py:attribute:: X_MAJOR

      Indexed in variable-major order (`grad_{ij} = \frac{df_j}{dx_i}`).

  """
  F_MAJOR, X_MAJOR = range(2)

class ExportedFormat:
  """Enumerates available export formats.

  .. py:attribute:: OCTAVE

      :term:`Octave` format.

      Alias: ``"octave"``.

  .. py:attribute:: OCTAVE_MEX

      C source for a MEX file.

      Aliases: ``"octave_mex"``, ``"mex"``.

  .. py:attribute:: C99_PROGRAM

      C source with the :func:`main()` function for a complete command-line based C program.

      Aliases: ``"c99_program"``, ``"c_program"``, ``"program"``.

  .. py:attribute:: C99_HEADER

      C header of the target function.

      Aliases: ``"c99_header"``, ``"c_header"``, ``"header"``.

  .. py:attribute:: C99_SOURCE

      C header and implementation of the target function.

      Aliases: ``"c99_source"``, ``"c_source"``, ``"c"``.

  .. py:attribute:: EXCEL_DLL

      C implementation of the model intended for creating a DLL compatible with Microsoft Excel.

      Aliases: ``"excel_dll"``, ``"excel"``.

  """
  OCTAVE, OCTAVE_MEX, C99_PROGRAM, C99_HEADER, C99_SOURCE, EXCEL_DLL = range(6)

  FORMATS = {'octave': OCTAVE,
             'octave_mex': OCTAVE_MEX,
             'mex': OCTAVE_MEX,
             'c99_program': C99_PROGRAM,
             'c_program': C99_PROGRAM,
             'program': C99_PROGRAM,
             'c99_header': C99_HEADER,
             'c_header': C99_HEADER,
             'header': C99_HEADER,
             'c99_source': C99_SOURCE,
             'c_source': C99_SOURCE,
             'c': C99_SOURCE,
             'excel_dll': EXCEL_DLL,
             'excel': EXCEL_DLL,
               }

  DEFAULT_NAME = {  OCTAVE: "octave", OCTAVE_MEX: "octave_mex", C99_PROGRAM: "c_program",
                    C99_HEADER: "c_header", C99_SOURCE: "c_source", EXCEL_DLL: "excel_dll"}
  DEFAULT_EXT = { OCTAVE: ".m", OCTAVE_MEX: ".c", C99_PROGRAM: ".c", C99_HEADER: ".h",
                  C99_SOURCE: ".c", EXCEL_DLL: ".c"}

  @staticmethod
  def from_string(fmt_name):
    try:
      fmt_code = int(fmt_name)
    except:
      fmt_code = ExportedFormat.FORMATS.get(str(fmt_name).lower(), -1)

    if fmt_code not in range(7):
      raise ValueError('\'%s\' cannot be converted to export format' % fmt_name)

    return fmt_code

  @staticmethod
  def to_string(fmt):
    try:
      code = ExportedFormat.FORMATS.get(str(fmt).lower(), fmt)
    except:
      code = fmt

    if code is not None:
      code = ExportedFormat.DEFAULT_NAME.get(code)

    if code is None:
      raise ValueError("Invalid or unsupported file format: %s" % fmt)

    return code

  @staticmethod
  def default_extension(fmt):
    try:
      code = ExportedFormat.FORMATS.get(str(fmt).lower(), fmt)
    except:
      code = fmt

    if code is not None:
      code = ExportedFormat.DEFAULT_EXT.get(code)

    if code is None:
      raise ValueError("Invalid or unsupported file format: %s" % fmt)

    return code

GT_DR_BY_DIM, GT_DR_BY_ERR, GT_DR_FE, GT_DR_FE_BB = range(4)

# brings all submodules to package root namespace
from .builder import Builder
from .model import Model, _debug_export_file_size

__all__ = ['Builder', 'Model', 'GradMatrixOrder', 'ExportedFormat']
