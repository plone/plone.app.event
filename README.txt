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
$ ./bin/buildout -c buildout.cfg

Start:

$ ./bin/instance fg

Or add plone.app.event sources-ro.cfg or sources-rw.cfg to your plone 4.2
buildout.

Or use 
Sometime:
Add plone.app.event egg to your instance. (eventually include a zcml file).


Install plone.app.event and import ATContentType respectively the dexterity
profiles.



Contributions
=============
Philip Bauer, <bauer@starzel.de>
Jure Cerjak, <jcerjak@termitnjak.si>
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

and possibly many many more...
