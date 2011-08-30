from Products.Five.browser import BrowserView
from Products.CMFPlone.i18nl10n import ulocalized_time
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

    # TODO convert start_date, start_time, end_date, end_time
    # to user or portal timezone. Don't convert iso.

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
        # TODO convert start_date, start_time, end_date, end_time
        # to user or portal timezone. Don't convert iso.
        context = self.context
        events = map(
            lambda occ: dict(
                start_date = ulocalized_time(occ[0], False, time_only=None, context=context),
                end_date = ulocalized_time(occ[1], False, time_only=None, context=context),
                start_time = ulocalized_time(occ[0], False, time_only=True, context=context),
                end_time = ulocalized_time(occ[1], False, time_only=True, context=context),
                start_iso = occ[0].isoformat(),
                end_iso = occ[1].isoformat(),
                same_day = occ[0].date() == occ[1].date(),
                same_time = occ[0].time() == occ[1].time(),
            ), context.occurrences())

        return events
