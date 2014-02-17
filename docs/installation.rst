Installation
============

Compatibility
-------------

plone.app.event is tested with latest Plone 4.3 and the upcoming Plone 5.0.


Removed 4.2 compatibility
-------------------------

Since plone.app.event 1.1b1 we depend on changes from plone.app.contenttypes
1.1b1, which depends on plone.dexterity>=2.2.1 which itself (since 2.2) depends
on a AccessControl version not provided by the Plone 4.2 version fixes.

You can still experiment with Plone 4.2 compatibility if you need to, but
officially it's support in plone.app.event is removed. There are a number of
other compatibility issues to be solved and the tests will fail anyways. If you
really need to, use this as a starting point: `plone.app.dexterity =
2.0.10`, `plone.dexterity = 2.1.3`, `plone.app.contenttypes = 1.1a1`, `z3c.form
  = 3.0.5`, `plone.app.z3cform = 0.7.5`.


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


Plone 4.3 installation
~~~~~~~~~~~~~~~~~~~~~~

plone.app.event depends on ``plone.app.portlets>=2.5a1``. This version has the
calendar and event portlet removed, which are now in plone.app.event itself.
Also, it allows the calendar portlet to do AJAX calls without KSS via standard
jQuery. For Plone < 5.0 you have to fix the plone.app.portlets version in your
buildout like so::

    [buildout]
    versions = versions

    [versions]
    plone.app.portlets = 2.5a1


Upgrading from plone.app.event 1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "ploneintegration" setuptools extra, subpackage and GenericSetup profile
have been gone. You just need to remove these dependencies from your setup and
use the "plone.app.event.at:default" profile instead, if you plan to use the
Archetypes based ATEvent type.

Use the provided upgrade steps to upgrade Dexterity behaviors: Attribute
storage (Migrate fields from annotation storage to attribute storage) and New
IRichText behavior (Enable the new IRichText instead of the IEventSummary
behavior).


Upgrading from Products.ATContentType to plone.app.event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

  Please backup before upgrading and check the upgraded contents for validity!

If you want to upgrade Products.ATContentTypes based ATEvents to
plone.app.event ones, there is an upgrade step for that: "Upgrades old AT
events to plone.app.events" (Metadata version 1 to 2).

Upgrade steps to migrate Products.ATContentTypes based ATEvents,
plone.app.event based ATEvents or plone.app.event Dexterity example types
(plone.app.event.dx.event) to plone.app.contenttypes Dexterity Events can be
found within plone.app.contenttypes. This package utilizes plone.app.event's
Dexterity behaviors for it's Event type.


Configuration
-------------

.. note::

  Don't forget to set the portal timezone!

After installation, please set your timezone in the @@event-settings
controlpanel. Otherwise time calculations are based on UTC and likely wrong for
your timezone. Also set the first weekday setting for correct display of the
first weekday in calendar views.


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

You might also need to "clear and rebuild" the catalog after upgrading. You can
do so at Plone Control Center -> ZMI -> portal_catalog -> Advanced (this 
may take a while)
