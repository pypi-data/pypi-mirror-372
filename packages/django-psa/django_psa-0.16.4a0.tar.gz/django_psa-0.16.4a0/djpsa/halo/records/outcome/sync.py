from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class OutcomeSynchronizer(sync.HaloSynchronizer):
    model_class = models.OutcomeTracker
    client_class = api.OutcomeAPI

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client.add_condition({
            'showhidden': True,
        })

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.outcome = json_data.get('outcome')
        instance.button_name = json_data.get('buttonname')
        instance.label_long = json_data.get('labellong')
        instance.sequence = json_data.get('sequence')
        instance.hidden = json_data.get('hidden', False)
        instance.icon = json_data.get('icon')
