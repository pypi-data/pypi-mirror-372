from typing import Any, List

from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class AgentSynchronizer(sync.ResponseKeyMixin,
                        sync.HaloSynchronizer):

    model_class = models.AgentTracker
    client_class = api.AgentAPI
    response_key = "results"

    def __init__(
            self,
            full: bool = False,
            conditions: List = None,
            *args: Any,
            **kwargs: Any):
        super().__init__(full, conditions, *args, **kwargs)
        self.client.add_condition({
            'includeenabled': True,
            'includedisabled': True,
            'includeunassigned': False,
        })

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.is_disabled = json_data.get('isdisabled')
        instance.email = json_data.get('email')
        instance.initials = json_data.get('initials')
        instance.firstname = json_data.get('firstname')
        instance.surname = json_data.get('surname')
        instance.colour = json_data.get('colour')

        teams = json_data.get('teams')
        if teams and instance.tracker.previous('id') is not None:
            # Teams can only be saved if the agent instance
            # already exists in the database. If it doesn't exist
            # yet, we'll let it be saved now and then next time this runs
            # the teams will be set.

            # Get the list of team IDs
            remote_team_ids = [team['team_id'] for team in teams]

            # Get the teams from the db
            local_teams = models.Team.objects.filter(id__in=remote_team_ids)

            # Set the teams for the agent instance, this handles adding
            # and removing teams from the agent instance.
            instance.teams.set(local_teams)
