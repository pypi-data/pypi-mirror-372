#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present

"""
Simplified implementation for Abstract Base Classes (ABC) for python < 2.6
---------------------------

.. currentmodule:: da.p7core.utils.abc

"""

def abstractmethod(funcobj):
  funcobj.__isabstractmethod__ = True
  return funcobj

class abstractproperty(property):
  __isabstractmethod__ = True

class ABCMeta(type):
  def __new__(mcls, name, bases, namespace):
    cls = super(ABCMeta, mcls).__new__(mcls, name, bases, namespace)
    abstracts = set(name
                 for name, value in namespace.items()
                 if getattr(value, "__isabstractmethod__", False))
    for base in bases:
      for name in getattr(base, "__abstractmethods__", set()):
        value = getattr(cls, name, None)
        if getattr(value, "__isabstractmethod__", False):
          abstracts.add(name)
    cls.__abstractmethods__ = frozenset(abstracts)
    cls.__new__ = staticmethod(cls.new)
    return cls

  def new(self, cls, *args, **kwargs):
    if len(cls.__abstractmethods__):
      error_message = "Can't instantiate abstract class " + cls.__name__ + \
                      " with abstract methods:\n" + '\n  '.join(cls.__abstractmethods__)
      raise TypeError(error_message)
    return object.__new__(cls)
