from cloudcix.client import Client


class Support:
    """
    The Support application is both a ticketing system, and a returns management system
    This is to be deprecated for the Helpdesk Application
    """
    _application_name = 'support'

    item = Client(
        _application_name,
        'ticket/{transaction_type_id}/{tsn}/item/',
    )
    item_history = Client(
        _application_name,
        'ticket/{transaction_type_id}/{tsn}/item/{item_id}/history/',
    )
    item_status = Client(
        _application_name,
        'item_status/',
    )
    part_used = Client(
        _application_name,
        'ticket/{transaction_type_id}/{tsn}/item/{item_id}/part_used/',
    )
    reason_for_return = Client(
        _application_name,
        'reason_for_return/',
    )
    reason_for_return_translation = Client(
        _application_name,
        'reason_for_return/{reason_for_return_id}/translation/',
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
    summary_support_ticket = Client(
        _application_name,
        'summary_support_ticket/',
    )
    ticket = Client(
        _application_name,
        'ticket/{transaction_type_id}/',
    )
    ticket_history = Client(
        _application_name,
        'ticket/{transaction_type_id}/{tsn}/history/',
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
