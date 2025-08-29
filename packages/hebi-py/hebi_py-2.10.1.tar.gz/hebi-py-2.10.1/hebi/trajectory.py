# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------


import ctypes as _ctypes
import numpy as np
from ._internal import math_utils as _math_utils
from ._internal.trajectory import Trajectory as _Trajectory
from ._internal.ffi import api

from ._internal.ffi.ctypes_utils import pointer_offset, c_double_p
from ._internal.ffi.ctypes_defs import HebiTimeEstimationParams
from ._internal.ffi.enums import TimeEstimationMethod, StatusSuccess, StatusArgumentOutOfRange, StatusInvalidArgument

import typing
from typing import overload
if typing.TYPE_CHECKING:
  from typing import Literal
  import numpy.typing as npt


def _check_dims_2d(arr, name, waypoints, joints):
  shape = arr.shape
  shape_expected = (joints, waypoints)
  if shape != shape_expected:
    raise ValueError(f"Invalid dimensionality of {name} matrix (expected {shape_expected}, got {shape})")


def create_trajectory(time: 'npt.ArrayLike', position: 'npt.ArrayLike', velocity: 'npt.ArrayLike | None' = None, acceleration: 'npt.ArrayLike | None' = None):
  """Creates a smooth trajectory through a set of waypoints (position velocity
  and accelerations defined at particular times). This trajectory wrapper
  object can create multi-dimensional trajectories (i.e., multiple joints
  moving together using the same time reference).

  :param time: A vector of desired times at which to reach each
               waypoint; this must be defined
               (and not ``None`` or ``nan`` for any element).
  :type time:  list, numpy.ndarray

  :param position: A matrix of waypoint joint positions (in SI units). The
                   number of rows should be equal to the number of joints,
                   and the number of columns equal to the number of waypoints.
                   Any elements that are ``None`` or ``nan`` will be considered
                   free parameters when solving for a trajectory.
                   Values of ``+/-inf`` are not allowed.
  :type position:  list, numpy.ndarray, ctypes.Array

  :param velocity: An optional matrix of velocity constraints at the
                   corresponding waypoints; should either be ``None``
                   or matching the size of the positions matrix.
                   Any elements that are ``None`` or ``nan`` will be considered
                   free parameters when solving for a trajectory.
                   Values of ``+/-inf`` are not allowed.
  :type velocity:  NoneType, list, numpy.ndarray, ctypes.Array

  :param acceleration: An optional matrix of acceleration constraints at
                       the corresponding waypoints; should either be ``None``
                       or matching the size of the positions matrix.
                       Any elements that are ``None`` or ``nan`` will be considered
                       free parameters when solving for a trajectory.
                       Values of ``+/-inf`` are not allowed.
  :type acceleration:  NoneType, list, numpy.ndarray, ctypes.Array

  :return: The trajectory. This will never be ``None``.
  :rtype: Trajectory

  :raises ValueError: If dimensionality or size of any
                      input parameters are invalid.
  :raises RuntimeError: If trajectory could not be created.
  """
  if time is None:
    raise ValueError("time cannot be None")
  if position is None:
    raise ValueError("position cannot be None")

  time = np.asarray(time, np.float64)
  position = np.asarray(position, np.float64)
  # reshape 1D vector to 1xn 2darray
  if len(position.shape) == 1:
    position = position.reshape((1, -1))
  joints: int = position.shape[0]
  waypoints: int = position.shape[1]

  pointer_stride = waypoints * 8
  shape_checker = lambda arr, name: _check_dims_2d(arr, name, waypoints, joints)

  if time.size != waypoints:
    raise ValueError(f'length of time vector must be equal to number of waypoints (time: {time.size} != waypoints: {waypoints})')

  if not _math_utils.is_finite(time):
    raise ValueError('time vector must have all finite values')

  t_prev = time[0]
  for idx, t in enumerate(time[1:]):
    if t <= t_prev:
      raise ValueError(f'Trajectory waypoint times must monotonically increase! Waypoint at index {idx+1} '
                       f'with time {t} is not later than previous waypoint time {t_prev}')
    t_prev = t

  if velocity is None:
    velocity = np.full(position.shape, np.nan)
    velocity[:, 0] = 0
    velocity[:, -1] = 0

  velocity = np.asarray(velocity, np.float64)
  if len(velocity.shape) == 1:
    velocity = velocity.reshape((1, -1))

  shape_checker(velocity, 'velocity')
  velocity_c = velocity.ctypes.data_as(c_double_p)
  get_vel_offset = lambda i: pointer_offset(velocity_c, i * pointer_stride)

  if acceleration is None:
    acceleration = np.full(position.shape, np.nan)
    acceleration[:, 0] = 0
    acceleration[:, -1] = 0

  acceleration = np.asarray(acceleration, np.float64)
  if len(acceleration.shape) == 1:
    acceleration = acceleration.reshape((1, -1))

  shape_checker(acceleration, 'acceleration')
  acceleration_c = acceleration.ctypes.data_as(c_double_p)
  get_acc_offset = lambda i: pointer_offset(acceleration_c, i * pointer_stride)

  time_c = time.ctypes.data_as(c_double_p)
  position_c = position.ctypes.data_as(c_double_p)
  trajectories = [None] * joints

  for i in range(0, joints):
    pos_offset = pointer_offset(position_c, i * pointer_stride)
    vel_offset = get_vel_offset(i)
    acc_offset = get_acc_offset(i)
    c_trajectory = api.hebiTrajectoryCreateUnconstrainedQp(waypoints, pos_offset, vel_offset, acc_offset, time_c)

    if not c_trajectory:
      raise RuntimeError('Could not create trajectory')
    trajectories[i] = c_trajectory

  return _Trajectory(trajectories, time.copy(), waypoints)

def segment_times_to_waypoint_times(segment_times: 'npt.ArrayLike') -> 'npt.NDArray[np.float64]':
  """Converts segment times to a vector of time values at each waypoint. The first element of
  the vector is the time at which the trajectory starts is always zero.

  :param segment_times: A vector of segment times (in seconds), where each element represents
                        the duration of a segment between waypoints. Must contain at least
                        one element and all values must be finite (and not ``None`` or ``nan``).
  :type segment_times: list, numpy.ndarray

  :return: A vector of waypoint times. This will never be ``None``.
  :rtype: numpy.ndarray

  :raises ValueError: If segment times vector is empty (less than one element)
                      or if any of the segment times are not finite.
  """
  segment_times = np.asarray(segment_times, np.float64)
  if len(segment_times) < 1:
    raise ValueError("At least one segment time is required to compute waypoint times.")
  if not _math_utils.is_finite(segment_times):
    raise ValueError("Segment times must have all finite values.")

  waypoint_times = np.zeros(len(segment_times) + 1, np.float64)
  waypoint_times[1:] = np.cumsum(segment_times)
  return waypoint_times

def waypoint_times_to_segment_times(waypoint_times: 'npt.ArrayLike') -> 'npt.NDArray[np.float64]':
  """Converts waypoint times to a vector of duration values for each segment between waypoints.

  :param waypoint_times: A vector of waypoint times (in seconds), where each element represents
                         the time at which a waypoint is reached. Must contain at least two
                         elements and all elements must be finite (and not ``None`` or ``nan``).
  :type waypoint_times: list, numpy.ndarray

  :return: A vector of segment times. This will never be ``None``.
  :rtype: numpy.ndarray

  :raises ValueError: If size of the waypoint times vector is less than two
                      or if any of the waypoint times are not finite.
  """
  waypoint_times = np.asarray(waypoint_times, np.float64)
  if len(waypoint_times) < 2:
    raise ValueError("At least two waypoint times are required to compute segment times.")
  if not _math_utils.is_finite(waypoint_times):
    raise ValueError("Waypoint times must have all finite values.")

  segment_times = np.diff(waypoint_times)
  return segment_times

def _estimate_segment_times(positions: 'npt.ArrayLike', max_velocities: 'npt.ArrayLike', max_accelerations: 'npt.ArrayLike', params: HebiTimeEstimationParams, min_segment_time: float = 0.01):
  """Estimates the time required to move between waypoints based on the given positions, maximum
  velocities, and maximum accelerations.

  :param positions: A matrix of waypoint joint positions (in SI units). The
                    number of rows should be equal to the number of joints,
                    and the number of columns equal to the number of waypoints.
                    Values of ``+/-inf``, ``None``, or ``nan`` are not allowed.
  :type positions:  list, numpy.ndarray, ctypes.Array

  :param max_velocities: A vector of maximum velocities (in SI units) for each joint.
                         Size must match the number of joints in the positions matrix.
                         Values must be a positive number (and not ``None`` or ``nan``).
  :type max_velocities:  list, numpy.ndarray, ctypes.Array

  :param max_accelerations: A vector of maximum accelerations (in SI units) for each joint.
                            Size must match the number of joints in the positions matrix.
                            Values must be a positive number (and not ``None`` or ``nan``).
  :type max_accelerations:  list, numpy.ndarray, ctypes.Array

  :param params: Parameters for the time estimation algorithm. Depends on the specific
                 method being used (e.g., NFabian, VelocityRamp, etc.).
  :type params: HebiTimeEstimationParams

  :param min_segment_time: The minimum allowed segment time (in seconds).
  :type min_segment_time: float

  :return: A vector of estimated segment times (in seconds) for each segment between waypoints.
  :rtype: numpy.ndarray

  :raises ValueError: If the dimensionality or size of any input parameters are invalid,
                      or if any of the values in the input matrices is not a number.
  """
  if positions is None:
    raise ValueError("positions cannot be None")
  if max_velocities is None:
    raise ValueError("max_velocities cannot be None")
  if max_accelerations is None:
    raise ValueError("max_accelerations cannot be None")

  # Convert inputs to numpy arrays
  positions = np.asarray(positions, np.float64)
  max_velocities = np.asarray(max_velocities, np.float64)
  max_accelerations = np.asarray(max_accelerations, np.float64)

  # Reshape 1D position vector to 1xn 2D array
  if len(positions.shape) == 1:
    positions = positions.reshape((1, -1))

  num_joints: int = positions.shape[0]
  num_waypoints: int = positions.shape[1]
  if max_velocities.size != num_joints:
    raise ValueError(f'max_velocities size ({max_velocities.size}) must match number of joints ({num_joints})')
  if max_accelerations.size != num_joints:
    raise ValueError(f'max_accelerations size ({max_accelerations.size}) must match number of joints ({num_joints})')
  if np.isnan(max_velocities).any():
    raise ValueError('max_velocities must have all positive values')
  if np.isnan(max_accelerations).any():
    raise ValueError('max_accelerations must have all positive values')
  if not _math_utils.is_finite(min_segment_time) or min_segment_time < 0:
    raise ValueError(f'min_segment_time must be a non-negative finite number (got {min_segment_time})')

  segment_times = np.zeros(num_waypoints - 1, np.float64)
  segment_times_c = segment_times.ctypes.data_as(c_double_p)

  result = api.hebiEstimateSegmentTimes(positions.ctypes.data_as(c_double_p),
                                        max_velocities.ctypes.data_as(c_double_p),
                                        max_accelerations.ctypes.data_as(c_double_p),
                                        num_joints, num_waypoints,
                                        segment_times_c,
                                        min_segment_time,
                                        _ctypes.byref(params))

  if result == StatusInvalidArgument:
    if num_joints == 0 or num_waypoints == 0:
      raise ValueError("positions matrix cannot be empty")
    if num_waypoints < 2:
      raise ValueError(f'At least 2 waypoints are required (got {num_waypoints})')
    if np.isnan(positions).any():
      raise ValueError('positions matrix cannot have NaNs')
    raise ValueError('Invalid arguments')
  elif result == StatusArgumentOutOfRange:
    if np.any(max_velocities <= 0):
      raise ValueError('max_velocities must have all positive values')
    if np.any(max_accelerations <= 0):
      raise ValueError('max_accelerations must have all positive values')
    raise ValueError('Argument out of range')
  elif result != StatusSuccess:
    raise RuntimeError("An unexpected error occurred during segment time estimation.")

  return segment_times

@overload
def estimate_segment_times(method: 'Literal[TimeEstimationMethod.NFabian]', positions: 'npt.ArrayLike', max_velocities: 'npt.ArrayLike', max_accelerations: 'npt.ArrayLike', *, n_fabian=6.5, min_segment_time: float = 0.01):
  """Estimates the segment times using the NFabian method.

  :param positions: A matrix of waypoint joint positions (in SI units). The
                    number of rows should be equal to the number of joints,
                    and the number of columns equal to the number of waypoints.
                    Values of ``+/-inf``, ``None``, or ``nan`` are not allowed.
  :type positions:  list, numpy.ndarray, ctypes.Array

  :param max_velocities: A vector of maximum velocities (in SI units) for each joint.
                         Size must match the number of joints in the positions matrix.
                         Values must be a positive number (and not ``None`` or ``nan``).
  :type max_velocities:  list, numpy.ndarray, ctypes.Array

  :param max_accelerations: A vector of maximum accelerations (in SI units) for each joint.
                            Size must match the number of joints in the positions matrix.
                            Values must be a positive number (and not ``None`` or ``nan``).
  :type max_accelerations:  list, numpy.ndarray, ctypes.Array

  :param fabian_constant: The NFabian constant to use for the estimation.
  :type fabian_constant: float

  :param min_segment_time: The minimum allowed segment time (in seconds).
  :type min_segment_time: float

  :return: A vector of estimated segment times (in seconds) for each segment between waypoints.
  :rtype: numpy.ndarray

  :raises ValueError: If the dimensionality or size of any input parameters are invalid,
                      or if any of the values in the input matrices is not a number.
  """

@overload
def estimate_segment_times(method: 'Literal[TimeEstimationMethod.VelocityRamp]', positions: 'npt.ArrayLike', max_velocities: 'npt.ArrayLike', max_accelerations: 'npt.ArrayLike', *, min_segment_time: float = 0.01):
  """Estimates the segment times using the VelocityRamp method.

  :param positions: A matrix of waypoint joint positions (in SI units). The
                    number of rows should be equal to the number of joints,
                    and the number of columns equal to the number of waypoints.
                    Values of ``+/-inf``, ``None``, or ``nan`` are not allowed.
  :type positions:  list, numpy.ndarray, ctypes.Array

  :param max_velocities: A vector of maximum velocities (in SI units) for each joint.
                         Size must match the number of joints in the positions matrix.
                         Values must be a positive number (and not ``None`` or ``nan``).
  :type max_velocities:  list, numpy.ndarray, ctypes.Array

  :param max_accelerations: A vector of maximum accelerations (in SI units) for each joint.
                            Size must match the number of joints in the positions matrix.
                            Values must be a positive number (and not ``None`` or ``nan``).
  :type max_accelerations:  list, numpy.ndarray, ctypes.Array

  :param min_segment_time: The minimum allowed segment time (in seconds).
  :type min_segment_time: float

  :return: A vector of estimated segment times (in seconds) for each segment between waypoints.
  :rtype: numpy.ndarray

  :raises ValueError: If the dimensionality or size of any input parameters are invalid,
                      or if any of the values in the input matrices is not a number.
  """

def estimate_segment_times(method: 'TimeEstimationMethod', positions: 'npt.ArrayLike', max_velocities: 'npt.ArrayLike', max_accelerations: 'npt.ArrayLike', **kwargs):
  params = HebiTimeEstimationParams()
  params.method_type_ = method
  if method == TimeEstimationMethod.NFabian:
    fabian_constant: float = kwargs.get('fabian_constant', 6.5)
    params.n_fabian_params_.magic_fabian_constant_ = fabian_constant

  min_segment_time = kwargs.get('min_segment_time', 0.01)
  return _estimate_segment_times(positions, max_velocities, max_accelerations, params, min_segment_time)
