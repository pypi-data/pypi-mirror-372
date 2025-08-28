"""
This package contains the hansken extraction plugin framework.

It is split into four submodules:

  * `api`, which contains the api of the classes that are used when implementing an extraction plugin.
  * `framework`, which contains the generated gRPC code to communicate with the remote (Hansken).
  * `runtime`, which contains implementations of the api.
  * `test_framework`, which contains code to test extraction plugins with known input and outputs.

Copyright 2021-2024 Netherlands Forensic Institute

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from importlib import metadata
import sys

import logbook  # type: ignore

try:
    # reads the installed package version, defined by setup.py
    __version__ = metadata.version('hansken_extraction_plugin')
except metadata.PackageNotFoundError:
    # when running inside a build env, like a virtualenv (tox, IDE), no version
    # information is available, so use a fixed version 'development'
    __version__ = 'development'

# Log to stdout
log_handler = logbook.StreamHandler(sys.stdout, level='WARNING', bubble=True)
log_handler.push_application()

# redirect all calls to logging to logbook
logbook.compat.redirect_logging()

logbook.set_datetime_format('utc')
