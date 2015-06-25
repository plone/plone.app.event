from plone.app.event.dx.traverser import OccurrenceTraverser as OccTravDX
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now as PN

import mock


class TestEventSummaryDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    @property
    def traverser(self):
        return OccTravDX(self.now_event, self.request)

    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_event_summary__non_recurring(self):
        """Test if some specific content is included here.
        """
        view = self.portal.future.restrictedTraverse('@@event_summary')

        output = view()

        self.assertTrue('2013-05-15' in output)
        self.assertTrue('(Europe/Vienna / UTC200)' in output)
        self.assertTrue('Graz' in output)
        self.assertTrue('All dates' not in output)

    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_event_summary__recurring(self):
        """Test if some specific content is included here.
        """
        view = self.portal.now.restrictedTraverse('@@event_summary')

        self.assertEqual(view.is_occurrence, False)
        self.assertEqual(len(view.next_occurrences), 3)
        self.assertEqual(view.num_more_occurrences, 0)

        output = view()

        # self.assertTrue('Now Event' not in output)  # Title not shown by def.
        self.assertTrue('2013-05-05' in output)
        self.assertTrue('All dates' in output)
        self.assertTrue('2013-05-07' in output)
        self.assertTrue('2013-05-09' in output)
        self.assertTrue('http://plone.org' in output)

    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_event_summary__recurring_occurrence(self):
        """Test if some specific content is included here.
        """
        occ = self.traverser.publishTraverse(self.request, '2013-05-07')
        view = occ.restrictedTraverse('@@event_summary')

        self.assertEqual(view.is_occurrence, True)
        # Lists only upcoming relative to occurrence's date
        self.assertEqual(len(view.next_occurrences), 2)
        # The num_more_occurrences link is shown as soon not all occurrences
        # are listed. Here. it's referencing the already passed occurrence.
        self.assertEqual(view.num_more_occurrences, 1)

        output = view()

        self.assertTrue('Now Event' not in output)  # Title not shown by def.
        self.assertTrue('All dates' in output)
        self.assertTrue('2013-05-05' not in output)  # Lists only upcoming relative to occurrence's date  # noqa
        self.assertTrue('2013-05-07' in output)
        self.assertTrue('2013-05-09' in output)
        self.assertTrue('http://plone.org' in output)

    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_event_summary__recurring_last_occurrence(self):
        """Test if some specific content is included here.

        On the last occurrence, no other occurrences should be listed but only
        the link to the event_listing view, where all occurrences of the event
        are shown.
        """
        occ = self.traverser.publishTraverse(self.request, '2013-05-09')
        view = occ.restrictedTraverse('@@event_summary')

        self.assertEqual(view.is_occurrence, True)
        # Lists only upcoming relative to occurrence's date. Here no other,
        # than the current (which is hidden from the occurrences list via the
        # template).
        self.assertEqual(len(view.next_occurrences), 1)
        # The num_more_occurrences link is shown as soon not all occurrences
        # are listed. Here. it's referencing the already passed occurrence.
        self.assertEqual(view.num_more_occurrences, 2)

        output = view()

        self.assertTrue('Now Event' not in output)  # Title not shown by def.
        self.assertTrue('All dates' in output)
        self.assertTrue('2013-05-05' not in output)
        self.assertTrue('2013-05-07' not in output)
        self.assertTrue('2013-05-09' in output)
        self.assertTrue('http://plone.org' in output)

    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_event_summary__recurring_excludes(self):
        """Test if some specific content is included here.
        """
        view = self.portal.now.restrictedTraverse('@@event_summary')
        ex = view.excludes
        view.excludes = ['occurrences', 'event_url']

        output = view()

        self.assertTrue('Now Event' in output)  # Title not shown by def.
        self.assertTrue('2013-05-05' in output)
        self.assertTrue('All dates' not in output)
        self.assertTrue('2013-05-07' not in output)
        self.assertTrue('2013-05-09' not in output)
        self.assertTrue('http://plone.org' not in output)

        # Restore default excludes
        view.excludes = ex
