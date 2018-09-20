# -*- coding: utf-8 -*-
from datetime import timedelta
from plone.app.event.base import localized_now
from plone.app.event.portlets import portlet_events
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import set_env_timezone
from plone.app.event.testing import set_timezone
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.dexterity.utils import createContentInContainer
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import _getDottedName
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import setHooks
from zope.component.hooks import setSite
from zope.interface import alsoProvides

import pytz
import unittest


TZNAME = 'Australia/Brisbane'
PTYPE = 'plone.app.event.dx.event'


class PortletTest(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        self.request = self.layer['request']
        alsoProvides(self.request, IPloneFormLayer)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        setHooks()
        setSite(portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        self.assertEqual(portlet.addview, 'portlets.Events')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            ['plone.app.portlets.interfaces.IColumn',
             'plone.app.portlets.interfaces.IDashboard'],
            registered_interfaces
        )

    def testInterfaces(self):
        portlet = portlet_events.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn'
        )
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(
            isinstance(list(mapping.values())[0], portlet_events.Assignment)
        )

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()

        mapping['foo'] = portlet_events.Assignment(count=5)
        editview = getMultiAdapter((mapping['foo'], self.request), name='edit')
        self.assertTrue(isinstance(editview, portlet_events.EditForm))

    def testRenderer(self):
        context = self.portal
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(
            IPortletManager, name='plone.leftcolumn', context=self.portal
        )
        assignment = portlet_events.Assignment(count=5)

        renderer = getMultiAdapter(
            (context, self.request, view, manager, assignment),
            IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, portlet_events.Renderer))

    def test_disable_dasboard_breaks_event_portlet(self):
        # Bug #8230: disabling the dashboard breaks the event portlet
        self.portal.manage_permission(
            'Portlets: Manage own portlets',
            roles=['Manager'],
            acquire=0
        )

        portlet = getUtility(IPortletType, name='portlets.Events')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn'
        )
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        try:
            addview.createAndAdd(data={})
        except Unauthorized:
            self.fail()


class RendererTest(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.setDefaultChain("simple_publication_workflow")
        set_env_timezone(TZNAME)
        set_timezone(TZNAME)

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.leftcolumn', context=self.portal
        )
        assignment = assignment or portlet_events.Assignment(
            template='portlet_recent', macro='portlet'
        )

        return getMultiAdapter(
            (context, request, view, manager, assignment),
            IPortletRenderer
        )

    def test_portlet_event_renderer__get_events(self):
        start = localized_now()
        end = start + timedelta(hours=1)

        e1 = createContentInContainer(
            self.portal, PTYPE,
            id='e1', title=u'e1', start=start, end=end)
        self.portal.portal_workflow.doActionFor(e1, 'publish')

        self.portal.invokeFactory('Folder', 'eventfolder')
        createContentInContainer(
            self.portal.eventfolder, PTYPE,
            id='e2', title=u'e2', start=start, end=end)

        r = self.renderer(assignment=portlet_events.Assignment(
            count=5, state=('draft',)))
        r.update()
        self.assertEqual(0, len(r.events))

        r = self.renderer(assignment=portlet_events.Assignment(
            count=5, state=('published', )))
        r.update()
        self.assertEqual(1, len(r.events))

        r = self.renderer(assignment=portlet_events.Assignment(
            count=5, state=('published', 'private',)))
        r.update()
        self.assertEqual(2, len(r.events))

        r = self.renderer(assignment=portlet_events.Assignment(count=5))
        r.update()
        self.assertEqual(2, len(r.events))

        # No search base gives calendar urls with event_listing part
        self.assertTrue('event_listing' in r.render())

        r = self.renderer(assignment=portlet_events.Assignment(
            count=5, search_base_uid=self.portal.eventfolder.UID()))
        r.update()
        self.assertEqual(1, len(r.events))

        # A given search base gives calendar urls without event_listing part
        self.assertTrue('event_listing' not in r.render())

    def test_portlet_event_renderer__recurring(self):
        start = localized_now() + timedelta(days=1)

        e1 = createContentInContainer(
            self.portal, PTYPE, id='e1', title=u'Event 1', start=start,
            recurrence='RRULE:FREQ=WEEKLY;COUNT=10')
        createContentInContainer(
            self.portal, PTYPE, id='e1', title=u'Event 1', start=start,
            recurrence='RRULE:FREQ=DAILY;COUNT=3')

        self.portal.portal_workflow.doActionFor(e1, 'publish')

        r = self.renderer(
            assignment=portlet_events.Assignment(count=5,
                                                 state=('published',)))
        r.update()
        events = r.events
        self.assertEqual(5, len(events))
        self.assertTrue('Event 2' not in [x.title for x in events])

        rd = r.render()
        occ1dt = start + timedelta(days=7)
        # The first occurrence of the event itself should show up. It should
        # link to the event and not an occurrence.
        self.assertTrue('http://nohost/plone/e1"' in rd)
        # Occurrences should link to the Occurrence.
        self.assertTrue(
            'http://nohost/plone/e1/%s-%02d-%02d' %
            (occ1dt.year, occ1dt.month, occ1dt.day) in rd
        )

    def test_portlet_event_renderer__listing_link(self):
        r = self.renderer(assignment=portlet_events.Assignment(count=5))
        r.update()
        rd = r.render()
        self.assertTrue('?mode=future' in rd)
        self.assertTrue('?mode=past' in rd)
