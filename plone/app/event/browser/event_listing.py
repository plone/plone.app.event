# -*- coding: utf-8 -*-
from calendar import monthrange
from datetime import date
from datetime import timedelta
from plone.app.event import _
from plone.app.event.base import _prepare_range
from plone.app.event.base import expand_events
from plone.app.event.base import get_events
from plone.app.event.base import guess_date_from
from plone.app.event.base import localized_now
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import spell_date
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import start_end_query
from plone.app.event.ical.exporter import construct_icalendar
from plone.app.querystring import queryparser
from plone.memoize import view
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider


try:
    from Products.CMFPlone.defaultpage import get_default_page
except ImportError:
    # Plone 4
    from plone.app.layout.navigation.defaultpage import getDefaultPage as get_default_page  # noqa

try:
    from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection as ICollection  # noqa
except ImportError:
    ICollection = None


class EventListing(BrowserView):

    def __init__(self, context, request):
        super(EventListing, self).__init__(context, request)

        self.now = now = localized_now(context)

        # Try to get the default page
        default = get_default_page(context)
        self.default_context = context[default] if default else context

        self.is_collection = False
        if ICollection:
            self.is_collection = ICollection.providedBy(self.default_context)

        # Request parameter
        req = self.request.form

        b_size  = int(req.get('b_size', 0))
        if not b_size and self.is_collection:
            collection_behavior = ICollection(self.default_context)
            b_size = getattr(collection_behavior, 'item_count', 0)
        self.b_size = b_size or 10
        self.b_start = int(req.get('b_start', 0))
        self.orphan  = int(req.get('orphan', 1))
        self.mode    = req.get('mode', None)
        self._date   = req.get('date', None)
        self.tags    = req.get('tags', None)
        self.searchable_text = req.get('SearchableText', None)
        self.path    = req.get('path', None)

        day   = int(req.get('day', 0)) or None
        month = int(req.get('month', 0)) or None
        year  = int(req.get('year', 0)) or None

        if not self._date and day or month or year:
            self._date = date(year or now.year,
                              month or now.month,
                              day or now.day).isoformat()

        if self.mode is None:
            self.mode = 'day' if self._date else 'future'

        self.uid = None  # Used to get all occurrences from a single event. Overrides all other settings  # noqa

    @property
    def show_filter(self):
        ret = True
        if self.is_collection:
            ctx = self.default_context
            query = queryparser.parseFormquery(ctx, ctx.query)
            if 'start' in query or 'end' in query:
                # Don't show the date filter, if a date is given in the
                # collection's query
                ret = False
        return ret

    @property
    def date(self):
        dt = None
        if self._date:
            try:
                dt = guess_date_from(self._date)
            except TypeError:
                pass
        return dt

    @property
    def _start_end(self):
        start, end = start_end_from_mode(self.mode, self.date, self.context)
        return start, end

    def _get_events(self, ret_mode=RET_MODE_ACCESSORS, expand=True):
        context = self.context
        kw = {}
        if self.uid:
            # In this case, restrict search for single event
            kw['UID'] = self.uid
        else:
            if self.path:
                kw['path'] = self.path
            else:
                # Search current and subsequent folders
                kw['path'] = '/'.join(context.getPhysicalPath())

            if self.tags:
                kw['Subject'] = {'query': self.tags, 'operator': 'and'}

            if self.searchable_text:
                kw['SearchableText'] = self.searchable_text

        # kw['b_start'] = self.b_start
        # kw['b_size']  = self.b_size

        start, end = self._start_end

        sort = 'start'
        sort_reverse = False
        if self.mode in ('past', 'all'):
            sort_reverse = True
        return get_events(context, start=start, end=end,
                          sort=sort, sort_reverse=sort_reverse,
                          ret_mode=ret_mode, expand=expand, **kw)

    @view.memoize
    def events(self, ret_mode=RET_MODE_ACCESSORS, expand=True, batch=True):
        res = []
        if self.is_collection:
            ctx = self.default_context
            # Whatever sorting is defined, we're overriding it.
            sort_on = 'start'
            sort_order = None
            if self.mode in ('past', 'all'):
                sort_order = 'reverse'
            query = queryparser.parseFormquery(
                ctx, ctx.query, sort_on=sort_on, sort_order=sort_order
            )
            custom_query = self.request.get('contentFilter', {})
            if 'start' not in query or 'end' not in query:
                # ... else don't show the navigation bar
                start, end = self._start_end
                start, end = _prepare_range(ctx, start, end)
                custom_query.update(start_end_query(start, end))
            res = ctx.results(
                batch=False, brains=True, custom_query=custom_query
            )
            if expand:
                # get start and end values from the query to ensure limited
                # listing for occurrences
                start, end = self._expand_events_start_end(
                    query.get('start') or custom_query.get('start'),
                    query.get('end') or custom_query.get('end')
                )
                res = expand_events(
                    res, ret_mode,
                    start=start, end=end,
                    sort=sort_on, sort_reverse=True if sort_order else False
                )
        else:
            res = self._get_events(ret_mode, expand=expand)
        if batch:
            b_start = self.b_start
            b_size = self.b_size
            res = Batch(res, size=b_size, start=b_start, orphan=self.orphan)
        return res

    @property
    def ical(self):
        # Get as objects.
        # Don't include occurrences to avoid having them along with their
        # original events and it's recurrence definition in icalendar exports.
        events = self.events(ret_mode=RET_MODE_OBJECTS, expand=False,
                             batch=False)
        cal = construct_icalendar(self.context, events)
        name = '%s.ics' % self.context.getId()
        contents = cal.to_ical()
        self.request.response.setHeader('Content-Type', 'text/calendar')
        self.request.response.setHeader(
            'Content-Disposition',
            'attachment; filename="%s"' % name
        )
        self.request.response.setHeader('Content-Length', len(contents))
        self.request.response.write(contents)

    @property
    def ical_url(self):
        date = self.date
        mode = self.mode

        qstr = '&'.join([
            it for it in ['mode=%s' % mode if mode else None,
                          'date=%s' % date if date else None]
            if it
        ])
        qstr = '?%s' % qstr if qstr else ''
        return '%s/@@event_listing_ical%s' % (
            self.context.absolute_url(),
            qstr
        )

    # COLLECTION daterange start/end determination
    def _expand_events_start_end(self, start, end):
        # make sane start and end values for expand_events from
        # Collection start/end criterions.
        # if end/min is given, it overrides start/min settings to make sure,
        # ongoing events are shown in the listing!
        # XXX: This actually fits most needs, but not all. Maybe someone
        # wants to come up with some edgecases!
        se = dict(start=None, end=None)
        if start:
            q = start.get('query')
            r = start.get('range')
            if r == "min":
                se["start"] = q
            elif r == "max":
                se["end"] = q
            elif r in ("minmax", "min:max"):
                list(q).sort()
                se["start"] = q[0]
                se["end"] = q[1]
        if end:
            q = end.get('query')
            r = end.get('range')
            if r == "min":
                se["start"] = q
        return se["start"], se["end"]

    def formatted_date(self, occ):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(occ)

    def date_speller(self, date):
        return spell_date(date, self.context)

    @property
    def header_string(self):
        start, end = self._start_end
        start_dict = spell_date(start, self.context) if start else None
        end_dict = spell_date(end, self.context) if end else None

        mode = self.mode
        main_msgid = None
        sub_msgid = None
        if mode == 'all':
            main_msgid = _(u"all_events", default=u"All events")

        elif mode == 'past':
            main_msgid = _(u"past_events", default=u"Past events")

        elif mode == 'future':
            main_msgid = _(u"future_events", default=u"Future events")

        elif mode == 'now':
            main_msgid = _(u"todays_upcoming_events",
                           default=u"Todays upcoming events")

        elif mode == 'today':
            main_msgid = _(u"todays_events", default=u"Todays events")

        elif mode == '7days':
            main_msgid = _(u"7days_events", default=u"Events in next 7 days.")
            sub_msgid = _(
                u"events_from_until",
                default=u"${from} until ${until}.",
                mapping={
                    'from': "%s, %s. %s %s" % (
                        start_dict['wkday_name'],
                        start.day,
                        start_dict['month_name'],
                        start.year
                    ),
                    'until': "%s, %s. %s %s" % (
                        end_dict['wkday_name'],
                        end.day,
                        end_dict['month_name'],
                        end.year
                    ),
                }
            )

        elif mode == 'day':
            main_msgid = _(
                u"events_on_day",
                default=u"Events on ${day}",
                mapping={
                    'day': "%s, %s. %s %s" % (
                        start_dict['wkday_name'],
                        start.day,
                        start_dict['month_name'],
                        start.year
                    ),
                }
            )

        elif mode == 'week':
            main_msgid = _(u"events_in_week",
                           default=u"Events in week ${weeknumber}",
                           mapping={'weeknumber': start.isocalendar()[1]})
            sub_msgid = _(
                u"events_from_until",
                default=u"${from} until ${until}.",
                mapping={
                    'from': "%s, %s. %s %s" % (
                        start_dict['wkday_name'],
                        start.day,
                        start_dict['month_name'],
                        start.year
                    ),
                    'until': "%s, %s. %s %s" % (
                        end_dict['wkday_name'],
                        end.day,
                        end_dict['month_name'],
                        end.year
                    ),
                }
            )

        elif mode == 'month':
            main_msgid = _(
                u"events_in_month",
                default=u"Events in ${month} ${year}",
                mapping={
                    'month': start_dict['month_name'],
                    'year': start.year,
                }
            )

        trans = self.context.translate
        return {'main': trans(main_msgid) if main_msgid else '',
                'sub': trans(sub_msgid) if sub_msgid else ''}

    # MODE URLs
    def _date_nav_url(self, mode, datestr=''):
        return '%s?mode=%s%s' % (
            self.request.getURL(),
            mode,
            '&date=%s' % datestr if datestr else ''
        )

    @property
    def mode_all_url(self):
        return self._date_nav_url('all')

    @property
    def mode_future_url(self):
        return self._date_nav_url('future')

    @property
    def mode_past_url(self):
        return self._date_nav_url('past')

    @property
    def mode_day_url(self):
        now = self.date or self.now
        return self._date_nav_url('day', now.date().isoformat())

    @property
    def mode_week_url(self):
        now = self.date or self.now
        return self._date_nav_url('week', now.date().isoformat())

    @property
    def mode_month_url(self):
        now = self.date or self.now
        return self._date_nav_url('month', now.date().isoformat())

    # DAY NAV
    @property
    def next_day_url(self):
        now = self.date or self.now
        datestr = (now + timedelta(days=1)).date().isoformat()
        return self._date_nav_url('day', datestr)

    @property
    def today_url(self):
        return self._date_nav_url('day')

    @property
    def prev_day_url(self):
        now = self.date or self.now
        datestr = (now - timedelta(days=1)).date().isoformat()
        return self._date_nav_url('day', datestr)

    # WEEK NAV
    @property
    def next_week_url(self):
        now = self.date or self.now
        datestr = (now + timedelta(days=7)).date().isoformat()
        return self._date_nav_url('week', datestr)

    @property
    def this_week_url(self):
        return self._date_nav_url('week')

    @property
    def prev_week_url(self):
        now = self.date or self.now
        datestr = (now - timedelta(days=7)).date().isoformat()
        return self._date_nav_url('week', datestr)

    # MONTH NAV
    @property
    def next_month_url(self):
        now = self.date or self.now
        last_day = monthrange(now.year, now.month)[1]  # (wkday, days)
        datestr = (now.replace(day=last_day) +
                   timedelta(days=1)).date().isoformat()
        return self._date_nav_url('month', datestr)

    @property
    def this_month_url(self):
        return self._date_nav_url('month')

    @property
    def prev_month_url(self):
        now = self.date or self.now
        datestr = (now.replace(day=1) - timedelta(days=1)).date().isoformat()
        return self._date_nav_url('month', datestr)


class EventListingIcal(EventListing):
    def __call__(self, *args, **kwargs):
        return self.ical


class EventEventListing(EventListing):
    """This is an EventListing for an individual event, to list all
    occurrences batched and navigatable with all the features, the EventListing
    offers.
    """
    def __init__(self, context, request):
        super(EventEventListing, self).__init__(context, request)
        self.uid = IUUID(self.context)
