from datetime import datetime
from datetime import timedelta
from plone.app.event.base import default_timezone
from plone.app.event.interfaces import IEventSettings
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry

import unittest2 as unittest
import zope.component


def patched_now(context=None):
    """Patch localized_now to allow stable results in tests.
    """
    if not context:
        context = None
    tzinfo = default_timezone(context=context, as_tzinfo=True)
    now = datetime(2013, 5, 5, 10, 0, 0, tzinfo=tzinfo).replace(microsecond=0)
    return now


class AbstractSampleDataEvents(unittest.TestCase):
    layer = None  # Set the plone.app.testing layer in concrete implementation

    def event_factory(self):
        # Return the IEventAccessor.create event factory.
        raise NotImplementedError

    def make_dates(self):
        now      = self.now      = patched_now()
        past     = self.past     = now - timedelta(days=10)
        future   = self.future   = now + timedelta(days=10)
        far      = self.far      = now + timedelta(days=30)
        duration = self.duration = timedelta(hours=1)
        return (now, past, future, far, duration)

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.layer['request']

        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        default_tz = default_timezone()
        settings.portal_timezone = default_tz

        now, past, future, far, duration = self.make_dates()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        factory = self.event_factory()
        self.past_event = factory(
            container=self.portal,
            content_id='past',
            title=u'Past Event',
            start=past,
            end=past + duration,
            location=u"Vienna",
            timezone=default_tz,
            recurrence='RRULE:FREQ=DAILY;COUNT=3',
            )

        self.now_event = factory(
            container=self.portal,
            content_id='now',
            title=u'Now Event',
            start=now,
            end=now + duration,
            location=u"Vienna",
            timezone=default_tz,
            recurrence='RRULE:FREQ=DAILY;COUNT=3;INTERVAL=2',
            )

        self.future_event = factory(
            container=self.portal,
            content_id='future',
            title=u'Future Event',
            start=future,
            end=future + duration,
            location=u'Graz',
            timezone=default_tz)

        self.portal.invokeFactory('Folder', 'sub', title=u'sub')
        self.long_event = factory(
            container=self.portal.sub,
            content_id='long',
            title=u'Long Event',
            start=past,
            end=far,
            location=u'Schaftal',
            timezone=default_tz)

