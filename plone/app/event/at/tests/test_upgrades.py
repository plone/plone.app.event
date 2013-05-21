from DateTime import DateTime
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.Archetypes import atapi
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.tests.utils import mkDummyInContext
from plone.app.event.at.content import ATEvent
from plone.app.event.at.content import ATEventSchema
from plone.app.event.at.upgrades.event import upgrade_step_1
from plone.app.event.at.upgrades.event import upgrade_step_2
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent

import unittest2 as unittest
import zope.interface


# For Schema upgrade test, copy the ATEventSchema and add timezone and
# recurrence field with AnnotationStorage
MockSchema = ATEventSchema.copy()
MockSchema.addField(
    atapi.StringField('timezone',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(),
    )
)
MockSchema.addField(
    atapi.StringField('recurrence',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(),
    )
)


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

    def test_upgrade_step_1(self):
        _dummy_1 = mkDummyInContext(MockATEvent_1, oid='dummy_1',
                                    context=self.portal,
                                    schema=ATContentTypeSchema)
        _dummy_1.title = 'Foo'
        _dummy_1.reindexObject()

        event = self.portal['dummy_1']
        self.assertTrue(not IEvent.providedBy(event))
        del event

        upgrade_step_1(self.portal)

        event = self.portal['dummy_1']
        self.assertTrue(IEvent.providedBy(event))
        self.assertEqual('', event.recurrence)
        self.assertEqual('Foo', event.Title())

    def test_upgrade_step_2(self):
        _dummy_2 = mkDummyInContext(MockATEvent_2, oid='dummy_2',
                                    context=self.portal,
                                    schema=MockSchema)
        _dummy_2.title = 'Baz'
        _dummy_2.setStartDate(DateTime())
        _dummy_2.setEndDate(DateTime())
        _dummy_2.setTimezone("Europe/Vienna")
        _dummy_2.setRecurrence("RRULE:FREQ=DAILY;COUNT=3")
        _dummy_2.reindexObject()

        event = self.portal['dummy_2']

        # Old schema. Values as expected, storage is AnnotationStorage
        self.assertTrue(event.getTimezone() == 'Europe/Vienna')
        self.assertTrue(event.getRecurrence() == 'RRULE:FREQ=DAILY;COUNT=3')
        self.assertTrue(isinstance(event.getField('timezone').storage,
                                   atapi.AnnotationStorage))
        self.assertTrue(isinstance(event.getField('recurrence').storage,
                                   atapi.AnnotationStorage))

        schema = event.schema
        schema.addField(
            atapi.StringField('timezone',
                widget=atapi.StringWidget(),
            )
        )
        schema.addField(
            atapi.StringField('recurrence',
                widget=atapi.StringWidget(),
            )
        )

        # New schema before upgrade. Empty fields, storage is AttributeStorage
        self.assertTrue(event.getTimezone() == '')
        self.assertTrue(event.getRecurrence() == '')
        self.assertTrue(isinstance(event.getField('timezone').storage,
                                   atapi.AttributeStorage))
        self.assertTrue(isinstance(event.getField('recurrence').storage,
                                   atapi.AttributeStorage))

        # Upgrade!
        upgrade_step_2(self.portal)

        # New schema after upgrade. Values as expected, storage is
        # AttributeStorage
        self.assertTrue(event.getTimezone() == 'Europe/Vienna')
        self.assertTrue(event.getRecurrence() == 'RRULE:FREQ=DAILY;COUNT=3')
        self.assertTrue(isinstance(event.getField('timezone').storage,
                                   atapi.AttributeStorage))
        self.assertTrue(isinstance(event.getField('recurrence').storage,
                                   atapi.AttributeStorage))
