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


TZNAME = "Europe/Vienna"
PTYPE = "plone.app.event.dx.event"


class PortletTest(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer["portal"]
        self.portal = portal
        self.request = self.layer["request"]
        setRoles(portal, TEST_USER_ID, ["Manager"])
        setHooks()
        setSite(portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name="portlets.Calendar")
        self.assertEqual(portlet.addview, "portlets.Calendar")

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name="portlets.Calendar")
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEqual(
            [
                "plone.app.portlets.interfaces.IColumn",
                "plone.app.portlets.interfaces.IDashboard",
            ],
            registered_interfaces,
        )

    def testInterfaces(self):
        portlet = portlet_calendar.Assignment()
        self.assertTrue(IPortletAssignment.providedBy(portlet))
        self.assertTrue(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name="portlets.Calendar")
        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEqual(len(mapping), 1)
        self.assertTrue(
            isinstance(list(mapping.values())[0], portlet_calendar.Assignment)
        )

    def testRenderer(self):
        context = self.portal
        view = context.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
        )
        assignment = portlet_calendar.Assignment()

        renderer = getMultiAdapter(
            (context, self.request, view, manager, assignment), IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, portlet_calendar.Renderer))


class RendererTest(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer["portal"]
        self.portal = portal
        self.request = self.layer["request"]
        self.wft = getToolByName(self.portal, "portal_workflow")
        self.wft.setDefaultChain("simple_publication_workflow")
        setRoles(portal, TEST_USER_ID, ["Manager"])
        setHooks()
        setSite(portal)

        set_env_timezone(TZNAME)
        set_timezone(TZNAME)

    def renderer(
        self, context=None, request=None, view=None, manager=None, assignment=None
    ):
        context = context or self.portal
        request = request or self.request
        view = view or context.restrictedTraverse("@@plone")
        manager = manager or getUtility(
            IPortletManager, name="plone.rightcolumn", context=self.portal
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
            self.portal, PTYPE, title="e1", start=start, end=end
        )
        self.portal.invokeFactory("Folder", "eventfolder")
        createContentInContainer(
            self.portal.eventfolder, PTYPE, title="e2", start=start, end=end
        )
        self.portal.portal_workflow.doActionFor(e1, "publish")

        r = self.renderer(assignment=portlet_calendar.Assignment(state=("draft",)))
        r.update()
        rd = r.render()
        self.assertTrue("e1" not in rd and "e2" not in rd)

        r = self.renderer(assignment=portlet_calendar.Assignment(state=("published",)))
        r.update()
        rd = r.render()
        self.assertTrue("e1" in rd and "e2" not in rd)

        r = self.renderer(
            assignment=portlet_calendar.Assignment(
                state=(
                    "published",
                    "private",
                )
            )
        )
        r.update()
        rd = r.render()
        self.assertTrue("e1" in rd and "e2" in rd)

        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()
        rd = r.render()
        self.assertTrue("e1" in rd and "e2" in rd)

        # No search base gives calendar urls with event_listing part
        self.assertTrue("event_listing?mode=day" in rd)

        r = self.renderer(
            assignment=portlet_calendar.Assignment(
                search_base_uid=self.portal.eventfolder.UID()
            )
        )
        r.update()
        rd = r.render()
        self.assertTrue("e1" not in rd and "e2" in rd)

        # A given search base gives calendar urls without event_listing part
        self.assertTrue("event_listing?mode=day" not in rd)

        # link to calendar view in rendering
        self.assertTrue("?mode=day&amp;date=" in rd)

    def test_long_event(self):
        """Test a long event.

        An event happening on three days, should have an indication on all
        three days.  That is the main thing we test here.

        But the test may fail on the first day of the month.
        See https://github.com/plone/plone.app.event/issues/334
        When generating the portlet on the first day of the month, it seems
        depending on time zones we might get the previous month.  This would
        mean our event is not (fully) visible.  So we force showing the
        calendar of the month that we want.  This test is not about whether
        the correct month is shown at one minute past midnight.

        Previously we created an event on the first day.  But depending on
        the day of the week that the new month starts, this may also influence
        what is visible: we may see Friday 1st and Saturday 2nd, but not
        Sunday 3rd.  So now we pick a day in the middle of the month.
        """
        tz = pytz.timezone(TZNAME)
        actual = tz.localize(datetime.now())
        start = tz.localize(datetime(actual.year, actual.month, 15))
        end = start + timedelta(days=2)

        e1 = createContentInContainer(
            self.portal, PTYPE, title="e1", start=start, end=end
        )
        self.portal.portal_workflow.doActionFor(e1, "publish")

        self.request["year"] = actual.year
        self.request["month"] = actual.month
        r = self.renderer(assignment=portlet_calendar.Assignment(state=("published",)))
        r.update()
        rd = r.render()
        self.assertEqual(rd.count("e1"), 3)

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
        createContentInContainer(self.portal, PTYPE, title="e1", start=start, end=end)

        # Try to render the calendar portlet again, it must be different Now
        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()
        self.assertNotEqual(html, r.render(), "Cache key wasn't invalidated")

    def test_event_nonascii(self):
        # test issue with non-ascii event title and location
        title = "Plön€¢önf München 2012"

        tz = pytz.timezone(TZNAME)
        start = tz.localize(datetime.now())
        end = start + timedelta(hours=1)
        e1 = createContentInContainer(
            self.portal, PTYPE, title=title, start=start, end=end, location="München"
        )
        self.wft.doActionFor(e1, "publish")
        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()
        self.assertTrue(title in r.render())

    def test_prev_next_query(self):
        r = self.renderer(assignment=portlet_calendar.Assignment())
        r.update()

        year, month = r.year_month_display()
        prev_expected = "?month={1}&year={0}".format(*r.get_previous_month(year, month))
        next_expected = "?month={1}&year={0}".format(*r.get_next_month(year, month))
        self.assertEqual(next_expected, r.next_query)
        self.assertEqual(prev_expected, r.prev_query)

    def test_invalid_request(self):
        self.request.form["month"] = [3, 4]
        self.request.form["year"] = [2011]
        r = self.renderer()
        r.update()
        today = localized_today(self.portal)
        self.assertEqual(r.year_month_display(), (today.year, today.month))

    def test_with_collection_as_source(self):
        """When selecting a Collection as source, the events in that collection
        are used to build the calendar
        """
        tz = pytz.timezone(TZNAME)
        start = tz.localize(datetime.now())
        end = start + timedelta(hours=1)

        createContentInContainer(self.portal, PTYPE, title="e1", start=start, end=end)

        createContentInContainer(self.portal, PTYPE, title="e2", start=start, end=end)

        # starts yesterday, ends yesterday
        start_yesterday = tz.localize(datetime.now() - timedelta(days=1))
        end_yesterday = start + timedelta(hours=1)

        createContentInContainer(
            self.portal,
            PTYPE,
            title="e3",
            start=start_yesterday,
            end=end_yesterday,
        )

        # starts today, ends tomorrow
        start_today = tz.localize(datetime.now())
        end_tomorrow = start + timedelta(days=1)

        createContentInContainer(
            self.portal,
            PTYPE,
            title="e4",
            start=start_today,
            end=end_tomorrow,
        )

        # starts yesterday, ends tomorrow
        start_yesterday = tz.localize(datetime.now() - timedelta(days=1))
        end_tomorrow = tz.localize(datetime.now()) + timedelta(days=1)

        createContentInContainer(
            self.portal,
            PTYPE,
            title="e5",
            start=start_yesterday,
            end=end_tomorrow,
        )

        # starts tomorrow, ends tomorrow + 1
        start_tomorrow = tz.localize(datetime.now() + timedelta(days=1))
        end_tomorrow_1 = start_tomorrow + timedelta(days=1)

        createContentInContainer(
            self.portal,
            PTYPE,
            title="e6",
            start=start_tomorrow,
            end=end_tomorrow_1,
        )

        # self.wft.doActionFor(self.portal.e1, "publish")
        self.wft.doActionFor(self.portal.e2, "publish")
        self.wft.doActionFor(self.portal.e3, "publish")
        self.wft.doActionFor(self.portal.e4, "publish")
        self.wft.doActionFor(self.portal.e5, "publish")
        self.wft.doActionFor(self.portal.e6, "publish")

        self.portal.invokeFactory(
            "Collection",
            "eventcollection",
            query=[
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": [PTYPE],
                },
                {
                    "i": "end",
                    "o": "plone.app.querystring.operation.date.afterToday",
                    "v": "",
                },
                {
                    "i": "review_state",
                    "o": "plone.app.querystring.operation.selection.any",
                    "v": ["published"],
                },
            ],
        )

        r = self.renderer(
            # context=self.portal.eventcollection,
            assignment=portlet_calendar.Assignment(
                state=("published",),
                search_base_uid=self.portal.eventcollection.UID(),
            ),
        )
        r.update()
        rd = r.render()

        self.assertTrue("e1" not in rd)
        self.assertTrue("e2" in rd)
        self.assertTrue("e3" in rd)
        self.assertTrue("e4" in rd)
        self.assertTrue("e5" in rd)
        self.assertTrue("e6" in rd)
