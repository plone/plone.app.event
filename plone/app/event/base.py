import pytz
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.i18nl10n import ulocalized_time as orig_ulocalized_time
from datetime import date
from datetime import datetime
from datetime import timedelta
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.event.interfaces import IEvent, IEventRecurrence
from plone.event.interfaces import IRecurrenceSupport, IEventAccessor
from plone.event.utils import default_timezone as fallback_default_timezone
from plone.event.utils import pydt
from plone.event.utils import validated_timezone
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implements, Interface

from plone.app.event.interfaces import ICalendarLinkbase
from plone.app.event.interfaces import IEventSettings
from plone.app.event.interfaces import ISO_DATE_FORMAT


DEFAULT_END_DELTA = 1 # hours
FALLBACK_TIMEZONE = 'UTC'


class CalendarLinkbase(object):
    """Default adapter to retrieve a base url for a calendar view. The methods
    in this default implementation return the @@search view as calendar view.

    """
    adapts(Interface)
    implements(ICalendarLinkbase)

    def __init__(self, context):
        self.context = context
        portal = getSite()
        self.navroot = getNavigationRootObject(context, portal)
        self.navroot_url = self.navroot.absolute_url()

    def date_events_url(self, date, path=None):
        """Get a URL to retrieve all events on a given day.

        :param date: The date to search events for in isoformat (ISO 8601,
                    YYYY-MM-DD).
        :type date: string
        
        :param path: Events context path (optional).
        :type path: string

        :returns: URL linking to a page with events on the given date.
        :rtype: string

        """
        url = '%s/@@search?advanced_search=True&'\
              'start.query:record:list:date=%s+23:59:59&'\
              'start.range:record=max&'\
              'end.query:record:list:date=%s+00:00:00&'\
              'end.range:record=min&'\
              'object_provides=plone.event.interfaces.IEvent'\
              % (self.navroot_url, date, date)
        return url

    def past_events_url(self):
        """Get a URL to retrieve past events.

        :returns: URL linking to a page with past events.
        :rtype: string

        """
        # take care dont use self.portal here since support
        # of INavigationRoot features likely will breake #9246 #9668
        url = None
        navigation_root_url = self.navroot_url
        events_folder = self._events_folder()
        if (events_folder and
            'aggregator' in events_folder.objectIds() and
            'previous' in events_folder['aggregator'].objectIds()):
            url = '%s/events/aggregator/previous' % navigation_root_url
        elif (events_folder and 'previous' in events_folder.objectIds()):
            url = '%s/events/previous' % navigation_root_url
        else:
            # show all past events
            now = datetime.utcnow().strftime('%Y-%m-%d+%H:%M')
            url = '%s/@@search?advanced_search=True'\
                  '&end.query:record:list:date=%s'\
                  '&end.range:record=max'\
                  '&object_provides=plone.event.interfaces.IEvent'\
                   % (navigation_root_url, now)
        return url

    def next_events_url(self):
        """Get a URL to retrieve upcoming events.

        :returns: URL linking to a page with upcoming events.
        :rtype: string

        """
        navigation_root_url = self.navroot_url
        url = None
        if self._events_folder():
            url = '%s/events' % navigation_root_url
        else:
            # search all events which are in the future or ongoing
            now = datetime.utcnow().strftime('%Y-%m-%d+%H:%M')
            url = '%s/@@search?advanced_search=True'\
                  '&start.query:record:list:date=%s'\
                  '&start.range:record=min'\
                  '&end.query:record:list:date=%s'\
                  '&end.range:record=min'\
                  '&object_provides=plone.event.interfaces.IEvent'\
                   % (navigation_root_url, now, now)
        return url

    def all_events_url(self):
        """Get a URL to retrieve all events.

        :returns: URL linking to a page with events on the given date.
        :rtype: string

        """
        navigation_root_url = self.navroot_url
        url = None
        if self._events_folder():
            url = '%s/events' % navigation_root_url
        else:
            # search all events which are in the future or ongoing
            url = '%s/@@search?advanced_search=True'\
                  '&object_provides=plone.event.interfaces.IEvent'\
                   % navigation_root_url
        return url

    def _events_folder(self):
        navroot = self.navroot
        return 'events' in navroot and navroot['events'] or None



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

    if range_start:
        # All events from range_start ongoing:
        # The minimum end date must be the date from which we search.
        query['end'] = {'query': range_start, 'range': 'min'}
    if range_end:
        # All events until range_end:
        # The maximum start date must be the date until we search.
        query['start'] = {'query': range_end, 'range': 'max'}
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

        if IEventRecurrence.providedBy(obj):
            occurrences = IRecurrenceSupport(obj).occurrences(
                range_start, range_end)
        else:
            occurrences = [obj]

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
    ret = None
    if isinstance(dt, datetime):
        zone_id = getattr(dt.tzinfo, 'zone', tz)
        tz = validated_timezone(zone_id, tz)
        ret = DateTime(dt.year, dt.month, dt.day,\
                        dt.hour, dt.minute, dt.second, tz)
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
