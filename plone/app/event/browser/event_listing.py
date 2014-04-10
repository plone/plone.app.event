from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView
from calendar import monthrange
from datetime import date
from datetime import timedelta
from plone.app.event import messageFactory as _
from plone.app.event.base import AnnotationAdapter
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.base import RET_MODE_OBJECTS
from plone.app.event.base import date_speller
from plone.app.event.base import expand_events
from plone.app.event.base import get_events
from plone.app.event.base import guess_date_from
from plone.app.event.base import localized_now
from plone.app.event.base import start_end_from_mode
from plone.app.event.browser.event_view import get_location
from plone.app.event.ical.exporter import construct_icalendar
from plone.app.layout.navigation.defaultpage import getDefaultPage
from plone.app.querystring import queryparser
from plone.memoize import view
from plone.uuid.interfaces import IUUID
from plone.z3cform.layout import wrap_form
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope import schema
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import Interface
from zope.interface import implements

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
        self.settings = IEventListingSettings(self.context)

        # Request parameter
        req = self.request.form
        self.b_start = 'b_start' in req and int(req['b_start']) or 0
        self.b_size = 'b_size' in req and int(req['b_size']) or 10
        self.orphan = 'orphan' in req and int(req['orphan']) or 1
        self.mode = 'mode' in req and req['mode'] or None
        self._date = 'date' in req and req['date'] or None
        self.tags = 'tags' in req and req['tags'] or None
        self.searchable_text = 'SearchableText' in req and\
            req['SearchableText'] or None
        self.path = 'path' in req and req['path'] or None

        day = 'day' in req and int(req['day']) or None
        month = 'month' in req and int(req['month']) or None
        year = 'year' in req and int(req['year']) or None

        if not self._date and day or month or year:
            self._date = date(year or now.year,
                              month or now.month,
                              day or now.day).isoformat()

        if self.mode is None:
            self.mode = self._date and 'day' or 'future'

        self.uid = None  # Used to get all occurrences from a single event.
                         # Overrides all other settings

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
    def _get_events(self, ret_mode=RET_MODE_ACCESSORS, expand=True):
        context = self.context
        kw = {}
        if self.uid:
            # In this case, restrict search for single event
            kw['UID'] = self.uid
        else:
            if self.path:
                kw['path'] = self.path
            elif self.settings.current_folder_only:
                kw['path'] = '/'.join(context.getPhysicalPath())

            if self.tags:
                kw['Subject'] = {'query': self.tags, 'operator': 'and'}

            if self.searchable_text:
                kw['SearchableText'] = self.searchable_text

        #kw['b_start'] = self.b_start
        #kw['b_size']  = self.b_size

        start, end = self._start_end

        sort = 'start'
        sort_reverse = False
        if self.mode in ('past', 'all'):
            sort_reverse = True
        return get_events(context, start=start, end=end,
                          sort=sort, sort_reverse=sort_reverse,
                          ret_mode=ret_mode, expand=expand, **kw)

    def events(self, ret_mode=RET_MODE_ACCESSORS, expand=True, batch=True):
        res = []
        is_col = self.is_collection
        is_top = self.is_topic
        if is_col or is_top:
            ctx = self.default_context
            if is_col:
                res = ctx.results(batch=False, sort_on='start', brains=True)
                query = queryparser.parseFormquery(ctx, ctx.getRawQuery())
            else:
                res = ctx.queryCatalog(batch=False, full_objects=False)
                query = ctx.buildQuery()
            if expand:
                # get start and end values from the query to ensure limited
                # listing for occurrences
                start, end = self._expand_events_start_end(query.get('start'),
                                                           query.get('end'))
                res = expand_events(res, ret_mode, sort='start', start=start,
                                    end=end)
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
        self.request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        self.request.RESPONSE.setHeader(
            'Content-Disposition',
            'attachment; filename="%s"' % name
        )
        self.request.RESPONSE.write(cal.to_ical())

    @property
    def ical_url(self):
        date = self.date
        mode = self.mode
        qstr = (date or mode) and '?%s%s%s' % (
            mode and 'mode=%s' % mode,
            mode and date and '&' or '',
            date and 'date=%s' % date or ''
        ) or ''
        return '%s/@@event_listing_ical%s' % (
            self.context.absolute_url(),
            qstr
        )

    def get_location(self, occ):
        return get_location(occ)

    def formatted_date(self, occ):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(occ)

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
            sub_msgid = _(
                u"events_from_until",
                default=u"${from} until ${until}.",
                mapping={
                    'from': "%s, %s. %s %s" % (
                        start_dict['wkday'],
                        start.day,
                        start_dict['month'],
                        start.year
                    ),
                    'until': "%s, %s. %s %s" % (
                        end_dict['wkday'],
                        end.day,
                        end_dict['month'],
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
                        start_dict['wkday'],
                        start.day,
                        start_dict['month'],
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
                        start_dict['wkday'],
                        start.day,
                        start_dict['month'],
                        start.year
                    ),
                    'until': "%s, %s. %s %s" % (
                        end_dict['wkday'],
                        end.day,
                        end_dict['month'],
                        end.year
                    ),
                }
            )

        elif mode == 'month':
            main_msgid = _(
                u"events_in_month",
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
            datestr and '&date=%s' % datestr or ''
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

    # COLLECTION daterange start/end determination
    def _expand_events_start_end(self, start, end):
        # make sane start and end values for expand_events from
        # Collection/Topic start/end criterions.
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


class IEventListingSettings(Interface):

    current_folder_only = schema.Bool(
        title=_('label_current_folder', default=u'Current folder'),
        description=_('help_current_folder',
                      default=u'Search events in current folder only.'),
        default=False
    )


class EventListingSettings(AnnotationAdapter):
    """Annotation Adapter for IEventListingSettings
    """
    implements(IEventListingSettings)
    adapts(Interface)
    ANNOTATION_KEY = "plone.app.event-event_listing-settings"


class EventListingSettingsForm(form.Form):
    fields = field.Fields(IEventListingSettings)
    ignoreContext = False

    def getContent(self):
        data = {}
        settings = IEventListingSettings(self.context)
        data['current_folder_only'] = settings.current_folder_only
        return data

    def form_next(self):
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(u'Save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return False
        settings = IEventListingSettings(self.context)
        settings.current_folder_only = data['current_folder_only']
        self.form_next()

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.form_next()


EventListingSettingsFormView = wrap_form(EventListingSettingsForm)
