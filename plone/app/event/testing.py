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


import os
from zope.configuration import xmlconfig
from zope.component import provideUtility
from plone.registry import Registry
from plone.registry.interfaces import IRegistry

from plone.testing import Layer
from plone.testing.zca import ZCML_DIRECTIVES
from plone.testing.z2 import STARTUP
from plone.app.event.interfaces import IEventSettings

class TimezoneLayer(Layer):
    defaultBases = (ZCML_DIRECTIVES, STARTUP,)

    def setUp(self):
        context = self['configurationContext']
        import plone.registry
        import plone.app.event
        xmlconfig.file('configure.zcml', plone.registry, context=context)

        self['plone_registry'] = Registry()
        self['plone_registry'].registerInterface(IEventSettings)
        provideUtility(self['plone_registry'], IRegistry)

        self['ostz'] = 'TZ' in os.environ.keys() and os.environ['TZ'] or None
        os.environ['TZ'] = "CET"

    def tearDown(self):
        # delete resources from setUp
        if self['ostz']:
            os.environ['TZ'] = self['ostz']
        else:
            del os.environ['TZ']

TIMEZONE_LAYER = TimezoneLayer()
