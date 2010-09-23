from Products.Five.browser import BrowserView
from plone.app.event import event_util

from plone.app.event.interfaces import IRecurrenceSupport

class EventView(BrowserView):

    def date_for_display(self):
        return event_util.toDisplay(self.context)

    def occurrences(self):
        recur = IRecurrenceSupport(self.context)
        return recur.occurences()