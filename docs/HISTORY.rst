Changelog
=========

1.0a2 (2012-03-28)
------------------

- Added traverser for occurrences. The event view is used to show
  individual occurrences.
  [romanofski]

- Broken paging in the calendar portlet has been fixed (#11).
  [romanofski]

- Make the start DateTime timezone aware and fix an issue where the start date
  was after the end date. Fixes: #8.
  [romanofski]

- Add portlet GenericSetup registration for calendar and event portlet.
  [thet]

- API CHANGE: Use zope.annotation for behaviors, remove unnecessary factories,
  create IRecurrence adapter for access to occurrences.
  [thet]

1.0a1 (2012-03-12)
------------------

- Initial alpha release.
  [thet]
