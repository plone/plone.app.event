from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Archetypes.atapi import ObjectField
from Products.Archetypes.Registry import registerField

from plone.formwidget.recurrence.atwidget import RecurrenceWidget

class RecurrenceField(ObjectField):
    """ A field for recurrence support.
    """
    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'object',
        'widget': RecurrenceWidget})

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """ Set recurrence data.

        Recurrence rules are in RFC2445 iCal format and stored as string in the
        field. i.e. RRULE:FREQ=DAILY;INTERVAL=10;COUNT=5

        See http://www.ietf.org/rfc/rfc2445.txt and
            http://labix.org/python-dateutil
        If the string does not conform to RFC2445 or dateutil.rrule.rrulestring
        format, dateutil will throw an error through Products.DateRecurringIndex.
        """
        if not value:
            value = None
        ObjectField.set(self, instance, value)

InitializeClass(RecurrenceField)
registerField(RecurrenceField,
              title='Recurring Date',
              description='Used to store recuring dates data.')
