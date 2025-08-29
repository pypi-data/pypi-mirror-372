# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from authomatic.core import User
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_INTEGRATION_TESTING
from pas.plugins.imio.tests.utils import MockupUser
from plone import api

import random
import string
import unittest


class TestPlugin(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        acl_users = api.portal.get_tool("acl_users")
        self.plugin = acl_users["authentic"]

    def test_add_user(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {}
        data["id"] = "imio"
        data["username"] = "imiousername"
        data["email"] = "imio@username.be"
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        new_user = self.plugin._useridentities_by_userid.get("imio")
        self.assertEqual(new_user.userid, "imio")
        self.assertEqual(new_user.login, "imiousername")

    def test_enumerate_users(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {"id": "imio", "username": "imio username", "email": "imio@username.be"}
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        self.assertEqual(
            self.plugin.enumerateUsers(login="")[0]["login"], "imio username"
        )
        self.assertEqual(self.plugin.enumerateUsers(login="james"), [])
        data = {"id": "123456", "username": "jamesbond", "email": "james@bond.co.uk"}
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        self.assertEqual(
            self.plugin.enumerateUsers(id="123456"),
            [{"login": "jamesbond", "pluginid": "authentic", "id": "123456"}],
        )
        self.assertEqual(
            self.plugin.enumerateUsers(login="james"),
            [{"login": "jamesbond", "pluginid": "authentic", "id": "123456"}],
        )
        self.assertEqual(
            self.plugin.enumerateUsers(login="bond"),
            [{"login": "jamesbond", "pluginid": "authentic", "id": "123456"}],
        )
        self.assertEqual(self.plugin.enumerateUsers(login="bond", exact_match=True), [])
        self.assertEqual(
            self.plugin.enumerateUsers(login="jamesbond", exact_match=True),
            [{"login": "jamesbond", "pluginid": "authentic", "id": "123456"}],
        )

    def test_search_all_users(self):
        count_users = 1
        users = api.user.get_users()
        if "admin" in [user.id for user in users]:
            count_users += 1
        self.assertEqual(len(users), count_users)
        data = {
            "id": "12345-67890",
            "username": "imio username",
            "email": "imio@username.be",
        }
        authomatic_user = User("authentic", **data)
        mockup_user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(mockup_user)
        users = api.user.get_users()
        count_users += 1
        self.assertEqual(len(users), count_users)
        self.assertIn("12345-67890", [user.id for user in users])

    def test_search_user(self):
        data = {
            "id": "12345-67890",
            "username": "imio username",
            "email": "imio@username.be",
        }
        authomatic_user = User("authentic", **data)
        mockup_user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(mockup_user)
        user = api.user.get(userid="12345-67890")
        self.assertEqual(user.id, "12345-67890")
        user = api.user.get(userid="imio username")
        self.assertEqual(user.id, "12345-67890")
        user = api.user.get(username="imio username")
        self.assertEqual(user.id, "12345-67890")

    def test_keeping_groups(self):
        # create on user with a group
        user_id = "123456789"
        username = "mynewuser"
        email = "imio@username.be"
        registration = api.portal.get_tool("portal_registration")
        chars = string.ascii_letters + string.digits
        password = "".join(random.choice(chars) for char in range(8))
        properties = {"email": email, "username": username}
        registration.addMember(username, password, ("Member",), properties=properties)
        group = api.group.create("test_group")
        api.group.add_user(group=group, username=username)
        groups = api.group.get_groups(username=username)
        self.assertIn("test_group", [group.id for group in groups])
        acl_users = api.portal.get_tool("acl_users")
        source_users = acl_users.source_users
        self.assertIn(username, [user for user in source_users.listUserIds()])
        data = {
            "id": user_id,
            "username": username,
            "email": email,
        }

        # migrate user
        authomatic_user = User("authentic", **data)
        mockup_user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(mockup_user)

        source_users = acl_users.source_users
        self.assertNotIn(username, [user for user in source_users.listUserIds()])
        self.assertNotIn(user_id, [user for user in source_users.listUserIds()])
        groups = api.group.get_groups(username=user_id)
        self.assertIn("test_group", [group.id for group in groups])
