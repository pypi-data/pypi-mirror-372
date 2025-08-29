from typing import Any, List

from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class HaloUserSynchronizer(sync.ResponseKeyMixin, sync.HaloSynchronizer):
    model_class = models.HaloUserTracker
    response_key = 'users'
    client_class = api.UserAPI

    related_meta = {
        'client_id': (models.Client, 'client'),
        'linked_agent_id': (models.Agent, 'agent'),
    }

    def __init__(self,
                 full: bool = False,
                 conditions: List = None,
                 *args: Any,
                 **kwargs: Any):
        super().__init__(full, conditions, *args, **kwargs)

        self.client.add_condition({
            'includeactive': True,
        })

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.first_name = json_data.get('firstname')
        instance.surname = json_data.get('surname')
        instance.initials = json_data.get('initials')
        instance.email = json_data.get('emailaddress')
        instance.colour = json_data.get('colour')
        instance.active = not json_data.get('inactive', True)
        instance.login = json_data.get('login')
        instance.use = json_data.get('use')
        instance.never_send_emails = json_data.get('neversendemails', False)
        instance.phone_number = json_data.get('phonenumber')
        instance.mobile_number = json_data.get('mobilenumber')
        instance.mobile_number_2 = json_data.get('mobilenumber2')
        instance.home_number = json_data.get('homenumber')
        instance.tel_pref = json_data.get('telpref')
        instance.is_service_account = json_data.get('isserviceaccount', False)
        instance.is_important_contact = \
            json_data.get('isimportantcontact', False)
        instance.is_important_contact_2 = \
            json_data.get('isimportantcontact2', False)

        if json_data.get('linked_agent_id') == 0:
            json_data['linked_agent_id'] = None

        self.set_relations(instance, json_data)
