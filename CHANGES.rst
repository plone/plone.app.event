Changelog
=========

1.0dev (unreleased)
-------------------

- Add open_end option for Dexterity behaviors and Archetypes type.
  [thet]

- For whole_day events, let dates_for_display return the iso-date
  representation from date and not datetime instances.
  [thet]

- Remove support of microseconds and default to a resolution of one second for
  all datetime getter/setter and conversions. Microseconds exactness is not
  needed and dateutil does not support microseconds which results in unexpected
  results in comparisons.
  [thet]

- Changing the timezone in events is a corner case, so the timezone field is
  moved to the "dates" schemata an ATEvent.
  [thet]

- Remove font-weight bold for monthdays and font-weight normal for table header
  in portlet calendar. Set div.portletCalendar with to auto instead of
  unnecessary 100% + margin. Align with plonetheme.sunburst.
  [thet]

- Let the IRecurrenceSupport adapter return the event itself, when the event
  starts before and ends after a given range_start. Fixes a case, where
  get_events didn't return a long lasting event for a given timeframe with
  expand set to True.
  [thet]

- Let the @@event_listing view work on IATTopic and ICollection contexts.
  [thet]

- In event_view, handle the case that the location field is not of type
  basestring but a reference to another object, for example provided by
  collective.venue.
  [thet]

- Use plone.app.event's MessageFactory for ATEvent.
  [thet]

- Let EventAccessor for Archetypes based content type return it's values from
  property accessors instead properties directly. This let's return the correct
  value when an property get's overridden by archetypes.schemaextender.
  [thet]

- Deprecate upgrade_step_2 to plone.app.event beta 2, which is likely not
  necessary for any existing plone.app.event installation out there.
  [thet]

- For the Archetypes based ATEvent migration step, do a transaction.commit()
  before each migration to commit previous changes. This avoids running out of
  space for large migrations.
  [thet]

- Let IEventAccessor adapters set/get all basestring values in unicode.
  [thet]

- Add and install plone.app.collection in test environment, as we cannot assume
  that it's installed.
  [thet]

- Re-Add cmf_edit method for ATEvent to ensure better backwards compatibility.
  Move related cmf_edit tests from Products.CMFPlone to plone.app.event.
  [thet]

- Add Event profile definition for ATEvent completly in order to remove it from
  Products.CMFPlone. ATEvent is installed by ATContentTypes automatically as
  part of upcoming plone.app.contenttypes merge.
  [thet]

- Optimize css by using common classes for event_listing and event_view.
  [thet]

- Add schema.org and hCalendar microdata to event_view and event_listing views.
  Fixes #2, fixes #57.
  [thet]


1.0b7 (2013-04-24)
------------------

- Don't show plone.app.event:default and
  plone.app.event.ploneintegration:prepare profiles when creating a Plone site
  with @@plone-addsite.
  [thet]

- Remove render_cachekey from portlet_events, since it depends on an
  undocumented internal _data structure, which must contain catalog brains.
  [thet]

- In tests, use AbstractSampleDataEvents as base class for tests, which depend
  on AT or DX event content.
  [thet]

- Introduce create and edit functions in IEventAccessor objects.
  [thet]

- API Refactorings. In base.py:
    * get_portal_events and get_occurrences_from_brains combined to get_events.
    * get_occurrences_by_date refactored to construct_calendar.
    * Renamings:
        - default_start_dt -> default_start,
        - default_end_dt -> default_end,
        - cal_to_strftime_wkday -> wkday_to_mon1,
        - strftime_to_cal_wkday -> wkday_to_mon0.

    * Remove:
        - default_start_DT (use DT(default_start()) instead),
        - default_end_DT (use DT(default_end()) instead),
        - first_weekday_sun0 (use wkday_to_mon1(first_weekday()) instead),
        - default_tzinfo (use default_timezone(as_tzinfo=True) instead).

  In ical:
    * Renamed construct_calendar to construct_icalendar to avoid same name as
      in base.py.

  BBB code will be removed with 1.0.
  [thet]

- Update translations and translate event_view and event_listing.
  [thet]

- Configure event_listing to be an available view on Collections, Folders,
  Plone Sites and Topics.
  [thet]

- Depend on plone.app.dextterity in ZCML, so that all DublinCore metadata
  behaviors are set up correctly.
  [thet]

- Backport from seanupton: IObjectModifiedEvent subscriber returns early on
  newly created event (Commit c60c8b521c6b1ca219bfeaddb08e26605707e17 on
  https://github.com/seanupton/plone.app.event).
  [seanupton]

- Calendar portlet tooltips css optimizations: max-with and z-index.
  [thet]

- Add Brazilian Portuguese translation
  [ericof]

- Add ical import feature, register action to enable it and add a object tab to
  the @@ical_import_settings form. .ics files can be uploaded or fetched from
  the net from other calendar servers.
  [thet]

- Since more ical related code is upcoming (importer), add ical subpackage and
  move ical related code in here.
  [thet]

- When exporting whole_day/all day events to icalendar, let them end a day
  after at midnight instead on the defined day one second before midnight. This
  behavior is the preferred method of exporting all day events to icalendar.
  [thet]

- Additionally to the 'date' parameter, allow passing of year, month and day
  query string parameters to the event_listing view and automatically set the
  mode to 'day' if a date was passed.
  [thet]

- Backport from plone.app.portlets: Don't fail on invalid (ambigous) date
  information in request (Commit a322676 on plone.app.portlets).
  [tomgross]

- Backport from plone.app.portlets: Use str view names for getMultiAdapter
  calls (commit c296408 on plone.app.portlets).
  [wichert]


1.0b6 (2013-02-14)
------------------

- Styles for event_listing date navigation.
  [thet]

- Add datepicker for day selection in event_listing view.
  [thet]

- Fix event_listing to search only for events in the current context's path.
  Allow "all" request parameter for no path restriction in searches.
  [thet]

- Backport change from seanupton: get_portal_events() fix: navroot path index
  incorrectly passed as tuple, now fixed to path string.
  [seanupton, thet]

- Fix get_portal_events to respect path for query if given in keywords.
  [thet]


1.0b5 (2013-02-11)
------------------

- Restore Python 2.6 compatibility by avoiding total_seconds method from
  timedelta instances in icalendar export.
  [thet]


1.0b4 (2013-02-08)
------------------

- Remove occurrences.html view because it's replaced by event_listing view.
  [thet]

- Changed Dexterity event-type title from "Event (DX)" to "Event" for
  consistent naming between Archetypes and Dexterity content types.
  [thet]

- Updated and synced translations (.pot and German translations).
  [thet]

- Use content-core fill/define metal definitions in all templates which use
  main_template's master macro.
  [thet]

- Calendar Portlet: Better portlet and tooltip styling. Drop usage of
  todayevent and todaynoevent classes. Fix Linking to calendar_listing.
  [thet]

- Event listing: Optimized layout and styles, mode switch, calendar-navigation,
  timespan header.
  [thet]

- Implement week and month mode for start_end_from_mode function.
  [thet]

- Add icalendar timezone support and properly export whole day events.
  Fixes #22, Fixes #71.
  [thet]

- Don't set icon_expr for the Dexterity content type and use css instead.
  [thet]

- Restore compatibility to Plone 4.3 by including the ploneintegration module
  also for Plone 4.3 but not 4.4.
  [thet]

- Version fix for z3c.unconfigure==1.0.1. This fix can be removed, once Plone
  depends on zope.configuration>=3.8.
  [thet]

- Add icon_export_ical.png from Products.ATContentTypes to plone.app.event.
  [thet]

- Configure first_day parameter for DateTime and Recurrence Widget (AT and DX).
  [thet]

- Configure the default_view of plone.app.event's ATEvent to be @@event_view.
  This prevents of referencing the old event_view from the plone_content skin
  layer to be used in some cases.
  [thet]

- Style the calendar portlet tooltips only for the calendar portlet.
  [thet]


1.0b3 (2012-12-18)
------------------

- Set the CalendarLinkbase urlpath to respect the search_base in calendar and
  event portlets.
  [thet]

- Depend on plone.app.portlets >= 2.4.0, since portlet_calendar needs the
  render_portlet view for it's ajaxification. This may break Plone 4.2
  integrations, until you make a buildout version fix.
  [thet]

- Remove dependency on Grok for the Dexterity behaviors.
  [thet]

- Just use classes instead of id's for the calendar portlet's page switcher.
  [thet]

- Reimplement the calendar page switcher from the calendar portlet with jQuery
  and remove the implicit dependency on KSS.
  [thet]

- Use event_listing instead of the search view in CalendarLinkbase for calendar
  and event portlets.
  [thet]

- Add new API functions:
  [thet]

  - date_speller to format a date in a readable manner,

  - start_end_from_mode to return start and end date accordin to a mode string
    (today, past, future, etc.),

  - dt_start_of_day and dt_end_of_day to set a date to the start of the day
    (00:00:00) and to the end of the day (23:59:59) for use in searches.

- Add new event_listing view to show previous, upcoming, todays and other
  events in a listing.
  [thet]

- Fix EventAccessor for ATEvent to correctly return the description.
  [thet]

- In portlet_calendar, grey-out previous and next month dates by making them
  transparent.
  [thet]


1.0b2 (2012-10-29)
------------------

- Fix ical export of RDATE and EXDATE recurrence definitions. Fixes #63.
  [thet]

- Align ATEvent more to Archetypes standards and avoid AnnotationStorage and
  ATFieldProperty. We needed to remove the ATFieldProperty for the timezone
  field for a custom setter. By doing so, the other two ATFieldProperties were
  changed too. This way, the ATEvent API gets more consistent. For a convenient
  access to ATEvent as well as dextterity based event types, use the
  IEventAccessor from plone.event.interfaces. Upgrade step from pre 1.0b2 based
  ATEvent types is provided.
  [thet]

- Treat start/end datetime input always as localized values. Changing the
  timezone now doesn't convert the start/end values to the new zone (AT, DX).
  [thet]

- Fix moving start/end dates when saving an unchanged DX event (issue #62).
  [thet]

- Portlet assignment fix. Now both - calendar and event portlet - are
  installed.
  [thet]


1.0b1 (2012-10-12)
------------------

- Add the calendar portlet by default when installing plone.app.event.
  [thet]

- Backport changes from "merge plip-10888-kss branch" in plone.app.portlets.
  KSS attributes still left in place for backwards compatibility.
  [thet]

- Buildout infrastructure update.
  [thet]

- Icalendar export of attendees almost according to the RFC5545 standard. At
  the moment, we do not distinguish between CN and CAL-ADDRESS in Plone, so we
  just put the attendee value to the CN and CAL-ADDRESS parameter. Fixes #24.
  [thet]

- Support microseconds for DateTime conversions. For recurrence rules,
  timezones are not supported due to a python-datetime limitation.
  [thet]

- Don't allow ambiguous timezones like 'CET', which also have implementation
  errors in DateTime. Force them to another zone. Timezones should be set
  explicitly anyways.
  [thet]

- Let EventOccurrenceAccessor return its own URL instead of its parent.
  Once again fixes #58.
  [thet]

- Fix calendar portlet header, which day names were shifted by one day since a
  incompatibility between the calendar module (0 is Monday) and the strftime
  function (0 is Sunday).
  [thet]

- Create an formated_date content provider, which takes an occurrence or event
  object when called and formats the start/end date and times for display. This
  content provider can be overridden for other contexts. E.g. the events
  portlet uses just shows the start date and not the end date.
  [thet]

- Let IRecurrenceSupport adapter's occurrences method return as first
  occurrence the event object itself instead of an Occurrence object.
  Fixes #58.
  [thet]

- Include plone.event's new configure.zcml.
  [thet]

- For the ATEvent type, use a more specific IATEvent interface with IEvent and
  P.ATCT's IATEvent as bases. So we can provide adapters, overriding more
  general IEvent adapting adapters.
  [thet]

- Don't show start occurrence in "More occurrences" section in event_view.
  [thet]

- Create adapter ICalendarLinkbase which returns links to calendar views and
  can be overridden through a more specific implementation by addon products.
  For example, the portlet_calendar and portlet_events links to the @@search
  view can be changed to URLs to a real calendar view, if one is installed.
  [thet]

- For portlet_calendar and portlet_events configuration, make the workflow
  state selection optional. If nothing is selected, all states are searched.
  [thet]

- Add search_base (select path to search for events) and state (select review
  state for events to search) to portlet_calendar settings and search_base to
  portlet_events.
  [thet]

- Limit the amount of occurrences in the event view if the event yields
  more than 7 occurrences. Show only 6 occurrences and the last
  occurrence.
  [romanofski]

- More minor fixes.
  [thet]

  * Don't force DateTime conversion in query parameters of get_portal_events.
    The catalog index uses Python's datetime anyways.

  * Only set end date in _prepare_range to next day, if it's a date and not
    datetime.

  * Register the Archetypes postprocessing event subscribers also for
    IObjectCreatedEvent.

- Fix #51, logical error with range_end parameter in get_portal_events.
  [thet]

- Fix test startup by not depending on getSite().translate, which is a
  filesystem script.
  [thet]

- Backport changes from davilima: Add safety check for False all_events_links.
  [davilima6]

- Make get_occurrences_by_date work for events which do not have
  IRecurrenceSupport (e.g. Dexterity events without the recurrence behavior).
  [thet]

- Don't run event handlers for ATEvent, if it doesn't provide IEvent.
  [thet]

- Fix utf-8 encoding problem with icalendar export.
  [rnix]

- Unregister ics_view for ATFolder and ATBTreeFolder as well in
  ploneintegration.
  [rnix]

- Workaround for buggy strftime with timezone handling in DateTime.
  See: https://github.com/plone/plone.app.event/pull/47
  [seanupton]

- Rebind portlet_calendar tooltips after ajax calendar reloads.
  [thet]

- Allow the refreshCalendar kss view also on Occurrence objects.
  [thet]

- Let portlet_events link to @@search for future and previous events for sites
  without the standard events folder.
  [thet]

- Moved docs/HISTORY.rst to CHANGES.txt.
  [seanupton]

- Calendar portlet search links now use @@search (from plone.app.search)
  instead of (since Plone 4.2) deprecated ./search (search.pt).  Requires
  recent plone.app.search changes.
  [seanupton]

- Integrate the plone.app.event-ploneintegration functionality for Plone
  versions without plone.app.event core integration (all current version)
  into this package for simplification.
  [thet]

- IEventSummary behavior added for body text on Dexterity event type,
  as well as a SearchableText indexer adapter for the Dexterity event
  type.
  [seanupton]

- Filter calendar portlet search URLs for each day to a whitelist of
  event portal_type values.  Prevents non-event add-on types with
  start/end fields from showing up in calendar, as defense against
  unintended consequences (add-ons could explicitly override this
  template if they define additional Event types).
  [seanupton]

- API refactoring:
  * Move all generic interfaces to plone.event,
  * Extend IEventAccessor adapters to also be able to set attributes.
  [thet]

- Copy plonetheme.sunburst styles for the calendar portlet to event.css. This
  way, the calendar portlet is nicely styled, even without sunburst theme
  applied.
  [thet]

- For Dexterity behaviors, use IEventRecurrence adapter to store attributes
  directly on the context.  This fixes that recurrence occurrences start and
  end dates were not indexed, because the DateRecurringIndex had not access to
  the recurrence attribute.
  [thet]

- IRecurrence adapter returns now acquisition-wrapped occurrence
  objects.
  [romanofski]

- Event portlet is now showing occurrences, sorted by start date.
  [romanofski]

- Moved whole_day field in directly after the end date to get a more logical
  group.
  [thet]

- Added dedicated timezone validator with fallback zone.

- Added traverser for occurrences. The event view is used to show
  individual occurrences.
  [romanofski]

- Broken paging in the calendar portlet has been fixed (#11).
  [romanofski]

- Make the start DateTime timezone aware and fix an issue where the start date
  was after the end date. Fixes: #8.
  [romanofski]


1.0a2 (2012-03-28)
------------------

- Add portlet GenericSetup registration for calendar and event portlet.
  [thet]

- API CHANGE: Use zope.annotation for behaviors, remove unnecessary factories,
  create IRecurrence adapter for access to occurrences.
  [thet]


1.0a1 (2012-03-12)
------------------

- Initial alpha release.
  [thet]
