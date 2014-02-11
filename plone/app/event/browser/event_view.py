from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider


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

    @property
    def get_location(self):
        return get_location(self.context)

    @property
    def is_occurrence(self):
        return IOccurrence.providedBy(self.context)

    @property
    def occurrence_parent_url(self):
        if self.is_occurrence:
            return aq_parent(self.context).absolute_url()
        return None

    def formatted_date(self, occ):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(occ.context)

    @property
    def next_occurrences(self):
        """Returns all occurrences for this context, except the start
        occurrence.
        The maximum defaults to 7 occurrences. If there are more occurrences
        defined for this context, the result will contain the last item
        of the occurrence list.

        :returns: Dictionary with ``events`` and ``tail`` as keys.
        :rtype: dict

        """
        occ_dict = dict(events=[], tail=None)
        context = self.context
        adapter = IRecurrenceSupport(context, None)
        if adapter is not None:
            occurrences = adapter.occurrences()[1:]  # don't include first
            occ_dict['events'], occ_dict['tail'] = (
                self._get_occurrences_helper(occurrences)
            )
        return occ_dict

    def _get_occurrences_helper(self, occ_list, limit=7):
        """For many occurrences we limit the amount of occurrences to
        display. That is, this method returns the first 6 (limit)
        occurrences and the last occurrence in the list.

        :param occ_list: The list of occurrences returned from
                         IRecurrenceSupport
        :type occ_list: list
        :param limit: optional, defaults to 7
        :type limit: integer
        :rtype: tuple of (list of events, last item of occ_list)

        """
        events = []
        tail = None
        if occ_list:
            events = occ_list[:limit]
            many = len(occ_list) > limit
            tail = events and occ_list.pop() or None
            tail = tail if many else None
        return (events, tail)
