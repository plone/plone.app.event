from Products.Five.browser import BrowserView
from plone.app.event.base import get_occurrences_from_brains
from plone.app.event.base import get_portal_events
from plone.app.event.base import date_formater
from Products.CMFPlone.PloneBatch import Batch
from zope.contentprovider.interfaces import IContentProvider
from zope.component import getMultiAdapter


class EventListing(BrowserView):

    def __init__(self, context, request):
        super(EventListing, self).__init__(context, request)

        # Batch parameter
        self.b_start = 'b_start' in self.request and\
                        int(self.request['b_start']) or 0
        self.b_size  = 'b_size' in self.request and\
                        int(self.request['b_size']) or 10
        self.orphan  = 'orphan' in self.request and\
                        int(self.request['orphan']) or 1

    def get_events(self, start=None, end=None, batch=True):
        context = self.context

        b_start = b_size = None
        if batch:
            b_start=self.b_start
            b_size=self.b_size

        occs = get_occurrences_from_brains(
                context,
                get_portal_events(context, start, end,
                    #b_start=b_start, b_size=b_size,
                    path=context.getPhysicalPath()),
                start,
                end)

        if batch:
            ret = Batch(occs, size=b_size, start=b_start, orphan=self.orphan)
        else:
            ret = occs

        return ret

    def formated_date(self, occ):
        provider = getMultiAdapter((self.context, self.request, self),
                IContentProvider, name=u"formated_date")
        return provider(occ.context)

    def date_formater(self, date):
        return date_formater(self.context, date)
