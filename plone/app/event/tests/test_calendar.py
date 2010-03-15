# -*- coding: utf-8 -*-

from unittest import defaultTestLoader
from zope.interface import classImplements
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest
from zope.annotation.interfaces import IAttributeAnnotatable

from Products.ATContentTypes.tests.atcttestcase import ATCTSiteTestCase
from Products.ATContentTypes.interfaces import ICalendarSupport
from Products.ATContentTypes.browser.calendar import cachekey


def makeResponse(request):
    """ create a fake request and set up logging of output """
    headers = {}
    output = []
    class Response:
        def setHeader(self, header, value):
            headers[header] = value
        def write(self, msg):
            output.append(msg)
    request.RESPONSE = Response()
    return headers, output, request


class EventCalendarTests(ATCTSiteTestCase):

    def afterSetUp(self):
        folder = self.folder
        event1 = folder[folder.invokeFactory('Event',
            id='ploneconf2007', title='Plone Conf 2007',
            startDate='2007/10/10', endDate='2007/10/12', location='Naples',
            eventUrl='http://plone.org/events/conferences/2007-naples')]
        event2 = folder[folder.invokeFactory('Event',
            id='ploneconf2008', title='Plone Conf 2008',
            startDate='2008/10/08', endDate='2008/10/10', location='DC',
            eventUrl='http://plone.org/events/conferences/2008-washington-dc')]
        classImplements(TestRequest, IAttributeAnnotatable)

    def testCalendarView(self):
        view = getMultiAdapter((self.folder, TestRequest()), name='ics_view')
        view.update()
        self.assertEqual(len(view.events), 2)
        self.assertEqual(sorted([ e.Title for e in view.events ]),
            ['Plone Conf 2007', 'Plone Conf 2008'])

    def testCalendarViewForTopic(self):
        self.setRoles(('Manager',))
        folder = self.folder
        topic = self.folder[self.folder.invokeFactory('Topic', id='dc')]
        crit = topic.addCriterion('SearchableText', 'ATSimpleStringCriterion')
        crit.setValue('DC')
        view = getMultiAdapter((topic, TestRequest()), name='ics_view')
        view.update()
        self.assertEqual(len(view.events), 1)
        self.assertEqual(sorted([ e.Title for e in view.events ]),
            ['Plone Conf 2008'])
        folder[folder.invokeFactory('Event',
            id='inaug09', title='Inauguration Day 2009',
            startDate='2009/01/20', endDate='2009/01/20', location='DC')]
        view.update()
        self.assertEqual(len(view.events), 2)
        self.assertEqual(sorted([ e.Title for e in view.events ]),
            ['Inauguration Day 2009', 'Plone Conf 2008'])

    def testDuplicateQueryParameters(self):
        self.setRoles(('Manager',))
        folder = self.folder
        topic = self.folder[self.folder.invokeFactory('Topic', id='dc')]
        crit = topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Event')
        crit = topic.addCriterion('object_provides', 'ATSimpleStringCriterion')
        crit.setValue(ICalendarSupport.__identifier__)
        query = topic.buildQuery()
        self.assertEqual(len(query), 2)
        self.assertEqual(query['portal_type'], 'Event')
        self.assertEqual(query['object_provides'], ICalendarSupport.__identifier__)
        view = getMultiAdapter((topic, TestRequest()), name='ics_view')
        view.update()
        self.assertEqual(len(view.events), 2)
        self.assertEqual(sorted([ e.Title for e in view.events ]),
            ['Plone Conf 2007', 'Plone Conf 2008'])

    def checkOrder(self, text, *order):
        for item in order:
            position = text.find(item)
            self.failUnless(position >= 0,
                'menu item "%s" missing or out of order' % item)
            text = text[position:]

    def testRendering(self):
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.folder, request), name='ics_view')
        view.render()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2007',
            'LOCATION:Naples',
            'URL:http://plone.org/events/conferences/2007-naples',
            'END:VEVENT',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2008',
            'LOCATION:DC',
            'END:VEVENT',
            'END:VCALENDAR')

    def testCalendarInfo(self):
        self.folder.processForm(values={'title': 'Foo', 'description': 'Bar'})
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.folder, request), name='ics_view')
        view.render()
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'X-WR-CALNAME:Foo',
            'X-WR-CALDESC:Bar',
            'BEGIN:VEVENT',
            'BEGIN:VEVENT',
            'END:VCALENDAR')
        # another folder should have another name, even though the set
        # of events might be the same...
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.portal, request), name='ics_view')
        view.render()
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'X-WR-CALNAME:Plone site',
            'X-WR-CALDESC:',
            'BEGIN:VEVENT',
            'BEGIN:VEVENT',
            'END:VCALENDAR')
        # changing the title should be immediately reflected...
        self.folder.processForm(values={'title': 'Föö!!'})
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.folder, request), name='ics_view')
        view.render()
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'X-WR-CALNAME:Föö!!',
            'X-WR-CALDESC:Bar',
            'BEGIN:VEVENT',
            'BEGIN:VEVENT',
            'END:VCALENDAR')

    def testRenderingForTopic(self):
        self.setRoles(('Manager',))
        folder = self.folder
        topic = self.folder[self.folder.invokeFactory('Topic', id='dc')]
        crit = topic.addCriterion('SearchableText', 'ATSimpleStringCriterion')
        crit.setValue('DC')
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((topic, request), name='ics_view')
        view.render()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.checkOrder(''.join(output),
            'BEGIN:VCALENDAR',
            'BEGIN:VEVENT',
            'SUMMARY:Plone Conf 2008',
            'LOCATION:DC',
            'URL:http://plone.org/events/conferences/2008-washington-dc',
            'END:VEVENT',
            'END:VCALENDAR')
        lines = ''.join(output).splitlines()
        self.assertEqual(len([ l for l in lines if l == 'BEGIN:VEVENT']), 1)

    def testCacheKey(self):
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.folder, request), name='ics_view')
        # calculate original key for caching...
        view.update()
        key1 = cachekey(None, view)
        # a second invocation should return the same key...
        view.update()
        key2 = cachekey(None, view)
        self.assertEqual(key1, key2)
        # even with a new view...
        headers, output, request = makeResponse(TestRequest())
        view = getMultiAdapter((self.folder, request), name='ics_view')
        view.update()
        key3 = cachekey(None, view)
        self.assertEqual(key1, key3)
        # however, if one of the object gets changed, the key should as well
        self.folder.ploneconf2007.processForm(values={'location': 'Naples, Italy'})
        view.update()
        key4 = cachekey(None, view)
        self.assertNotEqual(key1, key4)
        # the same goes if another one is added
        self.folder[self.folder.invokeFactory('Event',
            id='ploneconf2009', title='Plone Conf 2009',
            startDate='2008/10/28', endDate='2008/10/30', location='Budapest',
            eventUrl='http://plone.org/events/conferences/2009')]
        view.update()
        key5 = cachekey(None, view)
        self.assertNotEqual(key1, key5)
        self.assertNotEqual(key4, key5)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
