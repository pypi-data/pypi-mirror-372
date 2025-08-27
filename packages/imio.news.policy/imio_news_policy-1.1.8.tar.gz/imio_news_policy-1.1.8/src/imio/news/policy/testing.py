# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2
from zope.globalrequest import setRequest

import imio.news.policy


class ImioNewsPolicyLayer(PloneSandboxLayer):
    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi

        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=imio.news.policy)

    def setUpPloneSite(self, portal):
        request = portal.REQUEST
        # set basic request to be able to handle redirect in subscribers
        setRequest(request)
        applyProfile(portal, "imio.news.policy:default")


IMIO_NEWS_POLICY_FIXTURE = ImioNewsPolicyLayer()


IMIO_NEWS_POLICY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IMIO_NEWS_POLICY_FIXTURE,),
    name="ImioNewsPolicyLayer:IntegrationTesting",
)


IMIO_NEWS_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IMIO_NEWS_POLICY_FIXTURE,),
    name="ImioNewsPolicyLayer:FunctionalTesting",
)


IMIO_NEWS_POLICY_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        IMIO_NEWS_POLICY_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="ImioNewsPolicyLayer:AcceptanceTesting",
)
