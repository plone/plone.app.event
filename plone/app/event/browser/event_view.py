from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IRecurrenceSupport
from plone.event.interfaces import IOccurrence

from plone.app.event.base import prepare_for_display


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
        """Returns all occurrences for this context, except the start
        occurrence.
        The maximum defaults to 7 occurrences. If there are more occurrences
        defined for this context, the result will contain the last item
        of the occurrence list.

        :rtype: dict - with ``events`` and ``tail`` as keys.

        """
        eventsinfo = dict(events=[], tail=None)
        context = self.context
        adapter = IRecurrenceSupport(context, None)
        if adapter is not None:
            occurrences = adapter.occurrences()[1:] # don't include first
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
        :param limit: optional, defaults to 7
        :type limit: integer
        :rtype: tuple of (list of events, last item of occ_list)
        """
        events = []
        tail = None
        if occ_list:
            occurrences = occ_list[:limit]
            occurrences.append(occ_list.pop())
            many = len(occ_list) > limit
            for occ in occurrences:
                acc = IEventAccessor(occ)
                display = prepare_for_display(
                    self.context, acc.start, acc.end, acc.whole_day)
                display.update({'url': acc.context.absolute_url()})
                events.append(display)
            tail = events and events.pop() or None
            tail = tail if many else None
        return (events, tail)
