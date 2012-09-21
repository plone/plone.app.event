Changelog
=========

1.0b1 (unreleased)
------------------

- Limit the amount of occurrences in the event view if the event yields
  more than 7 occurrences. Show only 6 occurrences and the last
  occurrence.
  [romanofski]

- More minor fixes:
  * Don't force DateTime conversion in query parameters of get_portal_events.
    The catalog index uses Python's datetime anyways.
  * Only set end date in _prepare_range to next day, if it's a date and not
    datetime.
  * Register the Archetypes postprocessing event subscribers also for
    IObjectCreatedEvent.
  [thet]

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
  See: https://github.com/collective/plone.app.event/pull/47
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
