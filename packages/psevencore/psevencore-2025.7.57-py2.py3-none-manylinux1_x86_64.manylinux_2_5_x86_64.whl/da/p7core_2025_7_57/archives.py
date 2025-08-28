#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

from __future__ import with_statement
from __future__ import division

import sys as _sys
import os as _os
import time as _time
import contextlib as _contextlib
import zipfile as _zipfile
import tarfile as _tarfile
import codecs as _codecs

from . import shared as _shared

@_contextlib.contextmanager
def _with_zipfile(file, *args, **kwargs):
  obj = _zipfile.ZipFile(file, *args, **kwargs)
  try:
    yield obj
  finally:
    obj.close()

@_contextlib.contextmanager
def _with_tarfile(file, *args, **kwargs):
  obj = _tarfile.open(file, *args, **kwargs)
  try:
    yield obj
  finally:
    obj.close()

def _detect_tar_mode(filename):
  tar_codes = ((".tar", "w"), (".tgz", "w:gz"), (".tar.gz", "w:gz"), (".taz", "w:gz"), (".tbz", "w:bz2"), (".tbz2", "w:bz2"), (".tar.bz2", "w:bz2"))
  for tar_ext, tar_mode in tar_codes:
    ext_pos = -len(tar_ext)
    if filename[ext_pos:].lower() == tar_ext:
      return filename[:ext_pos], tar_mode
  return filename, None

class _BasicArchveWriter(object):
  def __init__(self, file_obj):
    self.pending_error = None
    self.file_obj = file_obj

  def process_exception(self):
    if self.pending_error is None:
      self.pending_error = _sys.exc_info()

  def flush_callback_exceptions(self, succeeded, model_error):
    if self.pending_error is not None:
      exc_type, exc_val, exc_tb = self.pending_error
      if model_error is not None and model_error[1]:
        exc_val = ("%s The origin of the exception is: %s" % (_shared._safestr(model_error[1]).strip(), _shared._safestr(exc_val).strip())) if exc_val else model_error[1]
      _shared.reraise(exc_type, exc_val, exc_tb)

    if model_error is not None and model_error[0] is not None:
      raise model_error[0](model_error[1] or "Failed to write archive.")

class _ZipArchiveWriter(_BasicArchveWriter):
  def __call__(self, archname, bytes):
    try:
      self.file_obj.writestr(_shared._preprocess_utf8(archname), bytes, _zipfile.ZIP_DEFLATED)
      return True
    except:
      self.process_exception()
    return False

class _SequentialReader(object):
  def __init__(self, data, size=None):
    self.data = data
    self.size = len(data) if size is None else size

  def read(self, size=-1):
    size = self.size if (size is None or size < 0) else min(size, self.size)
    data_block = self.data[:size]
    self.data = self.data[size:]
    self.size -= size
    return data_block

class _TarArchiveWriter(_BasicArchveWriter):
  def __call__(self, archname, bytes):
    try:
      info = _tarfile.TarInfo(_shared._preprocess_utf8(archname))
      info.size = len(bytes)
      info.mode = 438 # chmod a+rw
      info.mtime = _time.time()
      self.file_obj.addfile(info, _SequentialReader(bytes, info.size))
      return True
    except:
      self.process_exception()
    return False

class _DirectoryWriter(_BasicArchveWriter):
  def __init__(self, directory, fixed_filename):
    super(_DirectoryWriter, self).__init__(None)
    self.directory = directory
    self.filename = fixed_filename

  @staticmethod
  def _create_path(dirname):
    if not dirname or _os.path.exists(dirname):
      return

    try:
      _os.makedirs(dirname)
    except:
      exc_type, exc_val, exc_tb = _sys.exc_info()
      _shared.reraise(exc_type, ('Failed to create directory "%s": %s' % (dirname, exc_val)), exc_tb)

  def __call__(self, archname, bytes):
    try:
      archname = _os.path.join(self.directory, _shared._preprocess_utf8(archname))

      self._create_path(_os.path.split(archname)[0])
      with _codecs.open(self.filename or archname, "w", encoding="utf8") as fobj:
        fobj.write(_shared._preprocess_utf8(bytes))
      return True
    except:
      self.process_exception()
    return False

class _MemoryFileWriter(_BasicArchveWriter):
  def __init__(self):
    super(_MemoryFileWriter, self).__init__(None)
    self.files = []

  def __call__(self, archname, bytes):
    try:
      self.files.append((_shared._preprocess_utf8(archname), _shared._preprocess_utf8(bytes)))
      return True
    except:
      self.process_exception()
    return False
