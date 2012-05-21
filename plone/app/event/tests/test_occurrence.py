from plone.app.event.at.content import IATEvent
from plone.app.event.base import get_occurrences
from plone.app.event.base import get_portal_events
from plone.app.event.base import localized_now
from plone.app.event.interfaces import IEventAccessor
from plone.app.event.interfaces import IEventSettings
from plone.app.event.interfaces import IOccurrence
from plone.app.event.occurrence import Occurrence
from plone.app.event.occurrence import OccurrenceTraverser
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.event.utils import pydt
from plone.event.utils import tzdel
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from zope.publisher.browser import TestRequest
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
                                  title='Event1')
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

        qdatedt = pydt(self.at.start() + 7)
        item = self.at_traverser.publishTraverse(self.layer['request'],
                                                 str(qdatedt.date()))
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

        qdatedt = pydt(self.at.start() + 7)
        url = '/'.join([self.portal['at'].absolute_url(),
                        str(qdatedt.date())])

        browser = Browser(self.layer['app'])
        browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_ID, TEST_USER_PASSWORD))
        browser.open(url)
        self.assertTrue(
            self.portal['at'].title.encode('ascii') in browser.contents)


class TestOccurrences(unittest.TestCase):

    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        default_tz = 'CET'

        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = default_tz

        now = localized_now()
        yesterday = now - datetime.timedelta(days=1)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(
            'Event',
            'daily',
            title=u'Daily Event',
            start=now,
            end=now + datetime.timedelta(hours=1),
            location=u'Vienna',
            timezone=default_tz,
            whole_day=False)

        self.portal.invokeFactory(
            'Event',
            'interval',
            title=u'Interval Event',
            start=yesterday,
            end=yesterday + datetime.timedelta(hours=1),
            location=u'Halle',
            timezone=default_tz,
            whole_day=False)

        self.now = now
        self.yesterday = yesterday

        self.daily = self.portal['daily']
        self.daily.setRecurrence('RRULE:FREQ=DAILY;COUNT=4')

        self.interval = self.portal['interval']
        self.interval.setRecurrence(
            'RRULE:FREQ=DAILY;INTERVAL=2;COUNT=5')
        transaction.commit()

    def test_get_occurrences(self):
        result = get_occurrences(self.portal,
                                 get_portal_events(self.portal))
        self.assertTrue(len(result) == 9)

        result = get_occurrences(self.portal,
                                 get_portal_events(self.portal), limit=5)
        self.assertTrue(len(result) == 5)
        self.assertTrue(IOccurrence.providedBy(result[0]))


class TestOccurrencesView(unittest.TestCase):

    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        default_tz = 'CET'

        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = default_tz

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory(
            'Event',
            'e1',
            title=u'Daily Event',
            location=u'Vienna',
            timezone=default_tz,
            recurrence='RRULE:FREQ=DAILY;COUNT=10',
            whole_day=False)

        self.e1 = self.portal['e1']

    def test_get_data_startdate(self):
        future = localized_now() + datetime.timedelta(days=5)
        form = dict(start=str(future.date()))
        request = TestRequest(form=form)
        view = zope.component.getMultiAdapter(
            (self.portal, request), name='occurrences.html')

        result = view.get_data()
        self.assertEqual(5, len(result))

    def test_get_data_invalid(self):
        request = TestRequest(form=dict(start='invalid'))
        view = zope.component.getMultiAdapter(
            (self.portal, request), name='occurrences.html')
        result = view.get_data()
        self.assertEqual(10, len(result))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
