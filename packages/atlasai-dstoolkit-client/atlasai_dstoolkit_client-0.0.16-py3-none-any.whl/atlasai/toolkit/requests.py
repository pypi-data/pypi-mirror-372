import os

import requests
from requests.adapters import HTTPAdapter, Retry
from .constants import DISABLE_SSL_VERIFICATION


STATUS_FORCELIST = tuple([429, 500, 502, 503, 504])

def mount_retry(
    session,
    total=10,
    backoff_factor=0.2,
    allowed_methods=None,
    status_forcelist=STATUS_FORCELIST,
):
    """
    Attach retry handlers to HTTP and HTTPS endpoints of a Requests Session
    """

    retries = Retry(
        total=total,
        backoff_factor=backoff_factor,
        allowed_methods=allowed_methods,
        status_forcelist=status_forcelist,
    )

    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

def get_session(
    total=3,
    backoff_factor=0.2,
    allowed_methods=None,
    status_forcelist=STATUS_FORCELIST,
):
    """
    Get a Requests Session with retry handlers for HTTP and HTTPS endpoints
    """

    sess = requests.Session()
    if os.getenv(DISABLE_SSL_VERIFICATION):
        sess.verify = False
    mount_retry(
        sess,
        total=total,
        backoff_factor=backoff_factor,
        allowed_methods=allowed_methods,
        status_forcelist=status_forcelist,
    )

    return sess
