from django.db import models
from model_utils import FieldTracker


class SLA(models.Model):

    name = models.CharField(max_length=255)
    hours_are_techs_local_time = models.BooleanField(default=False)
    response_reset = models.BooleanField(default=False)
    response_reset_approval = models.BooleanField(default=False)
    track_sla_fix_by_time = models.BooleanField(default=False)
    track_sla_response_time = models.BooleanField(default=False)
    workday_id = models.IntegerField(blank=True, null=True)
    auto_release_limit = models.IntegerField(blank=True, null=True)
    auto_release_option = models.BooleanField(default=False)
    status_after_first_warning = models.IntegerField(blank=True, null=True)
    status_after_second_warning = models.IntegerField(blank=True, null=True)
    status_after_auto_release = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "SLAs"

    def __str__(self):
        return str(self.name)


class SLATracker(SLA):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_sla'
