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
    get_occurrences,
    get_portal_events,
    localized_now
)
from plone.app.event.interfaces import IEventSettings
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry


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
        cet = pytz.timezone('CET')
        self.assertTrue(DT(datetime.datetime(2011, 11, 11, 11, 0, 0, tzinfo=cet)) ==
                        DateTime('2011/11/11 11:00:00 GMT+1'))

        # Python dates get converted to a DateTime with timecomponent including
        # a timezone
        self.assertTrue(DT(datetime.date(2011, 11, 11)) ==
                        DateTime('2011/11/11 00:00:00 UTC'))

        # DateTime with valid zone
        self.assertTrue(DT(DateTime(2011, 11, 11, 11, 0, 0, 'Europe/Vienna'))
                        == DateTime('2011/11/11 11:00:00 Europe/Vienna'))

        # Zope DateTime with valid DateTime zone but invalid pytz is kept as is
        self.assertTrue(DT(DateTime(2011, 11, 11, 11, 0, 0, 'GMT+1')) ==
                        DateTime('2011/11/11 11:00:00 GMT+1'))

        # Invalid datetime zones are converted to the portal timezone
        # Testing with no timezone
        self.assertTrue(DT(datetime.datetime(2011, 11, 11, 11, 0, 0)) ==
                        DateTime('2011/11/11 11:00:00 UTC'))



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
        res1 = get_portal_events(self.portal)
        self.assertTrue(len(res1) == 4)

        res2 = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.future)
        self.assertTrue(len(res2) == 4)

        res3 = get_portal_events(self.portal,
                                 range_end=self.future)
        self.assertTrue(len(res3) == 4)

        res4 = get_portal_events(self.portal,
                                 range_start=self.past)
        self.assertTrue(len(res4) == 4)


        # only on now-date
        res5 = get_portal_events(self.portal,
                                 range_start=self.now,
                                 range_end=self.now)
        self.assertTrue(len(res5) == 2)

        # only on past date
        res6 = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.past)
        self.assertTrue(len(res6) == 2)

        # one recurrence occurrence in future
        res7 = get_portal_events(self.portal,
                                 range_start=self.far,
                                 range_end=self.far)
        self.assertTrue(len(res7) == 1)

        # from now on
        res8 = get_portal_events(self.portal,
                                 range_start=self.now)
        self.assertTrue(len(res8) == 3)

        # until now
        res9 = get_portal_events(self.portal,
                                 range_end=self.now)
        self.assertTrue(len(res9) == 3)

    def test_get_occurrences(self):
        get_occurrences(object, [], range_start=datetime.datetime.today())

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
        res1 = get_portal_events(self.portal)
        self.assertTrue(len(res1) == 4)

        res2 = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.future)
        self.assertTrue(len(res2) == 4)

        res3 = get_portal_events(self.portal,
                                 range_end=self.future)
        self.assertTrue(len(res3) == 4)

        res4 = get_portal_events(self.portal,
                                 range_start=self.past)
        self.assertTrue(len(res4) == 4)


        # only on now-date
        res5 = get_portal_events(self.portal,
                                 range_start=self.now,
                                 range_end=self.now)
        self.assertTrue(len(res5) == 2)

        # only on past date
        res6 = get_portal_events(self.portal,
                                 range_start=self.past,
                                 range_end=self.past)
        self.assertTrue(len(res6) == 2)

        # one recurrence occurrence in future
        res7 = get_portal_events(self.portal,
                                 range_start=self.far,
                                 range_end=self.far)
        self.assertTrue(len(res7) == 1)

        # from now on
        res8 = get_portal_events(self.portal,
                                 range_start=self.now)
        self.assertTrue(len(res8) == 3)

        # until now
        res9 = get_portal_events(self.portal,
                                 range_end=self.now)
        self.assertTrue(len(res9) == 3)
