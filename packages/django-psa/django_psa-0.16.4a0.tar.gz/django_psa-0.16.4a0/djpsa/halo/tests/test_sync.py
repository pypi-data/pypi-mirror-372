from unittest import TestCase
from django.utils import timezone
from dateutil.parser import parse
from djpsa.halo.sync import empty_date_parser, ResponseKeyMixin


class TestEmptyDateParser(TestCase):

    def test_valid_date(self):
        date_str = "2023-10-10T10:00:00"
        expected_date = timezone.make_aware(parse(date_str), timezone.utc)
        self.assertEqual(empty_date_parser(date_str), expected_date)

    def test_empty_date(self):
        date_str = "1900-01-01T00:00:00"
        self.assertIsNone(empty_date_parser(date_str))

    def test_none_date(self):
        self.assertIsNone(empty_date_parser(None))

    def test_edge_case_date(self):
        date_str = "1980-01-01T00:00:00"
        self.assertIsNone(empty_date_parser(date_str))

    def test_above_edge_case_date(self):
        date_str = "1981-01-01T00:00:00"
        expected_date = timezone.make_aware(parse(date_str), timezone.utc)
        self.assertEqual(empty_date_parser(date_str), expected_date)


class TestResponseKeyMixin(TestCase):

    def setUp(self):
        class TestClass(ResponseKeyMixin):
            response_key = 'data'

        self.test_instance = TestClass()

    def test_unpack_records(self):
        response = {'data': [{'id': 1, 'name': 'Test'}]}
        expected_records = [{'id': 1, 'name': 'Test'}]
        self.assertEqual(
            self.test_instance._unpack_records(response), expected_records)
