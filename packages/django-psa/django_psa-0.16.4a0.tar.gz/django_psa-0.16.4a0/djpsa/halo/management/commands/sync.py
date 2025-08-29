from collections import OrderedDict

from djpsa.halo.records import sync
from djpsa.sync.management.commands.base_sync import BaseSyncCommand


class Command(BaseSyncCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.synchronizer_map = OrderedDict(sync.sync_command_list)
