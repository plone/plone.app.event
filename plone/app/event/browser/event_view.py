from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor


def get_location(accessor):
    """Return the location.
    This method can be overwritten by external packages, for example to provide
    a reference to a Location object as done by collective.venue.

    :param accessor: Event, Occurrence or IEventAccessor object.
    :type accessor: IEvent, IOccurrence or IEventAccessor

    :returns: A location string. Possibly a HTML structure to link to another
              object, representing the location.
    :rtype: string
    """
    if not IEventAccessor.providedBy(accessor):
        accessor = IEventAccessor(accessor)
    return accessor.location


class EventView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = IEventAccessor(context)
