from Products.Five.browser import BrowserView
from Products.CMFPlone.i18nl10n import ulocalized_time
from plone.event.interfaces import IRecurrenceSupport
from plone.event.utils import isSameDay, isSameTime


def toDisplay(event):
    """ Return dict containing pre-calculated information for
        building a <start>-<end> date string. Keys are
       'start_date' - date string of the start date
       'start_time' - time string of the start date
       'end_date' - date string of the end date
       'end_time' - time string of the end date
       'same_day' - event ends on the same day
    """

    # The behavior os ulocalized_time() with time_only is odd.
    # Setting time_only=False should return the date part only and *not*
    # the time
    #
    # ulocalized_time(event.start(), False,  time_only=True, context=event)
    # u'14:40'
    # ulocalized_time(event.start(), False,  time_only=False, context=event)
    # u'14:40'
    # ulocalized_time(event.start(), False,  time_only=None, context=event)
    # u'16.03.2010'

    # this needs to separate date and time as ulocalized_time does
    start_date = ulocalized_time(event.start(), False,
                                 time_only=None, context=event)
    start_time = ulocalized_time(event.start(), False,
                                 time_only=True, context=event)
    end_date = ulocalized_time(event.end(), False,
                               time_only=None, context=event)
    end_time = ulocalized_time(event.end(), False,
                               time_only=True, context=event)
    same_day = isSameDay(event)
    same_time = isSameTime(event)

    # set time fields to None for whole day events
    if event.whole_day():
        start_time = end_time = None

    return  dict(start_date=start_date,
                 start_time=start_time,
                 end_date=end_date,
                 end_time=end_time,
                 start_iso=event.start().ISO8601(),
                 end_iso=event.end().ISO8601(),
                 same_day=same_day,
                 same_time=same_time)


class EventView(BrowserView):

    def date_for_display(self):
        return toDisplay(self.context)

    @property
    def occurrences(self):
        recur = IRecurrenceSupport(self.context)
        events = map(
            lambda event:dict(
                start_date = ulocalized_time(event['start_date'], False, time_only=None, context=self.context),
                end_date = ulocalized_time(event['end_date'], False, time_only=None, context=self.context),
                start_time = ulocalized_time(event['start_date'], False, time_only=True, context=self.context),
                end_time = ulocalized_time(event['end_date'], False, time_only=True, context=self.context),
                start_iso = event['start_date'].isoformat(),
                end_iso = event['end_date'].isoformat(),
                same_day = event['start_date'].date() == event['end_date'].date(),
                same_time = event['start_date'].time() == event['end_date'].time(),
            ), recur.occurences())

        return events
