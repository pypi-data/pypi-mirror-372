from cloudcix.client import Client


class PAT:
    """
    The Pat Application exposes a REST API capable of managing Pod records
    """
    _application_name = 'pat'
    galaxy = Client(
        _application_name,
        'galaxy/',
    )
    main_firewall_rules = Client(
        _application_name,
        'pod/{pod_id}/main_firewall_rules/',
    )
    pod = Client(
        _application_name,
        'pod/',
    )
