# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2022 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

from .wrappers import FieldDetails, MessageEnum

# CommandFloatField
class CommandFloatField(MessageEnum):
    Velocity = (0, FieldDetails('rad/s', 'velocity'))
    Effort = (1, FieldDetails('N*m', 'effort'))
    PositionKp = (2, FieldDetails('None', 'position_kp'))
    PositionKi = (3, FieldDetails('None', 'position_ki'))
    PositionKd = (4, FieldDetails('None', 'position_kd'))
    PositionFeedForward = (5, FieldDetails('None', 'position_feed_forward'))
    PositionDeadZone = (6, FieldDetails('None', 'position_dead_zone'))
    PositionIClamp = (7, FieldDetails('None', 'position_i_clamp'))
    PositionPunch = (8, FieldDetails('None', 'position_punch'))
    PositionMinTarget = (9, FieldDetails('None', 'position_min_target'))
    PositionMaxTarget = (10, FieldDetails('None', 'position_max_target'))
    PositionTargetLowpass = (11, FieldDetails('None', 'position_target_lowpass'))
    PositionMinOutput = (12, FieldDetails('None', 'position_min_output'))
    PositionMaxOutput = (13, FieldDetails('None', 'position_max_output'))
    PositionOutputLowpass = (14, FieldDetails('None', 'position_output_lowpass'))
    VelocityKp = (15, FieldDetails('None', 'velocity_kp'))
    VelocityKi = (16, FieldDetails('None', 'velocity_ki'))
    VelocityKd = (17, FieldDetails('None', 'velocity_kd'))
    VelocityFeedForward = (18, FieldDetails('None', 'velocity_feed_forward'))
    VelocityDeadZone = (19, FieldDetails('None', 'velocity_dead_zone'))
    VelocityIClamp = (20, FieldDetails('None', 'velocity_i_clamp'))
    VelocityPunch = (21, FieldDetails('None', 'velocity_punch'))
    VelocityMinTarget = (22, FieldDetails('None', 'velocity_min_target'))
    VelocityMaxTarget = (23, FieldDetails('None', 'velocity_max_target'))
    VelocityTargetLowpass = (24, FieldDetails('None', 'velocity_target_lowpass'))
    VelocityMinOutput = (25, FieldDetails('None', 'velocity_min_output'))
    VelocityMaxOutput = (26, FieldDetails('None', 'velocity_max_output'))
    VelocityOutputLowpass = (27, FieldDetails('None', 'velocity_output_lowpass'))
    EffortKp = (28, FieldDetails('None', 'effort_kp'))
    EffortKi = (29, FieldDetails('None', 'effort_ki'))
    EffortKd = (30, FieldDetails('None', 'effort_kd'))
    EffortFeedForward = (31, FieldDetails('None', 'effort_feed_forward'))
    EffortDeadZone = (32, FieldDetails('None', 'effort_dead_zone'))
    EffortIClamp = (33, FieldDetails('None', 'effort_i_clamp'))
    EffortPunch = (34, FieldDetails('None', 'effort_punch'))
    EffortMinTarget = (35, FieldDetails('None', 'effort_min_target'))
    EffortMaxTarget = (36, FieldDetails('None', 'effort_max_target'))
    EffortTargetLowpass = (37, FieldDetails('None', 'effort_target_lowpass'))
    EffortMinOutput = (38, FieldDetails('None', 'effort_min_output'))
    EffortMaxOutput = (39, FieldDetails('None', 'effort_max_output'))
    EffortOutputLowpass = (40, FieldDetails('None', 'effort_output_lowpass'))
    SpringConstant = (41, FieldDetails('N/m', 'spring_constant'))
    ReferencePosition = (42, FieldDetails('rad', 'reference_position'))
    ReferenceEffort = (43, FieldDetails('N*m', 'reference_effort'))
    VelocityLimitMin = (44, FieldDetails('rad/s', 'velocity_limit_min'))
    VelocityLimitMax = (45, FieldDetails('rad/s', 'velocity_limit_max'))
    EffortLimitMin = (46, FieldDetails('N*m', 'effort_limit_min'))
    EffortLimitMax = (47, FieldDetails('N*m', 'effort_limit_max'))
    MotorFocId = (48, FieldDetails('???', 'motor_foc_id'))
    MotorFocIq = (49, FieldDetails('???', 'motor_foc_iq'))
    UserSettingsFloat1 = (50, FieldDetails('???', 'user_settings_float1'))
    UserSettingsFloat2 = (51, FieldDetails('???', 'user_settings_float2'))
    UserSettingsFloat3 = (52, FieldDetails('???', 'user_settings_float3'))
    UserSettingsFloat4 = (53, FieldDetails('???', 'user_settings_float4'))
    UserSettingsFloat5 = (54, FieldDetails('???', 'user_settings_float5'))
    UserSettingsFloat6 = (55, FieldDetails('???', 'user_settings_float6'))
    UserSettingsFloat7 = (56, FieldDetails('???', 'user_settings_float7'))
    UserSettingsFloat8 = (57, FieldDetails('???', 'user_settings_float8'))

class CommandHighResAngleField(MessageEnum):
    Position = (0, FieldDetails('rad', 'position'))
    PositionLimitMin = (1, FieldDetails('rad', 'position_limit_min'))
    PositionLimitMax = (2, FieldDetails('rad', 'position_limit_max'))


# CommandEnumField
class CommandEnumField(MessageEnum):
    ControlStrategy = (0, FieldDetails('None', 'control_strategy'))
    MstopStrategy = (1, FieldDetails('None', 'mstop_strategy'))
    MinPositionLimitStrategy = (2, FieldDetails('None', 'min_position_limit_strategy'))
    MaxPositionLimitStrategy = (3, FieldDetails('None', 'max_position_limit_strategy'))

# CommandUInt64Field
class CommandUInt64Field(MessageEnum):
    IpAddress = (0,)
    SubnetMask = (1,)

# CommandBoolField
class CommandBoolField(MessageEnum):
    PositionDOnError = (0, FieldDetails('None', 'position_d_on_error'))
    VelocityDOnError = (1, FieldDetails('None', 'velocity_d_on_error'))
    EffortDOnError = (2, FieldDetails('None', 'effort_d_on_error'))
    AccelIncludesGravity = (3, FieldDetails('None', 'accel_includes_gravity'))

# CommandNumberedFloatField
class CommandNumberedFloatField(MessageEnum):
    Debug = (0,)

# CommandIoBankField
class CommandIoBankField(MessageEnum):
    A = (0,)
    B = (1,)
    C = (2,)
    D = (3,)
    E = (4,)
    F = (5,)

# CommandLedField
class CommandLedField(MessageEnum):
    Led = (0, FieldDetails('None', 'led'))

# CommandStringField
class CommandStringField(MessageEnum):
    Name = (0, None, 'Cannot set same name for all modules in a group.')
    Family = (1,)
    AppendLog = (2,)
    UserSettingsBytes1 = (3,)
    UserSettingsBytes2 = (4,)
    UserSettingsBytes3 = (5,)
    UserSettingsBytes4 = (6,)
    UserSettingsBytes5 = (7,)
    UserSettingsBytes6 = (8,)
    UserSettingsBytes7 = (9,)
    UserSettingsBytes8 = (10,)

# CommandFlagField
class CommandFlagField(MessageEnum):
    SaveCurrentSettings = (0, FieldDetails('None', 'save_current_settings'))
    Reset = (1, FieldDetails('None', 'reset'))
    Boot = (2, FieldDetails('None', 'boot'))
    StopBoot = (3, FieldDetails('None', 'stop_boot'))
    ClearLog = (4, FieldDetails('None', 'clear_log'))

# FeedbackFloatField
class FeedbackFloatField(MessageEnum):
    BoardTemperature = (0, FieldDetails('C', 'board_temperature'))
    ProcessorTemperature = (1, FieldDetails('C', 'processor_temperature'))
    Voltage = (2, FieldDetails('V', 'voltage'))
    Velocity = (3, FieldDetails('rad/s', 'velocity'))
    Effort = (4, FieldDetails('N*m', 'effort'))
    VelocityCommand = (5, FieldDetails('rad/s', 'velocity_command'))
    EffortCommand = (6, FieldDetails('N*m', 'effort_command'))
    Deflection = (7, FieldDetails('rad', 'deflection'))
    DeflectionVelocity = (8, FieldDetails('rad/s', 'deflection_velocity'))
    MotorVelocity = (9, FieldDetails('rad/s', 'motor_velocity'))
    MotorCurrent = (10, FieldDetails('A', 'motor_current'))
    MotorSensorTemperature = (11, FieldDetails('C', 'motor_sensor_temperature'))
    MotorWindingCurrent = (12, FieldDetails('A', 'motor_winding_current'))
    MotorWindingTemperature = (13, FieldDetails('C', 'motor_winding_temperature'))
    MotorHousingTemperature = (14, FieldDetails('C', 'motor_housing_temperature'))
    BatteryLevel = (15, FieldDetails('None', 'battery_level'))
    PwmCommand = (16, FieldDetails('None', 'pwm_command'))
    InnerEffortCommand = (17, FieldDetails('???', 'inner_effort_command'))
    MotorWindingVoltage = (18, FieldDetails('???', 'motor_winding_voltage'))
    MotorPhaseCurrentA = (19, FieldDetails('???', 'motor_phase_current_a'))
    MotorPhaseCurrentB = (20, FieldDetails('???', 'motor_phase_current_b'))
    MotorPhaseCurrentC = (21, FieldDetails('???', 'motor_phase_current_c'))
    MotorPhaseVoltageA = (22, FieldDetails('???', 'motor_phase_voltage_a'))
    MotorPhaseVoltageB = (23, FieldDetails('???', 'motor_phase_voltage_b'))
    MotorPhaseVoltageC = (24, FieldDetails('???', 'motor_phase_voltage_c'))
    MotorPhaseDutyCycleA = (25, FieldDetails('???', 'motor_phase_duty_cycle_a'))
    MotorPhaseDutyCycleB = (26, FieldDetails('???', 'motor_phase_duty_cycle_b'))
    MotorPhaseDutyCycleC = (27, FieldDetails('???', 'motor_phase_duty_cycle_c'))
    MotorFocId = (28, FieldDetails('None', 'motor_foc_id'))
    MotorFocIq = (29, FieldDetails('None', 'motor_foc_iq'))
    MotorFocIdCommand = (30, FieldDetails('None', 'motor_foc_id_command'))
    MotorFocIqCommand = (31, FieldDetails('None', 'motor_foc_iq_command'))


# FeedbackHighResAngleField
class FeedbackHighResAngleField(MessageEnum):
    Position = (0, FieldDetails('rad', 'position'))
    PositionCommand = (1, FieldDetails('rad', 'position_command'))
    MotorPosition = (2, FieldDetails('rad', 'motor_position'))


# FeedbackVector3fField
class FeedbackVector3fField(MessageEnum):
    Accelerometer = (0,)
    Gyro = (1,)
    ArPosition = (2,)

# FeedbackQuaternionfField
class FeedbackQuaternionfField(MessageEnum):
    Orientation = (0,)
    ArOrientation = (1,)

# FeedbackUInt64Field
class FeedbackUInt64Field(MessageEnum):
    SequenceNumber = (0, FieldDetails('None', 'sequence_number'))
    ReceiveTime = (1, FieldDetails('us', 'receive_time'))
    TransmitTime = (2, FieldDetails('us', 'transmit_time'))
    HardwareReceiveTime = (3, FieldDetails('us', 'hardware_receive_time'))
    HardwareTransmitTime = (4, FieldDetails('us', 'hardware_transmit_time'))
    SenderId = (5, FieldDetails('None', 'sender_id'))
    RxSequenceNumber = (6, FieldDetails('None', 'rx_sequence_number'))

# FeedbackEnumField
class FeedbackEnumField(MessageEnum):
    TemperatureState = (0, FieldDetails('None', 'temperature_state'))
    MstopState = (1, FieldDetails('None', 'mstop_state'))
    PositionLimitState = (2, FieldDetails('None', 'position_limit_state'))
    VelocityLimitState = (3, FieldDetails('None', 'velocity_limit_state'))
    EffortLimitState = (4, FieldDetails('None', 'effort_limit_state'))
    CommandLifetimeState = (5, FieldDetails('None', 'command_lifetime_state'))
    ArQuality = (6, FieldDetails('None', 'ar_quality'))
    MotorHallState = (7, FieldDetails('None', 'motor_hall_state'))


# FeedbackNumberedFloatField
class FeedbackNumberedFloatField(MessageEnum):
    Debug = (0,)

# FeedbackIoBankField
class FeedbackIoBankField(MessageEnum):
    A = (0,)
    B = (1,)
    C = (2,)
    D = (3,)
    E = (4,)
    F = (5,)


# FeedbackLedField
class FeedbackLedField(MessageEnum):
    Led = (0, FieldDetails('None', 'led'))


# InfoFloatField
class InfoFloatField(MessageEnum):
    PositionKp = (0, FieldDetails('None', 'position_kp'))
    PositionKi = (1, FieldDetails('None', 'position_ki'))
    PositionKd = (2, FieldDetails('None', 'position_kd'))
    PositionFeedForward = (3, FieldDetails('None', 'position_feed_forward'))
    PositionDeadZone = (4, FieldDetails('None', 'position_dead_zone'))
    PositionIClamp = (5, FieldDetails('None', 'position_i_clamp'))
    PositionPunch = (6, FieldDetails('None', 'position_punch'))
    PositionMinTarget = (7, FieldDetails('None', 'position_min_target'))
    PositionMaxTarget = (8, FieldDetails('None', 'position_max_target'))
    PositionTargetLowpass = (9, FieldDetails('None', 'position_target_lowpass'))
    PositionMinOutput = (10, FieldDetails('None', 'position_min_output'))
    PositionMaxOutput = (11, FieldDetails('None', 'position_max_output'))
    PositionOutputLowpass = (12, FieldDetails('None', 'position_output_lowpass'))
    VelocityKp = (13, FieldDetails('None', 'velocity_kp'))
    VelocityKi = (14, FieldDetails('None', 'velocity_ki'))
    VelocityKd = (15, FieldDetails('None', 'velocity_kd'))
    VelocityFeedForward = (16, FieldDetails('None', 'velocity_feed_forward'))
    VelocityDeadZone = (17, FieldDetails('None', 'velocity_dead_zone'))
    VelocityIClamp = (18, FieldDetails('None', 'velocity_i_clamp'))
    VelocityPunch = (19, FieldDetails('None', 'velocity_punch'))
    VelocityMinTarget = (20, FieldDetails('None', 'velocity_min_target'))
    VelocityMaxTarget = (21, FieldDetails('None', 'velocity_max_target'))
    VelocityTargetLowpass = (22, FieldDetails('None', 'velocity_target_lowpass'))
    VelocityMinOutput = (23, FieldDetails('None', 'velocity_min_output'))
    VelocityMaxOutput = (24, FieldDetails('None', 'velocity_max_output'))
    VelocityOutputLowpass = (25, FieldDetails('None', 'velocity_output_lowpass'))
    EffortKp = (26, FieldDetails('None', 'effort_kp'))
    EffortKi = (27, FieldDetails('None', 'effort_ki'))
    EffortKd = (28, FieldDetails('None', 'effort_kd'))
    EffortFeedForward = (29, FieldDetails('None', 'effort_feed_forward'))
    EffortDeadZone = (30, FieldDetails('None', 'effort_dead_zone'))
    EffortIClamp = (31, FieldDetails('None', 'effort_i_clamp'))
    EffortPunch = (32, FieldDetails('None', 'effort_punch'))
    EffortMinTarget = (33, FieldDetails('None', 'effort_min_target'))
    EffortMaxTarget = (34, FieldDetails('None', 'effort_max_target'))
    EffortTargetLowpass = (35, FieldDetails('None', 'effort_target_lowpass'))
    EffortMinOutput = (36, FieldDetails('None', 'effort_min_output'))
    EffortMaxOutput = (37, FieldDetails('None', 'effort_max_output'))
    EffortOutputLowpass = (38, FieldDetails('None', 'effort_output_lowpass'))
    SpringConstant = (39, FieldDetails('N/m', 'spring_constant'))
    VelocityLimitMin = (40, FieldDetails('rad/s', 'velocity_limit_min'))
    VelocityLimitMax = (41, FieldDetails('rad/s', 'velocity_limit_max'))
    EffortLimitMin = (42, FieldDetails('N*m', 'effort_limit_min'))
    EffortLimitMax = (43, FieldDetails('N*m', 'effort_limit_max'))
    UserSettingsFloat1 = (44,)
    UserSettingsFloat2 = (45,)
    UserSettingsFloat3 = (46,)
    UserSettingsFloat4 = (47,)
    UserSettingsFloat5 = (48,)
    UserSettingsFloat6 = (49,)
    UserSettingsFloat7 = (50,)
    UserSettingsFloat8 = (51,)
    

# InfoHighResAngleField
class InfoHighResAngleField(MessageEnum):
    PositionLimitMin = (0, FieldDetails('rad', 'position_limit_min'))
    PositionLimitMax = (1, FieldDetails('rad', 'position_limit_max'))


# InfoEnumField
class InfoEnumField(MessageEnum):
    ControlStrategy = (0, FieldDetails('None', 'control_strategy'))
    CalibrationState = (1, FieldDetails('None', 'calibration_state'))
    MstopStrategy = (2, FieldDetails('None', 'mstop_strategy'))
    MinPositionLimitStrategy = (3, FieldDetails('None', 'min_position_limit_strategy'))
    MaxPositionLimitStrategy = (4, FieldDetails('None', 'max_position_limit_strategy'))

# InfoUInt64Field
class InfoUInt64Field(MessageEnum):
    IpAddress = (0,)
    SubnetMask = (1,)
    DefaultGateway = (2,)


# InfoBoolField
class InfoBoolField(MessageEnum):
    PositionDOnError = (0, FieldDetails('None', 'position_d_on_error'))
    VelocityDOnError = (1, FieldDetails('None', 'velocity_d_on_error'))
    EffortDOnError = (2, FieldDetails('None', 'effort_d_on_error'))
    AccelIncludesGravity = (3, FieldDetails('None', 'accel_includes_gravity'))

# InfoIoBankField
class InfoIoBankField(MessageEnum):
    A = (0,)
    B = (1,)
    C = (2,)
    D = (3,)
    E = (4,)
    F = (5,)

# InfoLedField
class InfoLedField(MessageEnum):
    Led = (0, FieldDetails('None', 'led'))

# InfoStringField
class InfoStringField(MessageEnum):
    Name = (0,)
    Family = (1,)
    Serial = (2,)
    ElectricalType = (3,)
    ElectricalRevision = (4,)
    MechanicalType = (5,)
    MechanicalRevision = (6,)
    FirmwareType = (7,)
    FirmwareRevision = (8,)
    UserSettingsBytes1 = (9,)
    UserSettingsBytes2 = (10,)
    UserSettingsBytes3 = (11,)
    UserSettingsBytes4 = (12,)
    UserSettingsBytes5 = (13,)
    UserSettingsBytes6 = (14,)
    UserSettingsBytes7 = (15,)
    UserSettingsBytes8 = (16,)

# InfoFlagField
class InfoFlagField(MessageEnum):
    SaveCurrentSettings = (0, FieldDetails('None', 'save_current_settings'))
