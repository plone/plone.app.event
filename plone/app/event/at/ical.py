from datetime import datetime, timedelta
import icalendar

from zope.component import adapter
from zope.interface import implementer

from plone.event.utils import pydt, utc

# ical adapter implementation interfaces
from plone.app.event.interfaces import IICalendarComponent

# ical adapter adapting interfaces
from Products.ATContentTypes.interfaces import IATEvent


@implementer(IICalendarComponent)
@adapter(IATEvent)
def event_component(context):
    """ Returns an icalendar object of the event.

    """
    ical_event = icalendar.Event()
    # TODO: until VTIMETZONE component is added and TZID used, everything is
    #       converted to UTC. use real TZID, when VTIMEZONE is used!
    ical_event.add('dtstamp', utc(pydt(datetime.now())))
    ical_event.add('created', utc(pydt(context.creation_date)))
    ical_event.add('uid', context.UID())
    ical_event.add('last-modified', utc(pydt(context.modification_date)))
    ical_event.add('summary', context.Title())
    if context.whole_day:
        ical_event.add('dtstart', utc(pydt(context.start())).date())
        ical_event.add('dtend', utc(pydt(context.end())
                                         + timedelta(days=1)).date())
    else:
        ical_event.add('dtstart', utc(pydt(context.start())))
        ical_event.add('dtend', utc(pydt(context.end())))

    recurrence = context.recurrence
    if recurrence:
        if recurrence.startswith('RRULE:'): recurrence = recurrence[6:]
        ical_event.add('rrule', icalendar.prop.vRecur.from_ical(recurrence))

    description = context.Description()
    if description:
        ical_event.add('description', description)

    location = context.getLocation()
    if location:
        ical_event.add('location', location)

    subjects= context.Subject()
    for subject in subjects:
        ical_event.add('categories', subject)

    # TODO: revisit and implement attendee export according to RFC
    attendees = context.getAttendees()
    for attendee in attendees:
        ical_event.add('attendee', attendee)

    cn = []
    contact = context.contact_name()
    if contact:
        cn.append(contact) # TODO safe_unicode conversion needed?
    phone = context.contact_phone()
    if phone:
        cn.append(phone)
    email = context.contact_email()
    if email:
        cn.append(email)
    if cn:
        ical_event.add('contact', u', '.join(cn))

    url = context.event_url()
    if url:
        ical_event.add('url', url)

    return ical_event
