legend:
OK ... that item is done
IP ... that item is in progress


INFO: plone.app.event and plone.formwidget.dateinput were refactored to have
seperated at and dx/z3cform submodules. All functionality dependend on AT or DX
respectively z3cforms, should reside in those subpackages, so that they can
easily be switched off.


TODO, thet's next
=================
* use p.a.event.base.get_portal_events all over, where needed (e.g. event
  portlet)
* make ical adapters for dx based types
    . remove adapters for IATFolder, etc. since IFolder does the same.
    . can you use IFolder also for IDexterityContainer objects?
* begin with developer's documentation
* refactor for and put some stuff into plone.event or drop that package.
* fix vincent's dt-javascript's, which are failing now
* create z3cform based recurrence widget for use with dx types
* integrate lennart's plone.app.eventindex

TODO, future
============

- provide caldav support, using webdav. make Zope2.webdav obsolete and use
  z3c.dav or wsgidav or whatever.

- Integrate RSVP - Resource reSerVation Protocol (IP, RFC 2205)

TODO, bigger
============

* Use VTIMEZONE compoenent and TZID properties in ical exports for every
  date/datetime

* Rethink the catalog metadata entries. ADD whole_day (Solegma asked for it).

* Factor out generic methods without plone.app.* or Zope2 dependencies and move
  them to plone.event.
  - Cleanup plone.event for unused methods
  - Cleanup plone.event for critical dependencies.

- integrate a localized, nice formated duration function

OK - thet - ditch Products.CMFCalendar, if possible.
    in branch - merge-CMFCalendar

    cmfcalendar seems to be only used by calendarportlet.
    $ grept cmfalendar parts/omelette/*

    OK - thet - calendarportlet: refactoring for removed portal_calendar dependency and 
      new plone.app.event.base based approach.
        NO - calendar portlet using jquery tools calendar?
        - template change, so that a viewlet can also use calendar via
          metal:macros.

    - deprecate/remove portal_calendar from Products.CMFPlone

    OK - thet - merge calendar and plone.app.event portlet.
    OK - reimplement important functionality from calendar configlet
        -> upgrade step
    - Remove calendar configlet from plone.app.controlpanel


* add more ICalendar fields to create an generic interface to event content
  types
  - eventually ditch start_date and end_date, replacing them with more RFC5545
    names dtstart, dtend...
    !!! probably NOT. that might cause trouble.
    !!! on the other hand... it's not used anyways and the api changed from pre
    plone.app.event ATEvent implementation anyways...
    $ grept start_date parts/omelette/*

* permissions of cmfcalendar in plone.app.event
  or REMOVE those permissions, using at/dx seperated ones - event if their name
  is more generic? martin says in his book, that cmfcalendar permissions are an
  historical accident. upgrade step probably needed.

IP - thet (regebro) * finish icalendar 3.0 branch, where __str__ isn't used
  - to_ical method into event content type. method may use more generic one.

OK - thet (regebro) * rrule freq must be present. make/update validator with that.

OK - thet * make generic ical adapter.

IP - supton * merge sean upton's uu.smartdate with plone.formwidget.datetime
  http://bazaar.launchpad.net/~upiq-dev/upiq/uu.smartdate/changes

IP - taito * Bring pone.formwidget.dateinput forward. Fix tests, finish the merge of
  archetypes.datetimewidget and collective.z3form.datetimewidget.

IP - regebro - brong forward plone.formwidget.recurrence and jquery.recurrence


upgrade / migration steps
-------------------------
* portlets renamed, fix it in old instances: event -> portlet_event, calendar ->
portlet_calendar (calendar is a python module.)
maybe not needed, since legacy calendar and event modules left in
plone.app.portlets.

* if default timezone is not set, migration cannot run
- migration from old ATEvent
* Check if any upgrade steps are neccassary for changed permission names (see
  config.py)


Notes, don't forget
===================

* DX: when calculating default_end time at 23:xx, its 0:xx. the hour component
  isn't displayed in the datetime widget.

* Check ordering of schema fields.

* Fix tests for refactored plone.app.event.
* atevent tests with recurrence

* plone.app.event.browser.event_view.pt -> eventually make view more generic
  and usable for dx also... by replacing widget-calls

* move parts/omelette/Products/CMFPlone/skins/plone_form_scripts/validate_start_end_date.vpy
  to plone.formwidget.dateinput

* notify(ObjectModifiedEvent(event)) has always to be called manually if object
isn't modified by a form. is that failure proof?

* remove portal_skins/plone_content/event_view.pt

* remove portal/icon_export_vcal.png

* label_add_to_vcal


More
====

documentation
-------------
- plip documentation
- document daterecurringindex benchmark results
- document TZ behavior with examples
- document removal of ICalendarSupport (interface for ical export ability) in
  plone.app.event.interfaces. MAYBE provide that interface in ATContentTypes
  for backwards compatibility

general
-------
- remove recurrence dependency in plone.app.event. makes shipping of first
  release easier.
  - disable recurrence for now: hide the recurring field .. add it later, per
  profile or so.

OK - garbas/thet - use icalendar instead of plone.rfc5545 / plone.event

OK - thet - Refactor plone.app.event for usage of an subpackage "at" (later
    also "dx") where all ATCT (later also dexterity) related stuff resides.
    when dexterity becomes one day the default content type framework, we won't
    depend on AT anymore...


daterecurringindex
------------------
- usage of IIBTree - see discussion on plone-dev
test if IIBTrees or set are faster
>>> ts = time.time(); b=difference(IISet(a), IISet(b)); time.time() - ts
0.014604091644287109
>>> ts = time.time(); b=set(a) - set(b); time.time() - ts


timezone support
----------------
- eventually provide configlet to configure TZ per user
  user should be able to select his timezone in user properties

- allow no TZ setting on content context at all - this solves "world plone
  day" problem (event in different timezones, whole day in every timezone)

- GenericSetup import profile for setting the default timezone on install time
  (and upgrade time as well).
- if no timezone is selected: same as mail settings: note in nonfig area - at least
  display in edit form to link in control panel.
FIXES:
- on fresh install, when creating an event - no timezones are configured and
  cannot be selected - but are mandatory. at least a default timezone has to
  be selected in the event-settings configlet. that should be set at install
  time.


datetimewidget
--------------
- calendar starting year, calendar future years options in datetimewidget.

OK - thet - archetypes.datetimewidget, collective.z3cform.datetimewidget -> merge into
  plone.formwidget.dateinput

Testing
-------
OK/IP (check again) - thet - move tests to plone.app.testing
- improve jenkins integration

cleanup
-------
OK/IP (check again) * remove all vcal references in favor or ical

plip buildout
-------------
OK - thet - here are git:// and git@ checkouts for ppl without/with rw permissions.
  maybe https handles both?

ATEvent
-------
- "no end date" boolean option
- [X] recurrence field goes after end date.
  [ ] hide text area with css display:none
  [X] remove schemata recurrence
  [ ] provide checkbox "this date recurrs ..." and toggle textarea then

DXEvent
-------
IP - provide it. providing behaviors, based on plone.app.page


done
====

OK * dependency on plone.folder as well as plone.app.collection are only for
  registering ical adapters and might make backporting harder than neccassary.
  optional via zcml:condition

OK * p.a.event tests: ATEvent cannot be created - the factory method is not created... investigate.

OK - datetimewidget calendar images missing...
OK - new TZ field on ATEvent. store all dates in UTC timezone. store TZ extra.
   display dates in user's timezone (via TZ fetcher utility). use getter and
   setter to calculate timezones (get: UTC-userTZ set: userTZ->UTC).
OK - provide configlet to configure portal's TZ. use dropdown for
   default_timezone and in-out-widget for allowed_timezones (which then are
   used to filter tz's with elephantvocabulary)
OK - plone.event -> TZ vocabulary
OK - plone.app.event -> TZ vocabulary based on elephantvocabulary filter
   get filtered items or display items from plone.registry

OK - TZ fetcher utility
  OK - plone.event: OS TZ
  OK - plone.app.event portal TZ
  - context, user, portal TZ

general
-------
OK - move buildout configs out of coredev/plip into p.a.event to be used
  independently
OK - merge branches with trunk

plip buildout
-------------
OK - there is a git checkout which isn't handled by mr.developer because it's no
  python package and thus could break. mr.developer supports co option
  egg=false ... use that.

daterecurringindex
------------------
OK - complete the benchmark products.daterecurringindex
OK - sync with hanno's changes to dateindex

timezone support
----------------
OK - provide widget for TZ field described above


ATEvent
-------
OK - jure - error when submitting random data to recurrence field. catch 
  dateutil's error and raise validation error. display error as error message.


internal notes for thet, forget this..
--------------------------------------
- isSameDay, isSameTime -... taking event as parameter. change to date1, date2
- toDisplay, doing nearly the same as function below. factor out a to_display
function which can used in both
- fix portal_calendar or filtered occurences. calendar portlet is showing event
  from previous month every day.
- avoid dependency on portal_calendar or bring that tool in here.


