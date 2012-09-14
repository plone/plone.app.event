import pytz
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import i18nl10n
from Products.CMFPlone.i18nl10n import ulocalized_time as orig_ulocalized_time
from datetime import date
from datetime import datetime
from datetime import timedelta
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.event.interfaces import IEvent, IRecurrenceSupport, IEventAccessor
from plone.event.utils import default_timezone as fallback_default_timezone
from plone.event.utils import pydt
from plone.event.utils import validated_timezone
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component.hooks import getSite

from plone.app.event.interfaces import IEventSettings
from plone.app.event.interfaces import ISO_DATE_FORMAT


DEFAULT_END_DELTA = 1 # hours
FALLBACK_TIMEZONE = 'UTC'

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

    membership = getToolByName(context, 'portal_membership')
    if not membership.isAnonymousUser(): # the user has not logged in
        member = membership.getAuthenticatedMember()
        member_timezone = member.getProperty('timezone', None)
        if member_timezone:
            return pytz.timezone(member_timezone).zone

    controlpanel = getUtility(IRegistry).forInterface(IEventSettings,
                                                    prefix="plone.app.event")
    portal_timezone = controlpanel.portal_timezone

    # fallback to what plone.event is doing
    if not portal_timezone:
        return fallback_default_timezone()

    return validated_timezone(portal_timezone, FALLBACK_TIMEZONE)


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


def get_portal_events(context, range_start=None, range_end=None, limit=None,
                      sort='start', sort_reverse=False, **kw):
    """Return all events as catalog brains, possibly within a given
    timeframe.

    :param context: [required] A context object.
    :type context: Content object
    :param range_start: Date, from which on events should be searched.
    :type range_start: Python datetime.
    :param range_end: Date, until which events should be searched.
    :type range_end: Python datetime
    :param limit: Number of items to be returned.
    :type limit: integer
    :param sort: Catalog index id to sort on.
    :type sort: string
    :param sort_reverse: Change the order of the sorting.
    :type sort_reverse: boolean
    :returns: Portal events, matching the search criteria.
    :rtype: catalog brains

    """
    range_start, range_end = _prepare_range(context, range_start, range_end)

    query = {}
    query['object_provides'] = IEvent.__identifier__

    if 'path' not in kw:
        # limit to the current navigation root, usually (not always) site
        portal = getSite()
        navroot = getNavigationRootObject(context, portal)
        query['path'] = navroot.getPhysicalPath()

    # TODO: revisit and correct
    if range_start:
        query['end'] = {'query': DT(range_start), 'range': 'min'}
    if range_end:
        query['end'] = {'query': DT(range_end), 'range': 'max'}
    query['sort_on'] = sort
    if sort_reverse: query['sort_order'] = 'reverse'

    query.update(kw)

    cat = getToolByName(context, 'portal_catalog')
    if limit:
        query['sort_limit'] = limit
        result = cat(**query)[:limit]
    else:
        result = cat(**query)
    return result


def get_occurrences_by_date(context, range_start=None, range_end=None, **kw):
    """Return a dictionary with dates in a given timeframe as keys and the
    actual occurrences for that date for building calendars.

    :param context: [required] A context object.
    :type context: Content object
    :param range_start: Date, from which on events should be searched.
    :type range_start: Python datetime.
    :param range_end: Date, until which events should be searched.
    :type range_end: Python datetime
    :returns: Dictionary with dates keys and occurrences as values.
    :rtype: dict

    """
    range_start, range_end = _prepare_range(context, range_start, range_end)

    events = get_portal_events(context, range_start, range_end, **kw)
    events_by_date = {}
    for event in events:
        obj = event.getObject()

        # TODO: this returns only occurrences of recurring events.
        #       non-recurring events won't have any hits here.
        #       Maybe provide an adapter for non-recurring events (dx+at) which
        #       return just start and end datetime
        occurrences = IRecurrenceSupport(obj).occurrences(
            range_start, range_end)
        for occ in occurrences:
            accessor = IEventAccessor(occ)
            start_str = datetime.strftime(accessor.start, '%Y-%m-%d')
            # TODO: add span_events parameter to include dates btw. start
            # and end also. for events lasting longer than a day...
            if start_str not in events_by_date:
                events_by_date[start_str] = [occ]
            else:
                events_by_date[start_str].append(occ)
    return events_by_date


def get_occurrences(context, brains, range_start=None, range_end=None,
                    limit=None):
    """Returns a flat list of occurrence objects from a given result of a
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

    >>> from plone.app.event.base import get_occurrences
    >>> import datetime
    >>> get_occurrences(object, [], range_start=datetime.datetime.today())
    []

    """
    result = []
    start = localized_now() if (range_start is None) else range_start
    for brain in brains:
        obj = brain.getObject()
        occurrences = [
            IEventAccessor(occ) for occ in
            IRecurrenceSupport(obj).occurrences(start, range_end)
        ]
        result += occurrences
    result.sort(key=lambda x: x.start)
    if limit is not None:
        result = result[:limit]
    return result


def DT(dt):
    """Return a Zope DateTime instance from a Python datetime instance.

    :param dt: Python datetime instance.
    :type dt: Python datetime
    :returns: Zope DateTime
    :rtype: Zope DateTime

    """
    tz = default_timezone(getSite())
    if isinstance(dt, datetime):
        zone_id = getattr(dt.tzinfo, 'zone', tz)
        tz = validated_timezone(zone_id, tz)
        return DateTime(dt.year, dt.month, dt.day,\
                        dt.hour, dt.minute, dt.second, tz)
    elif isinstance(dt, date):
        return DateTime(dt.year, dt.month, dt.day, 0, 0, 0, tz)
    elif isinstance(dt, DateTime):
        # No timezone validation. DateTime knows how to handle it's zones.
        return dt
    else:
        return None


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
    if isinstance(end, date):
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


# Workaround for buggy strftime with timezone handling in DateTime.
# See: https://github.com/collective/plone.app.event/pull/47
# TODO: should land in CMFPlone or fixed in DateTime.
_strftime = lambda v, fmt: pydt(v).strftime(fmt)

class PatchedDateTime(DateTime):
    def strftime(self, fmt):
        return _strftime(self, fmt)

def ulocalized_time(time, *args, **kwargs):
    """Corrects for DateTime bugs doing wrong thing with timezones"""
    wrapped_time = PatchedDateTime(time)
    return orig_ulocalized_time(wrapped_time, *args, **kwargs)
