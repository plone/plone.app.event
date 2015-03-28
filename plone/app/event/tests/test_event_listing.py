from plone.app.event.base import localized_today
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import make_fake_response
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now as PN

import mock


class TestEventsListingPortal(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def _listing_view(self, name='@@event_listing'):
        return self.portal.restrictedTraverse(name)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_future(self):
        # Default mode is to show all events from now on.
        view = self._listing_view()
        self.assertEqual(len(view.events(batch=False)), 5)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_past(self):
        self.request.form.update({'mode': 'past'})
        view = self._listing_view()
        self.assertEqual(len(view.events(batch=False)), 5)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_all(self):
        self.request.form.update({'mode': 'all'})
        view = self._listing_view()
        self.assertEqual(len(view.events(batch=False)), 8)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_today(self):
        today = localized_today().isoformat()
        self.request.form.update({'mode': 'day', 'date': today})
        view = self._listing_view()
        self.assertEqual(len(view.events(batch=False)), 2)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_events_listing_ical(self):
        # Default mode is to show all events from now on.
        headers, output, request = make_fake_response(self.request)
        view = self._listing_view(name='@@event_listing_ical')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)
        self.assertTrue('Long Event' in icalstr)


class TestEventsListingCollection(TestEventsListingPortal):

    def _listing_view(self, name='@@event_listing'):
        return self.portal.collection.restrictedTraverse(name)

    def test_date_filtering(self):
        """Test if date filters are available on Collections without start or
        end search criterias.
        """
        # plone.app.contenttypes ICollection type
        self.portal.invokeFactory(
            'Collection', 'col_without_date_criterion', title=u'Col')
        collection = self.portal.col_without_date_criterion
        collection.query = [
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.is',
             'v': ['Event', 'plone.app.event.dx.event']
             },
        ]
        view = self.portal.col_without_date_criterion.restrictedTraverse(
            '@@event_listing'
        )
        out = view()
        for _class in [
            'mode_future',
            'mode_past',
            'mode_month',
            'mode_week',
            'mode_day',
        ]:
            self.assertTrue(_class in out)

    def test_no_date_filtering(self):
        """Test if date filters are not available on Collections with start or
        end search criterias.
        """
        # plone.app.contenttypes ICollection type
        self.portal.invokeFactory(
            'Collection', 'col_with_date_criterion', title=u'Col')
        collection = self.portal.col_with_date_criterion
        collection.query = [
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.is',
             'v': ['Event', 'plone.app.event.dx.event']
             },
            {'i': 'start',
             'o': 'plone.app.querystring.operation.date.afterToday',
             'v': ''}
        ]
        view = self.portal.col_with_date_criterion.restrictedTraverse(
            '@@event_listing'
        )
        out = view()
        for _class in [
            'mode_future',
            'mode_past',
            'mode_month',
            'mode_week',
            'mode_day',
        ]:
            self.assertTrue(_class not in out)
