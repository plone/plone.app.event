# -*- coding: utf-8 -*-
from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from zope.component import getMultiAdapter


# TODO:
# * test all event properties
# * enforce correct order: EXDATE and RDATE directly after RRULE

def make_response(request):
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


class ICalendarExportTestDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
        return DXEventAccessor.create

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.failUnless(position >= 0,
                'menu item "%s" missing or out of order' % item)
            text = text[position:]

    def test_event_ical(self):
        headers, output, request = make_response(self.request)
        view = getMultiAdapter((self.now_event, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.checkOrder(icalstr,
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
            'CONTACT:Auto Testdriver\\, +123456789\\, testdriver@plone.org\\, http://plone',
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
        headers, output, request = make_response(self.request)
        view = getMultiAdapter((self.portal, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)

        self.checkOrder(icalstr,
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
            'CONTACT:Auto Testdriver\\, +123456789\\, testdriver@plone.org\\, http://plone',
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
