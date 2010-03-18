"""
Display helper methods for showing whole-day or same-day events
"""

from Products.CMFPlone.i18nl10n import ulocalized_time
from plone.app.event.utils import rfc2445dt

def isSameDay(event):
    return event.start().year() == event.end().year() and \
           event.start().month() == event.end().month() and \
           event.start().day() == event.end().day()

def isSameTime(event):
    return event.start().time == event.end().time


def toDisplay(event):
    """ Return dict containing pre-calculated information for
        building a <start>-<end> date string. Keys are
       'start_date' - date string of the start date
       'start_time' - time string of the start date
       'end_date' - date string of the end date
       'end_time' - time string of the end date
       'same_day' - event ends on the same day
    """

    # The behavior os ulocalized_time() with time_only is odd. Setting time_only=False
    # should return the date part only and *not* the time
    #
    # ulocalized_time(event.start(), False,  time_only=True, context=event)
    # u'14:40'
    # ulocalized_time(event.start(), False,  time_only=False, context=event)
    # u'14:40'
    # ulocalized_time(event.start(), False,  time_only=None, context=event)
    # u'16.03.2010'

    start_date = ulocalized_time(event.start(), False, time_only=None, context=event)
    end_date = ulocalized_time(event.end(), False, time_only=None, context=event)
    start_time = ulocalized_time(event.start(), False, time_only=True, context=event)
    end_time = ulocalized_time(event.end(), False, time_only=True, context=event)
    same_day = isSameDay(event)
    same_time = isSameTime(event)

    # set time fields to None for whole day events
    if event.getWholeDay():
        start_time = end_time = None

    return  dict(start_date=start_date,
                 start_time=start_time,
                 end_date=end_date,
                 end_time=end_time,
                 same_day=same_day,
                 same_time=same_time)


def _dateForWholeDay(dt):
    """ Replacement for rfc2445dt() for events lasting whole day in
        order to get the date string according to the current time zone.
        rfc2445dt() returns the date string according to UTC which is
        *not* what we want!
    """
    return dt.strftime('%Y%m%d')


def dateStringsForEvent(event):
    # Smarter handling for whole-day events
    data_dict = toDisplay(event)
    if event.getWholeDay():
        # For all-day events we must not include the time within
        # the date-time string
        start_str = _dateForWholeDay(event.start())[:8]
        if data_dict['same_day']:
            # one-day events end with the timestamp of the next day
            # (which is the start data plus 1 day)
            end_str = _dateForWholeDay(event.start() + 1)[:8]
        else:
            # all-day events lasting several days end at the next
            # day after the end date
            end_str = _dateForWholeDay(event.end() + 1)[:8]
    else:
        # default (as used in Plone)
        start_str = rfc2445dt(event.start())
        end_str = rfc2445dt(event.end())

    return start_str, end_str

