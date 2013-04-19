from calendar import monthrange
from datetime import date
from datetime import datetime
from datetime import timedelta

import pytz
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time as orig_ulocalized_time
from Products.CMFPlone.utils import safe_callable
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.event.interfaces import IEvent, IEventRecurrence
from plone.event.interfaces import IRecurrenceSupport, IEventAccessor
from plone.event.utils import default_timezone as fallback_default_timezone
from plone.event.utils import validated_timezone
from plone.event.utils import pydt
from plone.event.utils import is_same_day, is_same_time
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility, queryUtility
from zope.component.hooks import getSite
from zope.interface import implements, Interface

from plone.app.event.interfaces import ICalendarLinkbase
from plone.app.event.interfaces import IEventSettings
from plone.app.event.interfaces import ISO_DATE_FORMAT
from plone.app.event.vocabularies import replacement_zones


DEFAULT_END_DELTA = 1 # hours
FALLBACK_TIMEZONE = 'UTC'


# RETRIEVE EVENTS

def get_events(context, start=None, end=None, limit=None,
               ret_mode=1, expand=False,
               sort='start', sort_reverse=False, **kw):
    """Return all events as catalog brains, possibly within a given
    timeframe.

    :param context: [required] A context object.
    :type context: Content object

    :param start: Date, from which on events should be searched.
    :type start: Python datetime.

    :param end: Date, until which events should be searched.
    :type end: Python datetime

    :param limit: Number of items to be returned.
    :type limit: integer

    :param ret_mode: Return type of search results. These options are
                     available:
                         * 1 (brains): Return results as catalog brains.
                         * 2 (objects): Return results as IEvent and/or
                                        IOccurrence objects.
                         * 3 (accessors): Return results as IEventAccessor
                                          wrapper objects.
    :type ret_mode: integer [1|2|3]

    :param expand: Expand the results to all occurrences (withing the
                   timeframe, if given.). With this option set to True, the
                   resultset also includes the event's recurrence occurrences.
                   The result is sorted by the start date.
                   Only available in ret_mode 2 (objects) and 3 (accessors).
    :type expand: boolean

    :param sort: Catalog index id to sort on. Not available with expand=True.
    :type sort: string

    :param sort_reverse: Change the order of the sorting.
    :type sort_reverse: boolean

    :returns: Portal events, matching the search criteria.
    :rtype: catalog brains

    """
    start, end = _prepare_range(context, start, end)

    query = {}
    query['object_provides'] = IEvent.__identifier__

    if 'path' not in kw:
        # limit to the current navigation root, usually (not always) site
        portal = getSite()
        navroot = getNavigationRootObject(context, portal)
        query['path'] = '/'.join(navroot.getPhysicalPath())
    else:
        query['path'] = kw['path']

    if start:
        # All events from start date ongoing:
        # The minimum end date of events is the date from which we search.
        query['end'] = {'query': start, 'range': 'min'}
    if end:
        # All events until range_end:
        # The maximum start date must be the date until we search.
        query['start'] = {'query': end, 'range': 'max'}

    if not expand:
        # Expanded results will be sorted later.
        query['sort_on'] = sort
        if sort_reverse: query['sort_order'] = 'reverse'

    if limit:
        query['sort_limit'] = limit

    query.update(kw)

    cat = getToolByName(context, 'portal_catalog')
    result = cat(**query)

    def _getattr_safe_called(obj, attr):
        val = getattr(obj, attr, None)
        if safe_callable(val):
            val = val()
        return val
    def _obj_or_acc(obj, ret_mode):
        if ret_mode == 2:
            return obj
        elif ret_mode == 3:
            return IEventAccessor(obj)

    if ret_mode in (2, 3) and expand == False:
        result = [_obj_or_acc(it.getObject(), ret_mode) for it in result]
    elif ret_mode in (2, 3) and expand == True:
        exp_result = []
        for it in result:
            obj = it.getObject()
            if IEventRecurrence.providedBy(obj):
                occurrences = [_obj_or_acc(occ, ret_mode) for occ in
                               IRecurrenceSupport(obj).occurrences(start, end)]
            else:
                occurrences = [obj]
            exp_result += occurrences
        if sort:
            # support AT and DX without wrapped by IEventAccessor (mainly for
            # sorting after "start" or "end").
            exp_result.sort(key=lambda x: _getattr_safe_called(x, sort))
        if sort_reverse:
            exp_result.reverse()
        result = exp_result

    if limit:
        # Expanded events as well as catalog search results (which might not
        # exactly be limited by the query) must be limited again.
        result = result[:limit]

    return result


def construct_calendar(context, events):
    """Return a dictionary with dates in a given timeframe as keys and the
    actual occurrences for that date for building calendars.

    :param context: [required] A context object.
    :type context: Content object

    :param events: List of IEvent and/or IOccurrence objects, to construct a
                   calendar data structure from.
    :type events: list

    :returns: Dictionary with dates keys and occurrences as values.
    :rtype: dict

    """
    events_by_date = {}
    for event in events:
        acc = IEventAccessor(event)
        start_str = datetime.strftime(acc.start, '%Y-%m-%d')
        # TODO: add span_events parameter to include dates btw. start
        # and end also. for events lasting longer than a day...
        if start_str not in events_by_date:
            events_by_date[start_str] = [event]
        else:
            events_by_date[start_str].append(event)
    return events_by_date


class CalendarLinkbase(object):
    """Default adapter to retrieve a base url for a calendar view.
    In this default implementation we use the @@event_listing view as calendar
    view.

    For method documentation, see interfaces.py.

    """
    adapts(Interface)
    implements(ICalendarLinkbase)

    def __init__(self, context):
        self.context = context
        portal = getSite()
        self.urlpath = getNavigationRootObject(context, portal).absolute_url()

    def date_events_url(self, date):
        url = '%s/@@event_listing?mode=day&date=%s' % (self.urlpath, date)
        return url

    def past_events_url(self):
        """Get a URL to retrieve past events.
        """
        url = '%s/@@event_listing?mode=past' % self.urlpath
        return url

    def next_events_url(self):
        """Get a URL to retrieve upcoming events.
        """
        url = '%s/@@event_listing?mode=future' % self.urlpath
        return url

    def all_events_url(self):
        """Get a URL to retrieve all events.
        """
        url = '%s/@@event_listing?mode=all' % self.urlpath
        return url


def dt_start_of_day(dt):
    """Returns a Python datetime instance set to the start time of the given
    day (00:00:00).

    :param dt: datetime to set to the start time of the day.
    :type dt: Python datetime
    :returns: datetime set to the start time of the day (00:00:00).
    :rtype: Python datetime

    """
    if not isinstance(dt, datetime):
        # is a date
        dt = datetime.fromordinal(dt.toordinal())
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def dt_end_of_day(dt):
    """Returns a Python datetime instance set to the end time of the given day
    (23:59:59).

    :param dt: datetime to set to the end time of the day.
    :type dt: Python datetime
    :returns: datetime set to the end time of the day (23:59:59).
    :rtype: Python datetime

    """
    if not isinstance(dt, datetime):
        # is a date
        dt = datetime.fromordinal(dt.toordinal())
    return dt.replace(hour=23, minute=59, second=59, microsecond=0)


def start_end_from_mode(mode, dt=None, context=None):
    """Return a start and end date from a given mode string, like
    "today", "past" or "future". This can be used in event retrieval
    functions.

    :param mode: One of the following modes:
                    'all' Show all events.
                    'past': Show only past events with descending sorting.
                    'future': Show only future events (default).
                    'today': Show todays events.
                    'now': Show todays upcoming events.
                    '7days': Show events until 7 days in future.
                    'day': Return all events on the given day (dt parameter
                           required)
                    'week': Show a weeks events, optionally from a given date.
                 These settings override the start and end parameters.
                    Not implemented yet:
                    'month': Show this month's events.
    :type mode: string

    :param dt: Optional datetime for day mode.
    :type dt: Python datetime

    """
    if not context: context = getSite()
    now = localized_now(context)
    start = end = None

    if mode == 'all':
        start = None
        end = None

    elif mode == 'past':
        start = None
        end = now

    elif mode == 'future':
        start = now
        end = None

    elif mode == 'now':
        start = now
        end = dt_end_of_day(now)

    elif mode == '7days':
        start = now
        end = dt_end_of_day(now+timedelta(days=6))

    elif mode == 'day' or mode =='today':
        if not dt: dt = now # show today
        start = dt_start_of_day(dt)
        end = dt_end_of_day(dt)

    elif mode == 'week':
        if not dt: dt = now # show this week
        wkd = dt.weekday()
        first = first_weekday()

        if first <= wkd:
            delta = wkd - first # >= 0
        if first > wkd:
            delta = wkd + 7 - first # > 0

        start = dt_start_of_day(dt - timedelta(days=delta))
        end = dt_end_of_day(start + timedelta(days=6))

    elif mode =='month':
        if not dt: dt = now # show this month
        year = dt.year
        month = dt.month
        last_day = monthrange(year, month)[1] # (wkday, days)
        start = dt_start_of_day(datetime(year, month, 1))
        end = dt_end_of_day(datetime(year, month, last_day))

    return start, end


def default_end_dt():
    """Return the default end as python datetime for prefilling forms.

    :returns: Default end datetime.
    :rtype: Python datetime

    """
    return localized_now() + timedelta(hours=DEFAULT_END_DELTA)


def default_end_DT():
    """Return the default end as Zope DateTime for prefilling forms.

    :returns: Default end DateTime.
    :rtype: Zope DateTime

    """
    return DT(default_end_dt())


def default_start_dt():
    """Return the default start as python datetime for prefilling forms.

    :returns: Default start datetime.
    :rtype: Python datetime

    """
    return localized_now()


def default_start_DT():
    """Return the default start as a Zope DateTime for prefilling archetypes
    forms.

    :returns: Default start DateTime.
    :rtype: Zope DateTime

    """
    return DT(default_start_dt())


def default_timezone(context=None):
    """Return the timezone from the portal or user.

    :param context: Optional context. If not given, the current Site is used.
    :type context: Content object
    :returns: Timezone identifier.
    :rtype: string

    """
    # TODO: test member timezone
    if not context: context = getSite()

    membership = getToolByName(context, 'portal_membership', None)
    if membership and not membership.isAnonymousUser(): # the user has not logged in
        member = membership.getAuthenticatedMember()
        member_timezone = member.getProperty('timezone', None)
        if member_timezone:
            return pytz.timezone(member_timezone).zone

    portal_timezone = None
    reg = queryUtility(IRegistry, context=context, default=None)
    if reg:
        portal_timezone= reg.forInterface(
                IEventSettings, prefix="plone.app.event").portal_timezone

    # fallback to what plone.event is doing
    if not portal_timezone:
        portal_timezone = fallback_default_timezone()

    if portal_timezone in replacement_zones.keys():
        portal_timezone = replacement_zones[portal_timezone]
    portal_timezone = validated_timezone(portal_timezone, FALLBACK_TIMEZONE)

    return portal_timezone


def default_tzinfo(context=None):
    """Return the default timezone as tzinfo instance.

    :param context: Optional context. If not given, the current Site is used.
    :type context: Content object
    :returns: Pytz timezone object.
    :rtype: Python tzinfo

    """
    return pytz.timezone(default_timezone(context))


def first_weekday():
    """Returns the number of the first Weekday in a Week, as defined in
    the registry. 0 is Monday, 6 is Sunday, as expected by Python's datetime.

    PLEASE NOTE: strftime %w interprets 0 as Sunday unlike the calendar module!

    :returns: Index of first weekday (0..Monday, 6..Sunday)
    :rtype: integer

    """
    controlpanel = getUtility(IRegistry).forInterface(IEventSettings,
                                                      prefix="plone.app.event")
    first_wd = controlpanel.first_weekday
    if not first_wd:
        return 0
    else:
        return int(first_wd)

def first_weekday_sun0():
    """Returns the number of the first Weekday in a Week, as defined in
    the registry.
    In this case 0 is Sunday and 6 is Saturday, as expected by Strftime.

    This method exists, because IRegistry utility isn't early available and in
    some cases we need to pass a first weekday config parameter to another
    package, which then gets just called.

    """
    return cal_to_strftime_wkday(first_weekday())


def cal_to_strftime_wkday(day):
    """Convert calendar day numbers to strftime day numbers.
    Strftime %w interprets 0 as Sunday unlike the calendar:
    Calendar: 0..Monday, 6..Sunday
    Strftime: 0..Sunday, 6..Saturday

    :param day: The calendar.Calendar day number.
    :type day: integer
    :returns: The strftime day number.
    :rtype: integer

    """
    if day==6:
        return 0
    else:
        return day+1


def strftime_to_cal_wkday(day):
    """Convert strftime day numbers to calendar day numbers.
    Strftime %w interprets 0 as Sunday unlike the calendar:
    Calendar: 0..Monday, 6..Sunday
    Strftime: 0..Sunday, 6..Saturday

    :param day: The strftime day number.
    :type day: integer
    :returns: The calendar.Calendar day number.
    :rtype: integer

    """
    if day==0:
        return 6
    else:
        return day-1


def DT(dt):
    """Return a Zope DateTime instance from a Python datetime instance.

    :param dt: Python datetime instance.
    :type dt: Python datetime
    :returns: Zope DateTime
    :rtype: Zope DateTime

    """
    tz = default_timezone(getSite())
    ret = None
    if isinstance(dt, datetime):
        zone_id = getattr(dt.tzinfo, 'zone', tz)
        tz = validated_timezone(zone_id, tz)
        ret = DateTime(dt.year, dt.month, dt.day,\
                        dt.hour, dt.minute, dt.second+dt.microsecond/1000000.0,
                        tz)
    elif isinstance(dt, date):
        ret = DateTime(dt.year, dt.month, dt.day, 0, 0, 0, tz)
    elif isinstance(dt, DateTime):
        # No timezone validation. DateTime knows how to handle it's zones.
        ret = dt
    return ret


def localized_now(context=None):
    """Return the current datetime localized to the default timezone.

    :param context: Context object.
    :type context: Content object
    :returns: Localized current datetime.
    :rtype: Python datetime

    """
    if not context: context = getSite()
    return datetime.now(default_tzinfo(context))


def localized_today(context=None):
    """Return the current date localized to the default timezone.

    :param context: Context object.
    :type context: Content object
    :returns: Localized current date.
    :rtype: Python date

    """
    now = localized_now(context)
    return date(now.year, now.month, now.day)


def _prepare_range(context, start, end):
    """Prepare a date-range to contain timezone info and set end to next day,
    if end is a date.

    :param context: [required] Context object.
    :type context: Content object
    :param start: [required] Range start.
    :type start: Python date or datetime
    :param end: [required] Range end.
    :type end: Python date or datetime
    :returns: Localized start and end datetime.
    :rtype: tuple

    """
    tz = default_tzinfo(context)
    start = pydt(start, missing_zone=tz)
    if not isinstance(end, datetime) and isinstance(end, date):
        # set range_end to the next day, time will be 0:00
        # so the whole previous day is also used for search
        end = end + timedelta(days=1)
    end = pydt(end, missing_zone=tz)
    return start, end


def guess_date_from(datestr, context=None):
    """Returns a timezone aware date object if an arbitrary ASCII string is
    formatted in an ISO date format, otherwise None is returned.

    Used for traversing and Occurence ids.

    :param datestr: Date string in an ISO format.
    :type datestr: string
    :param context: Context object (for retrieving the timezone).
    :type context: Content object
    :returns: Localized date object.
    :rtype: Python date

    """
    try:
        dateobj = datetime.strptime(datestr, ISO_DATE_FORMAT)
    except ValueError:
        return

    return pytz.timezone(default_timezone(context)).localize(dateobj)


def dates_for_display(occurrence):
    """ Return a dictionary containing pre-calculated information for building
    <start>-<end> date strings.

    Keys are:
        'start_date' - date string of the start date
        'start_time' - time string of the start date
        'end_date'   - date string of the end date
        'end_time'   - time string of the end date
        'start_iso'  - start date in iso format
        'end_iso'    - end date in iso format
        'same_day'   - event ends on the same day
        'same_time'  - event ends at same time


    The behavior os ulocalized_time() with time_only is odd.
    Setting time_only=False should return the date part only and *not*
    the time

    >>> from DateTime import DateTime
    >>> start = DateTime(2010,3,16,14,40)
    >>> from zope.componen.hooks import getSite
    >>> site = getSite()
    >>> ulocalized_time(start, False,  time_only=True, context=site)
    u'14:40'
    >>> ulocalized_time(start, False,  time_only=False, context=site)
    u'14:40'
    >>> ulocalized_time(start, False,  time_only=None, context=site)
    u'16.03.2010'

    """
    acc = IEventAccessor(occurrence)

    # this needs to separate date and time as ulocalized_time does
    DT_start = DT(acc.start)
    DT_end = DT(acc.end)
    start_date = ulocalized_time(
            DT_start, long_format=False, time_only=None, context=occurrence)
    start_time = ulocalized_time(
            DT_start, long_format=False, time_only=True, context=occurrence)
    end_date = ulocalized_time(
            DT_end, long_format=False, time_only=None, context=occurrence)
    end_time = ulocalized_time(
            DT_end, long_format=False, time_only=True, context=occurrence)

    same_day = is_same_day(acc.start, acc.end)
    same_time = is_same_time(acc.start, acc.end)

    # set time fields to None for whole day events
    if acc.whole_day:
        start_time = end_time = None

    return dict(# Start
                start_date=start_date,
                start_time=start_time,
                start_iso=acc.start.isoformat(),
                # End
                end_date=end_date,
                end_time=end_time,
                end_iso=acc.end.isoformat(),
                # Meta
                same_day=same_day,
                same_time=same_time,
                whole_day=acc.whole_day,
                url=acc.url)


def date_speller(context, dt):
    """Return a dictionary with localized and readably formated date parts.

    """
    dt = DT(dt)
    util = getToolByName(context, 'translation_service')
    dom = 'plonelocales'

    def zero_pad(num):
        return '%02d' % num

    date_dict = dict(
        year = dt.year(),

        month = util.translate(util.month_msgid(dt.month()),
                domain=dom, context=context),

        month_abbr = util.translate(util.month_msgid(dt.month(),'a'),
                domain=dom, context=context),

        wkday = util.translate(util.day_msgid(dt.dow()),
                domain=dom, context=context),

        wkday_abbr = util.translate(util.day_msgid(dt.dow(),'a'),
                domain=dom, context=context),

        day = dt.day(),
        day2 = zero_pad(dt.day()),

        hour = dt.hour(),
        hour2 = zero_pad(dt.hour()),

        minute = dt.minute(),
        minute2 = zero_pad(dt.minute()),

        second = dt.second(),
        second2 = zero_pad(dt.second())
    )
    return date_dict


# Workaround for buggy strftime with timezone handling in DateTime.
# See: https://github.com/plone/plone.app.event/pull/47
# TODO: should land in CMFPlone or fixed in DateTime.
_strftime = lambda v, fmt: pydt(v).strftime(fmt)

class PatchedDateTime(DateTime):
    def strftime(self, fmt):
        return _strftime(self, fmt)

def ulocalized_time(time, *args, **kwargs):
    """Corrects for DateTime bugs doing wrong thing with timezones"""
    wrapped_time = PatchedDateTime(time)
    return orig_ulocalized_time(wrapped_time, *args, **kwargs)



# BBB - Remove with 1.0
def get_portal_events(context, range_start=None, range_end=None, limit=None,
                      sort='start', sort_reverse=False, **kw):
    return get_events(context, start=range_start, end=range_end, limit=limit,
                      sort=sort, sort_reverse=sort_reverse, **kw)

def get_occurrences_by_date(context, range_start=None, range_end=None, **kw):
    events = get_events(context, start=range_start, end=range_end,
                        ret_mode=2, expand=True, **kw)
    return construct_calendar(context, events)

def get_occurrences_from_brains(context, brains,
        range_start=None, range_end=None, limit=None):
    """Returns a flat list of EventAccessor objects from a given result of a
    catalog query. The list is sorted by the occurrence start date.

    :param context: [required] A context object.
    :type context: Content object
    :param brains: [required] Catalog brains from a previous search.
    :param range_start: Date, from which on events should be searched.
    :type range_start: Python datetime.
    :param range_end: Date, until which events should be searched.
    :type range_end: Python datetime
    :param limit: Number of items to be returned.
    :type limit: integer
    :returns: List of occurrence objects.
    :rtype: Occurrence objects

    """
    result = []
    for brain in brains:
        obj = brain.getObject()
        occurrences = [
            IEventAccessor(occ) for occ in
            IRecurrenceSupport(obj).occurrences(range_start, range_end)
        ]
        result += occurrences
    result.sort(key=lambda x: x.start)
    if limit is not None:
        result = result[:limit]
    return result

