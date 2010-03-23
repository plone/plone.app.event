
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class RecurrenceWidget(BrowserView):
    """ """
    template = ViewPageTemplateFile('recurrence.pt')

    @property
    def macros(self):
        return self.template.macros
