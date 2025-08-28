# Methods for ensuring data reaches a remote host in its entirity
# stdlib
from copy import deepcopy
from typing import Any, Dict, Optional, Tuple
# libs
from pylxd import Client
from pylxd.exceptions import ClientConnectionFailed, LXDAPIException
# local
from cloudcix.rcc.channel_codes import (
    API_ERROR,
    API_SUCCESS,
    CHANNEL_SUCCESS,
    CONNECTION_ERROR,
)
from cloudcix.rcc.response import RESPONSE_DICT


def comms_lxd(
    endpoint_url: str,
    cli: str,
    project: Optional[str] = None,
    verify: bool = True,
    api: bool = False,
    **kwargs,
) -> Dict[str, Any]:
    """
    Run a PyLXD API request on a LXD host over a PyLXD Client connection
    Raises `CouldNotConnectException` if a PyLXD Client connection cannot be established
    :param endpoint_url: The enpoint url where the PyLXD API request should be made to
    :param cli: The PyLXD service for the request and the method to run
    :param project (optional): Name of the LXD project to create the PyLXD client for.
    :param verify (optional): Whether to the verify the TLS certificate or not in the PyLXD Client. Defaults to True
    :param api (optional): If True, use .api on the PyLXD Client connection. Defaults to False
    :return: A dictionary with the following properties:
        channel_code:
            description: A code representing if suuccessful PyLXD Client connection was made.
        channel_error:
            description: Optional string value representing an error raised validating the sent params.
        channel_message:
            description: String message representing if PyLXD Client connection was successful.
        payload_code:
            description: A code resresenting if the cli request was successful or not.
        payload_error:
            description: Optional string value representing the error returned for the PyLXD API cli request.
        payload_message:
            description: Optional string value representing the response from the PyLXD API cli request.
    """
    response = deepcopy(RESPONSE_DICT)

    client, err = _get_client(endpoint_url, verify, project)
    if err is not None:
        response['channel_code'] = CONNECTION_ERROR
        response['channel_message'] = f'Could not eastablish a PyLXD client connection to {endpoint_url}.'
        response['channel_error'] = err
        return response

    # If api is True, switch to .api client
    if api:
        client = client.api

    method, err = _get_method(client, cli, api)
    if err is not None:
        response['channel_code'] = CONNECTION_ERROR
        response['channel_message'] = f'The provided PyLXD service or method in "{cli}" is invalid'
        response['channel_error'] = err
        return response

    response['channel_code'] = CHANNEL_SUCCESS
    response['channel_message'] = f' PyLXD client and method connection established to {endpoint_url} for {cli}'

    pylxd_response, err = _deploy(method, **kwargs)
    if err is not None:
        response['payload_code'] = API_ERROR
        response['payload_message'] = f'The PyLXD API request for {cli} was unsuccessful.'
        response['payload_error'] = err
    else:
        response['payload_code'] = API_SUCCESS
        response['payload_message'] = pylxd_response

    return response


def _get_client(endpoint_url: str, verify: bool, project: Optional[str]) -> Tuple[Client, str]:
    """
    Obtain a pylxd.Client connected to the given `endpoint_url`
    :param endpoint_url: The IP address for the PyLXD Client
    :param verify: Whether to the verify the TLS certificate or not in the PyLXD Client. Defaults to True
    :param project (optional): Name of the LXD project to create the PyLXD client for.
    :return: A PyLXD client
    """
    try:
        client = Client(endpoint=endpoint_url, verify=verify, project=project)
    except ClientConnectionFailed as e:
        return '', str(e)
    except Exception as e:
        return '', f'An unknown exception occurred: {e}'

    return client, None


def _get_method(client: Client, cli: str, api: bool):
    """
    Parses and resolves the service and method from the `cli` string.

    :param client: A pylxd.Client instance that is for a LXD host and Project
    :param cli: Command string specifying service and method.
        - For `api=False`: 'service.method'
        - For `api=True`: 'service["resource"].method'
    :param api: Determines if `cli` is in API-style format.
    :return: A PyLXD Client method to be called
    """
    if api:
        # Split on the last '.' to separate method from service/resource
        service_part, method_name = cli.rsplit('.', 1)

        # Extract service and resource using eval to handle the ["resource"] syntax
        try:
            # Evaluating service_part to dynamically resolve service and resource
            service = eval(f'client.{service_part}')
        except AttributeError as e:
            return '', str(e)
    else:
        # For non-API style, simply split on the '.'
        service_name, method_name = cli.split('.', 1)

        # Resolve the service directly from client
        try:
            service = getattr(client, service_name)
        except AttributeError as e:
            return '', str(e)

    # Resolve the method within the service
    try:
        method = getattr(service, method_name)
    except AttributeError as e:
        return '', str(e)
    except Exception as e:
        return '', f'An unknown exception occurred: {e}'

    return method, None


def _deploy(method, **kwargs) -> Tuple[Any, str]:
    """
    Deploy the given `**kwargs` to the LXD host accessible via the supplied `client`
    :param method: A PyLXD Client for a specific service and method
    :return: Response from the called metod
    """
    try:
        pylxd_response = method(**kwargs)
    except LXDAPIException as e:
        return '', str(e)
    except Exception as e:
        return '', f'An unknown exception occurred: {e}'

    return pylxd_response, None
