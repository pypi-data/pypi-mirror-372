from typing import Any, List
from django.utils import timezone
from dateutil.parser import parse

from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class AppointmentSynchronizer(sync.CreateMixin,
                              sync.UpdateMixin,
                              sync.DeleteMixin,
                              sync.ResponseKeyMixin,
                              sync.HaloSynchronizer):
    response_key = 'appointments'
    model_class = models.AppointmentTracker
    client_class = api.AppointmentAPI

    related_meta = {
        'client_id': (models.Client, 'client'),
        'agent_id': (models.Agent, 'agent'),
        'site_id': (models.Site, 'site'),
        'user_id': (models.HaloUser, 'user'),
        'ticket_id': (models.Ticket, 'ticket'),
    }

    def __init__(
            self,
            full: bool = False,
            conditions: List = None,
            *args: Any,
            **kwargs: Any):
        super().__init__(full, conditions, *args, **kwargs)

        self.client.add_condition({
            'hidecompleted': True,
        })

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.subject = json_data.get('subject')
        instance.start_date = \
            timezone.make_aware(
                parse(json_data.get('start_date')),
                timezone.utc
            )
        instance.end_date = \
            timezone.make_aware(
                parse(json_data.get('end_date')),
                timezone.utc
            )
        instance.appointment_type = json_data.get('appointment_type_name')
        instance.is_private = json_data.get('is_private')
        instance.is_task = json_data.get('is_task', False)
        instance.complete_status = json_data.get('complete_status')
        instance.colour = json_data.get('colour')
        instance.online_meeting_url = json_data.get('online_meeting_url')

        self.set_relations(instance, json_data)
