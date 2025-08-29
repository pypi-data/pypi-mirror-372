# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from pas.plugins.imio.browser.view import AddAuthenticUsers
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_INTEGRATION_TESTING  # noqa
from pas.plugins.imio.testing import PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING  # noqa
from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter

import os
import unittest


def mock_get_authentic_users():
    return [
        {
            u"last_name": u"Suttor",
            u"id": 2,
            u"first_name": u"Beno\xeet",
            u"email": u"benoit.suttor@imio.be",
            u"username": u"bsuttor",
            u"password": u"",
            u"ou": u"default",
            u"uuid": u"2",
        }
    ]


class TestView(unittest.TestCase):
    """Test that pas.plugins.imio is properly installed."""

    layer = PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.portal.REQUEST
        acl_users = api.portal.get_tool("acl_users")
        self.plugin = acl_users["authentic"]
        os.environ["service_ou"] = "testou"
        os.environ["service_slug"] = "testslug"
        os.environ["authentic_usagers_hostname"] = "usagers.test.be"

    def test_add_authentic_users(self):
        self.assertEqual(self.plugin.enumerateUsers(), ())
        data = {}
        data["id"] = "imio"
        data["preferred_username"] = "imiousername"
        data["given_name"] = "imio"
        data["family_name"] = "imio"
        data["email"] = "imio@username.be"
        view = AddAuthenticUsers(self.portal, self.portal.REQUEST)
        self.assertEqual(view.next_url, "http://nohost/plone")
        self.portal.REQUEST.form["next_url"] = "https://www.imio.be"
        view = AddAuthenticUsers(self.portal, self.portal.REQUEST)
        self.assertEqual(view.next_url, "https://www.imio.be")
        view.get_authentic_users = mock_get_authentic_users
        self.assertEqual(view.get_authentic_users()[0]["username"], u"bsuttor")
        self.assertEqual(self.plugin._useridentities_by_userid.get("2"), None)
        view()
        new_user = self.plugin._useridentities_by_userid.get("2")
        self.assertEqual(new_user.userid, "2")
        new_user = self.plugin._useridentities_by_login.get("bsuttor")
        self.assertEqual(new_user.userid, "2")

    def test_authentic_handler(self):
        view = api.content.get_view(
            name="authentic-handler", context=self.portal, request=self.request
        )
        self.assertIn(
            "authentic-agents", [prov["identifier"] for prov in view.providers()]
        )

    def test_add_authentic_users_get_arg(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.request.form["type"] = "agents"
        view = getMultiAdapter((self.portal, self.request), name="add-authentic-users")
        self.assertEqual(
            view.authentic_api_url,
            "https://agents.staging.imio.be/api/users/?service-ou=testou&service-slug=testslug",
        )

    def test_usergroup_userprefs(self):
        view = api.content.get_view(
            "usergroup-userprefs", context=self.portal, request=self.request
        )
        self.assertEqual(
            view.get_agent_url(), "https://agents.staging.imio.be/manage/users/"
        )
        self.assertEqual(
            view.get_update_url(),
            "http://nohost/plone/add-authentic-users?type=agents&next_url=http://nohost/plone/@@usergroup-userprefs",
        )
        self.assertIn('<button type="button"', view())
        self.assertIn("Wallonie-Connect", view())

    def test_redirect_parameter_before_login(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        redirect_target = api.content.create(
            type="Folder",
            id="secret",
            container=self.portal,
        )

        # Check login next_url
        view = api.content.get_view(
            name="imio_login", context=self.portal, request=self.request
        )
        expected = "http://nohost/plone/authentic-handler/?next_url=/secret"

        self.request.set("came_from", redirect_target.absolute_url())
        view()
        self.assertEqual(expected, self.request.RESPONSE.getHeader("location"))

        self.request.set("came_from", None)
        self.request.set("HTTP_REFERER", redirect_target.absolute_url())
        view()
        self.assertEqual(expected, self.request.RESPONSE.getHeader("location"))

        # Check authentic-handler next_url
        view = api.content.get_view(
            name="authentic-handler", context=self.portal, request=self.request
        )
        expected = "?next_url={}".format(redirect_target.absolute_url())
        self.request.form = {"next_url": redirect_target.absolute_url()}
        self.assertEqual(expected, view.next())

    def test_authentic_view_session_already_exists(self):
        view = api.content.get_view(
            "authentic-handler", context=self.portal, request=self.request
        )
        # not self.provider
        self.assertFalse(
            hasattr(view, "provider"), "Authentic View should not have a provider"
        )
        self.assertFalse(api.user.is_anonymous(), "User should not be anonymous.")
        view()
        self.assertEqual(self.request.RESPONSE.status, 302)
        self.assertEqual(
            self.request.RESPONSE.getHeader("location"), self.portal.absolute_url()
        )
        self.assertNotIn("Wallonie Connect", view())

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        redirect_target = api.content.create(
            type="Folder",
            id="secret",
            container=self.portal,
        )
        self.request.form = {"next_url": redirect_target.absolute_url()}
        view()
        self.assertEqual(self.request.RESPONSE.status, 302)
        self.assertEqual(
            self.request.RESPONSE.getHeader("location"), redirect_target.absolute_url()
        )
        self.assertNotIn("Wallonie Connect", view())

        # use provider
        view.provider = u"authentic-agents"
        self.request.form = {}
        view()
        self.assertEqual(self.request.RESPONSE.status, 302)
        self.assertEqual(
            self.request.RESPONSE.getHeader("location"), self.portal.absolute_url()
        )
        self.assertNotIn("Wallonie Connect", view())

        self.request.form = {"next_url": redirect_target.absolute_url()}
        view()
        self.assertEqual(self.request.RESPONSE.status, 302)
        self.assertEqual(
            self.request.RESPONSE.getHeader("location"), redirect_target.absolute_url()
        )
        self.assertNotIn("Wallonie Connect", view())

    def test_authentic_view_session_does_not_exist(self):
        view = api.content.get_view(
            "authentic-handler", context=self.portal, request=self.request
        )
        logout()

        # not self.provider
        self.assertFalse(
            hasattr(view, "provider"), "Authentic View should not have a provider"
        )
        self.assertTrue(api.user.is_anonymous(), "User should be anonymous.")
        self.assertIn("Wallonie Connect", view())

    def test_authentic_view_redirect_to_portal(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        folder = api.content.create(
            type="Folder",
            id="myfolder",
            container=self.portal,
        )
        logout()
        view = api.content.get_view(
            name="authentic-handler", context=folder, request=folder.REQUEST
        )
        authentic_url = "{0}/authentic-handler/".format(api.portal.get().absolute_url())
        view()
        self.assertEqual(authentic_url, self.request.response.getHeader("location"))

    def test_revoke_user_access_view(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        user = api.user.create(
            email="nope@test.imio",
            username="revoketester",
            password="12345-i-am-evil",
            roles=(
                "Member",
                "Reader",
                "Contributor",
                "Editor",
                "Reviewer",
                "Site Administrator",
                "Manager",
            ),
        )
        for group in api.group.get_groups():
            if group.id not in user.getGroups():
                api.group.add_user(group=group, user=user)

        # refresh user info
        user = api.user.get(user.id)
        self.assertListEqual(
            sorted(user.getRoles()),
            [
                "Authenticated",
                "Contributor",
                "Editor",
                "Manager",
                "Member",
                "Reader",
                "Reviewer",
                "Site Administrator",
            ],
        )

        self.assertListEqual(
            sorted(user.getGroups()),
            [
                "Administrators",
                "AuthenticatedUsers",
                "Reviewers",
                "Site Administrators",
            ],
        )

        self.request.form = {"userid": user.id}
        view = api.content.get_view(
            name="revoke-user-access", context=self.portal, request=self.request
        )
        view()

        # refresh user info
        user = api.user.get(user.id)
        self.assertListEqual(
            user.getRoles(),
            ["Authenticated"],
        )

        self.assertListEqual(
            user.getGroups(),
            ["AuthenticatedUsers"],
        )
