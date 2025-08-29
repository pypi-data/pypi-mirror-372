# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2022 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

from typing import Generic, TypeVar
import typing
import threading
import numpy as np
import ctypes
from ctypes import byref, Array, cast, sizeof

from ..graphics import Color, color_from_int, string_to_color
from . import api, enums
from .wrappers import MessageEnum, UnmanagedObject, WeakReferenceContainer  # TODO: fix import
from ..type_utils import decode_string_buffer as decode_str  # TODO: fix import
from ..type_utils import create_string_buffer_compat as create_str  # TODO: fix import

from .ctypes_defs import HebiCommandMetadata, HebiFeedbackMetadata, HebiInfoMetadata, HebiHighResAngleStruct
from .ctypes_utils import cast_to_float_ptr, c_bool_p, c_float_p, c_double_p, c_uint64_p, c_int32_p, c_int64_p


_command_metadata = HebiCommandMetadata()
_feedback_metadata = HebiFeedbackMetadata()
_info_metadata = HebiInfoMetadata()
api.hebiCommandGetMetadata(byref(_command_metadata))
api.hebiFeedbackGetMetadata(byref(_feedback_metadata))
api.hebiInfoGetMetadata(byref(_info_metadata))


BankType = TypeVar('BankType')
Scalar = TypeVar('Scalar')

if typing.TYPE_CHECKING:
  from typing import Any, Callable, Union, Iterable, Sequence, Protocol
  import numpy.typing as npt
  from .ctypes_defs import HebiCommandRef, HebiFeedbackRef, HebiInfoRef
  from ._message_types import Command, Info, Feedback, GroupCommandBase, GroupInfoBase, GroupFeedbackBase
  HebiRef = Union[HebiCommandRef, HebiFeedbackRef, HebiInfoRef]
  ArrayHebiRefs = Union[Array[HebiCommandRef], Array[HebiFeedbackRef], Array[HebiInfoRef]]
  from ..graphics import Color
  Colorable = Union[Color, int, str]

  class HasGroupBaseRefProtocol(Protocol):
    def _get_ref(self) -> 'GroupCommandBase | GroupFeedbackBase | GroupInfoBase': ...

  class HasRefProtocol(Protocol):
    _ref: 'HebiCommandRef | HebiFeedbackRef | HebiInfoRef'
else:
  class Protocol:
    ...

  class HasGroupBaseRefProtocol:
    ...

  class HasRefProtocol:
    ...


################################################################################
# Pretty Printers
################################################################################


def _fmt_float_array(array: 'list[float]'):
  return '[' + ', '.join([f'{i:.2f}' for i in array]) + ']'


def _numbered_float_repr(c: 'Any', enum_type: 'MessageEnum'):
  try:
    enum_name = enum_type.name
  except:
    enum_name = enum_type
  desc = f'Numbered float (Enumeration {enum_name}):'
  try:
    _ = c._get_ref()
    return '\n'.join([
      desc,
      f'  float1: {_fmt_float_array(c.float1)}',
      f'  float2: {_fmt_float_array(c.float2)}',
      f'  float3: {_fmt_float_array(c.float3)}',
      f'  float4: {_fmt_float_array(c.float4)}',
      f'  float5: {_fmt_float_array(c.float5)}',
      f'  float6: {_fmt_float_array(c.float6)}',
      f'  float7: {_fmt_float_array(c.float7)}',
      f'  float8: {_fmt_float_array(c.float8)}',
      f'  float9: {_fmt_float_array(c.float9)}'
    ])
  except RuntimeError:
    return desc + '  <Group message was finalized>'


def _fmt_io_bank_pin(pins: 'Sequence', indent: int = 4):
  indent_str = ''.join([' '] * indent)
  pins_has_i = pins[1]
  pins_i = pins[1]
  pins_has_f = pins[2]
  pins_f = pins[3]

  pins_i_str = '[' + ', '.join([(f'{entry:9g}' if has_entry else "     None") for has_entry, entry in zip(pins_has_i, pins_i)]) + ']'
  pins_f_str = '[' + ', '.join([(f'{entry:9.8g}' if has_entry else "     None") for has_entry, entry in zip(pins_has_f, pins_f)]) + ']'

  res = f'{indent_str}Int:   {pins_i_str}\n{indent_str}Float: {pins_f_str}'
  if len(pins) <= 4:
    return res

  pins_l = pins[4]
  pins_l_str = '[' + ', '.join([format(entry or "None", ">9s") for entry in pins_l]) + ']'
  res += f'\n{indent_str}Label: {pins_l_str}'
  return res


def _fmt_io_info_bank_pin(pins, indent: int = 4):
  indent_str = ''.join([' '] * indent)
  pins_str = '[' + ', '.join([format(entry or "None", ">9s") for entry in pins]) + ']'
  return f'{indent_str}Label: {pins_str}'


def _io_bank_repr(bank_container: 'GroupFeedbackIoFieldBank | GroupCommandIoFieldBank', bank: 'MessageEnum', bank_readable: str):
  try:
    enum_name = bank.name
  except:
    enum_name = bank
  desc = f'IO Bank \'{bank_readable}\' (Enumeration {enum_name}):\n'
  try:
    io_container = bank_container._get_ref()
  except RuntimeError:
    # Handles the case where IO Container object was finalized already
    return desc + "  <IO Container was finalized>"

  def get_fmt_pin(pin: int):
    fields = [bank_container.has_int(pin), bank_container.get_int(pin), bank_container.has_float(pin), bank_container.get_float(pin)]
    if isinstance(io_container, GroupCommandIoField):
      fields.append(io_container.get_label(bank, pin))
    return _fmt_io_bank_pin(fields)

  return (desc +\
      f'  Pin 1:\n{get_fmt_pin(1)}\n'
      f'  Pin 2:\n{get_fmt_pin(2)}\n'
      f'  Pin 3:\n{get_fmt_pin(3)}\n'
      f'  Pin 4:\n{get_fmt_pin(4)}\n'
      f'  Pin 5:\n{get_fmt_pin(5)}\n'
      f'  Pin 6:\n{get_fmt_pin(6)}\n'
      f'  Pin 7:\n{get_fmt_pin(7)}\n'
      f'  Pin 8:\n{get_fmt_pin(8)}\n')


def _io_info_bank_repr(bank_container: 'GroupInfoIoFieldBank', bank: 'MessageEnum', bank_readable):
  try:
    enum_name = bank.name
  except:
    enum_name = bank
  desc = f'IO Bank \'{bank_readable}\' (Enumeration {enum_name}):\n'
  try:
    _ = bank_container._get_ref()
  except RuntimeError:
    # Handles the case where IO Container object was finalized already
    return desc + "  <IO Container was finalized>"

  def get_fmt_pin(pin):
    return _fmt_io_info_bank_pin(bank_container.get_label(pin))

  return (desc +\
      f'  Pin 1:\n{get_fmt_pin(1)}\n'
      f'  Pin 2:\n{get_fmt_pin(2)}\n'
      f'  Pin 3:\n{get_fmt_pin(3)}\n'
      f'  Pin 4:\n{get_fmt_pin(4)}\n'
      f'  Pin 5:\n{get_fmt_pin(5)}\n'
      f'  Pin 6:\n{get_fmt_pin(6)}\n'
      f'  Pin 7:\n{get_fmt_pin(7)}\n'
      f'  Pin 8:\n{get_fmt_pin(8)}\n')


def _io_repr(io: 'GroupInfoIoField'):
  try:
    _ = io._get_ref()
    return '\n'.join([
      'IO Banks: [A, B, C, D, E, F]',
      str(io.a), str(io.b), str(io.c),
      str(io.d), str(io.e), str(io.f)
    ])
  except RuntimeError:
    return 'IO Banks: [A, B, C, D, E, F]\n  <Group message was finalized>'


################################################################################
# Numbered Fields
################################################################################

################################################################################
# `has` creators
################################################################################


def create_numbered_float_group_has(refs, field: 'MessageEnum', has: 'Callable', metadata: 'HebiCommandMetadata | HebiFeedbackMetadata | HebiInfoMetadata'):
  """Returns a callable which accepts 1 argument."""
  relative_offset = int(metadata.numbered_float_relative_offsets_[int(field)])
  bit_index = metadata.numbered_float_field_bitfield_offset_ + relative_offset
  size = len(refs)

  def ret_has(number: int) -> 'npt.NDArray[np.bool_]':
    out = np.empty(size, dtype=bool)
    has(out.ctypes.data_as(c_bool_p), refs, size, bit_index + number)
    return out
  return ret_has


def create_io_group_has(refs, has):
  """Returns a callable which accepts 2 arguments."""
  size = len(refs)

  def ret_has(field: 'MessageEnum', number: int):
    out = np.empty(size, dtype=bool)
    has(out.ctypes.data_as(c_bool_p), refs, size, number - 1, field.value)
    return out
  return ret_has


################################################################################
# `getter` creators
################################################################################


def create_numbered_float_group_getter(refs: 'ArrayHebiRefs', field: 'MessageEnum', getter: 'Callable[..., Any]'):
  """Returns a callable which accepts 1 argument."""
  size = len(refs)

  def ret_getter(number: int):
    out = np.empty(size, dtype=np.float32)
    getter(out.ctypes.data_as(c_float_p), refs, size, number - 1, field.value)
    return out
  return ret_getter


def create_io_float_group_getter(refs, getter):
  """Returns a callable which accepts 2 arguments."""
  size = len(refs)

  def ret_getter(field: 'MessageEnum', number: int):
    out = np.empty(size, dtype=np.float32)
    getter(out.ctypes.data_as(c_float_p), refs, size, number - 1, field.value)
    return out
  return ret_getter


def create_io_int_group_getter(refs, getter):
  """Returns a callable which accepts 2 arguments."""
  size = len(refs)

  def ret_getter(field: 'MessageEnum', number: int):
    out = np.empty(size, dtype=np.int64)
    getter(out.ctypes.data_as(c_int64_p), refs, size, number - 1, field.value)
    return out
  return ret_getter


################################################################################
# `setter` creators
################################################################################


def create_numbered_float_group_setter(refs, field, setter):
  """Returns a callable which accepts 2 arguments."""
  size = len(refs)

  def ret_setter(number: int, value: 'float | Sequence[float] | None'):
    if value is None:
      bfr = None
    else:
      _tls.ensure_capacity(size)
      bfr = _tls.c_float_array
      if isinstance(value, (int, float)):
        for i in range(size):
          bfr[i] = value
      else:
        for i in range(size):
          bfr[i] = value[i]

    setter(refs, bfr, size, number - 1, field.value)
  return ret_setter


def create_io_float_group_setter(refs, setter):
  """Returns a callable which accepts 3 arguments."""
  size = len(refs)

  def ret_setter(field: 'MessageEnum', number: int, value: 'float | Sequence[float] | None'):
    if value is None:
      bfr = None
    else:
      _tls.ensure_capacity(size)
      bfr = _tls.c_float_array
      if isinstance(value, (int, float)):
        for i in range(size):
          bfr[i] = value
      else:
        for i in range(size):
          bfr[i] = value[i]

    setter(refs, bfr, size, number - 1, field.value)
  return ret_setter


def create_io_int_group_setter(refs, setter):
  """Returns a callable which accepts 3 arguments."""
  size = len(refs)

  def ret_setter(field: 'MessageEnum', number: int, value: 'float | Sequence[float] | None'):
    if value is None:
      bfr = None
    else:
      _tls.ensure_capacity(size)
      bfr = _tls.c_int64_array
      if isinstance(value, (int, float)):
        for i in range(size):
          bfr[i] = value
      else:
        for i in range(size):
          bfr[i] = value[i]

    setter(refs, bfr, size, number - 1, field.value)
  return ret_setter


def create_led_group_setter(refs: 'Array[HebiCommandRef]', field: 'MessageEnum', setter: 'Callable[..., None]'):
  """Returns a callable which accepts 1 argument."""
  size = len(refs)

  def ret_setter(value: 'Array[ctypes.c_int32] | None'):
    _tls.ensure_capacity(size)
    setter(refs, value, size, field.value)
  return ret_setter


def create_numbered_float_single_getter(ref, field: 'MessageEnum', getter):
  def ret_getter(number: int):
    ret = _tls.c_float
    getter(byref(ref), byref(ret), 1, number, field.value)
    return ret.value
  return ret_getter


################################################################################
# Classes
################################################################################


class GroupFeedbackNumberedFloatField(WeakReferenceContainer["GroupFeedbackBase"]):
  """A read only view into a set of numbered float fields."""

  __slots__ = ['_getter', '_has', '_field']

  def __init__(self, internal: 'GroupFeedbackBase', field: 'MessageEnum'):
    super().__init__(internal)
    self._field = field
    self._getter = create_numbered_float_group_getter(internal._refs, enums.FeedbackNumberedFloatField.Debug, api.hwFeedbackGetNumberedFloat)
    self._has = create_numbered_float_group_has(internal._refs, enums.FeedbackNumberedFloatField.Debug, api.hwFeedbackHasField, _feedback_metadata)

  def __repr__(self):
    return _numbered_float_repr(self, self._field)

  @property
  def has_float1(self):
    return self._has(1)

  @property
  def has_float2(self):
    return self._has(2)

  @property
  def has_float3(self):
    return self._has(3)

  @property
  def has_float4(self):
    return self._has(4)

  @property
  def has_float5(self):
    return self._has(5)

  @property
  def has_float6(self):
    return self._has(6)

  @property
  def has_float7(self):
    return self._has(7)

  @property
  def has_float8(self):
    return self._has(8)

  @property
  def has_float9(self):
    return self._has(9)

  @property
  def float1(self):
    return self._getter(1)

  @property
  def float2(self):
    return self._getter(2)

  @property
  def float3(self):
    return self._getter(3)

  @property
  def float4(self):
    return self._getter(4)

  @property
  def float5(self):
    return self._getter(5)

  @property
  def float6(self):
    return self._getter(6)

  @property
  def float7(self):
    return self._getter(7)

  @property
  def float8(self):
    return self._getter(8)

  @property
  def float9(self):
    return self._getter(9)


class GroupCommandNumberedFloatField(WeakReferenceContainer["GroupCommandBase"]):
  """A mutable view into a set of numbered float fields."""

  __slots__ = ['_getter', '_has', '_setter', '_field']

  def __init__(self, internal: 'GroupCommandBase', field: 'MessageEnum'):
    super().__init__(internal)
    self._field = field
    self._getter = create_numbered_float_group_getter(internal._refs, enums.CommandNumberedFloatField.Debug, api.hwCommandGetNumberedFloat)
    self._has = create_numbered_float_group_has(internal._refs, enums.CommandNumberedFloatField.Debug, api.hwCommandHasField, _command_metadata)
    self._setter = create_numbered_float_group_setter(internal._refs, enums.CommandNumberedFloatField.Debug, api.hwCommandSetNumberedFloat)

  def __repr__(self):
    return _numbered_float_repr(self, self._field)

  @property
  def has_float1(self):
    return self._has(1)

  @property
  def has_float2(self):
    return self._has(2)

  @property
  def has_float3(self):
    return self._has(3)

  @property
  def has_float4(self):
    return self._has(4)

  @property
  def has_float5(self):
    return self._has(5)

  @property
  def has_float6(self):
    return self._has(6)

  @property
  def has_float7(self):
    return self._has(7)

  @property
  def has_float8(self):
    return self._has(8)

  @property
  def has_float9(self):
    return self._has(9)

  @property
  def float1(self):
    return self._getter(1)

  @property
  def float2(self):
    return self._getter(2)

  @property
  def float3(self):
    return self._getter(3)

  @property
  def float4(self):
    return self._getter(4)

  @property
  def float5(self):
    return self._getter(5)

  @property
  def float6(self):
    return self._getter(6)

  @property
  def float7(self):
    return self._getter(7)

  @property
  def float8(self):
    return self._getter(8)

  @property
  def float9(self):
    return self._getter(9)

  @float1.setter
  def float1(self, value: float):
    self._setter(1, value)

  @float2.setter
  def float2(self, value: float):
    self._setter(2, value)

  @float3.setter
  def float3(self, value: float):
    self._setter(3, value)

  @float4.setter
  def float4(self, value: float):
    self._setter(4, value)

  @float5.setter
  def float5(self, value: float):
    self._setter(5, value)

  @float6.setter
  def float6(self, value: float):
    self._setter(6, value)

  @float7.setter
  def float7(self, value: float):
    self._setter(7, value)

  @float8.setter
  def float8(self, value: float):
    self._setter(8, value)

  @float9.setter
  def float9(self, value: float):
    self._setter(9, value)


class IoField(Generic[BankType], Protocol):
  _a: 'BankType'
  _b: 'BankType'
  _c: 'BankType'
  _d: 'BankType'
  _e: 'BankType'
  _f: 'BankType'
  banks: 'dict[MessageEnum, BankType]'

  @property
  def a(self):
    return self._a

  @property
  def b(self):
    return self._b

  @property
  def c(self):
    return self._c

  @property
  def d(self):
    return self._d

  @property
  def e(self):
    return self._e

  @property
  def f(self):
    return self._f


class IoPinBank(HasRefProtocol, Protocol):
  _relative_offset: int
  _bitfield_offset: int

  def has_int(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    ref = self._ref

    relative_idx = self._relative_offset + pin_number - 1
    bit_idx = self._bitfield_offset + relative_idx

    pin = ref.io_fields_[relative_idx]
    is_int = (pin.stored_type_ == 1) # 1 for int, 2 for float
    bit_set = (ref.message_bitfield_[bit_idx // 32] >> (bit_idx % 32)) & 1
    return is_int and bit_set

  def has_float(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    ref = self._ref

    relative_idx = self._relative_offset + pin_number - 1
    bit_idx = self._bitfield_offset + relative_idx

    pin = ref.io_fields_[relative_idx]
    is_float = (pin.stored_type_ == 2) # 1 for int, 2 for float
    bit_set = (ref.message_bitfield_[bit_idx // 32] >> (bit_idx % 32)) & 1
    return is_float and bit_set

  def get_int(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    relative_idx = self._relative_offset + pin_number - 1

    if self.has_int(pin_number):
      return self._ref.io_fields_[relative_idx].int_value_
    else:
      return 0

  def get_float(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    ref = self._ref

    relative_idx = self._relative_offset + pin_number - 1

    if self.has_float(pin_number):
      return ref.io_fields_[relative_idx].float_value_
    else:
      return np.nan


class GroupIoPinBank(HasGroupBaseRefProtocol, Protocol):
  """Mixin for Field Banks that have pin getters/setters."""

  _relative_offset: int
  _bitfield_offset: int

  _type_view: 'npt.NDArray[np.int32]'
  _as_float_view: 'npt.NDArray[np.float32]'
  _as_int_view: 'npt.NDArray[np.int64]'

  __slots__ = ()

  def has_int(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    refs = self._get_ref().refs

    relative_idx = self._relative_offset + pin_number - 1
    bit_idx = self._bitfield_offset + relative_idx

    out = np.empty(len(refs), dtype=np.bool_)
    for i, ref in enumerate(refs):
      pin = ref.io_fields_[relative_idx]
      is_int = (pin.stored_type_ == 1) # 1 for int, 2 for float
      bit_set = (ref.message_bitfield_[bit_idx // 32] >> (bit_idx % 32)) & 1
      out[i] = is_int and bit_set
    return out

  def has_float(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    refs = self._get_ref().refs

    relative_idx = self._relative_offset + pin_number - 1
    bit_idx = self._bitfield_offset + relative_idx

    out = np.empty(len(refs), dtype=np.bool_)
    for i, ref in enumerate(refs):
      pin = ref.io_fields_[relative_idx]
      is_float = (pin.stored_type_ == 2) # 1 for int, 2 for float
      bit_set = (ref.message_bitfield_[bit_idx // 32] >> (bit_idx % 32)) & 1
      out[i] = is_float and bit_set
    return out

  def get_int(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    refs = self._get_ref().refs

    relative_idx = self._relative_offset + pin_number - 1

    has_ints = self.has_int(pin_number)
    for i, ref in enumerate(refs):
      if has_ints[i]:
        self._as_int_view[i] = ref.io_fields_[relative_idx].int_value_
      else:
        self._as_int_view[i] = 0
    return self._as_int_view

  def get_float(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    refs = self._get_ref().refs

    relative_idx = self._relative_offset + pin_number - 1

    has_floats = self.has_float(pin_number)
    for i, ref in enumerate(refs):
      if has_floats[i]:
        self._as_float_view[i] = ref.io_fields_[relative_idx].float_value_
      else:
        self._as_float_view[i] = np.nan
    return self._as_float_view


class FeedbackIoFieldBank(IoPinBank):

  __slots__ = [
      '_ref',
      '_bank',
      '_bank_readable',
      '_relative_offset',
      '_bitfield_offset',
  ]

  def __init__(self, bank: 'MessageEnum', bank_readable: str, fbk: 'Feedback'):
    self._ref = fbk._ref
    self._bank = bank
    self._bank_readable = bank_readable.strip().upper()
    self._relative_offset = _feedback_metadata.io_relative_offsets_[bank.value]
    self._bitfield_offset = _feedback_metadata.io_field_bitfield_offset_


class FeedbackIoField(IoField["FeedbackIoFieldBank"]):

  __slots__ = ['_a', '_b', '_c', '_d', '_e', '_f', 'banks']

  def __init__(self, fbk_message: 'Feedback'):

    bank_a = enums.FeedbackIoBankField(0)
    bank_b = enums.FeedbackIoBankField(1)
    bank_c = enums.FeedbackIoBankField(2)
    bank_d = enums.FeedbackIoBankField(3)
    bank_e = enums.FeedbackIoBankField(4)
    bank_f = enums.FeedbackIoBankField(5)

    self._a = FeedbackIoFieldBank(bank_a, 'a', fbk_message)
    self._b = FeedbackIoFieldBank(bank_b, 'b', fbk_message)
    self._c = FeedbackIoFieldBank(bank_c, 'c', fbk_message)
    self._d = FeedbackIoFieldBank(bank_d, 'd', fbk_message)
    self._e = FeedbackIoFieldBank(bank_e, 'e', fbk_message)
    self._f = FeedbackIoFieldBank(bank_f, 'f', fbk_message)

    self.banks = {
        bank_a: self._a,
        bank_b: self._b,
        bank_c: self._c,
        bank_d: self._d,
        bank_e: self._e,
        bank_f: self._f,
    }

  def has_int(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].has_int(pin_number)

  def has_float(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].has_float(pin_number)

  def get_int(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].get_int(pin_number)

  def get_float(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].get_float(pin_number)


class GroupInfoIoFieldBank(WeakReferenceContainer["GroupInfoBase"]):
  """Represents a read only IO bank for settings only."""

  __slots__ = ['_bank', '_bank_readable']

  def __init__(self, bank: 'MessageEnum', bank_readable: str, group_base: 'GroupInfoBase'):
    super().__init__(group_base)
    self._bank = bank
    self._bank_readable = bank_readable.strip().upper()

  def __repr__(self):
    return _io_info_bank_repr(self, self._bank, self._bank_readable)

  def get_label(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    info_base = self._get_ref()
    getter = lambda msg, field, buffer, buffer_size: api.hebiInfoGetIoLabelString(msg, field.value, pin_number, buffer, buffer_size)
    return __get_string_group(info_base, self._bank, [None] * info_base.size, getter)


class GroupFeedbackIoFieldBank(WeakReferenceContainer["GroupFeedbackBase"], GroupIoPinBank):
  """Represents a read only IO bank."""

  __slots__ = [
      '_bank',
      '_bank_readable',
      '_relative_offset',
      '_bitfield_offset',
      '_type_view',
      '_as_int_view',
      '_as_float_view'
  ]

  def __init__(self, bank: 'MessageEnum', bank_readable: str, group_base: 'GroupFeedbackBase'):
    super().__init__(group_base)
    self._bank = bank
    self._bank_readable = bank_readable.strip().upper()
    self._relative_offset = _feedback_metadata.io_relative_offsets_[bank.value]
    self._bitfield_offset = _feedback_metadata.io_field_bitfield_offset_
    num_refs = len(self._get_ref().refs)
    self._as_int_view = np.empty(num_refs, dtype=np.int64)
    self._as_float_view = np.empty(num_refs, dtype=np.float32)

  def __repr__(self):
    return _io_bank_repr(self, self._bank, self._bank_readable)

  def setup_views(self):
    refs = self._get_ref().refs
    self._type_view = get_group_feedback_io_bank_type_view(refs, self._bank)
    self._as_int_view = get_group_feedback_io_bank_int_view(refs, self._bank)
    self._as_float_view = get_group_feedback_io_bank_float_view(refs, self._bank)


class GroupCommandIoFieldBank(WeakReferenceContainer["GroupCommandBase"], GroupIoPinBank):
  """Represents a mutable IO Bank."""

  __slots__ = ['_bank', '_bank_readable', '_relative_offset', '_bitfield_offset', '_type_view', '_as_int_view', '_as_float_view']

  def __init__(self, bank: 'MessageEnum', bank_readable: str, group_base: 'GroupCommandBase'):
    super().__init__(group_base)
    self._bank = bank
    self._bank_readable = bank_readable.strip().upper()
    self._relative_offset = _command_metadata.io_relative_offsets_[bank.value]
    self._bitfield_offset = _command_metadata.io_field_bitfield_offset_
    num_refs = len(self._get_ref().refs)
    self._as_int_view = np.empty(num_refs, dtype=np.int64)
    self._as_float_view = np.empty(num_refs, dtype=np.float32)

  def __repr__(self):
    return _io_bank_repr(self, self._bank, self._bank_readable)

  def set_int(self, pin_number: int, value: 'int | None'):
    """
    Note: `pin_number` indexing starts at `1`
    """
    refs = self._get_ref()._refs
    size = len(refs)
    if value is None:
      bfr = None
    else:
      _tls.ensure_capacity(size)
      bfr = _tls.c_int64_array
      if isinstance(value, (int, float)):
        for i in range(size):
          bfr[i] = value
      else:
        for i in range(size):
          bfr[i] = value[i]

    api.hwCommandSetIoPinInt(refs, bfr, size, pin_number - 1, self._bank.value)

  def set_float(self, pin_number: int, value: 'float | None'):
    """
    Note: `pin_number` indexing starts at `1`
    """
    refs = self._get_ref()._refs
    size = len(refs)

    if value is None:
      bfr = None
    else:
      _tls.ensure_capacity(size)
      bfr = _tls.c_float_array
      if isinstance(value, (int, float)):
        for i in range(size):
          bfr[i] = value
      else:
        for i in range(size):
          bfr[i] = value[i]

    api.hwCommandSetIoPinFloat(refs, bfr, size, pin_number - 1, self._bank.value)

  def get_label(self, pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    cmd_base = self._get_ref()
    getter = lambda msg, field, buffer, buffer_size: api.hebiCommandGetIoLabelString(msg, field.value, pin_number, buffer, buffer_size)
    return __get_string_group(cmd_base, self._bank, [None] * cmd_base.size, getter)

  def set_label(self, pin_number: int, value: 'str | None'):
    """
    Note: `pin_number` indexing starts at `1`
    """
    modules = self._get_ref().modules

    if value is None:
      for module in modules:
        api.hebiCommandSetIoLabelString(module, self._bank, pin_number, None, None)
    else:
      if len(modules) > 1 and not self._bank.allow_broadcast:
        raise ValueError(f'Cannot broadcast scalar value \'{value}\' ' +
                         f'to the field \'{self._bank.name}\' ' +
                         'in all modules of the group.' +
                         f'\nReason: {self._bank.not_broadcastable_reason}')

      for m in modules:
        alloc_size = len(value.encode('utf-8'))
        alloc_size_c = _tls.c_size_t
        # TODO: use tls string buffer and copy val into it instead
        string_buffer = create_str(value, size=alloc_size)
        alloc_size_c.value = alloc_size
        api.hebiCommandSetIoLabelString(m, self._bank, pin_number, string_buffer, byref(alloc_size_c))


class GroupInfoIoField(WeakReferenceContainer["GroupInfoBase"], IoField['GroupInfoIoFieldBank']):
  """Represents a read only view into IO banks for settings only."""

  __slots__ = ['_a', '_b', '_c', '_d', '_e', '_f', 'banks']

  def __init__(self, group_message: 'GroupInfoBase'):
    super().__init__(group_message)

    bank_a = enums.InfoIoBankField(0)
    bank_b = enums.InfoIoBankField(1)
    bank_c = enums.InfoIoBankField(2)
    bank_d = enums.InfoIoBankField(3)
    bank_e = enums.InfoIoBankField(4)
    bank_f = enums.InfoIoBankField(5)

    self._a = GroupInfoIoFieldBank(bank_a, 'a', group_message)
    self._b = GroupInfoIoFieldBank(bank_b, 'b', group_message)
    self._c = GroupInfoIoFieldBank(bank_c, 'c', group_message)
    self._d = GroupInfoIoFieldBank(bank_d, 'd', group_message)
    self._e = GroupInfoIoFieldBank(bank_e, 'e', group_message)
    self._f = GroupInfoIoFieldBank(bank_f, 'f', group_message)

    self.banks = {
        bank_a: self._a,
        bank_b: self._b,
        bank_c: self._c,
        bank_d: self._d,
        bank_e: self._e,
        bank_f: self._f,
    }

  def __repr__(self):
    return _io_repr(self)

  def get_label(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    msg_base = self._get_ref()
    getter = lambda msg, field, buffer, buffer_size: api.hebiInfoGetIoLabelString(msg, field.value, pin_number, buffer, buffer_size)
    return __get_string_group(msg_base, bank, [None] * msg_base.size, getter)


class GroupFeedbackIoField(WeakReferenceContainer["GroupFeedbackBase"], IoField['GroupFeedbackIoFieldBank']):
  """Represents a read only view into IO banks."""

  __slots__ = ['_a', '_b', '_c', '_d', '_e', '_f', 'banks']

  def __init__(self,
               group_message: 'GroupFeedbackBase'):
    super().__init__(group_message)

    bank_a = enums.FeedbackIoBankField(0)
    bank_b = enums.FeedbackIoBankField(1)
    bank_c = enums.FeedbackIoBankField(2)
    bank_d = enums.FeedbackIoBankField(3)
    bank_e = enums.FeedbackIoBankField(4)
    bank_f = enums.FeedbackIoBankField(5)

    self._a = GroupFeedbackIoFieldBank(bank_a, 'a', group_message)
    self._b = GroupFeedbackIoFieldBank(bank_b, 'b', group_message)
    self._c = GroupFeedbackIoFieldBank(bank_c, 'c', group_message)
    self._d = GroupFeedbackIoFieldBank(bank_d, 'd', group_message)
    self._e = GroupFeedbackIoFieldBank(bank_e, 'e', group_message)
    self._f = GroupFeedbackIoFieldBank(bank_f, 'f', group_message)

    self.banks = {
        bank_a: self._a,
        bank_b: self._b,
        bank_c: self._c,
        bank_d: self._d,
        bank_e: self._e,
        bank_f: self._f,
    }

  def __repr__(self):
    try:
      _ = self._get_ref()
      return '\n'.join([
        'IO Banks: [A, B, C, D, E, F]' +
        str(self.a), str(self.b), str(self.c),
        str(self.d), str(self.e), str(self.f)
      ])
    except RuntimeError:
      return 'IO Banks: [A, B, C, D, E, F]\n  <Group message was finalized>'

  def setup_bank_views(self):
    for bank in self.banks.values():
      bank.setup_views()

  def has_int(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].has_int(pin_number)

  def has_float(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].has_float(pin_number)

  def get_int(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].get_int(pin_number)

  def get_float(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].get_float(pin_number)


class GroupCommandIoField(WeakReferenceContainer["GroupCommandBase"], IoField['GroupCommandIoFieldBank']):
  """Represents a mutable view into IO banks."""

  __slots__ = ['_a', '_b', '_c', '_d', '_e', '_f', 'banks']

  def __init__(self, group_message: 'GroupCommandBase'):
    super().__init__(group_message)

    bank_a = enums.CommandIoBankField(0)
    bank_b = enums.CommandIoBankField(1)
    bank_c = enums.CommandIoBankField(2)
    bank_d = enums.CommandIoBankField(3)
    bank_e = enums.CommandIoBankField(4)
    bank_f = enums.CommandIoBankField(5)

    self._a = GroupCommandIoFieldBank(bank_a, 'a', group_message)
    self._b = GroupCommandIoFieldBank(bank_b, 'b', group_message)
    self._c = GroupCommandIoFieldBank(bank_c, 'c', group_message)
    self._d = GroupCommandIoFieldBank(bank_d, 'd', group_message)
    self._e = GroupCommandIoFieldBank(bank_e, 'e', group_message)
    self._f = GroupCommandIoFieldBank(bank_f, 'f', group_message)

    self.banks = {
        bank_a: self._a,
        bank_b: self._b,
        bank_c: self._c,
        bank_d: self._d,
        bank_e: self._e,
        bank_f: self._f,
    }

  def __repr__(self):
    try:
      _ = self._get_ref()
      return '\n'.join([
        'IO Banks: [A, B, C, D, E, F]\n',
        str(self.a), str(self.b), str(self.c),
        str(self.d), str(self.e), str(self.f)
      ])
    except RuntimeError:
      return 'IO Banks: [A, B, C, D, E, F]\n  <Group message was finalized>'

  def has_int(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].has_int(pin_number)

  def has_float(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].has_float(pin_number)

  def get_int(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].get_int(pin_number)

  def get_float(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].get_float(pin_number)

  def set_int(self, bank: 'MessageEnum', pin_number: int, value: 'int | None'):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].set_int(pin_number, value)

  def set_float(self, bank: 'MessageEnum', pin_number: int, value: 'float | None'):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].set_float(pin_number, value)

  def get_label(self, bank: 'MessageEnum', pin_number: int):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].get_label(pin_number)

  def set_label(self, bank: 'MessageEnum', pin_number: int, value: 'str | None'):
    """
    Note: `pin_number` indexing starts at `1`
    """
    if pin_number < 1:
      raise ValueError("pin_number must be greater than 0")
    return self.banks[bank].set_label(pin_number, value)


################################################################################
# LED Field Containers
################################################################################


def _get_led_values(colors: 'Colorable | Iterable[Colorable]', size: int):
  _tls.ensure_capacity(size)
  bfr = _tls.c_int32_array

  if isinstance(colors, str):
    bfr[:size] = [int(string_to_color(colors)) for _ in range(size)]
  elif isinstance(colors, int):
    bfr[:size] = [colors for _ in range(size)]
  elif isinstance(colors, Color):
    bfr[:size] = [int(colors) for _ in range(size)]
  elif hasattr(colors, '__iter__'):
    bfr[:size] = [int(entry) for entry in colors]
  else:
    raise ValueError('Cannot broadcast input to array of colors')
  return bfr


class GroupFeedbackLEDField(WeakReferenceContainer["GroupFeedbackBase | GroupInfoBase"]):

  __slots__ = ['_field']

  def __init__(self, internal: 'GroupFeedbackBase | GroupInfoBase', field: 'MessageEnum'):
    super().__init__(internal)
    self._field = field

  def __repr__(self):
    try:
      enum_name = self._field.name
    except:
      enum_name = self._field
    desc = f'LED (Enumeration {enum_name}):\n'
    try:
      _ = self._get_ref()
      colors = self.color
      return desc + '  [' + ', '.join([repr(color) for color in colors]) + ']'
    except RuntimeError:
      return desc + '  <Group message was finalized>'

  @property
  def color(self):
    refs = self._get_ref()._refs
    return [color_from_int(ref.led_fields_[self._field.value]) for ref in refs]


class GroupCommandLEDField(WeakReferenceContainer["GroupCommandBase"]):
  __slots__ = ['_field']

  def __init__(self, internal: 'GroupCommandBase', field: 'MessageEnum' = enums.CommandLedField.Led):
    super().__init__(internal)
    self._field = field

  def __repr__(self):
    try:
      enum_name = self._field.name
    except AttributeError:
      enum_name = self._field
    desc = f'LED (Enumeration {enum_name}):\n'
    try:
      _ = self._get_ref()
      colors = self.color
      return desc + '  [' + ', '.join([repr(color) for color in colors]) + ']'
    except RuntimeError:
      return desc + '  <Group message was finalized>'

  @property
  def color(self):
    refs = self._get_ref()._refs
    return [color_from_int(ref.led_fields_[self._field.value]) for ref in refs]

  @color.setter
  def color(self, value: 'Colorable | list[Colorable] | None'):
    if value is None:
      self.clear()
    else:
      self.__set_colors(value)

  def clear(self):
    """Clears all LEDs."""
    messages = self._get_ref()
    api.hwCommandSetLed(messages._refs,
                        None,
                        messages.size,
                        enums.CommandLedField.Led)

  def __set_colors(self, colors: 'Colorable | list[Colorable]'):
    messages = self._get_ref()
    api.hwCommandSetLed(messages._refs,
                        _get_led_values(colors, messages.size),
                        messages.size,
                        enums.CommandLedField.Led)


class CommandLEDField(WeakReferenceContainer["HebiCommandRef"]):
  __slots__ = ['_field']

  def __init__(self, internal: 'HebiCommandRef', field: 'MessageEnum' = enums.CommandLedField.Led):
    super().__init__(internal)
    self._field = field

  @property
  def led(self):
    return color_from_int(self._get_ref().led_fields_[self._field.value])

  @led.setter
  def led(self, value: 'Colorable | None'):
    api.hwCommandSetLed(self._get_ref(), __get_led_value(value), 1, self._field)

  def clear(self):
    api.hwCommandSetLed(self._get_ref(), None, 1, self._field)


def __get_led_value(color: 'Colorable | None'):
  if isinstance(color, str):
    return int(string_to_color(color))
  elif isinstance(color, int):
    return color
  elif isinstance(color, Color):
    return int(color)

  return None


################################################################################
# TLS for accessors and mutators
################################################################################


class MessagesTLS_Holder:

  __slots__ = [
      # Scalars
      '_c_bool', '_c_int32', '_c_int64', '_c_uint64', '_c_size_t', '_c_float', '_c_double',
      '_c_vector3f', '_c_quaternionf', '_c_null_str', '_c_str', '_c_high_res_angle',
      "_array_size",
      # Arrays
      "_c_bool_array", "_c_int32_array", "_c_int64_array", "_c_uint64_array", "_c_size_t_array",
      "_c_float_array", "_c_double_array", "_c_vector3f_array", "_c_quaternionf_array",
      "_c_high_res_angle_array"
  ]

  def _grow_arrays(self, size: int):
    if size > self._array_size:
      self._c_bool_array = (ctypes.c_bool * size)()
      self._c_int32_array = (ctypes.c_int32 * size)()
      self._c_int64_array = (ctypes.c_int64 * size)()
      self._c_uint64_array = (ctypes.c_uint64 * size)()
      self._c_size_t_array = (ctypes.c_size_t * size)()
      self._c_float_array = (ctypes.c_float * size)()
      self._c_double_array = (ctypes.c_double * size)()
      self._c_high_res_angle_array = (HebiHighResAngleStruct * size)()
      self._array_size = size

  def __init__(self):
    self._c_bool = ctypes.c_bool(False)
    self._c_int32 = ctypes.c_int32(0)
    self._c_int64 = ctypes.c_int64(0)
    self._c_uint64 = ctypes.c_uint64(0)
    self._c_size_t = ctypes.c_size_t(0)
    self._c_float = ctypes.c_float(0)
    self._c_double = ctypes.c_double(0)
    self._c_high_res_angle = HebiHighResAngleStruct()
    self._c_null_str = ctypes.c_char_p(None)
    self._c_str = create_str(512)

    self._array_size = 0
    self._grow_arrays(6)


class MessagesTLS(threading.local):
  def __init__(self):
    super().__init__()
    self._holder = MessagesTLS_Holder()

  def ensure_capacity(self, size: int):
    self._holder._grow_arrays(size)

  @property
  def c_bool(self):
    return self._holder._c_bool

  @property
  def c_int32(self):
    return self._holder._c_int32

  @property
  def c_int64(self):
    return self._holder._c_int64

  @property
  def c_uint64(self):
    return self._holder._c_uint64

  @property
  def c_size_t(self):
    return self._holder._c_size_t

  @property
  def c_float(self):
    return self._holder._c_float

  @property
  def c_double(self):
    return self._holder._c_double

  @property
  def c_vector3f(self):
    return self._holder._c_vector3f

  @property
  def c_quaternionf(self):
    return self._holder._c_quaternionf

  @property
  def c_null_str(self):
    return self._holder._c_null_str

  @property
  def c_str(self):
    return self._holder._c_str

  @property
  def c_high_res_angle(self):
    return self._holder._c_high_res_angle

  @property
  def c_bool_array(self):
    return self._holder._c_bool_array

  @property
  def c_int32_array(self):
    return self._holder._c_int32_array

  @property
  def c_int64_array(self):
    return self._holder._c_int64_array

  @property
  def c_uint64_array(self):
    return self._holder._c_uint64_array

  @property
  def c_size_t_array(self):
    return self._holder._c_size_t_array

  @property
  def c_float_array(self):
    return self._holder._c_float_array

  @property
  def c_double_array(self):
    return self._holder._c_double_array

  @property
  def c_vector3f_array(self):
    return self._holder._c_vector3f_array

  @property
  def c_quaternionf_array(self):
    return self._holder._c_quaternionf_array

  @property
  def c_high_res_angle_array(self):
    return self._holder._c_high_res_angle_array


_tls = MessagesTLS()


################################################################################
# Accessors
################################################################################


def __get_flag_group(refs: 'ArrayHebiRefs', field: 'MessageEnum', getter: 'Callable[..., None]') -> 'npt.NDArray[np.bool_]':
  size = len(refs)
  out = np.empty(size, dtype=bool)
  getter(out.ctypes.data_as(c_bool_p), refs, size, field.value)
  return out


def __get_highresangle_group(refs: 'ArrayHebiRefs', field: 'MessageEnum', getter) -> 'npt.NDArray[np.float64]':
  size = len(refs)
  out = np.empty(size, dtype=np.float64)
  getter(out.ctypes.data_as(c_double_p), refs, size, field.value)
  return out


def __get_scalar_field_single(message: 'HebiRef', field: 'MessageEnum', ret: 'ctypes._SimpleCData[Scalar]', getter) -> 'Scalar':
  getter(byref(ret), message, 1, field.value)
  return ret.value


def __get_string_group(message_list: 'GroupInfoBase | GroupCommandBase', field: 'MessageEnum', output: 'list[str | None]', getter):
  alloc_size_c = _tls.c_size_t
  alloc_size = 0
  null_str = _tls.c_null_str

  for i, message in enumerate(message_list.modules):
    res = getter(message, field.value, null_str, byref(alloc_size_c))
    alloc_size = max(alloc_size, alloc_size_c.value + 1)

  if alloc_size > len(_tls.c_str):
    string_buffer = create_str(alloc_size)
  else:
    string_buffer = _tls.c_str

  for i, message in enumerate(message_list.modules):
    alloc_size_c.value = alloc_size
    if getter(message, field.value, string_buffer, byref(alloc_size_c)) == enums.StatusSuccess:
      output[i] = decode_str(string_buffer.value)
    else:
      output[i] = None
  return output


def __get_string_single(message: 'Command | Info', field: 'MessageEnum', getter):
  alloc_size_c = _tls.c_size_t
  null_str = _tls.c_null_str

  getter(message, field.value, null_str, byref(alloc_size_c))
  alloc_size = alloc_size_c.value + 1

  if alloc_size > len(_tls.c_str):
    string_buffer = create_str(alloc_size)
  else:
    string_buffer = _tls.c_str

  alloc_size_c.value = alloc_size
  if getter(message, field.value, string_buffer, byref(alloc_size_c)) == enums.StatusSuccess:
    return decode_str(string_buffer.value)

  return None


################################################################################
# Mutators
################################################################################


def __set_flag_group(refs: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[bool] | bool | None', setter):
  size = len(refs)
  _tls.ensure_capacity(size)
  if value is None:
    bfr = None
  elif isinstance(value, bool):
    bfr = _tls.c_bool_array
    for i in range(size):
      bfr[i] = value
  else:
    bfr = _tls.c_bool_array
    for i in range(size):
      bfr[i] = value[i]
  setter(refs, bfr, size, field.value)


def __set_bool_group(refs: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[bool] | bool | None', setter):
  size = len(refs)
  _tls.ensure_capacity(size)
  if value is None:
    bfr = None
  elif isinstance(value, bool):
    bfr = _tls.c_bool_array
    for i in range(size):
      bfr[i] = value
  else:
    bfr = _tls.c_bool_array
    for i in range(size):
      bfr[i] = value[i]
  setter(refs, bfr, size, field.value)


def __set_enum_group(refs: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[int] | int | None', setter):
  size = len(refs)
  _tls.ensure_capacity(size)
  if value is None:
    bfr = None
  else:
    bfr = _tls.c_int32_array
    if isinstance(value, int):
      for i in range(size):
        bfr[i] = value
    else:
      for i in range(size):
        bfr[i] = value[i]
  setter(refs, bfr, size, field.value)


def __set_float_group(refs: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[float] | float | None', setter):
  size = len(refs)
  _tls.ensure_capacity(size)
  if value is None:
    bfr = None
  else:
    bfr = _tls.c_float_array
    if isinstance(value, (int, float)):
      for i in range(size):
        bfr[i] = value
    else:
      for i in range(size):
        bfr[i] = value[i]
  setter(refs, bfr, size, field.value)


def __set_highresangle_group(refs: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[float] | float | None', setter):
  size = len(refs)
  _tls.ensure_capacity(size)
  if value is None:
    bfr = None
  else:
    bfr = _tls.c_double_array
    if isinstance(value, (int, float)):
      for i in range(size):
        bfr[i] = value
    else:
      for i in range(size):
        bfr[i] = value[i]
  setter(refs, bfr, size, field.value)


def __set_field_single(ref: 'HebiRef', field: 'MessageEnum', value, value_ctype, setter: 'Callable[[Any, Any, int, int], None]'):
  if value is not None:
    value_ctype.value = value
    setter(byref(ref), byref(value_ctype), 1, field.value)
  else:
    setter(byref(ref), None, 1, field.value)


def __set_string_group(message_list: 'GroupCommandBase', field: 'MessageEnum', value: 'str | None', setter):
  alloc_size_c = _tls.c_size_t
  if value is None:
    for message in message_list.modules:
      setter(message, field.value, None, None)
  else:
    if message_list.size > 1 and not field.allow_broadcast:
      raise ValueError(f"Cannot broadcast scalar value '{value}' to the "
                       f"field \'{field.name}\' in all modules of the group.\n"
                       f"Reason: {field.not_broadcastable_reason}")

    for message in message_list.modules:
      alloc_size = len(value.encode('utf-8'))
      # TODO: use tls string buffer and copy val into it instead
      string_buffer = create_str(value, size=alloc_size)
      alloc_size_c.value = alloc_size
      setter(message, field.value, string_buffer, byref(alloc_size_c))


def __set_string_single(message, field: 'MessageEnum', value: 'str | None', setter):
  if value is not None:
    alloc_size_c = _tls.c_size_t
    alloc_size = len(value.encode('utf-8'))
    # TODO: use tls string buffer and copy val into it instead
    string_buffer = create_str(value, size=alloc_size)
    alloc_size_c.value = alloc_size
    setter(message, field.value, string_buffer, byref(alloc_size_c))
  else:
    setter(message, field.value, None, None)

################################################################################
# General
################################################################################


def get_bool(msg: 'HebiRef', field: 'MessageEnum') -> bool:
  return msg.bool_fields_[field.value]


def get_enum(msg: 'HebiRef', field: 'MessageEnum') -> int:
  return msg.enum_fields_[field.value]


def get_float(msg: 'HebiRef', field: 'MessageEnum') -> float:
  return msg.float_fields_[field.value]


def get_uint64(msg: 'HebiRef', field: 'MessageEnum') -> int:
  return msg.uint64_fields_[field.value]


#def get_group_float_view(msg: 'ArrayHebiRefs', field: 'MessageEnum'):
#  t: 'HebiCommandRef | HebiFeedbackRef | HebiInfoRef' = type(msg[0])
#  t_size = ctypes.sizeof(t)
#  offset: int = t.float_fields_.offset
#  view_start_addr = ctypes.cast(msg, ctypes.c_void_p).value + offset + field.value
#  view_array = np.ctypeslib.as_array(view_start, (t_size * len(msg),))


def get_group_bool(msg: 'ArrayHebiRefs', field: 'MessageEnum'):
  size = len(msg)
  out = np.empty(size, np.bool_)
  for i in range(size):
    out[i] = msg[i].bool_fields_[field.value]
  return out


def get_group_enum(msg: 'ArrayHebiRefs', field: 'MessageEnum'):
  size = len(msg)
  out = np.empty(size, np.int32)
  for i in range(size):
    out[i] = msg[i].enum_fields_[field.value]
  return out


def get_group_float(msg: 'ArrayHebiRefs', field: 'MessageEnum'):
  size = len(msg)
  out = np.empty(size, np.float32)
  for i in range(size):
    out[i] = msg[i].float_fields_[field.value]
  return out


def get_group_uint64(msg: 'ArrayHebiRefs', field: 'MessageEnum'):
  size = len(msg)
  out = np.empty(size, np.uint64)
  for i in range(size):
    out[i] = msg[i].uint64_fields_[field.value]
  return out


def get_group_float_into(refs: 'ArrayHebiRefs', field: 'MessageEnum', output: 'npt.NDArray[np.float32]'):
  for i, ref in enumerate(refs):
    output[i] = ref.float_fields_[field.value]


################################################################################
# Command
################################################################################


def get_command_flag(msg: 'HebiCommandRef', field: 'MessageEnum'):
  return __get_scalar_field_single(msg, field, _tls.c_bool, api.hwCommandGetFlag)


def get_command_highresangle(msg: 'HebiCommandRef', field: 'MessageEnum'):
  return __get_scalar_field_single(msg, field, _tls.c_double, api.hwCommandGetHighResAngle)


def get_command_string(msg: 'Command', field: 'MessageEnum'):
  ret = __get_string_single(msg, field, api.hebiCommandGetString)
  return ret


def set_command_flag(msg: 'HebiCommandRef', field: 'MessageEnum', value: 'bool | None'):
  __set_field_single(msg, field, value, _tls.c_bool, api.hwCommandSetFlag)


def set_command_bool(msg: 'HebiCommandRef', field: 'MessageEnum', value: 'bool | None'):
  __set_field_single(msg, field, value, _tls.c_bool, api.hwCommandSetBool)


def set_command_enum(msg: 'HebiCommandRef', field: 'MessageEnum', value: 'int | None'):
  __set_field_single(msg, field, value, _tls.c_int32, api.hwCommandSetEnum)


def set_command_uint64(msg: 'HebiCommandRef', field: 'MessageEnum', value: 'int | None'):
  __set_field_single(msg, field, value, _tls.c_uint64, api.hwCommandSetUInt64)


def set_command_float(msg: 'HebiCommandRef', field: 'MessageEnum', value: 'float | None'):
  __set_field_single(msg, field, value, _tls.c_float, api.hwCommandSetFloat)


def set_command_highresangle(msg: 'HebiCommandRef', field: 'MessageEnum', value: 'float | None'):
  __set_field_single(msg, field, value, _tls.c_double, api.hwCommandSetHighResAngle)


def set_command_string(msg: 'Command', field: 'MessageEnum', value: 'str | None'):
  __set_string_single(msg, field, value, api.hebiCommandSetString)


def get_group_command_flag(msg: 'Array[HebiCommandRef]', field: 'MessageEnum'):
  return __get_flag_group(msg, field, api.hwCommandGetFlag)


def get_group_command_highresangle(msg: 'Array[HebiCommandRef]', field: 'MessageEnum'):
  return __get_highresangle_group(msg, field, api.hwCommandGetHighResAngle)


def get_group_command_string(msg: 'GroupCommandBase', field: 'MessageEnum', output: 'list[str | None]'):
  return __get_string_group(msg, field, output, api.hebiCommandGetString)


def set_group_command_flag(msg: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[bool] | bool | None'):
  __set_flag_group(msg, field, value, api.hwCommandSetFlag)


def set_group_command_bool(msg: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[bool] | bool | None'):
  __set_bool_group(msg, field, value, api.hwCommandSetBool)


def set_group_command_enum(msg: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[int] | int | None'):
  __set_enum_group(msg, field, value, api.hwCommandSetEnum)


def set_group_command_uint64(msg: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[int] | int | None'):
  __set_enum_group(msg, field, value, api.hwCommandSetUInt64)


def set_group_command_float(msg: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[float] | float | None'):
  __set_float_group(msg, field, value, api.hwCommandSetFloat)


def set_group_command_highresangle(msg: 'Array[HebiCommandRef]', field: 'MessageEnum', value: 'Sequence[float] | float | None'):
  __set_highresangle_group(msg, field, value, api.hwCommandSetHighResAngle)


def set_group_command_string(msg: 'GroupCommandBase', field: 'MessageEnum', value: 'str | None'):
  alloc_size_c = _tls.c_size_t
  if value is not None:
    for message in msg.modules:
      alloc_size = len(value.encode('utf-8'))
      # TODO: use tls string buffer and copy val into it instead
      string_buffer = create_str(value, size=alloc_size)
      alloc_size_c.value = alloc_size
      api.hebiCommandSetString(message, field.value, string_buffer, byref(alloc_size_c))
  else:
    for message in msg.modules:
      api.hebiCommandSetString(message, field.value, None, None)


def get_group_command_float_view(msg: 'Array[HebiCommandRef]', field: 'MessageEnum'):
  cmd_ref_size: int = api.hebiCommandGetSize()
  num_refs = len(msg)
  first = msg[0].float_fields_
  size = sizeof(first._type_)
  buffer_size = 1 + (num_refs - 1) * (cmd_ref_size // size)
  first_vp = cast(first, ctypes.c_void_p)
  first_vp.value += field.value * size # type: ignore
  view = np.ctypeslib.as_array(cast(first_vp, c_float_p), (buffer_size,))
  strided_view = np.lib.stride_tricks.as_strided(view, (num_refs,), (cmd_ref_size,))
  return strided_view


################################################################################
# Feedback
################################################################################

def get_feedback_vector3f(msg: 'HebiFeedbackRef', field: 'MessageEnum'):
  ret = byref(msg.vector3f_fields_[field.value])
  return np.ctypeslib.as_array(cast_to_float_ptr(ret), (3,))


def get_feedback_quaternionf(msg: 'HebiFeedbackRef', field: 'MessageEnum'):
  ret = byref(msg.quaternionf_fields_[field.value])
  return np.ctypeslib.as_array(cast_to_float_ptr(ret), (4,))


def get_feedback_highresangle(msg: 'HebiFeedbackRef', field: 'MessageEnum'):
  return __get_scalar_field_single(msg, field, _tls.c_double, api.hwFeedbackGetHighResAngle)


def get_group_feedback_float_view(msg: 'Array[HebiFeedbackRef]', field: 'MessageEnum'):
  fbk_ref_size: int = api.hebiFeedbackGetSize()
  num_refs = len(msg)
  first = msg[0].float_fields_
  size = sizeof(first._type_)
  buffer_size = 1 + (num_refs - 1) * (fbk_ref_size // size)
  first_vp = cast(first, ctypes.c_void_p)
  first_vp.value += field.value * size # type: ignore
  view = np.ctypeslib.as_array(cast(first_vp, c_float_p), (buffer_size,))
  strided_view = np.lib.stride_tricks.as_strided(view, (num_refs,), (fbk_ref_size,))
  return strided_view


def get_group_feedback_vector3f_view(msg: 'Array[HebiFeedbackRef]', field: 'MessageEnum') -> 'npt.NDArray[np.float32]':
  fbk_ref_size: int = api.hebiFeedbackGetSize()
  num_refs = len(msg)
  first = msg[0].vector3f_fields_[field.value]
  buffer_size = 1 + (num_refs - 1) * (fbk_ref_size // sizeof(first))
  view = np.ctypeslib.as_array(cast(byref(first), c_float_p), (buffer_size, 3))
  strided_view = np.lib.stride_tricks.as_strided(view, (num_refs, 3), (fbk_ref_size, view.strides[1]))
  return strided_view


def get_group_feedback_quaternionf_view(msg: 'Array[HebiFeedbackRef]', field: 'MessageEnum') -> 'npt.NDArray[np.float32]':
  fbk_ref_size: int = api.hebiFeedbackGetSize()
  num_refs = len(msg)
  first = msg[0].quaternionf_fields_[field.value]
  buffer_size = 1 + (num_refs - 1) * (fbk_ref_size // sizeof(first))
  view = np.ctypeslib.as_array(cast(byref(first), c_float_p), (buffer_size, 4))
  strided_view = np.lib.stride_tricks.as_strided(view, (num_refs, 4), (fbk_ref_size, view.strides[1]))
  return strided_view


def get_group_feedback_io_bank_type_view(msg: 'Array[HebiFeedbackRef]', bank: 'MessageEnum'):
  fbk_ref_size: int = api.hebiFeedbackGetSize()
  num_refs = len(msg)
  relative_offset = _feedback_metadata.io_relative_offsets_[bank.value]
  first = msg[0].io_fields_[relative_offset]
  size = sizeof(ctypes.c_int)
  buffer_size = 1 + (num_refs - 1) * (fbk_ref_size // size)
  first_vp = cast(byref(first), ctypes.c_void_p)
  first_vp.value += bank.value * size  # type: ignore
  first_vp.value += sizeof(ctypes.c_int64)  # offset past the union to the 'stored_type_' field
  view = np.ctypeslib.as_array(cast(first_vp, c_int32_p), (buffer_size,))
  strided_view: 'npt.NDArray[np.int32]' = np.lib.stride_tricks.as_strided(view, (num_refs,), (fbk_ref_size,))
  return strided_view


def get_group_feedback_io_bank_int_view(msg: 'Array[HebiFeedbackRef]', bank: 'MessageEnum'):
  fbk_ref_size: int = api.hebiFeedbackGetSize()
  num_refs = len(msg)
  relative_offset = _feedback_metadata.io_relative_offsets_[bank.value]
  first = msg[0].io_fields_[relative_offset]
  size = sizeof(ctypes.c_int64)
  buffer_size = 1 + (num_refs - 1) * (fbk_ref_size // size)
  first_vp = cast(byref(first), ctypes.c_void_p)
  first_vp.value += bank.value * size  # type: ignore
  view = np.ctypeslib.as_array(cast(first_vp, c_int64_p), (buffer_size,))
  strided_view: 'npt.NDArray[np.int64]' = np.lib.stride_tricks.as_strided(view, (num_refs,), (fbk_ref_size,))
  return strided_view


def get_group_feedback_io_bank_float_view(msg: 'Array[HebiFeedbackRef]', bank: 'MessageEnum'):
  fbk_ref_size: int = api.hebiFeedbackGetSize()
  num_refs = len(msg)
  relative_offset = _feedback_metadata.io_relative_offsets_[bank.value]
  first = msg[0].io_fields_[relative_offset]
  size = sizeof(ctypes.c_float)
  buffer_size = 1 + (num_refs - 1) * (fbk_ref_size // size)
  first_vp = cast(byref(first), ctypes.c_void_p)
  first_vp.value += bank.value * size  # type: ignore
  view = np.ctypeslib.as_array(cast(first_vp, c_float_p), (buffer_size,))
  strided_view: 'npt.NDArray[np.float32]' = np.lib.stride_tricks.as_strided(view, (num_refs,), (fbk_ref_size,))
  return strided_view


def get_group_feedback_vector3f(msg: 'Array[HebiFeedbackRef]', field: 'MessageEnum'):
  size = len(msg)
  out = np.empty((size, 3), dtype=np.float32)
  for i, ref in enumerate(msg):
    out[i, :] = ref.vector3f_fields_[field.value]
  return out


def get_group_feedback_quaternionf(msg: 'Array[HebiFeedbackRef]', field: 'MessageEnum'):
  size = len(msg)
  out = np.empty((size, 4), dtype=np.float32)
  for i, ref in enumerate(msg):
    out[i, :] = ref.quaternionf_fields_[field.value]
  return out


def get_group_feedback_highresangle(msg: 'Array[HebiFeedbackRef]', field: 'MessageEnum'):
  return __get_highresangle_group(msg, field, api.hwFeedbackGetHighResAngle)


def get_group_feedback_highresangle_into(refs: 'Array[HebiFeedbackRef]', field: 'MessageEnum', output: 'npt.NDArray[np.float64]'):
  size = len(refs)
  api.hwFeedbackGetHighResAngle(output.ctypes.data_as(c_double_p), refs, size, field.value)


################################################################################
# Info
################################################################################


def get_info_flag(msg: 'HebiInfoRef', field: 'MessageEnum'):
  return __get_scalar_field_single(msg, field, _tls.c_bool, api.hwInfoGetFlag)


def get_info_highresangle(msg: 'HebiInfoRef', field: 'MessageEnum'):
  return __get_scalar_field_single(msg, field, _tls.c_double, api.hwInfoGetHighResAngle)


def get_info_string(msg: 'Info', field: 'MessageEnum'):
  return __get_string_single(msg, field, api.hebiInfoGetString)


def get_group_info_flag(msg: 'Array[HebiInfoRef]', field: 'MessageEnum'):
  return __get_flag_group(msg, field, api.hwInfoGetFlag)


def get_group_info_highresangle(msg: 'Array[HebiInfoRef]', field: 'MessageEnum'):
  return __get_highresangle_group(msg, field, api.hwInfoGetHighResAngle)


def get_group_info_string(msg: 'GroupInfoBase', mTraits: 'MessageEnum', output: 'list[str | None]'):
  return __get_string_group(msg, mTraits, output, api.hebiInfoGetString)
