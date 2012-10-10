from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from Products.DateRecurringIndex.testing import DRI_FIXTURE

from plone.testing import z2

from zope.component import getUtility
from plone.app.event.interfaces import IEventSettings
from plone.registry.interfaces import IRegistry


def set_timezone(tz="UTC"):
    # Set the portal timezone
    reg = getUtility(IRegistry)
    settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
    settings.portal_timezone = tz


class PAEventLayer(PloneSandboxLayer):

    # TODO: DRI_FIXTURE temporary until removal of DRI
    defaultBases = (DRI_FIXTURE, PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.event
        self.loadZCML(package=plone.app.event, context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event:default')
        set_timezone(tz='UTC')


PAEvent_FIXTURE = PAEventLayer()
PAEvent_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEvent_FIXTURE,),
    name="PAEvent:Integration")


class PAEventATLayer(PloneSandboxLayer):

    defaultBases = (PAEvent_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.event.at
        self.loadZCML(package=plone.app.event.at, context=configurationContext)

        z2.installProduct(app, 'plone.app.event.at')

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event.at:default')

PAEventAT_FIXTURE = PAEventATLayer()
PAEventAT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEventAT_FIXTURE,),
    name="PAEventAT:Integration")


class PAEventDXLayer(PloneSandboxLayer):

    defaultBases = (PAEvent_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.event.dx
        self.loadZCML(package=plone.app.event.dx, context=configurationContext)

        z2.installProduct(app, 'plone.app.event.dx')

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event.dx:default')

PAEventDX_FIXTURE = PAEventDXLayer()
PAEventDX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEventDX_FIXTURE,),
    name="PAEventDX:Integration")
