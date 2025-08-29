# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------

from ._internal import log_file as _log_file
from ._internal import group as _group
from ._internal import mobile_io as _mobile_io

from os.path import isfile as _isfile

import typing
if typing.TYPE_CHECKING:
  from typing import Union, Any
  from ._internal.lookup import Lookup
  from hebi import GroupFeedback
  from ._internal.log_file import TimedGroupFeedback
  from ._internal.trajectory import Trajectory
  Loggable = Union[_log_file.LogFile, str]

try:
  import imp
  imp.find_module('matplotlib')
  _found_matplotlib = True


except ImportError:
  _found_matplotlib = False

if not _found_matplotlib:
  print('matplotlib not found - hebi.util.plot_logs and hebi.util.plot_trajectory will not work.')

try:
  from pynput import keyboard
except ImportError:
  print('pynput not found - HebiKeyboard will not work')


def create_imitation_group(size):
  """Create an imitation group of the provided size. The imitation group
  returned from this function provides the exact same interface as a group
  created from the :class:`Lookup` class.

  However, there are a few subtle differences between the imitation group and
  group returned from a lookup operation. See :ref:`imitation-group-contrast` section
  for more information.

  :param size: The number of modules in the imitation group
  :type size:  int

  :return: The imitation group. This will never be ``None``
  :rtype:  Group

  :raises ValueError: If size is less than 1
  """
  return _group.create_imitation_group(size)


def load_log(file: str, load: bool = True):
  """Opens an existing log file.

  :param file: the path to an existing log file
  :type file:  str, unicode

  :return: The log file. This function will never return ``None``
  :rtype:  LogFile

  :raises TypeError: If file is an invalid type
  :raises IOError: If the file does not exist or is not a valid log file
  """
  try:
    f_exists = _isfile(file)
  except TypeError as t:
    raise TypeError(f'Invalid type for file. Caught TypeError with message: {t.args}')

  if not f_exists:
    raise IOError(f'file {file} does not exist')

  from ._internal.ffi import api
  log_file = api.hebiLogFileOpen(file.encode('utf-8'))
  if log_file is None:
    raise IOError(f'file {file} is not a valid log file')

  log = _log_file.LogFile(log_file)
  if load:
    log.load()
  return log


def plot_logs(logs: 'Loggable | list[Loggable]', fbk_field: str, figure_spec: 'int | None' = None, modules: 'list[int] | None' = None):
  """Nicely formatted plotting of HEBI logs.

  :param logs: The log(s) (or file path to a log) to plot
  :type logs: list, LogFile, str

  :param fbk_field: Feedback field to plot
  :type fbk_field:  str

  :param figure_spec: The figure number you would like to use for plots. If multiple log files
            are plotted, then the subsequent figure numbers increment by 1 starting
            at `figure_spec`. If unspecified, a new figure will be created to avoid
            overwriting previous figures.
  :type figure_spec:  int

  :param modules: Optionally select which modules to plot
  :type modules: NoneType, list
  """
  from matplotlib import pyplot as plt
  if isinstance(logs, _log_file.LogFile) or isinstance(logs, str):
    logs = [logs]
  elif not isinstance(logs, list):
    raise TypeError(f'Parameter logs was of unexpected type {type(logs).__name__}')

  logfiles: 'list[str]' = []
  # First build list of filenames
  for i, entry in enumerate(logs[:]):
    if isinstance(entry, _log_file.LogFile) and entry.filename is not None:
      # Reload the log to not propagate out state change to input variables
      logfiles.append(entry.filename)
    elif not isinstance(entry, str):
      raise TypeError("All input entries must be a LogFile or string")
    else:
      logfiles.append(entry)

  # Load LogFiles
  loaded_logs = [load_log(lf) for lf in logfiles]

  from ._internal.field_bindings import get_field_info
  feedback_info = get_field_info(fbk_field)
  command_plot = feedback_info.snake_case in [
    'position', 'velocity', 'effort']

  for i, log in enumerate(loaded_logs):
    if modules is None:
      plot_mask = [int(j) for j in range(log.number_of_modules)]
    else:
      plot_mask = modules

    def get_y(entry: 'GroupFeedback | TimedGroupFeedback'):
      return feedback_info.get_field(entry)[plot_mask]

    if figure_spec is None:
      fig = plt.figure()
    else:
      curr_fig = figure_spec + i
      fig = plt.figure(curr_fig, clear=True)

    if command_plot:
      ax = plt.subplot(2, 1, 1)
      ax2 = plt.subplot(2, 1, 2)
      plt.sca(ax)
    else:
      ax = plt.axes()

    num_plots = len(plot_mask)

    x_module_series: 'list[list[Any]]' = list()
    y_module_series: 'list[list[Any]]' = list()
    cmd_module_series: 'list[list[Any]]' = list()
    diff_module_series: 'list[list[Any]]' = list()

    for _ in range(num_plots):
      x_module_series.append(list())
      y_module_series.append(list())
      cmd_module_series.append(list())
      diff_module_series.append(list())

    x_lim_max = 0
    x_lim_min = None

    if command_plot:
      cmd_info = get_field_info(feedback_info.snake_case + "_command")
      def get_cmd(entry): return cmd_info.get_field(entry)[plot_mask]

      last_entry = None

      for entry in log.feedback_iterate:
        last_entry = entry
        entry_time = entry.time[plot_mask]
        entry_y = get_y(entry)
        entry_cmd = get_cmd(entry)

        if x_lim_min is None:
          x_lim_min = entry_time.min()

        for j in range(num_plots):
          x = entry_time[j]
          y = entry_y[j]
          cmd = entry_cmd[j]
          diff = y - cmd

          x_module_series[j].append(x)
          y_module_series[j].append(y)
          cmd_module_series[j].append(cmd)
          diff_module_series[j].append(diff)
      x_lim_max = last_entry.time[plot_mask].max()
    else:
      last_entry = None
      for entry in log.feedback_iterate:
        last_entry = entry
        entry_time = entry.time[plot_mask]
        entry_y = get_y(entry)

        if x_lim_min is None:
          x_lim_min = entry_time.min()

        for j in range(num_plots):
          x = entry_time[j]
          y = entry_y[j]
          x_module_series[j].append(x)
          y_module_series[j].append(y)
      x_lim_max = last_entry.time[plot_mask].max()

    y_label_unit_str = f' ({feedback_info.units})'

    for j in range(num_plots):
      plt.plot(x_module_series[j], y_module_series[j])

    plt.xlabel('time (sec)')
    plt.ylabel(feedback_info.pascal_case + y_label_unit_str)
    plt.title(f'{feedback_info.pascal_case} - Log {i+1} of {len(logs)}')
    plt.xlim(x_lim_min, x_lim_max)
    plt.grid(True)

    if command_plot:
      plt.sca(ax2)
      plt.xlabel('time (sec)')
      plt.ylabel('error' + y_label_unit_str)
      plt.title(f'{feedback_info.pascal_case} error')
      plt.xlim(x_lim_min, x_lim_max)
      plt.grid(True)

      for j in range(num_plots):
        plt.sca(ax)
        ax.ColorOrderIndex = 1
        plt.plot(x_module_series[j], cmd_module_series[j], '--')

        plt.sca(ax2)
        plt.plot(x_module_series[j], diff_module_series[j])

    plt.legend([str(mask) for mask in plot_mask])

  plt.tight_layout()
  plt.show()


def plot_trajectory(trajectory: 'Trajectory', dt=0.01, figure_spec=None, legend=None):
  """Visualizes position, velocity, and acceleration of a trajectory.

  :param trajectory:
  :type trajectory:  hebi.trajectory.Trajectory

  :param dt: Delta between points in trajectory to plot
  :type dt:  int, float

  :param figure_spec: The figure number or figure handle that should be used for plotting.
            If a figure with the specified number exists it will be overwritten.
            If left unspecified, a new figure will automatically be generated.
  :type figure_spec:  int, str

  :param legend: String of the text that gets displayed as the legend.
           By default it shows the joint number.
  :type legend:  str
  """
  from matplotlib import pyplot as plt
  import numpy as np

  if figure_spec is None:
    fig = plt.figure()
  elif isinstance(figure_spec, (int, str)):
    fig = plt.figure(num=figure_spec)
  else:
    raise TypeError(f'Parameter figure_spec was of unexpected type {type(figure_spec).__name__}.')

  if legend is None:
    # Joint number::: TODO
    legend = ''

  duration = trajectory.duration
  linear_times = np.arange(0.0, duration, dt)
  actual_times = trajectory.waypoint_times

  linear_pos = []
  linear_vel = []
  linear_acc = []
  actual_pos = []
  actual_vel = []
  actual_acc = []

  for i, t in enumerate(linear_times):
    p_t, v_t, a_t = trajectory.get_state(t)
    linear_pos.append(p_t)
    linear_vel.append(v_t)
    linear_acc.append(a_t)

  for i, t in enumerate(actual_times):
    p_t, v_t, a_t = trajectory.get_state(t)
    actual_pos.append(p_t)
    actual_vel.append(v_t)
    actual_acc.append(a_t)

  # NOTE:
  #   time          == linear_times
  #   waypointTime  == actual_times

  ax = plt.subplot(3, 1, 1)
  plt.plot(linear_times, linear_pos)
  ax.ColorOrderIndex = 1

  plt.plot(actual_times, actual_pos, marker='o')
  plt.title('Trajectory Profile')
  plt.ylabel('position (rad)')
  plt.xlabel('time (sec)')
  plt.grid(True)

  plt.legend(legend)

  ax = plt.subplot(3, 1, 2)
  plt.plot(linear_times, linear_vel)
  ax.ColorOrderIndex = 1
  plt.plot(actual_times, actual_vel, marker='o')
  plt.ylabel('velocity (rad/sec)')
  plt.xlabel('time (sec)')
  plt.grid(True)

  ax = plt.subplot(3, 1, 3)
  plt.plot(linear_times, linear_acc)
  ax.ColorOrderIndex = 1
  plt.plot(actual_times, actual_acc, marker='o')
  plt.ylabel('acceleration (rad/sec^2)')
  plt.xlabel('time (sec)')
  plt.grid(True)

  plt.tight_layout()
  plt.show()


def clear_all_groups():
  """Clear all groups currently allocated by the API.

  This is useful to clear up resources when running in an environment
  such as IPython.
  """
  from ._internal.group import GroupDelegate
  GroupDelegate.destroy_all_instances()


def create_mobile_io(lookup: 'Lookup', family='HEBI', name='mobileIO'):
  """Create a :class:`hebi._internal.mobile_io.MobileIO` instance with the
  specified family and name.

  :param lookup: An existing lookup instance to use to look for the mobile device
  :type lookup:  hebi.Lookup

  :param family: The family of the mobile IO device
  :type family:  str

  :param name: The name of the mobile IO device
  :type name:  str

  :return: the mobile IO instance, or `None` on failure
  :rtype:  hebi._internal.mobile_io.MobileIO
  """
  group = lookup.get_group_from_names([family], [name])
  if group is None:
    return None

  layout_url = "UNKNOWN"

  for elem in lookup.entrylist:
    if family == elem.family and name == elem.name:
      ip_addr = elem.ip_address
      layout_url = f'http://{ip_addr}/'
      break

  return _mobile_io.MobileIO(group, layout_url=layout_url)


class KeyboardIO:

  def __init__(self, keymap: 'dict[str, tuple[str, int | float]]'):
    self.listener = keyboard.Listener(
      on_press=self.on_press,
      on_release=self.on_release)

    self.keymap = keymap

    self.state = {
      'b1': 0,
      'b2': 0,
      'b3': 0,
      'b4': 0,
      'b5': 0,
      'b6': 0,
      'b7': 0,
      'b8': 0,
      'a1': 0,
      'a2': 0,
      'a3': 0,
      'a4': 0,
      'a5': 0,
      'a6': 0,
      'a7': 0,
      'a8': 0,
    }
    self.prev_state = self.state.copy()
    self.diff_state = self.state.copy()

    self.listener.start()


  def stop(self):
    self.listener.stop()


  def update(self):
    for k in self.state.keys():
      if 'b' in k:
        self.diff_state[k] = self.state[k] - self.prev_state[k]
        self.prev_state[k] = self.state[k]
    return True


  def set_led_color(self, color):
    return

  def add_text(self, text):
    return

  def clear_text(self):
    return

  def get_button_state(self, pin):
    return self.state[f'b{pin}']


  def get_button_diff(self, pin):
    return self.diff_state[f'b{pin}']


  def get_axis_state(self, pin):
    return self.state[f'a{pin}']


  def _update(self, pin, value):
    self.state[pin] = value


  def on_press(self, key):
    try:
      if key.char in self.keymap:
        value = self.keymap[key.char]
        self._update(value[0], value[1])

    except AttributeError:
      if key is keyboard.Key.shift:
        # Release all lower case keybinds because shift is pressed
        for k in self.keymap.keys():
          if k.islower():
            value = self.keymap[k]
            self._update(value[0], 0)

  def on_release(self, key):
    try:
      if key.char in self.keymap:
        value = self.keymap[key.char]
        self._update(value[0], 0)

    except AttributeError:
      if key is keyboard.Key.shift:
        # Release all upper case keybinds because shift is released
        for k in self.keymap.keys():
          if k.isupper():
            value = self.keymap[k]
            self._update(value[0], 0)

DEFAULT_KEYMAP = {
  '1': ('b1', 1),
  '2': ('b2', 1),
  '3': ('b3', 1),
  '4': ('b4', 1),
  '5': ('b5', 1),
  '6': ('b6', 1),
  '7': ('b7', 1),
  '8': ('b8', 1),

  # Left joystick
  'a': ('a1', -1.0),
  'd': ('a1',  1.0),
  's': ('a2', -1.0),
  'w': ('a2',  1.0),

  # Middle sliders
  'f': ('a3', -1.0),
  'r': ('a3',  1.0),
  'g': ('a4', -1.0),
  't': ('a4',  1.0),
  'h': ('a5', -1.0),
  'y': ('a5',  1.0),
  'j': ('a6', -1.0),
  'u': ('a6',  1.0),

  # Right joystick
  'k': ('a7', -1.0),
  ';': ('a7',  1.0),
  'l': ('a8', -1.0),
  'o': ('a8',  1.0),
}


def create_keyboard_io(keymap:'dict[str, tuple[str, int | float]] | None' = None):
  """Create a :class:`KeyboardIO` instance with the specified keymap

  :param keymap: A dictionary mapping 
  :type lookup:  dict

  :return: the keyboard IO instance
  :rtype:  hebi.util.KeyboardIO
  """

  if keymap is None:
    keymap = DEFAULT_KEYMAP

  return KeyboardIO(keymap)
