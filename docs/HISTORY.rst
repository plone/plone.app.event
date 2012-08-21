Changelog
=========

1.0a3 (unreleased)
------------------

- Calendar portlet search links now use @@search (from plone.app.search)
  instead of (since Plone 4.2) deprecated ./search (search.pt).  Requires
  recent plone.app.search changes.
  [seanupton]

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

- For dexterity behaviors, use a custom behavior adapter to store attributes
  directly on the context. This fixes that recurrence occurrences start and end
  dates were not indexed, because the DateRecurringIndex had not access to the
  recurrence attribute.
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
