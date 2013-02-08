from calendar import monthrange
from datetime import timedelta

from Products.CMFPlone.PloneBatch import Batch
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider

from plone.app.event.base import date_speller
from plone.app.event.base import get_occurrences_from_brains
from plone.app.event.base import get_portal_events
from plone.app.event.base import start_end_from_mode
from plone.app.event.base import guess_date_from
from plone.app.event.base import localized_now

from plone.app.event import messageFactory as _

class EventListing(BrowserView):

    def __init__(self, context, request):
        super(EventListing, self).__init__(context, request)

        # Batch parameter
        req = self.request
        self.b_start = 'b_start' in req and int(req['b_start']) or 0
        self.b_size  = 'b_size'  in req and int(req['b_size'])  or 10
        self.orphan  = 'orphan'  in req and int(req['orphan'])  or 1
        self.mode    = 'mode'    in req and req['mode']         or 'future'
        self._date   = 'date'    in req and req['date']         or None

        self.now = localized_now(context)

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

    @property
    def get_events(self):
        context = self.context

        b_start=self.b_start
        b_size=self.b_size

        start, end = self._start_end
        occs = get_occurrences_from_brains(
                context,
                get_portal_events(context, start, end,
                    #b_start=b_start, b_size=b_size,
                    path=context.getPhysicalPath()),
                start,
                end)

        return Batch(occs, size=b_size, start=b_start, orphan=self.orphan)

    def formated_date(self, occ):
        provider = getMultiAdapter((self.context, self.request, self),
                IContentProvider, name=u"formated_date")
        return provider(occ.context)

    def date_speller(self, date):
        return date_speller(self.context, date)

    @property
    def header_string(self):
        start, end = self._start_end
        start_dict = start and date_speller(self.context, start) or None
        end_dict = end and date_speller(self.context, end) or None

        mode = self.mode
        if mode == 'all':
            msgid = _(u"all_events", default=u"All events")

        elif mode == 'past':
            msgid = _(u"past_events", default=u"Past events")

        elif mode == 'future':
            msgid = _(u"future_events", default=u"Future events")

        elif mode == 'now':
            msgid = _(u"todays_upcoming_events", default=u"Todays upcoming events")

        elif mode == 'today':
            msgid = _(u"todays_events", default=u"Todays events")

        elif mode == '7days':
            msgid = _(u"events_from_until",
                      default=u"Events from ${from} until ${until}",
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
            msgid = _(u"events_on_day",
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
            msgid = _(u"events_in_week",
                      default=u"Events in week ${weeknumber},"
                              u" from ${from} until ${until}",
                      mapping={
                          'weeknumber': start.isocalendar()[1],
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
            msgid = _(u"events_in_month",
                      default=u"Events in ${month} ${year}",
                      mapping={
                          'month': start_dict['month'],
                          'year': start.year,
                        }
                    )

        return self.context.translate(msgid)


    # MODE URLs
    @property
    def mode_day_url(self):
        now = self.date
        datestr = now and now.date().isoformat() or None
        return '%s/%s?mode=day%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr and '&date=%s' % datestr or '')

    @property
    def mode_week_url(self):
        now = self.date
        datestr = now and now.date().isoformat() or None
        return '%s/%s?mode=week%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr and '&date=%s' % datestr or '')

    @property
    def mode_month_url(self):
        now = self.date
        datestr = now and now.date().isoformat() or None
        return '%s/%s?mode=month%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr and '&date=%s' % datestr or '')

    # DAY NAV
    @property
    def next_day_url(self):
        now = self.date or self.now
        datestr = (now + timedelta(days=1)).date().isoformat()
        return '%s/%s?mode=day&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)

    @property
    def today_url(self):
        return '%s/%s?mode=today' % (
                self.context.absolute_url(),
                self.__name__)

    @property
    def prev_day_url(self):
        now = self.date or self.now
        datestr = (now - timedelta(days=1)).date().isoformat()
        return '%s/%s?mode=day&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)

    # WEEK NAV
    @property
    def next_week_url(self):
        now = self.date or self.now
        datestr = (now + timedelta(days=7)).date().isoformat()
        return '%s/%s?mode=week&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)

    @property
    def this_week_url(self):
        now = self.now
        datestr = now.date().isoformat()
        return '%s/%s?mode=week&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)

    @property
    def prev_week_url(self):
        now = self.date or self.now
        datestr = (now - timedelta(days=7)).date().isoformat()
        return '%s/%s?mode=week&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)

    # MONTH NAV
    @property
    def next_month_url(self):
        now = self.date or self.now
        last_day = monthrange(now.year, now.month)[1] # (wkday, days)
        datestr = (now.replace(day=last_day) +
                   timedelta(days=1)).date().isoformat()
        return '%s/%s?mode=month&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)

    @property
    def this_month_url(self):
        now = self.now
        datestr = now.date().isoformat()
        return '%s/%s?mode=month&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)

    @property
    def prev_month_url(self):
        now = self.date or self.now
        datestr = (now.replace(day=1) - timedelta(days=1)).date().isoformat()
        return '%s/%s?mode=month&date=%s' % (
                self.context.absolute_url(),
                self.__name__,
                datestr)
