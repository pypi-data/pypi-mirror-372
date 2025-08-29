from djpsa.halo.api import HaloAPIClient


class ChargeRateAPI(HaloAPIClient):
    # Including parameter in the endpoint because we never
    # want this API class to access a different lookup id.
    endpoint = 'Lookup?lookupid=17'
