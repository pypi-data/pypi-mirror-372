#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

class NullLogger(object):

  def dbg(self, message):
    pass

  def info(self, message):
    pass

  def warn(self, message):
    pass

  def error(self, message):
    pass

  def fatal(self, message):
    pass


def pretty_file_size(size):
  """pretty print for file size"""
  x = ['Tb', 'Gb', 'Mb', 'Kb', 'byte(s)']
  step = 1024.0
  units = x.pop()
  if size < step:
    return '%d %s' % (size, units)
  while x and size >= step:
    size //= step
    units = x.pop()
  return '%.1f %s' % (size, units)


def test_ssh_connection(hostname, port=22, username=None, password=None, private_key=None):
  """Check if it is possible to connect via ssh with given credentials"""
  import paramiko
  ssh = paramiko.SSHClient()
  ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  if private_key:
    from ..six import StringIO
    keyfile = StringIO(private_key)
    private_key = paramiko.RSAKey.from_private_key(keyfile)
  ssh.connect(hostname, port, username, password, private_key, allow_agent=False)
  ssh.close()
