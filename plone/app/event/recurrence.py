from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Archetypes.atapi import ObjectField
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerField


class RecurrenceWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': "recurring_date",
        'helper_js': ('++resource++recurrence.js',),
        'helper_css': ('++resource++recurrence.css',),
        })

    security = ClassSecurityInfo()

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """A custom implementation for the recurring widget form processing.
        """
        fname = field.getName()

        # Assemble the recurring date from the input components
        kwargs = dict()
        kwargs['recurrence_rfc'] = form.get('%s_recurrence_rfc' % fname, None)

        value = kwargs['recurrence_rfc']
        # Stick it back in request.form
        form[fname] = value
        return value, {}

InitializeClass(RecurrenceWidget)
registerWidget(RecurrenceWidget,
               title='Recurring Date',
               description=('Renders a HTML form to enter all the info '
                            'for recurring dates.'),
               used_for=('plone.app.event.event.RecurrenceField',))


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
        field.
        See http://www.ietf.org/rfc/rfc2445.txt and
            http://labix.org/python-dateutil
        If the string does not conform to RFC2445 or dateutil.rrule.rrulestring
        format, dateutil will throw an error throughProducts.DateRecurringIndex.
        """
        if not value:
            value = None
        ObjectField.set(self, instance, value)

InitializeClass(RecurrenceField)
registerField(RecurrenceField,
              title='Recurring Date',
              description='Used to store recuring dates data.')