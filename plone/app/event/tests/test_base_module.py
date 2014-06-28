from DateTime import DateTime
from plone.app.event import base
from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.base import AnnotationAdapter
from plone.app.event.base import DEFAULT_END_DELTA
from plone.app.event.base import DT
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import construct_calendar
from plone.app.event.base import dates_for_display
from plone.app.event.base import default_end
from plone.app.event.base import default_start
from plone.app.event.base import default_timezone
from plone.app.event.base import find_context
from plone.app.event.base import find_event_listing
from plone.app.event.base import find_ploneroot
from plone.app.event.base import find_site
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import TEST_TIMEZONE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.utils import pydt
from zope.annotation.interfaces import IAnnotations
from zope.component.interfaces import ISite
from zope.interface import directlyProvides

import datetime
import pytz
import unittest2 as unittest


class TestBaseModule(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def assertEqualDatetime(self, date1, date2, msg=None):
        """ Compare two datetime instances to a resolution of minutes.
        """
        format_ = '%Y-%m-%d %H:%M %Z'
        self.assertEqual(date1.strftime(format_), date2.strftime(format_), msg)

    def test_default_end(self):
        self.assertEqualDatetime(
            default_end() - datetime.timedelta(hours=DEFAULT_END_DELTA),
            default_start())

    def test_default_start(self):
        now = localized_now().replace(minute=0, second=0, microsecond=0)
        self.assertEqualDatetime(default_start(), now)

    def test_DT(self):
        # Python datetime with valid zone. Zope converts it to GMT+1...
        # TODO: DateTime better shouldn't do this!
        cet = pytz.timezone('CET')
        self.assertEqual(
            DT(datetime.datetime(2011, 11, 11, 11, 0, 0, tzinfo=cet)),
            DateTime('2011/11/11 11:00:00 GMT+1')
        )

        # Python dates get converted to a DateTime with timecomponent including
        # a timezone
        self.assertEqual(
            DT(datetime.date(2011, 11, 11)),
            DateTime('2011/11/11 00:00:00 UTC')
        )

        # DateTime with valid zone
        self.assertEqual(
            DT(DateTime(2011, 11, 11, 11, 0, 0, 'Europe/Vienna')),
            DateTime('2011/11/11 11:00:00 Europe/Vienna')
        )

        # Zope DateTime with valid DateTime zone but invalid pytz is kept as is
        self.assertEqual(
            DT(DateTime(2011, 11, 11, 11, 0, 0, 'GMT+1')),
            DateTime('2011/11/11 11:00:00 GMT+1')
        )

        # Invalid datetime zones are converted to the portal timezone
        # Testing with no timezone
        self.assertEqual(
            DT(datetime.datetime(2011, 11, 11, 11, 0, 0)),
            DateTime('2011/11/11 11:00:00 UTC')
        )

        # Conversion from string
        self.assertEqual(
            DT('2011/11/11 11:00:00 Europe/Vienna'),
            DateTime('2011/11/11 11:00:00 Europe/Vienna')
        )

        ## TEST WITH/WITHOUT MICROSECONDS

        # From Python datetime

        tz = pytz.timezone('Europe/Vienna')

        # exact=False
        self.assertEqual(
            DT(datetime.datetime(2012, 12, 12, 10, 10, 10, 123456,
               tzinfo=tz), exact=False),
            DateTime('2012/12/12 10:10:10 Europe/Vienna')
        )

        # exact=True
        self.assertEqual(
            DT(datetime.datetime(2012, 12, 12, 10, 10, 10, 123456,
               tzinfo=tz), exact=True),
            DateTime('2012/12/12 10:10:10.123456 Europe/Vienna')
        )

        # From Zope DateTime

        # Exact=False
        self.assertEqual(
            DT(DateTime(2012, 12, 12, 10, 10, 10.123456, 'Europe/Vienna'),
               exact=False),
            DateTime('2012/12/12 10:10:10 Europe/Vienna')
        )

        # Exact=True
        self.assertEqual(
            DT(DateTime(2012, 12, 12, 10, 10, 10.123456, 'Europe/Vienna'),
               exact=True),
            DateTime('2012/12/12 10:10:10.123456 Europe/Vienna')
        )

    def test_wkday_to_mon1(self):
        from plone.app.event.base import wkday_to_mon1
        li = [wkday_to_mon1(day) for day in range(0, 7)]
        self.assertEqual(li, [1, 2, 3, 4, 5, 6, 0])

    def test_wkday_to_mon0(self):
        from plone.app.event.base import wkday_to_mon0
        li = [wkday_to_mon0(day) for day in range(0, 7)]
        self.assertEqual(li, [6, 0, 1, 2, 3, 4, 5])

    def test__default_timezone(self):
        """Test, if default_timezone returns something other than None if
        called with and without a context.
        """
        self.assertTrue(default_timezone() is not None)
        self.assertTrue(default_timezone(context=self.portal) is not None)

    def test__dt_start_of_day(self):
        from plone.app.event.base import dt_start_of_day
        self.assertEqual(
            dt_start_of_day(datetime.datetime(2013, 2, 1, 18, 35)),
            datetime.datetime(2013, 2, 1, 0, 0, 0, 0)
        )
        self.assertEqual(
            dt_start_of_day(datetime.date(2013, 2, 1)),
            datetime.datetime(2013, 2, 1, 0, 0, 0, 0)
        )

    def test__dt_end_of_day(self):
        from plone.app.event.base import dt_end_of_day
        self.assertEqual(
            dt_end_of_day(datetime.datetime(2013, 2, 1, 18, 35)),
            datetime.datetime(2013, 2, 1, 23, 59, 59, 0)
        )
        self.assertEqual(
            dt_end_of_day(datetime.date(2013, 2, 1)),
            datetime.datetime(2013, 2, 1, 23, 59, 59, 0)
        )

    def test__start_end_from_mode(self):
        from plone.app.event.base import start_end_from_mode
        from plone.app.event.base import dt_end_of_day

        # ALL
        #
        start, end = start_end_from_mode('all')
        self.assertTrue(start is None and end is None)

        # PAST
        #
        start, end = start_end_from_mode('past')
        self.assertTrue(start is None and isinstance(end, datetime.datetime))

        # FUTURE
        #
        start, end = start_end_from_mode('future')
        self.assertTrue(isinstance(start, datetime.datetime) and end is None)

        # NOW
        #
        start, end = start_end_from_mode('now')
        self.assertTrue(
            isinstance(start, datetime.datetime) and
            isinstance(end, datetime.datetime) and
            end.hour == 23 and end.minute == 59 and end.second == 59
        )

        # 7DAYS
        #
        start, end = start_end_from_mode('7days')
        self.assertTrue(
            isinstance(start, datetime.datetime) and
            isinstance(end, datetime.datetime) and
            end == dt_end_of_day(start + datetime.timedelta(days=6))
        )

        # TODAY
        #
        start, end = start_end_from_mode('today')
        self.assertTrue(
            isinstance(start, datetime.datetime) and
            isinstance(end, datetime.datetime) and
            start.hour == 0 and start.minute == 0 and start.second == 0 and
            end.hour == 23 and end.minute == 59 and end.second == 59 and
            (start, end) == start_end_from_mode('day')
        )

        # DAY
        #
        day = datetime.datetime(2013, 2, 1, 18, 22)
        start, end = start_end_from_mode('day', day)
        self.assertTrue(
            start.date() == day.date() == end.date() and
            start.hour == 0 and start.minute == 0 and start.second == 0 and
            end.hour == 23 and end.minute == 59 and end.second == 59
        )

        # test with date-only
        day = datetime.datetime(2013, 2, 1)
        start, end = start_end_from_mode('day', day)
        self.assertTrue(
            start.date() == day.date() == end.date() and
            start.hour == 0 and start.minute == 0 and start.second == 0 and
            end.hour == 23 and end.minute == 59 and end.second == 59
        )

        # WEEK
        #
        def ret_0():
            return 0  # Monday

        def ret_1():
            return 1  # Tuesday

        def ret_6():
            return 6  # Sunday

        # prepare patched first_weekday
        orig_first_weekday = base.first_weekday

        base.first_weekday = ret_0
        day = datetime.datetime(2013, 2, 2)
        start, end = start_end_from_mode('week', day)
        self.assertTrue(
            start.isoformat() == '2013-01-28T00:00:00' and
            end.isoformat() == '2013-02-03T23:59:59'
        )

        base.first_weekday = ret_1
        day = datetime.datetime(2013, 2, 2)
        start, end = start_end_from_mode('week', day)
        self.assertTrue(
            start.isoformat() == '2013-01-29T00:00:00' and
            end.isoformat() == '2013-02-04T23:59:59'
        )

        base.first_weekday = ret_6
        day = datetime.datetime(2013, 2, 1)
        start, end = start_end_from_mode('week', day)
        self.assertTrue(
            start.isoformat() == '2013-01-27T00:00:00' and
            end.isoformat() == '2013-02-02T23:59:59'
        )

        base.first_weekday = orig_first_weekday  # restore orig first_weekday

        # MONTH
        #
        start, end = start_end_from_mode('month')
        self.assertTrue(start < end and start.day == 1)

        day = datetime.datetime(2013, 2, 7)
        start, end = start_end_from_mode('month', day)
        self.assertTrue(
            start.year == 2013 and start.month == 2 and start.day == 1 and
            start.hour == 0 and start.minute == 0 and start.second == 0 and
            end.year == 2013 and end.month == 2 and end.day == 28 and
            end.hour == 23 and end.minute == 59 and end.second == 59
        )


class TestAnnotationAdapter(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_annotation_adapter(self):
        # Normally called via adapter lookup from it's interface. but for
        # testing, we don't register the adapter, but use it directlyProvides
        an = AnnotationAdapter(self.portal)

        # ANNOTATION_KEY of abstract class not set - an._data is None
        self.assertEqual(an._data, None)

        # ANNOTATION_KEY set, but no attribute set yet - an._data still None
        an.ANNOTATION_KEY = 'testing_annotation'
        an._data = IAnnotations(self.portal).get(an.ANNOTATION_KEY, None)

        # Test attribute access, an._data still None
        self.assertEqual(an.foo, None)
        self.assertEqual(an._data, None)

        # Test attribute set, an._data will set. First, Test with None, which
        # also should set the annotation on the context.
        # am._data will be set then.
        an.bar = None
        self.assertEqual(an.bar, None)
        self.assertTrue(an._data is not None)

        # Set with something else than None
        an.foo = '123'
        self.assertEqual(an.foo, '123')


class TestFindContext(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Folder', 'newsite')
        portal.newsite.invokeFactory('Folder', 'subfolder')
        portal.invokeFactory('Folder', 'subfolder2')
        portal.subfolder2.invokeFactory('Folder', 'subfolder3')

        directlyProvides(portal.newsite, ISite)
        self.assertTrue(ISite.providedBy(portal.newsite))

    def test_find_ploneroot(self):
        p1 = find_ploneroot(self.portal.newsite.subfolder)
        p2 = find_ploneroot(self.portal.subfolder2)
        self.assertEqual(p1, self.portal)
        self.assertEqual(p1, p2)

        self.assertEqual(
            find_ploneroot(self.portal.newsite.subfolder, as_url=True),
            'http://nohost/plone'
        )

    def test_find_site(self):
        self.assertEqual(
            find_site(self.portal.newsite.subfolder),
            self.portal.newsite
        )

        self.assertEqual(
            find_site(self.portal.newsite.subfolder, as_url=True),
            'http://nohost/plone/newsite'
        )

    def test_find_event_listing(self):
        self.portal.subfolder2.setLayout('event_listing')
        self.assertEqual(
            find_event_listing(self.portal.subfolder2.subfolder3),
            self.portal.subfolder2
        )
        self.assertEqual(
            find_event_listing(self.portal.subfolder2.subfolder3, as_url=True),
            'http://nohost/plone/subfolder2'
        )

        self.assertEqual(
            find_context(
                self.portal.subfolder2.subfolder3,
                viewname='foo',
                as_url=True,
                append_view=True),
            'http://nohost/plone/foo'
        )


class TestGetEventsDX(AbstractSampleDataEvents):
    """Test get_events with DX objects.
    """
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
        DXEventAccessor.portal_type = 'plone.app.event.dx.event'
        return DXEventAccessor.create

    def test_get_events(self):

        # whole range
        res = get_events(self.portal)
        self.assertEqual(len(res), 4)

        res = get_events(self.portal,
                         start=self.past,
                         end=self.future)
        self.assertEqual(len(res), 4)

        res = get_events(self.portal,
                         end=self.future)
        self.assertEqual(len(res), 4)

        res = get_events(self.portal,
                         start=self.past)
        self.assertEqual(len(res), 4)

        # Limit
        res = get_events(self.portal, limit=2)
        self.assertEqual(len(res), 2)

        # Return objects
        res = get_events(self.portal, ret_mode=RET_MODE_OBJECTS)
        self.assertTrue(IEvent.providedBy(res[0]))

        # Return IEventAccessor
        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS)
        self.assertTrue(IEventAccessor.providedBy(res[0]))
        # Test sorting
        self.assertTrue(res[0].start < res[-1].start)

        # Test reversed sorting
        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS,
                         sort_reverse=True)
        self.assertTrue(res[0].start > res[-1].start)

        # Test sort_on
        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS,
                         sort="start")
        self.assertEqual(
            [it.title for it in res][2:],
            [u'Now Event', u'Future Event']
        )
        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS, sort="end")
        self.assertEqual(
            [it.title for it in res],
            [u'Past Event', u'Now Event', u'Future Event', u'Long Event']
        )

        # Test expansion
        res = get_events(self.portal, ret_mode=RET_MODE_OBJECTS, expand=True)
        self.assertEqual(len(res), 8)

        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS, expand=True)
        self.assertEqual(len(res), 8)
        # Test sorting
        self.assertTrue(res[0].start < res[-1].start)

        res = get_events(self.portal, ret_mode=RET_MODE_ACCESSORS,
                         expand=True, sort_reverse=True)
        # Test sorting
        self.assertTrue(res[0].start > res[-1].start)

        # only on now-date
        res = get_events(self.portal,
                         start=self.now,
                         end=self.now)
        self.assertEqual(len(res), 2)

        # only on now-date as date
        # NOTE: converting self.now to python datetime to allow testing also
        # with dates as Zope DateTime objects.
        res = get_events(self.portal,
                         start=pydt(self.now).date(),
                         end=pydt(self.now).date())
        self.assertEqual(len(res), 2)

        # only on past date
        res = get_events(self.portal,
                         start=self.past,
                         end=self.past)
        self.assertEqual(len(res), 2)

        # one recurrence occurrence in far future
        res = get_events(self.portal,
                         start=self.far,
                         end=self.far)
        self.assertEqual(len(res), 1)

        # from now on
        res = get_events(self.portal,
                         start=self.now)
        self.assertEqual(len(res), 3)

        # until now
        res = get_events(self.portal,
                         end=self.now)
        self.assertEqual(len(res), 3)

        # in subfolder
        path = '/'.join(self.portal.sub.getPhysicalPath())
        res = get_events(self.portal, path=path)
        self.assertEqual(len(res), 1)

    def test_get_event_limit(self):
        """Test pull-request #93.
        The limit on the query has to be removed, because:

            - In the index, for each occurrence an index entry is created with
              reference to the originating event object (not an occurrence
              object - such doesn't exist).

            - The event object's start and end dates are the very first
              occurrence. Every other occurence is not stored anywhere but
              created on the fly from a recurrence rule.

            - Sorting on start sorts on the very first occurrence - this is
              where the problem originates.

        When doing a range search for events from now on and sorting for the
        start date, an event in the past might be sorted before tomorrow's
        event even if the next occurrence is somewhere in the future.

        Now, when limiting the result set with the catalog's sort_limit before
        expanding the recurrence to occurrences, tomorrow's event might fall
        out and the past event might be in. So limiting the result set can only
        be done after expanding the occurrences. Then we really have the
        correct order.
        """
        factory = self.event_factory()
        factory(
            container=self.portal,
            content_id='past_recur1',
            title=u'Past Event recurring 1',
            start=self.past,
            end=self.past + self.duration,
            location=u"Dornbirn",
            timezone=TEST_TIMEZONE,
            recurrence='RRULE:FREQ=WEEKLY;COUNT=4',
        )
        factory(
            container=self.portal,
            content_id='tomorrow',
            title=u'Tomorrow event',
            start=self.tomorrow,
            end=self.tomorrow + self.duration,
            open_end=True,
            location=u"Dornbirn",
            timezone=TEST_TIMEZONE,
        )

        limit = get_events(self.portal, start=self.now, expand=True,
                           ret_mode=RET_MODE_ACCESSORS, limit=3)
        all_ = get_events(self.portal, start=self.now, expand=True,
                          ret_mode=RET_MODE_ACCESSORS)
        self.assertEqual([e.url for e in limit], [e.url for e in all_[:3]])

    def test_construct_calendar(self):
        res = get_events(self.portal, ret_mode=RET_MODE_OBJECTS, expand=True)
        cal = construct_calendar(res)  # keys are date-strings.

        def _num_events(values):
            num = 0
            for val in values:
                num += len(val)
            return num

        # The long_event occurs on every day in the resulting calendar data
        # structure.
        self.assertEqual(_num_events(cal.values()), 48)

        # Test with range
        #

        # Completly outside range and start, end given as datetime
        cal = construct_calendar(
            res,
            start=datetime.datetime(2000, 1, 1, 10, 0),
            end=datetime.datetime(2000, 1, 2, 10, 0)
        )
        self.assertEqual(_num_events(cal.values()), 0)

        # Within range
        cal = construct_calendar(
            res,
            start=datetime.date(2013, 5, 1),
            end=datetime.date(2013, 5, 31)
        )
        self.assertEqual(_num_events(cal.values()), 34)

        # invalid start
        def _invalid_start():
            return construct_calendar(
                res,
                start='invalid',
                end=datetime.datetime(2000, 1, 2, 10, 0)
            )

        self.assertRaises(AssertionError, _invalid_start)

        # invalid end
        def _invalid_end():
            return construct_calendar(
                res,
                start=datetime.datetime(2000, 1, 1, 10, 0),
                end='invalid'
            )
        self.assertRaises(AssertionError, _invalid_end)


class TestGetEventsATPydt(TestGetEventsDX):
    """Test get_events with AT objects and datetime based dates.
    """
    layer = PAEventAT_INTEGRATION_TESTING

    def event_factory(self):
        return ATEventAccessor.create


class TestGetEventsATZDT(TestGetEventsATPydt):
    """Test get_events with AT objects and Zope DateTime based dates.
    """
    layer = PAEventAT_INTEGRATION_TESTING

    def make_dates(self):
        def_tz = default_timezone()
        now = self.now = DateTime(2013, 5, 5, 10, 0, 0, def_tz)
        self.tomorrow = DateTime(2013, 5, 6, 10, 0, 0, def_tz)
        past = self.past = DateTime(2013, 4, 25, 10, 0, 0, def_tz)
        future = self.future = DateTime(2013, 5, 15, 10, 0, 0, def_tz)
        far = self.far = DateTime(2013, 6, 4, 10, 0, 0, def_tz)
        duration = self.duration = 0.1
        return (now, past, future, far, duration)


class TestGetEventsOptimizations(AbstractSampleDataEvents):
    """Test get_events performance optimizations

    Issue #114: The limit bug described above and in #92 and #93
    is actually a manifestation of a deeper sorting bug,
    that also affects unlimited and unexpanded get_events().
    """
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
        DXEventAccessor.portal_type = 'plone.app.event.dx.event'
        return DXEventAccessor.create

    def setUp(self):
        AbstractSampleDataEvents.setUp(self)

        # add extra events to the base setup
        factory = self.event_factory()
        factory(
            container=self.portal,
            content_id='past_recur',
            title=u'Past Recur',
            start=self.past + self.duration,
            end=self.past + self.duration + self.duration,
            location=u"Dornbirn",
            timezone=TEST_TIMEZONE,
            recurrence='RRULE:FREQ=WEEKLY;COUNT=4',
        )
        factory(
            container=self.portal,
            content_id='tomorrow',
            title=u'Tomorrow event',
            start=self.tomorrow,
            end=self.tomorrow + self.duration,
            open_end=True,
            location=u"Dornbirn",
            timezone=TEST_TIMEZONE,
        )
        self.occ = [
            (u'Past Event', '2013-04-25 00:00:00', '2013-04-25 23:59:59'),
            (u'Long Event', '2013-04-25 10:00:00', '2013-06-04 10:00:00'),
            (u'Past Recur', '2013-04-25 11:00:00', '2013-04-25 12:00:00'),
            (u'Past Event', '2013-04-26 00:00:00', '2013-04-26 23:59:59'),
            (u'Past Event', '2013-04-27 00:00:00', '2013-04-27 23:59:59'),
            (u'Past Recur', '2013-05-02 11:00:00', '2013-05-02 12:00:00'),
            (u'Now Event', '2013-05-05 10:00:00', '2013-05-05 11:00:00'),
            (u'Tomorrow event', '2013-05-06 10:00:00', '2013-05-06 23:59:59'),
            (u'Now Event', '2013-05-07 10:00:00', '2013-05-07 11:00:00'),
            (u'Now Event', '2013-05-09 10:00:00', '2013-05-09 11:00:00'),
            (u'Past Recur', '2013-05-09 11:00:00', '2013-05-09 12:00:00'),
            (u'Future Event', '2013-05-15 10:00:00', '2013-05-15 11:00:00'),
            (u'Past Recur', '2013-05-16 11:00:00', '2013-05-16 12:00:00')]

    def diff(self, list1, list2):
        c = set(list1).union(set(list2))
        d = set(list1).intersection(set(list2))
        return list(c - d)

    def fmt(self, seq):
        return [(x.title,
                 x.start.strftime('%Y-%m-%d %H:%M:%S'),
                 x.end.strftime('%Y-%m-%d %H:%M:%S'))
                for x in seq]

    ### expand=True: events

    def test_expand_all(self):
        # all occurrences, sorted by start
        res = self.fmt(get_events(self.portal, expand=True,
                                  ret_mode=RET_MODE_ACCESSORS))
        self.assertEqual(res, self.occ)

    def test_expand_all_limit(self):
        # limited occurrences
        res = self.fmt(get_events(self.portal, expand=True,
                                  limit=3,
                                  ret_mode=RET_MODE_ACCESSORS))
        expect = self.occ[:3]
        self.assertEqual(res, expect, self.diff(res, expect))

    def test_expand_start(self):
        # now+future occurrences
        res = self.fmt(get_events(self.portal, expand=True,
                                  start=self.now,
                                  ret_mode=RET_MODE_ACCESSORS))
        expect = self.occ[1:2] + self.occ[6:]  # includes ongoing long event
        self.assertEqual(res, expect, self.diff(res, expect))

    def test_expand_start_limit(self):
        # limited now+future occurrences
        res = self.fmt(get_events(self.portal, expand=True,
                                  start=self.now, limit=3,
                                  ret_mode=RET_MODE_ACCESSORS))
        expect = self.occ[1:2] + self.occ[6:8]  # includes ongoing long event
        self.assertEqual(res, expect, self.diff(res, expect))

    ### expand=False: events

    def test_noexpand_all(self):
        # all events
        res = self.fmt(get_events(self.portal, expand=False,
                                  ret_mode=RET_MODE_ACCESSORS))
        expect = [
            (u'Past Event', '2013-04-25 00:00:00', '2013-04-25 23:59:59'),
            (u'Long Event', '2013-04-25 10:00:00', '2013-06-04 10:00:00'),
            (u'Past Recur', '2013-04-25 11:00:00', '2013-04-25 12:00:00'),
            (u'Now Event', '2013-05-05 10:00:00', '2013-05-05 11:00:00'),
            (u'Tomorrow event', '2013-05-06 10:00:00', '2013-05-06 23:59:59'),
            (u'Future Event', '2013-05-15 10:00:00', '2013-05-15 11:00:00')]
        self.assertEqual(res, expect, self.diff(res, expect))

        # limited events
        res = self.fmt(get_events(self.portal, expand=False,
                                  limit=3,
                                  ret_mode=RET_MODE_ACCESSORS))
        self.assertEqual(res, expect[:3], self.diff(res, expect[:3]))

    def test_noexpand_start(self):
        # now+future events
        res = self.fmt(get_events(self.portal, expand=False,
                                  start=self.now,
                                  ret_mode=RET_MODE_ACCESSORS))
        expect = [
            (u'Long Event', '2013-04-25 10:00:00', '2013-06-04 10:00:00'),
            (u'Now Event', '2013-05-05 10:00:00', '2013-05-05 11:00:00'),
            (u'Tomorrow event', '2013-05-06 10:00:00', '2013-05-06 23:59:59'),
            # Past Recur next occurrence: '2013-05-09 11:00:00'
            # Past Recur brain.start: '2013-04-25 11:00:00'
            (u'Past Recur', '2013-04-25 11:00:00', '2013-04-25 12:00:00'),
            (u'Future Event', '2013-05-15 10:00:00', '2013-05-15 11:00:00')]
        self.assertEqual(res, expect, self.diff(res, expect))

        # limited now+future events
        res = self.fmt(get_events(self.portal, expand=False,
                                  start=self.now, limit=3,
                                  ret_mode=RET_MODE_ACCESSORS))
        self.assertEqual(res, expect[:3], self.diff(res, expect[:3]))

    def test_noexpand_end(self):
        # past+now events
        res = self.fmt(get_events(self.portal, expand=False,
                                  end=self.now,
                                  ret_mode=RET_MODE_ACCESSORS))
        expect = [
            (u'Past Event', '2013-04-25 00:00:00', '2013-04-25 23:59:59'),
            (u'Long Event', '2013-04-25 10:00:00', '2013-06-04 10:00:00'),
            (u'Past Recur', '2013-04-25 11:00:00', '2013-04-25 12:00:00'),
            (u'Now Event', '2013-05-05 10:00:00', '2013-05-05 11:00:00')]
        self.assertEqual(res, expect, self.diff(res, expect))

        # limited past+now events
        res = self.fmt(get_events(self.portal, expand=False,
                                  end=self.now,
                                  limit=3,
                                  ret_mode=RET_MODE_ACCESSORS))
        self.assertEqual(res, expect[:3], self.diff(res, expect[:3]))

    def test_noexpand_start_end(self):
        # only now events
        res = self.fmt(get_events(self.portal, expand=False,
                                  start=self.now,
                                  end=self.now,
                                  ret_mode=RET_MODE_ACCESSORS))
        expect = [
            (u'Long Event', '2013-04-25 10:00:00', '2013-06-04 10:00:00'),
            (u'Now Event', '2013-05-05 10:00:00', '2013-05-05 11:00:00')]
        self.assertEqual(res, expect, self.diff(res, expect))

        # limited now events
        res = self.fmt(get_events(self.portal, expand=False,
                                  start=self.now,
                                  end=self.now,
                                  limit=3,
                                  ret_mode=RET_MODE_ACCESSORS))
        self.assertEqual(res, expect[:3], self.diff(res, expect[:3]))


class TestDatesForDisplayAT(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_prep_display_with_time(self):
        event_id = self.portal.invokeFactory(
            'Event',
            id="event",
            startDate='2000/10/12 06:00:00',
            endDate='2000/10/12 18:00:00',
            timezone="Europe/Vienna"
        )
        event = self.portal[event_id]
        self.assertEqual(
            dates_for_display(event),
            {'start_date': u'Oct 12, 2000',
             'start_time': u'06:00 AM',
             'start_iso':  '2000-10-12T06:00:00+02:00',
             'end_date':   u'Oct 12, 2000',
             'end_time':   u'06:00 PM',
             'end_iso':    '2000-10-12T18:00:00+02:00',
             'same_day':   True,
             'same_time':  False,
             'whole_day':  False,
             'open_end':   False,
             }
        )

    def test_prep_display_wholeday_sameday(self):
        event_id = self.portal.invokeFactory(
            'Event',
            id="event",
            startDate='2000/10/12 06:00:00',
            endDate='2000/10/12 18:00:00',
            timezone="Europe/Vienna",
            wholeDay=True
        )
        event = self.portal[event_id]
        self.assertEqual(
            dates_for_display(event),
            {'start_date': u'Oct 12, 2000',
             'start_time': None,
             'start_iso':  '2000-10-12',
             'end_date':   u'Oct 12, 2000',
             'end_time':   None,
             'end_iso':    '2000-10-12',
             'same_day':   True,
             'same_time':  False,
             'whole_day':  True,
             'open_end':   False
             }
        )

    def test_prep_display_wholeday_differentdays(self):
        event_id = self.portal.invokeFactory(
            'Event',
            id="event",
            startDate='2000/10/12 06:00:00',
            endDate='2000/10/13 18:00:00',
            timezone="Europe/Vienna",
            wholeDay=True
        )
        event = self.portal[event_id]
        self.assertEqual(
            dates_for_display(event),
            {'start_date': u'Oct 12, 2000',
             'start_time': None,
             'start_iso':  '2000-10-12',
             'end_date':   u'Oct 13, 2000',
             'end_time':   None,
             'end_iso':    '2000-10-13',
             'same_day':   False,
             'same_time':  False,
             'whole_day':  True,
             'open_end':   False,
             }
        )


class TestDatesForDisplayDX(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_prep_display_with_time(self):
        event_id = self.portal.invokeFactory(
            'plone.app.event.dx.event',
            id="event",
            start=datetime.datetime(2000, 10, 12, 6, 0, 0),
            end=datetime.datetime(2000, 10, 12, 18, 0, 0),
            timezone="Europe/Vienna",
            whole_day=False,
            open_end=False
        )
        event = self.portal[event_id]
        self.assertEqual(
            dates_for_display(event),
            {'start_date': u'Oct 12, 2000',
             'start_time': u'06:00 AM',
             'start_iso':  '2000-10-12T06:00:00+02:00',
             'end_date':   u'Oct 12, 2000',
             'end_time':   u'06:00 PM',
             'end_iso':    '2000-10-12T18:00:00+02:00',
             'same_day':   True,
             'same_time':  False,
             'whole_day':  False,
             'open_end':   False,
             }
        )

    def test_prep_display_wholeday_sameday(self):
        event_id = self.portal.invokeFactory(
            'plone.app.event.dx.event',
            id="event",
            start=datetime.datetime(2000, 10, 12, 6, 0, 0),
            end=datetime.datetime(2000, 10, 12, 18, 0, 0),
            timezone="Europe/Vienna",
            whole_day=True,
            open_end=False
        )
        event = self.portal[event_id]
        self.assertEqual(
            dates_for_display(event),
            {'start_date': u'Oct 12, 2000',
             'start_time': None,
             'start_iso':  '2000-10-12',
             'end_date':   u'Oct 12, 2000',
             'end_time':   None,
             'end_iso':    '2000-10-12',
             'same_day':   True,
             'same_time':  False,
             'whole_day':  True,
             'open_end':   False,
             }
        )

    def test_prep_display_wholeday_differentdays(self):
        event_id = self.portal.invokeFactory(
            'plone.app.event.dx.event',
            id="event",
            start=datetime.datetime(2000, 10, 12, 6, 0, 0),
            end=datetime.datetime(2000, 10, 13, 18, 0, 0),
            timezone="Europe/Vienna",
            whole_day=True,
            open_end=False
        )
        event = self.portal[event_id]
        self.assertEqual(
            dates_for_display(event),
            {'start_date': u'Oct 12, 2000',
             'start_time': None,
             'start_iso':  '2000-10-12',
             'end_date':   u'Oct 13, 2000',
             'end_time':   None,
             'end_iso':    '2000-10-13',
             'same_day':   False,
             'same_time':  False,
             'whole_day':  True,
             'open_end':   False,
             }
        )
