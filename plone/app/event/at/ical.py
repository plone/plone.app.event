from datetime import datetime
import icalendar

from zope.component import adapter
from zope.interface import implementer

from plone.event.utils import pydt

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
    ical_event.add('dtstamp', datetime.now())
    ical_event.add('created', pydt(context.creation_date))
    ical_event.add('uid', context.UID())
    ical_event.add('last-modified', pydt(context.modification_date))
    ical_event.add('summary', context.Title())
    ical_event.add('dtstart', pydt(context.start()))
    ical_event.add('dtend', pydt(context.end()))

    recurrence = context.recurrence
    if recurrence:
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
