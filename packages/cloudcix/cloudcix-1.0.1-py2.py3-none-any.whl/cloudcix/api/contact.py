from cloudcix.client import Client


class Contact:
    """
    Contact Application will replace the Contacts Application

    The Contact Application is a CRM application that exposes a REST API to manage a shared address book between Users
    in the same Member.

    It is also a management system for the management of your CloudCIX Chatbots

    Contact can be used as a sales and marketing tool or just as a general purpose address book.
    """
    _application_name = 'Contact'

    answer = Client(
        _application_name,
        'answer/{chatbot_name}/',
    )
    auth = Client(
        _application_name,
        'auth/{chatbot_name}/',
    )
    campaign = Client(
        _application_name,
        'campaign/',
    )
    campaign_contact = Client(
        _application_name,
        'campaign/{campaign_id}/contact/',
    )
    chatbot = Client(
        _application_name,
        'chatbot/',
    )
    contact = Client(
        _application_name,
        'contact/',
    )
    conversation = Client(
        _application_name,
        'conversation/{chatbot_name}/',
    )
    corpus = Client(
        _application_name,
        'chatbot/{chatbot_id}/corpus/',
    )
    embeddings = Client(
        _application_name,
        'embeddings/{chatbot_name}/',
    )
    exclusion = Client(
        _application_name,
        'exclusion/',
    )
    group = Client(
        _application_name,
        'group/',
    )
    group_contact = Client(
        _application_name,
        'group/{group_id}/contact/',
    )
    opportunity = Client(
        _application_name,
        'opportunity/',
    )
    opportunity_contact = Client(
        _application_name,
        'opportunity/{opportunity_id}/contact/',
    )
    opportunity_history = Client(
        _application_name,
        'opportunity/{opportunity_id}/history/',
    )
    q_and_a = Client(
        _application_name,
        'conversation/{chatbot_name}/{conversation_id}/q_and_a/',
    )
    question = Client(
        _application_name,
        'question/',
    )
    question_set = Client(
        _application_name,
        'question_set/',
    )
    summary = Client(
        _application_name,
        'summary/{chatbot_name}/',
    )
