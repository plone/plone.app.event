import os
from zope.configuration import xmlconfig
from zope.component import provideUtility, getUtility
from plone.registry import Registry
from plone.registry.interfaces import IRegistry

from plone.testing import Layer
from plone.testing.zca import ZCML_DIRECTIVES
from plone.testing.z2 import STARTUP
from plone.app.event.controlpanel.event import IEventSettings

class TimezoneLayer(Layer):
    defaultBases = (ZCML_DIRECTIVES, STARTUP,)

    def setUp(self):
        context = self['configurationContext']
        import plone.registry
        import plone.event
        import plone.app.event
        xmlconfig.file('configure.zcml', plone.registry, context=context)
        xmlconfig.file('configure.zcml', plone.event, context=context)
        xmlconfig.file('timezone.zcml', plone.app.event, context=context)

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

    def testSetUp(self):
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings)
        settings.portal_timezone = None
        settings.available_timezones = None

    def testTeasDown(self):
        reg = getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings)
        settings.portal_timezone = None
        settings.available_timezones = None


TIMEZONE_LAYER = TimezoneLayer()
