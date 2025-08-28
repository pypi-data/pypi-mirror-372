import os
from http import HTTPStatus
import json
import logging

from furl import furl

from .constants import DS_TOOLKIT_URL
from .requests import get_session

logger = logging.getLogger(__name__)


def _get_headers(access_token):
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

def _get_access_token():
    env_name = os.getenv('ATLASAI_TOKEN_NAME', 'ATLASAI_TOKEN')
    access_token = os.getenv(env_name)
    if not access_token:
        raise Exception('No access token found. Call the `login()` method first!')
    return access_token

def _add_params(f, params=None):
    if params is None:
        params = {}

    for k, v in params.items():
        if v:
            f.args[k] = v
    return f

def _process_data(data):
    if not data:
        return '{}'
    return json.dumps({k: v for k, v in data.items() if v is not None})

def _paginate(method, url, access_token=None, params=None):
    if access_token is None:
        access_token = _get_access_token()
    results = []
    if params is None:
        params = {}
    if params.get('limit') is None:
        params['limit'] = 100

    if params.get('offset') is None:
        params['offset'] = 0

    def get_results(_url, _params):
        f = furl(_url)
        f = _add_params(f, _params)
        _response = session.request(method, f.url, headers=_get_headers(access_token))
        _response.raise_for_status()
        return _response

    session = get_session()
    while True:
        response = get_results(url, params)
        data = response.json()
        if not data:
            break

        results.extend(data)

        if len(data) < params['limit']:
            break
        params['offset'] = params['offset'] + params['limit']
    return results

def _get(access_token=None, resource=None, _id=None, method='get', params=None):
    if access_token is None:
        access_token = _get_access_token()
    session = get_session()

    f = furl(DS_TOOLKIT_URL)
    f.path = f'api/{resource}/{_id}' if _id else f'api/{resource}'
    f = _add_params(f, params)
    url = f.url

    response = session.request(method, url, headers=_get_headers(access_token))
    response.raise_for_status()
    return response.status_code, response.json()


def _list(access_token=None, resource=None, method='get', params=None, is_paginated=True):
    if access_token is None:
        access_token = _get_access_token()
    session = get_session()

    f = furl(DS_TOOLKIT_URL)
    f.path = f'api/{resource}'
    url = f.url

    # return all the records if limit not specified
    if is_paginated and not params.get('limit') and not params.get('offset'):
        return 200, _paginate(method, url, access_token, params)

    f = _add_params(f, params)
    url = f.url
    response = session.request(method, url, headers=_get_headers(access_token))
    response.raise_for_status()
    return response.status_code, response.json()

def _post(access_token=None, resource=None, method='post', data=None, params=None, url=None):
    if access_token is None:
        access_token = _get_access_token()
    session = get_session()

    f = furl(url or DS_TOOLKIT_URL)
    f.path = f'api/{resource}'
    f = _add_params(f, params)

    url = f.url
    data = _process_data(data)

    response = session.request(method, url, headers=_get_headers(access_token), data=data)
    response.raise_for_status()
    if response.status_code == HTTPStatus.NO_CONTENT:
        return response.status_code, None
    elif response.status_code == HTTPStatus.ACCEPTED:
        return response.status_code, response.headers['Location']
    else:
        return response.status_code, response.json()

def _patch(access_token=None, resource=None, method='patch', data=None, params=None):
    if access_token is None:
        access_token = _get_access_token()
    session = get_session()

    f = furl(DS_TOOLKIT_URL)
    f.path = f'api/{resource}'
    f = _add_params(f, params)

    url = f.url
    data = _process_data(data)

    response = session.request(method, url, headers=_get_headers(access_token), data=data)
    response.raise_for_status()
    if response.status_code == HTTPStatus.NO_CONTENT:
        return response.status_code, None
    elif response.status_code == HTTPStatus.ACCEPTED:
        return response.status_code, response.headers['Location']
    else:
        return response.status_code, response.json()

def _delete(access_token=None, resource=None, method='delete', data=None, params=None):
    if access_token is None:
        access_token = _get_access_token()
    session = get_session()

    f = furl(DS_TOOLKIT_URL)
    f.path = f'api/{resource}'
    f = _add_params(f, params)

    url = f.url
    if data:
        response = session.request(method, url, headers=_get_headers(access_token), data=_process_data(data))
    else:
        response = session.request(method, url, headers=_get_headers(access_token))
    response.raise_for_status()
    if response.status_code == HTTPStatus.NO_CONTENT:
        return response.status_code, None
    elif response.status_code == HTTPStatus.ACCEPTED:
        return response.status_code, response.headers['Location']
    else:
        return response.status_code, response.json()
