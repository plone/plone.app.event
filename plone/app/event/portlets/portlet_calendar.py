# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from ComputedAttribute import ComputedAttribute
from plone.app.event import _
from plone.app.event.base import _prepare_range
from plone.app.event.base import construct_calendar
from plone.app.event.base import expand_events
from plone.app.event.base import first_weekday
from plone.app.event.base import get_events
from plone.app.event.base import localized_today
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import start_end_query
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.app.portlets.portlets import base
from plone.app.querystring import queryparser
from plone.app.uuid.utils import uuidToObject
from plone.app.vocabularies.catalog import CatalogSource
from plone.event.interfaces import IEventAccessor
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from zope import schema
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

import calendar
import json


try:
    from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection as ICollection  # noqa
    from plone.app.contenttypes.interfaces import IFolder
    search_base_uid_source = CatalogSource(object_provides={
        'query': [
            ICollection.__identifier__,
            IFolder.__identifier__
        ],
        'operator': 'or'
    })
except ImportError:
    search_base_uid_source = CatalogSource(is_folderish=True)
    ICollection = None

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

    search_base_uid = schema.Choice(
        title=_(u'portlet_label_search_base', default=u'Search base'),
        description=_(
            u'portlet_help_search_base',
            default=u'Select search base Folder or Collection to search for '
                    u'events. The URL to to this item will also be used to '
                    u'link to in calendar searches. If empty, the whole site '
                    u'will be searched and the event listing view will be '
                    u'called on the site root.'
        ),
        required=False,
        source=search_base_uid_source,
    )


@implementer(ICalendarPortlet)
class Assignment(base.Assignment):
    title = _(u'Calendar')

    # reduce upgrade pain
    state = None

    def __init__(self, state=None, search_base_uid=None):
        self.state = state
        self.search_base_uid = search_base_uid

    def _uid(self):
        # This is only called if the instance doesn't have a search_base_uid
        # attribute, which is probably because it has an old
        # 'search_base' attribute that needs to be converted.
        path = self.search_base
        try:
            search_base = getSite().unrestrictedTraverse(path.lstrip('/'))
        except (AttributeError, KeyError, TypeError, NotFound):
            return
        return search_base.UID()
    search_base_uid = ComputedAttribute(_uid, 1)


class Renderer(base.Renderer):
    render = ViewPageTemplateFile('portlet_calendar.pt')
    _search_base = None

    @property
    def search_base(self):
        if not self._search_base and self.data.search_base_uid:
            self._search_base = uuidToObject(self.data.search_base_uid)
        return aq_inner(self._search_base) if self._search_base else None

    @property
    def search_base_path(self):
        return '/'.join(self.search_base.getPhysicalPath()) if self.search_base else None  # noqa

    def update(self):
        context = aq_inner(self.context)

        self.calendar_url = get_calendar_url(context, self.search_base_path)

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = (
            self.get_previous_month(year, month))
        self.next_year, self.next_month = next_year, next_month = (
            self.get_next_month(year, month))
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

        start = monthdates[0]
        end = monthdates[-1]

        data = self.data
        query = {}
        if data.state:
            query['review_state'] = data.state

        events = []
        query.update(self.request.get('contentFilter', {}))
        if ICollection and ICollection.providedBy(self.search_base):
            # Whatever sorting is defined, we're overriding it.
            query = queryparser.parseFormquery(
                self.search_base, self.search_base.query,
                sort_on='start', sort_order=None
            )

            # restrict start/end with those from query, if given.
            if 'start' in query and query['start'] > start:
                start = query['start']
            if 'end' in query and query['end'] < end:
                end = query['end']

            start, end = _prepare_range(self.search_base, start, end)
            query.update(start_end_query(start, end))
            events = self.search_base.results(
                batch=False, brains=True, custom_query=query
            )
            events = expand_events(
                events, ret_mode=RET_MODE_OBJECTS,
                start=start, end=end,
                sort='start', sort_reverse=False
            )
        else:
            if self.search_base_path:
                query['path'] = {'query': self.search_base_path}
            events = get_events(context, start=start, end=end,
                                ret_mode=RET_MODE_OBJECTS,
                                expand=True, **query)

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

            events_string_list = []
            if date_events:
                for occ in date_events:
                    accessor = IEventAccessor(occ)
                    location = accessor.location
                    whole_day = accessor.whole_day
                    time = accessor.start.time().strftime('%H:%M')
                    # TODO: make 24/12 hr format configurable
                    events_string_list.append(
                        u'{0}{1}{2}{3}'.format(
                            accessor.title,
                            u' {0}'.format(time) if not whole_day else u'',
                            u', ' if not whole_day and location else u'',
                            u' {0}'.format(location) if location else u''
                        )
                    )

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
                 'events_string': u' | '.join(events_string_list),
                 'events': date_events})
        return caldata

    def nav_pattern_options(self, year, month):
        val = self.hash
        if isinstance(val, bytes):
            val = val.decode("utf-8")

        return json.dumps({
            'url': '%s/@@render-portlet?portlethash=%s&year=%s&month=%s' % (
                getSite().absolute_url(),
                val,
                year, month),
            'target': '#portletwrapper-%s > *' % val
        })

    @property
    def hash(self):
        return self.request.form.get(
            'portlethash',
            getattr(self, '__portlet_metadata__', {}).get('hash', ''))


class AddForm(base.AddForm):
    schema = ICalendarPortlet
    label = _(u"Add Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")

    def create(self, data):
        return Assignment(
            state=data.get('state', None),
            search_base_uid=data.get('search_base_uid', None)
        )


class EditForm(base.EditForm):
    schema = ICalendarPortlet
    label = _(u"Edit Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")
