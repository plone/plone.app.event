from plone.memoize import ram
from zope.publisher.browser import BrowserView

from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.interfaces import ICalendarSupport

from plone.app.event.constants import (
        PRODID, ICS_HEADER, ICS_FOOTER)

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


class EventICal(BrowserView):
    """ view for aggregating event data into an `.ics` feed """

    def update(self):
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        path = '/'.join(context.getPhysicalPath())
        provides = ICalendarSupport.__identifier__
        self.events = catalog(path=path, object_provides=provides)

    def render(self):
        self.update()       # collect events
        context = self.context
        request = self.request
        name = '%s.ics' % context.getId()
        request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s"' % name)
        request.RESPONSE.write(self.feeddata())

    @ram.cache(cachekey)
    def feeddata(self):
        context = self.context
        data = ICS_HEADER % dict(prodid=PRODID)
        data += 'X-WR-CALNAME:%s\n' % context.Title()
        data += 'X-WR-CALDESC:%s\n' % context.Description()
        for brain in self.events:
            data += brain.getObject().getICal()
        data += ICS_FOOTER
        return data

    __call__ = render


class TopicEventICal(EventICal):
    """ view (on "topic" content) for aggregating event data into
        an `.ics` feed """

    def update(self):
        context = self.context
        catalog = getToolByName(context, 'portal_catalog')
        if 'object_provides' in catalog.indexes():
            query = {'object_provides': ICalendarSupport.__identifier__}
        else:
            query = {'portal_type': 'Event'}
        self.events = context.queryCatalog(**query)
