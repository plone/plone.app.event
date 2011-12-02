import icalendar

from zope.component import adapter
from zope.interface import implementer

# ical adapter implementation interfaces
from plone.app.event.interfaces import IICalendarComponent

# ical adapter adapting interfaces
from plone.app.event.dx.interfaces import IDXEvent


@implementer(IICalendarComponent)
@adapter(IDXEvent)
def event_component(context):
    """ Returns an icalendar object of the event.

    """
    ical_event = icalendar.Event()
    # TODO: implement me!
    return ical_event
