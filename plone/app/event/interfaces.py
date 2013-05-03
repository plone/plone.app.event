from plone.app.event import messageFactory as _
from plone.event.utils import default_timezone as fallback_default_timezone
from zope import schema
from zope.interface import Attribute
from zope.interface import Interface


ISO_DATE_FORMAT = '%Y-%m-%d'


class IICalendarImportEnabled(Interface):
    """Marker interface for contexts, where icalendar import is enabled.
    """

class ICalendarLinkbase(Interface):
    """Adapter Interface to retrieve a base url for a calendar view.

    """

    urlpath = Attribute("""Urlpath for the CalendarLinkbase methods. In the
            default implementation, it's the NavigationRoot's absolute_url.
            After instantiating the class, you can easily overwrite or extend
            this attribute.""")

    def date_events_url(date):
        """Get a URL to retrieve all events on a given day.

        :param date: The date to search events for in isoformat (ISO 8601,
                    YYYY-MM-DD).
        :type date: string

        :returns: URL linking to a page with events on the given date.
        :rtype: string

        """

    def past_events_url():
        """Get a URL to retrieve past events.

        :returns: URL linking to a page with past events.
        :rtype: string

        """

    def next_events_url():
        """Get a URL to retrieve upcoming events.

        :returns: URL linking to a page with upcoming events.
        :rtype: string

        """

    def all_events_url():
        """Get a URL to retrieve all events.

        :returns: URL linking to a page with events on the given date.
        :rtype: string

        """


class IEventSettings(Interface):
    """Global Controlpanel settings for eventish content types.
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
            default='0',
            vocabulary="plone.app.event.Weekdays"
            )
