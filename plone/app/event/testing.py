from Products.DateRecurringIndex.testing import DRI_FIXTURE
from plone.app.event.interfaces import IEventSettings
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from zope.component import getUtility

import os


def set_timezone(tz):
    # Set the portal timezone
    reg = getUtility(IRegistry)
    settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
    settings.portal_timezone = tz

def set_env_timezone(tz):
    os.environ['TZ'] = tz

def os_zone():
    return 'TZ' in os.environ.keys() and os.environ['TZ'] or None


class PAEventLayer(PloneSandboxLayer):
    defaultBases = (DRI_FIXTURE, PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # store original TZ, for the case it's overwritten
        self.ostz = os_zone()

        # Load ZCML
        import plone.app.event
        self.loadZCML(package=plone.app.event, context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event:default')
        set_timezone(tz='UTC')

    def tearDownZope(self, app):
        # reset OS TZ
        if self.ostz:
            os.environ['TZ'] = self.ostz
        elif 'TZ' in os.environ:
            del os.environ['TZ']


PAEvent_FIXTURE = PAEventLayer()
PAEvent_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEvent_FIXTURE,),
    name="PAEvent:Integration")


class PAEventATLayer(PloneSandboxLayer):

    defaultBases = (PAEvent_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.ostz = os_zone()
        # Load ZCML
        import plone.app.event.at
        self.loadZCML(package=plone.app.event.at, context=configurationContext)

        z2.installProduct(app, 'plone.app.event.at')

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event.at:default')
        set_timezone(tz='UTC')

PAEventAT_FIXTURE = PAEventATLayer()
PAEventAT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEventAT_FIXTURE,),
    name="PAEventAT:Integration")


class PAEventDXLayer(PloneSandboxLayer):

    defaultBases = (PAEvent_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.ostz = os_zone()
        # Load ZCML
        import plone.app.event.dx
        self.loadZCML(package=plone.app.event.dx, context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event.dx:default')
        set_timezone(tz='UTC')

PAEventDX_FIXTURE = PAEventDXLayer()
PAEventDX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEventDX_FIXTURE,),
    name="PAEventDX:Integration")


class PAEventATDXLayer(PloneSandboxLayer):
    defaultBases = (PAEvent_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        self.ostz = os_zone()
        # Load ZCML
        import plone.app.event.at
        self.loadZCML(package=plone.app.event.at, context=configurationContext)
        z2.installProduct(app, 'plone.app.event.at')

        import plone.app.event.dx
        self.loadZCML(package=plone.app.event.dx, context=configurationContext)

        import plone.app.collection
        self.loadZCML(package=plone.app.collection, context=configurationContext)
        z2.installProduct(app, 'plone.app.collection')


    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event.at:default')
        self.applyProfile(portal, 'plone.app.event.dx:default')
        self.applyProfile(portal, 'plone.app.collection:default')
        set_timezone(tz='UTC')


PAEventATDX_FIXTURE = PAEventATDXLayer()
PAEventATDX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEventATDX_FIXTURE,),
    name="PAEventATDX:Integration")
