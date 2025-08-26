# -*- coding: utf-8 -*-
from collective.timestamp.browser.viewlet import TimestampViewlet
from collective.timestamp.interfaces import ITimeStamper
from collective.timestamp.tests import TimestampIntegrationTestCase
from datetime import datetime
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from zope.component import getMultiAdapter
from zope.interface.interfaces import ComponentLookupError

import pytz


class TestInfos(TimestampIntegrationTestCase):

    def _timestamped_view(self):
        return getMultiAdapter(
            (self.timestamped_file, self.request), name="timestamp-info"
        )

    def _not_timestamped_view(self):
        return getMultiAdapter((self.file, self.request), name="timestamp-info")

    def test_viewlet(self):
        logout()
        viewlet = TimestampViewlet(self.document, self.request, None)
        with self.assertRaises(TypeError):
            viewlet.available()
        viewlet = TimestampViewlet(self.file, self.request, None)
        self.assertFalse(viewlet.available())
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        self.assertFalse(viewlet.available())
        handler = ITimeStamper(self.file)
        handler.timestamp()
        self.assertTrue(viewlet.available())
        viewlet.update()
        html = viewlet.render()
        self.assertIn("svg", html)

    def test_view(self):
        logout()
        not_timestamped_view = self._not_timestamped_view()
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter((self.document, self.request), name="timestamp")
        self.assertIn("This content is not timestamped.", not_timestamped_view())
        self.assertFalse(not_timestamped_view.is_timestamped())
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        self.assertIn("This content is not timestamped.", not_timestamped_view())
        self.assertFalse(not_timestamped_view.is_timestamped())

        timestamped_view = self._timestamped_view()

        self.assertIn("Timestamped on", timestamped_view())
        self.assertEqual(
            timestamped_view.more_infos_url(), "http://documentation.timestamptest.com"
        )
        self.assertTrue(timestamped_view.is_timestamped())
        self.assertEqual(
            timestamped_view.timestamp_date(),
            datetime(2025, 8, 25, 14, 49, 8, tzinfo=pytz.UTC),
        )

    def test_timestamp_authority(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertDictEqual(not_timestamped_view.timestamp_authority(), {})

        timestamped_view = self._timestamped_view()
        timestamp_authority = timestamped_view.timestamp_authority()
        self.assertSetEqual(
            set(timestamp_authority.keys()),
            {
                "country_name",
                "locality_name",
                "organization_name",
                "organization_identifier",
                "common_name",
            },
        )

    def test_timestamp_precision(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertIsNone(not_timestamped_view.timestamp_precision())

        timestamped_view = self._timestamped_view()
        self.assertEqual(timestamped_view.timestamp_precision(), "1 second(s)")

    def test_timestamp_protocol(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertIsNone(not_timestamped_view.timestamp_protocol())

        timestamped_view = self._timestamped_view()
        self.assertEqual(timestamped_view.timestamp_protocol(), "RFC 3161")

    def test_timestamp_algorithm(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertIsNone(not_timestamped_view.timestamp_algorithm())

        timestamped_view = self._timestamped_view()
        self.assertEqual(timestamped_view.timestamp_algorithm(), "sha256")

    def test_timestamp_hash(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertIsNone(not_timestamped_view.timestamp_hash())

        timestamped_view = self._timestamped_view()
        self.assertIsNotNone(timestamped_view.timestamp_hash())
        self.assertEqual(
            timestamped_view.timestamp_hash(),
            "86f3c70fb6673cf303d2206db5f23c237b665d5df9d3e44efef5114845fc9f59",
        )

    def test_policy_oid_present(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertIsNone(not_timestamped_view.timestamp_policy_oid())

        timestamped_view = self._timestamped_view()
        oid = timestamped_view.timestamp_policy_oid()
        self.assertEqual("2.16.56.13.6.3.1.1000", oid)

    def test_serial_is_int_and_positive(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertIsNone(not_timestamped_view.timestamp_serial_number())

        timestamped_view = self._timestamped_view()
        serial = timestamped_view.timestamp_serial_number()
        self.assertEqual(serial, 7378481000937193731)

    def test_timestamp_file_and_tsr_links(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertIsNone(not_timestamped_view.timestamp_tsr_link())

        timestamped_view = self._timestamped_view()
        file_link = timestamped_view.timestamp_file_link()
        tsr_link = timestamped_view.timestamp_tsr_link()
        # File link
        self.assertIsNotNone(file_link)
        self.assertEqual(file_link["label"], "file.txt")
        self.assertIn("/@@download/file/file.txt", file_link["url"])
        # TSR link
        self.assertIsNotNone(tsr_link)
        self.assertTrue(tsr_link["label"].lower().endswith(".tsr"))
        self.assertIn("/@@download/timestamp/", tsr_link["url"])

    def test_certificate_chain_nonempty_and_order(self):
        not_timestamped_view = self._not_timestamped_view()
        self.assertListEqual(not_timestamped_view.certificate_chain(), [])

        timestamped_view = self._timestamped_view()
        chain = timestamped_view.certificate_chain()
        # At least the signer should be present
        self.assertGreaterEqual(len(chain), 1)

        # The first element is the signer; check that matches signer_certificate()
        signer = timestamped_view.signer_certificate()
        self.assertIsNotNone(signer)
        self.assertIs(chain[0], signer)

    def test_certificate_chain_info_shapes_and_dates(self):
        timestamped_view = self._timestamped_view()

        info = timestamped_view.certificate_chain_info()
        self.assertIsInstance(info, list)
        self.assertGreaterEqual(len(info), 1)

        first = info[0]
        for key in (
            "subject",
            "issuer",
            "serial_number",
            "fingerprint",
            "self_issued",
            "has_ski",
            "has_aki",
            "not_before",
            "not_after",
        ):
            self.assertIn(key, first)

        self.assertIsInstance(first["serial_number"], int)
        self.assertIsInstance(first["fingerprint"], str)
        self.assertRegex(
            first["fingerprint"], r"^[0-9a-f]{64}$"
        )  # sha256 hex by default
        self.assertIsInstance(first["self_issued"], bool)
        self.assertIsInstance(first["has_ski"], bool)
        self.assertIsInstance(first["has_aki"], bool)
        self.assertIsInstance(first["not_before"], datetime)
        self.assertIsInstance(first["not_after"], datetime)
        self.assertLess(first["not_before"], first["not_after"])

    def test_timestamp_signer_subject_mapping(self):
        timestamped_view = self._timestamped_view()
        subj = timestamped_view.timestamp_signer_subject()
        self.assertIsInstance(subj, dict)
        for k, v in subj.items():
            self.assertIn("label", v)
            self.assertIn("value", v)
            break  # one is enough to prove shape

    def test_certificates_in_token_basic(self):
        timestamped_view = self._timestamped_view()
        certs = timestamped_view.certificates_in_token()
        # There should be at least the signer certificate
        self.assertIsInstance(certs, list)
        self.assertGreaterEqual(len(certs), 1)
