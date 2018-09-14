# -*- coding: utf-8 -*-
from plone.app.event.base import localized_today
from plone.app.event.testing import make_fake_response
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import patched_now as PN
from plone.app.event.tests.base_setup import AbstractSampleDataEvents

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
        self.assertEqual(len(headers), 3)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        self.assertTrue('Content-Length' in headers)
        icalstr = b''.join(output)
        self.assertTrue(b'Long Event' in icalstr)


class TestEventsListingCollection(TestEventsListingPortal):

    def _listing_view(self, name='@@event_listing'):
        return self.portal.collection.restrictedTraverse(name)

    def _collection_batching_base(self):
        """Base preparation for batching tests below.

        The event_listing view caches it's results on the request, so the
        batching tests below need to be in seperate test methods to get a fresh
        environment with newly calculated results.
        """
        # plone.app.contenttypes ICollection type
        self.portal.invokeFactory('Collection', 'col_test', title=u'Col')
        collection = self.portal.col_test
        collection.query = [
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.any',
             'v': ['Event', 'plone.app.event.dx.event']
             },
        ]
        self.request.form.update({'mode': 'all'})
        return collection

    def test_collection_batching__all(self):
        """Don't limit the results.
        """
        collection = self._collection_batching_base()
        view = collection.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view.events(batch=True)), 8)

    def test_collection_batching__reduce_by_collection_setting(self):
        """Limit the results by setting item_count on the collection.
        """
        collection = self._collection_batching_base()
        view = collection.restrictedTraverse('@@event_listing')
        collection.item_count = 4
        view = collection.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view.events(batch=True)), 4)

    def test_collection_batching__reduce_by_request_parameter(self):
        """Limit the results by using a request parameter.
        """
        collection = self._collection_batching_base()
        self.request.form.update({'b_size': 2})
        view = collection.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view.events(batch=True)), 2)

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
             'o': 'plone.app.querystring.operation.selection.any',
             'v': ['Event', 'plone.app.event.dx.event']
             },
        ]
        view = self.portal.col_without_date_criterion.restrictedTraverse(
            '@@event_listing'
        )
        out = view()
        self.assertTrue('mode_past' in out)

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
             'o': 'plone.app.querystring.operation.selection.any',
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
