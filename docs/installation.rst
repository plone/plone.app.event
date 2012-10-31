Installation
============

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


Upgrading from previous versions of the plone.app.event ATEvent type
--------------------------------------------------------------------

If you have used plone.app.event before, it's good to know following things:

- The ATEvent type now implements plone.app.event.at.interfaces.IATEvent, which
  itself derives from Products.ATContentTypes.interfaces.IATEvent. In order to
  get the object_provides catalog metadata updated, please clear and rebuild
  your catalog.

- The ATEvent fields "recurrence", "timezone" and "wholeDay" now do not have
  ATFieldProperty definitions anymore and aren't stored in Annotations but
  directly on the context. The change was neccasary for the timezone field,
  since we had to implement a custom setter. Besides, it avoids confusion, that
  wholeDay has to be set as wholeDay for invokeFactory but as whole_day on the
  context itself.  There is an upgrade step, addressing this change ("Upgrade
  to plone.app.event beta2", from metadata version 2 to 3).


Upgrading from Products.ATContentType to plone.app.event
--------------------------------------------------------

If you want to upgrade Products.ATContentTypes based ATEvents to
plone.app.event ones, there is an upgrade step for that: "Upgrades old AT
events to plone.app.events" (Metadata version 1 to 2).

Please note, that this feature is still experimental. Please report any issues
with upgrading from old ATEvent types here:
https://github.com/plone/plone.app.event/issues
