from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.base import localized_today
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import make_fake_response
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now as PN

import mock


class TestEventsListingDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
        DXEventAccessor.portal_type = 'plone.app.event.dx.event'
        return DXEventAccessor.create

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_future(self):
        # Default mode is to show all events from now on.
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 5)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_past(self):
        self.request.form.update({'mode': 'past'})
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 5)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_all(self):
        self.request.form.update({'mode': 'all'})
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 8)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_get_events_today(self):
        today = localized_today().isoformat()
        self.request.form.update({'mode': 'day', 'date': today})
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 2)

    @mock.patch('plone.app.event.browser.event_listing.localized_now', new=PN)
    @mock.patch('plone.app.event.base.localized_now', new=PN)
    def test_events_listing_ical(self):
        # Default mode is to show all events from now on.
        headers, output, request = make_fake_response(self.request)
        view = self.portal.restrictedTraverse('@@event_listing_ical')
        view()
        self.assertEqual(len(headers), 2)
        self.assertEqual(headers['Content-Type'], 'text/calendar')
        icalstr = ''.join(output)
        self.assertTrue('Long Event' in icalstr)


class TestEventsListingAT(TestEventsListingDX):
    layer = PAEventAT_INTEGRATION_TESTING

    def event_factory(self):
        return ATEventAccessor.create
