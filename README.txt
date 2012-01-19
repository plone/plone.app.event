Introduction
============

Event content type, browser views, utilities and portlets for Plone.
The event content type supports whole day events and recurrences based on
RFC2445.

It replaces the ATContentType event impementation and provides dexterity
behaviors. The ATContentType and dexterity features are automatically enabled
depending on installed packages.


Tryout / Installation
=====================

Build with buildout.cfg:

$ python bootstrap.cfg -d

$ ./bin/buildout -c buildout.cfg  # for normal building

- or -

$ ./bin/buildout -c dev.cfg  # for development building with R/W checkouts


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
