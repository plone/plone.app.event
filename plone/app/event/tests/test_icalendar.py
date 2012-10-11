# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter

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


import unittest2 as unittest
from plone.app.event.testing import PAEventATDX_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from datetime import datetime

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
            eventUrl='http://plone.org/events/conferences/2008-washington-dc')

        portal.events.invokeFactory('plone.app.event.dx.event',
            id='ploneconf2012', title='Plone Conf 2012',
            start=datetime(2012,10,10,8,0),
            end=datetime(2012,10,12,18,0),
            timezone="Europe/Amsterdam",
            location='Arnhem')

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
        self.assertTrue(results.length == 2)

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
            'DTSTART;VALUE=DATE-TIME:20121010T060000Z',
            'DTEND;VALUE=DATE-TIME:20121012T160000Z',
            'UID:',
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
        # TODO: there is a side effect when running all tests, where this one fails.
        # icalstr when running all tests is:
        # 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Plone.org//NONSGML plone.app.event//EN\r\nX-WR-CALNAME:Plone Conf 2007\r\nX-WR-RELCALID:68c3f018da8940dc87b4631f64b9a0a9\r\nX-WR-TIMEZONE:Atlantic/Bermuda\r\nBEGIN:VEVENT\r\nSUMMARY:Plone Conf 2007\r\nDTSTART;VALUE=DATE-TIME:20071010T030000Z\r\nDTEND;VALUE=DATE-TIME:20071012T030000Z\r\nDTSTAMP;VALUE=DATE-TIME:20121009T165501Z\r\nUID:68c3f018da8940dc87b4631f64b9a0a9\r\nCONTACT:http://plone.org/events/conferences/2007-naples\r\nCREATED;VALUE=DATE-TIME:20121009T145501Z\r\nLAST-MODIFIED;VALUE=DATE-TIME:20121009T145501Z\r\nLOCATION:Naples\r\nURL:http://nohost/plone/events/ploneconf2007\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n'
        # maybe there is somewhere a timezone set, but not reset?
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
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2007',
            'END:VEVENT',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2008',
            'END:VEVENT',
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
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2007',
            'END:VEVENT',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2008',
            'END:VEVENT',
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
