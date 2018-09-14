# -*- coding: utf-8 -*-
from plone.app.event.interfaces import IBrowserLayer
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from zope.component import getUtility
from zope.interface import alsoProvides

import os


def set_browserlayer(request):
    """Set the BrowserLayer for the request.

    We have to set the browserlayer manually, since importing the profile alone
    doesn't do it in tests.
    """
    alsoProvides(request, IBrowserLayer)


def set_timezone(tz):
    # Set the portal timezone
    if tz is None:
        return None
    reg = getUtility(IRegistry)
    current_tz = reg.get('plone.portal_timezone', None)
    reg['plone.portal_timezone'] = tz
    return current_tz


def set_env_timezone(tz):
    if tz is None:
        os.environ.pop('TZ')
        return None
    current_tz = os.environ.get('TZ', None)
    os.environ['TZ'] = tz
    return current_tz


def os_zone():
    return os.environ['TZ'] if 'TZ' in os.environ.keys() else None


def make_fake_response(request):
    """Create a fake response and set up logging of output."""
    headers = {}
    output = []

    class Response(object):
        def setHeader(self, header, value):
            headers[header] = value

        def write(self, msg):
            output.append(msg)

    request.response = Response()
    return headers, output, request


class PAEventLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # store original TZ, for the case it's overwritten
        self.ostz = os_zone()

        # Install products that use an old-style initialize() function
        z2.installProduct(app, 'Products.DateRecurringIndex')

        # Load ZCML
        import plone.app.event
        self.loadZCML(package=plone.app.event, context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.event:default')
        set_timezone(tz='UTC')

    def tearDownZope(self, app):
        # Uninstall old-style Products
        z2.uninstallProduct(app, 'Products.DateRecurringIndex')

        # reset OS TZ
        if self.ostz:
            os.environ['TZ'] = self.ostz
        elif 'TZ' in os.environ:
            del os.environ['TZ']


PAEvent_FIXTURE = PAEventLayer()
PAEvent_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEvent_FIXTURE,),
    name="PAEvent:Integration")


class PAEventDXLayer(PloneSandboxLayer):

    defaultBases = (PAEvent_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.ostz = os_zone()
        # Load ZCML
        import plone.app.contenttypes
        self.loadZCML(package=plone.app.contenttypes,
                      context=configurationContext)

        import plone.app.event.dx
        self.loadZCML(package=plone.app.event.dx,
                      context=configurationContext)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'plone.app.contenttypes:default')
        self.applyProfile(portal, 'plone.app.event:testing')
        set_timezone(tz='UTC')


PAEventDX_FIXTURE = PAEventDXLayer()
PAEventDX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PAEventDX_FIXTURE,),
    name="PAEventDX:Integration")
# Functional testing needed for tests, with explicit transaction commits.
PAEventDX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PAEventDX_FIXTURE,),
    name="PAEventDX:Functional")
PAEventDX_ROBOT_TESTING = FunctionalTesting(
    bases=(
        PAEventDX_FIXTURE,
        AUTOLOGIN_LIBRARY_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name="plone.app.event.dx:Robot")
