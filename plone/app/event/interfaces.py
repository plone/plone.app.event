from zope import schema
from zope.interface import Interface, Attribute

from plone.event.utils import default_timezone as fallback_default_timezone
from plone.app.event import messageFactory as _


class IEvent(Interface):
    """ Generic Event
    """
    start = Attribute(u"Event start date")
    end = Attribute(u"Event end date")
    timezone = Attribute(u"Timezone of the event")
    whole_day = Attribute(u"Event lasts whole day")
    recurrence = Attribute(u"RFC5545 compatible recurrence definition")
    location = Attribute(u"Location of the event")
    attendees = Attribute(u"List of attendees")
    contact_name = Attribute(u"Contact name")
    contact_email = Attribute(u"Contact email")
    contact_phone = Attribute(u"Contact phone")
    event_url = Attribute(u"Website of the event")
    subjects = Attribute(u"Categories")
    text = Attribute(u"Summary of the event")


## Adapter interfaces

class IRecurrence(Interface):
    """ Adapter for recurring events.
    """
    def occurrences(limit_start, limit_end):
        """ Return the occurrences of the recurring event.
        """

class IICalendar(Interface):
    """ Adapter, which is used to construct an icalendar object.
    """

class IICalendarComponent(Interface):
    """ Adapter, which is used to construct an event component object for
    icalendar.
    """

class IEventAccessor(Interface):
    """ Generic Event Accessor
    """


# Controlpanel Interface

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

    # TODO: weekday vocab isn't displayed correctly. the default of messageid
    # isn't displayed but the id itself. the value isn't displayed but also the
    # messageid.
    first_weekday = schema.Choice(
            title=_(u'label_first_weekday', default=u'First Weekday'),
            description=_(u'help_first_weekday', default=u'First day in the Week.'),
            required=True,
            default='0',
            vocabulary="plone.app.event.Weekdays"
            )
