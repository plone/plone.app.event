

def isSameDay(event):

    # Events without end date always cound as same-day event        
    if not event.useEndDate():
        return True

    return event.start().year() == event.end().year() and \
           event.start().month() == event.end().month() and \
           event.start().day() == event.end().day()
