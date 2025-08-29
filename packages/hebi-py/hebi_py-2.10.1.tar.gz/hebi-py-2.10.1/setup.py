# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018-2019 HEBI Robotics
#  See http://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------

import re
from setuptools import setup, find_packages

with open('hebi/version.py') as f:
    api_version = re.search(r"HEBI_PY_VERSION = '(.*)'", f.read()).group(1)

api_reference_url = f"https://files.hebi.us/docs/python/{api_version}/"
changelog_url = "http://docs.hebi.us/downloads_changelogs.html#python-api-changelog"
documentation_url = "http://docs.hebi.us/tools.html#python-api"
license_url = "https://www.hebirobotics.com/softwarelicense"

description = f"""
HEBI Core Python API
====================

HEBI Python provides bindings for the HEBI Core library.

API Reference available at {api_reference_url}

Documentation available on [docs.hebi.us]({documentation_url}).

Refer to the [API changelog]({changelog_url}) for version history.

By using this software, you agree to our [software license]({license_url}).
"""


setup(name='hebi-py',
      version=api_version,
      long_description=description,
      long_description_content_type="text/markdown",
      packages=find_packages(),
      package_data={'hebi': [
          'lib/**/libhebi.so*',
          'lib/**/libhebi.*dylib',
          'lib/**/hebi.dll',
          '_internal/*',
          '_internal/ffi/*'
      ]},
      include_package_data=True,
      url='https://docs.hebi.us',
      project_urls={
          "API Reference": api_reference_url,
          "Changelog": changelog_url,
          "Documentation": documentation_url,
          "Examples": "https://github.com/HebiRobotics/hebi-python-examples"
      }
      )
