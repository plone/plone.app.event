import unittest
from DateTime import DateTime

from plone.app.event import event_util
from plone.app.event.event import ATEvent as Event
from Products.CMFPlone.tests import PloneTestCase


class EventUtilsTests(PloneTestCase):

    def testIsSameDay(self):

        event = Event('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.isSameDay(event), True)

        event = Event('2000/10/12 06:00:00', '2000/10/13 18:00:00')
        self.assertEqual(event_util.isSameDay(event), False)

    def testIsSameDayWithoutEndDate(self):

        # events with useEndDate==False are always same-day events
        event = Event('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          useEndDate=False)
        self.assertEqual(event_util.isSameDay(event), True)

        event = Event('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
                          useEndDate=False)
        self.assertEqual(event_util.isSameDay(event), True)

    def testToDisplayWithTime(self):
        event = Event('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12 06:00:00',
                 'end' : '2000/10/12 18:00:00',
                 'same_day' : True,
                })

    def testToDisplayWholeDaySameDay(self):
        event = Event('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12',
                 'end' : None,
                 'same_day' : True,
                })
                          
    def testToDisplayWholeDayDifferentDays(self):
        event = Event('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12',
                 'end' : '2000/10/13',
                 'same_day' : False,
                })

    def testToDisplayWithoutEndDateDifferentDates(self):
        event = Event('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
                          useEndDate=False,
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12',
                 'end' : None,
                 'same_day' : True,
                })

    def testToDisplayWithoutEndDateStartAndEndDateEqual(self):
        event = Event('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          useEndDate=False,
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12',
                 'end' : None,
                 'same_day' : True,
                })

#class ToDisplayPloneTests(PloneTestCase):
#
#    def testSimple(self):
#        pass
#

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EventUtilsTests))
#    suite.addTest(unittest.makeSuite(ToDisplayPloneTests))
    return suite


