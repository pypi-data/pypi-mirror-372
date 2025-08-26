# -*- coding: utf-8 -*-

from collective.timestamp.interfaces import ITimeStamper
from collective.timestamp.testing import COLLECTIVE_TIMESTAMP_INTEGRATION_TESTING
from collective.timestamp.tests import TimestampIntegrationTestCase
from datetime import datetime
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from plone.uuid.interfaces import IUUID

import unittest


class TestAdapter(TimestampIntegrationTestCase):

    def test_adapter(self):
        with self.assertRaises(TypeError):
            ITimeStamper(self.document)
        self.assertIsNotNone(ITimeStamper(self.file))

    def test_get_file_field(self):
        handler = ITimeStamper(self.file)
        self.assertIsNone(handler.get_file_field())
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        field = handler.get_file_field()
        self.assertIsNotNone(field)
        self.assertEqual(field.fieldname, "file")

    def test_get_data(self):
        handler = ITimeStamper(self.file)
        self.assertIsNone(handler.get_data())
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        self.assertEqual(handler.get_data(), b"file data")

    def test_is_timestamped(self):
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        handler = ITimeStamper(self.file)
        self.assertFalse(handler.is_timestamped())
        handler.timestamp()
        self.assertTrue(handler.is_timestamped())

    def test_is_timestampable(self):
        handler = ITimeStamper(self.file)
        self.assertFalse(handler.is_timestampable())
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        self.assertTrue(handler.is_timestampable())
        self.file.enable_timestamping = False
        self.assertFalse(handler.is_timestampable())
        self.file.enable_timestamping = True
        self.assertTrue(handler.is_timestampable())
        handler.timestamp()
        self.assertFalse(handler.is_timestampable())

    def test_timestamp(self):
        uuid = IUUID(self.file)
        handler = ITimeStamper(self.file)
        first_effective_date = self.file.effective()
        with self.assertRaises(ValueError):
            handler.timestamp()
        self.assertIsNone(self.file.timestamp)
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        catalog = api.portal.get_tool("portal_catalog")
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        first_effective_index = indexes.get("effective")
        first_effective_range_index = indexes.get("effectiveRange")
        self.assertFalse(indexes.get("is_timestamped"))
        data, timestamp_date = handler.timestamp()
        self.assertIsInstance(data, bytes)
        self.assertIsInstance(timestamp_date, datetime)
        self.assertEqual(data, self.file.file.data)
        self.assertEqual(timestamp_date, self.file.effective().asdatetime())
        self.assertIsNotNone(self.file.timestamp)
        self.assertNotEqual(first_effective_date, self.file.effective())
        brain = api.content.find(UID=uuid)[0]
        indexes = catalog.getIndexDataForRID(brain.getRID())
        self.assertNotEqual(first_effective_index, indexes.get("effective"))
        self.assertNotEqual(first_effective_range_index, indexes.get("effectiveRange"))
        self.assertTrue(indexes.get("is_timestamped"))
