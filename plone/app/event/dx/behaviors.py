"""Behaviors to enable calendarish event extension to dexterity content types.
"""
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
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
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.interfaces import IPloneFormLayer
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.event.interfaces import IEventAccessor
from plone.event.utils import pydt
from plone.event.utils import utc
from plone.formwidget.recurrence.z3cform.widget import RecurrenceWidget
from plone.indexer import indexer
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from z3c.form.interfaces import IFieldWidget
from z3c.form.util import getSpecification
from z3c.form.widget import FieldWidget
from zope import schema
from zope.component import adapter
from zope.interface import Invalid
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

# TODO: altern., for backwards compat., we could import from plone.z3cform
from z3c.form.browser.textlines import TextLinesFieldWidget

import pkg_resources

try:
    # Plone 5
    pkg_resources.get_distribution('plone.app.z3cform')
    from plone.app.z3cform.widget import DatetimeWidget
except pkg_resources.DistributionNotFound:
    from plone.app.widgets.dx import DatetimeWidget


def first_weekday_sun0():
    return wkday_to_mon1(first_weekday())


class StartBeforeEnd(Invalid):
    __doc__ = _("error_invalid_date",
                default=u"Invalid start or end date")


@provider(IContextAwareDefaultFactory)
def default_start(context):
    """Provide default start for the form.
    """
    return default_start_dt(context)


@provider(IContextAwareDefaultFactory)
def default_end(context):
    """Provide default end for the form.
    """
    return default_end_dt(context)


class IEventBasic(model.Schema, IDXEvent):
    """ Basic event schema.
    """
    start = schema.Datetime(
        title=_(
            u'label_event_start',
            default=u'Event Starts'
        ),
        description=_(
            u'help_event_start',
            default=u'Date and Time, when the event begins.'
        ),
        required=True,
        defaultFactory=default_start
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
        required=True,
        defaultFactory=default_end
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
    widget.default_timezone = default_timezone
    return widget


@adapter(getSpecification(IEventBasic['end']), IPloneFormLayer)
@implementer(IFieldWidget)
def EndDateFieldWidget(field, request):
    widget = FieldWidget(field, DatetimeWidget(request))
    widget.default_timezone = default_timezone
    return widget


class IEventRecurrence(model.Schema, IDXEventRecurrence):
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


# Mark these interfaces as form field providers
alsoProvides(IEventBasic, IFormFieldProvider)
alsoProvides(IEventRecurrence, IFormFieldProvider)
alsoProvides(IEventLocation, IFormFieldProvider)
alsoProvides(IEventAttendees, IFormFieldProvider)
alsoProvides(IEventContact, IFormFieldProvider)


"""
if not obj.sync_uid:
    # sync_uid has to be set for icalendar data exchange.
    uid = IUUID(obj)
    # We don't want to fail when getRequest() returns None, e.g when
    # creating an event during test layer setup time.
    request = getRequest() or {}
    domain = request.get('HTTP_HOST')
    obj.sync_uid = '%s%s' % (
        uid,
        '@%s' % domain if domain else ''
    )
"""


## Attribute indexer

# Start indexer
@indexer(IDXEvent)
def start_indexer(obj):
    return IEventAccessor(obj).start


# End indexer
@indexer(IDXEvent)
def end_indexer(obj):
    return IEventAccessor(obj).end


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
        return None
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

@adapter(IDXEvent)
@implementer(IEventAccessor)
class EventAccessor(object):
    """Generic event accessor adapter implementation for Dexterity content
       objects.
    """

    def __init__(self, context):
        object.__setattr__(self, 'context', context)

        bm = dict(
            start=IEventBasic,
            end=IEventBasic,
            whole_day=IEventBasic,
            open_end=IEventBasic,
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

    @property
    def start(self):
        start = IEventBasic(self.context).start
        if self.whole_day:
            start = dt_start_of_day(start)
        return start

    @start.setter
    def start(self, value):
        return setattr(self, 'start', value)

    @property
    def end(self):
        end = IEventBasic(self.context).end
        if self.open_end:
            end = IEventBasic(self.context).start
        if self.open_end or self.whole_day:
            end = dt_end_of_day(end)
        return end

    @end.setter
    def end(self, value):
        return setattr(self, 'end', value)

    @property
    def timezone(self):
        """Returns the timezone name for the event. If the start timezone
        differs from the end timezone, it returns a tuple with
        (START_TIMEZONENAME, END_TIMEZONENAME).
        """
        tz_start = tz_end = None
        tz = getattr(IEventBasic(self.context).start, 'tzinfo', None)
        if tz:
            tz_start = tz.zone
        tz = getattr(IEventBasic(self.context).end, 'tzinfo', None)
        if tz:
            tz_end = tz.zone
        return tz_start if tz_start == tz_end else (tz_start, tz_end)

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
