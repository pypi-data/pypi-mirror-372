import logging

from django.utils import timezone
from dateutil.parser import parse
from djpsa.sync.sync import Synchronizer
from django.db.models.fields import DateTimeField
from django.db.models.fields.related import ForeignKey

# README #
#
# "response_key"
#    The Halo API is very inconsistent, the response_key field is used to
#     specify the key in the response that contains the data we want to unpack.
#
#     Where when the response is just a list with no key, the response_key is
#     omitted from the class. ResponseKeyMixin should be applied to any class
#     that requires the response_key field.
#
# "lookup_key"
#    Some records need to be tracked by a different field than id for the
#     primary key. For example, the priority model uses priorityid as the
#     primary key, so the lookup_key is set to 'priorityid'. This is because
#     in the Halo API the 'id' seems to be a large alphanumeric string, and
#     isn't used on the ticket model.

logger = logging.getLogger(__name__)


def empty_date_parser(date_time):
    # Halo API returns a date of 1/1/1900 or earlier as an empty date.
    # This will set the model fields as None if it is an impossible date.
    # Set to 1980 in case they also do 1950 or something and I haven't seen it.
    if date_time:
        try:
            date_time = timezone.make_aware(parse(date_time), timezone.utc)
        except ValueError:
            date_time = parse(date_time)
        return date_time if date_time.year > 1980 else None


class ResponseKeyMixin:
    response_key = None

    def _unpack_records(self, response):
        records = response[self.response_key]
        return records


class ApiConvertMixin:
    client = None
    model_class = None

    def _convert_fields_to_api_format(self, data):
        """
        Converts the model field names to the API field names.
        """
        api_data = {}
        for key, value in data.items():
            api_data[self.model_class.API_FIELDS[key]] = value
        return api_data

    def _convert_fields(self, data):
        """
        Convert field values as necessary:
        * Datetime fields to ISO string format.
        * Team just wants a name, not the ID.
        * Foreign keys to the ID of the related object.
        """
        for key, value in data.items():
            field_class = self.model_class._meta.get_field(key).__class__
            if field_class == DateTimeField:
                data[key] = value.isoformat() if value else None
            elif key == 'team':
                # Team requires the name of the team, not the ID. :rageguy:
                data[key] = value.name if value else None
            elif field_class == ForeignKey:
                try:
                    data[key] = value.id if value else None
                except AttributeError:
                    # The field is a string, not a model instance.
                    data[key] = value
            else:
                data[key] = value
        return data


class CreateMixin(ApiConvertMixin):

    def create(self, data, *args, **kwargs):
        data = self._convert_fields(data)
        body = self._convert_fields_to_api_format(data)
        response = self.client.create(body)

        instance, _ = self.update_or_create_instance(response)
        return instance


class UpdateMixin(ApiConvertMixin):

    def update(self, record, data, *args, **kwargs):
        data = self._convert_fields(data)
        body = self._convert_fields_to_api_format(data)

        response = self.client.update(record.id, body)

        instance, _ = self.update_or_create_instance(response)
        return instance


class DeleteMixin:
    client = None

    def delete(self, record_id, *args, **kwargs):
        return self.client.delete(record_id)


class HaloSynchronizer(Synchronizer):

    def _format_job_condition(self, last_sync_time):
        return {
            self.last_updated_field: last_sync_time
        }


class HaloChildFetchRecordsMixin:
    parent_model_class = None
    parent_field = None

    def __init__(self, parent_object_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_object_id = parent_object_id

    def fetch_records(self, results, params=None):
        params = params or {}

        batch = 1
        for object_id in self.parent_object_ids:
            logger.info(
                'Fetching {} records, batch {}'.format(
                    self.get_model_name(), batch)
            )
            params.update(self.format_parent_params(object_id))
            response = self.client.fetch_resource(params=params)
            records = self._unpack_records(response)
            self.persist_page(records, results)
            batch += 1

        return results

    @property
    def parent_object_ids(self):
        object_ids = self.parent_model_class.objects.all() \
            .values_list('id', flat=True)

        if self.parent_object_id:
            object_ids = [self.parent_object_id]

        return object_ids

    def format_parent_params(self, object_id):
        return {
            self.parent_field: object_id
        }
