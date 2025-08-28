#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Supplementary python functions."""

import sys
import os
import platform
import re
import ctypes

def _platformInfo():
  """Get platform info."""
  (sysname, nodename, release, version, machine, processor) = platform.uname()

  try:
    machine = 'x64' if ctypes.sizeof(ctypes.c_void_p) > 4 else 'x86'
  except:
    machine = 'x64' if platform.architecture()[0] == '64bit' else 'x86'

  suffix = str()
  if sysname == 'Linux':
    suffix = 'so'
  elif sysname == 'Windows':
    suffix = 'dll'
  else:
    raise Exception('Unsupported system!')
  return sysname.lower(), machine, suffix


def _searchLib(libname, libpath, platform_info=None):
  """Searches specific directory for a native library with platform-dependent name.

  :param libname: library basename
  :param libpath: path to look in
  :param platform_info: (optional) platform tuple (sysname, machine, suffix)
  """
  try:
    sysname, machine, suffix = _platformInfo() if platform_info is None else platform_info
    return sorted([os.path.join(libpath, fname) for fname in os.listdir(libpath) \
      if re.match(r'^(lib)?%s-2025.7.57-%s-%s-[^-]+(-s)?(-dbg)?\.%s$' % (libname, sysname, machine, suffix), fname) != None], \
      reverse=True)
  except OSError:
    return []


def _searchPy(libname, libpath):
  """Searches specific directory for a python module.

  :param libname: module name
  :param libpath: path to look in
  """
  try:
    files = os.listdir(libpath)
    files = list([f for f in files if ('%s.py' % libname) == f])
  except OSError:
    files = []
  return libpath if files else None

def _searchPyDir(dirname, libpath):
  """Searches specific directory for a python package.

  :param dirname: package name
  :param libpath: path to look in
  """
  try:
    entities = [os.path.join(libpath, fpath) for fpath in os.listdir(libpath) if fpath == dirname]
    entities = [fpath for fpath in entities if os.path.isdir(fpath)]
  except OSError:
    entities = []
  return libpath if entities else None


def appendModulePath(libname, prefix=None, maxLevel=4, root=None):
  """Searches for a "libname" python module in any 'python' directories.

  The search starts from root (from __file__ parent directory if none provided) and up + in current directory.
  :param libname: module name
  :param prefix: additional prefix to bin/lib directories
  :param maxLevel: maximum 'steps' up the directory tree
  :param root: start search from here
  """
  if not root:
    root = os.path.dirname(os.path.realpath(__file__))

  pdir = _searchPy(libname, root)
  if prefix and not pdir:
    searchpath = os.path.join(root, prefix)
    pdir = _searchPy(libname, searchpath)

  currentRoot = root
  currentLevel = 0
  while not pdir and (currentLevel < maxLevel):
    pdir = _searchPy(libname, os.path.join(currentRoot, 'python'))
    if prefix and not pdir:
      searchpath = os.path.join(currentRoot, prefix)
      pdir = _searchPy(libname, os.path.join(searchpath, 'python'))
    try:
      currentRoot = os.path.split(currentRoot)[0]
    except:
      break
    currentLevel = currentLevel + 1
  if not pdir:
    raise Exception('Cannot find "%s" python module!'  % libname)
  sys.path.append(pdir)


def appendPackagePath(libname, prefix=None, maxLevel=4, root=None):
  """Searches for a "libname" python package in any 'python' directories.

  The search starts from root (from __file__ parent directory if none provided) and up + in current directory.
  :param libname: module name
  :param prefix: additional prefix to bin/lib directories
  :param maxLevel: maximum 'steps' up the directory tree
  :param root: start search from here
  """
  if not root:
    root = os.path.dirname(os.path.realpath(__file__))
  pdir = _searchPyDir(libname, root)

  if prefix and not pdir:
    searchpath = os.path.join(root, prefix)
    pdir = _searchPyDir(libname, searchpath)

  currentRoot = root
  currentLevel = 0
  while not pdir and (currentLevel < maxLevel):
    pdir = _searchPyDir(libname, os.path.join(currentRoot, 'python'))
    if prefix and not pdir:
      searchpath = os.path.join(currentRoot, prefix)
      pdir = _searchPyDir(libname, searchpath)
    try:
      currentRoot = os.path.split(currentRoot)[0]
    except:
      break
    currentLevel = currentLevel + 1
  if not pdir:
    raise Exception('Cannot find "%s" python package!' % libname)
  sys.path.append(pdir)


def loadNativeLib(libname, prefix=None, maxLevel=4, root=None):
  """Search for a "libname" native library in any 'bin' and 'lib' directories.

  The search starts from root (from __file__ parent directory if none provided) and up + in current directory.

  .. note::

  Requires ctypes!

  :param libname: module name
  :param prefix: additional prefix to bin/lib directories
  :param maxLevel: maximum 'steps' up the directory tree
  :param root: start search from here
  """
  if not root:
    root = os.path.dirname(os.path.realpath(__file__))

  def search_libs(root, platform_info):
    libs = _searchLib(libname, root, platform_info)
    if prefix and not libs:
      searchpath = os.path.join(root, prefix)
      libs = _searchLib(libname, searchpath)
    currentRoot = root

    currentLevel = 0
    def scanlibpaths(searchpath):
      libs = _searchLib(libname, os.path.join(searchpath, 'lib'), platform_info)
      if not libs:
        libs = _searchLib(libname, os.path.join(searchpath, 'bin'), platform_info)
      if not libs:
        libs = _searchLib(libname, os.path.join(searchpath, 'bin', sysname + '-' + machine), platform_info)
      return libs

    while not libs and (currentLevel < maxLevel):
      libs = scanlibpaths(currentRoot)
      if not libs and prefix:
        libs = scanlibpaths(os.path.join(currentRoot, prefix))
      try:
        currentRoot = os.path.split(currentRoot)[0]
      except:
        break
      currentLevel = currentLevel + 1
    return libs

  sysname, machine, suffix = _platformInfo()
  libs = search_libs(root, (sysname, machine, suffix))

  if not libs:
    raise Exception('Cannot find "%s" native library!' % libname)

  library = None

  try:
    origCwd = os.getcwdu()
  except AttributeError:
    origCwd = os.getcwd()

  for lib in libs:
    try:
      os.chdir(os.path.dirname(lib))
      try:
        library = ctypes.CDLL(lib)
        if library:
          message = 'Loaded "%s" library at path "%s"' % (libname, lib)
          break
      except:
        pass
    finally:
      os.chdir(origCwd)
  if not library:
    message = 'No loaded "%s" library' % libname
  return library, message
