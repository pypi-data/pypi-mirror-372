# -*- coding: utf-8 -*-

from collective.timestamp.interfaces import ITimeStamper
from collective.timestamp.testing import COLLECTIVE_TIMESTAMP_INTEGRATION_TESTING
from collective.timestamp.tests import TimestampIntegrationTestCase
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.namedfile.file import NamedBlobFile
from Products.statusmessages.interfaces import IStatusMessage
from rfc3161ng import TimestampingError
from unittest.mock import patch
from zope.lifecycleevent import modified

import unittest


class TestRule(TimestampIntegrationTestCase):

    def test_rule_action(self):
        handler = ITimeStamper(self.file)
        self.assertFalse(handler.is_timestamped())
        self.file.file = NamedBlobFile(data=b"file data", filename="file.pdf")
        modified(self.file)
        self.assertTrue(handler.is_timestamped())
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 1)
        self.assertEqual(
            "Timestamp file has been successfully generated and saved for my-file",
            show[0].message,
        )

    def test_rule_action_error(self):
        with patch(
            "collective.timestamp.adapters.TimeStamper.timestamp",
            side_effect=TimestampingError,
        ):
            self.file.file = NamedBlobFile(data=b"file data", filename="file.pdf")
            modified(self.file)
            messages = IStatusMessage(self.request)
            show = messages.show()
            self.assertEqual(len(show), 1)
            self.assertIn("Unable to timestamp", show[0].message)
