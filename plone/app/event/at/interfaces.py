from Products.ATContentTypes.interfaces import IATEvent as IATEvent_ATCT
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventRecurrence


class IATEvent(IATEvent_ATCT, IEvent):
    """IATEvent marker interface.
    """


class IATEventRecurrence(IEventRecurrence):
    """IATEventRecurrence marker interface.
    """
