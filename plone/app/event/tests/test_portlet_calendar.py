# -*- coding: utf-8 -*-
from calendar import monthrange
from datetime import datetime
from datetime import timedelta
from plone.app.event.base import localized_today
from plone.app.event.portlets import portlet_calendar
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import set_env_timezone
from plone.app.event.testing import set_timezone
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import _getDottedName
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import setHooks
from zope.component.hooks import setSite

import pytz
import unittest


TZNAME = 'Europe/Vienna'
PTYPE = 'plone.app.event.dx.event'


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
        self.assertEqual(portlet.addview, 'portlets.Calendar')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Calendar')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual([
            'plone.app.portlets.interfaces.IColumn',
            'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces
        )

    def testInterfaces(self):
        portlet = portlet_calendar.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Calendar')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn'
        )
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(
            isinstance(list(mapping.values())[0], portlet_calendar.Assignment)
        )

    def testRenderer(self):
        context = self.portal
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager,
            name='plone.rightcolumn',
            context=self.portal
        )
        assignment = portlet_calendar.Assignment()

        renderer = getMultiAdapter(
            (context, self.request, view, manager, assignment),
            IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, portlet_calendar.Renderer))


class RendererTest(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        self.request = self.layer['request']
        self.wft = getToolByName(self.portal, 'portal_workflow')
        self.wft.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ['Manager'])
        setHooks()
        setSite(portal)

        set_env_timezone(TZNAME)
        set_timezone(TZNAME)

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager,
            name='plone.rightcolumn',
            context=self.portal
        )
        assignment = assignment or portlet_calendar.Assignment()

        return getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )

    def test_portlet_config(self):
        tz = pytz.timezone(TZNAME)
        start = tz.localize(datetime.now())
        end = start + timedelta(hours=1)

        e1 = createContentInContainer(
            self.portal, PTYPE, title=u'e1', start=start, end=end)
        self.portal.invokeFactory('Folder', 'eventfolder')
        createContentInContainer(
            self.portal.eventfolder, PTYPE, title=u'e2', start=start, end=end)
        self.portal.portal_workflow.doActionFor(e1, 'publish')

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

        # No search base gives calendar urls with event_listing part
        self.assertTrue('event_listing?mode=day' in rd)

        r = self.renderer(assignment=portlet_calendar.Assignment(
            search_base_uid=self.portal.eventfolder.UID()))
        r.update()
        rd = r.render()
        self.assertTrue('e1' not in rd and 'e2' in rd)

        # A given search base gives calendar urls without event_listing part
        self.assertTrue('event_listing?mode=day' not in rd)

        # link to calendar view in rendering
        self.assertTrue('?mode=day&amp;date=' in rd)

    def test_long_event(self):
        tz = pytz.timezone(TZNAME)
        actual = tz.localize(datetime.now())
        start = tz.localize(datetime(actual.year, actual.month, 1))
        end = start + timedelta(days=2)

        e1 = createContentInContainer(
            self.portal, PTYPE, title=u'e1', start=start, end=end)
        self.portal.portal_workflow.doActionFor(e1, 'publish')

        r = self.renderer(
            assignment=portlet_calendar.Assignment(state=('published', ))
        )
        r.update()
        rd = r.render()
        self.assertEqual(rd.count('e1'), 3)

    def test_event_created_last_day_of_month_invalidate_cache(self):
        # First render the calendar portlet when there's no events
        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()
        html = r.render()

        # Now let's add a new event on the first day of the current month
        year, month = r.year_month_display()
        day = monthrange(year, month)[1]  # (wkday, days)

        tz = pytz.timezone(TZNAME)
        start = tz.localize(datetime(year, month, day, 23, 0, 0))
        end = tz.localize(datetime(year, month, day, 23, 30, 0))
        # Event starts at 23:00 and ends at 23:30
        createContentInContainer(
            self.portal, PTYPE, title=u'e1', start=start, end=end
        )

        # Try to render the calendar portlet again, it must be different Now
        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()
        self.assertNotEqual(
            html, r.render(), "Cache key wasn't invalidated"
        )

    def test_event_nonascii(self):
        # test issue with non-ascii event title and location
        title = u'Plön€¢önf München 2012'

        tz = pytz.timezone(TZNAME)
        start = tz.localize(datetime.now())
        end = start + timedelta(hours=1)
        e1 = createContentInContainer(
            self.portal, PTYPE, title=title, start=start, end=end,
            location=u'München')
        self.wft.doActionFor(e1, 'publish')
        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()
        self.assertTrue(title in r.render())

    def test_prev_next_query(self):
        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()

        year, month = r.year_month_display()
        prev_expected = '?month={1}&year={0}'.format(
            *r.get_previous_month(year, month))
        next_expected = '?month={1}&year={0}'.format(
            *r.get_next_month(year, month))
        self.assertEqual(next_expected, r.next_query)
        self.assertEqual(prev_expected, r.prev_query)

    def test_invalid_request(self):
        self.request.form['month'] = [3, 4]
        self.request.form['year'] = [2011]
        r = self.renderer()
        r.update()
        today = localized_today(self.portal)
        self.assertEqual(r.year_month_display(), (today.year, today.month))
