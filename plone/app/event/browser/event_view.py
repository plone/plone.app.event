from Products.Five.browser import BrowserView
from Products.CMFPlone.i18nl10n import ulocalized_time
from plone.app.event import event_util
from plone.event.interfaces import IRecurrenceSupport

class EventView(BrowserView):

    def date_for_display(self):
        return event_util.toDisplay(self.context)

    def occurrences(self):
        recur = IRecurrenceSupport(self.context)
        # TODO: check again. also check need of event_util module
        events = map(
            lambda event:dict(
                start_date = ulocalized_time(event['start_date'], False, time_only=None, context=self.context),
                end_date = ulocalized_time(event['end_date'], False, time_only=None, context=self.context),
                start_time = ulocalized_time(event['start_date'], False, time_only=True, context=self.context),
                end_time = ulocalized_time(event['end_date'], False, time_only=True, context=self.context),
                same_day = event['start_date'].date() == event['end_date'].date(),
                same_time = event['start_date'].time() == event['end_date'].time(),
            ), recur.occurences())

        return events