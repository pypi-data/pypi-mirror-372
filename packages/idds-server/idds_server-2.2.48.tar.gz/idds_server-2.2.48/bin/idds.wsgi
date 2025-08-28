#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0OA
#
# Authors:
# - Wen Guan, <wen.guan@cern.ch>, 2019

"""----------------------
   Web service startup
----------------------"""

import os
os.environ['IDDS_CONFIG'] = '/opt/hostedtoolcache/Python/3.13.7/x64/etc/idds/idds.cfg'

from idds.rest.v1.app import create_app  # noqa: E402


application = create_app()
