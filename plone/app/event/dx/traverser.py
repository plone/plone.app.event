from plone.app.event.base import guess_date_from
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.dexterity.browser.traversal import DexterityPublishTraverse
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IRecurrenceSupport
from plone.event.utils import is_same_day
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest


class OccurrenceTraverser(DexterityPublishTraverse):
    """Occurrence Traverser for Dexterity based contexts.

    Please note: here is not ImageTraverser support included, since accessing
    images is done by calling the @@images view.
    """
    adapts(IDXEventRecurrence, IBrowserRequest)

    def publishTraverse(self, request, name):
        dateobj = guess_date_from(name, self.context)
        if dateobj:
            occurrence = IRecurrenceSupport(self.context).occurrences(
                range_start=dateobj)[0]
            occ_acc = IEventAccessor(occurrence)
            if is_same_day(dateobj, occ_acc.start):
                return occurrence
        return super(OccurrenceTraverser, self).publishTraverse(request, name)
