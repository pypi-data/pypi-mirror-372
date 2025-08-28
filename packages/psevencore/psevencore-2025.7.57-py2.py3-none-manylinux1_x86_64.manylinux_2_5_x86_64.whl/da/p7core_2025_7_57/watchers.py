#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

"""Default watcher."""

class DefaultWatcher(object):
  """Never-interrupting watcher.

  Always returns ``True``, never interrupting the watched process.

  """
  def __call__(self, msg=None):
    return True
