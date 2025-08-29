import logging
import requests
import hashlib
from django.conf import settings
from django.core.cache import cache

from djpsa.api.client import APIClient
from djpsa.api.exceptions import APIError
from djpsa.utils import LockNotAcquiredError, redis_lock

logger = logging.getLogger(__name__)


HALO_TOKEN_CACHE_NAME = 'halo_token:{}:{}'
CACHE_EXPIRE_TIME = 3540  # 1 hour less 1 minute so the token expires
# locally before expiring remotely, so we avoid access denied errors.
TOKEN_REQUEST_TIMEOUT = 30
TOKEN_LOCK_LIFETIME = TOKEN_REQUEST_TIMEOUT + 1
TOKEN_LOCK_ACQUIRE_TIMEOUT = 60


class HaloAPICredentials:
    def __init__(self, authorisation_server, client_id, client_secret):
        self.authorisation_server = authorisation_server
        if not self.authorisation_server.endswith('/'):
            self.authorisation_server += '/'
        self.client_id = client_id
        self.client_secret = client_secret


class HaloAPIClient(APIClient):
    endpoint = None

    def __init__(self,
                 conditions=None,
                 credentials=None,
                 resource_server=None,
                 token_locking=True):
        super().__init__(conditions)
        if not credentials:
            credentials = HaloAPICredentials(
                settings.HALO_AUTHORISATION_SERVER,
                settings.HALO_CLIENT_ID,
                settings.HALO_CLIENT_SECRET,
            )

        self.resource_server = resource_server or settings.HALO_RESOURCE_SERVER
        if not self.resource_server.endswith('/'):
            self.resource_server += '/'

        self.token_fetcher = HaloAPITokenFetcher(credentials, token_locking)

    def check_auth(self):
        return bool(self.token_fetcher.get_token(use_cache=False))

    def get_page(self, page=None, batch_size=None, params=None):
        params = params or {}
        if page:
            params['page_no'] = page
        if batch_size:
            params['page_size'] = batch_size
        return self.fetch_resource(params=params)

    def get(self, record_id):
        return self.request('GET', params={'search_id': record_id})

    def create(self, data):
        # Halo API expects a list of records, even if we're only creating one
        if not isinstance(data, list):
            data = [data]

        return self.request('POST', body=data)

    def update(self, record_id, data):
        data.update({'id': record_id})
        if not isinstance(data, list):
            data = [data]
        return self.request('POST', body=data)

    def delete(self, record_id):
        return self.request(
            'DELETE',
            endpoint_url=self._format_endpoint(record_id)
        )

    def remove_condition(self, condition):
        # self.conditions is a list of dictionaries, so we need to remove the
        # dictionary that contains the key we want to remove, value doesn't
        # matter
        self.conditions = \
            [c for c in self.conditions if c.get(condition) is None]

    def _format_endpoint(self, record_id=None):

        if record_id:
            return '{}{}/{}'.format(
                self.resource_server, self.endpoint, record_id)

        return '{}{}'.format(self.resource_server, self.endpoint)

    def _format_params(self, params=None):
        params = params or {}
        request_params = {}

        for condition in self.conditions:
            request_params.update(condition)

        request_params.update(params)

        if 'page_no' in request_params:
            request_params['page_size'] = \
                params.get('page_size', self.request_settings['batch_size'])
            request_params['pageinate'] = True

        return request_params

    def _request(
            self, method, endpoint_url, headers=None, params=None, **kwargs):
        token = self.token_fetcher.get_token()
        token_header = {'Authorization': f'Bearer {token}'}

        # If kwargs contains headers, update it with the token, if not,
        # create it
        if headers:
            headers.update(token_header)
        else:
            headers = token_header

        logger.debug(
            'Making %s request to %s: params %s, kwargs %s',
            method, endpoint_url, params, kwargs
        )
        # Make the actual request
        response = requests.request(
            method,
            endpoint_url,
            headers=headers,
            params=params,
            timeout=self.request_settings['timeout'],
            **kwargs
        )

        # If the token is invalid, refresh it and retry
        if response.status_code == 401:
            token = self.token_fetcher.get_token()
            headers['Authorization'] = f'Bearer {token}'
            response = requests.request(
                method,
                endpoint_url,
                headers=headers,
                params=params,
                **kwargs
            )

        return response

    def _prepare_error_response(self, response):
        result = response.json()
        error = ""

        if isinstance(result, str):
            # Error responses can be a string.
            return result

        try:
            error = result['error']
            error_desc = error['error_description']
        except KeyError:
            try:
                error = result['ClassName']
                error_desc = result['Message']
            except KeyError:
                try:
                    if len(result) == 1:
                        # This is about the best we can do. The Halo API
                        # doesn't provide a standard error format. There's
                        # no telling how deep the rabbit hole goes. We will
                        # just have to handle new error types as they come.
                        error_desc = (list(result.values())[0]
                                      .replace(
                                          "\r", ""
                                      ).replace(
                                          "\n", ""
                                      ).replace(
                                          "\'", "")
                                      )
                    else:
                        logger.error(f"Unknown error format: {result}")
                        error_desc = "An unknown error has occurred."
                except Exception as e:
                    logger.error(
                        f"Failed to process error from response: "
                        f"{result}, {e}"
                    )
                    raise e

        return f"{error}: {error_desc}" if error else error_desc


class WebhookAPIClient(HaloAPIClient):
    endpoint = 'webhook'

    def get(self, **kwargs):
        return self.request('GET')


class NotificationAPIClient(HaloAPIClient):
    # API for webhook event creation, tickets, clients, etc
    endpoint = 'notification'


class HaloAPITokenFetcher:
    def __init__(self, credentials, token_locking=True):
        self.credentials = credentials
        self.token_locking = token_locking

    def get_token(self, use_cache=True):
        if use_cache:
            token = self._get_saved_token()
            if token:
                return token

        if self.token_locking:
            try:
                with redis_lock(
                        'halo_token_lock',
                        TOKEN_LOCK_LIFETIME,
                        TOKEN_LOCK_ACQUIRE_TIMEOUT):
                    # Check if a valid token is already available. May
                    # have been fetched by another worker thread while we
                    # were waiting.
                    if use_cache:
                        token = self._get_saved_token()
                        if token:
                            return token

                    # No valid token- get a new one.
                    # We'll save it even if we didn't use the cache, because
                    # it's possible getting a new token invalidates prior
                    # tokens.
                    return self._get_new_token_and_save()
            except LockNotAcquiredError as e:
                logger.error(f"Could not acquire lock: {e}")
        else:
            # Get a new token without locking
            return self._get_new_token_and_save()

    def _get_cache_name(self):
        """Return the cache name for the token."""
        # One-way hash of secret so it's not stored in plain text
        secret_hash = hashlib.sha256(
            self.credentials.client_secret.encode('utf-8')
        ).hexdigest()
        return HALO_TOKEN_CACHE_NAME.format(
            self.credentials.client_id, secret_hash)

    def _get_saved_token(self):
        return cache.get(self._get_cache_name())

    def _get_new_token_and_save(self):
        logger.debug('Getting new access token')
        token_url = '{}token'.format(self.credentials.authorisation_server)
        try:
            response = requests.post(
                token_url,
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'scope': 'all',
                },
                timeout=TOKEN_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            token = response.json()['access_token']
        except requests.RequestException as e:
            logger.error(f"Failed to get new token: {e}")
            raise APIError('{}'.format(e))

        cache.set(self._get_cache_name(), token, CACHE_EXPIRE_TIME)
        return token
