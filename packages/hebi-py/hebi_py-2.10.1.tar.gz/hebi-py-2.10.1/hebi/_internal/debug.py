# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2017 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------


import sys


def __default_out_stream(msg: str):
  print(msg)


def __default_err_stream(msg: str):
  sys.stderr.write(msg + '\n')


def __print_to_stream(msg: str, stream, prefix: str):
  if '\n' in msg:
    for entry in msg.splitlines():
      stream(prefix + entry)
  else:
    stream(prefix + msg)


__hebi_debug = False
__hebi_out_stream = __default_out_stream
__hebi_err_stream = __default_err_stream


def set_debug_mode(dbg):
  global __hebi_debug
  __hebi_debug = bool(dbg)


def debug_mode():
  return __hebi_debug


def debug_log(msg: str):
  if __hebi_debug:
    __print_to_stream(msg, __hebi_out_stream, '[HEBI Debug] ')


def warn_log(msg: str):
  __print_to_stream(msg, __hebi_err_stream, '[HEBI Warning] ')
