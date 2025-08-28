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

import uuid
import arrow

from . import api, constants, utils


def search(*args, **kwargs):
    fs = FabricSearch(*args, **kwargs)
    utils.show_page(fs.page)
    return fs

class FabricSearch:

    def __init__(self, id=None, *args, **kwargs):
        self.id = id or uuid.uuid4()
        self._search = None

    def __repr__(self):
        return f'FabricSearch({self.id})'

    def __str__(self):
        return f'FabricSearch({self.id})'

    @property
    def page(self):
        return f'{constants.DS_TOOLKIT_URL}/fabric/search/{self.id}'

    @property
    def search(self):
        return self._search

    def refresh(self):
        if self._search is None:
            self._search = self._refresh()
        else:
            new_version = self._info()
            # new updates ? pull them
            if arrow.get(new_version['update_date']) > arrow.get(self._search['update_date']):
                self._search = self._refresh()
        return self._search

    def info(self):
        return self._info()

    def _info(self):
        resource = f'fabric/search/{self.id}/info'
        _, data = api._get(resource=resource)
        return data['data']

    def _refresh(self):
        resource = f'fabric/search/{self.id}/select'
        _, data = api._get(resource=resource)
        return data['data']
