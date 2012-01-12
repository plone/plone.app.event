from Products.Five.browser import BrowserView
from Products.CMFPlone.i18nl10n import ulocalized_time
from plone.event.utils import is_same_day, is_same_time
from plone.app.event.base import DT
from plone.app.event.interfaces import IEventAccessor
from plone.app.event.interfaces import IRecurrence


def prepare_for_display(context, start, end, whole_day):
    """ Return a dictionary containing pre-calculated information for building
    <start>-<end> date strings.

    Keys are:
        'start_date' - date string of the start date
        'start_time' - time string of the start date
        'end_date'   - date string of the end date
        'end_time'   - time string of the end date
        'start_iso'  - start date in iso format
        'end_iso'    - end date in iso format
        'same_day'   - event ends on the same day
        'same_time'  - event ends at same time
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
    DT_start = DT(start)
    DT_end = DT(end)
    start_date = ulocalized_time(DT_start, long_format=False, time_only=None,
                                 context=context)
    start_time = ulocalized_time(DT_start, long_format=False, time_only=True,
                                 context=context)
    end_date = ulocalized_time(DT_end, long_format=False, time_only=None,
                               context=context)
    end_time = ulocalized_time(DT_end, long_format=False, time_only=True,
                               context=context)
    same_day = is_same_day(start, end)
    same_time = is_same_time(start, end)

    # set time fields to None for whole day events
    if whole_day:
        start_time = end_time = None

    return  dict(start_date=start_date,
                 start_time=start_time,
                 start_iso=start.isoformat(),
                 end_date=end_date,
                 end_time=end_time,
                 end_iso=end.isoformat(),
                 same_day=same_day,
                 same_time=same_time)


class EventView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = IEventAccessor(self.context)

    def date_for_display(self):
        return prepare_for_display(
                self.context,
                self.data['start'],
                self.data['end'],
                self.data['whole_day'])

    @property
    def occurrences(self):
        context = self.context
        events = map(
            lambda (start, end):
                prepare_for_display(self.context, start, end,
                                    self.data['whole_day']),
            IRecurrence(context).occurrences())
        return events
