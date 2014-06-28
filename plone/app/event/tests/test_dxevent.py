# -*- coding: utf-8 -*-
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from datetime import datetime, timedelta
from plone.app.event.base import DEFAULT_END_DELTA
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.dx.behaviors import IEventAttendees
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventContact
from plone.app.event.dx.behaviors import IEventLocation
from plone.app.event.dx.behaviors import IEventRecurrence
from plone.app.event.dx.behaviors import StartBeforeEnd
from plone.app.event.dx.behaviors import default_end
from plone.app.event.dx.behaviors import default_start
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.app.event.dx.upgrades.upgrades import upgrade_attribute_storage
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import set_browserlayer
from plone.app.event.testing import set_env_timezone
from plone.app.event.tests.base_setup import patched_now
from plone.app.event.tests.base_setup import TEST_TIMEZONE
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityFTI
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.testing.z2 import Browser
from zope.annotation.interfaces import IAnnotations
from zope.component import createObject
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import mock
import pytz
import unittest2 as unittest
import zope.interface


TZNAME = "Europe/Vienna"


class MockEvent(SimpleItem):
    """ Mock event"""


class TestDXAddEdit(unittest.TestCase):
    layer = PAEventDX_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    @mock.patch('plone.app.event.base.localized_now', new=patched_now)
    def test_defaults(self):
        """Test, if defaults are set correctly.

        Would have loved to do it like follows, but that doesn't set defaults:

        TRY 1:
        self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'event1',
            title="event1",
        )

        TRY 2:
        from plone.dexterity.utils import createContentInContainer
        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            'event1'
        )

        TRY 3:
        from plone.dexterity.browser.add import DefaultAddForm
        form = DefaultAddForm(self.portal, self.request)
        form.portal_type = 'plone.app.event.dx.event'
        e1 = form.create(data={'title': 'event1'})
        form.add(e1)
        """

        self.browser.open('{}/{}'.format(
            self.portal.absolute_url(),
            '++add++plone.app.event.dx.event'
        ))

        self.browser.getControl(
            name='form.widgets.IDublinCore.title'
        ).value = "TestEvent"

        self.browser.getControl('Save').click()

        # CHECK VALUES
        #
        # TODO: fix all defaults
        event = self.portal['testevent']
        # self.assertEqual(
        #     event.start,
        #     patched_now()
        # )
        # self.assertEqual(
        #     event.end,
        #     patched_now() + timedelta(hours=DEFAULT_END_DELTA)
        # )
        self.assertEqual(event.whole_day, False)
        self.assertEqual(event.open_end, False)
        # self.assertEqual(event.timezone, TEST_TIMEZONE)

    def test_edit_context(self):
        """Test if already added event can be edited directly on the context as
        intended.
        If should not fail with a timezone related error.
        """
        """
        self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'testevent',
            title="Test Event",
            start=datetime(2014, 03, 29, 21, 53),
            end=datetime(2014, 03, 29, 22, 45),
            timezone=TZNAME
        )

        from plone.dexterity.browser.edit import DefaultEditForm
        # DOES NOT WORK...
        testevent = self.portal.testevent
        request = self.request
        request.form = {
            'form.widgets.IEventBasic.start': ('2014', '2', '2', '10', '10')
        }
        edit = DefaultEditForm(testevent, request)
        edit.update()

        save = edit.buttons['save']
        edit.handlers.getHandler(save)(edit, edit)
        """

        # ADD
        #
        self.browser.open(self.portal.absolute_url())
        self.browser.getLink('plone.app.event.dx.event').click()
        self.browser.getControl(
            name='form.widgets.IDublinCore.title'
        ).value = "TestEvent"

        self.browser.getControl(
            name='form.widgets.IEventBasic.start-year').value = ("2014",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.start-month').value = ("3",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.start-day').value = ("30",)

        self.browser.getControl(
            name='form.widgets.IEventBasic.end-year').value = ("2014",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.end-month').value = ("3",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.end-day').value = ("31",)

        self.browser.getControl('Save').click()

        # CHECK VALUES
        #
        self.assertTrue(self.browser.url.endswith('testevent/view'))
        self.assertTrue('TestEvent' in self.browser.contents)
        self.assertTrue('2014-03-30' in self.browser.contents)
        self.assertTrue('2014-03-31' in self.browser.contents)

        # EDIT
        #
        testevent = self.portal.testevent
        self.browser.open('%s/@@edit' % testevent.absolute_url())

        self.browser.getControl(
            name='form.widgets.IEventBasic.start-year').value = ("2014",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.start-month').value = ("2",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.start-day').value = ("2",)

        self.browser.getControl(
            name='form.widgets.IEventBasic.end-year').value = ("2014",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.end-month').value = ("2",)
        self.browser.getControl(
            name='form.widgets.IEventBasic.end-day').value = ("3",)

        self.browser.getControl('Save').click()

        # CHECK VALUES
        #
        self.assertTrue('2014-02-02' in self.browser.contents)
        self.assertTrue('2014-02-03' in self.browser.contents)


class TestDXIntegration(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_start_defaults(self):
        data = MockEvent()
        data.context = MockEvent()
        default_value = default_start(data)
        now = localized_now().replace(minute=0, second=0, microsecond=0)
        delta = default_value - now
        self.assertEqual(0, delta.seconds)

    def test_end_default(self):
        data = MockEvent()
        data.context = MockEvent()
        default_value = default_end(data)
        delta = default_value - default_start(data)
        self.assertEqual(3600, delta.seconds)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='plone.app.event.dx.event')
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='plone.app.event.dx.event')
        factory = fti.factory
        new_object = createObject(factory)
        self.assertTrue(IDXEvent.providedBy(new_object))
        self.assertTrue(IDXEventRecurrence.providedBy(new_object))
        self.assertTrue(IEventLocation.providedBy(new_object))
        self.assertTrue(IEventAttendees.providedBy(new_object))
        self.assertTrue(IEventContact.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'event1',
            start=datetime(2011, 11, 11, 11, 0),
            end=datetime(2011, 11, 11, 12, 0),
            timezone=TZNAME,
            whole_day=False
        )
        e1 = self.portal['event1']
        self.assertTrue(IDXEvent.providedBy(e1))
        self.assertTrue(IDXEventRecurrence.providedBy(e1))
        self.assertTrue(IEventLocation.providedBy(e1))
        self.assertTrue(IEventAttendees.providedBy(e1))
        self.assertTrue(IEventContact.providedBy(e1))

    def test_start_end_dates_indexed(self):
        self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'event1',
            start=datetime(2011, 11, 11, 11, 0),
            end=datetime(2011, 11, 11, 12, 0),
            timezone=TZNAME,
            whole_day=False
        )
        e1 = self.portal['event1']
        e1.reindexObject()

        result = self.portal.portal_catalog(
            path='/'.join(e1.getPhysicalPath())
        )
        self.assertEqual(1, len(result))
        # result returns Zope's DateTime
        self.assertEqual(
            result[0].start,
            DateTime('2011/11/11 11:00:00 %s' % TZNAME)
        )
        self.assertEqual(
            result[0].end,
            DateTime('2011/11/11 12:00:00 %s' % TZNAME)
        )

    def test_data_postprocessing(self):
        # Addressing bug #62
        self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'event1',
            start=datetime(2012, 10, 19, 0, 30),
            end=datetime(2012, 10, 19, 1, 30),
            timezone="Europe/Vienna",
            whole_day=False
        )
        e1 = self.portal['event1']
        e1.reindexObject()

        # Prepare reference objects
        tzname_1 = "Europe/Vienna"
        tz_1 = pytz.timezone(tzname_1)
        dt_1 = tz_1.localize(datetime(2012, 10, 19, 0, 30))
        dt_1_1 = tz_1.localize(datetime(2012, 10, 19, 0, 0))
        dt_1_2 = tz_1.localize(datetime(2012, 10, 19, 23, 59, 59))

        tzname_2 = "Hongkong"
        tz_2 = pytz.timezone(tzname_2)
        dt_2 = tz_2.localize(datetime(2012, 10, 19, 0, 30))
        dt_2_1 = tz_2.localize(datetime(2012, 10, 19, 0, 0))
        dt_2_2 = tz_2.localize(datetime(2012, 10, 19, 23, 59, 59))

        # See, if start isn't moved by timezone offset. Addressing issue #62
        self.assertTrue(IEventBasic(e1).start == dt_1)
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_1)

        # After timezone changes, only the timezone should be applied, but the
        # date and time values not converted.
        IEventAccessor(e1).timezone = tzname_2
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_2)

        # Test open_end events
        # For open_end events, setting the end date has no effect
        IEventAccessor(e1).edit(
            timezone=tzname_1,
            open_end=True,
            end=datetime(2012, 11, 11, 10, 10, 0),
        )
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_1)
        self.assertTrue(IEventBasic(e1).end == dt_1_2)

        # Likewise with whole_day events. If values were converted, the days
        # would drift apart.
        IEventAccessor(e1).whole_day = True
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_1_1)
        self.assertTrue(IEventBasic(e1).end == dt_1_2)

        IEventAccessor(e1).timezone = tzname_2
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(IEventBasic(e1).start == dt_2_1)
        self.assertTrue(IEventBasic(e1).end == dt_2_2)

    def test_recurrence_indexing(self):
        utc = pytz.utc
        self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'event1',
            start=datetime(2011, 11, 11, 11, 0, tzinfo=utc),
            end=datetime(2011, 11, 11, 12, 0, tzinfo=utc),
            timezone='UTC',
            whole_day=False
        )
        e1 = self.portal['event1']
        e1rec = IEventRecurrence(e1)
        e1rec.recurrence = 'RRULE:FREQ=DAILY;COUNT=4'
        e1.reindexObject()

        # test, if the recurrence attribute is available on the context.
        # DRI needs that for indexing.
        self.assertTrue(e1.recurrence == e1rec.recurrence)

        # test, if the occurrences are indexed by DRI
        result = get_events(
            e1,
            start=datetime(2011, 11, 12, 11, 0, tzinfo=utc)
        )
        self.assertTrue(len(result) == 1)

    def test_event_accessor(self):
        utc = pytz.utc
        self.portal.invokeFactory(
            'plone.app.event.dx.event',
            'event1',
            start=datetime(2011, 11, 11, 11, 0, tzinfo=utc),
            end=datetime(2011, 11, 11, 12, 0, tzinfo=utc),
            timezone='UTC',
            whole_day=False
        )
        e1 = self.portal['event1']

        # setting attributes via the accessor
        acc = IEventAccessor(e1)
        acc.end = datetime(2011, 11, 13, 10, 0)
        acc.timezone = TZNAME

        tz = pytz.timezone(TZNAME)

        # accessor should return end datetime in the event's timezone
        self.assertTrue(acc.end == datetime(2011, 11, 13, 11, 0, tzinfo=tz))

        # the behavior's end datetime is stored in utc on the content object
        self.assertTrue(e1.end == datetime(2011, 11, 13, 10, 0, tzinfo=utc))

        # accessing the end property via the behavior adapter, returns the
        # value converted to the event's timezone
        self.assertTrue(
            IEventBasic(e1).end == datetime(2011, 11, 13, 11, 0, tzinfo=tz)
        )

        # timezone should be the same on the event object and accessor
        self.assertTrue(e1.timezone == acc.timezone)


class TestDXEventRecurrence(unittest.TestCase):

    layer = PAEventDX_INTEGRATION_TESTING

    def test_recurrence(self):
        tz = pytz.timezone('Europe/Vienna')
        duration = timedelta(days=4)
        mock = MockEvent()
        mock.start = datetime(2011, 11, 11, 11, 00, tzinfo=tz)
        mock.end = mock.start + duration
        mock.recurrence = 'RRULE:FREQ=DAILY;COUNT=4'
        zope.interface.alsoProvides(
            mock, IEvent, IEventBasic, IEventRecurrence,
            IDXEvent, IDXEventRecurrence)
        result = IRecurrenceSupport(mock).occurrences()
        result = list(result)  # cast generator to list

        self.assertEqual(4, len(result))

        # First occurrence is an IEvent object
        self.assertTrue(IEvent.providedBy(result[0]))

        # Subsequent ones are IOccurrence objects
        self.assertTrue(IOccurrence.providedBy(result[1]))


class TestDXEventUnittest(unittest.TestCase):
    """ Unit test for Dexterity event behaviors.
    """

    def setUp(self):
        set_env_timezone(TZNAME)

    def test_validate_invariants_ok(self):
        mock = MockEvent()
        mock.start = datetime(2009, 1, 1)
        mock.end = datetime(2009, 1, 2)

        try:
            IEventBasic.validateInvariants(mock)
        except:
            self.fail()

    def test_validate_invariants_fail(self):
        mock = MockEvent()
        mock.start = datetime(2009, 1, 2)
        mock.end = datetime(2009, 1, 1)
        mock.open_end = False

        try:
            IEventBasic.validateInvariants(mock)
            self.fail()
        except StartBeforeEnd:
            pass

    def test_validate_invariants_edge(self):
        mock = MockEvent()
        mock.start = datetime(2009, 1, 2)
        mock.end = datetime(2009, 1, 2)
        mock.open_end = False

        try:
            IEventBasic.validateInvariants(mock)
        except:
            self.fail()

    def test_validate_invariants_openend(self):
        mock = MockEvent()
        mock.start = datetime(2009, 1, 2)
        mock.end = datetime(2009, 1, 1)
        mock.open_end = True

        try:
            IEventBasic.validateInvariants(mock)
        except:
            self.fail()


class TestDXAnnotationStorageUpdate(unittest.TestCase):
    """ Unit tests for the Annotation Storage migration
    """
    layer = PAEventDX_INTEGRATION_TESTING

    location = u"Köln"
    attendees = (u'Peter', u'Søren', u'Madeleine')
    contact_email = u'person@email.com'
    contact_name = u'Peter Parker'
    contact_phone = u'555 123 456'
    event_url = u'http://my.event.url'
    text = u'<p>Cathedral Sprint in Köln</p>'

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_migrate_fields(self):
        self.portal.invokeFactory(
            'Event',
            'event1',
            start=datetime(2011, 11, 11, 11, 0),
            end=datetime(2011, 11, 11, 12, 0),
            timezone=TZNAME,
            whole_day=False
        )
        e1 = self.portal['event1']
        # Fill the field values into the annotation storage
        ann = IAnnotations(e1)
        ann['plone.app.event.dx.behaviors.IEventLocation.location'] = \
            self.location
        ann['plone.app.event.dx.behaviors.IEventAttendees.attendees'] = \
            self.attendees
        ann['plone.app.event.dx.behaviors.IEventContact.contact_email'] = \
            self.contact_email
        ann['plone.app.event.dx.behaviors.IEventContact.contact_name'] = \
            self.contact_name
        ann['plone.app.event.dx.behaviors.IEventContact.contact_phone'] = \
            self.contact_phone
        ann['plone.app.event.dx.behaviors.IEventContact.event_url'] = \
            self.event_url
        ann['plone.app.event.dx.behaviors.IEventSummary.text'] = \
            RichTextValue(raw=self.text)

        # All behavior-related fields are not set yet
        self.assertEqual(e1.location, None)
        self.assertEqual(e1.attendees, ())
        self.assertEqual(e1.contact_email, None)
        self.assertEqual(e1.contact_name, None)
        self.assertEqual(e1.contact_phone, None)
        self.assertEqual(e1.event_url, None)
        self.assertEqual(e1.text, None)

        # Run the upgrade step
        upgrade_attribute_storage(self.portal)

        # All behavior-related fields have been migrated
        self.assertEqual(e1.location, self.location)
        self.assertEqual(e1.attendees, self.attendees)
        self.assertEqual(e1.contact_email, self.contact_email)
        self.assertEqual(e1.contact_name, self.contact_name)
        self.assertEqual(e1.contact_phone, self.contact_phone)
        self.assertEqual(e1.event_url, self.event_url)
        self.assertEqual(e1.text.raw, self.text)

    def test_no_overwrite(self):
        self.portal.invokeFactory(
            'Event',
            'event1',
            start=datetime(2011, 11, 11, 11, 0),
            end=datetime(2011, 11, 11, 12, 0),
            timezone=TZNAME,
            whole_day=False
        )
        e1 = self.portal['event1']

        # Fill the field values into the annotation storage
        ann = IAnnotations(e1)
        ann['plone.app.event.dx.behaviors.IEventLocation.location'] = \
            self.location + u'X'
        ann['plone.app.event.dx.behaviors.IEventAttendees.attendees'] = \
            self.attendees + (u'Paula',)
        ann['plone.app.event.dx.behaviors.IEventContact.contact_email'] = \
            self.contact_email + u'X'
        ann['plone.app.event.dx.behaviors.IEventContact.contact_name'] = \
            self.contact_name + u'X'
        ann['plone.app.event.dx.behaviors.IEventContact.contact_phone'] = \
            self.contact_phone + u'X'
        ann['plone.app.event.dx.behaviors.IEventContact.event_url'] = \
            self.event_url + u'X'
        ann['plone.app.event.dx.behaviors.IEventSummary.text'] = \
            RichTextValue(raw=self.text + u'X')

        # Add values into the fields in the new way
        e1.location = self.location
        e1.attendees = self.attendees
        e1.contact_email = self.contact_email
        e1.contact_phone = self.contact_phone
        e1.contact_name = self.contact_name
        e1.event_url = self.event_url
        e1.text = RichTextValue(raw=self.text)

        upgrade_attribute_storage(self.portal)

        # The already existing field values were not touched by the upgrade
        self.assertEqual(e1.location, self.location)
        self.assertEqual(e1.attendees, self.attendees)
        self.assertEqual(e1.contact_email, self.contact_email)
        self.assertEqual(e1.contact_phone, self.contact_phone)
        self.assertEqual(e1.contact_name, self.contact_name)
        self.assertEqual(e1.event_url, self.event_url)
        self.assertEqual(e1.text.raw, self.text)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
