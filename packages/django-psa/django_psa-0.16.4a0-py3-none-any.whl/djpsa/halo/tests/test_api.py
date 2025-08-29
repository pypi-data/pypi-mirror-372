import unittest
from unittest.mock import patch, MagicMock
from djpsa.halo.api import HaloAPIClient


class TestHaloAPIClient(unittest.TestCase):

    @patch('djpsa.halo.api.requests.request')
    @patch('djpsa.halo.api.HaloAPITokenFetcher.get_token',
           return_value='test_token')
    def test_request_success(self, _, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        client = HaloAPIClient()
        response = client._request('GET', 'http://example.com')

        self.assertEqual(response, mock_response)
        mock_request.assert_called_once_with(
            'GET',
            'http://example.com',
            headers={'Authorization': 'Bearer test_token'},
            params=None,
            timeout=30.0
        )

    @patch('djpsa.halo.api.requests.request')
    @patch('djpsa.halo.api.HaloAPITokenFetcher.get_token')
    def test_request_token_refresh(
            self, mock_get_token, mock_request):
        mock_get_token.side_effect = ['expired_token', 'new_token']
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_request.side_effect = [mock_response_401, mock_response_200]

        client = HaloAPIClient()
        response = client._request('GET', 'http://example.com')

        self.assertEqual(response, mock_response_200)
        self.assertEqual(mock_get_token.call_count, 2)
        self.assertEqual(mock_request.call_count, 2)
        mock_request.assert_called_with(
            'GET',
            'http://example.com',
            headers={'Authorization': 'Bearer new_token'},
            params=None
        )
