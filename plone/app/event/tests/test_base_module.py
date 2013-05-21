from DateTime import DateTime
from plone.app.event import base
from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.base import DEFAULT_END_DELTA
from plone.app.event.base import DT
from plone.app.event.base import construct_calendar
from plone.app.event.base import dates_for_display
from plone.app.event.base import default_end
from plone.app.event.base import default_start
from plone.app.event.base import default_timezone
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.interfaces import ICalendarLinkbase
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.utils import pydt
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
            localized_now())

    def test_default_start(self):
        self.assertEqualDatetime(default_start(), localized_now())

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
        self.assertEqual(dt_start_of_day(datetime.datetime(2013,2,1,18,35)),
                         datetime.datetime(2013,2,1,0,0,0,0))
        self.assertEqual(dt_start_of_day(datetime.date(2013,2,1)),
                         datetime.datetime(2013,2,1,0,0,0,0))

    def test__dt_end_of_day(self):
        from plone.app.event.base import dt_end_of_day
        self.assertEqual(dt_end_of_day(datetime.datetime(2013,2,1,18,35)),
                         datetime.datetime(2013,2,1,23,59,59,0))
        self.assertEqual(dt_end_of_day(datetime.date(2013,2,1)),
                         datetime.datetime(2013,2,1,23,59,59,0))

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
        self.assertTrue(isinstance(start, datetime.datetime) and
                        isinstance(end, datetime.datetime) and
                        end.hour==23 and end.minute==59 and end.second==59)

        # 7DAYS
        #
        start, end = start_end_from_mode('7days')
        self.assertTrue(isinstance(start, datetime.datetime) and
                        isinstance(end, datetime.datetime) and
                        end == dt_end_of_day(start+datetime.timedelta(days=6)))

        # TODAY
        #
        start, end = start_end_from_mode('today')
        self.assertTrue(isinstance(start, datetime.datetime) and
                        isinstance(end, datetime.datetime) and
                        start.hour==0 and start.minute==0 and start.second==0
                        and
                        end.hour==23 and end.minute==59 and end.second==59 and
                        (start, end) == start_end_from_mode('day'))

        # DAY
        #
        day = datetime.datetime(2013,2,1,18,22)
        start, end = start_end_from_mode('day', day)
        self.assertTrue(start.date() == day.date() == end.date() and
                        start.hour==0 and start.minute==0 and start.second==0
                        and
                        end.hour==23 and end.minute==59 and end.second==59)

        # test with date-only
        day = datetime.datetime(2013,2,1)
        start, end = start_end_from_mode('day', day)
        self.assertTrue(start.date() == day.date() == end.date() and
                        start.hour==0 and start.minute==0 and start.second==0
                        and
                        end.hour==23 and end.minute==59 and end.second==59)

        # WEEK
        #
        def ret_0(): return 0 # Monday
        def ret_1(): return 1 # Tuesday
        def ret_6(): return 6 # Sunday
        orig_first_weekday = base.first_weekday # prepare patched first_weekday

        base.first_weekday = ret_0
        day = datetime.datetime(2013,2,2)
        start, end = start_end_from_mode('week', day)
        self.assertTrue(start.isoformat() == '2013-01-28T00:00:00' and
                        end.isoformat()   == '2013-02-03T23:59:59')

        base.first_weekday = ret_1
        day = datetime.datetime(2013,2,2)
        start, end = start_end_from_mode('week', day)
        self.assertTrue(start.isoformat() == '2013-01-29T00:00:00' and
                        end.isoformat()   == '2013-02-04T23:59:59')

        base.first_weekday = ret_6
        day = datetime.datetime(2013,2,1)
        start, end = start_end_from_mode('week', day)
        self.assertTrue(start.isoformat() == '2013-01-27T00:00:00' and
                        end.isoformat()   == '2013-02-02T23:59:59')

        base.first_weekday = orig_first_weekday # restore orig first_weekday

        # MONTH
        #
        start, end = start_end_from_mode('month')
        self.assertTrue(start < end and start.day==1)

        day = datetime.datetime(2013,2,7)
        start, end = start_end_from_mode('month', day)
        self.assertTrue(start.year==2013 and start.month==2 and start.day==1
                        and
                        start.hour==0 and start.minute==0 and start.second==0
                        and
                        end.year==2013 and end.month==2 and end.day==28
                        and
                        end.hour==23 and end.minute==59 and end.second==59)


class TestCalendarLinkbase(unittest.TestCase):
    # TODO: test overriding of ICalendarLinkbase
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_date_events_url(self):
        lb = ICalendarLinkbase(self.portal)
        url = 'http://nohost/plone/@@event_listing?mode=day&date=2012-12-07'
        self.assertEqual(lb.date_events_url('2012-12-07'), url)

    def test_all_events_url(self):
        lb = ICalendarLinkbase(self.portal)
        url = 'http://nohost/plone/@@event_listing?mode=all'
        self.failUnless(lb.all_events_url() == url)

    def test_next_events_url(self):
        lb = ICalendarLinkbase(self.portal)
        url = 'http://nohost/plone/@@event_listing?mode=future'
        self.failUnless(lb.next_events_url() == url)

    def test_past_events_url(self):
        lb = ICalendarLinkbase(self.portal)
        url = 'http://nohost/plone/@@event_listing?mode=past'
        self.failUnless(lb.past_events_url() == url)

    def test_events_url_with_navigation_root(self):
        # ensure support of INavigationRoot features dosen't break #9246 #9668
        self.portal.invokeFactory('Folder', 'mynewsite')
        directlyProvides(self.portal.mynewsite, INavigationRoot)
        self.failUnless(INavigationRoot.providedBy(self.portal.mynewsite))
        lb = ICalendarLinkbase(self.portal.mynewsite)

        url = 'http://nohost/plone/mynewsite/@@event_listing?mode=day&date=2012-12-07'
        self.failUnless(lb.date_events_url('2012-12-07') == url)

        url = 'http://nohost/plone/mynewsite/@@event_listing?mode=all'
        self.failUnless(lb.all_events_url() == url)

        url = 'http://nohost/plone/mynewsite/@@event_listing?mode=future'
        self.failUnless(lb.next_events_url() == url)

        url = 'http://nohost/plone/mynewsite/@@event_listing?mode=past'
        self.failUnless(lb.past_events_url() == url)


class TestGetEventsDX(AbstractSampleDataEvents):
    """Test get_events with DX objects.
    """
    layer = PAEventDX_INTEGRATION_TESTING
    def event_factory(self):
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
        res = get_events(self.portal, ret_mode=2)
        self.assertTrue(IEvent.providedBy(res[0]))

        # Return IEventAccessor
        res = get_events(self.portal, ret_mode=3)
        self.assertTrue(IEventAccessor.providedBy(res[0]))
        # Test sorting
        self.assertTrue(res[0].start < res[-1].start)

        # Test reversed sorting
        res = get_events(self.portal, ret_mode=3, sort_reverse=True)
        self.assertTrue(res[0].start > res[-1].start)

        # Test sort_on
        res = get_events(self.portal, ret_mode=3, sort="start")
        self.assertEqual(
            [it.title for it in res][2:],
            [u'Now Event', u'Future Event']
        )
        res = get_events(self.portal, ret_mode=3, sort="end")
        self.assertEqual(
            [it.title for it in res],
            [u'Past Event', u'Now Event', u'Future Event', u'Long Event']
        )

        # Test expansion
        res = get_events(self.portal, ret_mode=2, expand=True)
        self.assertEqual(len(res), 8)

        res = get_events(self.portal, ret_mode=3, expand=True)
        self.assertEqual(len(res), 8)
        # Test sorting
        self.assertTrue(res[0].start < res[-1].start)

        res = get_events(self.portal, ret_mode=3, expand=True,
                         sort_reverse=True)
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

    def test_construct_calendar(self):
        res = get_events(self.portal, ret_mode=2, expand=True)
        cal = construct_calendar(res)  # keys are date-strings.
        # Should be more than one, but we can't exactly say how much. This
        # depends on the date, the test is run. E.g. on last day of month, only
        # long, past and now without recurrences are returned, others are in
        # next month.
        self.assertTrue(len(cal.keys()) > 1)


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
        now      = self.now      = DateTime(2012, 9,10,10,10, 0, def_tz)
        past     = self.past     = DateTime(2012, 9, 1,10,10, 0, def_tz)
        future   = self.future   = DateTime(2012, 9,20,10,10, 0, def_tz)
        far      = self.far      = DateTime(2012, 9,22,10,10, 0, def_tz)
        duration = self.duration = 0.1
        return (now, past, future, far, duration)


class TestDatesForDisplayAT(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_prep_display_with_time(self):
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/12 18:00:00',
                timezone="Europe/Vienna")
        event = self.portal[event_id]
        self.assertEqual(dates_for_display(event),
                {'start_date': u'Oct 12, 2000',
                 'start_time': u'06:00 AM',
                 'start_iso':  u'2000-10-12T06:00:00+02:00',
                 'end_date':   u'Oct 12, 2000',
                 'end_time':   u'06:00 PM',
                 'end_iso':    u'2000-10-12T18:00:00+02:00',
                 'same_day':   True,
                 'same_time':  False,
                 'whole_day':  False,
                 'open_end':   False,
                })

    def test_prep_display_wholeday_sameday(self):
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/12 18:00:00',
                timezone="Europe/Vienna",
                wholeDay=True)
        event = self.portal[event_id]
        self.assertEqual(dates_for_display(event),
                {'start_date': u'Oct 12, 2000',
                 'start_time': None,
                 'start_iso':  u'2000-10-12',
                 'end_date':   u'Oct 12, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-12',
                 'same_day':   True,
                 'same_time':  False,
                 'whole_day':  True,
                 'open_end':   False
                })

    def test_prep_display_wholeday_differentdays(self):
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/13 18:00:00',
                timezone="Europe/Vienna",
                wholeDay=True)
        event = self.portal[event_id]
        self.assertEqual(dates_for_display(event),
                {'start_date': u'Oct 12, 2000',
                 'start_time': None,
                 'start_iso':  u'2000-10-12',
                 'end_date':   u'Oct 13, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-13',
                 'same_day':   False,
                 'same_time':  False,
                 'whole_day':  True,
                 'open_end':   False,
                })


class TestDatesForDisplayDX(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_prep_display_with_time(self):
        event_id = self.portal.invokeFactory('plone.app.event.dx.event',
                id="event",
                start=datetime.datetime(2000, 10, 12, 6, 0, 0),
                end=datetime.datetime(2000, 10, 12, 18, 0, 0),
                timezone="Europe/Vienna")
        event = self.portal[event_id]
        self.assertEqual(dates_for_display(event),
                {'start_date': u'Oct 12, 2000',
                 'start_time': u'06:00 AM',
                 'start_iso':  u'2000-10-12T06:00:00+02:00',
                 'end_date':   u'Oct 12, 2000',
                 'end_time':   u'06:00 PM',
                 'end_iso':    u'2000-10-12T18:00:00+02:00',
                 'same_day':   True,
                 'same_time':  False,
                 'whole_day':  False,
                 'open_end':   False,
                })

    def test_prep_display_wholeday_sameday(self):
        event_id = self.portal.invokeFactory('plone.app.event.dx.event',
                id="event",
                start=datetime.datetime(2000, 10, 12, 6, 0, 0),
                end=datetime.datetime(2000, 10, 12, 18, 0, 0),
                timezone="Europe/Vienna",
                whole_day=True)
        event = self.portal[event_id]
        self.assertEqual(dates_for_display(event),
                {'start_date': u'Oct 12, 2000',
                 'start_time': None,
                 'start_iso':  u'2000-10-12',
                 'end_date':   u'Oct 12, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-12',
                 'same_day':   True,
                 'same_time':  False,
                 'whole_day':  True,
                 'open_end':   False,
                })

    def test_prep_display_wholeday_differentdays(self):
        event_id = self.portal.invokeFactory('plone.app.event.dx.event',
                id="event",
                start=datetime.datetime(2000, 10, 12, 6, 0, 0),
                end=datetime.datetime(2000, 10, 13, 18, 0, 0),
                timezone="Europe/Vienna",
                whole_day=True)
        event = self.portal[event_id]
        self.assertEqual(dates_for_display(event),
                {'start_date': u'Oct 12, 2000',
                 'start_time': None,
                 'start_iso':  u'2000-10-12',
                 'end_date':   u'Oct 13, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-13',
                 'same_day':   False,
                 'same_time':  False,
                 'whole_day':  True,
                 'open_end':   False,
                })
