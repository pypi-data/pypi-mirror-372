from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class PrioritySynchronizer(sync.HaloSynchronizer):

    model_class = models.PriorityTracker
    lookup_key = 'priorityid'
    client_class = api.PriorityAPI

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('priorityid')
        instance.name = json_data.get('name')
        instance.colour = json_data.get('colour')
        instance.is_hidden = json_data.get('ishidden')
