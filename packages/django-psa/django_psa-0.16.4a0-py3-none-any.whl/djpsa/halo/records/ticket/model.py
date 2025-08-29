from enum import Enum

from django.db import models
from model_utils import FieldTracker


class ItilRequestType(Enum):
    # System defined ITIL request types. We can use these to identify
    # the type of ticket we are dealing with. This is useful for
    # when an instance has custom ticket types beyond the default.
    INCIDENT = 1
    CHANGE_REQUEST = 2
    SERVICE_REQUEST = 3
    PROBLEM = 4
    REQUEST_FOR_QUOTE = 20
    ADVICE_OTHER = 21
    PROJECTS = 22
    TASKS = 23


class TicketOnlyManager(models.Manager):
    """
    Tickets are tickets that are not in the appropriate ITIL request type
    and don't have a parent project.
    """
    def get_queryset(self):
        return super().get_queryset().exclude(
            itil_request_type=ItilRequestType.PROJECTS.value,
            project=None,
        )


class ProjectOnlyManager(models.Manager):
    """
    Projects are tickets with the appropriate ITIL request type
    and have no relation to a parent project.

    This should match the logic of the is_project method.
    """
    def get_queryset(self):
        return super().get_queryset().filter(
            itil_request_type=ItilRequestType.PROJECTS.value,
            project=None,
        )


class Ticket(models.Model):
    summary = models.CharField(blank=True, null=True, max_length=255)
    details = models.TextField(
        blank=True, null=True
    )
    status = models.ForeignKey('Status', on_delete=models.CASCADE)
    priority = models.ForeignKey(
        'Priority', blank=True, null=True, on_delete=models.CASCADE)
    client = models.ForeignKey(
        'Client', blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(
        'Agent', blank=True, null=True, on_delete=models.CASCADE)
    sla = models.ForeignKey(
        'SLA', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(
        'HaloUser', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name='Contact',
    )
    site = models.ForeignKey(
        'Site', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey(
        'TicketType', blank=True, null=True, on_delete=models.CASCADE)
    project = models.ForeignKey(
        'Ticket', blank=True, null=True, on_delete=models.CASCADE)
    team = models.ForeignKey(
        'Team', blank=True, null=True, on_delete=models.CASCADE)
    user_email = models.EmailField(blank=True, null=True)
    reported_by = models.CharField(max_length=255, blank=True, null=True)
    end_user_status = models.IntegerField(blank=True, null=True)
    category_1 = models.CharField(max_length=255, blank=True, null=True)
    category_2 = models.CharField(max_length=255, blank=True, null=True)
    category_3 = models.CharField(max_length=255, blank=True, null=True)
    category_4 = models.CharField(max_length=255, blank=True, null=True)
    inactive = models.BooleanField(default=False)
    sla_response_state = \
        models.CharField(max_length=255, blank=True, null=True)
    sla_hold_time = models.FloatField(blank=True, null=True)
    date_occurred = models.DateTimeField(blank=True, null=True)
    respond_by_date = models.DateTimeField(blank=True, null=True)
    fix_by_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name='Fix by',
    )
    date_assigned = models.DateTimeField(blank=True, null=True)
    response_date = models.DateTimeField(blank=True, null=True)
    deadline_date = models.DateTimeField(
        blank=True, null=True,
        verbose_name='Deadline',
    )
    last_action_date = models.DateTimeField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)
    date_closed = models.DateTimeField(blank=True, null=True)

    # Target and Start date are actually 2 fields from Halo,
    # but we are syncing both into the same field in the model.
    target_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)

    last_incoming_email = models.DateTimeField(blank=True, null=True)
    impact = models.IntegerField(blank=True, null=True)
    impact_level = models.IntegerField(blank=True, null=True)
    flagged = models.BooleanField(default=False)
    on_hold = models.BooleanField(default=False)
    project_time_actual = models.FloatField(blank=True, null=True)
    project_money_actual = models.FloatField(blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    estimate = models.FloatField(
        blank=True, null=True,
        help_text='Effort in hours',
    )
    estimated_days = models.FloatField(blank=True, null=True)
    exclude_from_sla = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    email_to_list = models.TextField(blank=True, null=True)
    urgency = models.IntegerField(blank=True, null=True)
    service_status_note = \
        models.TextField(blank=True, null=True)
    ticket_tags = models.TextField(blank=True, null=True)
    appointment_type = models.IntegerField(blank=True, null=True)
    itil_request_type = models.IntegerField(
        choices=[(
            e.value,
            e.name.replace('_', ' ').title()
        ) for e in ItilRequestType],
        default=ItilRequestType.INCIDENT.value,
        verbose_name='ITIL request type'
    )

    use = models.CharField(max_length=255, blank=True, null=True)

    API_FIELDS = {
        "id": "id",
        "summary": "summary",
        "details": "details",
        "last_action_date": "lastactiondate",
        "last_update": "last_update",
        "date_closed": "dateclosed",
        "user_email": "useremail",
        "reported_by": "reportedby",
        "end_user_status": "enduserstatus",
        "category_1": "category1",
        "category_2": "category2",
        "category_3": "category3",
        "category_4": "category4",
        "inactive": "inactive",
        "impact": "impact",
        "deadline_date": "deadlinedate",
        "flagged": "flagged",
        "on_hold": "onhold",
        "cost": "cost",
        "estimate": "estimate",
        "estimated_days": "estimateddays",
        "exclude_from_sla": "excludefromslas",
        "team": "team",
        "read": "read",
        "use": "use",
        "email_to_list": "emailtolist",
        "urgency": "urgency",
        "service_status_note": "servicestatusnote",
        "ticket_tags": "tickettags",
        "appointment_type": "appointment_type",
        "impact_level": "impactlevel",
        "fix_by_date": "fixbydate",
        "start_date": "startdate",
        "target_date": "targetdate",
        "last_incoming_email": "lastincomingemail",
        "client": "client_id",
        "status": "status_id",
        "priority": "priority_id",
        "agent": "agent_id",
        "sla": "sla_id",
        "user": "user_id",
        "site": "site_id",
        "type": "tickettype_id",
        "itil_request_type": "itil_requesttype_id",
        "project": "parent_id",
    }

    objects = models.Manager()
    tickets_only = TicketOnlyManager()
    projects_only = ProjectOnlyManager()

    class Meta:
        verbose_name_plural = "Tickets"

    def __str__(self):
        return str(self.summary)

    @property
    def budget_hours(self):
        budget_hours = 0

        for budget in self.budgetdata_set.all():
            budget_hours += budget.hours

        return budget_hours

    def is_project(self):
        """
        Return true if this is a project.

        This should match the projects_only manager logic.
        """
        return (self.itil_request_type == ItilRequestType.PROJECTS.value and
                self.project is None)


class TicketTracker(Ticket):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_ticket'
