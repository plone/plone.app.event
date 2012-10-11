import os
import itertools

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.interfaces.layer import ILayerContainer

from Products.Archetypes import atapi

from Products.ATContentTypes.tests.utils import dcEdit
from Products.ATContentTypes.tests.utils import EmptyValidator
from Products.ATContentTypes.tests.utils import EmailValidator
from Products.ATContentTypes.tests.utils import URLValidator
from Products.ATContentTypes.tests.utils import NotRequiredTidyHTMLValidator

from DateTime import DateTime

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest

from Products.ATContentTypes.interfaces import IATEvent as IATEvent_ATCT
from plone.event.interfaces import IEvent, IEventRecurrence
from plone.app.event.at.interfaces import IATEvent, IATEventRecurrence

from plone.event.utils import pydt
from plone.app.event.ical import EventsICal
from plone.app.event.base import (
    default_start_DT,
    default_end_DT,
    default_timezone,
    dates_for_display
)

from plone.formwidget.datetime.at import DatetimeWidget
from plone.formwidget.recurrence.at.widget import RecurrenceWidget
from plone.formwidget.recurrence.at.widget import RecurrenceValidator

import unittest2 as unittest
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.testing import set_env_timezone
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


TZNAME = "Europe/Vienna"

OBJ_DATA = {
    'location': 'my location',
    'subject': 'Meeting',
    'eventUrl': 'http://example.org/',
    'startDate': DateTime(TZNAME), # Initialize with timezone, even if
    'endDate': DateTime(TZNAME)+1, # it wouldn't be needed here.
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
        req = {'startDate':'2010-10-30'}
        err = {'endDate':None}
        errors = err.copy()
        self.obj.post_validate(req, errors)
        self.assertEqual(errors, err)
        req = {'startDate':'2x10-10-30'}
        errors = {}
        self.obj.post_validate(req, errors)
        self.assertTrue('startDate' in errors)

    def test_edit(self):
        new = self.obj
        self._edit_atevent(new)
        self.assertEqual(new.start_date, pydt(new.start()))
        self.assertEqual(new.end_date, pydt(new.end()))
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

        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day30, title='event')
        self.assertEqual(cmp(e1, e2), 0)

        # start date
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day30, endDate=day31, title='event')
        self.assertEqual(cmp(e1, e2), -1) # e1 < e2

        # duration
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day31, title='event')
        self.assertEqual(cmp(e1, e2), -1)  # e1 < e2

        # title
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day30, title='evenz')
        self.assertEqual(cmp(e1, e2), -1)  # e1 < e2

    def test_get_size(self):
        event = self.obj
        self._edit_atevent(event)
        self.assertEqual(event.get_size(), len(OBJ_DATA['text']))


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
        self.assertTrue(field.default == (), 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.assertTrue(isinstance(field.widget, atapi.LinesWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactEmailField(self):
        field = self.obj.getField('contactEmail')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == None, 'Value is %s' % str(field.default))
        self.assertTrue(field.default_method == default_end_DT,
                        'Value is %s' % str(field.default_method))
        self.assertTrue(field.searchable == False, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == False, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(isinstance(field.storage, atapi.AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(field.getLayerImpl('storage') == atapi.AnnotationStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))

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
        self.assertTrue(field.default == None , 'Value is %s' % str(field.default))
        self.assertTrue(field.default_method == default_start_DT , 'Value is %s' % str(field.default_method))
        self.assertTrue(field.searchable == False, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == (), 'Value is %s' % str(str(field.default)))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 1,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 1, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.MetadataStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.assertTrue(field.validators == EmptyValidator,
                        'Value is %s' % repr(field.validators))
        self.assertTrue(isinstance(field.widget, atapi.KeywordWidget),
                        'Value is %s' % id(field.widget))

    def test_textField(self):
        field = self.obj.getField('text')

        self.assertTrue(ILayerContainer.providedBy(field))
        self.assertTrue(field.required == 0, 'Value is %s' % field.required)
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 1, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == '', 'Value is %s' % str(field.default))
        self.assertTrue(field.default_method == default_timezone,
                        'Value is %s' % str(field.default_method))
        self.assertTrue(field.searchable == 0, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.vocabulary_factory ==
                        u'plone.app.event.AvailableTimezones')
        self.assertTrue(field.enforceVocabulary == True,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(isinstance(field.storage, atapi.AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.assertTrue(field.getLayerImpl('storage') == atapi.AnnotationStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
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
        self.assertTrue(field.default == False, 'Value is %s' % str(field.default))
        self.assertTrue(field.searchable == 0, 'Value is %s' % field.searchable)
        self.assertTrue(field.vocabulary == (('True', 'Yes', 'yes'), ('False', 'No', 'no')),
                        'Value is %s' % str(field.vocabulary))
        self.assertTrue(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.assertTrue(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.assertTrue(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
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
        self.assertTrue(field.getLayerImpl('storage') == atapi.AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.assertEqual(field.validators, EmptyValidator)
        self.assertTrue(isinstance(field.widget, atapi.BooleanWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.assertTrue(isinstance(vocab, atapi.DisplayList),
                        'Value is %s' % type(vocab))
        self.assertTrue(tuple(vocab) == ('True', 'False'), 'Value is %s' % str(tuple(vocab)))


    def test_wholeday_handler(self):
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/13 18:00:00',
                timezone=TZNAME,
                wholeDay=True)
        event = self.portal[event_id]
        self.assertTrue(event.whole_day)
        self.assertEqual(event.start().Time(), '00:00:00')
        self.assertEqual(event.end().Time(), '23:59:59')

    def test_wholeday_handler_notwholeday(self):
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/13 18:00:00',
                timezone=TZNAME)
        event = self.portal[event_id]
        self.assertFalse(event.whole_day)
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Time(), '18:00:00')

    def test_timezone_handler(self):
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/13 18:00:00',
                timezone=TZNAME)
        event = self.portal[event_id]
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Time(), '18:00:00')
        self.assertEqual(event.start().timezone(), TZNAME)
        self.assertEqual(event.end().timezone(), TZNAME)
        self.assertEqual(event.start_date.tzinfo.zone, TZNAME)
        self.assertEqual(event.end_date.tzinfo.zone, TZNAME)
