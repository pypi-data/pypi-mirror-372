from django.db import models
from model_utils import FieldTracker


class Status(models.Model):
    name = models.CharField(max_length=255)
    colour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Statuses"

    def __str__(self):
        return str(self.name)


class StatusTracker(Status):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_status'
