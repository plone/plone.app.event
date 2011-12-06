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

from plone.app.event.dx.interfaces import IDXEventRecurrence


def default_end_date():
    """
    """
    return DateTime(datetime.now() + timedelta(hours=1))

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

def prepare_range(context, start, end):
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

def get_portal_events(context, range_start=None, range_end=None, limit=None,
                      **kw):
    """ Return all events as catalog brains, possibly within a given
    timeframe.

    """
    range_start, range_end = prepare_range(context, range_start, range_end)

    query = {}
    query['object_provides'] = IEvent.__identifier__

    if 'path' not in kw:
        # always limit to the current portal root
        # TODO: is there a better method to get portal/navigation root's path
        #       without having to have the request available?
       query['path'] = '/'.join(getSite().getPhysicalPath())

    if range_start:
        query['start'] = {'query': DT(range_start), 'range': 'min'}
    if range_end:
        query['end'] = {'query': DT(range_end), 'range': 'max'}
    query['sort_on'] = 'start'

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
    range_start, range_end = prepare_range(context, range_start, range_end)

    events = get_portal_events(context, range_start, range_end, **kw)
    events_by_date = {}
    for event in events:
        obj = event.getObject()

        if IDXEventRecurrence.providedBy(obj):
            # Adapt obj to provide correct behavior
            # Import here to avoid circular imports
            # (dx/behaviors imports localized_now from here)
            from plone.app.event.dx.behaviors import IEventRecurrence
            obj = IEventRecurrence(obj)

        occurrences = obj.occurrences(range_start, range_end)
        for occ in occurrences:
            # occ: (start, end)
            start_str = datetime.strftime(occ[0], '%Y-%m-%d')
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

    >>>

    """

    if isinstance(dt, datetime):
        return DateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.tzinfo.zone)
    elif isinstance(dt, date):
        return DateTime(dt.year, dt.month, dt.day, 0, 0, 0, dt.tzinfo.zone)
    elif isinstance(dt, DateTime):
        return dt
    else:
        return None


### ARE THESE NEEDED?

def localized_now(context=None):
    if not context: context = getSite()
    return datetime.now(default_tzinfo(context))

def localized_today(context=None):
    now = localized_now(context)
    return date(now.year, now.month, now.day)

def dt_from_brain(datestr):
    """ Return python datetime instance from a catalog brain's date string.

    %Y/%m/%d %H:%M:%S TZINFO
    Since strptime doesn't handle pytz zones very well, we need to bypass
    this limitation.

    """
    # TODO: file a bug for strptime pytz names handling.

    start_parts = datestr.split(' ')
    start = datetime.strptime(' '.join(start_parts)[0:2], '%Y/%m/%d %H:%M:%S')
    tz = pytz.timezone(start_parts[2])
    start = tz.localize(start) # convert naive date to event's zone

def dt_to_zone(dt, tzstring):
    """ Return a datetime instance converted to the timezone given by the
    string.

    """
    return dt.astimezone(pytz.timezone(tzstring))
