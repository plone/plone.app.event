from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IRecurrenceSupport
from plone.event.interfaces import IOccurrence

from plone.event.utils import is_same_day, is_same_time

from plone.app.event.base import DT, ulocalized_time


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

    @property
    def is_occurrence(self):
        return IOccurrence.providedBy(self.context)

    @property
    def occurrence_parent_url(self):
        if self.is_occurrence:
            return aq_parent(self.context).absolute_url()
        return None

    @property
    def data(self):
        accessor = IEventAccessor(self.context)
        return accessor

    def date_for_display(self):
        display = prepare_for_display(
                self.context,
                self.data.start,
                self.data.end,
                self.data.whole_day)
        display.update({'url': self.data.context.absolute_url()})
        return display

    @property
    def occurrences(self):
        """Returns all occurrences for this context. The maximum
        defaults to 10 occurrences. If there are more occurrences
        defined for this context, the result will contain the last item
        of the occurrence list.

        :rtype: dict - with ``events`` and ``tail`` as keys.
        """
        eventsinfo = dict(events=[], tail=None)
        context = self.context
        adapter = IRecurrenceSupport(context, None)
        if adapter is not None:
            occurrences = adapter.occurrences()
            eventsinfo['events'], eventsinfo['tail'] = (
                self._get_occurrences_helper(occurrences)
            )
        return eventsinfo

    def _get_occurrences_helper(self, occ_list, limit=7):
        """For many occurrences we limit the amount of occurrences to
        display. That is, this method returns the first 6 (limit)
        occurrences and the last occurrence in the list.

        :param occ_list: The list of occurrences returned from
                         IRecurrenceSupport
        :type occ_list: list
        :param limit: optional, defaults to 10
        :rtype: tuple of (list of events, last item of occ_list)
        """
        events = []
        occurrences = occ_list[:limit]
        occurrences.append(occ_list.pop())
        many = len(occ_list) > limit
        for occ in occurrences:
            acc = IEventAccessor(occ)
            display = prepare_for_display(
                self.context, acc.start, acc.end, acc.whole_day)
            display.update({'url': acc.context.absolute_url()})
            events.append(display)
        tail = events.pop()
        tail = tail if many else None
        return (events, tail)
