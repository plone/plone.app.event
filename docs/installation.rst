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

Then install plone.app.event via the controlpanel or by depending on the
following GenericSetup profile in metadata.xml::

    plone.app.event:default

For Archetypes, use this one::

    plone.app.event.at:default

Don't use the ``plone.app.event.dx:default`` profile, which will be removed in
future versions of plone.app.event. Please create your own type based on
plone.app.event's Dexterity behaviors (Through the web or via a GenericSetup
profile), or install plone.app.contenttypes for ready-to-use Dexterity types.


Plone 4.2 and 4.3 installation
------------------------------

If you want to install plone.app.event before Plone 5.0 (where it's included in
core), also depend on the ploneintegration extra::

    'plone.app.event [dexterity, ploneintegration]'

or::

    'plone.app.event [archetypes, ploneintegration]'


Then run this profile along with the dx or at profile (described above)::

    plone.app.event.ploneintegration:default


.. note::

  plone.app.event depends on ``plone.app.portlets>=2.4.0``. This version allows
  the calendar portlet to do AJAX calls without KSS via standard jQuery. For
  Plone < 4.3 you have to fix the plone.app.portlets version in your buildout
  to a recent 2.4 version (see below).

  Currently the package ``z3c.unconfigure`` depends on ``zope.configuration >=
  3.8`` but Plone still uses zope.configuration 3.7.4. To successfully install
  plone.app.event with it's ploneintegration extra, you have to make a version
  fix in your buildout. Wether fix z3c.unconfigure to 1.0.1 (recommended and
  included in this buildout) or fix zope.configuration for example to 4.0.2
  (not backwards-compatible).

  The following shows an example buildout version fix::

    [buildout]
    versions = versions

    [versions]
    plone.app.portlets = 2.4.6
    z3c.unconfigure = 1.0.1


.. note::

    The ``ploneintegration`` setuptools extra and GenericSetup profiles are
    deprecated an will be removed with plone.app.event 1.1.


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
events to plone.app.events" (Metadata version 1 to 2). In order to use it, go
to Plone Control Center -> ZMI -> portal_setup -> Upgrades. Select 
"plone.app.event.at:default" profile and click "Show old upgrades". Select the
upgrade step and run it.

