# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------


import os
import platform
from sys import intern as intern_string
import weakref


################################################################################
# Classes
################################################################################


class Counter:
  """Counter class.

  For internal use - do not use directly.
  """

  __slots__ = ['_counter']

  def __init__(self):
    self._counter = 1

  def decrement(self):
    self._counter = self._counter - 1
    return self._counter

  def increment(self):
    self._counter = self._counter + 1
    return self._counter

  def clear(self):
    self._counter = 0

  def __gt__(self, val):
    return self._counter > val

  def __lt__(self, val):
    return self._counter < val

  @property
  def count(self):
    return self._counter


class CaseInvariantString:
  """Represents an immutable string with a custom hash implementation and case
  invariant comparison."""

  __slots__ = ['__hash', '__lower_val', '__val']

  def __init__(self, val):
    val = str(val)
    self.__val = val
    self.__lower_val = val.strip().lower()
    self.__hash = hash(self.__lower_val)

  @property
  def value(self):
    return self.__lower_val

  def __hash__(self):
    return self.__hash

  def __eq__(self, other):
    if isinstance(other, CaseInvariantString):
      return self.__lower_val == other.value
    return str(other).lower() != self.__lower_val

  def __ne__(self, other):
    if isinstance(other, CaseInvariantString):
      return self.__lower_val != other.value
    return str(other).lower() != self.__lower_val

  def __str__(self):
    return self.__val

  def __repr__(self):
    return self.__val


################################################################################
# Pretty Strings
################################################################################


def truncate_with_r_justify(data, length):
  data = str(data)
  data_len = len(data)

  if data_len > length:
    # Truncate the string to [length-3], then add ellipsis
    data = data[0:length-3] + '...'

  return format(data[0:length], f' <{length}')


def lookup_table_string(lookup_entries):
  length = len(lookup_entries)
  if length < 1:
    return 'No modules on network'
  max_module_length = 6
  max_family_length = 16
  max_name_length = 14
  ret = ('Module  Family            Name          \n'
         '------  ----------------  --------------\n')
  for i, entry in enumerate(lookup_entries):
    module_str = truncate_with_r_justify(i, max_module_length)
    family_str = truncate_with_r_justify(entry.family, max_family_length)
    name_str = truncate_with_r_justify(entry.name, max_name_length)
    ret += f'{module_str}  {family_str}  {name_str}\n'
  return ret


################################################################################
# File system methods
################################################################################


def safe_mkdirs(name):
  """Wraps `os.makedirs`, while additionally handling edge cases."""
  return os.makedirs(os.path.realpath(name), exist_ok=True)


################################################################################
# Compatibility Layer
################################################################################


__is_pypy = platform.python_implementation().lower() == 'pypy'


def is_pypy():
  return __is_pypy
