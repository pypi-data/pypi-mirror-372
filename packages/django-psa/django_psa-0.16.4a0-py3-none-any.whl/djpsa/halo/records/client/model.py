from django.db import models
from model_utils import FieldTracker


class Client(models.Model):
    name = models.CharField(max_length=255)
    inactive = models.BooleanField(default=False)
    colour = models.CharField(max_length=255, blank=True, null=True)
    main_site = models.ForeignKey('Site',
                                  blank=True,
                                  null=True,
                                  on_delete=models.SET_NULL,
                                  related_name='client_primary'
                                  )
    phone_number = models.CharField(blank=True, null=True, max_length=250)

    class Meta:
        verbose_name_plural = "Clients"

    def __str__(self):
        return str(self.name)


class ClientTracker(Client):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_client'
