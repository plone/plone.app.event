from OFS.SimpleItem import SimpleItem
from plone.app.event.at.interfaces import IATEvent
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.interfaces import IEventSettings
from plone.app.event.recurrence import Occurrence
from plone.app.event.recurrence import OccurrenceTraverser
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.event.utils import pydt
from plone.event.utils import tzdel
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from zope.publisher.interfaces.browser import IBrowserView

import datetime
import pytz
import transaction
import unittest2 as unittest
import zope.component


TZNAME = "Europe/Vienna"


class TestTraversal(unittest.TestCase):

    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = "Australia/Brisbane"

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(type_name='Event', id='at',
                                  title='Event1')
        self.at = self.portal['at']
        self.at_traverser = OccurrenceTraverser(self.at, self.layer['request'])

    def test_no_occurrence(self):
        self.assertRaises(
            AttributeError,
            self.at_traverser.publishTraverse,
            self.layer['request'], 'foo')

    def test_default_views(self):
        view = self.at_traverser.publishTraverse(
            self.layer['request'], 'event_view')
        self.assertTrue(IBrowserView.providedBy(view))

    def test_occurrence(self):
        self.at.setRecurrence('RRULE:FREQ=WEEKLY;COUNT=10')

        # does not match occurrence date
        qdate = datetime.date.today() + datetime.timedelta(days=4)
        self.assertRaises(
            AttributeError,
            self.at_traverser.publishTraverse,
            self.layer['request'], str(qdate))

        qdatedt = pydt(self.at.start() + 7)
        item = self.at_traverser.publishTraverse(self.layer['request'],
                                                 str(qdatedt.date()))
        self.assertTrue(IOccurrence.providedBy(item))
        self.assertTrue(IATEvent.providedBy(item.aq_parent))

    def test_occurrence_accessor(self):
        start = datetime.datetime.today()
        end = datetime.datetime.today()
        occ = Occurrence('ignored', start, end)
        occ = occ.__of__(self.portal['at'])
        data = IEventAccessor(occ)
        self.assertNotEqual(data.start,
                            tzdel(self.portal['at'].start_date))
        self.assertEqual(start, data.start)
        self.assertEqual(data.url, 'http://nohost/plone/at/ignored')


class TestTraversalBrowser(TestTraversal):

    def test_traverse_occurrence(self):
        self.at.setRecurrence('RRULE:FREQ=WEEKLY;COUNT=10')
        transaction.commit()

        qdatedt = pydt(self.at.start() + 7)
        url = '/'.join([self.portal['at'].absolute_url(),
                        str(qdatedt.date())])

        browser = Browser(self.layer['app'])
        browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_ID, TEST_USER_PASSWORD))
        browser.open(url)
        self.assertTrue(
            self.portal['at'].title.encode('ascii') in browser.contents)


class TestOccurrences(unittest.TestCase):

    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = TZNAME

        now = localized_now()

        yesterday = now - datetime.timedelta(days=1)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(
            'Event',
            'daily',
            title=u'Daily Event',
            start=now,
            end=now + datetime.timedelta(hours=1),
            location=u'Vienna',
            recurrence='RRULE:FREQ=DAILY;COUNT=4',
            timezone=TZNAME)

        self.portal.invokeFactory(
            'Event',
            'interval',
            title=u'Interval Event',
            start=yesterday,
            end=yesterday + datetime.timedelta(hours=1),
            location=u'Halle',
            recurrence='RRULE:FREQ=DAILY;INTERVAL=2;COUNT=5',
            timezone=TZNAME)

        self.now = now
        self.yesterday = yesterday
        self.daily = self.portal['daily']
        self.interval = self.portal['interval']

    def test_get_occurrences(self):
        res = get_events(self.portal, ret_mode=3, expand=True)
        self.assertTrue(len(res) == 9)

        res = get_events(self.portal, start=self.now, ret_mode=3, expand=True)
        self.assertTrue(len(res) == 9)

        res = get_events(self.portal, ret_mode=3, expand=True, limit=5)
        self.assertTrue(len(res) == 5)
        self.assertTrue(IEventAccessor.providedBy(res[0]))

    def test_eventview_occurrences(self):
        self.portal.invokeFactory(
            'Event',
            'many',
            title=u'Interval Event',
            location=u'Brisbane',
            recurrence='RRULE:FREQ=DAILY;COUNT=1000')

        view = zope.component.getMultiAdapter(
            (self.portal['interval'], self.request), name='event_view')
        result = view.next_occurrences
        # altogether 5 occurrences, but start occurrence is not included
        self.assertEqual(4, len(result['events']))
        self.assertFalse(result['events'][-1] == result['tail'])

        view = zope.component.getMultiAdapter(
            (self.portal['many'], self.request), name='event_view')
        result = view.next_occurrences
        self.assertEqual(7, len(result['events']))
        self.assertFalse(result['events'][-1] == result['tail'])


class MockEvent(SimpleItem):
    """ Mock event"""


class TestRecurrenceSupport(unittest.TestCase):

    layer = PAEvent_INTEGRATION_TESTING

    def test_recurrence(self):
        tz = pytz.timezone('Europe/Vienna')
        duration = datetime.timedelta(days=4)
        data = MockEvent()
        data.start = datetime.datetime(2011, 11, 11, 11, 00, tzinfo=tz)
        data.end = data.start + duration
        data.recurrence = 'RRULE:FREQ=DAILY;COUNT=4'
        zope.interface.alsoProvides(data, IEvent, IEventRecurrence)
        result = IRecurrenceSupport(data).occurrences()

        self.assertEqual(4, len(result))

        # First occurrence is an IEvent object
        self.assertTrue(IEvent.providedBy(result[0]))

        # Subsequent ones are IOccurrence objects
        self.assertTrue(IOccurrence.providedBy(result[1]))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
