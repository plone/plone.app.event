Changelog
=========

1.0a3 (unreleased)
------------------

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
