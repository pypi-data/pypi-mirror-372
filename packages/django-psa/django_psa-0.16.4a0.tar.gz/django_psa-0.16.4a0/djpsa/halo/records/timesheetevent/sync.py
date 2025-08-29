from djpsa.halo.records import api
from djpsa.halo import sync, models
from djpsa.halo.records.ticket.sync import TicketSynchronizer


class TimeSheetEventSynchronizer(
            sync.ResponseKeyMixin,
            sync.CreateMixin,
            sync.HaloSynchronizer,
        ):
    model_class = None
    client_class = api.TimesheetEventAPI
    # For now, these are also the only fields we will support. We will
    # need to revisit this when we also improve action creation.
    required_fields = [
        'start_date',
        'end_date',
        'ticket_id',
        'agent_id',
        'charge_rate',
        'note'
    ]

    def create(self, data, *args, **kwargs):
        """
        Example data format:
        {
          "end_date": "2025-02-25T18:26:00.000Z",
          "start_date": "2025-02-25T18:10:00.000Z",
          "ticket_id": 2267,
          "agent_id": "3",
          "charge_rate": "1",
          "note": "log time action test, delete me",
        }
        """
        for field in self.required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Convert datetimes to string format.
        data['start_date'] = data['start_date'].isoformat()
        data['end_date'] = data['end_date'].isoformat()

        # Don't create a new ticket when logging time
        data['lognewticket'] = False

        # This is the event type for a quick time entry... I think...
        # It's probably one of the LookupType system events, but I can't find
        # it. However, this is what Halo uses when you do a quick time entry
        # from the time sheet, so that's what we'll use.
        data['event_type'] = 0

        self.client.create(data)

        ticket = models.Ticket.objects.get(id=data['ticket_id'])

        # Sync related to pull down the newly created action
        sync = TicketSynchronizer()
        sync.sync_related(ticket)
