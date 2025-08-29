import json
import logging
import hmac
import hashlib
import base64

from braces import views
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings

from djpsa.halo.records.ticket.sync import TicketSynchronizer

logger = logging.getLogger(__name__)


class CallBackView(views.CsrfExemptMixin,
                   views.JsonRequestResponseMixin, View):
    entity_type = None
    sync_class = None
    callback_handler = None

    def post(self, request, *args, **kwargs):
        logger.debug(f"Received callback {request.path} {request.method}")

        try:
            received_token = request.headers['Token']
        except KeyError:
            logger.error('Token header missing in webhook request')
            return HttpResponse(status=401)

        computed_hash = hmac.new(
            settings.CALLBACK_SECRET.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).digest()
        computed_token = base64.b64encode(computed_hash).decode()

        if not hmac.compare_digest(computed_token, received_token):
            logger.error('Invalid token received')
            return HttpResponse(status=401)

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError as e:
            logger.error('Error decoding JSON for callback: %s', e)
            return HttpResponse(status=400)

        self.handle(data)

        return HttpResponse(status=200)

    def handle(self, data):
        """
        Do the interesting stuff here, so that it can be overridden in
        a child class if needed.
        """

        if self.callback_handler:
            # Call the callback handler if it's defined
            self.callback_handler(data)
        else:
            sync = self.sync_class()

            instance, _ = sync.update_or_create_instance(
                data.get(self.entity_type))

            # Sync related records, actions, appointments, etc.
            sync.sync_related(instance)

    @classmethod
    def register_callback_handler(cls, callback_handler):
        """
        Register a callback handler for the ticket callback.
        """
        cls.callback_handler = callback_handler


class TicketCallBackView(CallBackView):

    entity_type = 'ticket'
    sync_class = TicketSynchronizer

    # This must be defined on child classes or the parent class
    # handler will be overridden for each child class.
    callback_handler = None
