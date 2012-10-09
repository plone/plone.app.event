from Acquisition import Explicit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.event.base import dates_for_display


class FormatedDateProvider(Explicit):
    template = ViewPageTemplateFile(u'formated_date.pt')

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    def __call__(self, occ):
        """Return a formated date string.

        :param occ: An event or occurrence.
        :type occ: IEven or IOccurrence
        :returns: Formated date string for display.
        :rtype: string

        """
        self.date_dict = dates_for_display(occ)
        return self.template(self)


class FormatedStartDateProvider(FormatedDateProvider):
    template = ViewPageTemplateFile(u'formated_start_date.pt')
