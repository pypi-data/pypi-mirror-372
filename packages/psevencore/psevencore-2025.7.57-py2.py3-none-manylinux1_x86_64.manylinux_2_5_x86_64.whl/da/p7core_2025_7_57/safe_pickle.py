#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#

import sys

try:
  import numpy as _numpy
except:
  _numpy = None

PY_2 = sys.version_info[0] == 2
SAFE_PICKLE_UID = "db9c8cf4-cc63-4164-b941-942ddab61f20"

_GENERIC_TYPES = (dict,  set, frozenset,
                  str, list, tuple, bytearray,
                  float, int, complex,
                  type, bool, type(None),)

if PY_2:
  import cPickle as pickle
  from StringIO import StringIO as _BytesIO

  _GENERIC_TYPES = _GENERIC_TYPES + (unicode, long, )
  _FIX_IMPORTS = {}

  _SafePicklerBase = object
  _SafeUnpicklerBase = object

else:
  import pickle
  from io import BytesIO as _BytesIO
  _FIX_IMPORTS = {"fix_imports": True}

  _SafePicklerBase = pickle.Pickler
  _SafeUnpicklerBase = pickle.Unpickler

def _dump_dtype(dtype):
  return (dtype.str if (not dtype.isalignedstruct and dtype.kind in "biufcmMOSU") else dtype.descr), dtype.isalignedstruct

def _load_dtype(dtype_args):
  return _numpy.dtype(*dtype_args)

class _SafePickler(_SafePicklerBase):
  def __init__(self, *args, **kwargs):
    super(_SafePickler, self).__init__(*args, **kwargs)
    self._special_data = {}
    self._next_custom_id = 0

  def _proceed_special(self, prefix, data):
    self._next_custom_id += 1
    data_id = prefix + str(self._next_custom_id)
    self._special_data[data_id] = data
    return data_id

  def persistent_id(self, obj):
    if _numpy is not None:
      try:
        if isinstance(obj, _numpy.ndarray):
          if obj.dtype != object:
            obj_data = {"shape": obj.shape, "data": bytearray(obj.tobytes())}
            try:
              obj_data["dtype"] = _dump_dtype(obj.dtype)
            except:
              obj_data["dtype"] = (obj.dtype,)
            return self._proceed_special("numpy.ndarray#", obj_data)
        elif isinstance(obj, _numpy.dtype):
          return self._proceed_special("numpy.dtype#", _dump_dtype(obj.dtype))
        elif _numpy.issubdtype(type(obj), _numpy.generic):
          obj_dt = _dump_dtype(obj.dtype)
          obj_data = bytearray(_numpy.array((obj,), dtype=_load_dtype(obj_dt)).tobytes())
          return self._proceed_special("numpy.generic#", {"dtype": obj_dt,  "data": obj_data})
      except:
        pass

    # This check must be here because _numpy.float64 is instance of float
    if isinstance(obj, _GENERIC_TYPES):
      return None

    try:
      obj = (True, repr(type(obj)), bytearray(pickle.dumps(obj, protocol=2, **_FIX_IMPORTS)))
    except:
      obj = (False, repr(type(obj)), None)

    return self._proceed_special("generic#", obj)

class _SafeUnpickler(_SafeUnpicklerBase):
  def __init__(self, data, *args, **kwargs):
    super(_SafeUnpickler, self).__init__(*args, **kwargs)
    self._special_data = data
    self._ignore_errors = True

  def persistent_load(self, data_id):
    if data_id not in self._special_data:
      if self.raise_on_failure:
        raise pickle.UnpicklingError('Invalid persistent id ' + str(data_id))
      return None

    obj_data = self._special_data.pop(data_id)

    try:
      if _numpy is not None:
        if data_id.startswith("numpy.ndarray#"):
          return _numpy.fromstring(bytes(obj_data["data"]), dtype=_load_dtype(obj_data["dtype"])).reshape(obj_data["shape"])
        elif data_id.startswith("numpy.dtype#"):
          return _numpy.dtype(*obj_data)
        elif data_id.startswith("numpy.generic#"):
          return _numpy.fromstring(bytes(obj_data["data"]), dtype=_load_dtype(obj_data["dtype"]))[0]

      if data_id.startswith("generic#"):
        succeeded, kind, data = obj_data
        if succeeded:
          return pickle.loads(bytes(data))

        if self._ignore_errors:
          return None

        raise pickle.UnpicklingError('Failed to transfer an object of type ' + str(kind))
    except:
      if not self._ignore_errors:
        raise
      return None


    if not self._ignore_errors:
      raise pickle.UnpicklingError('Invalid persistent id ' + str(data_id))

    return None


def _safe_pickle_dump(source, fout):
  data_stream = _BytesIO()

  if PY_2:
    # in Python 2.7 pickle.Pickler is a method rather than a class
    pickle_stream = pickle.Pickler(data_stream, protocol=2, **_FIX_IMPORTS)
    special_processor = _SafePickler()
    pickle_stream.persistent_id = special_processor.persistent_id
    pickle_stream.dump(source)
    special_data = special_processor._special_data
  else:
    pickle_stream = _SafePickler(data_stream, protocol=2, **_FIX_IMPORTS)
    pickle_stream.dump(source)
    special_data = pickle_stream._special_data

  if special_data:
    # write special uid in first part so that when loading can know to use safe load
    pickle.dump(SAFE_PICKLE_UID, fout, protocol=2, **_FIX_IMPORTS)
    pickle.dump(special_data, fout, protocol=2, **_FIX_IMPORTS)
  fout.write(data_stream.getvalue())

def _safe_pickle_load(fin):
  special_unpickler = None
  # Python 2 mode
  if PY_2:
    signture_or_data = pickle.load(fin)
    # need to use safe load for safe data dumps
    if signture_or_data == SAFE_PICKLE_UID:
      special_processor = _SafeUnpickler(pickle.load(fin))
      special_unpickler = pickle.Unpickler(fin)
      special_unpickler.persistent_load = special_processor.persistent_load
  # Python 3 mode
  else:
    signture_or_data = pickle.load(fin, fix_imports=True, encoding='latin1')
    # need to use safe load for safe data dumps
    if signture_or_data == SAFE_PICKLE_UID:
      special_payload = pickle.load(fin, fix_imports=True, encoding='latin1')
      special_unpickler = _SafeUnpickler(special_payload, fin, fix_imports=True, encoding='latin1')

  if special_unpickler is not None:
    return special_unpickler.load()
  # for "usual" dumps, additional load is not required, since the data has already been loaded in first part
  return signture_or_data
