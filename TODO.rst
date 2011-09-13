TODO artsprint 2011
===================

legend:
OK ... that item is done
IP ... that item is in progress



* quick fix plone.formwidget.datetime
* integrate sean upton's uu.smartdate / http://bazaar.launchpad.net/~upiq-dev/upiq/uu.smartdate/changes

#########
$ grept start_date parts/omelette/*
$ grept cmfalendar parts/omelette/*
* remove start_date, add dtstart
* more ICalendar fields

* move parts/omelette/Products/CMFPlone/skins/plone_form_scripts/validate_start_end_date.vpy
  to plone.formwidget.dateinput

* permissions of cmfcalendar in plone.app.event
* remove cmfcalendar

* make generic ical adapter.
* to_ical method into event content type. method may use more generic one.

IP * rrule freq must be present. make/update validator with that.

* atevent tests with recurrence

* notify(ObjectModifiedEvent(event)) has always to be called manually if object
isn't modified by a form. is that failure proof?

POSSIBLE TASKS FOR Zidanca Sprint 2011
======================================

- Bring pone.formwidget.dateinput forward. Fix tests, finish the merge of
archetypes.datetimewidget and collective.z3form.datetimewidget.

- Fix tests for refactored plone.app.event.

INFO: plone.app.event and plone.formwidget.dateinput were refactored to have
seperated at and dx/z3cform submodules. All functionality dependend on AT or DX
respectively z3cforms, should reside in those subpackages, so that they can
easily be switched off.



HIGH PRIORITY
=============

general
-------
IP - use icalendar instead of plone.rfc5545 / plone.event
IP - Refactor plone.app.event for usage of an subpackage "at" (later also "dx")
  where all ATCT (later also dexterity) related stuff resides.
- remove recurrence dependency in plone.app.event. makes shipping of first
  release easier.

documentation
-------------
- plip documentation
- document daterecurringindex benchmark results
- document TZ behavior with examples
- document removal of ICalendarSupport (interface for ical export ability) in
  plone.app.event.interfaces. MAYBE provide that interface in ATContentTypes
  for backwards compatibility

daterecurringindex
------------------
- usage of IIBTree - see discussion on plone-dev
test if IIBTrees or set are faster
>>> ts = time.time(); b=difference(IISet(a), IISet(b)); time.time() - ts
0.014604091644287109
>>> ts = time.time(); b=set(a) - set(b); time.time() - ts

timezone support
----------------
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
IP - archetypes.datetimewidget, collective.z3cform.datetimewidget -> merge into
  plone.formwidget.dateinput

portlet stuff (plone.app.event.portlets.calendar)
-------------

- calendar portlet should use jquery tools calendar. maybe construct portlet,
  so that a viewlet can also use calendar via metal:macros.
  NOTE: calendar portlet works now with recurring events. that work was done
  at bssp2011.
- review and cleanup

ATEvent
-------
- error when submitting random data to recurrence field. catch dateutil's
  error and raise validation error. display error as error message.
  NOTE: that work was done at bssp2011. integration still to be done (comes
  soon)

Testing
-------
- move tests to plone.app.testing
- improve jenkins integration


cleanup
-------
* remove all vcal references in favor or ical
* remove portal_skins/plone_content/event_view.pt
* remove portal/icon_export_vcal.png
* label_add_to_vcal



low priority
============

more cleanup
------------
- ditch Products.CMFCalendar, if possible.
- move portal_calendar from Products.CMFPlone into plone.app.event

timezone
--------
- eventually provide configlet to configure TZ per user
  user should be able to select his timezone in user properties

- allow no TZ setting on content context at all - this solves "world plone
  day" problem (event in different timezones, whole day in every timezone)

controlpanel
-------------
- merge calendar and plone.app.event portlet.
  uninstall calendar configlet, install p.a.event -> upgrade step

recurrence widget
-----------------
- recurrence widget.
- disable recurrence for now: hide the recurring field .. add it later, per
  profile or so.

migration steps
---------------
* if default timezone is not set, migration cannot run
- migration from old ATEvent
* Check if any upgrade steps are neccassary for changed permission names (see
  config.py)

plip buildout
-------------
- there are git:// and git@ checkouts for ppl without/with rw permissions.
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
- provide it.

- when dexterity becomes one day the default content type framework, we won't
  depend on AT anymore... maybe the package layout should be respect that *now*
    - done with setuptools and zcml extras


done
====

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



internal notes for thet, forget this..
--------------------------------------
- isSameDay, isSameTime -... taking event as parameter. change to date1, date2
- toDisplay, doing nearly the same as function below. factor out a to_display
function which can used in both
- fix portal_calendar or filtered occurences. calendar portlet is showing event
  from previous month every day.
- avoid dependency on portal_calendar or bring that tool in here.


