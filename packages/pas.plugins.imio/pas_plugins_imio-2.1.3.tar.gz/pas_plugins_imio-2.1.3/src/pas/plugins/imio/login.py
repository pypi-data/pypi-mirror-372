# -*- coding: utf-8 -*-
from plone import api
from Products.Five import BrowserView


class ImioLoginFormView(BrowserView):
    def __call__(self):
        """Redirect login to authentic"""
        response = self.request.response
        next_url = self.request.get("HTTP_REFERER", self.context.absolute_url())
        url = "{0}/authentic-handler".format(api.portal.get().absolute_url())
        if next_url and next_url != api.portal.get().absolute_url():
            next_url = next_url.replace(api.portal.get().absolute_url(), "")
            url = "{0}/authentic-handler/?next_url={1}".format(
                api.portal.get().absolute_url(), next_url
            )
        next_url = self.request.get("came_from", None)
        if next_url and next_url != api.portal.get().absolute_url():
            next_url = next_url.replace(api.portal.get().absolute_url(), "")
            url = "{0}/authentic-handler/?next_url={1}".format(
                api.portal.get().absolute_url(), next_url
            )

        response.redirect(url)
