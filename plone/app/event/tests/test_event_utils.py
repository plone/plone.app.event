import unittest
from DateTime import DateTime

from plone.app.event import event_util
from Products.CMFPlone.tests import PloneTestCase

class MockEvent(object):

    def __init__(self, start, end, wholeDay=False, useEndDate=True):

        self._start = DateTime(start)
        self._end = DateTime(end)
        self._wholeDay = wholeDay
        self._useEndDate = useEndDate

    def start(self):
        return self._start

    def end(self):
        return self._end

    def getWholeDay(self):
        return self._wholeDay

    def useEndDate(self):
        return self._useEndDate


class EventUtilsTests(unittest.TestCase):

    def testIsSameDay(self):

        event = MockEvent('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.isSameDay(event), True)

        event = MockEvent('2000/10/12 06:00:00', '2000/10/13 18:00:00')
        self.assertEqual(event_util.isSameDay(event), False)

    def testIsSameDayWithoutEndDate(self):

        # events with useEndDate==False are always same-day events
        event = MockEvent('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          useEndDate=False)
        self.assertEqual(event_util.isSameDay(event), True)

        event = MockEvent('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
                          useEndDate=False)
        self.assertEqual(event_util.isSameDay(event), True)

    def testToDisplayWithTime(self):
        event = MockEvent('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12 06:00:00',
                 'end' : '2000/10/12 18:00:00',
                 'same_day' : True,
                })

    def testToDisplayWholeDaySameDay(self):
        event = MockEvent('2000/10/12 06:00:00', '2000/10/12 18:00:00', 
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12',
                 'end' : None,
                 'same_day' : True,
                })
                          
    def testToDisplayWholeDayDifferentDays(self):
        event = MockEvent('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
                          wholeDay=True)
        self.assertEqual(event_util.toDisplay(event), 
                {'start': '2000/10/12',
                 'end' : '2000/10/13',
                 'same_day' : False,
                })

    def testToDisplayWithoutEndDate(self):
        event = MockEvent('2000/10/12 06:00:00', '2000/10/13 18:00:00', 
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


