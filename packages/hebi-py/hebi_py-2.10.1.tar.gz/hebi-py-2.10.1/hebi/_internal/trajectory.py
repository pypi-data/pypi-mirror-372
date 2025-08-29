# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------

from ctypes import c_double, byref, POINTER
import numpy as np

from hebi._internal.errors import HEBI_Exception
from .ffi.enums import StatusCode
from .ffi import api

import typing
if typing.TYPE_CHECKING:
  import numpy.typing as npt


class Trajectory:
  """Represents a smooth trajectory through a set of waypoints."""

  __slots__ = ['_trajectories', '_waypoint_times', '_number_of_waypoints', '_number_of_joints', '_start_time', '_end_time']

  def __init__(self, trajectories, waypoint_times: 'npt.NDArray[np.float64]', num_waypoints: int):
    self._trajectories = trajectories
    self._waypoint_times = waypoint_times
    self._number_of_waypoints = num_waypoints
    self._number_of_joints = len(trajectories)
    self._start_time = waypoint_times[0]
    self._end_time = waypoint_times[-1]

  @property
  def number_of_waypoints(self):
    """The number of waypoints in this trajectory.

    :return: number of waypoints
    :rtype:  int
    """
    return self._number_of_waypoints

  @property
  def number_of_joints(self):
    """The number of joints in this trajectory.

    :return: the number of joints
    :rtype:  int
    """
    return len(self._trajectories)

  @property
  def start_time(self):
    """The time (in seconds) at which the trajectory starts.

    :return: the start time
    :rtype:  float
    """
    return self._start_time

  @property
  def end_time(self):
    """The time (in seconds) at which the trajectory ends.

    :return: the end time
    :rtype:  float
    """
    return self._end_time

  @property
  def duration(self):
    """The time (in seconds) between the start and end of this trajectory.

    :return: the duration
    :rtype:  float
    """
    return self._end_time - self._start_time

  @property
  def waypoint_times(self):
    """

    :return: The input time (in seconds) for each waypoint
    :rtype:  numpy.ndarray
    """
    return self._waypoint_times

  def get_state(self, time: float, *,
                position: 'npt.NDArray[np.float64] | None' = None,
                velocity: 'npt.NDArray[np.float64] | None' = None,
                acceleration: 'npt.NDArray[np.float64] | None' = None):
    """Returns the position, velocity, and acceleration for a given point in
    time along the trajectory.

    :param time: the time, in seconds
    :type time:  int, float

    :return: a triplet containing the position, velocity, and acceleration
             at the given point in time.
    :rtype:  numpy.ndarray, numpy.ndarray, numpy.ndarray
    """
    n = self.number_of_joints

    if position is None:
      position = np.empty(n, np.float64)
    else:
      position.resize(n)

    if velocity is None:
      velocity = np.empty(n, np.float64)
    else:
      velocity.resize(n)

    if acceleration is None:
      acceleration = np.empty(n, np.float64)
    else:
      acceleration.resize(n)

    position_val = c_double(0.0)
    velocity_val = c_double(0.0)
    acceleration_val = c_double(0.0)

    for i, trajectory in enumerate(self._trajectories):
      ret = api.hebiTrajectoryGetState(trajectory, time, byref(position_val), byref(velocity_val), byref(acceleration_val))
      passed_run = ret == StatusCode.Success

      position[i] = position_val.value
      velocity[i] = velocity_val.value
      acceleration[i] = acceleration_val.value

    return position, velocity, acceleration

  def get_min_max_position(self):
    min_position = np.empty(len(self._trajectories))
    max_position = np.empty(len(self._trajectories))

    for idx, traj in enumerate(self._trajectories):
      min_val = c_double(min_position[idx])
      max_val = c_double(max_position[idx])
      res = api.hebiTrajectoryGetMinMaxPosition(traj, byref(min_val), byref(max_val))
      if res != StatusCode.Success:
        raise HEBI_Exception('Failure getting Min/Max position from Trajectory!')
      min_position[idx] = min_val.value
      max_position[idx] = max_val.value

    return min_position, max_position

  def get_max_velocity(self):
    max_velocity = np.empty(len(self._trajectories))

    for idx, traj in enumerate(self._trajectories):
      val = c_double(max_velocity[idx])
      res = api.hebiTrajectoryGetMaxVelocity(traj, byref(val))
      if res != StatusCode.Success:
        raise HEBI_Exception('Failure getting Max Velocity from Trajectory!')
      max_velocity[idx] = val.value

    return max_velocity

  def get_max_acceleration(self):
    max_acceleration = np.empty(len(self._trajectories))

    for idx, traj in enumerate(self._trajectories):
      val = c_double(max_acceleration[idx])
      res = api.hebiTrajectoryGetMaxAcceleration(traj, byref(val))
      if res != StatusCode.Success:
        raise HEBI_Exception('Failure getting Max Acceleration from Trajectory!')
      max_acceleration[idx] = val.value

    return max_acceleration
