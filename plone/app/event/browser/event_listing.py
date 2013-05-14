from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView
from calendar import monthrange
from datetime import date
from datetime import timedelta
from plone.app.event import messageFactory as _
from plone.app.event.base import date_speller
from plone.app.event.base import get_events
from plone.app.event.base import guess_date_from
from plone.app.event.base import localized_now
from plone.app.event.base import start_end_from_mode
from plone.app.event.ical.exporter import construct_icalendar
from plone.app.layout.navigation.defaultpage import getDefaultPage
from plone.event.interfaces import IEventAccessor
from plone.memoize import view
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
try:
    from plone.app.collection.interfaces import ICollection
except ImportError:
    ICollection = None
try:
    from Products.ATContentTypes.interfaces import IATTopic
except ImportError:
    IATTopic = None


class EventListing(BrowserView):

    def __init__(self, context, request):
        super(EventListing, self).__init__(context, request)

        self.now = now = localized_now(context)

        # Batch parameter
        req = self.request.form
        self.b_start = 'b_start' in req and int(req['b_start']) or 0
        self.b_size  = 'b_size'  in req and int(req['b_size'])  or 10
        self.orphan  = 'orphan'  in req and int(req['orphan'])  or 1
        self.mode    = 'mode'    in req and req['mode']         or None
        self._date   = 'date'    in req and req['date']         or None
        self._all    = 'all'     in req and True                or False

        day   = 'day'   in req and int(req['day'])   or None
        month = 'month' in req and int(req['month']) or None
        year  = 'year'  in req and int(req['year'])  or None

        if not self._date and day or month or year:
            self._date = date(year or now.year,
                              month or now.month,
                              day or now.day).isoformat()

        if self.mode == None:
            self.mode = self._date and 'day' or 'future'

    @property
    def default_context(self):
        # Try to get the default page
        context = self.context
        default = getDefaultPage(context)
        if default:
            context = context[default]
        return context

    @property
    def is_collection(self):
        ctx = self.default_context
        return ICollection and ICollection.providedBy(ctx) or False

    @property
    def is_topic(self):
        ctx = self.default_context
        return IATTopic and IATTopic.providedBy(ctx) or False

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

    @view.memoize
    def _get_events(self, ret_mode=3):
        context = self.context
        kw = {}
        if not self._all:
            kw['path'] = '/'.join(context.getPhysicalPath())
        #kw['b_start'] = self.b_start
        #kw['b_size']  = self.b_size

        start, end = self._start_end
        return get_events(context, start=start, end=end,
                          ret_mode=ret_mode, expand=True, **kw)

    def events(self, ret_mode=3, batch=True):
        res = []
        is_col = self.is_collection
        is_top = self.is_topic
        if is_col or is_top:
            ctx = self.default_context
            if is_col:
                res = ctx.results(batch=False, sort_on='start', brains=False)
            else:
                res = ctx.queryCatalog(
                    REQUEST=self.request, batch=False, full_objects=True
                )
            # TODO: uff, we have to walk through all results...
            if ret_mode == 3:
                res = [IEventAccessor(obj) for obj in res]
        else:
            res = self._get_events(ret_mode)
        if batch:
            b_start = self.b_start
            b_size  = self.b_size
            res = Batch(res, size=b_size, start=b_start, orphan=self.orphan)
        return res

    @property
    def ical(self):
        events = self.events(ret_mode=2, batch=False)  # get as objects
        cal = construct_icalendar(self.context, events)
        name = '%s.ics' % self.context.getId()
        self.request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        self.request.RESPONSE.setHeader('Content-Disposition',
            'attachment; filename="%s"' % name)
        self.request.RESPONSE.write(cal.to_ical())

    @property
    def ical_url(self):
        date = self.date
        mode = self.mode
        qstr = (date or mode) and '?%s%s%s' %\
                (mode and 'mode=%s' % mode,
                 mode and date and '&' or '',
                 date and 'date=%s' % date or '') or ''
        return '%s/@@event_listing_ical%s' % (
            self.context.absolute_url(),
            qstr
        )

    def formated_date(self, occ):
        provider = getMultiAdapter((self.context, self.request, self),
                IContentProvider, name='formated_date')
        return provider(occ.context)

    def date_speller(self, date):
        return date_speller(self.context, date)

    @property
    def header_string(self):
        start, end = self._start_end
        start_dict = start and date_speller(self.context, start) or None
        end_dict = end and date_speller(self.context, end) or None

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
            sub_msgid = _(u"events_from_until",
                      default=u"${from} until ${until}.",
                      mapping={
                          'from': "%s, %s. %s %s" % (
                                start_dict['wkday'],
                                start.day,
                                start_dict['month'],
                                start.year),
                          'until': "%s, %s. %s %s" % (
                                end_dict['wkday'],
                                end.day,
                                end_dict['month'],
                                end.year),
                        }
                    )

        elif mode == 'day':
            main_msgid = _(u"events_on_day",
                      default=u"Events on ${day}",
                      mapping={
                          'day': "%s, %s. %s %s" % (
                                start_dict['wkday'],
                                start.day,
                                start_dict['month'],
                                start.year),
                        }
                    )

        elif mode == 'week':
            main_msgid = _(u"events_in_week",
                           default=u"Events in week ${weeknumber}",
                           mapping={'weeknumber': start.isocalendar()[1]})
            sub_msgid = _(u"events_from_until",
                      default=u"${from} until ${until}.",
                      mapping={
                          'from': "%s, %s. %s %s" % (
                                start_dict['wkday'],
                                start.day,
                                start_dict['month'],
                                start.year),
                          'until': "%s, %s. %s %s" % (
                                end_dict['wkday'],
                                end.day,
                                end_dict['month'],
                                end.year),
                        }
                    )

        elif mode == 'month':
            main_msgid = _(u"events_in_month",
                      default=u"Events in ${month} ${year}",
                      mapping={
                          'month': start_dict['month'],
                          'year': start.year,
                        }
                    )

        trans = self.context.translate
        return {'main': main_msgid and trans(main_msgid) or '',
                'sub': sub_msgid and trans(sub_msgid) or ''}

    # MODE URLs
    def _date_nav_url(self, mode, datestr=''):
        return '%s?mode=%s%s' % (
                self.request.getURL(),
                mode,
                datestr and '&date=%s' % datestr or '')

    @property
    def mode_all_url(self):
        return self._date_nav_url('all')

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
