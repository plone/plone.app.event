from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.Archetypes import atapi
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.tests.utils import mkDummyInContext
from plone.app.event.at.content import ATEvent
from plone.app.event.at.content import ATEventSchema
from plone.app.event.at.upgrades.event import upgrade_step_1
from plone.app.event.testing import PAEventAT_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent

import unittest2 as unittest
import zope.interface


# For Schema upgrade test, copy the ATEventSchema and add timezone and
# recurrence field with AnnotationStorage
MockSchema = ATEventSchema.copy()
MockSchema.addField(
    atapi.StringField(
        'timezone',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(),
    )
)
MockSchema.addField(
    atapi.StringField(
        'recurrence',
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
    layer = PAEventAT_FUNCTIONAL_TESTING

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
