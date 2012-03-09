plone.app.event overview
========================

plone.app.event
---------------
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
