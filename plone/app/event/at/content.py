from datetime import datetime
import icalendar

from zope.interface import implements

from DateTime import DateTime
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
#from Products.CMFPlone.utils import safe_unicode
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.interfaces import IATEvent
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes import ATCTMessageFactory as _

from plone.formwidget.recurrence.atwidget import RecurrenceWidget
from plone.formwidget.datetime.at import DatetimeWidget

from plone.app.event.at import atapi
from plone.app.event.at import packageName
from plone.app.event.interfaces import IEvent
from plone.app.event.base import default_end_date
from plone.app.event.base import default_timezone as default_tz
from plone.event.recurrence import recurrence_sequence_ical
from plone.event.utils import pydt


ATEventSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.StringField('location',
        searchable=True,
        write_permission=ModifyPortalContent,
        widget=atapi.StringWidget(
            label=_(u'label_event_location', default=u'Event Location'),
            description=_(u'help_event_location', default=u""),
            ),
        ),

    atapi.BooleanField('wholeDay',
        default=False,
        write_permission=ModifyPortalContent,
        languageIndependent=True,
        widget=atapi.BooleanWidget(
            label=_(u'label_whole_day_event', u'Whole day event'),
            description=_(u'help_whole_day_location', default=u""),
            ),
        ),

    atapi.DateTimeField('startDate',
        required=True,
        searchable=False,
        accessor='start',
        write_permission=ModifyPortalContent,
        default_method=DateTime,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(u'label_event_start', default=u'Event Starts'),
            description=_(u'help_start_location', default=u""),
            with_time=1,
            ),
        ),

    atapi.DateTimeField('endDate',
        required=True,
        searchable=False,
        accessor='end',
        write_permission=ModifyPortalContent,
        default_method=default_end_date,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(u'label_event_end', default=u'Event Ends'),
            description=_(u'help_end_location', default=u""),
            with_time=1,
            ),
        ),

    atapi.StringField('timezone',
        storage=atapi.AnnotationStorage(),
        required=True,
        searchable=False,
        languageIndependent=True,
        vocabulary_factory=u"plone.app.event.AvailableTimezones",
        enforceVocabulary=True,
        default_method='default_timezone',
        widget=atapi.SelectionWidget(
            label=_(u'label_event_timezone', default=u"Timezone"),
            description=_(u'help_event_timezone',
                default=u"Select the Timezone, where this event happens."),
            ),
        ),

    atapi.StringField('recurrence',
        storage=atapi.AnnotationStorage(),
        languageIndependent=True,
        write_permission=ModifyPortalContent,
        validators=('isRecurrence',),
        widget=RecurrenceWidget(
            label=_(u'label_event_recurrence', default=u'Event Recurrence'),
            description=_(u'help_event_recurrence',
                default='Enter recurrence rules, one per line.'),
            ),
        ),

    atapi.TextField('text',
        required=False,
        searchable=True,
        primary=True,
        storage=atapi.AnnotationStorage(migrate=True),
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u'label_event_announcement', default=u'Event body text'),
            description=_(u'help_event_announcement', default=u''),
            rows=25,
            allow_file_upload=zconf.ATDocument.allow_document_upload
            ),
        ),

    atapi.LinesField('attendees',
        languageIndependent=True,
        searchable=True,
        write_permission=ModifyPortalContent,
        widget=atapi.LinesWidget(
            label=_(u'label_event_attendees', default=u'Attendees'),
            description=_(u'help_event_attendees', default=u''),
            ),
        ),

    atapi.StringField('eventUrl',
        required=False,
        searchable=True,
        accessor='event_url',
        write_permission=ModifyPortalContent,
        validators=('isURL',),
        widget=atapi.StringWidget(
            label=_(u'label_event_url', default=u'Event URL'),
            description=_(u'help_event_url',
                default=u"Web address with more info about the event. "
                        u"Add http:// for external links."),
            ),
        ),

    atapi.StringField('contactName',
        required=False,
        searchable=True,
        accessor='contact_name',
        write_permission=ModifyPortalContent,
        widget=atapi.StringWidget(
            label=_(u'label_event_contact_name', default=u'Contact Name'),
            description=_(u'help_event_contact_name', default=u''),
            ),
        ),

    atapi.StringField('contactEmail',
        required=False,
        searchable=True,
        accessor='contact_email',
        write_permission=ModifyPortalContent,
        validators=('isEmail',),
        widget=atapi.StringWidget(
            label=_(u'label_event_contact_email', default=u'Contact E-mail'),
            description=_(u'help_event_contact_email', default=u''),
        ),
    ),

    atapi.StringField('contactPhone',
        required=False,
        searchable=True,
        accessor='contact_phone',
        write_permission=ModifyPortalContent,
        validators=(),
        widget=atapi.StringWidget(
            label=_(u'label_event_contact_phone', default=u'Contact Phone'),
            description=_(u'help_event_contact_phone', default=u'')
            ),
        ),

    ), marshall=atapi.RFC822Marshaller())


# Repurpose the subject field for the event type
ATEventSchema.moveField('subject', before='eventUrl')
ATEventSchema['subject'].write_permission = ModifyPortalContent
ATEventSchema['subject'].widget.label = _(u'label_event_type',
                                          default=u'Event Type(s)')
ATEventSchema['subject'].widget.size = 6
ATEventSchema.changeSchemataForField('subject', 'default')

finalizeATCTSchema(ATEventSchema)
# finalizeATCTSchema moves 'location' into 'categories', we move it back:
ATEventSchema.changeSchemataForField('location', 'default')
ATEventSchema.moveField('location', before='wholeDay')


class ATEvent(ATCTContent, HistoryAwareMixin):
    """ Information about an upcoming event, which can be displayed in the
        calendar."""

    implements(IEvent, IATEvent)

    schema = ATEventSchema
    security = ClassSecurityInfo()
    portal_type = archetype_name = 'Event'

    recurrence = atapi.ATFieldProperty('recurrence')
    timezone = atapi.ATFieldProperty('timezone')
    whole_day = atapi.ATFieldProperty('wholeDay')

    def occurrences(self, limit_start=None, limit_end=None):
        starts = recurrence_sequence_ical(
                self.start(),
                recrule=self.recurrence,
                from_=limit_start, until=limit_end)
        ends = recurrence_sequence_ical(
                self.end(),
                recrule=self.recurrence,
                from_=limit_start, until=limit_end)
        events = map(lambda start,end:(start, end), starts, ends)
        return events

    def to_icalendar(self):
        """ Returns an icalendar object of the event.

        """
        event = self
        ical_event = icalendar.Event()
        ical_event.add('dtstamp', datetime.now())
        ical_event.add('created', pydt(event.creation_date))
        ical_event.add('uid', event.UID())
        ical_event.add('last-modified', pydt(event.modification_date))
        ical_event.add('summary', event.Title())
        ical_event.add('dtstart', pydt(event.start()))
        ical_event.add('dtend', pydt(event.end()))

        recurrence = event.recurrence
        if recurrence:
            ical_event.add('rrule', icalendar.prop.vRecur.from_ical(recurrence))

        description = event.Description()
        if description:
            ical_event.add('description', description)

        location = event.getLocation()
        if location:
            ical_event.add('location', location)

        subject = event.Subject()
        if subject:
            ical_event.add('categories', u','.join(subject))

        # TODO: revisit and implement attendee export according to RFC
        attendees = event.getAttendees()
        for attendee in attendees:
            ical_event.add('attendee', attendee)

        cn = []
        contact = event.contact_name()
        if contact:
            cn.append(contact) # TODO safe_unicode conversion needed?
        phone = event.contact_phone()
        if phone:
            cn.append(phone)
        email = event.contact_email()
        if email:
            cn.append(email)
        if cn:
            ical_event.add('contact', u', '.join(cn))

        url = event.event_url()
        if url:
            ical_event.add('url', url)

        return ical_event

    def default_timezone(self):
        return default_tz()

    security.declareProtected(View, 'post_validate')
    def post_validate(self, REQUEST=None, errors=None):
        """Validates start and end date

        End date must be after start date
        """

        if 'startDate' in errors or 'endDate' in errors:
            # No point in validating bad input
            return

        rstartDate = REQUEST.get('startDate', None)
        rendDate = REQUEST.get('endDate', None)

        if rendDate:
            try:
                end = DateTime(rendDate)
            except:
                errors['endDate'] = _(u'error_invalid_end_date',
                                      default=u'End date is not valid.')
        else:
            end = self.end()
        if rstartDate:
            try:
                start = DateTime(rstartDate)
            except:
                errors['startDate'] = _(u'error_invalid_start_date',
                                        default=u'Start date is not valid.')
        else:
            start = self.start()

        if 'startDate' in errors or 'endDate' in errors:
            # No point in validating bad input
            return

        if start > end:
            errors['endDate'] = _(u'error_end_must_be_after_start_date',
                              default=u'End date must be after start date.')

    def _dt_getter(self, field):
        # always get the date in event's timezone
        timezone = self.getField('timezone').get(self)
        dt = self.getField(field).get(self)
        return dt.toZone(timezone)

    def _dt_setter(self, fieldtoset, value, **kwargs):
        # Always set the date in UTC, saving the timezone in another field.
        # But since the timezone value isn't known at the time of saving the
        # form, we have to save it timezone-naive first and let
        # timezone_handler convert it to the target zone afterwards.

        # Note: The name of the first parameter shouldn't be field, because
        # it's already in kwargs in some case.

        # TODO the endDate and startDate should be updated if the timezone
        # of the event change.
        if not isinstance(value, DateTime): value = DateTime(value)
        value = DateTime('%04d-%02d-%02dT%02d:%02d:%02dZ' % (
                    value.year(),
                    value.month(),
                    value.day(),
                    value.hour(),
                    value.minute(),
                    value.second())
                )
        self.getField(fieldtoset).set(self, value, **kwargs)


    #
    # We MUST make sure we are storing datetime fields in UTC
    #

    security.declareProtected('View', 'start')
    def start(self):
        return self._dt_getter('startDate')

    security.declareProtected('View', 'end')
    def end(self):
        return self._dt_getter('endDate')

    security.declareProtected(ModifyPortalContent, 'setStartDate')
    def setStartDate(self, value, **kwargs):
        self._dt_setter('startDate', value, **kwargs)

    security.declareProtected(ModifyPortalContent, 'setEndDate')
    def setEndDate(self, value, **kwargs):
        self._dt_setter('endDate', value, **kwargs)

    # TODO: Why is this needed!!!
    #
    security.declareProtected(ModifyPortalContent, 'update')
    def update(self, event=None, **kwargs):
        # Clashes with BaseObject.update, so
        # we handle gracefully
        info = {}
        if event is not None:
            for field in event.Schema().fields():
                info[field.getName()] = event[field.getName()]
        elif kwargs:
            info = kwargs
        ATCTContent.update(self, **info)


    security.declareProtected(View, 'start_date')
    @property
    def start_date(self):
        value = self['startDate']  # This call the accessor.
        if value is None:
            value = self['creation_date']
        return pydt(value)

    security.declareProtected(View, 'end_date')
    @property
    def end_date(self):
        value = self['endDate']
        if value is None:
            return self.start_date
        return pydt(value)

    security.declareProtected(View, 'duration')
    @property
    def duration(self):
        return self.end_date - self.start_date

    def __cmp__(self, other):
        """Compare method

        If other is based on ATEvent, compare start, duration and title.
        #If other is a number, compare duration and number
        If other is a DateTime instance, compare start date with date
        In all other cases there is no specific order
        """
        # TODO: needed?
        # TODO: maybe also include location to compate two events.

        # Please note that we can not use self.Title() here: the generated
        # edit accessor uses getToolByName, which ends up in
        # five.localsitemanager looking for a parent using a comparison
        # on this object -> infinite recursion.
        if IATEvent.providedBy(other):
            return cmp((self.start_date, self.duration, self.title),
                       (other.start_date, other.duration, other.title))
        elif isinstance(other, DateTime):
            return cmp(self.start(), other)
        else:
            # TODO come up with a nice cmp for types
            return cmp(self.title, other)

    def __hash__(self):
        # TODO: for what's that?
        return hash((self.start_date, self.duration, self.title))


registerATCT(ATEvent, packageName)

def timezone_handler(obj, event):
    """ When setting the startDate and endDate, the value of the timezone field
    isn't known, so we have to convert those timezone-naive dates into
    timezone-aware ones afterwards.

    """
    timezone = obj.getField('timezone').get(obj)
    start_field = obj.getField('startDate')
    end_field = obj.getField('endDate')
    start = start_field.get(obj)
    end = end_field.get(obj)

    def make_DT(value, timezone):
        return DateTime(
            value.year(),
            value.month(),
            value.day(),
            value.hour(),
            value.minute(),
            value.second(),
            timezone)

    start = make_DT(start, timezone).toZone('UTC')
    end = make_DT(end, timezone).toZone('UTC')
    start_field.set(obj, start)
    end_field.set(obj, end)
    obj.reindexObject()
