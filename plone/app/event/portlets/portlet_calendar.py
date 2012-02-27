import calendar
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from plone.app.event.base import first_weekday
from plone.app.event.base import localized_today
from plone.app.event.base import get_events_by_date

PLMF = MessageFactory('plonelocales')


class ICalendarPortlet(IPortletDataProvider):
    """A portlet displaying a calendar
    """


class Assignment(base.Assignment):
    implements(ICalendarPortlet)
    title = _(u'Calendar')


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet_calendar.pt')

    def update(self):
        context = aq_inner(self.context)

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = self.previous_month(year, month)
        self.next_year, self.next_month = next_year, next_month = self.next_month(year, month)
        # TODO: respect current query string
        self.prev_query = '?month=%s&year=%s' % (prev_year, prev_month)
        self.next_query = '?month=%s&year=%s' % (next_year, next_month)

        self.cal = calendar.Calendar(first_weekday())
        self._ts = getToolByName(context, 'translation_service')
        self.month_name = PLMF(self._ts.month_msgid(month),
                              default=self._ts.month_english(month))
        self.weekdays = [PLMF(self._ts.day_msgid(day, format='s'),
                              default=self._ts.weekday_english(day, format='a'))
                         for day in self.cal.iterweekdays()]

    def year_month_display(self):
        """ Return the year and month to display in the calendar.
        """
        context = aq_inner(self.context)
        request = self.request

        # Try to get year and month from requst
        year = request.get('year', None)
        month = request.get('month', None)

        # Or use current date
        if not year or month:
            today = localized_today(context)
            if not year:
                year = today.year
            if not month:
                month = today.month

        return int(year), int(month)

    def previous_month(self, year, month):
        if month==0 or month==1:
            month, year = 12, year - 1
        else:
            month-=1
        return (year, month)

    def next_month(self, year, month):
        if month==12:
            month, year = 1, year + 1
        else:
            month+=1
        return (year, month)

    @property
    def cal_data(self):
        """ Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
        events = get_events_by_date(context, monthdates[0], monthdates[-1])
        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        caldata = [[]]
        for dat in monthdates:
            if len(caldata[-1]) == 7:
                caldata.append([])
            date_events = None
            isodat = dat.isoformat()
            if isodat in events:
                date_events = events[isodat]

            events_string = u""
            if date_events:
                for event in date_events:
                    events_string += u'%s<a href="%s">%s</a>%s' % (
                        events_string and u"</br>" or u"",
                        event.getURL(),
                        event.Title.decode('utf-8'),
                        event.location and u" %s" % event.location or u"")

            caldata[-1].append(
                {'date':dat,
                 'day':dat.day,
                 'prev_month': dat.month < month,
                 'next_month': dat.month > month,
                 'today': dat.year == today.year and\
                          dat.month == today.month and\
                          dat.day == today.day,
                 'date_string': u"%s-%s-%s" % (dat.year, dat.month, dat.day),
                 'events_string': events_string,
                 'events':date_events})
        return caldata


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
