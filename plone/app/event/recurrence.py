from Acquisition import aq_parent
from OFS.SimpleItem import SimpleItem
from Products.CMFPlone.utils import safe_unicode
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.app.event.base import guess_date_from
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.event.recurrence import recurrence_sequence_ical
from plone.event.utils import is_same_day
from zope.component import adapts
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserPublisher

import itertools


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

        Please note: Events beginning before range_start but ending afterwards
                     won't be found.

        TODO: test with event start = 21st feb, event end = start+36h,
        recurring for 10 days, range_start = 1st mar, range_end = last Mark

        """
        event = IEventAccessor(self.context)
        starts = recurrence_sequence_ical(event.start,
                                          recrule=event.recurrence,
                                          from_=range_start, until=range_end)

        if range_start and\
            event.start < range_start and\
            event.end >= range_start and\
            event.start not in starts:
            # Include event, which started before range but lasts until it.
            starts = itertools.chain(starts, [event.start])

        # We get event ends by adding a duration to the start. This way, we
        # prevent that the start and end lists are of different size if an
        # event starts before range_start but ends afterwards.
        duration = event.duration

        # XXX potentially occurrence won't need to be wrapped anymore
        # but doing it for backwards compatibility as views/templates
        # still rely on acquisition-wrapped objects.
        def get_obj(start):
            if event.start.replace(microsecond=0) == start:
                # If the occurrence date is the same as the event object, the
                # occurrence is the event itself. return it as such.
                # Dates from recurrence_sequence_ical are explicitly without
                # microseconds, while event.start may contain it. So we have to
                # remove it for a valid comparison.
                return self.context
            return Occurrence(
                id=str(start.date()),
                start=start,
                end=start + duration).__of__(self.context)

        events = map(get_obj, starts)
        return events


class OccurrenceTraverser(DefaultPublishTraverse):
    implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        # TODO: here is something odd....
        #       called every time, when an attribute is traversed/accessed?
        dateobj = guess_date_from(name, self.context)
        if dateobj:
            occurrence = IRecurrenceSupport(self.context).occurrences(
                range_start=dateobj)[0]
            occ_acc = IEventAccessor(occurrence)
            if is_same_day(dateobj, occ_acc.start):
                return occurrence
        return self.fallback(name)

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

        own_attr = ['start', 'end', 'url', 'parent']
        object.__setattr__(self, '_own_attr', own_attr)

    def _get_context(self, name):
        # TODO: save parent context on self, so it must not be called every
        #       time
        oa = self._own_attr
        if name in oa:
            return self.context
        else:
            return IEventAccessor(aq_parent(self.context))

    def __getattr__(self, name):
        return getattr(self._get_context(name), name, None)

    def __setattr__(self, name, value):
        return setattr(self._get_context(name), name, value)

    def __delattr__(self, name):
        delattr(self._get_context(name), name)

    # R/O properties
    # TODO: Having uid here makes probably no sense, since Occurrences are
    #       created on the fly and not persistent.

    @property
    def url(self):
        return safe_unicode(self.context.absolute_url())
