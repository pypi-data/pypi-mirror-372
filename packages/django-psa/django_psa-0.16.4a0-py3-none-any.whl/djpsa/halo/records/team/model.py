from django.db import models
from model_utils import FieldTracker


class Team(models.Model):
    name = models.CharField(max_length=255)
    ticket_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Teams"

    def __str__(self):
        return str(self.name)


class TeamTracker(Team):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_team'
