Installation
============

Depend on one (or both) of these setuptools dependencies::

    'plone.app.event [dexterity]'

or::

    'plone.app.event [archetypes]'

The plone.app.event zcml dependency should be loaded automatically by
z3c.autoinclude.

Then install plone.app.event via the controlpanel or by depending on one or
both of these GenericSetup profiles::

    plone.app.event.at:default

or::

    plone.app.event.dx:default


.. note::

  After installation, please set your timezone in the @@event-settings
  controlpanel. Otherwise time calculations are based on UTC and likely wrong
  for your timezone.

.. note::

  For recurring events, we do not support unlimited occurrences. The number of
  possible recurrences of an event is limited to 1000 occurrences. This way,
  indexing and other operations doesn't take too long.  The maximum number of
  occurrences is set via the ``MAXCOUNT`` constant in
  ``plone.event.recurrence``.


Installing plone.app.event for Plone 4.2 or Plone 4.3
-----------------------------------------------------

.. note::

  plone.app.event depends on ``plone.app.portlets>=2.5a1``. This version has
  the calendar and event portlet removed, which are now in plone.app.event
  itself. Also, it allows the calendar portlet to do AJAX calls without KSS via
  standard jQuery. For Plone < 5.0 you have to fix the plone.app.portlets
  version in your buildout like so::

    [buildout]
    versions = versions

    [versions]
    plone.app.portlets = 2.5a1



Upgrading from Products.ATContentType to plone.app.event
--------------------------------------------------------

.. warning::

  Please backup before upgrading and check the upgraded contents for validity!

If you want to upgrade Products.ATContentTypes based ATEvents to
plone.app.event ones, there is an upgrade step for that: "Upgrades old AT
events to plone.app.events" (Metadata version 1 to 2).


Bug reports
-----------

Please report any bugs, issues or feature requests:
https://github.com/plone/plone.app.event/issues

And better yet, help out with pull-requests!
