import unittest
import requests
from unittest.mock import patch, MagicMock
from json import JSONDecodeError

from djpsa.api.client import APIClient
from djpsa.api import exceptions as exc


class TestAPIClient(unittest.TestCase):

    def setUp(self):
        self.client = APIClient()
        self.client.request_settings = {
            'max_attempts': 3,
            'timeout': 5
        }

    @patch('djpsa.api.client.APIClient.request')
    def test_fetch_resource_success(self, mock_request):
        mock_request.return_value = {'data': 'test'}
        response = \
            self.client.fetch_resource('http://example.com/api/resource')
        self.assertEqual(response, {'data': 'test'})

    @patch('djpsa.api.client.APIClient.request')
    def test_fetch_resource_api_error(self, mock_request):
        mock_request.side_effect = exc.APIError('API Error')
        with self.assertRaises(exc.APIError):
            self.client.fetch_resource('http://example.com/api/resource')

    @patch.object(
        APIClient, '_format_endpoint', return_value='http://example.com')
    @patch.object(APIClient, '_request')
    @patch.object(APIClient, '_get_headers', return_value={})
    @patch.object(
        APIClient, '_format_params', return_value={'param': 'value'})
    def test_request_success(self, _, _a, mock_request, mock_format_endpoint):
        client = APIClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'key': 'value'}
        mock_request.return_value = mock_response

        response = client.request('GET')

        self.assertEqual(response, {'key': 'value'})
        mock_format_endpoint.assert_called_once()
        mock_request.assert_called_once_with(
            'GET', 'http://example.com', headers={}, params={'param': 'value'})

    @patch.object(
        APIClient, '_format_endpoint', return_value='http://example.com')
    @patch.object(APIClient, '_request')
    @patch.object(APIClient, '_get_headers', return_value={})
    @patch.object(APIClient, '_format_params', return_value={'param': 'value'})
    def test_request_json_decode_error(
            self, _, _a, mock_request, mock_format_endpoint):
        client = APIClient()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = \
            JSONDecodeError('Expecting value', 'doc', 0)
        mock_request.return_value = mock_response

        with self.assertRaises(exc.APIError):
            client.request('GET')

        mock_format_endpoint.assert_called_once()
        mock_request.assert_called_once_with(
            'GET', 'http://example.com', headers={}, params={'param': 'value'})

    @patch.object(
        APIClient, '_format_endpoint', return_value='http://example.com')
    @patch.object(APIClient, '_request')
    @patch.object(APIClient, '_get_headers', return_value={})
    @patch.object(APIClient, '_format_params', return_value={'param': 'value'})
    def test_request_request_exception(
            self, _, _a, mock_request, mock_format_endpoint):
        client = APIClient()
        mock_request.side_effect = requests.RequestException('Request failed')

        with self.assertRaises(exc.APIError):
            client.request('GET')

        mock_format_endpoint.assert_called_once()
        mock_request.assert_called_once_with(
            'GET', 'http://example.com', headers={}, params={'param': 'value'})

    @patch.object(
        APIClient, '_format_endpoint', return_value='http://example.com')
    @patch.object(APIClient, '_request')
    @patch.object(APIClient, '_get_headers', return_value={})
    @patch.object(APIClient, '_format_params', return_value={'param': 'value'})
    def test_request_unexpected_code(
            self, _, _a, mock_request, mock_format_endpoint):
        client = APIClient()
        mock_response = MagicMock()
        mock_response.status_code = 418
        mock_request.return_value = mock_response

        with self.assertRaises(exc.APIError):
            client.request('GET')

        mock_format_endpoint.assert_called_once()
        mock_request.assert_called_once_with(
            'GET', 'http://example.com', headers={}, params={'param': 'value'})
