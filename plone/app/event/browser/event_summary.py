from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from plone.app.event.browser.event_view import get_location


class EventSummaryView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = IEventAccessor(context)
        self.max_occurrences = 6
        self.excludes = ['title', ]

    @property
    def get_location(self):
        return get_location(self.context)

    @property
    def is_occurrence(self):
        return IOccurrence.providedBy(self.context)

    @property
    def event_context(self):
        if self.is_occurrence:
            return aq_parent(self.context)
        return self.context

    def formatted_date(self, occ):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(occ)

    @property
    def next_occurrences(self):
        """Returns occurrences for this context, except the start
        occurrence, limited to self.max_occurrence occurrences.

        :returns: List with next occurrences.
        :rtype: list
        """
        occurrences = []
        adapter = IRecurrenceSupport(self.event_context, None)
        if adapter:
            for cnt, occ in enumerate(adapter.occurrences()):
                if cnt == self.max_occurrences:
                    break
                occurrences.append(occ)
        return occurrences

    @property
    def num_more_occurrences(self):
        """Return the number of extra occurrences, which are not listed by
        next_occurrences.
        """
        uid = IUUID(self.event_context, None)
        if not uid:
            # Might be an occurrence
            return 0
        catalog = getToolByName(self.event_context, 'portal_catalog')
        brain = catalog(UID=uid)[0]  # assuming, that the current context is
                                     # in the catalog
        idx = catalog.getIndexDataForRID(brain.getRID())

        num = len(idx['start']) - self.max_occurrences
        return num if num > 0 else 0

    # BBB Removed with next version
    @property
    def occurrence_parent_url(self):
        if self.is_occurrence:
            return aq_parent(self.context).absolute_url()
        return None
