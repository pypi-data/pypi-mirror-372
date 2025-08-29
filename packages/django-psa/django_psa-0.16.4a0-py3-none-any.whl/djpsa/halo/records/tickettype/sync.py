from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class TicketTypeSynchronizer(sync.HaloSynchronizer):
    model_class = models.TicketTypeTracker
    client_class = api.TicketTypeAPI

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.description = json_data.get('description')
        instance.active = json_data.get('active', False)
        instance.use = json_data.get('use')
        instance.colour = json_data.get('colour')
