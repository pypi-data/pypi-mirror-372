# This file is used to import all the models for the records module
#  from a single location.

from djpsa.halo.records.ticket.model import Ticket, TicketTracker
from djpsa.halo.records.priority.model import Priority, PriorityTracker
from djpsa.halo.records.status.model import Status, StatusTracker
from djpsa.halo.records.client.model import Client, ClientTracker
from djpsa.halo.records.agent.model import Agent, AgentTracker
from djpsa.halo.records.site.model import Site, SiteTracker
from djpsa.halo.records.sla.model import SLA, SLATracker
from djpsa.halo.records.appointment.model import Appointment, AppointmentTracker
from djpsa.halo.records.halouser.model import HaloUser, HaloUserTracker
from djpsa.halo.records.tickettype.model import TicketType, TicketTypeTracker
from djpsa.halo.records.action.model import Action, ActionTracker
from djpsa.halo.records.team.model import Team, TeamTracker
from djpsa.halo.records.budgettype.model import BudgetType, BudgetTypeTracker
from djpsa.halo.records.budgetdata.model import BudgetData, BudgetDataTracker
from djpsa.halo.records.outcome.model import Outcome, OutcomeTracker
from djpsa.halo.records.chargerate.model import ChargeRate, ChargeRateTracker
