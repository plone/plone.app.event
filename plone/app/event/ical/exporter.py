# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from datetime import datetime
from datetime import timedelta
from plone.app.contentlisting.interfaces import IContentListingObject
from plone.app.event.base import default_timezone
from plone.app.event.base import get_events
from plone.app.event.base import RET_MODE_BRAINS
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IICalendar
from plone.event.interfaces import IICalendarEventComponent
from plone.event.interfaces import IOccurrence
from plone.event.utils import is_datetime
from plone.event.utils import tzdel
from plone.event.utils import utc
from Products.ZCatalog.interfaces import ICatalogBrain
from zope.interface import implementer
from zope.publisher.browser import BrowserView

import icalendar
import pytz


PRODID = "-//Plone.org//NONSGML plone.app.event//EN"
VERSION = "2.0"


def construct_icalendar(context, events):
    """Returns an icalendar.Calendar object.

    :param context: A content object, which is used for calendar details like
                    Title and Description. Usually a container, collection or
                    the event itself.

    :param events: The list of event objects, which are included in this
                   calendar.
    """
    cal = icalendar.Calendar()
    cal.add('prodid', PRODID)
    cal.add('version', VERSION)

    cal_tz = default_timezone(context)
    if cal_tz:
        cal.add('x-wr-timezone', cal_tz)

    tzmap = {}
    if not getattr(events, '__getitem__', False):
        events = [events]
    for event in events:
        if ICatalogBrain.providedBy(event) or\
                IContentListingObject.providedBy(event):
            event = event.getObject()
        if not (IEvent.providedBy(event) or IOccurrence.providedBy(event)):
            # Must be an event.
            continue
        acc = IEventAccessor(event)
        tz = acc.timezone
        # TODO: the standard wants each recurrence to have a valid timezone
        # definition. sounds decent, but not realizable.
        if not acc.whole_day:  # whole day events are exported as dates without
                               # timezone information
            if isinstance(tz, tuple):
                tz_start, tz_end = tz
            else:
                tz_start = tz_end = tz
            tzmap = add_to_zones_map(tzmap, tz_start, acc.start)
            tzmap = add_to_zones_map(tzmap, tz_end, acc.end)
        cal.add_component(IICalendarEventComponent(event).to_ical())

    for (tzid, transitions) in tzmap.items():
        cal_tz = icalendar.Timezone()
        cal_tz.add('tzid', tzid)
        cal_tz.add('x-lic-location', tzid)

        for (transition, tzinfo) in transitions.items():

            if tzinfo['dst']:
                cal_tz_sub = icalendar.TimezoneDaylight()
            else:
                cal_tz_sub = icalendar.TimezoneStandard()

            cal_tz_sub.add('tzname', tzinfo['name'])
            cal_tz_sub.add('dtstart', transition)
            cal_tz_sub.add('tzoffsetfrom', tzinfo['tzoffsetfrom'])
            cal_tz_sub.add('tzoffsetto', tzinfo['tzoffsetto'])
            # TODO: add rrule
            # tzi.add('rrule',
            #         {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
            cal_tz.add_component(cal_tz_sub)
        cal.add_component(cal_tz)

    return cal


def add_to_zones_map(tzmap, tzid, dt):
    """Build a dictionary of timezone information from a timezone identifier
    and a date/time object for which the timezone information should be
    calculated.

    :param tzmap: An existing dictionary of timezone information to be extended
                  or an empty dictionary.
    :type tzmap: dictionary
    :param tzid: A timezone identifier.
    :type tzid: string
    :param dt: A datetime object.
    :type dt: datetime

    :returns: A dictionary with timezone information needed to build VTIMEZONE
              entries.
    :rtype: dictionary
    """

    if tzid.lower() == 'utc' or not is_datetime(dt):
        # no need to define UTC nor timezones for date objects.
        return tzmap
    null = datetime(1, 1, 1)
    tz = pytz.timezone(tzid)
    transitions = getattr(tz, '_utc_transition_times', None)
    if not transitions:
        return tzmap  # we need transition definitions
    dtzl = tzdel(utc(dt))

    # get transition time, which is the dtstart of timezone.
    #     the key function returns the value to compare with. as long as item
    #     is smaller or equal like the dt value in UTC, return the item. as
    #     soon as it becomes greater, compare with the smallest possible
    #     datetime, which wouldn't create a match within the max-function. this
    #     way we get the maximum transition time which is smaller than the
    #     given datetime.
    transition = max(transitions,
                     key=lambda item: item if item <= dtzl else null)

    # get previous transition to calculate tzoffsetfrom
    idx = transitions.index(transition)
    prev_idx = idx - 1 if idx > 0 else idx
    prev_transition = transitions[prev_idx]

    def localize(tz, dt):
        if dt is null:
            # dummy time, edge case
            # (dt at beginning of all transitions, see above.)
            return null
        return pytz.utc.localize(dt).astimezone(tz)  # naive to utc + localize
    transition = localize(tz, transition)
    dtstart = tzdel(transition)  # timezone dtstart must be in local time
    prev_transition = localize(tz, prev_transition)

    if tzid not in tzmap:
        tzmap[tzid] = {}  # initial
    if dtstart in tzmap[tzid]:
        return tzmap  # already there
    tzmap[tzid][dtstart] = {
        'dst': transition.dst() > timedelta(0),
        'name': transition.tzname(),
        'tzoffsetfrom': prev_transition.utcoffset(),
        'tzoffsetto': transition.utcoffset(),
        # TODO: recurrence rule
    }
    return tzmap


@implementer(IICalendar)
def calendar_from_event(context):
    """Event adapter. Returns an icalendar.Calendar object from an Event
    context.
    """
    context = aq_inner(context)
    return construct_icalendar(context, [context])


@implementer(IICalendar)
def calendar_from_container(context):
    """Container adapter. Returns an icalendar.Calendar object from a
    Containerish context like a Folder.
    """
    context = aq_inner(context)
    path = '/'.join(context.getPhysicalPath())
    result = get_events(context, ret_mode=RET_MODE_BRAINS,
                        expand=False, path=path)
    return construct_icalendar(context, result)


@implementer(IICalendar)
def calendar_from_collection(context):
    """Container/Event adapter. Returns an icalendar.Calendar object from a
    Collection.
    """
    context = aq_inner(context)
    # The keyword argument brains=False was added to plone.app.contenttypes
    # after 1.0
    result = context.results(batch=False, sort_on='start')
    return construct_icalendar(context, result)


@implementer(IICalendarEventComponent)
class ICalendarEventComponent(object):
    """Returns an icalendar object of the event.
    """

    def __init__(self, context):
        self.context = context
        self.event = IEventAccessor(self.context)
        self.ical = icalendar.Event()

    @property
    def dtstamp(self):
        # must be in uc
        return {'value': utc(datetime.now())}

    @property
    def created(self):
        # must be in uc
        return {'value': utc(self.event.created)}

    @property
    def last_modified(self):
        # must be in uc
        return {'value': utc(self.event.last_modified)}

    @property
    def uid(self):
        return {'value': self.event.sync_uid}

    @property
    def url(self):
        return {'value': self.event.url}

    @property
    def summary(self):
        return {'value': self.event.title}

    @property
    def description(self):
        return {'value': self.event.description}

    @property
    def dtstart(self):
        if self.event.whole_day:
            # RFC5545, 3.6.1
            # For cases where a "VEVENT" calendar component
            # specifies a "DTSTART" property with a DATE value type but no
            # "DTEND" nor "DURATION" property, the event's duration is taken to
            # be one day.
            return {'value': self.event.start.date()}

        # Normal case + Open End case:
        # RFC5545, 3.6.1
        # For cases where a "VEVENT" calendar component
        # specifies a "DTSTART" property with a DATE-TIME value type but no
        # "DTEND" property, the event ends on the same calendar date and
        # time of day specified by the "DTSTART" property.
        return {'value': self.event.start}

    @property
    def dtend(self):
        if self.event.whole_day:
            # RFC5545, 3.6.1
            # For cases where a "VEVENT" calendar component
            # specifies a "DTSTART" property with a DATE value type but no
            # "DTEND" nor "DURATION" property, the event's duration is taken to
            # be one day.
            #
            # RFC5545 doesn't define clearly, if all-day events should have
            # a end date on the same date or one day after the start day at
            # 0:00. Most icalendar libraries use the latter method.
            # Internally, whole_day events end on the same day one second
            # before midnight. Using the RFC5545 preferred method for
            # plone.app.event seems not appropriate, since we would have to fix
            # the date to end a day before for displaying.
            # For exporting, we let whole_day events end on the next day at
            # midnight.
            # See:
            # http://stackoverflow.com/questions/1716237/single-day-all-day
            # -appointments-in-ics-files
            # http://icalevents.com/1778-all-day-events-adding-a-day-or-not/
            # http://www.innerjoin.org/iCalendar/all-day-events.html
            return {'value': self.event.end.date() + timedelta(days=1)}

        elif self.event.open_end:
            # RFC5545, 3.6.1
            # For cases where a "VEVENT" calendar component
            # specifies a "DTSTART" property with a DATE-TIME value type but no
            # "DTEND" property, the event ends on the same calendar date and
            # time of day specified by the "DTSTART" property.
            return None

        return {'value': self.event.end}

    @property
    def recurrence(self):
        if not self.event.recurrence or IOccurrence.providedBy(self.context):
            return None

        ret = []
        for recdef in self.event.recurrence.split():
            prop, val = recdef.split(':')
            if prop == 'RRULE':
                ret.append({
                    'property': prop,
                    'value': icalendar.prop.vRecur.from_ical(val)
                })

            elif prop in ('EXDATE', 'RDATE'):
                factory = icalendar.prop.vDDDLists

                # localize ex/rdate
                # TODO: should better already be localized by event object
                tzid = self.event.timezone
                if isinstance(tzid, tuple):
                    tzid = tzid[0]
                # get list of datetime values from ical string
                try:
                    dtlist = factory.from_ical(val, timezone=tzid)
                except ValueError:
                    # TODO: caused by a bug in plone.formwidget.recurrence,
                    # where the recurrencewidget or plone.event fails with
                    # COUNT=1 and a extra RDATE.
                    # TODO: REMOVE this workaround, once this failure is
                    # fixed in recurrence widget.
                    continue
                ret.append({
                    'property': prop,
                    'value': dtlist
                })

        return ret

    @property
    def location(self):
        return {'value': self.event.location}

    @property
    def attendee(self):
        # TODO: revisit and implement attendee export according to RFC
        ret = []
        for attendee in self.event.attendees or []:
            att = icalendar.prop.vCalAddress(attendee)
            att.params['cn'] = icalendar.prop.vText(attendee)
            att.params['ROLE'] = icalendar.prop.vText('REQ-PARTICIPANT')
            ret.append(att)
        return {'value': ret}

    @property
    def contact(self):
        cn = []
        event = self.event
        if event.contact_name:
            cn.append(event.contact_name)
        if event.contact_phone:
            cn.append(event.contact_phone)
        if event.contact_email:
            cn.append(event.contact_email)
        if event.event_url:
            cn.append(event.event_url)

        return {'value': u', '.join(cn)}

    @property
    def categories(self):
        ret = []
        for cat in self.event.subjects or []:
            ret.append({'value': cat})
        return ret or None

    @property
    def geo(self):
        """Not implemented.
        """
        return

    def ical_add(self, prop, val):
        if not val:
            return

        if not isinstance(val, list):
            val = [val]

        for _val in val:
            assert(isinstance(_val, dict))
            value = _val['value']
            if not value:
                continue
            prop = _val.get('property', prop)
            params = _val.get('parameters', None)
            self.ical.add(prop, value, params)

    def to_ical(self):
        # TODO: event.text

        ical_add = self.ical_add
        ical_add('dtstamp', self.dtstamp)
        ical_add('created', self.created)
        ical_add('last-modified', self.last_modified)
        ical_add('uid', self.uid)
        ical_add('url', self.url)
        ical_add('summary', self.summary)
        ical_add('description', self.description)
        ical_add('dtstart', self.dtstart)
        ical_add('dtend', self.dtend)
        ical_add(None, self.recurrence)  # property key set via val
        ical_add('location', self.location)
        ical_add('attendee', self.attendee)
        ical_add('contact', self.contact)
        ical_add('categories', self.categories)
        ical_add('geo', self.geo)

        return self.ical


class EventsICal(BrowserView):
    """Returns events in iCal format.
    """

    def get_ical_string(self):
        cal = IICalendar(self.context)
        return cal.to_ical()

    def __call__(self):
        ical = self.get_ical_string()
        name = '{0}.ics'.format(self.context.getId())
        self.request.response.setHeader('Content-Type', 'text/calendar')
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="{0}"'.format(name)
        )
        self.request.response.setHeader('Content-Length', len(ical))
        self.request.response.write(ical)
