# -*- coding: utf-8 -*-
from datetime import datetime
from plone.app.event.testing import PAEventATDX_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEventAccessor
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import unittest2 as unittest


# TODO:
# * test all event properties
# * enforce correct order: EXDATE and RDATE directly after RRULE

def makeResponse(request):
    """ create a fake response and set up logging of output """
    headers = {}
    output = []
    class Response:
        def setHeader(self, header, value):
            headers[header] = value
        def write(self, msg):
            output.append(msg)
    request.RESPONSE = Response()
    return headers, output, request


class ICalendarExportTest(unittest.TestCase):
    layer = PAEventATDX_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])

        portal.invokeFactory('Folder',
                id='events', title=u"Events",
                Description=u"The portal's Events")

        portal.events.invokeFactory('Event',
            id='ploneconf2007', title='Plone Conf 2007',
            startDate='2007/10/10', endDate='2007/10/12',
            location='Naples',
            eventUrl='http://plone.org/events/conferences/2007-naples',
            attendees=['anne','bob','cesar'])

        portal.events.invokeFactory('Event',
            id='ploneconf2008', title='Plone Conf 2008',
            startDate='2008/10/08', endDate='2008/10/10', location='DC',
            recurrence=u'RRULE:FREQ=DAILY;COUNT=5\r\nEXDATE:20081011T000000,20081012T000000\r\nRDATE:20081007T000000',
            eventUrl='http://plone.org/events/conferences/2008-washington-dc')

        portal.events.invokeFactory('plone.app.event.dx.event',
            id='ploneconf2012', title='Plone Conf 2012',
            recurrence=u'RRULE:FREQ=DAILY;COUNT=5\r\nEXDATE:20121013T000000,20121014T000000\r\nRDATE:20121009T000000',
            start=datetime(2012,10,10,8,0),
            end=datetime(2012,10,10,18,0),
            timezone='Europe/Amsterdam')
        pc12 = IEventAccessor(portal.events.ploneconf2012)
        pc12.location = 'Arnhem'
        pc12.contact_name = 'Four Digits'
        pc12.contact_email = 'info@ploneconf.org'
        pc12.contact_phone = '+123456789'
        pc12.event_url = 'http://ploneconf.org'
        pc12.subjects = ['plone', 'conference',]
        notify(ObjectModifiedEvent(portal.events.ploneconf2012))

        portal.events.invokeFactory('plone.app.event.dx.event',
            id='artsprint2013', title='Artsprint 2013',
            start=datetime(2013,2,18),
            end=datetime(2013,2,22),
            whole_day=True,
            timezone='Europe/Vienna')

        # Standard Time
        portal.events.invokeFactory('plone.app.event.dx.event',
            id='standardtime', title='Standard Time',
            start=datetime(2013,12,24,12,0),
            end=datetime(2013,12,29,12,0),
            open_end=True,
            timezone='Europe/Vienna'
            )

        portal.invokeFactory("Collection",
                             "collection",
                             title="New Collection",
                             sort_on='start')
        portal['collection'].setQuery([{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'Event',
        }, ])

        self.portal = portal

    def testCollectionResult(self):
        collection = self.portal['collection']
        results = collection.results()
        # Should find Archetypes and Dexterity events
        self.assertEqual(results.length, 5)

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.failUnless(position >= 0,
                'menu item "%s" missing or out of order' % item)
            text = text[position:]

    def testEventDXICal(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.events.ploneconf2012, request),
                                name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.checkOrder(icalstr,
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2012',
            'DTSTART;TZID=Europe/Amsterdam;VALUE=DATE-TIME:20121010T080000',
            'DTEND;TZID=Europe/Amsterdam;VALUE=DATE-TIME:20121010T180000',
            'UID:',
            'RDATE;TZID=Europe/Amsterdam:20121009T000000',
            'EXDATE;TZID=Europe/Amsterdam:20121013T000000,20121014T000000',
            'CATEGORIES:plone',
            'CATEGORIES:conference',
            'CONTACT:Four Digits\\, +123456789\\, info@ploneconf.org\\, http://ploneconf.o\r\n rg\r\n',
            'LOCATION:Arnhem',
            'RRULE:FREQ=DAILY;COUNT=5',
            'URL:http://nohost/plone/events/ploneconf2012',
            'END:VEVENT',
            'BEGIN:VTIMEZONE',
            'TZID:Europe/Amsterdam',
            'X-LIC-LOCATION:Europe/Amsterdam',
            'BEGIN:DAYLIGHT',
            'DTSTART;VALUE=DATE-TIME:20120325T030000',
            'TZNAME:CEST',
            'TZOFFSETFROM:+0100',
            'TZOFFSETTO:+0200',
            'END:DAYLIGHT',
            'END:VTIMEZONE',
            'END:VCALENDAR')

    def testEventStandardTime(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.events.standardtime, request),
                                name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.checkOrder(icalstr,
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'SUMMARY:Standard Time',
            'DTSTART;TZID=Europe/Vienna;VALUE=DATE-TIME:20131224T120000',
            'URL:http://nohost/plone/events/standardtime',
            'END:VEVENT',
            'BEGIN:VTIMEZONE',
            'TZID:Europe/Vienna',
            'X-LIC-LOCATION:Europe/Vienna',
            'BEGIN:STANDARD',
            'DTSTART;VALUE=DATE-TIME:20131027T020000',
            'TZNAME:CET',
            'TZOFFSETFROM:+0200',
            'TZOFFSETTO:+0100',
            'END:STANDARD',
            'END:VTIMEZONE',
            'END:VCALENDAR',
        )


    def testWholeDayICal(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.events.artsprint2013, request),
                                name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)
        self.checkOrder(icalstr,
            'BEGIN:VCALENDAR',
            'X-WR-CALNAME:Artsprint 2013',
            'BEGIN:VEVENT',
            'SUMMARY:Artsprint 2013',
            'DTSTART;VALUE=DATE:20130218',
            'DTEND;VALUE=DATE:20130223',
            'END:VEVENT',
            'END:VCALENDAR')

    def testEventICal(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.events.ploneconf2007, request),
                                name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)
        self.checkOrder(icalstr,
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2007',
            'DTSTART;VALUE=DATE-TIME:20071010T000000Z',
            'DTEND;VALUE=DATE-TIME:20071012T000000Z',
            'ATTENDEE;CN=anne;ROLE=REQ-PARTICIPANT:anne',
            'ATTENDEE;CN=bob;ROLE=REQ-PARTICIPANT:bob',
            'ATTENDEE;CN=cesar;ROLE=REQ-PARTICIPANT:cesar',
            'END:VEVENT',
            'END:VCALENDAR')

    def testCollectionICal(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.collection, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.assertTrue(
            'URL:http://nohost/plone/events/ploneconf2007' in icalstr)
        self.assertTrue(
            'URL:http://nohost/plone/events/ploneconf2008' in icalstr)
        self.assertTrue(
            'URL:http://nohost/plone/events/ploneconf2012' in icalstr)

        self.assertTrue(
            'CONTACT:http://plone.org/events/conferences/2008-washington-dc' in
            icalstr)

        self.checkOrder(icalstr,
            'BEGIN:VCALENDAR',
            'X-WR-CALNAME:New Collection',
            'X-WR-TIMEZONE:UTC',

            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2007',
            'DTSTART;VALUE=DATE-TIME:20071010T000000Z',
            'DTEND;VALUE=DATE-TIME:20071012T000000Z',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2008',
            'DTSTART;VALUE=DATE-TIME:20081008T000000Z',
            'DTEND;VALUE=DATE-TIME:20081010T000000Z',
            'RDATE:20081007T000000Z',
            'EXDATE:20081011T000000Z,20081012T000000Z',
            'RRULE:FREQ=DAILY;COUNT=5',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2012',
            'DTSTART;TZID=Europe/Amsterdam;VALUE=DATE-TIME:20121010T080000',
            'DTEND;TZID=Europe/Amsterdam;VALUE=DATE-TIME:20121010T180000',
            'RDATE;TZID=Europe/Amsterdam:20121009T000000',
            'EXDATE;TZID=Europe/Amsterdam:20121013T000000,20121014T000000',
            'RRULE:FREQ=DAILY;COUNT=5',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Artsprint 2013',
            'DTSTART;VALUE=DATE:20130218',
            'DTEND;VALUE=DATE:20130223',
            'END:VEVENT',

            'BEGIN:VTIMEZONE',
            'TZID:Europe/Amsterdam',
            'BEGIN:DAYLIGHT',
            'DTSTART;VALUE=DATE-TIME:20120325T030000',
            'TZNAME:CEST',
            'TZOFFSETFROM:+0100',
            'TZOFFSETTO:+0200',
            'END:DAYLIGHT',
            'END:VTIMEZONE',

            'END:VCALENDAR')

    def testFolderICal(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.events, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.checkOrder(icalstr,
            'BEGIN:VCALENDAR',
            'X-WR-CALNAME:Events',
            'X-WR-TIMEZONE:UTC',

            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2007',
            'DTSTART;VALUE=DATE-TIME:20071010T000000Z',
            'DTEND;VALUE=DATE-TIME:20071012T000000Z',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2008',
            'DTSTART;VALUE=DATE-TIME:20081008T000000Z',
            'DTEND;VALUE=DATE-TIME:20081010T000000Z',
            'RDATE:20081007T000000Z',
            'EXDATE:20081011T000000Z,20081012T000000Z',
            'RRULE:FREQ=DAILY;COUNT=5',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2012',
            'DTSTART;TZID=Europe/Amsterdam;VALUE=DATE-TIME:20121010T080000',
            'DTEND;TZID=Europe/Amsterdam;VALUE=DATE-TIME:20121010T180000',
            'RDATE;TZID=Europe/Amsterdam:20121009T000000',
            'EXDATE;TZID=Europe/Amsterdam:20121013T000000,20121014T000000',
            'RRULE:FREQ=DAILY;COUNT=5',
            'END:VEVENT',

            'BEGIN:VEVENT',
            'SUMMARY:Artsprint 2013',
            'DTSTART;VALUE=DATE:20130218',
            'DTEND;VALUE=DATE:20130223',
            'END:VEVENT',

            'BEGIN:VTIMEZONE',
            'TZID:Europe/Amsterdam',
            'BEGIN:DAYLIGHT',
            'DTSTART;VALUE=DATE-TIME:20120325T030000',
            'TZNAME:CEST',
            'TZOFFSETFROM:+0100',
            'TZOFFSETTO:+0200',
            'END:DAYLIGHT',
            'END:VTIMEZONE',

            'END:VCALENDAR')

    def testFolderICalInfo(self):
        events = self.portal.events
        events.processForm(values={'title': 'Foo', 'description': 'Bar'})
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((events, request), name='ics_view')
        view()
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'X-WR-CALDESC:Bar',
            'X-WR-CALNAME:Foo',
            'BEGIN:VEVENT',
            'BEGIN:VEVENT',
            'END:VCALENDAR')

        # another folder should have another name, even though the set
        # of events might be the same...
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal, request), name='ics_view')
        view()
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'X-WR-CALNAME:Plone site',
            'BEGIN:VEVENT',
            'BEGIN:VEVENT',
            'END:VCALENDAR')
        self.assertTrue('X-WR-CALDESC' not in ''.join(output))

        # changing the title should be immediately reflected...
        events.processForm(values={'title': u'Föö!!'})
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((events, request), name='ics_view')
        view()
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'X-WR-CALDESC:Bar',
            'X-WR-CALNAME:Föö!!',
            'BEGIN:VEVENT',
            'BEGIN:VEVENT',
            'END:VCALENDAR')
