# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See http://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------


from ctypes import Array, c_char, create_string_buffer, c_double, c_float
import numpy as np
import re
from .utils import is_pypy

import typing
from typing import overload

if typing.TYPE_CHECKING:
  from typing import Type
  import numpy.typing as npt


def __mac_address_from_bytes(a, b, c, d, e, f):
  """Used internally by ``to_mac_address``"""
  from .lookup import MacAddress
  return MacAddress(int(a), int(b), int(c), int(d), int(e), int(f))


def __mac_address_from_string(address):
  """Used internally by `to_mac_address`"""
  from .lookup import MacAddress
  if not isinstance(address, str):
    try:
      address = str(address)
    except:
      raise ValueError('Input must be string or convertible to string')

  match = re.match(r'^(([a-fA-F0-9]{2}):){5}([a-fA-F0-9]{2})$', address)
  if match != None:
    mac_byte_a = int(address[0:2], 16)
    mac_byte_b = int(address[3:5], 16)
    mac_byte_c = int(address[6:8], 16)
    mac_byte_d = int(address[9:11], 16)
    mac_byte_e = int(address[12:14], 16)
    mac_byte_f = int(address[15:17], 16)
    return MacAddress(mac_byte_a, mac_byte_b, mac_byte_c,
                      mac_byte_d, mac_byte_e, mac_byte_f)
  else:
    raise ValueError(f'Unable to parse mac address from string {address}')


def to_mac_address(*args):
  """Convert input argument(s) to a MacAddress object. Only 1 or 6 arguments
  are valid.

  If 1 argument is provided, try the following:

    * If input type is MacAddress, simply return that object
    * If input type is list or ctypes Array, recall with these elements
    * If input is of another type, try to parse a MAC address from its
      `__str__` representation

  When 6 parameters are provided, this attempts to construct a MAC address
  by interpreting the input parameters as sequential bytes of a mac address.

  If the provided argument count is neither 1 or 6,
  this function throws an exception.

  :param args: 1 or 6 element list of variadic arguments
  :return: a MacAddress instance
  """
  from .lookup import MacAddress

  if len(args) == 1:
    if isinstance(args[0], MacAddress):
      return args[0]
    elif isinstance(args[0], list) or isinstance(args[0], Array):
      if len(args[0]) == 1:
        return to_mac_address(args[0])
      elif len(args[0]) == 6:
        arg = args[0]
        return to_mac_address(*arg)
      else:
        raise ValueError(f'Invalid amount of arguments provided ({args[0]}). Expected 1 or 6')
    else:
      try:
        return __mac_address_from_string(args[0])
      except ValueError as v:
        raise ValueError('Could not create mac address from argument', v)
  elif len(args) == 6:
    return __mac_address_from_bytes(*args)
  else:
    raise ValueError(f'Invalid amount of arguments provided ({len(args)}). Expected 1 or 6')


################################################################################
# Converting to numpy types
################################################################################


def __to_contig_sq_mat_chk_size(size):
  try:
    size = int(size)
  except Exception as e:
    raise ValueError('size must be convertible to an integer', e)
  if size < 1:
    raise ValueError('size must be greater than zero')
  return size


def __to_contig_sq_mat_handle_ret(ret: 'npt.NDArray', size):
  expected_shape = (size, size)
  if ret.shape != expected_shape:
    ret = ret.reshape(expected_shape)

  # Enforce output will be right shape
  if ret.shape != expected_shape:
    raise ValueError(f'Cannot convert input to shape {expected_shape}')

  # Enforce contiguous in memory
  if not ret.flags['C_CONTIGUOUS']:
    ret = np.ascontiguousarray(ret)
  return ret


if is_pypy():

  __pypy_ctypes_arr_types = dict()

  def __to_contig_sq_mat_impl(mat, size):
    size = __to_contig_sq_mat_chk_size(size)
    # Hack to fix weird pypy numpy issues with __buffer__
    if isinstance(mat, Array) and not hasattr(mat, '_HEBI_PYPY_HACK'):
      mat = mat[:]
    ret = np.asarray(mat, dtype=np.float64)
    return __to_contig_sq_mat_handle_ret(ret, size)

else:

  def __to_contig_sq_mat_impl(mat, size):
    size = __to_contig_sq_mat_chk_size(size)
    ret = np.asarray(mat, dtype=np.float64)
    return __to_contig_sq_mat_handle_ret(ret, size)


def to_contig_sq_mat(mat: 'npt.NDArray', size=3):
  """Converts input to a numpy square matrix of the specified data type and
  size.

  This function ensures that the underlying data is laid out
  in contiguous memory.

  :param mat: Input matrix
  :param dtype: Data type of matrix
  :param size: Size of matrix
  :return: a `size`x`size` numpy matrix with elements of type `dtype`
  """
  return __to_contig_sq_mat_impl(mat, size)


if is_pypy():

  from ctypes import POINTER
  _CTypes_LP_Double = POINTER(c_double)

  class _PyPyLP_Double(_CTypes_LP_Double):
    _type_ = _CTypes_LP_Double._type_
    __slots__ = ['_HEBI_PYPY_HACK']

    def __init__(self, val):
      super().__init__(val)
      self._HEBI_PYPY_HACK = True

    def __buffer__(self, *args):
      pass

  def np_array_from_dbl_ptr(ptr, size):
    return np.ctypeslib.as_array(_PyPyLP_Double(ptr.contents), size)

else:

  def np_array_from_dbl_ptr(ptr, size):
    return np.ctypeslib.as_array(ptr, size)


################################################################################
# CTypes Compatibility functions
################################################################################

@overload
def create_string_buffer_compat(init: str) -> 'Array[c_char]': ...


@overload
def create_string_buffer_compat(init: int) -> 'Array[c_char]': ...


@overload
def create_string_buffer_compat(init: str, size: int) -> 'Array[c_char]': ...


def create_string_buffer_compat(init, size=None):
  if size is not None:
    return create_string_buffer(bytes(init, 'utf8'), size)

  if isinstance(init, str):
    return create_string_buffer(bytes(init, 'utf8'))
  elif isinstance(init, int):
    return create_string_buffer(init)
  raise TypeError(init)


def decode_string_buffer(bfr, encoding='utf8') -> 'str | None':
  """Enables compatibility between Python 2 and 3.

  :param bfr: a string, ``bytes``, or ctypes array
  :return: a string
  """
  import ctypes
  if isinstance(bfr, str):
    return bfr
  elif isinstance(bfr, bytes):
    return bfr.decode(encoding, 'replace')
  elif isinstance(bfr, ctypes.Array):
    casted = ctypes.cast(bfr, ctypes.c_char_p).value
    if casted is None:
      return None
    return casted.decode(encoding, 'replace')
  else:
    raise TypeError(bfr)


def __is_int_type(val):
  return isinstance(val, int)


def __dbl_bf_check(size):
  if not __is_int_type(size):
    raise TypeError('size must be an integer')
  if size < 1:
    raise ValueError('size must be a positive number')


if is_pypy():
  # Work around some ridiculous PyPy numpy-ctypes bugs here

  __pypy_dbl_bfr_types = dict()
  __pypy_float_bfr_types = dict()

  def __terrible_Ctypes_Array_Type_Hack(cls):
    class PyPyBufferType(cls):
      __slots__ = ['_HEBI_PYPY_HACK']

      def __init__(self, *args):
        super().__init__(*args)
        self._HEBI_PYPY_HACK = True

      def __buffer__(self, *args, **kwargs):
        # For some reason, numpy on PyPy wants to call buffer,
        # which will return a __builtin__.buffer object, which
        # is absolutely wrong.
        # If numpy succeeds in calling buffer(), the dtype will become `uint8`,
        # which is obviously entirely wrong here.
        pass
    return PyPyBufferType

  def create_float_buffer(size):
    __dbl_bf_check(size)
    try:
      PyPyBufferType = __pypy_float_bfr_types[size]
    except KeyError:
      PyPyBufferType = __terrible_Ctypes_Array_Type_Hack((c_float * size))
      __pypy_float_bfr_types[size] = PyPyBufferType
    return PyPyBufferType()

  # This works around very strange pypy numpy bugs

  def create_double_buffer(size):
    __dbl_bf_check(size)
    try:
      PyPyBufferType = __pypy_dbl_bfr_types[size]
    except KeyError:
      PyPyBufferType = __terrible_Ctypes_Array_Type_Hack((c_double * size))
      __pypy_dbl_bfr_types[size] = PyPyBufferType
    return PyPyBufferType()

  # Cache used sizes
  create_double_buffer(6)
  create_double_buffer(16)
  create_double_buffer(256)

  create_float_buffer(3)
  create_float_buffer(4)

else:

  __dbl_bfr_types: 'dict[int, Type[Array[c_double]]]' = dict()
  __float_bfr_types: 'dict[int, Type[Array[c_float]]]' = dict()

  def create_double_buffer(size: int):
    """Creates a ctypes array of c_double elements.

    :param size: The number of elements to be in the array
    :return: c_double array
    """
    __dbl_bf_check(size)
    try:
      ArrType = __dbl_bfr_types[size]
    except KeyError:
      ArrType = (c_double * size)
      __dbl_bfr_types[size] = ArrType
    return ArrType()

  def create_float_buffer(size: int):
    """Creates a ctypes array of c_float elements.

    :param size: The number of elements to be in the array
    :return: c_float array
    """
    __dbl_bf_check(size)
    try:
      ArrType = __float_bfr_types[size]
    except KeyError:
      ArrType = (c_float * size)
      __float_bfr_types[size] = ArrType
    return ArrType()

  # Cache used sizes
  __dbl_bfr_types[6] = (c_double * 6)
  __dbl_bfr_types[16] = (c_double * 16)
  __dbl_bfr_types[256] = (c_double * 256)

  __float_bfr_types[3] = (c_float * 3)
  __float_bfr_types[4] = (c_float * 4)
