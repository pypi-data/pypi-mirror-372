# -*- coding: utf-8 -*-
from authomatic.core import User
from BTrees.OOBTree import OOBTree
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING
from pas.plugins.imio.tests.utils import MockupUser
from plone import api

import os
import unittest


class _MockPlugin(object):

    _useridentities_by_userid = OOBTree()


class TestProvierUserIDFactories(unittest.TestCase):

    layer = PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.acl_users = api.portal.get_tool("acl_users")
        self.plugin = self.acl_users["authentic"]
        os.environ["service_ou"] = "testou"
        os.environ["service_slug"] = "testslug"
        os.environ["authentic_usagers_hostname"] = "usagers.test.be"

    def test_normalizer(self):
        from pas.plugins.imio.useridfactories import ProviderIDFactory

        pidf = ProviderIDFactory()

        self.plugin = self.acl_users["authentic"]
        data = {}
        data["id"] = "imio"
        data["username"] = "jamesbond"
        data["email"] = "james@bond.co.uk"
        authomatic_user = User("authentic", **data)

        mock_agent_result = MockupUser(self.plugin, authomatic_user)

        self.assertEqual("jamesbond", pidf(self.plugin, mock_agent_result))
        self.plugin._useridentities_by_userid["fo"] = 1
        mock_usager_result = MockupUser(
            self.plugin, authomatic_user, "authentic-usagers"
        )
        self.assertEqual("james@bond.co.uk", pidf(self.plugin, mock_usager_result))
