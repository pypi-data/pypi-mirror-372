# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2024 HEBI Robotics
#  See https://hebi.us/softwarelicense for license details
#
# ------------------------------------------------------------------------------

from dataclasses import dataclass
import yaml
import os

import typing
if typing.TYPE_CHECKING:
  from typing import Any


@dataclass
class HebiConfig:
  version: 'str'
  families: 'list[str]'
  names: 'list[str]'
  hrdf: 'str | None'
  gains: 'dict[str, str] | None'
  plugins: 'list[Any] | None'
  user_data: 'dict[str, Any] | None'
  config_location: 'str'


def load_config(cfg_file: str) -> HebiConfig:
  config = None

  cfg_file = os.path.abspath(cfg_file)
  cfg_dir = os.path.dirname(cfg_file)
  with open(cfg_file) as f:
    config = yaml.safe_load(f.read())

  if config is None:
    raise FileNotFoundError(f'Cannot find config file at path {cfg_file}')

  # Check if there are any other top level keys, this is not allowed
  # All extra fields should be added to 'user_data'
  allowed_keys = {'version', 'families', 'names', 'hrdf', 'gains', 'plugins', 'user_data'}
  if any(k not in allowed_keys for k in config.keys()):
    raise ValueError(f'Extra top levels sections detected: {config.keys() - allowed_keys}, not compliant with HEBI config file spec')

  version = config['version']
  version = str(version)

  families = config['families']
  if not isinstance(families, list):
    families = [families]

  names = config['names']
  if not isinstance(names, list):
    names = [names]

  hrdf = os.path.join(cfg_dir, config['hrdf']) if 'hrdf' in config else None

  gains = {}
  if 'gains' in config:
    if isinstance(config['gains'], str):
      gains['default'] = os.path.join(cfg_dir, config['gains'])
    elif isinstance(config['gains'], dict):
      for key in config['gains']:
        gains[key] = os.path.join(cfg_dir, config['gains'].get(key))
    else:
      raise TypeError('HEBI config "gains" field must be a single string or dictionary of gains files, not parseable as either')

  plugins = None
  if 'plugins' in config:
    if isinstance(config['plugins'], list):
      plugins = config['plugins']
    else:
      raise TypeError('HEBI config "plugins" field must be a list of plugins, not parseable as list')

  user_data = config['user_data'] if 'user_data' in config else None

  return HebiConfig(version,
                    families,
                    names,
                    hrdf,
                    gains,
                    plugins,
                    user_data,
                    cfg_dir)
