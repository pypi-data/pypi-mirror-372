#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Generic Tool for Approximation (GTApprox) module."""

class GradMatrixOrder(object):
  r"""Enumerates available gradient output modes.

  .. py:attribute:: F_MAJOR

      Indexed in function-major order (`grad_{ij} = \frac{df_i}{dx_j}`).

  .. py:attribute:: X_MAJOR

      Indexed in variable-major order (`grad_{ij} = \frac{df_j}{dx_i}`).

  """
  F_MAJOR, X_MAJOR = range(2)

class ExportedFormat(object):
  """Enumerates available export formats.

  .. versionadded:: 6.10
     added ``str`` aliases for export formats.

  .. versionchanged:: 6.16
     added the C# source format, see :attr:`~da.p7core.gtapprox.ExportedFormat.CSHARP_SOURCE`.

  .. versionchanged:: 6.16.1
     C# source export is supported for all GTApprox models but is not yet supported for GTDF models loaded to :class:`.gtapprox.Model`.

  In :meth:`~da.p7core.gtapprox.Model.export_to()` you can specify *format* in two ways:

  #. Using enumeration, for example: ``my_model.export_to(gtapprox.ExportedFormat.C99_PROGRAM, "func_name", "comment", "my_model.c")``.
  #. Using ``str`` alias (*added in 6.10*), for example: ``my_model.export_to("c_program", "func_name", "comment", "my_model.c")``.

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

      C header of the model.

      Aliases: ``"c99_header"``, ``"c_header"``, ``"header"``.

  .. py:attribute:: C99_SOURCE

      C header and implementation of the model.

      Aliases: ``"c99_source"``, ``"c_source"``, ``"c"``.

  .. py:attribute:: EXCEL_DLL

      C implementation of the model intended for creating a DLL compatible with Microsoft Excel.

      Aliases: ``"excel_dll"``, ``"excel"``.

  .. py:attribute:: CSHARP_SOURCE

      .. versionadded:: 6.16

      C# implementation of the model.

      Alias: ``"c#"``.

      .. note::

         The C# source export is not yet supported for GTDF models loaded to :class:`.gtapprox.Model`.

      .. note::

         The C# source export requires an up to date license valid for pSeven Core 6.16 and above.

  """
  OCTAVE, OCTAVE_MEX, C99_PROGRAM, C99_HEADER, C99_SOURCE, EXCEL_DLL, CSHARP_SOURCE = range(7)

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
             'c#': CSHARP_SOURCE,
             'csharp': CSHARP_SOURCE,
               }

  DEFAULT_NAME = {  OCTAVE: "octave", OCTAVE_MEX: "octave_mex", C99_PROGRAM: "c_program",
                    C99_HEADER: "c_header", C99_SOURCE: "c_source", EXCEL_DLL: "excel_dll",
                    CSHARP_SOURCE: "c#"}
  DEFAULT_EXT = { OCTAVE: ".m", OCTAVE_MEX: ".c", C99_PROGRAM: ".c", C99_HEADER: ".h",
                  C99_SOURCE: ".c", EXCEL_DLL: ".c", CSHARP_SOURCE: ".cs"}

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

# brings all submodules to package root namespace
from .builder import Builder
from .model import Model, _debug_export_file_size
from .utilities import Utilities, set_remote_build, disable_remote_build, calculate_errors, get_nan_structure, export_fmi_cs, export_fmi_me, export_fmi_20
from ..shared import TeeLogger
from .split_sample import train_test_split

__all__ = ['Builder', 'Model', 'GradMatrixOrder', 'ExportedFormat', 'Utilities', 'TeeLogger', 'set_remote_build', 'train_test_split',
           'disable_remote_build', 'calculate_errors', 'get_nan_structure', 'export_fmi_cs', 'export_fmi_me', 'export_fmi_20']
