import ctypes as _ctypes
import numpy as _np


################################################################################
### Common ctypes classes and values
################################################################################


c_bool_p = _ctypes.POINTER(_ctypes.c_bool)
c_int_p = _ctypes.POINTER(_ctypes.c_int)
c_int32_p = _ctypes.POINTER(_ctypes.c_int32)
c_uint32_p = _ctypes.POINTER(_ctypes.c_uint32)
c_int64_p = _ctypes.POINTER(_ctypes.c_int64)
c_uint64_p = _ctypes.POINTER(_ctypes.c_uint64)
c_float_p = _ctypes.POINTER(_ctypes.c_float)
c_double_p = _ctypes.POINTER(_ctypes.c_double)

NULLPTR = _ctypes.c_void_p(0)


################################################################################
### Common ctypes functions
################################################################################


to_ctypes = _np.ctypeslib.as_ctypes
cast = _ctypes.cast
byref = _ctypes.byref


cast_to_double_ptr = lambda val: cast(val, c_double_p)
cast_to_float_ptr = lambda val: cast(val, c_float_p)


def pointer_offset(ptr: '_ctypes._Pointer[_ctypes.c_double]', offset: int):
  """Equivalent to `(char*)ptr + offset` or `&((char*)ptr)[offset]`"""
  return byref(ptr.contents, offset)


def to_double_ptr(val):
  """Retrieve a ctypes pointer to the provided numpy object."""
  return cast(val.__array_interface__['data'][0], c_double_p)


def to_float_ptr(val):
  """Retrieve a ctypes pointer to the provided numpy object."""
  return cast(val.__array_interface__['data'][0], c_float_p)
