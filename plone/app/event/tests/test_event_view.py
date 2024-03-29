from plone.app.event.dx.traverser import OccurrenceTraverser as OccTravDX
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now as PN
from unittest import mock


class FunctionalTestEventViewDX(AbstractSampleDataEvents):
    layer = PAEventDX_FUNCTIONAL_TESTING

    @property
    def traverser(self):
        return OccTravDX(self.now_event, self.request)

    @mock.patch("plone.app.event.base.localized_now", new=PN)
    def test_event_view__non_recurring(self):
        view = self.portal.future.restrictedTraverse("@@event_view")

        output = view()

        self.assertTrue("Future Event" in output)
        self.assertTrue("2013-05-15" in output)
        self.assertTrue("Europe/Vienna" in output)
        self.assertTrue("UTC200" in output)
        self.assertTrue("Graz" in output)
        self.assertTrue("All dates" not in output)

    @mock.patch("plone.app.event.base.localized_now", new=PN)
    def test_event_view__recurring(self):
        view = self.portal.now.restrictedTraverse("@@event_view")

        output = view()

        self.assertTrue("Now Event" in output)
        self.assertTrue("2013-05-05" in output)
        self.assertTrue("All dates" in output)
        self.assertTrue("2013-05-07" in output)
        self.assertTrue("2013-05-09" in output)
        self.assertTrue("http://plone.org" in output)

    @mock.patch("plone.app.event.base.localized_now", new=PN)
    def test_event_view__recurring_occurrence(self):
        occ = self.traverser.publishTraverse(self.request, "2013-05-07")
        view = occ.restrictedTraverse("@@event_view")

        output = view()

        self.assertTrue("Now Event" in output)
        self.assertTrue(
            "2013-05-05" not in output
        )  # Lists only upcoming relative to occurrence's date  # noqa
        self.assertTrue("2013-05-07" in output)
        self.assertTrue("2013-05-09" in output)
        self.assertTrue("http://plone.org" in output)
