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
plone.app.event-ploneintegration package from pypi. Include it in your buildout
config or in your integration package's setup.py and apply the "plone.app.event
Plone4 integration" profile.  The plone.app.event-ploneintegration package
pulls all dependencies, which are needed for plone.app.event.


Warning
-------

!!!
Backup! Don't do this on a Plone setups in production, only install
plone.app.event for new setups or report any upgrade issues. Upgrading is yet
not tested and no upgrade steps are provided - this is still a task to do.
Expect weired behavior regarding date/time/timezones and any other bugs.
!!!


What to do
----------
Add some events. Add some with recurrence - but limit the occurences or write
bug reports. Add some in different timezones and write bug reports. Add the
calendar portlet - shows published events. Write bug reports.

Go to the event controlpanel and try different settings. Download events as
ical. Install dexterity, apply the plone.app.event dexterity profile and start
using the provided behaviors.

If possible, write fix code and write tests.

Please note, allowing pull requests needs that she/he must have signed the
contributor agreement.


Known issues
------------
- Incomplete tests.
- There is may be one Unicode/Encoding issue with non-ascii chars when
  exporting to iCal.
- Allowing unlimited occurences for recurring events break at 30000 iterations
  and take a long time. Solution: not allowing unlimited occurences, breaking
  earlier.


Bug reporting
-------------

Please report bugs here: https://github.com/collective/plone.app.event 

This url may change to https://github.com/plone/plone.app.event some time soon!


Installation from the sources
-----------------------------

R/W checkout from github:
$ git clone git@github.com:collective/plone.app.event.github

R/O checkouts:
$ git clone git://github.com/collective/plone.app.event.git

If you want to install plone.app.event from the sources for development, run
the provided buildout files - and read the sources.

$ python bootstrap.cfg -d

For Plone 4.1 and standard ATContentTypes
$ ./bin/buildout -c alpha.cfg

- or -
Normal Building
$ ./bin/buildout -c buildout.cfg

- or -
For development building with R/W checkouts
$ ./bin/buildout -c dev.cfg

There is also a dexterity.cfg buildout configuration, which can be used to
extend another buildout and install the Dexterity flavor of plone.app.event.

Start
$ ./bin/instance fg

After fireing up the Zope instance, visit the ZMI and create a Plone site.
The plone.app.event's Archetypes profile would automatically be installed due
to the Products.CMFPlone branch, but please import plone.app.event's dexterity
profile also. This way, the dexterity behaviors are registered and an example
Dexterity event type is installed.

--
