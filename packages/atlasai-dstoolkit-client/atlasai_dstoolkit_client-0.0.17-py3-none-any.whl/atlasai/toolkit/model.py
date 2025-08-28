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

import pandas as pd
from typing import Union

from atlasai.mlhub import client

from .api import _get_access_token
from .utils import is_notebook


def search(name=None, version=None, source=None, tags=None, aliases=None):
    return ModelSearch(name, version, source, tags, aliases).search()

def get(name, version=None):
    return ModelGet(name, version).get()


class ModelPredictWrapper:
    def __init__(self, model):
        self._model = model

    def __repr__(self):
        return f'Model {self._model.name} - version: {self._model.version}'

    def __str__(self):
        return f'Model {self._model.name} - version: {self._model.version}'

    def predict(
        self,
        data: Union[dict, str, pd.DataFrame] = None,
        deployment_type: str = 'http',
        timeout: int = 3600,
        wait_for_completion: bool = True,
        tabular: bool = True,
        data_type: str = 'json'
    ):
        if deployment_type not in self._model.deployments:
            raise Exception(f'This model has no {deployment_type} deployment.')

        return client.evaluate(
            self._model.name,
            self._model.version,
            deployment_type=deployment_type,
            data=data,
            wait_for_completion=wait_for_completion,
            timeout=timeout,
            tabular=tabular,
            data_type=data_type

        )

    def __getattr__(self, item):
        return getattr(self._model, item)


class ModelResults:
    def __init__(self, results):
        self.results = results

    def __iter__(self):
        return iter(self.results)

    def __getitem__(self, index):
        return self.results[index]

    def display_tags(self, tags):
        if not isinstance(tags, dict):
            return tags
        return '\n'.join([f'{k}:{v}' for k, v in tags.items()])

    def display(self):
        data = [
            {
                'name': r.name,
                'version': r.version,
                'aliases': r.aliases if r.aliases else '',
                'tags': self.display_tags(r.tags)
            } for r in self.results
        ]
        df = pd.DataFrame(data)
        if is_notebook():
            from IPython.display import display, HTML
            html = df.to_html().replace("\\n", "<br>")
            display(HTML(html))
        return df

    def first(self):
        return self.results[0]

    def last(self):
        return self.results[-1]

    def all(self):
        return self.results

class ModelSearch:
    def __init__(self, name=None, version=None, source=None, tags=None, aliases=None):
        if aliases is None:
            aliases = []
        if tags is None:
            tags = {}
        self.name = name
        self.version = version
        self.source = source
        self.tags = tags
        self.aliases = aliases if isinstance(aliases, list) else [aliases]

    def search(self):
        _search = {}
        filters = ['name', 'version', 'source', 'tags', 'aliases']
        for f in filters:
            if not getattr(self, f, None):
                continue
            _search[f] = getattr(self, f)

        _get_access_token()
        results = client.get_models(search=_search, tabular=False)
        return ModelResults([ModelPredictWrapper(r) for r in results])

class ModelGet:
    def __init__(self, name, version=None):
        self.name = name
        self.version = version

    def get(self):
        result = client.get_model_info(self.name, self.version)
        return ModelPredictWrapper(result)
