"""
Display helper methods for showing whole-day or same-day events
"""

from Products.CMFPlone.i18nl10n import ulocalized_time

def isSameDay(event):

    # Events without end date always cound as same-day event        
    if not event.getUseEndDate():
        return True

    return event.start().year() == event.end().year() and \
           event.start().month() == event.end().month() and \
           event.start().day() == event.end().day()


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

    # set time fields to None for whole day events
    if event.getWholeDay():
        start_time = end_time = None

    # set end date to None for same-day events
    if start_date == end_date:
        end = None

    return  dict(start_date=start_date, 
                 start_time=start_time,
                 end_date=end_date, 
                 end_time=end_time,
                 same_day=same_day)
