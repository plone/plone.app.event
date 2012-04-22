from DateTime import DateTime
from plone.app.event.interfaces import IOccurrence
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.event.traversal import OccurrenceTraverser
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
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
        self.portal.invokeFactory(type_name='Event', id='dx',
                                  title='Event1',
                                  start=DateTime('Australia/Brisbane'),
                                  end=DateTime('Australia/Brisbane') + 1)
        self.at = self.portal['at']
        self.dx = self.portal['dx']
        self.at_traverser = OccurrenceTraverser(self.at, self.layer['request'])
        self.dx_traverser = OccurrenceTraverser(self.dx, self.layer['request'])

    def test_no_occurrence(self):
        self.assertRaises(
            AttributeError,
            self.at_traverser.publishTraverse,
            self.layer['request'], 'foo')

    def test_occurrence(self):
        self.at.setRecurrence('RRULE:FREQ=DAILY;COUNT=10')
        qdate = datetime.date.today() + datetime.timedelta(days=4)
        item = self.at_traverser.publishTraverse(self.layer['request'],
                                                 str(qdate))
        self.assertTrue(IOccurrence.providedBy(item))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
