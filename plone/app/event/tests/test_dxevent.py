import pytz
import unittest2 as unittest
import zope.interface
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from datetime import datetime, timedelta
from plone.app.event.testing import set_env_timezone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.interfaces import IEvent, IRecurrenceSupport, IOccurrence
from plone.event.interfaces import IEventAccessor
from zope.component import createObject
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from plone.app.event.base import get_portal_events
from plone.app.event.base import localized_now
from plone.app.event.dx.behaviors import (
    default_start,
    default_end,
    default_tz,
    StartBeforeEnd,
    IEventBasic,
    IEventRecurrence,
    IEventLocation,
    IEventAttendees,
    IEventContact
)
from plone.app.event.dx.interfaces import (
    IDXEvent,
    IDXEventRecurrence,
    IDXEventLocation,
    IDXEventAttendees,
    IDXEventContact
)
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING


TZNAME = "Europe/Vienna"


class MockEvent(SimpleItem):
    """ Mock event"""

class TestDXIntegration(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

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

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='plone.app.event.dx.event')
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='plone.app.event.dx.event')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IDXEvent.providedBy(new_object))
        self.failUnless(IDXEventRecurrence.providedBy(new_object))
        self.failUnless(IDXEventLocation.providedBy(new_object))
        self.failUnless(IDXEventAttendees.providedBy(new_object))
        self.failUnless(IDXEventContact.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime(2011,11,11,11,00),
                end=datetime(2011,11,11,12,00),
                timezone=TZNAME,
                whole_day=False)
        e1 = self.portal['event1']
        self.failUnless(IDXEvent.providedBy(e1))
        self.failUnless(IDXEventRecurrence.providedBy(e1))
        self.failUnless(IDXEventLocation.providedBy(e1))
        self.failUnless(IDXEventAttendees.providedBy(e1))
        self.failUnless(IDXEventContact.providedBy(e1))

    def test_view(self):
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime(2011,11,11,11,00),
                end=datetime(2011,11,11,12,00),
                timezone=TZNAME,
                whole_day=False)
        e1 = self.portal['event1']
        view = e1.restrictedTraverse('@@event_view')
        self.assertTrue(view.formated_date(e1) is not None)
        self.assertTrue(view.next_occurrences is not None)


    def test_start_end_dates_indexed(self):
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime(2011,11,11,11,00),
                end=datetime(2011,11,11,12,00),
                timezone=TZNAME,
                whole_day=False)
        e1 = self.portal['event1']
        e1.reindexObject()

        result = self.portal.portal_catalog(path='/'.join(e1.getPhysicalPath()))
        self.assertEquals(1, len(result))
        # result returns Zope's DateTime
        self.assertEquals(result[0].start,
                DateTime('2011/11/11 11:00:00 %s' % TZNAME))
        self.assertEquals(result[0].end,
                DateTime('2011/11/11 12:00:00 %s' % TZNAME))


    def test_data_postprocessing(self):
        # Addressing bug #62
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime(2012,10,19,0,30),
                end=datetime(2012,10,19,1,30),
                timezone="Europe/Vienna",
                whole_day=False)
        e1 = self.portal['event1']
        e1.reindexObject()

        # Prepare reference objects
        tzname_1 = "Europe/Vienna"
        tz_1 = pytz.timezone(tzname_1)
        dt_1 = tz_1.localize(datetime(2012,10,19,0,30))
        dt_1_1 = tz_1.localize(datetime(2012,10,19,0,0))
        dt_1_2 = tz_1.localize(datetime(2012,10,19,23,59,59))

        tzname_2 = "Hongkong"
        tz_2 = pytz.timezone(tzname_2)
        dt_2 = tz_2.localize(datetime(2012,10,19,0,30))
        dt_2_1 = tz_2.localize(datetime(2012,10,19,0,0))
        dt_2_2 = tz_2.localize(datetime(2012,10,19,23,59,59))

        # See, if start isn't moved by timezone offset. Addressing issue #62
        self.assertTrue(IEventBasic(e1).start == dt_1)
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_1)

        # After timezone changes, only the timezone should be applied, but the
        # date and time values not converted.
        IEventAccessor(e1).timezone = tzname_2
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_2)

        # Likewise with whole_day events. If values were converted, the days
        # would drift apart.
        IEventAccessor(e1).whole_day = True
        IEventAccessor(e1).timezone = tzname_1
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_1_1)
        self.assertTrue(IEventBasic(e1).end == dt_1_2)

        IEventAccessor(e1).timezone = tzname_2
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_2_1)
        self.assertTrue(IEventBasic(e1).end == dt_2_2)


    def test_recurrence_indexing(self):
        utc = pytz.utc
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime(2011,11,11,11,0, tzinfo=utc),
                end=datetime(2011,11,11,12,0, tzinfo=utc),
                timezone='UTC',
                whole_day=False)
        e1 = self.portal['event1']
        e1rec = IEventRecurrence(e1)
        e1rec.recurrence = 'RRULE:FREQ=DAILY;COUNT=4'
        e1.reindexObject()

        # test, if the recurrence attribute is available on the context.
        # DRI needs that for indexing.
        self.assertTrue(e1.recurrence == e1rec.recurrence)

        # test, if the occurrences are indexed by DRI
        result = get_portal_events(
                e1,
                range_start=datetime(2011,11,12,11,0, tzinfo=utc))
        self.assertTrue(len(result)==1)


    def test_event_accessor(self):
        utc = pytz.utc
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime(2011,11,11,11,0, tzinfo=utc),
                end=datetime(2011,11,11,12,0, tzinfo=utc),
                timezone='UTC',
                whole_day=False)
        e1 = self.portal['event1']

        # setting attributes via the accessor
        acc = IEventAccessor(e1)
        acc.end = datetime(2011,11,13,10,0)
        acc.timezone = TZNAME

        tz = pytz.timezone(TZNAME)

        # accessor should return end datetime in the event's timezone
        self.assertTrue(acc.end == datetime(2011,11,13,11,0, tzinfo=tz))

        # the behavior's end datetime is stored in utc on the content object
        self.assertTrue(e1.end == datetime(2011,11,13,10,0, tzinfo=utc))

        # accessing the end property via the behavior adapter, returns the
        # value converted to the event's timezone
        self.assertTrue(IEventBasic(e1).end ==
                datetime(2011,11,13,11,0, tzinfo=tz))

        # timezone should be the same on the event object and accessor
        self.assertTrue(e1.timezone == acc.timezone)



class TestDXEventRecurrence(unittest.TestCase):

    layer = PAEventDX_INTEGRATION_TESTING

    def test_recurrence(self):
        tz = pytz.timezone('Europe/Vienna')
        duration = timedelta(days=4)
        data = MockEvent()
        data.start = datetime(2011, 11, 11, 11, 00, tzinfo=tz)
        data.end = data.start + duration
        data.recurrence = 'RRULE:FREQ=DAILY;COUNT=4'
        zope.interface.alsoProvides(
            data, IEvent, IEventBasic, IEventRecurrence,
            IDXEvent, IDXEventRecurrence)
        result = IRecurrenceSupport(data).occurrences()
        self.assertEqual(4, len(result))

        # First occurrence is an IEvent object
        self.assertTrue(IEvent.providedBy(result[0]))

        # Subsequent ones are IOccurrence objects
        self.assertTrue(IOccurrence.providedBy(result[1]))


class TestDXEventUnittest(unittest.TestCase):
    """ Unit test for Dexterity event behaviors.
    """

    def setUp(self):
        set_env_timezone(TZNAME)

    def test_validate_invariants_ok(self):
        data = MockEvent()
        data.start = datetime(2009, 1, 1)
        data.end = datetime(2009, 1, 2)

        try:
            IEventBasic.validateInvariants(data)
        except:
            self.fail()

    def test_validate_invariants_fail(self):
        data = MockEvent()
        data.start = datetime(2009, 1, 2)
        data.end = datetime(2009, 1, 1)

        try:
            IEventBasic.validateInvariants(data)
            self.fail()
        except StartBeforeEnd:
            pass

    def test_validate_invariants_edge(self):
        data = MockEvent()
        data.start = datetime(2009, 1, 2)
        data.end = datetime(2009, 1, 2)

        try:
            IEventBasic.validateInvariants(data)
        except:
            self.fail()

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
