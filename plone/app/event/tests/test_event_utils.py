import unittest
from DateTime import DateTime

from plone.app.event import event_util
from plone.app.event.event import ATEvent as Event
from plone.app.event.tests.base import EventTestCase


class EventUtilsTests(EventTestCase):

    def _makeOne(self, start, end, useEndDate=True, wholeDay=False):
        self.login()
        self.setRoles('Manager')
        self.portal.invokeFactory('Event', id='event')
        event = self.portal['event']
        event.setStartDate(start)
        event.setEndDate(end)
        event.setUseEndDate(useEndDate)
        event.setWholeDay(wholeDay)
        return event

    def testIsSameDay(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.isSameDay(event), True)

    def testIsSameDayFailing(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00')
        self.assertEqual(event_util.isSameDay(event), False)

    def testIsSameDayWithoutEndDate(self):
        # events with useEndDate==False are always same-day events
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          useEndDate=False)
        self.assertEqual(event_util.isSameDay(event), True)

    def testIsSameDayWithoutEndDateFailing(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
                          useEndDate=False)
        self.assertEqual(event_util.isSameDay(event), True)

    def testToDisplayWithTime(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.toDisplay(event), 
                {'start_date': '2000/10/12 06:00:00',
                 'end_date' : '2000/10/12 18:00:00',
                 'same_day' : True,
                })

    def testToDisplayWholeDaySameDay(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,
                 'end_date' : None,
                 'end_time' : None,  
                 'same_day' : True,
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
                })

    def testToDisplayWithoutEndDateDifferentDates(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
                          useEndDate=False,
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start_date': '2000/10/12',
                 'start_time': None, 
                 'end_date' : None,
                 'end_time': None, 
                 'same_day' : True,
                })

    def testToDisplayWithoutEndDateStartAndEndDateEqual(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          useEndDate=False,
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,  
                 'end_date' : None,
                 'end_time' : None,
                 'same_day' : True,
                })


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventUtilsTests))
    return suite


