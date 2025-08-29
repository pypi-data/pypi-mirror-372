from djpsa.halo.records import api


class BudgetDataAPI(api.TicketAPI):
    # Not a real endpoint, just an easy way to get
    # budgets off of a ticket

    def get(self, record_id):
        return self.request(
            'GET', endpoint_url=self._format_endpoint(record_id))
