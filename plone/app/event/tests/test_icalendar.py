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
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class ICalendarExportTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

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
                eventUrl='http://plone.org/events/conferences/2007-naples')
        self.event1 = portal.events['ploneconf2007']

        portal.events.invokeFactory('Event',
            id='ploneconf2008', title='Plone Conf 2008',
            startDate='2008/10/08', endDate='2008/10/10', location='DC',
            eventUrl='http://plone.org/events/conferences/2008-washington-dc')
        self.event2 = portal.events['ploneconf2008']

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
            'VALUE=DATE-TIME:20071010T000000Z',
            'DTEND;VALUE=DATE-TIME:20071012T000000Z',
            'END:VEVENT',
            'END:VCALENDAR')

    def testCollectionICal(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.collection, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)
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
