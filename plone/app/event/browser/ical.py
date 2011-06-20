from zope.publisher.browser import BrowserView
from Acquisition import aq_inner

from Products.ATContentTypes.interfaces import IATTopic

# TODO: fix this.
from plone.event.interfaces import IICalEventExporter, IICalendar, IEvent
from plone.app.event import messageFactory as _


class EventsICal(BrowserView):
    """Returns events in iCal format"""

    def __call__(self):
        data = self.getICal()
        if not data:
            return _(u"No events found.")

        name = '%s.ics' % self.context.getId()
        self.request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        self.request.RESPONSE.setHeader('Content-Disposition',
            'attachment; filename="%s"' % name)

        # get iCal
        ical = IICalendar(self.context)
        data = u''.join([ical.header(), data, ical.footer()])
        self.request.RESPONSE.write(data.encode('utf-8'))

    def getICal(self):
        # collect iCal entries for found events
        data = u""
        for event in self.getEvents():
            data += IICalEventExporter(event).feed()
        return data

    def getEvents(self):
        context = aq_inner(self.context)
        query = {'object_provides':IEvent.__identifier__}
        if not IATTopic.providedBy(context):
            query['path'] = '/'.join(context.getPhysicalPath())
        return [b.getObject() for b in context.queryCatalog(REQUEST=query)]
