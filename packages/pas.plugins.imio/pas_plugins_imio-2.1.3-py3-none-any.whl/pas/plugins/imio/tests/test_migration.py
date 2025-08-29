# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from authomatic.core import User
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING
from pas.plugins.imio.tests.utils import MockupUser
from pas.plugins.imio.upgrades import convert_userid_with_plugin
from pas.plugins.imio.upgrades import convert_userids_with_plugin
from pas.plugins.imio.upgrades import do_migrate_roles_with_plugin
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import os
import transaction
import unittest


class TestMigration(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.acl_users = api.portal.get_tool("acl_users")
        self.plugin = self.acl_users["authentic"]
        self.acl_users._doAddUser("jamesbond", "secret", ["Site Administrator"], [])
        self.acl_users._doAddUser("shakespeare", "secret", ["Contributor"], [])
        transaction.commit()
        os.environ["service_ou"] = "testou"
        os.environ["service_slug"] = "testslug"
        os.environ["authentic_usagers_hostname"] = "usagers.test.be"

    # self.browser.addHeader("Authorization", "Basic jamesbond:secret")

    def test_add_existing_user(self):
        # os.environ["authentic_usagers_hostname"] = "agents.test.be"
        self.assertEqual(self.plugin.enumerateUsers(), ())
        self.assertIn("jamesbond", self.acl_users.source_users.getUserIds())
        # source_users = self.acl_users.source_users
        member = api.portal.get_tool("portal_membership").getMemberById("jamesbond")
        self.assertEqual(member.getProperty("email", ""), "")
        self.assertIn("Site Administrator", member.getRoles())
        data = {}
        data["id"] = "12345-67890"
        data["username"] = "jamesbond"
        data["email"] = "james@bond.co.uk"
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        self.assertNotIn("jamesbond", self.acl_users.source_users.getUserIds())
        new_user = self.plugin._useridentities_by_userid.get("12345-67890")
        self.assertEqual(new_user.login, "jamesbond")
        new_user = self.plugin._useridentities_by_login.get("jamesbond")
        self.assertEqual(new_user.userid, "12345-67890")
        member = api.portal.get_tool("portal_membership").getMemberById("12345-67890")
        self.assertEqual(member.getProperty("email", ""), "james@bond.co.uk")
        self.assertIn("Site Administrator", member.getRoles())

    def test_convert_userid(self):
        data = {}
        data["id"] = "54321-98765"
        data["username"] = "mylogin"
        data["email"] = "my@login.com"
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)
        self.assertEqual(
            convert_userid_with_plugin(self.plugin, "nonexisting"), "nonexisting"
        )
        self.assertEqual(
            convert_userid_with_plugin(self.plugin, "mylogin"), "54321-98765"
        )
        self.assertListEqual(
            convert_userids_with_plugin(self.plugin, ["mylogin"]), ["54321-98765"]
        )
        self.assertListEqual(
            convert_userids_with_plugin(self.plugin, ["mylogin", "nonexisting"]),
            ["54321-98765", "nonexisting"],
        )

    def test_keep_ownership(self):
        login(self.portal, "shakespeare")
        content = api.content.create(
            type="Document",
            id="document",
            container=self.portal,
        )
        content.setContributors(("shakespeare", "jamesbond"))
        data = {}
        data["id"] = "54321-98765"
        data["username"] = "shakespeare"
        data["email"] = "shake@speare.co.uk"
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)

        self.assertTupleEqual(content.listCreators(), ("shakespeare",))
        self.assertTupleEqual(content.listContributors(), ("shakespeare", "jamesbond"))
        do_migrate_roles_with_plugin(self.plugin, content, "")
        self.assertTupleEqual(content.listCreators(), ("54321-98765",))
        self.assertTupleEqual(content.listContributors(), ("54321-98765", "jamesbond"))

    def test_keep_local_roles(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        content = api.content.create(
            type="Folder",
            id="folder",
            container=self.portal,
        )
        api.user.grant_roles(
            username="shakespeare", obj=content, roles=["Editor", "Reviewer"]
        )
        data = {}
        data["id"] = "54321-98765"
        data["username"] = "shakespeare"
        data["email"] = "shake@speare.co.uk"
        authomatic_user = User("authentic", **data)
        user = MockupUser(self.plugin, authomatic_user)
        self.plugin.remember_identity(user)

        local_roles = content.__ac_local_roles__
        self.assertListEqual(sorted(local_roles.keys()), ["shakespeare", TEST_USER_ID])
        self.assertListEqual(sorted(local_roles["shakespeare"]), ["Editor", "Reviewer"])

        do_migrate_roles_with_plugin(self.plugin, content, "")

        self.assertListEqual(sorted(local_roles.keys()), ["54321-98765", TEST_USER_ID])
        self.assertListEqual(sorted(local_roles["54321-98765"]), ["Editor", "Reviewer"])
