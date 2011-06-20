from zope import schema
from zope.interface import Interface

from plone.rfc5545.interfaces import IEvent as IBaseEvent
from plone.app.event.base import default_timezone
from plone.app.event import messageFactory as _


class IEvent(IBaseEvent):
    """
    """
    #TODO: define schema interface from event at schema


class IEventSettings(Interface):
    """ Global settings for eventish content types.
    """

    portal_timezone = schema.Choice(
            title=_(u"Portal default timezone"),
            description=_(u"help_portal_timezone",
                default=u"The timezone setting of the portal. Users can set "
                         "their own timezone, if available timezones are defined."),
            required=True,
            default=default_timezone,
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
                vocabulary="plone.app.event.AvailableTimezones"
                )
            )
