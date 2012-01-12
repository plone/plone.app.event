import icalendar

from Acquisition import aq_inner
from zope.interface import implementer
from zope.publisher.browser import BrowserView

from plone.app.event.base import default_timezone
from plone.app.event.base import get_portal_events

# ical adapter implementation interfaces
from plone.app.event.interfaces import IICalendar
from plone.app.event.interfaces import IICalendarComponent


PRODID = "-//Plone.org//NONSGML plone.app.event//EN"
VERSION = "2.0"

def construct_calendar(context, events):
    """ Returns an icalendar.Calendar object.

    :param context: A content object, which is used for calendar details like
                    Title and Description. Usually a container, collection or
                    the event itself.

    :param events: The list of event objects, which are included in this
                   calendar.

    """
    cal = icalendar.Calendar()
    cal.add('prodid', PRODID)
    cal.add('version', VERSION)

    # TODO: use plone's new uuid adapter instead of uid
    # Non-Standard calendar extensions. also see:
    # http://en.wikipedia.org/wiki/ICalendar#cite_note-11
    cal_title = context.Title()
    if cal_title: cal.add('x-wr-calname', cal_title)
    cal_desc = context.Description()
    if cal_desc: cal.add('x-wr-caldesc', cal_desc)
    if getattr(context, 'UID', False): # portal object does not have UID
        cal_uid = context.UID()
        cal.add('x-wr-relcalid', cal_uid)
    cal_tz = default_timezone(context)
    if cal_tz: cal.add('x-wr-timezone', cal_tz)

    for event in events:
        cal.add_component(IICalendarComponent(event))

    return cal


@implementer(IICalendar)
def calendar_from_event(context):
    """ Event adapter. Returns an icalendar.Calendar object from an Event
    context.

    """
    context = aq_inner(context)
    events = [context]
    return construct_calendar(context, events)


@implementer(IICalendar)
def calendar_from_container(context):
    """ Container adapter. Returns an icalendar.Calendar object from a 
    Containerish context like a Folder.

    """
    context = aq_inner(context)
    path = '/'.join(context.getPhysicalPath())
    result = get_portal_events(context, path=path)
    events = [item.getObject() for item in result]
    # TODO: should i become a generator?
    # TODO: let construct_calendar expand brains to objects - so a
    # generator would make some sense...
    return construct_calendar(context, events)


@implementer(IICalendar)
def calendar_from_collection(context):
    """ Container/Event adapter. Returns an icalendar.Calendar object from a
    Collection.

    """
    context = aq_inner(context)
    result = get_portal_events(context)
    events = [item.getObject() for item in result]
    return construct_calendar(context, events)


class EventsICal(BrowserView):
    """Returns events in iCal format"""

    def get_ical_string(self):
        cal = IICalendar(self.context)
        # TODO: unicode decode error, if umlaute in cal.as_string
        #       e.g. umlaute in subjects
        #       cal.as_string returns ascii instead of unicode.
        #       FIX in icalendar package
        return cal.to_ical().encode('utf-8')

    def __call__(self):
        name = '%s.ics' % self.context.getId()
        self.request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        self.request.RESPONSE.setHeader('Content-Disposition',
            'attachment; filename="%s"' % name)
        self.request.RESPONSE.write(self.get_ical_string())
