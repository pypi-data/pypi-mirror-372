from django.apps import AppConfig
from django.conf import settings


class HaloConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djpsa.halo'
    label = 'halo'

    def ready(self):
        from djpsa.halo import provider
        settings.PROVIDER = provider
