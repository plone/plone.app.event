import pytz
from datetime import datetime
from datetime import date
from datetime import timedelta

from zope.component import getUtility
from zope.component.hooks import getSite
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from plone.event.utils import default_timezone as fallback_default_timezone
from plone.event.utils import pydt
from plone.app.event.interfaces import IEvent
from plone.app.event.interfaces import IEventSettings
from plone.app.event.interfaces import IRecurrence

DEFAULT_END_DELTA = 1 # hours

def default_end_dt():
    """ Return the default end as python datetime for prefilling forms.

    >>> from datetime import timedelta
    >>> from plone.app.event.base import default_end_dt
    >>> from plone.app.event.base import localized_now
    >>> assertTrue(default_end_dt() - timedelta(hours=DEFAULT_END_DELTA) ==
    ...            localized_now())
    """
    return localized_now() + timedelta(hours=DEFAULT_END_DELTA)


def default_end_DT():
    """ Return the default end as Zope DateTime for prefilling forms.

    >>> from DateTime import DateTime
    >>> from plone.app.event.base import default_end_DT
    >>> from plone.app.event.base import localized_now
    >>> from plone.app.event.base import DT
    >>> DTE = default_end_DT()
    >>> DTN = DT(localized_now)

    TODO: only True when not run around midnight.
    >>> assertTrue(DTE.year() == DTN.year() and
    ...            DTE.month() == DTN.month() and
    ...            DTE.day() == DTN.day() and
    ...            DTE.hour() == DTN.hour() + 1 and
    ...            DTE.minute() == DTN.minute())
    """
    return DT(default_end_dt())


def default_timezone(context=None):
    """ Retrieve the timezone from the portal or user.

    TODO: test member timezone
    """
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

    # following statement ensures, that timezone is a valid pytz zone
    return pytz.timezone(portal_timezone).zone


def default_tzinfo(context=None):
    """ Return the default timezone as tzinfo instance.
    """
    return pytz.timezone(default_timezone(context))


def first_weekday():
    """ Returns the number of the first Weekday in a Week, as defined in
    the registry.
    0 is Monday, 6 is Sunday, as expected by python's datetime.

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
    """ Return all events as catalog brains, possibly within a given
    timeframe.

    """
    range_start, range_end = _prepare_range(context, range_start, range_end)

    query = {}
    query['object_provides'] = IEvent.__identifier__

    if 'path' not in kw:
        # always limit to the current portal root
        # TODO: is there a better method to get portal/navigation root's path
        #       without having to have the request available?
        #query['path'] = '/'.join(getSite().getPhysicalPath())
        urltool = getToolByName(context, "portal_url")
        query['path'] = urltool.getPortalObject().getPhysicalPath()

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


def get_events_by_date(context, range_start=None, range_end=None, **kw):
    """ Return a dictionary with dates in a given timeframe as keys and
    the actual events for that date.

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
        occurrences = IRecurrence(obj).occurrences(range_start, range_end)
        for start, end in occurrences:
            start_str = datetime.strftime(start, '%Y-%m-%d')
            # TODO: add span_events parameter to include dates btw. start
            # and end also. for events lasting longer than a day...
            if start_str not in events_by_date:
                events_by_date[start_str] = [event]
            else:
                events_by_date[start_str].append(event)
    return events_by_date


def DT(dt):
    """ Return a DateTime instance from a python datetime instance.

    @param dt: python datetime instance

    >>> from plone.app.event.base import DT
    >>> from datetime import datetime
    >>> pdt = datetime(2011, 11, 23)
    >>> from DateTime import DateTime
    >>> zDT = DateTime(2011, 11, 23)
    >>> zDT == DT(pdt)
    True

    """

    tz = default_timezone(getSite())
    if isinstance(dt, datetime):
        tz = dt.tzname() or tz
        return DateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, tz)
    elif isinstance(dt, date):
        return DateTime(dt.year, dt.month, dt.day, 0, 0, 0, tz)
    elif isinstance(dt, DateTime):
        return dt
    else:
        return None


def localized_now(context=None):
    if not context: context = getSite()
    return datetime.now(default_tzinfo(context))


def localized_today(context=None):
    now = localized_now(context)
    return date(now.year, now.month, now.day)


def _prepare_range(context, start, end):
    """ Prepare a date-range to contain timezone info and set end to next day,
    if end is a date.

    """
    tz = default_tzinfo(context)
    start = pydt(start, missing_zone=tz)
    if isinstance(end, date):
        # set range_end to the next day, time will be 0:00
        # so the whole previous day is also used for search
        end = end + timedelta(days=1)
    end = pydt(end, missing_zone=tz)
    return start, end
