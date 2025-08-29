from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class StatusSynchronizer(sync.HaloSynchronizer):
    model_class = models.StatusTracker
    client_class = api.StatusAPI

    def _try_validate(self, api_instance):
        status_type = api_instance.get('type')

        # Zero is the status type for Ticket statuses, other types
        # are not for ticket. It is worth noting the API has a parameter
        # to filter by type, but it does not work.
        return status_type == 0

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.colour = json_data.get('colour')
