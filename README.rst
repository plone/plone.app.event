plone.app.event
===============

Plone.app.event is the calendaring framework for Plone. It provides Dexterity behaviors and an Archetypes type, Timezone support, RFC5545 icalendar export, Recurrence support, event views and a lot more.

For a Dexterity event type using plone.app.event, use plone.app.contenttypes 1.1 or newer.

The complete documentation can be found on: https://ploneappevent.readthedocs.org


Installation
------------

For Standalone installation follow the standard buildout procedure::

    $ virtualenv .
    $ ./bin/pip install -U zc.buildout setuptools pip
    $ ./bin/buildout

Note, both commands will install a test and development environment.
