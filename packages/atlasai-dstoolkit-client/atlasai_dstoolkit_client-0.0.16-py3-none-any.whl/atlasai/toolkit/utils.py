import arrow
import os

from furl import furl
import webbrowser

from . import api, constants

def is_notebook() -> bool:
    try:
        from IPython import get_ipython
        shell = get_ipython().__class__.__name__
        if shell != 'TerminalInteractiveShell':
            return True
        return False
    except Exception:
        return False


def show_page(page):
    f = furl(page)

    if is_first_page():
        token = retrieve_one_time_token()
        set_token_env_vars(token)
        f.args['token'] = token

    if is_notebook():
        from IPython.core.display import display
        from IPython.display import Javascript
        display(Javascript(f"window.open('{f.url}', '_blank')"))
    else:
        webbrowser.open(f.url)

def is_first_page():
    if os.getenv(constants.TOKEN_ENV_VAR) is None:
        return True
    last_set = os.getenv(constants.TOKEN_TIMESTAMP_ENV_VAR)
    if last_set:
        last_set = arrow.get(last_set)
        # if had passed more than 24h since last iframe. pass the token again in case it needs it
        if arrow.utcnow() >= last_set.shift(hours=+24):
            return True

def set_token_env_vars(token):
    os.environ[constants.TOKEN_ENV_VAR] = token
    os.environ[constants.TOKEN_TIMESTAMP_ENV_VAR] = arrow.now().isoformat()

def clean_token_env_vars():
    os.environ.pop(constants.TOKEN_ENV_VAR, None)
    os.environ.pop(constants.TOKEN_TIMESTAMP_ENV_VAR, None)

def retrieve_one_time_token():
    _, data = api._post(resource='token/wrap', url=constants.VINZ_URL)
    return data['token']
