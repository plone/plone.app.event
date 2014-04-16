from plone.app.event.base import default_timezone
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import set_env_timezone
from plone.app.event.testing import set_timezone
from plone.event.utils import default_timezone as os_default_timezone
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest2 as unittest


class TimezoneTest(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        set_env_timezone('UTC')
        set_timezone('UTC')

    def test_default_timezone(self):
        self.assertTrue(os_default_timezone() == default_timezone() == 'UTC')

        registry = getUtility(IRegistry)
        registry['plone.portal_timezone'] = "Europe/Vienna"
        self.assertTrue(default_timezone() == 'Europe/Vienna')
