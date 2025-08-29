from os.path import join, dirname, realpath, abspath
from platform import architecture, machine
from ctypes import CDLL

from .. import debug

import typing
if typing.TYPE_CHECKING:
  pass


class HEBICoreLibrary:
  """Loads the C API functions.

  Do not use.
  """
  __slots__ = ['__core_api_version', 'core_lib', '__core_location']

  def __init__(self, core_lib: CDLL, core_location: str):
    self.core_lib = core_lib
    self.__core_location = core_location

    from .ctypes_loader import populate_hebi_funcs, populate_hebi_wrapper_funcs
    populate_hebi_funcs(core_lib)
    populate_hebi_wrapper_funcs(core_lib)

    from .. import Version, min_c_api_version
    self.__core_api_version = Version(-1, -1, -1)

    from ctypes import byref, c_int32
    from .. import debug

    # Make sure to check for a compatible version of the C API first
    if hasattr(core_lib, 'hebiGetLibraryVersion'):
      c_api_version = min_c_api_version()
      c_min_major = c_api_version.major_version
      c_min_minor = c_api_version.minor_version
      c_min_patch = c_api_version.patch_version

      major_version = c_int32(0)
      minor_version = c_int32(0)
      patch_version = c_int32(0)
      core_lib.hebiGetLibraryVersion(byref(major_version), byref(minor_version), byref(patch_version))

      req_str = f'{c_min_major}.{c_min_minor}.{c_min_patch}'
      cur_str = f'{major_version.value}.{minor_version.value}.{patch_version.value}'
      debug.debug_log(f'hebiGetLibraryVersion() ==> {cur_str}')

      if major_version.value != 2:
        # Refuse to load anything which is not a 2.x.x binary
        raise RuntimeError(f"C API library must be a 2.x.x release (loaded version {cur_str})")

      if cur_str < req_str:
        print('Warning: loaded C library may be incompatible, as it is an outdated library. ' +
              f'Loaded library version is {cur_str}, required minimum is {req_str}')

      self.__core_api_version._major_version = major_version.value
      self.__core_api_version._minor_version = minor_version.value
      self.__core_api_version._patch_version = patch_version.value

    from .ctypes_defs import HebiCommandMetadata, HebiFeedbackMetadata, HebiInfoMetadata

    command_metadata = HebiCommandMetadata()
    feedback_metadata = HebiFeedbackMetadata()
    info_metadata = HebiInfoMetadata()

    core_lib.hebiCommandGetMetadata(byref(command_metadata))
    core_lib.hebiFeedbackGetMetadata(byref(feedback_metadata))
    core_lib.hebiInfoGetMetadata(byref(info_metadata))

  def __del__(self):
    self.core_lib.hebiCleanup()

  @property
  def core_lib_location(self) -> str:
    return self.__core_location

  @property
  def version(self):
    from .. import Version
    maj_v = self.__core_api_version.major_version
    min_v = self.__core_api_version.minor_version
    pat_v = self.__core_api_version.patch_version
    return Version(maj_v, min_v, pat_v)


class SharedLibraryLoader:
  def __init__(self, library: str):
    self._candidates: 'list[str]' = list()
    self._library = library

  def add_candidate(self, loc: str):
    self._candidates.append(loc)

  @property
  def candidates(self):
    return self._candidates

  def try_load_library(self):
    """Goes through all candidate libraries in priority order.

    :return: a tuple (pair): `ctypes` object representing the library, along with the file path of the library
    """
    candidates = self.candidates
    candidate_count = len(candidates)
    debug.debug_log(f"Loading library {self._library}.")
    debug.debug_log(f"Loader(library={self._library}): {candidate_count} candidate binaries:")
    debug.debug_log(f"Loader(library={self._library}): Candidate binaries, in order of priority:")

    # Loop twice so all candidate libraries can be printed to debug stream in case of debugging enabled
    for i, candidate in enumerate(candidates):
      debug.debug_log(f"Candidate {i+1}: {candidate}")

    from ctypes import cdll
    for candidate in candidates:
      try:
        lib = cdll.LoadLibrary(candidate)
        debug.debug_log(f'Successfully loaded library at {candidate}')
        return lib, candidate
      except Exception as e:
        debug.debug_log(f"Attempting to load library {candidate} raised exception:\n{e}")

    debug.warn_log(f"Unable to load (library={self._library}).\nCandidate libraries attempted (in order):")
    for i, candidate in enumerate(candidates):
      debug.warn_log(f"Candidate {i+1}: {candidate}")
    return None, None


def _get_library_load_candidates(library: str, readable_name: str, env_var: 'str | None' = None):
  ret: 'list[str]' = list()
  from os import environ
  import sys

  # Top priority: environment variables (if set)
  if env_var is not None:
    environ_val = environ.get(env_var)
    if environ_val is not None:
      debug.debug_log(f"{readable_name} library candidate '{environ_val}' from {env_var} environment variable")
      ret.append(environ_val)

  # Lower priority: load from installed package
  lib_base_path = abspath(join(join(dirname(realpath(__file__)), '..', '..'), 'lib'))

  from hebi import version
  c_api_version = version.min_c_api_version()
  maj_ver = c_api_version.major_version
  min_ver = c_api_version.minor_version

  if sys.platform.startswith('linux'):
    _find_linux_candidates(ret, lib_base_path, maj_ver, min_ver, library)
  elif sys.platform == 'darwin':
    _find_mac_candidates(ret, lib_base_path, maj_ver, library)
  elif sys.platform == 'win32':
    _find_win_candidates(ret, lib_base_path, library)

  return ret


def _load_shared_library(name: str, readable_name: str, env_var: 'str | None' = None):
  loader = SharedLibraryLoader(name)

  for entry in _get_library_load_candidates(name, readable_name, env_var):
    loader.add_candidate(entry)

  loaded_c_lib, loaded_loc = loader.try_load_library()
  if loaded_c_lib is None:
    raise RuntimeError(f'{readable_name} library not found')

  assert loaded_loc is not None
  return loaded_c_lib, loaded_loc


def _load_core_shared_library(): return _load_shared_library('hebi', 'HEBI Core', 'HEBI_C_LIB')


def _find_linux_candidates(output: 'list[str]', lib_base_path: str, maj_ver: int, min_ver: int, library: str):
  import re
  cpu = machine()
  py_exec_arch = architecture()[0]
  lib_str = f'lib{library}.so'

  if cpu == 'x86_64' and ('64' in py_exec_arch):
    # 64 bit x86 CPU with 64 bit python
    lib_path = join(lib_base_path, 'linux_x86_64', lib_str)

  elif ((re.match('i[3-6]86', cpu) is not None)
        or (cpu == 'x86_64') and ('32' in py_exec_arch)):
    raise RuntimeError('i686 is no longer supported. If you are on a 64 bit kernel, install and run an x86_64 instance of Python.')

  elif (re.match('arm.*', cpu) is not None) and ('32' in py_exec_arch):
    # 32 bit armhf with 32 bit python
    lib_path = join(lib_base_path, 'linux_armhf', lib_str)

  elif ((re.match('arm.*', cpu) is not None)
        or 'aarch64' in cpu and ('64' in py_exec_arch)):
    lib_path = join(lib_base_path, 'linux_aarch64', lib_str)
  elif 'aarch64' in cpu and ('32' in py_exec_arch):
    lib_path = join(lib_base_path, 'linux_armhf', lib_str)
  else:
    raise RuntimeError(f'Unknown architecture {cpu}')

  output.append(f'{lib_path}.{maj_ver}.{min_ver}')
  output.append(f'{lib_path}.{maj_ver}')
  output.append(lib_path)


def _find_mac_candidates(output: 'list[str]', lib_base_path: str, maj_ver: str, library: str):
  output.append(join(lib_base_path, 'osx', f'lib{library}.{maj_ver}.dylib'))
  output.append(join(lib_base_path, 'osx', f'lib{library}.dylib'))


def _find_win_candidates(output: 'list[str]', lib_base_path: str, library: str):
  cpu = machine()
  py_exec_arch = architecture()[0]

  if cpu == 'AMD64' or cpu == 'x86':
    # Windows doesn't like to make it easy to detect which architecture the process is running in (x86 vs x64)
    # You can use `ctypes` to detect this, but this is a more terse way.
    output.append(join(lib_base_path, 'win_x64', f'{library}.dll'))
    output.append(join(lib_base_path, 'win_x86', f'{library}.dll'))
  elif cpu == 'ARM':
    # XXX Not yet supported :(
    # 32 bit ARM on Windows
    raise RuntimeError('ARM is not yet supported on Windows')
  elif cpu == 'ARM64':
    # XXX Not yet supported :(
    # 64 bit ARM on Windows
    raise RuntimeError('ARM64 is not yet supported on Windows')
  else:
    raise RuntimeError(f'Unknown architecture {cpu}')


def _init_libraries():
  core_lib, core_loc = _load_core_shared_library()

  return HEBICoreLibrary(core_lib, core_loc)


# Load library on import
_handle = _init_libraries()
