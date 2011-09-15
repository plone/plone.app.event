""" Behaviours to enable calendarish event extension to dexterity content
types.

"""

from zope import schema
from zope.component import adapts
from zope.interface import implements, alsoProvides
from plone.directives import form
from plone.app.event import messageFactory as _
from plone.dexterity.interfaces import IDexterityContent


# TODO: create different, minimalist behaviors for every aspect of an event.
# ILocationAware, IAttendee, IContact, IRecurrence

class IEvent(form.Schema):
    """Add tags to content
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

    start = schema.DateTime(
        title = _(u'label_start', default=u'Event start date'),
        description = _(u'help_start', default=u'Date and Time, when the event begins.'),
        required = True
        )

    end = schema.DateTime(
        title = _(u'label_end', default=u'Event end date'),
        description = _(u'help_end', default=u'Date and Time, when the event ends.'),
        required = True
        )

    timezone = schema.TextLine(
        title = _(u'label_timezone', default=u'Timezone'),
        description = _(u'help_timezone', default=u'Timezone of the event'),
        required = True,
        )

    recurrence = schema.TextLine(
        title = _(u'label_recurrence', default=u'Recurrence'),
        description = _(u'help_recurrence', default=u'RFC5545 compatible recurrence definition'),
    )

    whole_day = schema.Bool(
        title = _(u'label_whole_day', default=u'Whole Day'),
        description = _(u'help_whole_day', default=u'Event lasts whole day'),
        )

    location = schema.TextLine(
        title = _(u'label_location', default=u'Location'),
        description = _(u'help_location', default=u'Location of the event'),
        )

    attendees = schema.Text(
        title = _(u'label_attendees', default=u'Attendees'),
        description = _(u'help_attendees', default=u'List of attendees'),
        )

    event_url = schema.TextLine(
        title = _(u'label_event_url', default=u'Event Url'),
        description = _(u'help_event_url', default=u'Website of the event'),
        )

    contact_name = schema.TextLine(
        title = _(u'label_contact_name', default=u'Contact Name'),
        description = _(u'help_contact_name', default=u'Name of a person to contact about this event.'),
        )

    contact_email = schema.TextLine(
        title = _(u'label_contact_email', default=u'Contact Email'),
        description = _(u'help_contact_email', default=u'Email address to contact about this event.'),
        )

    contact_phone = schema.TextLine(
        title = _(u'label_contact_phone', default=u'Contact Phone'),
        description = _(u'help_contact_phone', default=u'Phone number to contact about this event.'),
        )

alsoProvides(IEvent, form.IFormFieldProvider)


class EventBase(object):
    """ This adapter acts as a Base Adapter for more specific Event Behaviors.
    """
    implements(IEvent)
    adapts(IDexterityContent)

    def __init__(self, context):
        self.context = context
