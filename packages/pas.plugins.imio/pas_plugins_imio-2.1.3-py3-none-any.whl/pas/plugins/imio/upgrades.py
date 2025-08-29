from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from plone import api
from Products.CMFCore.interfaces import IContentish
from pas.plugins.imio.browser.view import AddAuthenticUsers
from authomatic.core import User

import logging

logger = logging.getLogger(__file__)


def set_new_userid(context=None):
    portal = api.portal.get()
    catalog = api.portal.get_tool("portal_catalog")
    membership = api.portal.get_tool("portal_membership")
    view = AddAuthenticUsers(portal, portal.REQUEST)
    users = view.get_authentic_users()

    acl_users = api.portal.get_tool("acl_users")
    plugin = acl_users.authentic
    plugin._useridentities_by_login = OOBTree()
    provider_name = "authentic-agents"

    for data in users:
        username = data["username"]
        mutable_properties = acl_users.mutable_properties
        if username in [us.get("id") for us in mutable_properties.enumerateUsers()]:
            mutable_properties.deleteUser(username)
            logger.info(
                "deleted user {} from mutable_properties plugin".format(username)
            )

        data["id"] = data["uuid"]
        user = User(provider_name, **data)
        userlogin = user.username
        userid = user.id
        saved_user = plugin._useridentities_by_userid.get(userlogin)
        member = membership.getMemberById(userlogin)
        old_roles = member and member.getRoles() or []
        if "Authenticated" in old_roles:
            old_roles.remove("Authenticated")

        if saved_user is None:
            logger.warning(
                "user not found in plugin (id: {}, login: {})".format(userid, userlogin)
            )
            continue
        saved_user.userid = userid
        saved_user.login = userlogin
        # saved_user._identities["authentic-agents"].update({"user_id": userid, "login": "userlogin"})
        plugin._useridentities_by_userid[userid] = saved_user
        plugin._useridentities_by_login[userlogin] = saved_user
        plugin._userid_by_identityinfo[(provider_name, userid)] = userid
        del plugin._useridentities_by_userid[userlogin]
        del plugin._userid_by_identityinfo[(provider_name, userlogin)]
        logger.info(
            "user updated, new id is:{}, new login is: {}".format(userid, userlogin)
        )
        api.user.grant_roles(username=userid, roles=old_roles)

    def do_migrate_roles(obj, path):
        do_migrate_roles_with_plugin(plugin, obj, path)

    portal.ZopeFindAndApply(portal, search_sub=True, apply_func=do_migrate_roles)
    catalog.reindexIndex("allowedRolesAndUsers", None)
    logger.info("Reindexed security")


def do_migrate_roles_with_plugin(plugin, obj, path):
    obj_url = obj.absolute_url()
    if not IContentish.providedBy(obj):
        return

    # migrate local roles
    if getattr(aq_base(obj), "__ac_local_roles__", None) is not None:
        localroles = obj.__ac_local_roles__
        migrated = False
        for login in list(localroles.keys()):
            roles = localroles[login]
            userid = convert_userid_with_plugin(plugin, login)
            if userid == login:
                continue
            obj.manage_delLocalRoles([login])
            obj.manage_setLocalRoles(userid=userid, roles=roles)
            migrated = True
        if migrated:
            logger.info("Migrated userids in local roles on {}".format(obj_url))

    # migrate creators
    creators = getattr(obj, "listCreators", [])
    if callable(creators):
        creators = creators()
    new_creators = tuple(convert_userids_with_plugin(plugin, creators))
    if creators != new_creators:
        obj.setCreators(new_creators)
        obj.reindexObject(idxs=["Creator", "listCreators"])
        logger.info("Migrated creator(s) on {}".format(obj_url))

    # migrate contributors
    contributors = getattr(obj, "listContributors", [])
    if callable(contributors):
        contributors = contributors()
    new_contributors = tuple(convert_userids_with_plugin(plugin, contributors))
    if contributors != new_contributors:
        obj.setContributors(new_contributors)
        logger.info("Migrated contributors(s) on {}".format(obj_url))


def convert_userid_with_plugin(plugin, login):
    user = plugin._useridentities_by_login.get(login)
    return user and user.userid or login


def convert_userids_with_plugin(plugin, logins):
    result = []
    for login in logins:
        userid = convert_userid_with_plugin(plugin, login)
        result.append(userid)
    return result
