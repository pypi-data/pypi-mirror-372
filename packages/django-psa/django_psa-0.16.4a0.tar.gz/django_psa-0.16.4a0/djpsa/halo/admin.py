from django.contrib import admin

from djpsa.halo import models


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'summary',
        'client',
        'status',
        'priority',
        'agent',
        'type'
    )
    search_fields = [
        'id',
        'summary',
        'client__name',
        'status__name',
        'priority__name',
        'agent__name'
    ]
    list_filter = ('status', 'priority', 'agent', 'type')


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'inactive')
    search_fields = ['id', 'name']


@admin.register(models.Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_disabled')
    search_fields = ['id', 'name']


@admin.register(models.Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


@admin.register(models.Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'colour')
    search_fields = ['id', 'name']
    list_filter = ('is_hidden',)


@admin.register(models.TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


@admin.register(models.HaloUser)
class HaloUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'active', 'agent', 'client', 'site')
    search_fields = ['id', 'name', 'email']


@admin.register(models.Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'start_date', 'end_date')
    search_fields = ['id', 'subject']


@admin.register(models.SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


@admin.register(models.Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


@admin.register(models.Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'outcome',
        'action_arrival_date',
        'action_completion_date',
        'time_taken',
        'note')
    search_fields = \
        ['id', 'ticket__id', 'time_taken', 'project__id', 'agent__id']


@admin.register(models.Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'outcome')
    search_fields = ['id', 'name']


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'ticket_count')
    search_fields = ['id', 'name']


@admin.register(models.ChargeRate)
class ChargeRateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


@admin.register(models.BudgetType)
class BudgetTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['id', 'name']


@admin.register(models.BudgetData)
class BudgetDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'budget_type', 'ticket')
    search_fields = ['id', 'budget_type__name', 'ticket__id']
