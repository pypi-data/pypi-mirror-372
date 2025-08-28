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
import io
import pandas as pd

from . import api, constants, utils
from .requests import get_session

def register(product_name: str, data=None, file=None, start_date: str = None, end_date: str = None, tags: dict = None, type: str = 'Other'):
    """

    Parameters
    ----------
    data: The data you want to upload
    file: The file you want to upload. It's either a file or data in RAM
    product_name: The name of the product you want to be registered
    start_date: Effective start date of the product in YYYY-MM-DD format
    end_date: Effective end date of the product in YYYY-MM-DD format
    tags: Tags you want to add to the product and instance
    type: Type of the asset

    Returns
    -------

    """
    if data is None and file is None:
        raise Exception('data or file parameter required')

    if file:
        with open('data.json', 'r', encoding='utf-8') as f:
            file_contents = f.read()
            data = io.StringIO(file_contents)
    else:
        if isinstance(data, pd.DataFrame):
            data = data.to_json(orient='records')
        data = io.StringIO(data)

    additional_params = [
        ('start_date', start_date),
        ('end_date', end_date),
        ('tags', tags),
        ('type', type)
    ]
    _, result = api._post(resource='dataset/upload')
    result = result['data']
    session = get_session()
    response = session.put(result['signed_url'], data=data, headers=result['headers'])
    response.raise_for_status()

    register_data = {
        'product_name': product_name,
        'path': result['storage_path'],
    }
    for name, value in additional_params:
        if value:
            register_data[name] = value

    _, data = api._post(resource='dataset/register', data=register_data)
    return {
        'product_name': data['data']['product_name'],
        'storage_path': result['storage_path']
    }

def search(*args, **kwargs):
    ds = DatasetSearch(*args, **kwargs)
    utils.show_page(ds.page)
    return ds

class DatasetSearch:

    def __init__(self, id=None, *args, **kwargs):
        self.id = id or uuid.uuid4()
        self._search = None

    def __repr__(self):
        return f'DatasetSearch({self.id})'

    def __str__(self):
        return f'DatasetSearch({self.id})'

    @property
    def page(self):
        return f'{constants.DS_TOOLKIT_URL}/dataset/search/{self.id}'

    @property
    def search(self):
        return self._search

    def info(self):
        return self._info()

    def _info(self):
        resource = f'dataset/search/{self.id}/info'
        _, data = api._get(resource=resource)
        return data['data']
