# -*- coding: utf-8 -*-
from authomatic import Authomatic
from authomatic.core import User
from pas.plugins.imio import _
from pas.plugins.imio.integration import ZopeRequestAdapter
from pas.plugins.imio.utils import authentic_cfg
from pas.plugins.imio.utils import authomatic_settings
from pas.plugins.imio.utils import getAuthenticPlugin
from pas.plugins.imio.utils import protocol
from pas.plugins.imio.utils import SimpleAuthomaticResult
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFDiffTool.utils import safe_utf8
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PluggableAuthService.events import PrincipalCreated
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging
import os
import requests
import six


logger = logging.getLogger(__file__)


class AddAuthenticUsers(BrowserView):
    def __init__(self, context, request, authentic_type="agents"):
        super(AddAuthenticUsers, self).__init__(context, request)
        config = authentic_cfg()
        if "type" in self.request.form.keys():
            self.authentic_type = self.request.form["type"]
        else:
            self.authentic_type = authentic_type
        if self.authentic_type not in ["usagers", "agents"]:
            return None
        self.next_url = api.portal.get().absolute_url()
        if "next_url" in self.request.form.keys():
            self.next_url = self.request.form["next_url"]

        self.authentic_config = config.get("authentic-{0}".format(self.authentic_type))
        self.consumer_key = os.getenv(
            "consumer_key_{0}".format(self.authentic_type), "my-consumer-key"
        )
        self.consumer_secret = os.getenv(
            "consumer_secret_{0}".format(self.authentic_type), "my-consumer-secret"
        )

    @property
    def authentic_api_url(self):
        authentic_hostname = self.authentic_config["hostname"]
        ou = os.getenv("service_ou", "default")
        service_slug = os.getenv("service_slug", "default")
        api_url = "{0}://{1}/api/users/?service-ou={2}&service-slug={3}".format(
            protocol(), authentic_hostname, ou, service_slug
        )
        return api_url

    def get_authentic_users(self):
        logger.warn(
            "{} {}:{}".format(
                self.authentic_api_url, self.consumer_key, self.consumer_secret
            )
        )
        req = requests.get(
            self.authentic_api_url, auth=(self.consumer_key, self.consumer_secret)
        )
        users = []
        if req.status_code == 200:
            response = req.json()
            users = users + response.get("results")
            next = response.get("next", "")
            while next:
                logger.info("count: {0}".format(len(users)))
                req = requests.get(next, auth=(self.consumer_key, self.consumer_secret))
                response = req.json()
                users = users + response.get("results")
                next = response.get("next", "")
            return users
        else:
            # be more explicit
            raise ConnectionError("Not able to connect to Authentic")

    def __call__(self):
        if self.authentic_type not in ["usagers", "agents"]:
            msg = "HTTP type GET argument should be usagers or agents, not: {0}".format(
                self.authentic_type
            )
            api.portal.show_message(message=msg, type="warn", request=self.request)
            self.request.response.redirect(api.portal.get().absolute_url())
            return ""
        plugin = getAuthenticPlugin()
        if not self.authentic_config:
            return ""

        users = self.get_authentic_users()
        new_users = 0
        for data in users:
            data["id"] = data["uuid"]
            user = User("authentic-{0}".format(self.authentic_type), **data)
            if not user.username:
                if six.PY2 and isinstance(user.email, six.text_type):
                    # user.id = safe_utf8(user.email)
                    user.username = safe_utf8(user.email)
                else:
                    # user.id = user.email
                    user.username = user.email
            if six.PY2 and isinstance(user.last_name, six.text_type):
                fullname = "{0} {1}".format(
                    safe_utf8(user.first_name), safe_utf8(user.last_name)
                )
            else:
                fullname = "{0} {1}".format(user.first_name, user.last_name)
            if not fullname.strip():
                user.fullname = user.username
            else:
                if six.PY2 and isinstance(fullname, six.text_type):
                    user.fullname = safe_utf8(fullname)
                else:
                    user.fullname = fullname

            if not plugin._useridentities_by_userid.get(user.id, None):
                # save
                # provider = Authentic()
                res = SimpleAuthomaticResult(plugin, self.authentic_type, user)
                useridentities = plugin.remember_identity(res)
                aclu = api.portal.get_tool("acl_users")
                ploneuser = aclu._findUser(aclu.plugins, useridentities.userid)
                notify(PrincipalCreated(ploneuser))
                logmsg = "User {0} added".format(user.username)
                logger.info(logmsg)
                new_users += 1
        import transaction

        transaction.commit()
        message = "{0} users added".format(new_users)
        api.portal.show_message(message=message, request=self.request)
        self.request.response.redirect(self.next_url)
        return "redirecting"


@implementer(IPublishTraverse)
class AuthenticView(BrowserView):

    template = ViewPageTemplateFile("authentic.pt")

    def publishTraverse(self, request, name):
        if name and not hasattr(self, "provider"):
            self.provider = name
        return self

    @property
    def _provider_names(self):
        cfgs = authentic_cfg()
        if not cfgs:
            raise ValueError("Authomatic configuration has errors.")
        return cfgs.keys()

    def providers(self):
        cfgs = authentic_cfg()
        if not cfgs:
            raise ValueError("Authomatic configuration has errors.")
        for identifier, cfg in cfgs.items():
            entry = cfg.get("display", {})
            cssclasses = entry.get("cssclasses", {})
            record = {
                "identifier": identifier,
                "title": entry.get("title", identifier),
                "iconclasses": cssclasses.get("icon", "glypicon glyphicon-log-in"),
                "buttonclasses": cssclasses.get(
                    "button", "plone-btn plone-btn-default"
                ),
                "as_form": entry.get("as_form", False),
            }
            yield record

    def _add_identity(self, result, provider_name):
        # delegate to PAS plugin to add the identity
        alsoProvides(self.request, IDisableCSRFProtection)
        aclu = api.portal.get_tool("acl_users")
        aclu.authentic.remember_identity(result)
        api.portal.show_message(
            _(
                "added_identity",
                default="Added identity provided by ${provider}",
                mapping={"provider": provider_name},
            ),
            self.request,
        )

    def _remember_identity(self, result, provider_name):
        alsoProvides(self.request, IDisableCSRFProtection)
        aclu = api.portal.get_tool("acl_users")

        aclu.authentic.remember(result)
        api.portal.show_message(
            _(
                "logged_in_with",
                "Logged in with ${provider}",
                mapping={"provider": provider_name},
            ),
            self.request,
        )

    def next(self):
        """Used to login page view"""
        next_url = self.request.form.get("next_url")
        if next_url:
            return "?next_url={0}".format(next_url)
        return ""

    def __call__(self):
        cfg = authentic_cfg()
        if cfg is None:
            return "Authomatic is not configured"
        if not (
            ISiteRoot.providedBy(self.context)
            or INavigationRoot.providedBy(self.context)
        ):
            # callback url is expected on site root by authentic; so before going on redirect
            root = api.portal.get()
            self.request.response.redirect(
                "{0}/authentic-handler/{1}".format(
                    root.absolute_url(), getattr(self, "provider", "")
                )
            )
            return "redirecting"
        if not hasattr(self, "provider"):
            # verify if is already connected
            if not self.is_anon:
                return self.redirect_next_url()
            return self.template()
        if self.provider not in cfg:
            return "Provider not supported"
        if not self.is_anon:
            if self.provider in self._provider_names:
                api.portal.show_message(
                    message="Session already active!",
                    request=self.request,
                    type="Warning",
                )
                return self.redirect_next_url()
            # todo: some sort of CSRF check might be needed, so that
            #       not an account got connected by CSRF. Research needed.
            pass
        secret = authomatic_settings().secret
        if six.PY2 and isinstance(secret, six.text_type):
            secret = secret.encode("utf8")
        auth = Authomatic(cfg, secret=secret)
        zope_request_adapter = ZopeRequestAdapter(self)
        result = auth.login(zope_request_adapter, self.provider)
        if not result:
            logger.info("return from view")
            # let authomatic do its work
            return
        if result.error:
            return result.error.message
        display = cfg[self.provider].get("display", {})
        provider_name = display.get("title", self.provider)

        if not self.is_anon:
            # now we delegate to PAS plugin to add the identity
            self._add_identity(result, provider_name)
            return self.redirect_next_url()
        else:
            # now we delegate to PAS plugin in order to login
            self._remember_identity(result, provider_name)
            redirect_url = self.context.absolute_url()
            state = result.provider.params.get("state")
            if state:
                decoded_state = result.provider.decode_state(state)
                if decoded_state:
                    redirect_url = "{0}{1}".format(redirect_url, decoded_state)
            self.request.response.redirect(redirect_url)
        return "redirecting"

    @property
    def is_anon(self):
        return api.user.is_anonymous()

    def redirect_next_url(self):
        next_url = self.request.form.get("next_url", self.context.absolute_url())
        return self.request.response.redirect(next_url)


class RevokeUserAccess(BrowserView):
    def __call__(self):
        user_id = self.request.form and self.request.form.get("userid", "")
        # api.user.get doesn't beak down if you give it garbage to find. It just returns None like a man
        user = api.user.get(user_id)
        if user:
            groups = [
                group
                for group in api.group.get_groups(user=user)
                if group.id != "AuthenticatedUsers"
            ]

            for group in groups:
                api.group.remove_user(group=group, user=user)

            roles = [
                role
                for role in user.getRoles()
                if role not in ("Anonymous", "Authenticated")
            ]
            api.user.revoke_roles(user=user, roles=roles)
        # if user_id doesn't exists, you get an error page. Which is good for you.
        self.request.response.redirect(
            "{}/@@usergroup-usermembership?userid={}".format(
                api.portal.get().absolute_url(), user_id
            )
        )
