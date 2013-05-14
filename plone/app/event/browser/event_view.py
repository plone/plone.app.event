from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from plone.app.event.at.interfaces import IATEvent
from plone.app.event.dx.interfaces import IDXEvent


class EventView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = IEventAccessor(context)

    def get_location(self):
        """In case location is not of type basestring, it's propably a
        reference, which case we handle here.
        """
        context = self.context

        # Get the original location directly from the context, as in case of
        # reference, the accessor might return an string representing the
        # location instead of the referenced object.
        location = None
        if IATEvent.providedBy(context):
            location = context.getLocation()
        elif IDXEvent.providedBy(context):
            from plone.app.event.dx.behaviors import IEventLocation
            location = IEventLocation(context).location

        if location and not isinstance(location, basestring) and\
            hasattr(location, 'absolute_url') and\
            hasattr(location, 'Title'):
            # Then I'm a reference
            location = u'<a href="%s" title="%s">%s</a>' % (
                location.absolute_url(),
                self.data.location,  # A meaningful title, e.g. the address
                location.Title()
            )
        return location

    @property
    def is_occurrence(self):
        return IOccurrence.providedBy(self.context)

    @property
    def occurrence_parent_url(self):
        if self.is_occurrence:
            return aq_parent(self.context).absolute_url()
        return None

    def formated_date(self, occ):
        provider = getMultiAdapter((self.context, self.request, self),
                IContentProvider, name='formated_date')
        return provider(occ)

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
