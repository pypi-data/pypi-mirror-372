import ctypes as _ctypes
import threading

from .ctypes_utils import cast, c_int_p, c_int32_p, c_uint32_p, c_int64_p, c_uint64_p, c_float_p, c_double_p


class TLS_Holder:
  __slots__ = [
      "_buffer", "_size", "_c_int_p", "_c_int32_p", "_c_uint32_p",
      "_c_int64_p", "_c_uint64_p", "_c_float_p", "_c_double_p"
  ]

  def _grow_arrays(self, size: int):
    if size > self._size:
      bfr = _ctypes.c_buffer(size)
      self._c_int_p = cast(bfr, c_int_p)
      self._c_int32_p = cast(bfr, c_int32_p)
      self._c_uint32_p = cast(bfr, c_uint32_p)
      self._c_int64_p = cast(bfr, c_int64_p)
      self._c_uint64_p = cast(bfr, c_uint64_p)
      self._c_float_p = cast(bfr, c_float_p)
      self._c_double_p = cast(bfr, c_double_p)
      self._buffer = bfr
      self._size = size

  def __init__(self):
    self._size = 0
    self._grow_arrays(1024)


class MessagesTLS(threading.local):
  def __init__(self):
    super().__init__()
    self._holder = TLS_Holder()


_tls = MessagesTLS()


int_buffer = lambda: _tls._holder._c_int_p
int32_buffer = lambda: _tls._holder._c_int32_p
uint32_buffer = lambda: _tls._holder._c_uint32_p
int64_buffer = lambda: _tls._holder._c_int64_p
uint64_buffer = lambda: _tls._holder._c_uint64_p
float_buffer = lambda: _tls._holder._c_float_p
double_buffer = lambda: _tls._holder._c_double_p


grow_buffer_if_needed_int = lambda size: _tls._holder._grow_arrays(size * 4)
grow_buffer_if_needed_long = lambda size: _tls._holder._grow_arrays(size * 8)
