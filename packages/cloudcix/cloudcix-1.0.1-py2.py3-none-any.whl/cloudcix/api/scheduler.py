from cloudcix.client import Client


class Scheduler:
    """
    Scheduler is an application that allows the User to create recurring transactions.

    A recurring transaction is a transaction that will be recreated one or several times according to the rules the
    User gives.
    """
    _application_name = 'scheduler'

    task = Client(
        _application_name,
        'task/',
    )
    task_log = Client(
        _application_name,
        'task_log/',
    )
