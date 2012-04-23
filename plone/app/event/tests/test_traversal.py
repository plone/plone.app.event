from DateTime import DateTime
from plone.app.event.at.content import IATEvent
from plone.app.event.interfaces import IEventAccessor
from plone.app.event.interfaces import IOccurrence
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.traversal import Occurrence
from plone.app.event.traversal import OccurrenceTraverser
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.event.utils import tzdel
import datetime
import unittest2 as unittest


class TestTraversal(unittest.TestCase):

    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
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

        qdate = datetime.date.today() + datetime.timedelta(days=6)
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


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
