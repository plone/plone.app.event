from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from Acquisition import aq_inner

from Products.ATContentTypes.interfaces import IATTopic

from plone.event.interfaces import IICalEventExporter, IICalendar, IEvent
from plone.app.event import messageFactory as _


class EventsICal(BrowserView):
    """Returns events in iCal format"""

    def getEvents(self):
        context = aq_inner(self.context)
        query = {'object_provides':IEvent.__identifier__}
        if not IATTopic.providedBy(context):
            query['path'] = '/'.join(context.getPhysicalPath())
        return [b.getObject() for b in context.queryCatalog(REQUEST=query)]

    def __call__(self):
        # collect events
        events = self.getEvents()
        if len(events) == 0:
            return _(u"No events found.")
        
        # get iCal header
        ical = IICalendar(self.context)
        data = ical.header()
        
        # collect iCal entries for found events
        for event in events:
            data += IICalEventExporter(event).feed()
        
        # now add iCal footer
        data += ical.footer()
        
        name = '%s.ics' % self.context.getId()
        self.request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        self.request.RESPONSE.setHeader('Content-Disposition',
            'attachment; filename="%s"' % name)
        self.request.RESPONSE.write(data.encode('utf-8'))
