from .exporter import (
    construct_icalendar,
    calendar_from_event,
    calendar_from_container,
    calendar_from_collection,
    ICalendarEventComponent,
    EventsICal
)
from .importer import ical_import

from zope.deprecation import deprecate

# BBB - remove with 1.0
@deprecate('construct_calendar is deprecated and will be removed in version'
           '1.0. Please use construct_icalendar instead.')
def construct_calendar(context, events):
    return construct_icalendar(context, events)
