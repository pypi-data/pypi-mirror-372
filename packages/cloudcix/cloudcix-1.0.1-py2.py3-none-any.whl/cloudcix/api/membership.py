from cloudcix.client import Client


class Membership:
    """
    Membership is a CloudCIX Application that exposes a REST API capable of managing CloudCIX Members and relationships
    between those Members
    """
    _application_name = 'membership'
    address = Client(
        _application_name,
        'address/',
    )
    address_link = Client(
        _application_name,
        'address/{address_id}/link/',
    )
    api_key = Client(
        _application_name,
        'api_key/',
    )
    cloud_bill = Client(
        _application_name,
        'cloud_bill/{address_id}/{target_address_id}/',
    )
    cloud_budget = Client(
        _application_name,
        'cloud_budget/',
    )
    conversation = Client(
        _application_name,
        'conversation/',
    )
    country = Client(
        _application_name,
        'country/',
    )
    currency = Client(
        _application_name,
        'currency/',
    )
    department = Client(
        _application_name,
        'department/',
    )
    email_confirmation = Client(
        _application_name,
        'email_confirmation/{email_token}',
    )
    franchise_logic = Client(
        _application_name,
        'franchise_logic/{builder_address_id}/{distributor_address_id}/',
    )
    hpc_admin = Client(
        _application_name,
        'hpc_admin',
    )
    hpc_i_use = Client(
        _application_name,
        'hpc_i_use',
    )
    hpc_type = Client(
        _application_name,
        'hpc_type',
    )
    idp = Client(
        _application_name,
        'idp/',
    )
    idp_configuration = Client(
        _application_name,
        'idp_configuration/',
    )
    language = Client(
        _application_name,
        'language/',
    )
    member = Client(
        _application_name,
        'member/',
    )
    member_link = Client(
        _application_name,
        'member/{member_id}/link/',
    )
    notification = Client(
        _application_name,
        'address/{address_id}/notification/',
    )
    profile = Client(
        _application_name,
        'profile/',
    )
    public_key = Client(
        _application_name,
        'public_key/',
    )
    q_and_a = Client(
        _application_name,
        'conversation/{conversation_id}/q_and_a/',
    )
    subdivision = Client(
        _application_name,
        'country/{country_id}/subdivision/',
    )
    team = Client(
        _application_name,
        'team/',
    )
    territory = Client(
        _application_name,
        'territory/',
    )
    token = Client(
        _application_name,
        'auth/login/',
    )
    token_idp = Client(
        _application_name,
        'auth/login/idp/',
    )
    transaction_type = Client(
        _application_name,
        'transaction_type/',
    )
    user = Client(
        _application_name,
        'user/',
    )
    verbose_address = Client(
        _application_name,
        'address/verbose/',
    )
