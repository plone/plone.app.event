# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility, getMultiAdapter
from zope.site.hooks import setHooks, setSite

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from DateTime import DateTime
from plone.app.event.portlets import portlet_calendar

import unittest2 as unittest
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class PortletTest(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        self.request = self.layer['request']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        setHooks()
        setSite(portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Calendar')
        self.assertEquals(portlet.addview, 'portlets.Calendar')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Calendar')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = portlet_calendar.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Calendar')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], portlet_calendar.Assignment))

    def testRenderer(self):
        context = self.portal
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = portlet_calendar.Assignment()

        renderer = getMultiAdapter((context, self.request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, portlet_calendar.Renderer))


class RendererTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        self.request = self.layer['request']
        self.wft = getToolByName(self.portal, 'portal_workflow')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        setHooks()
        setSite(portal)

        # Make sure Events use simple_publication_workflow
        self.portal.portal_workflow.setChainForPortalTypes(['Event'], ['simple_publication_workflow'])

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or portlet_calendar.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_portlet_config(self):
        start = DateTime('Europe/Vienna')
        end = DateTime('Europe/Vienna') + 0.1
        self.portal.invokeFactory('Event', 'e1',
                                  startDate=start, endDate=end)
        self.portal.invokeFactory('Folder', 'eventfolder')
        # one event in the events folder
        self.portal.eventfolder.invokeFactory('Event', 'e2',
                                              startDate=start, endDate=end)
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')

        r = self.renderer(assignment=portlet_calendar.Assignment(
            state=('draft',)))
        r.update()
        rd = r.render()
        self.assertTrue('e1' not in rd and 'e2' not in rd)

        r = self.renderer(assignment=portlet_calendar.Assignment(
            state=('published', )))
        r.update()
        rd = r.render()
        self.assertTrue('e1' in rd and 'e2' not in rd)

        r = self.renderer(assignment=portlet_calendar.Assignment(
            state=('published', 'private',)))
        r.update()
        rd = r.render()
        self.assertTrue('e1' in rd and 'e2' in rd)

        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()
        rd = r.render()
        self.assertTrue('e1' in rd and 'e2' in rd)

        r = self.renderer(assignment=portlet_calendar.Assignment(
            search_base="/eventfolder"))
        r.update()
        rd = r.render()
        self.assertTrue('e1' not in rd and 'e2' in rd)
        # test link from base.CalendarLinkbase.date_events_url
        self.assertTrue('@@search?advanced_search=True&amp;start.query' in rd)

    def test_event_created_last_day_of_month_invalidate_cache(self):
        # First render the calendar portlet when there's no events
        portlet = self.renderer(assignment=portlet_calendar.Assignment())
        portlet.update()
        html = portlet.render()

        # Now let's add a new event in the last day of the current month
        year, month = portlet.year_month_display()
        last_day_month = DateTime('%s/%s/1' % (year, month)) - 1
        hour = 1 / 24.0
        # Event starts at 23:00 and ends at 23:30
        self.portal.invokeFactory('Event', 'e1',
                                  startDate=last_day_month + 23*hour,
                                  endDate=last_day_month + 23.5*hour)

        # Try to render the calendar portlet again, it must be different now
        portlet = self.renderer(assignment=portlet_calendar.Assignment())
        portlet.update()
        self.assertNotEqual(html, portlet.render(), "Cache key wasn't invalidated")

    def test_event_nonascii(self):
        # test issue with non-ascii event title and location
        title = u'Plön€¢önf München 2012'
        self.portal.invokeFactory('Event', 'e1', title=title,
                                  location=u'München')
        #self.wft.doActionFor(self.portal.e1, 'publish')
        portlet = self.renderer(assignment=portlet_calendar.Assignment())
        portlet.update()
        self.assertTrue(title in portlet.render())

    def test_prev_next_query(self):
        portlet = self.renderer(assignment=portlet_calendar.Assignment())
        portlet.update()

        year, month = portlet.year_month_display()
        prev_expected = '?month={1}&year={0}'.format(
            *portlet.get_previous_month(year, month))
        next_expected = '?month={1}&year={0}'.format(
            *portlet.get_next_month(year, month))
        self.assertEqual(next_expected, portlet.next_query)
        self.assertEqual(prev_expected, portlet.prev_query)
