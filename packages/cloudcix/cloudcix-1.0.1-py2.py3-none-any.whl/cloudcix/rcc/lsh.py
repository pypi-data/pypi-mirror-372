# Local Shell(lsh) for running commands on local machine
import subprocess
from copy import deepcopy
from typing import Any, Dict
# local
from cloudcix.rcc.channel_codes import CHANNEL_SUCCESS, CONNECTION_ERROR
from cloudcix.rcc.response import RESPONSE_DICT


def comms_lsh(payload: str) -> Dict[str, Any]:

    response = deepcopy(RESPONSE_DICT)

    try:
        # Run the command, capture stdout and stderr
        process = subprocess.Popen(payload, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Get the output and error
        output, error = process.communicate()

        response['channel_code'] = CHANNEL_SUCCESS
        response['channel_message'] = 'Connenction to localhost successful.'
        response['payload_code'] = process.returncode
        response['payload_message'] = output.decode()
        response['payload_error'] = error.decode()

    except Exception as e:
        response['channel_code'] = CONNECTION_ERROR
        response['channel_message'] = f'An unknown exception occurred executing command "{payload}"'
        response['channel_error'] = str(e)

    return response
