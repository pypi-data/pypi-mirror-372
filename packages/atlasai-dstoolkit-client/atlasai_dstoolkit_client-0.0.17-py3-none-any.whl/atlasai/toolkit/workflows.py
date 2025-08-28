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
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
import logging
import os
import random
import time

import leafmap
import pandas as pd
import requests
from tqdm import tqdm

from . import api, constants, output as o

logger = logging.getLogger('atlasai.toolkit')

@dataclass()
class WorkflowResponse:
    id: str
    uid: str
    name: str
    create_date: str
    update_date: str
    status: str
    message: str


class Workflow:
    type = None
    id = None

    def __init__(self, id=None):
        # Allow the selection of an existing workflow and check the logs.
        self.id = id
        self._run_results = []

    @property
    def status(self):
        _result = self.get()
        return _result['data']['status']

    def results(self, *args, **kwargs):
        return self._results(*args, **kwargs)

    def _set(self, result):
        self.id = result['data']['id']

    def _config(self):
        raise NotImplementedError()

    def _validate(self):
        raise NotImplementedError()

    def _results(self, *args, **kwargs):
        raise NotImplementedError

    def preview(self, *args, **kwargs):
        raise NotImplementedError

    def get(self):
        if not self.id:
            raise Exception('No valid execution of the workflow. Please use the `run` method first.')

        _, result = api._get(resource=f'workflow/{self.id}')
        return result

    def logs(self, only_errors=True):
        def cleanup_logs(logs):
            if not logs:
                return "-"
            return ast.literal_eval(logs).decode('utf-8')

        if not self.id:
            raise Exception('No valid execution of the workflow. Please use the `run` method first.')

        workflow = self.get()

        _, result = api._get(resource=f'workflow/{self.id}/logs', params={'only_errors': only_errors})

        o.print_title(f'Workflow: {workflow["data"]["name"]}')
        o.print_subtitle(f'Status: {workflow["data"]["status"]}')
        o.print_subtitle(f'Message: {workflow["data"]["message"] or "-"}')

        o.print_body('---------------------------------------------------')
        if not result['data']:
            if only_errors:
                o.print_title('No errors detected.')
            else:
                o.print_title('No pod found to pull logs from.')

        for pod, data in result['data'].items():
            o.print_title(f'Pod: {pod}')
            o.print_subtitle(f'Message: {data["message"] or "-"}')
            o.print_subtitle(f'Logs: {cleanup_logs(data.get("logs"))}')
            o.print_body('---------------------------------------------------')

    def run(self, wait_until_complete=False):
        self._validate()
        status = 'Running'
        message = ''
        data = dict(
            type=self.type,
            config=self._config()
        )
        _, result = api._post(resource='workflow', data=data)
        self._set(result)
        if wait_until_complete:
            while True:
                _result = self.get()
                if _result['data']['status'].lower() != 'running':
                    status = _result['data']['status']
                    message = _result['data']['message']
                    break

                time.sleep(5)
        return WorkflowResponse(**result['data'], status=status, message=message)

class Test(Workflow):
    type = 'test'

    def __repr__(self):
        return 'Test'

    def __str__(self):
        return 'Test'

    def configure(self):
        pass

    def _config(self):
        return dict()

    def _validate(self):
        pass


class Electrification(Workflow):
    type = 'electrification'

    def __init__(self, id=None):
        self.aoi_name = None
        self.aoi_path = None
        self.aoi = None
        self.output_path = None

        super().__init__(id)

    def __repr__(self):
        return f'Electrification({self.aoi_name})'

    def __str__(self):
        return f'Electrification({self.aoi_name})'

    def configure(self, aoi_name=None, aoi_path=None, aoi=None, output_path=None):
        self.aoi_name = aoi_name or self.aoi_name
        self.aoi_path = aoi_path or self.aoi_path
        self.aoi = aoi or self.aoi
        self.output_path = output_path or self.output_path

    def _config(self):
        cfg = {}
        for name, value in (
                ('aoi_name', self.aoi_name),
                ('aoi_geojson', self.aoi),
                ('aoi_geojson_uri', self.aoi_path),
                ('output_bucket', self.output_path)
        ):
            if value:
                cfg[name] = value
        return cfg

    def _validate(self):
        if not self.aoi_name:
            raise Exception('`aoi_name` must be specified.')

        if not self.aoi_path and not self.aoi:
            raise Exception('`aoi_path` or `aoi` must be specified.')

    def _results(self, save_to=None, force=False):
        if self._run_results and not force:
            return self._run_results

        results = []
        if not self.id:
            raise Exception('No valid execution of the workflow. Please use the `run` method first.')

        workflow = self.get()
        if not workflow['data']['status'] == 'Succeeded':
            raise Exception(f'Workflow not in `Succeeded` state. Current state: {workflow["data"]["status"]}')

        _, result = api._get(resource=f'workflow/{self.id}/results')

        with ThreadPoolExecutor(max_workers=8) as ex, tqdm(total=len(result['data']), desc="Downloading", unit="file") as pbar:
            fut_map = {ex.submit(self._download_file, res["name"], res["url"], save_to): i
                       for i, res in enumerate(result['data'])}
            for fut in as_completed(fut_map):
                results.append(fut.result())
                pbar.update(1)
        self._run_results = results
        return results

    def _download_file(self, name, url, to=None):
        local_path = os.path.join(to or os.getcwd(), name.split('/')[-1])

        logger.debug(f'Downloading :{name}')

        with requests.get(url, stream=True, timeout=120) as r:

            logger.debug(f'Finished downloading: {name}')
            r.raise_for_status()
            with open(local_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

            logger.debug(f'Finished saving: {name}')

        return local_path

    def preview(self, from_=None, to_=None, selection=None, limit=None):
        if not self._run_results:
            raise Exception('No result to be displayed. Run the workflow first and wait for its completion.')

        _results = []
        if selection is None:
            selection = []
        if selection:
            selection = ['-'.join(s.split('-')[:2]) for s in selection]
            from_, to_, limit = None, None, None

        if from_:
            from_ = datetime.strptime(from_, "%Y-%m-%d")
        if to_:
            to_ = datetime.strptime(to_, "%Y-%m-%d")

        for f in sorted(self._run_results):
            yyyy, mm = f.split('_')[-1].replace('.tif', '').split('-')
            dt = datetime(year=int(yyyy), month=int(mm), day=1)
            if selection:
                if f'{yyyy}-{mm}' not in selection:
                    continue
            if from_ and from_ > dt:
                continue
            if to_ and to_ < dt:
                continue
            if limit and len(_results) >= limit:
                continue
            _results.append(dict(
                layer_name=f'{yyyy}-{mm}',
                file=f,
                colormap=constants.LEAFMAP_COLORMAP[random.randint(0, len(constants.LEAFMAP_COLORMAP) - 1)]
            ))
        if not _results:
            raise Exception('No result matches your criteria.')
        m = leafmap.Map()
        if len(_results) > 10:
            logger.warning(f'Too many layers to display. Expect increased loading time. Layers to display: {len(_results)}')

        for idx, f in enumerate(_results):
            m.add_raster(
                f['file'],
                layer_name=f['layer_name'],
                nodata=0,
                colormap=f['colormap'],
                opacity=0.5,
            )
        if hasattr(m, "add_layers_control"):
            m.add_layers_control()
        elif hasattr(m, "add_layer_control"):
            m.add_layer_control()
        return m

def List(search=None, offset=0, limit=100):
    pd.set_option("display.max_colwidth", None)
    resource = 'workflows'
    _, data = api._list(resource=resource, params={'search': search, 'offset': offset, 'limit': limit})
    df = pd.DataFrame(data['data'])
    df = df.drop(columns=['update_date', 'uid'])
    return df
