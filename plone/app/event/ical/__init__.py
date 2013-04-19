from .exporter import (
    construct_icalendar,
    calendar_from_event,
    calendar_from_container,
    calendar_from_collection,
    ICalendarEventComponent,
    EventsICal
)
from .importer import ical_import

# BBB - remove with 1.0
def construct_calendar(context, events):
    return construct_icalendar(context, events)
