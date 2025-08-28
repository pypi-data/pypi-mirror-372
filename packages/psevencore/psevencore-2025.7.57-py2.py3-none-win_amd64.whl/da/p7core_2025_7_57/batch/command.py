#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
# cloned std.ShellScript/command.py

from __future__ import with_statement

import socket
import subprocess
import traceback
import os
import sys
import errno
from stat import S_ISDIR, S_IXUSR
import tempfile
import shutil
import logging
import paramiko

from .utils import NullLogger, pretty_file_size

from .. import shared as _shared
from .. import six as _six

# reduce logging spam from paramiko
logging.getLogger("paramiko").setLevel(logging.WARNING)

SSHException = paramiko.SSHException


class Command(object):
  """
  Command and its arguments
  """

  def __init__(self, command, args=None):
    """
    Instantiates new L{Command}
    """
    self.__command = command
    self.__args = args if args else []

  @property
  def command(self):
    return self.__command

  @property
  def args(self):
    return self.__args


class CommandResult(object):
  """
  Result of command execution: exit code, stdOut as string and stdErr as string
  """

  def __init__(self):
    """
    Instantiates new L{CommandResult}
    """
    self.exitCode = None
    self.stdOut = None
    self.stdErr = None

class Transport(object):
  """
  Base abstract class for transports
  """

  def __init__(self):
    """
    Create new L{Transport} instance
    """
    pass

  def release(self):
    """
    Cleanup internal transport structures. Call when transport object is no longer required
    """
    pass

  @staticmethod
  def normalizePath(path):
    if path is not None:
      if not path.endswith("/"):
        path += "/"
    else:
      path = "./"

    return path

  @staticmethod
  def getFullPath(workingDirectory, path):
    workingDirectory = Transport.normalizePath(workingDirectory)
    if path is not None:
      if path.startswith("./"):
        path = path[2:]

    return (workingDirectory if not path.startswith("/") else "") + (path or "")

  def makeDirectory(self, dirname):
    """
    Make directory named `dirname`
    @return absolute path of created directory
    """
    raise NotImplementedError()

  def makeTempDirectory(self, template):
    """
    Make uniquely named directory
    @return absolute path of created directory
    """
    raise NotImplementedError()

  def removeDirectory(self, dirname):
    """
    Remove directory named `dirname`
    """
    return NotImplementedError


  def executeCommand(self, command):
    """
    Executes C{command} using this transport

    @param command: command to execute
    @type command: L{Command}

    @return: command execution result: exit code, AtdOut string and StdErr string
    @rtype: L{CommandResult}

    @raise TransportException: if something goes wrong executing the command specified
    """
    raise NotImplementedError()

  def readFile(self, filePath, fromIndex=0, targetFile=None):
    """
    Reads file to string using this transport

    @param fromIndex: skip bytes from the beginning
    @type fromIndex: int

    @param filePath: path of the target file
    @type filePath: str

    @param targetFile: read and output data to this file, do not return
    @type targetFile: file

    @return: pair [str, pos] where str is file contents as string and pos is current file position

    @raise TransportException: if something goes wrong reading this file
    """
    raise NotImplementedError()

  def writeFile(self, targetPath, sourceFile, append=False):
    """
    Writes file using this transport

    @param sourceFile: file to read data from

    @param targetPath: path of the target file
    @type targetPath: str

    @raise TransportException: if something goes wrong writing this file
    """
    raise NotImplementedError()

  def deleteFile(self, filePath):
    """
    Deletes file using this transport

    @param filePath: path of the target file
    @type filePath: str

    @raise TransportException: if something goes wrong deleting this file
    """
    raise NotImplementedError()

  def upload_dir(self, local_path, remote_path, resume_info=None):
    """
    Upload contents of the directory `local_path` to `remote_path` on remote host

    resume_info - `dict`: local_filename -> boolean
                False - download of key has been initiated
                True - download of key has been completed
    @type resume_info: `dict`
    @raise TransportException
    """
    raise NotImplementedError()

  def download_dir(self, remote_path, local_path, resume_info=None):
    """
    Download contents of directory `remote_path` on remote host to `local_path`

    @param resume_info - maps remote_filename -> boolean
               False - download of key has been initiated
               True - download of key has been completed
    @type resume_info: `dict`
    @raise TransportException
    """
    raise NotImplementedError()


class TransportException(Exception):
  """Raised if something goes wrong executing command using specified transport"""
  pass


class TransportAuthenticationException(Exception):
  """Raised if transport requires authentication and it has failed"""
  pass


class LocalTransport(Transport):
  CHUNK_SIZE = 32768 # 32k

  def __init__(self, logger=NullLogger()):
    """
    Create new L{LocalTransport} instance
    """
    super(LocalTransport, self).__init__()
    self._logger = logger

  def executeCommand(self, command):
    """
    Executes C{command} on local computer

    @param command: command to execute
    @type command: L{Command}

    @return: command execution result: exit code, StdOut string and StdErr string
    @rtype: L{CommandResult}
    """
    shellCommand = [command.command]
    if command.args is not None:
      shellCommand += command.args
    shellCommand = " ".join(shellCommand)
    try:
      process = subprocess.Popen(shellCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8")
    except TypeError:
      process = None
    if process is None:
      process = subprocess.Popen(shellCommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    exitCode = process.wait()
    result = CommandResult()
    result.exitCode = exitCode
    result.stdOut = stdout
    result.stdErr = stderr
    return result

  def makeDirectory(self, dirname):
    if not os.path.exists(dirname):
      try:
        os.makedirs(dirname)
      except Exception:
        exc_info = sys.exc_info()
        _shared.reraise(TransportException, ('Failed to create directory "%s": %s' % (dirname, exc_info[1])), exc_info[2])
    return os.path.abspath(dirname)

  def makeTempDirectory(self, template):
    return tempfile.mkdtemp(prefix=template.rstrip("X"), dir=_six.moves.getcwd())

  def removeDirectory(self, dirname):
    def onerror(function, path, excinfo):
      if function in [os.rmdir, os.remove] and self._logger:
        self._logger.warn('failed to remove "%s": %s' % (path, excinfo))
    shutil.rmtree(dirname, onerror=onerror)

  def readFile(self, filePath, fromIndex=0, targetFile=None):
    fileContents = None
    remoteFileSize = 0

    try:
      with open(filePath, "rb") as handle:
        remoteFileSize = os.path.getsize(filePath)

        offset = fromIndex
        if offset is None:
          if targetFile:
            targetFile.seek(0, os.SEEK_END)
            targetFileSize = targetFile.tell()
            targetFile.seek(0, 0)
            offset = targetFileSize
          else:
            offset = 0

        if offset > remoteFileSize:
          raise TransportException("Offset (" + str(fromIndex) + ") is greater than file size (" + str(remoteFileSize) + ")")

        if offset:
          handle.seek(offset)
        if targetFile:
          for chunk in iter(lambda: handle.read(LocalTransport.CHUNK_SIZE), _six.b("")):
            targetFile.write(chunk)
        else:
          fileContents = handle.read()
    except (IOError, OSError):
      _shared.reraise(TransportException, *sys.exc_info()[1:])

    return [fileContents, remoteFileSize]

  def writeFile(self, targetPath, sourceFile, append=False):
    if append:
      try:
        remoteFileSize = os.path.getsize(targetPath)
      except OSError:
        exc_info = sys.exc_info()
        if exc_info[1].errno == errno.ENOENT:
          remoteFileSize = 0
        else:
          _shared.reraise(*exc_info)
    else:
      remoteFileSize = 0

    sourceFile.seek(0, os.SEEK_END)
    localFileSize = sourceFile.tell()
    sourceFile.seek(0, 0)

    if localFileSize < remoteFileSize:
      remoteFileSize = 0
      append = False

    createDisposition = "ab" if append and remoteFileSize > 0 else "w+b"
    sourceFile.seek(remoteFileSize)
    with open(targetPath, createDisposition) as handle:
      handle.seek(remoteFileSize)
      for chunk in iter(lambda: sourceFile.read(LocalTransport.CHUNK_SIZE), _six.b("")):
        handle.write(chunk)

  def deleteFile(self, filePath):
    try:
      os.remove(filePath)
    except (IOError, OSError):
      exc_info = sys.exc_info()
      if exc_info[1].errno != errno.ENOENT:
        _shared.reraise(TransportException, *exc_info[1:])


# @todo all ssh operations should have resonable timeout. For some reason paramiko ignores all or some of set timeouts.
# Timeouts should apply to:
#   ssh.connect(..., timeout=60)
#   any ftp channel (ftp = ssh.open_sftp(); ftp.get_channel().settimeout(60))
#   any ssh channel (channel = transport.open_session(); channel.settimeout(60))
class SSHTransport(Transport):
  DEFAULT_SSH_PORT = 22
  CHUNK_SIZE = 512 * 1024 # 512k (sdk.file has poor perfomance on small chunk buffer)

  def __init__(self, host=None, port=DEFAULT_SSH_PORT, username=None, password=None, private_key=None, logger=NullLogger()):
    """
    Prepares SSH connection to remote host to execute commands on

    @param host: the server to connect to
    @type host: str
    @param port: the server port to connect to
    @type port: int
    @param username: the username to authenticate as
    @type username: str
    @param password: a password to use for authentication or for unlocking a private key
    @type password: str
    @param private_key: an optional RSA private key to use for authentication (OpenSSH format)
    @type private_key: str
    """
    super(SSHTransport, self).__init__()
    self.host = host
    self.port = port
    self.username = username
    self.password = password
    self.private_key = None
    if private_key:
      keyfile = _six.StringIO(private_key)
      self.private_key = paramiko.RSAKey.from_private_key(keyfile)
    self.logger = logger
    self._exception_counter = 0
    self._ssh = None
    self._ftp = None
    self._execute_in_user_environment = True
    self._is_old_paramiko_version = tuple(int(_) for _ in paramiko.__version__.split('.')) < (1, 16, 0)

  def release(self):
    if self._ssh:
      self._ssh.close()
      self._ssh = None
    if self._ftp:
      self._ftp.close()
      self._ftp = None

  def count_exception(self):
    """count exceptions and release ssh session if there are too many of them"""
    self._exception_counter += 1
    if self._exception_counter > 100:
      self._exception_counter = 0
      self.release()

  def ssh_wrapper(self):
    """decorator for methods which use get_ssh() or get_ftp()"""
    def wrapped_func(this, *args, **kwargs):
      try:
        result = self(this, *args, **kwargs)
        return result
      except paramiko.AuthenticationException:
        ex, tb = sys.exc_info()[1:]
        this.release()
        _shared.reraise(TransportAuthenticationException, ex, tb)
      except (socket.error, socket.herror, socket.gaierror, socket.timeout):
        ex, tb = sys.exc_info()[1:]
        this.release()
        _shared.reraise(TransportException, ex, tb)
      except Exception:
        exc_info = sys.exc_info()
        this.count_exception()
        _shared.reraise(*exc_info)

    return wrapped_func

  def get_ssh(self):
    if not self._ssh:
      ssh = paramiko.SSHClient()
      ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      ssh.connect(hostname=self.host, port=self.port, username=self.username, password=self.password, pkey=self.private_key, allow_agent=False)
      ssh.get_transport().window_size = 2147483647 # hack: increase default value to make transfer faster
      self._ssh = ssh
      ssh = None
    return self._ssh

  def get_ftp(self):
    if not self._ftp:
      self._ftp = self.get_ssh().open_sftp()
    return self._ftp

  def to_remote_path(self, path):
    """convert path separator to target system"""
    return "/".join(path.split(os.sep))

  @classmethod
  def check_private_key(cls, private_key):
    """Check if private key is valid RSA key"""
    if private_key:
      keyfile = _six.StringIO(private_key)
      paramiko.RSAKey.from_private_key(keyfile)

  @ssh_wrapper
  def executeCommand(self, command):
    """
    Executes C{command} on this SSH connection

    @param command: command to execute
    @type command: L{Command}

    @return: command execution result: exit code, StdOut string and StdErr string
    @rtype: L{CommandResult}

    @raise TransportException: if something goes wrong executing the command specified
    """
    shellCommand = command.command
    for arg in command.args:
      shellCommand += " " + arg

    ssh = self.get_ssh()
    transport = ssh.get_transport()
    channel = transport.open_session()
    if self._execute_in_user_environment:
      shellCommand = ". ~/.profile >/dev/null 2>&1; " + shellCommand
    channel.exec_command(shellCommand)
    channel.shutdown_write()
    exitCode = channel.recv_exit_status()
    stdOut = channel.makefile("rb")
    stdErr = channel.makefile_stderr("rb")

    result = CommandResult()
    result.exitCode = exitCode
    result.stdOut = _shared._preprocess_utf8(stdOut.read())
    result.stdErr = _shared._preprocess_utf8(stdErr.read())

    channel.close()
    return result

  @ssh_wrapper
  def makeDirectory(self, dirname):
    command = Command("mkdir -p \"" + dirname + "\" && cd \"" + dirname + "\" && pwd")
    commandResult = self.executeCommand(command)
    if commandResult.exitCode != 0:
      raise TransportException("Unable to create directory '%s': %s" % (dirname, commandResult.stdErr))
    return commandResult.stdOut.splitlines()[0]

  @ssh_wrapper
  def removeDirectory(self, dirname):
    command = Command("rm -rf \"%s\"" % dirname)
    commandResult = self.executeCommand(command)
    if commandResult.exitCode != 0:
      raise TransportException("Unable to remove directory '%s': %s" % (dirname, commandResult.stdErr))

  @ssh_wrapper
  def makeTempDirectory(self, template):
    command = Command("mktemp -d \"`pwd`/%s\"" % template)
    commandResult = self.executeCommand(command)
    if commandResult.exitCode != 0:
      raise TransportException("Unable to create temp directory '%s': %s" % (template, commandResult.stdErr))
    return commandResult.stdOut.splitlines()[0]

  @ssh_wrapper
  def readFile(self, filePath, fromIndex=None, targetFile=None):
    try:
      ftp = self.get_ftp()

      f = ftp.open(filePath, "rb")
      st = f.stat()
      if self._is_old_paramiko_version:
        f.prefetch()
      else:
        f.prefetch(st.st_size) # speed up future reads
      remoteFileLength = st.st_size

      offset = fromIndex
      if offset is None:
        if targetFile:
          targetFile.seek(0, os.SEEK_END)
          targetFileSize = targetFile.tell()
          targetFile.seek(0, 0)

          offset = targetFileSize
        else:
          offset = 0
      else:
        f.seek(fromIndex)

      if offset > remoteFileLength:
        raise TransportException("Offset (" + str(fromIndex) + ") is greater than file size (" + str(remoteFileLength) + ")")

      content = _six.b("")
      for chunk in iter(lambda: f.read(SSHTransport.CHUNK_SIZE), _six.b("")):
        if targetFile:
          targetFile.write(chunk)
        else:
          content += chunk
      pos = f.tell()
      f.close()
      return [content, pos]
    except (IOError, OSError):
      e, tb = sys.exc_info()[1:]
      _shared.reraise(TransportException, TransportException("Unable to read remote file '%s': %s" % (filePath, e)), tb)

  @ssh_wrapper
  def writeFile(self, targetPath, sourceFile, append=False):
    try:
      ftp = self.get_ftp()

      if append:
        f = ftp.open(targetPath, "wb")
        st = f.stat()
        f.close()
        remoteFileSize = st.st_size
      else:
        remoteFileSize = 0

      sourceFile.seek(0, os.SEEK_END)
      localFileSize = sourceFile.tell()
      sourceFile.seek(0, 0)

      if localFileSize < remoteFileSize:
        remoteFileSize = 0
        append = False

      f = ftp.open(targetPath, "a+b" if append else "wb")
      f.set_pipelined(True) # speed up writes
      sourceFile.seek(remoteFileSize)
      for chunk in iter(lambda: sourceFile.read(SSHTransport.CHUNK_SIZE), _six.b("")):
        f.write(chunk)
      f.close()
      ftp.chmod(targetPath, 0x1ED) # 0755
    except (IOError, OSError):
      e, tb = sys.exc_info()[1:]
      _shared.reraise(TransportException, TransportException("Unable to write remote file '%s': %s" % (targetPath, e)), tb)

  @ssh_wrapper
  def deleteFile(self, filePath):
    try:
      ftp = self.get_ftp()
      ftp.remove(filePath)
    except (IOError, OSError):
      ex, tb = sys.exc_info()[1:]
      if ex.errno == errno.ENOENT:
        return [None, 0]
      else:
        _shared.reraise(TransportException, TransportException(ex), tb)
    except Exception:
      ex, tb = sys.exc_info()[1:]
      _shared.reraise(TransportException, TransportException(ex), tb)

  @ssh_wrapper
  def upload_dir(self, local_path, remote_path, resume_info=None):
    if not resume_info:
      resume_info = {}

    def fix_permissions(bits):
      if sys.platform == "win32":
        bits = bits | S_IXUSR
      return bits

    try:
      ssh = self.get_ssh()

      remote_path = self.to_remote_path(remote_path)
      channel = ssh.get_transport().open_session()
      channel.exec_command("mkdir -p \"%s\" && echo" % remote_path)
      channel.shutdown_write()
      exit_code = channel.recv_exit_status()
      stderr = channel.makefile_stderr().read()
      channel.close()

      if exit_code != 0:
        raise OSError("Unable to create remote directory '%s': %s" % (remote_path, stderr))

      ftp = self.get_ftp()
      ftp.chdir(".")
      if not os.path.isabs(remote_path):
        remote_path = os.path.join(ftp.getcwd(), remote_path)

      for root, dirs, files in os.walk(local_path):
        for d in dirs:
          remote_filepath = self.to_remote_path(os.path.join(remote_path, os.path.relpath(os.path.join(root, d), local_path)))
          dir_exists = False

          try:
            dir_exists = S_ISDIR(ftp.stat(remote_filepath).st_mode)
          except:
            pass

          try:
            if not dir_exists:
              ftp.mkdir(remote_filepath)
          except (OSError, IOError):
            e, tb = sys.exc_info()[1:]
            _shared.reraise(TransportException, TransportException("Unable to create remote directory '%s': %s" % (remote_filepath, e)), tb)
        for filename in files:
          local_filepath = os.path.join(root, filename)
          remote_filepath = self.to_remote_path(os.path.join(remote_path, os.path.relpath(local_filepath, local_path)))

          if resume_info.get(local_filepath, False):
            self.logger.dbg("Skipping local file '%s' - already uploaded" % (local_filepath))
            continue

          resume_at = 0
          if local_filepath in resume_info:
            try:
              remote_size = ftp.stat(remote_filepath).st_size
              if remote_size < os.path.getsize(local_filepath):
                resume_at = remote_size
            except OSError:
              pass
          resume_info[local_filepath] = False

          with open(local_filepath, "rb") as f_local:
            with ftp.open(remote_filepath, "wb") as f_remote:
              f_remote.set_pipelined(True)  # speed up writes

            pretty_size = pretty_file_size(os.path.getsize(local_filepath))
            message = "Uploading file '%s' => '%s' (%s)" % (local_filepath, remote_filepath, pretty_size)
            if resume_at:
              message += " - resuming at %d" % (resume_at)
              f_remote.seek(resume_at)
              f_local.seek(resume_at)

            self.logger.dbg(message)
            for chunk in iter(lambda: f_local.read(SSHTransport.CHUNK_SIZE), _six.b("")):
              f_remote.write(chunk)
          resume_info[local_filepath] = True

          # copy local file permissions and flags
          ftp.chmod(remote_filepath, fix_permissions(os.stat(local_filepath).st_mode))

    except (OSError, IOError):
      e, tb = sys.exc_info()[1:]
      _shared.reraise(TransportException, TransportException("Unable to upload contents of '%s' to '%s': %s" % (local_path, remote_path, e)), tb)


  @ssh_wrapper
  def download_dir(self, remote_path, local_path, resume_info=None):
    if not resume_info:
      resume_info = {}

    try:
      ftp = self.get_ftp()

      def download(remote_dir, local_dir):
        if not os.path.exists(local_dir):
          os.makedirs(local_dir)
        dir_items = ftp.listdir_attr(remote_dir)
        for item in dir_items:
          remote_filepath = self.to_remote_path(os.path.join(remote_dir, item.filename))
          local_filepath = os.path.join(local_dir, item.filename)
          if S_ISDIR(item.st_mode):
            download(remote_filepath, local_filepath)
          else:
            if resume_info.get(remote_filepath, False):
              self.logger.dbg("Skipping remote file '%s' - already downloaded" % (remote_filepath))
              continue
            resume_at = 0
            if remote_filepath in resume_info:
              try:
                local_size = os.path.getsize(local_filepath)
                if local_size < item.st_size:
                  resume_at = local_size
              except OSError:
                pass
            resume_info[remote_filepath] = False

            with ftp.open(remote_filepath, "rb") as f_remote:
              with open(local_filepath, "wb") as f_local:
                if self._is_old_paramiko_version:
                  f_remote.prefetch()
                else:
                  f_remote.prefetch(item.st_size)  # speed up future reads

              pretty_size = pretty_file_size(item.st_size)
              message = "Downloading file '%s' => '%s' (%s)" % (remote_filepath, local_filepath, pretty_size)
              if resume_at:
                message += " - resuming at %d" % (resume_at)
                f_remote.seek(resume_at)
                f_local.seek(resume_at)

              self.logger.dbg(message)
              for chunk in iter(lambda: f_remote.read(SSHTransport.CHUNK_SIZE), _six.b("")):
                f_local.write(chunk)
            resume_info[remote_filepath] = True

            # copy remote file permissions and flags
            os.chmod(local_filepath, item.st_mode)

      download(self.to_remote_path(remote_path), local_path)
    except (OSError, IOError):
      e, tb = sys.exc_info()[1:]
      _shared.reraise(TransportException, TransportException("Unable to download contents of '%s' to '%s': %s" % (remote_path, local_path, e)), tb)

