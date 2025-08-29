from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class BudgetTypeSynchronizer(sync.HaloSynchronizer):
    model_class = models.BudgetTypeTracker
    client_class = api.BudgetTypeAPI

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.default_rate = json_data.get('defaultrate')
