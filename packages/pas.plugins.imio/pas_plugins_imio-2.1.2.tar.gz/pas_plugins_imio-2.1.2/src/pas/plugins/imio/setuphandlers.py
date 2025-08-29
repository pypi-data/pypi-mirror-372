# -*- coding: utf-8 -*-
from pas.plugins.imio.plugin import AuthenticPlugin
from pkg_resources import parse_version
from plone import api
from plone.api import env
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


HAS_PLONE5 = parse_version(env.plone_version()) >= parse_version("5.0")


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            "pas.plugins.imio:base",
            "pas.plugins.imio:uninstall",
            "pas.plugins.authomatic:default",
        ]


def _add_plugin(pas, pluginid="authentic"):
    if pluginid in pas.objectIds():
        return pluginid + " already installed."
    plugin = AuthenticPlugin(pluginid, title="Authentic")
    pas._setObject(pluginid, plugin)
    plugin = pas[plugin.getId()]  # get plugin acquisition wrapped!
    for info in pas.plugins.listPluginTypeInfo():
        interface = info["interface"]
        if not interface.providedBy(plugin):
            continue
        pas.plugins.activatePlugin(interface, plugin.getId())
        pas.plugins.movePluginsDown(
            interface, [x[0] for x in pas.plugins.listPlugins(interface)[:-1]]
        )


def post_install(context):
    """Post install script"""
    if HAS_PLONE5:
        api.portal.set_registry_record("plone.external_login_url", "imio_login")
        api.portal.set_registry_record("plone.external_logout_url", "imio_logout")
    else:
        portal_properties = api.portal.get_tool("portal_properties")
        site_properties = portal_properties.site_properties
        site_properties.external_login_url = u"imio_login"
        site_properties.external_logout_url = u"imio_logout"
    _add_plugin(api.portal.get_tool("acl_users"))


def uninstall(context):
    """Uninstall script"""
    if HAS_PLONE5:
        api.portal.set_registry_record("plone.external_login_url", "")
        api.portal.set_registry_record("plone.external_logout_url", "")
    else:
        portal_properties = api.portal.get_tool("portal_properties")
        site_properties = portal_properties.site_properties
        site_properties.external_login_url = ""
        site_properties.external_logout_url = ""
