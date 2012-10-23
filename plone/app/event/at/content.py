from zope.component import adapts
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
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.ATContentTypes import ATCTMessageFactory as _

from plone.formwidget.recurrence.at.widget import RecurrenceWidget
from plone.formwidget.datetime.at import DatetimeWidget
from plone.uuid.interfaces import IUUID

from plone.app.event.at import atapi
from plone.app.event.at import packageName
from plone.app.event.at.interfaces import IATEvent, IATEventRecurrence
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.utils import utc
from plone.app.event.base import default_end_DT
from plone.app.event.base import default_start_DT
from plone.app.event.base import default_timezone
from plone.app.event.base import DT
from plone.event.utils import pydt


ATEventSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.DateTimeField('startDate',
        required=True,
        searchable=False,
        accessor='start',
        write_permission=ModifyPortalContent,
        default_method=default_start_DT,
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
        default_method=default_end_DT,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(u'label_event_end', default=u'Event Ends'),
            description=_(u'help_end_location', default=u""),
            with_time=1,
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

    atapi.StringField('timezone',
        required=True,
        searchable=False,
        languageIndependent=True,
        vocabulary_factory=u"plone.app.event.AvailableTimezones",
        enforceVocabulary=True,
        default_method=default_timezone,
        widget=atapi.SelectionWidget(
            label=_(u'label_event_timezone', default=u"Timezone"),
            description=_(u'help_event_timezone',
                default=u"Select the Timezone, where this event happens."),
            ),
        ),

    atapi.StringField('recurrence',
        languageIndependent=True,
        write_permission=ModifyPortalContent,
        validators=('isRecurrence',),
        widget=RecurrenceWidget(
            label=_(u'label_event_recurrence', default=u'Event Recurrence'),
            description=_(u'help_event_recurrence',
                default='Enter recurrence rules, one per line.'),
            startFieldYear='startDate-year',
            startFieldMonth='startDate-month',
            startFieldDay='startDate-day',
            ),
        ),

    atapi.StringField('location',
        searchable=True,
        write_permission=ModifyPortalContent,
        widget=atapi.StringWidget(
            label=_(u'label_event_location', default=u'Event Location'),
            description=_(u'help_event_location', default=u""),
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

    atapi.StringField('contactName',
        required=False,
        searchable=True,
        accessor='contact_name',
        write_permission=ModifyPortalContent,
        widget=atapi.StringWidget(
            label=_(u'label_contact_name', default=u'Contact Name'),
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
            label=_(u'label_contact_email', default=u'Contact E-mail'),
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
            label=_(u'label_contact_phone', default=u'Contact Phone'),
            description=_(u'help_event_contact_phone', default=u'')
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
ATEventSchema.moveField('location', before='attendees')


class ATEvent(ATCTContent, HistoryAwareMixin):
    """Information about an upcoming event, which can be displayed in the
    calendar.

    """
    implements(IATEvent, IATEventRecurrence)

    schema = ATEventSchema
    security = ClassSecurityInfo()
    portal_type = archetype_name = 'Event'

    # TODO: rethink this
    # if we want recurrence and timezone be ATFieldProperties, then we need
    # them to be stored in AnnotationStorage to avoid namespace clashes.
    # if we access the object via the generic_event_accessor always, we might
    # not need the convinient ATFieldProperties and avoid AnnotationStorage for
    # those attributes.
    whole_day = atapi.ATFieldProperty('wholeDay')

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

    ###
    # Timezone / start / end getter / setter
    def setTimezone(self, value, **kwargs):
        tz = self.getField('timezone').get(self)
        if tz:
            # The event is edited and not newly created, otherwise the timezone
            # info wouldn't exist.
            # In order to avoid converting the datetime input to the new target
            # zone after changing the zone but to treat user datetime input as
            # localized, we have to store the old timezone. This way we can
            # restore the datetime input from the context's UTC value before
            # applying the new zone in the data_postprocessing event
            # subscriber.
            self.previous_timezone = tz
        self.getField('timezone').set(self, value, **kwargs)

    def _dt_getter(self, field):
        # Always get the date in event's timezone
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

        if not isinstance(value, DateTime): value = DateTime(value)

        # Get microseconds from seconds, which is a floating value. Round it
        # up, to bypass precision errors.
        micro = int(round(value.second()%1 * 1000000))

        value = DateTime('%04d-%02d-%02dT%02d:%02d:%02d%s' % (
                    value.year(),
                    value.month(),
                    value.day(),
                    value.hour(),
                    value.minute(),
                    value.second(),
                    micro and '.%s' % micro or ''
                    )
                )
        self.getField(fieldtoset).set(self, value, **kwargs)

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

    security.declareProtected(View, 'start_date')
    @property
    def start_date(self):
        """ Return start date as Python datetime.

        :returns: Start of the event.
        :rtype: Python datetime

        """
        return pydt(self.start())

    security.declareProtected(View, 'end_date')
    @property
    def end_date(self):
        """ Return end date as Python datetime.

        Please note, the end date marks only the end of an individual
        occurrence and not the end of a recurrence sequence.

        :returns: End of the event.
        :rtype: Python datetime

        """
        return pydt(self.end())

    security.declareProtected(View, 'duration')
    @property
    def duration(self):
        """ Return duration of the event as Python timedelta.

        :returns: Duration of the event.
        :rtype: Python timedelta

        """
        return self.end_date - self.start_date


    # TODO: Why is this needed?
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

    def __cmp__(self, other):
        """Compare method

        If other is based on ATEvent, compare start, duration and title.
        #If other is a number, compare duration and number
        If other is a DateTime instance, compare start date with date
        In all other cases there is no specific order
        """
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
        return hash((self.start_date, self.duration, self.title))


registerATCT(ATEvent, packageName)


## Event handlers

def data_postprocessing(obj, event):
    """When setting the startDate and endDate, the value of the timezone field
    isn't known, so we have to convert those timezone-naive dates into
    timezone-aware ones afterwards.

    For whole day events, set start time to 0:00:00 and end time toZone
    23:59:59.

    """

    if not IEvent.providedBy(obj):
        # don't run me, if i'm not installed
        return

    timezone = obj.getField('timezone').get(obj)
    start_field = obj.getField('startDate')
    end_field = obj.getField('endDate')

    # The previous_timezone is set, when the timezone has changed to another
    # value. In this case we need to convert the UTC dt values to the
    # previous_timezone, so that we get the datetime values, as the user
    # entered them. However, this value might be always set, even when creating
    # an event, since ObjectModifiedEvent is called several times when editing.
    prev_tz = getattr(obj, 'previous_timezone', None)
    if prev_tz: delattr(obj, 'previous_timezone')

    def _fix_zone(dt, tz):
        if not dt.timezoneNaive():
            # The object is edited and the value alreadty stored in UTC on the
            # object. In this case we want the value converted to the given
            # timezone, in which the user entered the data.
            dt = dt.toZone(tz)
        return dt

    start = _fix_zone(start_field.get(obj), prev_tz and prev_tz or timezone)
    end = _fix_zone(end_field.get(obj), prev_tz and prev_tz or timezone)

    def make_DT(value, timezone):
        return DateTime(
            value.year(),
            value.month(),
            value.day(),
            value.hour(),
            value.minute(),
            value.second(),
            timezone)

    start = make_DT(start, timezone)
    end = make_DT(end, timezone)

    if obj.whole_day:
        start = DateTime('%s 0:00:00 %s' % (start.Date(), timezone))
        end = DateTime('%s 23:59:59 %s' % (end.Date(), timezone))

    start_field.set(obj, start.toZone('UTC'))
    end_field.set(obj, end.toZone('UTC'))
    obj.reindexObject()


## Object adapters

class EventAccessor(object):
    """ Generic event accessor adapter implementation for Archetypes content
        objects.

    """
    implements(IEventAccessor)
    adapts(IATEvent)

    def __init__(self, context):
        self.context = context

    @property
    def uid(self):
        return IUUID(self.context, None)

    @property
    def url(self):
        return self.context.absolute_url()

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
        return getattr(self.context, 'title', None)
    @title.setter
    def title(self, value):
        return setattr(self.context, 'title', value)

    @property
    def description(self):
        return getattr(self.context, 'description', None)
    @description.setter
    def description(self, value):
        return setattr(self.context, 'description', value)


    @property
    def start(self):
        return self.context.start_date
    @start.setter
    def start(self, value):
        self.context.setStartDate(DT(value))

    @property
    def end(self):
        return self.context.end_date
    @end.setter
    def end(self, value):
        self.context.setEndDate(DT(value))

    @property
    def whole_day(self):
        return self.context.whole_day
    @whole_day.setter
    def whole_day(self, value):
        self.context.whole_day = value

    @property
    def timezone(self):
        return self.context.getTimezone()
    @timezone.setter
    def timezone(self, value):
        self.context.setTimezone(value)

    @property
    def recurrence(self):
        return self.context.getRecurrence()
    @recurrence.setter
    def recurrence(self, value):
        self.context.setRecurrence(value)

    @property
    def location(self):
        return self.context.location
    @location.setter
    def location(self, value):
        self.context.setLocation(value)

    @property
    def attendees(self):
        return self.context.attendees
    @attendees.setter
    def attendees(self, value):
        self.context.setAttendees(value)

    @property
    def contact_name(self):
        return self.context.contactName
    @contact_name.setter
    def contact_name(self, value):
        self.context.setContactName(value)

    @property
    def contact_email(self):
        return self.context.contactEmail
    @contact_email.setter
    def contact_email(self, value):
        self.context.setContactEmail(value)

    @property
    def contact_phone(self):
        return self.context.contactPhone
    @contact_phone.setter
    def contact_phone(self, value):
        self.context.setContactPhone(value)

    @property
    def event_url(self):
        return self.context.eventUrl
    @event_url.setter
    def event_url(self, value):
        self.context.setEventUrl(value)

    @property
    def subjects(self):
        return self.context.Subject()
    @subjects.setter
    def subjects(self, value):
        self.context.setSubject(value)

    @property
    def text(self):
        return self.context.getText()
    @text.setter
    def text(self, value):
        self.context.setText(value)
