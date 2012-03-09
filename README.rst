plone.app.event
===============

Plone.app.event is the calendaring implementation for Plone. It provides Event
Content Types (Archetypes based as well as Dexterity Behaviors), Timezone
support, RFC5545 icalendar export, Recurrence support and a lot more.

The ATContentType and dexterity features are automatically enabled depending
on installed packages.


Installation for Plone 4.1
--------------------------

To install plone.app.event for Plone 4.1, please use the
plone.app.event-ploneintegration package. Include it in your buildout config or
in your integration package's setup.py and apply the 
"plone.app.event Plone4 integration" profile.
The plone.app.event-ploneintegration package pulls all dependencies, which are
needed for plone.app.event.


Warning
-------

!!!
Backup! Don't do this on a Plone setups in production, only install
plone.app.event for new setups or report any upgrade issues. Upgrading is yet
not tested and no upgrade steps are provided - this is still a task to do.
Expect weired behavior regarding date/time/timezones and any other bugs.
!!!


Bug reporting
-------------

Please report bugs here: https://github.com/collective/plone.app.event 

This url may change to https://github.com/plone/plone.app.event some time soon!


Installation from the sources
-----------------------------

If you want to install plone.app.event from the sources for development, run
the provided buildout files - and read the sources.

$ python bootstrap.cfg -d

$ ./bin/buildout -c buildout.cfg  # for normal building

- or -

$ ./bin/buildout -c dev.cfg  # for development building with R/W checkouts

There is also a dexterity.cfg buildout configuration, which can be used to
extend another buildout and install the Dexterity flavor of plone.app.event.


Start:

$ ./bin/instance fg

After fireing up the Zope instance, visit the ZMI and create a Plone site.
The plone.app.event's Archetypes profile would automatically be installed due
to the Products.CMFPlone branch, but please import plone.app.event's dexterity
profile also. This way, the dexterity behaviors are registered and an example
Dexterity event type is installed.


Contributions
-------------
Philip Bauer, <bauer@starzel.de>
Jure Cerjak, <jcerjak@termitnjak.si>
JeanMichel FRANCOIS, <toutpt@gmail.com>
Vincent Fretin, <vincent.fretin@gmail.com>
Rok Garbas, <rok.garbas@gmail.com>
Tom Gross, <itconsense@gmail.com>
Andreas Jung, <lists@zopyx.com>
Jens Klein, <jens@bluedynamics.com>
Ryan Northey, <ryan@3ca.org.uk>
Simone Orsi, <simahawk@gmail.com>
Vitaliy Podoba, <vitaliypodoba@gmail.com>
Johannes Raggam, <johannes@raggam.co.at>
Lennart Regebro, <regebro@gmail.com>
Mike Rhodes, <mike.rhodes@gmail.com>
Dorneles Tremea, <dorneles@tremea.com>
Nejc Zupan, <nejc.zupan@niteoweb.com>
Giacomo Spettoli, <giacomo.spettoli@gmail.com>
Taito Horiuchi, <taito.horiuchi@hexagonit.fi>


and possibly many many more...
