from cStringIO import StringIO

from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from DateTime import DateTime

from plone.memoize import ram
from Products.CMFPlone.utils import safe_unicode
from Products.ATContentTypes.interfaces import IATTopic

from plone.event.interfaces import IEvent
from plone.event.utils import rfc2445dt, vformat, foldline, dateStringsForEvent
from plone.event.constants import PRODID, VCS_HEADER, VCS_FOOTER, \
    VCS_EVENT_START, VCS_EVENT_END


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
        request.RESPONSE.write(self.feeddata().encode('utf-8'))

    @ram.cache(cachekey)
    def feeddata(self):
        context = self.context
        data = VCS_HEADER % dict(prodid=PRODID)
        data += u'X-WR-CALNAME:%s\n' % safe_unicode(context.Title())
        data += u'X-WR-CALDESC:%s\n' % safe_unicode(context.Description())
        for brain in self.events:
            data += getMultiAdapter((brain.getObject(), self.request),
                             name=u'vcs_view').getVCal()
        data += VCS_FOOTER
        return data

    __call__ = render

    def getVCal(self):
        """get VCal data
        """
        start_str, end_str = dateStringsForEvent(self.context)
        out = []
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(self.context.CreationDate())),
            'uid'       : self.context.UID(),
            'modified'  : rfc2445dt(DateTime(self.context.ModificationDate())),
            'summary'   : vformat(safe_unicode(self.context.Title())),
            'startdate' : start_str,
            'enddate'   : end_str,
            }
        out.append(VCS_EVENT_START % map)

        description = self.context.Description()
        if description:
            out.append(foldline(u'DESCRIPTION:%s\n' %
                vformat(safe_unicode(description))))

        location = self.context.getLocation()
        if location:
            out.append(u'LOCATION:%s\n' % vformat(safe_unicode(location)))

        # allow derived event types to inject additional data for vCal
        if hasattr(self.context, 'getVCalSupplementary'):
            self.context.getVCalSupplementary(out)

        out.append(VCS_EVENT_END)
        return u''.join(out)

    __call__ = render
