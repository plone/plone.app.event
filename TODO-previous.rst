TODO
====

* There seems to be a problem with exclusion rulesets and timezones. There is
a possibility that different results for start and end dates are produced. This has
to be fixed (documented above in howto).

* Andreas Jung reported a problem where the enddate is incorrectly validated. This
has to be fixed.

- Check all packages for correct Licenses
- Add tests to ensure, DateRecurringIndex is actually installed.
- Make event.recurrence not an ATFieldProperty, since that is deprecated
- For recurring events, which have occurrences in the future, show future
occurrences first and hide past occurrences with javascript or so. Needs new
methods (next_occurrences, past_occurrences, next_occurence, previous_occurence)
in RecurrenceSupport event adapter.
- upgrade step for portlets move into plone.app.event. see traceback http://pastebin.com/YFyCytXg
- add <property name="index_naive_time_as_local">True</property> property for
  start and end indexes in catalog.xml as soon as P.DRI has that extra property
- write tests to check if events and calendar portlets work with recurrence. manual test was ok.
- add deprecation warnings for imports from ATContentTypes
- make BBB back-imports of CT, utilities, interfaces, etc in ATContentTypes and deprecate them
- leave utils.txt with it's date conversion functions and test_bugs.py back in
  P.ATCT, but deprecate them.
- upgrade step to recatalog the start and end indexes
- make calendar widget display (hidden) the timezone
- add a hook to getICal(), getVCal() for retrieving additional data
  from derived event types
- check how much sense start&end metadata columns in catalog.xml make sense.
  they return start&end of first occurence but nothing else.
  --> guess its used by folder_listing displaying start and end time from brain info.
- think about storing all dates in utc and converting them on display to
  localized time.
  usecase where this won't work: dates going over DST borders. like meeting from
  oktober-november shouldn't change the relative time

OUT OF SCOPE FOR NOW - let P.Archetypes set the timezone regarding the timezone
set in the request/user's browser.

OK - Make event.whole_day not an ATFieldProperty, since that is deprecated
OK - Check dependencies in setup.py for every package
OK - set start and end for wholedayevents to 0:00, resp, 23:59:59
         - test whole day event handler
OK - check display of recurring events
  OK - start date included twice
  OK - line breaks btw dates
  OK - recurrence dates wrongly displayed
OK - use plone.event.utils.pydt instead of DT2dt - it uses real timezones and
     converts the date to UTC if the timezone cant be retrieved (like: GMT+1
     is a GMT/UTC offset, but not a "real" timezone where daylight saving
     changes can be derived).
OK - update calendar-portlet and move it into plone.app.event
OK - update events-portlet and move it into plone.app.event
OK - actually test, if calendar and events portlets work with recurrence
OK - check use of MessageFactory. should message factory be in plone namespace?
  yes
OK - synchronize package with newest ATContentTypes (diff modified with trunk)
OK - clean up recurrence code and only use new rrulestring implementation
OBSOLETE - rename package to plone.app.calendar and create one for
    plone.calendar (e.g. for RFC2445 definitions)
OK - test for disabled recurrence and None values to store in recurrence field.
    see how index is behaving

Future
======
- integrate hcal microformat
- use plone.testing and plone.app.testing

TODO for Plone
==============
OK - depend on plone.app.event
Ok - include plone.app.event package in configure.zcml
OK - include plone.app.event in metadata.xml GS profile
OK - remove catalog index and metadata column and use those in plone.app.event
