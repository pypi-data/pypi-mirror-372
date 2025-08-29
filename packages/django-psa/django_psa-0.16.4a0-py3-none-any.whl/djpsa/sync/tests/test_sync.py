from unittest import TestCase
from unittest.mock import MagicMock, patch
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError

from djpsa.sync.sync import Synchronizer, SyncResults, CREATED, UPDATED, \
    SKIPPED


class TestSynchronizer(TestCase):

    def setUp(self):
        # Mock settings
        settings.PROVIDER = MagicMock()
        settings.PROVIDER.get_request_settings.return_value = \
            {'batch_size': 100}

        # Mock model class
        self.model_class_mock = MagicMock()
        self.model_class_mock.objects.all.return_value = [1, 2, 3]

        # Mock client class
        self.client_class_mock = MagicMock()
        self.client_class_mock.return_value.get_page.\
            return_value = {'data': [{'id': 1}, {'id': 2}]}

        class MockSynchronizer(Synchronizer):
            model_class = self.model_class_mock
            client_class = self.client_class_mock
            lookup_key = 'id'

            def get_model_name(self):
                return 'MockModel'

        # Create an instance of Synchronizer
        self.synchronizer = MockSynchronizer()

    @patch('djpsa.sync.sync.SyncJob')
    def test_get_last_sync_job_time(self, _):

        with patch.object(
                self.synchronizer,
                '_format_job_condition') as format_job_condition_mock:
            # Mock SyncJob queryset
            sync_job_qset_mock = MagicMock()
            sync_job_qset_mock.count.return_value = 2
            last_sync_job = MagicMock()
            last_sync_job.start_time = timezone.now()
            sync_job_qset_mock.last.return_value = last_sync_job
            self.synchronizer.last_updated_field = 'updated_at'
            self.synchronizer.full = False
            self.synchronizer.partial_sync_support = True

            # Call the method
            self.synchronizer._get_last_sync_job_time(sync_job_qset_mock)

        # Assertions
        self.assertEqual(format_job_condition_mock.call_count, 1)

    @patch('djpsa.sync.sync.SyncJob')
    def test_get_last_sync_job_time_no_last_updated_field(self, _):
        # Mock SyncJob queryset
        sync_job_qset_mock = MagicMock()
        sync_job_qset_mock.count.return_value = 2
        self.synchronizer.last_updated_field = None
        self.synchronizer.full = False
        self.synchronizer.partial_sync_support = True

        # Call the method
        last_sync_time = \
            self.synchronizer._get_last_sync_job_time(sync_job_qset_mock)

        # Assertions
        self.assertIsNone(last_sync_time)

    @patch('djpsa.sync.sync.SyncJob')
    def test_get_last_sync_job_time_full_sync(self, _):
        # Mock SyncJob queryset
        sync_job_qset_mock = MagicMock()
        sync_job_qset_mock.count.return_value = 2
        self.synchronizer.last_updated_field = 'updated_at'
        self.synchronizer.full = True
        self.synchronizer.partial_sync_support = True

        # Call the method
        last_sync_time = \
            self.synchronizer._get_last_sync_job_time(sync_job_qset_mock)

        # Assertions
        self.assertIsNone(last_sync_time)

    @patch('djpsa.sync.sync.SyncJob')
    def test_get_last_sync_job_time_partial_sync_not_supported(self, _):
        # Mock SyncJob queryset
        sync_job_qset_mock = MagicMock()
        sync_job_qset_mock.count.return_value = 2
        self.synchronizer.last_updated_field = 'updated_at'
        self.synchronizer.full = False
        self.synchronizer.partial_sync_support = False

        # Call the method
        last_sync_time = \
            self.synchronizer._get_last_sync_job_time(sync_job_qset_mock)

        # Assertions
        self.assertIsNone(last_sync_time)

    @patch.object(Synchronizer, 'persist_page')
    @patch.object(Synchronizer, '_unpack_records')
    def test_fetch_records(self, mock_unpack_records, mock_persist_page):
        with patch.object(
                self.synchronizer.client_class, 'get_page') as mock_get_page:
            results = SyncResults()

            # First page response
            # Second page response
            # Empty response to stop the loop
            mock_get_page.side_effect = [
                {'data': 'page1'},
                {'data': 'page2'},
                {}
            ]

            # Unpacked records from first page
            # Unpacked records from second page
            # No records in the last page
            mock_unpack_records.side_effect = [
                [{'id': 1, 'summary': 'record1'},
                 {'id': 2, 'summary': 'record2'}],
                [{'id': 3, 'summary': 'record3'}, ],
                []
            ]

            self.synchronizer.batch_size = 2

            # Execute
            results = self.synchronizer.fetch_records(results)

            self.synchronizer.batch_size = 100

            # Verify
            self.assertEqual(mock_unpack_records.call_count, 2)
            self.assertEqual(mock_persist_page.call_count, 2)
            self.assertEqual(results.created_count, 0)
            self.assertEqual(results.updated_count, 0)
            self.assertEqual(results.skipped_count, 0)
            self.assertEqual(results.deleted_count, 0)

    def test_persist_page_created(self):
        records = [{'id': 1}, {'id': 2}]
        results = SyncResults()
        self.synchronizer.update_or_create_instance = MagicMock(side_effect=[
            (MagicMock(), CREATED),
            (MagicMock(), CREATED)
        ])

        self.synchronizer.persist_page(records, results)

        self.assertEqual(results.created_count, 2)
        self.assertEqual(results.updated_count, 0)
        self.assertEqual(results.skipped_count, 0)
        self.assertEqual(results.synced_ids, {1, 2})

    def test_persist_page_updated(self):
        records = [{'id': 1}, {'id': 2}]
        results = SyncResults()
        self.synchronizer.update_or_create_instance = MagicMock(side_effect=[
            (MagicMock(), UPDATED),
            (MagicMock(), UPDATED)
        ])

        self.synchronizer.persist_page(records, results)

        self.assertEqual(results.created_count, 0)
        self.assertEqual(results.updated_count, 2)
        self.assertEqual(results.skipped_count, 0)
        self.assertEqual(results.synced_ids, {1, 2})

    def test_persist_page_skipped(self):
        records = [{'id': 1}, {'id': 2}]
        results = SyncResults()
        self.synchronizer.update_or_create_instance = MagicMock(side_effect=[
            (MagicMock(), SKIPPED),
            (MagicMock(), SKIPPED)
        ])

        self.synchronizer.persist_page(records, results)

        self.assertEqual(results.created_count, 0)
        self.assertEqual(results.updated_count, 0)
        self.assertEqual(results.skipped_count, 2)
        self.assertEqual(results.synced_ids, {1, 2})

    @patch('djpsa.sync.sync.logger')
    def test_persist_page_exception(self, mock_logger):
        records = [{'id': 1}, {'id': 2}]
        results = SyncResults()
        self.synchronizer.update_or_create_instance = \
            MagicMock(side_effect=IntegrityError('Test error'))

        self.synchronizer.persist_page(records, results)

        self.assertEqual(results.created_count, 0)
        self.assertEqual(results.updated_count, 0)
        self.assertEqual(results.skipped_count, 0)
        self.assertEqual(results.synced_ids, {1, 2})
        self.assertTrue(mock_logger.warning.called)

    def test_prune_stale_records(self):
        mock_get_delete_qset = self.synchronizer.get_delete_qset = MagicMock()
        initial_ids = {1, 2, 3, 4}
        synced_ids = {2, 3}

        mock_delete_qset = MagicMock()
        mock_delete_qset.count.return_value = 2
        mock_get_delete_qset.return_value = mock_delete_qset

        deleted_count = \
            self.synchronizer.prune_stale_records(initial_ids, synced_ids)

        self.assertEqual(deleted_count, 2)
        mock_get_delete_qset.assert_called_once_with({1, 4})
        mock_delete_qset.delete.assert_called_once()
