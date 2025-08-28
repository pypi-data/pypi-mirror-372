# Copyright 2025 AtlasAI PBC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# flake8: noqa
import os
import os.path as osp

from dotenv import load_dotenv

# do this first!
from .init import configure_logging
configure_logging()
del configure_logging

env_file = osp.join(osp.dirname(__file__), '.env')
if osp.exists(env_file):
    load_dotenv(env_file)

del load_dotenv
del env_file
del osp
del os


from . import fabric, feature, dataset, model, workflows
from .login import login, logout
