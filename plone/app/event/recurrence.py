
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Archetypes.atapi import LinesField
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget


class RecurrenceField(LinesField):

    security = ClassSecurityInfo()

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        If passed-in value is a string, split at line breaks and
        remove leading and trailing white space before storing in object
        with rest of properties.
        """
        __traceback_info__ = value, type(value)
        if isinstance(value, basestring):
            value = value.splitlines()
        value = [v for v in value if v]
        LinesField.set(self, instance, value, **kwargs)


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
        kwargs['enabled'] = form.get('%s_enabled' % fname, False)
        kwargs['duration'] = form.get('%s_duration' % fname, None)
        kwargs['frequency'] = int(form.get('%s_frequency' % fname, 3))
        kwargs['daily_interval'] = form.get('%s_daily_interval' % fname, 'day')
        kwargs['daily_interval_number'] = int(form.get('%s_daily_interval_number' % fname, 1))
        kwargs['weekly_interval'] = tuple(map(int, form.get('%s_weekly_interval' % fname, ())))
        kwargs['weekly_interval_number'] = int(form.get('%s_weekly_interval_number' % fname, 1))
        kwargs['monthly_interval'] = form.get('%s_monthly_interval' % fname, 'dayofmonth')
        kwargs['monthly_interval_day'] = int(form.get('%s_monthly_interval_day' % fname, 1))
        kwargs['monthly_interval_number1'] = int(form.get('%s_monthly_interval_number1' % fname, 1))
        kwargs['monthly_interval_number2'] = int(form.get('%s_monthly_interval_number2' % fname, 1))
        kwargs['monthly_ordinal_week'] = int(form.get('%s_monthly_ordinal_week' % fname, 1))
        kwargs['monthly_weekday'] = int(form.get('%s_monthly_weekday' % fname, 0))
        kwargs['yearly_interval'] = form.get('%s_yearly_interval' % fname, 'dayofmonth')
        kwargs['yearly_month1'] = int(form.get('%s_yearly_month1' % fname, 1))
        kwargs['yearly_month2'] = int(form.get('%s_yearly_month2' % fname, 1))
        kwargs['yearly_interval_day'] = int(form.get('%s_yearly_interval_day' % fname, 1))
        kwargs['yearly_ordinal_week'] = int(form.get('%s_yearly_ordinal_week' % fname, 1))
        kwargs['yearly_weekday'] = int(form.get('%s_yearly_weekday' % fname, 0))
        kwargs['range_name'] = form.get('%s_range' % fname, 'ever')
        kwargs['range_count'] = int(form.get('%s_range_count' % fname, 10))
        kwargs['start_date'] = form.get('%s_range_start' % fname, None)
        kwargs['end_date'] = form.get('%s_range_end' % fname, None)

        #value = RecurringData(**kwargs)

        # Stick it back in request.form
        #form[fname] = value
        return [], {}

InitializeClass(RecurrenceWidget)

registerWidget(RecurrenceWidget,
               title='Recurring Date',
               description=('Renders a HTML form to enter all the info '
                            'for recurring dates.'),
               used_for=('plone.app.event.event.RecurrenceField',))

