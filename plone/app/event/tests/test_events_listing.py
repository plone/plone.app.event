
import datetime
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor

import logging
logger = logging.getLogger(name="plone.app.event test_events_listing")

class TestEventsListingDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
        return DXEventAccessor.create

    # TODO: FRAGILE TESTS! test data seems not to be good enough.
    #       fails with '9 != 8'

    def test_get_events_future(self):
        # Default mode is to show all events from now on.
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 8)

    def test_get_events_past(self):
        self.request.form.update({'mode': 'past'})
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 3)

    def test_get_events_all(self):
        self.request.form.update({'mode': 'all'})
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 11)

    def test_get_events_today(self):
        today = datetime.date.today().isoformat()
        self.request.form.update({'mode': 'day', 'date': today})
        view = self.portal.restrictedTraverse('@@event_listing')
        self.assertEqual(len(view._get_events()), 1)

    def test_events_listing_ical(self):
        # Default mode is to show all events from now on.
        view = self.portal.restrictedTraverse('@@event_listing_ical')
        view() # At least, this should not fail.
               # Don't know yet how to catch Content-Disposition output
        #out = view()
        #self.assertEqual(out.count('BEGIN:VEVENT'), 8)
