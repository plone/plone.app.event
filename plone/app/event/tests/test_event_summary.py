from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.at.traverser import OccurrenceTraverser as OccTravAT
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.dx.traverser import OccurrenceTraverser as OccTravDX
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now as PN

import mock


class TestEventSummaryDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
        DXEventAccessor.portal_type = 'plone.app.event.dx.event'
        return DXEventAccessor.create

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
        self.assertEqual(view.get_location, u'Vienna')
        self.assertEqual(view.occurrence_parent_url, None)
        self.assertEqual(len(view.next_occurrences), 3)
        self.assertEqual(view.num_more_occurrences, 0)

        output = view()

        #self.assertTrue('Now Event' not in output)  # Title not shown by def.
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
        self.assertEqual(view.get_location, u'Vienna')
        self.assertEqual(view.occurrence_parent_url, 'http://nohost/plone/now')
        self.assertEqual(len(view.next_occurrences), 3)
        self.assertEqual(view.num_more_occurrences, 0)

        output = view()

        self.assertTrue('Now Event' not in output)  # Title not shown by def.
        self.assertTrue('All dates' in output)
        self.assertTrue('2013-05-05' in output)
        self.assertTrue('2013-05-07' in output)
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


class TestEventSummaryAT(TestEventSummaryDX):
    layer = PAEventAT_INTEGRATION_TESTING

    def event_factory(self):
        return ATEventAccessor.create

    @property
    def traverser(self):
        return OccTravAT(self.now_event, self.request)
