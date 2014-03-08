from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.uuid.interfaces import IUUID
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
        self.max_occurrences = 6

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
        return provider(occ)

    @property
    def next_occurrences(self):
        """Returns occurrences for this context, except the start
        occurrence, limited to self.num_occurrences occurrences.

        :returns: List with next occurrences.
        :rtype: list
        """
        occurrences = []
        adapter = IRecurrenceSupport(self.context, None)
        if adapter:
            for cnt, occ in enumerate(adapter.occurrences()):
                if cnt == self.max_occurrences + 1:
                    break
                elif cnt == 0:
                    continue
                occurrences.append(occ)
        return occurrences

    @property
    def num_occurrences(self):
        uid = IUUID(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        brain = catalog(UID=uid)[0]  # assuming, that the current context is
                                     # in the catalog
        idx = catalog.getIndexDataForRID(brain.getRID())

        num = len(idx['start']) - 1 - self.max_occurrences
        return num > 0 and num or 0
