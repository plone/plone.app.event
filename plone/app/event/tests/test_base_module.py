import datetime
import pytz
import unittest2 as unittest
import zope.component
from DateTime import DateTime
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
from plone.app.event.interfaces import IEventSettings, ICalendarLinkbase
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.interface import directlyProvides


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


class TestCalendarLinkbase(unittest.TestCase):
    # TODO: test overriding of ICalendarLinkbase
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_date_events_url(self):
        lb = ICalendarLinkbase(self.portal)
        res = 'http://nohost/plone/@@search?advanced_search=True&start.query'\
              ':record:list:date=2012-12-24+23:59:59&start.range:record=max&'\
              'end.query:record:list:date=2012-12-24+00:00:00&end.range:reco'\
              'rd=min&object_provides=plone.event.interfaces.IEvent'
        self.assertTrue(lb.date_events_url('2012-12-24') == res)

    def test_all_events_url(self):
        # if there is an 'events' object in the portal root, we expect
        # the events portlet to link to it
        if 'events' in self.portal:
            self.portal._delObject('events')
        lb = ICalendarLinkbase(self.portal)
        self.failUnless('@@search?advanced_search=True&object_provides'
                        in lb.all_events_url())

        self.portal.invokeFactory('Folder', 'events')
        self.failUnless(lb.all_events_url().endswith('/events'))

    def test_all_events_url_and_navigation_root(self):
        # ensure support of INavigationRoot features dosen't break #9246 #9668
        self.portal.invokeFactory('Folder', 'mynewsite')
        directlyProvides(self.portal.mynewsite, INavigationRoot)
        self.failUnless(INavigationRoot.providedBy(self.portal.mynewsite))

        lb = ICalendarLinkbase(self.portal.mynewsite)
        self.failUnless('mynewsite/@@search?advanced_search=True&object_prov'
                        in lb.all_events_url())

        self.portal.mynewsite.invokeFactory('Folder', 'events')
        self.failUnless(lb.all_events_url().endswith('/mynewsite/events'))

    def test_next_events_url(self):
        # if there is an 'events' object in the portal root, we expect
        # the events portlet to link to it
        if 'events' in self.portal:
            self.portal._delObject('events')
        lb = ICalendarLinkbase(self.portal)
        self.failUnless('@@search?advanced_search=True&start.query'
                        in lb.next_events_url())

        self.portal.invokeFactory('Folder', 'events')
        self.failUnless(lb.next_events_url().endswith('/events'))

    def test_next_events_url_and_navigation_root(self):
        # ensure support of INavigationRoot features dosen't break #9246 #9668
        self.portal.invokeFactory('Folder', 'mynewsite')
        directlyProvides(self.portal.mynewsite, INavigationRoot)
        self.failUnless(INavigationRoot.providedBy(self.portal.mynewsite))

        lb = ICalendarLinkbase(self.portal.mynewsite)
        self.failUnless('mynewsite/@@search?advanced_search=True&start.query'
                        in lb.next_events_url())

        self.portal.mynewsite.invokeFactory('Folder', 'events')
        self.failUnless(lb.next_events_url().endswith('/mynewsite/events'))

    def test_past_events_url(self):
        lb = ICalendarLinkbase(self.portal)
        if lb._events_folder():
            self.failUnless(lb.past_events_url().endswith(
                '/events/aggregator/previous'))

        if lb._events_folder():
            self.portal._delObject('events')

        self.portal.invokeFactory('Folder', 'events')
        self.portal.events.invokeFactory('Folder', 'previous')
        self.failUnless(lb.past_events_url().endswith(
            '/events/previous'))

        self.portal._delObject('events')
        self.failUnless('@@search?advanced_search=True&end.query'
                        in lb.past_events_url())

    def test_past_events_url_and_navigation_root(self):
        # ensure support of INavigationRoot features dosen't break #9246 #9668

        # remove default plone content(s)
        if 'events' in self.portal:
            self.portal._delObject('events')

        # lets create mynewsite
        self.portal.invokeFactory('Folder', 'mynewsite')
        directlyProvides(self.portal.mynewsite, INavigationRoot)
        self.failUnless(INavigationRoot.providedBy(self.portal.mynewsite))

        lb = ICalendarLinkbase(self.portal.mynewsite)

        # mynewsite events:
        # -- events
        # ---- aggregator
        # ------ previous
        self.portal.mynewsite.invokeFactory('Folder', 'events')
        self.portal.mynewsite.events.invokeFactory('Folder', 'aggregator')
        self.portal.mynewsite.events.aggregator.invokeFactory('Folder', 'previous')
        self.failUnless(lb.past_events_url().endswith(
            '/mynewsite/events/aggregator/previous'))

        # mynewsite events:
        # -- events
        # ---- previous
        self.portal.mynewsite._delObject('events')
        self.portal.mynewsite.invokeFactory('Folder', 'events')
        self.portal.mynewsite.events.invokeFactory('Folder', 'previous')
        self.failUnless(lb.past_events_url().endswith(
            '/mynewsite/events/previous'))

        # no mynewsite events
        self.portal.mynewsite._delObject('events')
        self.assertTrue('@@search?advanced_search=True&end.query'
                        in lb.past_events_url())


class TestBaseModuleQueryPydt(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        default_tz = default_timezone()
        #default_tz = 'Europe/Vienna'

        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = default_tz

        now = localized_now()
        past = now - datetime.timedelta(days=2)
        future = now + datetime.timedelta(days=2)
        far = now + datetime.timedelta(days=8)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory(
            'Event',
            'past',
            title=u'Past event',
            startDate=past,
            endDate=past + datetime.timedelta(hours=1),
            location=u'Vienna',
            timezone=default_tz,
            whole_day=False)

        self.portal.invokeFactory(
            'Event',
            'now',
            title=u'Now event',
            startDate=now,
            endDate=now + datetime.timedelta(hours=1),
            location=u'Vienna',
            recurrence='RRULE:FREQ=DAILY;COUNT=4;INTERVAL=4',
            timezone=default_tz,
            whole_day=False)

        self.portal.invokeFactory(
            'Event',
            'future',
            title=u'Future event',
            startDate=future,
            endDate=future + datetime.timedelta(hours=1),
            location=u'Graz',
            timezone=default_tz,
            whole_day=False)

        self.portal.invokeFactory(
            'Event',
            'long',
            title=u'Long event',
            startDate=past,
            endDate=future,
            location=u'Schaftal',
            timezone=default_tz,
            whole_day=False)

        self.now = now
        self.past = past
        self.future = future
        self.far = far

        self.now_event = self.portal['now']
        self.past_event = self.portal['past']
        self.future_event = self.portal['future']
        self.long_event = self.portal['long']


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

    def test_get_occurrences(self):
        get_occurrences_from_brains(object, [],
                range_start=datetime.datetime.today())

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
            timezone=default_tz,
            whole_day=False)

        self.portal.invokeFactory(
            'Event',
            'now',
            title=u'Now event',
            startDate=now,
            endDate=now+0.1,
            location=u'Vienna',
            recurrence='RRULE:FREQ=DAILY;COUNT=4;INTERVAL=4',
            timezone=default_tz,
            whole_day=False)

        self.portal.invokeFactory(
            'Event',
            'future',
            title=u'Future event',
            startDate=future,
            endDate=future+0.1,
            location=u'Graz',
            timezone=default_tz,
            whole_day=False)

        self.portal.invokeFactory(
            'Event',
            'long',
            title=u'Long event',
            startDate=past,
            endDate=future,
            location=u'Schaftal',
            timezone=default_tz,
            whole_day=False)

        self.now = now
        self.past = past
        self.future = future
        self.far = far

        self.now_event = self.portal['now']
        self.past_event = self.portal['past']
        self.future_event = self.portal['future']
        self.long_event = self.portal['long']


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
