from zope.interface import Interface
from plone.app.event.interfaces import IEvent

class IDXEvent(IEvent):
    """ Marker interface for Dexterity events.
    """

class IDXEventRecurrence(Interface):
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
