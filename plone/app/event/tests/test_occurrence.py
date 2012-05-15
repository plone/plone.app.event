from DateTime import DateTime
from plone.app.event.at.content import IATEvent
from plone.app.event.interfaces import IEventAccessor
from plone.app.event.interfaces import IEventSettings
from plone.app.event.interfaces import IOccurrence
from plone.app.event.occurrence import Occurrence
from plone.app.event.occurrence import OccurrenceTraverser
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.event.utils import tzdel
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
import datetime
import transaction
import unittest2 as unittest
import zope.component


class TestTraversal(unittest.TestCase):

    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = "Australia/Brisbane"

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(type_name='Event', id='at',
                                  title='Event1',
                                  start=DateTime('Australia/Brisbane'),
                                  end=DateTime('Australia/Brisbane') + 1)
        self.at = self.portal['at']
        self.at_traverser = OccurrenceTraverser(self.at, self.layer['request'])

    def test_no_occurrence(self):
        self.assertRaises(
            AttributeError,
            self.at_traverser.publishTraverse,
            self.layer['request'], 'foo')

    def test_occurrence(self):
        self.at.setRecurrence('RRULE:FREQ=WEEKLY;COUNT=10')

        # does not match occurrence date
        qdate = datetime.date.today() + datetime.timedelta(days=4)
        self.assertRaises(
            AttributeError,
            self.at_traverser.publishTraverse,
            self.layer['request'], str(qdate))

        qdate = datetime.date.today() + datetime.timedelta(days=7)
        item = self.at_traverser.publishTraverse(self.layer['request'],
                                                 str(qdate))
        self.assertTrue(IOccurrence.providedBy(item))
        self.assertTrue(IATEvent.providedBy(item.aq_parent))

    def test_occurrence_accessor(self):
        start = datetime.datetime.today()
        end = datetime.datetime.today()
        occ = Occurrence('ignored', start, end)
        occ = occ.__of__(self.portal['at'])
        data = IEventAccessor(occ)
        self.assertNotEqual(data['start'],
                            tzdel(self.portal['at'].start_date))
        self.assertEqual(start, data['start'])


class TestTraversalBrowser(TestTraversal):

    def test_traverse_occurrence(self):
        self.at.setRecurrence('RRULE:FREQ=WEEKLY;COUNT=10')
        transaction.commit()

        qdate = datetime.date.today() + datetime.timedelta(days=7)
        url = '/'.join([self.portal['at'].absolute_url(), str(qdate)])

        browser = Browser(self.layer['app'])
        browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_ID, TEST_USER_PASSWORD))
        browser.open(url)
        self.assertTrue(
            self.portal['at'].title.encode('ascii') in browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
