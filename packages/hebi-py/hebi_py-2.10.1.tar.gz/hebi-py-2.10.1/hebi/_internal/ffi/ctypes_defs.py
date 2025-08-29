import ctypes


################################################################################
# Used to populate the robot model metadata structure
################################################################################


class _MetaDataAnonActuatorCTypes(ctypes.Structure):
  _fields_ = [("actuator_type_", ctypes.c_int)]


class _MetaDataAnonBracketCTypes(ctypes.Structure):
  _fields_ = [("bracket_type_", ctypes.c_int)]


class _MetaDataAnonJointCTypes(ctypes.Structure):
  _fields_ = [("joint_type_", ctypes.c_int)]


class _MetaDataAnonLinkCTypes(ctypes.Structure):
  _fields_ = [
      ("link_type_", ctypes.c_int),
      ("input_type_", ctypes.c_int),
      ("output_type_", ctypes.c_int),
      ("extension_", ctypes.c_float),
      ("twist_", ctypes.c_float)
  ]


class _MetaDataAnonEndEffectorCTypes(ctypes.Structure):
  _fields_ = [("end_effector_type_", ctypes.c_int)]


class _MetaDataUnionCTypes(ctypes.Union):
  _anonymous_ = ("actuator_type_struct_", "bracket_type_struct_", "joint_type_struct_", "link_type_struct_", "end_effector_type_struct_")
  _fields_ = [
      ("actuator_type_struct_", _MetaDataAnonActuatorCTypes),
      ("bracket_type_struct_", _MetaDataAnonBracketCTypes),
      ("joint_type_struct_", _MetaDataAnonJointCTypes),
      ("link_type_struct_", _MetaDataAnonLinkCTypes),
      ("end_effector_type_struct_", _MetaDataAnonEndEffectorCTypes)
  ]

################################################################################
# Anonymous unions
################################################################################


class _IoPinUnion(ctypes.Union):
  _fields_ = [
      ("int_value_", ctypes.c_int64),
      ("float_value_", ctypes.c_float)
  ]


#  TODO: This is not an anonymous union, but needs to be declared before the union. Fix?
class HebiTimeEstimationNFabianParams(ctypes.Structure):
  _fields_ = [
    ("magic_fabian_constant_", ctypes.c_double),
  ]


class _TimeEstimationParamsUnion(ctypes.Union):
  _fields_ = [
      ("n_fabian_params_", HebiTimeEstimationNFabianParams),
      ("float_value_", ctypes.c_float)
  ]


################################################################################
# Public facing
################################################################################

class HebiTimeEstimationParams(ctypes.Structure):
  _anonymous_ = ("__time_estimation_params_union_",)
  _fields_ = [
      ("method_type_", ctypes.c_int),
      ("__time_estimation_params_union_", _TimeEstimationParamsUnion)
  ]


class HebiMacAddress(ctypes.Structure):
  _fields_ = [
      ("bytes_", ctypes.c_uint8 * 6)
  ]


class HebiVector3f(ctypes.Structure):
  _fields_ = [
      ("data", ctypes.c_float * 3)
  ]


class HebiQuaternionf(ctypes.Structure):
  _fields_ = [
      ("data", ctypes.c_float * 4)
  ]


class HebiRobotModelElementMetadata(ctypes.Structure):
  _anonymous_ = ("__element_struct_",)
  _fields_ = [
      ("struct_size_", ctypes.c_uint32),
      ("element_type_", ctypes.c_int),
      ("__element_struct_", _MetaDataUnionCTypes)
  ]


class HebiRobotModelElementTopology(ctypes.Structure):
  _fields_ = [
      ("element_index_", ctypes.c_int32),
      ("parent_index_", ctypes.c_int32),
      ("parent_output_", ctypes.c_int32),
      ("dof_location_", ctypes.c_int32),
      ("com_index_", ctypes.c_int32),
      ("output_index_", ctypes.c_int32),
      ("end_effector_index_", ctypes.c_int32)
  ]


class HebiHighResAngleStruct(ctypes.Structure):
  _fields_ = [
      ("revolutions_", ctypes.c_int64),
      ("offset_", ctypes.c_float)
  ]


class HebiIoBankPinStruct(ctypes.Structure):
  _anonymous_ = ("__io_union_",)
  _fields_ = [
      ("__io_union_", _IoPinUnion),
      ("stored_type_", ctypes.c_int)
  ]


class HebiCommandRef(ctypes.Structure):
  _fields_ = [
      ("message_bitfield_", ctypes.POINTER(ctypes.c_int32)),
      ("float_fields_", ctypes.POINTER(ctypes.c_float)),
      ("high_res_angle_fields_", ctypes.POINTER(HebiHighResAngleStruct)),
      ("vector3f_fields_", ctypes.POINTER(HebiVector3f)),
      ("quaternionf_fields_", ctypes.POINTER(HebiQuaternionf)),
      ("uint64_fields_", ctypes.POINTER(ctypes.c_uint64)),
      ("enum_fields_", ctypes.POINTER(ctypes.c_int32)),
      ("bool_fields_", ctypes.POINTER(ctypes.c_bool)),
      ("numbered_float_fields_", ctypes.POINTER(ctypes.c_float)),
      ("io_fields_", ctypes.POINTER(HebiIoBankPinStruct)),
      ("led_fields_", ctypes.POINTER(ctypes.c_uint32)),
      ("reserved_", ctypes.c_void_p)
  ]


class HebiCommandMetadata(ctypes.Structure):
  _fields_ = [
      ("float_field_count_", ctypes.c_uint32),
      ("high_res_angle_field_count_", ctypes.c_uint32),
      ("vector3f_field_count_", ctypes.c_uint32),
      ("quaternionf_field_count_", ctypes.c_uint32),
      ("uint64_field_count_", ctypes.c_uint32),
      ("enum_field_count_", ctypes.c_uint32),
      ("bool_field_count_", ctypes.c_uint32),
      ("numbered_float_field_count_", ctypes.c_uint32),
      ("io_field_count_", ctypes.c_uint32),
      ("led_field_count_", ctypes.c_uint32),
      ("string_field_count_", ctypes.c_uint32),
      ("flag_field_count_", ctypes.c_uint32),
      ("float_field_bitfield_offset_", ctypes.c_uint32),
      ("high_res_angle_field_bitfield_offset_", ctypes.c_uint32),
      ("vector3f_field_bitfield_offset_", ctypes.c_uint32),
      ("quaternionf_field_bitfield_offset_", ctypes.c_uint32),
      ("uint64_field_bitfield_offset_", ctypes.c_uint32),
      ("enum_field_bitfield_offset_", ctypes.c_uint32),
      ("bool_field_bitfield_offset_", ctypes.c_uint32),
      ("numbered_float_field_bitfield_offset_", ctypes.c_uint32),
      ("io_field_bitfield_offset_", ctypes.c_uint32),
      ("led_field_bitfield_offset_", ctypes.c_uint32),
      ("string_field_bitfield_offset_", ctypes.c_uint32),
      ("flag_field_bitfield_offset_", ctypes.c_uint32),
      ("numbered_float_relative_offsets_", ctypes.POINTER(ctypes.c_uint32)),
      ("numbered_float_field_sizes_", ctypes.POINTER(ctypes.c_uint32)),
      ("io_relative_offsets_", ctypes.POINTER(ctypes.c_uint32)),
      ("io_field_sizes_", ctypes.POINTER(ctypes.c_uint32)),
      ("message_bitfield_count_", ctypes.c_uint32),
  ]


class HebiFeedbackRef(ctypes.Structure):
  _fields_ = [
      ("message_bitfield_", ctypes.POINTER(ctypes.c_int32)),
      ("float_fields_", ctypes.POINTER(ctypes.c_float)),
      ("high_res_angle_fields_", ctypes.POINTER(HebiHighResAngleStruct)),
      ("vector3f_fields_", ctypes.POINTER(HebiVector3f)),
      ("quaternionf_fields_", ctypes.POINTER(HebiQuaternionf)),
      ("uint64_fields_", ctypes.POINTER(ctypes.c_uint64)),
      ("enum_fields_", ctypes.POINTER(ctypes.c_int32)),
      ("bool_fields_", ctypes.POINTER(ctypes.c_bool)),
      ("numbered_float_fields_", ctypes.POINTER(ctypes.c_float)),
      ("io_fields_", ctypes.POINTER(HebiIoBankPinStruct)),
      ("led_fields_", ctypes.POINTER(ctypes.c_uint32)),
      ("reserved_", ctypes.c_void_p)
  ]


class HebiFeedbackMetadata(ctypes.Structure):
  _fields_ = [
      ("float_field_count_", ctypes.c_uint32),
      ("high_res_angle_field_count_", ctypes.c_uint32),
      ("vector3f_field_count_", ctypes.c_uint32),
      ("quaternionf_field_count_", ctypes.c_uint32),
      ("uint64_field_count_", ctypes.c_uint32),
      ("enum_field_count_", ctypes.c_uint32),
      ("bool_field_count_", ctypes.c_uint32),
      ("numbered_float_field_count_", ctypes.c_uint32),
      ("io_field_count_", ctypes.c_uint32),
      ("led_field_count_", ctypes.c_uint32),
      ("string_field_count_", ctypes.c_uint32),
      ("flag_field_count_", ctypes.c_uint32),
      ("float_field_bitfield_offset_", ctypes.c_uint32),
      ("high_res_angle_field_bitfield_offset_", ctypes.c_uint32),
      ("vector3f_field_bitfield_offset_", ctypes.c_uint32),
      ("quaternionf_field_bitfield_offset_", ctypes.c_uint32),
      ("uint64_field_bitfield_offset_", ctypes.c_uint32),
      ("enum_field_bitfield_offset_", ctypes.c_uint32),
      ("bool_field_bitfield_offset_", ctypes.c_uint32),
      ("numbered_float_field_bitfield_offset_", ctypes.c_uint32),
      ("io_field_bitfield_offset_", ctypes.c_uint32),
      ("led_field_bitfield_offset_", ctypes.c_uint32),
      ("string_field_bitfield_offset_", ctypes.c_uint32),
      ("flag_field_bitfield_offset_", ctypes.c_uint32),
      ("numbered_float_relative_offsets_", ctypes.POINTER(ctypes.c_uint32)),
      ("numbered_float_field_sizes_", ctypes.POINTER(ctypes.c_uint32)),
      ("io_relative_offsets_", ctypes.POINTER(ctypes.c_uint32)),
      ("io_field_sizes_", ctypes.POINTER(ctypes.c_uint32)),
      ("message_bitfield_count_", ctypes.c_uint32),
  ]


class HebiInfoRef(ctypes.Structure):
  _fields_ = [
      ("message_bitfield_", ctypes.POINTER(ctypes.c_int32)),
      ("float_fields_", ctypes.POINTER(ctypes.c_float)),
      ("high_res_angle_fields_", ctypes.POINTER(HebiHighResAngleStruct)),
      ("vector3f_fields_", ctypes.POINTER(HebiVector3f)),
      ("quaternionf_fields_", ctypes.POINTER(HebiQuaternionf)),
      ("uint64_fields_", ctypes.POINTER(ctypes.c_uint64)),
      ("enum_fields_", ctypes.POINTER(ctypes.c_int32)),
      ("bool_fields_", ctypes.POINTER(ctypes.c_bool)),
      ("numbered_float_fields_", ctypes.POINTER(ctypes.c_float)),
      ("io_fields_", ctypes.POINTER(HebiIoBankPinStruct)),
      ("led_fields_", ctypes.POINTER(ctypes.c_uint32)),
      ("reserved_", ctypes.c_void_p)
  ]


class HebiInfoMetadata(ctypes.Structure):
  _fields_ = [
      ("float_field_count_", ctypes.c_uint32),
      ("high_res_angle_field_count_", ctypes.c_uint32),
      ("vector3f_field_count_", ctypes.c_uint32),
      ("quaternionf_field_count_", ctypes.c_uint32),
      ("uint64_field_count_", ctypes.c_uint32),
      ("enum_field_count_", ctypes.c_uint32),
      ("bool_field_count_", ctypes.c_uint32),
      ("numbered_float_field_count_", ctypes.c_uint32),
      ("io_field_count_", ctypes.c_uint32),
      ("led_field_count_", ctypes.c_uint32),
      ("string_field_count_", ctypes.c_uint32),
      ("flag_field_count_", ctypes.c_uint32),
      ("float_field_bitfield_offset_", ctypes.c_uint32),
      ("high_res_angle_field_bitfield_offset_", ctypes.c_uint32),
      ("vector3f_field_bitfield_offset_", ctypes.c_uint32),
      ("quaternionf_field_bitfield_offset_", ctypes.c_uint32),
      ("uint64_field_bitfield_offset_", ctypes.c_uint32),
      ("enum_field_bitfield_offset_", ctypes.c_uint32),
      ("bool_field_bitfield_offset_", ctypes.c_uint32),
      ("numbered_float_field_bitfield_offset_", ctypes.c_uint32),
      ("io_field_bitfield_offset_", ctypes.c_uint32),
      ("led_field_bitfield_offset_", ctypes.c_uint32),
      ("string_field_bitfield_offset_", ctypes.c_uint32),
      ("flag_field_bitfield_offset_", ctypes.c_uint32),
      ("numbered_float_relative_offsets_", ctypes.POINTER(ctypes.c_uint32)),
      ("numbered_float_field_sizes_", ctypes.POINTER(ctypes.c_uint32)),
      ("io_relative_offsets_", ctypes.POINTER(ctypes.c_uint32)),
      ("io_field_sizes_", ctypes.POINTER(ctypes.c_uint32)),
      ("message_bitfield_count_", ctypes.c_uint32),
  ]


class HebiUserState(ctypes.Structure):
  _fields_ = [
      ("state_1", ctypes.POINTER(ctypes.c_double)),
      ("state_2", ctypes.POINTER(ctypes.c_double)),
      ("state_3", ctypes.POINTER(ctypes.c_double)),
      ("state_4", ctypes.POINTER(ctypes.c_double)),
      ("state_5", ctypes.POINTER(ctypes.c_double)),
      ("state_6", ctypes.POINTER(ctypes.c_double)),
      ("state_7", ctypes.POINTER(ctypes.c_double)),
      ("state_8", ctypes.POINTER(ctypes.c_double)),
      ("state_9", ctypes.POINTER(ctypes.c_double))
  ]
