from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import first_weekday
from plone.app.event.base import get_events, construct_calendar
from plone.app.event.base import localized_today
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.event.interfaces import IEventAccessor
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.formlib import form
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

import calendar


PLMF = MessageFactory('plonelocales')


class ICalendarPortlet(IPortletDataProvider):
    """A portlet displaying a calendar
    """

    state = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=None,
        required=False,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates")
    )

    search_base = schema.Choice(
        title=_(u'portlet_label_search_base', default=u'Search base'),
        description=_(
            u'portlet_help_search_base',
            default=u'Select search base folder to search for events. This '
                    u'folder will also be used to link to in calendar '
                    u'searches. If empty, the whole site will be searched and '
                    u'the event listing view will be called on the site root.'
        ),
        required=False,
        source=SearchableTextSourceBinder(
            {'is_folderish': True},
            default_query='path:'
        ),
    )


class Assignment(base.Assignment):
    implements(ICalendarPortlet)
    title = _(u'Calendar')

    # reduce upgrade pain
    state = None
    search_base = None

    def __init__(self, state=None, search_base=None):
        self.state = state
        self.search_base = search_base


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet_calendar.pt')

    def update(self):
        context = aq_inner(self.context)

        self.calendar_url = get_calendar_url(context, self.data.search_base)

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = (
            self.get_previous_month(year, month))
        self.next_year, self.next_month = next_year, next_month = (
            self.get_next_month(year, month))
        # TODO: respect current url-query string
        self.prev_query = '?month=%s&year=%s' % (prev_month, prev_year)
        self.next_query = '?month=%s&year=%s' % (next_month, next_year)

        self.cal = calendar.Calendar(first_weekday())
        self._ts = getToolByName(context, 'translation_service')
        self.month_name = PLMF(
            self._ts.month_msgid(month),
            default=self._ts.month_english(month)
        )

        # strftime %w interprets 0 as Sunday unlike the calendar.
        strftime_wkdays = [
            wkday_to_mon1(day) for day in self.cal.iterweekdays()
        ]
        self.weekdays = [
            PLMF(self._ts.day_msgid(day, format='s'),
                 default=self._ts.weekday_english(day, format='a'))
            for day in strftime_wkdays
        ]

    def year_month_display(self):
        """ Return the year and month to display in the calendar.
        """
        context = aq_inner(self.context)
        request = self.request

        # Try to get year and month from request
        year = request.get('year', None)
        month = request.get('month', None)

        # Or use current date
        today = localized_today(context)
        if not year:
            year = today.year
        if not month:
            month = today.month

        # try to transform to number but fall back to current
        # date if this is ambiguous
        try:
            year, month = int(year), int(month)
        except (TypeError, ValueError):
            year, month = today.year, today.month

        return year, month

    def get_previous_month(self, year, month):
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def get_next_month(self, year, month):
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)

    def date_events_url(self, date):
        return '%s?mode=day&date=%s' % (self.calendar_url, date)

    @property
    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]

        data = self.data
        query_kw = {}
        if data.search_base:
            portal = getToolByName(context, 'portal_url').getPortalObject()
            query_kw['path'] = {'query': '%s%s' % (
                '/'.join(portal.getPhysicalPath()), data.search_base)}

        if data.state:
            query_kw['review_state'] = data.state

        start = monthdates[0]
        end = monthdates[-1]
        events = get_events(context, start=start, end=end,
                            ret_mode=RET_MODE_OBJECTS,
                            expand=True, **query_kw)
        cal_dict = construct_calendar(events, start=start, end=end)

        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        caldata = [[]]
        for dat in monthdates:
            if len(caldata[-1]) == 7:
                caldata.append([])
            date_events = None
            isodat = dat.isoformat()
            if isodat in cal_dict:
                date_events = cal_dict[isodat]

            events_string = u""
            if date_events:
                for occ in date_events:
                    accessor = IEventAccessor(occ)
                    location = accessor.location
                    whole_day = accessor.whole_day
                    time = accessor.start.time().strftime('%H:%M')
                    # TODO: make 24/12 hr format configurable
                    base = u'<a href="%s"><span class="title">%s</span>'\
                           u'%s%s%s</a>'
                    events_string += base % (
                        accessor.url,
                        accessor.title,
                        not whole_day and u' %s' % time or u'',
                        not whole_day and location and u', ' or u'',
                        location and u' %s' % location or u'')

            caldata[-1].append(
                {'date': dat,
                 'day': dat.day,
                 'prev_month': dat.month < month,
                 'next_month': dat.month > month,
                 'today':
                    dat.year == today.year and
                    dat.month == today.month and
                    dat.day == today.day,
                 'date_string': u"%s-%s-%s" % (dat.year, dat.month, dat.day),
                 'events_string': events_string,
                 'events': date_events})
        return caldata


class AddForm(base.AddForm):
    form_fields = form.Fields(ICalendarPortlet)
    label = _(u"Add Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")
    form_fields = form.Fields(ICalendarPortlet)
    form_fields['search_base'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(state=data.get('state', None),
                          search_base=data.get('search_base', None))


class EditForm(base.EditForm):
    form_fields = form.Fields(ICalendarPortlet)
    label = _(u"Edit Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")
    form_fields = form.Fields(ICalendarPortlet)
    form_fields['search_base'].custom_widget = UberSelectionWidget
