# -*- coding: utf-8 -*-
"""Behaviors to enable calendarish event extension to dexterity content types.
"""
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.app.event import _
from plone.app.event.base import default_end as default_end_dt
from plone.app.event.base import default_start as default_start_dt
from plone.app.event.base import default_timezone
from plone.app.event.base import DT
from plone.app.event.base import dt_end_of_day
from plone.app.event.base import dt_start_of_day
from plone.app.event.base import first_weekday
from plone.app.event.base import localized_now
from plone.app.event.base import wkday_to_mon1
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.interfaces import IDXEventRecurrence
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField
from plone.app.textfield.value import RichTextValue
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IRecurrenceSupport
from plone.event.utils import pydt
from plone.event.utils import utc
from plone.formwidget.recurrence.z3cform.widget import RecurrenceFieldWidget
from plone.indexer import indexer
from plone.supermodel import model
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.browser.text import TextFieldWidget
from z3c.form.browser.textlines import TextLinesFieldWidget
from zope import schema
from zope.component import adapter
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory

import six


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
    directives.widget(
        'start',
        DatetimeFieldWidget,
        default_timezone=default_timezone,
        klass=u'event_start'
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
    directives.widget(
        'end',
        DatetimeFieldWidget,
        default_timezone=default_timezone,
        klass=u'event_end'
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
    directives.widget(
        'whole_day',
        SingleCheckBoxFieldWidget,
        klass=u'event_whole_day'
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
    directives.widget(
        'open_end',
        SingleCheckBoxFieldWidget,
        klass=u'event_open_end'
    )

    # icalendar event uid
    sync_uid = schema.TextLine(required=False)
    directives.mode(sync_uid='hidden')

    @invariant
    def validate_start_end(data):
        if (
            data.start
            and data.end
            and data.start > data.end
            and not data.open_end
        ):
            raise StartBeforeEnd(
                _("error_end_must_be_after_start_date",
                  default=u"End date must be after start date.")
            )


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
    directives.widget(
        'recurrence',
        RecurrenceFieldWidget,
        start_field=u'IEventBasic.start',
        first_day=first_weekday_sun0,
        show_repeat_forever=False,
        klass=u'event_recurrence'
    )


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
    directives.widget(
        'location',
        TextFieldWidget,
        klass=u'event_location'
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
    directives.widget(
        'attendees',
        TextLinesFieldWidget,
        klass=u'event_attendees'
    )


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
    directives.widget(
        'contact_name',
        TextFieldWidget,
        klass=u'event_contact_name'
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
    directives.widget(
        'contact_email',
        TextFieldWidget,
        klass=u'event_contact_email'
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
    directives.widget(
        'contact_phone',
        TextFieldWidget,
        klass=u'event_contact_phone'
    )

    event_url = schema.URI(
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
    directives.widget(
        'event_url',
        TextFieldWidget,
        klass=u'event_url'
    )


# Mark these interfaces as form field providers
alsoProvides(IEventBasic, IFormFieldProvider)
alsoProvides(IEventRecurrence, IFormFieldProvider)
alsoProvides(IEventLocation, IFormFieldProvider)
alsoProvides(IEventAttendees, IFormFieldProvider)
alsoProvides(IEventContact, IFormFieldProvider)


# Language independent fields
alsoProvides(IEventBasic['start'], ILanguageIndependentField)
alsoProvides(IEventBasic['end'], ILanguageIndependentField)
alsoProvides(IEventBasic['whole_day'], ILanguageIndependentField)
alsoProvides(IEventBasic['open_end'], ILanguageIndependentField)


# Attribute indexer

# Start indexer
@indexer(IDXEvent)
def start_indexer(obj):
    start = IEventAccessor(obj).start
    if not start:
        raise AttributeError
    return start


# End indexer
@indexer(IDXEvent)
def end_indexer(obj):
    end = IEventAccessor(obj).end
    if not end:
        raise AttributeError
    return end


# Location indexer
@indexer(IDXEvent)
def location_indexer(obj):
    location_adapter = IEventLocation(obj, None)
    location = getattr(location_adapter, 'location', None)
    if not location:
        raise AttributeError
    return location


# icalendar event UID indexer
@indexer(IDXEvent)
def sync_uid_indexer(obj):
    sync_uid = IEventAccessor(obj).sync_uid
    if not sync_uid:
        raise AttributeError
    return sync_uid


# Body text indexing
@indexer(IDXEvent)
def searchable_text_indexer(obj):
    acc = IEventAccessor(obj)
    text = u''
    text += u'%s\n' % acc.title
    text += u'%s\n' % acc.description
    textvalue = acc.text
    transforms = getToolByName(obj, 'portal_transforms')
    if six.PY2:
        textvalue = textvalue.encode('utf8')
    body_plain = transforms.convertTo(
        'text/plain',
        textvalue,
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
        try:
            # see, if attribute is available.
            object.__getattribute__(self, name)
            # if so, set the value
            object.__setattr__(self, name, value)
        except AttributeError:
            # if not, get the attribute from the behavior map, if available
            if name in bm:
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

    def _recurrence_upcoming_event(self):
        """Return the next upcoming event"""
        adapter = IRecurrenceSupport(self.context)
        occs = adapter.occurrences(range_start=localized_now())
        try:
            return next(occs)
        except StopIteration:
            # No more future occurrences: passed event
            return IEventBasic(self.context)

    @property
    def start(self):
        if getattr(self.context, 'recurrence', None):
            start = self._recurrence_upcoming_event().start
        else:
            start = IEventBasic(self.context).start

        if self.whole_day:
            start = dt_start_of_day(start)
        return start

    @start.setter
    def start(self, value):
        value = pydt(value)
        self._behavior_map['start'](self.context).start = value

    @property
    def end(self):
        if getattr(self.context, 'recurrence', None):
            end = self._recurrence_upcoming_event().end
        elif self.open_end:
            end = IEventBasic(self.context).start
        else:
            end = IEventBasic(self.context).end

        if self.open_end or self.whole_day:
            end = dt_end_of_day(end)
        return end

    @end.setter
    def end(self, value):
        value = pydt(value)
        self._behavior_map['end'](self.context).end = value

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

    @property
    def sync_uid(self):
        # Return externally set sync_uid or Plone's UUID + @domain.
        sync_uid = getattr(self.context, 'sync_uid', None)
        if not sync_uid:
            # Return internal sync_uid
            request = getRequest() or {}
            domain = request.get('HTTP_HOST', None)
            domain = '@' + domain if domain else ''
            sync_uid = self.uid + domain if self.uid else None
        return sync_uid

    # rw properties not in behaviors.
    # TODO: revisit, deprecate.

    @property
    def title(self):
        return safe_unicode(getattr(self.context, 'title', None))

    @title.setter
    def title(self, value):
        self.context.title = safe_unicode(value)

    @property
    def description(self):
        return safe_unicode(getattr(self.context, 'description', None))

    @description.setter
    def description(self, value):
        self.context.description = safe_unicode(value)

    @property
    def last_modified(self):
        return utc(self.context.modification_date)

    @last_modified.setter
    def last_modified(self, value):
        tz = default_timezone(self.context, as_tzinfo=True)
        mod = DT(pydt(value, missing_zone=tz))
        self.context.modification_date = mod

    @property
    def text(self):
        textvalue = getattr(self.context, 'text', None)
        if textvalue is None:
            return u''
        return safe_unicode(textvalue.output_relative_to(self.context))

    @text.setter
    def text(self, value):
        self.context.text = RichTextValue(raw=safe_unicode(value))
