from djpsa.halo.api import HaloAPIClient


UNASSIGNED_CLIENT_ID = 1  # See comment in agent/api.py


class ClientAPI(HaloAPIClient):
    endpoint = 'Client'
