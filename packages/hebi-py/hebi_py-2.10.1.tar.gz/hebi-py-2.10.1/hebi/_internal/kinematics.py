# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2022 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

from .ffi import enums
import numpy as np
from math import pi
from threading import local
from .utils import CaseInvariantString, intern_string

import typing
if typing.TYPE_CHECKING:
  from typing import Any
  import numpy.typing as npt
  from .ffi.wrappers import EnumTraits

neg_half_pi = pi*-0.5


################################################################################
# Transform Functions
################################################################################


def set_translate(matrix, x, y, z):
  matrix[0, 3] = x
  matrix[1, 3] = y
  matrix[2, 3] = z


def set_rotate_x(matrix, radians):
  from math import cos, sin
  c_r = cos(radians)
  s_r = sin(radians)
  matrix[0, 0] = 1.0
  matrix[0, 1] = 0.0
  matrix[0, 2] = 0.0
  matrix[1, 0] = 0.0
  matrix[1, 1] = c_r
  matrix[1, 2] = -s_r
  matrix[2, 0] = 0.0
  matrix[2, 1] = s_r
  matrix[2, 2] = c_r


def set_sphere_inertia(inertia, mass, radius):
  inertia[0:3] = 0.4 * mass * radius * radius
  inertia[3:6] = 0.0


def set_rod_x_axis_inertia(inertia, mass, length):
  inertia[1:3] = mass * length * length * 0.083333333333333333
  inertia[3:6] = inertia[0] = 0.0


################################################################################
# Descriptor classes returned from parser functions
################################################################################


class ActuatorDesc:

  __slots__ = ['_com', '_com_xyz', '_inertia', '_input_to_axis', '_input_to_axis_xyz', '_mass', '_name']

  def __init__(self, name, mass, inertia, com_xyz, input_to_axis_xyz):
    self._name = name
    self._mass = mass
    self._inertia: 'npt.NDArray[np.float64]' = np.array(inertia, dtype=np.float64)
    self._com_xyz = com_xyz
    self._input_to_axis_xyz = input_to_axis_xyz
    self._com: 'npt.NDArray[np.float64]' = np.identity(4, np.float64)
    self._input_to_axis: 'npt.NDArray[np.float64]' = np.identity(4, np.float64)

    v = com_xyz
    set_translate(self._com, v[0], v[1], v[2])
    v = input_to_axis_xyz
    set_translate(self._input_to_axis, v[0], v[1], v[2])

  @property
  def name(self):
    return self._name

  @property
  def mass(self):
    return self._mass

  @property
  def moments_of_inertia(self):
    return self._inertia

  @property
  def com(self):
    return self._com

  @property
  def input_to_axis(self):
    return self._input_to_axis


class BracketDesc:

  __slots__ = ['_mass', '_mount', '_name']

  def __init__(self, name, mount, mass):
    self._name = name
    self._mount = mount
    self._mass = mass

  @property
  def name(self):
    return self._name

  @property
  def mount(self):
    return self._mount

  @property
  def mass(self):
    return self._mass


################################################################################
# Descriptor Classes for parsing
################################################################################


class BracketParserMatch:

  __slots__ = ['_mount', '_parser']

  def __init__(self, parser: 'BracketParser', mount: str):
    self._parser = parser
    self._mount = mount

  @property
  def bracket_name(self):
    return self._parser.name

  @property
  def light(self):
    return 'Light' in self._parser.name

  @property
  def heavy(self):
    return 'Heavy' in self._parser.name

  @property
  def left(self):
    return 'left' in self._mount

  @property
  def right(self):
    return 'right' in self._mount

  @property
  def inside(self):
    return 'inside' in self._mount

  @property
  def outside(self):
    return 'outside' in self._mount

  @property
  def mass(self):
    return self._parser.mass


class BracketParser:

  __slots__ = ['_mass', '_mounts', '_name']

  def __init__(self, name: str, mounts: 'list[str]', mass: float):
    self._name = intern_string(name)
    self._mounts = [intern_string(mount) for mount in mounts]
    self._mass = mass

  def match(self, name, mount):
    if name == self._name:
      mount = intern_string(mount)
      for entry in self._mounts:
        if mount == entry:
          return BracketParserMatch(self, mount)
    return None

  @property
  def mass(self):
    return self._mass

  @property
  def name(self):
    return self._name


################################################################################
# Maps and Lists for HEBI Products
################################################################################


class KinematicsParserTLS(local):
  """Used to cache valid strings mapped to kinematics objects."""

  def __init__(self):
    super().__init__()
    self.parsed_joint_strs: 'dict[str, enums.JointType]' = dict()
    self.parsed_frame_type_strs: 'dict[str, enums.FrameType]' = dict()
    self.parsed_actuator_strs: 'dict[str, enums.ActuatorType]' = dict()
    self.parsed_link_strs: 'dict[str, enums.LinkType]' = dict()
    self.parsed_bracket_strs: 'dict[str, enums.BracketType]' = dict()

  def get_joint(self, joint: str):
    return self.parsed_joint_strs.get(joint)

  def set_joint(self, joint: str, value: 'enums.JointType'):
    self.parsed_joint_strs[joint] = value

  def get_frame_type(self, frame_type: str):
    return self.parsed_frame_type_strs.get(frame_type)

  def set_frame_type(self, frame_type: str, value: 'enums.FrameType'):
    self.parsed_frame_type_strs[frame_type] = value

  def get_actuator(self, actuator: str):
    return self.parsed_actuator_strs.get(actuator)

  def set_actuator(self, actuator: str, value: 'enums.ActuatorType'):
    self.parsed_actuator_strs[actuator] = value


_parser_tls = KinematicsParserTLS()

# TODO: Maybe move this into a catalogue module?

__joint_types_to_enum = {
    'tx': enums.JointTypeTranslationX, 'x': enums.JointTypeTranslationX,
    'ty': enums.JointTypeTranslationY, 'y': enums.JointTypeTranslationY,
    'tz': enums.JointTypeTranslationZ, 'z': enums.JointTypeTranslationZ,
    'rx': enums.JointTypeRotationX,
    'ry': enums.JointTypeRotationY,
    'rz': enums.JointTypeRotationZ
}

__enum_to_joint_types = dict((v, k) for k, v in __joint_types_to_enum.items())

__end_effector_types_to_enum = {
    'custom': enums.EndEffectorTypeCustom,
    'x5': enums.EndEffectorTypeX5Parallel, 'x8': enums.EndEffectorTypeX5Parallel,
    'X5': enums.EndEffectorTypeX5Parallel, 'X8': enums.EndEffectorTypeX5Parallel,
    'r8': enums.EndEffectorTypeR8Parallel, 'R8': enums.EndEffectorTypeR8Parallel,
}

__enum_to_end_effector_types = dict((v, k) for k, v in __end_effector_types_to_enum.items())

__frame_types_to_enum = {
    'CoM': enums.FrameTypeCenterOfMass,
    'com': enums.FrameTypeCenterOfMass,
    'output': enums.FrameTypeOutput,
    'endeffector': enums.FrameTypeEndEffector, 'EndEffector': enums.FrameTypeEndEffector,
    'input': enums.FrameTypeInput,
    'mesh': enums.FrameTypeMesh,
}

__X5_moi = [0.00015, 0.000255, 0.000350, 0.0000341, 0.0000118, 0.00000229]
__X8_moi = [0.000246, 0.000380, 0.000463, 0.0000444, 0.0000266, 0.00000422]
__R8_moi = [0.000246, 0.000380, 0.000463, 0.0000444, 0.0000266, 0.00000422]  # TODO

__actuators = {
    'X5-1': ActuatorDesc('X5-1', 0.315, __X5_moi, [0.0142, -0.0031, 0.0165], [0.0, 0.0, 0.03105]),
    'X5-4': ActuatorDesc('X5-4', 0.335, __X5_moi, [0.0142, -0.0031, 0.0165], [0.0, 0.0, 0.03105]),
    'X5-9': ActuatorDesc('X5-9', 0.360, __X5_moi, [0.0142, -0.0031, 0.0165], [0.0, 0.0, 0.03105]),
    'X8-3': ActuatorDesc('X8-3', 0.460, __X8_moi, [-0.0145, -0.0031, 0.0242], [0.0, 0.0, 0.0451]),
    'X8-9': ActuatorDesc('X8-9', 0.480, __X8_moi, [-0.0145, -0.0031, 0.0242], [0.0, 0.0, 0.0451]),
    'X8-16': ActuatorDesc('X8-16', 0.500, __X8_moi, [-0.0145, -0.0031, 0.0242], [0.0, 0.0, 0.0451]),
    'R8-3': ActuatorDesc('R8-3', 0.500, __R8_moi, [-0.0145, -0.0031, 0.0242], [0.0, 0.0, 0.0451]),
    'R8-9': ActuatorDesc('R8-9', 0.500, __R8_moi, [-0.0145, -0.0031, 0.0242], [0.0, 0.0, 0.0451]),
    'R8-16': ActuatorDesc('R8-16', 0.500, __R8_moi, [-0.0145, -0.0031, 0.0242], [0.0, 0.0, 0.0451]),
}

__actuator_to_enum = {
    CaseInvariantString('X5-1'): enums.ActuatorType.X5_1,
    CaseInvariantString('X5-4'): enums.ActuatorType.X5_4,
    CaseInvariantString('X5-9'): enums.ActuatorType.X5_9,
    CaseInvariantString('X8-3'): enums.ActuatorType.X8_3,
    CaseInvariantString('X8-9'): enums.ActuatorType.X8_9,
    CaseInvariantString('X8-16'): enums.ActuatorType.X8_16,
    CaseInvariantString('R8-3'): enums.ActuatorType.R8_3,
    CaseInvariantString('R8-9'): enums.ActuatorType.R8_9,
    CaseInvariantString('R8-16'): enums.ActuatorType.R8_16,
    CaseInvariantString('T5-1'): enums.ActuatorType.T5_1,
    CaseInvariantString('T5-4'): enums.ActuatorType.T5_4,
    CaseInvariantString('T5-9'): enums.ActuatorType.T5_9,
    CaseInvariantString('T8-3'): enums.ActuatorType.T8_3,
    CaseInvariantString('T8-9'): enums.ActuatorType.T8_9,
    CaseInvariantString('T8-16'): enums.ActuatorType.T8_16,
    CaseInvariantString('R25-8'): enums.ActuatorType.R25_8,
    CaseInvariantString('R25-20'): enums.ActuatorType.R25_20,
    CaseInvariantString('R25-40'): enums.ActuatorType.R25_40,
    CaseInvariantString('T25-8'): enums.ActuatorType.T25_8,
    CaseInvariantString('T25-20'): enums.ActuatorType.T25_20,
    CaseInvariantString('T25-40'): enums.ActuatorType.T25_40,
}

__enum_to_actuator = dict((v, str(k)) for k, v in __actuator_to_enum.items())


def _make_tup(a, b):
  return (CaseInvariantString(a), CaseInvariantString(b))


__actuator_brackets_to_enum = {
    _make_tup('X5-LightBracket', 'left'): enums.BracketType.X5LightLeft,
    _make_tup('X5-LightBracket', 'right'): enums.BracketType.X5LightRight,
    _make_tup('X5-HeavyBracket', 'left-inside'): enums.BracketType.X5HeavyLeftInside,
    _make_tup('X5-HeavyBracket', 'right-inside'): enums.BracketType.X5HeavyRightInside,
    _make_tup('X5-HeavyBracket', 'left-outside'): enums.BracketType.X5HeavyLeftOutside,
    _make_tup('X5-HeavyBracket', 'right-outside'): enums.BracketType.X5HeavyRightOutside,
    _make_tup('R8-LightBracket', 'left'): enums.BracketType.R8LightLeft,
    _make_tup('R8-LightBracket', 'right'): enums.BracketType.R8LightRight,
    _make_tup('R8-HeavyBracket', 'left-inside'): enums.BracketType.R8HeavyLeftInside,
    _make_tup('R8-HeavyBracket', 'right-inside'): enums.BracketType.R8HeavyRightInside,
    _make_tup('R8-HeavyBracket', 'left-outside'): enums.BracketType.R8HeavyLeftOutside,
    _make_tup('R8-HeavyBracket', 'right-outside'): enums.BracketType.R8HeavyRightOutside,
}

__enum_to_actuator_brackets = dict((v, str(k[0]) + f' ({k[1]})') for k, v in __actuator_brackets_to_enum.items())

__actuator_links_to_enum = {
    CaseInvariantString('X5'): enums.LinkType.X5,
    CaseInvariantString('X8'): enums.LinkType.X5,
    CaseInvariantString('R8'): enums.LinkType.R8,
}

__enum_to_actuator_links = dict((v, str(k)) for k, v in __actuator_links_to_enum.items())

__actuator_links = {
    CaseInvariantString('X5'),
    CaseInvariantString('X8'),
    CaseInvariantString('R8'),
}

__brackets = [
    BracketParser('X5-LightBracket',
                  ['left', 'right'], 0.1),
    BracketParser('X5-HeavyBracket',
                  ['left-inside', 'right-inside',
                   'left-outside', 'right-outside'], 0.215),
    BracketParser('R8-LightBracket',
                  ['left', 'right'], 0.1),  # FIXME: MASS
    BracketParser('R8-HeavyBracket',
                  ['left-inside', 'right-inside',
                   'left-outside', 'right-outside'], 0.215),  # FIXME: MASS
]


################################################################################
# Parsing Functions
################################################################################


def __assert_str(value, name='value'):
  if not isinstance(value, str):
    raise TypeError(f'{name} must be a str')


def parse_frame_type(value: str):
  tls_val = _parser_tls.get_frame_type(value)
  if tls_val is not None:
    return tls_val
  # If not cached:
  try:
    tls_val = __frame_types_to_enum[value]
    _parser_tls.set_frame_type(value, tls_val)
    return tls_val
  except Exception as e:
    __assert_str(value, 'frame type')
    if isinstance(e, KeyError):
      raise ValueError(f'{value} is not a valid frame type')
    else:
      raise e


def parse_joint_type(value: str):
  tls_val = _parser_tls.get_joint(value)
  if tls_val is not None:
    return tls_val
  # If not cached:
  try:
    fixed_val = value.lower()
    tls_val = __joint_types_to_enum[fixed_val]
    _parser_tls.set_joint(value, tls_val)
    return tls_val
  except Exception as e:
    __assert_str(value, 'joint type')
    if isinstance(e, KeyError):
      raise ValueError(f'{value} is not a valid joint type')
    else:
      raise e


def parse_actuator(value: str):
  tls_val = _parser_tls.get_actuator(value)
  if tls_val is not None:
    return tls_val
  # If not cached:
  try:
    fixed_val = value.upper()
    tls_val = __actuator_to_enum[CaseInvariantString(fixed_val)]
    _parser_tls.set_actuator(value, tls_val)
    return tls_val
  except Exception as e:
    __assert_str(value, 'actuator')
    if isinstance(e, KeyError):
      raise ValueError(f'{value} is not a valid actuator')
    else:
      raise e


def parse_actuator_link(value, extension, twist):
  __assert_str(value)

  value = value.strip().upper()
  if not (value in __actuator_links):
    raise ValueError(f'{value} is not a valid actuator link')

  try:
    extension = float(extension)
  except ValueError:
    raise ValueError(f'cannot convert extension={extension} to a float')
  except TypeError:
    raise TypeError(f'cannot convert extension={extension} (type {type(extension)}) to a float')

  try:
    twist = float(twist)
  except ValueError:
    raise ValueError(f'cannot convert twist={twist} to a float')
  except TypeError:
    raise TypeError(f'cannot convert twist={twist} (type {type(twist)}) to a float')

  return extension, twist


def parse_bracket(bracket, mount):
  __assert_str(bracket, 'bracket')
  __assert_str(mount, 'mount')

  bracket = bracket.strip()
  mount = mount.strip().lower()

  for entry in __brackets:
    match = entry.match(bracket, mount)
    if match:
      break
  else:
    # Should never happen, but let's make this lint-free
    match = None

  if not match:
    raise ValueError(f'bracket={bracket} and mount={mount} is not a valid bracket')

  com = np.identity(4, np.float64)
  output = np.identity(4, np.float64)
  mass = match.mass

  if match.light:
    if match.right:
      mult = -1.0
    else:
      mult = 1.0

    set_translate(com, 0.0, mult*0.0215, 0.02)
    set_rotate_x(output, mult*neg_half_pi)
    set_translate(output, 0.0, mult*0.043, 0.04)

  elif match.heavy:
    if match.right:
      lr_mult = -1.0
    else:
      lr_mult = 1.0

    if match.outside:
      y_dist = 0.0375
    else:
      y_dist = -0.0225

    set_translate(com, 0.0, lr_mult * 0.5 * y_dist, 0.0275)
    set_rotate_x(output, lr_mult * neg_half_pi)
    set_translate(output, 0.0, lr_mult * y_dist, 0.055)

  else:
    raise RuntimeError(f'Unknown bracket type {match.bracket_name}')

  return com, output, mass


################################################################################
# String to enum
################################################################################


def actuator_str_to_enum(actuator: str):
  __assert_str(actuator, 'actuator')
  actuator_ci = CaseInvariantString(actuator)
  if actuator_ci not in __actuator_to_enum:
    raise ValueError(f'Unknown actuator type {actuator_ci}')
  return __actuator_to_enum[actuator_ci]


def bracket_str_to_enum(bracket, mount):
  __assert_str(bracket, 'bracket')
  __assert_str(mount, 'mount')

  k = _make_tup(bracket, mount)
  if k not in __actuator_brackets_to_enum:
    raise ValueError(f'Unknown bracket type (bracket: {bracket}, mount: {mount})')
  return __actuator_brackets_to_enum[k]


def link_str_to_enum(link: str):
  __assert_str(link, 'link')
  link_ci = CaseInvariantString(link)

  if link_ci not in __actuator_links_to_enum:
    raise ValueError(f'Unknown link type {link_ci}')
  return __actuator_links_to_enum[link_ci]


def end_effector_str_to_enum(end_effector):
  __assert_str(end_effector, 'end_effector')

  if end_effector not in __end_effector_types_to_enum:
    raise ValueError(f'Unknown end effector type {end_effector}')
  return __end_effector_types_to_enum[end_effector]


################################################################################
# Enum to string
################################################################################


def _add_pure_ints(d: 'dict[Any, str]'):
  to_add = [(int(key), val) for (key, val) in d.items() if not isinstance(key, int)]
  for k, v in to_add:
    d[k] = v


_add_pure_ints(__enum_to_actuator)
_add_pure_ints(__enum_to_actuator_brackets)
_add_pure_ints(__enum_to_actuator_links)
_add_pure_ints(__enum_to_joint_types)

actuator_enum_to_str = lambda actuator: __enum_to_actuator[actuator]
bracket_enum_to_str = lambda bracket: __enum_to_actuator_brackets[bracket]
link_enum_to_str = lambda link: __enum_to_actuator_links[link]
joint_enum_to_str = lambda joint: __enum_to_joint_types[joint]
end_effector_enum_to_str = lambda joint: __enum_to_end_effector_types[joint]
