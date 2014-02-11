from plone.app.event.dx.behaviors import IEventAttendees
from plone.app.event.dx.behaviors import IEventContact
from plone.app.event.dx.behaviors import IEventLocation
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventRecurrence


class IDXEvent(IEvent):
    """ Marker interface for Dexterity events.
    """


class IDXEventRecurrence(IEventRecurrence):
    """ Marker interface for recurring Dexterity events.
    """


class IDXEventLocation(IEventLocation):
    """ Marker interface for Dexterity events with location.
    """


class IDXEventAttendees(IEventAttendees):
    """ Marker interface for Dexterity events with attendees.
    """


class IDXEventContact(IEventContact):
    """ Marker interface for Dexterity events with contact information.
    """
