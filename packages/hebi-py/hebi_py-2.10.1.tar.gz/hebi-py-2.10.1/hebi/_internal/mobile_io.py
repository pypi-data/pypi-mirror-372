from .ffi._message_types import GroupCommand, GroupFeedback
from .group import Group
from .graphics import Color


class MobileIO:
  """Wrapper around a mobile IO controller."""

  __slots__ = ('_group', '_cmd', '_fbk', '_last_button_state', '_layout_url')

  def __init__(self, group: Group, layout_url: 'str | None' = None):
    self._group = group
    self._cmd = GroupCommand(group.size)
    self._fbk = GroupFeedback(group.size)
    self._last_button_state = [0] * 8
    self._layout_url = layout_url

  def __repr__(self):
    def btn_repr(btn):
      ret = f'  Button {btn}: {self.get_button_state(btn)} ({self.get_button_diff(btn)})\n'
      return ret

    def axis_repr(axis):
      ret = f'  Axis {axis}:   {self.get_axis_state(axis)}\n'
      return ret

    ret = 'MobileIO:\n'
    for i in range(8):
      ret += btn_repr(i+1)
    for i in range(8):
      ret += axis_repr(i+1)
    return ret

  def update(self, timeout_ms: 'float | None' = None):
    """Updates the button and axis values and state. Returns ``False`` if
    feedback could not be received.

    :rtype:  bool
    :return: ``True`` on success; ``False`` otherwise
    """
    # save button states before updating feedback
    b_bank = self._fbk[0].io.b
    for i in range(8):
      self._last_button_state[i] = b_bank.get_int(i+1)

    if self._group.get_next_feedback(timeout_ms=timeout_ms, reuse_fbk=self._fbk) is None:
      return False

    return True

  def resetUI(self):
    """Resets button and axis values and state to defaults. Returns ``False``
    if feedback could not be received.

    :rtype:  bool
    :return: ``True`` on success; ``False`` otherwise
    """
    for i in range(8):
      # sliders
      self._cmd.io.a.set_float(i+1, 0.0) # snap
      self._cmd.io.f.set_float(i+1, 0.0) # value
      self._cmd.io.a.set_label(i+1, f'A{i+1}')
      # buttons
      self._cmd.io.b.set_int(i+1, 0) # mode
      self._cmd.io.e.set_int(i+1, 0) # output
      self._cmd.io.b.set_label(i+1, f'B{i+1}')
    self._cmd.clear_log = True
    self._cmd.led.color = 'transparent'
    res = self._group.send_command_with_acknowledgement(self._cmd)
    self._cmd.clear()
    return res

  def send_layout(self, *, layout_file: 'str | None' = None, layout = None, timeout_ms: 'int | None' = None):
    """Sends a new layout configuration to the mobileIO device. Either pass the
    path to a json file as ``layout_file``, or a Python object representing the json structure as ``layout``

    :param layout_file: The path of a layout file to send to MobileIO
    :type layout_file:  str

    :param layout: The json contents of a layout file as a string
    :type layout:  str

    :rtype:  bool
    :return: ``True`` on success; ``False`` otherwise
    """

    if not self._layout_url:
      return False

    if layout_file is not None and layout is not None:
      raise ValueError('Should not provide "layout" and "layout_file" parameters at the same time')
    elif layout_file is not None:
      return self._group.send_layout(layout_file=layout_file, timeout_ms=timeout_ms)
    elif layout is not None:
      return self._group.send_layout(layout=layout, timeout_ms=timeout_ms)
    else:
      raise ValueError('Should provide either "layout" or "layout_file" parameter, both are None')

  def get_button_diff(self, index: int):
    """Retrieve the current diff of the specified button.

    Note that this method uses 1-indexing.

    :param index: The index of the button (indices starting at 1).
    :type index:  int

    :rtype: int
    :return: ``0`` if value has not changed, ``+/-1`` for edge triggers
    """
    return self.get_button_state(index) - self._last_button_state[index-1]

  def get_button_state(self, index: int):
    """Retrieve the current (pressed/unpressed) state of the specified button.

    Note that this method uses 1-indexing.

    :param index: The index of the button (indices starting at 1).
    :type index:  int

    :rtype: bool
    """
    if index < 1 or index > 8:
      raise IndexError("index must be between 1 and 8 inclusive")
    return bool(self._fbk[0].io.b.get_int(index))

  def get_axis_state(self, index: int) -> float:
    """Retrieve the current state of the specified axis.

    Note that this method uses 1-indexing.

    :param index: The index of the axis (indices starting at 1).
    :type index:  int

    :rtype: float
    """
    if index < 1 or index > 8:
      raise IndexError("index must be between 1 and 8 inclusive")
    return self._fbk[0].io.a.get_float(index)

  def set_snap(self, slider: int, value: float):
    """Set the snap position on a slider.

    Note that this method uses 1-indexing.

    :param slider: The index of the slider to modify (indices starting at 1)
    :type slider:  int

    :param value: The value to set. Note that this will be converted to a `float`.
    :type value:  int, float

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    self._cmd.io.a.set_float(slider, value)
    retval = self._group.send_command_with_acknowledgement(self._cmd)
    # Clear this so other "set" commands (color, etc) don't keep setting the snap
    self._cmd.io.a.set_float(slider, None)
    return retval

  def set_axis_value(self, slider: int, value: float):
    """Set the position on a slider.

    Note that this method uses 1-indexing.

    :param slider: The index of the slider to modify (indices starting at 1)
    :type slider:  int

    :param value: The value to set. Note that this will be converted to a `float`.
    :type value:  int, float

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    self._cmd.io.f.set_float(slider, value)
    retval = self._group.send_command_with_acknowledgement(self._cmd)
    # Clear this so other "set" commands (color, etc) don't keep setting the value
    self._cmd.io.f.set_float(slider, None)
    return retval

  def set_button_mode(self, button: int, value: 'int | str'):
    """Set the mode of the specified button to momentary or toggle.

    Note that this method uses 1-indexing.

    :param button: The index of the button to modify (indices starting at 1).
    :type button:  int

    :param value: The value to set.
                  Momentary corresponds to ``0`` (default) and toggle corresponds to ``1``.
                  This parameter allows the strings 'momentary' and 'toggle'
    :type value:  int, str

    :raises ValueError: If `value` is an unrecognized string

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    if isinstance(value, str):
      if value == 'momentary':
        value = 0
      elif value == 'toggle':
        value = 1
      else:
        raise ValueError(f"Unrecognized string value {value}")
    self._cmd.io.b.set_int(button, value)
    return self._group.send_command_with_acknowledgement(self._cmd)

  def set_button_output(self, button: int, value: int):
    """Set the button output behavior (indicator ring on or off).

    Note that this method uses 1-indexing.

    :param button: The index of the button to modify (indices starting at 1).
    :type button:  int

    :param value: The value to set.
                  To illuminate the indicator ring, use ``1``. To hide it, use ``0``.
    :type value:  int

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    self._cmd.io.e.set_int(button, value)
    return self._group.send_command_with_acknowledgement(self._cmd)

  def set_led_color(self, color: 'Color | int | str', blocking: bool = True):
    """Set the edge led color.

    :param color: The color to which the edge color is set. Certain strings are recognized as colors.
                  Reference :py:attr:`~hebi.GroupCommand.led` for a complete list of allowed colors.
    :type color:  int, str

    :param blocking: If ``True``, block for acknowledgement from the device. Otherwise, return as quickly as possible.
    :type blocking:  bool

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    self._cmd.led.color = color
    ret = False
    if blocking:
      ret = self._group.send_command_with_acknowledgement(self._cmd)
    else:
      ret = self._group.send_command(self._cmd)
    self._cmd.led.clear()
    return ret

  def add_text(self, message: str, blocking: bool = True):
    """Append a message to the text display.

    :param message: The string to append to the display
    :type message:  str

    :param blocking: If ``True``, block for acknowledgement from the device. Otherwise, return as quickly as possible.
    :type blocking:  bool

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    self._cmd.append_log = message
    retval = None
    if blocking:
      retval = self._group.send_command_with_acknowledgement(self._cmd)
    else:
      retval = self._group.send_command(self._cmd)
    # clear field so string isn't repeat appended
    self._cmd.append_log = None
    return retval

  def clear_text(self, blocking: bool = True):
    """Clear the text display.

    :param blocking: If ``True``, block for acknowledgement from the device. Otherwise, return as quickly as possible.
    :type blocking:  bool

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    self._cmd.clear_log = True
    retval = None
    if blocking:
      retval = self._group.send_command_with_acknowledgement(self._cmd)
    else:
      retval = self._group.send_command(self._cmd)
    self._cmd.clear_log = False
    return retval

  def set_button_label(self, button: int, label: str, blocking: bool = True):
    self._cmd.io.b.set_label(button, label)
    if blocking:
      return self._group.send_command_with_acknowledgement(self._cmd)
    return self._group.send_command(self._cmd)

  def set_axis_label(self, axis: int, label: str, blocking: bool = True):
    self._cmd.io.a.set_label(axis, label)
    if blocking:
      return self._group.send_command_with_acknowledgement(self._cmd)
    return self._group.send_command(self._cmd)

  def send_vibrate(self, blocking: bool = True):
    """Send a command to vibrate the device. Note that this feature depends on
    device support. If the device does not support programmatic vibrating, then
    this will be a no-op.

    :param blocking: If ``True``, block for acknowledgement from the device. Otherwise, return as quickly as possible.
    :type blocking:  bool

    :rtype: bool
    :return: ``True`` if the device received the command and successfully sent an acknowledgement; ``False`` otherwise.
    """
    self._cmd.effort = 1
    if blocking:
      return self._group.send_command_with_acknowledgement(self._cmd)
    return self._group.send_command(self._cmd)

  def get_last_feedback(self):
    """Retrieve the last receieved feedback from the mobile IO device.

    :rtype: hebi._internal.ffi._message_types.Feedback
    """
    return self._fbk[0]

  @property
  def position(self):
    """Retrieve the AR position of the mobile IO device.

    Note that this will only return valid data if the device supports an AR framework.

    :rtype: numpy.ndarray
    """
    return self._fbk[0].ar_position

  @property
  def orientation(self):
    """Retrieve the AR orientation of the mobile IO device.

    Note that this will only return valid data if the device supports an AR framework.

    :rtype: numpy.ndarray
    """
    return self._fbk[0].ar_orientation
