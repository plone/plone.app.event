# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.ical.importer import ical_import
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import make_fake_response
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEventAccessor
from plone.event.utils import pydt
from zope.component import getMultiAdapter

import os
import pytz
import unittest2 as unittest


# TODO:
# * test all event properties
# * enforce correct order: EXDATE and RDATE directly after RRULE


class ICalendarExportTestDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
        return DXEventAccessor.create

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.failUnless(
                position >= 0,
                'menu item "%s" missing or out of order' % item
            )
            text = text[position:]

    def test_event_ical(self):
        headers, output, request = make_fake_response(self.request)
        view = getMultiAdapter((self.now_event, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.checkOrder(
            icalstr,
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Plone.org//NONSGML plone.app.event//EN',
            'X-WR-CALNAME:Now Event',  # calendar name == event title
            'X-WR-RELCALID:',
            'X-WR-TIMEZONE:Europe/Vienna',
            'BEGIN:VEVENT',
            'SUMMARY:Now Event',
            'DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130505T100000',
            'DTEND;TZID=Europe/Vienna;VALUE=DATE-TIME:20130505T110000',
            'DTSTAMP;VALUE=DATE-TIME:',
            'UID:',
            'RDATE;TZID=Europe/Vienna:20130509T000000',
            'EXDATE;TZID=Europe/Vienna:20130506T000000,20140404T000000',
            'CATEGORIES:plone',
            'CATEGORIES:testing',
            'CONTACT:Auto Testdriver\\, +123456789\\, testdriver@plone.org\\, '
            'http://plone',  # continuation of line above
            ' .org',  # line longer than max length spec by icalendar
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Vienna',
            'RRULE:FREQ=DAILY;COUNT=3;INTERVAL=1',
            'URL:http://nohost/plone/now',
            'END:VEVENT',
            'BEGIN:VTIMEZONE',
            'TZID:Europe/Vienna',
            'X-LIC-LOCATION:Europe/Vienna',
            'BEGIN:DAYLIGHT',
            'DTSTART;VALUE=DATE-TIME:20130331T030000',
            'TZNAME:CEST',
            'TZOFFSETFROM:+0100',
            'TZOFFSETTO:+0200',
            'END:DAYLIGHT',
            'END:VTIMEZONE',
            'END:VCALENDAR')

    def test_portal_ical(self):
        headers, output, request = make_fake_response(self.request)
        view = getMultiAdapter((self.portal, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.checkOrder(
            icalstr,
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Plone.org//NONSGML plone.app.event//EN',
            'X-WR-CALNAME:Plone site',  # calendar name == plone site title
            'X-WR-TIMEZONE:Europe/Vienna',
            # whole_day event
            'BEGIN:VEVENT',
            'SUMMARY:Past Event',
            'DTSTART;VALUE=DATE:20130425',
            'DTEND;VALUE=DATE:20130426',
            'DTSTAMP;VALUE=DATE-TIME:',
            'UID:',
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Vienna',
            'RRULE:FREQ=DAILY;COUNT=3',
            'URL:http://nohost/plone/past',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Long Event',
            'DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130425T100000',
            'DTEND;TZID=Europe/Vienna;VALUE=DATE-TIME:20130604T100000',
            'DTSTAMP;VALUE=DATE-TIME:',
            'UID:',
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Schaftal',
            'URL:http://nohost/plone/sub/long',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Now Event',
            'DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130505T100000',
            'DTEND;TZID=Europe/Vienna;VALUE=DATE-TIME:20130505T110000',
            'DTSTAMP;VALUE=DATE-TIME:',
            'UID:',
            'RDATE;TZID=Europe/Vienna:20130509T000000',
            'EXDATE;TZID=Europe/Vienna:20130506T000000,20140404T000000',
            'CATEGORIES:plone',
            'CATEGORIES:testing',
            'CONTACT:Auto Testdriver\\, +123456789\\, testdriver@plone.org\\, '
            'http://plone',  # continuation of line above
            ' .org',
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Vienna',
            'RRULE:FREQ=DAILY;COUNT=3;INTERVAL=1',
            'URL:http://nohost/plone/now',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Future Event',
            'DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130515T100000',
            'DTEND;TZID=Europe/Vienna;VALUE=DATE-TIME:20130515T110000',
            'DTSTAMP;VALUE=DATE-TIME:',
            'UID:',
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Graz',
            'URL:http://nohost/plone/future',
            'END:VEVENT',

            'BEGIN:VTIMEZONE',
            'TZID:Europe/Vienna',
            'X-LIC-LOCATION:Europe/Vienna',
            'BEGIN:DAYLIGHT',
            'DTSTART;VALUE=DATE-TIME:20130331T030000',
            'TZNAME:CEST',
            'TZOFFSETFROM:+0100',
            'TZOFFSETTO:+0200',
            'END:DAYLIGHT',
            'END:VTIMEZONE',
            'END:VCALENDAR')


class ICalendarExportTestAT(ICalendarExportTestDX):
    layer = PAEventAT_INTEGRATION_TESTING

    def event_factory(self):
        return ATEventAccessor.create


class TestIcalImportDX(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'impfolder')
        self.impfolder = self.portal.impfolder

    def test_import_from_ics(self):
        # Ical import unit test.

        directory = os.path.dirname(__file__)
        icsfile = open(os.path.join(directory, 'icaltest.ics'), 'rb').read()
        res = ical_import(self.impfolder, icsfile, 'plone.app.event.dx.event')

        self.assertEqual(res['count'], 5)

        at = pytz.timezone('Europe/Vienna')
        utc = pytz.utc

        # Use pydt to normalize for DST times.

        # TODO: test for attendees. see note in
        # plone.app.event.ical.importer.ical_import
        e1 = IEventAccessor(self.impfolder.e1)
        self.assertEqual(
            e1.start,
            pydt(datetime(2013, 7, 19, 12, 0, tzinfo=at))
        )
        self.assertEqual(
            e1.end,
            pydt(datetime(2013, 7, 20, 13, 0, tzinfo=at))
        )
        self.assertEqual(
            e1.description,
            'A basic event with many properties.'
        )
        self.assertEqual(
            e1.whole_day,
            False
        )
        self.assertEqual(
            e1.open_end,
            False
        )

        e2 = IEventAccessor(self.impfolder.e2)
        self.assertEqual(
            e2.start,
            pydt(datetime(1996, 4, 1, 1, 0, tzinfo=utc))
        )
        self.assertEqual(
            e2.end,
            pydt(datetime(1996, 4, 1, 2, 0, tzinfo=utc))
        )
        self.assertEqual(
            e2.recurrence,
            u'RRULE:FREQ=DAILY;COUNT=100\nEXDATE:19960402T010000Z,'
            u'19960403T010000Z,19960404T010000Z'
        )

        e3 = IEventAccessor(self.impfolder.e3)
        self.assertEqual(
            e3.start,
            pydt(datetime(2012, 3, 27, 10, 0, tzinfo=at))
        )
        self.assertEqual(
            e3.end,
            pydt(datetime(2012, 3, 27, 18, 0, tzinfo=at))
        )
        self.assertEqual(
            e3.recurrence,
            u'RRULE:FREQ=WEEKLY;UNTIL=20120703T080000Z;BYDAY=TU\n'
            u'EXDATE:20120529T100000,20120403T100000,20120410T100000,'
            u'20120501T100000,20120417T100000'
        )

        e4 = IEventAccessor(self.impfolder.e4)
        self.assertEqual(
            e4.start,
            pydt(datetime(2013, 4, 4, 0, 0, tzinfo=utc))
        )
        self.assertEqual(
            e4.end,
            pydt(datetime(2013, 4, 4, 23, 59, 59, tzinfo=utc))
        )
        self.assertEqual(
            e4.whole_day,
            True
        )
        self.assertEqual(
            e4.open_end,
            False
        )

        e5 = IEventAccessor(self.impfolder.e5)
        self.assertEqual(
            e5.start,
            pydt(datetime(2013, 4, 2, 12, 0, tzinfo=utc))
        )
        self.assertEqual(
            e5.end,
            pydt(datetime(2013, 4, 2, 23, 59, 59, tzinfo=utc))
        )
        self.assertEqual(
            e5.whole_day,
            False
        )
        self.assertEqual(
            e5.open_end,
            True
        )

    # TODO ical import browser tests
