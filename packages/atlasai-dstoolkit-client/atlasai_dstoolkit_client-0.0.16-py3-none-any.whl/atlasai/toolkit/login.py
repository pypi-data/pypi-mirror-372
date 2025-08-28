import hmac
import logging
import os
from urllib.parse import urlparse
import warnings

import arrow
from furl import furl
import requests

from . import constants
from .utils import clean_token_env_vars


logger = logging.getLogger(__name__)


def login(env_name='ATLASAI_TOKEN', return_access_token=False):
    """
     Authenticate with Vinz

     Returns an OAuth2 Access Token

     If `env_name` provided, the Access Token will be saved
     to the named environment variable

     #### Usage

     ```python
     from atlasai.vinz import client

     token = client.authenticate(<OPTIONAL_ENV_VARIABLE_NAME>)
     ```
     """
    os.environ['ATLASAI_TOKEN_NAME'] = env_name
    f = furl(constants.VINZ_URL)
    f.path = 'api/token'
    url = f.url
    headers = {}
    include_authorization(url, headers)

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    token = data['access_token']

    os.environ[env_name] = token

    user_id = data.get('email') or data.get('sub') or 'AtlasAI Employee'
    os.environ['LOGNAME'] = user_id

    if return_access_token:
        return token

def logout():
    os.environ.pop(os.getenv('ATLASAI_TOKEN_NAME', ''), None)
    clean_token_env_vars()

def load_credentials(access_key=None, secret_key=None):
    access_key = access_key or os.getenv('ATLASAI_ACCESS_KEY')
    secret_key = secret_key or os.getenv('ATLASAI_SECRET_KEY')

    return access_key, secret_key


def include_authorization(url, headers, bearer_token=None, access_key=None, secret_key=None):
    bearer_token = bearer_token or os.getenv('ATLASAI_BEARER_TOKEN')
    access_key, secret_key = load_credentials(
        access_key=access_key,
        secret_key=secret_key,
    )

    if bearer_token:
        headers['Authorization'] = f'Bearer {bearer_token}'
        return

    if not access_key or not secret_key:
        warnings.warn('No API Keys provided to access Vinz API. Provide the following pair ATLASAI_ACCESS_KEY and ATLASAI_SECRET_KEY')
        raise ValueError('ATLASAI_ACCESS_KEY and ATLASAI_SECRET_KEY must be provided together')

    product, version = 'atlasai', '1'
    headers.update({
        'Host': urlparse(url).netloc,
        'X-AtlasAI-Date': arrow.utcnow().isoformat(),
        'X-AtlasAI-Credential': '/'.join([product, version, access_key]),
        'X-AtlasAI-SignedHeaders': 'x-atlasai-date;x-atlasai-credential;host',
    })

    sign_request(headers, secret_key)


def sign_request(headers, secret_key):
    product, version, access_key = headers['X-AtlasAI-Credential'].split('/')
    key = f'{product}{version}{secret_key}'.encode('utf-8')
    for msg in (
        headers['X-AtlasAI-Date'],
        f'{product}_{version}_request',
    ):
        obj = hmac.new(key, msg.encode('utf-8'), 'sha256')
        key = obj.digest()

    msg = '\n'.join([
        headers['X-AtlasAI-Date'],
        headers['X-AtlasAI-Credential'],
        headers['Host']
    ])
    headers['X-AtlasAI-Signature'] = hmac.new(key, msg.encode('utf-8'), 'sha256').hexdigest()
