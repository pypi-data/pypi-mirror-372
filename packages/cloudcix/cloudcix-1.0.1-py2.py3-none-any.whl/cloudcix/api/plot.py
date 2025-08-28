from cloudcix.client import Client


class Plot:
    """
    The Plot Application exposes a REST API capable of managing historial measurement data
    """
    _application_name = 'plot'

    alert = Client(
        _application_name,
        'alert/',
    )
    category = Client(
        _application_name,
        'category/',
    )
    reading = Client(
        _application_name,
        'reading/',
    )
    source = Client(
        _application_name,
        'source/',
    )
    source_share = Client(
        _application_name,
        'source_share/',
    )
    source_group_summary = Client(
        _application_name,
        'source_group_summary/{source}/',
    )
    source_summary = Client(
        _application_name,
        'source_summary/{source_id}/',
    )
    unit = Client(
        _application_name,
        'unit/',
    )
