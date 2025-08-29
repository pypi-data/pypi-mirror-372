from django.db import models
from model_utils import FieldTracker


class Priority(models.Model):
    # priorityid is actual ID for sync
    name = models.CharField(max_length=255, blank=True, null=True)
    is_hidden = models.BooleanField(default=False)
    colour = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Priorities"

    def __str__(self):
        return str(self.name)


class PriorityTracker(Priority):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_priority'
