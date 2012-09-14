from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.interfaces.event import IATEvent
from Products.Archetypes.BaseContent import BaseContent
from Products.Archetypes.tests.utils import mkDummyInContext
from plone.app.event.at.upgrades.event import migrateATEvents
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.interfaces import IEvent
import unittest2 as unittest
import zope.interface


class MockATEvent(BaseContent):

    zope.interface.implements(IATEvent)
    portal_type = 'Event'
    meta_type = 'ATEvent'


class PAEventATMigrationTest(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        portal = self.layer['portal']
        self.portal = portal
        setRoles(portal, TEST_USER_ID, ['Manager'])
        self._dummy = mkDummyInContext(MockATEvent, oid='dummy',
                                       context=self.portal,
                                       schema=ATContentTypeSchema)
        self._dummy.title = 'Foo'
        self._dummy.reindexObject()

    def test_upgradeATEvent(self):
        migrateATEvents(self.portal)
        event = self.portal['dummy']
        self.assertTrue(IEvent.providedBy(event))
        self.assertEqual('', event.recurrence)
        self.assertEqual('Foo', event.Title())

