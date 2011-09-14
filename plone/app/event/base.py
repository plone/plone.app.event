import pytz
from datetime import datetime
from datetime import timedelta

from zope.component import getUtility

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from plone.event.utils import default_timezone as fallback_default_timezone

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
