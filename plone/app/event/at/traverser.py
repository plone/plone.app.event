from plone.app.event.at.interfaces import IATEventRecurrence
from plone.app.event.recurrence import OccurrenceTraverser as DefaultTraverser
from plone.app.imaging.traverse import ImageTraverser
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest


class OccurrenceTraverser(DefaultTraverser):
    """Archetypes image scale traversing support for OccurrenceTraverser.
    You can access scale names like so: URL/TO/OBJECT/IMAGEFIELD_SCALENAME.
    """
    adapts(IATEventRecurrence, IBrowserRequest)

    def fallbackTraverse(self, request, name):
        return ImageTraverser(
            self.context, request).publishTraverse(request, name)
