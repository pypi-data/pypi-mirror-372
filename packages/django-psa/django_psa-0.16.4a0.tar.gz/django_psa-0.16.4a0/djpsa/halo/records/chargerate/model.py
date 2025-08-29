from django.db import models
from model_utils import FieldTracker


class ChargeRate(models.Model):
    # Currently charge rates are only used for creating time entries.
    # We don't need the rate data or anything, but the user needs to
    # select one to create a time sheet event.
    name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.name)


class ChargeRateTracker(ChargeRate):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_chargerate'
