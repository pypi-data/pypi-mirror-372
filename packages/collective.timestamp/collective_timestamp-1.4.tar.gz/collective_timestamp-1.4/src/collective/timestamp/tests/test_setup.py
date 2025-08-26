# -*- coding: utf-8 -*-

from collective.timestamp.testing import COLLECTIVE_TIMESTAMP_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.timestamp is properly installed."""

    layer = COLLECTIVE_TIMESTAMP_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if collective.timestamp is installed."""
        self.assertTrue(self.installer.is_product_installed("collective.timestamp"))

    def test_browserlayer(self):
        """Test that ICollectiveTimestampLayer is registered."""
        from collective.timestamp.interfaces import ICollectiveTimestampLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveTimestampLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_TIMESTAMP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("collective.timestamp")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if collective.timestamp is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("collective.timestamp"))

    def test_browserlayer_removed(self):
        """Test that ICollectiveTimestampLayer is removed."""
        from collective.timestamp.interfaces import ICollectiveTimestampLayer
        from plone.browserlayer import utils

        self.assertNotIn(ICollectiveTimestampLayer, utils.registered_layers())
