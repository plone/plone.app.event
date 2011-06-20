import os

from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.utils import safe_unicode
from Products.Archetypes.interfaces.layer import ILayerContainer
from Products.Archetypes.atapi import *

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

from Products.ATContentTypes.interfaces import IATEvent
from plone.event.tests.test_doctest import FakeEvent
from plone.event.utils import pydt
from plone.app.event.at.content import ATEvent
from plone.app.event.interfaces import ICalendarSupport
from plone.app.event.browser.vcal import EventsVCal
from plone.app.event.browser.ical import EventsICal
from plone.app.event.browser.event_view import toDisplay
from plone.app.event.base import default_end_date

from plone.formwidget.dateinput.at import DatetimeWidget


import unittest2 as unittest
from plone.app.event.at.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


OBJ_DATA = {
    'location': 'my location',
    'subject': 'Meeting',
    'eventUrl': 'http://example.org/'
    'startDate': DateTime(),
    'endDate': DateTime()+1,
    'contactName': 'John Doe',
    'contactPhone': '+1212356789',
    'contactEmail': 'john@example.org',
    'attendees': (
        'john@doe.com',
        'john@doe.org',
        'john@example.org')
    'text': "lorem ipsum"}


class PAEventATTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(type_name='Event', id='event1', title='Event1')
        self.obj = portal['event1']


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

    def test_doesImplementCalendarSupport(self):
        self.failUnless(ICalendarSupport.providedBy(self.obj))
        self.failUnless(verifyObject(ICalendarSupport, self.obj))

    def test_implementsATEvent(self):
        self.failUnless(iface.providedBy(self.obj))
        self.failUnless(verifyObject(IATEvent, self.obj))

    def test_props(self):
        self.assertEquals(self.obj.cmf_edit_kws,
                ('effectiveDay', 'effectiveMo', 'effectiveYear',
                 'expirationDay', 'expirationMo', 'expirationYear',
                 'start_time', 'startAMPM', 'stop_time', 'stopAMPM',
                 'start_date', 'end_date', 'contact_name', 'contact_email',
                 'contact_phone', 'event_url'))

    def test_cmfedit(self):
        self.assertNotEqual(self.obj.end().Date(), '2010/10/31')
        self.obj.cmf_edit(start_date='2010-10-30', end_date='2010-10-31')
        self.assertEqual(self.obj.end().Date(), '2010/10/31')

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
        self.assertEquals(new.start_date, pydt(new.start()))
        self.assertEquals(new.end_date, pydt(new.end()))
        self.assertEquals(new.start_date, pydt(OBJ_DATA['startDate']))
        self.assertEquals(new.end_date, pydt(OBJ_DATA['endDate']))
        self.assertEquals(new.duration, new.end_date - new.start_date)

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
        self.failUnlessEqual(cmp(e1, e2), 0)

        # start date
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day30, endDate=day31, title='event')
        self.failUnlessEqual(cmp(e1, e2), -1) # e1 < e2

        # duration
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day31, title='event')
        self.failUnlessEqual(cmp(e1, e2), -1)  # e1 < e2

        # title
        e1.edit(startDate = day29, endDate=day30, title='event')
        e2.edit(startDate = day29, endDate=day30, title='evenz')
        self.failUnlessEqual(cmp(e1, e2), -1)  # e1 < e2

    def test_ical(self):
        event = self.obj
        event.setStartDate(DateTime('2001/01/01 12:00:00 GMT+1'))
        event.setEndDate(DateTime('2001/01/01 14:00:00 GMT+1'))
        event.setTitle('cool event')
        view = EventsICal(event, TestRequest())
        ical = view.getICal()
        lines = ical.split('\n')
        self.assertEqual(lines[0], u"BEGIN:VEVENT")
        self.assertEqual(lines[5], u"SUMMARY:%s" % safe_unicode(event.Title()))
        # times should be converted to UTC
        self.assertEqual(lines[6], u"DTSTART:20010101T110000Z")
        self.assertEqual(lines[7], u"DTEND:20010101T130000Z")

    def test_vcal(self):
        event = self.obj
        event.setStartDate(DateTime('2001/01/01 12:00:00 GMT+1'))
        event.setEndDate(DateTime('2001/01/01 14:00:00 GMT+1'))
        event.setTitle('cool event')
        view = EventsVCal(event, TestRequest())
        vcal = view.getVCal()
        lines = vcal.split(u'\n')
        self.assertEqual(lines[0], u"BEGIN:VEVENT")
        self.assertEqual(lines[7], u"SUMMARY:%s" % safe_unicode(event.Title()))
        # times should be converted to UTC
        self.assertEqual(lines[1], u"DTSTART:20010101T110000Z")
        self.assertEqual(lines[2], u"DTEND:20010101T130000Z")

    def test_get_size(self):
        event = self.obj
        self._edit_atevent(event)
        self.failUnlessEqual(event.get_size(), len(OBJ_DATA['text']))


class PAEventATFieldTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        setRoles(portal, TEST_USER_ID, ['Manager'])
        portal.invokeFactory(type_name='Event', id='event1', title='Event1')
        self.obj = portal['event1']

    def test_locationField(self):
        field = self.obj.getField('location')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getLocation',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setLocation',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission == ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_subjectField(self):
        field = self.obj.getField('subject')
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == (), 'Value is %s' % str(str(field.default)))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 1,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 1, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'Subject',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setSubject',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'mVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'lines', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, MetadataStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == MetadataStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % repr(field.validators))
        self.failUnless(isinstance(field.widget, KeywordWidget),
                        'Value is %s' % id(field.widget))


    def test_eventUrlField(self):
        field = self.obj.getField('eventUrl')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'event_url',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setEventUrl',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnlessEqual(field.validators, URLValidator)
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_startDateField(self):
        field = self.obj.getField('startDate')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == None , 'Value is %s' % str(field.default))
        self.failUnless(field.default_method == DateTime , 'Value is %s' % str(field.default_method))
        self.failUnless(field.searchable == False, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'start',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setStartDate',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'datetime', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, DatetimeWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))


    def test_endDateField(self):
        field = self.obj.getField('endDate')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 1, 'Value is %s' % field.required)
        self.failUnless(field.default == None, 'Value is %s' % str(field.default))
        self.failUnless(field.default_method == default_end_date,
                        'Value is %s' % str(field.default_method))
        self.failUnless(field.searchable == False, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'end',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setEndDate',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'datetime', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.validators == (),
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, DatetimeWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactNameField(self):
        field = self.obj.getField('contactName')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'contact_name',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setContactName',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.validators == EmptyValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactEmailField(self):
        field = self.obj.getField('contactEmail')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'contact_email',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setContactEmail',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.validators == EmailValidator,
                        'Value is %s' % str(field.validators))
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_contactPhoneField(self):
        field = self.obj.getField('contactPhone')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'contact_phone',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setContactPhone',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'string', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnlessEqual(field.validators, EmptyValidator)
        self.failUnless(isinstance(field.widget, StringWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_attendeesField(self):
        field = self.obj.getField('attendees')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == (), 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getAttendees',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setAttendees',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'lines', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AttributeStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AttributeStorage(),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(isinstance(field.widget, LinesWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

    def test_textField(self):
        field = self.obj.getField('text')

        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.required == 0, 'Value is %s' % field.required)
        self.failUnless(field.default == '', 'Value is %s' % str(field.default))
        self.failUnless(field.searchable == 1, 'Value is %s' % field.searchable)
        self.failUnless(field.vocabulary == (),
                        'Value is %s' % str(field.vocabulary))
        self.failUnless(field.enforceVocabulary == 0,
                        'Value is %s' % field.enforceVocabulary)
        self.failUnless(field.multiValued == 0,
                        'Value is %s' % field.multiValued)
        self.failUnless(field.isMetadata == 0, 'Value is %s' % field.isMetadata)
        self.failUnless(field.accessor == 'getText',
                        'Value is %s' % field.accessor)
        self.failUnless(field.mutator == 'setText',
                        'Value is %s' % field.mutator)
        self.failUnless(field.read_permission == View,
                        'Value is %s' % field.read_permission)
        self.failUnless(field.write_permission ==
                        ModifyPortalContent,
                        'Value is %s' % field.write_permission)
        self.failUnless(field.generateMode == 'veVc',
                        'Value is %s' % field.generateMode)
        self.failUnless(field.force == '', 'Value is %s' % field.force)
        self.failUnless(field.type == 'text', 'Value is %s' % field.type)
        self.failUnless(isinstance(field.storage, AnnotationStorage),
                        'Value is %s' % type(field.storage))
        self.failUnless(field.getLayerImpl('storage') == AnnotationStorage(migrate=True),
                        'Value is %s' % field.getLayerImpl('storage'))
        self.failUnless(ILayerContainer.providedBy(field))
        self.failUnless(field.validators == NotRequiredTidyHTMLValidator,
                        'Value is %s' % repr(field.validators))
        self.failUnless(isinstance(field.widget, RichWidget),
                        'Value is %s' % id(field.widget))
        vocab = field.Vocabulary(self.obj)
        self.failUnless(isinstance(vocab, DisplayList),
                        'Value is %s' % type(vocab))
        self.failUnless(tuple(vocab) == (), 'Value is %s' % str(tuple(vocab)))

        self.failUnless(field.primary == 1, 'Value is %s' % field.primary)
        self.failUnless(field.default_content_type is None,
                        'Value is %s' % field.default_content_type)
        self.failUnless(field.default_output_type == 'text/x-html-safe',
                        'Value is %s' % field.default_output_type)
        self.failUnless('text/html' in field.getAllowedContentTypes(self.obj))

    def _makeOne(self, start, end, whole_day=False):
        event = FakeEvent(start=start, end=end, whole_day=whole_day)
        # ulocalized_time need the REQUEST attribute
        event.REQUEST = self.portal.REQUEST
        return event

    def testToDisplayWithTime(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00')
        self.assertEqual(toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : '06:00 AM',
                 'start_iso': '2000-10-12T06:00:00',
                 'end_date' : 'Oct 12, 2000',
                 'end_time' : '06:00 PM',
                 'end_iso': '2000-10-12T18:00:00',
                 'same_day' : True,
                 'same_time' : False,
                })

    def testToDisplayWholeDaySameDay(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/12 18:00:00',
                          whole_day=True)
        self.assertEqual(toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,
                 'start_iso': '2000-10-12T06:00:00',
                 'end_date' : 'Oct 12, 2000',
                 'end_time' : None,
                 'end_iso': '2000-10-12T18:00:00',
                 'same_day' : True,
                 'same_time' : False,
                })

    def testToDisplayWholeDayDifferentDays(self):
        event = self._makeOne('2000/10/12 06:00:00', '2000/10/13 18:00:00',
                          whole_day=True)
        self.assertEqual(toDisplay(event),
                {'start_date': 'Oct 12, 2000',
                 'start_time' : None,
                 'start_iso': '2000-10-12T06:00:00',
                 'end_date' : 'Oct 13, 2000',
                 'end_time' : None,
                 'end_iso': '2000-10-13T18:00:00',
                 'same_day' : False,
                 'same_time' : False,
                })

    def testWholeDayEventSubscriber(self):
        os.environ['TZ'] = "Europe/Vienna"
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/13 18:00:00',
                timezone="Europe/Vienna",
                wholeDay=True)
        event = self.portal[event_id]
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Time(), '18:00:00')
        self.assertTrue(event.whole_day())
        notify(ObjectModifiedEvent(event))
        self.assertEqual(event.start().Time(), '00:00:00')
        self.assertEqual(event.end().Time(), '23:59:59')

    def testWholeDayEventSubscriberNotWholeDayEvent(self):
        os.environ['TZ'] = "Europe/Vienna"
        event_id = self.portal.invokeFactory('Event',
                id="event",
                startDate='2000/10/12 06:00:00',
                endDate='2000/10/13 18:00:00',
                timezone="Europe/Vienna")
        event = self.portal[event_id]
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Time(), '18:00:00')
        self.assertFalse(event.whole_day())
        notify(ObjectModifiedEvent(event))
        self.assertEqual(event.start().Time(), '06:00:00')
        self.assertEqual(event.end().Time(), '18:00:00')
