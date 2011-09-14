import icalendar

from Acquisition import aq_inner
from Products.ATContentTypes.interfaces import IATTopic

from zope.publisher.browser import BrowserView
from plone.event.interfaces import IEvent
from plone.app.event.base import default_timezone

from plone.app.event import messageFactory as _

PRODID = "-//Plone.org//NONSGML plone.event//EN"
VERSION = "2.0"

# TODO: factor out ical generation stuff into own ical module. this should be
# able to operate on a generic context which follows IEvent attributes. IEvent
# should define attributes to comply with RFC5545. dexterity then should
# implement them as in RFC

class EventsICal(BrowserView):
    """Returns events in iCal format"""

    def __call__(self):
        cal = self.getICal()
        if not cal:
            return _(u"No events found.")

        name = '%s.ics' % self.context.getId()
        self.request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        self.request.RESPONSE.setHeader('Content-Disposition',
            'attachment; filename="%s"' % name)

        # get iCal
        self.request.RESPONSE.write(cal.as_string().encode('utf-8'))

    def getICal(self):
        # collect iCal entries for found events
        events = self.getEvents()
        if not events: return None

        cal = icalendar.Calendar()
        cal.add('prodid', PRODID)
        cal.add('version', VERSION)

        # TODO: is there a UUID to use instead of UID?
        # Non-Standard calendar extensions. also see:
        # http://en.wikipedia.org/wiki/ICalendar#cite_note-11
        cal_context = self.context
        cal_title = cal_context.Title()
        if cal_title: cal.add('x-wr-calname', cal_title)
        cal_desc = cal_context.Description()
        if cal_desc: cal.add('x-wr-caldesc', cal_desc)
        if getattr(cal_context, 'UID', False): # portal object does not have UID
            cal_uid = cal_context.UID()
            cal.add('x-wr-relcalid', cal_uid)
        cal_tz = default_timezone(cal_context)
        if cal_tz: cal.add('x-wr-timezone', cal_tz)

        for event in events:
            cal.add_component(event.to_icalendar())

        return cal

    def getEvents(self):
        context = aq_inner(self.context)
        query = {'object_provides':IEvent.__identifier__}
        if not IATTopic.providedBy(context):
            query['path'] = '/'.join(context.getPhysicalPath())
        return [item.getObject()
                for item in context.queryCatalog(REQUEST=query)]
