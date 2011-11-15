""" Behaviours to enable calendarish event extension to dexterity content
types.

"""
import pytz
from zope import schema
from zope.component import adapts
from zope.interface import implements, alsoProvides, invariant
from plone.directives import form
from plone.app.event import messageFactory as _
from plone.app.event.interfaces import IEvent
from plone.dexterity.interfaces import IDexterityContent


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

    timezone = schema.TextLine(
        title = _(u'label_timezone', default=u'Timezone'),
        description = _(u'help_timezone', default=u'Timezone of the event'),
        required = True,
        )

    whole_day = schema.Bool(
        title = _(u'label_whole_day', default=u'Whole Day'),
        description = _(u'help_whole_day', default=u'Event lasts whole day'),
        required = False
        )

    event_url = schema.TextLine(
        title = _(u'label_event_url', default=u'Event Url'),
        description = _(u'help_event_url', default=u'Website of the event'),
        required = False
        )


class IEventRecurrence(form.Schema):
    """ Recurring Event Schema.

    """
    recurrence = schema.TextLine(
        title = _(u'label_recurrence', default=u'Recurrence'),
        description = _(u'help_recurrence', default=u'RFC5545 compatible recurrence definition'),
        required = False)

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
    attendees = schema.Text(
        title = _(u'label_attendees', default=u'Attendees'),
        description = _(u'help_attendees', default=u'List of attendees'),
        required = False
        )

class IEventContact(form.Schema):
    """ Event Contact Schema.
    """
    contact_name = schema.TextLine(
        title = _(u'label_contact_name', default=u'Contact Name'),
        description = _(u'help_contact_name', default=u'Name of a person to contact about this event.'),
        required = False
        )

    contact_email = schema.TextLine(
        title = _(u'label_contact_email', default=u'Contact Email'),
        description = _(u'help_contact_email', default=u'Email address to contact about this event.'),
        required = False
        )

    contact_phone = schema.TextLine(
        title = _(u'label_contact_phone', default=u'Contact Phone'),
        description = _(u'help_contact_phone', default=u'Phone number to contact about this event.'),
        required = False
        )


class IEventBehavior(IEventBasic, IEventRecurrence, IEventLocation, IEventAttendees, IEventContact):
    """ Full Event Behavior.

    """
    form.fieldset(
            'event',
            label=_(u'label_fieldset_event', default=u'Event'),
            fields=(
                'start',
                'end',
                'timezone',
                'recurrence',
                'whole_day',
                'location',
                'attendees',
                'event_url',
                'contact_name',
                'contact_email',
                'contact_phone',
                ),
        )

# Mark these interfaces as form field providers
alsoProvides(IEventBasic, form.IFormFieldProvider)
alsoProvides(IEventRecurrence, form.IFormFieldProvider)
alsoProvides(IEventLocation, form.IFormFieldProvider)
alsoProvides(IEventAttendees, form.IFormFieldProvider)
alsoProvides(IEventContact, form.IFormFieldProvider)
alsoProvides(IEventBehavior, form.IFormFieldProvider)


class EventBase(object):
    """ This adapter acts as a Base Adapter for more specific Event Behaviors.
    """
    implements(IEvent) # TODO: better alsoProvides?
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context

class EventBasic(EventBase):
    implements(IEventBasic)

    def _get_start(self):
        return self.context.start
    def _set_start(self, value):
        self.context.start = value
    start = property(_get_start, _set_start)

    def _get_end(self):
        return self.context.end
    def _set_end(self, value):
        self.context.end = value
    end = property(_get_end, _set_end)

    def _get_timezone(self):
        return self.context.timezone
    def _set_timezone(self, value):
        self.context.timezone = value
    timezone = property(_get_timezone, _set_timezone)

    def _get_whole_day(self):
        return self.context.whole_day
    def _set_whole_day(self, value):
        self.context.whole_day = value
    whole_day = property(_get_whole_day, _set_whole_day)

    def _get_event_url(self):
        return self.context.event_url
    def _set_event_url(self, value):
        self.context.event_url = value
    event_url = property(_get_event_url, _set_event_url)


class EventRecurrence(EventBase):
    implements(IEventRecurrence)

    def _get_recurrence(self):
        return self.context.recurrence
    def _set_recurrence(self, value):
        self.context.recurrence = value
    recurrence = property(_get_recurrence, _set_recurrence)


class EventLocation(EventBase):
    implements(IEventLocation)

    def _get_location(self):
        return self.context.location
    def _set_location(self, value):
        self.context.location = value
    location = property(_get_location, _set_location)


class EventAttendees(EventBase):
    implements(IEventAttendees)

    def _get_attendees(self):
        return self.context.attendees
    def _set_attendees(self, value):
        self.context.attendees = value
    attendees = property(_get_attendees, _set_attendees)


class EventContact(EventBase):
    implements(IEventContact)

    def _get_contact_name(self):
        return self.context.contact_name
    def _set_contact_name(self, value):
        self.context.contact_name = value
    contact_name = property(_get_contact_name, _set_contact_name)

    def _get_contact_email(self):
        return self.context.contact_email
    def _set_contact_email(self, value):
        self.context.contact_email = value
    contact_email = property(_get_contact_email, _set_contact_email)

    def _get_contact_phone(self):
        return self.context.contact_phone
    def _set_contact_phone(self, value):
        self.context.contact_phone = value
    contact_phone = property(_get_contact_phone, _set_contact_phone)



class EventBehavior(EventBasic, EventRecurrence, EventLocation, EventAttendees, EventContact):
    implements(IEventBehavior)


def data_postprocessing(obj, event):
    print "DX: executing invariant"
    tz = pytz.timezone(obj.timezone)
    start = tz.localize(obj.start)
    end = obj.end.replace(tzinfo=tz)

    if obj.whole_day:
        start = start.replace(hour=0,minute=0,second=0)
        end = end.replace(hour=23,minute=59,second=59)
    # TODO: reindex
