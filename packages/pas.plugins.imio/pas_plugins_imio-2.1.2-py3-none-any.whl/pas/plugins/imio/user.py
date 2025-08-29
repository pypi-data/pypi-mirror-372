# -*- coding: utf-8 -*-
from plone import api

try:
    from plone.app.users.browser.personalpreferences import UserDataPanel
    from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
    from plone.app.users.browser.personalpreferences import UserDataConfiglet
except ImportError:
    from plone.app.users.browser.userdatapanel import UserDataPanel
    from plone.app.users.browser.userdatapanel import UserDataPanelAdapter
    from plone.app.users.browser.userdatapanel import UserDataConfiglet

try:
    from plone.app.users.userdataschema import checkEmailAddress
    from plone.app.users.userdataschema import IUserDataSchema
    from plone.app.users.userdataschema import IUserDataSchemaProvider as IUserSchemaProvider
except ImportError:
    from plone.app.users.schema import IUserDataSchema
    from plone.app.users.schema import IUserSchemaProvider
    from plone.app.users.schema import checkEmailAddress

from Products.CMFPlone import PloneMessageFactory as _
from zope import schema
from zope.browserpage import ViewPageTemplateFile
from zope.interface import implementer


@implementer(IUserSchemaProvider)
class UserDataSchemaProvider(object):
    def getSchema(self):
        """ """
        return IPASUserDataSchema


class IPASUserDataSchema(IUserDataSchema):
    """Use all the fields from the default user data schema, and add various
    extra fields.
    """

    # username = schema.TextLine(
    #     title=_(u"label_user_name", default=u"User Name"),
    #     description=_(
    #         u"help_user_name_creation", default=u"Enter user name, e.g. jsmith."
    #     ),
    #     required=False,
    #     readonly=True,
    # )

    fullname = schema.TextLine(
        title=_(u"label_full_name", default=u"Full Name"),
        description=_(
            u"help_full_name_creation", default=u"Enter full name, e.g. John Smith."
        ),
        required=False,
        readonly=True,
    )

    email = schema.ASCIILine(
        title=_(u"label_email", default=u"E-mail"),
        description=u"",
        required=True,
        readonly=True,
        constraint=checkEmailAddress,
    )


class PASUserDataPanelAdapter(UserDataPanelAdapter):
    """ """


class PasUserDataPanel(UserDataPanel):
    """
    """
    def __init__(self, context, request):
        super(PasUserDataPanel, self).__init__(context, request)
        if self.userid:
            pas = api.portal.get_tool("acl_users")
            if self.userid in pas.source_users.listUserIds():
                self.form_fields.get('fullname').field.readonly = False
                self.form_fields.get('email').field.readonly = False


class PasUserDataConfiglet(PasUserDataPanel):
    template = ViewPageTemplateFile(UserDataConfiglet.template.filename)
