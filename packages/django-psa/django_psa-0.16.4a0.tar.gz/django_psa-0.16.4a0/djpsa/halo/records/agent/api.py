from djpsa.halo.api import HaloAPIClient


UNASSIGNED_AGENT_ID = 1  # The Agent with id 1 represents the concept of being
# unassigned. Apparently the designer of this API dropped out before the
# lesson on NULLs.


class AgentAPI(HaloAPIClient):
    endpoint = 'Agent'
