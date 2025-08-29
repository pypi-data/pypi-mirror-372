# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import pas.plugins.imio


class PasPluginsImioLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=pas.plugins.imio)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "pas.plugins.imio:default")


PAS_PLUGINS_IMIO_FIXTURE = PasPluginsImioLayer()


PAS_PLUGINS_IMIO_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAS_PLUGINS_IMIO_FIXTURE,), name="PasPluginsImioLayer:IntegrationTesting"
)


PAS_PLUGINS_IMIO_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PAS_PLUGINS_IMIO_FIXTURE,), name="PasPluginsImioLayer:FunctionalTesting"
)


PAS_PLUGINS_IMIO_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(PAS_PLUGINS_IMIO_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PasPluginsImioLayer:AcceptanceTesting",
)
