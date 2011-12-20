plone.app.event notes for the Framework Team
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This document describes the current preview status of plone.app.event.

Notes on how to install it
==========================

Build it eather via buildout.coredev:

$ git clone git@github.com:plone/buildout.coredev.git
$ python ./bin/bootstrap.py
$ ./bin/buildout -c plips/plip10886-event-improvements.cfg

or directly with plone.app.event's buildout:

$ git clone git@github.com:collective/plone.app.event.git
$ python ./bin/bootstrap.py
$ ./bin/buildout -c dev.cfg

After fireing up the Zope instance, visit the ZMI and create a Plone site.
The plone.app.event's Archetypes profile would automatically be installed due
to the Products.CMFPlone branch, but please import plone.app.event's dexterity
profile also. This way, the dexterity behaviors are registered and an example
Dexterity event type is installed.


What do do
==========

* Go to the Control Panel and edit the event settings (you don't need to
  edit the calendar settings).

* Add an Event with some recurrence rule and other settings as you like.

* Publish it. You should see now the event in the event portlet.

* Click on it. You should also see every occurence listed.

* Download it as ical. You should be able to import it in Google Calendar too.

* Go to the start site and add an calendar portlet. In the portlet, you should
  see for every occurrence an entry. Place your mouse over one and you should
  see some details popping up.

* Add an Dexterity based Event (Event (DX)). Please fill everything correctly
  in the first place. You aren't able to edit it afterwards. This has to be
  bugfixed, see below. Publish the event.

* You should see the DX event in the event and calendar portlet too. Also the
  details page is the same as the one from ATEvent.

* Go to the site root and add ics_view to the url. All events in the portal -
  Dexterity and Archetypes based - should be exported as an icalendar file.
  Exporting Dexterity based events won't work in the Event-Collection, since
  the old Collection implementation does not support Dexterity based contents -
  IIRC.


Overview, status and code review
================================

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

The tests are all portet to plone.app.testing.

Status
------

Almost finished, but there are only few tests, which pass. Most of the time we
tried to keep all tests running through, but at the last refactoring effort i
had enough of alwys fixing the tests for a fast moving target. So all tests
have to be checked again and DX tests have to be written

Icalendar export cannot handle timezones yet, so all dates are converted to UTC
for this at the moment. This must be fixed, otherwise ical export is not really
usable.

Editing dexterity events after creating leads into errors, because
plone.formwidget.datetime returns a datetime instance without timezone
information, but we store datetimes with timezone information. Such dates
cannot be compared. Wether the z3cform package has to be fixed at that point to
be more forgiving at comparing datetime instances or plone.formwidget.datetime
has to be extended to optionally return datetime instances with a tzinfo
component - even if it's a dummy component.

We store the timezone in a seperate field, so use cases where an event starts
in one zone and ends in another cannot be done. All date/times are stored in
UTC and converted to the target zone (wether the event or the user's zone) when
accessed. We use pytz for timezone information. The timezone and the available
timezones (a subset of all timezones) can be configured in the control panel.
For the datetime vocabulary we use the elephantvocabulary to avoid problems
when removing an entry from the vocab at a later time.


plone.event
-----------

Date/time related utilities, recurrence calculations. Might still be updated
with some more generic interfaces from plone.app.event.


plone.formwidget.datetime
-------------------------

Derived from collective.z3cform.datetimewidget and archetypes.datetimewidget
(which itself was derived from the former). It is splitted into "at" and
"z3cform" subpackages, like plone.app.event. Still needs some testing and
polishing, but basically it's working.

plone.formwidget.recurrence
---------------------------

Lennart's recurrence widget, which works like the recurrence widget in Google
Calendar. The archetypes based widget is done and tested, but a z3cform based
must still be provided, so that the Dexterity types also can use it.

Products.DateRecurringIndex
---------------------------

A drop-in replacement for Zope's DateIndex with support for recurring events.
Each recurrence get's an index entry. It's tested and it works. Hanno said, in
order to be used in Plone core, we have to make use of some BTree data
structures and do some more performance testing. Indexing recurring events does
take longer than indexing non-recurring events.
Lennart Regebro created a plone.eventindex package with recurrence support and
lazy indexing, which is also tested and should work as a drop-in replacement as
well. I guess, we should switch over to it.


icalendar
---------

icalendar parser/generator framework from Max M, which was located on codespeak.
Rok Garbas maintains it from now on.
There is a 3.x branch which tries to unify the API and make it Python3
compatible. Tests are failing for this branch yet, so we use the current stable
one. Switching later should be easy...



Minor adaptions for plone.app.event
===================================

Products.CMFPlone
-----------------

Products.ATContentTypes
-----------------------

plone.app.portlets
------------------

Products.PloneTestCase
----------------------



