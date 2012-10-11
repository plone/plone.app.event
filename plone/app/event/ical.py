import icalendar
from Acquisition import aq_inner
from datetime import datetime, timedelta
from plone.uuid.interfaces import IUUID
from zope.interface import implementer
from zope.interface import implements
from zope.publisher.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IICalendar
from plone.event.interfaces import IICalendarEventComponent
from plone.event.utils import pydt, utc
from plone.app.event.base import default_timezone
from plone.app.event.base import get_portal_events

PRODID = "-//Plone.org//NONSGML plone.app.event//EN"
VERSION = "2.0"


def construct_calendar(context, events):
    """ Returns an icalendar.Calendar object.

    :param context: A content object, which is used for calendar details like
                    Title and Description. Usually a container, collection or
                    the event itself.

    :param events: The list of event objects, which are included in this
                   calendar.

    """
    cal = icalendar.Calendar()
    cal.add('prodid', PRODID)
    cal.add('version', VERSION)

    cal_title = context.Title()
    if cal_title: cal.add('x-wr-calname', cal_title)
    cal_desc = context.Description()
    if cal_desc: cal.add('x-wr-caldesc', cal_desc)

    uuid = IUUID(context, None)
    if uuid: # portal object does not have UID
        cal.add('x-wr-relcalid', uuid)

    cal_tz = default_timezone(context)
    if cal_tz: cal.add('x-wr-timezone', cal_tz)

    for event in events:
        cal.add_component(IICalendarEventComponent(event).to_ical())

    return cal


@implementer(IICalendar)
def calendar_from_event(context):
    """ Event adapter. Returns an icalendar.Calendar object from an Event
    context.

    """
    context = aq_inner(context)
    events = [context]
    return construct_calendar(context, events)


@implementer(IICalendar)
def calendar_from_container(context):
    """ Container adapter. Returns an icalendar.Calendar object from a
    Containerish context like a Folder.

    """
    context = aq_inner(context)
    path = '/'.join(context.getPhysicalPath())
    result = get_portal_events(context, path=path)
    events = [item.getObject() for item in result]
    # TODO: should i become a generator?
    # TODO: let construct_calendar expand brains to objects - so a
    # generator would make some sense...
    return construct_calendar(context, events)


@implementer(IICalendar)
def calendar_from_collection(context):
    """ Container/Event adapter. Returns an icalendar.Calendar object from a
    Collection.

    """
    context = aq_inner(context)
    result = get_portal_events(context)
    events = [item.getObject() for item in result]
    return construct_calendar(context, events)


class ICalendarEventComponent(object):
    """ Returns an icalendar object of the event.

    """
    implements(IICalendarEventComponent)

    def __init__(self, context):
        self.context = context
        self.event = IEventAccessor(context)

    def to_ical(self):

        ical = icalendar.Event()

        event = self.event

        # TODO: event.text

        # TODO: until VTIMETZONE component is added and TZID used, everything is
        #       converted to UTC. use real TZID, when VTIMEZONE is used!

        ical.add('dtstamp', utc(pydt(datetime.now())))
        ical.add('created', utc(pydt(event.created)))

        ical.add('uid', event.uid)
        ical.add('url', event.url)

        ical.add('last-modified', utc(pydt(event.last_modified)))
        ical.add('summary', event.title)

        if event.description: ical.add('description', event.description)

        if event.whole_day:
            ical.add('dtstart', utc(pydt(event.start)).date())
            ical.add('dtend', utc(pydt(event.end + timedelta(days=1))).date())
        else:
            ical.add('dtstart', utc(pydt(event.start)))
            ical.add('dtend', utc(pydt(event.end)))

        if event.recurrence:
            if event.recurrence.startswith('RRULE:'):
                recurrence = event.recurrence[6:]
            else:
                recurrence = event.recurrence
            ical.add('rrule', icalendar.prop.vRecur.from_ical(recurrence))

        if event.location: ical.add('location', event.location)

        # TODO: revisit and implement attendee export according to RFC
        if event.attendees:
            for attendee in event.attendees:
                att = icalendar.prop.vCalAddress(attendee)
                att.params['cn'] = icalendar.prop.vText(attendee)
                att.params['ROLE'] = icalendar.prop.vText('REQ-PARTICIPANT')
                ical.add('attendee', att)

        cn = []
        if event.contact_name:
            cn.append(event.contact_name)
        if event.contact_phone:
            cn.append(event.contact_phone)
        if event.contact_email:
            cn.append(event.contact_email)
        if event.event_url:
            cn.append(event.event_url)
        if cn:
            ical.add('contact', u', '.join(cn))

        if event.subjects:
            for subject in event.subjects:
                ical.add('categories', subject)

        return ical


class EventsICal(BrowserView):
    """Returns events in iCal format"""

    def get_ical_string(self):
        cal = IICalendar(self.context)
        return cal.to_ical()

    def __call__(self):
        name = '%s.ics' % self.context.getId()
        self.request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        self.request.RESPONSE.setHeader('Content-Disposition',
            'attachment; filename="%s"' % name)
        self.request.RESPONSE.write(self.get_ical_string())
