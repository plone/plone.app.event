from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Archetypes.atapi import ObjectField
from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Registry import registerField

#from dateutil import rrule
#from DateTime import DateTime
#from plone.app.event.dtutils import DT2dt

import datetime
import dateutil
from plone.app.event.interfaces import IRecurringEvent, IRecurrence
# from dateable.kalends import IRecurrence, IOccurrence, IEventProvider
from zope.component import adapts
from zope.interface import implements
from plone.app.event import event_util
from Products.CMFPlone.i18nl10n import ulocalized_time

class RecurringEvent(object):
    implements(IRecurrence)
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



#class RecurringData(object):
    #"""Stores all the fields from the recurring widget.i
    #"""

    #enabled = False
    #start_time = ''
    #end_time = ''
    #frequency = 3 # 2, 1, 0
    #daily_interval = 'day' # 'weekday'
    #daily_interval_number = 1
    #weekly_interval = () # (0, 1, 2, 3, 4, 5, 6)
    #weekly_interval_number = 1
    #monthly_interval = 'dayofmonth' # 'dayofweek'
    #monthly_interval_day = 1
    #monthly_interval_number1 = 1
    #monthly_interval_number2 = 1
    #monthly_ordinal_week = 1
    #monthly_weekday = 0
    #yearly_interval = 'dayofmonth' # 'dayofweek'
    #yearly_month1 = 1
    #yearly_month2 = 1
    #yearly_interval_day = 1
    #yearly_ordinal_week = 1
    #yearly_weekday = 0
    #range_name = 'ever' # 'count', 'until'
    #range_count = 10
    #start_date = ''
    #end_date = ''

    #def __init__(self, **kwargs):
        #self.__dict__.update(kwargs)

    #def getRecurrenceRule(self):
        #if not self.enabled:
            #return None

        #dtstart = ('%s %s' % (self.start_date, self.start_time)).strip()
        #if not dtstart:
            #return None

        #dtstart = DT2dt(DateTime(dtstart))
        #params = dict(
            #dtstart=dtstart,
            ##wkst=None,
            ##byyearday=None,
            ##byeaster=None,
            ##byweekno=None,
            ##byhour=None,
            ##byminute=None,
            ##bysecond=None,
            ##cache=False
        #)

        ## byweekday
        #if self.frequency == rrule.DAILY and self.daily_interval == 'weekday':
            #params['byweekday'] = range(5)
        #elif self.frequency == rrule.WEEKLY:
            #days = [int(day) for day in self.weekly_interval]
            #if not days:
                #days = [dtstart.weekday()]
            #params['byweekday'] = days
        #elif self.frequency == rrule.MONTHLY and self.monthly_interval == 'dayofweek':
            #if self.monthly_weekday == 7: # Day
                #days = (0, 1, 2, 3, 4, 5, 6)
                #params['bysetpos'] = self.monthly_ordinal_week
            #elif self.monthly_weekday == 8: # Weekday
                #days = (0, 1, 2, 3, 4)
                #params['bysetpos'] = self.monthly_ordinal_week
            #elif self.monthly_weekday == 9: # Weekend day
                #days = (5, 6)
                #params['bysetpos'] = self.monthly_ordinal_week
            #else:
                #days = rrule.weekdays[self.monthly_weekday](self.monthly_ordinal_week)
            #params['byweekday'] = days
        #elif self.frequency == rrule.YEARLY and self.yearly_interval == 'dayofweek':
            #if self.yearly_weekday == 7: # Day
                #days = (0, 1, 2, 3, 4, 5, 6)
                #params['bysetpos'] = self.yearly_ordinal_week
            #elif self.yearly_weekday == 8: # Weekday
                #days = (0, 1, 2, 3, 4)
                #params['bysetpos'] = self.yearly_ordinal_week
            #elif self.yearly_weekday == 9: # Weekend day
                #days = (5, 6)
                #params['bysetpos'] = self.yearly_ordinal_week
            #else:
                #days = rrule.weekdays[self.yearly_weekday](self.yearly_ordinal_week)
            #params['byweekday'] = days

        ## bymonthday
        #if self.frequency == rrule.MONTHLY and self.monthly_interval == 'dayofmonth':
            ## Make sure to recur when the month has less then the required
            ## day. So, when selecting 31/30/29 it will also recur on months
            ## with less days: http://labix.org/python-dateutil#line-516
            #params['bysetpos'] = 1
            #params['bymonthday'] = (self.monthly_interval_day, -1)
        #elif self.frequency == rrule.YEARLY and self.yearly_interval == 'dayofmonth':
            #params['bymonthday'] = self.yearly_interval_day

        ## bymonth
        #if self.frequency == rrule.YEARLY:
            #if self.yearly_interval == 'dayofmonth':
                #params['bymonth'] = [self.yearly_month1]
            #elif self.yearly_interval == 'dayofweek':
                #params['bymonth'] = [self.yearly_month2]

        ## interval
        #if self.frequency == rrule.DAILY and self.daily_interval == 'day':
            #params['interval'] = self.daily_interval_number
        #elif self.frequency == rrule.WEEKLY:
            #params['interval'] = self.weekly_interval_number
        #elif self.frequency == rrule.MONTHLY:
            #if self.monthly_interval == 'dayofmonth':
                #params['interval'] = self.monthly_interval_number1
            #elif self.monthly_interval == 'dayofweek':
                #params['interval'] = self.monthly_interval_number2

        ## count
        #if self.range_name == 'count' and self.range_count:
            #params['count'] = self.range_count

        ## until
        #if self.range_name == 'until' and self.end_date:
            #until = DT2dt(DateTime(self.end_date))
            #until = until.replace(hour=23, minute=59, second=59, microsecond=999999)
            #params['until'] = until

        #params['freq'] = self.frequency
        #return rrule.rrule(**params)

    #def dict2rfc(data):
        #pass

    #def rfc2dict(data):
        #pass


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

        #kwargs['enabled'] = form.get('%s_enabled' % fname, False)
        #kwargs['frequency'] = int(form.get('%s_frequency' % fname, 3))
        #kwargs['daily_interval'] = form.get('%s_daily_interval' % fname, 'day')
        #kwargs['daily_interval_number'] = int(form.get('%s_daily_interval_number' % fname, 1))
        #kwargs['weekly_interval'] = tuple(map(int, form.get('%s_weekly_interval' % fname, ())))
        #kwargs['weekly_interval_number'] = int(form.get('%s_weekly_interval_number' % fname, 1))
        #kwargs['monthly_interval'] = form.get('%s_monthly_interval' % fname, 'dayofmonth')
        #kwargs['monthly_interval_day'] = int(form.get('%s_monthly_interval_day' % fname, 1))
        #kwargs['monthly_interval_number1'] = int(form.get('%s_monthly_interval_number1' % fname, 1))
        #kwargs['monthly_interval_number2'] = int(form.get('%s_monthly_interval_number2' % fname, 1))
        #kwargs['monthly_ordinal_week'] = int(form.get('%s_monthly_ordinal_week' % fname, 1))
        #kwargs['monthly_weekday'] = int(form.get('%s_monthly_weekday' % fname, 0))
        #kwargs['yearly_interval'] = form.get('%s_yearly_interval' % fname, 'dayofmonth')
        #kwargs['yearly_month1'] = int(form.get('%s_yearly_month1' % fname, 1))
        #kwargs['yearly_month2'] = int(form.get('%s_yearly_month2' % fname, 1))
        #kwargs['yearly_interval_day'] = int(form.get('%s_yearly_interval_day' % fname, 1))
        #kwargs['yearly_ordinal_week'] = int(form.get('%s_yearly_ordinal_week' % fname, 1))
        #kwargs['yearly_weekday'] = int(form.get('%s_yearly_weekday' % fname, 0))
        #kwargs['range_name'] = form.get('%s_range' % fname, 'ever')
        #kwargs['range_count'] = int(form.get('%s_range_count' % fname, 10))
        #kwargs['start_date'] = form.get('%s_range_start' % fname, None)
        #kwargs['end_date'] = form.get('%s_range_end' % fname, None)

        #value = RecurringData(**kwargs)

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

        #Check if value is an actual RecurringData object. If not,
        #attempt to convert it to one; otherwise set to None. Assign
        #all properties passed as kwargs to the object.
        #Create then a rrule.rruleset and stor it
        """
        if not value:
            value = None
        #elif not isinstance(value, RecurringData):
            #value = RecurringData(**kwargs)
        #if isinstance(value, RecurringData):
            ## TODO: check again
            #ruleset = rrule.rruleset()
            #ruleset.rrule(value.getRecurrenceRule())
            #value = ruleset

        ObjectField.set(self, instance, value)

    ## TODO: GET! maybe storing a datastructure is better than rrule?
    #def get(self, instance, **kwargs):
        #value = ObjectField.get(self, instance, **kwargs)
        #recdata = None
        #if value:
            #recdata = {}
            #recdata['recurrence_rfc'] = value
            ### return ruleset.getRecurrenceRule()
            ##recdata = {}
            ##rrule = ruleset._rrule[0]
            ##recdata['enabled'] = True
            ##recdata['freq'] = rrule._freq
            ##recdata['dtstart'] = rrule._dtstart
        #return recdata

InitializeClass(RecurrenceField)

registerField(RecurrenceField,
              title='Recurring Date',
              description='Used to store recuring dates data.')
