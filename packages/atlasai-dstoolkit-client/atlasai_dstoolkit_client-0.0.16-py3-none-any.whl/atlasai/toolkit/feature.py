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
import uuid

import geopandas as gpd
import pandas as pd
from shapely import wkb

from . import api, constants, utils

logger = logging.getLogger(__name__)

def export(*args, **kwargs):
    fe = FeatureExport(*args, **kwargs)
    utils.show_page(fe.page)
    return fe

class FeatureExport:
    def __init__(self, search, id=None, *args, **kwargs):
        self.id = id or uuid.uuid4()
        self._search = search
        self._export = None

    def __repr__(self):
        return f'FeatureExport({self._search.id})'

    def __str__(self):
        return f'FeatureExport({self.id})'

    @property
    def page(self):
        return f'{constants.DS_TOOLKIT_URL}/feature/export/{self.id}?feature_search_id={self._search.id}'

    @property
    def export(self):
        return self._export

    @property
    def search(self):
        return self._search.search

    def details(self):
        if self.export is None or self.export.get('status') not in ['succeeded', 'failed']:
            self._export = self._details()
        return self.export

    def refresh(self):
        self._export = self._details()
        return self.export

    def results(self, limit=None, as_gdf=False) -> pd.DataFrame:
        if not self.export:
            return pd.DataFrame([])

        dfs = []
        if self.export.get('status') not in ['succeeded', 'failed']:
            raise Exception(f'Export state is: {self.export.get("status")}')
        grouped = self.export.get('search_result', {}).get('grouped', [])
        for group in grouped:
            path = group.get('url')
            if not path:
                continue
            df = pd.read_parquet(path, engine='pyarrow')
            dfs.append(df)
        if not dfs:
            raise Exception('No dataframe found')

        df = pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]

        if limit:
            df = df.head(limit)

        try:
            df['shape'] = wkb.loads(df['shape'])
            if as_gdf:
                df = gpd.GeoDataFrame(df, geometry="shape")
        except Exception:
            logger.warning('Shape field is not in WKB format. Skipping conversion.')

        return df

    def _details(self):
        resource = f'feature/export/{self.id}/details'
        _, data = api._get(resource=resource)
        return data['data']
