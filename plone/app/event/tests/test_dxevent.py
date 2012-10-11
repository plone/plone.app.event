from plone.app.event.base import localized_now
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
import datetime
import os
import unittest2 as unittest


from plone.app.event.dx.behaviors import (
    default_start,
    default_end,
    default_tz,
    StartBeforeEnd,
    IEventBasic
)
from plone.app.event.testing import set_env_timezone

TZNAME = "Europe/Vienna"


class MockEvent(object):
    """ Mock event.
    """


class TestDXEventIntegration(unittest.TestCase):

    layer = PAEventAT_INTEGRATION_TESTING

    def test_start_defaults(self):
        data = MockEvent()
        default_value = default_start(data)
        today = localized_now()
        delta = default_value - today
        self.assertEquals(-1, delta.days)

    def test_end_default(self):
        data = MockEvent()
        default_value = default_end(data)
        today = localized_now()
        delta = default_value - today
        self.assertEquals(0, delta.days)


class TestDXEventUnittest(unittest.TestCase):
    """ Unit test for Dexterity event behaviors.
    """

    def setUp(self):
        set_env_timezone(TZNAME)

    def test_validate_invariants_ok(self):
        data = MockEvent()
        data.start = datetime.datetime(2009, 1, 1)
        data.end = datetime.datetime(2009, 1, 2)

        try:
            IEventBasic.validateInvariants(data)
        except:
            self.fail()

    def test_validate_invariants_fail(self):
        data = MockEvent()
        data.start = datetime.datetime(2009, 1, 2)
        data.end = datetime.datetime(2009, 1, 1)

        try:
            IEventBasic.validateInvariants(data)
            self.fail()
        except StartBeforeEnd:
            pass

    def test_validate_invariants_edge(self):
        data = MockEvent()
        data.start = datetime.datetime(2009, 1, 2)
        data.end = datetime.datetime(2009, 1, 2)

        try:
            IEventBasic.validateInvariants(data)
        except:
            self.fail()

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
