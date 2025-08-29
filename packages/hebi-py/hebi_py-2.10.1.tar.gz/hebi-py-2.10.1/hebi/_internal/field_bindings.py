# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2017-2019 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

from .ffi import enums as _enums
from .ffi.wrappers import FieldDetails

import typing
if typing.TYPE_CHECKING:
  from .ffi.wrappers import NumberedFieldDetails


_feedback_scalars = [
    _enums.FeedbackFloatField.BoardTemperature,
    _enums.FeedbackFloatField.ProcessorTemperature,
    _enums.FeedbackFloatField.Voltage,
    _enums.FeedbackFloatField.Velocity,
    _enums.FeedbackFloatField.Effort,
    _enums.FeedbackFloatField.VelocityCommand,
    _enums.FeedbackFloatField.EffortCommand,
    _enums.FeedbackFloatField.Deflection,
    _enums.FeedbackFloatField.DeflectionVelocity,
    _enums.FeedbackFloatField.MotorVelocity,
    _enums.FeedbackFloatField.MotorCurrent,
    _enums.FeedbackFloatField.MotorSensorTemperature,
    _enums.FeedbackFloatField.MotorWindingCurrent,
    _enums.FeedbackFloatField.MotorWindingTemperature,
    _enums.FeedbackFloatField.MotorHousingTemperature,
    _enums.FeedbackFloatField.BatteryLevel,
    _enums.FeedbackFloatField.PwmCommand,
    _enums.FeedbackHighResAngleField.Position,
    _enums.FeedbackHighResAngleField.PositionCommand,
    _enums.FeedbackHighResAngleField.MotorPosition,
    _enums.FeedbackUInt64Field.SequenceNumber,
    _enums.FeedbackUInt64Field.ReceiveTime,
    _enums.FeedbackUInt64Field.TransmitTime,
    _enums.FeedbackUInt64Field.HardwareReceiveTime,
    _enums.FeedbackUInt64Field.HardwareTransmitTime,
    _enums.FeedbackUInt64Field.SenderId,
    _enums.FeedbackEnumField.TemperatureState,
    _enums.FeedbackEnumField.MstopState,
    _enums.FeedbackEnumField.PositionLimitState,
    _enums.FeedbackEnumField.VelocityLimitState,
    _enums.FeedbackEnumField.EffortLimitState,
    _enums.FeedbackEnumField.CommandLifetimeState,
    _enums.FeedbackEnumField.ArQuality,
    _enums.FeedbackIoBankField.A,
    _enums.FeedbackIoBankField.B,
    _enums.FeedbackIoBankField.C,
    _enums.FeedbackIoBankField.D,
    _enums.FeedbackIoBankField.E,
    _enums.FeedbackIoBankField.F]


_feedback_scalars_map: 'dict[str, FieldDetails | NumberedFieldDetails.Subfield]' = {}


def __add_fbk_scalars_field(field: 'FieldDetails | NumberedFieldDetails.Subfield'):
  for alias in field.aliases:
    _feedback_scalars_map[alias] = field


def __populate_fbk_scalars_map():
  for entry in _feedback_scalars:

    field = entry.field_details

    if field is None:
      # TODO: THIS IS TEMPORARY. FIX THIS BY DEFINING FIELD_DETAILS FOR ALL FIELDS ABOVE
      continue

    if isinstance(field, FieldDetails):
      # Will be an instance of `MessageEnum`
      __add_fbk_scalars_field(field)
    else:
      for sub_field in field.scalars.values():
        # Unspecified class type: will have all functionality of `MessageEnum`
        __add_fbk_scalars_field(sub_field)


__populate_fbk_scalars_map()


def get_field_info(field_name: str):
  """Get the info object representing the given field name.

  The field binder is a lambda which accepts a group feedback instance and returns the input field name

  :param field_name:
  :return:
  """
  if field_name not in _feedback_scalars_map:
    raise KeyError(field_name)

  return _feedback_scalars_map[field_name]
