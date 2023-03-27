================================================
plone.app.event - a calendar framework for Plone
================================================

.. topic:: Overview

    plone.app.event is a new calendar framework for Plone.

    Features:

    - Dexterity behaviors and Archetypes type,
    - Timezone support,
    - Recurring Events,
    - Whole day events,
    - Open end events (End on the same day),
    - Icalendar export,
    - Icalendar import,
    - Better calendar and events portlets,
    - An event listing and event detail view.


    It was developed with these goals in mind:

    - Encapsulation and independence: All event related code should reside in a single package. Relevant, re-usable functionality is split to separate packages.  Plone's dependencies on calendar related code should be reduced to a minimum. plone.app.event should be able to be deinstalled from Plone.

    - Dexterity and Archetypes support: plone.app.event should provide Dexterity behaviors, which can be used in Dexterity types and an ATEvent content type (factored out from ATContentTypes). For a Dexterity event type, use plone.app.contenttypes 1.1 or newer.

    - Standards compliance: We support the icalendar standard (`RFC5545 <http://tools.ietf.org/html/rfc5545>`_) including recurrence.

    - Recurring events based on the RFC5545 standard.


Documentation
=============

.. toctree::
    :maxdepth: 2

    installation.rst
    architectural-overview.rst
    development.rst
    tests.rst
    designchoices.rst


API documentation
=================

.. toctree::

    api/index.rst
