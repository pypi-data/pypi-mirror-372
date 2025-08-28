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

import logging
import os

def configure_logging():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-5.5s [%(name)s][pid:%(process)s tid:%(thread)s] %(message)s'
    )
    handler.setFormatter(formatter)

    log_level = (os.getenv('DSTOOLKIT_LOG_LEVEL') or 'INFO').upper()
    log_level = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger('atlasai.toolkit')
    logger.setLevel(log_level)
    logger.addHandler(handler)
