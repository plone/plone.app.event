from plone.app.event.recurrence import OccurrenceTraverser as DefaultTraverser
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.dexterity.browser.traversal import DexterityPublishTraverse
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest


class OccurrenceTraverser(DefaultTraverser):
    """Occurrence Traverser for Dexterity based contexts.

    Please note: here is not ImageTraverser support included, since accessing
    images is done by calling the @@images view.
    """
    adapts(IDXEventRecurrence, IBrowserRequest)

    def fallbackTraverse(self, request, name):
        return DexterityPublishTraverse(
            self.context, request).publishTraverse(request, name)
