
import sys
if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
  from time import perf_counter as _get_time
else:
  from time import time as _get_time
from time import strftime


import numpy as np
import threading


class _HebiProfilerTLS_Data:

  __slots__ = ['_func_name', '_start_time', '_func_stats']

  def __init__(self):
    self._func_name = None
    self._start_time = None
    self._func_stats = dict()
    from .loader import _c_api_functions
    for entry in _c_api_functions:
      self._func_stats[entry.name] = list()

  @property
  def func_name(self):
    return self._func_name

  @func_name.setter
  def func_name(self, value):
    self._func_name = value

  @property
  def start_time(self):
    return self._start_time

  @start_time.setter
  def start_time(self, value: float):
    self._start_time = value

  @property
  def func_stats(self):
    return self._func_stats


class _HebiProfilerTLS(threading.local):
  """Thread local storage for the internal profiler."""

  def __init__(self):
    self._data = _HebiProfilerTLS_Data()

  @property
  def data(self):
    return self._data


_profiler_tls = _HebiProfilerTLS()


class _SimpleHEBIProfiler:
  """A simple profiler used to profile how long calls into HEBI C API take.

  Note: this works on a per thread basis and is currently an internal API.
  """

  def __init__(self):
    pass

  def enter(self, func_name):
    tls_data = _profiler_tls.data
    tls_data.func_name = func_name
    tls_data.start_time = _get_time()

  def exit(self):
    tls_data = _profiler_tls.data
    if tls_data.start_time is not None:
      tls_data.func_stats[tls_data.func_name].append(_get_time()-tls_data.start_time)

  def _write_entry(self, f, func_name):
    tls_data = _profiler_tls.data
    entries = tls_data.func_stats[func_name]
    if len(entries) == 0:
      return
    entries = np.array(entries)
    min_val = np.amin(entries)
    max_val = np.amax(entries)
    mean = np.mean(entries)
    stddev = np.std(entries)
    count = entries.size
    pct_90 = np.percentile(entries, 90)
    pct_95 = np.percentile(entries, 95)
    pct_99 = np.percentile(entries, 99)
    cumulative = np.sum(entries)
    f.write(f'{func_name},{count},{cumulative},{mean},{min_val},{max_val},{stddev},{pct_90},{pct_95},{pct_99}\n')

  def dump_stats(self, path=None):
    if path is None:
      thd = threading.current_thread()
      path = f"{strftime('%m_%d_%y_%H-%M-%S')}_{thd.name}-{thd.ident}_c_profile.csv"

    tls_data = _profiler_tls.data
    with open(path, 'w') as f:
      f.write('function,count,cumulative,avg,min,max,stddev,90pct,95pct,99pct\n')
      for func_name in tls_data.func_stats.keys():
        self._write_entry(f, func_name)


_C_API_profiler = _SimpleHEBIProfiler()


def enter_c_func(func_name):
  _C_API_profiler.enter(func_name)


def exit_c_func():
  _C_API_profiler.exit()


def dump_c_api_stats(path=None):
  _C_API_profiler.dump_stats(path)
