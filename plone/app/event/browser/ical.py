from datetime import datetime
import icalendar

from Acquisition import aq_inner
from Products.ATContentTypes.interfaces import IATTopic

from zope.publisher.browser import BrowserView
from plone.event.interfaces import IEvent
from plone.event.utils import pydt
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
        # TODO: add proper properties (proid, etc.)
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

        for event in self.getEvents():
            ical_event = icalendar.Event()
            ical_event.add('dtstamp', datetime.now())
            ical_event.add('created', pydt(event.creation_date))
            ical_event.add('uid', event.UID())
            ical_event.add('last-modified', pydt(event.modification_date))
            ical_event.add('summary', event.Title())
            ical_event.add('startdate', pydt(event.start()))
            ical_event.add('enddate', pydt(event.end()))

            recurrence = event.recurrence
            if recurrence:
                ical_event.add('rrule', icalendar.prop.vRecur.from_ical(recurrence))

            description = event.Description()
            if description:
                ical_event.add('description', description)

            location = event.getLocation()
            if location:
                ical_event.add('location', location)

            subject = event.Subject()
            if subject:
                ical_event.add('categories', u','.join(subject))

            # TODO: revisit and implement attendee export according to RFC
            attendees = event.getAttendees()
            for attendee in attendees:
                ical_event.add('attendee', attendee)

            cn = []
            contact = event.contact_name()
            if contact:
                cn.append(contact) # TODO safe_unicode conversion needed?
            phone = event.contact_phone()
            if phone:
                cn.append(phone)
            email = event.contact_email()
            if email:
                cn.append(email)
            if cn:
                ical_event.add('contact', u', '.join(cn))

            url = event.event_url()
            if url:
                ical_event.add('url', url)

            # TODO: IIRC this function was added in bristol. rethink it's api
            # and keep it, since it's definetly useful
            ## allow derived event types to inject additional data for iCal
            #if hasattr(event, 'getICalSupplementary'):
            #    event.getICalSupplementary(event)

            cal.add_component(ical_event)

        return cal


    def getEvents(self):
        context = aq_inner(self.context)
        query = {'object_provides':IEvent.__identifier__}
        if not IATTopic.providedBy(context):
            query['path'] = '/'.join(context.getPhysicalPath())
        return [item.getObject()
                for item in context.queryCatalog(REQUEST=query)]
