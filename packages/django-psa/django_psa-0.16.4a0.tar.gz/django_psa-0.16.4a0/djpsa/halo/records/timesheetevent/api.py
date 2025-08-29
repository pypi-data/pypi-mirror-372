from djpsa.halo.api import HaloAPIClient


class TimesheetEventAPI(HaloAPIClient):
    # This is just for logging time, ugh
    endpoint = 'TimesheetEvent'
