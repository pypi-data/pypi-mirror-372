from typing import Any, List
from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class SiteSynchronizer(sync.ResponseKeyMixin, sync.HaloSynchronizer):

    model_class = models.SiteTracker
    response_key = 'sites'
    client_class = api.SiteAPI

    related_meta = {
        'client_id': (models.Client, 'client'),
        'sla_id': (models.SLA, 'sla'),
    }

    def __init__(self,
                 full: bool = False,
                 conditions: List = None,
                 *args: Any,
                 **kwargs: Any):
        super().__init__(full, conditions, *args, **kwargs)

        self.client.add_condition({
            'includeaddress': True,
        })

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        # api has client_id as decimal, convert to int. It's never
        # actually a decimal. The API docs has it as an int, but for some
        # reason it's being returned as a decimal on Site records.
        if json_data.get('client_id'):
            json_data['client_id'] = int(json_data.get('client_id'))

        # This is the worst thing I have ever seen.
        instance.delivery_address = json_data.get('delivery_address_line1')
        instance.delivery_address += \
            " {}".format(json_data.get('delivery_address_line2'))
        instance.delivery_address += \
            " {}".format(json_data.get('delivery_address_line3'))
        instance.delivery_address += \
            " {}".format(json_data.get('delivery_address_line4'))
        instance.delivery_address += \
            " {}".format(json_data.get('delivery_address_line5'))

        instance.colour = json_data.get('colour')
        instance.active = json_data.get('active', False)
        instance.phone_number = json_data.get('phone_number')
        instance.use = json_data.get('use')

        self.set_relations(instance, json_data)
