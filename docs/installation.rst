Installation
============

Compatibility
-------------

plone.app.event is tested with latest Plone 4.2, Plone 4.3 and the upcoming
Plone 5.0.


Installation
------------

Depend on one (or both) of these setuptools dependencies::

    'plone.app.event [dexterity]'

or::

    'plone.app.event [archetypes]'


The zcml dependency is be loaded automatically by z3c.autoinclude.

Then install plone.app.event via the controlpanel or by depending on one or
both of these GenericSetup profiles in metadata.xml::

    plone.app.event.at:default

or::

    plone.app.event.dx:default


Plone 4.2 and 4.3 note
----------------------

plone.app.event depends on ``plone.app.portlets>=2.5a1``. This version has the
calendar and event portlet removed, which are now in plone.app.event itself.
Also, it allows the calendar portlet to do AJAX calls without KSS via standard
jQuery. For Plone < 5.0 you have to fix the plone.app.portlets version in your
buildout like so::

    [buildout]
    versions = versions

    [versions]
    plone.app.portlets = 2.5a1


Configuration
-------------

.. note::

  Don't forget to set the portal timezone!

After installation, please set your timezone in the @@event-settings
controlpanel. Otherwise time calculations are based on UTC and likely wrong for
your timezone.


Upgrading from Products.ATContentType to plone.app.event
--------------------------------------------------------

.. warning::

  Please backup before upgrading and check the upgraded contents for validity!

If you want to upgrade Products.ATContentTypes based ATEvents to
plone.app.event ones, there is an upgrade step for that: "Upgrades old AT
events to plone.app.events" (Metadata version 1 to 2).

