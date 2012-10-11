**************************************************
plone.app.event - The Calendar Framework for Plone
**************************************************

.. topic:: Overview

    plone.app.event is a new calendar framework for Plone.

    Features:

    * Archetypes and Dexterity Type,
    * Timezone support,
    * Recurring Events,
    * Whole day events,
    * Icalendar export.

    It was developed with these goals in mind:
   
    - Encapsulation and independence: All event related code should reside in a
      single package. Relevant, re-usable functionality is split to seperate
      packages.  Plone's dependencies on calendar related code should be
      reduced to a minimum. plone.app.event should be able to be deinstalled
      from Plone.

    - Archetypes and Dexterity types: plone.app.event should provide the
      ATEvent content type (factored out from ATContentTypes) and also
      Dexterity behaviors, which can be used in Dexterity types.

    - Standards compliancy: We support the icalendar standard (RFC5545)
      including recurrence.
      
    - Recurring events based on the RFC5545 standard.
