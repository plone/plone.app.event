from plone.app.imaging.traverse import ImageTraverser
from plone.app.event.base import guess_date_from
from plone.event.interfaces import IRecurrenceSupport
from plone.event.interfaces import IEventAccessor
from plone.event.utils import is_same_day
from plone.app.event.at.interfaces import IATEventRecurrence
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import adapts


class OccurrenceTraverser(ImageTraverser):
    """Archetypes image scale traversing support for OccurrenceTraverser.
    You can access scale names like so: URL/TO/OBJECT/IMAGEFIELD_SCALENAME.
    """
    adapts(IATEventRecurrence, IBrowserRequest)

    def publishTraverse(self, request, name):
        dateobj = guess_date_from(name, self.context)
        if dateobj:
            occurrence = IRecurrenceSupport(self.context).occurrences(
                range_start=dateobj)[0]
            occ_acc = IEventAccessor(occurrence)
            if is_same_day(dateobj, occ_acc.start):
                return occurrence
        # No self.fallback to avoid circular call from ImageTraverser
        return super(OccurrenceTraverser, self).publishTraverse(request, name)
