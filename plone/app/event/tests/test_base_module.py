import datetime
import pytz
import unittest2 as unittest
import zope.component
from DateTime import DateTime
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.interface import directlyProvides

from plone.app.event.base import (
    DEFAULT_END_DELTA,
    DT,
    default_end_DT,
    default_end_dt,
    default_start_DT,
    default_start_dt,
    default_timezone,
    get_occurrences_from_brains,
    get_portal_events,
    localized_now,
    dates_for_display
)
from plone.app.event import base
from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.interfaces import IEventSettings, ICalendarLinkbase
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents

class TestBaseModule(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def assertEqualDatetime(self, date1, date2, msg=None):
        """ Compare two datetime instances to a resolution of minutes.
        """
        compare_str = '%Y-%m-%d %H:%M %Z'
        self.assertTrue(date1.strftime(compare_str) ==\
                        date2.strftime(compare_str), msg)

    def test_default_end_dt(self):
        self.assertEqualDatetime(
            default_end_dt() - datetime.timedelta(hours=DEFAULT_END_DELTA),
            localized_now())

    def test_default_start_dt(self):
        self.assertEqualDatetime(default_start_dt(), localized_now())

    def test_default_end_DT(self):
        DTE = default_end_DT()
        DTN = DT(localized_now() + datetime.timedelta(hours=DEFAULT_END_DELTA))

        self.assertTrue(DTE.year() == DTN.year() and
                        DTE.month() == DTN.month() and
                        DTE.day() == DTN.day() and
                        DTE.hour() == DTN.hour() and
                        DTE.minute() == DTN.minute())

    def test_default_start_DT(self):
        DTS = default_start_DT()
        DTN = DT(localized_now())

        self.assertTrue(DTS.year() == DTN.year() and
                        DTS.month() == DTN.month() and
                        DTS.day() == DTN.day() and
                        DTS.hour() == DTN.hour() and
                        DTS.minute() == DTN.minute())

    def test_DT(self):
        # Python datetime with valid zone. Zope converts it to GMT+1...
        # TODO: DateTime better shouldn't do this!
        cet = pytz.timezone('CET')
        self.assertTrue(
            DT(datetime.datetime(2011, 11, 11, 11, 0, 0, tzinfo=cet)) ==
            DateTime('2011/11/11 11:00:00 GMT+1')
        )

        # Python dates get converted to a DateTime with timecomponent including
        # a timezone
        self.assertTrue(
            DT(datetime.date(2011, 11, 11)) ==
            DateTime('2011/11/11 00:00:00 UTC')
        )

        # DateTime with valid zone
        self.assertTrue(
            DT(DateTime(2011, 11, 11, 11, 0, 0, 'Europe/Vienna')) ==
            DateTime('2011/11/11 11:00:00 Europe/Vienna')
        )

        # Zope DateTime with valid DateTime zone but invalid pytz is kept as is
        self.assertTrue(
            DT(DateTime(2011, 11, 11, 11, 0, 0, 'GMT+1')) ==
            DateTime('2011/11/11 11:00:00 GMT+1')
        )

        # Invalid datetime zones are converted to the portal timezone
        # Testing with no timezone
        self.assertTrue(
            DT(datetime.datetime(2011, 11, 11, 11, 0, 0)) ==
            DateTime('2011/11/11 11:00:00 UTC')
        )

        # Testing conversion of datetime with microseconds
        tz = pytz.timezone('Europe/Vienna')
        self.assertTrue(
            DT(datetime.datetime(2012, 12, 12, 10, 10, 10, 123456,
               tzinfo=tz)) ==
            DateTime('2012/12/12 10:10:10.123456 Europe/Vienna')
        )


    def test_cal_to_strftime_wkday(self):
        from plone.app.event.base import cal_to_strftime_wkday
        li = [cal_to_strftime_wkday(day) for day in range(0,7)]
        self.assertTrue(li == [1, 2, 3, 4, 5, 6, 0])

    def test_strftime_to_cal_wkday(self):
        from plone.app.event.base import strftime_to_cal_wkday
        li = [strftime_to_cal_wkday(day) for day in range(0,7)]
        self.assertTrue(li == [6, 0, 1, 2, 3, 4, 5])

    def test__default_timezone(self):
        """Test, if default_timezone returns something other than None if
        called with and without a context.
        """
        self.assertTrue(default_timezone() is not None)
        self.assertTrue(default_timezone(context=self.portal) is not None)

    def test__dt_start_of_day(self):
        from plone.app.event.base import dt_start_of_day
        self.assertTrue(dt_start_of_day(datetime.datetime(2013,2,1,18,35))
                        == datetime.datetime(2013,2,1,0,0,0,0))
        self.assertTrue(dt_start_of_day(datetime.date(2013,2,1))
                        == datetime.datetime(2013,2,1,0,0,0,0))

    def test__dt_end_of_day(self):
        from plone.app.event.base import dt_end_of_day
        self.assertTrue(dt_end_of_day(datetime.datetime(2013,2,1,18,35))
                        == datetime.datetime(2013,2,1,23,59,59,0))
        self.assertTrue(dt_end_of_day(datetime.date(2013,2,1))
                        == datetime.datetime(2013,2,1,23,59,59,0))

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
        self.assertTrue(lb.date_events_url('2012-12-07') == url)

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
    layer = PAEventDX_INTEGRATION_TESTING
    def event_factory(self):
        return DXEventAccessor.create

    def test_get_portal_events(self):
        # whole range
        res = get_portal_events(self.portal)
        self.assertTrue(len(res) == 4)

        res = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.future)
        self.assertTrue(len(res) == 4)

        res = get_portal_events(self.portal,
                                 range_end=self.future)
        self.assertTrue(len(res) == 4)

        res = get_portal_events(self.portal,
                                 range_start=self.past)
        self.assertTrue(len(res) == 4)


        # only on now-date
        res = get_portal_events(self.portal,
                                 range_start=self.now,
                                 range_end=self.now)
        self.assertTrue(len(res) == 2)

        # only on now-date as date
        res = get_portal_events(self.portal,
                                 range_start=self.now.date(),
                                 range_end=self.now.date())
        self.assertTrue(len(res) == 2)

        # only on past date
        res = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.past)
        self.assertTrue(len(res) == 2)

        # one recurrence occurrence in future
        res = get_portal_events(self.portal,
                                 range_start=self.far,
                                 range_end=self.far)
        self.assertTrue(len(res) == 1)

        # from now on
        res = get_portal_events(self.portal,
                                 range_start=self.now)
        self.assertTrue(len(res) == 3)

        # until now
        res = get_portal_events(self.portal,
                                 range_end=self.now)
        self.assertTrue(len(res) == 3)

        # in subfolder
        path = '/'.join(self.portal.sub.getPhysicalPath())
        res = get_portal_events(self.portal, path=path)
        self.assertTrue(len(res) == 1)

    def test_get_occurrences(self):
        get_occurrences_from_brains(object, [],
                range_start=datetime.datetime.today())


class TestGetEventsAT(TestGetEventsDX):
    layer = PAEventAT_INTEGRATION_TESTING
    def event_factory(self):
        return ATEventAccessor.create


class TestBaseModuleQueryZDT(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        default_tz = default_timezone()

        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = default_tz

        # Zope DateTime
        now =    DateTime(2012, 9,10,10,10, 0, default_tz)
        past =   DateTime(2012, 9, 1,10,10, 0, default_tz)
        future = DateTime(2012, 9,20,10,10, 0, default_tz)
        far =    DateTime(2012, 9,22,10,10, 0, default_tz)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory(
            'Event',
            'past',
            title=u'Past event',
            startDate=past,
            endDate=past+0.1, # Zope DT
            location=u'Vienna',
            timezone=default_tz)

        self.portal.invokeFactory(
            'Event',
            'now',
            title=u'Now event',
            startDate=now,
            endDate=now+0.1,
            location=u'Vienna',
            recurrence='RRULE:FREQ=DAILY;COUNT=4;INTERVAL=4',
            timezone=default_tz)

        self.portal.invokeFactory(
            'Event',
            'future',
            title=u'Future event',
            startDate=future,
            endDate=future+0.1,
            location=u'Graz',
            timezone=default_tz)

        self.portal.invokeFactory('Folder', 'sub', title=u'sub')
        self.portal.sub.invokeFactory(
            'Event',
            'long',
            title=u'Long event',
            startDate=past,
            endDate=future,
            location=u'Schaftal',
            timezone=default_tz)

        self.now = now
        self.past = past
        self.future = future
        self.far = far

        self.now_event = self.portal['now']
        self.past_event = self.portal['past']
        self.future_event = self.portal['future']
        self.long_event = self.portal['sub']['long']


    def test_get_portal_events(self):

        # whole range
        res = get_portal_events(self.portal)
        self.assertTrue(len(res) == 4)

        res = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.future)
        self.assertTrue(len(res) == 4)

        res = get_portal_events(self.portal,
                                 range_end=self.future)
        self.assertTrue(len(res) == 4)

        res = get_portal_events(self.portal,
                                 range_start=self.past)
        self.assertTrue(len(res) == 4)


        # only on now-date
        res = get_portal_events(self.portal,
                                 range_start=self.now,
                                 range_end=self.now)
        self.assertTrue(len(res) == 2)

        # only on past date
        res = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.past)
        self.assertTrue(len(res) == 2)

        # one recurrence occurrence in future
        res = get_portal_events(self.portal,
                                 range_start=self.far,
                                 range_end=self.far)
        self.assertTrue(len(res) == 1)

        # from now on
        res = get_portal_events(self.portal,
                                 range_start=self.now)
        self.assertTrue(len(res) == 3)

        # until now
        res = get_portal_events(self.portal,
                                 range_end=self.now)
        self.assertTrue(len(res) == 3)

        # in subfolder
        path = '/'.join(self.portal.sub.getPhysicalPath())
        res = get_portal_events(self.portal, path=path)
        self.assertTrue(len(res) == 1)


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
                 'url': 'http://nohost/plone/event'
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
                 'start_iso':  u'2000-10-12T00:00:00+02:00',
                 'end_date':   u'Oct 12, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-12T23:59:59+02:00',
                 'same_day':   True,
                 'same_time':  False,
                 'whole_day':  True,
                 'url': 'http://nohost/plone/event'
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
                 'start_iso':  u'2000-10-12T00:00:00+02:00',
                 'end_date':   u'Oct 13, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-13T23:59:59+02:00',
                 'same_day':   False,
                 'same_time':  False,
                 'whole_day':  True,
                 'url': 'http://nohost/plone/event'
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
                 'url': 'http://nohost/plone/event'
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
                 'start_iso':  u'2000-10-12T00:00:00+02:00',
                 'end_date':   u'Oct 12, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-12T23:59:59+02:00',
                 'same_day':   True,
                 'same_time':  False,
                 'whole_day':  True,
                 'url': 'http://nohost/plone/event'
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
                 'start_iso':  u'2000-10-12T00:00:00+02:00',
                 'end_date':   u'Oct 13, 2000',
                 'end_time':   None,
                 'end_iso':    u'2000-10-13T23:59:59+02:00',
                 'same_day':   False,
                 'same_time':  False,
                 'whole_day':  True,
                 'url': 'http://nohost/plone/event'
                })
