Installation
============

Depend on 'plone.app.event [dexterity]' or 'plone.app.event [archetypes]' or
both in your setup.py or buildout configuration.

You don't have to depend on plone.app.event in your configure.zcml, but if you
want to do so to make things explicit, just include the plone.app.event package
and no subpackage, as they are loaded automatically::

    <include package="plone.app.event"/>

.. note::
  After installation, please set your timezone in the @@event-settings
  controlpanel. Otherwise there some weired behavior can occur, like you're
  apparently unable to set the time for dexterity types not to what you want.
  For timezone handling, we use pytz.

.. note::

  Unlimited occurrences are not supported at the moment. The number of possible
  recurrences of an event is limited to 1000 occurrences. This way, indexing
  and other operations doesn't take too long.  The maximum number of
  occurrences is set via the ``MAXCOUNT`` constant in
  ``plone.event.recurrence``.


Using plone.app.event before Plone 4.4
--------------------------------------

If you want to install plone.app.event before Plone 4.4 (where it's included in
core), also depend on the ploneintegration extra: 'plone.app.event [archetypes,
ploneintegration]' (again, and/or 'dexterity').

Then - don't forget - run the plone.app.event.ploneintegration:default profile
once to re-register portlets, re-adding the DateRecurringIndex for start and
end indices and so on.

.. note::
  Run the "ploneintegration" profile only once (or after whole site-profiles
  are re-applied). Otherwise you have to clear and rebuild the index every
  time, because the start and end indices are removed and re-added

.. note::
  Currently the package ``z3c.unconfigure`` depends on ``zope.configuration >=
  3.8`` but Plone 4.2.4 uses zope.configuration 3.7.4. To successfully install
  plone.app.event with it's ploneintegration extra, you have to make a version
  fix in your buildout. Wether fix z3c.unconfigure to 1.0.1 (recommended and
  included in this buildout) or fix zope.configuration for example to 4.0.2
  (not backwards-compatible).


Upgrading from Products.ATContentType to plone.app.event
--------------------------------------------------------

.. warning::
  Content upgrades from the old ATEvent type are experimental, so don't rely
  on this.

If you want to upgrade Products.ATContentTypes based ATEvents to
plone.app.event ones, there is an upgrade step for that: "Upgrades old AT
events to plone.app.events" (Metadata version 1 to 2).

Please note, that this feature is still experimental. Report any upgrade issues
from old ATEvent types here: https://github.com/plone/plone.app.event/issues
