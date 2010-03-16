
"""
Display helper methods for showing whole-day or same-day events
"""

def isSameDay(event):

    # Events without end date always cound as same-day event        
    if not event.useEndDate():
        return True

    return event.start().year() == event.end().year() and \
           event.start().month() == event.end().month() and \
           event.start().day() == event.end().day()

def toDisplay(event, long_fmt='%Y/%m/%d %H:%M:%S', short_fmt='%Y/%m/%d'):
    """ Return dict containing pre-calculated information for 
        building a <start>-<end> date string. Keys are
       'start' - date string for start date
       'end' - date string for end date (None if not being displayed)
       'same_day' - event ends on the same day
    """

    start = event.start().strftime(short_fmt)
    end = event.end().strftime(short_fmt)
    same_day = isSameDay(event)

    if not event.getWholeDay():
        start = event.start().strftime(long_fmt)
        end = event.end().strftime(long_fmt)

    if not event.useEndDate():
        end = None
    
    if start == end:
        return dict(start=start, end=None, same_day=same_day)
    return  dict(start=start, end=end, same_day=same_day)
