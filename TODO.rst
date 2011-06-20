TODO artsprint 2011
===================

legend:
OK ... that item is done
IP ... that item is in progress

* remove vcal in favor or ical
* remove portal_skins/plone_content/event_view.pt
* remove portal/icon_export_vcal.png
* label_add_to_vcal

HIGH PRIORITY
=============

general
-------
OK - move buildout configs out of coredev/plip into p.a.event to be used
  independently
OK - merge branches with trunk
- remove recurrence dependency in plone.app.event. makes shipping of first
  release easier.

documentation
-------------
- plip documentation
- document daterecurringindex benchmark results
- document TZ behavior with examples


daterecurringindex
------------------
test if IIBTrees or set are faster
>>> ts = time.time(); b=difference(IISet(a), IISet(b)); time.time() - ts
0.014604091644287109
>>> ts = time.time(); b=set(a) - set(b); time.time() - ts

OK - complete the benchmark products.daterecurringindex
OK - sync with hanno's changes to dateindex

timezone support
----------------
OK - provide widget for TZ field described above

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
- archetypes.datetimewidget, collective.z3cform.datetimewidget -> merge into
  plone.formwidget.datetime
  at least rename to plone.f.datetimeinput..

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

plip buildout
-------------
OK - there is a git checkout which isn't handled by mr.developer because it's no
  python package and thus could break. mr.developer supports co option
  egg=false ... use that.
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
----
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

internal notes for thet, forget this..
--------------------------------------
- isSameDay, isSameTime -... taking event as parameter. change to date1, date2
- toDisplay, doing nearly the same as function below. factor out a to_display
function which can used in both
- fix portal_calendar or filtered occurences. calendar portlet is showing event
  from previous month every day.
- avoid dependency on portal_calendar or bring that tool in here.


