# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPasPluginsImioLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAuthenticPlugin(Interface):
    """Member Properties To Group Plugin"""

    def remember(result):
        """remember user as valid

        result is authomatic result data.
        """
