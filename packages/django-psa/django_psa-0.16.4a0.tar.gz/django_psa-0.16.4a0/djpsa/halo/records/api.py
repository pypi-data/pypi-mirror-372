# This file is used to import all the api classes for the records module
# from a single location.

from djpsa.halo.records.ticket.api import TicketAPI
from djpsa.halo.records.priority.api import PriorityAPI
from djpsa.halo.records.status.api import StatusAPI
from djpsa.halo.records.client.api import ClientAPI
from djpsa.halo.records.agent.api import AgentAPI
from djpsa.halo.records.site.api import SiteAPI
from djpsa.halo.records.sla.api import SLAAPI
from djpsa.halo.records.appointment.api import AppointmentAPI
from djpsa.halo.records.halouser.api import UserAPI
from djpsa.halo.records.tickettype.api import TicketTypeAPI
from djpsa.halo.records.action.api import ActionAPI
from djpsa.halo.records.team.api import TeamAPI
from djpsa.halo.records.budgettype.api import BudgetTypeAPI
from djpsa.halo.records.budgetdata.api import BudgetDataAPI
from djpsa.halo.records.outcome.api import OutcomeAPI
from djpsa.halo.records.chargerate.api import ChargeRateAPI
from djpsa.halo.records.timesheetevent.api import TimesheetEventAPI
