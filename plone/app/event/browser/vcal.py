from cStringIO import StringIO

from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from DateTime import DateTime

from plone.memoize import ram
from Products.ATContentTypes.interfaces import IATTopic

from plone.event.interfaces import IEvent
from plone.event.utils import rfc2445dt, vformat, foldline
from plone.app.event import event_util
from plone.app.event.constants import (
    PRODID, VCS_HEADER, VCS_FOOTER, VCS_EVENT_START, VCS_EVENT_END)


def cachekey(fun, self):
    """ generate a cache key based on the following data:
          * context URL
          * fingerprint of the brains found in the query
        the returned key is suitable for usage with `memoize.ram.cache` """
    context = self.context
    def add(brain):
        path = brain.getPath().decode('ascii', 'replace').encode('utf-8')
        return '%s\n%s\n\n' % (path, brain.modified)
    url = context.absolute_url()
    title = context.Title()
    fingerprint = ''.join(map(add, self.events))
    return ''.join((url, title, fingerprint))


class EventsVCal(BrowserView):
    """ view for event data into an `.vcs` feed """

    def update(self):
        context = aq_inner(self.context)
        query = {'object_provides':IEvent.__identifier__}
        if not IATTopic.providedBy(context):
            query['path'] = '/'.join(context.getPhysicalPath())
        self.events = context.queryCatalog(REQUEST=query)

    def render(self):
        self.update()       # collect events
        context = self.context
        request = self.request
        name = '%s.vcs' % context.getId()
        request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        request.RESPONSE.setHeader('Content-Disposition',
                                   'attachment; filename="%s"' % name)
        request.RESPONSE.write(self.feeddata())

    @ram.cache(cachekey)
    def feeddata(self):
        context = self.context
        data = VCS_HEADER % dict(prodid=PRODID)
        data += 'X-WR-CALNAME:%s\n' % context.Title()
        data += 'X-WR-CALDESC:%s\n' % context.Description()
        for brain in self.events:
            data += getMultiAdapter((brain.getObject(), self.request),
                             name=u'vcs_view').getVCal()
        data += VCS_FOOTER
        return data

    __call__ = render

    def getVCal(self):
        """get VCal data
        """
        start_str, end_str = event_util.dateStringsForEvent(self.context)
        out = StringIO()
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(self.context.CreationDate())),
            'uid'       : self.context.UID(),
            'modified'  : rfc2445dt(DateTime(self.context.ModificationDate())),
            'summary'   : vformat(self.context.Title()),
            'startdate' : start_str,
            'enddate'   : end_str,
            }
        out.write(VCS_EVENT_START % map)

        description = self.context.Description()
        if description:
            out.write(foldline('DESCRIPTION:%s\n' % vformat(description)))

        location = self.context.getLocation()
        if location:
            out.write('LOCATION:%s\n' % vformat(location))

        # allow derived event types to inject additional data for iCal
        try:
            self.context.getVCalSupplementary(out)
        except AttributeError:
            pass

        out.write(VCS_EVENT_END)
        return out.getvalue()

    __call__ = render
