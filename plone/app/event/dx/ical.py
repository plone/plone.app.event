from datetime import datetime, timedelta
import icalendar

from zope.component import adapter
from zope.interface import implementer

# ical adapter implementation interfaces
from plone.app.event.interfaces import IICalendarComponent

# ical adapter adapting interfaces
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.app.event.dx.interfaces import IDXEventLocation
from plone.app.event.dx.interfaces import IDXEventAttendees
from plone.app.event.dx.interfaces import IDXEventContact

# DX event behavior adapters
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventRecurrence
from plone.app.event.dx.behaviors import IEventLocation
from plone.app.event.dx.behaviors import IEventAttendees
from plone.app.event.dx.behaviors import IEventContact
from plone.app.dexterity.behaviors.metadata import ICategorization

from plone.event.utils import pydt, utc


@implementer(IICalendarComponent)
@adapter(IDXEvent)
def event_component(context):
    """ Returns an icalendar object of the event.

    """
    ical_event = icalendar.Event()
    # TODO: until VTIMETZONE component is added and TZID used, everything is
    #       converted to UTC. use real TZID, when VTIMEZONE is used!
    ical_event.add('dtstamp', utc(pydt(datetime.now())))
    ical_event.add('created', utc(pydt(context.creation_date)))
    # TODO: UID not present!
    #ical_event.add('uid', context.UID())
    ical_event.add('last-modified', utc(pydt(context.modification_date)))
    ical_event.add('summary', context.title)

    description = context.description
    if description:
        ical_event.add('description', description)

    event_basic = IEventBasic(context)
    if event_basic.whole_day:
        ical_event.add('dtstart', utc(pydt(event_basic.start)).date())
        ical_event.add('dtend', utc(pydt(event_basic.end
                                         + timedelta(days=1))).date())
    else:
        ical_event.add('dtstart', utc(pydt(event_basic.start)))
        ical_event.add('dtend', utc(pydt(event_basic.end)))

    if IDXEventRecurrence.providedBy(context):
        recurrence = IEventRecurrence(context).recurrence
        if recurrence:
            if recurrence.startswith('RRULE:'): recurrence = recurrence[6:]
            ical_event.add('rrule', icalendar.prop.vRecur.from_ical(recurrence))

    if IDXEventLocation.providedBy(context):
        location = IEventLocation(context).location
        if location:
            ical_event.add('location', location)

    # TODO: revisit and implement attendee export according to RFC
    if IDXEventAttendees.providedBy(context):
        attendees = IEventAttendees(context).attendees
        if attendees:
            for attendee in attendees:
                ical_event.add('attendee', attendee)

    if IDXEventContact.providedBy(context):
        event_contact = IEventContact(context)
        cn = []
        if event_contact.contact_name:
            cn.append(event_contact.contact_name)
        if event_contact.contact_phone:
            cn.append(event_contact.contact_phone)
        if event_contact.contact_email:
            cn.append(event_contact.contact_email)
        if cn:
            ical_event.add('contact', u', '.join(cn))

        if event_contact.event_url:
            ical_event.add('url', event_contact.event_url)

    event_cat = ICategorization(context, None)
    if event_cat is not None:
        subjects = event_cat.subjects
        if subjects:
            for subject in subjects:
                ical_event.add('categories', subject)

    return ical_event
