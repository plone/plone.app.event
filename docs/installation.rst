Installation
============

Compatibility
-------------

plone.app.event 2.0 is a rewrite of plone.app.event 1.x and fixes some issues.  See Changelog.rst.

The following is a compatibility map of all current plone.app.event versions:

===============  ======  ==========  =================  ======================  ==========
plone.app.event            Plone     plone.app.widgets  plone.app.contenttypes  Archetypes
---------------  ------  ----------  -----------------  ----------------------  ----------
version          branch
===============  ======  ==========  =================  ======================  ==========
1.1.x            1.1.x   Plone 4.3+         No                   1.1.x              Yes
1.2.x            1.2.x   Plone 4.3+      >= 1.4.0              < 1.2a3              Yes
2.x              master  Plone 4.3+      >= 1.7.0             >= 1.2a3              No
===============  ======  ==========  =================  ======================  ==========


Buildout files
--------------

- ``buildout.cfg``: Base installation for Plone 5.

- ``buildout-43.cfg``: Base installation for Plone 4.3.

- ``dev.cfg``: Development configuration, including tests, for Plone 5.

- ``test.cfg``: Test build for Plone 5.

- ``test-43.cfg``: Test build for Plone 4.3.

- ``sources.cfg``: mr.developer source definitions.

- ``versions.cfg``: Recommended version requirements.


Installation
------------

``plone.app.event`` only provides Dexterity behaviors to build own types based on them.  If you want to install a Dexterity based Event type, you can simply use ``plone.app.contenttypes`` 1.2a3 or up.

Depend on one (or both) of these setuptools dependencies::

    'plone.app.event'


The zcml dependency is be loaded automatically by z3c.autoinclude.

Then install plone.app.event via the controlpanel or by depending on the following GenericSetup profile in metadata.xml::

    plone.app.event:default


Upgrading from plone.app.event 1.x
----------------------------------

TODO: ...

There are upgrade steps in plone.app.contenttypes for 1.x to 2.0. That has to be revisited and refactored.


Upgrading from plone.app.event 1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TODO: ...

The "ploneintegration" setuptools extra, subpackage and GenericSetup profile have been gone. You just need to remove these dependencies from your setup and use the "plone.app.event.at:default" profile instead, if you plan to use the Archetypes based ATEvent type.

Use the provided upgrade steps to upgrade Dexterity behaviors: Attribute storage (Migrate fields from annotation storage to attribute storage) and New IRichText behavior (Enable the new IRichText instead of the IEventSummary behavior).


Upgrading from Products.ATContentType to plone.app.event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

  Please backup before upgrading and check the upgraded contents for validity!

If you want to upgrade Products.ATContentTypes based ATEvents to plone.app.event ones, there is an upgrade step for that: "Upgrades old AT events to plone.app.events" (Metadata version 1 to 2). In order to use it, go to Plone Control Center -> ZMI -> portal_setup -> Upgrades. Select "plone.app.event.at:default" profile and click "Show old upgrades". Select the upgrade step and run it.

You might also need to "clear and rebuild" the catalog after upgrading. You can do so at Plone Control Center -> ZMI -> portal_catalog -> Advanced (this may take a while)


Upgrading to Dexterity
~~~~~~~~~~~~~~~~~~~~~~

Upgrade steps to migrate Products.ATContentTypes based ATEvents, plone.app.event based ATEvents or plone.app.event Dexterity example types (plone.app.event.dx.event) to plone.app.contenttypes Dexterity Events can be found within plone.app.contenttypes. This package utilizes plone.app.event's Dexterity behaviors for it's Event type.


Configuration
-------------

.. note::

  Don't forget to set the portal timezone!

After installation, please set your timezone in the @@event-settings controlpanel. Otherwise time calculations are based on UTC and likely wrong for your timezone. Also set the first weekday setting for correct display of the first weekday in calendar views.
