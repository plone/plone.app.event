from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventRecurrence
from zope.interface import Interface


class IDXEvent(IEvent):
    """ Marker interface for Dexterity events.
    """

class IDXEventRecurrence(IEventRecurrence):
    """ Marker interface for recurring Dexterity events.
    """

class IDXEventLocation(Interface):
    """ Marker interface for Dexterity events with location.
    """

class IDXEventAttendees(Interface):
    """ Marker interface for Dexterity events with attendees.
    """

class IDXEventContact(Interface):
    """ Marker interface for Dexterity events with contact information.
    """
