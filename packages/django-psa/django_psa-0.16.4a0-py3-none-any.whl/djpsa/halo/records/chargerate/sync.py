from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class ChargeRateSynchronizer(sync.HaloSynchronizer):
    model_class = models.ChargeRateTracker
    client_class = api.ChargeRateAPI

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
