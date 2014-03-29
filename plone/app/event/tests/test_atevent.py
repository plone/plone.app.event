from DateTime import DateTime
from Products.ATContentTypes.interfaces import IATEvent as IATEvent_ATCT
from Products.ATContentTypes.tests.utils import EmailValidator
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import NotRequiredTidyHTMLValidator
from Products.ATContentTypes.tests.utils import URLValidator
from Products.ATContentTypes.tests.utils import dcEdit
from Products.Archetypes import atapi
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from datetime import datetime
from plone.app.event.at.content import default_end
from plone.app.event.at.content import default_start
from plone.app.event.at.interfaces import IATEvent
from plone.app.event.at.interfaces import IATEventRecurrence
from plone.app.event.base import default_timezone
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import set_env_timezone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IEventRecurrence
from plone.event.utils import pydt
from plone.formwidget.datetime.at import DatetimeWidget
from plone.formwidget.recurrence.at.widget import RecurrenceValidator
from plone.formwidget.recurrence.at.widget import RecurrenceWidget
from zope.event import notify
from zope.interface.verify import verifyObject
from zope.lifecycleevent import ObjectModifiedEvent

import itertools
import pytz
import unittest2 as unittest


TZNAME = "Europe/Vienna"

OBJ_DATA = {
    'location': 'my location',
    'subject': 'Meeting',
    'eventUrl': 'http://example.org/',
    'startDate': DateTime(TZNAME),    # Initialize with timezone, even if
    'endDate': DateTime(TZNAME) + 1,  # it wouldn't be needed here.
                                      # It's needed for test comparsion.
    'timezone': TZNAME,
    'contactName': 'John Doe',
    'contactPhone': '+1212356789',
    'contactEmail': 'john@example.org',
    'attendees': (
        'john@doe.com',
        'john@doe.org',
        'john@example.org'),
    'text': "lorem ipsum"}


class FakeRequest:

    def __init__(self):
        self.other = {}
        self.form = {}


class PAEventAccessorTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_event_accessor(self):
        utc = pytz.utc
        vienna = pytz.timezone('Europe/Vienna')

        self.portal.invokeFactory(
            'Event',
            'event1',
            description='a description',
            startDate=datetime(2011, 11, 11, 11, 0, tzinfo=utc),
            endDate=datetime(2011, 11, 11, 12, 0, tzinfo=utc),
            timezone='UTC',
            wholeDay=False
        )
        e1 = self.portal['event1']
        acc = IEventAccessor(e1)

        # TEST DATES
        self.assertEqual(acc.start, datetime(2011, 11, 11, 11, 0, tzinfo=utc))
        self.assertEqual(acc.end, datetime(2011, 11, 11, 12, 0, tzinfo=utc))

        acc.start = datetime(2011, 11, 13, 9, 0)  # tzinfo does not matter,
        acc.end = datetime(2011, 11, 13, 10, 0)  # it's set by subscription
                                                # adapter

        # If using EventAccessor's edit method, calling notify isn't needed
        acc.edit(timezone=u'Europe/Vienna')

        # accessor should return start/end datetimes in the event's timezone
        self.assertEqual(
            acc.start,
            datetime(2011, 11, 13, 9, 0, tzinfo=vienna))
        self.assertEqual(
            acc.end,
            datetime(2011, 11, 13, 10, 0, tzinfo=vienna))

        # start/end dates are stored in UTC zone on the context, but converted
        # to event's timezone via the attribute getter.
        self.assertEqual(
            e1.end(),
            DateTime('2011/11/13 10:00:00 Europe/Vienna')
        )

        # timezone should be the same on the event object and accessor
        self.assertEqual(e1.getTimezone(), acc.timezone)

        # Open End Test
        acc.edit(open_end=True)
        self.assertEqual(
            acc.start,
            datetime(2011, 11, 13, 9, 0, tzinfo=vienna))
        self.assertEqual(
            acc.end,
            datetime(2011, 11, 13, 23, 59, 59, tzinfo=vienna))

        # Whole Day Test
        acc.edit(whole_day=True, open_end=False)
        self.assertEqual(
            acc.start,
            datetime(2011, 11, 13, 0, 0, tzinfo=vienna))
        self.assertEqual(
            acc.end,
            datetime(2011, 11, 13, 23, 59, 59, tzinfo=vienna))

        # TEST DESCRIPTION
        self.assertTrue(acc.description == 'a description')
        acc.description = 'another desc'
        self.assertTrue(acc.description == 'another desc')

        # TEST OTHER PROPERTIES
        acc.title = u"An Event"
        acc.recurrence = u'RRULE:FREQ=DAILY;COUNT=5'
        acc.location = u"Home"
        acc.attendees = [u'me', u'you']
        acc.contact_name = u"Max Mustermann"
        acc.contact_email = u"test@test.com"
        acc.contact_phone = u"+1234567890"
        acc.event_url = u"http://plone.org/"
        acc.subjects = [u"tag1", u"tag2"]
        acc.text = u"body text with <b>html</b> formating."

        # If not using EventAccessor's edit method, call notify manually
        notify(ObjectModifiedEvent(acc.context))

        self.assertEqual(acc.recurrence, u'RRULE:FREQ=DAILY;COUNT=5')
        self.assertEqual(acc.location, u'Home')
        self.assertEqual(acc.attendees, (u'me', u'you'))
        self.assertEqual(acc.contact_name, u"Max Mustermann")
        self.assertEqual(acc.contact_email, u'test@test.com')
        self.assertEqual(acc.contact_phone, u"+1234567890")
        self.assertEqual(acc.event_url, u"http://plone.org/")
        self.assertEqual(acc.subjects, (u"tag1", u"tag2"))
        self.assertEqual(acc.text, u"body text with <b>html</b> formating.")


class PAEventATTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(type_name='Event', id='event1', title='Event1')
        self.obj = portal['event1']
        set_env_timezone(TZNAME)

    def _edit_atevent(self, obj):
        dcEdit(obj)
        obj.setLocation(OBJ_DATA['location'])
        obj.setSubject(OBJ_DATA['subject'])
        obj.setEventUrl(OBJ_DATA['eventUrl'])
        obj.setStartDate(OBJ_DATA['startDate'])
        obj.setEndDate(OBJ_DATA['endDate'])
        obj.setContactName(OBJ_DATA['contactName'])
        obj.setContactPhone(OBJ_DATA['contactPhone'])
        obj.setContactEmail(OBJ_DATA['contactEmail'])
        obj.setAttendees(OBJ_DATA['attendees'])
        obj.setText(OBJ_DATA['text'])
        obj.setTimezone(OBJ_DATA['timezone'])
        notify(ObjectModifiedEvent(obj))

    def test_implementsInterfaces(self):
        """Test if an ATEvent object implements all relevant interfaces.

        """
        self.assertTrue(IEvent.providedBy(self.obj))
        self.assertTrue(IEventRecurrence.providedBy(self.obj))
        self.assertTrue(IATEvent.providedBy(self.obj))
        self.assertTrue(IATEventRecurrence.providedBy(self.obj))

        self.assertTrue(IATEvent_ATCT.providedBy(self.obj))
        self.assertTrue(verifyObject(IATEvent_ATCT, self.obj))

    def test_validation(self):
        req = FakeRequest()

        # Also return any given errors
        req.form.update({'startDate': '2010-10-30'})
        err = {'endDate': None}
        errors = self.obj.validate(req, err)
        self.assertEqual(errors, err)

        # Bad input
        req.form.update({'startDate': '2x10-10-30'})
        req.form.update({'endDate': 'bla'})
        errors = self.obj.validate(req, errors=None)
        self.assertTrue('startDate' in errors)
        self.assertTrue('endDate' in errors)

        # Start date must be before end date
        req.form.update({'startDate': '2010-10-30', 'endDate': '2010-10-01'})
        errors = self.obj.validate(req, errors=None)
        self.assertTrue('endDate' in errors)

        # ... except if open_end=True
        req.form.update({'startDate': '2010-10-30', 'endDate': '2010-10-01',
                         'openEnd': True})
        errors = self.obj.validate(req, errors=None)
        self.assertEqual(errors, {})

    def test_edit(self):
        new = self.obj
        self._edit_atevent(new)
        self.assertEqual(new.start_date, pydt(new.start()))
        self.assertEqual(new.end_date, pydt(new.end()))

        # TODO: sometimes the following tests fails, because of comparison of
        # microseconds. Is it an rounding error?
        # AssertionError: datetime.datetime(2012, 10, 25, 14, 2, 11, 855640,
        # tzinfo=<DstTzInfo 'Europe/Vienna' CEST+2:00:00 DST>) !=
        # datetime.datetime(2012, 10, 25, 14, 2, 11, 85564, tzinfo=<DstTzInfo
        # 'Europe/Vienna' CEST+2:00:00 DST>)
        self.assertEqual(new.start_date, pydt(OBJ_DATA['startDate']))
        self.assertEqual(new.end_date, pydt(OBJ_DATA['endDate']))
        self.assertEqual(new.duration, new.end_date - new.start_date)

    def test_sane_start_end(self):
        self.assertTrue(self.obj.start() <= self.obj.end())

    def test_cmp(self):
        portal = self.portal
        e1 = self.obj
        portal.invokeFactory(type_name='Event', id='event2', title='Event 2')
        e2 = portal['event2']

        day29 = DateTime('2004-12-29 0:00:00')
        day30 = DateTime('2004-12-30 0:00:00')
        day31 = DateTime('2004-12-31 0:00:00')

        e1.edit(startDate=day29, endDate=day30, title='event')
        e2.edit(startDate=day29, endDate=day30, title='event')
        self.assertEqual(cmp(e1, e2), 0)

        # start date
        e1.edit(startDate=day29, endDate=day30, title='event')
        e2.edit(startDate=day30, endDate=day31, title='event')
        self.assertEqual(cmp(e1, e2), -1)  # e1 < e2

        # duration
        e1.edit(startDate=day29, endDate=day30, title='event')
        e2.edit(startDate=day29, endDate=day31, title='event')
        self.assertEqual(cmp(e1, e2), -1)  # e1 < e2

        # title
        e1.edit(startDate=day29, endDate=day30, title='event')
        e2.edit(startDate=day29, endDate=day30, title='evenz')
        self.assertEqual(cmp(e1, e2), -1)  # e1 < e2

    def test_get_size(self):
        event = self.obj
        self._edit_atevent(event)
        self.assertEqual(event.get_size(), len(OBJ_DATA['text']))

    def test_data_postprocessing(self):
        # TODO: since we use an IEventAccessor here, this is a possible
        # canditate for merging with
        # the test_dxevent.TestDXIntegration.test_data_postprocessing test.

        # Addressing bug #62
        self.portal.invokeFactory(
            'Event',
            'ate1',
            startDate=DateTime(2012, 10, 19, 0, 30),
            endDate=DateTime(2012, 10, 19, 1, 30),
            timezone="Europe/Vienna",
            wholeDay=False
        )
        e1 = self.portal['ate1']
        e1.reindexObject()

        acc = IEventAccessor(e1)

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

        # See, if start isn't moved by timezone offset.
        self.assertTrue(acc.start == dt_1)
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(acc.start == dt_1)

        # After timezone changes, only the timezone should be applied, but the
        # date and time values not converted.
        acc.timezone = tzname_2
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(acc.start == dt_2)

        # Likewise with wholeDay events. If values were converted, the days
        # would drift apart.
        acc.whole_day = True
        acc.timezone = tzname_1
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(acc.start == dt_1_1)
        self.assertTrue(acc.end == dt_1_2)

        acc.timezone = tzname_2
        notify(ObjectModifiedEvent(e1))
        self.assertTrue(acc.start == dt_2_1)
        self.assertTrue(acc.end == dt_2_2)


class PAEventCMFEditTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        setRoles(portal, TEST_USER_ID, ['Manager'])
        set_env_timezone(TZNAME)

    def testEventCreate(self):
        self.portal.invokeFactory('Event', id='event',
                                  title='Foo',
                                  start_date='2003-09-18',
                                  end_date='2003-09-19')
        self.assertEqual(self.portal.event.Title(), 'Foo')
        self.assertTrue(self.portal.event.start().ISO8601()
                            .startswith('2003-09-18T00:00:00'))
        self.assertTrue(self.portal.event.end().ISO8601()
                            .startswith('2003-09-19T00:00:00'))

    def testEventEdit(self):
        self.portal.invokeFactory('Event', id='event')
        if not getattr(self.portal.event, 'event_edit', None):
            # event_edit script is removed in Plone 5
            return
        self.portal.event.event_edit(title='Foo',
                                     start_date='2003-09-18',
                                     end_date='2003-09-19')
        self.assertEqual(self.portal.event.Title(), 'Foo')
        self.assertTrue(self.portal.event.start().ISO8601()
                            .startswith('2003-09-18T00:00:00'))
        self.assertTrue(self.portal.event.end().ISO8601()
                            .startswith('2003-09-19T00:00:00'))


class PAEventATFieldTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(type_name='Event', id='event1', title='Event1')
        self.obj = portal['event1']

    def test_attendeesField(self):
        field = self.obj.getField('attendees')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == (),
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'getAttendees',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setAttendees',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'lines', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(isinstance(field.widget, atapi.LinesWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactEmailField(self):
        field = self.obj.getField('contactEmail')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0,
                        'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'contact_email',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setContactEmail',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'string', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == EmailValidator,
                        'Value is %s' % str(field.validators))
        self.assertTrue(isinstance(field.widget, atapi.StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactNameField(self):
        field = self.obj.getField('contactName')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'contact_name',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setContactName',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'string', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.assertTrue(isinstance(field.widget, atapi.StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactPhoneField(self):
        field = self.obj.getField('contactPhone')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'contact_phone',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setContactPhone',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'string', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertEqual(field.validators, EmptyValidator)
        self.assertTrue(isinstance(field.widget, atapi.StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_endDateField(self):
        field = self.obj.getField('endDate')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 1, 'Value is %s' % field.required)
        self.assertTrue(field.default is None,
                        'Value is %s' % str(field.default))
        self.assertTrue(field.default_method == default_end,
                        'Value is %s' % str(field.default_method))
        self.assertTrue(field.searchable is False,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'end',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setEndDate',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'datetime', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.assertTrue(isinstance(field.widget, DatetimeWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_eventUrlField(self):
        field = self.obj.getField('eventUrl')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'event_url',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setEventUrl',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'string', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertEqual(field.validators, URLValidator)
        self.assertTrue(isinstance(field.widget, atapi.StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_locationField(self):
        field = self.obj.getField('location')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'getLocation',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setLocation',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'string', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.assertTrue(isinstance(field.widget, atapi.StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_recurrenceField(self):
        field = self.obj.getField('recurrence')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable is False,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'getRecurrence',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setRecurrence',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'string', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )

        # flatten nested tuples
        valis = list(itertools.chain(*field.validators))
        is_recval = False
        for vali in valis:
            is_recval = is_recval or isinstance(vali, RecurrenceValidator)
        self.assertTrue(is_recval)

        self.assertTrue(isinstance(field.widget, RecurrenceWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_startDateField(self):
        field = self.obj.getField('startDate')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 1, 'Value is %s' % field.required)
        self.assertTrue(field.default is None,
                        'Value is %s' % str(field.default))
        self.assertTrue(field.default_method == default_start,
                        'Value is %s' % str(field.default_method))
        self.assertTrue(field.searchable is False,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'start',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setStartDate',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'datetime', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.assertTrue(isinstance(field.widget, DatetimeWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_subjectField(self):
        field = self.obj.getField('subject')
        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == (),
                        'Value is %s' % str(str(field.default)))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 1,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 1,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'Subject',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setSubject',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'mVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'lines', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.MetadataStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.MetadataStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == EmptyValidator,
                        'Value is %s' % repr(field.validators))
        self.assertTrue(isinstance(field.widget, atapi.KeywordWidget),
                        'Value is %s' % id(field.widget))

    def test_textField(self):
        field = self.obj.getField('text')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'getText',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setText',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'text', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') ==
            atapi.AnnotationStorage(migrate=True),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == NotRequiredTidyHTMLValidator,
                        'Value is %s' % repr(field.validators))
        self.assertTrue(isinstance(field.widget, atapi.RichWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

        self.assertTrue(field.primary == 1, 'Value is %s' % field.primary)
        self.assertTrue(field.default_content_type is None,
                        'Value is %s' % field.default_content_type)
        self.assertTrue(field.default_output_type == 'text/x-html-safe',
                        'Value is %s' % field.default_output_type)
        self.assertTrue('text/html' in field.getAllowedContentTypes(self.obj))

    def test_timezoneField(self):
        field = self.obj.getField('timezone')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 1, 'Value is %s' % field.required)
        self.assertTrue(field.default == '',
                        'Value is %s' % str(field.default))
        self.assertTrue(field.default_method == default_timezone,
                        'Value is %s' % str(field.default_method))
        self.assertTrue(field.searchable == 0,
                        'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.vocabulary_factory ==
                        u'plone.app.event.AvailableTimezones')
        self.assertTrue(field.enforceVocabulary is True,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'getTimezone',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setTimezone',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'string', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertTrue(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.assertTrue(isinstance(field.widget, atapi.SelectionWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue('Africa/Abidjan' in tuple(vocab),
                        'Value is %s' % str(tuple(vocab)))

    def test_wholeDayField(self):
        field = self.obj.getField('wholeDay')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default is False,
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 0,
                        'Value is %s' % field.searchable)
        self.assertTrue(
            field.vocabulary == (('True', 'Yes', 'yes'),
                                 ('False', 'No', 'no')),
            'Value is %s' % str(field.vocabulary)
        )
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'getWholeDay',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setWholeDay',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'boolean', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertEqual(field.validators, EmptyValidator)
        self.assertTrue(isinstance(field.widget, atapi.BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(
            tuple(vocab) == ('True', 'False'),
            'Value is %s' % str(tuple(vocab))
        )

    def test_openEndField(self):
        field = self.obj.getField('openEnd')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default is False,
                        'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 0,
                        'Value is %s' % field.searchable)
        self.assertTrue(
            field.vocabulary == (('True', 'Yes', 'yes'),
                                 ('False', 'No', 'no')),
            'Value is %s' % str(field.vocabulary)
        )
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0,
                        'Value is %s' % field.isMetadata)
        self.assertTrue(field.accessor == 'getOpenEnd',
                        'Value is %s' % field.accessor)
        self.assertTrue(field.mutator == 'setOpenEnd',
                        'Value is %s' % field.mutator)
        self.assertTrue(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.assertTrue(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.assertTrue(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.assertTrue(field.force == '', 'Value is %s' % field.force)
        self.assertTrue(field.type == 'boolean', 'Value is %s' % field.type)
        self.assertTrue(isinstance(field.storage, atapi.AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(
            field.getLayerImpl('storage') == atapi.AttributeStorage(),
            'Value is %s' % field.getLayerImpl('storage')
        )
        self.assertEqual(field.validators, EmptyValidator)
        self.assertTrue(isinstance(field.widget, atapi.BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(
            tuple(vocab) == ('True', 'False'),
            'Value is %s' % str(tuple(vocab))
        )

    def test_openEnd_handler(self):
        event_id = self.portal.invokeFactory(
            'Event',
            id="event",
            startDate='2000/10/12 06:00:00',
            endDate='2000/10/14 18:00:00',
            timezone=TZNAME,
            openEnd=True
        )
        event = self.portal[event_id]
        self.assertTrue(event.getOpenEnd())
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Date(), '2000/10/12')
        self.assertEqual(event.end().Time(), '23:59:59')

    def test_wholeday_handler(self):
        event_id = self.portal.invokeFactory(
            'Event',
            id="event",
            startDate='2000/10/12 06:00:00',
            endDate='2000/10/13 18:00:00',
            timezone=TZNAME,
            wholeDay=True
        )
        event = self.portal[event_id]
        self.assertTrue(event.getWholeDay())
        self.assertEqual(event.start().Time(), '00:00:00')
        self.assertEqual(event.end().Time(), '23:59:59')

    def test_wholeday_handler_notwholeday(self):
        event_id = self.portal.invokeFactory(
            'Event',
            id="event",
            startDate='2000/10/12 06:00:00',
            endDate='2000/10/13 18:00:00',
            timezone=TZNAME
        )
        event = self.portal[event_id]
        self.assertFalse(event.getWholeDay())
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Time(), '18:00:00')

    def test_timezone_handler(self):
        event_id = self.portal.invokeFactory(
            'Event',
            id="event",
            startDate='2000/10/12 06:00:00',
            endDate='2000/10/13 18:00:00',
            timezone=TZNAME
        )
        event = self.portal[event_id]
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Time(), '18:00:00')
        self.assertEqual(event.start().timezone(), TZNAME)
        self.assertEqual(event.end().timezone(), TZNAME)
        self.assertEqual(event.start_date.tzinfo.zone, TZNAME)
        self.assertEqual(event.end_date.tzinfo.zone, TZNAME)
