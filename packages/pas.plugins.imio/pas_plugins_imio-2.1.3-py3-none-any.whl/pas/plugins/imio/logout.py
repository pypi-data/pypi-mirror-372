# -*- coding: utf-8 -*-
from pas.plugins.imio.utils import authentic_cfg
from pas.plugins.imio.utils import protocol
from plone import api
from Products.CMFPlone.utils import transaction_note
from Products.Five import BrowserView


class ImioLogoutFormView(BrowserView):
    def __call__(self):
        """Redirect login to authentic"""

        mt = api.portal.get_tool("portal_membership")
        mt.logoutUser(self.request)
        transaction_note("Logged out")
        config = authentic_cfg()
        authentic_type = "agents"
        authentic_config = config.get("authentic-{0}".format(authentic_type))
        authentic_hostname = authentic_config["hostname"]
        if not authentic_hostname:
            return
        authentic_logout_url = (
            "{0}://{1}/idp/oidc/logout?post_logout_redirect_uri={2}".format(
                protocol(), authentic_hostname, api.portal.get().absolute_url()
            )
        )

        response = self.request.response
        response.redirect(authentic_logout_url)
