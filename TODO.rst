===========
PLEASE NOTE
===========

This file is for reference and will be removed when all relevant issues are
handled by the github issue tracker. Here are still some TODO's which should be
checked again.


======
legend
======

OK ... that item is done
IP ... that item is in progress
ISSUED ... moved to github tracker



TODO
====
OK - plone.app.collection: integrate, add relative time delta

ISSUED - generalize IRecurrence adapter. move out o' contenttypes and use generic
  event accessor to access event's attributes.

ISSUED - use generic event accessor also for ical serialization. no need for
  content-type specific adapters then.

ISSUED - plone.app.event.at in seperate egg...

ISSUED - GMT offsets have to be supported ... maybe a converter btw olson and GMT . look
into pytz for a converter

ISSUED - timezone getting/in which timezone is an event displayed. --/ document!
generic event aceesor : also for json...

whole day handler : good self speaking test cases, 

timezone of the request???
ISSUED - different timezone conversion strategies.... > display always in portal timezone, display in user timezone..., ...
ISSUED - prefix with _...

BUG
---

OK - recurring events: when searching for events within a timeframe, the
IRecurrence.occurrences method possibly returned a list where starts and ends
are of different lenght, leading into an error.  now, the end dates of the
occurrences list are calculated from the start date + a duration.

OK+Test: calendarportlet: unicodedecodeerror with umlauts in title, desc or location.


portlet_calendar
++++++++++++++++
- next/previous: overlay displays raw-overlay string
ISSUED - remove kss dependency, use jquery-only


PLONECONF TALk
--------------

ISSUED - fix icalendar timezone export

OK - plone.formwidget.datetime
OK -    fix for AT and DX

OK polish dx type
OK    integrate recurrence widget
OK    defaults for recurrencewidget.
OK    ical export

OK fix vincentfretin's start/end js (unify datetime templates for that?)

ISSUED - create uninstall profiles
OK - create pre-plone43 profiles (uninstalls default plone stuff)


thet
----

ISSUED thet - fix whole_day event export.... end-date is set startdate+1. in some cases end-date is two days after
start-date. this has something to do with utc conversion...
or set end-date to same date as start date, which is semantically more correct?

ISSUED FIRST: fix timezone support in icalendar export. then this issue is also gone.


thet - atevent: after changes to default_start and default_end, start+end is now 1,
  resp. 2 hours in future. check why

thet - add portlet_calendar and portlet_events on startpage (this one with unpublished and published events).

thet - show unpublished events as such in portlet_events and portlet_calendar


ical
----

ISSUED - ical export, dx types: UID not present in events

ISSUED - Use VTIMEZONE compoenent and TZID properties in ical exports for every
  date/datetime

ISSUED - Proper ATTENDEES support for icalendar export

OK - fix tests


datetime widget
---------------

WONTFIX - 1) - unify plone.formwidget.datetime templates

OK - 2) - fix vincent's dt-javascript's, which are failing now

- eventually merge supton's uu.smartdate with plone.formwidget.datetime
  http://bazaar.launchpad.net/~upiq-dev/upiq/uu.smartdate/changes

- DX: when calculating default_end time at 23:xx, its 0:xx. the hour component
  isn't displayed in the datetime widget.

- move parts/omelette/Products/CMFPlone/skins/plone_form_scripts/validate_start_end_date.vpy
  to plone.formwidget.dateinput or plone.app.event.

OK - years_range - calendar starting year, calendar future years options in datetimewidget.

ISSUED - option: use textinput style with fallback to selectors if no js is avail.

ISSUED - integrate timepicker (adapted from mozi)


recurring widget
----------------

- remove the leading zero 2nd method.


index
-----

- integrate lennart's plone.app.eventindex

OK (artsprint) - benchmarks for both indices

- usage of IIBTree - see discussion on plone-dev
test if IIBTrees or set are faster
>>> ts = time.time(); b=difference(IISet(a), IISet(b)); time.time() - ts
0.014604091644287109
>>> ts = time.time(); b=set(a) - set(b); time.time() - ts

- do we need to add the indices to ATContentTypes.criteria.__init__ indices
  Constants?

types
-----

ISSUED - uninstall profiles

- "no end date" boolean option


dexterity behaviors / types
---------------------------

OK - editing DX types with event behavior fails, since a tznaive DT is compared
    to timzone aware DT. see inline TODO statements.

- in metadata catalog, timezone'd times should reside, not un-timezone'd (see
    atevent)

- z3cform: for time 0:00, the hour is not displayed. when displaying, 12:00
    AM is shown.


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


documentation
-------------

- plip documentation

- document daterecurringindex benchmark results

- document TZ behavior with examples

- document api to get lsit of event

- sphinx API autodoc?

- document removal of ICalendarSupport (interface for ical export ability) in
  plone.app.event.interfaces. MAYBE provide that interface in ATContentTypes
  for backwards compatibility


general
-------

ISSUED - Factor out generic methods without plone.app.* or Zope2 dependencies and move
  them to plone.event.

OK - Solgema * recurrence widget dateinput is behind overlay

- integrate a localized, nice formated duration function

- Rethink the catalog metadata entries. ADD whole_day (Solegma asked for it).

- Generic icalendar types interfaces for event, journal, todo in plone.event

- Check ordering of schema fields.

OK - Refactor tests.

- the content types depend on event handlers.
  notify(ObjectModifiedEvent(event)) has always to be called manually if object
  isn't modified by a form. is that failure proof?

- eventually remove recurrence functionality for plip submission?

- improve jenkins integration


CMFPlone
--------

- remove portal_skins/plone_content/event_view.pt

- remove portal/icon_export_vcal.png

- remove label_add_to_vcal


CMFCalendar deprecation
-----------------------

- deprecate/remove portal_calendar from Products.CMFPlone

- migration steps

- Remove calendar configlet from plone.app.controlpanel

- provide an utility for portal-message/warning viewlet info, so that warnings
  can be injected and that warning-checker code must not be in the
  controlpanel-overview template anymore.

- permissions of cmfcalendar in plone.app.event, if possible - or drop em.
  martin says in his book, that cmfcalendar permissions are an historical 
  accident. upgrade step probably needed.


migration steps
---------------

- if default timezone is not set, migration cannot run

- migration from old ATEvent (catalog update)

- Check if any upgrade steps are neccassary for changed permission names (see
  config.py)


future
------

- provide caldav support, using webdav. make Zope2.webdav obsolete and use
  z3c.dav or wsgidav or whatever.

- Integrate RSVP - Resource reSerVation Protocol (IP, RFC 2205)



DONE
====

OK plone.forminput.recurrence * create z3cform based recurrence widget for use with dx types

OK * register sample DX event with event_view

OK * unify AT and DX event browser view

OK * use p.a.event.base.get_portal_events all over, where needed (e.g. event
  portlet)

OK * make ical adapters for dx based types
    OK . remove adapters for IATFolder, etc. since IFolder does the same.
    NO . can you use IFolder also for IDexterityContainer objects?

OK - DX events: calendar portlet breaks

OK - thet * support allday events in icalendar: export date-only, enddate+1day

OK - Cleanup plone.event for unused methods

OK - Cleanup plone.event for critical dependencies.

OK - thet - ditch Products.CMFCalendar, if possible.
    in branch - merge-CMFCalendar

    cmfcalendar seems to be only used by calendarportlet.
    $ grept cmfalendar parts/omelette/*

    OK - thet - calendarportlet: refactoring for removed portal_calendar dependency and 
      new plone.app.event.base based approach.
        NO - calendar portlet using jquery tools calendar?
        - template change, so that a viewlet can also use calendar via
          metal:macros.

    OK - thet - merge calendar and plone.app.event portlet.
    OK - reimplement important functionality from calendar configlet
        -> upgrade step

NO - eventually ditch start_date and end_date, replacing them with more RFC5545
    names dtstart, dtend...
    !!! probably NOT. that might cause trouble.
    !!! on the other hand... it's not used anyways and the api changed from pre
    plone.app.event ATEvent implementation anyways...
    $ grept start_date parts/omelette/*

OK - thet (regebro) * finish icalendar 3.0 branch, where __str__ isn't used
  - to_ical method into event content type. method may use more generic one.

OK - thet (regebro) * rrule freq must be present. make/update validator with that.

OK - thet * make generic ical adapter.

OK - regebro - bring forward plone.formwidget.recurrence and jquery.recurrence

OK * portlets renamed, fix it in old instances: event -> portlet_event, calendar ->
    portlet_calendar (calendar is a python module.)
   not needed, since legacy calendar and event modules left in
   plone.app.portlets.

OK * plone.app.event.browser.event_view.pt -> eventually make view more generic
  and usable for dx also... by replacing widget-calls

OK - garbas/thet - use icalendar instead of plone.rfc5545 / plone.event

OK - thet - Refactor plone.app.event for usage of an subpackage "at" (later
    also "dx") where all ATCT (later also dexterity) related stuff resides.
    when dexterity becomes one day the default content type framework, we won't
    depend on AT anymore...

OK - thet - archetypes.datetimewidget, collective.z3cform.datetimewidget -> merge into
  plone.formwidget.dateinput

OK - thet - move tests to plone.app.testing

OK - remove all vcal references in favor or ical

OK - thet - here are git:// and git@ checkouts for ppl without/with rw permissions.
  maybe https handles both?

OK - ATEvent
  [X] recurrence field goes after end date.
  [ ] hide text area with css display:none
  [X] remove schemata recurrence
  [ ] provide checkbox "this date recurrs ..." and toggle textarea then

OK - DX Events: Provide it. providing behaviors, based on plone.app.page

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

OK - move buildout configs out of coredev/plip into p.a.event to be used
  independently

OK - merge branches with trunk

OK - buildout: there is a git checkout which isn't handled by mr.developer because it's no
  python package and thus could break. mr.developer supports co option
  egg=false ... use that.

OK - index: complete the benchmark products.daterecurringindex

OK - index: sync with hanno's changes to dateindex

OK - TZ: provide widget for TZ field described above

OK - jure - ATEvent: error when submitting random data to recurrence field. catch 
  dateutil's error and raise validation error. display error as error message.

OK - in plone.event.utils now - isSameDay, isSameTime -... taking event as parameter. change to date1, date2

OK - toDisplay, doing nearly the same as function below. factor out a to_display
function which can used in both

OK - fix portal_calendar or filtered occurences. calendar portlet is showing event
  from previous month every day.

OK - avoid dependency on portal_calendar or bring that tool in here.
