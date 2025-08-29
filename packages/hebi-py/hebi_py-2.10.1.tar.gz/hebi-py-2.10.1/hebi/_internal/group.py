# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------


from typing import overload
import typing
from atexit import register as __register
from ctypes import CFUNCTYPE, POINTER, pointer, c_size_t, c_void_p, c_char_p, c_double, byref
import os
from weakref import ref

import json

from .ffi.ctypes_defs import HebiUserState

from .log_file import LogFile
from .ffi import api, enums
from .ffi.wrappers import UnmanagedObject, UnmanagedSharedObject
from .ffi._message_types import GroupCommand, GroupFeedback, GroupInfo
from .utils import safe_mkdirs
from . import type_utils

_FeedbackHandlerFunction = CFUNCTYPE(None, c_void_p, c_void_p)

if typing.TYPE_CHECKING:
  from typing import Callable


class GroupDelegate(UnmanagedObject):
  """Delegate for Group."""

  __slots__ = ['_c_callback', '_feedback_callbacks', '_number_of_modules', '__weakref__']

  __instances: 'list[ref[GroupDelegate]]' = list()

  @staticmethod
  def destroy_all_instances():
    for entry in GroupDelegate.__instances:
      try:
        e = entry()
        if e is not None:
          e.force_delete()
      except:
        pass

  def __parse_to(self, timeout_ms: 'float | None'):
    if timeout_ms is None:
      return Group.DEFAULT_TIMEOUT_MS
    else:
      try:
        return int(timeout_ms)
      except:
        raise ValueError('timeout_ms must be a number')

  def __feedback_handler(self, c_fbk, c_data):

    class FlyweightGroupFeedback(GroupFeedback):
      __slots__ = []

      def __init__(self, number_of_modules: int, internal):
        # Explicitly skip over GroupFeedback constructor
        UnmanagedSharedObject.__init__(self, internal=internal)
        self._initialize(number_of_modules)

    feedback = FlyweightGroupFeedback(self._number_of_modules, c_fbk)
    for entry in self._feedback_callbacks:
      entry(feedback)
    # Don't allow any dangling references
    feedback._holder.force_delete()

  def __setup_feedback_handler(self):
    fbk_handler = self.__feedback_handler
    c_callback = _FeedbackHandlerFunction(fbk_handler)
    self._c_callback = c_callback
    api.hebiGroupRegisterFeedbackHandler(self, c_callback, c_void_p(0))

  def __init__(self, internal):

    def deleter(internal):
      api.hebiGroupSetFeedbackFrequencyHz(internal, 0.0)
      api.hebiGroupClearFeedbackHandlers(internal)
      # If the group is logging, stop.
      c_log = api.hebiGroupStopLog(internal)
      if c_log is not None:
        # Release the log file, if it was created.
        api.hebiLogFileRelease(c_log)
      api.hebiGroupRelease(internal)

    super().__init__(internal, on_delete=deleter)

    GroupDelegate.__instances.append(ref(self))

    self._number_of_modules = int(api.hebiGroupGetSize(internal))
    self._feedback_callbacks: 'list[Callable[[GroupFeedback], None]]' = list()

  @property
  def size(self):
    return self._number_of_modules

  @property
  def feedback_frequency(self):
    return float(api.hebiGroupGetFeedbackFrequencyHz(self))

  @feedback_frequency.setter
  def feedback_frequency(self, value):
    try:
      value = float(value)
    except:
      raise ValueError("frequency must be a number")
    if api.hebiGroupSetFeedbackFrequencyHz(self, value) != enums.StatusCode.Success:
      raise RuntimeError(f'Could not set feedback frequency to {value}')

  @property
  def command_lifetime(self):
    return int(api.hebiGroupGetCommandLifetime(self))

  @command_lifetime.setter
  def command_lifetime(self, value):
    try:
      value = int(value)
    except:
      raise ValueError("lifetime must be a number")
    if api.hebiGroupSetCommandLifetime(self, value) != enums.StatusCode.Success:
      raise RuntimeError(f'Could not set command lifetime to {value}')

  def send_command(self, group_command: 'GroupCommand') -> bool:
    return api.hebiGroupSendCommand(self, group_command) == enums.StatusCode.Success

  def send_command_with_acknowledgement(self, group_command: 'GroupCommand', timeout_ms=None) -> bool:
    timeout_ms = self.__parse_to(timeout_ms)
    status = api.hebiGroupSendCommandWithAcknowledgement(self, group_command, timeout_ms)
    return status == enums.StatusCode.Success

  def send_layout(self, layout_file=None, layout=None, timeout_ms=None) -> bool:
    timeout_ms = self.__parse_to(timeout_ms)
    if layout_file is not None:
      layout_file = str(layout_file)
      c_layout_file = type_utils.create_string_buffer_compat(layout_file)
      return api.hebiGroupSendLayout(self, c_layout_file, 0, 0, timeout_ms) == enums.StatusCode.Success
    elif layout is not None:
      c_layout = type_utils.create_string_buffer_compat(json.dumps(layout, ensure_ascii=False))
      return api.hebiGroupSendLayoutBuffer(self, c_layout, len(c_layout)-1, 0, 0, timeout_ms) == enums.StatusCode.Success
    else:
      return False

  def send_feedback_request(self):
    return api.hebiGroupSendFeedbackRequest(self) == enums.StatusCode.Success

  def get_next_feedback(self, timeout_ms=None, reuse_fbk: 'GroupFeedback | None' = None):
    timeout_ms = self.__parse_to(timeout_ms)
    if reuse_fbk:
      feedback = reuse_fbk
    else:
      feedback = GroupFeedback(self._number_of_modules)

    res = api.hebiGroupGetNextFeedback(self, feedback, timeout_ms)
    if res == enums.StatusCode.Success:
      return feedback
    else:
      return None

  def request_info(self, timeout_ms: 'float | None' = None, reuse_info: 'GroupInfo | None' = None, request_extra_info=False):
    timeout_ms = self.__parse_to(timeout_ms)
    if reuse_info is not None:
      info = GroupInfo(self._number_of_modules)
    else:
      info = GroupInfo(self._number_of_modules, reuse_info)

    if request_extra_info:
      request_flags = 0x01 + 0x02 + 0x04
    else:
      request_flags = 0
    res = api.hebiGroupRequestInfoExtra(self, info, request_flags, timeout_ms)
    if res == enums.StatusCode.Success:
      return info
    else:
      return None

  def start_log(self, directory: 'str | None' = None, name: 'str | None' = None):
    if directory is None:
      c_directory = c_char_p(None)
    else:
      directory = str(directory)
      c_directory = type_utils.create_string_buffer_compat(directory)

    if name is None:
      c_name = c_char_p(None)
    else:
      name = str(name)
      if '.' not in name:
        name = name + '.hebilog'
      c_name = type_utils.create_string_buffer_compat(name)

    c_string_ret = c_void_p(0)
    res = api.hebiGroupStartLog(self, c_directory, c_name, byref(c_string_ret))

    if res != enums.StatusCode.Success:
      return None

    c_str_length = c_size_t(0)
    api.hebiStringGetString(c_string_ret, c_char_p(None), byref(c_str_length))

    if c_str_length.value == 0:  # Unknown error
      api.hebiStringRelease(c_string_ret)
      raise RuntimeError('Underlying C API call hebiStringGetString'
                         'returned length of zero')

    c_str_buffer = type_utils.create_string_buffer_compat(c_str_length.value)
    api.hebiStringGetString(c_string_ret, c_str_buffer, byref(c_str_length))

    ret: str = c_str_buffer.value.decode('utf-8')
    api.hebiStringRelease(c_string_ret)
    return ret

  def stop_log(self):
    c_log = api.hebiGroupStopLog(self)
    if c_log is None:
      return None
    return LogFile(c_log)

  def log_user_state(self,
                     v1: 'float | None',
                     v2: 'float | None',
                     v3: 'float | None',
                     v4: 'float | None',
                     v5: 'float | None',
                     v6: 'float | None',
                     v7: 'float | None',
                     v8: 'float | None',
                     v9: 'float | None') -> bool:

    state = HebiUserState()

    state.state_1 = POINTER(c_double)() if v1 is None else pointer(c_double(v1))
    state.state_2 = POINTER(c_double)() if v2 is None else pointer(c_double(v2))
    state.state_3 = POINTER(c_double)() if v3 is None else pointer(c_double(v3))
    state.state_4 = POINTER(c_double)() if v4 is None else pointer(c_double(v4))
    state.state_5 = POINTER(c_double)() if v5 is None else pointer(c_double(v5))
    state.state_6 = POINTER(c_double)() if v6 is None else pointer(c_double(v6))
    state.state_7 = POINTER(c_double)() if v7 is None else pointer(c_double(v7))
    state.state_8 = POINTER(c_double)() if v8 is None else pointer(c_double(v8))
    state.state_9 = POINTER(c_double)() if v9 is None else pointer(c_double(v9))

    return api.hebiGroupLogUserState(self, state) == enums.StatusCode.Success

  def add_feedback_handler(self, handler: 'Callable[[GroupFeedback], None]'):
    if not callable(handler):
      raise ValueError('handler was not callable')
    if handler in self._feedback_callbacks:
      return
    self._feedback_callbacks.append(handler)
    if len(self._feedback_callbacks) == 1:
      self.__setup_feedback_handler()

  def clear_feedback_handlers(self):
    self._feedback_callbacks = list()
    api.hebiGroupClearFeedbackHandlers(self)


def create_imitation_group(size):
  if not isinstance(size, int):
    raise TypeError('size must be an int')
  if size < 1:
    raise ValueError('size must be greater than zero')

  ret = Group(GroupDelegate(api.hebiGroupCreateImitation(size)))
  return ret


class Group:
  """Represents a group of physical HEBI modules, and allows Command, Feedback,
  and Info objects to be sent to and recieved from the hardware."""

  __slots__ = ['__delegate']

  DEFAULT_TIMEOUT_MS = 500
  """The default timeout (in milliseconds)"""

  def __init__(self, delegate: GroupDelegate):
    """This is created internally.

    Do not instantiate directly.
    """
    self.__delegate = delegate

  def __repr__(self):
    if self.__delegate.finalized:
      return f'Finalized group (size: {self.size})'
    feedback_freq = self.feedback_frequency
    # command_lifetime is in milliseconds - convert to seconds
    cmd_lifetime = float(self.command_lifetime) * 0.001
    num_modules = self.size

    justify_size = 20
    justify_fmt = f' >{justify_size}'

    ret = (format('feedback_frequency: ', justify_fmt) + f'{feedback_freq} [Hz]\n' +
           format('command_lifetime: ', justify_fmt) + f'{cmd_lifetime} [s]\n' +
           format('size: ', justify_fmt) + f'{num_modules}')

    # XXX: We should really add the module info table, to match MATLAB
    return ret

  def __str__(self):
    feedback_freq = self.feedback_frequency
    # command_lifetime is in milliseconds - convert to seconds
    cmd_lifetime = float(self.command_lifetime) * 0.001
    num_modules = self.size
    return f'Group(feedback_frequency={feedback_freq}, command_lifetime={cmd_lifetime}, size={num_modules})'

  @property
  def size(self):
    """The number of modules in the group.

    :return: size of the group
    :rtype: int
    """
    return self.__delegate.size

  @property
  def feedback_frequency(self):
    """The frequency of the internal feedback request + callback thread.

    :return: the frequency
    :rtype: float
    """
    return self.__delegate.feedback_frequency

  @feedback_frequency.setter
  def feedback_frequency(self, value: float):
    """Sets the frequency of the internal feedback request + callback thread.

    :param value: the new frequency, in hertz
    :type value: float
    """
    self.__delegate.feedback_frequency = value

  @property
  def command_lifetime(self):
    """The command lifetime for the modules in this group.

    :return: the command lifetime
    :rtype: int
    """
    return self.__delegate.command_lifetime

  @command_lifetime.setter
  def command_lifetime(self, value: int):
    """Set the command lifetime for the modules in this group.

    This parameter defines how long a module will execute a command set
    point sent to it. Note the commands from other systems/applications
    are ignored during this time. A value of ``0`` indicates commands last
    forever, and there is no lockout behavior.

    :param value: The command lifetime, in milliseconds
    :type value:  int
    """
    self.__delegate.command_lifetime = value

  def send_command(self, group_command: 'GroupCommand'):
    """Send a command to the given group without requesting an acknowledgement.
    This is appropriate for high-frequency applications.

    :param group_command: The command to send
    :type group_command:  GroupCommand

    :return: ``True`` if succeeded, ``False`` otherwise
    :rtype:  bool
    """
    return self.__delegate.send_command(group_command)

  def send_command_with_acknowledgement(self, group_command: 'GroupCommand', timeout_ms: 'int | None' = None) -> bool:
    """Send a command to the given group, requesting an acknowledgement of
    transmission to be sent back.

    Note: A non-true return does not indicate a specific failure, and may
    result from an error while sending or simply a timeout/dropped response
    packet after a successful transmission.

    :param group_command: The command to send
    :type group_command:  GroupCommand

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :return: ``True`` if succeeded, ``False`` otherwise
    :rtype:  bool
    """
    return self.__delegate.send_command_with_acknowledgement(group_command,
                                                             timeout_ms)

  @overload
  def send_layout(self, *, layout_file: 'str', timeout_ms: 'int | None' = None) -> bool: ...

  @overload
  def send_layout(self, *, layout: 'list[dict]', timeout_ms: 'int | None' = None) -> bool: ...

  def send_layout(self, layout_file: 'str | None' = None, layout: 'list[dict] | None' = None, timeout_ms: 'int | None' = None) -> bool:
    """Send a layout configuration to the given group. Pass either layout_file
    or layout.

    Note: A non-true return does not indicate a specific failure, and may
    result from an error while sending or simply a timeout/dropped response
    packet after a successful transmission.

    :param layout_file: The path of a layout file to send to MobileIO
    :type layout_file:  str

    :param layout: The contents of a layout file as a list of dictionaries
    :type layout:  [dict]

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :return: ``True`` if succeeded, ``False`` otherwise
    :rtype:  bool
    """
    return self.__delegate.send_layout(layout_file, layout, timeout_ms)

  def send_feedback_request(self):
    """Requests feedback from the group.

    Sends a background request to the modules in the group; if/when all modules
    return feedback, any associated handler functions are called. This returned
    feedback is also stored to be returned by the next call to
    :meth:`.get_next_feedback` (any previously returned data is discarded).

    :return: ``True`` if succeeded, ``False`` otherwise
    :rtype:  bool
    """
    return self.__delegate.send_feedback_request()

  def get_next_feedback(self, timeout_ms: 'float | None' = None, reuse_fbk: 'GroupFeedback | None' = None):
    """Returns the most recently stored feedback from a sent feedback request,
    or the next one received (up to the requested timeout).

    Note that a feedback request can be sent either with the
    send_feedback_request function, or by setting a background feedback
    frequency with :attr:`.feedback_frequency`.

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :param reuse_fbk: An optional parameter which can be used to reuse
                      an existing GroupFeedback instance. It is recommended
                      to provide this parameter inside a repetitive loop,
                      as reusing feedback instances results in substantially
                      fewer heap allocations.
    :type reuse_fbk:  GroupFeedback

    :return: The most recent feedback, provided one became available before the
             timeout. ``None`` is returned if there was no available feedback.
    :rtype:  GroupFeedback
    """
    return self.__delegate.get_next_feedback(timeout_ms, reuse_fbk)

  def request_info(self, timeout_ms: 'float | None' = None, reuse_info: 'GroupInfo | None' = None):
    """Request info from the group, and store it in the passed-in info object.

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :param reuse_info: An optional parameter which can be used to reuse
                       an existing GroupInfo instance. It is recommended
                       to provide this parameter inside a repetitive loop,
                       as reusing info instances results in substantially
                       fewer heap allocations.
    :type reuse_info:  GroupInfo

    :return: the updated info on success, ``None`` otherwise
    :rtype:  GroupInfo
    """
    return self.__delegate.request_info(timeout_ms, reuse_info)

  def request_info_extra(self, timeout_ms: 'float | None' = None, reuse_info: 'GroupInfo | None' = None):
    """Request info from the group, and store it in the passed-in info object.

    Extra info includes networking info and userdata. These fields are not populated using
    the base request_info call to avoid excessive traffic on the network.

    :param timeout_ms: The maximum amount of time to wait, in milliseconds.
                       This is an optional parameter with a default value of
                       :attr:`Group.DEFAULT_TIMEOUT_MS`.
    :type timeout_ms:  int

    :param reuse_info: An optional parameter which can be used to reuse
                       an existing GroupInfo instance. It is recommended
                       to provide this parameter inside a repetitive loop,
                       as reusing info instances results in substantially
                       fewer heap allocations.
    :type reuse_info:  GroupInfo

    :return: the updated info on success, ``None`` otherwise
    :rtype:  GroupInfo
    """
    return self.__delegate.request_info(timeout_ms, reuse_info, request_extra_info=True)

  def start_log(self, directory: 'str | None' = None, name: 'str | None' = None, mkdirs: bool = False):
    """Start logging information and feedback from this group.

    If a log file was already started before this (and not stopped using :meth:`.stop_log`),
    then that file will be gracefully closed.

    Note that the `directory` folder must exist if `mkdirs` is not ``True``

    :param directory: Optional directory into which the log file will be created.
                      If ``None``, the process' current working directory is used.
    :type directory:  str

    :param name: Optional name of the log file.
                 If ``None``, a name will be generated using the time
                 at which this function was invoked.
    :type name:  str

    :param mkdirs: Optional flag denoting if the base path represented by `directory` should be created,
                   if they do not exist
    :type mkdirs:  bool

    :return: The path, including the file, of the log file. Never ``None``.
    :rtype:  str

    :raises IOError: If the group could not start logging
    """
    if directory is not None:
      if mkdirs:
        safe_mkdirs(directory)
      elif not os.path.isdir(directory):
        raise IOError(f"Could not start logging because directory '{directory}' does not exist and 'mkdirs=False'")

    ret = self.__delegate.start_log(directory, name)
    if ret is None:
      raise IOError("Could not start logging")
    return ret

  def stop_log(self):
    """Stop logging data into the last opened log file. If no log file was
    opened, None will be returned. If an error occurs while stopping the
    previously started log file, None will be returned.

    :return: a LogFile object on success, or None
    :rtype: LogFile
    """
    return self.__delegate.stop_log()

  def log_user_state(self,
                     v1: 'float | None' = None,
                     v2: 'float | None' = None,
                     v3: 'float | None' = None,
                     v4: 'float | None' = None,
                     v5: 'float | None' = None,
                     v6: 'float | None' = None,
                     v7: 'float | None' = None,
                     v8: 'float | None' = None,
                     v9: 'float | None' = None):
    """Writes values to the active log as a UserState, which can be viewed in the Scope log viewer.
    If an error occurs while writing to the log, returns False.

    :rtype: bool
    """
    return self.__delegate.log_user_state(v1, v2, v3, v4, v5, v6, v7, v8, v9)

  def add_feedback_handler(self, handler: 'Callable[[GroupFeedback], None]'):
    """Adds a handler function to be called by the internal feedback request
    thread.

    Note that this function must execute very quickly:
    If a handler takes more time than the reciprocal of the feedback
    thread frequency, the thread will saturate in feedback events to dispatch.
    This may cause feedback packets to be dropped from handler dispatch,
    or delayed invocation of the feedback handlers.

    :param handler: A function which is able to accept a single argument
    """
    self.__delegate.add_feedback_handler(handler)

  def clear_feedback_handlers(self):
    """Removes all feedback handlers presently added."""
    self.__delegate.clear_feedback_handlers()


# Destroy all GroupDelegate objects on exit.
# This ensures that the feedback handlers cannot be invoked while Python is finalizing.
# This allows Python to exit gracefully, while also additionally allowing any potentially
# open log files to gracefully be closed and validated (preventing corruption).
__register(GroupDelegate.destroy_all_instances)
