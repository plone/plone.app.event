from DateTime import DateTime
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.Archetypes import atapi
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.tests.utils import mkDummyInContext
from plone.app.event.at.upgrades.event import upgrade_step_1, upgrade_step_2
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent
import unittest2 as unittest
import zope.interface
from plone.app.event.at.content import ATEvent

MockSchema = ATContentTypeSchema.copy() + atapi.Schema((
    atapi.DateTimeField('startDate',
        accessor='start',
        default_method=DateTime,
        widget=atapi.StringWidget(),
    ),
    atapi.DateTimeField('endDate',
        accessor='end',
        default_method=DateTime,
        widget=atapi.StringWidget(),
    ),
    atapi.StringField('timezone',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(),
        ),
    atapi.StringField('recurrence',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(),
    ),
))

class MockATEvent_1(BaseContent):
    zope.interface.implements(IATEvent)
    portal_type = 'Event'
    meta_type = 'ATEvent'


class MockATEvent_2(ATEvent):
    zope.interface.implements(IATEvent)
    schema = MockSchema
    portal_type = 'Event'
    meta_type = 'ATEvent'


class PAEventATMigrationTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        setRoles(portal, TEST_USER_ID, ['Manager'])
        self._dummy_1 = mkDummyInContext(MockATEvent_1, oid='dummy_1',
                                       context=self.portal,
                                       schema=ATContentTypeSchema)
        self._dummy_1.title = 'Foo'
        self._dummy_1.reindexObject()

        #self._dummy_2 = mkDummyInContext(MockATEvent_2, oid='dummy_2',
        #                               context=self.portal,
        #                               schema=MockSchema)
        #self._dummy_2.title = 'Baz'
        #self._dummy_2.setStartDate(DateTime())
        #self._dummy_2.setEndDate(DateTime())
        #self._dummy_2.setTimezone("Europe/Vienna")
        #self._dummy_2.setRecurrence("RRULE:FREQ=DAILY;COUNT=3")
        #self._dummy_2.reindexObject()

    def test_upgrade_step_1(self):
        upgrade_step_1(self.portal)
        event = self.portal['dummy_1']
        self.assertTrue(IEvent.providedBy(event))
        self.assertEqual('', event.recurrence)
        self.assertEqual('Foo', event.Title())

#    def test_upgrade_step_2(self):
#
#        upgrade_step_2(self.portal)
#
#        event = self.portal['dummy_2']
#        tz_field = event.getField('timezone')
#        re_field = event.getField('recurrence')
#        self.assertTrue(isinstance(tz_field.storage, atapi.AttributeStorage))
#        self.assertTrue(tz_field.getLayerImpl('storage') ==
#                        atapi.AttributeStorage())
#        self.assertTrue(isinstance(re_field.storage, atapi.AttributeStorage))
#        self.assertTrue(re_field.getLayerImpl('storage') ==
#                        atapi.AttributeStorage())
