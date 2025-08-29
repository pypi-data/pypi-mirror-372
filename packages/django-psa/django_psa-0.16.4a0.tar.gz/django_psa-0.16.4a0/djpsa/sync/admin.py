import datetime

from django.contrib import admin

from djpsa.sync import models


@admin.register(models.SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    actions = None
    change_form_template = 'change_form.html'
    list_display = (
        'id', 'start_time', 'end_time', 'duration_or_zero', 'entity_name',
        'synchronizer_class', 'success', 'added', 'updated', 'skipped',
        'deleted', 'sync_type',
    )
    list_filter = ('sync_type', 'success', 'entity_name', 'synchronizer_class')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def duration_or_zero(self, obj):
        """
        Return the duration, or just the string 0 (otherwise we get 0:00:00)
        """
        duration = obj.duration()
        if duration:
            # Get rid of the microseconds part
            duration_seconds = duration - datetime.timedelta(
                microseconds=duration.microseconds
            )
            return duration_seconds if duration_seconds else '0'
    duration_or_zero.short_description = 'Duration'
