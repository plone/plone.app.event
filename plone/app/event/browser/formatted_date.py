from Acquisition import Explicit
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.event.base import dates_for_display


class FormattedDateProvider(Explicit):
    template = ViewPageTemplateFile(u'formatted_date.pt')

    def __init__(self, context, request, view):
        self.__parent__ = view
        self.context = context
        self.request = request

    def __call__(self, occ):
        """Return a formatted date string.

        :param occ: An event or occurrence.
        :type occ: IEvent, IOccurrence or IEventAccessor based object
        :returns: Formatted date string for display.
        :rtype: string

        """
        self.date_dict = dates_for_display(occ)
        return self.template(self)


class FormattedStartDateProvider(FormattedDateProvider):
    template = ViewPageTemplateFile(u'formatted_start_date.pt')
