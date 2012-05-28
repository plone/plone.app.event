""" Behaviors to enable calendarish event extension to dexterity content
types.

"""
import pytz
from Acquisition import aq_base
from plone.directives import form
from plone.event.interfaces import IEventAccessor, IRecurrenceSupport
from plone.event.utils import tzdel, utc, utctz, dt_to_zone
from plone.formwidget.recurrence.z3cform.widget import RecurrenceWidget, ParameterizedWidgetFactory
from plone.indexer import indexer
from plone.uuid.interfaces import IUUID
from zope import schema
from zope.component import adapts
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import invariant, Invalid
from plone.app.event.dx.interfaces import IDXEvent, IDXEventRecurrence
from plone.app.event.occurrence import Occurrence
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.event.base import default_timezone, default_end_dt
from plone.app.event.base import localized_now, DT
from plone.app.event import messageFactory as _

# TODO: altern., for backwards compat., we could import from plone.z3cform
from z3c.form.browser.textlines import TextLinesFieldWidget


class StartBeforeEnd(Invalid):
    __doc__ = _("exception_start_before_end",
                default=u"The start or end date is invalid")


class IEventBasic(form.Schema):
    """ Basic event schema.

    """
    start = schema.Datetime(
        title = _(u'label_start', default=u'Event start date'),
        description = _(u'help_start', default=u'Date and Time, when the event begins.'),
        required = True
        )

    end = schema.Datetime(
        title = _(u'label_end', default=u'Event end date'),
        description = _(u'help_end', default=u'Date and Time, when the event ends.'),
        required = True
        )

    whole_day = schema.Bool(
        title = _(u'label_whole_day', default=u'Whole Day'),
        description = _(u'help_whole_day', default=u'Event lasts whole day'),
        required = False
        )

    timezone = schema.Choice(
        title = _(u'label_timezone', default=u'Timezone'),
        description = _(u'help_timezone', default=u'Timezone of the event'),
        required = True,
        vocabulary="plone.app.event.AvailableTimezones"
        )

    @invariant
    def validate_start_end(data):
        if data.start > data.end:
            raise StartBeforeEnd(_("exception_start_before_end_text",
                                   default=u"The start date must be before the\
                                             end date."))

@form.default_value(field=IEventBasic['start'])
def default_start(data):
    return localized_now()

@form.default_value(field=IEventBasic['end'])
def default_end(data):
    return default_end_dt()

@form.default_value(field=IEventBasic['timezone'])
def default_tz(data):
    return default_timezone()


class IEventRecurrence(form.Schema):
    """ Recurring Event Schema.

    """
    recurrence = schema.Text(
        title = _(u'label_recurrence', default=u'Recurrence'),
        description = _(u'help_recurrence', default=u'RFC5545 compatible recurrence definition'),
        required = False)

# TODO: DOCUMENT! If a behavior, made out of IEventBasic and IRecurrence is
# used then a new ParameterizedWidgetFactory has to be used and the start_field
# parameter must be set to the name of the new behavior.

# Adding a parametirized widget (this will be simpler in future versions of plone.autoform)
IEventRecurrence.setTaggedValue('plone.autoform.widgets',
    {'recurrence': ParameterizedWidgetFactory(RecurrenceWidget,
        start_field='IEventBasic.start')})



class IEventLocation(form.Schema):
    """ Event Location Schema.
    """
    location = schema.TextLine(
        title = _(u'label_location', default=u'Location'),
        description = _(u'help_location', default=u'Location of the event'),
        required = False
        )


class IEventAttendees(form.Schema):
    """ Event Attendees Schema.
    """
    attendees = schema.Tuple(
        title = _(u'label_attendees', default=u'Attendees'),
        description = _(u'help_attendees', default=u'List of attendees'),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )
    form.widget(attendees = TextLinesFieldWidget)


class IEventContact(form.Schema):
    """ Event Contact Schema.
    """
    contact_name = schema.TextLine(
        title = _(u'label_contact_name', default=u'Contact Name'),
        description = _(u'help_contact_name', default=u'Name of a person to contact about this event.'),
        required = False
        )

    contact_email = schema.TextLine(
        title = _(u'label_contact_email', default=u'Contact E-mail'),
        description = _(u'help_contact_email', default=u'Email address to contact about this event.'),
        required = False
        )

    contact_phone = schema.TextLine(
        title = _(u'label_contact_phone', default=u'Contact Phone'),
        description = _(u'help_contact_phone', default=u'Phone number to contact about this event.'),
        required = False
        )

    event_url = schema.TextLine(
        title = _(u'label_event_url', default=u'Event URL'),
        description = _(u'help_event_url', default=u'Web address with more info about the event. Add http:// for external links.'),
        required = False
        )


# Mark these interfaces as form field providers
alsoProvides(IEventBasic, form.IFormFieldProvider)
alsoProvides(IEventRecurrence, form.IFormFieldProvider)
alsoProvides(IEventLocation, form.IFormFieldProvider)
alsoProvides(IEventAttendees, form.IFormFieldProvider)
alsoProvides(IEventContact, form.IFormFieldProvider)


class EventBasic(object):

    def __init__(self, context):
        self.context = context

    @property
    def start(self):
        return self._prepare_dt_get(self.context.start)
    @start.setter
    def start(self, value):
        self.context.start = self._prepare_dt_set(value)

    @property
    def end(self):
        return self._prepare_dt_get(self.context.end)
    @end.setter
    def end(self, value):
        self.context.end = self._prepare_dt_set(value)

    @property
    def timezone(self):
        return self.context.timezone
    @timezone.setter
    def timezone(self, value):
        self.context.timezone = value

    @property
    def whole_day(self):
        return self.context.whole_day
    @whole_day.setter
    def whole_day(self, value):
        self.context.whole_day = value

    @property
    def duration(self):
        return self.context.end - self.context.start

    def _prepare_dt_get(self, dt):
        # always get the date in event's timezone
        return dt_to_zone(dt, self.context.timezone)

    def _prepare_dt_set(self, dt):
        # Dates are always set in UTC, saving the actual timezone in another
        # field. But since the timezone value isn't known at time of saving the
        # form, we have to save it with a dummy zone first and replace it with
        # the target zone afterwards. So, it's not timezone naive and can be
        # compared to timezone aware Dates.
        return dt.replace(tzinfo=utctz()) # return with dummy zone


class EventRecurrence(object):

    def __init__(self, context):
        self.context = context

    @property
    def recurrence(self):
        return self.context.recurrence
    @recurrence.setter
    def recurrence(self, value):
        self.context.recurrence = value


# Object adapters

class Recurrence(object):
    """ IRecurrenceSupport Adapter.
    """
    implements(IRecurrenceSupport)
    adapts(IDXEventRecurrence)

    def __init__(self, context):
        self.context = context

    def occurrences(self, limit_start=None, limit_end=None):
        """ Return all occurrences of an event, possibly within a start and end
        limit.

        Please note: Events beginning before limit_start but ending afterwards
                     won't be found.

        TODO: test with event start = 21st feb, event end = start+36h,
        recurring for 10 days, limit_start = 1st mar, limit_end = last Mark

        """
        event = IEventBasic(self.context)
        recrule = IEventRecurrence(self.context).recurrence
        starts = recurrence_sequence_ical(
                event.start,
                recrule=recrule,
                from_=limit_start, until=limit_end)

        # We get event ends by adding a duration to the start. This way, we
        # prevent that the start and end lists are of different size if an
        # event starts before limit_start but ends afterwards.
        duration = event.duration

        # XXX potentially occurrence won't need to be wrapped anymore
        # but doing it for backwards compatibility as views/templates
        # still rely on acquisition-wrapped objects.
        func = lambda start: Occurrence(
            id=str(start.date()),
            parent=event,
            start=start,
            end=start + duration).__of__(self.context)
        events = map(IEventAccessor, map(func, starts))
        return events


## Event handlers

def data_postprocessing(obj, event):
    # We handle date inputs as floating dates without timezones and apply
    # timezones afterwards.
    start = tzdel(obj.start)
    end = tzdel(obj.end)

    # set the timezone
    tz = pytz.timezone(obj.timezone)
    start = tz.localize(start)
    end = tz.localize(end)

    # adapt for whole Day
    if obj.whole_day:
        start = start.replace(hour=0,minute=0,second=0)
        end = end.replace(hour=23,minute=59,second=59)

    # save back
    obj.start = utc(start)
    obj.end = utc(end)

    # reindex
    obj.reindexObject()


## Attribute indexer

# Start indexer
@indexer(IDXEvent)
def start_indexer(obj):
    event = IEventBasic(obj)
    if event.start is None:
        return None
    return DT(event.start)

# End indexer
@indexer(IDXEvent)
def end_indexer(obj):
    event = IEventBasic(obj)
    if event.end is None:
        return None
    return DT(event.end)
# Object adapters


class EventAccessor(object):
    """ Generic event accessor adapter implementation for dexterity content
        objects.

    """

    implements(IEventAccessor)
    adapts(IDXEvent)

    def __init__(self, context):
        context = aq_base(context)
        object.__setattr__(self, 'context', context)

        bm = dict(
            start=IEventBasic,
            end=IEventBasic,
            timezone=IEventBasic,
            whole_day=IEventBasic,
            recurrence=IEventRecurrence,
            location=IEventLocation,
            attendees=IEventAttendees,
            contact_name=IEventContact,
            contact_email=IEventContact,
            contact_phone=IEventContact,
            event_url=IEventContact,
            subjects=ICategorization
        )
        object.__setattr__(self, '_behavior_map', bm)

    def __getattr__(self, name):
        bm = self._behavior_map
        if name in bm:
           behavior = bm[name](self.context, None)
           if behavior: return getattr(behavior, name, None)
        return None

    def __setattr__(self, name, value):
        bm = self._behavior_map
        if name in bm:
            behavior = bm[name](self.context, None)
            if behavior: setattr(behavior, name, value)

    def __delattr__(self, name):
        bm = self._behavior_map
        if name in bm:
           behavior = bm[name](self.context, None)
           if behavior: delattr(behavior, name)


    # ro properties

    @property
    def uid(self):
        return IUUID(self.context, None)

    @property
    def created(self):
        return utc(self.context.creation_date)

    @property
    def last_modified(self):
        return utc(self.context.modification_date)

    @property
    def duration(self):
        return self.end - self.start

    # rw properties not in behaviors (yet) # TODO revisit

    def get_title(self):
        return getattr(self.context, 'title', None)
    def set_title(self, value):
        return setattr(self.context, 'title', value)
    title = property(get_title, set_title)

    def get_description(self):
        return getattr(self.context, 'description', None)
    def set_description(self, value):
        return setattr(self.context, 'description', value)
    description = property(get_description, set_description)

    def get_text(self):
        return getattr(self.context, 'text', None)
    def set_text(self, value):
        return setattr(self.context, 'text', value)
    text = property(get_text, set_text)
