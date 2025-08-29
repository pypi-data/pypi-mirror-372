# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2022 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

import numpy as np
import ctypes

# imports for dealing w/ IP addresses
import socket
import struct

from .wrappers import UnmanagedObject, UnmanagedSharedObject
from . import _marshalling
from ._marshalling import GroupFeedbackNumberedFloatField, GroupCommandNumberedFloatField, GroupInfoIoField, FeedbackIoField, GroupFeedbackIoField, GroupCommandIoField, GroupFeedbackLEDField, GroupCommandLEDField, CommandLEDField
from . import api, enums, ctypes_defs
from ..graphics import color_from_int, string_to_color
from .ctypes_defs import HebiCommandRef, HebiFeedbackRef
from hebi._internal.type_utils import create_string_buffer_compat as create_str

from ctypes import byref, cast
from .ctypes_utils import c_float_p
from numpy.ctypeslib import as_array

import typing
if typing.TYPE_CHECKING:
  from typing import Sequence, Mapping
  import numpy.typing as npt


class Command(UnmanagedObject):
  """Used to represent a Command object.

  Do not instantiate directly - use only through a GroupCommand instance.
  """

  __slots__ = ["_ref", "_led"]

  def __init__(self, internal, ref: 'HebiCommandRef'):
    """This is invoked internally.

    Do not use directly.
    """
    super().__init__(internal)
    self._ref = ref
    self._led = CommandLEDField(self._ref)

  def copy_gains_from(self, other: 'Command | Info'):
    if isinstance(other, Info):
      res = api.hebiCommandCopyGainsFromInfo(self, other)
    else:
      res = api.hebiCommandCopyGainsFromCommand(self, other)
    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiCommandCopyGainsFromCommand/Info failed')

  @property
  def led(self):
    """The module's LED.

    The available string colors are

      * red
      * green
      * blue
      * black
      * white
      * cyan
      * magenta
      * yellow
      * transparent

    :messageType led:
    :messageUnits n/a:
    """
    return self._led

  @property
  def velocity(self):
    """Velocity of the module output (post-spring).

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.Velocity)

  @velocity.setter
  def velocity(self, value: 'float | None'):
    """Setter for velocity."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.Velocity, value)

  @property
  def effort(self):
    """
    Effort at the module output; units vary (e.g., N * m for rotational joints and N for linear stages).

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.Effort)

  @effort.setter
  def effort(self, value: 'float | None'):
    """Setter for effort."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.Effort, value)

  @property
  def position_kp(self):
    """Proportional PID gain for position.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionKp)

  @position_kp.setter
  def position_kp(self, value: 'float | None'):
    """Setter for position_kp."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionKp, value)

  @property
  def position_ki(self):
    """Integral PID gain for position.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionKi)

  @position_ki.setter
  def position_ki(self, value: 'float | None'):
    """Setter for position_ki."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionKi, value)

  @property
  def position_kd(self):
    """Derivative PID gain for position.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionKd)

  @position_kd.setter
  def position_kd(self, value: 'float | None'):
    """Setter for position_kd."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionKd, value)

  @property
  def position_feed_forward(self):
    """Feed forward term for position (this term is multiplied by the target
    and added to the output).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionFeedForward)

  @position_feed_forward.setter
  def position_feed_forward(self, value: 'float | None'):
    """Setter for position_feed_forward."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionFeedForward, value)

  @property
  def position_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionDeadZone)

  @position_dead_zone.setter
  def position_dead_zone(self, value: 'float | None'):
    """Setter for position_dead_zone."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionDeadZone, value)

  @property
  def position_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionIClamp)

  @position_i_clamp.setter
  def position_i_clamp(self, value: 'float | None'):
    """Setter for position_i_clamp."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionIClamp, value)

  @property
  def position_punch(self):
    """Constant offset to the position PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionPunch)

  @position_punch.setter
  def position_punch(self, value: 'float | None'):
    """Setter for position_punch."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionPunch, value)

  @property
  def position_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionMinTarget)

  @position_min_target.setter
  def position_min_target(self, value: 'float | None'):
    """Setter for position_min_target."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionMinTarget, value)

  @property
  def position_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionMaxTarget)

  @position_max_target.setter
  def position_max_target(self, value: 'float | None'):
    """Setter for position_max_target."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionMaxTarget, value)

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionTargetLowpass)

  @position_target_lowpass.setter
  def position_target_lowpass(self, value: 'float | None'):
    """Setter for position_target_lowpass."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionTargetLowpass, value)

  @property
  def position_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionMinOutput)

  @position_min_output.setter
  def position_min_output(self, value: 'float | None'):
    """Setter for position_min_output."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionMinOutput, value)

  @property
  def position_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionMaxOutput)

  @position_max_output.setter
  def position_max_output(self, value: 'float | None'):
    """Setter for position_max_output."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionMaxOutput, value)

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.PositionOutputLowpass)

  @position_output_lowpass.setter
  def position_output_lowpass(self, value: 'float | None'):
    """Setter for position_output_lowpass."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.PositionOutputLowpass, value)

  @property
  def velocity_kp(self):
    """Proportional PID gain for velocity.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityKp)

  @velocity_kp.setter
  def velocity_kp(self, value: 'float | None'):
    """Setter for velocity_kp."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityKp, value)

  @property
  def velocity_ki(self):
    """Integral PID gain for velocity.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityKi)

  @velocity_ki.setter
  def velocity_ki(self, value: 'float | None'):
    """Setter for velocity_ki."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityKi, value)

  @property
  def velocity_kd(self):
    """Derivative PID gain for velocity.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityKd)

  @velocity_kd.setter
  def velocity_kd(self, value: 'float | None'):
    """Setter for velocity_kd."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityKd, value)

  @property
  def velocity_feed_forward(self):
    """Feed forward term for velocity (this term is multiplied by the target
    and added to the output).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityFeedForward)

  @velocity_feed_forward.setter
  def velocity_feed_forward(self, value: 'float | None'):
    """Setter for velocity_feed_forward."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityFeedForward, value)

  @property
  def velocity_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityDeadZone)

  @velocity_dead_zone.setter
  def velocity_dead_zone(self, value: 'float | None'):
    """Setter for velocity_dead_zone."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityDeadZone, value)

  @property
  def velocity_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityIClamp)

  @velocity_i_clamp.setter
  def velocity_i_clamp(self, value: 'float | None'):
    """Setter for velocity_i_clamp."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityIClamp, value)

  @property
  def velocity_punch(self):
    """Constant offset to the velocity PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityPunch)

  @velocity_punch.setter
  def velocity_punch(self, value: 'float | None'):
    """Setter for velocity_punch."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityPunch, value)

  @property
  def velocity_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityMinTarget)

  @velocity_min_target.setter
  def velocity_min_target(self, value: 'float | None'):
    """Setter for velocity_min_target."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityMinTarget, value)

  @property
  def velocity_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityMaxTarget)

  @velocity_max_target.setter
  def velocity_max_target(self, value: 'float | None'):
    """Setter for velocity_max_target."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityMaxTarget, value)

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityTargetLowpass)

  @velocity_target_lowpass.setter
  def velocity_target_lowpass(self, value: 'float | None'):
    """Setter for velocity_target_lowpass."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityTargetLowpass, value)

  @property
  def velocity_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityMinOutput)

  @velocity_min_output.setter
  def velocity_min_output(self, value: 'float | None'):
    """Setter for velocity_min_output."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityMinOutput, value)

  @property
  def velocity_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityMaxOutput)

  @velocity_max_output.setter
  def velocity_max_output(self, value: 'float | None'):
    """Setter for velocity_max_output."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityMaxOutput, value)

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityOutputLowpass)

  @velocity_output_lowpass.setter
  def velocity_output_lowpass(self, value: 'float | None'):
    """Setter for velocity_output_lowpass."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityOutputLowpass, value)

  @property
  def effort_kp(self):
    """Proportional PID gain for effort.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortKp)

  @effort_kp.setter
  def effort_kp(self, value: 'float | None'):
    """Setter for effort_kp."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortKp, value)

  @property
  def effort_ki(self):
    """Integral PID gain for effort.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortKi)

  @effort_ki.setter
  def effort_ki(self, value: 'float | None'):
    """Setter for effort_ki."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortKi, value)

  @property
  def effort_kd(self):
    """Derivative PID gain for effort.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortKd)

  @effort_kd.setter
  def effort_kd(self, value: 'float | None'):
    """Setter for effort_kd."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortKd, value)

  @property
  def effort_feed_forward(self):
    """Feed forward term for effort (this term is multiplied by the target and
    added to the output).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortFeedForward)

  @effort_feed_forward.setter
  def effort_feed_forward(self, value: 'float | None'):
    """Setter for effort_feed_forward."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortFeedForward, value)

  @property
  def effort_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortDeadZone)

  @effort_dead_zone.setter
  def effort_dead_zone(self, value: 'float | None'):
    """Setter for effort_dead_zone."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortDeadZone, value)

  @property
  def effort_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortIClamp)

  @effort_i_clamp.setter
  def effort_i_clamp(self, value: 'float | None'):
    """Setter for effort_i_clamp."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortIClamp, value)

  @property
  def effort_punch(self):
    """Constant offset to the effort PID output outside of the deadzone; it is
    added when the error is positive and subtracted when it is negative.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortPunch)

  @effort_punch.setter
  def effort_punch(self, value: 'float | None'):
    """Setter for effort_punch."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortPunch, value)

  @property
  def effort_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortMinTarget)

  @effort_min_target.setter
  def effort_min_target(self, value: 'float | None'):
    """Setter for effort_min_target."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortMinTarget, value)

  @property
  def effort_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortMaxTarget)

  @effort_max_target.setter
  def effort_max_target(self, value: 'float | None'):
    """Setter for effort_max_target."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortMaxTarget, value)

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortTargetLowpass)

  @effort_target_lowpass.setter
  def effort_target_lowpass(self, value: 'float | None'):
    """Setter for effort_target_lowpass."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortTargetLowpass, value)

  @property
  def effort_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortMinOutput)

  @effort_min_output.setter
  def effort_min_output(self, value: 'float | None'):
    """Setter for effort_min_output."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortMinOutput, value)

  @property
  def effort_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortMaxOutput)

  @effort_max_output.setter
  def effort_max_output(self, value: 'float | None'):
    """Setter for effort_max_output."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortMaxOutput, value)

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortOutputLowpass)

  @effort_output_lowpass.setter
  def effort_output_lowpass(self, value: 'float | None'):
    """Setter for effort_output_lowpass."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortOutputLowpass, value)

  @property
  def spring_constant(self):
    """The spring constant of the module.

    :rtype: float
    :messageType float:
    :messageUnits N/m:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.SpringConstant)

  @spring_constant.setter
  def spring_constant(self, value: 'float | None'):
    """Setter for spring_constant."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.SpringConstant, value)

  @property
  def reference_position(self):
    """Set the internal encoder reference offset so that the current position
    matches the given reference command.

    :rtype: float
    :messageType float:
    :messageUnits rad:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.ReferencePosition)

  @reference_position.setter
  def reference_position(self, value: 'float | None'):
    """Setter for reference_position."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.ReferencePosition, value)

  @property
  def reference_effort(self):
    """Set the internal effort reference offset so that the current effort
    matches the given reference command.

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.ReferenceEffort)

  @reference_effort.setter
  def reference_effort(self, value: 'float | None'):
    """Setter for reference_effort."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.ReferenceEffort, value)

  @property
  def velocity_limit_min(self):
    """The firmware safety limit for the minimum allowed velocity.

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityLimitMin)

  @velocity_limit_min.setter
  def velocity_limit_min(self, value: 'float | None'):
    """Setter for velocity_limit_min."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityLimitMin, value)

  @property
  def velocity_limit_max(self):
    """The firmware safety limit for the maximum allowed velocity.

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.VelocityLimitMax)

  @velocity_limit_max.setter
  def velocity_limit_max(self, value: float):
    """Setter for velocity_limit_max."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.VelocityLimitMax, value)

  @property
  def effort_limit_min(self):
    """The firmware safety limit for the minimum allowed effort.

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortLimitMin)

  @effort_limit_min.setter
  def effort_limit_min(self, value: float):
    """Setter for effort_limit_min."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortLimitMin, value)

  @property
  def effort_limit_max(self):
    """The firmware safety limit for the maximum allowed effort.

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.CommandFloatField.EffortLimitMax)

  @effort_limit_max.setter
  def effort_limit_max(self, value: float):
    """Setter for effort_limit_max."""
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.EffortLimitMax, value)

  @property
  def motor_foc_id(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.MotorFocId)

  @motor_foc_id.setter
  def motor_foc_id(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.MotorFocId, value)

  @property
  def motor_foc_iq(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.MotorFocIq)

  @motor_foc_iq.setter
  def motor_foc_iq(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.MotorFocIq, value)

  @property
  def user_settings_float1(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat1)

  @user_settings_float1.setter
  def user_settings_float1(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat1, value)

  @property
  def user_settings_float2(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat2)

  @user_settings_float2.setter
  def user_settings_float2(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat2, value)

  @property
  def user_settings_float3(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat3)

  @user_settings_float3.setter
  def user_settings_float3(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat3, value)

  @property
  def user_settings_float4(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat4)

  @user_settings_float4.setter
  def user_settings_float4(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat4, value)

  @property
  def user_settings_float5(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat5)

  @user_settings_float5.setter
  def user_settings_float5(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat5, value)

  @property
  def user_settings_float6(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat6)

  @user_settings_float6.setter
  def user_settings_float6(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat6, value)

  @property
  def user_settings_float7(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat7)

  @user_settings_float7.setter
  def user_settings_float7(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat7, value)

  @property
  def user_settings_float8(self):
    return _marshalling.get_float(self._ref, enums.CommandFloatField.UserSettingsFloat8)

  @user_settings_float8.setter
  def user_settings_float8(self, value: float):
    _marshalling.set_command_float(self._ref, enums.CommandFloatField.UserSettingsFloat8, value)

  @property
  def ip_address(self):
    raw_value = _marshalling.get_uint64(self._ref, enums.CommandUInt64Field.IpAddress)
    return socket.inet_ntoa(struct.pack("!I", raw_value))

  @ip_address.setter
  def ip_address(self, value: str):
    return _marshalling.set_command_uint64(self._ref, enums.CommandUInt64Field.IpAddress, struct.unpack("!I", socket.inet_aton(value))[0])

  @property
  def subnet_mask(self):
    raw_value = _marshalling.get_uint64(self._ref, enums.CommandUInt64Field.SubnetMask)
    return socket.inet_ntoa(struct.pack("!I", raw_value))

  @subnet_mask.setter
  def subnet_mask(self, value: str):
    return _marshalling.set_command_uint64(self._ref, enums.CommandUInt64Field.SubnetMask, struct.unpack("!I", socket.inet_aton(value))[0])

  @property
  def position(self):
    """Position of the module output (post-spring).

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_command_highresangle(self._ref, enums.CommandHighResAngleField.Position)

  @position.setter
  def position(self, value: float):
    """Setter for position."""
    _marshalling.set_command_highresangle(self._ref, enums.CommandHighResAngleField.Position, value)

  @property
  def position_limit_min(self):
    """The firmware safety limit for the minimum allowed position.

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_command_highresangle(self._ref, enums.CommandHighResAngleField.PositionLimitMin)

  @position_limit_min.setter
  def position_limit_min(self, value: float):
    """Setter for position_limit_min."""
    _marshalling.set_command_highresangle(self._ref, enums.CommandHighResAngleField.PositionLimitMin, value)

  @property
  def position_limit_max(self):
    """The firmware safety limit for the maximum allowed position.

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_command_highresangle(self._ref, enums.CommandHighResAngleField.PositionLimitMax)

  @position_limit_max.setter
  def position_limit_max(self, value: float):
    """Setter for position_limit_max."""
    _marshalling.set_command_highresangle(self._ref, enums.CommandHighResAngleField.PositionLimitMax, value)

  @property
  def position_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.CommandBoolField.PositionDOnError)

  @position_d_on_error.setter
  def position_d_on_error(self, value: bool):
    """Setter for position_d_on_error."""
    _marshalling.set_command_bool(self._ref, enums.CommandBoolField.PositionDOnError, value)

  @property
  def velocity_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.CommandBoolField.VelocityDOnError)

  @velocity_d_on_error.setter
  def velocity_d_on_error(self, value: bool):
    """Setter for velocity_d_on_error."""
    _marshalling.set_command_bool(self._ref, enums.CommandBoolField.VelocityDOnError, value)

  @property
  def effort_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.CommandBoolField.EffortDOnError)

  @effort_d_on_error.setter
  def effort_d_on_error(self, value: bool):
    """Setter for effort_d_on_error."""
    _marshalling.set_command_bool(self._ref, enums.CommandBoolField.EffortDOnError, value)

  @property
  def accel_includes_gravity(self):
    """Whether to include acceleration due to gravity in acceleration feedback.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.CommandBoolField.AccelIncludesGravity)

  @accel_includes_gravity.setter
  def accel_includes_gravity(self, value: bool):
    """Setter for accel_includes_gravity."""
    _marshalling.set_command_bool(self._ref, enums.CommandBoolField.AccelIncludesGravity, value)

  @property
  def save_current_settings(self):
    """Indicates if the module should save the current values of all of its
    settings.

    :rtype: bool
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_command_flag(self._ref, enums.CommandFlagField.SaveCurrentSettings)

  @save_current_settings.setter
  def save_current_settings(self, value: bool):
    """Setter for save_current_settings."""
    _marshalling.set_command_flag(self._ref, enums.CommandFlagField.SaveCurrentSettings, value)

  @property
  def reset(self):
    """Restart the module.

    :rtype: bool
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_command_flag(self._ref, enums.CommandFlagField.Reset)

  @reset.setter
  def reset(self, value: bool):
    """Setter for reset."""
    _marshalling.set_command_flag(self._ref, enums.CommandFlagField.Reset, value)

  @property
  def boot(self):
    """Boot the module from bootloader into application.

    :rtype: bool
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_command_flag(self._ref, enums.CommandFlagField.Boot)

  @boot.setter
  def boot(self, value: bool):
    """Setter for boot."""
    _marshalling.set_command_flag(self._ref, enums.CommandFlagField.Boot, value)

  @property
  def stop_boot(self):
    """Stop the module from automatically booting into application.

    :rtype: bool
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_command_flag(self._ref, enums.CommandFlagField.StopBoot)

  @stop_boot.setter
  def stop_boot(self, value: bool):
    """Setter for stop_boot."""
    _marshalling.set_command_flag(self._ref, enums.CommandFlagField.StopBoot, value)

  @property
  def clear_log(self):
    """Clears the log message on the module.

    :rtype: bool
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_command_flag(self._ref, enums.CommandFlagField.ClearLog)

  @clear_log.setter
  def clear_log(self, value: bool):
    """Setter for clear_log."""
    _marshalling.set_command_flag(self._ref, enums.CommandFlagField.ClearLog, value)

  @property
  def control_strategy(self):
    """How the position, velocity, and effort PID loops are connected in order
    to control motor PWM.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.CommandEnumField.ControlStrategy)

  @control_strategy.setter
  def control_strategy(self, value: 'int | str'):
    """Setter for control_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "Off"
      * "DirectPWM"
      * "Strategy2"
      * "Strategy3"
      * "Strategy4"
    """
    value = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_control_strategy_str_mappings)
    _marshalling.set_command_enum(self._ref, enums.CommandEnumField.ControlStrategy, value)

  @property
  def mstop_strategy(self):
    """The motion stop strategy for the actuator.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.CommandEnumField.MstopStrategy)

  @mstop_strategy.setter
  def mstop_strategy(self, value: 'int | str'):
    """Setter for mstop_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "Disabled"
      * "MotorOff"
      * "HoldPosition"
    """
    value = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_mstop_strategy_str_mappings)
    _marshalling.set_command_enum(self._ref, enums.CommandEnumField.MstopStrategy, value)

  @property
  def min_position_limit_strategy(self):
    """The position limit strategy (at the minimum position) for the actuator.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.CommandEnumField.MinPositionLimitStrategy)

  @min_position_limit_strategy.setter
  def min_position_limit_strategy(self, value: 'int | str'):
    """Setter for min_position_limit_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "HoldPosition"
      * "DampedSpring"
      * "MotorOff"
      * "Disabled"
    """
    value = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_min_position_limit_strategy_str_mappings)
    _marshalling.set_command_enum(self._ref, enums.CommandEnumField.MinPositionLimitStrategy, value)

  @property
  def max_position_limit_strategy(self):
    """The position limit strategy (at the maximum position) for the actuator.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.CommandEnumField.MaxPositionLimitStrategy)

  @max_position_limit_strategy.setter
  def max_position_limit_strategy(self, value: 'int | str'):
    """Setter for max_position_limit_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "HoldPosition"
      * "DampedSpring"
      * "MotorOff"
      * "Disabled"
    """
    value = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_max_position_limit_strategy_str_mappings)
    _marshalling.set_command_enum(self._ref, enums.CommandEnumField.MaxPositionLimitStrategy, value)

  @property
  def name(self):
    """The name for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_command_string(self, enums.CommandStringField.Name)

  @name.setter
  def name(self, value: str):
    """Setter for name."""
    _marshalling.set_command_string(self, enums.CommandStringField.Name, value)

  @property
  def family(self):
    """The family for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_command_string(self, enums.CommandStringField.Family)

  @family.setter
  def family(self, value: 'str | None'):
    """Setter for family."""
    _marshalling.set_command_string(self, enums.CommandStringField.Family, value)

  @property
  def append_log(self):
    """Appends to the current log message on the module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_command_string(self, enums.CommandStringField.AppendLog)

  @append_log.setter
  def append_log(self, value: str):
    """Setter for append_log."""
    _marshalling.set_command_string(self, enums.CommandStringField.AppendLog, value)


class Feedback(UnmanagedObject):
  """Used to represent a Feedback object.

  Do not instantiate directly - use only through a GroupFeedback instance.
  """

  __slots__ = [
      "_ref",
      "_io",
      "_accelerometer_view",
      "_gyro_view",
      "_ar_position_view",
      "_orientation_view",
      "_ar_orientation_view",

  ]

  def __init__(self, internal, ref: 'HebiFeedbackRef'):
    """This is invoked internally.

    Do not use directly.
    """
    super().__init__(internal)
    self._ref = ref
    self._io = FeedbackIoField(self)

    self._accelerometer_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._gyro_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._ar_position_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._orientation_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._ar_orientation_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)

  @property
  def io(self):
    return self._io

  @property
  def board_temperature(self):
    """Ambient temperature inside the module (measured at the IMU chip)

    :rtype: float
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.BoardTemperature)

  @property
  def processor_temperature(self):
    """Temperature of the processor chip.

    :rtype: float
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.ProcessorTemperature)

  @property
  def voltage(self):
    """Bus voltage at which the module is running.

    :rtype: float
    :messageType float:
    :messageUnits V:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.Voltage)

  @property
  def velocity(self):
    """Velocity of the module output (post-spring).

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.Velocity)

  @property
  def effort(self):
    """
    Effort at the module output; units vary (e.g., N * m for rotational joints and N for linear stages).

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.Effort)

  @property
  def velocity_command(self):
    """Commanded velocity of the module output (post-spring)

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.VelocityCommand)

  @property
  def effort_command(self):
    """
    Commanded effort at the module output; units vary (e.g., N * m for rotational joints and N for linear stages).

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.EffortCommand)

  @property
  def deflection(self):
    """Difference between the pre-spring and post-spring output position.

    :rtype: float
    :messageType float:
    :messageUnits rad:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.Deflection)

  @property
  def deflection_velocity(self):
    """Velocity of the difference between the pre-spring and post-spring output
    position.

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.DeflectionVelocity)

  @property
  def motor_velocity(self):
    """The velocity of the motor shaft.

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorVelocity)

  @property
  def motor_current(self):
    """Current supplied to the motor.

    :rtype: float
    :messageType float:
    :messageUnits A:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorCurrent)

  @property
  def motor_sensor_temperature(self):
    """The temperature from a sensor near the motor housing.

    :rtype: float
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorSensorTemperature)

  @property
  def motor_winding_current(self):
    """The estimated current in the motor windings.

    :rtype: float
    :messageType float:
    :messageUnits A:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorWindingCurrent)

  @property
  def motor_winding_temperature(self):
    """The estimated temperature of the motor windings.

    :rtype: float
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorWindingTemperature)

  @property
  def motor_housing_temperature(self):
    """The estimated temperature of the motor housing.

    :rtype: float
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorHousingTemperature)

  @property
  def battery_level(self):
    """Charge level of the device's battery (in percent).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.BatteryLevel)

  @property
  def pwm_command(self):
    """Commanded PWM signal sent to the motor; final output of PID controllers.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.PwmCommand)

  @property
  def inner_effort_command(self):
    """In control strategies 2 and 4, this is the torque of force command going
    to the inner torque PID loop.

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.InnerEffortCommand)

  @property
  def motor_winding_voltage(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorWindingVoltage)

  @property
  def motor_phase_current_a(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseCurrentA)

  @property
  def motor_phase_current_b(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseCurrentB)

  @property
  def motor_phase_current_c(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseCurrentC)

  @property
  def motor_phase_voltage_a(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseVoltageA)

  @property
  def motor_phase_voltage_b(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseVoltageB)

  @property
  def motor_phase_voltage_c(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseVoltageC)

  @property
  def motor_phase_duty_cycle_a(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseDutyCycleA)

  @property
  def motor_phase_duty_cycle_b(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseDutyCycleB)

  @property
  def motor_phase_duty_cycle_c(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorPhaseDutyCycleC)

  @property
  def motor_foc_id(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorFocId)

  @property
  def motor_foc_iq(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorFocIq)

  @property
  def motor_foc_id_command(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorFocIdCommand)

  @property
  def motor_foc_iq_command(self):
    return _marshalling.get_float(self._ref, enums.FeedbackFloatField.MotorFocIqCommand)

  @property
  def position(self):
    """Position of the module output (post-spring).

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_feedback_highresangle(self._ref, enums.FeedbackHighResAngleField.Position)

  @property
  def position_command(self):
    """Commanded position of the module output (post-spring).

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_feedback_highresangle(self._ref, enums.FeedbackHighResAngleField.PositionCommand)

  @property
  def motor_position(self):
    """The position of an actuator's internal motor before the gear reduction.

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_feedback_highresangle(self._ref, enums.FeedbackHighResAngleField.MotorPosition)

  @property
  def sequence_number(self):
    """Sequence number going to module (local)

    :rtype: int
    :messageType UInt64:
    :messageUnits None:
    """
    return _marshalling.get_uint64(self._ref, enums.FeedbackUInt64Field.SequenceNumber)

  @property
  def receive_time(self):
    """Timestamp of when message was received from module (local)

    :rtype: int
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_uint64(self._ref, enums.FeedbackUInt64Field.ReceiveTime)

  @property
  def transmit_time(self):
    """Timestamp of when message was transmitted to module (local)

    :rtype: int
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_uint64(self._ref, enums.FeedbackUInt64Field.TransmitTime)

  @property
  def hardware_receive_time(self):
    """Timestamp of when message was received by module (remote)

    :rtype: int
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_uint64(self._ref, enums.FeedbackUInt64Field.HardwareReceiveTime)

  @property
  def hardware_transmit_time(self):
    """Timestamp of when message was transmitted from module (remote)

    :rtype: int
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_uint64(self._ref, enums.FeedbackUInt64Field.HardwareTransmitTime)

  @property
  def sender_id(self):
    """Unique ID of the module transmitting this feedback.

    :rtype: int
    :messageType UInt64:
    :messageUnits None:
    """
    return _marshalling.get_uint64(self._ref, enums.FeedbackUInt64Field.SenderId)

  @property
  def rx_sequence_number(self):
    """Rx Sequence number of this feedback.

    :rtype: int
    :messageType UInt64:
    :messageUnits None:
    """
    return _marshalling.get_uint64(self._ref, enums.FeedbackUInt64Field.RxSequenceNumber)

  @property
  def accelerometer(self):
    """Accelerometer data.

    :rtype: numpy.array
    :messageType vector3f:
    :messageUnits m/s^2:
    """

    if self._accelerometer_view.size == 0:
      v3f_acc = self._ref.vector3f_fields_[enums.FeedbackVector3fField.Accelerometer.value]
      self._accelerometer_view: 'npt.NDArray[np.float32]' = as_array(cast(byref(v3f_acc), c_float_p), (3,))
    return self._accelerometer_view

  @property
  def gyro(self):
    """Gyro data.

    :rtype: numpy.array
    :messageType vector3f:
    :messageUnits rad/s:
    """
    if self._gyro_view.size == 0:
      v3f_gyro = self._ref.vector3f_fields_[enums.FeedbackVector3fField.Gyro.value]
      self._gyro_view: 'npt.NDArray[np.float32]' = as_array(cast(byref(v3f_gyro), c_float_p), (3,))
    return self._gyro_view

  @property
  def ar_position(self):
    """A device's position in the world as calculated from an augmented reality
    framework.

    :rtype: numpy.array
    :messageType vector3f:
    :messageUnits m:
    """
    if self._ar_position_view.size == 0:
      v3f_ar_pos = self._ref.vector3f_fields_[enums.FeedbackVector3fField.ArPosition.value]
      self._ar_position_view: 'npt.NDArray[np.float32]' = as_array(cast(byref(v3f_ar_pos), c_float_p), (3,))
    return self._ar_position_view

  @property
  def orientation(self):
    """A filtered estimate of the orientation of the module.

    :rtype: numpy.array
    :messageType quaternionf:
    :messageUnits None:
    """
    if self._orientation_view.size == 0:
      quatf_orientation = self._ref.quaternionf_fields_[enums.FeedbackQuaternionfField.Orientation.value]
      self._orientation_view: 'npt.NDArray[np.float32]' = as_array(cast(byref(quatf_orientation), c_float_p), (4,))
    return self._orientation_view

  @property
  def ar_orientation(self):
    """A device's orientation in the world as calculated from an augmented
    reality framework.

    :rtype: numpy.array
    :messageType quaternionf:
    :messageUnits None:
    """
    if self._ar_orientation_view.size == 0:
      quatf_ar_orientation = self._ref.quaternionf_fields_[enums.FeedbackQuaternionfField.ArOrientation.value]
      self._ar_orientation_view: 'npt.NDArray[np.float32]' = as_array(cast(byref(quatf_ar_orientation), c_float_p), (4,))
    return self._ar_orientation_view

  @property
  def temperature_state(self):
    """Describes how the temperature inside the module is limiting the output
    of the motor.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.TemperatureState)

  @property
  def mstop_state(self):
    """Current status of the MStop.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.MstopState)

  @property
  def position_limit_state(self):
    """Software-controlled bounds on the allowable position of the module; user
    settable.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.PositionLimitState)

  @property
  def velocity_limit_state(self):
    """Software-controlled bounds on the allowable velocity of the module.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.VelocityLimitState)

  @property
  def effort_limit_state(self):
    """Software-controlled bounds on the allowable effort of the module.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.EffortLimitState)

  @property
  def command_lifetime_state(self):
    """The state of the command lifetime safety controller, with respect to the
    current group.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.CommandLifetimeState)

  @property
  def ar_quality(self):
    """The status of the augmented reality tracking, if using an AR enabled
    device. See HebiArQuality for values.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.ArQuality)

  @property
  def motor_hall_state(self):
    """The status of the motor driver hall sensor.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.FeedbackEnumField.MotorHallState)


class Info(UnmanagedObject):
  """Used to represent a Info object.

  Do not instantiate directly - use only through a GroupInfo instance.
  """

  __slots__ = ["_ref"]

  def __init__(self, internal, ref):
    """This is invoked internally.

    Do not use directly.
    """
    super().__init__(internal)
    self._ref = ref

  @property
  def position_kp(self):
    """Proportional PID gain for position.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionKp)

  @property
  def position_ki(self):
    """Integral PID gain for position.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionKi)

  @property
  def position_kd(self):
    """Derivative PID gain for position.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionKd)

  @property
  def position_feed_forward(self):
    """Feed forward term for position (this term is multiplied by the target
    and added to the output).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionFeedForward)

  @property
  def position_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionDeadZone)

  @property
  def position_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionIClamp)

  @property
  def position_punch(self):
    """Constant offset to the position PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionPunch)

  @property
  def position_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionMinTarget)

  @property
  def position_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionMaxTarget)

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionTargetLowpass)

  @property
  def position_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionMinOutput)

  @property
  def position_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionMaxOutput)

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.PositionOutputLowpass)

  @property
  def velocity_kp(self):
    """Proportional PID gain for velocity.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityKp)

  @property
  def velocity_ki(self):
    """Integral PID gain for velocity.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityKi)

  @property
  def velocity_kd(self):
    """Derivative PID gain for velocity.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityKd)

  @property
  def velocity_feed_forward(self):
    """Feed forward term for velocity (this term is multiplied by the target
    and added to the output).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityFeedForward)

  @property
  def velocity_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityDeadZone)

  @property
  def velocity_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityIClamp)

  @property
  def velocity_punch(self):
    """Constant offset to the velocity PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityPunch)

  @property
  def velocity_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityMinTarget)

  @property
  def velocity_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityMaxTarget)

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityTargetLowpass)

  @property
  def velocity_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityMinOutput)

  @property
  def velocity_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityMaxOutput)

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityOutputLowpass)

  @property
  def effort_kp(self):
    """Proportional PID gain for effort.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortKp)

  @property
  def effort_ki(self):
    """Integral PID gain for effort.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortKi)

  @property
  def effort_kd(self):
    """Derivative PID gain for effort.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortKd)

  @property
  def effort_feed_forward(self):
    """Feed forward term for effort (this term is multiplied by the target and
    added to the output).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortFeedForward)

  @property
  def effort_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortDeadZone)

  @property
  def effort_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortIClamp)

  @property
  def effort_punch(self):
    """Constant offset to the effort PID output outside of the deadzone; it is
    added when the error is positive and subtracted when it is negative.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortPunch)

  @property
  def effort_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortMinTarget)

  @property
  def effort_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortMaxTarget)

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortTargetLowpass)

  @property
  def effort_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortMinOutput)

  @property
  def effort_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortMaxOutput)

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: float
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortOutputLowpass)

  @property
  def spring_constant(self):
    """The spring constant of the module.

    :rtype: float
    :messageType float:
    :messageUnits N/m:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.SpringConstant)

  @property
  def velocity_limit_min(self):
    """The firmware safety limit for the minimum allowed velocity.

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityLimitMin)

  @property
  def velocity_limit_max(self):
    """The firmware safety limit for the maximum allowed velocity.

    :rtype: float
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.VelocityLimitMax)

  @property
  def effort_limit_min(self):
    """The firmware safety limit for the minimum allowed effort.

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortLimitMin)

  @property
  def effort_limit_max(self):
    """The firmware safety limit for the maximum allowed effort.

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.EffortLimitMax)

  @property
  def position_limit_min(self):
    """The firmware safety limit for the minimum allowed position.

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_info_highresangle(self._ref, enums.InfoHighResAngleField.PositionLimitMin)

  @property
  def position_limit_max(self):
    """The firmware safety limit for the maximum allowed position.

    :rtype: float
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_info_highresangle(self._ref, enums.InfoHighResAngleField.PositionLimitMax)

  @property
  def position_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.InfoBoolField.PositionDOnError)

  @property
  def velocity_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.InfoBoolField.VelocityDOnError)

  @property
  def effort_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.InfoBoolField.EffortDOnError)

  @property
  def accel_includes_gravity(self):
    """Whether to include acceleration due to gravity in acceleration feedback.

    :rtype: bool
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_bool(self._ref, enums.InfoBoolField.AccelIncludesGravity)

  @property
  def save_current_settings(self):
    """Indicates if the module should save the current values of all of its
    settings.

    :rtype: bool
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_info_flag(self._ref, enums.InfoFlagField.SaveCurrentSettings)

  @property
  def control_strategy(self):
    """How the position, velocity, and effort PID loops are connected in order
    to control motor PWM.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.InfoEnumField.ControlStrategy)

  @property
  def calibration_state(self):
    """The calibration state of the module.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.InfoEnumField.CalibrationState)

  @property
  def mstop_strategy(self):
    """The motion stop strategy for the actuator.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.InfoEnumField.MstopStrategy)

  @property
  def min_position_limit_strategy(self):
    """The position limit strategy (at the minimum position) for the actuator.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.InfoEnumField.MinPositionLimitStrategy)

  @property
  def max_position_limit_strategy(self):
    """The position limit strategy (at the maximum position) for the actuator.

    :rtype: int
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_enum(self._ref, enums.InfoEnumField.MaxPositionLimitStrategy)

  @property
  def name(self):
    """The name for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.Name)

  @property
  def family(self):
    """The family for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.Family)

  @property
  def serial(self):
    """Gets the serial number for this module (e.g., X5-0001).

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.Serial)

  @property
  def ip_address(self):
    raw_value = _marshalling.get_uint64(self._ref, enums.InfoUInt64Field.IpAddress)
    return socket.inet_ntoa(struct.pack("!I", raw_value))

  @property
  def subnet_mask(self):
    raw_value = _marshalling.get_uint64(self._ref, enums.InfoUInt64Field.SubnetMask)
    return socket.inet_ntoa(struct.pack("!I", raw_value))

  @property
  def default_gateway(self):
    raw_value = _marshalling.get_uint64(self._ref, enums.InfoUInt64Field.DefaultGateway)
    return socket.inet_ntoa(struct.pack("!I", raw_value))

  @property
  def electrical_type(self):
    """Gets the electrical type for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.ElectricalType)

  @property
  def electrical_revision(self):
    """Gets the electrical revision for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.ElectricalRevision)

  @property
  def mechanical_type(self):
    """Gets the mechanical type for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.MechanicalType)

  @property
  def mechanical_revision(self):
    """Gets the mechanical revision for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.MechanicalRevision)

  @property
  def firmware_type(self):
    """Gets the firmware type for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.FirmwareType)

  @property
  def firmware_revision(self):
    """Gets the firmware revision for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.FirmwareRevision)

  @property
  def user_settings_float1(self):
    """Gets the user setting (float1) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat1)

  @property
  def user_settings_float2(self):
    """Gets the user setting (float2) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat2)

  @property
  def user_settings_float3(self):
    """Gets the user setting (float3) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat3)

  @property
  def user_settings_float4(self):
    """Gets the user setting (float4) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat4)

  @property
  def user_settings_float5(self):
    """Gets the user setting (float5) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat5)

  @property
  def user_settings_float6(self):
    """Gets the user setting (float6) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat6)

  @property
  def user_settings_float7(self):
    """Gets the user setting (float7) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat7)

  @property
  def user_settings_float8(self):
    """Gets the user setting (float8) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_float(self._ref, enums.InfoFloatField.UserSettingsFloat8)

  @property
  def user_settings_bytes1(self):
    """Gets the user setting (float1) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes1)

  @property
  def user_settings_bytes2(self):
    """Gets the user setting (float2) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes2)

  @property
  def user_settings_bytes3(self):
    """Gets the user setting (float3) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes3)

  @property
  def user_settings_bytes4(self):
    """Gets the user setting (float4) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes4)

  @property
  def user_settings_bytes5(self):
    """Gets the user setting (float5) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes5)

  @property
  def user_settings_bytes6(self):
    """Gets the user setting (float6) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes6)

  @property
  def user_settings_bytes7(self):
    """Gets the user setting (float7) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes7)

  @property
  def user_settings_bytes8(self):
    """Gets the user setting (float8) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_info_string(self, enums.InfoStringField.UserSettingsBytes8)


class GroupCommandBase(UnmanagedSharedObject):
  """Base class for command.

  Do not use directly.
  """

  __slots__ = [
      '_refs',
      '_number_of_modules',
      '__weakref__',
      '_io',
      '_debug',
      '_led',
      '_velocity_view',
      '_effort_view',
  ]

  def _initialize(self, number_of_modules: int):
    self._number_of_modules = number_of_modules
    self._refs = (HebiCommandRef * number_of_modules)()

    self._io = GroupCommandIoField(self)
    self._debug = GroupCommandNumberedFloatField(self, enums.CommandNumberedFloatField.Debug)
    self._led = GroupCommandLEDField(self)

    self._velocity_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._effort_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)

  def __init__(self, internal=None, on_delete=(lambda _: None), existing=None, isdummy=False):
    super().__init__(internal, on_delete, existing, isdummy)

  def copy_gains_from(self, other: 'GroupCommandBase | GroupInfoBase'):
    if isinstance(other, GroupInfoBase):
      res = api.hebiGroupCommandCopyGainsFromInfo(self, other)
    elif isinstance(other, GroupCommandBase):
      res = api.hebiGroupCommandCopyGainsFromCommand(self, other)
    else:
      raise TypeError(f'Cannot copy gains from unknown object type {type(other)}')

    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupCommandCopyGainsFromCommand/Info failed')

  @property
  def refs(self):
    return (HebiCommandRef * self._number_of_modules)(*self._refs)

  @property
  def size(self):
    """The number of modules in this group message."""
    return self._number_of_modules

  @property
  def modules(self) -> 'list[Command]':
    raise NotImplementedError()

  @property
  def velocity(self):
    """Velocity of the module output (post-spring).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    if self._velocity_view.size == 0:
      return _marshalling.get_group_float(self._refs, enums.CommandFloatField.Velocity)
    return self._velocity_view

  @velocity.setter
  def velocity(self, value):
    """Setter for velocity."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.Velocity, value)

  @property
  def effort(self):
    """
    Effort at the module output; units vary (e.g., N * m for rotational joints and N for linear stages).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    if self._effort_view.size == 0:
      _marshalling.get_group_float(self._refs, enums.CommandFloatField.Effort)
    return self._effort_view

  @effort.setter
  def effort(self, value):
    """Setter for effort."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.Effort, value)

  @property
  def position_kp(self):
    """Proportional PID gain for position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionKp)

  @position_kp.setter
  def position_kp(self, value):
    """Setter for position_kp."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionKp, value)

  @property
  def position_ki(self):
    """Integral PID gain for position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionKi)

  @position_ki.setter
  def position_ki(self, value):
    """Setter for position_ki."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionKi, value)

  @property
  def position_kd(self):
    """Derivative PID gain for position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionKd)

  @position_kd.setter
  def position_kd(self, value):
    """Setter for position_kd."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionKd, value)

  @property
  def position_feed_forward(self):
    """Feed forward term for position (this term is multiplied by the target
    and added to the output).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionFeedForward)

  @position_feed_forward.setter
  def position_feed_forward(self, value):
    """Setter for position_feed_forward."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionFeedForward, value)

  @property
  def position_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionDeadZone)

  @position_dead_zone.setter
  def position_dead_zone(self, value):
    """Setter for position_dead_zone."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionDeadZone, value)

  @property
  def position_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionIClamp)

  @position_i_clamp.setter
  def position_i_clamp(self, value):
    """Setter for position_i_clamp."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionIClamp, value)

  @property
  def position_punch(self):
    """Constant offset to the position PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionPunch)

  @position_punch.setter
  def position_punch(self, value):
    """Setter for position_punch."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionPunch, value)

  @property
  def position_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionMinTarget)

  @position_min_target.setter
  def position_min_target(self, value):
    """Setter for position_min_target."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionMinTarget, value)

  @property
  def position_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionMaxTarget)

  @position_max_target.setter
  def position_max_target(self, value):
    """Setter for position_max_target."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionMaxTarget, value)

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionTargetLowpass)

  @position_target_lowpass.setter
  def position_target_lowpass(self, value):
    """Setter for position_target_lowpass."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionTargetLowpass, value)

  @property
  def position_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionMinOutput)

  @position_min_output.setter
  def position_min_output(self, value):
    """Setter for position_min_output."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionMinOutput, value)

  @property
  def position_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionMaxOutput)

  @position_max_output.setter
  def position_max_output(self, value):
    """Setter for position_max_output."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionMaxOutput, value)

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.PositionOutputLowpass)

  @position_output_lowpass.setter
  def position_output_lowpass(self, value):
    """Setter for position_output_lowpass."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.PositionOutputLowpass, value)

  @property
  def velocity_kp(self):
    """Proportional PID gain for velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityKp)

  @velocity_kp.setter
  def velocity_kp(self, value):
    """Setter for velocity_kp."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityKp, value)

  @property
  def velocity_ki(self):
    """Integral PID gain for velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityKi)

  @velocity_ki.setter
  def velocity_ki(self, value):
    """Setter for velocity_ki."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityKi, value)

  @property
  def velocity_kd(self):
    """Derivative PID gain for velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityKd)

  @velocity_kd.setter
  def velocity_kd(self, value):
    """Setter for velocity_kd."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityKd, value)

  @property
  def velocity_feed_forward(self):
    """Feed forward term for velocity (this term is multiplied by the target
    and added to the output).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityFeedForward)

  @velocity_feed_forward.setter
  def velocity_feed_forward(self, value):
    """Setter for velocity_feed_forward."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityFeedForward, value)

  @property
  def velocity_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityDeadZone)

  @velocity_dead_zone.setter
  def velocity_dead_zone(self, value):
    """Setter for velocity_dead_zone."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityDeadZone, value)

  @property
  def velocity_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityIClamp)

  @velocity_i_clamp.setter
  def velocity_i_clamp(self, value):
    """Setter for velocity_i_clamp."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityIClamp, value)

  @property
  def velocity_punch(self):
    """Constant offset to the velocity PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityPunch)

  @velocity_punch.setter
  def velocity_punch(self, value):
    """Setter for velocity_punch."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityPunch, value)

  @property
  def velocity_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityMinTarget)

  @velocity_min_target.setter
  def velocity_min_target(self, value):
    """Setter for velocity_min_target."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityMinTarget, value)

  @property
  def velocity_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityMaxTarget)

  @velocity_max_target.setter
  def velocity_max_target(self, value):
    """Setter for velocity_max_target."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityMaxTarget, value)

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityTargetLowpass)

  @velocity_target_lowpass.setter
  def velocity_target_lowpass(self, value):
    """Setter for velocity_target_lowpass."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityTargetLowpass, value)

  @property
  def velocity_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityMinOutput)

  @velocity_min_output.setter
  def velocity_min_output(self, value):
    """Setter for velocity_min_output."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityMinOutput, value)

  @property
  def velocity_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityMaxOutput)

  @velocity_max_output.setter
  def velocity_max_output(self, value):
    """Setter for velocity_max_output."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityMaxOutput, value)

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityOutputLowpass)

  @velocity_output_lowpass.setter
  def velocity_output_lowpass(self, value):
    """Setter for velocity_output_lowpass."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityOutputLowpass, value)

  @property
  def effort_kp(self):
    """Proportional PID gain for effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortKp)

  @effort_kp.setter
  def effort_kp(self, value):
    """Setter for effort_kp."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortKp, value)

  @property
  def effort_ki(self):
    """Integral PID gain for effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortKi)

  @effort_ki.setter
  def effort_ki(self, value):
    """Setter for effort_ki."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortKi, value)

  @property
  def effort_kd(self):
    """Derivative PID gain for effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortKd)

  @effort_kd.setter
  def effort_kd(self, value):
    """Setter for effort_kd."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortKd, value)

  @property
  def effort_feed_forward(self):
    """Feed forward term for effort (this term is multiplied by the target and
    added to the output).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortFeedForward)

  @effort_feed_forward.setter
  def effort_feed_forward(self, value):
    """Setter for effort_feed_forward."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortFeedForward, value)

  @property
  def effort_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortDeadZone)

  @effort_dead_zone.setter
  def effort_dead_zone(self, value):
    """Setter for effort_dead_zone."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortDeadZone, value)

  @property
  def effort_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortIClamp)

  @effort_i_clamp.setter
  def effort_i_clamp(self, value):
    """Setter for effort_i_clamp."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortIClamp, value)

  @property
  def effort_punch(self):
    """Constant offset to the effort PID output outside of the deadzone; it is
    added when the error is positive and subtracted when it is negative.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortPunch)

  @effort_punch.setter
  def effort_punch(self, value):
    """Setter for effort_punch."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortPunch, value)

  @property
  def effort_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortMinTarget)

  @effort_min_target.setter
  def effort_min_target(self, value):
    """Setter for effort_min_target."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortMinTarget, value)

  @property
  def effort_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortMaxTarget)

  @effort_max_target.setter
  def effort_max_target(self, value):
    """Setter for effort_max_target."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortMaxTarget, value)

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortTargetLowpass)

  @effort_target_lowpass.setter
  def effort_target_lowpass(self, value):
    """Setter for effort_target_lowpass."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortTargetLowpass, value)

  @property
  def effort_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortMinOutput)

  @effort_min_output.setter
  def effort_min_output(self, value):
    """Setter for effort_min_output."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortMinOutput, value)

  @property
  def effort_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortMaxOutput)

  @effort_max_output.setter
  def effort_max_output(self, value):
    """Setter for effort_max_output."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortMaxOutput, value)

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortOutputLowpass)

  @effort_output_lowpass.setter
  def effort_output_lowpass(self, value):
    """Setter for effort_output_lowpass."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortOutputLowpass, value)

  @property
  def spring_constant(self):
    """The spring constant of the module.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N/m:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.SpringConstant)

  @spring_constant.setter
  def spring_constant(self, value):
    """Setter for spring_constant."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.SpringConstant, value)

  @property
  def reference_position(self):
    """Set the internal encoder reference offset so that the current position
    matches the given reference command.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.ReferencePosition)

  @reference_position.setter
  def reference_position(self, value):
    """Setter for reference_position."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.ReferencePosition, value)

  @property
  def reference_effort(self):
    """Set the internal effort reference offset so that the current effort
    matches the given reference command.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.ReferenceEffort)

  @reference_effort.setter
  def reference_effort(self, value):
    """Setter for reference_effort."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.ReferenceEffort, value)

  @property
  def velocity_limit_min(self):
    """The firmware safety limit for the minimum allowed velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityLimitMin)

  @velocity_limit_min.setter
  def velocity_limit_min(self, value):
    """Setter for velocity_limit_min."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityLimitMin, value)

  @property
  def velocity_limit_max(self):
    """The firmware safety limit for the maximum allowed velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.VelocityLimitMax)

  @velocity_limit_max.setter
  def velocity_limit_max(self, value):
    """Setter for velocity_limit_max."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.VelocityLimitMax, value)

  @property
  def effort_limit_min(self):
    """The firmware safety limit for the minimum allowed effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortLimitMin)

  @effort_limit_min.setter
  def effort_limit_min(self, value):
    """Setter for effort_limit_min."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortLimitMin, value)

  @property
  def effort_limit_max(self):
    """The firmware safety limit for the maximum allowed effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.EffortLimitMax)

  @effort_limit_max.setter
  def effort_limit_max(self, value):
    """Setter for effort_limit_max."""
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.EffortLimitMax, value)

  @property
  def motor_foc_id(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.MotorFocId)

  @motor_foc_id.setter
  def motor_foc_id(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.MotorFocId, value)

  @property
  def motor_foc_iq(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.MotorFocIq)

  @motor_foc_iq.setter
  def motor_foc_iq(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.MotorFocIq, value)

  @property
  def user_settings_float1(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat1)

  @user_settings_float1.setter
  def user_settings_float1(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat1, value)

  @property
  def user_settings_float2(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat2)

  @user_settings_float2.setter
  def user_settings_float2(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat2, value)

  @property
  def user_settings_float3(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat3)

  @user_settings_float3.setter
  def user_settings_float3(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat3, value)

  @property
  def user_settings_float4(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat4)

  @user_settings_float4.setter
  def user_settings_float4(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat4, value)

  @property
  def user_settings_float5(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat5)

  @user_settings_float5.setter
  def user_settings_float5(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat5, value)

  @property
  def user_settings_float6(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat6)

  @user_settings_float6.setter
  def user_settings_float6(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat6, value)

  @property
  def user_settings_float7(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat7)

  @user_settings_float7.setter
  def user_settings_float7(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat7, value)

  @property
  def user_settings_float8(self):
    return _marshalling.get_group_float(self._refs, enums.CommandFloatField.UserSettingsFloat8)

  @user_settings_float8.setter
  def user_settings_float8(self, value: float):
    _marshalling.set_group_command_float(self._refs, enums.CommandFloatField.UserSettingsFloat8, value)

  @property
  def position(self):
    """Position of the module output (post-spring).

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_command_highresangle(self._refs, enums.CommandHighResAngleField.Position)

  @position.setter
  def position(self, value):
    """Setter for position."""
    _marshalling.set_group_command_highresangle(self._refs, enums.CommandHighResAngleField.Position, value)

  @property
  def position_limit_min(self):
    """The firmware safety limit for the minimum allowed position.

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_command_highresangle(self._refs, enums.CommandHighResAngleField.PositionLimitMin)

  @position_limit_min.setter
  def position_limit_min(self, value):
    """Setter for position_limit_min."""
    _marshalling.set_group_command_highresangle(self._refs, enums.CommandHighResAngleField.PositionLimitMin, value)

  @property
  def position_limit_max(self):
    """The firmware safety limit for the maximum allowed position.

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_command_highresangle(self._refs, enums.CommandHighResAngleField.PositionLimitMax)

  @position_limit_max.setter
  def position_limit_max(self, value):
    """Setter for position_limit_max."""
    _marshalling.set_group_command_highresangle(self._refs, enums.CommandHighResAngleField.PositionLimitMax, value)

  @property
  def debug(self):
    """Values for internal debug functions (channel 1-9 available)."""
    return self._debug

  @property
  def position_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.CommandBoolField.PositionDOnError)

  @position_d_on_error.setter
  def position_d_on_error(self, value):
    """Setter for position_d_on_error."""
    _marshalling.set_group_command_bool(self._refs, enums.CommandBoolField.PositionDOnError, value)

  @property
  def velocity_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.CommandBoolField.VelocityDOnError)

  @velocity_d_on_error.setter
  def velocity_d_on_error(self, value):
    """Setter for velocity_d_on_error."""
    _marshalling.set_group_command_bool(self._refs, enums.CommandBoolField.VelocityDOnError, value)

  @property
  def effort_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.CommandBoolField.EffortDOnError)

  @effort_d_on_error.setter
  def effort_d_on_error(self, value):
    """Setter for effort_d_on_error."""
    _marshalling.set_group_command_bool(self._refs, enums.CommandBoolField.EffortDOnError, value)

  @property
  def accel_includes_gravity(self):
    """Whether to include acceleration due to gravity in acceleration feedback.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.CommandBoolField.AccelIncludesGravity)

  @accel_includes_gravity.setter
  def accel_includes_gravity(self, value):
    """Setter for accel_includes_gravity."""
    _marshalling.set_group_command_bool(self._refs, enums.CommandBoolField.AccelIncludesGravity, value)

  @property
  def save_current_settings(self):
    """Indicates if the module should save the current values of all of its
    settings.

    :rtype: numpy.ndarray
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_group_command_flag(self._refs, enums.CommandFlagField.SaveCurrentSettings)

  @save_current_settings.setter
  def save_current_settings(self, value: 'Sequence[bool] | bool | None'):
    """Setter for save_current_settings."""
    _marshalling.set_group_command_flag(self._refs, enums.CommandFlagField.SaveCurrentSettings, value)

  @property
  def reset(self):
    """Restart the module.

    :rtype: numpy.ndarray
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_group_command_flag(self._refs, enums.CommandFlagField.Reset)

  @reset.setter
  def reset(self, value):
    """Setter for reset."""
    _marshalling.set_group_command_flag(self._refs, enums.CommandFlagField.Reset, value)

  @property
  def boot(self):
    """Boot the module from bootloader into application.

    :rtype: numpy.ndarray
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_group_command_flag(self._refs, enums.CommandFlagField.Boot)

  @boot.setter
  def boot(self, value):
    """Setter for boot."""
    _marshalling.set_group_command_flag(self._refs, enums.CommandFlagField.Boot, value)

  @property
  def stop_boot(self):
    """Stop the module from automatically booting into application.

    :rtype: numpy.ndarray
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_group_command_flag(self._refs, enums.CommandFlagField.StopBoot)

  @stop_boot.setter
  def stop_boot(self, value):
    """Setter for stop_boot."""
    _marshalling.set_group_command_flag(self._refs, enums.CommandFlagField.StopBoot, value)

  @property
  def clear_log(self):
    """Clears the log message on the module.

    :rtype: numpy.ndarray
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_group_command_flag(self._refs, enums.CommandFlagField.ClearLog)

  @clear_log.setter
  def clear_log(self, value):
    """Setter for clear_log."""
    _marshalling.set_group_command_flag(self._refs, enums.CommandFlagField.ClearLog, value)

  @property
  def control_strategy(self):
    """How the position, velocity, and effort PID loops are connected in order
    to control motor PWM.

    Possible values include:

      * :code:`Off` (raw value: :code:`0`): The motor is not given power (equivalent to a 0 PWM value)
      * :code:`DirectPWM` (raw value: :code:`1`): A direct PWM value (-1 to 1) can be sent to the motor (subject to onboard safety limiting).
      * :code:`Strategy2` (raw value: :code:`2`): A combination of the position, velocity, and effort loops with P and V feeding to T; documented on docs.hebi.us under "Control Modes"
      * :code:`Strategy3` (raw value: :code:`3`): A combination of the position, velocity, and effort loops with P, V, and T feeding to PWM; documented on docs.hebi.us under "Control Modes"
      * :code:`Strategy4` (raw value: :code:`4`): A combination of the position, velocity, and effort loops with P feeding to T and V feeding to PWM; documented on docs.hebi.us under "Control Modes"

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.CommandEnumField.ControlStrategy)

  @control_strategy.setter
  def control_strategy(self, value):
    """Setter for control_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "Off"
      * "DirectPWM"
      * "Strategy2"
      * "Strategy3"
      * "Strategy4"
    """
    if isinstance(value, (int, str)):
      out = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_control_strategy_str_mappings)
    else:
      out = GroupCommandBase._map_enum_strings_if_needed(value, GroupCommandBase._enum_control_strategy_str_mappings)
    _marshalling.set_group_command_enum(self._refs, enums.CommandEnumField.ControlStrategy, out)

  @property
  def mstop_strategy(self):
    """The motion stop strategy for the actuator.

    Possible values include:

      * :code:`Disabled` (raw value: :code:`0`): Triggering the M-Stop has no effect.
      * :code:`MotorOff` (raw value: :code:`1`): Triggering the M-Stop results in the control strategy being set to 'off'. Remains 'off' until changed by user.
      * :code:`HoldPosition` (raw value: :code:`2`): Triggering the M-Stop results in the motor holding the motor position. Operations resume to normal once trigger is released.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.CommandEnumField.MstopStrategy)

  @mstop_strategy.setter
  def mstop_strategy(self, value):
    """Setter for mstop_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "Disabled"
      * "MotorOff"
      * "HoldPosition"
    """
    if isinstance(value, (int, str)):
      out = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_mstop_strategy_str_mappings)
    else:
      out = GroupCommandBase._map_enum_strings_if_needed(value, GroupCommandBase._enum_mstop_strategy_str_mappings)
    _marshalling.set_group_command_enum(self._refs, enums.CommandEnumField.MstopStrategy, out)

  @property
  def min_position_limit_strategy(self):
    """The position limit strategy (at the minimum position) for the actuator.

    Possible values include:

      * :code:`HoldPosition` (raw value: :code:`0`): Exceeding the position limit results in the actuator holding the position. Needs to be manually set to 'disabled' to recover.
      * :code:`DampedSpring` (raw value: :code:`1`): Exceeding the position limit results in a virtual spring that pushes the actuator back to within the limits.
      * :code:`MotorOff` (raw value: :code:`2`): Exceeding the position limit results in the control strategy being set to 'off'. Remains 'off' until changed by user.
      * :code:`Disabled` (raw value: :code:`3`): Exceeding the position limit has no effect.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.CommandEnumField.MinPositionLimitStrategy)

  @min_position_limit_strategy.setter
  def min_position_limit_strategy(self, value):
    """Setter for min_position_limit_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "HoldPosition"
      * "DampedSpring"
      * "MotorOff"
      * "Disabled"
    """
    if isinstance(value, (int, str)):
      out = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_min_position_limit_strategy_str_mappings)
    else:
      out = GroupCommandBase._map_enum_strings_if_needed(value, GroupCommandBase._enum_min_position_limit_strategy_str_mappings)
    _marshalling.set_group_command_enum(self._refs, enums.CommandEnumField.MinPositionLimitStrategy, out)

  @property
  def max_position_limit_strategy(self):
    """The position limit strategy (at the maximum position) for the actuator.

    Possible values include:

      * :code:`HoldPosition` (raw value: :code:`0`): Exceeding the position limit results in the actuator holding the position. Needs to be manually set to 'disabled' to recover.
      * :code:`DampedSpring` (raw value: :code:`1`): Exceeding the position limit results in a virtual spring that pushes the actuator back to within the limits.
      * :code:`MotorOff` (raw value: :code:`2`): Exceeding the position limit results in the control strategy being set to 'off'. Remains 'off' until changed by user.
      * :code:`Disabled` (raw value: :code:`3`): Exceeding the position limit has no effect.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.CommandEnumField.MaxPositionLimitStrategy)

  @max_position_limit_strategy.setter
  def max_position_limit_strategy(self, value):
    """Setter for max_position_limit_strategy.

    Note that the following (case sensitive) strings can also be used:
      * "HoldPosition"
      * "DampedSpring"
      * "MotorOff"
      * "Disabled"
    """
    if isinstance(value, (int, str)):
      out = GroupCommandBase._map_enum_string_if_needed(value, GroupCommandBase._enum_max_position_limit_strategy_str_mappings)
    else:
      out = GroupCommandBase._map_enum_strings_if_needed(value, GroupCommandBase._enum_max_position_limit_strategy_str_mappings)
    _marshalling.set_group_command_enum(self._refs, enums.CommandEnumField.MaxPositionLimitStrategy, out)

  @property
  def io(self):
    """Interface to the IO pins of the module.

    This field exposes a mutable view of all banks - ``a``, ``b``, ``c``, ``d``, ``e``, ``f`` - which
    all have one or more pins. Each pin has ``int`` and ``float`` values. The two values are not the same
    view into a piece of data and thus can both be set to different values.

    Examples::

      a2 = cmd.io.a.get_int(2)
      e4 = cmd.io.e.get_float(4)
      cmd.io.a.set_int(1, 42)
      cmd.io.e.set_float(4, 13.0)


    :messageType ioBank:
    :messageUnits n/a:
    """
    return self._io

  @property
  def name(self):
    """The name for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: list
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_command_string(self, enums.CommandStringField.Name, [None] * self._number_of_modules)

  @name.setter
  def name(self, value):
    """Setter for name."""
    _marshalling.set_group_command_string(self, enums.CommandStringField.Name, value)

  @property
  def family(self):
    """The family for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: list
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_command_string(self, enums.CommandStringField.Family, [None] * self._number_of_modules)

  @family.setter
  def family(self, value: 'str | None'):
    """Setter for family."""
    _marshalling.set_group_command_string(self, enums.CommandStringField.Family, value)

  @property
  def append_log(self):
    """Appends to the current log message on the module.

    :rtype: list
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_command_string(self, enums.CommandStringField.AppendLog, [None] * self._number_of_modules)

  @append_log.setter
  def append_log(self, value):
    """Setter for append_log."""
    _marshalling.set_group_command_string(self, enums.CommandStringField.AppendLog, value)

  @property
  def led(self):
    """The module's LED.

    You can retrieve or set the LED color through this interface. The underlying object has a field ``color``
    which can be set using an integer or string. For example::

      cmd.led.color = 'red'
      cmd.led.color = 0xFF0000

    The available string colors are

      * red
      * green
      * blue
      * black
      * white
      * cyan
      * magenta
      * yellow
      * transparent

    :messageType led:
    :messageUnits n/a:
    """
    return self._led

  @staticmethod
  def _map_enum_entry(value: str, mapping: 'Mapping[str, int]'):
    if value in mapping:
      return mapping[value]
    else:
      raise ValueError(f"{value} is not a valid value for enum.\nValid values: {mapping.keys()}")

  @staticmethod
  def _map_enum_string_if_needed(value: 'int | str', mapping: 'Mapping[str, int]'):
    if isinstance(value, int):
      return value
    elif isinstance(value, str):
      return GroupCommand._map_enum_entry(value, mapping)

  @staticmethod
  def _map_enum_strings_if_needed(value: 'Sequence[int | str]', mapping: 'Mapping[str, int]') -> 'list[int]':
    ret: 'list[int]' = []
    for val in value:
      if isinstance(val, str):
        ret.append(GroupCommand._map_enum_entry(val, mapping))
      else:
        ret.append(val)
    return ret

  _enum_control_strategy_str_mappings = {
      "Off": 0,
      "DirectPWM": 1,
      "Strategy2": 2,
      "Strategy3": 3,
      "Strategy4": 4,
  }
  _enum_mstop_strategy_str_mappings = {
      "Disabled": 0,
      "MotorOff": 1,
      "HoldPosition": 2,
  }
  _enum_min_position_limit_strategy_str_mappings = {
      "HoldPosition": 0,
      "DampedSpring": 1,
      "MotorOff": 2,
      "Disabled": 3,
  }
  _enum_max_position_limit_strategy_str_mappings = {
      "HoldPosition": 0,
      "DampedSpring": 1,
      "MotorOff": 2,
      "Disabled": 3,
  }


class GroupCommand(GroupCommandBase):
  """Command objects have various fields that can be set; when sent to the
  module, these fields control internal properties and setpoints."""

  __slots__ = ['_commands']

  def _initialize(self, number_of_modules: int):
    super(GroupCommand, self)._initialize(number_of_modules)

    self._commands: 'list[Command]' = []
    for i in range(self._number_of_modules):
      ref = self._refs[i]
      mod = Command(api.hebiGroupCommandGetModuleCommand(self, i), ref)
      self._commands.append(mod)
      api.hebiCommandGetReference(mod, ctypes.byref(ref))

    self._velocity_view = _marshalling.get_group_command_float_view(self._refs, enums.CommandFloatField.Velocity)
    self._effort_view = _marshalling.get_group_command_float_view(self._refs, enums.CommandFloatField.Effort)

  def __init__(self, number_of_modules: int, shared=None):
    if shared:
      if not (isinstance(shared, GroupCommand)):
        raise TypeError('Parameter shared must be a GroupCommand')
      elif number_of_modules != shared.size:
        raise ValueError('Requested number of modules does not match shared parameter')
      super().__init__(existing=shared)
    else:
      super().__init__(internal=api.hebiGroupCommandCreate(number_of_modules), on_delete=api.hebiGroupCommandRelease)
    self._initialize(number_of_modules)

  def __getitem__(self, key: int):
    return self._commands[key]

  @property
  def modules(self):
    return self._commands[:]

  def clear(self):
    """Clears all of the fields."""
    api.hebiGroupCommandClear(self)

  def create_view(self, mask: 'list[int]'):
    """Creates a view into this instance with the indices as specified.

    Note that the created view will hold a strong reference to this object.
    This means that this object will not be destroyed until the created view
    is also destroyed.

    For example::

      # group_command has a size of at least 4
      indices = [0, 1, 2, 3]
      view = group_command.create_view(indices)
      # use view like a GroupCommand object

    :rtype: GroupCommandView
    """
    return GroupCommandView(self, [int(entry) for entry in mask])

  def copy_from(self, src: 'GroupCommand'):
    """Copies all fields from the provided message.

    All fields in the current message are cleared before copied from
    `src`.
    """
    if self._number_of_modules != src._number_of_modules:
      raise ValueError("Number of modules must be equal")
    elif not isinstance(src, GroupCommand):
      raise TypeError("Input must be a GroupCommand instance")
    return api.hebiGroupCommandCopy(self, src) == enums.StatusSuccess

  def read_gains(self, file: str):
    """Import the gains from a file into this object.

    :raises: IOError if the file could not be opened for reading
    """
    from os.path import isfile
    if not isfile(file):
      raise IOError(f'{file} is not a file')

    res = api.hebiGroupCommandReadGains(self, create_str(file))
    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupCommandReadGains failed')

  def write_gains(self, file: str):
    """Export the gains from this object into a file, creating it if
    necessary."""
    res = api.hebiGroupCommandWriteGains(self, create_str(file))
    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupCommandWriteGains failed')

  def read_safety_params(self, file: str):
    """Import the safety params from a file into this object.

    :raises: IOError if the file could not be opened for reading
    """
    from os.path import isfile
    if not isfile(file):
      raise IOError(f'{file} is not a file')

    res = api.hebiGroupCommandReadSafetyParameters(self, create_str(file))
    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupCommandReadSafetyParameters failed')

  def write_safety_params(self, file: str):
    """Export the safety params from this object into a file, creating it if
    necessary."""
    res = api.hebiGroupCommandWriteSafetyParameters(self, create_str(file))
    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupCommandWriteSafetyParameters failed')


class GroupCommandView(GroupCommandBase):
  """A view into a GroupCommand instance.

  This is meant to be used to read and write into a subset of the
  GroupCommand.
  """

  __slots__ = ['_indices', '_modules']

  def __repr__(self):
    return f'GroupCommandView(mask: {self._indices})'

  def _initialize(self, number_of_modules: int, msg: GroupCommandBase, indices: 'list[int]'):
    super()._initialize(number_of_modules)

    for i, entry in enumerate(indices):
      self._refs[i] = msg._refs[entry]

    # check if indices are all adjacent
    adjacent = True
    for i in range(len(indices)-1):
      if indices[i+1] != indices[i] + 1:
        adjacent = False

    if adjacent:
      self._velocity_view = _marshalling.get_group_command_float_view(self._refs, enums.CommandFloatField.Velocity)
      self._effort_view = _marshalling.get_group_command_float_view(self._refs, enums.CommandFloatField.Effort)

  def __init__(self, msg: GroupCommandBase, indices: 'list[int]'):
    super().__init__(existing=msg)
    num_indices = len(indices)
    num_modules = msg.size

    for entry in indices:
      if not entry < num_modules or entry < 0:
        raise ValueError(f"input indices is out of range (expected (0 <= x < {num_modules})")

    all_modules = msg.modules
    self._modules = [all_modules[index] for index in indices]
    self._indices = indices
    self._initialize(num_indices, msg, indices)

  @property
  def modules(self):
    return self._modules[:]

  @property
  def _as_parameter_(self):
    raise TypeError("Attempted to use a GroupCommandView to a ctypes function. Did you mean to use a GroupCommand object instead?")


class GroupFeedbackBase(UnmanagedSharedObject):
  """Base class for feedback.

  Do not use directly.
  """

  __slots__ = [
      '_refs',
      '_number_of_modules',
      '__weakref__',
      '_io',
      '_debug',
      '_led',
      '_velocity_view',
      '_effort_view',
      '_accelerometer_view',
      '_gyro_view',
      '_ar_position_view',
      '_orientation_view',
      '_ar_orientation_view',
  ]

  def _initialize(self, number_of_modules: int):
    self._number_of_modules = number_of_modules
    self._refs = (HebiFeedbackRef * number_of_modules)()

    self._io = GroupFeedbackIoField(self)
    self._debug = GroupFeedbackNumberedFloatField(self, enums.FeedbackNumberedFloatField.Debug)
    self._led = GroupFeedbackLEDField(self, enums.FeedbackLedField.Led)

    self._velocity_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._effort_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)

    self._accelerometer_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._gyro_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._ar_position_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._orientation_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)
    self._ar_orientation_view: 'npt.NDArray[np.float32]' = np.empty(0, dtype=np.float32)

  def __init__(self, internal=None, on_delete=(lambda _: None), existing=None, isdummy=False):
    super().__init__(internal, on_delete, existing, isdummy)

  @property
  def refs(self):
    return (HebiFeedbackRef * self._number_of_modules)(*self._refs)

  @property
  def modules(self) -> 'list[Feedback]':
    raise NotImplementedError()

  @property
  def size(self):
    """The number of modules in this group message."""
    return self._number_of_modules

  @property
  def board_temperature(self):
    """Ambient temperature inside the module (measured at the IMU chip)

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.BoardTemperature)

  @property
  def processor_temperature(self):
    """Temperature of the processor chip.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.ProcessorTemperature)

  @property
  def voltage(self):
    """Bus voltage at which the module is running.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits V:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.Voltage)

  @property
  def velocity(self):
    """Velocity of the module output (post-spring).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    if self._velocity_view.size == 0:
      return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.Velocity)
    return self._velocity_view

  @property
  def effort(self):
    """
    Effort at the module output; units vary (e.g., N * m for rotational joints and N for linear stages).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    if self._effort_view.size == 0:
      return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.Effort)
    return self._effort_view

  @property
  def velocity_command(self):
    """Commanded velocity of the module output (post-spring)

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.VelocityCommand)

  @property
  def effort_command(self):
    """
    Commanded effort at the module output; units vary (e.g., N * m for rotational joints and N for linear stages).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.EffortCommand)

  @property
  def deflection(self):
    """Difference between the pre-spring and post-spring output position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.Deflection)

  @property
  def deflection_velocity(self):
    """Velocity of the difference between the pre-spring and post-spring output
    position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.DeflectionVelocity)

  @property
  def motor_velocity(self):
    """The velocity of the motor shaft.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorVelocity)

  @property
  def motor_current(self):
    """Current supplied to the motor.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits A:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorCurrent)

  @property
  def motor_sensor_temperature(self):
    """The temperature from a sensor near the motor housing.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorSensorTemperature)

  @property
  def motor_winding_current(self):
    """The estimated current in the motor windings.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits A:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorWindingCurrent)

  @property
  def motor_winding_temperature(self):
    """The estimated temperature of the motor windings.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorWindingTemperature)

  @property
  def motor_housing_temperature(self):
    """The estimated temperature of the motor housing.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits C:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorHousingTemperature)

  @property
  def battery_level(self):
    """Charge level of the device's battery (in percent).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.BatteryLevel)

  @property
  def pwm_command(self):
    """Commanded PWM signal sent to the motor; final output of PID controllers.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.PwmCommand)

  @property
  def inner_effort_command(self):
    """In control strategies 2 and 4, this is the torque of force command going
    to the inner torque PID loop.

    :rtype: float
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.InnerEffortCommand)

  @property
  def motor_winding_voltage(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorWindingVoltage)

  @property
  def motor_phase_current_a(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseCurrentA)

  @property
  def motor_phase_current_b(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseCurrentB)

  @property
  def motor_phase_current_c(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseCurrentC)

  @property
  def motor_phase_voltage_a(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseVoltageA)

  @property
  def motor_phase_voltage_b(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseVoltageB)

  @property
  def motor_phase_voltage_c(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseVoltageC)

  @property
  def motor_phase_duty_cycle_a(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseDutyCycleA)

  @property
  def motor_phase_duty_cycle_b(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseDutyCycleB)

  @property
  def motor_phase_duty_cycle_c(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorPhaseDutyCycleC)

  @property
  def motor_foc_id(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorFocId)

  @property
  def motor_foc_iq(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorFocIq)

  @property
  def motor_foc_id_command(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorFocIdCommand)

  @property
  def motor_foc_iq_command(self):
    return _marshalling.get_group_float(self._refs, enums.FeedbackFloatField.MotorFocIqCommand)

  @property
  def position(self):
    """Position of the module output (post-spring).

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_feedback_highresangle(self._refs, enums.FeedbackHighResAngleField.Position)

  @property
  def position_command(self):
    """Commanded position of the module output (post-spring).

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_feedback_highresangle(self._refs, enums.FeedbackHighResAngleField.PositionCommand)

  @property
  def motor_position(self):
    """The position of an actuator's internal motor before the gear reduction.

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_feedback_highresangle(self._refs, enums.FeedbackHighResAngleField.MotorPosition)

  @property
  def debug(self):
    """Values for internal debug functions (channel 1-9 available)."""
    return self._debug

  @property
  def sequence_number(self):
    """Sequence number going to module (local)"""
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.SequenceNumber)

  @property
  def receive_time(self):
    """Timestamp of when message was received from module (local) in seconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits s:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.ReceiveTime) * 1e-6

  @property
  def receive_time_us(self):
    """Timestamp of when message was received from module (local) in
    microseconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.ReceiveTime)

  @property
  def transmit_time(self):
    """Timestamp of when message was transmitted to module (local) in seconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits s:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.TransmitTime) * 1e-6

  @property
  def transmit_time_us(self):
    """Timestamp of when message was transmitted to module (local) in
    microseconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.TransmitTime)

  @property
  def hardware_receive_time(self):
    """Timestamp of when message was received by module (remote) in seconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits s:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.HardwareReceiveTime) * 1e-6

  @property
  def hardware_receive_time_us(self):
    """Timestamp of when message was received by module (remote) in
    microseconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.HardwareReceiveTime)

  @property
  def hardware_transmit_time(self):
    """Timestamp of when message was transmitted from module (remote) in
    seconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits s:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.HardwareTransmitTime) * 1e-6

  @property
  def hardware_transmit_time_us(self):
    """Timestamp of when message was transmitted from module (remote) in
    microseconds.

    :rtype: numpy.ndarray
    :messageType UInt64:
    :messageUnits μs:
    """
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.HardwareTransmitTime)

  @property
  def sender_id(self):
    """Unique ID of the module transmitting this feedback."""
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.SenderId)

  @property
  def rx_sequence_number(self):
    """Rx Sequence number of this feedback."""
    return _marshalling.get_group_uint64(self._refs, enums.FeedbackUInt64Field.RxSequenceNumber)

  @property
  def accelerometer(self):
    """Accelerometer data.

    :rtype: numpy.ndarray
    :messageType vector3f:
    :messageUnits m/s^2:
    """
    if self._accelerometer_view.size == 0:
      return _marshalling.get_group_feedback_vector3f(self._refs, enums.FeedbackVector3fField.Accelerometer)
    return self._accelerometer_view

  @property
  def gyro(self):
    """Gyro data.

    :rtype: numpy.ndarray
    :messageType vector3f:
    :messageUnits rad/s:
    """
    if self._gyro_view.size == 0:
      return _marshalling.get_group_feedback_vector3f(self._refs, enums.FeedbackVector3fField.Gyro)
    return self._gyro_view

  @property
  def ar_position(self):
    """A device's position in the world as calculated from an augmented reality
    framework.

    :rtype: numpy.ndarray
    :messageType vector3f:
    :messageUnits m:
    """
    if self._ar_position_view.size == 0:
      return _marshalling.get_group_feedback_vector3f(self._refs, enums.FeedbackVector3fField.ArPosition)
    return self._ar_position_view

  @property
  def orientation(self):
    """A filtered estimate of the orientation of the module.

    :rtype: numpy.ndarray
    :messageType quaternionf:
    :messageUnits None:
    """
    if self._orientation_view.size == 0:
      return _marshalling.get_group_feedback_vector3f(self._refs, enums.FeedbackQuaternionfField.Orientation)
    return self._orientation_view

  @property
  def ar_orientation(self):
    """A device's orientation in the world as calculated from an augmented
    reality framework.

    :rtype: numpy.ndarray
    :messageType quaternionf:
    :messageUnits None:
    """
    if self._ar_orientation_view.size == 0:
      return _marshalling.get_group_feedback_vector3f(self._refs, enums.FeedbackQuaternionfField.ArOrientation)
    return self._ar_orientation_view

  @property
  def temperature_state(self):
    """Describes how the temperature inside the module is limiting the output
    of the motor.

    Possible values include:

      * :code:`Normal` (raw value: :code:`0`): Temperature within normal range
      * :code:`Critical` (raw value: :code:`1`): Motor output beginning to be limited due to high temperature
      * :code:`ExceedMaxMotor` (raw value: :code:`2`): Temperature exceeds max allowable for motor; motor output disabled
      * :code:`ExceedMaxBoard` (raw value: :code:`3`): Temperature exceeds max allowable for electronics; motor output disabled

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.TemperatureState)

  @property
  def mstop_state(self):
    """Current status of the MStop.

    Possible values include:

      * :code:`Triggered` (raw value: :code:`0`): The MStop is pressed
      * :code:`NotTriggered` (raw value: :code:`1`): The MStop is not pressed

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.MstopState)

  @property
  def position_limit_state(self):
    """Software-controlled bounds on the allowable position of the module; user
    settable.

    Possible values include:

      * :code:`Below` (raw value: :code:`0`): The position of the module was below the lower safety limit; the motor output is set to return the module to within the limits
      * :code:`AtLower` (raw value: :code:`1`): The position of the module was near the lower safety limit, and the motor output is being limited or reversed
      * :code:`Inside` (raw value: :code:`2`): The position of the module was within the safety limits
      * :code:`AtUpper` (raw value: :code:`3`): The position of the module was near the upper safety limit, and the motor output is being limited or reversed
      * :code:`Above` (raw value: :code:`4`): The position of the module was above the upper safety limit; the motor output is set to return the module to within the limits
      * :code:`Uninitialized` (raw value: :code:`5`): The module has not been inside the safety limits since it was booted or the safety limits were set

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.PositionLimitState)

  @property
  def velocity_limit_state(self):
    """Software-controlled bounds on the allowable velocity of the module.

    Possible values include:

      * :code:`Below` (raw value: :code:`0`): The velocity of the module was below the lower safety limit; the motor output is set to return the module to within the limits
      * :code:`AtLower` (raw value: :code:`1`): The velocity of the module was near the lower safety limit, and the motor output is being limited or reversed
      * :code:`Inside` (raw value: :code:`2`): The velocity of the module was within the safety limits
      * :code:`AtUpper` (raw value: :code:`3`): The velocity of the module was near the upper safety limit, and the motor output is being limited or reversed
      * :code:`Above` (raw value: :code:`4`): The velocity of the module was above the upper safety limit; the motor output is set to return the module to within the limits
      * :code:`Uninitialized` (raw value: :code:`5`): The module has not been inside the safety limits since it was booted or the safety limits were set

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.VelocityLimitState)

  @property
  def effort_limit_state(self):
    """Software-controlled bounds on the allowable effort of the module.

    Possible values include:

      * :code:`Below` (raw value: :code:`0`): The effort of the module was below the lower safety limit; the motor output is set to return the module to within the limits
      * :code:`AtLower` (raw value: :code:`1`): The effort of the module was near the lower safety limit, and the motor output is being limited or reversed
      * :code:`Inside` (raw value: :code:`2`): The effort of the module was within the safety limits
      * :code:`AtUpper` (raw value: :code:`3`): The effort of the module was near the upper safety limit, and the motor output is being limited or reversed
      * :code:`Above` (raw value: :code:`4`): The effort of the module was above the upper safety limit; the motor output is set to return the module to within the limits
      * :code:`Uninitialized` (raw value: :code:`5`): The module has not been inside the safety limits since it was booted or the safety limits were set

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.EffortLimitState)

  @property
  def command_lifetime_state(self):
    """The state of the command lifetime safety controller, with respect to the
    current group.

    Possible values include:

      * :code:`Unlocked` (raw value: :code:`0`): There is not command lifetime active on this module
      * :code:`LockedByOther` (raw value: :code:`1`): Commands are locked out due to control from other users
      * :code:`LockedBySender` (raw value: :code:`2`): Commands from others are locked out due to control from this group

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.CommandLifetimeState)

  @property
  def ar_quality(self):
    """The status of the augmented reality tracking, if using an AR enabled
    device. See HebiArQuality for values.

    Possible values include:

      * :code:`ArQualityNotAvailable` (raw value: :code:`0`): Camera position tracking is not available.
      * :code:`ArQualityLimitedUnknown` (raw value: :code:`1`): Tracking is available albeit suboptimal for an unknown reason.
      * :code:`ArQualityLimitedInitializing` (raw value: :code:`2`): The AR session has not yet gathered enough camera or motion data to provide tracking information.
      * :code:`ArQualityLimitedRelocalizing` (raw value: :code:`3`): The AR session is attempting to resume after an interruption.
      * :code:`ArQualityLimitedExcessiveMotion` (raw value: :code:`4`): The device is moving too fast for accurate image-based position tracking.
      * :code:`ArQualityLimitedInsufficientFeatures` (raw value: :code:`5`): The scene visible to the camera does not contain enough distinguishable features for image-based position tracking.
      * :code:`ArQualityNormal` (raw value: :code:`6`): Camera position tracking is providing optimal results.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.ArQuality)

  @property
  def motor_hall_state(self):
    """The status of the motor driver hall sensor.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.FeedbackEnumField.MotorHallState)

  @property
  def io(self):
    """Interface to the IO pins of the module.

    This field exposes a read-only view of all banks - ``a``, ``b``, ``c``, ``d``, ``e``, ``f`` - which
    all have one or more pins. Each pin has ``int`` and ``float`` values. The two values are not the same
    view into a piece of data and thus can both be set to different values.

    Examples::

      a2 = fbk.io.a.get_int(2)
      e4 = fbk.io.e.get_float(4)


    :messageType ioBank:
    :messageUnits n/a:
    """
    return self._io

  @property
  def led(self):
    """The module's LED.

    :messageType led:
    :messageUnits n/a:
    """
    return self._led


class GroupFeedback(GroupFeedbackBase):
  """Feedback objects have various fields representing feedback from modules;
  which fields are populated depends on the module type and various other
  settings."""

  __slots__ = ['_feedbacks']

  def _initialize(self, number_of_modules: int):
    super(GroupFeedback, self)._initialize(number_of_modules)

    self._feedbacks: 'list[Feedback]' = []
    for i in range(self._number_of_modules):
      ref = self._refs[i]
      mod = Feedback(api.hebiGroupFeedbackGetModuleFeedback(self, i), ref)
      self._feedbacks.append(mod)
      api.hebiFeedbackGetReference(mod, ctypes.byref(ref))

    self._velocity_view = _marshalling.get_group_feedback_float_view(self._refs, enums.FeedbackFloatField.Velocity)
    self._effort_view = _marshalling.get_group_feedback_float_view(self._refs, enums.FeedbackFloatField.Effort)

    self._accelerometer_view = _marshalling.get_group_feedback_vector3f_view(self._refs, enums.FeedbackVector3fField.Accelerometer)
    self._gyro_view = _marshalling.get_group_feedback_vector3f_view(self._refs, enums.FeedbackVector3fField.Gyro)
    self._ar_position_view = _marshalling.get_group_feedback_vector3f_view(self._refs, enums.FeedbackVector3fField.ArPosition)

    self._orientation_view = _marshalling.get_group_feedback_quaternionf_view(self._refs, enums.FeedbackQuaternionfField.Orientation)
    self._ar_orientation_view = _marshalling.get_group_feedback_quaternionf_view(self._refs, enums.FeedbackQuaternionfField.ArOrientation)

    #self._io.setup_bank_views()

  def __init__(self, number_of_modules: int, shared=None):
    if shared:
      if not (isinstance(shared, GroupFeedback)):
        raise TypeError('Parameter shared must be a GroupFeedback')
      elif number_of_modules != shared.size:
        raise ValueError('Requested number of modules does not match shared parameter')
      super().__init__(existing=shared)
    else:
      super().__init__(internal=api.hebiGroupFeedbackCreate(number_of_modules), on_delete=api.hebiGroupFeedbackRelease)
    self._initialize(number_of_modules)

  def __getitem__(self, key: int):
    return self._feedbacks[key]

  def clear(self):
    """Clears all of the fields."""
    api.hebiGroupFeedbackClear(self)

  def create_view(self, mask: 'Sequence[int]'):
    """Creates a view into this instance with the indices as specified.

    Note that the created view will hold a strong reference to this object.
    This means that this object will not be destroyed until the created view
    is also destroyed.

    For example::

      # group_feedback has a size of at least 4
      indices = [0, 1, 2, 3]
      view = group_feedback.create_view(indices)
      # use view like a GroupFeedback object

    :rtype: GroupFeedbackView
    """
    return GroupFeedbackView(self, [int(entry) for entry in mask])

  def copy_from(self, src: 'GroupFeedback'):
    """Copies all fields from the provided message.

    All fields in the current message are cleared before copied from
    `src`.
    """
    if self._number_of_modules != src._number_of_modules:
      raise ValueError("Number of modules must be equal")
    elif not isinstance(src, GroupFeedback):
      raise TypeError("Input must be a GroupFeedback instance")
    return api.hebiGroupFeedbackCopy(self, src) == enums.StatusSuccess

  def get_position(self, array: 'npt.NDArray[np.float64]'):
    """Convenience method to get positions into an existing array. The input
    must be a numpy object with dtype compatible with ``numpy.float64``.

    :param array: a numpy array or matrix with size matching the
                  number of modules in this group message
    :type array:  numpy.ndarray
    """
    if array.size != self._number_of_modules:
      raise ValueError('Input array must be the size of the group feedback')
    _marshalling.get_group_feedback_highresangle_into(self._refs, enums.FeedbackHighResAngleField.Position, array)

  def get_position_command(self, array: 'npt.NDArray[np.float64]'):
    """Convenience method to get position commands into an existing array. The
    input must be a numpy object with dtype compatible with ``numpy.float64``.

    :param array: a numpy array or matrix with size matching the
                  number of modules in this group message
    :type array:  numpy.ndarray
    """
    if array.size != self._number_of_modules:
      raise ValueError('Input array must be the size of the group feedback')
    _marshalling.get_group_feedback_highresangle_into(self._refs, enums.FeedbackHighResAngleField.PositionCommand, array)

  def get_velocity(self, array: 'npt.NDArray[np.float32]'):
    """Convenience method to get velocities into an existing array. The input
    must be a numpy object with dtype compatible with ``numpy.float32``.

    :param array: a numpy array or matrix with size matching the
                  number of modules in this group message
    :type array:  numpy.ndarray
    """
    if array.size != self._number_of_modules:
      raise ValueError('Input array must be the size of the group feedback')
    _marshalling.get_group_float_into(self._refs, enums.FeedbackFloatField.Velocity, array)

  def get_velocity_command(self, array: 'npt.NDArray[np.float32]'):
    """Convenience method to get velocity commands into an existing array. The
    input must be a numpy object with dtype compatible with ``numpy.float32``.

    :param array: a numpy array or matrix with size matching the
                  number of modules in this group message
    :type array:  numpy.ndarray
    """
    if array.size != self._number_of_modules:
      raise ValueError('Input array must be the size of the group feedback')
    _marshalling.get_group_float_into(self._refs, enums.FeedbackFloatField.VelocityCommand, array)

  def get_effort(self, array: 'npt.NDArray[np.float32]'):
    """Convenience method to get efforts into an existing array. The input must
    be a numpy object with dtype compatible with ``numpy.float32``.

    :param array: a numpy array or matrix with size matching the
                  number of modules in this group message
    :type array:  numpy.ndarray
    """
    if array.size != self._number_of_modules:
      raise ValueError('Input array must be the size of the group feedback')
    _marshalling.get_group_float_into(self._refs, enums.FeedbackFloatField.Effort, array)

  def get_effort_command(self, array: 'npt.NDArray[np.float32]'):
    """Convenience method to get effort commands into an existing array. The
    input must be a numpy object with dtype compatible with ``numpy.float32``.

    :param array: a numpy array or matrix with size matching the
                  number of modules in this group message
    :type array:  numpy.ndarray
    """
    if array.size != self._number_of_modules:
      raise ValueError('Input array must be the size of the group feedback')
    _marshalling.get_group_float_into(self._refs, enums.FeedbackFloatField.EffortCommand, array)

  @property
  def modules(self):
    return self._feedbacks[:]


class GroupFeedbackView(GroupFeedbackBase):
  """A view into a GroupFeedback instance.

  This is meant to be used to read into a subset of the GroupFeedback.
  """

  __slots__ = ['_indices', '_modules']

  def __repr__(self):
    return f'GroupFeedbackView(mask: {self._indices})'

  def _initialize(self, number_of_modules: int, msg: GroupFeedback, indices: 'Sequence[int]'):
    super()._initialize(number_of_modules)

    for i, entry in enumerate(indices):
      self._refs[i] = msg._refs[entry]

    # check if indices are all adjacent
    adjacent = True
    for i in range(len(indices)-1):
      if indices[i+1] != indices[i] + 1:
        adjacent = False

    if adjacent:
      self._velocity_view = _marshalling.get_group_feedback_float_view(self._refs, enums.FeedbackFloatField.Velocity)
      self._effort_view = _marshalling.get_group_feedback_float_view(self._refs, enums.FeedbackFloatField.Effort)

      self._accelerometer_view = _marshalling.get_group_feedback_vector3f_view(self._refs, enums.FeedbackVector3fField.Accelerometer)
      self._gyro_view = _marshalling.get_group_feedback_vector3f_view(self._refs, enums.FeedbackVector3fField.Gyro)
      self._ar_position_view = _marshalling.get_group_feedback_vector3f_view(self._refs, enums.FeedbackVector3fField.ArPosition)

      self._orientation_view = _marshalling.get_group_feedback_quaternionf_view(self._refs, enums.FeedbackQuaternionfField.Orientation)
      self._ar_orientation_view = _marshalling.get_group_feedback_quaternionf_view(self._refs, enums.FeedbackQuaternionfField.ArOrientation)

  def __init__(self, msg: GroupFeedback, indices: 'Sequence[int]'):
    super().__init__(existing=msg)
    num_indices = len(indices)
    num_modules = msg.size

    for entry in indices:
      if not entry < num_modules or entry < 0:
        raise ValueError(f"input indices is out of range (expected (0 <= x < {num_modules})")

    all_modules = msg.modules
    self._modules = [all_modules[index] for index in indices]
    self._indices = indices
    self._initialize(num_indices, msg, indices)

  @property
  def modules(self):
    return self._modules[:]

  @property
  def _as_parameter_(self):
    raise TypeError("Attempted to use a GroupFeedbackView to a ctypes function. Did you mean to use a GroupFeedback object instead?")


class GroupInfoBase(UnmanagedSharedObject):
  """Base class for info.

  Do not use directly.
  """

  __slots__ = ['_refs', '_number_of_modules', '__weakref__', '_io', '_led']

  def _initialize(self, number_of_modules: int):
    self._number_of_modules = number_of_modules
    from hebi._internal.ffi.ctypes_defs import HebiInfoRef
    self._refs = (HebiInfoRef * number_of_modules)()

    self._io = GroupInfoIoField(self)
    self._led = GroupFeedbackLEDField(self, enums.InfoLedField.Led)

  def __init__(self, internal=None, on_delete=(lambda _: None), existing=None, isdummy=False):
    super().__init__(internal, on_delete, existing, isdummy)

  @property
  def refs(self):
    return (ctypes_defs.HebiInfoRef * self._number_of_modules)(*self._refs)

  @property
  def modules(self) -> 'list[Info]':
    raise NotImplementedError()

  @property
  def size(self):
    """The number of modules in this group message."""
    return self._number_of_modules

  @property
  def position_kp(self):
    """Proportional PID gain for position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionKp)

  @property
  def position_ki(self):
    """Integral PID gain for position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionKi)

  @property
  def position_kd(self):
    """Derivative PID gain for position.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionKd)

  @property
  def position_feed_forward(self):
    """Feed forward term for position (this term is multiplied by the target
    and added to the output).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionFeedForward)

  @property
  def position_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionDeadZone)

  @property
  def position_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionIClamp)

  @property
  def position_punch(self):
    """Constant offset to the position PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionPunch)

  @property
  def position_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionMinTarget)

  @property
  def position_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionMaxTarget)

  @property
  def position_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionTargetLowpass)

  @property
  def position_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionMinOutput)

  @property
  def position_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionMaxOutput)

  @property
  def position_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.PositionOutputLowpass)

  @property
  def velocity_kp(self):
    """Proportional PID gain for velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityKp)

  @property
  def velocity_ki(self):
    """Integral PID gain for velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityKi)

  @property
  def velocity_kd(self):
    """Derivative PID gain for velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityKd)

  @property
  def velocity_feed_forward(self):
    """Feed forward term for velocity (this term is multiplied by the target
    and added to the output).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityFeedForward)

  @property
  def velocity_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityDeadZone)

  @property
  def velocity_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityIClamp)

  @property
  def velocity_punch(self):
    """Constant offset to the velocity PID output outside of the deadzone; it
    is added when the error is positive and subtracted when it is negative.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityPunch)

  @property
  def velocity_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityMinTarget)

  @property
  def velocity_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityMaxTarget)

  @property
  def velocity_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityTargetLowpass)

  @property
  def velocity_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityMinOutput)

  @property
  def velocity_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityMaxOutput)

  @property
  def velocity_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityOutputLowpass)

  @property
  def effort_kp(self):
    """Proportional PID gain for effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortKp)

  @property
  def effort_ki(self):
    """Integral PID gain for effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortKi)

  @property
  def effort_kd(self):
    """Derivative PID gain for effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortKd)

  @property
  def effort_feed_forward(self):
    """Feed forward term for effort (this term is multiplied by the target and
    added to the output).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortFeedForward)

  @property
  def effort_dead_zone(self):
    """Error values within +/- this value from zero are treated as zero (in
    terms of computed proportional output, input to numerical derivative, and
    accumulated integral error).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortDeadZone)

  @property
  def effort_i_clamp(self):
    """Maximum allowed value for the output of the integral component of the
    PID loop; the integrated error is not allowed to exceed value that will
    generate this number.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortIClamp)

  @property
  def effort_punch(self):
    """Constant offset to the effort PID output outside of the deadzone; it is
    added when the error is positive and subtracted when it is negative.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortPunch)

  @property
  def effort_min_target(self):
    """Minimum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortMinTarget)

  @property
  def effort_max_target(self):
    """Maximum allowed value for input to the PID controller.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortMaxTarget)

  @property
  def effort_target_lowpass(self):
    """
    A simple lowpass filter applied to the target set point; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortTargetLowpass)

  @property
  def effort_min_output(self):
    """Output from the PID controller is limited to a minimum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortMinOutput)

  @property
  def effort_max_output(self):
    """Output from the PID controller is limited to a maximum of this value.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortMaxOutput)

  @property
  def effort_output_lowpass(self):
    """
    A simple lowpass filter applied to the controller output; needs to be between 0 and 1. At each timestep: x_t = x_t * a + x_{t-1} * (1 - a).

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortOutputLowpass)

  @property
  def spring_constant(self):
    """The spring constant of the module.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N/m:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.SpringConstant)

  @property
  def velocity_limit_min(self):
    """The firmware safety limit for the minimum allowed velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityLimitMin)

  @property
  def velocity_limit_max(self):
    """The firmware safety limit for the maximum allowed velocity.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits rad/s:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.VelocityLimitMax)

  @property
  def effort_limit_min(self):
    """The firmware safety limit for the minimum allowed effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortLimitMin)

  @property
  def effort_limit_max(self):
    """The firmware safety limit for the maximum allowed effort.

    :rtype: numpy.ndarray
    :messageType float:
    :messageUnits N*m:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.EffortLimitMax)

  @property
  def position_limit_min(self):
    """The firmware safety limit for the minimum allowed position.

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_info_highresangle(self._refs, enums.InfoHighResAngleField.PositionLimitMin)

  @property
  def position_limit_max(self):
    """The firmware safety limit for the maximum allowed position.

    :rtype: numpy.ndarray
    :messageType highResAngle:
    :messageUnits rad:
    """
    return _marshalling.get_group_info_highresangle(self._refs, enums.InfoHighResAngleField.PositionLimitMax)

  @property
  def position_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.InfoBoolField.PositionDOnError)

  @property
  def velocity_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.InfoBoolField.VelocityDOnError)

  @property
  def effort_d_on_error(self):
    """Controls whether the Kd term uses the "derivative of error" or
    "derivative of measurement." When the setpoints have step inputs or are
    noisy, setting this to @c false can eliminate corresponding spikes or noise
    in the output.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.InfoBoolField.EffortDOnError)

  @property
  def accel_includes_gravity(self):
    """Whether to include acceleration due to gravity in acceleration feedback.

    :rtype: numpy.ndarray
    :messageType bool:
    :messageUnits None:
    """
    return _marshalling.get_group_bool(self._refs, enums.InfoBoolField.AccelIncludesGravity)

  @property
  def save_current_settings(self):
    """Indicates if the module should save the current values of all of its
    settings.

    :rtype: numpy.ndarray
    :messageType flag:
    :messageUnits None:
    """
    return _marshalling.get_group_info_flag(self._refs, enums.InfoFlagField.SaveCurrentSettings)

  @property
  def control_strategy(self):
    """How the position, velocity, and effort PID loops are connected in order
    to control motor PWM.

    Possible values include:

      * :code:`Off` (raw value: :code:`0`): The motor is not given power (equivalent to a 0 PWM value)
      * :code:`DirectPWM` (raw value: :code:`1`): A direct PWM value (-1 to 1) can be sent to the motor (subject to onboard safety limiting).
      * :code:`Strategy2` (raw value: :code:`2`): A combination of the position, velocity, and effort loops with P and V feeding to T; documented on docs.hebi.us under "Control Modes"
      * :code:`Strategy3` (raw value: :code:`3`): A combination of the position, velocity, and effort loops with P, V, and T feeding to PWM; documented on docs.hebi.us under "Control Modes"
      * :code:`Strategy4` (raw value: :code:`4`): A combination of the position, velocity, and effort loops with P feeding to T and V feeding to PWM; documented on docs.hebi.us under "Control Modes"

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.InfoEnumField.ControlStrategy)

  @property
  def calibration_state(self):
    """The calibration state of the module.

    Possible values include:

      * :code:`Normal` (raw value: :code:`0`): The module has been calibrated; this is the normal state
      * :code:`UncalibratedCurrent` (raw value: :code:`1`): The current has not been calibrated
      * :code:`UncalibratedPosition` (raw value: :code:`2`): The factory zero position has not been set
      * :code:`UncalibratedEffort` (raw value: :code:`3`): The effort (e.g., spring nonlinearity) has not been calibrated

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.InfoEnumField.CalibrationState)

  @property
  def mstop_strategy(self):
    """The motion stop strategy for the actuator.

    Possible values include:

      * :code:`Disabled` (raw value: :code:`0`): Triggering the M-Stop has no effect.
      * :code:`MotorOff` (raw value: :code:`1`): Triggering the M-Stop results in the control strategy being set to 'off'. Remains 'off' until changed by user.
      * :code:`HoldPosition` (raw value: :code:`2`): Triggering the M-Stop results in the motor holding the motor position. Operations resume to normal once trigger is released.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.InfoEnumField.MstopStrategy)

  @property
  def min_position_limit_strategy(self):
    """The position limit strategy (at the minimum position) for the actuator.

    Possible values include:

      * :code:`HoldPosition` (raw value: :code:`0`): Exceeding the position limit results in the actuator holding the position. Needs to be manually set to 'disabled' to recover.
      * :code:`DampedSpring` (raw value: :code:`1`): Exceeding the position limit results in a virtual spring that pushes the actuator back to within the limits.
      * :code:`MotorOff` (raw value: :code:`2`): Exceeding the position limit results in the control strategy being set to 'off'. Remains 'off' until changed by user.
      * :code:`Disabled` (raw value: :code:`3`): Exceeding the position limit has no effect.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.InfoEnumField.MinPositionLimitStrategy)

  @property
  def max_position_limit_strategy(self):
    """The position limit strategy (at the maximum position) for the actuator.

    Possible values include:

      * :code:`HoldPosition` (raw value: :code:`0`): Exceeding the position limit results in the actuator holding the position. Needs to be manually set to 'disabled' to recover.
      * :code:`DampedSpring` (raw value: :code:`1`): Exceeding the position limit results in a virtual spring that pushes the actuator back to within the limits.
      * :code:`MotorOff` (raw value: :code:`2`): Exceeding the position limit results in the control strategy being set to 'off'. Remains 'off' until changed by user.
      * :code:`Disabled` (raw value: :code:`3`): Exceeding the position limit has no effect.

    :rtype: numpy.ndarray
    :messageType enum:
    :messageUnits None:
    """
    return _marshalling.get_group_enum(self._refs, enums.InfoEnumField.MaxPositionLimitStrategy)

  @property
  def io(self):
    """Interface to the IO pins of the module.  This is used to identify labels
    on Mobile IO devices.

    This field exposes a mutable view of all banks - ``a``, ``b``, ``c``, ``d``, ``e``, ``f`` - which
    all have one or more pins. Each pin has a ``label`` value.

    Examples::

      a2 = cmd.io.a.get_label(2)

    :messageType ioBank:
    :messageUnits n/a:
    """
    return self._io

  @property
  def name(self):
    """The name for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: list
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.Name, [None] * self._number_of_modules)

  @property
  def family(self):
    """The family for this module. The string must be null-terminated and less
    than 21 characters.

    :rtype: list
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.Family, [None] * self._number_of_modules)

  @property
  def serial(self):
    """Gets the serial number for this module (e.g., X5-0001).

    :rtype: list
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.Serial, [None] * self._number_of_modules)

  @property
  def ip_address(self):
    raw_value = _marshalling.get_group_uint64(self._refs, enums.InfoUInt64Field.IpAddress)
    ip2str = lambda rv: socket.inet_ntoa(struct.pack("!I", rv))
    return np.array([ip2str(ip) for ip in raw_value])

  @property
  def subnet_mask(self):
    raw_value = _marshalling.get_group_uint64(self._refs, enums.InfoUInt64Field.SubnetMask)
    ip2str = lambda rv: socket.inet_ntoa(struct.pack("!I", rv))
    return np.array([ip2str(ip) for ip in raw_value])

  @property
  def default_gateway(self):
    raw_value = _marshalling.get_group_uint64(self._refs, enums.InfoUInt64Field.DefaultGateway)
    ip2str = lambda rv: socket.inet_ntoa(struct.pack("!I", rv))
    return np.array([ip2str(ip) for ip in raw_value])

  @property
  def electrical_type(self):
    """Gets the electrical type for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.ElectricalType, [None] * self._number_of_modules)

  @property
  def electrical_revision(self):
    """Gets the electrical revision for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.ElectricalRevision, [None] * self._number_of_modules)

  @property
  def mechanical_type(self):
    """Gets the mechanical type for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.MechanicalType, [None] * self._number_of_modules)

  @property
  def mechanical_revision(self):
    """Gets the mechanical revision for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.MechanicalRevision, [None] * self._number_of_modules)

  @property
  def firmware_type(self):
    """Gets the firmware type for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.FirmwareType, [None] * self._number_of_modules)

  @property
  def firmware_revision(self):
    """Gets the firmware revision for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.FirmwareRevision, [None] * self._number_of_modules)

  @property
  def user_settings_float1(self):
    """Gets the user setting (float1) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat1)

  @property
  def user_settings_float2(self):
    """Gets the user setting (float2) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat2)

  @property
  def user_settings_float3(self):
    """Gets the user setting (float3) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat3)

  @property
  def user_settings_float4(self):
    """Gets the user setting (float4) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat4)

  @property
  def user_settings_float5(self):
    """Gets the user setting (float5) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat5)

  @property
  def user_settings_float6(self):
    """Gets the user setting (float6) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat6)

  @property
  def user_settings_float7(self):
    """Gets the user setting (float7) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat7)

  @property
  def user_settings_float8(self):
    """Gets the user setting (float8) for this module.

    :rtype: float
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_float(self._refs, enums.InfoFloatField.UserSettingsFloat8)

  @property
  def user_settings_bytes1(self):
    """Gets the user setting (float1) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes1, [None] * self._number_of_modules)

  @property
  def user_settings_bytes2(self):
    """Gets the user setting (float2) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes2, [None] * self._number_of_modules)

  @property
  def user_settings_bytes3(self):
    """Gets the user setting (float3) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes3, [None] * self._number_of_modules)

  @property
  def user_settings_bytes4(self):
    """Gets the user setting (float4) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes4, [None] * self._number_of_modules)

  @property
  def user_settings_bytes5(self):
    """Gets the user setting (float5) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes5, [None] * self._number_of_modules)

  @property
  def user_settings_bytes6(self):
    """Gets the user setting (float6) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes6, [None] * self._number_of_modules)

  @property
  def user_settings_bytes7(self):
    """Gets the user setting (float7) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes7, [None] * self._number_of_modules)

  @property
  def user_settings_bytes8(self):
    """Gets the user setting (float8) for this module.

    :rtype: str
    :messageType string:
    :messageUnits None:
    """
    return _marshalling.get_group_info_string(self, enums.InfoStringField.UserSettingsBytes8, [None] * self._number_of_modules)

  @property
  def led(self):
    """The module's LED.

    :messageType led:
    :messageUnits n/a:
    """
    return self._led


class GroupInfo(GroupInfoBase):
  """Info objects have various fields representing the module state; which
  fields are populated depends on the module type and various other
  settings."""

  __slots__ = ['_infos']

  def _initialize(self, number_of_modules: int):
    super(GroupInfo, self)._initialize(number_of_modules)

    self._infos: 'list[Info]' = []
    for i in range(self._number_of_modules):
      ref = self._refs[i]
      mod = Info(api.hebiGroupInfoGetModuleInfo(self, i), ref)
      self._infos.append(mod)
      api.hebiInfoGetReference(mod, ctypes.byref(ref))

  def __init__(self, number_of_modules: int, shared=None):
    if shared:
      if not (isinstance(shared, GroupInfo)):
        raise TypeError('Parameter shared must be a GroupInfo')
      elif number_of_modules != shared.size:
        raise ValueError('Requested number of modules does not match shared parameter')
      super().__init__(existing=shared)
    else:
      super().__init__(internal=api.hebiGroupInfoCreate(number_of_modules), on_delete=api.hebiGroupInfoRelease)
    self._initialize(number_of_modules)

  def __getitem__(self, key: int):
    return self._infos[key]

  def copy_from(self, src: 'GroupInfo'):
    """Copies all fields from the provided message.

    All fields in the current message are cleared before copied from
    `src`.
    """
    if self._number_of_modules != src._number_of_modules:
      raise ValueError("Number of modules must be equal")
    elif not isinstance(src, GroupInfo):
      raise TypeError("Input must be a GroupInfo instance")
    return api.hebiGroupInfoCopy(self, src) == enums.StatusSuccess

  def write_gains(self, file: str):
    """Export the gains from this object into a file, creating it if
    necessary."""
    res = api.hebiGroupInfoWriteGains(self, create_str(file))
    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupInfoWriteGains failed')

  def write_safety_params(self, file):
    """Export the safety params from this object into a file, creating it if
    necessary."""
    res = api.hebiGroupInfoWriteSafetyParameters(self, create_str(file))
    if res != enums.StatusSuccess:
      from hebi._internal.errors import HEBI_Exception
      raise HEBI_Exception(res, 'hebiGroupInfoWriteSafetyParameters failed')

  @property
  def modules(self):
    return self._infos[:]
