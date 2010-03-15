

def isSameDay(event):

    return event.start().year() == event.end().year() and \
           event.start().month() == event.end().month() and \
           event.start().day() == event.end().day()
