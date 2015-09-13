from OFS.SimpleItem import SimpleItem
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.base import get_events
from plone.app.event.dx.traverser import OccurrenceTraverser
from plone.app.event.recurrence import Occurrence
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import set_browserlayer
from plone.app.event.testing import set_env_timezone
from plone.app.event.testing import set_timezone
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now
from plone.app.testing import TEST_USER_ID, TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.testing.z2 import Browser
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserView
from mock import Mock

import datetime
import pytz
import transaction
import unittest
import zope.component


TZNAME = "Europe/Vienna"


class TestTraversalDX(AbstractSampleDataEvents):
    """Test OccurrenceTraverser with DX objects.
    """
    layer = PAEventDX_FUNCTIONAL_TESTING

    @property
    def occ_traverser_1(self):
        return OccurrenceTraverser(self.now_event, self.request)

    def test_no_occurrence(self):
        self.assertRaises(
            AttributeError,
            self.occ_traverser_1.publishTraverse,
            self.request,
            'foo'
        )

    def test_default_views(self):
        view = self.occ_traverser_1.publishTraverse(self.request, 'event_view')
        self.assertTrue(IBrowserView.providedBy(view))

    def test_occurrence(self):
        # start date of self.now_event = 2013-05-05, 10:00.
        # recurrence rule = 'RRULE:FREQ=DAILY;COUNT=3;INTERVAL=2'

        # Try to traverse to inexistent occurrence
        self.assertRaises(
            AttributeError,
            self.occ_traverser_1.publishTraverse,
            self.request, '2000-01-01')

        # Traverse to existent occurrence
        item = self.occ_traverser_1.publishTraverse(self.request, '2013-05-07')
        self.assertTrue(IOccurrence.providedBy(item))
        self.assertEqual(type(self.now_event), type(item.aq_parent))

        # Test attributes of Occurrence
        self.assertEqual(item.portal_type, 'Occurrence')
        self.assertEqual(item.id, '2013-05-07')
        delta = datetime.timedelta(days=2)
        self.assertEqual(item.start, self.now + delta)
        self.assertEqual(item.end, self.now + delta + self.duration)

    def test_occurrence_accessor(self):
        start = self.now
        end = self.future
        occ = Occurrence('ignored', start, end)
        occ = occ.__of__(self.now_event)
        acc_occ = IEventAccessor(occ)
        acc_ctx = IEventAccessor(self.now_event)
        self.assertEqual(acc_occ.start, acc_ctx.start)
        self.assertEqual(acc_occ.url, 'http://nohost/plone/now/ignored')

    def test_traverse_occurrence(self):
        transaction.commit()
        browser = Browser(self.app)
        browser.addHeader(
            'Authorization', 'Basic %s:%s' % (TEST_USER_ID, TEST_USER_PASSWORD)
        )
        url = '/'.join([self.now_event.absolute_url(), '2013-05-07'])
        browser.open(url)
        title = self.now_event.title.encode('ascii')
        self.assertTrue(title in browser.contents)

    def test_traverse_occurrence_imagescaling(self):
        self.now_event.image = Mock()
        occurrence = self.occ_traverser_1.publishTraverse(
            self.request, '2013-05-07'
        )
        image_view = occurrence.restrictedTraverse('@@images')
        self.assertEqual(image_view.context, self.now_event)


class TestOccurrences(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        set_browserlayer(self.request)
        set_env_timezone(TZNAME)
        set_timezone(TZNAME)

        now = patched_now()

        yesterday = now - datetime.timedelta(days=1)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.daily = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            id='daily',
            title=u'Daily Event',
            start=now,
            end=now + datetime.timedelta(hours=1),
            location=u'Vienna',
            recurrence='RRULE:FREQ=DAILY;COUNT=4',
        )
        self.interval = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            id='interval',
            title=u'Interval Event',
            start=yesterday,
            end=yesterday + datetime.timedelta(hours=1),
            location=u'Halle',
            recurrence='RRULE:FREQ=DAILY;INTERVAL=2;COUNT=5',
        )

        self.now = now
        self.yesterday = yesterday

    def test_get_occurrences(self):
        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS,
                         expand=True)
        self.assertEqual(len(res), 9)
        res = get_events(self.portal, start=self.now,
                         ret_mode=RET_MODE_ACCESSORS, expand=True)
        self.assertEqual(len(res), 8)

        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS,
                         expand=True, limit=5)
        self.assertEqual(len(res), 5)
        self.assertTrue(IEventAccessor.providedBy(res[0]))

    def test_event_summary_occurrences(self):
        createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            id='many',
            title=u'Interval Event',
            location=u'Brisbane',
            recurrence='RRULE:FREQ=DAILY;COUNT=1000'
        )

        view = zope.component.getMultiAdapter(
            (self.portal['interval'], self.request), name='event_summary')
        result = view.next_occurrences
        # altogether 5 occurrences, start occurrence is included
        self.assertEqual(5, len(result))

        view = zope.component.getMultiAdapter(
            (self.portal['many'], self.request), name='event_summary')

        # Number of shown occurrences should match max_occurrences setting
        self.assertEqual(len(view.next_occurrences), view.max_occurrences)
        # num_more_occurrences should return number of remaining occurrences
        self.assertEqual(
            view.num_more_occurrences, 1000 - view.max_occurrences)


class MockEvent(SimpleItem):
    """Mock event"""


class TestRecurrenceSupport(unittest.TestCase):

    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.tz = tz = pytz.timezone('Europe/Vienna')
        duration = datetime.timedelta(days=4)
        data = MockEvent()
        data.start = datetime.datetime(2011, 11, 11, 11, 00, tzinfo=tz)
        data.end = data.start + duration
        data.recurrence = 'RRULE:FREQ=DAILY;COUNT=4'
        alsoProvides(data, IEvent, IEventRecurrence)
        self.data = data

    def test_recurrence_occurrences(self):
        result = IRecurrenceSupport(self.data).occurrences()
        result = list(result)  # cast generator to list

        self.assertEqual(4, len(result))

        # First occurrence is an IEvent object
        self.assertTrue(IEvent.providedBy(result[0]))

        # Subsequent ones are IOccurrence objects
        self.assertTrue(IOccurrence.providedBy(result[1]))

    def test_recurrence_occurrences_with_range_start_1(self):
        # Test with range
        rs = datetime.datetime(2011, 11, 15, 11, 0, tzinfo=self.tz)
        result = IRecurrenceSupport(self.data).occurrences(range_start=rs)
        result = list(result)  # cast generator to list

        self.assertEqual(4, len(result))

        # First occurrence is an IEvent object
        self.assertTrue(IEvent.providedBy(result[0]))

        # Subsequent ones are IOccurrence objects
        self.assertTrue(IOccurrence.providedBy(result[1]))

    def test_recurrence_occurrences_with_range_start_2(self):
        # Test with range
        rs = datetime.datetime(2011, 11, 16, 11, 0, tzinfo=self.tz)
        result = IRecurrenceSupport(self.data).occurrences(range_start=rs)
        result = list(result)  # cast generator to list

        self.assertEqual(3, len(result))

        # Only IOccurrence objects in the result set
        self.assertTrue(IOccurrence.providedBy(result[0]))

    def test_recurrence_occurrences_with_range_start_and_end(self):
        # Test with range
        rs = datetime.datetime(2011, 11, 11, 11, 0, tzinfo=self.tz)
        re = datetime.datetime(2011, 11, 12, 11, 0, tzinfo=self.tz)
        result = IRecurrenceSupport(self.data).occurrences(range_start=rs,
                                                           range_end=re)
        result = list(result)  # cast generator to list

        self.assertEqual(2, len(result))

        # First occurrence is an IEvent object
        self.assertTrue(IEvent.providedBy(result[0]))

        # Subsequent ones are IOccurrence objects
        self.assertTrue(IOccurrence.providedBy(result[1]))
