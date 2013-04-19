import datetime
import zope.component
from plone.app.event.base import (
    default_timezone,
    localized_now,
)
from plone.registry.interfaces import IRegistry
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.event.interfaces import IEventSettings
import unittest2 as unittest

class AbstractSampleDataEvents(unittest.TestCase):
    layer = None # Set the plone.app.testing layer in concrete implementation

    def event_factory(self):
        # Return the IEventAccessor.create event factory.
        raise NotImplementedError

    def setUp(self):
        self.portal = self.layer['portal']
        default_tz = default_timezone()

        reg = zope.component.getUtility(IRegistry)
        settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
        settings.portal_timezone = default_tz

        now = localized_now()
        past = now - datetime.timedelta(days=2)
        future = now + datetime.timedelta(days=2)
        far = now + datetime.timedelta(days=8)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        factory = self.event_factory()
        self.past_event = factory(
            container=self.portal,
            content_id='past',
            title=u'Past Event',
            start=past,
            end=past + datetime.timedelta(hours=1),
            location=u"Vienna",
            timezone=default_tz)

        self.now_event = factory(
            container=self.portal,
            content_id='now',
            title=u'Now Event',
            start=now,
            end=now + datetime.timedelta(hours=1),
            location=u"Vienna",
            recurrence='RRULE:FREQ=DAILY;COUNT=4;INTERVAL=4',
            timezone=default_tz)

        self.future_event = factory(
            container=self.portal,
            content_id='future',
            title=u'Future Event',
            start=future,
            end=future + datetime.timedelta(hours=1),
            location=u'Graz',
            timezone=default_tz)

        self.portal.invokeFactory('Folder', 'sub', title=u'sub')
        self.future_event = factory(
            container=self.portal.sub,
            content_id='long',
            title=u'Long Event',
            start=past,
            end=future,
            location=u'Schaftal',
            timezone=default_tz)

        self.now = now
        self.past = past
        self.future = future
        self.far = far
