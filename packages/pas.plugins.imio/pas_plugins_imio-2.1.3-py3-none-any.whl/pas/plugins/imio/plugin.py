# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import manage_users as ManageUsers
from AccessControl.requestmethod import postonly
from authomatic.core import User
from BTrees.OOBTree import OOBTree
from operator import itemgetter
from pas.plugins.authomatic.plugin import AuthomaticPlugin
from pas.plugins.imio.interfaces import IAuthenticPlugin
from pas.plugins.imio.useridentities import UserIdentities
from pas.plugins.imio.useridfactories import new_userid
from pas.plugins.imio.useridfactories import new_login
from pas.plugins.imio.utils import authentic_cfg
from pas.plugins.imio.utils import protocol
from pas.plugins.imio.utils import SimpleAuthomaticResult
from plone import api
from Products.CMFCore.permissions import ManagePortal
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.events import PrincipalCreated
from Products.PluggableAuthService.interfaces import plugins as pas_interfaces
from Products.PlonePAS.interfaces.plugins import IUserIntrospection
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.event import notify
from zope.interface import implementer
from jwcrypto.jwk import JWKSet
from jwcrypto.jwt import JWT


import json
import requests
import logging
import os
import six


logger = logging.getLogger(__name__)
tpl_dir = os.path.join(os.path.dirname(__file__), "browser")

_marker = {}


def manage_addAuthenticPlugin(context, id="authentic", title="", RESPONSE=None, **kw):
    """Create an instance of a Authentic Plugin."""
    plugin = AuthenticPlugin(id, title, **kw)
    context._setObject(plugin.getId(), plugin)
    if RESPONSE is not None:
        RESPONSE.redirect("manage_workspace")


manage_addAuthenticPluginForm = PageTemplateFile("www/AuthenticPluginForm", globals())


@implementer(
    IAuthenticPlugin,
    pas_interfaces.IAuthenticationPlugin,
    pas_interfaces.IExtractionPlugin,
    pas_interfaces.IPropertiesPlugin,
    pas_interfaces.IUserEnumerationPlugin,
    pas_interfaces.IRolesPlugin,
    IUserIntrospection,
)
class AuthenticPlugin(AuthomaticPlugin):
    """Authentic PAS Plugin"""

    security = ClassSecurityInfo()
    meta_type = "Authentic Plugin"
    # BasePlugin.manage_options
    manage_options = (
        {"label": "Authentic Users", "action": "manage_authenticplugin"},
    ) + AuthomaticPlugin.manage_options
    security.declareProtected(ManagePortal, "manage_authenticplugin")
    manage_authenticplugin = PageTemplateFile(
        "zmi", globals(), __name__="manage_authenticplugin"
    )

    # Tell PAS not to swallow our exceptions
    _dont_swallow_my_exceptions = True

    # ##
    # pas_interfaces.plugins.IUserEnumaration

    def _init_trees(self):
        # (provider_name, provider_userid) -> userid
        self._userid_by_identityinfo = OOBTree()

        # userid / login -> userdata
        self._useridentities_by_userid = OOBTree()
        self._useridentities_by_login = OOBTree()

    @security.private
    def remember_identity(self, result, userid=None):
        # useridentities = super(AuthenticPlugin, self).remember_identity(result, userid)
        new_user = False
        if userid is None:
            # create a new userid
            new_user = True
            userid = new_userid(self, result)
            login = new_login(self, result)
            useridentities = UserIdentities(userid, login)

            # get roles and groups
            membership = api.portal.get_tool("portal_membership")
            member = membership.getMemberById(login)
            old_roles = member and member.getRoles() or []
            if "Authenticated" in old_roles:
                old_roles.remove("Authenticated")
            old_groups = member and api.group.get_groups(username=login) or []
            old_group_ids = [group.id for group in old_groups]
            if "AuthenticatedUsers" in old_group_ids:
                old_group_ids.remove("AuthenticatedUsers")
            self._useridentities_by_userid[userid] = useridentities
            self._useridentities_by_login[login] = useridentities
        else:
            # use existing userid
            useridentities = self._useridentities_by_userid.get(userid, None)
            if useridentities is None:
                raise ValueError("Invalid userid")
        provider_id = self._provider_id(result)
        if provider_id not in self._userid_by_identityinfo:
            self._userid_by_identityinfo[provider_id] = userid

        useridentities.handle_result(result)
        if new_user:
            acl_users = api.portal.get_tool("acl_users")
            username = result.user.username
            # clean mutable_properties
            mutable_properties = acl_users.mutable_properties
            if username in [us.get("id") for us in mutable_properties.enumerateUsers()]:
                mutable_properties.deleteUser(username)

            # remove old plone userid from source_users and set roles and groups to new
            source_users = acl_users.source_users
            if username in [us.get("id") for us in source_users.enumerateUsers()]:
                api.user.grant_roles(username=userid, roles=old_roles)
                for group in old_group_ids:
                    api.group.add_user(groupname=group, username=userid)
                source_users.removeUser(username)
        return useridentities

    @security.protected(ManageUsers)
    def getUsers(self):
        users = []
        for id in self._useridentities_by_userid:
            identity = self._useridentities_by_userid[id]
            user = PloneUser(id)
            user.addPropertysheet(
                "email", data={"email": identity.propertysheet.getProperty("email", "")}
            )
            users.append(user)
        return users

    @security.protected(ManageUsers)
    def getPluginUsers(self):
        users = []
        for plugin_id, userid in self._userid_by_identityinfo:
            user = {}
            user["id"] = userid
            identity = self._useridentities_by_userid[userid]
            if hasattr(identity, "login"):
                user["login"] = identity.login
            else:
                user["login"] = ""
            user["email"] = identity.propertysheet.getProperty("email", "")
            user["fullname"] = identity.propertysheet.getProperty("fullname", "")
            user["plugin_type"] = plugin_id
            users.append(user)
        return users

    @security.protected(ManageUsers)
    def removeUser(self, userid, provider_name="authentic-agents"):
        if "\r" in userid:
            userid = userid.replace("\r", "")
        if hasattr(self._useridentities_by_userid[userid], "login"):
            login = self._useridentities_by_userid[userid].login
            try:
                del self._useridentities_by_login[login]
            except:
                logger.error("Failed to remove user: {0}".format(login))
                pass
        else:
            login = userid
        del self._useridentities_by_userid[userid]
        del self._userid_by_identityinfo[(provider_name, userid)]
        return login

    @security.protected(ManageUsers)
    @postonly
    def manage_removeUser(self, REQUEST):
        """Delete users of Authentic Plugin."""
        response = REQUEST.response
        users_to_delete = [
            users for users in REQUEST.form.keys() if not users.startswith("_")
        ]  # do not get _authenticator form
        login_deleted = []
        for userid in users_to_delete:
            # todo get provider_name
            login_deleted.append(self.removeUser(userid))
        response.redirect(
            "{0}/manage_authenticplugin?manage_tabs_message={1}".format(
                self.absolute_url(), ", ".join(login_deleted) + " deleted."
            )
        )

    @security.private
    def enumerateUsers(
        self,
        id=None,
        login=None,
        exact_match=False,
        sort_by=None,
        max_results=None,
        **kw
    ):
        """-> ( user_info_1, ... user_info_N )
        OVERRIDE OF PARENT because empty search should get all user and not any.

        o Return mappings for users matching the given criteria.

        o 'id' or 'login', in combination with 'exact_match' true, will
          return at most one mapping per supplied ID ('id' and 'login'
          may be sequences).

        o If 'exact_match' is False, then 'id' and / or login and / or email may be
          treated by the plugin as "contains" searches (more complicated
          searches may be supported by some plugins using other keyword
          arguments).

        o If 'sort_by' is passed, the results will be sorted accordingly.
          known valid values are 'id' and 'login' (some plugins may support
          others).

        o If 'max_results' is specified, it must be a positive integer,
          limiting the number of returned mappings.  If unspecified, the
          plugin should return mappings for all users satisfying the criteria.

        o Minimal keys in the returned mappings:

          'id' -- (required) the user ID, which may be different than
                  the login name

          'login' -- (required) the login name

          'pluginid' -- (required) the plugin ID (as returned by getId())

          'editurl' -- (optional) the URL to a page for updating the
                       mapping's user

        o Plugin *must* ignore unknown criteria.

        o Plugin may raise ValueError for invalid criteria.

        o Insufficiently-specified criteria may have catastrophic
          scaling issues for some implementations.
        """
        if id and login and id != login:
            raise ValueError("plugin does not support id different from login")
        search_id = id or login
        if search_id:
            if not isinstance(search_id, six.string_types):
                raise NotImplementedError("sequence is not supported.")
        else:
            if search_id != "":
                return ()

        pluginid = self.getId()
        ret = list()
        # shortcut for exact match of login/id
        identity = None
        if exact_match:
            if search_id in self._useridentities_by_userid:
                identity = self._useridentities_by_userid[search_id]
            elif search_id in self._useridentities_by_login:
                identity = self._useridentities_by_login[search_id]
            else:
                return []
        if identity is not None:
            identity_userid = identity.userid
            if hasattr(identity, "login"):
                identity_userlogin = identity.login
            else:
                identity_userlogin = identity.userid
            if six.PY2 and isinstance(identity_userid, six.text_type):
                identity_userid = identity_userid.encode("utf8")
                identity_userlogin = identity_userlogin.encode("utf8")

            ret.append(
                {
                    "id": identity_userid,
                    "login": identity_userlogin,
                    "pluginid": pluginid,
                }
            )
            return ret

        # non exact expensive search
        for userid in self._useridentities_by_userid:
            user = self._useridentities_by_userid.get(userid, "")
            login = getattr(user, "login", None) or ""
            email = user.propertysheet.getProperty("email", "")
            # if hasattr(user, "login"):
            if not userid and not email:
                logger.warn("None userid found. This should not happen!")
                continue
            if not (search_id in userid or search_id in login or search_id in email):
                logger.debug("not searchable: {0} for {1}".format(search_id, userid))
                continue
            identity = self._useridentities_by_userid[userid]
            identity_userid = identity.userid
            if hasattr(identity, "login"):
                identity_userlogin = identity.login
            else:
                identity_userlogin = identity.userid

            if six.PY2 and isinstance(identity_userid, six.text_type):
                identity_userid = identity_userid.encode("utf8")
                identity_userlogin = identity_userlogin.encode("utf8")
            ret.append(
                {
                    "id": identity_userid,
                    "login": identity_userlogin,
                    "pluginid": pluginid,
                }
            )
            if max_results and len(ret) >= max_results:
                break
        if sort_by in ["id", "login"]:
            return sorted(ret, key=itemgetter(sort_by))
        return ret

    @security.private
    def getRolesForPrincipal(self, user, request=None):
        """Fullfill RolesPlugin requirements"""
        identity = self._useridentities_by_userid.get(user.getId(), None)
        if not identity:
            return ()
        if not identity._identities:
            return ()
        keys = [key for key in identity._identities.keys()]
        provider_id = keys[0]
        if "roles" in identity._identities[provider_id].keys():
            roles = identity._identities[provider_id]["roles"]
            if isinstance(roles, list):
                return tuple(roles)
            else:
                return ()
        else:
            return ()

    @security.private
    def extractCredentials(self, request):
        """Extract an OAuth2 bearer access token from the request.
        Implementation of IExtractionPlugin that extracts any 'Bearer' token
        from the HTTP 'Authorization' header.
        """
        # See RFC 6750 (2.1. Authorization Request Header Field) for details
        # on bearer token usage in OAuth2
        # https://tools.ietf.org/html/rfc6750#section-2.1

        creds = {}
        auth = request._auth
        if auth is None:
            return None
        if auth[:7].lower() == "bearer ":
            creds["token"] = auth.split()[-1]
        else:
            return None

        return creds

    @security.public
    def authenticateCredentials(self, credentials):
        """credentials -> (userid, login)

        - 'credentials' will be a mapping, as returned by IExtractionPlugin.
        - Return a  tuple consisting of user ID (which may be different
          from the login name) and login
        - If the credentials cannot be authenticated, return None.
        """
        token = credentials.get("token", None)
        if token:
            payload = self._decode_token(token)
            userid = payload.get("sub", None)
            login = payload.get("userid", None)
            if not userid:
                return None
            if userid not in self._useridentities_by_userid:
                authentic_type = "agents"
                user = User("authentic-{0}".format(authentic_type))
                user.id = userid
                user.username = login
                res = SimpleAuthomaticResult(self, authentic_type, user)
                self.remember_identity(res)
                # useridentities = self.remember_identity(res)
                # aclu = api.portal.get_tool("acl_users")
                # ploneuser = aclu._findUser(aclu.plugins, useridentities.userid)
                # notify(PrincipalCreated(ploneuser))
            return userid, login

    def _decode_token(self, token):
        authentic_type = "authentic-agents"
        hostname = authentic_cfg()[authentic_type]["hostname"]
        certs_url = "{0}://{1}/idp/oidc/certs/".format(protocol(), hostname)
        keyset = JWKSet.from_json(requests.get(certs_url).content)
        # keyset = JWKSet.from_json(json.dumps(requests.get(certs_url).json()))
        if os.getenv("ENV") == "test":
            # do not check if payload is valid
            jwtcrypto = JWT(jwt=token, algs=["RS256"])
            payload = json.loads(jwtcrypto.token.objects.get("payload"))
        else:
            jwtcrypto = JWT(jwt=token, key=keyset, algs=["RS256"])
            payload = json.loads(jwtcrypto.token.payload)
        return payload


InitializeClass(AuthenticPlugin)
