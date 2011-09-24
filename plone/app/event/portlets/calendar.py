from plone.portlets.interfaces import IPortletDataProvider

from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base

import calendar
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
    render = ViewPageTemplateFile('calendar.pt')

    # TODO: find a way how to insert dynamic translation strings in templates.
    # does this work? i18n:translate="day-${daynumber}"?
    # use python's urlquote instead of Products.PythonScripts.standard.url_quote_plus

    def update(self):
        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = self.previous_month(year, month)
        self.next_year, self.next_month = next_year, next_month = self.next_month(year, month)
        # TODO: respect current query string
        self.prev_query = '?month=%s&year=%s' % (prev_year, prev_month)
        self.next_query = '?month=%s&year=%s' % (next_year, next_month)

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
    def cal(self):
        """ Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        cal = calendar.Calendar(first_weekday)
        monthdates = [dat for dat in cal.itermonthdates(year, month)]
        # TODO: get_events_by_date probably needs a DateTime instance
        events = get_events_by_date(context, monthdates[0], monthdates[-1])
        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        cal = []
        for dat in monthdates:
            for cnt in range(7):
                if cnt == 0:
                    cal.append([])
                date_events = None
                isodat = dat.isoformat()
                if isodat in events:
                    date_events = events[isodat]
                cal[-1].append(
                    {'date':dat,
                     'prev': dat.month < month,
                     'next': dat.month > month,
                     'today': dat.year == today.year and\
                              dat.month == today.month and\
                              dat.day == today.day,
                     'events':date_events})
        return cal

    @property
    def weekdays(self):
        cal = calendar.Calendar(first_weekday)
        return cal.iterweekdays()


    ####
    # OLD METHODS
    # WILL BE REMOVED

    def getEventsForCalendar(self):
        context = aq_inner(self.context)
        year = self.year
        month = self.month
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()
        weeks = self.calendar.getEventsForCalendar(month, year, path=navigation_root_path)
        for week in weeks:
            for day in week:
                daynumber = day['day']
                if daynumber == 0:
                    continue
                day['is_today'] = self.isToday(daynumber)
                if day['event']:
                    cur_date = DateTime(year, month, daynumber)
                    localized_date = [self._ts.ulocalized_time(cur_date, context=context, request=self.request)]
                    day['eventstring'] = '\n'.join(localized_date+[' %s' % self.getEventString(e) for e in day['eventslist']])
                    day['date_string'] = '%s-%s-%s' % (year, month, daynumber)

        return weeks

    def getEventString(self, event):
        start = event['start'] and ':'.join(event['start'].split(':')[:2]) or ''
        end = event['end'] and ':'.join(event['end'].split(':')[:2]) or ''
        title = safe_unicode(event['title']) or u'event'

        if start and end:
            eventstring = "%s-%s %s" % (start, end, title)
        elif start: # can assume not event['end']
            eventstring = "%s - %s" % (start, title)
        elif event['end']: # can assume not event['start']
            eventstring = "%s - %s" % (title, end)
        else: # can assume not event['start'] and not event['end']
            eventstring = title

        return eventstring

    def getYearAndMonthToDisplay(self):
        session = None
        request = self.request

        # First priority goes to the data in the REQUEST
        year = request.get('year', None)
        month = request.get('month', None)

        # Next get the data from the SESSION
        if self.calendar.getUseSession():
            session = request.get('SESSION', None)
            if session:
                if not year:
                    year = session.get('calendar_year', None)
                if not month:
                    month = session.get('calendar_month', None)

        # Last resort to today
        if not year:
            year = self.now[0]
        if not month:
            month = self.now[1]

        year, month = int(year), int(month)

        # Store the results in the session for next time
        if session:
            session.set('calendar_year', year)
            session.set('calendar_month', month)

        # Finally return the results
        return year, month


    def getWeekdays(self):
        """Returns a list of Messages for the weekday names."""
        weekdays = []
        # list of ordered weekdays as numbers
        for day in self.calendar.getDayNumbers():
            weekdays.append(PLMF(self._ts.day_msgid(day, format='s'),
                                 default=self._ts.weekday_english(day, format='a')))

        return weekdays

    def isToday(self, day):
        """Returns True if the given day and the current month and year equals
           today, otherwise False.
        """
        return self.now[2]==day and self.now[1]==self.month and \
               self.now[0]==self.year

    def getReviewStateString(self):
        states = self.calendar.getCalendarStates()
        return ''.join(map(lambda x : 'review_state=%s&amp;' % self.url_quote_plus(x), states))

    def getQueryString(self):
        request = self.request
        query_string = request.get('orig_query',
                                   request.get('QUERY_STRING', None))
        if len(query_string) == 0:
            query_string = ''
        else:
            query_string = '%s&amp;' % query_string
        return query_string


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
