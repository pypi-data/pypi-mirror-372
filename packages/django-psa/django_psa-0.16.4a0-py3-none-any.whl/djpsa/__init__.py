# -*- coding: utf-8 -*-
from importlib.metadata import version

__version__ = version("django-psa")

default_app_config = 'djpsa.sync.apps.SyncConfig'
