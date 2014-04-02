from Products.CMFCore.utils import getToolByName
from datetime import datetime
from datetime import timedelta
from plone.app.event.dx import behaviors
from plone.app.event.dx.behaviors import data_postprocessing_context
from plone.app.event.testing import set_browserlayer
from plone.app.event.testing import set_timezone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer

import unittest2 as unittest
import pytz

TEST_TIMEZONE = 'Europe/Vienna'


def patched_now(context=None):
    """Patch localized_now to allow stable results in tests.
    """
    if not context:
        context = None
    tzinfo = pytz.timezone(TEST_TIMEZONE)
    now = datetime(2013, 5, 5, 10, 0, 0).replace(microsecond=0)
    now = tzinfo.localize(now)  # set tzinfo with correct DST offset
    return now


# Patch EventAccessor for IDXEvent to set the correct testing portal type.
# For custom accessor in addons you would rather do that in an adapter.
behaviors.EventAccessor.event_type = 'plone.app.event.dx.event'


class AbstractSampleDataEvents(unittest.TestCase):
    layer = None  # Set the plone.app.testing layer in concrete implementation

    def event_factory(self, container, **kwargs):
        # Return the IEventAccessor.create event factory.
        return createContentInContainer(
            container,
            'plone.app.event.dx.event',
            **kwargs
        )

    def make_dates(self):
        tz = pytz.timezone(TEST_TIMEZONE)
        now = self.now = patched_now()
        tomorrow = self.tomorrow = tz.normalize(now + timedelta(days=1))
        past = self.past = tz.normalize(now - timedelta(days=10))
        future = self.future = tz.normalize(now + timedelta(days=10))
        far = self.far = tz.normalize(now + timedelta(days=30))
        duration = self.duration = timedelta(hours=1)
        return (now, past, future, far, duration)

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        set_timezone(TEST_TIMEZONE)

        now, past, future, far, duration = self.make_dates()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        workflow = getToolByName(self.portal, 'portal_workflow')

        factory = self.event_factory
        self.past_event = factory(
            container=self.portal,
            id='past',
            title=u'Past Event',
            start=past,
            end=past + duration,
            location=u"Vienna",
            whole_day=True,
            recurrence='RRULE:FREQ=DAILY;COUNT=3')
        workflow.doActionFor(self.past_event, 'publish')
        # adjust start and end according to whole_day and open_end
        data_postprocessing_context(self.past_event)
        self.past_event.reindexObject()

        self.now_event = factory(
            container=self.portal,
            id='now',
            title=u'Now Event',
            start=now,
            end=now + duration,
            location=u"Vienna",
            recurrence="""RRULE:FREQ=DAILY;COUNT=3;INTERVAL=1
RDATE:20130509T000000
EXDATE:20130506T000000,20140404T000000""",
            contact_name='Auto Testdriver',
            contact_email='testdriver@plone.org',
            contact_phone='+123456789',
            event_url='http://plone.org',
            subject=('plone', 'testing'))  # change to subjects, once this is
        # fixed:
        # https://github.com/plone/plone.dexterity/pull/18
        # https://github.com/plone/plone.app.dexterity/issues/118
        workflow.doActionFor(self.now_event, 'publish')
        data_postprocessing_context(self.now_event)
        self.now_event.reindexObject()

        self.future_event = factory(
            container=self.portal,
            id='future',
            title=u'Future Event',
            start=future,
            end=future + duration,
            location=u'Graz')
        workflow.doActionFor(self.future_event, 'publish')
        data_postprocessing_context(self.future_event)
        self.future_event.reindexObject()

        self.portal.invokeFactory('Folder', 'sub', title=u'sub')
        self.long_event = factory(
            container=self.portal.sub,
            id='long',
            title=u'Long Event',
            start=past,
            end=far,
            location=u'Schaftal')
        workflow.doActionFor(self.long_event, 'publish')
        data_postprocessing_context(self.long_event)
        self.long_event.reindexObject()

        # For AT based tests, this is a plone.app.collection ICollection type
        # For DX based tests, it's a plone.app.contenttypes ICollection type
        self.portal.invokeFactory('Collection', 'collection', title=u'Col')
        collection = self.portal.collection
        collection.sort_on = u'start'
        collection.reverse_sort = True
        collection.query = [
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.is',
             'v': ['Event', 'plone.app.event.dx.event']
             },
        ]
        collection.reindexObject()
