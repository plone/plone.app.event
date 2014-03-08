from plone.app.event import messageFactory as _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


ISO_DATE_FORMAT = '%Y-%m-%d'


class IBrowserLayer(IDefaultBrowserLayer):
    """plone.app.event specific browser layer.
    """


class IICalendarImportEnabled(Interface):
    """Marker interface for contexts, where icalendar import is enabled.
    """


class IEventSettings(Interface):
    """Global Controlpanel settings for eventish content types.
    """

    portal_timezone = schema.Choice(
        title=_(u"Portal default timezone"),
        description=_(
            u"help_portal_timezone",
            default=u"The timezone setting of the portal. Users can set "
                    u"their own timezone, if available timezones are "
                    u"defined."),
        required=True,
        default=None,
        vocabulary="plone.app.event.Timezones")

    available_timezones = schema.List(
        title=_(u"Available timezones"),
        description=_(
            u"help_available_timezones",
            default=u"The timezones, which should be available for the "
                    u"portal. Can be set for users and events"),
        required=False,
        default=[],
        value_type=schema.Choice(vocabulary="plone.app.event.Timezones"))

    first_weekday = schema.Choice(
        title=_(u'label_first_weekday', default=u'First Weekday'),
        description=_(
            u'help_first_weekday',
            default=u'First day in the Week.'),
        required=True,
        default=None,
        vocabulary="plone.app.event.Weekdays")
