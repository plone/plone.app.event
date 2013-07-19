from datetime import datetime
from plone.app.event.at.content import EventAccessor as ATEventAccessor
from plone.app.event.base import localized_today
from plone.app.event.dx.behaviors import EventAccessor as DXEventAccessor
from plone.app.event.ical.importer import ical_import
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.tests.base_setup import AbstractSampleDataEvents
from plone.app.event.tests.base_setup import patched_now as PN
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEventAccessor

import logging
import mock
import os
import pytz
import unittest2 as unittest

logger = logging.getLogger(name="plone.app.event test_events_listing")


class TestEventsListingDX(AbstractSampleDataEvents):
    layer = PAEventDX_INTEGRATION_TESTING

    def event_factory(self):
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
        view = self.portal.restrictedTraverse('@@event_listing_ical')
        view()  # At least, this should not fail.
                # Don't know yet how to catch Content-Disposition output
        #out = view()
        #self.assertEqual(out.count('BEGIN:VEVENT'), 8)


class TestEventsListingAT(TestEventsListingDX):
    layer = PAEventAT_INTEGRATION_TESTING

    def event_factory(self):
        return ATEventAccessor.create


from plone.event.utils import pydt
class TestIcalImportDX(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'impfolder')
        self.impfolder = self.portal.impfolder

    def test_import_from_ics(self):
        # Ical import unit test.

        directory = os.path.dirname(__file__)
        icsfile = open(os.path.join(directory, 'icaltest.ics'), 'rb').read()
        res = ical_import(self.impfolder, icsfile, 'plone.app.event.dx.event')

        self.assertEqual(res['count'], 5)

        at = pytz.timezone('Europe/Vienna')
        utc = pytz.utc

        e1 = IEventAccessor(self.impfolder.e1)

        # Use pydt to normalize for DST times.

        # TODO: test for attendees. see note in
        # plone.app.event.ical.importer.ical_import
        self.assertEqual(
            e1.start,
            pydt(datetime(2013, 7, 19, 12, 0, tzinfo=at))
        )
        self.assertEqual(
            e1.end,
            pydt(datetime(2013, 7, 20, 13, 0, tzinfo=at))
        )
        self.assertEqual(
            e1.description,
            'A basic event with many properties.'
        )
        self.assertEqual(
            e1.whole_day,
            False
        )
        self.assertEqual(
            e1.open_end,
            False
        )


        e2 = IEventAccessor(self.impfolder.e2)
        self.assertEqual(
            e2.start,
            pydt(datetime(1996, 4, 1, 1, 0, tzinfo=utc))
        )
        self.assertEqual(
            e2.end,
            pydt(datetime(1996, 4, 1, 2, 0, tzinfo=utc))
        )
        self.assertEqual(
            e2.recurrence,
            u'RRULE:FREQ=DAILY;COUNT=100\nEXDATE:19960402T010000Z,19960403T010000Z,19960404T010000Z'
        )

        e3 = IEventAccessor(self.impfolder.e3)
        self.assertEqual(
            e3.start,
            pydt(datetime(2012, 3, 27, 10, 0, tzinfo=at))
        )
        self.assertEqual(
            e3.end,
            pydt(datetime(2012, 3, 27, 18, 0, tzinfo=at))
        )
        self.assertEqual(
            e3.recurrence,
            u'RRULE:FREQ=WEEKLY;UNTIL=20120703T080000Z;BYDAY=TU\nEXDATE:20120529T100000,20120403T100000,20120410T100000,20120501T100000,20120417T100000'
        )


        e4 = IEventAccessor(self.impfolder.e4)
        self.assertEqual(
            e4.start,
            pydt(datetime(2013, 4, 4, 0, 0, tzinfo=utc))
        )
        self.assertEqual(
            e4.end,
            pydt(datetime(2013, 4, 4, 23, 59, 59, tzinfo=utc))
        )
        self.assertEqual(
            e4.whole_day,
            True
        )
        self.assertEqual(
            e4.open_end,
            False
        )


        e5 = IEventAccessor(self.impfolder.e5)
        self.assertEqual(
            e5.start,
            pydt(datetime(2013, 4, 2, 12, 0, tzinfo=utc))
        )
        self.assertEqual(
            e5.end,
            pydt(datetime(2013, 4, 2, 23, 59, 59, tzinfo=utc))
        )
        self.assertEqual(
            e5.whole_day,
            False
        )
        self.assertEqual(
            e5.open_end,
            True
        )


    # TODO ical import browser tests

