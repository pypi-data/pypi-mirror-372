import logging

from django.conf import settings

from djpsa.halo.api import WebhookAPIClient, NotificationAPIClient
from djpsa.utils import get_djpsa_settings
from djpsa.sync.callbacks import CallbacksHandler

logger = logging.getLogger(__name__)

event_data = {
    'faults': [{
        "webhook_id": None,
        "type": "-2",
        "delivery_method": "6",
        "name": "Ticket updated",
        "agent_id": "0",
        "slack_id": "0",
        "teams_id": "0",
        "filter_type": "2",
        "restriction_type": "0",
        "popupinnotificationpane": False,
        "sendpushnotificationbrowser": False,
        "sendpushnotification": False,
        "customisecolour": False,
        "eventno": "61",
        "interval": "0",
        "useworkinghours": "0",
        "emailtemplate_id": "32",
        "conditions": [
            {
                "fieldname": "symptom",
                "value_type": "string",
                "tablename": "faults",
                "type": 1,
                "change_context": 0,
                "value_string": '""',
                "value_lookup": None,
                "value_display": "Incident",
            }
        ],
    }, {
        "webhook_id": None,
        "type": "-2",
        "delivery_method": "6",
        "name": "",
        "agent_id": "0",
        "slack_id": "0",
        "teams_id": "0",
        "email_list": "",
        "filter_type": "2",
        "restriction_type": "0",
        "sendpushnotification": False,
        "customisecolour": False,
        "eventno": "3",
        "interval": "0",
        "useworkinghours": "0",
        "conditions": [],
        "emailtemplate_id": "32"
    }]
}


class HaloCallbacksHandler(CallbacksHandler):
    api_client = WebhookAPIClient
    field_names = ['name', 'note', 'url']
    ident_field = 'name'
    base_callback_data = {
        'active': True,
        'algorithm': 0,
        'authentication_type': 0,
        'certificate_id': 0,
        'content_type': 'application/json',
        'inbound_authentication_type': 0,
        'method': 0,
        'major_version_number': 0,
        'minor_version_number': 1,
        'patch_version_number': 0,
        'runbook_start_type': 0,
        'type': 0,
        'systemuse': '',
        'version_number': '0.0.1'
    }

    def __init__(self):
        self.settings = get_djpsa_settings()
        self.event_api = NotificationAPIClient()
        super().__init__()

    @property
    def needed_callbacks(self):
        # NOTE: Halo doesn't give you anything to identify callbacks as your
        #  callbacks, so the 'callback_description' should be used to filter
        #  out callbacks that you shouldn't delete.
        callback_description = self.settings['callback_description']

        return [
            {
                'name': f'{callback_description} Ticket Callback',
                'note': 'faults',
                'url': "ticket/",
            },
        ]

    def _build_get_conditions(self):
        return {}

    def _build_post_data(self, callback):

        auth_data = {
            'authentication_header': "Token",
            'basic_password': settings.CALLBACK_SECRET,
            'authentication_type': "3",
        }

        callback = {
            **callback,
            **auth_data,
        }

        callback_post_data = {**self.base_callback_data, **callback}
        return callback_post_data

    def _clean_callbacks(self, callbacks):

        # Create a new list of elements from the callbacks list
        # that where the name field contains the string field
        # defined in 'callback_description'.

        names_to_check = [cb['name'] for cb in self.get_needed_callbacks()]

        return [
            cb for cb in callbacks
            if 'name' in cb
               and any(name in cb['name'] for name in names_to_check)
        ]

    def _post_register_processing(self, registered_callback):
        # Add events to the callback
        events = event_data.get(registered_callback['note'])

        if events:
            for event in events:
                event['webhook_id'] = registered_callback['id']
            self.event_api.create(data=events)
        else:
            logger.exception(
                f"No event template found for {registered_callback['note']}")
