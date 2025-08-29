from django.db import models
from model_utils import FieldTracker


class HaloUser(models.Model):

    # This is their username, even though it comes through the API
    # as name.
    name = models.CharField(max_length=255, blank=True, null=True)

    first_name = models.CharField(max_length=255, blank=True, null=True)
    initials = models.CharField(max_length=10, blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(null=True, blank=True, max_length=250)
    colour = models.CharField(max_length=50, null=True, blank=True)
    active = models.BooleanField(default=True)
    login = models.CharField(max_length=255, blank=True, null=True)
    use = models.CharField(max_length=255, blank=True, null=True)
    client = models.ForeignKey(
        'Client', blank=True, null=True, on_delete=models.CASCADE)
    agent = models.ForeignKey(
        'Agent', blank=True, null=True, on_delete=models.CASCADE)
    site = models.ForeignKey(
        'Site', blank=True, null=True, on_delete=models.SET_NULL)
    never_send_emails = models.BooleanField(default=False)
    phone_number = models.CharField(blank=True, null=True, max_length=250)
    mobile_number = models.CharField(blank=True, null=True, max_length=250)
    mobile_number_2 = models.CharField(blank=True, null=True, max_length=250)
    home_number = models.CharField(blank=True, null=True, max_length=250)
    tel_pref = models.IntegerField(blank=True, null=True)
    is_service_account = models.BooleanField(default=False)
    is_important_contact = models.BooleanField(default=False)
    is_important_contact_2 = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Halo Users"

    def __str__(self):
        return str(self.name)


class HaloUserTracker(HaloUser):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'halo_halouser'
