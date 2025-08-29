# -*- coding: utf-8 -*-
from pas.plugins.authomatic.useridfactories import BaseUserIDFactory

# from pas.plugins.imio import _
from pas.plugins.authomatic.interfaces import IUserIDFactory
from pas.plugins.authomatic.utils import authomatic_settings
from zope.component import queryUtility


class ProviderIDFactory(BaseUserIDFactory):

    title = u"Provider User ID for Authentic"

    def __call__(self, plugin, result):
        if result.provider.name.endswith("agents"):
            return self.normalize(plugin, result, result.user.username)
        else:
            return self.normalize(plugin, result, result.user.email)


def new_userid(plugin, result):
    factory = queryUtility(IUserIDFactory, name="userid", default=ProviderIDFactory())
    return factory(plugin, result)


def new_login(plugin, result):
    settings = authomatic_settings()
    factory = queryUtility(
        IUserIDFactory, name=settings.userid_factory_name, default=ProviderIDFactory()
    )
    return factory(plugin, result)
