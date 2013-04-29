Random, historical notes, too brilliant to delete
=================================================

Upgrading from previous versions of the plone.app.event ATEvent type
--------------------------------------------------------------------


If you have used plone.app.event before, it's good to know following things:

- The ATEvent type now implements plone.app.event.at.interfaces.IATEvent, which
  itself derives from Products.ATContentTypes.interfaces.IATEvent. In order to
  get the object_provides catalog metadata updated, please clear and rebuild
  your catalog.

- The ATEvent fields "recurrence", "timezone" and "wholeDay" now do not have
  ATFieldProperty definitions anymore and aren't stored in Annotations but
  directly on the context. The change was neccasary for the timezone field,
  since we had to implement a custom setter. Besides, it avoids confusion, that
  wholeDay has to be set as wholeDay for invokeFactory but as whole_day on the
  context itself.  There is an upgrade step, addressing this change ("Upgrade
  to plone.app.event beta2", from metadata version 2 to 3).


