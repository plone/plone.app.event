from zope.component import adapts
from zope.interface import implements
from plone.event.recurrence import recurrence_sequence_ical
from plone.event.interfaces import (
        IEventRecurrence,
        IEventAccessor,
        IRecurrenceSupport
)
from plone.app.event.occurrences import Occurrence


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
