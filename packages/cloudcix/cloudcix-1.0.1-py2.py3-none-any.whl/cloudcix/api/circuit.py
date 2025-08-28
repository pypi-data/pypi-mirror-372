from cloudcix.client import Client


class Circuit:
    """
    The Circuit Application allows for the management of circuits and devices.
    Will be deprecated for DCIM Application
    """
    _application_name = 'Circuit'

    circuit = Client(
        _application_name,
        'circuit/',
    )
    circuit_class = Client(
        _application_name,
        'circuit_class/',
    )
    property_type = Client(
        _application_name,
        'property_type/',
    )
    property_value = Client(
        _application_name,
        'property_value/{search_term}/',
    )
