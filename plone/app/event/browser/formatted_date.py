# -*- coding: utf-8 -*-
from Acquisition import Explicit
from plone.app.event.base import dates_for_display
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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
        if self.date_dict is None:
            # Don't break for potential Events without start/end.
            return u""
        return self.template(self)


class FormattedStartDateProvider(FormattedDateProvider):
    template = ViewPageTemplateFile(u'formatted_start_date.pt')
