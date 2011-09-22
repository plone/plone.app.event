from datetime import datetime
from App.class_init import InitializeClass
from plone.app.event.interfaces import IEvent
from plone.app.event.interfaces import IEventSettings
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from zope.component import getUtility


# TODO: this calendar tool should provide everything needed, without the
# dependency on P.CMFCalendar. CMFCalendar Settings are in event's controlpanel
# now... actually only first_weekday - others are obsolete:
#   calendar_types is not needed, since we search for objects implementing
#       IEvent
#   show_states shouldn't be neccassary, since user should see, what he/she is
#       allowed to see. portal_catalog query should handle this allone.
#   use_session to allow persistance of selected month in calendar over some
#       requests is nice, but....
# TODO: make the CalendarTool obsolete via moving those methods into base.py

# it seems that only the calendar portlet is a consumer of the CalendarTool in
# plone-core.

# TODO: use python's calendar for calendar calculations like list of days in
# week, etc

class CalendarTool(PloneBaseTool):
    """ A tool for encapsulating how calendars work and are displayed.
    """

    id = 'portal_calendar'
    meta_type = 'Plone Calendar Tool'
    toolicon = 'skins/plone_images/event_icon.png'

    # NEW METHODS..
    # TODO: get them into base.py, eventually.... getting rid of
    # portal_calendar tool completely

    @property
    def first_weekday(self):
        """ Returns the number of the first Weekday in a Week, as defined in
        the registry.
        0 is Monday, 6 is Sunday, as expected by python's datetime.

        """
        controlpanel = getUtility(IRegistry).forInterface(IEventSettings,
                                                          prefix="plone.app.event")
        first_wd = controlpanel.first_weekday
        if not first_wd:
            return 0
        else:
            return first_wd

    def get_portal_events(self, range_start=None, range_end=None, **kw):
        """ Return all events as catalog brains, possibly within a given
        timeframe.

        """
        query = {}
        query.update(kw)
        query['object_provides'] = IEvent.__identifier__
        if range_start:
            query['start'] = {'query': range_start, 'range': 'max'}
        if range_end:
            query['end'] = {'query': range_end, 'range': 'min'}
        query['sort_on'] = 'start'

        cat = getToolByName(self, 'portal_catalog')
        result = cat(**query)
        return result

    def get_events_by_date(self, range_start=None, range_end=None, **kw):
        """ Return a dictionary with dates in a given timeframe as keys and
        the actual events for that date.

        """
        events = self.get_portal_events(range_start, range_end, **kw)
        # TODO: catalog brains are timezone'd. shouldn't they be in UTC?
        ## example catalog entry: 2011/09/16 16:35:00 Brazil/West
        events_by_date = {}
        for event in events:
            obj = event.getObject()
            occurrences = obj.occurrences(range_start, range_end)
            for occ in occurrences:
                start_str = datetime.strftime(occ.start_date, '%Y-%m-%d')
                # TODO: add span_events parameter to include dates btw. start
                # and end also. for events lasting longer than a day...
                if start_str not in events_by_date:
                    events_by_date[start_str] = [event]
                else:
                    events_by_date[start_str].append(event)
            return events_by_date

    def dt_from_brain(datestr):
        """ Return python datetime instance from a catalog brain's date string.

        %Y/%m/%d %H:%M:%S TZINFO
        Since strptime doesn't handle pytz zones very well, we need to bypass
        this limitation.

        """
        # TODO: file a bug for strptime pytz names handling.

        from pytz import timezone
        start_parts = datestr.split(' ')
        start = datetime.strptime(' '.join(start_parts)[0:2], '%Y/%m/%d %H:%M:%S')
        tz = timezone(start_parts[2])
        start = tz.localize(start) # convert naive date to event's zone

    def dt_to_zone(dt, tzstring):
        """ Return a datetime instance converted to the timezone given by the
        string.

        """
        from pytz import timezone
        return dt.astimezone(timezone(tzstring))



    ### LEGACY

    def getDayNumbers(self):
        """ Returns a list of daynumbers with the correct start day first.

        """
        fwd = self.first_weekday
        return [i%7 for i in range(fwd, fwd + 7)]

    def getEventsForCalendar(self, month, year, **kw):
        """ Recreates a sequence of weeks, by days each day is a mapping.
            {'day': #, 'url': None}
        """
        year = int(year)
        month = int(month)
        # daysByWeek is a list of days inside a list of weeks, like so:
        # [[0, 1, 2, 3, 4, 5, 6],
        #  [7, 8, 9, 10, 11, 12, 13],
        #  [14, 15, 16, 17, 18, 19, 20],
        #  [21, 22, 23, 24, 25, 26, 27],
        #  [28, 29, 30, 31, 0, 0, 0]]
        daysByWeek = self._getCalendar().monthcalendar(year, month)
        weeks = []

        events = self.catalog_getevents(year, month, **kw)

        for week in daysByWeek:
            days = []
            for day in week:
                if events.has_key(day):
                    days.append(events[day])
                else:
                    days.append({'day': day, 'event': 0, 'eventslist': []})

            weeks.append(days)

        return weeks



    def catalog_getevents(self, year, month, **kw):
        """ given a year and month return a list of days that have events
        """
        # XXX: this method violates the rules for tools/utilities:
        # it depends on a non-utility tool
        year = int(year)
        month = int(month)
        last_day = self._getCalendar().monthrange(year, month)[1]
        first_date = self.getBeginAndEndTimes(1, month, year)[0]
        last_date = self.getBeginAndEndTimes(last_day, month, year)[1]

        query_args = {
            'portal_type': self.getCalendarTypes(),
            'review_state': self.getCalendarStates(),
            'start': {'query': last_date, 'range': 'max'},
            'end': {'query': first_date, 'range': 'min'},
            'sort_on': 'start'}
        query_args.update(kw)

        ctool = getToolByName(self, 'portal_catalog')
        query = ctool(**query_args)

        # compile a list of the days that have events
        eventDays={}
        for daynumber in range(1, 32): # 1 to 31
            eventDays[daynumber] = {'eventslist': [],
                                    'event': 0,
                                    'day': daynumber}
        # prepare occurences
        all_events_occurences = []
        for result in query:
            # TODO: avoid getobject, let occurences be a property of the event object and indexed as metadata?
            occurences = result.getObject().occurences(first_date, last_date)
            for occurence in occurences:
                all_events_occurences.append(
                        dict(event=result,
                             start_date = occurence[0],
                             end_date = occurence[1]))

        for occurence in all_events_occurences:
            # TODO: 4 lines below need to be removed. Does this break anything?
            # It seems they are not needed: why would the catalog return
            # one event multiple times?
            # if occurence['event'].getRID() in includedevents:
            #     break
            # else:
            #     includedevents.append(occurence['event'].getRID())
            event={}
            # we need to deal with events that end next month
            if occurence['end_date'].month != month:
                # doesn't work for events that last ~12 months
                # fix it if it's a problem, otherwise ignore
                eventEndDay = last_day
                event['end'] = None
            else:
                eventEndDay = occurence['end_date'].day
                event['end'] = occurence['end_date'].strftime('%H:%M:%S')
            # and events that started last month
            if occurence['start_date'].month != month:  # same as above (12 month thing)
                eventStartDay = 1
                event['start'] = None
            else:
                eventStartDay = occurence['start_date'].day
                event['start'] = occurence['start_date'].strftime('%H:%M:%S')

            event['title'] = occurence['event'].Title or occurence['event'].getId

            if eventStartDay != eventEndDay:
                allEventDays = range(eventStartDay, eventEndDay+1)
                eventDays[eventStartDay]['eventslist'].append(
                        {'end': None,
                         'start': occurence['start_date'].strftime('%H:%M:%S'),
                         'title': event['title']})
                eventDays[eventStartDay]['event'] = 1

                for eventday in allEventDays[1:-1]:
                    eventDays[eventday]['eventslist'].append(
                        {'end': None,
                         'start': None,
                         'title': event['title']})
                    eventDays[eventday]['event'] = 1

                if occurence['end_date'] == occurence['end_date'].replace(hour=0, minute=0, second=0):
                    last_day_data = eventDays[allEventDays[-2]]
                    last_days_event = last_day_data['eventslist'][-1]
                    last_days_event['end'] = (occurence['end_date']-1).replace(hour=23, minute=59, second=59).strftime('%H:%M:%S')
                else:
                    eventDays[eventEndDay]['eventslist'].append(
                        {'end': occurence['end_date'].strftime('%H:%M:%S'),
                         'start': None, 'title': event['title']})
                    eventDays[eventEndDay]['event'] = 1
            else:
                eventDays[eventStartDay]['eventslist'].append(event)
                eventDays[eventStartDay]['event'] = 1
            # This list is not uniqued and isn't sorted
            # uniquing and sorting only wastes time
            # and in this example we don't need to because
            # later we are going to do an 'if 2 in eventDays'
            # so the order is not important.
            # example:  [23, 28, 29, 30, 31, 23]
        return eventDays

InitializeClass(CalendarTool)
