# This file is used to import all the synchronizers for the records module
# from a single location.

from django.utils.translation import gettext_lazy as _

from djpsa.halo.records.ticket.sync import TicketSynchronizer
from djpsa.halo.records.priority.sync import PrioritySynchronizer
from djpsa.halo.records.status.sync import StatusSynchronizer
from djpsa.halo.records.client.sync import ClientSynchronizer
from djpsa.halo.records.agent.sync import AgentSynchronizer
from djpsa.halo.records.site.sync import SiteSynchronizer
from djpsa.halo.records.sla.sync import SLASynchronizer
from djpsa.halo.records.appointment.sync import AppointmentSynchronizer
from djpsa.halo.records.halouser.sync import HaloUserSynchronizer
from djpsa.halo.records.tickettype.sync import TicketTypeSynchronizer
from djpsa.halo.records.action.sync import ActionSynchronizer
from djpsa.halo.records.team.sync import TeamSynchronizer
from djpsa.halo.records.budgettype.sync import BudgetTypeSynchronizer
from djpsa.halo.records.budgetdata.sync import BudgetDataSynchronizer
from djpsa.halo.records.outcome.sync import OutcomeSynchronizer
from djpsa.halo.records.chargerate.sync import ChargeRateSynchronizer
from djpsa.halo.records.timesheetevent.sync import TimeSheetEventSynchronizer

from djpsa.sync.grades import SyncGrades


class HaloSyncGrades(SyncGrades):
    def partial_grades(self):
        return [
            TicketSynchronizer,
        ]

    def operational_grades(self):
        return [
            HaloUserSynchronizer,
            AgentSynchronizer,
            ClientSynchronizer,
            TicketSynchronizer,
            AppointmentSynchronizer,
            ActionSynchronizer,
        ]

    def configuration_grades(self):
        """
        Return a list of synchronizers for resources that change infrequently-
        such as on a weekly or monthly basis. For example, ticket types, statuses,
        priorities, etc.
        """
        return [
            SLASynchronizer,
            StatusSynchronizer,
            SiteSynchronizer,
            PrioritySynchronizer,
            TicketTypeSynchronizer,
            ChargeRateSynchronizer,
            OutcomeSynchronizer,
            TeamSynchronizer,
            BudgetTypeSynchronizer,
            BudgetDataSynchronizer,
        ]


sync_command_list = [
        ('status', (StatusSynchronizer, _('Status'))),
        ('priority', (PrioritySynchronizer, _('Priority'))),
        ('client', (ClientSynchronizer, _('Client'))),
        ('sla', (SLASynchronizer, _('SLA'))),
        ('site', (SiteSynchronizer, _('Site'))),
        ('user', (HaloUserSynchronizer, _('User'))),
        ('agent', (AgentSynchronizer, _('Agent'))),
        ('chargerate', (ChargeRateSynchronizer, _('ChargeRate'))),
        ('outcome', (OutcomeSynchronizer, _('Outcome'))),
        ('ticket_type', (TicketTypeSynchronizer, _('TicketType'))),
        ('ticket', (TicketSynchronizer, _('Ticket'))),
        ('appointment', (AppointmentSynchronizer, _('Appointment'))),
        ('action', (ActionSynchronizer, _('Action'))),
        ('team', (TeamSynchronizer, _('Team'))),
        ('budget_type', (BudgetTypeSynchronizer, _('BudgetType'))),
        ('budget_data', (BudgetDataSynchronizer, _('BudgetData'))),
    ]
