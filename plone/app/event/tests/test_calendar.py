# -*- coding: utf-8 -*-
from zope.component import getMultiAdapter
from plone.app.event.interfaces import IEvent

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


class CalendarTest(unittest.TestCase):
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

        self.portal = portal

    def testCalendarView(self):
        view = getMultiAdapter((self.portal.events, self.request), name='ics_view')
        events = view.getEvents()
        self.assertEqual(len(events), 2)
        self.assertEqual(sorted([e.Title() for e in events]),
            ['Plone Conf 2007', 'Plone Conf 2008'])

    def testCalendarViewForTopic(self):
        portal = self.portal
        portal.invokeFactory('Topic', id='calendar')
        topic = portal['calendar']
        crit = topic.addCriterion('SearchableText', 'ATSimpleStringCriterion')
        crit.setValue('DC')
        view = getMultiAdapter((topic, self.request), name='ics_view')
        events = view.getEvents()
        self.assertEqual(len(events), 1)
        self.assertEqual(
                sorted([e.Title() for e in events]),
                ['Plone Conf 2008'])
        portal.invokeFactory('Event',
            id='inaug09', title='Inauguration Day 2009',
            startDate='2009/01/20', endDate='2009/01/20', location='DC')
        events = view.getEvents()
        self.assertEqual(len(events), 2)
        self.assertEqual(sorted([e.Title() for e in events]),
            ['Inauguration Day 2009', 'Plone Conf 2008'])

    def testDuplicateQueryParameters(self):
        portal = self.portal
        portal.invokeFactory('Topic', id='dc')
        topic = portal['dc']
        crit = topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Event')
        crit = topic.addCriterion('object_provides', 'ATSimpleStringCriterion')
        crit.setValue(IEvent.__identifier__)
        query = topic.buildQuery()
        self.assertEqual(len(query), 2)
        self.assertEqual(query['portal_type'], 'Event')
        self.assertEqual(query['object_provides'], IEvent.__identifier__)
        view = getMultiAdapter((topic, self.request), name='ics_view')
        events = view.getEvents()
        self.assertEqual(len(events), 2)
        self.assertEqual(sorted([e.Title() for e in view.getEvents()]),
            ['Plone Conf 2007', 'Plone Conf 2008'])

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.failUnless(position >= 0,
                'menu item "%s" missing or out of order' % item)
            text = text[position:]

    def testRendering(self):
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((self.portal.events, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'LOCATION:Naples',
            'SUMMARY:Plone Conf 2007',
            'URL:http://plone.org/events/conferences/2007-naples',
            'END:VEVENT',
            'BEGIN:VEVENT',
            'LOCATION:DC',
            'SUMMARY:Plone Conf 2008',
            'END:VEVENT',
            'END:VCALENDAR')

    def testCalendarInfo(self):
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

    def testRenderingForTopic(self):
        portal = self.portal
        portal.invokeFactory('Topic', id='calendar')
        topic = portal['calendar']
        crit = topic.addCriterion('SearchableText', 'ATSimpleStringCriterion')
        crit.setValue('DC')
        headers, output, request = makeResponse(self.request)
        view = getMultiAdapter((topic, request), name='ics_view')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'LOCATION:DC',
            'SUMMARY:Plone Conf 2008',
            'URL:http://plone.org/events/conferences/2008-washington-dc',
            'END:VEVENT',
            'END:VCALENDAR')
        lines = ''.join(output).splitlines()
        self.assertEqual(len([l for l in lines if l == 'BEGIN:VEVENT']), 1)
