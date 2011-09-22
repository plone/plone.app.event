import pytz
from datetime import datetime
from datetime import timedelta

from zope.component import getUtility

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from plone.event.utils import default_timezone as fallback_default_timezone

from plone.app.event.interfaces import IEvent
from plone.app.event.interfaces import IEventSettings


def default_end_date():
    """
    """
    return DateTime(datetime.now() + timedelta(hours=1))

def default_timezone(context=None):
    """ Retrieve the timezone from the portal or user.

    TODO: test member timezone
    """

    if context:
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


def whole_day_handler(obj, event):
    """ For whole day events only, set start time to 0:00:00 and end time to
        23:59:59
    """

    if not obj.whole_day:
        return
    startDate = obj.startDate.toZone(obj.timezone)
    startDate = startDate.Date() + ' 0:00:00 ' + startDate.timezone()
    endDate = obj.endDate.toZone(obj.timezone)
    endDate = endDate.Date() + ' 23:59:59 ' + endDate.timezone()
    obj.setStartDate(DateTime(startDate))
    obj.setEndDate(DateTime(endDate))
    obj.reindexObject()  # reindex obj to store upd values in catalog


@property
def first_weekday(self):
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
        return first_wd


def get_portal_events(context, range_start=None, range_end=None, **kw):
    """ Return all events as catalog brains, possibly within a given
    timeframe.

    """
    query = {}
    query['object_provides'] = IEvent.__identifier__
    if range_start:
        query['start'] = {'query': range_start, 'range': 'max'}
    if range_end:
        query['end'] = {'query': range_end, 'range': 'min'}
    query['sort_on'] = 'start'
    query.update(kw)

    cat = getToolByName(context, 'portal_catalog')
    result = cat(**query)
    return result


def get_events_by_date(context, range_start=None, range_end=None, **kw):
    """ Return a dictionary with dates in a given timeframe as keys and
    the actual events for that date.

    """
    events = get_portal_events(context, range_start, range_end, **kw)
    # TODO: catalog brains are timezone'd. shouldn't they be in UTC?
    ## example catalog entry: 2011/09/16 16:35:00 Brazil/West
    events_by_date = {}
    for event in events:
        obj = event.getObject()
        occurrences = obj.occurrences(range_start, range_end)
        for occ in occurrences:
            start_str = datetime.strftime(occ.start_date, '%Y-%m-%d')
            # TODO: add span_events parameter to include dates btw. start
            # and end also. for events lasting longer than a day...
            if start_str not in events_by_date:
                events_by_date[start_str] = [event]
            else:
                events_by_date[start_str].append(event)
        return events_by_date
