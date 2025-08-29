# -*- coding: utf-8 -*-
from pas.plugins.authomatic.utils import authomatic_settings
from pas.plugins.imio.interfaces import IAuthenticPlugin
from plone import api
from zope.dottedname.resolve import resolve

import json
import os


def authentic_cfg():
    """fetches the authomatic configuration from the settings and
    returns it as a dict
    """
    settings = authomatic_settings()
    try:
        cfg = json.loads(settings.json_config)
    except ValueError:
        return None
    if not isinstance(cfg, dict):
        return None
    for provider in cfg:
        if "class_" in cfg[provider]:
            cfg[provider]["class_"] = resolve(cfg[provider]["class_"])
        if u"id" in cfg[provider]:
            cfg[provider][u"id"] = int(cfg[provider][u"id"])
        if u"consumer_key" not in cfg[provider]:
            cfg[provider][u"consumer_key"] = os.getenv(
                "consumer_key_{0}".format(cfg[provider]["type"]), "my-consumer-key"
            )
        if u"consumer_secret" not in cfg[provider]:
            cfg[provider][u"consumer_secret"] = os.getenv(
                "consumer_secret_{0}".format(cfg[provider]["type"]), "my-consumer-key"
            )
        cfg[provider][u"hostname"] = os.getenv(
            "authentic_{0}_hostname".format(cfg[provider]["type"])
        )
    return cfg


def getAuthenticPlugin():
    pas = api.portal.get_tool("acl_users")
    plugin = pas["authentic"]
    if IAuthenticPlugin.providedBy(plugin):
        return plugin
    raise KeyError


def protocol():
    return "http" if os.getenv("ENV", "prod") in ["dev"] else "https"


class SimpleAuthomaticResult:
    def __init__(self, provider, authentic_type, user):
        self.provider = provider
        self.provider.name = "authentic-{0}".format(authentic_type)
        self.user = user
        self.user.provider = self.provider
        self.user.data = {}
