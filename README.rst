plone.app.event
===============

Plone.app.event is the calendaring implementation for Plone. It provides Event
Content Types (Archetypes based as well as Dexterity Behaviors), Timezone
support, RFC5545 icalendar export, Recurrence support and a lot more.

The ATContentType and dexterity features are automatically enabled depending
on installed packages.


.. note::
  Please set your timezone in the @@event-settings controlpanel. Otherwise
  there some weired behavior can occur, like you're apparently unable to set
  the time for dexterity types not to what you want.  For timezone handling, we
  use pytz.


Installation for Plone 4.2
--------------------------

Just run the buildout.cfg, which is included with plone.app.event. There is
also a dev.cfg buildout file, which includes the sources of Plone core
package branches with integration changes for plone.app.event.

Or include the plone.app.event egg::

  eggs +=
      plone.app.event [ploneintegration,archetypes,dexterity]

Last, instal Plone with the "plone.app.event Plone4 integration" profile or
depend in Generic Setup in metadata.xml like so::

  <dependency>profile-plone.app.event.ploneintegration:default</dependency>

You can also install optionally or additionally the dexterity profile.


.. warning::
  Upgrading from the old ATEvent type is not tested, so don't rely on this.

Add some events, play with recurrence, whole day events and timezones, try out
the calendar and event portlets...


.. note::
  A limitation on recurrence is, that unlimited occurrences are not supported
  at the moment. The number of possible recurrences of an event is limited to
  1000 at the moment, so indexing - and other operations - doesn't take too
  long (see: plone.event.recurrence).


PLIP implementation
-------------------

This packages and the other listed in sources.cfg are part of the PLIP 10886.
See: http://dev.plone.org/plone/ticket/10886


Contributing
------------

- Report issues: https://github.com/collective/plone.app.event
- Write code and tests.


.. note::
  Please note, allowing pull requests require the signation of the contributor
  agreement.
