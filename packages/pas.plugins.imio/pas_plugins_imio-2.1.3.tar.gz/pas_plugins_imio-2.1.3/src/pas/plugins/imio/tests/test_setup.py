# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_INTEGRATION_TESTING  # noqa

import unittest

HAS_PLONE_5_AND_MORE = api.env.plone_version().startswith(
    "5"
) or api.env.plone_version().startswith("6")

if HAS_PLONE_5_AND_MORE:
    from Products.CMFPlone.utils import get_installer


class TestSetup(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if not HAS_PLONE_5_AND_MORE:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        else:
            self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if pas.plugins.imio is installed."""
        if not HAS_PLONE_5_AND_MORE:
            self.assertTrue(self.installer.isProductInstalled("pas.plugins.imio"))
        else:
            self.assertTrue(self.installer.is_product_installed("pas.plugins.imio"))

    def test_browserlayer(self):
        """Test that IPasPluginsImioLayer is registered."""
        from pas.plugins.imio.interfaces import IPasPluginsImioLayer
        from plone.browserlayer import utils

        self.assertIn(IPasPluginsImioLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = PAS_PLUGINS_IMIO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if not HAS_PLONE_5_AND_MORE:
            self.installer = api.portal.get_tool("portal_quickinstaller")
            self.installer.uninstallProducts(["pas.plugins.imio"])
        else:
            self.installer = get_installer(self.portal, self.layer["request"])
            self.installer.uninstall_product("pas.plugins.imio")

    def test_product_uninstalled(self):
        """Test if pas.plugins.imio is cleanly uninstalled."""
        if not HAS_PLONE_5_AND_MORE:
            self.assertFalse(self.installer.isProductInstalled("pas.plugins.imio"))
        else:
            self.assertFalse(self.installer.is_product_installed("pas.plugins.imio"))

    def test_browserlayer_removed(self):
        """Test that IPasPluginsImioLayer is removed."""
        from pas.plugins.imio.interfaces import IPasPluginsImioLayer
        from plone.browserlayer import utils

        self.assertNotIn(IPasPluginsImioLayer, utils.registered_layers())
