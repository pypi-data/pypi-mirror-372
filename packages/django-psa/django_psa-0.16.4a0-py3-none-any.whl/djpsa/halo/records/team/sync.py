from djpsa.halo import models
from djpsa.halo.records import api

from djpsa.halo import sync


class TeamSynchronizer(sync.HaloSynchronizer):
    model_class = models.TeamTracker
    client_class = api.TeamAPI

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.ticket_count = json_data.get('ticket_count')
