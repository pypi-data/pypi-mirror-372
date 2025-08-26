# -*- coding: utf-8 -*-
from collective.timestamp.tests import TimestampIntegrationTestCase
from collective.timestamp.utils import get_timestamp_date_from_tsr_file
from collective.timestamp.utils import localize_utc_date
from collective.timestamp.utils import timestamp
from datetime import datetime
from datetime import timedelta
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from unittest.mock import patch

import pytz


class TestUtils(TimestampIntegrationTestCase):

    def setUp(self):
        """Set up the test case."""
        super().setUp()
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        self.file_data = self.file.file.data

    def test_localize_utc_date(self):
        naive_datetime = datetime(2024, 9, 10, 12, 0, 0)
        localized_datetime = localize_utc_date(naive_datetime)
        expected_datetime = datetime(2024, 9, 10, 12, 0, 0, tzinfo=pytz.UTC)
        self.assertEqual(localized_datetime, expected_datetime)

    def test_timestamp(self):
        with patch("rfc3161ng.api.RemoteTimestamper.__call__") as mock_timestamper:
            mock_timestamper.return_value = self.tsr
            tsr, timestamp_date = timestamp(self.file_data, "http://freetsa.org/tsr")
        self.assertIsInstance(tsr, bytes)
        self.assertIsInstance(timestamp_date, datetime)
        self.assertEqual(
            timestamp_date, datetime(2025, 8, 25, 14, 49, 8, tzinfo=pytz.UTC)
        )

    def test_timestamp_retries(self):
        tsr, timestamp_date = timestamp(
            self.file_data,
            "https://httpbin.org/status/429",
            use_failover=True,
            failover_timestamping_service_urls=[
                "https://httpbin.org/status/429",
                "http://freetsa.org/tsr",
            ],
            max_retries=2,
            initial_backoff_seconds=0.1,
        )
        self.assertIsInstance(tsr, bytes)
        self.assertIsInstance(timestamp_date, datetime)
        self.assertAlmostEqual(
            timestamp_date, datetime.now(pytz.UTC), delta=timedelta(seconds=10)
        )

    def test_timestamp_raises_connection_error(self):
        with self.assertRaises(ConnectionError):
            timestamp(
                self.file_data,
                "https://httpbin.org/status/500",
                use_failover=True,
                failover_timestamping_service_urls=["https://httpbin.org/status/429"],
                max_retries=2,
                initial_backoff_seconds=0.01,
            )

    def test_get_timestamp_date_from_tsr_file(self):
        timestamp_date = get_timestamp_date_from_tsr_file(self.raw_tsr)
        self.assertEqual(
            timestamp_date, datetime(2025, 8, 25, 14, 49, 8, tzinfo=pytz.UTC)
        )
