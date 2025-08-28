# stdlib
import json
from copy import deepcopy
from typing import Any, Dict, Tuple
# lib
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
# local
from cloudcix.rcc.channel_codes import (
    CHANNEL_SUCCESS,
    CONNECTION_ERROR,
    VALIDATION_ERROR,
)
from cloudcix.rcc.response import RESPONSE_DICT

ALLOWED_METHODS = {'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT'}


def comms_http(
    url: str,
    method: str = 'GET',
    payload: Dict[str, Any] = None,
    headers: Dict[str, str] = None,
    timeout: int = 10,
    **kwargs,
) -> Dict[str, Any]:
    """
    Send an HTTP request and return a structured response following the RCC format.
    :param url: The URL endpoint for the API request.
    :param method: The HTTP method to use (e.g., GET, POST, PUT, DELETE).
    :param payload: The data to send with the request (for POST, PUT, etc.).
    :param headers: Any HTTP headers to include in the request.
    :param timeout: How long to wait (in seconds) for the server to respond.
    :param kwargs: Additional optional arguments to pass directly to the `requests.request` method.
    :return: A dictionary structured according to the RESPONSE_DICT template.

    Example:
    --------
    response = comms_http(
        url="https://api.example.com",
        method="POST",
        payload={"key": "value"},
        headers={"Authorization": "Bearer token"}
    )
    """
    response = deepcopy(RESPONSE_DICT)

    # The requests library expects the HTTP method (GET, POST, PUT, etc.) to be passed in uppercase,
    # as these are standard according to the HTTP specification.
    method = method.upper()

    # Handle validation errors
    valid, msg = _validate(url, method, payload, timeout)
    if not valid:
        response['channel_code'] = VALIDATION_ERROR
        response['channel_message'] = f'Validation error for sent parameter'
        response['channel_error'] = msg
        return response

    try:
        session = _get_retry_session()

        headers = headers or {'Content-Type': 'application/json'}
        # Send the request with **kwargs
        resp = session.request(method, url, json=payload, headers=headers, timeout=timeout, **kwargs)

        # Populate response structure
        response['channel_code'] = CHANNEL_SUCCESS
        response['channel_message'] = f'Connection established to URL {url}'
        response['payload_code'] = resp.status_code
        if 'application/json' in resp.headers.get('Content-Type', ''):
            response['payload_message'] = resp.json()
        else:
            response['payload_message'] = resp.text

        # Check for errors in the response
        if resp.status_code >= 400:
            response['payload_error'] = f'HTTP error {resp.status_code}: {resp.reason}. Headers: {resp.headers}'

    except requests.exceptions.RequestException as e:
        # Handle connection errors
        response['channel_code'] = CONNECTION_ERROR
        response['channel_message'] = f'Could not establish connection to {url}'
        response['channel_error'] = str(e)

    return response


def _validate(url: str, method: str, payload: Dict[str, Any], timeout: int) -> Tuple[bool, str]:
    valid = True
    msg = ''

    if not url.startswith(('http://', 'https://')):
        valid = False
        msg += f'Invalid "url": {url}. It muat start with "http://" or "https://".\n'

    if payload is not None:
        try:
            json.dumps(payload)
        except (TypeError, ValueError) as e:
            valid = False
            msg += f'Invalid "payload": {payload}. Exception: {e}.\n'

    if method not in ALLOWED_METHODS:
        valid = False
        msg += f'Invalid method: {method}. Supported methods are: {", ".join(ALLOWED_METHODS)}.\n'

    try:
        int(timeout)
    except (TypeError, ValueError):
        valid = False
        msg += f'Invalid timeout: {timeout}. It must be an integer.\n'

    return valid, msg


# Create session with retry capabilities
def _get_retry_session() -> requests.Session:
    """
    Returns a requests session with retry logic.
    Retry logic configuration
        total: Maximum number of retries for a request
        backoff_factor: Interval between retries (e.g., 0.3s, 0.6s, 1.2s, etc.)
        status_forcelist: HTTP status codes that trigger a retry
        raise_on_status: Prevent raising exceptions for retriable status codes
    :return: A requests session with retry logic.
    """

    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
