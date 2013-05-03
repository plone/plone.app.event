from plone.app.event.ical.exporter import EventsICal
from plone.app.event.ical.exporter import ICalendarEventComponent
from plone.app.event.ical.exporter import calendar_from_collection
from plone.app.event.ical.exporter import calendar_from_container
from plone.app.event.ical.exporter import calendar_from_event
from plone.app.event.ical.exporter import construct_icalendar
from plone.app.event.ical.importer import ical_import
from zope.deprecation import deprecate


# BBB - remove with 1.0
@deprecate('construct_calendar is deprecated and will be removed in version '
           '1.0. Please use construct_icalendar instead.')
def construct_calendar(context, events):
    return construct_icalendar(context, events)
