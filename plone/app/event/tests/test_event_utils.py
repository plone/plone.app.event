import plone.app.event.tests.base

import unittest
from DateTime import DateTime

from plone.app.event import event_util
from plone.app.event.event import ATEvent as Event
from plone.app.event.tests.base import EventTestCase

class EventUtilsTests(EventTestCase):

    def _makeOne(self, start, end, wholeDay=False):
        self.login()
        self.setRoles('Manager')
        self.portal.invokeFactory('Event', id='event')
        event = self.portal['event']
        event.setStartDate(start)
        event.setEndDate(end)
        event.setWholeDay(wholeDay)
        return event

    def testIsSameDay(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.isSameDay(event), True)

    def testIsSameDayFailing(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00')
        self.assertEqual(event_util.isSameDay(event), False)

    def testIsSameTime(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 06:00:00')
        self.assertEqual(event_util.isSameTime(event), True)

    def testIsSameTimeFailing(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.isSameTime(event), False)

    def testToDisplayWithTime(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : '06:00 AM',
                 'end_date' : 'Oct 12, 2000',
                 'end_time' : '06:00 PM',
                 'same_day' : True,
                 'same_time' : False,
                })

    def testToDisplayWholeDaySameDay(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00',
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,
                 'end_date' : 'Oct 12, 2000',
                 'end_time' : None,
                 'same_day' : True,
                 'same_time' : False,
                })

    def testToDisplayWholeDayDifferentDays(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00',
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,
                 'end_date' : 'Oct 13, 2000',
                 'end_time' : None,
                 'same_day' : False,
                 'same_time' : False,
                })


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventUtilsTests))
    return suite
