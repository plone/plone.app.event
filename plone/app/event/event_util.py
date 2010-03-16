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
       'start' - date string for start date
       'end' - date string for end date (None if not being displayed)
       'same_day' - event ends on the same day
    """

    start = ulocalized_time(event.start(), False, context=event)
    end = ulocalized_time(event.end(), False, context=event)

    same_day = isSameDay(event)

    if not event.getWholeDay():
        start = ulocalized_time(event.start(), True, context=event)
        end = ulocalized_time(event.end(), True, context=event)

    if not event.getUseEndDate():
        end = None
    
    if start == end:
        return dict(start=start, end=None, same_day=same_day)
    return  dict(start=start, end=end, same_day=same_day)
