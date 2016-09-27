"""Behaviors to enable calendarish event extension to dexterity content types.
"""
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from datetime import timedelta
from datetime import tzinfo
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.event import messageFactory as _
from plone.app.event import PloneMessageFactory as _PMF
from plone.app.event.base import DT
from plone.app.event.base import default_end as default_end_dt
from plone.app.event.base import default_start as default_start_dt
from plone.app.event.base import default_timezone
from plone.app.event.base import dt_end_of_day
from plone.app.event.base import dt_start_of_day
from plone.app.event.base import first_weekday
from plone.app.event.base import wkday_to_mon1
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from plone.event.interfaces import IEventAccessor
from plone.event.utils import dt_to_zone
from plone.event.utils import pydt
from plone.event.utils import tzdel
from plone.event.utils import utc
from plone.formwidget.datetime.z3cform.widget import DatetimeWidget
from plone.formwidget.recurrence.z3cform.widget import RecurrenceWidget
from plone.indexer import indexer
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import ComputedWidgetAttribute
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import adapter
from zope.component import adapts
from zope.component import provideAdapter
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import Invalid
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import implements
from zope.interface import invariant
from zope.lifecycleevent import ObjectModifiedEvent

import pytz


# TODO: altern., for backwards compat., we could import from plone.z3cform
from z3c.form.browser.textlines import TextLinesFieldWidget


def first_weekday_sun0():
    return wkday_to_mon1(first_weekday())


class StartBeforeEnd(Invalid):
    __doc__ = _("error_invalid_date",
                default=u"Invalid start or end date")


class IEventBasic(model.Schema):
    """ Basic event schema.
    """
    model.fieldset('dates', fields=['timezone'],
                   label=_PMF(u'label_schema_dates', default=u'Dates'),)

    start = schema.Datetime(
        title=_(
            u'label_event_start',
            default=u'Event Starts'
        ),
        description=_(
            u'help_event_start',
            default=u'Date and Time, when the event begins.'
        ),
        required=True
    )

    end = schema.Datetime(
        title=_(
            u'label_event_end',
            default=u'Event Ends'
        ),
        description=_(
            u'help_event_end',
            default=u'Date and Time, when the event ends.'
        ),
        required=True
    )

    whole_day = schema.Bool(
        title=_(
            u'label_event_whole_day',
            default=u'Whole Day'
        ),
        description=_(
            u'help_event_whole_day',
            default=u'Event lasts whole day.'
        ),
        required=False,
        default=False
    )

    open_end = schema.Bool(
        title=_(
            u'label_event_open_end',
            default=u'Open End'
        ),
        description=_(
            u'help_event_open_end',
            default=u"This event is open ended."
        ),
        required=False,
        default=False
    )

    # TODO: form.order_before(timezone="IPublication.effective")
    timezone = schema.Choice(
        title=_(
            u'label_event_timezone',
            default=u'Timezone'
        ),
        description=_(
            u'help_event_timezone',
            default=u'Select the Timezone, where this event happens.'
        ),
        required=True,
        vocabulary="plone.app.event.AvailableTimezones"
    )

    # icalendar event uid
    sync_uid = schema.TextLine(required=False)
    form.mode(sync_uid='hidden')

    @invariant
    def validate_start_end(data):
        # data_postprocessing sets end=start if open_end
        if data.start > data.end and not data.open_end:
            raise StartBeforeEnd(
                _("error_end_must_be_after_start_date",
                  default=u"End date must be after start date.")
            )


@adapter(getSpecification(IEventBasic['start']), IPloneFormLayer)
@implementer(IFieldWidget)
def StartDateFieldWidget(field, request):
    widget = FieldWidget(field, DatetimeWidget(request))
    widget.first_day = first_weekday_sun0
    return widget


@adapter(getSpecification(IEventBasic['end']), IPloneFormLayer)
@implementer(IFieldWidget)
def EndDateFieldWidget(field, request):
    widget = FieldWidget(field, DatetimeWidget(request))
    widget.first_day = first_weekday_sun0
    return widget


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
        title=_(
            u'label_event_recurrence',
            default=u'Recurrence'
        ),
        description=_(
            u'help_event_recurrence',
            default=u'Define the event recurrence rule.'
        ),
        required=False,
        default=None
    )


@adapter(getSpecification(IEventRecurrence['recurrence']), IPloneFormLayer)
@implementer(IFieldWidget)
def RecurrenceFieldWidget(field, request):
    # Please note: If you create a new behavior with superclasses IEventBasic
    # and IRecurrence, then you have to reconfigure the dotted path value of
    # the start_field parameter for the RecurrenceWidget to the new
    # behavior name, like: IMyNewBehaviorName.start.
    widget = FieldWidget(field, RecurrenceWidget(request))
    widget.start_field = 'IEventBasic.start'
    widget.first_day = first_weekday_sun0
    widget.show_repeat_forever = False
    return widget


class IEventLocation(model.Schema):
    """ Event Location Schema.
    """
    location = schema.TextLine(
        title=_(
            u'label_event_location',
            default=u'Location'
        ),
        description=_(
            u'help_event_location',
            default=u'Location of the event.'
        ),
        required=False,
        default=None
    )


class IEventAttendees(model.Schema):
    """ Event Attendees Schema.
    """
    attendees = schema.Tuple(
        title=_(
            u'label_event_attendees',
            default=u'Attendees'
        ),
        description=_(
            u'help_event_attendees',
            default=u'List of attendees.'
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
        default=(),
    )
    form.widget(attendees=TextLinesFieldWidget)


class IEventContact(model.Schema):
    """ Event Contact Schema.
    """
    contact_name = schema.TextLine(
        title=_(
            u'label_event_contact_name',
            default=u'Contact Name'
        ),
        description=_(
            u'help_event_contact_name',
            default=u'Name of a person to contact about this event.'
        ),
        required=False,
        default=None
    )

    contact_email = schema.TextLine(
        title=_(
            u'label_event_contact_email',
            default=u'Contact E-mail'
        ),
        description=_(
            u'help_event_contact_email',
            default=u'Email address to contact about this event.'
        ),
        required=False,
        default=None
    )

    contact_phone = schema.TextLine(
        title=_(
            u'label_event_contact_phone',
            default=u'Contact Phone'
        ),
        description=_(
            u'help_event_contact_phone',
            default=u'Phone number to contact about this event.'
        ),
        required=False,
        default=None
    )

    event_url = schema.TextLine(
        title=_(
            u'label_event_url',
            default=u'Event URL'
        ),
        description=_(
            u'help_event_url',
            default=u'Web address with more info about the event. '
                    u'Add http:// for external links.'
        ),
        required=False,
        default=None
    )


class EventLocation(object):

    implements(IEventLocation)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context


class EventAttendees(object):

    implements(IEventAttendees)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context


class EventContact(object):

    implements(IEventContact)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context


# Mark these interfaces as form field providers
alsoProvides(IEventBasic, IFormFieldProvider)
alsoProvides(IEventRecurrence, IFormFieldProvider)
alsoProvides(IEventLocation, IFormFieldProvider)
alsoProvides(IEventAttendees, IFormFieldProvider)
alsoProvides(IEventContact, IFormFieldProvider)


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
        start = getattr(self.context, 'start', None)
        return self._prepare_dt_get(start) if start else None

    @start.setter
    def start(self, value):
        self.context.start = self._prepare_dt_set(value)

    @property
    def end(self):
        end = getattr(self.context, 'end', None)
        return self._prepare_dt_get(end) if end else None

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

    @property
    def whole_day(self):
        return getattr(self.context, 'whole_day', None)

    @whole_day.setter
    def whole_day(self, value):
        self.context.whole_day = value

    @property
    def open_end(self):
        return getattr(self.context, 'open_end', None)

    @open_end.setter
    def open_end(self, value):
        self.context.open_end = value

    @property
    def sync_uid(self):
        return getattr(self.context, 'sync_uid', None)

    @sync_uid.setter
    def sync_uid(self, value):
        self.context.sync_uid = value

    @property
    def duration(self):
        return self.end - self.start

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
        return getattr(self.context, 'recurrence', None)

    @recurrence.setter
    def recurrence(self, value):
        self.context.recurrence = value


# Event handlers

def data_postprocessing(obj, event):

    # newly created object, without start/end/timezone (e.g. invokeFactory()
    # called without data from add form), ignore event; it will be notified
    # again later:
    if getattr(obj, 'start', None) is None:
        return

    # We handle date inputs as floating dates without timezones and apply
    # timezones afterwards.
    def _fix_zone(dt, tz):

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
    # Fix zones
    tz = pytz.timezone(behavior.timezone)
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

    if not behavior.sync_uid:
        # sync_uid has to be set for icalendar data exchange.
        uid = IUUID(obj, None)
        if uid:
            # We don't want to fail when getRequest() returns None, e.g when
            # creating an event during test layer setup time.
            request = getRequest() or {}
            domain = request.get('HTTP_HOST')
            behavior.sync_uid = '%s%s' % (
                uid,
                domain and '@%s' % domain or ''
            )

    # Reindex
    obj.reindexObject()


# Attribute indexer

# Start indexer
@indexer(IDXEvent)
def start_indexer(obj):
    event = IEventBasic(obj)
    if event.start is None:
        raise AttributeError
    return DT(event.start)


# End indexer
@indexer(IDXEvent)
def end_indexer(obj):
    event = IEventBasic(obj)
    if event.end is None:
        raise AttributeError
    return DT(event.end)


# Location indexer
@indexer(IDXEvent)
def location_indexer(obj):
    location_adapter = IEventLocation(obj, None)
    if location_adapter:
        return location_adapter.location

    raise AttributeError


# icalendar event UID indexer
@indexer(IDXEvent)
def sync_uid_indexer(obj):
    event = IEventBasic(obj)
    if not event.sync_uid:
        raise AttributeError
    return event.sync_uid


# Body text indexing
@indexer(IDXEvent)
def searchable_text_indexer(obj):
    acc = IEventAccessor(obj)
    text = u''
    text += u'%s\n' % acc.title
    text += u'%s\n' % acc.description
    textvalue = acc.text
    transforms = getToolByName(obj, 'portal_transforms')
    body_plain = transforms.convertTo(
        'text/plain',
        textvalue.encode('utf8'),
        mimetype='text/html',
    ).getData().strip()
    if isinstance(body_plain, str):
        body_plain = body_plain.decode('utf-8')
    text += body_plain
    return text.strip().encode('utf-8')


# Object adapters

class EventAccessor(object):
    """Generic event accessor adapter implementation for Dexterity content
       objects.
    """
    implements(IEventAccessor)
    adapts(IDXEvent)
    event_type = None  # If you use the accessor's create classmethod, override
    # this in your custom type.

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
            sync_uid=IEventBasic,
            recurrence=IEventRecurrence,
            location=IEventLocation,
            attendees=IEventAttendees,
            contact_name=IEventContact,
            contact_email=IEventContact,
            contact_phone=IEventContact,
            event_url=IEventContact,
            subjects=ICategorization,
        )
        object.__setattr__(self, '_behavior_map', bm)

    def __getattr__(self, name):
        bm = self._behavior_map
        if name in bm:  # adapt object with behavior and return the attribute
            behavior = bm[name](self.context, None)
            if behavior:
                return safe_unicode(getattr(behavior, name, None))
        return None

    def __setattr__(self, name, value):
        bm = self._behavior_map
        if name in ['title', 'description', 'last_modified', 'text']:
            # custom setters for these attributes
            object.__setattr__(self, name, value)
        if name in bm:  # set the attributes on behaviors
            behavior = bm[name](self.context, None)
            if behavior:
                setattr(behavior, name, safe_unicode(value))

    def __delattr__(self, name):
        bm = self._behavior_map
        if name in bm:
            behavior = bm[name](self.context, None)
            if behavior:
                delattr(behavior, name)

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
    def last_modified(self):
        return utc(self.context.modification_date)

    @last_modified.setter
    def last_modified(self, value):
        tz = default_timezone(self.context, as_tzinfo=True)
        mod = DT(pydt(value, missing_zone=tz))
        setattr(self.context, 'modification_date', mod)

    @property
    def text(self):
        textvalue = getattr(self.context, 'text', None)
        if textvalue is None:
            return u''
        return safe_unicode(textvalue.output)

    @text.setter
    def text(self, value):
        self.context.text = RichTextValue(raw=safe_unicode(value))
