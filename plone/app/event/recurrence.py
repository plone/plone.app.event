from Acquisition import aq_parent
from OFS.SimpleItem import SimpleItem
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.component import adapts
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserPublisher

from plone.event.recurrence import recurrence_sequence_ical
from plone.event.interfaces import (
        IEventRecurrence,
        IEventAccessor,
        IRecurrenceSupport
)
from plone.event.utils import is_same_day
from plone.app.event.base import guess_date_from
from plone.app.event.interfaces import IOccurrence


class RecurrenceSupport(object):
    """ IRecurrenceSupport Adapter.

    """
    implements(IRecurrenceSupport)
    adapts(IEventRecurrence)

    def __init__(self, context):
        self.context = context

    def occurrences(self, range_start=None, range_end=None):
        """ Return all occurrences of an event, possibly within a start and end
        limit.

        Please note: Events beginning before limit_start but ending afterwards
                     won't be found.

        TODO: test with event start = 21st feb, event end = start+36h,
        recurring for 10 days, limit_start = 1st mar, limit_end = last Mark

        """
        event = IEventAccessor(self.context)
        starts = recurrence_sequence_ical(event.start,
                                          recrule=event.recurrence,
                                          from_=range_start, until=range_end)

        # We get event ends by adding a duration to the start. This way, we
        # prevent that the start and end lists are of different size if an
        # event starts before limit_start but ends afterwards.
        duration = event.duration

        # XXX potentially occurrence won't need to be wrapped anymore
        # but doing it for backwards compatibility as views/templates
        # still rely on acquisition-wrapped objects.
        func = lambda start: Occurrence(
            id=str(start.date()),
            start=start,
            end=start + duration).__of__(self.context)
        events = map(func, starts)
        return events


class OccurrenceTraverser(DefaultPublishTraverse):
    implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        dateobj = guess_date_from(name, self.context)
        occurrence = IRecurrenceSupport(self.context).occurrences(dateobj)[0]
        if not dateobj or not is_same_day(dateobj, occurrence.start):
            return self.fallback(name)
        return occurrence

    def fallback(self, name):
        return super(OccurrenceTraverser, self).publishTraverse(
            self.request, name)


class Occurrence(SimpleItem):
    implements(IOccurrence)

    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end


class EventOccurrenceAccessor(object):
    """ Generic event accessor adapter implementation for Occurrence objects.

    """
    implements(IEventAccessor)
    adapts(IOccurrence)

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

        own_attr = ['start', 'end']
        object.__setattr__(self, '_own_attr', own_attr)

    def _get_context(self, name):
        oa = self._own_attr
        if name in oa:
            return self.context
        else:
            return aq_parent(self.context)

    def __getattr__(self, name):
        return getattr(self._get_context(name), name, None)

    def __setattr__(self, name, value):
        return setattr(self._get_context(name), name, value)

    def __delattr__(self, name):
        delattr(self._get_context(name), name)
