from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from Products.DateRecurringIndex.testing import DRI_FIXTURE

class PAEventLayer(PloneSandboxLayer):

    # TODO: DRI_FIXTURE temporary until removal of DRI
    defaultBases = (DRI_FIXTURE, PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.event
        self.loadZCML(package=plone.app.event, context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event:default')

PAEvent_FIXTURE = PAEventLayer()
PAEvent_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEvent_FIXTURE,),
    name="PAEvent:Integration")
