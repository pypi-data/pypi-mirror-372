# -*- coding: utf-8 -*-
"""Init and utils."""
from AccessControl.Permissions import add_user_folders
from pas.plugins.imio.plugin import AuthenticPlugin
from pas.plugins.imio.plugin import manage_addAuthenticPlugin
from pas.plugins.imio.plugin import manage_addAuthenticPluginForm
from pas.plugins.imio.plugin import tpl_dir
from Products.PluggableAuthService import registerMultiPlugin
from zope.i18nmessageid import MessageFactory

import os


_ = MessageFactory("pas.plugins.imio")


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """
    registerMultiPlugin("Authentic Plugin")
    context.registerClass(
        AuthenticPlugin,
        permission=add_user_folders,
        icon=os.path.join(tpl_dir, "static/logo-agent.svg"),
        constructors=(manage_addAuthenticPluginForm, manage_addAuthenticPlugin),
        visibility=None,
    )
