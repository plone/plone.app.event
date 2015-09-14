from Products.CMFCore.utils import getToolByName
from datetime import datetime
from datetime import timedelta
from plone.app.event.dx import behaviors
from plone.app.event.testing import set_browserlayer
from plone.app.event.testing import set_timezone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.dexterity.utils import createContentInContainer

import unittest
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
        self.tomorrow = tz.normalize(now + timedelta(days=1))
        past = self.past = tz.normalize(now - timedelta(days=10))
        future = self.future = tz.normalize(now + timedelta(days=10))
        far = self.far = tz.normalize(now + timedelta(days=30))
        duration = self.duration = timedelta(hours=1)
        return (now, past, future, far, duration)

    def setUp(self):
        """Construct sample contents.

        These are all events:

        'Long Event: 2013-04-25T10:00:00+02:00 - 2013-06-04T10:00:00+02:00'

        'Past Event: 2013-04-25T00:00:00+02:00 - 2013-04-25T23:59:59+02:00'
        'Past Event: 2013-04-26T00:00:00+02:00 - 2013-04-26T23:59:59+02:00'
        'Past Event: 2013-04-27T00:00:00+02:00 - 2013-04-27T23:59:59+02:00'

        'Now Event: 2013-05-05T10:00:00+02:00 - 2013-05-05T11:00:00+02:00'
        'Now Event: 2013-05-07T10:00:00+02:00 - 2013-05-07T11:00:00+02:00'
        'Now Event: 2013-05-09T10:00:00+02:00 - 2013-05-09T11:00:00+02:00'

        'Future Event: 2013-05-15T10:00:00+02:00 - 2013-05-15T11:00:00+02:00'

        """
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        set_timezone(TEST_TIMEZONE)

        now, past, future, far, duration = self.make_dates()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        workflow = getToolByName(self.portal, 'portal_workflow')
        workflow.setDefaultChain("simple_publication_workflow")

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
        self.now_event.reindexObject()

        self.future_event = factory(
            container=self.portal,
            id='future',
            title=u'Future Event',
            start=future,
            end=future + duration,
            location=u'Graz')
        workflow.doActionFor(self.future_event, 'publish')
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
        self.long_event.reindexObject()

        # plone.app.contenttypes ICollection type
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
