"""Setup tests for this package."""

from cs.translator.elhuyar.testing import CS_TRANSLATOR_ELHUYAR_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that cs.translator.elhuyar is properly installed."""

    layer = CS_TRANSLATOR_ELHUYAR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")

    def test_product_installed(self):
        """Test if cs.translator.elhuyar is installed."""
        self.assertTrue(self.installer.is_product_installed("cs.translator.elhuyar"))

    def test_browserlayer(self):
        """Test that ICsTranslatorElhuyarLayer is registered."""
        from cs.translator.elhuyar.interfaces import ICsTranslatorElhuyarLayer
        from plone.browserlayer import utils

        self.assertIn(ICsTranslatorElhuyarLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    layer = CS_TRANSLATOR_ELHUYAR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        if get_installer:
            self.installer = get_installer(self.portal, self.layer["request"])
        else:
            self.installer = api.portal.get_tool("portal_quickinstaller")
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("cs.translator.elhuyar")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if cs.translator.elhuyar is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("cs.translator.elhuyar"))

    def test_browserlayer_removed(self):
        """Test that ICsTranslatorElhuyarLayer is removed."""
        from cs.translator.elhuyar.interfaces import ICsTranslatorElhuyarLayer
        from plone.browserlayer import utils

        self.assertNotIn(ICsTranslatorElhuyarLayer, utils.registered_layers())
