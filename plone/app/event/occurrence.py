from Acquisition import aq_parent
from zope.component import adapts
from zope.interface import implements
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher
from OFS.SimpleItem import SimpleItem

from plone.event.interfaces import IEventAccessor, IRecurrenceSupport
from plone.app.event.base import guess_date_from
from plone.app.event.interfaces import IOccurrence
from plone.event.utils import is_same_day


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


class EventAccessor(object):
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
