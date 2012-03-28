
import unittest2 as unittest

import datetime
from DateTime import DateTime

from zope.component import createObject
from zope.component import queryUtility

from plone.dexterity.interfaces import IDexterityFTI

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

from plone.app.event.dx.behaviors import (
    IEventBasic,
    IEventRecurrence,
    IEventLocation,
    IEventAttendees,
    IEventContact
)
from plone.app.event.dx.interfaces import (
    IDXEvent,
    IDXEventRecurrence,
    IDXEventLocation,
    IDXEventAttendees,
    IDXEventContact
)



from plone.app.event.testing import PAEventDX_INTEGRATION_TESTING

class TextDXIntegration(unittest.TestCase):
    layer = PAEventDX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='plone.app.event.dx.event')
        self.assertNotEquals(None, fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='plone.app.event.dx.event')
        factory = fti.factory
        new_object = createObject(factory)
        self.failUnless(IDXEvent.providedBy(new_object))
        self.failUnless(IDXEventRecurrence.providedBy(new_object))
        self.failUnless(IDXEventLocation.providedBy(new_object))
        self.failUnless(IDXEventAttendees.providedBy(new_object))
        self.failUnless(IDXEventContact.providedBy(new_object))

    def test_adding(self):
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime.datetime(2011,11,11,11,00),
                end=datetime.datetime(2011,11,11,12,00),
                timezone='CET',
                whole_day=False)
        e1 = self.portal['event1']
        self.failUnless(IDXEvent.providedBy(e1))
        self.failUnless(IDXEventRecurrence.providedBy(e1))
        self.failUnless(IDXEventLocation.providedBy(e1))
        self.failUnless(IDXEventAttendees.providedBy(e1))
        self.failUnless(IDXEventContact.providedBy(e1))

    def test_view(self):
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime.datetime(2011,11,11,11,00),
                end=datetime.datetime(2011,11,11,12,00),
                timezone='CET',
                whole_day=False)
        e1 = self.portal['event1']
        view = e1.restrictedTraverse('@@event_view')
        self.assertTrue(view.date_for_display() is not None)
        self.assertTrue(view.occurrences is not None)


    def test_start_end_dates_indexed(self):
        self.portal.invokeFactory('plone.app.event.dx.event', 'event1',
                start=datetime.datetime(2011,11,11,11,00),
                end=datetime.datetime(2011,11,11,12,00),
                timezone='CET',
                whole_day=False)
        e1 = self.portal['event1']
        e1.reindexObject()

        result = self.portal.portal_catalog(path='/'.join(e1.getPhysicalPath()))
        self.assertEquals(1, len(result))
        # result returns Zope's DateTime
        self.assertEquals(result[0].start, DateTime('2011/11/11 11:00:00 GMT+1'))
        self.assertEquals(result[0].end, DateTime('2011/11/11 12:00:00 GMT+1'))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
