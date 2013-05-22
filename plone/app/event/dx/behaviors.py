""" Behaviors to enable calendarish event extension to dexterity content
types.

"""
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from datetime import timedelta
from datetime import tzinfo
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.event import messageFactory as _
from plone.app.event.base import DT
from plone.app.event.base import default_end as default_end_dt
from plone.app.event.base import default_start as default_start_dt
from plone.app.event.base import default_timezone
from plone.app.event.base import dt_end_of_day
from plone.app.event.base import dt_start_of_day
from plone.app.event.base import first_weekday
from plone.app.event.base import wkday_to_mon1
from plone.app.event.dx import ParameterizedWidgetFactory
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.event.interfaces import IEventAccessor
from plone.event.utils import tzdel, utc, dt_to_zone
from plone.formwidget.datetime.z3cform.widget import DatetimeWidget
from plone.formwidget.recurrence.z3cform.widget import RecurrenceWidget
from plone.indexer import indexer
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from z3c.form.widget import ComputedWidgetAttribute
from zope import schema
from zope.component import adapts
from zope.component import provideAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import invariant
from zope.interface import Invalid
from zope.lifecycleevent import ObjectModifiedEvent

import pytz


# TODO: altern., for backwards compat., we could import from plone.z3cform
from z3c.form.browser.textlines import TextLinesFieldWidget


def first_weekday_sun0():
    return wkday_to_mon1(first_weekday())


class StartBeforeEnd(Invalid):
    __doc__ = _("exception_start_before_end",
                default=u"The start or end date is invalid")


class IEventBasic(model.Schema):
    """ Basic event schema.

    """
    start = schema.Datetime(
        title = _(u'label_start', default=u'Event start date'),
        description = _(u'help_start',
                        default=u'Date and Time, when the event begins.'),
        required = True
        )

    end = schema.Datetime(
        title = _(u'label_end', default=u'Event end date'),
        description = _(u'help_end',
                        default=u'Date and Time, when the event ends.'),
        required = True
        )

    whole_day = schema.Bool(
        title = _(u'label_whole_day', default=u'Whole Day'),
        description = _(u'help_whole_day', default=u'Event lasts whole day'),
        required = False
        )

    open_end = schema.Bool(
        title = _(u'label_open_end', default=u'Open end event'),
        description=_(u'help_open_end', default=u"This event is open ended."),
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

# Adding a parametirized widget
# (this will be simpler in future versions of plone.autoform)
IEventBasic.setTaggedValue('plone.autoform.widgets',
    {'start': ParameterizedWidgetFactory(DatetimeWidget,
        first_day=first_weekday_sun0),
     'end': ParameterizedWidgetFactory(DatetimeWidget,
        first_day=first_weekday_sun0),
    })

def default_start(data):
    return default_start_dt(data.context)
provideAdapter(ComputedWidgetAttribute(
    default_start, field=IEventBasic['start']), name='default')

def default_end(data):
    return default_end_dt(data.context)
provideAdapter(ComputedWidgetAttribute(
    default_end, field=IEventBasic['end']), name='default')

def default_tz(data):
    return default_timezone()
provideAdapter(ComputedWidgetAttribute(
    default_tz, field=IEventBasic['timezone']), name='default')


class IEventRecurrence(model.Schema):
    """ Recurring Event Schema.

    """
    recurrence = schema.Text(
        title = _(u'label_recurrence', default=u'Recurrence'),
        description = _(u'help_recurrence',
                        default=u'RFC5545 compatible recurrence definition'),
        required = False)

# Please note: If a new behavior, made out of IEventBasic and IRecurrence is
# created then a new ParameterizedWidgetFactory has to be used and the
# start_field parameter must be set to the name of the new behavior.

# Adding a parametirized widget
# (this will be simpler in future versions of plone.autoform)
IEventRecurrence.setTaggedValue('plone.autoform.widgets',
    {'recurrence': ParameterizedWidgetFactory(RecurrenceWidget,
        start_field='IEventBasic.start',
        first_day=first_weekday_sun0
    )})


class IEventLocation(model.Schema):
    """ Event Location Schema.
    """
    location = schema.TextLine(
        title = _(u'label_location', default=u'Location'),
        description = _(u'help_location', default=u'Location of the event'),
        required = False
        )


class IEventAttendees(model.Schema):
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


class IEventContact(model.Schema):
    """ Event Contact Schema.
    """
    contact_name = schema.TextLine(
        title = _(u'label_contact_name', default=u'Contact Name'),
        description = _(u'help_contact_name',
                        default=u'Name of a person to contact about this '
                                u'event.'),
        required = False
        )

    contact_email = schema.TextLine(
        title = _(u'label_contact_email', default=u'Contact E-mail'),
        description = _(u'help_contact_email',
                        default=u'Email address to contact about this event.'),
        required = False
        )

    contact_phone = schema.TextLine(
        title = _(u'label_contact_phone', default=u'Contact Phone'),
        description = _(u'help_contact_phone',
                        default=u'Phone number to contact about this event.'),
        required = False
        )

    event_url = schema.TextLine(
        title = _(u'label_event_url', default=u'Event URL'),
        description = _(u'help_event_url',
                        default=u'Web address with more info about the event. '
                        u'Add http:// for external links.'),
        required = False
        )


class IEventSummary(model.Schema):
    """Event summary (body text) schema."""

    text = RichText(
        title=_(u'label_event_announcement', default=u'Event body text'),
        description=_(u'help_event_announcement', default=u''),
        required=False,
        )


# Mark these interfaces as form field providers
alsoProvides(IEventBasic, IFormFieldProvider)
alsoProvides(IEventRecurrence, IFormFieldProvider)
alsoProvides(IEventLocation, IFormFieldProvider)
alsoProvides(IEventAttendees, IFormFieldProvider)
alsoProvides(IEventContact, IFormFieldProvider)
alsoProvides(IEventSummary, IFormFieldProvider)


class FakeZone(tzinfo):
    """Fake timezone to be applied to EventBasic start and end dates before
    data_postprocessing event handler sets the correct one.

    """
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "FAKEZONE"

    def dst(self, dt):
        return timedelta(0)


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
        return getattr(self.context, 'timezone', None)
    @timezone.setter
    def timezone(self, value):
        if self.timezone:
            # The event is edited and not newly created, otherwise the timezone
            # info wouldn't exist.
            # In order to treat user datetime input as localized, so that the
            # values aren't converted to the target timezone, we have to set
            # start and end too. Then that a temporary fake zone is applied and
            # the data_postprocessing event subscriber can do it's job.
            self.start = self.start
            self.end = self.end
        self.context.timezone = value

    # TODO: whole day - and other attributes - might not be set at this time!
    # TODO: how to provide default values?
    @property
    def whole_day(self):
        return getattr(self.context, 'whole_day', False)
    @whole_day.setter
    def whole_day(self, value):
        self.context.whole_day = value

    @property
    def open_end(self):
        return getattr(self.context, 'open_end', False)
    @open_end.setter
    def open_end(self, value):
        self.context.open_end = value

    @property
    def duration(self):
        return self.context.end - self.context.start

    def _prepare_dt_get(self, dt):
        # always get the date in event's timezone
        return dt_to_zone(dt, self.context.timezone)

    def _prepare_dt_set(self, dt):
        # Dates are always set in UTC, saving the actual timezone in another
        # field. But since the timezone value isn't known at time of saving the
        # form, we have to save it with a fake zone first and replace it with
        # the target zone afterwards. So, it's not timezone naive and can be
        # compared to timezone aware Dates.

        # return with fake zone and without microseconds
        return dt.replace(microsecond=0, tzinfo=FakeZone())


class EventRecurrence(object):

    def __init__(self, context):
        self.context = context

    @property
    def recurrence(self):
        return self.context.recurrence
    @recurrence.setter
    def recurrence(self, value):
        self.context.recurrence = value


## Event handlers

def data_postprocessing(obj, event):

    # newly created object, without start/end/timezone (e.g. invokeFactory()
    # called without data from add form), ignore event; it will be notified
    # again later:
    if getattr(obj, 'start', None) is None:
        return

    # We handle date inputs as floating dates without timezones and apply
    # timezones afterwards.
    def _fix_zone(dt, zone):

        if dt.tzinfo is not None and isinstance(dt.tzinfo, FakeZone):
            # Delete the tzinfo only, if it was set by IEventBasic setter.
            # Only in this case the start value on the object itself is what
            # was entered by the user. After running this event subscriber,
            # it's in UTC then.
            # If tzinfo it's not available at all, a naive datetime was set
            # probably by invokeFactory in tests.
            dt = tzdel(dt)

        if dt.tzinfo is None:
            # In case the tzinfo was deleted above or was not present, we can
            # localize the dt value to the target timezone.
            dt = tz.localize(dt)

        else:
            # In this case, no changes to start, end or the timezone were made.
            # Just return the object's datetime (which is in UTC) localized to
            # the target timezone.
            dt = dt.astimezone(tz)

        return dt.replace(microsecond=0)

    behavior = IEventBasic(obj)
    tz = pytz.timezone(behavior.timezone)

    # Fix zones
    start = _fix_zone(obj.start, tz)
    end = _fix_zone(obj.end, tz)

    # Adapt for whole day
    if behavior.whole_day:
        start = dt_start_of_day(start)
    if behavior.open_end:
        end = start  # Open end events end on same day
    if behavior.open_end or behavior.whole_day:
        end = dt_end_of_day(end)

    # Save back
    obj.start = utc(start)
    obj.end = utc(end)

    # Reindex
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

# Body text indexing
@indexer(IDXEvent)
def searchable_text_indexer(obj):
    acc = IEventAccessor(obj)
    text = ''
    text += '%s\n' % acc.title
    text += '%s\n' % acc.description
    behavior = IEventSummary(obj, None)
    if behavior is None or behavior.text is None:
        return text
    output = behavior.text.output
    transforms = getToolByName(obj, 'portal_transforms')
    body_plain = transforms.convertTo(
        'text/plain',
        output,
        mimetype='text/html',
        ).getData().strip()
    text += body_plain
    return text.strip()


# Object adapters


class EventAccessor(object):
    """ Generic event accessor adapter implementation for Dexterity content
        objects.

    """

    implements(IEventAccessor)
    adapts(IDXEvent)
    event_type = 'plone.app.event.dx.event' # If you use a custom content-type,
                                            # override this.

    # Unified create method via Accessor
    @classmethod
    def create(cls, container, content_id, title, description=None,
               start=None, end=None, timezone=None,
               whole_day=None, open_end=None, **kwargs):
        container.invokeFactory(cls.event_type,
                                id=content_id,
                                title=title,
                                description=description,
                                start=start,
                                end=end,
                                whole_day=whole_day,
                                open_end=open_end,
                                timezone=timezone)
        content = container[content_id]
        acc = IEventAccessor(content)
        acc.edit(**kwargs)
        return acc

    def edit(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        notify(ObjectModifiedEvent(self.context))

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

        bm = dict(
            start=IEventBasic,
            end=IEventBasic,
            whole_day=IEventBasic,
            open_end=IEventBasic,
            timezone=IEventBasic,
            recurrence=IEventRecurrence,
            location=IEventLocation,
            attendees=IEventAttendees,
            contact_name=IEventContact,
            contact_email=IEventContact,
            contact_phone=IEventContact,
            event_url=IEventContact,
            subjects=ICategorization,
            text=IEventSummary,
        )
        object.__setattr__(self, '_behavior_map', bm)

    def __getattr__(self, name):
        bm = self._behavior_map
        if name in bm: # adapt object with behavior and return the attribute
           behavior = bm[name](self.context, None)
           if behavior: return safe_unicode(getattr(behavior, name, None))
        return None

    def __setattr__(self, name, value):
        bm = self._behavior_map
        if name in bm: # set the attributes on behaviors
            behavior = bm[name](self.context, None)
            if behavior: setattr(behavior, name, safe_unicode(value))

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
    def url(self):
        return safe_unicode(self.context.absolute_url())

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
    @property
    def title(self):
        return safe_unicode(getattr(self.context, 'title', None))
    @title.setter
    def title(self, value):
        setattr(self.context, 'title', safe_unicode(value))

    @property
    def description(self):
        return safe_unicode(getattr(self.context, 'description', None))
    @description.setter
    def description(self, value):
        setattr(self.context, 'description', safe_unicode(value))

    @property
    def text(self):
        behavior = IEventSummary(self.context)
        textvalue = getattr(behavior, 'text', None)
        if textvalue is None:
            return u''
        return safe_unicode(textvalue.output)
    @text.setter
    def text(self, value):
        behavior = IEventSummary(self.context)
        behavior.text = RichTextValue(raw=safe_unicode(value))
