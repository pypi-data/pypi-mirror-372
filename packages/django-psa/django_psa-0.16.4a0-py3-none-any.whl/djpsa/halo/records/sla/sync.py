from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


class SLASynchronizer(sync.HaloSynchronizer):

    model_class = models.SLATracker
    client_class = api.StatusAPI

    def _assign_field_data(self, instance, json_data):

        instance.id = json_data.get('id')
        instance.name = json_data.get('name')
        instance.hours_are_techs_local_time = \
            json_data.get('hoursaretechslocaltime', False)
        instance.response_reset = json_data.get('responsereset', False)
        instance.response_reset_approval = \
            json_data.get('response_reset_approval', False)
        instance.track_sla_fix_by_time = \
            json_data.get('trackslafixbytime', False)
        instance.track_sla_response_time = \
            json_data.get('trackslaresponsetime', False)
        instance.workday_id = json_data.get('workday_id')
        instance.auto_release_limit = json_data.get('autoreleaselimit')
        instance.auto_release_option = \
            json_data.get('autoreleaseoption', False)
        instance.status_after_first_warning = \
            json_data.get('statusafterfirstwarning')
        instance.status_after_second_warning = \
            json_data.get('statusaftersecondwarning')
        instance.status_after_auto_release = \
            json_data.get('statusafterautorelease')
