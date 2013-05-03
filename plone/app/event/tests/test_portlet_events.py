from DateTime import DateTime
from Products.GenericSetup.utils import _getDottedName
from plone.app.event.portlets import portlet_events
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from plone.app.event.testing import set_timezone
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import setHooks
from zope.component.hooks import setSite

import unittest2 as unittest


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
        portlet = getUtility(IPortletType, name='portlets.Events')
        self.assertEquals(portlet.addview, 'portlets.Events')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = portlet_events.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], portlet_events.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()

        mapping['foo'] = portlet_events.Assignment(count=5)
        editview = getMultiAdapter((mapping['foo'], self.request), name='edit')
        self.failUnless(isinstance(editview, portlet_events.EditForm))

    def testRenderer(self):
        context = self.portal
        view = context.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = portlet_events.Assignment(count=5)

        renderer = getMultiAdapter((context, self.request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, portlet_events.Renderer))


class RendererTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        self.request = self.layer['request']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        setHooks()
        setSite(portal)

        set_timezone("Australia/Brisbane")

        # TODO: don't use admin privileges for test methods except
        # test_prev_events_link and test_prev_events_link_and_navigation_root

        # Make sure Events use simple_publication_workflow
        self.portal.portal_workflow.setChainForPortalTypes(['Event'], ['simple_publication_workflow'])

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or portlet_events.Assignment(template='portlet_recent', macro='portlet')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_events(self):
        start = DateTime('Australia/Brisbane') + 2
        end = DateTime('Australia/Brisbane') + 4
        self.portal.invokeFactory('Event', 'e1',
                                  startDate=start, endDate=end)
        self.portal.invokeFactory('Folder', 'eventfolder')
        # one event in the events folder
        self.portal.eventfolder.invokeFactory('Event', 'e2',
                                              startDate=start, endDate=end)
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')

        portlet = self.renderer(assignment=portlet_events.Assignment(
            count=5, state=('draft',)))
        self.assertEquals(0, len(portlet.events))

        portlet = self.renderer(assignment=portlet_events.Assignment(
            count=5, state=('published', )))
        self.assertEquals(1, len(portlet.events))

        portlet = self.renderer(assignment=portlet_events.Assignment(
            count=5, state=('published', 'private',)))
        self.assertEquals(2, len(portlet.events))

        portlet = self.renderer(assignment=portlet_events.Assignment(count=5))
        self.assertEquals(2, len(portlet.events))

        portlet = self.renderer(assignment=portlet_events.Assignment(
            count=5, search_base="/eventfolder"))
        self.assertEquals(1, len(portlet.events))

        # TODO: better create objects at setup and use thest in these tests
        self.portal.manage_delObjects(['e1', 'eventfolder'])

    def test_events_recurring(self):
        startDT = DateTime('Australia/Brisbane')+1

        self.portal.invokeFactory('Event', 'e1', title='Event 1',
                                  startDate=startDT,
                                  recurrence='RRULE:FREQ=WEEKLY;COUNT=10',
                                  timezone="Australia/Brisbane")
        self.portal.invokeFactory('Event', 'e2', title='Event 2',
                                  startDate=startDT,
                                  recurrence='RRULE:FREQ=DAILY;COUNT=3',
                                  timezone="Australia/Brisbane")
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')

        r = self.renderer(
            assignment=portlet_events.Assignment(count=5,
                                                 state=('published',)))
        events = r.events
        self.assertEqual(5, len(events))
        self.assertTrue('Event 2' not in [x.title for x in events])

        rd = r.render()
        occ1DT = startDT+7
        # The first occurrence of the event itself should show up. It should
        # link to the event and not an occurrence.
        self.assertTrue('http://nohost/plone/e1"' in rd)
        # Occurrences should link to the Occurrence.
        self.assertTrue('http://nohost/plone/e1/%s-%02d-%02d' %
                (occ1DT.year(), occ1DT.month(), occ1DT.day()) in rd)

        self.portal.manage_delObjects(['e1', 'e2'])

    def test_events_listing_link(self):
        r = self.renderer(assignment=portlet_events.Assignment(count=5))
        rd = r.render()
        self.assertTrue('@@event_listing?mode=future' in rd)
        self.assertTrue('@@event_listing?mode=past' in rd)
