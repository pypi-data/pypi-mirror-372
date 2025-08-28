from cloudcix.client import Client


class DCIM:
    """
    The DCIM (Data Centre Infrastructure Management) Application allows for the management data centre infrastructure.
    """
    _application_name = 'dcim'

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
