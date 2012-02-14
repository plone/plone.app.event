Introduction
============

Plone.app.event is the calendaring implementation for Plone. It provides Event
Content Types (Archetypes based as well as Dexterity Behaviors), Timezone
support, RFC5545 icalendar export, Recurrence support and a lot more.

The ATContentType and dexterity features are automatically enabled depending
on installed packages.


Installation
------------

If you want to include plone.app.event in your Plone setup, include
wether the Archetypes or Dexterity or both extras of plone.app.event.

You can also install this package directly via the provided buildout
configuration:

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
=============
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
