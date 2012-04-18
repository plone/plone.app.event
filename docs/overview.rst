plone.app.event overview
========================


Design goals
------------

The current event type is in need of a major overhaul. The intention of this
PLIP is to provide a new event engine by a major refactoring and
reimplementation:

  [a] Encapsulation and independence: All event related code should reside in a
  seperate package (splitted into other packages, where appropriate). Plone
  should be least dependend on plone.app.event. Best would be that one can
  deinstall this feature completly.

  [b] Archetypes and Dexterity awareness: plone.app.event should provide the
  ATEvent content type (factored out from ATContentTypes) and also Dexterity
  behaviors, which can be used in Dexterity types.

  [c] Standards compliancy: the iCalendar / RFC5545 standard is wonderful
  flexible, so plone.app.event should provide support for it by allowing ical
  exports. This is also available for the current ATContentType based
  implementation, but plone.app.event aims to improve it. Sometime it might
  also support iCalendar import and Plone could also act as a caldav server.

  [d] Recurring events support based on the RFC5545 standard.

  [e] A modern dateinput widget.

  [f] Features like whole-day-events.

  [g] Timezone support. 

Encapsulation and independence: plone.app.event provides the Archetypes based
type and the Dexterity behaviors via two other subpackages in that package: at
and dx. Based on installed features (Products.ATContentTypes or
plone.dexterity, respectively), eather of those subpackages are included via
the zcml:condition statement. The calendar and event portlets were moved from
plone.app.portlets into plone.app.event, where they belong semantically - thus
improving encapsulation and independence. The calendar portlet was completly
refactored. The functionality of the CalendarTool (portal_calendar) was
reimplenented. Important settings from the calendar-controlpanel are now
available in the event configlet. Since the calendar portlet was the only
consumer of the CalendarTool, the CalendarTool, the calendar controlpanel and
the dependency to Products.CMFCalendar can be dropped. The new
plone.formwidget.datetime implements archetypes and z3cform based widgets, so
the old datetime widget can be dropped. Python-dateutil provides recurrence
calculations based on the RFC5545 standard - plone.formwidget.recurrence
provides a awidget for recurrence and Products.DateRecurringIndex an
appropriate index as a drop-in replacement for Zope's DateIndex. The iCalendar
package was improved and is now used for plone.app.event to provide icalendar
serialization. The timezone support is based on the pytz package. Plone has to
define a portal timezone now and every event can define another timezone, if
wished. User timezones are planned. Whole day events get their starttime set to
0:00 and endtime set to 23:59:59 - thats should be feasable in most cases
(excluding any scientific events...).


plone.app.event package overview
--------------------------------

The "at" submodule provides the Archetypes based ATEvent content type as a
drop-in replacement of the ATContentType based ATEvent. Ical, recurrence and
generic event accessor adapters and some event subscribers related to the
ATEvent.

The "dx" submodule provides Dexterity behaviors (some granular ones) and a
Dexterity based content type (Generic Setup). Like in the "at" submodule, ical,
recurrence and generic event accessor adapters as well as some event
subscribers are provided.

Both subpackages are only loaded, if the neccassary features are installed.

plone.app.event does not depend on CMFCalendar and the portal_calendar tool
any more. Plone core's only consumer of this package was the calendar portlet
anyways, which was completly rewritten.

base.py provides some basic event related functionality. Many of them need a
context in order to get the correct timezone.

The "browser" submodule provides the new "event" controlpanel (the "calendar"
controlpanel can be dropped, since we do not need CMFCalendar any more). The
settings are stored in plone.registry.
The event view is generic to ATEvent and DX based event types.

The ical.py module provides adapters to build icalendar export files. The
icalendar export view "ics_view" is also in there.

There is also a "locales" directory which holds locale files. Well, this one
might should go into plone.app.locales, but on the other hand - it's best
placed in here in order to follow one of plone.app.event's design principles:
"everything related in one package, minimum dependencies to plone.app.event
from external packages."

In the portlets subpackage there are portlet_calendar (a complete rewrite) and
portlet_events, both from plone.app.portlets, where only BBB imports exist, so
that existing installations do not break.

The tests are all ported to plone.app.testing.


plone.event
-----------

Date/time related utilities, recurrence calculations.


plone.formwidget.datetime
-------------------------

Derived from collective.z3cform.datetimewidget and archetypes.datetimewidget
(which itself was derived from the former). It is splitted into "at" and
"z3cform" subpackages, like plone.app.event.


plone.formwidget.recurrence
---------------------------

Recurrence widget based on jquery.recurrenceinput.js. Supports complex
recurrence rules with exclusion and inclusion dates, automatically updated
occurrences display within the widget and a nicely formatted string which
explains the recurrence rule.
The recurrence rule is stored as a RFC5545/icalendar compatible recurrence
string.


Products.DateRecurringIndex
---------------------------

A drop-in replacement for Zope's DateIndex with support for recurring events.
Each recurrence get's an index entry.


plone.eventindex
----------------

A possible alternative to Products.DateRecurringindex, which supports late
indexing and which does not have problems with unlimited occurrences.


icalendar
---------

icalendar parser/generator framework.


Branches of core packages for plone.app.event
---------------------------------------------

* Products.CMFPlone
* Products.ATContentTypes
* plone.app.portlets
* Products.PloneTestCase
