from typing import Any, List

from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class ClientSynchronizer(sync.ResponseKeyMixin, sync.HaloSynchronizer):
    response_key = 'clients'
    model_class = models.ClientTracker
    client_class = api.ClientAPI

    related_meta = {
        'main_site_id': (models.Site, 'site'),
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
        instance.inactive = json_data.get('inactive')
        instance.phone_number = json_data.get('main_phonenumber')

        self.set_relations(instance, json_data)
