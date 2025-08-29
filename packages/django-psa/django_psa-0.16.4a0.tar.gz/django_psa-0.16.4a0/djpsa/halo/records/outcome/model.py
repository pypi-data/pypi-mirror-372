from django.db import models
from model_utils import FieldTracker


class Outcome(models.Model):
    """
    Outcomes are essentially "Action Types"
    """
    # outcome is the name field of Outcome
    outcome = models.CharField(max_length=255)
    button_name = models.CharField(max_length=255)
    label_long = models.CharField(max_length=255)
    sequence = models.IntegerField()
    hidden = models.BooleanField(default=False)
    icon = models.CharField(max_length=255)

    def __str__(self):
        return str(self.outcome)


class OutcomeTracker(Outcome):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_outcome'
