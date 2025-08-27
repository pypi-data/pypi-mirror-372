"""Setup tests for this package."""

from dsetool.policy import testing
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer
from zope.component import getMultiAdapter
from zope.publisher.interfaces import IPublishTraverse

import unittest


class TestSetup(unittest.TestCase):
    """Test that dsetool.policy is properly installed."""

    layer = testing.DSETOOL_POLICY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if dsetool.policy is installed."""
        self.assertTrue(self.installer.is_product_installed("dsetool.policy"))

    def test_browserlayer(self):
        """Test that IDSEToolPolicyLayer is registered."""
        from dsetool.policy import interfaces
        from plone.browserlayer import utils

        self.assertIn(interfaces.IDSEToolPolicyLayer, utils.registered_layers())

    def test_jbot(self):
        """Test that z3c.jbot is installed."""
        request = self.layer["request"]

        traverser = getMultiAdapter((self.portal.client, request), IPublishTraverse)
        login_view = traverser.publishTraverse(request, "login")
        self.assertEqual(
            login_view.index.filename.endswith(
                "dsetool/policy/browser/overrides/euphorie.client.browser.templates.login.pt"  # noqa: E501
            ),
            True,
        )


class TestUninstall(unittest.TestCase):
    layer = testing.DSETOOL_POLICY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("dsetool.policy")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if dsetool.policy is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("dsetool.policy"))

    def test_browserlayer_removed(self):
        """Test that ICollectiveHardeningLayer is removed."""
        from dsetool.policy import interfaces
        from plone.browserlayer import utils

        self.assertNotIn(interfaces.IDSEToolPolicyLayer, utils.registered_layers())
