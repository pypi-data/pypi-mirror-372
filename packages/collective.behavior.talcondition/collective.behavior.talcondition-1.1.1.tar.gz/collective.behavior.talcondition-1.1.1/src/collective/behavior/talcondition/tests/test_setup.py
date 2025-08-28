# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""
from collective.behavior.talcondition import PLONE_VERSION
from collective.behavior.talcondition.testing import IntegrationTestCase
from plone import api


if PLONE_VERSION >= 5:
    from Products.CMFPlone.utils import get_installer


class TestInstall(IntegrationTestCase):
    """Test installation of collective.behavior.talcondition into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if PLONE_VERSION < 5:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        else:
            self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if collective.behavior.talcondition is installed with portal_quickinstaller."""
        if PLONE_VERSION < 5:
            self.assertTrue(
                self.installer.isProductInstalled("collective.behavior.talcondition")
            )
        else:
            self.assertTrue(
                self.installer.is_product_installed("collective.behavior.talcondition")
            )

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that ICollectiveBehaviorTalconditionLayer is registered."""
        from collective.behavior.talcondition.interfaces import ICollectiveBehaviorTalconditionLayer
        from plone.browserlayer import utils

        self.assertIn(ICollectiveBehaviorTalconditionLayer, utils.registered_layers())


class TestUninstall(IntegrationTestCase):
    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if PLONE_VERSION < 5:
            self.installer = api.portal.get_tool("portal_quickinstaller")
            self.installer.uninstallProducts(["collective.behavior.talcondition"])
        else:
            self.installer = get_installer(self.portal, self.layer["request"])
            self.installer.uninstall_product("collective.behavior.talcondition")

    def test_uninstall(self):
        """Test if collective.behavior.talcondition is cleanly uninstalled."""
        if PLONE_VERSION < 5:
            self.assertFalse(
                self.installer.isProductInstalled("collective.behavior.talcondition")
            )
        else:
            self.assertFalse(
                self.installer.is_product_installed("collective.behavior.talcondition")
            )
