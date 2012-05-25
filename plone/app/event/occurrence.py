import zope.component
import zope.interface
from OFS.SimpleItem import SimpleItem
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.app.event.base import guess_date_from
from plone.app.event.interfaces import IEventAccessor
from plone.app.event.interfaces import IOccurrence
from plone.app.event.interfaces import IRecurrence
from plone.event.utils import is_same_day
from zope.publisher.interfaces.browser import IBrowserPublisher


class OccurrenceTraverser(DefaultPublishTraverse):
    zope.interface.implements(IBrowserPublisher)

    def publishTraverse(self, request, name):
        dateobj = guess_date_from(name, self.context)
        occurrence = IRecurrence(self.context).occurrences(dateobj)[0]
        if not dateobj or not is_same_day(dateobj, occurrence.start):
            return self.fallback(name)

        return occurrence

    def fallback(self, name):
        return super(OccurrenceTraverser, self).publishTraverse(
            self.request, name)


class Occurrence(SimpleItem):

    zope.interface.implements(IOccurrence)

    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end


# TODO: adapt to new event accessor api
@zope.interface.implementer(IEventAccessor)
@zope.component.adapter(IOccurrence)
def generic_event_accessor(context):
    # usually rolled into DXEvent or ATEvent
    event = context.aq_parent
    data = IEventAccessor(event)
    data['start'] = context.start
    data['end'] = context.end
    return data
