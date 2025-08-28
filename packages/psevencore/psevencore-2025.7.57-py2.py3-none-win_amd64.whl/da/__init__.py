#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""
Init script for group of projects with version support.

This '__init__' script is intended to handle namespace-like package that in general combines different
projects - subpackages. Such subprojects may reside in different directories. Moreover there can be different
versions of single project. In any case this script will initialize multi directory package, will find the most
recent versions of existing subprojects and will initialize the routine which will import latest subproject if the
version is not explicitly specified.

It is much simpler to illustrate by an example.

Consider we have the following directories located in different places and each 'group' dir is pointed by the PYTHONPATH.

- A/group/prj1_1_0_0  # project 1 version 1.0.0
         /prj2_1_0_0  # project 2 version 1.0.0
         /__init__.py # this '__init__.py' file
- B/group/prj1_1_0_1  # project 1 version 1.0.1
         /__init__.py # this '__init__.py' file

In that case we will get desired behaviour - latest versions will be imported by default:

> from group import prj1
> print prj1
<module 'group.prj1_1_0_1' from '../B/group/prj1_1_0_1/__init__.pyc'>

> from group import prj2
> print prj2
<module 'group.prj2_1_x_x' from '../C/group/prj2_1_x_x/__init__.pyc'>

At the same time you can explicitly import some particular version:
> from group import prj1_1_0_0
> print prj1_1_0_0
<module 'group.prj1_1_0_0' from '../A/group/prj1_1_0_0/__init__.pyc'>

Typically, the 'group' in the example above is the company name or some metaproject name.

We assume that subpackages have the following naming scheme: '<package_name>_<version>',
where 'version' starts with a digit, and 'package_name' does not contain any digit with a preceding underscore.
"""

# add to the package's __path__ all subdirectories of directories on sys.path named after the package
from __future__ import with_statement

__path__ = __import__("pkgutil").extend_path(__path__, __name__)

class _pSevenModuleHook(object):
  class _LegacyLoader(object):
    def __init__(self, module_path, module_code):
      self.module_path = module_path
      self.module_code = module_code

    def load_module(self, fullname):
      import sys

      new_module = None

      try:
        import os
        import imp

        if fullname not in sys.modules:
          new_module = imp.new_module(fullname)
          sys.modules[fullname] = new_module

        module = sys.modules.get(fullname)
        module.__file__ = os.path.join(self.module_path, "__init__.py")
        module.__name__ = fullname
        module.__path__ = [self.module_path]
        module.__loader__ = self
        module.__package__ = fullname

        exec(self.module_code, module.__dict__)

        return module
      except:
        exc_value = sys.exc_info()[1]

      if new_module is not None:
        sys.modules.pop(fullname, None)

      raise ImportError(exc_value)

  def __init__(self, root_name):
    self._root_name = root_name
    self._modules = {}

  def __repr__(self):
    return "pSeven Core Package Finder"

  def _append(self, fullname, dirname):
    self._modules[self._root_name + "." + fullname] = dirname

  def find_spec(self, fullname, path, target=None):
    # The modern spec-based module finder.
    origin_module = self._modules.get(fullname)
    if not path or not origin_module:
      return None

    import os
    from importlib.util import spec_from_file_location

    for module_dir in path:
      try:
        module_path = os.path.join(module_dir, origin_module)
        module_init = os.path.join(module_path, "__init__.py")
        if os.path.exists(module_init):
          return spec_from_file_location(name=fullname, location=module_init, submodule_search_locations=[module_path])
      except:
        pass

    return None

  def find_module(self, fullname, path):
    # Good old PEP 302 module finder
    if not path:
      return None

    origin_module = self._modules.get(fullname)
    if not origin_module:
      return None

    try:
      import os

      for module_dir in path:
        module_path = os.path.join(module_dir, origin_module)
        try:
          with open(os.path.join(module_path, "__init__.py"), "r") as fid:
            module_code = fid.read(-1)
          return self._LegacyLoader(module_path, module_code)
        except:
          pass
    except:
      pass

    return None


def initialize_current_package():
  def _optional_int(value):
    try:
      return int(value)
    except:
      pass
    return value

  import sys
  import pkgutil
  import re

  versions = {}
  loaders = {}
  re_name = re.compile(r"^([A-Za-z0-9_]+?)_([0-9x]+.*)$")

  finder = _pSevenModuleHook(__name__)

  # iterate through all the subpackages located inside package directories
  for _, name_with_version, _ in pkgutil.iter_modules(__path__):
    try:
      # skip subpackages/submodules which names do not correspond to the naming rule
      match = re_name.match(name_with_version)
      if match is None:
        continue

      version = tuple(_optional_int(_) for _ in match.group(2).split('_'))

      for basename in (match.group(1), "macros"):
        finder._append(basename + "_" + match.group(2), name_with_version)

        # collect information about the latest version
        if versions.get(basename, (0,0,0)) <= version:
          versions[basename] = version
          loaders[basename] = name_with_version
    except:
      pass

  # install import hooks, which will handle the latest version as the default version
  for basename in loaders:
    finder._append(basename, loaders[basename])

  sys.meta_path.append(finder)

initialize_current_package()

# cleanup the namespace
del initialize_current_package
del with_statement
del _pSevenModuleHook

