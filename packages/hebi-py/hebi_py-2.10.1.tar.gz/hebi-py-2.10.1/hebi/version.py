from os.path import join, dirname

import typing
if typing.TYPE_CHECKING:
  from typing import Any


HEBI_PY_VERSION = '2.10.1'
HEBI_MIN_C_API_VERSION = '2.21.0'


def parse_version(s: str):
  split = s.split('.')
  #if len(split) > 3:
  #  raise ValueError(f"Period characters are not allowed in the suffix portion of the version string `{s}`")
  if len(split) < 3:
    raise ValueError(f"Malformed version string `{s}`")

  import re
  r = re.compile(r"^(\d+)([a-zA-Z_0-9-]+)?$")
  patch_str = split[2]
  patch_parts = r.split(patch_str)
  parts: 'list[str]' = []
  for entry in patch_parts:
    if entry != '':
      parts.append(entry)

  if len(parts) > 2 or len(parts) == 0:
    raise ValueError(s)
  elif len(parts) == 1:
    return Version(int(split[0]), int(split[1]), int(parts[0]))
  return Version(int(split[0]), int(split[1]), int(parts[0]), parts[1])


class Version:
  def __init__(self, maj: int, min: int, rev: int, suffix: 'str | None' = None):
    """Suffix string must only contain the following:

      * Underscore
      * Hyphen
      * alphabetical character (lower or uppercase) as determined by `[a-zA-Z]
      * numbers as determined by `[0-9]` or `\\d`

    Note that periods (`.`) are not allowed in the suffix.
    """
    self._major_version = maj
    self._minor_version = min
    self._patch_version = rev
    self._suffix = suffix or ''

  def __str__(self):
    return f'{self.major_version}.{self.minor_version}.{self.patch_version}{self.suffix}'

  def __repr__(self):
    return f'Version(major: {self.major_version}, minor: {self.minor_version}, patch: {self.patch_version}, suffix: {self.suffix})'

  def __eq__(self, o: 'Any') -> bool:
    if isinstance(o, Version):
      thiz_suffix = self._suffix or ''
      o_suffix = o._suffix or ''
      ret = o.major_version == self.major_version and \
          o.minor_version == self.minor_version and \
          o.patch_version == self.patch_version and \
          thiz_suffix == o_suffix
      return ret
    elif isinstance(o, str):
      return parse_version(o) == self
    else:
      return False

  def __ne__(self, o: 'Any') -> bool:
    if isinstance(o, Version):
      thiz_suffix = self._suffix or ''
      o_suffix = o._suffix or ''
      return o.major_version != self.major_version or \
          o.minor_version != self.minor_version or \
          o.patch_version != self.patch_version or \
          thiz_suffix != o_suffix
    else:
      return self != parse_version(o)

  def __gt__(self, o: 'Any') -> bool:
    if isinstance(o, Version):
      if self.major_version > o.major_version:
        return True
      elif self.major_version < o.major_version:
        return False
      elif self.minor_version > o.minor_version:
        return True
      elif self.minor_version < o.minor_version:
        return False
      elif self.patch_version > o.patch_version:
        return True
      elif self.patch_version < o.patch_version:
        return False
      thiz_suffix = self._suffix or ''
      o_suffix = o._suffix or ''
      return thiz_suffix > o_suffix
    elif isinstance(o, str):
      return self > parse_version(o)
    else:
      raise TypeError()

  def __lt__(self, o: 'Any') -> bool:
    if isinstance(o, Version):
      if self.major_version < o.major_version:
        return True
      elif self.major_version > o.major_version:
        return False
      elif self.minor_version < o.minor_version:
        return True
      elif self.minor_version > o.minor_version:
        return False
      elif self.patch_version < o.patch_version:
        return True
      elif self.patch_version > o.patch_version:
        return False
      thiz_suffix = self._suffix or ''
      o_suffix = o._suffix or ''
      return thiz_suffix < o_suffix
    elif isinstance(o, str):
      return self < parse_version(o)
    else:
      raise TypeError()

  @property
  def major_version(self):
    return self._major_version

  @property
  def minor_version(self):
    return self._minor_version

  @property
  def patch_version(self):
    return self._patch_version

  @property
  def suffix(self):
    return self._suffix


def read_version_file(relPath: str):
  return parse_version(open(join(dirname(__file__), relPath), 'r').read().strip())


def py_version():
  return parse_version(HEBI_PY_VERSION)


def min_c_api_version():
  return parse_version(HEBI_MIN_C_API_VERSION)


def loaded_c_api_version():
  from ._internal.ffi.loader import _handle
  return _handle.version


if __name__ == "__main__":
  import argparse

  def __disp(txt, vfunc):
    print(f'{txt}: {vfunc()}')

  parser = argparse.ArgumentParser()
  parser.add_argument("--min-c-api", help="Show minimum required C API version",
                      default=False, action="store_true")
  parser.add_argument("--py-api", help="Show the version of hebi-py",
                      default=False, action="store_true")
  args = parser.parse_args()
  if args.min_c_api:
    __disp('Minimum C API Version', min_c_api_version)
  if args.py_api:
    __disp('hebi-py Version', py_version)
