from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Archetypes.atapi import ObjectField
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerField

import datetime
import dateutil
from plone.app.event.interfaces import IRecurringEvent, IRecurrenceSupport
from zope.component import adapts
from zope.interface import implements
from plone.app.event import event_util
from Products.CMFPlone.i18nl10n import ulocalized_time

class RecurrenceSupport(object):
    """Recurrence support for IRecurringEvent objects.
       Tested with Archetypes based ATEvent. This one or another one may also
       be used for Dexterity based content types.
    """
    implements(IRecurrenceSupport)
    adapts(IRecurringEvent)

    def __init__(self, context):
        self.context = context

    def _recurrence_ruleset(self, dtstart=None):
        if not isinstance(dtstart, datetime.datetime):
            raise AttributeError, u"""No dtstart parameter given.s"""
        else:
            return dateutil.rrule.rrulestr(self.context.recurrence,
                                           forceset=True,
                                           dtstart=dtstart)

    def occurences_start(self):
        rset = self._recurrence_ruleset(self.context.start_date)
        return list(rset)

    def occurences_end(self):
        rset = self._recurrence_ruleset(self.context.end_date)
        return list(rset)

    def occurences(self):
        starts = self.occurences_start()
        ends = self.occurences_end()

        events = map(
            lambda start,end:dict(
                start_date = ulocalized_time(start, False, time_only=None, context=self.context),
                end_date = ulocalized_time(end, False, time_only=None, context=self.context),
                start_time = ulocalized_time(start, False, time_only=True, context=self.context),
                end_time = ulocalized_time(end, False, time_only=True, context=self.context),
                same_day = event_util.isSameDay(self.context),
                same_time = event_util.isSameTime(self.context),
            ), starts, ends )
        return events


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