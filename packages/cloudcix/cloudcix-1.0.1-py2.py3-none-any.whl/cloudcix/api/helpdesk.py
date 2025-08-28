from cloudcix.client import Client


class Helpdesk:
    """
    The Helpdesk application is both a ticketing system, and a returns management system
    """
    _application_name = 'helpdesk'

    item = Client(
        _application_name,
        'ticket/{ticket_id}/item/',
    )
    item_history = Client(
        _application_name,
        'ticket/{ticket_id}/item/{item_id}/history/',
    )
    item_status = Client(
        _application_name,
        'item_status/',
    )
    part_used = Client(
        _application_name,
        'ticket/{ticket_id}/item/{item_id}/part_used/',
    )
    reason_for_return = Client(
        _application_name,
        'reason_for_return/',
    )
    reason_for_return_translation = Client(
        _application_name,
        'reason_for_return/{reason_for_return_id}/translation/',
    )
    report_ticket = Client(
        _application_name,
        'report_ticket/',
    )
    report_ticket_client = Client(
        _application_name,
        'report_ticket_client/{client_address_id}/',
    )
    service_centre_logic = Client(
        _application_name,
        'service_centre_logic/',
    )
    service_centre_warrantor = Client(
        _application_name,
        'service_centre/{address_id}/warrantor/',
    )
    status = Client(
        _application_name,
        'status/',
    )
    ticket = Client(
        _application_name,
        'ticket/',
    )
    ticket_history = Client(
        _application_name,
        'ticket/{ticket_id}/history/',
    )
    ticket_question = Client(
        _application_name,
        'ticket_question/',
    )
    ticket_type = Client(
        _application_name,
        'ticket_type/',
    )
    warrantor_logic = Client(
        _application_name,
        'warrantor_logic/',
    )
    warrantor_service_centre = Client(
        _application_name,
        'warrantor/{address_id}/service_centre/',
    )
