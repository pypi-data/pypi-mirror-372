from typing import Any, List

from django.utils import timezone
from dateutil.parser import parse

from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync
from djpsa.halo.records.action.sync import ActionSynchronizer
from djpsa.halo.records.appointment.sync import AppointmentSynchronizer
from djpsa.halo.records.agent.api import UNASSIGNED_AGENT_ID
from djpsa.halo.records.client.api import UNASSIGNED_CLIENT_ID
from djpsa.utils import get_djpsa_settings


class TicketSynchronizer(sync.ResponseKeyMixin,
                         sync.CreateMixin,
                         sync.UpdateMixin,
                         sync.DeleteMixin,
                         sync.HaloSynchronizer,
                         ):
    response_key = 'tickets'
    model_class = models.TicketTracker
    client_class = api.TicketAPI
    last_updated_field = 'lastupdatefromdate'

    related_meta = {
        'client_id': (models.Client, 'client'),
        'status_id': (models.Status, 'status'),
        'priority_id': (models.Priority, 'priority'),
        'agent_id': (models.Agent, 'agent'),
        'sla_id': (models.SLA, 'sla'),
        'user_id': (models.HaloUser, 'user'),
        'site_id': (models.Site, 'site'),
        'tickettype_id': (models.TicketType, 'type'),
        'parent_id': (models.Ticket, 'project'),
    }

    def __init__(self,
                 full: bool = False,
                 conditions: List = None,
                 *args: Any,
                 **kwargs: Any):
        super().__init__(full, conditions, *args, **kwargs)

        self.client.add_condition({
            'open_only': True,
        })

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.summary = json_data.get('summary')
        instance.details = json_data.get('details')

        try:
            instance.last_action_date = timezone.make_aware(
                parse(json_data.get('lastactiondate')), timezone.utc)
        except ValueError:
            instance.last_action_date = parse(json_data.get('lastactiondate'))

        # Halo API has different keys for last update depending on if it's
        # a GET or POST request. This API is going to be the death of me.
        last_update = \
            json_data.get('lastupdate') or json_data.get('last_update')

        if last_update:
            try:
                instance.last_update = timezone.make_aware(
                    parse(last_update), timezone.utc)
            except ValueError:
                instance.last_update = parse(last_update)

        instance.user_email = json_data.get('useremail', instance.user_email)
        instance.reported_by = \
            json_data.get('reportedby', instance.reported_by)
        instance.end_user_status = json_data.get('enduserstatus')
        instance.category_1 = \
            json_data.get('category1') or json_data.get('category_1')
        instance.category_2 = \
            json_data.get('category2') or json_data.get('category_2')
        instance.category_3 = \
            json_data.get('category3') or json_data.get('category_3')
        instance.category_4 = \
            json_data.get('category4') or json_data.get('category_4')
        instance.inactive = json_data.get('inactive', False)
        instance.sla_response_state = json_data.get(
            'sla_response_state', instance.sla_response_state)
        instance.sla_hold_time = json_data.get('sla_hold_time',
                                               instance.sla_hold_time)
        instance.impact = json_data.get('impact')
        instance.flagged = json_data.get('flagged', False)
        instance.on_hold = json_data.get('onhold', False)
        instance.project_time_actual = \
            json_data.get('projecttimeactual', instance.project_time_actual)
        instance.project_money_actual = \
            json_data.get('projectmoneyactual', instance.project_money_actual)
        instance.cost = json_data.get('cost')
        instance.estimate = json_data.get('estimate')
        instance.estimated_days = json_data.get('estimateddays')
        instance.exclude_from_slas = json_data.get('excludefromslas', False)
        instance.reviewed = json_data.get('reviewed', False)
        instance.read = json_data.get('read', False)
        instance.use = json_data.get('use', instance.use)
        instance.email_to_list = \
            json_data.get('emailtolist', instance.email_to_list)
        instance.urgency = json_data.get('urgency', instance.urgency)
        instance.service_status_note = json_data.get('servicestatusnote')
        instance.ticket_tags = \
            json_data.get('tickettags', instance.ticket_tags)
        instance.appointment_type = json_data.get('appointment_type')
        instance.impact_level = json_data.get('impactlevel')
        instance.itil_request_type = json_data.get('itil_requesttype_id')

        date_occurred = json_data.get('dateoccurred')
        if date_occurred:
            instance.date_occurred = sync.empty_date_parser(date_occurred)

        respond_by_date = json_data.get('respondbydate')
        if respond_by_date:
            instance.respond_by_date = sync.empty_date_parser(respond_by_date)

        fix_by_date = json_data.get('fixbydate')
        if fix_by_date:
            instance.fix_by_date = sync.empty_date_parser(fix_by_date)

        date_assigned = json_data.get('dateassigned')
        if date_assigned:
            instance.date_assigned = sync.empty_date_parser(date_assigned)

        response_date = json_data.get('responsedate')
        if response_date:
            instance.response_date = sync.empty_date_parser(response_date)

        deadline_date = json_data.get('deadlinedate')
        if deadline_date:
            instance.deadline_date = sync.empty_date_parser(deadline_date)

        date_closed = json_data.get('dateclosed')
        if date_closed:
            instance.date_closed = sync.empty_date_parser(date_closed)

        start_date = json_data.get('startdate')
        if start_date:
            parsed_start_date = sync.empty_date_parser(start_date)

            parsed_start_date = parsed_start_date.replace(
                hour=parse(json_data.get('starttime')).hour,
                minute=parse(json_data.get('starttime')).minute,
                second=parse(json_data.get('starttime')).second
            ) if parsed_start_date else None  # Don't set time if start
            # date is an impossible date.

            if parsed_start_date:
                instance.start_date = parsed_start_date.date()

        target_date = json_data.get('targetdate')
        if target_date:
            parsed_target_date = sync.empty_date_parser(target_date)

            parsed_target_date = parsed_target_date.replace(
                hour=parse(json_data.get('targettime')).hour,
                minute=parse(json_data.get('targettime')).minute,
                second=parse(json_data.get('targettime')).second
            ) if parsed_target_date else None  # Don't set time if target
            # date is an impossible date.

            if parsed_target_date:
                instance.target_date = parsed_target_date.date()

        last_incoming_email_date = json_data.get('lastincomingemaildate')
        if last_incoming_email_date:
            instance.last_incoming_email_date = \
                sync.empty_date_parser(last_incoming_email_date)

        team_name = json_data.get('team')

        instance.team = models.Team.objects.filter(name=team_name).first()

        self.set_relations(instance, json_data)
        if instance.agent_id == UNASSIGNED_AGENT_ID:
            instance.agent = None
        if instance.client_id == UNASSIGNED_CLIENT_ID:
            instance.client = None

    def _post_sync_operations(self, results):
        if self.full:
            # Perform second sync for tickets that were closed
            # within the keep_closed_days setting.

            self.client.remove_condition('open_only')

            self.client.add_condition({
                'lastupdatefromdate':
                    self._get_keep_closed_cutoff().strftime(
                        '%Y-%m-%dT%H:%M:%S.%fZ')
            })
            self.client.add_condition({
                'closed_only': True,
            })

            results = self.fetch_records(results)

        return results

    def get_related_synchronizers(self, instance):
        """
        Return a list of related synchronizers.
        """
        sync_classes = []

        appointment_sync = AppointmentSynchronizer(
            full=True,
            conditions=[{
                'ticket_id': instance.id
            }]
        )

        sync_classes.append((appointment_sync, {'ticket': instance.id}))

        action_sync = ActionSynchronizer(
            full=True,
            parent_object_id=instance.id,
            conditions=[{
                'ticket_id': instance.id
            }])

        sync_classes.append((action_sync, {'ticket': instance.id}))

        return sync_classes

    def _try_validate(self, record):
        # Prevents closed tickets that were updated from re-syncing
        # every time there is an update to them.

        date_closed = record.get('dateclosed')

        if not date_closed:
            # Not closed, return true immediately.
            # Shouldn't happen, but just in case...
            return True

        true_date_closed = sync.empty_date_parser(date_closed)

        if true_date_closed:
            closed_date_cutoff = self._get_keep_closed_cutoff()

            if true_date_closed < closed_date_cutoff:
                # Closed, but older than the cutoff
                return False

        # Closed, but within the cutoff OR date_closed is not a valid date
        return True

    def _get_keep_closed_cutoff(self):
        djpsa_settings = get_djpsa_settings()
        keep_closed_days = djpsa_settings['keep_closed_days']

        return timezone.now() - timezone.timedelta(days=keep_closed_days)
