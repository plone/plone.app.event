from Products.Five.browser import BrowserView


from plone.app.event import event_util

class EventView(BrowserView):

    def date_for_display(self):

        # ATT: format string
        return event_util.toDisplay(self.context)

