import logging

from djpsa.halo import models
from djpsa.halo.records import api
from djpsa.halo import sync


logger = logging.getLogger(__name__)


class BudgetDataSynchronizer(sync.HaloSynchronizer):
    model_class = models.BudgetDataTracker
    client_class = api.BudgetDataAPI

    related_meta = {
        'ticket_id': (models.Ticket, 'ticket'),
        'budgettype_id': (models.BudgetType, 'budget_type'),
    }

    def fetch_records(self, results, params=None):
        batch = 1
        for ticket in models.Ticket.objects.all().values_list(
                'id', flat=True):
            logger.info(
                'Fetching {} records, batch {}'.format(
                    self.get_model_name(), batch)
            )
            response = self.client.get(ticket)
            records = self._unpack_records(response)
            self.persist_page(records, results)
            batch += 1

        return results

    def _unpack_records(self, response):
        return response.get('budgets', list())

    @property
    def object_ids(self):
        object_ids = models.Ticket.objects.all() \
            .values_list('id', flat=True)

        return object_ids

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data.get('id')
        instance.hours = json_data.get('hours')
        instance.rate = json_data.get('rate')
        instance.money = json_data.get('money')
        instance.estimated_hours = json_data.get('estimated_hours')
        instance.estimated_money = json_data.get('estimated_money')
        instance.actual_hours = json_data.get('actual_hours')
        instance.actual_money = json_data.get('actual_money')
        instance.scheduled_hours = json_data.get('scheduled_hours')
        instance.scheduled_value = json_data.get('scheduled_value')
        instance.toschedule_hours = json_data.get('toschedule_hours')
        instance.toschedule_value = json_data.get('toschedule_value')
        instance.remaining_hours = json_data.get('remaining_hours')
        instance.remaining_value = json_data.get('remaining_value')

        self.set_relations(instance, json_data)
