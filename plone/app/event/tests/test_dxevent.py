import os
import unittest2 as unittest
import datetime

from plone.app.event.dx.behaviors import (
    default_start,
    default_end,
    default_tz,
    StartBeforeEnd,
    IEventBasic
)


class MockEvent(object):
    """ Mock event.
    """

class TestDXEventUnittest(unittest.TestCase):
    """ Unit test for Dexterity event behaviors.
    """

    def setUp(self):
        self.ostz = 'TZ' in os.environ.keys() and os.environ['TZ'] or None
        os.environ['TZ'] = 'CET'

    def tearDown(self):
        if self.ostz:
            os.environ['TZ'] = self.ostz
        else:
            del os.environ['TZ']

    def test_start_defaults(self):
        data = MockEvent()
        default_value = default_start(data)
        today = datetime.datetime.today()
        delta = default_value - today
        self.assertEquals(6, delta.days)

    def test_end_default(self):
        data = MockEvent()
        default_value = default_end(data)
        today = datetime.datetime.today()
        delta = default_value - today
        self.assertEquals(9, delta.days)

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
