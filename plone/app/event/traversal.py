from OFS.SimpleItem import SimpleItem
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.app.event.interfaces import IEvent
from plone.app.event.interfaces import IOccurrence
from plone.app.event.interfaces import IRecurrence
from zope.publisher.interfaces import IPublishTraverse
import datetime
import zope.component


class OccurrenceTraverser(DefaultPublishTraverse):
    zope.component.adapts(IEvent, IPublishTraverse)

    format = '%Y-%m-%d'

    def publishTraverse(self, request, name):
        try:
            dateobj = datetime.datetime.strptime(name, self.format)
            occurrences = IRecurrence(self.context).occurrences(
                dateobj)
        except ValueError:
            occurrences = []

        if not occurrences:
            return super(OccurrenceTraverser, self).publishTraverse(request,
                                                                    name)
        occurrence = Occurrence(*occurrences[0])
        occurrence.__of__(self.context)
        return occurrence


class Occurrence(SimpleItem):

    zope.interface.implements(IOccurrence)

    def __init__(self, start, end):
        self.start = start
        self.end = end
