# -*- coding: utf-8 -*-

from collective.timestamp.behaviors.timestamp import ITimestampableDocument
from collective.timestamp.tests import TimestampFunctionalTestCase
from plone import api
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.behavior.interfaces import IBehavior
from plone.namedfile.file import NamedBlobFile
from plone.testing.z2 import Browser
from Products.statusmessages.interfaces import IStatusMessage
from rfc3161ng import TimestampingError
from unittest.mock import patch
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import Interface
from zope.lifecycleevent import Attributes
from zope.lifecycleevent import modified

import transaction
import unittest


class TestBehavior(TimestampFunctionalTestCase):

    def test_behavior_interface(self):
        behavior = getUtility(IBehavior, "collective.timestamp")
        self.assertEqual(behavior.marker, ITimestampableDocument)
        self.assertTrue(ITimestampableDocument.providedBy(self.file))

    def test_action(self):
        view = getMultiAdapter((self.document, self.request), name="timestamp_utils")
        self.assertFalse(view.available())

        view = getMultiAdapter((self.file, self.request), name="timestamp_utils")
        self.assertFalse(view.available())
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        self.assertTrue(view.available())

        view.timestamp()
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 1)
        self.assertIn(
            "Timestamp file has been successfully generated and saved", show[0].message
        )

        self.file.timestamp = None
        with patch(
            "collective.timestamp.adapters.TimeStamper.timestamp",
            side_effect=TimestampingError,
        ):
            view.timestamp()
            messages = IStatusMessage(self.request)
            show = messages.show()
            self.assertEqual(len(show), 2)
            self.assertIn("Timestamp has failed", show[1].message)

    def test_edition_warning(self):
        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.addHeader(
            "Authorization",
            "Basic %s:%s"
            % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            ),
        )
        browser.open("{}/edit".format(self.file.absolute_url()))
        html = browser.contents
        self.assertNotIn(
            "You are editing a timestamped content.",
            html,
        )
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        view = getMultiAdapter((self.file, self.request), name="timestamp_utils")
        view.timestamp()
        transaction.commit()
        browser.open("{}/edit".format(self.file.absolute_url()))
        html = browser.contents
        self.assertIn(
            "You are editing a timestamped content. Your modifications can invalidate the timestamp.",
            html,
        )

    def test_subscribers(self):
        self.file.file = NamedBlobFile(data=b"file data", filename="file.txt")
        modified(self.file, Attributes(IBasic, "IBasic.title"))
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 0)
        view = getMultiAdapter((self.file, self.request), name="timestamp_utils")
        self.assertTrue(view.available())
        view.timestamp()
        self.assertFalse(view.available())
        modified(self.file, Attributes(Interface, "file"))
        self.assertTrue(view.available())
        self.assertIsNone(self.file.timestamp)
        messages = IStatusMessage(self.request)
        show = messages.show()
        self.assertEqual(len(show), 2)
        self.assertIn(
            "Timestamp information has been removed since the data has changed",
            show[1].message,
        )
