# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

import sys
import ipaddress
from threading import RLock

from ctypes import byref, c_int32, cast, c_char_p, c_void_p, c_size_t, c_uint32, POINTER
from typing import Any

from .group import GroupDelegate, Group
from .type_utils import (create_string_buffer_compat, decode_string_buffer, to_mac_address)
from .ffi.enums import StatusSuccess
from .ffi import api
from .ffi.wrappers import UnmanagedObject
from .ffi.ctypes_defs import HebiMacAddress
HebiMacAddressPtr = POINTER(HebiMacAddress)
HebiMacAddressPtrPtr = POINTER(HebiMacAddressPtr)


################################################################################
# Mac Address
################################################################################


class MacAddress:
  """A simple wrapper class for internal C-API HebiMacAddress objects to allow
  interfacing with API calls that use MAC addresses."""

  __slots__ = ['_obj']

  def __init__(self, a: int, b: int, c: int, d: int, e: int, f: int):
    obj = HebiMacAddress()
    obj.bytes_[0:6] = [a, b, c, d, e, f]

    self._obj = obj

  def __repr__(self):
    return self.__human_readable()

  def __str__(self):
    return self.__human_readable()

  def __getitem__(self, item):
    return self._obj.bytes_[item]

  def __human_readable(self):
    b0 = "%0.2X" % self._obj.bytes_[0]
    b1 = "%0.2X" % self._obj.bytes_[1]
    b2 = "%0.2X" % self._obj.bytes_[2]
    b3 = "%0.2X" % self._obj.bytes_[3]
    b4 = "%0.2X" % self._obj.bytes_[4]
    b5 = "%0.2X" % self._obj.bytes_[5]
    return f'{b0}:{b1}:{b2}:{b3}:{b4}:{b5}'

  @property
  def _as_parameter_(self):
    return self._obj

  @property
  def raw_bytes(self):
    """An unsigned byte buffer view of the object (ctypes c_ubyte array).

    Use this if you need a serialized format of this object, or if you
    are marshalling data to an external C API, etc.
    """
    return self._obj.bytes_


################################################################################
# Lookup Entries
################################################################################


class Entry:
  """Represents a HEBI module.

  This is used by the Lookup class.
  """

  __slots__ = ['_family', '_ip_address', '_mac_address', '_name', '_is_stale']

  def __init__(self, name: str, family: str, mac_address: MacAddress, ip_address: int, is_stale: int):
    self._name = name
    self._family = family
    self._mac_address = mac_address

    # get the byte order right
    addr = int.from_bytes(ip_address.to_bytes(4, 'big'), sys.byteorder)
    self._ip_address = ipaddress.ip_address(addr)

    self._is_stale = is_stale == 1

  def __repr__(self):
    return self.__human_readable()

  def __str__(self):
    return self.__human_readable()

  def __human_readable(self):
    return f'Family: {self.family} Name: {self.name} Mac Address: {self.mac_address}'

  @property
  def name(self):
    """
    :return: The name of the module.
    :rtype:  str
    """
    return self._name

  @property
  def family(self):
    """
    :return: The family to which this module belongs.
    :rtype:  str
    """
    return self._family

  @property
  def mac_address(self):
    """
    :return: The immutable MAC address of the module.
    :rtype:  str
    """
    return self._mac_address

  @property
  def ip_address(self):
    """
    :return: The IP address of the module.
    :rtype:  str
    """
    return self._ip_address

  @property
  def is_stale(self):
    """
    :return: True if the module can no longer be found on the network
    :rtype: bool
    """
    return self._is_stale

class EntryList(UnmanagedObject):
  """A list of module entries.

  This is used by the :class:`~hebi.Lookup` class and is returned by
  :attr:`~hebi.Lookup.entrylist`.
  """
  __slots__ = ['_elements', '_iterator', '_size']

  def __init__(self, internal):
    super().__init__(internal, on_delete=api.hebiLookupEntryListRelease)
    bypass_debug_printing = True
    if bypass_debug_printing:  # with bypass_debug_printing:
      # In debug mode, this tries to call repr(self) before everything is initialized,
      # which makes Python complain. So scope to bypass debug printing.
      # If debug mode is not enabled, this does not change any behavior.
      self._size = api.hebiLookupEntryListGetSize(self)
      elements: 'list[Entry | None]' = list()
      for i in range(self._size):
        elements.append(self.__get_entry(i))
      self._elements = elements
      self._iterator = iter(elements)

  def __iter__(self):
    return self

  def __next__(self):
    try:
      return next(self._iterator)
    except StopIteration:
      # PEP 479 forbids the implicit propagation of StopIteration
      raise StopIteration

  def __repr__(self):
    return self.__human_readable()

  def __str__(self):
    return str([str(entry) for entry in self._elements])

  def __human_readable(self):
    modules: 'list[Entry | None]' = list()
    for entry in self._elements:
      modules.append(entry)
    from .utils import lookup_table_string
    return lookup_table_string(modules)

  def __get_entry(self, index):
    required_size = c_size_t(0)

    if (api.hebiLookupEntryListGetName(self, index, c_char_p(None), byref(required_size)) != StatusSuccess):
      return None
    c_buffer = create_string_buffer_compat(required_size.value)
    if (api.hebiLookupEntryListGetName(self, index, c_buffer, byref(required_size)) != StatusSuccess):
      return None
    name = decode_string_buffer(c_buffer, 'utf-8')

    if (api.hebiLookupEntryListGetFamily(self._internal, index, c_char_p(None), byref(required_size)) != StatusSuccess):
      return None
    c_buffer = create_string_buffer_compat(required_size.value)
    if (api.hebiLookupEntryListGetFamily(self._internal, index, c_buffer, byref(required_size)) != StatusSuccess):
      return None
    family = decode_string_buffer(c_buffer, 'utf-8')

    tmp_buffer = HebiMacAddress()
    if (api.hebiLookupEntryListGetMacAddress(self._internal, index, byref(tmp_buffer)) != StatusSuccess):
      return None

    ip_addr = c_uint32()
    if (api.hebiLookupEntryListGetIpAddress(self._internal, index, byref(ip_addr)) != StatusSuccess):
      return None

    is_stale = c_int32()
    if (api.hebiLookupEntryListGetIsStale(self._internal, index, byref(is_stale)) != StatusSuccess):
      return None

    if name is None or family is None:
      return None
    return Entry(name, family, MacAddress(*tmp_buffer.bytes_), ip_addr.value, is_stale.value)

  def __getitem__(self, index):
    return self.__get_entry(index)


################################################################################
# Lookup and delegates
################################################################################


class Lookup:
  """Maintains a registry of network-connected modules and returns
  :class:`hebi._internal.group.Group` objects to the user."""

  DEFAULT_TIMEOUT_MS = 500
  """
  The default timeout (in milliseconds)
  """

  __slots__ = ['__delegate']

  def __init__(self, interfaces: 'list[str]' = []):
    self.__delegate = LookupDelegate.get_singleton(interfaces)

  def __repr__(self):
    lookup_freq = self.lookup_frequency
    # We can't get lookup addresses from C API yet, so nothing to print re: that
    ret = f'lookup_frequency: {lookup_freq}\n\n'
    # Mobules table
    from .._internal.utils import lookup_table_string
    return ret + lookup_table_string([entry for entry in self.entrylist])

  def __str__(self):
    lookup_freq = self.lookup_frequency
    modules = [entry for entry in self.entrylist]
    modules_string = None
    num_modules = len(modules)
    if num_modules > 1:
      modules_string = f'{num_modules} modules'
    elif num_modules == 1:
      modules_string = '1 module'
    else:
      modules_string = 'no modules'
    return f'Lookup(lookup_frequency={lookup_freq}; {modules_string} found)'

  def reset(self):
    """Refresh the network lookup to remove stale modules."""
    self.__delegate.reset()

  @property
  def entrylist(self):
    """A list of discovered network connected modules.

    :return: The list of modules
    :rtype: EntryList
    """
    return self.__delegate.entrylist

  @property
  def lookup_frequency(self):
    return self.__delegate.lookup_frequency

  @lookup_frequency.setter
  def lookup_frequency(self, freq):
    self.__delegate.lookup_frequency = freq

  def get_group_from_names(self, families: 'str | list[str]', names: 'str | list[str]', timeout_ms: 'float | None' = None):
    """Get a group from modules with the given names and families.

    If the families or names provided as input is only a single element,
    then that element is assumed to pair with each item in the other parameter.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after :attr:`Lookup.DEFAULT_TIMEOUT_MS` milliseconds,
    if a matching group cannot be constructed.

    :param families:   A family or list of families corresponding to the device(s) to include in the Group
    :type families:    string or list

    :param names:      A name or list of names corresponding to the device(s) to include in the Group
    :type names:       string or list

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Lookup.DEFAULT_TIMEOUT_MS`.

    :return: A group on success; ``None`` if one or more devices specified could not be found
    :rtype: hebi._internal.group.Group
    """
    if not isinstance(families, list):
      families = [families]
    if not isinstance(names, list):
      names = [names]
    return self.__delegate.get_group_from_names(families, names, timeout_ms)

  def get_group_from_macs(self, addresses, timeout_ms=None):
    """Get a group from modules with the given mac addresses.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after :attr:`Lookup.DEFAULT_TIMEOUT_MS` milliseconds,
    if a matching group cannot be constructed.

    A mac address can be represented by a string or by a 6 element list of bytes::

      grp1 = lookup.get_group_from_macs(['aa:bb:cc:dd:ee:ff'])
      grp2 = lookup.get_group_from_macs([[0, 0, 42, 42, 42, 42]])


    :param addresses:  A list of mac addresses specifying the devices to include in the Group
    :type addresses:   list

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Lookup.DEFAULT_TIMEOUT_MS`.

    :return: A group on success; ``None`` if one or more devices specified could not be found
    :rtype: hebi._internal.group.Group
    """
    return self.__delegate.get_group_from_macs(addresses, timeout_ms)

  def get_group_from_family(self, family: str, timeout_ms=None):
    """Get a group from all known modules with the given family.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after :attr:`Lookup.DEFAULT_TIMEOUT_MS` milliseconds,
    if a matching group cannot be constructed.

    :param family:     The family of the devices to include in the Group
    :type family:      str

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Lookup.DEFAULT_TIMEOUT_MS`.

    :return: A group on success; ``None`` if one or more devices specified could not be found
    :rtype: hebi._internal.group.Group
    """
    return self.__delegate.get_group_from_family(family, timeout_ms)

  def get_connected_group_from_name(self, family, name, timeout_ms=None):
    """Get a group from all modules known to connect to a module with the given
    name and family.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after :attr:`Lookup.DEFAULT_TIMEOUT_MS` milliseconds,
    if a matching group cannot be constructed.

    :param family:     The family of the connected device, used to create the Group
    :type family:      str

    :param name:       The name of the connected device, used to create the Group
    :type name:        str

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Lookup.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int, float

    :return: A group on success; ``None`` if one or more devices specified could not be found
    :rtype: hebi._internal.group.Group
    """
    return self.__delegate.get_connected_group_from_name(family, name, timeout_ms)

  def get_connected_group_from_mac(self, address, timeout_ms=None):
    """Get a group from all modules known to connect to a module with the given
    mac address.

    This is a blocking call which returns a Group with the given parameters.
    This will time out after :attr:`Lookup.DEFAULT_TIMEOUT_MS` milliseconds,
    if a matching group cannot be constructed.

    A mac address can be represented by a string or by a 6 element list of bytes::

      grp1 = lookup.get_connected_group_from_mac('aa:bb:cc:dd:ee:ff')
      grp2 = lookup.get_connected_group_from_mac([0, 0, 42, 42, 42, 42])


    :param address:    The mac address of the connected device, used to create the Group
    :type address:     str, list

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Lookup.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int, float

    :return: A group on success; ``None`` if one or more devices specified could not be found
    :rtype: hebi._internal.group.Group
    """
    return self.__delegate.get_connected_group_from_mac(address, timeout_ms)


class LookupDelegate(UnmanagedObject):
  """Delegate for Lookup."""

  __slots__ = ['interfaces']

  __singleton: 'LookupDelegate | None' = None
  __singleton_lock = RLock()

  @staticmethod
  def get_singleton(interfaces: 'list[str]' = []):
    with LookupDelegate.__singleton_lock:
      if LookupDelegate.__singleton is None:
        LookupDelegate.__singleton = LookupDelegate(interfaces)
      elif interfaces != LookupDelegate.__singleton.interfaces:
        LookupDelegate.__singleton.reset(interfaces)
    return LookupDelegate.__singleton

  def __parse_to(self, timeout_ms: 'Any | None'):
    if timeout_ms is None:
      return Lookup.DEFAULT_TIMEOUT_MS
    else:
      try:
        return int(timeout_ms)
      except:
        raise ValueError('timeout_ms must be a number')

  def __init__(self, interfaces: 'list[str]' = []):
    self.interfaces = interfaces

    if_buffer, if_length = self.__string_list_to_c_char_p_arr(interfaces)
    super().__init__(api.hebiLookupCreate(cast(byref(if_buffer), POINTER(c_char_p)), if_length), on_delete=api.hebiLookupRelease)

  def reset(self, interfaces: 'list[str]' = []):
    with LookupDelegate.__singleton_lock:
      self.interfaces = interfaces
      if_buffer, if_length = self.__string_list_to_c_char_p_arr(interfaces)
      api.hebiLookupReset(self, cast(byref(if_buffer), POINTER(c_char_p)), if_length)

  @staticmethod
  def __string_list_to_c_char_p_arr(string_list):
    buffer = (c_char_p * len(string_list))()
    for idx, s in enumerate(string_list):
      buffer[idx] = cast(create_string_buffer_compat(s, len(s)+1), c_char_p)

    return buffer, len(string_list)

  @property
  def entrylist(self):
    list = api.hebiCreateLookupEntryList(self)
    if list:
      return EntryList(list)

    raise RuntimeError('API function hebiCreateLookupEntryList returned null pointer.'
                       'This should never happen')

  @property
  def lookup_frequency(self):
    return api.hebiLookupGetLookupFrequencyHz(self)

  @lookup_frequency.setter
  def lookup_frequency(self, freq):
    api.hebiLookupSetLookupFrequencyHz(self, freq)

  def get_group_from_names(self, families: 'list[str] | str', names: 'list[str] | str', timeout_ms: 'Any | None' = None):
    timeout_ms = self.__parse_to(timeout_ms)
    families_length = len(families)
    names_length = len(names)

    families_buffer = (c_char_p * families_length)()
    families_buffer_list = [create_string_buffer_compat(family, len(family)+1) for family in families]
    names_buffer = (c_char_p * names_length)()
    names_buffer_list = [create_string_buffer_compat(name, len(name)+1) for name in names]

    for i in range(families_length):
      families_buffer[i] = cast(families_buffer_list[i], c_char_p)

    for i in range(names_length):
      names_buffer[i] = cast(names_buffer_list[i], c_char_p)

    c_char_pp = POINTER(c_char_p)
    group = c_void_p(api.hebiGroupCreateFromNames(self,
                                                  cast(byref(families_buffer), c_char_pp),
                                                  families_length,
                                                  cast(byref(names_buffer), c_char_pp),
                                                  names_length,
                                                  timeout_ms))

    if group:
      return Group(GroupDelegate(group))
    return None

  def get_group_from_macs(self, addresses: 'list[Any]', timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    addresses_length = len(addresses)
    addresses_list = [to_mac_address(address) for address in addresses]

    addresses_list_c = (HebiMacAddressPtr * addresses_length)()
    for i in range(addresses_length):
      addresses_list_c[i] = HebiMacAddressPtr(addresses_list[i]._as_parameter_)

    group = c_void_p(api.hebiGroupCreateFromMacs(self, cast(addresses_list_c, HebiMacAddressPtrPtr),
                                                 addresses_length, timeout_ms))

    if group:
      return Group(GroupDelegate(group))
    return None

  def get_group_from_family(self, family, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    family_buffer = create_string_buffer_compat(family, len(family)+1)
    group = c_void_p(api.hebiGroupCreateFromFamily(self, family_buffer, timeout_ms))

    if (group):
      return Group(GroupDelegate(group))
    return None

  def get_connected_group_from_name(self, family, name, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    family_buffer = create_string_buffer_compat(family, len(family)+1)
    name_buffer = create_string_buffer_compat(name, len(name)+1)
    group = c_void_p(api.hebiGroupCreateConnectedFromName(self, family_buffer,
                                                          name_buffer, timeout_ms))

    if group:
      return Group(GroupDelegate(group))
    return None

  def get_connected_group_from_mac(self, address, timeout_ms=None):
    timeout_ms = self.__parse_to(timeout_ms)
    mac_address = to_mac_address(address)
    group = c_void_p(api.hebiGroupCreateConnectedFromMac(self, mac_address.raw_bytes,
                                                         timeout_ms))

    if group:
      return Group(GroupDelegate(group))
    return None
