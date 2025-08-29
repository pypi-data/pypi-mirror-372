# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2022 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------

import ctypes
from ._internal.errors import HEBI_Exception

from ._internal import type_utils as _type_utils
from ._internal import math_utils as _math_utils
from ._internal import kinematics as _kinematics

from ctypes import CFUNCTYPE, c_size_t, c_void_p, cast
from ._internal.ffi.ctypes_defs import HebiRobotModelElementMetadata, HebiRobotModelElementTopology
from ._internal.ffi.ctypes_utils import byref, c_double_p, to_double_ptr, NULLPTR

from ._internal.ffi import  api, enums as _enums
from ._internal.ffi.enums import RobotModelElementType, FrameType, LinkType, JointType, MatrixOrdering
from ._internal.ffi.wrappers import UnmanagedObject

import numpy as np
import threading as _threading

import typing

from hebi._internal.ffi import enums
if typing.TYPE_CHECKING:
  from typing import Union, Sequence, Callable, Any, Sized
  import numpy.typing as npt
  VectorType = Union[Sequence[float], npt.NDArray[np.float64]]


class _RobotModelTLS_Buffers:

  __slots__ = ["_base_frame", "_inertia", "_double_buffer", "_com_transform", "_output_transform"]

  def __init__(self):
    self._base_frame = _type_utils.create_double_buffer(16)
    self._inertia: 'npt.NDArray[np.float64]' = np.empty(6, dtype=np.float64)
    self._double_buffer = _type_utils.create_double_buffer(256)
    self._com_transform: 'npt.NDArray[np.float64]' = np.identity(4, dtype=np.float64)
    self._output_transform: 'npt.NDArray[np.float64]' = np.identity(4, dtype=np.float64)

  @property
  def base_frame(self):
    return self._base_frame

  @property
  def inertia(self):
    return self._inertia

  @property
  def double_buffer(self):
    return self._double_buffer

  @property
  def com_transform(self):
    return self._com_transform

  @property
  def output_transform(self):
    return self._output_transform

  def grow_double_buffer_if_needed(self, min_capacity: int):
    if len(self._double_buffer) < min_capacity:
      self._double_buffer = _type_utils.create_double_buffer(min_capacity)


class _RobotModelTLS(_threading.local):
  """Thread local buffers for the RobotModel API.

  Note: this class **cannot** have the `__slots__` attribute, as it breaks
        the `threading.local` API.
  """

  def __init__(self):
    self._buffers = _RobotModelTLS_Buffers()

  @property
  def buffers(self):
    return self._buffers


_tls = _RobotModelTLS()


################################################################################
# Marshalling functions
################################################################################


def _get_matrix_ordering(matrix):
  if matrix.flags.carray:
    return MatrixOrdering.RowMajor
  return MatrixOrdering.ColumnMajor


################################################################################
# Class definitions
################################################################################


class RobotModel(UnmanagedObject):
  """Represents a chain or tree of robot elements (rigid bodies and joints).

  Currently, only chains of elements are fully supported.
  """
  __slots__ = ['_dof_count', '_element_count', '_frame_count_map', '_masses_cached']

  def __init__(self, **kwargs):
    has_existing_handle = False
    if 'existing_handle' in kwargs:
      kin_handle = kwargs['existing_handle']
      has_existing_handle = True
    else:
      kin_handle = api.hebiRobotModelCreate()

    super().__init__(kin_handle, api.hebiRobotModelRelease)

    self._dof_count = 0
    self._element_count = 0
    self._frame_count_map: 'dict[FrameType, int]' = dict()
    for frame_type in FrameType:
      self._frame_count_map[frame_type] = 0

    self._masses_cached: 'npt.NDArray[np.float64]' = np.empty(0, np.float64)

    if has_existing_handle:
      self.__update_cached_frame_counts()


  def get_subtree_with_root(self, *, tag: 'str | None' = None, element_idx: 'int | None' = None):
    if element_idx is None:
      if tag is None:
        raise ValueError('Must supply either tag or element_idx')
      element_idx = self.get_element_idx_by_tag(tag)

    handle = api.hebiRobotModelCreateSubtreeFromElement(self, element_idx)
    if handle:
      return RobotModel(existing_handle=handle)
    return None

  def __repr__(self):
    masses = self.masses
    metadata = self.metadata
    total_mass = masses.sum()
    body_count = len(masses)
    dof_count = self.dof_count

    #NOTE: The C API does not support payloads yet. This is intentionally omitted.
    #payload = self.payload
    ret = ('RobotModel with properties:\n' +
           '\n' +
           f'    body_count: {body_count}\n' +
           f'     dof_count: {dof_count}\n' +
           f'          mass: {total_mass:0.2f} [kg]\n' +
           '\n' +
           '    body  type             is_dof  mass [kg]\n' +
           '    ----  ---------------  ------  ---------\n')

    mass_idx = 0

    for i, elem_metadata in enumerate(metadata):
      #TODO: Fix the MetaData classes so they have some kind of property that
      # can be read to see if they have a mass or not, so this logic is simplified

      # Non-actuator joints don't have a mass associated with them, so they don't have a
      # corresponding value in `masses`. Print their mass as 0.0 and don't increment
      # mass_idx so that the masses map properly to the correct frame
      if elem_metadata.is_dof and not isinstance(elem_metadata, ActuatorMetaData):
        mass = 0.0
      else:
        mass = masses[mass_idx]
        mass_idx += 1

      is_dof_str = "true" if elem_metadata.is_dof else "false"
      ret += f'    {i:<4}  {str(elem_metadata):<15}  {is_dof_str:<6}  {mass:>9.4f}\n'

    return ret

  @property
  def base_frame(self) -> 'npt.NDArray[np.float64]':
    """The transform from the world coordinate system to the root kinematic
    body.

    :return: The base frame 4x4 matrix
    :rtype:  numpy.ndarray
    """
    frame = _tls.buffers.base_frame
    code = api.hebiRobotModelGetBaseFrame(self, frame, MatrixOrdering.RowMajor.value)
    if code != _enums.StatusSuccess:
      raise HEBI_Exception(code, 'hebiRobotModelGetBaseFrame failed')

    return np.array(frame, dtype=np.float64).reshape(4, 4)

  @base_frame.setter
  def base_frame(self, value):
    """Set the transform from a world coordinate system to the input of the
    root element in this robot model. Defaults to an identity 4x4 matrix.

    The world coordinate system is used for all position, vector,
    and transformation matrix parameters in the member functions.

    :param value: A 4x4 matrix representing the base frame
    :type value:  list, numpy.ndarray, ctypes.Array

    :raises HEBI_Exception: If the base frame could not be set
    :raises ValueError:     If the input matrix is not of the right size or type
    """
    base_frame = _type_utils.to_contig_sq_mat(value, size=4)
    if not _math_utils.is_finite(base_frame):
      raise ValueError('Base frame must be entirely finite')

    code = api.hebiRobotModelSetBaseFrame(self, to_double_ptr(base_frame), _get_matrix_ordering(base_frame).value)
    if code != _enums.StatusSuccess:
      raise HEBI_Exception(code, 'hebiRobotModelSetBaseFrame failed')

  @property
  def metadata(self):
    """Retrieves a list of info about each individual element which composes
    this robot.

    :rtype: list
    """
    element_count = self._element_count
    ret = list()
    for i in range(element_count):
      meta_elem = HebiRobotModelElementMetadata()
      api.hebiRobotModelGetElementMetadata(self, i, byref(meta_elem))
      ret.append(_create_metadata_object(meta_elem))
    return ret

  @property
  def element_count(self):
    """The number of elements which compose the kinematic tree. This is greater
    than or equal to the degrees of freedom.

    :rtype: int
    """
    return self._element_count

  def __get_frame_count(self, frame_type: 'FrameType'):
    return self._frame_count_map[frame_type]

  def get_frame_count(self, frame_type: 'str | FrameType'):
    """The number of frames in the forward kinematics.

    Note that this depends on the type of frame requested:
      * for center of mass frames, there is one per added body.
      * for output frames, there is one per output per body.

    Valid strings for valid frame types are:
      * For center of mass:  ``'CoM'`` or ``'com'``
      * For output:          ``'output'``
      * For input:           ``'input'``

    :param frame_type: Which type of frame to consider
    :type frame_type:  str

    :return: the number of frames of the specified type
    :rtype:  int

    :raises ValueError: If the string from ``frame_type`` is invalid
    :raises TypeError:  If the ``frame_type`` argument is not a string
    """
    if isinstance(frame_type, str):
      frame_type_ = _kinematics.parse_frame_type(frame_type)
    else:
      frame_type_ = frame_type
    return self.__get_frame_count(frame_type_)

  def get_element_idx_by_tag(self, tag: str):
    # self, str, strlen, out_idx
    idx_out = c_size_t()
    from ._internal.type_utils import create_string_buffer_compat as create_str
    c_str = create_str(tag)
    api.hebiRobotModelGetElementIndexFromTag(self, c_str, len(c_str)-1, byref(idx_out))
    return idx_out.value

  def get_frame_idx_from_element_idx(self, element_idx: int, frame_type: 'enums.FrameType | str'):
    if isinstance(frame_type, str):
      frame_type = _kinematics.parse_frame_type(frame_type)

    num_frames = self.get_frame_count(frame_type)
    table = (HebiRobotModelElementTopology * num_frames)()
    if api.hebiRobotModelGetTreeTopology(self, frame_type, cast(table, ctypes.POINTER(HebiRobotModelElementTopology))) != enums.StatusSuccess:
      return -1

    for idx, elem in enumerate(table):
      if elem.element_index_ == element_idx:
        return idx

    return -1

  @property
  def dof_count(self):
    """The number of settable degrees of freedom in the kinematic tree. This is
    equal to the number of actuators added.

    :return: the degrees of freedom.
    :rtype:  int
    """
    return self._dof_count

  def __update_cached_masses(self, num_com_frames):
    masses: 'npt.NDArray[np.float64]' = np.empty(num_com_frames, dtype=np.float64)
    api.hebiRobotModelGetMasses(self, to_double_ptr(masses))
    self._masses_cached = masses

  def __update_cached_frame_counts(self):
    self._dof_count = int(api.hebiRobotModelGetNumberOfDoFs(self))
    self._element_count = int(api.hebiRobotModelGetNumberOfElements(self))
    for frame_type in FrameType:
      self._frame_count_map[frame_type] = api.hebiRobotModelGetNumberOfFrames(self, frame_type.value)

    self.__update_cached_masses(self._frame_count_map[FrameType.CenterOfMass])

  def __assert_equals_dof_count(self, positions: 'Sized'):
    expect = self._dof_count
    actual = len(positions)
    if actual != expect:
      raise ValueError(f'Input positions must be of same length of DOFs (expected length of {expect}, got {actual})')

  def __try_add(self, body, previous=None, output_index=0):
    res = api.hebiRobotModelAdd(self, previous, output_index, body)
    if res != _enums.StatusSuccess:
      return False
    self.__update_cached_frame_counts()
    return True

  def add_rigid_body(self, com, inertia, mass, output):
    """Adds a rigid body with the specified properties to the robot model.

    This can be 'combined' with the parent element
    (the element to which this is attaching), which means that the mass,
    inertia, and output frames of this element will be integrated with
    the parent. The mass will be combined, and the reported parent output frame
    that this element attached to will be replaced with the output from
    this element (so that the number of output frames and masses remains constant).

    Deprecation notice: It is deprecated to pass a `str` in as a parameter to any argument.
    This functionality will be removed in a future release.

    :param com: 3 element vector or 4x4 matrix.
                If this parameter is a 3 element vector, the elements will be used
                as the translation vector in a homogeneous transformation matrix.
                The homogeneous transform is to the center
                of mass location, relative to the input frame of the element.
                Note that this frame is also the frame in which
                the inertia tensor is given.
    :type com:  str, list, numpy.ndarray, ctypes.Array

    :param inertia: The 6 element representation (Ixx, Iyy, Izz, Ixy, Ixz, Iyz)
                    of the inertia tensor, in the frame given by the COM.
    :type inertia:  str, list, numpy.ndarray, ctypes.Array

    :param mass:    The mass of this element.
    :type mass:     int, float

    :param output:  4x4 matrix of the homogeneous transform to the output frame,
                    relative to the input frame of the element.
    :type output:   str, list, numpy.ndarray, ctypes.Array

    :return: ``True`` if the body could be added, ``False`` otherwise.
    :rtype:  bool

    :raises ValueError: if com, inertia, or output are of wrong size
    """
    inertia = np.asarray(inertia, np.float64)
    if len(inertia) != 6:
      raise ValueError('inertia must be a 6 element array')

    user_com = np.asarray(com, dtype=np.float64)
    com = np.identity(4, dtype=np.float64)
    if user_com.shape == (3,):
      # User provided 3 element array [x,y,z]
      # Use this in the translation verctor of transform
      com[0:3, 3] = user_com
    elif user_com.shape == (4, 4):
      np.copyto(com, user_com)

    body = api.hebiRobotModelElementCreateRigidBody(to_double_ptr(com), to_double_ptr(inertia), mass,
                                                    1, to_double_ptr(output), _get_matrix_ordering(output).value)
    return self.__try_add(body)

  def add_joint(self, joint_type):
    """Adds a degree of freedom about the specified axis.

    This does not represent an element with size or mass, but only a
    connection between two other elements about a particular axis.

    :param joint_type: The axis of rotation or translation about which this
                       joint allows motion.

                       For a linear joint, use:
                       ``tx``, ``x``, ``y``, ``ty``, ``tz``, or ``z``

                       For a rotation joint, use:
                       ``rx``, ``ry``, or ``rz``

                       This argument is case insensitive.
    :type joint_type:  str

    :raises ValueError: If the string from ``joint_type`` is invalid
    :raises TypeError:  If the ``joint_type`` argument is not a string
    """
    return self.__try_add(api.hebiRobotModelElementCreateJoint(_kinematics.parse_joint_type(joint_type).value))

  def add_actuator(self, actuator_type: str):
    """Add an element to the robot model with the kinematics/dynamics of an X
    or R series HEBI actuator.

    :param actuator_type: The type of actuator to add.
    :type actuator_type:  str, unicode

    :return: ``True`` if the actuator could be added, ``False`` otherwise.
    :rtype:  bool

    :raises ValueError: If the string from ``actuator_type`` is invalid
    :raises TypeError:  If the ``actuator_type`` argument is not a string
    """
    return self.__try_add(api.hebiRobotModelElementCreateActuator(_kinematics.actuator_str_to_enum(actuator_type).value))

  def add_link(self, link_type: str, extension: float, twist: float):
    """Add an element to the robot model with the kinematics/dynamics of a link
    between two actuators.

    :param link_type: The type of link between the actuators, e.g. a tube link
                      between two X5 or X8 actuators.
    :type link_type:  str, unicode

    :param extension: The center-to-center distance between the actuator
                      rotational axes.
    :type extension:  int, float

    :param twist:     The rotation (in radians) between the actuator axes of
                      rotation. Note that a 0 radian rotation will result
                      in a z-axis offset between the two actuators,
                      and a pi radian rotation will result in the actuator
                      interfaces to this tube being in the same plane, but the
                      rotational axes being anti-parallel.
    :type twist:      int, float

    :return: ``True`` if link was added, ``False`` otherwise
    :rtype:  bool

    :raises ValueError: If the string from ``link_type`` is invalid
    :raises TypeError:  If the ``link_type`` argument is not a string
    """
    extension = float(extension)
    twist = float(twist)

    input_type = _enums.LinkInputType.RightAngle
    output_type = _enums.LinkOutputType.RightAngle
    link_enum = _kinematics.link_str_to_enum(link_type)
    return self.__try_add(api.hebiRobotModelElementCreateLink(link_enum.value, input_type.value, output_type.value, extension, twist))

  def add_bracket(self, bracket_type: str, mount: str):
    """Add an element to the robot model with the kinematics/dynamics of a
    bracket between two actuators.

    :param bracket_type: The type of bracket to add.
    :type bracket_type:  str, unicode

    :param mount: The mount type of the bracket
    :type mount:  str, unicode

    :return: ``True`` if bracket was added, ``False`` otherwise
    :rtype:  bool

    :raises ValueError: If the string from either ``bracket_type`` or ``mount`` are invalid
    :raises TypeError:  If the either ``bracket_type`` or ``mount`` arguments are not strings
    """
    return self.__try_add(api.hebiRobotModelElementCreateBracket(_kinematics.bracket_str_to_enum(bracket_type, mount).value))

  def add_end_effector(self, end_effector_type: str):
    """Add an end effector element to the robot model.

    For a "custom" type end effector, indentity transforms and
    zero mass and inertia parameters are used.

    :param end_effector_type: The type of end_effector to add.
    :type end_effector_type:  str, unicode

    :return: ``True`` if the end effector was added, ``False`` otherwise
    :rtype:  bool

    :raises ValueError: If the string from ``end_effector_type`` is invalid
    :raises TypeError:  If the ``end_effector_type`` argument is not a string
    """
    end_effector_enum = _kinematics.end_effector_str_to_enum(end_effector_type)
    body = api.hebiRobotModelElementCreateEndEffector(end_effector_enum.value, None, None, 0, None, MatrixOrdering.RowMajor.value)
    return self.__try_add(body)

  def get_forward_kinematics(self,
                             frame_type: 'str | FrameType',
                             positions: 'VectorType',
                             output: 'list[npt.NDArray[np.float64]] | None' = None):
    """Generates the forward kinematics for the given robot model.

    The order of the returned frames is in a depth-first tree.

    :param frame_type: Which type of frame to consider. See :meth:`.get_frame_count` for valid values.
    :type frame_type:  str

    :param positions: A vector of joint positions/angles (in SI units of meters
                      or radians) equal in length to the number of DoFs
                      of the kinematic tree.
    :type positions:  list, numpy.ndarray, ctypes.Array

    :param output:    An optional parameter, which, if not ``None``, specifies
                      a list into which to put the output frames. If this
                      parameter is not ``None``, it must be large enough
                      to fit all of the frames. No type or size checking
                      is performed, and it is required that you handle error
                      cases yourself.
    :type output:     list

    :return:  An list of 4x4 transforms; this is resized as necessary
              in the function and filled in with the 4x4 homogeneous transform
              of each frame. Note that the number of frames depends
              on the frame type.
    :rtype:   list

    :raises TypeError:  If ``frame_type`` is not a string
    :raises ValueError: If the ``positions`` input is not equal to the
                        degrees of freedom of the RobotModel
    """
    if isinstance(frame_type, FrameType):
      frame_type_enum = frame_type
    else:
      frame_type_enum = _kinematics.parse_frame_type(frame_type)
    num_frames = self.__get_frame_count(frame_type_enum)

    positions = np.asarray(positions, np.float64)
    self.__assert_equals_dof_count(positions)
    if not _math_utils.is_finite(positions):
      raise ValueError('Input positions must be entirely finite')

    # Edge case
    if num_frames == 0:
      return []

    _tls.buffers.grow_double_buffer_if_needed(num_frames * 16)
    frames = _tls.buffers.double_buffer

    api.hebiRobotModelGetForwardKinematics(self, frame_type_enum.value, to_double_ptr(positions), frames, MatrixOrdering.RowMajor.value)

    if output is None:
      mat: 'npt.NDArray[np.float64]' = np.empty((4, 4), dtype=np.float64)
      output = [mat.copy() for _ in range(num_frames)]
    for i in range(num_frames):
      start = i * 16
      end = start + 16
      np.copyto(output[i].ravel(), frames[start:end])
    return output

  def get_forward_kinematics_mat(self, frame_type: 'str | FrameType', positions: 'VectorType', output: 'npt.NDArray[np.float64] | None' = None):
    """Generates the forward kinematics for the given robot model.

    The order of the returned frames is in a depth-first tree.

    :param frame_type: Which type of frame to consider. See :meth:`.get_frame_count` for valid values.
    :type frame_type:  str

    :param positions: A vector of joint positions/angles (in SI units of meters
                      or radians) equal in length to the number of DoFs
                      of the kinematic tree.
    :type positions:  list, numpy.ndarray, ctypes.Array

    :param output:    An optional parameter, which, if not ``None``, specifies
                      a numpy array into which to put the output frames. If this
                      parameter is not ``None``, it must be large enough
                      to fit all of the frames. No type or size checking
                      is performed, and it is required that you handle error
                      cases yourself.
    :type output:     numpy.ndarray

    :return:  An numpy array (4 x 4 x frames) of 4x4 transforms; this is resized
              as necessary in the function and filled in with the 4x4 homogeneous
              transform of each frame. Note that the number of frames depends
              on the frame type.
    :rtype:   numpy.ndarray

    :raises TypeError:  If ``frame_type`` is not a string
    :raises ValueError: If the ``positions`` input is not equal to the
                        degrees of freedom of the RobotModel
    """
    if isinstance(frame_type, FrameType):
      frame_type_enum = frame_type
    else:
      frame_type_enum = _kinematics.parse_frame_type(frame_type)
    num_frames = self.__get_frame_count(frame_type_enum)

    positions = np.asarray(positions, np.float64)
    self.__assert_equals_dof_count(positions)

    # Edge case
    if num_frames == 0:
      return np.empty(0)

    if output is None:
      output = np.empty((num_frames, 4, 4), dtype=np.float64)

    api.hebiRobotModelGetForwardKinematics(self,
                                           frame_type_enum,
                                           positions.ctypes.data_as(c_double_p),
                                           output.ctypes.data_as(c_double_p),
                                           MatrixOrdering.RowMajor.value)

    return output

  def get_end_effector(self, positions: 'VectorType', output: 'npt.NDArray[np.float64] | None' = None):
    """Generates the forward kinematics to the end effector (leaf node)

    Note: for center of mass frames, this is one per leaf node; for output
    frames, this is one per output per leaf node, in depth first order.

    This method is for kinematic chains that only have a single leaf node frame.

    :param positions: A vector of joint positions/angles
                      (in SI units of meters or radians) equal in length
                      to the number of DoFs of the kinematic tree.
    :type positions:  list, numpy.ndarray, ctypes.Array

    :param output:    An optional parameter which allows you to avoid an allocation
                      by copying the results into this parameter. The size of this
                      parameter is not checked, so you must be certain that it is
                      a numpy array of dtype :class:`float` (``np.float64``)
                      with 16 elements (e.g., a 4x4 matrix or 16 element array)
    :type output:     numpy.ndarray

    :return:  A 4x4 transform that is resized as necessary in the
              function and filled in with the homogeneous transform to the end
              effector frame.
    :rtype:   numpy.matrix

    :raises RuntimeError: If the RobotModel has no output frames
    :raises ValueError:   If the ``positions`` input is not equal to the
                          degrees of freedom of the RobotModel
    """
    num_frames = self.__get_frame_count(FrameType.Output)
    if num_frames == 0:
      raise RuntimeError('Cannot get end effector because RobotModel has no frames')

    positions = np.asarray(positions, np.float64)
    self.__assert_equals_dof_count(positions)
    if not _math_utils.is_finite(positions):
      raise ValueError('Input positions must be entirely finite')

    if output is None:
      output = np.empty((4, 4), dtype=np.float64)

    api.hebiRobotModelGetForwardKinematics(self,
                                           FrameType.EndEffector.value,
                                           positions.ctypes.data_as(c_double_p),
                                           output.ctypes.data_as(c_double_p),
                                           MatrixOrdering.RowMajor.value)
    return output

  def solve_inverse_kinematics(self, initial_positions: 'VectorType', *objectives: '_ObjectiveBase', **kwargs: 'Any'):
    """Solves for an inverse kinematics solution given a set of objectives.

    To avoid unnecessary allocations, provide ``output`` as a keyword argument.
    This argument must be a numpy array or matrix with dtype
    :class:`float` (``np.float64``) with size equal to the initial positions. *e.g.*,

    ``robot.solve_inverse_kinematics(positions, obj1, obj2, output=calc_pos) # calc_pos.size == positions.size``

    :param initial_positions: The seed positions/angles (in SI units of meters
                              or radians) from which to start the IK search;
                              equal in length to the number of DoFs of the
                              kinematic tree.
    :type initial_positions:  list, numpy.ndarray, ctypes.Array

    :param objectives:  A variable number of objectives used to define the IK
                        search (e.g., target end effector positions, etc).
                        Each argument must have a base class of Objective.

    :param kwargs:      An optional keyword arguments map, which currently
                        only allows an ``output`` argument

    :return:  A vector equal in length to the number of DoFs of the kinematic tree;
              this will be filled in with the IK solution
              (in SI units of meters or radians) and resized as necessary.
    :rtype:   numpy.ndarray

    :raises HEBI_Exception: If the IK solver failed
    :raises TypeError:      If any of the provided objectives are not
                            an objective type
    :raises ValueError:     If the ``initial_positions`` input is not equal
                            to the degrees of freedom of the RobotModel or has
                            non-finite elements (_i.e_, ``nan``, ``+/-inf``)
    """
    initial_positions = np.asarray(initial_positions, np.float64)
    self.__assert_equals_dof_count(initial_positions)
    if not _math_utils.is_finite(initial_positions):
      raise ValueError('Input initial positions must be entirely finite')

    dof_count = len(initial_positions)
    has_output = 'output' in kwargs
    if has_output:
      if kwargs['output'].size != dof_count:
        raise ValueError('output size must be same as initial_positions')

      output: 'npt.NDArray[np.float64]' = kwargs['output']
    else:
      output = np.empty(dof_count, dtype=np.float64)

    ik = api.hebiIKCreate()

    for entry in objectives:
      if not isinstance(entry, _ObjectiveBase):
        raise TypeError(f'{entry} is not an Objective')
      entry.add_objective(ik)

    code = api.hebiIKSolve(ik, self, to_double_ptr(initial_positions), output.ctypes.data_as(c_double_p), None)
    api.hebiIKRelease(ik)

    if code == _enums.StatusCode.InvalidArgument:
      raise HEBI_Exception(code, 'hebiIKSolve failed, one or more invalid objectives')
    elif code != _enums.StatusCode.Success:
      raise HEBI_Exception(code, 'hebiIKSolve failed')

    return output

  def __get_jacobians(self, frame_type, positions, rows: int, cols: int, order=MatrixOrdering.RowMajor, out: 'npt.NDArray[np.float64] | None' = None):
    """Callee is required to copy results back from TLS buffer."""
    if out is None:
      buffers = _tls.buffers
      buffers.grow_double_buffer_if_needed(rows * cols)
      ret = buffers.double_buffer
      api.hebiRobotModelGetJacobians(self, frame_type.value, positions, ret, order.value)
      return ret
    elif out.size != rows * cols:
      raise ValueError(f'Provided jacobians array should have {rows*cols} elements, has {out.size}.')

    api.hebiRobotModelGetJacobians(self, frame_type, positions, out.ctypes.data_as(c_double_p), order.value)
    return out

  def get_jacobians(self, frame_type: str, positions: 'VectorType', output: 'list[npt.NDArray[np.float64]] | None' = None):
    """Generates the Jacobian for each frame in the given kinematic tree.

    :param frame_type: Which type of frame to consider. See :meth:`.get_frame_count` for valid values.
    :param frame_type: str

    :param positions: A vector of joint positions/angles
                      (in SI units of meters or radians)
                      equal in length to the number of DoFs of the
                      kinematic tree.
    :type positions:  list, numpy.ndarray, ctypes.Array

    :param output:    An optional parameter which allows you to avoid an allocation
                      by copying the results into this parameter. The size of this
                      parameter is not checked, so you must be certain that it is
                      a list of the proper size with all numpy arrays
                      of dtype :class:`float` (``np.float64``) with (frames x dofs) elements
    :type output:     list

    :return:  A vector (length equal to the number of frames) of
              matrices; each matrix is a (6 x number of dofs)
              jacobian matrix for the corresponding frame of reference
              on the robot. It is resized as necessary inside this function.
    :rtype:   list
    """
    frame_type_enum = _kinematics.parse_frame_type(frame_type)
    num_frames = self.__get_frame_count(frame_type_enum)

    # Edge case
    if num_frames == 0:
      return []

    positions = np.asarray(positions, np.float64)
    self.__assert_equals_dof_count(positions)
    if not _math_utils.is_finite(positions):
      raise ValueError('Input positions must be entirely finite')

    dofs = self.dof_count
    rows = 6 * num_frames
    cols = dofs

    if output is None:
      mat = np.empty((6, cols), dtype=np.float64)
      output = [mat.copy() for _ in range(num_frames)]

    jacobians = self.__get_jacobians(frame_type_enum, to_double_ptr(positions), rows, cols)

    stride = cols * 6
    for i in range(0, num_frames):
      start = i * stride
      end = start + stride
      np.copyto(output[i].ravel(), jacobians[start:end])

    return output

  def get_jacobians_mat(self, frame_type: 'str | FrameType', positions: 'VectorType', output: 'npt.NDArray[np.float64] | None' = None):
    """Generates the Jacobian for each frame in the given kinematic tree.

    :param frame_type: Which type of frame to consider. See :meth:`.get_frame_count` for valid values.
    :param frame_type: str

    :param positions: A vector of joint positions/angles
                      (in SI units of meters or radians)
                      equal in length to the number of DoFs of the
                      kinematic tree.
    :type positions:  list, numpy.ndarray, ctypes.Array

    :param output:    An optional parameter which allows you to avoid an allocation
                      by copying the results into this parameter. The size of this
                      parameter is not checked, so you must be certain that it is
                      a numpy array with dimensions (6 x dofs x frames) and
                      dtype :class:`float` (``np.float64``)
    :type output:     numpy.ndarray

    :return:  A (6 x dofs x frames) numpy array containing the
              jacobian matrix for each frame of reference
              on the robot. It is resized as necessary inside this function.
    :rtype:   numpy.ndarray
    """
    if isinstance(frame_type, FrameType):
      frame_type_enum = frame_type
    else:
      frame_type_enum = _kinematics.parse_frame_type(frame_type)
    num_frames = self.__get_frame_count(frame_type_enum)

    # Edge case
    if num_frames == 0:
      return np.empty(0)

    positions = np.ascontiguousarray(positions, np.float64)
    self.__assert_equals_dof_count(positions)

    dofs = self.dof_count
    rows = 6 * num_frames
    cols = dofs

    if output is None:
      output = np.empty((num_frames, 6, cols), dtype=np.float64)

    self.__get_jacobians(frame_type_enum, to_double_ptr(positions), rows, cols, out=output)

    return output

  def get_jacobian_end_effector(self, positions, output=None):
    """Generates the Jacobian for the end effector (leaf node) frames(s).

    Note: for center of mass frames, this is one per leaf node; for output
    frames, this is one per output per leaf node, in depth first order.

    This method is for kinematic chains that only have a single leaf node frame.

    :param positions: A vector of joint positions/angles (in SI units of
                      meters or radians) equal in length to the number of
                      DoFs of the kinematic tree.
    :type positions:  list, numpy.ndarray, ctypes.Array

    :param output:    An optional parameter which allows you to avoid an allocation
                      by copying the results into this parameter. The size of this
                      parameter is not checked, so you must be certain that it is
                      a numpy array or matrix of dtype :class:`float` (``np.float64``)
                      with (frames x dofs) elements
    :type output:     numpy.ndarray

    :return:  A (6 x number of dofs) jacobian matrix for the corresponding
              end effector frame of reference on the robot. It is resized as
              necessary inside this function.
    :rtype:   numpy.ndarray

    :raises RuntimeError: If the RobotModel has no output frames
    :raises ValueError:   If the ``positions`` input is not equal to the
                          degrees of freedom of the RobotModel
    """
    num_frames = self.__get_frame_count(FrameType.EndEffector)
    if num_frames == 0:
      raise RuntimeError('Cannot get end effector because RobotModel has no frames')

    rows = 6 * num_frames
    cols = self.dof_count

    positions = np.asarray(positions, np.float64)
    self.__assert_equals_dof_count(positions)

    if output is None:
      output = np.empty((rows, cols), dtype=np.float64)

    self.__get_jacobians(FrameType.EndEffector, to_double_ptr(positions), rows, cols, out=output)

    return output

  @property
  def masses(self):
    """The mass of each rigid body (or combination of rigid bodies) in the
    robot.

    :return: The masses as an array
    :rtype:  numpy.ndarray
    """
    return self._masses_cached.copy()
  
  @property
  def max_speeds(self):
    """The maximum speed of each degree of freedom in the robot.

    :return: The maximum speeds as an array
    :rtype:  numpy.ndarray
    """
    max_speeds: 'npt.NDArray[np.float64]' = np.empty(self.dof_count, dtype=np.float64)
    api.hebiRobotModelGetMaxSpeeds(self, to_double_ptr(max_speeds))
    return max_speeds
  
  @property
  def max_efforts(self):
    """The maximum effort of each degree of freedom in the robot.

    :return: The maximum efforts as an array
    :rtype:  numpy.ndarray
    """
    max_efforts: 'npt.NDArray[np.float64]' = np.empty(self.dof_count, dtype=np.float64)
    api.hebiRobotModelGetMaxEfforts(self, to_double_ptr(max_efforts))
    return max_efforts

  def get_grav_comp_efforts(self,
                            positions: 'npt.NDArray[np.float64]',
                            gravity: 'npt.NDArray[np.floating[Any]]',
                            jacobians: 'npt.NDArray[np.float64] | None' = None,
                            output: 'npt.NDArray[np.float64] | None' = None):
    """
    :param positions:
    :param gravity:
    :param jacobians: Optionally pass in pre-computed jacobians for the
                      desired position to avoid recomputing them. Should
                      have dimensions (6 x dof x #frames)
    :type jacobians:  np.ndarray, NoneType

    :param output:
    :type output:  np.ndarray, NoneType

    :return:
    :rtype:  np.ndarray
    """
    g_norm = np.linalg.norm(gravity)
    if g_norm > 0.0:
      gravity *= -9.81/g_norm

    if output is None:
      comp_torque = np.empty(self.dof_count)
    else:
      comp_torque = output

    code = api.hebiRobotModelGetGravityCompensationTorques(self,
                                                           positions.ctypes.data_as(c_double_p),
                                                           gravity.ctypes.data_as(c_double_p),
                                                           comp_torque.ctypes.data_as(c_double_p))

    if code != _enums.StatusCode.Success:
      raise HEBI_Exception(code, 'hebiRobotModelGetGravityCompensationTorques failed')

    return comp_torque

  def get_dynamic_comp_efforts(self,
                               fbk_positions: 'npt.NDArray[np.float64]',
                               cmd_positions: 'npt.NDArray[np.float64]',
                               cmd_velocities: 'npt.NDArray[np.float64]',
                               cmd_accels: 'npt.NDArray[np.float64]',
                               dt=1e-3,
                               jacobians: 'npt.NDArray[np.float64] | None' = None,
                               output: 'npt.NDArray[np.float64] | None' = None):
    """
    :param fbk_positions:
    :param cmd_positions:
    :param cmd_velocities:
    :param cmd_accels:
    :param robot:
    :param dt:
    :param jacobians: Optionally pass in pre-computed jacobians for the
                      fbk_position to avoid recomputing them. Should
                      have dimensions (6 x dof x #frames)
    :type jacobians:  np.ndarray, NoneType

    :return:
    :rtype:  np.ndarray
    """

    if output is None:
      efforts = np.empty(self.dof_count, dtype=np.float64)
    else:
      efforts = output

    code = api.hebiRobotModelGetDynamicsCompensationTorques(self,
                                                            fbk_positions.ctypes.data_as(c_double_p),
                                                            cmd_positions.ctypes.data_as(c_double_p),
                                                            cmd_velocities.ctypes.data_as(c_double_p),
                                                            cmd_accels.ctypes.data_as(c_double_p),
                                                            efforts.ctypes.data_as(c_double_p))

    if code != _enums.StatusCode.Success:
      raise HEBI_Exception(code, 'hebiRobotModelGetDynamicsCompensationTorques failed')

    return efforts


################################################################################
# Robot Model metadata functionality
################################################################################


class OtherMetaData:
  """Metadata pertaining to an unknown object."""

  def __init__(self):
    pass

  def __repr__(self):
    return "Type: Unknown/Other"

  def __str__(self):
    return "Unknown/Other"

  @property
  def type(self):
    """
    :return: The enum value corresponding to this type
    """
    return RobotModelElementType.Other

  @property
  def is_dof(self):
    """
    :return: ``True`` if this element corresponds to a degree of freedom; ``False`` otherwise
    :rtype:  bool
    """
    return False


class ActuatorMetaData:
  """Metadata pertaining to an actuator."""

  __slots__ = ['_actuator_type']

  def __init__(self, actuator_type):
    self._actuator_type = actuator_type

  def __repr__(self):
    return "Type:  Actuator\n" +\
           f"Model: {_kinematics.actuator_enum_to_str(self._actuator_type)}\n"

  def __str__(self):
    return _kinematics.actuator_enum_to_str(self._actuator_type)

  @property
  def actuator_type(self):
    """
    :return: The enum value corresponding to the specific actuator type of this element
    """
    return self._actuator_type

  @property
  def type(self):
    """
    :return: The enum value corresponding to this type
    """
    return RobotModelElementType.Actuator

  @property
  def is_dof(self):
    """
    :return: ``True`` if this element corresponds to a degree of freedom; ``False`` otherwise
    :rtype:  bool
    """
    return True


class BracketMetaData:
  """Metadata pertaining to a bracket."""

  __slots__ = ['_bracket_type']

  def __init__(self, bracket_type):
    self._bracket_type = bracket_type

  def __repr__(self):
    return "Type:        Bracket\n" +\
           f"Orientation: {_kinematics.bracket_enum_to_str(self._bracket_type)}\n"

  def __str__(self):
    return "Bracket"

  @property
  def bracket_type(self):
    """
    :return: The enum value corresponding to the specific bracket type of this element
    """
    return self._bracket_type

  @property
  def type(self):
    """
    :return: The enum value corresponding to this type
    """
    return RobotModelElementType.Bracket

  @property
  def type_str(self):
    """
    :return: A string representing the type of this element
    :rtype: str
    """
    return "Bracket"

  @property
  def is_dof(self):
    """
    :return: ``True`` if this element corresponds to a degree of freedom; ``False`` otherwise
    :rtype:  bool
    """
    return False


class JointMetaData:
  """Metadata pertaining to a joint."""

  __slots__ = ['_joint_type']

  def __init__(self, joint_type: int):
    self._joint_type = JointType(joint_type)

  def __repr__(self):
    return "Type:      Joint\n" +\
           f"Transform: {_kinematics.joint_enum_to_str(self._joint_type)}\n"

  def __str__(self):
    return "Joint"

  @property
  def joint_type(self):
    """
    :return: The enum value corresponding to the specific joint type of this element
    """
    return self._joint_type

  @property
  def type(self):
    """
    :return: The enum value corresponding to this type
    """
    return RobotModelElementType.Joint

  @property
  def type_str(self):
    """
    :return: A string representing the type of this element
    :rtype: str
    """
    return "Joint"

  @property
  def is_dof(self):
    """
    :return: ``True`` if this element corresponds to a degree of freedom; ``False`` otherwise
    :rtype:  bool
    """
    return True


class LinkMetaData:
  """Metadata pertaining to a link."""

  __slots__ = ['_extension', '_link_type', '_twist']

  def __init__(self, link_type: int, extension, twist):
    self._link_type = LinkType(link_type)
    self._extension = extension
    self._twist = twist

  def __repr__(self):
    return "Type:      Link\n" +\
           f"SubType:   {_kinematics.link_enum_to_str(self._link_type)}\n" +\
           f"Extension: {self._extension}\n"

  def __str__(self):
    return "Link"

  @property
  def link_type(self):
    """
    :return: The enum value corresponding to the specific link type of this element
    """
    return self._link_type

  @property
  def extension(self):
    """
    :return: The extension of the link [m]
    :rtype:  float
    """
    return self._extension

  @property
  def twist(self):
    """
    :return: The twist/rotation of the link [rad]
    :rtype:  float
    """
    return self._twist

  @property
  def type(self):
    """
    :return: The enum value corresponding to this type
    """
    return RobotModelElementType.Link

  @property
  def type_str(self):
    """
    :return: A string representing the type of this element
    :rtype: str
    """
    return "Link"

  @property
  def is_dof(self):
    """
    :return: ``True`` if this element corresponds to a degree of freedom; ``False`` otherwise
    :rtype:  bool
    """
    return False

class RigidBodyMetaData:
  """Metadata pertaining to a rigid body."""

  __slots__ = []

  def __init__(self):
    pass

  def __repr__(self):
    return "Type: Rigid Body\n"

  def __str__(self):
    return "Rigid Body"

  @property
  def type(self):
    """
    :return: The enum value corresponding to this type
    """
    return RobotModelElementType.RigidBody

  @property
  def type_str(self):
    """
    :return: A string representing the type of this element
    :rtype: str
    """
    return "Rigid Body"

  @property
  def is_dof(self):
    """
    :return: ``True`` if this element corresponds to a degree of freedom; ``False`` otherwise
    :rtype:  bool
    """
    return False


class EndEffectorMetaData:
  """Metadata pertaining to an end effector."""

  __slots__ = ['_end_effector_type']

  def __init__(self, end_effector_type: int):
    self._end_effector_type = _enums.EndEffectorType(end_effector_type)

  def __repr__(self):
    return "Type:      End Effector\n" +\
           f"Transform: {_kinematics.end_effector_enum_to_str(self._end_effector_type)}\n"

  def __str__(self):
    return "End Effector"

  @property
  def end_effector_type(self):
    """
    :return: The enum value corresponding to the specific end effector type of this element
    """
    return self._end_effector_type

  @property
  def type(self):
    """
    :return: The enum value corresponding to this type
    """
    return RobotModelElementType.EndEffector

  @property
  def type_str(self):
    """
    :return: A string representing the type of this element
    :rtype: str
    """
    return "End Effector"

  @property
  def is_dof(self):
    """
    :return: ``True`` if this element corresponds to a degree of freedom; ``False`` otherwise
    :rtype:  bool
    """
    return False


def _create_metadata_object(c_data: HebiRobotModelElementMetadata):
  element_type = c_data.element_type_
  if element_type == RobotModelElementType.Actuator:
    return ActuatorMetaData(c_data.actuator_type_)
  elif element_type == RobotModelElementType.Bracket:
    return BracketMetaData(c_data.bracket_type_)
  elif element_type == RobotModelElementType.Joint:
    return JointMetaData(c_data.joint_type_)
  elif element_type == RobotModelElementType.Link:
    return LinkMetaData(c_data.link_type_, c_data.extension_, c_data.twist_)
  elif element_type == RobotModelElementType.RigidBody:
    return RigidBodyMetaData()
  elif element_type == RobotModelElementType.EndEffector:
    return EndEffectorMetaData(c_data.end_effector_type_)
  elif element_type == RobotModelElementType.Other:
    import sys
    sys.stderr.write(f"Warning: invalid robot model element type detected ({element_type})")
  return OtherMetaData()


################################################################################
# HRDF functionality
################################################################################


def _get_hrdf_import_error():
  c_buffer = api.hebiRobotModelGetImportError()
  return _type_utils.decode_string_buffer(c_buffer, 'utf-8')


def _get_hrdf_import_warning_count():
  return api.hebiRobotModelGetImportWarningCount()


def _get_hrdf_import_warning_at(index):
  if index < 0:
    raise IndexError(f'{index} < 0')
  count = _get_hrdf_import_warning_count()
  if index >= count:
    raise IndexError(f'{index} >= {count}')
  c_buffer = api.hebiRobotModelGetImportWarning(index)
  return _type_utils.decode_string_buffer(c_buffer, 'utf-8')


def _get_all_hrdf_import_warnings():
  count = _get_hrdf_import_warning_count()
  if count == 0:
    return []

  ret = [None] * count
  for i in range(0, count):
    ret[i] = _get_hrdf_import_warning_at(i)

  return ret


def import_from_hrdf(hrdf_file: str, warning_callback: 'Callable[[Any], None] | None' = None):
  """Import a robot description in the HRDF format as a RobotModel instance.

  Any warnings generated while importing will be printed to stderr,
  unless explicitly instructed otherwise by providing a callback.

  :param hrdf_file: The location of the HRDF file to import
  :param warning_callback: A function, which can accept one argument,
                           to call back if warnings are generated. If `None`,
                           warnings are printed to stderr

  :return: the RobotModel from the description file
  :rtype:  RobotModel

  :raises IOError:      If the provided file does not exist
  :raises RuntimeError: If the hrdf file could not be imported.
                        The associated error message will be displayed.
  """

  import os
  hrdf_file = str(hrdf_file)
  if not os.path.isfile(hrdf_file):
    raise IOError(f'{hrdf_file} is not a file')

  from ._internal.type_utils import create_string_buffer_compat as create_str
  handle = api.hebiRobotModelImport(create_str(hrdf_file))

  # Check if any warnings were generated
  warnings = _get_all_hrdf_import_warnings()
  if len(warnings) > 0:
    if warning_callback is None:
      msg = f'Importing HRDF file {hrdf_file} generated the following warning(s):\n'
      import sys
      sys.stderr.write(msg + '\n'.join(warnings) + '\n')
    else:
      warning_callback(warnings)

  if handle is None:
    error_message = _get_hrdf_import_error()
    raise RuntimeError(f'Failed to import HRDF file {hrdf_file}: {error_message}')

  return RobotModel(existing_handle=handle)


def import_from_hrdf_string(hrdf_string, warning_callback=None):
  """Provides same functionality as :meth:`.import_from_hrdf`, but accepts a
  string representing the HRDF as opposed to a string to the file representing
  the HRDF.

  :param hrdf_string: A string representing HRDF contents
  :type hrdf_string:  str
  """
  from ._internal.type_utils import create_string_buffer_compat as create_str
  handle = api.hebiRobotModelImportBuffer(create_str(hrdf_string), len(hrdf_string))

  # Check if any warnings were generated
  warnings = _get_all_hrdf_import_warnings()
  if len(warnings) > 0:
    if warning_callback is None:
      msg = 'Importing HRDF from buffer generated the following warning(s):\n'
      import sys
      sys.stderr.write(msg + '\n'.join(warnings) + '\n')
    else:
      warning_callback(warnings)

  if handle is None:
    error_message = _get_hrdf_import_error()
    raise RuntimeError(f'Failed to import HRDF from buffer: {error_message}')

  return RobotModel(existing_handle=handle)

################################################################################
# IK Objective functions
################################################################################


class _ObjectiveBase:

  __slots__ = ['__impl']

  def __init__(self, impl):
    self.__impl = impl

  def add_objective(self, internal):
    self.__impl(internal)


class PositionObjective(_ObjectiveBase):
  def __init__(self, frame_type: 'str | FrameType', *, xyz: 'npt.NDArray[np.float64]', idx: int = 0, weight: float = 1.0):
    self._x: float = xyz[0]
    self._y: float = xyz[1]
    self._z: float = xyz[2]

    if isinstance(frame_type, str):
      frame_type = _kinematics.parse_frame_type(frame_type)

    self._frame_type = frame_type
    self._idx = idx
    self._weight = float(weight)

    def hebi_ik_add_objective_frame_position(internal):
      res = api.hebiIKAddObjectiveFramePosition(internal,
                                                self._weight,
                                                self._frame_type.value,
                                                idx,
                                                self._x,
                                                self._y,
                                                self._z)
      if res != _enums.StatusSuccess:
        raise HEBI_Exception(res, 'hebiIKAddObjectiveFramePosition failed')

    super().__init__(hebi_ik_add_objective_frame_position)

  @property
  def x(self):
    return self._x

  @property
  def y(self):
    return self._y

  @property
  def z(self):
    return self._z

  @property
  def weight(self):
    return self._weight


def endeffector_position_objective(xyz: 'VectorType', weight: float = 1.0):
  """Create a position end effector objective with the given parameters.
  Analogous to `EndEffectorPositionObjective. <https://files.hebi.us/docs/cpp/cpp-1.0.0/classhebi_1_1robot__model_1_1EndEffectorPositionObjective.html>`_ in the C++ API.

  :param xyz: list of x, y, and z position objective points
  :type xyz:  list, numpy.ndarray, ctypes.Array

  :param weight: The weight of the objective
  :type weight:  int, float

  :return: the created objective

  :raises ValueError: if xyz does not have at least 3 elements
  """
  xyz = np.array(xyz, dtype=np.float64, copy=True)
  if len(xyz) < 3:
    raise ValueError('xyz must have length of at least 3')
  return PositionObjective(FrameType.EndEffector, xyz=xyz, weight=weight)


class SO3Objective(_ObjectiveBase):
  def __init__(self, frame_type: 'str | FrameType', *, rotation: 'npt.NDArray[np.float64]', idx: int = 0, weight: float = 1.0):
    if isinstance(frame_type, str):
      frame_type = _kinematics.parse_frame_type(frame_type)

    self._frame_type = frame_type
    self._rotation = rotation
    self._idx = idx
    self._weight = float(weight)

    def hebi_ik_add_objective_frame_so3(internal):
      res = api.hebiIKAddObjectiveFrameSO3(internal,
                                           self._weight,
                                           self._frame_type.value,
                                           idx,
                                           to_double_ptr(self._rotation),
                                           _get_matrix_ordering(self._rotation).value)
      if res != _enums.StatusSuccess:
        raise HEBI_Exception(res, 'hebiIKAddObjectiveFrameSO3 failed')

    super().__init__(hebi_ik_add_objective_frame_so3)

  @property
  def rotation(self):
    return self._rotation

  @property
  def weight(self):
    return self._weight


def endeffector_so3_objective(rotation: 'VectorType', weight: float = 1.0):
  """Create an SO3 end effector objective with the given parameters. Analogous
  to `EndEffectorSO3Objective. <https://files.hebi.us/docs/cpp/cpp-1.0.0/classhebi_1_1robot__model_1_1EndEffectorSO3Objective.html>`_ in the C++ API.

  :param rotation: SO3 rotation matrix
  :type rotation:  list, numpy.ndarray, ctypes.Array

  :param weight: The weight of the objective
  :type weight:  int, float

  :return: the created objective

  :raises ValueError: if rotation matrix is not convertible to a 3x3 matrix,
                      or if the rotation matrix is not in the
                      `SO(3) <https://en.wikipedia.org/wiki/Rotation_group_SO(3)>`_
                      group.
  """
  rotation = np.array(rotation, dtype=np.float64, copy=True)
  rotation = _type_utils.to_contig_sq_mat(rotation, size=3)

  if not _math_utils.is_so3_matrix(rotation):
    det = np.linalg.det(rotation)
    raise ValueError(f'Input rotation matrix is not SO(3). Determinant={det}')

  return SO3Objective(FrameType.EndEffector, rotation=rotation, weight=weight)


class TipAxisObjective(_ObjectiveBase):
  def __init__(self, frame_type: 'str | FrameType', *, axis: 'npt.NDArray[np.float64]', idx: int = 0, weight: float = 1.0):
    if isinstance(frame_type, str):
      frame_type = _kinematics.parse_frame_type(frame_type)

    self._frame_type = frame_type
    self._x: float = axis[0]
    self._y: float = axis[1]
    self._z: float = axis[2]
    self._idx = idx
    self._weight = float(weight)

    def hebi_ik_add_objective_frame_tip_axis(internal):
      res = api.hebiIKAddObjectiveFrameTipAxis(internal, self._weight, self._frame_type.value, self._idx, self._x, self._y, self._z)
      if res != _enums.StatusSuccess:
        raise HEBI_Exception(res, 'hebiIKAddObjectiveFrameTipAxis failed')

    super().__init__(hebi_ik_add_objective_frame_tip_axis)

  @property
  def x(self):
    return self._x

  @property
  def y(self):
    return self._y

  @property
  def z(self):
    return self._z

  @property
  def weight(self):
    return self._weight


def endeffector_tipaxis_objective(axis: 'VectorType', weight: float = 1.0):
  """Create a tip axis end effector objective with the given parameters.
  Analogous to `EndEffectorTipAxisObjective. <https://files.hebi.us/docs/cpp/cpp-1.0.0/classhebi_1_1robot__model_1_1EndEffectorTipAxisObjective.html>`_ in the C++ API.

  :param axis: list of x, y, and z tipaxis objective points
  :type axis:  list, numpy.ndarray, ctypes.Array

  :param weight: The weight of the objective
  :type weight:  int, float

  :return: the created objective

  :raises ValueError: if axis does not have at least 3 elements
  """
  axis = np.array(axis, dtype=np.float64, copy=True)
  if len(axis) < 3:
    raise ValueError('axis must have length of at least 3')

  return TipAxisObjective(FrameType.EndEffector, axis=axis, weight=weight)


def joint_limit_constraint(minimum: 'VectorType', maximum: 'VectorType', weight: float = 1.0):
  """Create a joint limit constraint objective. Analogous to
  `JointLimitConstraint. <https://files.hebi.us/docs/cpp/cpp-1.0.0/classhebi_1_1robot__model_1_1JointLimitConstraint.html>`_ in the C++ API.

  :param minimum:
  :type minimum:  str, list, numpy.ndarray, ctypes.Array

  :param maximum:
  :type maximum:  str, list, numpy.ndarray, ctypes.Array

  :param weight: The weight of the objective
  :type weight:  int, float

  :return: the created objective

  :raises ValueError: if minimum and maximum are not of the same size
  """
  minimum = np.array(minimum, dtype=np.float64, copy=True)
  maximum = np.array(maximum, dtype=np.float64, copy=True)

  if minimum.size != maximum.size:
    raise ValueError('size of min and max joint limit constraints must be equal')

  class JointLimitConstraint(_ObjectiveBase):
    def __init__(self, minimum, maximum, weight):
      self._minimum = minimum
      self._maximum = maximum
      self._weight = float(weight)

      def impl(internal):
        res = api.hebiIKAddConstraintJointAngles(internal, self._weight, self._minimum.size,
                                                 to_double_ptr(self._minimum), to_double_ptr(self._maximum))
        if res != _enums.StatusSuccess:
          raise HEBI_Exception(res, 'hebiIKAddConstraintJointAngles failed')

      super().__init__(impl)

    @property
    def minimum(self):
      return self._minimum

    @property
    def maximum(self):
      return self._maximum

    @property
    def weight(self):
      return self._weight

  return JointLimitConstraint(minimum, maximum, weight)


def custom_objective(num_errors, func, user_data=None, weight=1.0):
  """Construct a custom objective using a provided function. The `func`
  parameter is a function which accepts 3 parameters: `positions`, `errors` and
  `user_data`.

  The first two parameters are guaranteed to be numpy arrays
  with `dtype=np.float64`. The third parameter, `user_data`, may be `None`,
  or set by the user when invoking this function. It is simply used
  to share application state with the callback function.

  The length of `errors` in the callback will be equal to the `num_errors`
  parameter provided to this function.
  The elements in the `errors` parameter should be modified by the function
  to influence the IK solution.

  The `positions` parameter is the joints positions (or angles) at the current
  point in the optimization. This is a read only array - any attempt
  to modify its elements will raise an Exception.

  :param num_errors: The number of independent error values that this objective
                     returns
  :type num_errors:  int

  :param func:       The callback function

  :param weight:     The weight of the objective
  :type weight:      int, float

  :return: the created objective

  :raises ValueError: if num_errors is less than 1
  """
  if num_errors < 1:
    raise ValueError('num_errors must be a positive number')

  class CustomObjective(_ObjectiveBase):

    def __callback(self, user_data, num_positions, c_positions, c_errors):
      """The actual callback the C API invokes.

      Don't let the user mess with ffi calls.
      """
      positions = np.ctypeslib.as_array(c_positions, (num_positions,)).copy()
      errors = np.ctypeslib.as_array(c_errors, (self._num_errors,))
      self._func(positions, errors, self._user_data)

    def __init__(self, num_errors: int, func: 'Callable', user_data, weight):
      self._num_errors = num_errors
      self._func = func
      self._weight = float(weight)
      self._user_data = user_data

      self._c_func = CFUNCTYPE(None, c_void_p, c_size_t, c_double_p, c_double_p)(self.__callback)

      def impl(internal):
        res = api.hebiIKAddObjectiveCustom(internal, self._weight, self._num_errors, self._c_func, NULLPTR)
        if res != _enums.StatusSuccess:
          raise HEBI_Exception(res, 'hebiIKAddObjectiveCustom failed')

      super().__init__(impl)

    @property
    def num_errors(self):
      return self._num_errors

    @property
    def func(self):
      return self._func

    @property
    def weight(self):
      return self._weight

  return CustomObjective(num_errors, func, user_data, weight)
