from OFS.SimpleItem import SimpleItem
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.app.event.interfaces import IEventAccessor
from plone.app.event.interfaces import IOccurrence
from plone.app.event.interfaces import IRecurrence
from plone.event.utils import is_same_day
from zope.publisher.interfaces.browser import IBrowserPublisher
import datetime
import pytz
import zope.component
import zope.interface


class OccurrenceTraverser(DefaultPublishTraverse):
    zope.interface.implements(IBrowserPublisher)

    format = '%Y-%m-%d'

    def publishTraverse(self, request, name):
        try:
            dateobj = datetime.datetime.strptime(name, self.format)
        except ValueError:
            return self.fallback(name)

        dateobj = pytz.timezone(self.context.timezone).localize(dateobj)
        occurrences = IRecurrence(self.context).occurrences(dateobj)
        start, end = occurrences[0]
        if not is_same_day(dateobj, start):
            return self.fallback(name)

        occurrence = Occurrence(name, start, end)
        return occurrence.__of__(self.context)

    def fallback(self, name):
        return super(OccurrenceTraverser, self).publishTraverse(
            self.request, name)


class Occurrence(SimpleItem):

    zope.interface.implements(IOccurrence)

    def __init__(self, id, start, end):
        self.id = id
        self.start = start
        self.end = end


@zope.interface.implementer(IEventAccessor)
@zope.component.adapter(IOccurrence)
def generic_event_accessor(context):
    # usually rolled into DXEvent or ATEvent
    event = context.aq_parent
    data = IEventAccessor(event)
    data['start'] = context.start
    data['end'] = context.end
    return data
