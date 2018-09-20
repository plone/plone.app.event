# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from OFS.SimpleItem import SimpleItem
from plone.app.event import base
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.dx.behaviors import default_end
from plone.app.event.dx.behaviors import default_start
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventRecurrence
from plone.app.event.dx.behaviors import StartBeforeEnd
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.app.event.testing import PAEventDX_FUNCTIONAL_TESTING
from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING
from plone.app.event.testing import set_browserlayer
from plone.app.event.testing import set_env_timezone
from plone.app.event.tests.base_setup import patched_now
from plone.app.event.upgrades.upgrades import upgrade_attribute_storage
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.event import utils
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.testing.z2 import Browser
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations

import mock
import pytz
import unittest
import zope.interface


TEST_TIMEZONE = "Europe/Vienna"


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
            title=u"event1",
        )

        TRY 2:
        from plone.dexterity.utils import createContentInContainer
        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            u'event1'
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

        # TODO: these values are simply not set in the pat-pickadate pattern.
        self.browser.getControl(
            name='form.widgets.IEventBasic.start').value = '2014-03-30'
        self.browser.getControl(
            name='form.widgets.IEventBasic.end').value = '2014-03-31'

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
            timezone=TEST_TIMEZONE
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

        #
        # ADD
        #
        self.browser.open(self.portal.absolute_url())
        self.browser.getLink('plone.app.event.dx.event').click()
        self.browser.getControl(
            name='form.widgets.IDublinCore.title'
        ).value = "TestEvent"

        self.browser.getControl(
            name='form.widgets.IEventBasic.start').value = "2014-03-30 03:51"

        self.browser.getControl(
            name='form.widgets.IEventBasic.end').value = "2014-03-30 04:51"

        self.browser.getControl('Save').click()

        # CHECK VALUES
        #
        self.assertTrue(self.browser.url.endswith('testevent/view'))
        self.assertTrue('TestEvent' in self.browser.contents)
        self.assertTrue('2014-03-30' in self.browser.contents)

        #
        # EDIT
        #
        testevent = self.portal.testevent
        self.browser.open('%s/@@edit' % testevent.absolute_url())

        self.browser.getControl(
            name='form.widgets.IEventBasic.start').value = "2014-03-31 03:51"

        self.browser.getControl(
            name='form.widgets.IEventBasic.end').value = "2014-03-31 04:51"

        self.browser.getControl('Save').click()

        #
        # EDIT AGAIN
        #
        testevent = self.portal.testevent
        self.browser.open('%s/@@edit' % testevent.absolute_url())

        self.browser.getControl('Save').click()

        # CHECK DATES/TIMES, MUST NOT HAVE CHANGED
        #
        self.assertTrue('2014-03-31' in self.browser.contents)
        self.assertTrue('03:51' in self.browser.contents)
        self.assertTrue('04:51' in self.browser.contents)

        #
        # EDIT and set whole_day setting
        #
        testevent = self.portal.testevent
        self.browser.open('%s/@@edit' % testevent.absolute_url())

        self.browser.getControl(
            name='form.widgets.IEventBasic.whole_day:list').value = True

        self.browser.getControl('Save').click()

        # CHECK DATES/TIMES, IF THEY ADAPTED ACCORDING TO WHOLE DAY
        #
        self.assertTrue('2014-03-31' in self.browser.contents)
        self.assertTrue('0:00' in self.browser.contents)
        self.assertTrue('23:59' in self.browser.contents)


class TestEventAccessor(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_event_accessor(self):
        tz = pytz.timezone("Europe/Vienna")
        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            title=u'event1',
            start=tz.localize(datetime(2011, 11, 11, 11, 0)),
            end=tz.localize(datetime(2011, 11, 11, 12, 0)),
        )

        # setting attributes via the accessor
        acc = IEventAccessor(e1)
        new_end = tz.localize(datetime(2011, 11, 13, 10, 0))
        acc.end = new_end

        # context's end should be set to new_end
        self.assertEqual(e1.end, new_end)

        # accessor's and context datetime should be the same
        self.assertEqual(acc.end, e1.end)

    def test_event_accessor_whole_day__open_end(self):
        """Also ensures, that accessor method is called for getting start/end
        instead of a custom __getattr__ version.
        """
        at = pytz.timezone("Europe/Vienna")

        start = at.localize(datetime(2012, 10, 19, 0, 30))
        end = at.localize(datetime(2012, 10, 19, 1, 30))

        start_start = at.localize(datetime(2012, 10, 19, 0, 0, 0))
        end_end = at.localize(datetime(2012, 10, 19, 23, 59, 59))

        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            title=u'event1',
            start=start,
            end=end
        )
        acc = IEventAccessor(e1)

        # check set
        self.assertEqual(e1.start, start)
        self.assertEqual(e1.end, end)

        # Setting open end
        e1.open_end = True
        self.assertEqual(e1.start, start)
        self.assertEqual(e1.end, end)
        self.assertEqual(acc.start, start)
        self.assertEqual(acc.end, end_end)

        # Setting whole day
        e1.whole_day = True
        self.assertEqual(e1.start, start)
        self.assertEqual(e1.end, end)
        self.assertEqual(acc.start, start_start)
        self.assertEqual(acc.end, end_end)

    def test_event_accessor__sync_uid(self):
        self.request.set('HTTP_HOST', 'nohost')

        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            title=u'event1'
        )
        acc = IEventAccessor(e1)

        # setting no sync uid will automatically generate one
        self.assertTrue(acc.sync_uid, IUUID(e1) + '@nohost')
        # it's not stored on the object though
        self.assertEqual(e1.sync_uid, None)
        # but it's indexed
        result = self.portal.portal_catalog(sync_uid=IUUID(e1) + '@nohost')
        self.assertEqual(len(result), 1)

        # Setting the sync_uid
        acc.sync_uid = 'okay'
        e1.reindexObject()
        self.assertEqual(acc.sync_uid, 'okay')
        # Now, it's also stored on the object itself
        self.assertEqual(e1.sync_uid, 'okay')
        # and indexed
        result = self.portal.portal_catalog(sync_uid='okay')
        self.assertEqual(len(result), 1)

    def test_event_accessor__start_end(self):
        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            title=u'event1'
        )

        dt = datetime(2161, 1, 1)  # United Federation of Planets
        DT = DateTime('2161/01/01 00:00:00 UTC')

        acc = IEventAccessor(e1)

        # Setting a timezone-naive datetime should convert it to UTC
        acc.start = dt
        self.assertEqual(acc.start, utils.utc(dt))
        self.assertEqual(e1.start, utils.utc(dt))
        # Setting a DateTime should convert it to datetime
        acc.start = DT
        self.assertEqual(acc.start, utils.utc(dt))
        self.assertEqual(e1.start, utils.utc(dt))

        # Same goes for acc.end
        # Setting a timezone-naive datetime should convert it to UTC
        acc.end = dt
        self.assertEqual(acc.end, utils.utc(dt))
        self.assertEqual(e1.end, utils.utc(dt))
        # Setting a DateTime should convert it to datetime
        acc.end = DT
        self.assertEqual(acc.end, utils.utc(dt))
        self.assertEqual(e1.end, utils.utc(dt))


class TestDXIntegration(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.tz = pytz.timezone(TEST_TIMEZONE)

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

    def test_start_end_dates_indexed(self):
        tz = pytz.timezone("Europe/Vienna")
        start = tz.localize(datetime(2011, 11, 11, 11, 0))
        end = tz.localize(datetime(2011, 11, 11, 12, 0))
        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            title=u'event1',
            start=start,
            end=end
        )

        result = self.portal.portal_catalog(
            path='/'.join(e1.getPhysicalPath())
        )
        self.assertEqual(1, len(result))

        # The start and end datetime's are indexed as Python datetimes
        self.assertEqual(result[0].start, start)
        self.assertEqual(result[0].end, end)

    def test_recurrence_indexing(self):
        tz = pytz.timezone("Europe/Vienna")
        e1 = createContentInContainer(
            self.portal,
            'plone.app.event.dx.event',
            title=u'event1',
            start=tz.localize(datetime(2011, 11, 11, 11, 0)),
            end=tz.localize(datetime(2011, 11, 11, 12, 0)),
        )

        # When editing via behaviors, the attributes should also be available
        # on the context itself.
        IEventRecurrence(e1).recurrence = 'RRULE:FREQ=DAILY;COUNT=4'
        self.assertTrue(e1.recurrence == IEventRecurrence(e1).recurrence)

        e1.reindexObject()

        # get_events, no expanded occurrences
        result = get_events(self.portal)
        self.assertEqual(len(result), 1)

        # Get all the occurrences
        result = get_events(
            self.portal,
            start=tz.localize(datetime(2011, 11, 11, 11, 0)),
            ret_mode=base.RET_MODE_OBJECTS,
            expand=True
        )
        self.assertEqual(len(result), 4)


class TestDXEventRecurrence(unittest.TestCase):

    layer = PAEventDX_INTEGRATION_TESTING

    def test_recurrence(self):
        tz = pytz.timezone('Europe/Vienna')
        duration = timedelta(days=4)
        mock = MockEvent()
        mock.start = tz.localize(datetime(2011, 11, 11, 11, 0))
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
        self.orig_tz = set_env_timezone(TEST_TIMEZONE)

    def tearDown(self):
        set_env_timezone(self.orig_tz)

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

    def test_validate_dont_validate_incomplete(self):
        """Don't validate validate_start_end invariant, if start or end are
        None.
        """
        mock = MockEvent()
        mock.open_end = False

        mock.start = datetime(2016, 5, 18)
        mock.end = None
        try:
            IEventBasic.validateInvariants(mock)
        except:
            self.fail()

        mock.start = None
        mock.end = datetime(2016, 5, 18)
        try:
            IEventBasic.validateInvariants(mock)
        except:
            self.fail()

        mock.start = None
        mock.end = None
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
        tz = pytz.timezone('Europe/Berlin')
        e1 = createContentInContainer(
            self.portal,
            'Event',
            title=u'event1',
            start=tz.localize(datetime(2011, 11, 11, 11, 0)),
            end=tz.localize(datetime(2011, 11, 11, 12, 0)),
        )

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
        tz = pytz.timezone('Europe/Berlin')
        e1 = createContentInContainer(
            self.portal,
            'Event',
            title=u'event1',
            start=tz.localize(datetime(2011, 11, 11, 11, 0)),
            end=tz.localize(datetime(2011, 11, 11, 12, 0)),
        )

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
