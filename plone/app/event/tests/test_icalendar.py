# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.event import base
from plone.app.event.dx.traverser import OccurrenceTraverser as OccTravDX
from plone.app.event.ical.importer import ical_import
from plone.app.event.testing import make_fake_response
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.event.interfaces import IEventAccessor
from zope.component import getMultiAdapter

import os
import pytz
import six
import unittest


# TODO:
# * test all event properties
# * enforce correct order: EXDATE and RDATE directly after RRULE
# TODO ical import browser tests


class ICalendarExportTestDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def traverser(self, context, request):
        return OccTravDX(context, request)

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.assertTrue(
                position >= 0,
                'menu item "%s" missing or out of order' % item
            )
            text = text[position:]

    def test_event_ical(self):
        headers, output, request = make_fake_response(self.request)
        view = getMultiAdapter((self.now_event, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        if six.PY3:
            output = [i.decode('utf8') for i in output]
        icalstr = ''.join(output)
        self.checkOrder(
            icalstr,
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Plone.org//NONSGML plone.app.event//EN',
            'X-WR-TIMEZONE:Europe/Vienna',
            'BEGIN:VEVENT',
            'SUMMARY:Now Event',
            'DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20130505T100000',
            'DTEND;TZID=Europe/Vienna;VALUE=DATE-TIME:20130505T110000',
            'DTSTAMP;VALUE=DATE-TIME:',
            'UID:',
            'RRULE:FREQ=DAILY;COUNT=3;INTERVAL=1',
            'RDATE;TZID=Europe/Vienna:20130509T000000',
            'EXDATE;TZID=Europe/Vienna:20130506T000000,20140404T000000',
            'CATEGORIES:plone,testing',
            'CONTACT:Auto Testdriver\\, +123456789\\, testdriver@plone.org\\, http://plone',  # noqa
            ' .org',  # line longer than max length spec by icalendar
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Vienna',
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

    def test_event_occurrence_ical(self):
        """A event occurrence should not conain recurrence definitions from
        it's parent.
        """
        headers, output, request = make_fake_response(self.request)
        occ = self.traverser(self.now_event, request).publishTraverse(
            request, '2013-05-07'
        )
        view = getMultiAdapter((occ, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        if six.PY3:
            output = [i.decode('utf8') for i in output]
        icalstr = ''.join(output)
        self.assertTrue('Now Event' in icalstr)
        self.assertTrue('RRULE' not in icalstr)

    def test_portal_ical(self):
        headers, output, request = make_fake_response(self.request)
        view = getMultiAdapter((self.portal, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        if six.PY3:
            output = [i.decode('utf8') for i in output]
        icalstr = ''.join(output)

        # No occurrences in export. Otherwise count would be 8.
        self.assertEqual(icalstr.count('BEGIN:VEVENT'), 4)
        self.checkOrder(
            icalstr,
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Plone.org//NONSGML plone.app.event//EN',
            'X-WR-TIMEZONE:Europe/Vienna',
            # whole_day event
            'BEGIN:VEVENT',
            'SUMMARY:Past Event',
            'DTSTART;VALUE=DATE:20130425',
            'DTEND;VALUE=DATE:20130426',
            'DTSTAMP;VALUE=DATE-TIME:',
            'UID:',
            'RRULE:FREQ=DAILY;COUNT=3',
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Vienna',
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
            'RRULE:FREQ=DAILY;COUNT=3;INTERVAL=1',
            'RDATE;TZID=Europe/Vienna:20130509T000000',
            'EXDATE;TZID=Europe/Vienna:20130506T000000,20140404T000000',
            'CATEGORIES:plone,testing',
            'CONTACT:Auto Testdriver\\, +123456789\\, testdriver@plone.org\\, http://plone',  # noqa
            ' .org',
            'CREATED;VALUE=DATE-TIME:',
            'LAST-MODIFIED;VALUE=DATE-TIME:',
            'LOCATION:Vienna',
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

    def test_event_listing_ical_portal(self):
        """Test event_listing ical export. It should contain all events from
        the listing, except Occurrences. For occurrences, their original events
        are exported.
        """
        headers, output, request = make_fake_response(self.request)
        view = getMultiAdapter(
            (self.portal, request), name='event_listing_ical'
        )
        view.mode = 'all'
        view()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        if six.PY3:
            output = [i.decode('utf8') for i in output]
        icalstr = ''.join(output)
        # No occurrences in export. Otherwise count would be 8.
        self.assertEqual(icalstr.count('BEGIN:VEVENT'), 4)

    def test_event_listing_ical_portal__specific_date(self):
        """Test event_listing ical export for a specific date. The date is when
        a occurrence happens. It shouldn't contain the occurrence but the
        original event and the long lasting event.
        """
        headers, output, request = make_fake_response(self.request)
        view = getMultiAdapter(
            (self.portal, request), name='event_listing_ical'
        )
        view.mode = 'day'
        view._date = '2013-04-27'
        view()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        if six.PY3:
            output = [i.decode('utf8') for i in output]
        icalstr = ''.join(output)
        self.assertEqual(icalstr.count('BEGIN:VEVENT'), 2)
        self.assertTrue('Past Event' in icalstr)
        self.assertTrue('Long Event' in icalstr)

    def test_collection_ical(self):
        """Test basic icalendar export from Collections.
        """
        headers, output, request = make_fake_response(self.request)
        view = getMultiAdapter(
            (self.portal.collection, request),
            name='ics_view'
        )
        view()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        if six.PY3:
            output = [i.decode('utf8') for i in output]
        icalstr = ''.join(output)
        self.assertEqual(icalstr.count('BEGIN:VEVENT'), 4)

    def test_collection_all_ical(self):
        """Test basic icalendar export from Collections, which returns not only
        events.
        """
        headers, output, request = make_fake_response(self.request)
        self.portal.collection.query = [
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.any',
             'v': ['Event', 'plone.app.event.dx.event', 'Page']
             },
        ]
        view = getMultiAdapter(
            (self.portal.collection, request),
            name='ics_view'
        )
        view()
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        if six.PY3:
            output = [i.decode('utf8') for i in output]
        icalstr = ''.join(output)
        self.assertEqual(icalstr.count('BEGIN:VEVENT'), 4)


class TestIcalImportDX(unittest.TestCase):
    layer = PAEventDX_FUNCTIONAL_TESTING
    event_type = 'plone.app.event.dx.event'

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_import_from_ics(self):
        # Ical import unit test.
        self.portal.invokeFactory('Folder', 'impfolder1')
        impfolder = self.portal.impfolder1

        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'icaltest.ics'), 'rb') as icsfile:
            icsdata = icsfile.read()
        res = ical_import(impfolder, icsdata, self.event_type)

        self.assertEqual(res['count'], 5)
        self.assertEqual(len(impfolder.contentIds()), 5)

        at = pytz.timezone('Europe/Vienna')
        utc = pytz.utc

        # Use pydt to normalize for DST times.

        # TODO: test for attendees. see note in
        # plone.app.event.ical.importer.ical_import
        e1 = IEventAccessor(impfolder.e1)
        self.assertEqual(
            e1.start,
            at.localize(datetime(2013, 7, 19, 12, 0))
        )
        self.assertEqual(
            e1.end,
            at.localize(datetime(2013, 7, 20, 13, 0))
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
        self.assertEqual(
            e1.sync_uid,
            u'48f1a7ad64e847568d860cd092344970',
        )

        e2 = IEventAccessor(impfolder.e2)
        self.assertEqual(
            e2.start,
            utc.localize(datetime(1996, 4, 1, 1, 0))
        )
        self.assertEqual(
            e2.end,
            utc.localize(datetime(1996, 4, 1, 2, 0))
        )
        self.assertEqual(
            e2.recurrence,
            u'RRULE:FREQ=DAILY;COUNT=100\nEXDATE:19960402T010000Z,'
            u'19960403T010000Z,19960404T010000Z'
        )

        e3 = IEventAccessor(impfolder.e3)
        self.assertEqual(
            e3.start,
            at.localize(datetime(2012, 3, 27, 10, 0))
        )
        self.assertEqual(
            e3.end,
            at.localize(datetime(2012, 3, 27, 18, 0))
        )
        self.assertEqual(
            e3.recurrence,
            u'RRULE:FREQ=WEEKLY;UNTIL=20120703T080000Z;BYDAY=TU\n'
            u'EXDATE:20120529T100000,20120403T100000,20120410T100000,'
            u'20120501T100000,20120417T100000'
        )

        e4 = IEventAccessor(impfolder.e4)
        self.assertEqual(
            e4.start,
            utc.localize(datetime(2013, 4, 4, 0, 0))
        )
        self.assertEqual(
            e4.end,
            utc.localize(datetime(2013, 4, 4, 23, 59, 59))
        )
        self.assertEqual(
            e4.whole_day,
            True
        )
        self.assertEqual(
            e4.open_end,
            False
        )

        e5 = IEventAccessor(impfolder.e5)
        self.assertEqual(
            e5.start,
            utc.localize(datetime(2013, 4, 2, 12, 0))
        )
        self.assertEqual(
            e5.end,
            utc.localize(datetime(2013, 4, 2, 23, 59, 59))
        )
        self.assertEqual(
            e5.whole_day,
            False
        )
        self.assertEqual(
            e5.open_end,
            True
        )

    def test_import_from_ics__no_sync(self):
        """SYNC_NONE and importing the same file again should create new event
        objects and give them each a new sync_uid.
        """
        self.portal.invokeFactory('Folder', 'impfolder2')
        impfolder = self.portal.impfolder2

        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'icaltest.ics'), 'rb') as icsfile:
            icsdata = icsfile.read()

        res = ical_import(impfolder, icsdata, self.event_type)

        self.assertEqual(res['count'], 5)

        e11 = impfolder['e1']
        suid1 = IEventAccessor(e11).sync_uid

        res = ical_import(impfolder, icsdata, self.event_type,
                          sync_strategy=base.SYNC_NONE)
        self.assertEqual(res['count'], 5)

        e12 = impfolder['e1-1']
        suid2 = IEventAccessor(e12).sync_uid

        self.assertEqual(len(impfolder.contentIds()), 10)
        self.assertNotEqual(suid1, suid2)

    def test_import_from_ics__sync_keep_mine(self):
        """SYNC_KEEP_MINE and importing the same file again should do nothing.
        """
        self.portal.invokeFactory('Folder', 'impfolder3')
        impfolder = self.portal.impfolder3

        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'icaltest.ics'), 'rb') as icsfile:
            icsdata = icsfile.read()

        res = ical_import(impfolder, icsdata, self.event_type)
        self.assertEqual(res['count'], 5)

        e1a = IEventAccessor(impfolder.e1)
        mod1 = e1a.last_modified
        suid1 = e1a.sync_uid

        res = ical_import(impfolder, icsdata, self.event_type,
                          sync_strategy=base.SYNC_KEEP_MINE)
        self.assertEqual(res['count'], 0)
        e1a = IEventAccessor(impfolder.e1)
        mod2 = e1a.last_modified
        suid2 = e1a.sync_uid

        self.assertEqual(len(impfolder.contentIds()), 5)

        self.assertEqual(mod1, mod2)
        self.assertEqual(suid1, suid2)

    def test_import_from_ics__sync_drop_older(self):
        """SYNC_KEEP_NEWER and importing the same file again should update only
        newer and on equal modified date but drop the change when it is older.
        """
        self.portal.invokeFactory('Folder', 'impfolder4')
        impfolder = self.portal.impfolder4

        directory = os.path.dirname(__file__)
        with open(os.path.join(directory, 'icaltest.ics'), 'rb') as icsfile:
            icsdata1 = icsfile.read()

        with open(os.path.join(directory, 'icaltest2.ics'), 'rb') as icsfile:
            icsdata2 = icsfile.read()

        res = ical_import(impfolder, icsdata1, self.event_type)
        self.assertEqual(res['count'], 5)

        e1a = IEventAccessor(impfolder.e1)
        mod1 = e1a.last_modified
        suid1 = e1a.sync_uid
        title1 = e1a.title
        desc1 = e1a.description
        start1 = e1a.start
        end1 = e1a.end

        res = ical_import(impfolder, icsdata2, self.event_type,
                          sync_strategy=base.SYNC_KEEP_NEWER)
        self.assertEqual(res['count'], 4)
        e1a = IEventAccessor(impfolder.e1)
        mod2 = e1a.last_modified
        suid2 = e1a.sync_uid
        title2 = e1a.title
        desc2 = e1a.description
        start2 = e1a.start
        end2 = e1a.end

        self.assertEqual(len(impfolder.contentIds()), 5)

        self.assertTrue(mod1 < mod2)
        self.assertEqual(suid1, suid2)
        self.assertNotEqual(title1, title2)
        self.assertNotEqual(desc1, desc2)
        self.assertTrue(start1 < start2)
        self.assertTrue(end1 < end2)

    def test_import_from_ics__sync_keep_theirs(self):
        """SYNC_KEEP_THEIRS and importing the same file again should update
        all.
        """
        self.portal.invokeFactory('Folder', 'impfolder5')
        impfolder = self.portal.impfolder5

        directory = os.path.dirname(__file__)

        with open(os.path.join(directory, 'icaltest.ics'), 'rb') as icsfile:
            icsdata1 = icsfile.read()

        with open(os.path.join(directory, 'icaltest2.ics'), 'rb') as icsfile:
            icsdata2 = icsfile.read()

        res = ical_import(impfolder, icsdata1, self.event_type)
        self.assertEqual(res['count'], 5)

        e1a = IEventAccessor(impfolder.e1)
        mod11 = e1a.last_modified
        suid11 = e1a.sync_uid
        title11 = e1a.title
        desc11 = e1a.description
        start11 = e1a.start
        end11 = e1a.end

        e2a = IEventAccessor(impfolder.e2)
        suid21 = e2a.sync_uid
        title21 = e2a.title
        desc21 = e2a.description
        start21 = e2a.start
        end21 = e2a.end

        res = ical_import(impfolder, icsdata2, self.event_type,
                          sync_strategy=base.SYNC_KEEP_THEIRS)
        self.assertEqual(res['count'], 5)

        e1a = IEventAccessor(impfolder.e1)
        mod12 = e1a.last_modified
        suid12 = e1a.sync_uid
        title12 = e1a.title
        desc12 = e1a.description
        start12 = e1a.start
        end12 = e1a.end

        e2a = IEventAccessor(impfolder.e2)
        suid22 = e2a.sync_uid
        title22 = e2a.title
        desc22 = e2a.description
        start22 = e2a.start
        end22 = e2a.end

        self.assertEqual(len(impfolder.contentIds()), 5)

        self.assertTrue(mod11 < mod12)
        self.assertEqual(suid11, suid12)
        self.assertNotEqual(title11, title12)
        self.assertNotEqual(desc11, desc12)
        self.assertTrue(start11 < start12)
        self.assertTrue(end11 < end12)

        self.assertEqual(suid21, suid22)
        self.assertNotEqual(title21, title22)
        self.assertNotEqual(desc21, desc22)
        self.assertTrue(start21 < start22)
        self.assertTrue(end21 < end22)
