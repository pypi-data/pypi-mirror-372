# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2022 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------

import time
import numpy as np

from hebi._internal.ffi import enums

from ._internal.ffi.enums import FrameType
from ._internal.ffi._message_types import GroupCommand, GroupFeedback

from . import robot_model
from .robot_model import RobotModel, PositionObjective, TipAxisObjective, SO3Objective
from . import trajectory as trajectory_api
from ._internal.lookup import Lookup

import typing
from typing import Literal, overload
if typing.TYPE_CHECKING:
  from typing import Callable, Union, Sequence, Any
  import numpy.typing as npt
  from hebi._internal.group import Group
  from .robot_model import RobotModel
  from .config import HebiConfig
  VectorType = Union[Sequence[float], npt.NDArray[np.float64]]


class Arm:
  """"""

  __slots__ = (
      '_get_current_time_s', '_last_time', '_group', '_robot_model',
      '_end_effector', '_trajectory', '_masses', '_aux_times', '_aux',
      '_feedback', '_command', '_tmp_4x4d', '_plugins',
      '_min_positions', '_max_positions', '_com_jacobians')

  def __init__(self, time_getter: 'Callable[[], float]', group: 'Group', robot_model: 'RobotModel', end_effector: 'EndEffector | None' = None, plugins: 'list[ArmPlugin] | None' = None):
    self._get_current_time_s = time_getter
    self._group = group
    self._robot_model = robot_model
    self._end_effector = end_effector
    self._plugins: 'list[ArmPlugin]' = []

    self._com_jacobians = np.empty((self._robot_model.get_frame_count('CoM'), 6, robot_model.dof_count), dtype=np.float64)

    size = group.size

    self._last_time = time_getter()
    self._feedback = GroupFeedback(size)
    self._command = GroupCommand(size)
    self._masses = robot_model.masses

    self._trajectory = None

    self._min_positions = np.full(size, -np.inf)
    self._max_positions = np.full(size, np.inf)

    self._tmp_4x4d = np.identity(4, dtype=np.float64)

    # Arms always have grav and dynamic comp plugins
    if plugins is None:
      plugins = [
        GravCompEffortPlugin(name='gravComp', enabled=True, ramp_time=0.0),
        DynamicCompEffortPlugin(name='dynamicsComp', enabled=True, ramp_time=0.0)
      ]

    for plugin in plugins:
      self.add_plugin(plugin)

  @property
  def size(self):
    """The number of modules in the group.

    :rtype: int
    """
    return self._group.size

  @property
  def group(self):
    """The underlying group of the arm.

    Guaranteed to be non-null.
    """
    return self._group

  @property
  def robot_model(self):
    """The underlying robot description of the arm. Guaranteed to be non-null.

    :rtype: hebi.robot_model.RobotModel
    """
    return self._robot_model

  @property
  def trajectory(self):
    """The underlying trajectory object used to move the arm through the
    prescribed waypoints associated with the current goal.

    If there is no currently set goal, this will be ``None``.
    """
    return self._trajectory

  @property
  def end_effector(self) -> 'EndEffector | Gripper | None':
    """The currently set end effector.

    ``None`` if there is no end effector.
    """
    return self._end_effector

  @property
  def pending_command(self):
    """The command which will be send to the modules on :meth:`Arm.send`. This
    object is guaranteed to not change for the lifetime of the arm.

    :rtype: hebi.GroupCommand
    """
    return self._command

  @property
  def last_feedback(self):
    """The most recently received feedback from the arm. This object is
    guaranteed to not change for the lifetime of the arm.

    :rtype: hebi.GroupFeedback
    """
    return self._feedback

  @property
  def goal_progress(self):
    """Progress towards the current goal; in range of [0.0, 1.0].

    :rtype: float
    """
    if self.trajectory is None:
      return 0.0

    duration = self.trajectory.duration
    t_traj = self._last_time - self.trajectory.start_time
    return min(t_traj, duration) / duration

  @property
  def at_goal(self):
    """
    :rtype: bool
    """
    return self.goal_progress >= 1.0

  def get_plugin_by_name(self, name: str):
    """
    Gets the plugin by the specified name.

    :param name: The name of the plugin to get.
    :type name: str
    :return: The plugin with the specified name if it exists, otherwise None.
    :rtype: ArmPlugin | None
    """
    for plugin in self._plugins:
      if plugin.name == name:
        return plugin
    return None

  def get_plugin_by_type(self, plugin_type: type) -> 'ArmPlugin | None':
    """
    Gets the plugin by the specified type.

    :param plugin_type: The type of the plugin to get
    :type plugin_type: type
    :return: The plugin of the specified type if it exists, otherwise None
    :rtype: ArmPlugin | None
    """
    for plugin in self._plugins:
      if isinstance(plugin, plugin_type):
        return plugin
    return None

  def add_plugin(self, plugin: 'ArmPlugin'):
    """
    Adds the specified plugin to the arm, if not previously added.
    :meth:`ArmPlugin.on_associated` callback is invoked on the plugin specified.

    :param plugin: the plugin to add
    :type plugin: .ArmPlugin
    """
    # Check if a plugin of the same type has already been added
    for existing_plugin in self._plugins:
      if isinstance(existing_plugin, type(plugin)):
        print(f"Plugin of type {type(plugin).__name__} already added.")
        return

    # Add the plugin if it is not already present
    plugin.on_associated(self)
    self._plugins.append(plugin)

  def load_gains(self, gains_file: str, attempts: int = 5):
    """Load the gains from the provided file and send the gains to the
    underlying modules in the group.

    This method requests acknowledgement from all modules in the group that the gains
    were received. Consequently, this method may take a few seconds to execute
    if you are on a network which drops packets (e.g., a suboptimal WiFi network).
    The `attempts` parameter is used to re-send the gains to modules, on the event
    that an ack was not received from each module in the group.

    :param gains_file: The file location of the gains file
    :param attempts: the number of attempts to send the gains to the group.

    :return: ``True`` if gains were successfully sent to the modules; otherwise ``False``
    :rtype:  bool
    """
    gains_cmd = GroupCommand(self._group.size)
    gains_cmd.read_gains(gains_file)

    return _repetitive_send_command_with_ack(self._group, gains_cmd, attempts)

  def update(self):
    """Receive feedback from the modules, compute pending commands, and update
    state for the end effector and any associated plugins.

    :return: ``True`` if feedback was received and all components were able to be updated;
             ``False`` otherwise
    :rtype:  bool
    """
    t = self._get_current_time_s()

    # Time must be monotonically increasing
    if t < self._last_time:
      return False

    dt = t - self._last_time
    self._last_time = t
    group = self._group
    feedback = self._feedback

    if not group.get_next_feedback(reuse_fbk=feedback):
      return False

    command = self._command
    end_effector = self._end_effector
    aux = []

    if self.trajectory is not None:
      pos, vel, _ = self.trajectory.get_state(t)
      aux = self.get_aux(t)
    else:
      pos = np.full(group.size, np.nan)
      vel = np.full(group.size, np.nan)
      #acc = np.zeros(group.size)

    command.position = pos
    command.velocity = vel
    command.effort = 0.0

    res = True

    if end_effector is not None:
      res = end_effector.update(aux) and res

    # Cached values for plugin speedup
    self._robot_model.get_jacobians_mat(FrameType.CenterOfMass,
                                        self.last_feedback.position,
                                        output=self._com_jacobians)

    for plugin in self._plugins:
      res = plugin.update(self, dt) and res

    return res

  def send(self):
    """Send the pending commands to the arm and end effector (if non-null).

    :return: ``True`` if command was successfully sent to all components; ``False`` otherwise
    :rtype:  bool
    """
    res = self._group.send_command(self._command)
    end_effector = self._end_effector
    if end_effector is not None:
      res = res and end_effector.send()

    return res

  def set_end_effector(self, end_effector: 'EndEffector'):
    """Update the currently set end effector for the arm."""
    self._end_effector = end_effector

  def set_goal(self, goal: 'Goal'):
    """Sets the current goal of the arm as described by the input waypoints.

    :param goal: Goal object representing waypoints of the goal
    :type goal:  Goal
    """
    traj, aux_state = goal.build_trajectory_from(self._last_time, *self.current_state())
    self._trajectory = traj
    self._aux_times = aux_state[0]
    self._aux = aux_state[1]

  def current_state(self):
    if self.trajectory is not None:
      # Trajectory already exists. Use the expected location at the current time
      # as the initial waypoint for the new goal.
      return self.trajectory.get_state(self._last_time)

    # If there is no current trajectory, check if
    # robot has commands. If so, use as the initial
    # waypoint for the goal, otherwise feedback.
    curr_pos = self._feedback.position_command
    if any(np.isnan(curr_pos)):
      curr_pos = self._feedback.position

    curr_vel = self._feedback.velocity_command
    if any(np.isnan(curr_vel)):
      curr_vel = self._feedback.velocity

    curr_acc = np.zeros(curr_pos.size)
    return curr_pos, curr_vel, curr_acc


  def get_aux(self, t: float) -> 'npt.NDArray[np.float64]':
    """Retrieve the aux value at the given time point. If there are no aux
    values, an empty array is returned.

    :param t: The point in time, intended to be within the interval determined
              by the current goal.

    :rtype: np.ndarray
    """
    aux = self._aux
    aux_times = self._aux_times
    size = len(aux_times)
    t = float(t)

    if size == 0:
      return np.empty(0)

    for i in reversed(range(size)):
      if t >= aux_times[i]:
        if i == size-1:
          return aux[:, i].copy()
        return aux[:, i+1].copy()

    return aux[:, 0].copy()

  def cancel_goal(self):
    """Removes any currently set goal."""
    self._trajectory = None

  @property
  def use_joint_limits(self):
    has_max = any(np.isfinite(self._max_positions))
    has_min = any(np.isfinite(self._min_positions))
    return has_max or has_min

  def set_joint_limits(self, min_positions: 'VectorType', max_positions: 'VectorType'):
    """Replace any currently set joint limits with the limits provided.

    :param min_positions: The minimum position limits. Must be a list and not a scalar.
    :param max_positions: The maximum position limits. Must be a list and not a scalar.
    :type min_positions: collections.abc.Sequence
    :type max_positions: collections.abc.Sequence
    """
    expected_size = self._robot_model.dof_count
    if len(min_positions) != expected_size or len(max_positions) != expected_size:
      raise ValueError("Input size must be equal to degrees of freedom in robot")

    if any(np.isnan(min_positions)) or any(np.isnan(max_positions)):
      raise ValueError("Input must be non-nan")

    self._min_positions: 'npt.NDArray[np.float64]' = np.asarray(min_positions)
    self._max_positions: 'npt.NDArray[np.float64]' = np.asarray(max_positions)

  def clear_joint_limits(self):
    """Removes any currently set joint limits."""
    self._min_positions = np.full(self.size, -np.inf)
    self._max_positions = np.full(self.size, np.inf)

  def FK(self, positions: 'VectorType', **kwargs: 'Any'):
    """Retrieves the output frame of the end effector at the provided joint
    positions.

    The keys provided below show the possible retrievable representations
    of the resulting end effector transform.

    Possible keys:
      * `xyz_out`:          Used to store the 3d translation vector of the end effector
                            If this is set, this is also the object returned.
      * `tip_axis_out`:     Used to store the tip axis of the end effector
      * `orientation_out`:  Used to store the orientation (SO3 matrix) of the end effector

    :param positions: The joint space positions

    :return: The 3d translation vector of the end effector
    """
    out = kwargs.get('xyz_out', None)
    if out is None:
      ret = np.zeros((3,), dtype=np.float64)
    else:
      ret = out

    tmp = self._tmp_4x4d
    self._robot_model.get_end_effector(positions, output=tmp)
    np.copyto(ret, tmp[0:3, 3])

    tip_axis_out = kwargs.get('tip_axis_out', None)
    if tip_axis_out is not None:
      np.copyto(tip_axis_out, tmp[0:3, 2])

    orientation_out = kwargs.get('orientation_out', None)
    if orientation_out is not None:
      np.copyto(orientation_out, tmp[0:3, 0:3])

    return ret

  def ik_target_xyz(self, initial_position, target_xyz, out=None):
    """Solve for the joint space positions such that the end effector is near
    the target xyz position in space specified.

    If there are any joint limits set, the solver will attempt to respect them.

    :param initial_position: The seed angles for the IK solver
    :param target_xyz: The intended destination coordinate as a 3d vector
    :param out: The optional output parameter (also always returned)
    """
    return self.solve_ik(initial_position, target_xyz, out=out)

  def ik_target_xyz_tip_axis(self,
                             initial_position: 'VectorType',
                             target_xyz: 'VectorType',
                             tip_axis: 'VectorType',
                             out: 'npt.NDArray[np.float64] | None' = None):
    """Solve for the joint space positions such that the end effector is near
    the target xyz position in space and also oriented along the axis
    specified.

    If there are any joint limits set, the solver will attempt to respect them.

    :param initial_position: The seed angles for the IK solver
    :param target_xyz: The intended destination coordinate as a 3d vector
    :param tip_axis: The intended destination tip axis as a 3d vector
    :param out: The optional output parameter (also always returned)
    """
    return self.solve_ik(initial_position, target_xyz, tip_axis=tip_axis, out=out)

  def ik_target_xyz_so3(self,
                        initial_position: 'VectorType',
                        target_xyz: 'VectorType',
                        orientation: 'npt.NDArray[np.float64]',
                        out: 'npt.NDArray[np.float64] | None' = None):
    """Solve for the joint space positions such that the end effector is near
    the target xyz position in space with the specified SO3 orientation.

    If there are any joint limits set, the solver will attempt to respect them.

    :param initial_position: The seed angles for the IK solver
    :param target_xyz: The intended destination coordinate as a 3d vector
    :param orientation: The intended destination orientation as an SO3 matrix
    :param out: The optional output parameter (also always returned)
    """
    return self.solve_ik(initial_position, target_xyz, orientation=orientation, out=out)

  @overload
  def solve_ik(self,
               initial_position: 'VectorType',
               target_xyz: 'VectorType',
               *,
               out: 'npt.NDArray[np.float64] | None' = ...):
    """Solve for the joint space positions such that the end effector is near
    the target xyz position in space specified.

    If there are any joint limits set, the solver will attempt to respect them.

    :param initial_position: The seed angles for the IK solver
    :param target_xyz: The intended destination coordinate as a 3d vector
    :param out: The optional output parameter (also always returned)
    """

  @overload
  def solve_ik(self,
               initial_position: 'VectorType',
               target_xyz: 'VectorType',
               *,
               tip_axis: 'VectorType',
               out: 'npt.NDArray[np.float64] | None' = ...):
    """Solve for the joint space positions such that the end effector is near
    the target xyz position in space and also oriented along the axis
    specified.

    If there are any joint limits set, the solver will attempt to respect them.

    :param initial_position: The seed angles for the IK solver
    :param target_xyz: The intended destination coordinate as a 3d vector
    :param tip_axis: The intended destination tip axis as a 3d vector
    :param out: The optional output parameter (also always returned)
    """

  @overload
  def solve_ik(self,
               initial_position: 'VectorType',
               target_xyz: 'VectorType',
               *,
               orientation: 'npt.NDArray[np.float64]',
               out: 'npt.NDArray[np.float64] | None' = ...):
    """Solve for the joint space positions such that the end effector is near
    the target xyz position in space with the specified SO3 orientation.

    If there are any joint limits set, the solver will attempt to respect them.

    :param initial_position: The seed angles for the IK solver
    :param target_xyz: The intended destination coordinate as a 3d vector
    :param orientation: The intended destination orientation as an SO3 matrix
    :param out: The optional output parameter (also always returned)
    """

  def solve_ik(self,
               initial_position: 'VectorType',
               target_xyz: 'VectorType',
               *,
               tip_axis: 'VectorType | None' = None,
               orientation: 'npt.NDArray[np.float64] | None' = None,
               out: 'npt.NDArray[np.float64] | None' = None,
               frame_type: 'str' = 'endeffector',
               frame_id: 'str | int | None' = None,
               ):
    """Solve for joint space positions so that the target element
    (defaults to the end effector) meets the list of provided conditions.

    If there are any joint limits set, the solver will attempt to respect them.

    :param initial_position: The seed angles for the IK solver
    :param target_xyz: The intended destination coordinate as a 3d vector
    :param tip_axis: The intended destination tip direction as a 3d vector
    :param orientation: The intended destination orientation as an SO3 matrix
    :param out: The optional output parameter (also always returned)
    """

    if out is None:
      ret = np.empty(len(initial_position), dtype=np.float64)
    else:
      ret = out

    target_frame_idx = 0
    if isinstance(frame_id, int):
      target_frame_idx = frame_id
    elif isinstance(frame_id, str):
      elem_idx = self.robot_model.get_element_idx_by_tag(frame_id)
      target_frame_idx = self.robot_model.get_frame_idx_from_element_idx(elem_idx, frame_type)
    elif frame_id is not None:
      raise TypeError(f'Argument "frame_id" should be type "str | int" if provided, not {type(frame_id)}')

    objectives: 'list[robot_model._ObjectiveBase]' = []
    objectives.append(PositionObjective(frame_type,
                                        xyz=np.array(target_xyz),
                                        idx=target_frame_idx))

    # Maybe don't add both orientation and tipaxis at the same time?
    # TODO: figure out how to enforce this in the function signatures?
    if orientation is not None:
      objectives.append(SO3Objective(frame_type,
                                     rotation=orientation.copy(),
                                     idx=target_frame_idx))
    if tip_axis is not None:
      objectives.append(TipAxisObjective(frame_type,
                                         axis=np.array(tip_axis),
                                         idx=target_frame_idx))

    if self.use_joint_limits:
      # Add the `joint_limit_constraint` to the list of IK objectives
      objectives.append(robot_model.joint_limit_constraint(self._min_positions,
                                                           self._max_positions))

    self._robot_model.solve_inverse_kinematics(initial_position, *objectives,
                                               output=ret)

    return ret


class Goal:
  """Used to construct a goal for an arm.

  Intended to be passed into :meth:`Arm.set_goal`.
  """

  __slots__ = ('_times', '_positions', '_velocities', '_accelerations', '_aux', '_dof_count',
               '_waypoints_valid', '_result', '_user_time', '_user_aux')

  def __init__(self, dof_count: int):
    self._times: 'list[float]' = []
    self._positions: 'list[VectorType | None]' = []
    self._velocities: 'list[VectorType | None]' = []
    self._accelerations: 'list[VectorType | None]' = []
    self._aux = []
    self._dof_count = dof_count
    self._waypoints_valid = False
    self._user_time = False
    self._user_aux = False

    res: 'dict[str, Any]' = dict()
    res['times'] = None
    res['positions'] = None
    res['velocities'] = None
    res['accelerations'] = None
    res['aux'] = None
    self._result = res

  @property
  def waypoint_count(self):
    """
    :return: The number of waypoints added to this goal
    :rtype: int
    """
    return len(self._positions)

  @property
  def dof_count(self):
    """
    :return: The number of degrees of freedom in each waypoint
    :rtype: int
    """
    return self._dof_count

  def build_trajectory_from(self, curr_time: float, start_pos: 'npt.NDArray[np.float64]', start_vel: 'npt.NDArray[np.float64] | None' = None, start_acc: 'npt.NDArray[np.float64] | None' = None):
    """Builds a trajectory using the Goal's waypoints from the specified start state.

    :param curr_time: the current time, used for the start waypoint of the trajectory
    :type curr_time:  float

    :param start_pos: collection of the joint positions at the start of the returned trajectory
    :type start_pos:  numpy.ndarray

    :param start_vel: collection of the joint velocities at the start of the returned trajectory
                       If this is ``None``, the start velocity of each joint is assumed to be 0
    :type start_vel:  numpy.ndarray

    :param start_acc: collection of the joint accelerations at the start of the returned trajectory
                       If this is ``None``, the start acceleration of each joint is assumed to be 0
    :type start_acc:  numpy.ndarray

    """
    ret = self.build()
    times = ret['times']
    positions = ret['positions']
    velocities = ret['velocities']
    accelerations = ret['accelerations']
    aux = ret['aux']

    input_shape = positions.shape
    num_joints = input_shape[0]

    if len(input_shape) == 1:
      # Input is a single waypoint
      num_waypoints = 2
    else:
      num_waypoints = input_shape[1] + 1

    dst_positions = np.empty((num_joints, num_waypoints), dtype=np.float64)
    dst_velocities = np.empty((num_joints, num_waypoints), dtype=np.float64)
    dst_accelerations = np.empty((num_joints, num_waypoints), dtype=np.float64)

    # Initial state
    dst_positions[:, 0] = start_pos

    if start_vel is None:
      dst_velocities[:, 0] = 0.0
    else:
      dst_velocities[:, 0] = start_vel

    if start_acc is None:
      dst_accelerations[:, 0] = 0.0
    else:
      dst_accelerations[:, 0] = start_acc

    # Copy new waypoints
    dst_positions[:, 1:] = positions.reshape((num_joints, -1))
    dst_velocities[:, 1:] = velocities.reshape((num_joints, -1))
    dst_accelerations[:, 1:] = accelerations.reshape((num_joints, -1))

    waypoint_times = np.empty(num_waypoints)
    # If time is not provided, calculate it using a heuristic
    if times is None:
      _get_waypoint_times(waypoint_times, num_waypoints, dst_positions, dst_velocities, dst_accelerations)
    else:
      waypoint_times[0] = 0.0
      waypoint_times[1:] = times.reshape(-1)

    # Create new trajectory based off of the goal
    waypoint_times += curr_time
    ret_traj = trajectory_api.create_trajectory(waypoint_times, dst_positions, dst_velocities, dst_accelerations)

    ret_aux = (np.array([], dtype=np.float64), np.array([], dtype=np.float64))
    # Update aux state
    if aux is not None:
      goal_aux = np.asarray(aux)
      aux_shape = goal_aux.shape

      # HACK: Figure out a better way to handle logic here...
      if len(aux_shape) == 1:
        # Will occur if the aux provided is an array of scalars (i.e., 1 aux value per waypoint)
        aux_size = 1
        second_dim = len(aux)
      else:
        # Will occur if the aux provided has more than 1 aux value per waypoint
        aux_size = aux_shape[0]
        second_dim = aux_shape[1] + 1

      if second_dim == num_waypoints:
        # Update aux
        aux_arr = np.empty((aux_size, num_waypoints), dtype=np.float64)
        # aux = self._aux
        aux_arr[:, 0] = np.nan
        aux_arr[:, 1:] = goal_aux
        ret_aux = (waypoint_times, aux_arr)

    return ret_traj, ret_aux


  def build(self):
    """Return the dictionary depicting the currently specified elements."""
    if self._waypoints_valid:
      # Already cached results - return it
      return self._result

    num_waypoints = self.waypoint_count
    dof_count = self._dof_count

    if num_waypoints < 1:
      raise ValueError("A goal must have at least 1 waypoint")

    ret = self._result
    positions = np.empty((dof_count, num_waypoints), dtype=np.float64)
    velocities = np.empty((dof_count, num_waypoints), dtype=np.float64)
    accelerations = np.empty((dof_count, num_waypoints), dtype=np.float64)
    aux = self._aux

    last_waypoint = num_waypoints - 1

    in_pos = self._positions
    in_vel = self._velocities
    in_acc = self._accelerations

    for i in range(num_waypoints):
      pos_val = in_pos[i]
      vel_val = in_vel[i]
      acc_val = in_acc[i]

      if pos_val is None:
        if i == last_waypoint:
          pos_val = 0.0
        else:
          pos_val = np.nan

      if vel_val is None:
        if i == last_waypoint:
          vel_val = 0.0
        else:
          vel_val = np.nan

      if acc_val is None:
        if i == last_waypoint:
          acc_val = 0.0
        else:
          acc_val = np.nan

      positions[:, i] = pos_val
      velocities[:, i] = vel_val
      accelerations[:, i] = acc_val

    if self._user_time:
      times = np.asarray(self._times, dtype=np.float64)
    else:
      times = None

    ret['times'] = times
    ret['positions'] = positions
    ret['velocities'] = velocities
    ret['accelerations'] = accelerations
    ret['aux'] = aux

    self._waypoints_valid = True

    return ret

  def clear(self):
    """Remove any added waypoints."""
    self._waypoints_valid = False
    self._times.clear()
    self._positions.clear()
    self._velocities.clear()
    self._accelerations.clear()
    self._aux.clear()
    self._user_time = False
    self._user_aux = False

    return self

  def add_waypoint(self,
                   t: 'float | None' = None,
                   position: 'VectorType | None' = None,
                   velocity: 'VectorType | None' = None,
                   acceleration: 'VectorType | None' = None,
                   aux: 'float | VectorType | None' = None,
                   time_relative: bool = True):
    """

    :param t: The time point associated with this waypoint. `time_relative`
              parameter dictates whether this is relative or absolute.
              If ``None``, a heuristic will be used to determine time between waypoints.
              ``t`` must be defined for all waypoints or none.
    :type t:  int, float

    :param position: Vector corresponding to the position of each degree of freedom for the given waypoint.
                     If ``None``, this is interpreted as a "free" constraint (`nan`).
    :type position:  numpy.ndarray

    :param velocity: Vector corresponding to the velocity of each degree of freedom for the given waypoint.
                     If ``None``, this is interpreted as a "free" constraint (`nan`).
    :type velocity:  numpy.ndarray

    :param acceleration: Vector corresponding to the acceleration of each degree of freedom for the given
                         waypoint. If ``None``, this is interpreted as a "free" constraint (`nan`).
    :type acceleration:  numpy.ndarray

    :param aux: The aux value for the given waypoint. All other invocations of `add_waypoint` prior to passing this
                to :meth:`Arm.set_goal` must be consistent: either provide an ``aux`` value for each
                waypoint, or do not provide any at all.
    :type aux:  float, numpy.ndarray

    :param time_relative: Specifies whether to interpret `t` as relative or absolute. If this is the first waypoint
                          being added, this is relative to 0.
    :type time_relative:  bool
    """

    dof_count = self._dof_count
    user_time = self._user_time
    user_aux = self._user_aux

    if self.waypoint_count == 0:
      # Set the rule for any additional waypoints
      user_time = t is not None
      user_aux = aux is not None
      self._user_time = user_time
      self._user_aux = user_aux
    else:
      if not user_time and t is not None:
        # ``t`` was not provided previously but now is
        raise ValueError("waypoint times must be defined for all waypoints or none")

      if (aux is not None) != user_aux:
        # ``aux`` was not provided previously but now is
        # or
        # ``aux`` was provided previously but not here
        raise ValueError("waypoint aux must be defined for all waypoints or none")

    if position is None and velocity is None and acceleration is None:
      # At least one derivative of position, or position itself must be passed in for each waypoint
      raise ValueError("At least one of the following arguments must be non-null: position, velocity, acceleration")

    pos_val = None
    if position is not None:
      pos_val = position
      if len(position) != dof_count:
        raise ValueError("length of position input must be equal to dof_count")

    vel_val = None
    if velocity is not None:
      vel_val = velocity
      if len(velocity) != dof_count:
        raise ValueError("length of velocity input must be equal to dof_count")

    acc_val = None
    if acceleration is not None:
      acc_val = acceleration
      if len(acceleration) != dof_count:
        raise ValueError("length of acceleration input must be equal to dof_count")

    if user_time:
      if t is None:
        raise ValueError("waypoint times must be defined for all waypoints or none")
      curr_time = 0.0
      if self.waypoint_count > 0:
        curr_time = self._times[-1]
      if time_relative:
        t += curr_time
      # Check edge cases with time
      if curr_time >= t:
        raise ValueError("waypoint times must be monotonically increasing")
      elif not np.isfinite(t):
        raise ValueError("waypoint times must be finite")

      self._times.append(t)

    self._waypoints_valid = False
    self._positions.append(pos_val)
    self._velocities.append(vel_val)
    self._accelerations.append(acc_val)

    if user_aux:
      self._aux.append(aux)

    return self


class EndEffector:
  """Abstract base class representing an end effector to be used with an Arm
  object."""

  def __init__(self): pass

  def update(self, aux_state: 'float | VectorType') -> bool:
    """Update the aux state of the end effector.

    :param aux_state: a scalar number (`int` or `float`) or list of numbers.
    :type aux_state:  int, float, list

    :return: ``True`` on success, otherwise ``False``
    """
    return True

  def send(self) -> bool:
    """Sends the currently pending command to the end effector.

    :return: ``True`` on success; otherwise ``False``
    :rtype: bool
    """
    return True


class Gripper(EndEffector):
  """End effector implementation which is intended to be used to provide
  gripper functionality."""

  __slots__ = ('_state', '_close_effort', '_open_effort', '_group', '_command')

  def __init__(self, group: 'Group', close_effort: float, open_effort: float):
    self._group = group
    self._close_effort = close_effort
    self._open_effort = open_effort
    self._command = GroupCommand(1)
    self._state = 0.0
    self.update(self._state)

  @property
  def state(self):
    """The current state of the gripper. Range of the value is [0.0, 1.0].

    :rtype: float
    """
    return self._state

  @property
  def command(self):
    """The underlying command to be sent to the gripper. Can be modified to
    extend functionality.

    :rtype: hebi.GroupCommand
    """
    return self._command

  def close(self):
    """Sets the gripper to be fully closed."""
    self.update(1.0)

  def open(self):
    """Sets the gripper to be fully open."""
    self.update(0.0)

  def toggle(self):
    """Toggle the state of the gripper.

    If the gripper was fully closed, it will become fully open. If the
    gripper was fully open, it will become fully closed. Otherwise, this
    method is a no-op.
    """
    if self._state == 0.0:
      self.update(1.0)
    elif self._state == 1.0:
      self.update(0.0)

  def send(self):
    """Send the command to the gripper.

    :return: the result of :meth:`hebi._internal.group.Group.send_command`
    """
    return self._group.send_command(self._command)

  def update(self, aux: 'float | npt.NDArray[np.float64]'):
    """Update the state of the gripper.

    :param aux: The aux data. Can be a scalar value or a list of values.
                If a list, it is expected to contain only one element.
                Values be finite.
    :type aux:  int, float, numpy.ndarray

    :return: ``True`` on success; ``False`` otherwise
    """
    if isinstance(aux, (int, float)):
      val = aux
    elif hasattr(aux, '__len__'):
      if len(aux) == 1:
        val: float = aux[0]
      else:
        return False
    else:
      return False

    if not np.isfinite(val):
      return False

    self._command.effort = (val * self._close_effort + (1.0 - val) * self._open_effort)
    self._state = val
    return True

  def load_gains(self, gains_file: str, attempts: int = 5):
    """Load the gains from the provided file and send the gains to the gripper.

    This method requests acknowledgement from the gripper that the gains
    were received. Consequently, this method may take a few seconds to execute
    if you are on a network which drops packets (e.g., a suboptimal WiFi network).
    The `attempts` parameter is used to re-send the gains, in the event
    that an ack was not received from the gripper.

    :param gains_file: The file location of the gains file
    :param attempts: the number of attempts to send the gains to the gripper.

    :return: ``True`` if gains were successfully sent to the gripper; otherwise ``False``
    :rtype:  bool
    """
    gains_cmd = GroupCommand(self._group.size)
    gains_cmd.read_gains(gains_file)

    return _repetitive_send_command_with_ack(self._group, gains_cmd, attempts)


class ArmPlugin:
  """Abstract base class representing a plugin to be used for an Arm object."""

  __slots__ = ('_enabled', '_enabled_ratio', '_ramp_time', '_name')

  def __init__(self, name: str, enabled: bool, ramp_time: float):
    self._name = name
    self._enabled = enabled
    self._enabled_ratio = 1.0 if enabled else 0.0
    self._ramp_time = ramp_time

  @property
  def name(self):
    """The name of the plugin.

    :rtype: str
    """
    return self._name

  @property
  def enabled(self):
    """Determines if the plugin should be invoked by the owning arm. If
    ``False``, this plugin will not be invoked on :meth:`Arm.update`.

    :rtype: bool
    """
    return self._enabled

  @enabled.setter
  def enabled(self, value):
    self._enabled = bool(value)

  def update(self, arm: Arm, dt: float):
    """Callback which updates state on the arm. Invoked by :meth:`Arm.update`.

    An implementation must return a boolean denoting ``True`` on success
    and ``False`` otherwise.
    """
    if self._enabled and self._enabled_ratio < 1.0:
      if self._ramp_time == 0.0:
        self._enabled_ratio = 1.0
      else:
        self._enabled_ratio = min(1.0, self._enabled_ratio + dt / self._ramp_time)
    elif not self._enabled and self._enabled_ratio > 0.0:
      if self._ramp_time == 0.0:
        self._enabled_ratio = 0.0
      else:
        self._enabled_ratio = max(0.0, self._enabled_ratio - dt / self._ramp_time)

  def on_associated(self, arm: Arm):
    """Override to update any state based on the associated arm.

    Invoked when the instance is added to an arm via
    :meth:`Arm.add_plugin`
    """
    pass


class GravCompEffortPlugin(ArmPlugin):
  __slots__ = ('_imu_feedback_index', '_imu_frame_index', '_imu_rotation_offset', '_grav_efforts')

  #def __init__(self, name: str = 'gravComp', enabled: bool = True, ramp_time: float = 0.0,
  #             imu_feedback_index: int = 0, imu_frame_index: int = 0,
  #             imu_rotation_offset: np.ndarray = np.eye(3, dtype=np.float64)):
  def __init__(self, *, imu_feedback_index: int = 0, imu_frame_index: int = 0, imu_rotation_offset: np.ndarray = np.eye(3, dtype=np.float64), **kwargs):
    super().__init__(**kwargs)
    self._imu_feedback_index = imu_feedback_index
    self._imu_frame_index = imu_frame_index
    self._imu_rotation_offset = imu_rotation_offset

  def on_associated(self, arm: Arm):
    self._grav_efforts = np.empty(arm.size, dtype=np.float64)

  def update(self, arm: Arm, dt: float):
    super().update(arm, dt)
    gravity = _gravity_from_quaternion(arm.last_feedback.orientation[self._imu_feedback_index])
    g_norm = np.linalg.norm(gravity)
    if g_norm > 0.0:
      gravity = gravity / g_norm * -9.81

    frames = arm.robot_model.get_forward_kinematics_mat(FrameType.Input, arm.last_feedback.position)
    gravity = frames[self._imu_frame_index, :3, :3] @ self._imu_rotation_offset @ gravity

    arm.robot_model.get_grav_comp_efforts(arm.last_feedback.position,
                                          gravity,
                                          jacobians=arm._com_jacobians,
                                          output=self._grav_efforts)
    arm.pending_command.effort += self._grav_efforts * self._enabled_ratio

    return True


class DynamicCompEffortPlugin(ArmPlugin):
  __slots__ = ('_dyn_efforts')

  def __init__(self, **kwargs):
    if 'name' not in kwargs:
      kwargs['name'] = 'dynamicComp'
    super().__init__(**kwargs)

  def on_associated(self, arm: Arm):
    self._dyn_efforts = np.empty(arm.size, dtype=np.float64)

  def update(self, arm: Arm, dt: float):
    super().update(arm, dt)
    # apply compensation torques for arm dynamics
    if arm.trajectory is not None:
      fbk_p = arm.last_feedback.position
      p, v, a = arm.trajectory.get_state(arm._last_time)
      arm.robot_model.get_dynamic_comp_efforts(fbk_p,
                                               p,
                                               v,
                                               a,
                                               jacobians=arm._com_jacobians,
                                               output=self._dyn_efforts)
      arm.pending_command.effort += self._dyn_efforts * self._enabled_ratio

    return True


class EffortOffset(ArmPlugin):
  """Plugin implementation used to offset the effort to be sent to the group.

  This offset can be scalar or a vector of length equal to the size of
  the group.
  """

  __slots__ = ('_offset')

  def __init__(self, *, offset: 'npt.NDArray[np.float32]', **kwargs):
    super().__init__(**kwargs)
    self._offset = offset

  def update(self, arm: Arm, dt: float):
    super().update(arm, dt)
    cmd = arm.pending_command
    cmd.effort += self._offset * self._enabled_ratio

    return True


class ImpedanceController(ArmPlugin):
  """Plugin implementation which provides an impedance controller for the
  arm."""

  __slots__ = (
      '_desired_tip_fk', '_actual_tip_fk', '_jacobian_end_effector', '_cmd_pos',
      '_cmd_vel', '_fbk_pos', '_cmd_effort', '_fbk_vel', '_impedance_effort',
      '_kp', '_ki', '_kd', 'gains_in_end_effector_frame', '_i_err', '_i_clamp')

  def __init__(self, *, gains_in_end_effector_frame: bool = False, **kwargs):
    super().__init__(**kwargs)
    self._jacobian_end_effector: 'npt.NDArray[np.float64]' = np.empty(0, dtype=np.float64)
    self._cmd_pos: 'npt.NDArray[np.float64]' = np.empty(0, dtype=np.float64)
    self._cmd_vel: 'npt.NDArray[np.float64]' = np.empty(0, dtype=np.float64)
    self._cmd_effort: 'npt.NDArray[np.float64]' = np.empty(0, dtype=np.float64)
    self._fbk_pos: 'npt.NDArray[np.float64]' = np.empty(0, dtype=np.float64)
    self._fbk_vel: 'npt.NDArray[np.float64]' = np.empty(0, dtype=np.float64)
    self._impedance_effort: 'npt.NDArray[np.float64]' = np.empty(0, dtype=np.float64)
    self._i_err = np.zeros(6)
    self._i_clamp = np.full(6, np.nan)

    self._desired_tip_fk: 'npt.NDArray[np.float64]' = np.identity(4, dtype=np.float64)
    self._actual_tip_fk: 'npt.NDArray[np.float64]' = np.identity(4, dtype=np.float64)
    self._kp: 'npt.NDArray[np.float64]'= np.zeros(6, dtype=np.float64)
    self._kd: 'npt.NDArray[np.float64]' = np.zeros(6, dtype=np.float64)
    self._ki: 'npt.NDArray[np.float64]' = np.zeros(6, dtype=np.float64)
    self.gains_in_end_effector_frame = gains_in_end_effector_frame

  def on_associated(self, arm: Arm):
    dof_count = arm.robot_model.dof_count

    self._jacobian_end_effector = np.zeros((6, dof_count), dtype=np.float64)
    self._cmd_pos = np.zeros(dof_count, dtype=np.float64)
    self._cmd_vel = np.zeros(dof_count, dtype=np.float64)
    self._cmd_effort = np.zeros(dof_count, dtype=np.float64)
    self._fbk_pos = np.zeros(dof_count, dtype=np.float64)
    self._fbk_vel = np.zeros(dof_count, dtype=np.float64)
    self._impedance_effort = np.zeros(dof_count, dtype=np.float64)

  def set_kp(self, x: float, y: float, z: float, roll: float, pitch: float, yaw: float):
    """Sets the proportional gains for the impedance controller. Units are
    (N/m) or (Nm/rad).

    :type x:     float
    :type y:     float
    :type z:     float
    :type roll:  float
    :type pitch: float
    :type yaw:   float
    """
    self._kp[:] = [x, y, z, roll, pitch, yaw]

  def set_ki(self, x: float, y: float, z: float, roll: float, pitch: float, yaw: float):
    """Sets the integral gains for the impedance controller.

    :type x:     float
    :type y:     float
    :type z:     float
    :type roll:  float
    :type pitch: float
    :type yaw:   float
    """
    self._ki[:] = [x, y, z, roll, pitch, yaw]

  def set_kd(self, x: float, y: float, z: float, roll: float, pitch: float, yaw: float):
    """Sets the damping gains for the impedance controller. Units are
    (N/(m/sec)) or (Nm/(rad/sec)).

    :type x:     float
    :type y:     float
    :type z:     float
    :type roll:  float
    :type pitch: float
    :type yaw:   float
    """
    self._kd[:] = [x, y, z, roll, pitch, yaw]

  def set_i_clamp(self, x: float, y: float, z: float, roll: float, pitch: float, yaw: float):
    """Sets the clamping values for the wrench produced by the impedance controller integrator.

    :type x:     float
    :type y:     float
    :type z:     float
    :type roll:  float
    :type pitch: float
    :type yaw:   float
    """
    self._i_clamp[:] = [x, y, z, roll, pitch, yaw]

  def update(self, arm: Arm, dt: float):
    super().update(arm, dt)
    arm_cmd = arm.pending_command
    arm_fbk = arm.last_feedback

    cmd_pos = arm_cmd.position
    cmd_vel = arm_cmd.velocity

    if np.isnan(cmd_pos).any() or np.isnan(cmd_vel).any():
      self._i_err = np.zeros(6)
      return True

    fbk_pos = arm_fbk.position
    fbk_vel = arm_fbk.velocity

    # instance cached to improve fast-path performance
    jacobian_end_effector = self._jacobian_end_effector
    actual_tip_fk = self._actual_tip_fk
    desired_tip_fk = self._desired_tip_fk

    kin = arm.robot_model
    kin.get_end_effector(cmd_pos, desired_tip_fk)
    kin.get_end_effector(fbk_pos, actual_tip_fk)
    kin.get_jacobian_end_effector(fbk_pos, jacobian_end_effector)

    xyz_error = desired_tip_fk[0:3, 3] - actual_tip_fk[0:3, 3]
    error_rot_mat = desired_tip_fk[0:3, 0:3] @ actual_tip_fk[0:3, 0:3].T
    rot_error_vec = _rot2axisangle(error_rot_mat)

    if self.gains_in_end_effector_frame:
      frame_rot = actual_tip_fk[0:3, 0:3]
    else:
      frame_rot = np.eye(3, dtype=np.float64)

    pos_error = np.empty(6, dtype=np.float64)
    pos_error[0:3] = xyz_error
    pos_error[3:6] = rot_error_vec
    vel_error = jacobian_end_effector @ (cmd_vel - fbk_vel)
    vel_error[3:6] = 0.0

    # Calculate impedance control wrenches and appropriate joint torques
    pos_error = self.__rotate(frame_rot.T, pos_error)
    vel_error = self.__rotate(frame_rot.T, vel_error)

    self._i_err += pos_error * dt

    wrench = self._kp * pos_error

    i_wrench = self._ki * self._i_err
    if not np.isnan(self._i_clamp).any():
      i_wrench = np.maximum(i_wrench, -1 * self._i_clamp)
      i_wrench = np.minimum(i_wrench, self._i_clamp)

    wrench += i_wrench
    wrench += self._kd * vel_error

    wrench = self.__rotate(frame_rot, wrench)

    impedance_effort = jacobian_end_effector.T @ wrench

    arm_cmd.effort += impedance_effort * self._enabled_ratio

    return True

  def __rotate(self, R: 'npt.NDArray[np.float64]', vec: 'npt.NDArray[np.float64]'):
    res = np.zeros(6, dtype=np.float64)
    res[0:3] = R.dot(vec[0:3])  # linear component
    res[3:6] = R.dot(vec[3:6])  # rotational component
    return res


class DoubledJointMirror(ArmPlugin):
  """Plugin implementation meant to be used for an arm that has a joint which
  is composed of two modules in parallel."""

  __slots__ = ('_group', '_cmd', '_index', '_sign')

  def __init__(self, *, index: int, group: 'Group', mirror: bool = True, **kwargs):
    super().__init__(**kwargs)

    if group.size != 1:
      raise ValueError("Expected a group of size 1")
    if index < 0:
      raise ValueError("index must be non-negative")

    self._group = group
    self._index = index
    self._cmd = GroupCommand(1)
    self._sign = -1.0 if mirror else 1.0

  def update(self, arm: Arm, dt: float):
    super().update(arm, dt)
    arm_cmd = arm.pending_command
    index = self._index

    src = arm_cmd[index]
    dst = self._cmd

    src_pos = src.position
    src_vel = src.velocity
    src_eff = src.effort

    if not np.isnan(src_pos):
      dst.position = self._sign * src_pos
    else:
      dst.position = np.nan

    if not np.isnan(src_vel):
      dst.velocity = self._sign * src_vel
    else:
      dst.velocity = np.nan

    if not np.isnan(src_eff):
      # split the effort between the 2 actuators
      new_effort = src_eff * 0.5
      src.effort = new_effort
      dst.effort = self._sign * new_effort
    else:
      dst.effort = np.nan

    return self._group.send_command(dst)


################################################################################
# Internal Helper Functions
################################################################################


def _rot2axisangle(R: 'np.ndarray'):
  # operating on a 3x3 rotation matrix
  R = R[:3, :3]
  # to avoid numerical errors, clamp trace to range [-1, 3]
  trace = max(-1.0, min(3.0, R.trace()))
  angle = np.arccos((trace - 1) / 2)
  axis = np.zeros(3, np.float64)
  axis[0] = (R-R.T)[2, 1]
  axis[1] = (R-R.T)[0, 2]
  axis[2] = (R-R.T)[1, 0]
  axis_len = np.sqrt(axis.dot(axis))

  if axis_len > 1e-6:
    return angle * (axis / axis_len)

  # technically this only needs to be done when y == 0, but numerical errors are
  # going to get worse with the fast method as you divide by a smaller number,
  # so start using the more complex method as we approach 180 degree rotations
  # have to do this a bit differently for singular matrices (0/180 degree rotations)
  tmp = R + R.T - np.eye(3) * (trace - 1)
  row_norm = np.linalg.norm(tmp, axis=1, keepdims=True)
  for row in range(tmp.shape[0]):
    if row_norm[row, 0] > 0:
      axis[:] = tmp[row, :] / row_norm[row, 0]
      break

  return axis * angle


def _gravity_from_quaternion(quaternion: 'Sequence[float]'):
  output: 'npt.NDArray[np.float64]' = np.empty(3, dtype=np.float64)

  X = quaternion[1]
  Y = quaternion[2]
  Z = quaternion[3]
  W = quaternion[0]

  xx = X * X
  xz = X * Z
  xw = X * W
  yy = Y * Y
  yz = Y * Z
  yw = Y * W

  output[0] = -2.0 * (xz - yw)
  output[1] = -2.0 * (yz + xw)
  output[2] = -1.0 + 2.0 * (xx + yy)

  return output


def _get_waypoint_times(times, num_waypoints, positions, velocities, accelerations):
  for i in range(num_waypoints):
    times[i] = 1.2 * i

  return times


def _repetitive_send_command_with_ack(group: 'Group', cmd: 'GroupCommand', attempts: int):
  for i in range(attempts):
    try:
      if group.send_command_with_acknowledgement(cmd):
        return True
    except:
      pass

  return False


################################################################################
#
################################################################################

_start_time = time.time()


def create_from_config(config: 'HebiConfig', lookup: 'Lookup | None' = None, ):
  """
  Create an Arm object based on the provided HebiConfig.

  This function initializes an arm using the specified configuration, including 
  loading any plugins defined in the configuration, such as Gravity Compensation, 
  Dynamic Compensation, Impedance Controller, and Doubled Joint plugins. The configuration 
  can also specify HRDF files and gain files to be used for setting up the arm.

  Example usage:

  .. code-block:: python

    import hebi
    from hebi.arm import create_from_config

    lookup = hebi.Lookup()
    config = hebi.config.load_config("path_to_config_file.yaml")
    arm = create_from_config(lookup, config)

  :param config: The configuration object containing settings for the arm, including families, 
                  names, HRDF file paths, plugin configurations, and gains.
  :type config: hebi.HebiConfig

  :param lookup: An instance of the Lookup class to use for finding groups.
  :type lookup: hebi.Lookup

  :return: The initialized Arm object with the specified configuration.
  :rtype: hebi.arm.Arm
  """

  if config.hrdf:
    hrdf_file = config.hrdf

  if lookup is None:
    lookup = Lookup()
    # Allow lookup registry to populate
    time.sleep(2)

  arm = create(config.families,
               config.names,
               lookup=lookup,
               hrdf_file=hrdf_file,
               setup_default_plugins=False)

  if config.plugins:
    for plugin in config.plugins:
      enabled = plugin.get('enabled', True)
      ramp_time = float(plugin.get('ramp_time', 0.0))

      if plugin['type'] == 'GravityCompensationEffort':
        name = plugin.get('name', 'gravComp')
        imu_feedback_index = int(plugin.get('imu_feedback_index', 0))
        imu_frame_index = int(plugin.get('imu_frame_index', 0))
        imu_rotation_offset = plugin.get('imu_rotation_offset', [1, 0, 0, 0, 1, 0, 0, 0, 1])
        imu_rotation_offset = np.array(imu_rotation_offset, dtype=np.float64)
        imu_rotation_offset = imu_rotation_offset.reshape((3, 3))
        arm.add_plugin(GravCompEffortPlugin(name=name,
                                            enabled=enabled,
                                            ramp_time=ramp_time,
                                            imu_feedback_index=imu_feedback_index,
                                            imu_frame_index=imu_frame_index,
                                            imu_rotation_offset=imu_rotation_offset))

      elif plugin['type'] == 'DynamicsCompensationEffort':
        name = plugin.get('name', 'dynamicsComp')
        arm.add_plugin(DynamicCompEffortPlugin(name=name,
                                               enabled=enabled,
                                               ramp_time=ramp_time))

      elif plugin['type'] == 'ImpedanceController':
        name = plugin.get('name', 'impedanceController')
        if isinstance(plugin['gains_in_end_effector_frame'], bool):
          in_ee_frame = plugin['gains_in_end_effector_frame']
        else:
          TypeError("Impedance controller plugin's 'gains_in_end_effector_frame' field must be a bool.")
        p = ImpedanceController(name=name,
                                enabled=enabled,
                                ramp_time=ramp_time,
                                gains_in_end_effector_frame=in_ee_frame)

        p.set_kp(*[float(i) for i in plugin['kp']])
        p.set_kd(*[float(i) for i in plugin['kd']])
        if 'ki' in plugin:
          p.set_ki(*[float(i) for i in plugin['ki']])
        if 'i_clamp' in plugin:
          p.set_i_clamp(*[float(i) for i in plugin['i_clamp']])
        arm.add_plugin(p)

      elif plugin['type'] == 'EffortOffset':
        name = plugin.get('name', 'effortOffset')
        offset = np.array(plugin['offset'], dtype=np.float32)
        arm.add_plugin(EffortOffset(name=name,
                                    enabled=enabled,
                                    ramp_time=ramp_time,
                                    offset=offset))

      elif plugin['type'] == 'DoubledJointMirror':
        name = plugin.get('name', 'doubledJoint')
        family = plugin['group_family']
        name = plugin['group_name']
        idx = int(plugin['index'])
        mirror = plugin['mirror'] if 'mirror' in plugin else True

        grp = None
        for _ in range(3):
          grp = lookup.get_group_from_names(family, name)
          if grp is not None:
            break
          print(f'Double shoulder plugin looking for module with family "{family}", name "{name}"')
          time.sleep(1)
        if grp is None:
          raise RuntimeError(f'Cannot find double shoulder module "{family}", name "{name}"')

        arm.add_plugin(DoubledJointMirror(name=name,
                                          enabled=enabled,
                                          ramp_time=ramp_time,
                                          index=idx,
                                          group=grp,
                                          mirror=mirror))

  if config.gains and 'default' in config.gains:
    gains_file = config.gains['default']
    arm.load_gains(gains_file=gains_file)

  return arm


def create(families: 'str | list[str]', names: 'list[str]| None' = None, command_lifetime: float = 100, control_frequency: float = 100.0,
           hrdf_file: 'str | None' = None, robot_model: 'RobotModel | None' = None, end_effector: 'EndEffector | None' = None,
           time_getter: 'Callable[[], float] | None' = None, lookup: 'Lookup | None' = None, setup_default_plugins: 'bool' = True) -> 'Arm':
  """Create an arm object based off of the provided kinematic representation.

  Examples::

    import hebi
    from hebi import arm as arm_api

    # Create based off of a 6-DoF arm with an HRDF file
    arm1 = arm_api.create(["Example Arm"],
                          names=['J1_base', 'J2_shoulder', 'J3_elbow', 'J4_wrist1', 'J5_wrist2', 'J6_wrist3'],
                          hrdf_file="hrdf/A-2085-06.hrdf")

    # Use some existing objects
    lookup = hebi.Lookup()
    existing_robot_model = get_robot_model()
    families = get_families()
    names = get_names()
    time_function = get_simulator_time_function()

    arm2 = arm_api.create(families=families, names=names,
                          robot_model=existing_robot_model,
                          time_getter=time_function,
                          lookup=lookup)


  :param families: Required parameter.
  :type families:  list, str

  :param names: Names of the modules in the group. If ``None``,
                :meth:`hebi.Lookup.get_group_from_family` will be used
  :type names:  list

  :param command_lifetime: How long a command takes effect for on the robot
                           before expiring.
  :type command_lifetime:  int

  :param control_frequency: Loop rate, in Hz. This is how fast the arm update
                            loop will nominally run.
  :type control_frequency:  float

  :param hrdf_file: The robot description. Cannot be used in combination
                    with ``robot_model``.
  :type hrdf_file:  str

  :param robot_model: The robot description. Cannot be used in combination
                      with ``hrdf_file``.
  :type robot_model:  hebi.robot_model.RobotModel

  :param end_effector: Optionally, supply an end effector to be controlled
                       by the "aux" state of provided goals.
  :type end_effector:  hebi.arm.EndEffector

  :param time_getter: A function pointer which returns a float representing
                      the current time in seconds. Can be overloaded
                      to use, e.g., simulator time
  :type time_getter:  callable

  :param lookup: An optional lookup instance to use to find the group.
                 The default instance will be provided if ``None``
  :type lookup:  hebi.Lookup

  :rtype: hebi.arm.Arm
  """

  command_lifetime = int(command_lifetime)
  control_frequency = float(control_frequency)

  if hrdf_file is not None and robot_model is not None:
    raise ValueError("hrdf_file or robot_model must be defined, but not both")
  elif hrdf_file is None and robot_model is None:
    raise ValueError("hrdf_file or robot_model must be defined")

  if time_getter is not None:
    if not callable(time_getter):
      raise TypeError("time_getter must be a callable object")
  elif time_getter is None:
    time_getter = lambda: time.time() - _start_time

  if lookup is None:
    lookup = Lookup()
    # Allow lookup registry to populate
    time.sleep(2)

  if robot_model is None:
    from .robot_model import import_from_hrdf
    if hrdf_file is None:
      raise RuntimeError('Cannot create arm without robot_model or hrdf_file')
    robot = import_from_hrdf(hrdf_file)
  else:
    robot = robot_model

  if names is not None:
    group = lookup.get_group_from_names(families, names)
  else:
    if isinstance(families, str):
      family = families
    else:
      family = families[0]

    group = lookup.get_group_from_family(family)

  if group is None:
    raise RuntimeError('Could not create arm. Check that family and names match actuators on the network.')

  if group.size != robot.dof_count:
    raise RuntimeError('Robot does not have the same number of actuators as group.')

  group.command_lifetime = command_lifetime
  group.feedback_frequency = control_frequency

  got_feedback = False
  for i in range(10):
    if group.get_next_feedback() is not None:
      got_feedback = True
      break

  if not got_feedback:
    raise RuntimeError("Could not communicate with robot: check your network connection.")

  plugins = None if setup_default_plugins else []

  return Arm(time_getter, group, robot, end_effector, plugins=plugins)
