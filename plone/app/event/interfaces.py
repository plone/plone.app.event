from zope import schema
from zope.interface import Interface, Attribute

from plone.event.utils import default_timezone as fallback_default_timezone
from plone.app.event import messageFactory as _


class IICalendar(Interface):
    """ Adapter, which is used to construct an icalendar object.
    """

class IICalendarComponent(Interface):
    """ Adapter, which is used to construct an event component object for
    icalendar.
    """

class IEvent(Interface):
    """ Event schema

    For reference: this are the RFC5545 event properties:

    ; The following are REQUIRED,
    ; but MUST NOT occur more than once.
    ;
    dtstamp / uid /
    ;
    ; The following is REQUIRED if the component
    ; appears in an iCalendar object that doesn't
    ; specify the "METHOD" property; otherwise, it
    ; is OPTIONAL; in any case, it MUST NOT occur
    ; more than once.
    ;
    dtstart /
    ;
    ; The following are OPTIONAL,
    ; but MUST NOT occur more than once.
    ;
    class / created / description / geo /
    last-mod / location / organizer / priority /
    seq / status / summary / transp /
    url / recurid /
    ;
    ; The following is OPTIONAL,
    ; but SHOULD NOT occur more than once.
    ;
    rrule /
    ;
    ; Either 'dtend' or 'duration' MAY appear in
    ; a 'eventprop', but 'dtend' and 'duration'
    ; MUST NOT occur in the same 'eventprop'.
    ;
    dtend / duration /
    ;
    ; The following are OPTIONAL,
    ; and MAY occur more than once.
    ;
    attach / attendee / categories / comment /
    contact / exdate / rstatus / related /
    resources / rdate / x-prop / iana-prop
    """

    start = Attribute(u"Event start date")
    end = Attribute(u"Event end date")
    timezone = Attribute(u"Timezone of the event")
    recurrence = Attribute(u"RFC5545 compatible recurrence definition")
    whole_day = Attribute(u"Event lasts whole day")
    location = Attribute(u"Location of the event")
    text = Attribute(u"Summary of the event")
    attendees = Attribute(u"List of attendees")
    event_url = Attribute(u"Website of the event")
    contact_name = Attribute(u"Contact name")
    contact_email = Attribute(u"Contact email")
    contact_phone = Attribute(u"Contact phone")



class IEventSettings(Interface):
    """ Global settings for eventish content types.
    """

    portal_timezone = schema.Choice(
            title=_(u"Portal default timezone"),
            description=_(u"help_portal_timezone",
                default=u"The timezone setting of the portal. Users can set "
                         "their own timezone, if available timezones are defined."),
            required=True,
            default=fallback_default_timezone(),
            vocabulary="plone.app.event.Timezones"
            )

    available_timezones = schema.List(
            title=_(u"Available timezones"),
            description=_(u"help_available_timezones",
                default=u"The timezones, which should be available for the portal. "
                         "Can be set for users and events"),
            required=False,
            default=[],
            value_type=schema.Choice(
                vocabulary="plone.app.event.Timezones"
                )
            )

    first_weekday = schema.Choice(
            title=_(u'label_first_weekday', default=u'First Weekday'),
            description=_(u'help_first_weekday', default=u'First day in the Week.'),
            required=True,
            default=0,
            vocabulary="plone.app.event.Weekdays"
            )
