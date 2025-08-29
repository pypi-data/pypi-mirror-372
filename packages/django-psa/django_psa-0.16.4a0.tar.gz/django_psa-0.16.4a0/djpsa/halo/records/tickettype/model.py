from django.db import models
from model_utils import FieldTracker


class TicketType(models.Model):
    name = models.CharField(max_length=255)
    agents_can_select = models.BooleanField(default=False)
    end_users_can_select = models.BooleanField(default=False)
    allow_attachments = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    copy_attachments_to_child = models.BooleanField(default=False)
    copy_attachments_to_related = models.BooleanField(default=False)
    use = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.name)


class TicketTypeTracker(TicketType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_tickettype'
