# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from calendar import monthrange
from datetime import date
from datetime import datetime
from datetime import timedelta
from DateTime import DateTime
from persistent.dict import PersistentDict
from plone.app.event.interfaces import ISO_DATE_FORMAT
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IEventRecurrence
from plone.event.interfaces import IRecurrenceSupport
from plone.event.utils import default_timezone as fallback_default_timezone
from plone.event.utils import dt2int
from plone.event.utils import is_date
from plone.event.utils import is_datetime
from plone.event.utils import is_same_day
from plone.event.utils import is_same_time
from plone.event.utils import pydt
from plone.event.utils import validated_timezone
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time as orig_ulocalized_time
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import safe_callable
from zope.annotation.interfaces import IAnnotations
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.component.interfaces import ISite
from zope.deprecation import deprecate

import pytz
import six


DEFAULT_END_DELTA = 1  # hours
FALLBACK_TIMEZONE = 'UTC'

# Sync strategies
SYNC_NONE = 0
SYNC_KEEP_NEWER = 1
SYNC_KEEP_MINE = 2
SYNC_KEEP_THEIRS = 3

# Return modes for get_events
RET_MODE_BRAINS = 1
RET_MODE_OBJECTS = 2
RET_MODE_ACCESSORS = 3

# Map for ambiguous timezone abbreviations to their most common non-ambigious
# timezone name. E.g CST is ambiguous and is used for U.S./Canada Central
# Standard Time, Australian Central Standard Time, China Standard Time.
# TODO: incomplete map.
# TODO: do we need this at all or shouldn't we just fail with ambiguous
#       timezones?
replacement_zones = {
    'CET': 'Europe/Vienna',    # Central European Time
    'MET': 'Europe/Vienna',    # Middle European Time
    'EET': 'Europe/Helsinki',  # East European Time
    'WET': 'Europe/Lisbon',    # West European Time
}


# RETRIEVE EVENTS

def get_events(context, start=None, end=None, limit=None,
               ret_mode=RET_MODE_BRAINS, expand=False,
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

    :param expand: Expand the results to all occurrences (within a timeframe,
                   if given). With this option set to True, the resultset also
                   includes the event's recurrence occurrences and is sorted by
                   the start date.
                   Only available in ret_mode 2 (objects) and 3 (accessors).
    :type expand: boolean

    :param sort: Catalog index id to sort on.
    :type sort: string

    :param sort_reverse: Change the order of the sorting.
    :type sort_reverse: boolean

    :returns: Portal events, matching the search criteria.
    :rtype: catalog brains, event objects or IEventAccessor object wrapper,
            depending on ret_mode.
    """
    start, end = _prepare_range(context, start, end)

    query = {}
    query['object_provides'] = IEvent.__identifier__

    query.update(start_end_query(start, end))

    if 'path' not in kw:
        # limit to the current navigation root, usually (not always) site
        portal = getSite()
        navroot = getNavigationRootObject(context, portal)
        query['path'] = '/'.join(navroot.getPhysicalPath())
    else:
        query['path'] = kw['path']

    # Sorting
    # In expand mode we sort after calculation of recurrences again. But we
    # need to leave this sorting here in place, since no sort definition could
    # lead to arbitrary results when limiting with sort_limit.
    query['sort_on'] = sort
    if sort_reverse:
        query['sort_order'] = 'reverse'

    # cannot limit before resorting or expansion, see below

    query.update(kw)

    cat = getToolByName(context, 'portal_catalog')
    result = cat(**query)

    # unfiltered catalog results are already sorted correctly on brain.start
    # filtering on start/end requires a resort, see docstring below and
    # p.a.event.tests.test_base_module.TestGetEventsDX.test_get_event_sort
    if sort in ('start', 'end'):
        result = filter_and_resort(context, result,
                                   start, end,
                                   sort, sort_reverse)

        # Limiting a start/end-sorted result set is possible here
        # and provides an important optimization BEFORE costly expansion
        if limit:
            result = result[:limit]

    if ret_mode in (RET_MODE_OBJECTS, RET_MODE_ACCESSORS):
        if expand is False:
            result = [_obj_or_acc(it.getObject(), ret_mode) for it in result]
        else:
            result = expand_events(result, ret_mode, start, end, sort,
                                   sort_reverse)

    # Limiting a non-start-sorted result set can only happen here
    if limit:
        result = result[:limit]

    return result


def filter_and_resort(context, brains, start, end, sort, sort_reverse):
    """#114 sorting bug is fallout from a Products.DateRecurringIndex
    limitation. The index contains a set of start and end dates
    represented as integer: that allows valid slicing of searches.
    However the returned brains have a .start attribute which is
    the start DateTime of the *first* occurrence of an event.

    This results in mis-sorting of search results if the next occurrence
    of event B is after the next occurrence of event A, but the first
    occurrence of event B is *before* the first occurrence of event A.
    The catalog results sort that as B<A instead of A<B.

    This method works around that issue by extracting all occurrence
    start/end from the index, and then sorting on the actual next start/end.

    For ongoing events which have an occurrence starting in the past
    but ending in the future, the past start of that ongoing occurrence
    is selected, so this will show up right at the start of the result.

    :param context: [required] A context object.
    :type context: Content object

    :param brains: [required] catalog brains
    :type brains: catalog brains

    :param start: [required] min end datetime (sic!)
    :type start: Python datetime.

    :param end: [required] max start datetime (sic!)
    :type start: Python datetime.

    :param sort_reverse: Change the order of the sorting.
    :type sort_reverse: boolean

    :param sort: Which field to sort on
    :type sort: 'start' or 'end'

    :returns: catalog brains
    :rtype: catalog brains

    """
    _start = dt2int(start)  # index contains longint sets
    _end = dt2int(end)
    catalog = getToolByName(context, 'portal_catalog')
    items = []  # (start:int, occurrence:brain) pairs
    for brain in brains:
        # brain.start metadata reflects first occurrence.
        # instead, get all occurrence start/end from raw index
        idx = catalog.getIndexDataForRID(brain.getRID())
        _allstarts = sorted(idx['start'])
        _allends = sorted(idx['end'])
        # assuming (start, end) pairs belong together
        # assert(len(_allstarts) == len(_allends))
        _occ = six.moves.zip(_allstarts, _allends)
        if start:
            _occ = [(s, e) for (s, e) in _occ if e >= _start]
        if end:
            _occ = [(s, e) for (s, e) in _occ if s <= _end]
        if not _occ:
            continue
        if sort == 'start':
            # first start can be before filter window if end is in window
            _first = min([s for (s, e) in _occ])
        elif sort == 'end':
            _first = min([e for (s, e) in _occ])
        items.append((_first, brain))  # key on next start/end

    # sort brains by next start, discard sort key
    data = [x[1] for x in sorted(items, key=lambda x: x[0])]
    if sort_reverse:
        data.reverse()
    return data


def expand_events(events, ret_mode,
                  start=None, end=None,
                  sort=None, sort_reverse=None):
    """Expand to the recurrence occurrences of a given set of events.

    :param events: IEvent based objects or IEventAccessor object wrapper.

    :param ret_mode: Return type of search results. These options are
                     available:

                         * 2 (objects): Return results as IEvent and/or
                                        IOccurrence objects.
                         * 3 (accessors): Return results as IEventAccessor
                                          wrapper objects.
                     Option "1" (brains) is not supported.

    :type ret_mode: integer [2|3]

    :param start: Date, from which on events should be expanded.
    :type start: Python datetime.

    :param end: Date, until which events should be expanded.
    :type end: Python datetime

    :param sort: Object or IEventAccessor Attribute to sort on.
    :type sort: string

    :param sort_reverse: Change the order of the sorting.
    :type sort_reverse: boolean
    """
    assert(ret_mode is not RET_MODE_BRAINS)

    exp_result = []
    for it in events:
        obj = it.getObject() if getattr(it, 'getObject', False) else it
        if IEventRecurrence.providedBy(obj):
            occurrences = [_obj_or_acc(occ, ret_mode) for occ in
                           IRecurrenceSupport(obj).occurrences(start, end)]
        elif IEvent.providedBy(obj):
            occurrences = [_obj_or_acc(obj, ret_mode)]
        else:
            # No IEvent based object. Could come from a collection.
            continue
        exp_result += occurrences
    if sort:
        exp_result.sort(key=lambda x: _get_compare_attr(x, sort))
    if sort_reverse:
        exp_result.reverse()
    return exp_result


def _obj_or_acc(obj, ret_mode):
    """Return the content object or an IEventAccessor wrapper, depending on
    ret_mode. ret_mode 2 returns objects, ret_mode 3 returns IEventAccessor
    object wrapper. ret_mode 1 is not supported.
    """
    assert(ret_mode is not RET_MODE_BRAINS)
    if ret_mode == RET_MODE_OBJECTS:
        return obj
    elif ret_mode == RET_MODE_ACCESSORS:
        return IEventAccessor(obj)


def _get_compare_attr(obj, attr):
    """Return an compare attribute, supporting AT, DX and IEventAccessor
    objects.
    """
    val = getattr(obj, attr, None)
    if safe_callable(val):
        val = val()
    if isinstance(val, DateTime):
        val = pydt(val)
    return val


def construct_calendar(events, start=None, end=None):
    """Return a dictionary with dates in a given timeframe as keys and the
    actual occurrences for that date for building calendars.
    Long lasting events will occur on every day until their end.

    :param events: List of IEvent and/or IOccurrence objects, to construct a
                   calendar data structure from.
    :type events: list

    :param start: An optional start range date.
    :type start: Python datetime or date

    :param end: An optional start range date.
    :type end: Python datetime or date

    :returns: Dictionary with isoformat date strings as keys and event
              occurrences as values.
    :rtype: dict

    """
    if start:
        if is_datetime(start):
            start = start.date()
        assert is_date(start)
    if end:
        if is_datetime(end):
            end = end.date()
        assert is_date(end)

    cal = {}

    def _add_to_cal(cal_data, event, date):
        date_str = date.isoformat()
        if date_str not in cal_data:
            cal_data[date_str] = [event]
        else:
            cal_data[date_str].append(event)
        return cal_data

    for event in events:
        acc = IEventAccessor(event)
        start_date = acc.start.date()
        end_date = acc.end.date()

        # day span between start and end + 1 for the initial date
        range_days = (end_date - start_date).days + 1
        for add_day in range(range_days):
            next_start_date = start_date + timedelta(add_day)  # initial = 0

            # avoid long loops
            if start and end_date < start:
                break  # if the date is completly outside the range
            if start and next_start_date < start:
                continue  # if start_date is outside but end reaches into range
            if end and next_start_date > end:
                break  # if date is outside range

            _add_to_cal(cal, event, next_start_date)
    return cal


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
    tz = default_timezone(context, as_tzinfo=True)
    start = pydt(start, missing_zone=tz)
    if is_date(end):
        # set range_end to the next day, time will be 0:00
        # so the whole previous day is also used for search
        end = end + timedelta(days=1)
    end = pydt(end, missing_zone=tz)
    return start, end


def start_end_query(start, end):
    """Make a catalog query out of start and end dates.
    """
    query = {}
    if start:
        # All events from start date ongoing:
        # The minimum end date of events is the date from which we search.
        query['end'] = {'query': start, 'range': 'min'}
    if end:
        # All events until end date:
        # The maximum start date must be the date until we search.
        query['start'] = {'query': end, 'range': 'max'}
    return query


# TIMEZONE HANDLING

def default_timezone(context=None, as_tzinfo=False):
    """Return the timezone from the portal or user.

    :param context: Optional context. If not given, the current Site is used.
    :type context: Content object

    :param as_tzinfo: Return the default timezone as tzinfo object.
    :type as_tzinfo: boolean

    :returns: Timezone identifier or tzinfo object.
    :rtype: string or tzinfo object

    """
    # TODO: test member timezone
    if not context:
        context = getSite()

    membership = getToolByName(context, 'portal_membership', None)
    if membership and not membership.isAnonymousUser():  # user not logged in
        member = membership.getAuthenticatedMember()
        member_timezone = member.getProperty('timezone', None)
        if member_timezone:
            info = pytz.timezone(member_timezone)
            return info if as_tzinfo else info.zone

    reg_key = 'plone.portal_timezone'
    registry = getUtility(IRegistry)
    portal_timezone = registry.get(reg_key, None)

    # fallback to what plone.event is doing
    if not portal_timezone:
        portal_timezone = fallback_default_timezone()

    # Change any ambiguous timezone abbreviations to their most common
    # non-ambigious timezone name.
    if portal_timezone in replacement_zones.keys():
        portal_timezone = replacement_zones[portal_timezone]
    portal_timezone = validated_timezone(portal_timezone, FALLBACK_TIMEZONE)

    if as_tzinfo:
        return pytz.timezone(portal_timezone)

    return portal_timezone


def localized_now(context=None):
    """Return the current datetime localized to the default timezone.

    :param context: Context object.
    :type context: Content object
    :returns: Localized current datetime.
    :rtype: Python datetime

    """
    if not context:
        context = getSite()
    tzinfo = default_timezone(context=context, as_tzinfo=True)
    return datetime.now(tzinfo).replace(microsecond=0)


def localized_today(context=None):
    """Return the current date localized to the default timezone.

    :param context: Context object.
    :type context: Content object
    :returns: Localized current date.
    :rtype: Python date

    """
    now = localized_now(context)
    return date(now.year, now.month, now.day)


# DATETIME HELPERS

def first_weekday():
    """Returns the number of the first Weekday in a Week, as defined in
    the registry. 0 is Monday, 6 is Sunday, as expected by Python's datetime.

    PLEASE NOTE: strftime %w interprets 0 as Sunday unlike the calendar module!

    :returns: Index of first weekday [0(Monday)..6(Sunday)]
    :rtype: integer

    """
    reg_key = 'plone.first_weekday'
    registry = getUtility(IRegistry)
    first_wd = registry.get(reg_key, None)

    if not first_wd:
        return 0
    else:
        return int(first_wd)


def wkday_to_mon0(day):
    """Converts an integer weekday number to a representation where Monday is 0
    and Sunday is 6 (the datetime default), from a representation where Sunday
    is 0, Monday is 1 and Saturday is 6 (the strftime behavior).

    :param day: The weekday number [0(Sunday)..6]
    :type day: integer

    :returns: The weekday number [0(Monday)..6]
    :rtype: integer

    """
    if day == 0:
        return 6
    else:
        return day - 1


def wkday_to_mon1(day):
    """Converts an integer weekday number to a representation where Monday is
    1, Saturday is 6 and Sunday is 0 (the strftime behavior), from a
    representation where Monday is 0 and Sunday is 6 (the datetime default).

    :param day: The weekday number [0(Monday)..6]
    :type day: integer

    :returns: The weekday number [0(Sunday)..6]
    :rtype: integer

    """
    if day == 6:
        return 0
    else:
        return day + 1


def DT(dt, exact=False):
    """Return a Zope DateTime instance from a Python datetime instance.

    :param dt: Python datetime, Python date, Zope DateTime instance or string.
    :param exact: If True, the resolution goes down to microseconds. If False,
                  the resolution are seconds. Defaul is False.
    :type exact: Boolean
    :returns: Zope DateTime
    :rtype: Zope DateTime

    """

    def _adjust_DT(DT, exact):
        if exact:
            ret = DT
        else:
            ret = DateTime(
                DT.year(),
                DT.month(),
                DT.day(),
                DT.hour(),
                DT.minute(),
                int(DT.second()),
                DT.timezone()
            )
        return ret

    tz = default_timezone(getSite())
    ret = None
    if is_datetime(dt):
        zone_id = getattr(dt.tzinfo, 'zone', tz)
        tz = validated_timezone(zone_id, tz)
        second = dt.second
        if exact:
            second += dt.microsecond / 1000000.0
        ret = DateTime(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, second,
            tz
        )
    elif is_date(dt):
        ret = DateTime(dt.year, dt.month, dt.day, 0, 0, 0, tz)
    elif isinstance(dt, DateTime):
        # No timezone validation. DateTime knows how to handle it's zones.
        ret = _adjust_DT(dt, exact=exact)
    else:
        # Try to convert by DateTime itself
        ret = _adjust_DT(DateTime(dt), exact=exact)
    return ret


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

    ret = pytz.timezone(default_timezone(context)).localize(dateobj)
    return ret


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
    if not context:
        context = getSite()
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
        end = dt_end_of_day(now + timedelta(days=6))

    elif mode == 'day' or mode == 'today':
        if not dt:
            dt = now  # show today
        start = dt_start_of_day(dt)
        end = dt_end_of_day(dt)

    elif mode == 'week':
        if not dt:
            dt = now  # show this week
        wkd = dt.weekday()
        first = first_weekday()

        if first <= wkd:
            delta = wkd - first  # >= 0
        if first > wkd:
            delta = wkd + 7 - first  # > 0

        start = dt_start_of_day(dt - timedelta(days=delta))
        end = dt_end_of_day(start + timedelta(days=6))

    elif mode == 'month':
        if not dt:
            dt = now  # show this month
        year = dt.year
        month = dt.month
        last_day = monthrange(year, month)[1]  # (wkday, days)
        start = dt_start_of_day(datetime(year, month, 1))
        end = dt_end_of_day(datetime(year, month, last_day))

    return start, end


# DISPLAY HELPERS

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
        'whole_day'  - whole day events
        'open_end'   - events without end time

    :param occurrence: Event or occurrence object.
    :type occurrence: IEvent, IOccurrence or IEventAccessor based object.
    :returns: Dictionary with date strings.
    :rtype: dict


    The behavior os ulocalized_time() with time_only is odd.
    Setting time_only=False should return the date part only and *not*
    the time

    NOTE: these tests are not run, but serve as documentation.
    TODO: remove.
    >>> from DateTime import DateTime
    >>> start = DateTime(2010,3,16,14,40)
    >>> from zope.component.hooks import getSite
    >>> site = getSite()
    >>> ulocalized_time(start, False,  time_only=True, context=site)
    u'14:40'
    >>> ulocalized_time(start, False,  time_only=False, context=site)
    u'14:40'
    >>> ulocalized_time(start, False,  time_only=None, context=site)
    u'16.03.2010'

    """
    if IEventAccessor.providedBy(occurrence):
        acc = occurrence
        occurrence = occurrence.context
    else:
        acc = IEventAccessor(occurrence)

    if acc.start is None or acc.end is None:
        # Eventually optional start/end dates from a potentially Event.
        return None

    # this needs to separate date and time as ulocalized_time does
    DT_start = DT(acc.start)
    DT_end = DT(acc.end)
    start_date = ulocalized_time(
        DT_start, long_format=False, time_only=None, context=occurrence
    )
    start_time = ulocalized_time(
        DT_start, long_format=False, time_only=True, context=occurrence
    )
    end_date = ulocalized_time(
        DT_end, long_format=False, time_only=None, context=occurrence
    )
    end_time = ulocalized_time(
        DT_end, long_format=False, time_only=True, context=occurrence
    )

    same_day = is_same_day(acc.start, acc.end)
    same_time = is_same_time(acc.start, acc.end)

    # set time fields to None for whole day events
    if acc.whole_day:
        start_time = end_time = None
    if acc.open_end:
        end_time = None

    start_iso = acc.whole_day and acc.start.date().isoformat()\
        or acc.start.isoformat()
    end_iso = acc.whole_day and acc.end.date().isoformat()\
        or acc.end.isoformat()

    return dict(
        # Start
        start_date=start_date,
        start_time=start_time,
        start_iso=start_iso,

        # End
        end_date=end_date,
        end_time=end_time,
        end_iso=end_iso,

        # Meta
        same_day=same_day,
        same_time=same_time,
        whole_day=acc.whole_day,
        open_end=acc.open_end,
    )


@deprecate('date_speller is no longer supported, use spell_date instead.')
def date_speller(context, dt):
    return spell_date(dt, context)


def spell_date(dt, translation_context=None):
    """Return a dictionary with localized and readable formatted date parts.

    """
    if not translation_context:
        translation_context = getSite()

    dt = DT(dt)
    util = getToolByName(translation_context, 'translation_service')
    dom = 'plonelocales'

    def zero_pad(num):
        return '%02d' % num

    date_dict = dict(
        year=dt.year(),

        month=dt.month(),
        month2=zero_pad(dt.month()),
        month_name=util.translate(
            util.month_msgid(dt.month()),
            domain=dom, context=translation_context
        ),
        month_abbr=util.translate(
            util.month_msgid(dt.month(), 'a'),
            domain=dom, context=translation_context
        ),

        week=dt.week(),
        wkday=dt.dow(),
        wkday_name=util.translate(
            util.day_msgid(dt.dow()),
            domain=dom, context=translation_context
        ),
        wkday_abbr=util.translate(
            util.day_msgid(dt.dow(), 's'),
            domain=dom, context=translation_context
        ),

        day=dt.day(),
        day2=zero_pad(dt.day()),

        hour=dt.hour(),
        hour2=zero_pad(dt.hour()),

        minute=dt.minute(),
        minute2=zero_pad(dt.minute()),

        second=dt.second(),
        second2=zero_pad(dt.second())
    )
    return date_dict


def default_start(context=None):
    """Return the default start as python datetime for prefilling forms.

    :returns: Default start datetime.
    :rtype: Python datetime

    """
    now = localized_now(context=context)
    return now.replace(minute=0, second=0, microsecond=0)


def default_end(context=None):
    """Return the default end as python datetime for prefilling forms.

    :returns: Default end datetime.
    :rtype: Python datetime

    """
    return default_start(context=context) + timedelta(hours=DEFAULT_END_DELTA)


# General utils
# TODO: Better fits to CMFPlone. (Taken from CMFPlone's new syndication tool)

class AnnotationAdapter(object):
    """Abstract Base Class for an annotation storage.

    If the annotation wasn't set, it won't be created until the first attempt
    to set a property on this adapter.
    So, the context doesn't get polluted with annotations by accident.

    """
    ANNOTATION_KEY = None

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self._data = annotations.get(self.ANNOTATION_KEY, None)

    def __setattr__(self, name, value):
        if name in ('context', '_data', 'ANNOTATION_KEY'):
            self.__dict__[name] = value
        else:
            if self._data is None:
                self._data = PersistentDict()
                annotations = IAnnotations(self.context)
                annotations[self.ANNOTATION_KEY] = self._data
            self._data[name] = value

    def __getattr__(self, name):
        return self._data.get(name, None) if self._data else None


def find_context(context, viewname=None, iface=None,
                 as_url=False, append_view=True):
    """Find the next context with a given view name or interface, up in the
    content tree, starting from the given context. This might not be the
    IPloneSiteRoot, but another subsite.

    :param context: The context to start the search from.
    :param viewname: (optional) The name of a view which a context should have
                     configured as defaultView.
    :param iface: (optional) The interface, the context to search for should
                  implement.
    :param as_url: (optional) Return the URL of the context found.
    :param append_view: (optional) In case of a given viewname and called with
                        as_url, append the viewname to the url, if the context
                        hasn't configured it as defaultView. Otherwise ignore
                        this parameter.
    :returns: A context with the given view name, inteface or ISite root.
    """
    context = aq_inner(context)
    ret = None
    if viewname and context.defaultView() == viewname\
       or iface and iface.providedBy(context)\
       or IPloneSiteRoot.providedBy(context):
        # Search for viewname or interface but stop at IPloneSiteRoot
        ret = context
    else:
        ret = find_context(aq_parent(context), viewname=viewname, iface=iface,
                           as_url=False, append_view=False)
    if as_url:
        url = ret.absolute_url()
        if viewname and append_view and ret.defaultView() != viewname:
            url = '%s/%s' % (url, viewname)
        return url
    return ret


def find_site(context, as_url=False):
    return find_context(context, iface=ISite, as_url=as_url)


def find_ploneroot(context, as_url=False):
    return find_context(context, iface=IPloneSiteRoot, as_url=as_url)


def find_navroot(context, as_url=False):
    return find_context(context, iface=INavigationRoot, as_url=as_url)


def find_event_listing(context, as_url=False):
    return find_context(context, viewname='event_listing', iface=ISite,
                        as_url=as_url, append_view=True)


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
