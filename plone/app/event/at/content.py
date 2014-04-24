from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from Products.Archetypes.interfaces import IObjectPostValidation
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFPlone.utils import safe_unicode
from plone.app.event import messageFactory as _
from plone.app.event.at import atapi
from plone.app.event.at import packageName
from plone.app.event.at.interfaces import IATEvent, IATEventRecurrence
from plone.app.event.base import DT
from plone.app.event.base import default_end as default_end_dt
from plone.app.event.base import default_start as default_start_dt
from plone.app.event.base import default_timezone
from plone.app.event.base import first_weekday
from plone.app.event.base import wkday_to_mon1
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventAccessor
from plone.event.utils import pydt
from plone.event.utils import utc
from plone.formwidget.datetime.at import DatetimeWidget
from plone.formwidget.recurrence.at.widget import RecurrenceWidget
from plone.indexer import indexer
from plone.uuid.interfaces import IUUID
from zope.component import adapts
from zope.event import notify
from zope.globalrequest import getRequest
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent


def default_start():
    return DT(default_start_dt())


def default_end():
    return DT(default_end_dt())


def first_weekday_sun0():
    return wkday_to_mon1(first_weekday())


ATEventSchema = ATContentTypeSchema.copy() + atapi.Schema((

    atapi.DateTimeField(
        'startDate',
        required=True,
        searchable=False,
        accessor='start',
        write_permission=ModifyPortalContent,
        default_method=default_start,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(
                u'label_event_start',
                default=u'Event Starts'
            ),
            description=_(
                u'help_event_start',
                default=u"Date and Time, when the event begins."
            ),
            with_time=1,
            first_day=first_weekday_sun0,
        ),
    ),

    atapi.DateTimeField(
        'endDate',
        required=True,
        searchable=False,
        accessor='end',
        write_permission=ModifyPortalContent,
        default_method=default_end,
        languageIndependent=True,
        widget=DatetimeWidget(
            label=_(
                u'label_event_end',
                default=u'Event Ends'
            ),
            description=_(
                u'help_event_end',
                default=u"Date and Time, when the event ends."
            ),
            with_time=1,
            first_day=first_weekday_sun0,
        ),
    ),

    atapi.BooleanField(
        'wholeDay',
        required=False,
        default=False,
        write_permission=ModifyPortalContent,
        languageIndependent=True,
        widget=atapi.BooleanWidget(
            label=_(
                u'label_event_whole_day',
                default=u'Whole Day'
            ),
            description=_(
                u'help_event_whole_day',
                default=u"Event lasts whole day."
            ),
        ),
    ),

    atapi.BooleanField(
        'openEnd',
        required=False,
        default=False,
        write_permission=ModifyPortalContent,
        widget=atapi.BooleanWidget(
            label=_(
                u'label_event_open_end',
                default=u"Open End"
            ),
            description=_(
                u'help_event_open_end',
                default=u"This event is open ended."
            ),
        ),
    ),

    atapi.StringField(
        'timezone',
        required=True,
        searchable=False,
        languageIndependent=True,
        vocabulary_factory=u"plone.app.event.AvailableTimezones",
        enforceVocabulary=True,
        default_method=default_timezone,
        widget=atapi.SelectionWidget(
            label=_(
                u'label_event_timezone',
                default=u"Timezone"
            ),
            description=_(
                u'help_event_timezone',
                default=u"Select the Timezone, where this event happens."
            ),
        ),
    ),

    atapi.StringField(
        'recurrence',
        languageIndependent=True,
        write_permission=ModifyPortalContent,
        validators=('isRecurrence',),
        widget=RecurrenceWidget(
            label=_(
                u'label_event_recurrence',
                default=u'Recurrence'
            ),
            description=_(
                u'help_event_recurrence',
                default='Define the event recurrence rule.'
            ),
            startFieldYear='startDate-year',
            startFieldMonth='startDate-month',
            startFieldDay='startDate-day',
            first_day=first_weekday_sun0,
            show_repeat_forever=False
        ),
    ),

    atapi.StringField(
        'location',
        searchable=True,
        write_permission=ModifyPortalContent,
        widget=atapi.StringWidget(
            label=_(
                u'label_event_location',
                default=u'Location'
            ),
            description=_(
                u'help_event_location',
                default=u"Location of the event."
            ),
        ),
    ),

    atapi.LinesField(
        'attendees',
        languageIndependent=True,
        searchable=True,
        write_permission=ModifyPortalContent,
        widget=atapi.LinesWidget(
            label=_(
                u'label_event_attendees',
                default=u'Attendees'
            ),
            description=_(
                u'help_event_attendees',
                default=u'List of attendees.'
            ),
        ),
    ),

    atapi.StringField(
        'contactName',
        required=False,
        searchable=True,
        accessor='contact_name',
        write_permission=ModifyPortalContent,
        widget=atapi.StringWidget(
            label=_(
                u'label_event_contact_name',
                default=u'Contact Name'
            ),
            description=_(
                u'help_event_contact_name',
                default=u'Name of a person to contact about this event.'
            ),
        ),
    ),

    atapi.StringField(
        'contactEmail',
        required=False,
        searchable=True,
        accessor='contact_email',
        write_permission=ModifyPortalContent,
        validators=('isEmail',),
        widget=atapi.StringWidget(
            label=_(
                u'label_event_contact_email',
                default=u'Contact E-mail'
            ),
            description=_(
                u'help_event_contact_email',
                default=u'Email address to contact about this event.'
            ),
        ),
    ),

    atapi.StringField(
        'contactPhone',
        required=False,
        searchable=True,
        accessor='contact_phone',
        write_permission=ModifyPortalContent,
        validators=(),
        widget=atapi.StringWidget(
            label=_(
                u'label_event_contact_phone',
                default=u'Contact Phone'
            ),
            description=_(
                u'help_event_contact_phone',
                default=u'Phone number to contact about this event.'
            ),
        ),
    ),

    atapi.StringField(
        'eventUrl',
        required=False,
        searchable=True,
        accessor='event_url',
        write_permission=ModifyPortalContent,
        validators=('isURL',),
        widget=atapi.StringWidget(
            label=_(
                u'label_event_url',
                default=u'Event URL'
            ),
            description=_(
                u'help_event_url',
                default=u"Web address with more info about the event. "
                        u"Add http:// for external links."
            ),
        ),
    ),

    atapi.StringField(
        'eventUid',
        write_permission=ModifyPortalContent,
        widget=atapi.StringWidget(
            visible={'edit': 'invisible', 'view': 'invisible'}),
    ),

    atapi.TextField(
        'text',
        required=False,
        searchable=True,
        primary=True,
        storage=atapi.AnnotationStorage(migrate=True),
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(
                u'label_event_announcement',
                default=u'Event body text'
            ),
            description=_(
                u'help_event_announcement',
                default=u''
            ),
            rows=25,
            allow_file_upload=zconf.ATDocument.allow_document_upload
        ),
    ),

), marshall=atapi.RFC822Marshaller())


# Repurpose the subject field for the event type
ATEventSchema.moveField('subject', before='eventUrl')
ATEventSchema['subject'].write_permission = ModifyPortalContent
ATEventSchema['subject'].widget.size = 6
ATEventSchema.changeSchemataForField('subject', 'default')

ATEventSchema.changeSchemataForField('timezone', 'dates')
ATEventSchema.moveField('timezone', before='effectiveDate')

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

    cmf_edit_kws = ('effectiveDay', 'effectiveMo', 'effectiveYear',
                    'expirationDay', 'expirationMo', 'expirationYear',
                    'start_time', 'startAMPM', 'stop_time', 'stopAMPM',
                    'start_date', 'end_date', 'contact_name', 'contact_email',
                    'contact_phone', 'event_url')
    security.declarePrivate('cmf_edit')
    def cmf_edit(
        self, title=None, description=None, effectiveDay=None,
        effectiveMo=None, effectiveYear=None, expirationDay=None,
        expirationMo=None, expirationYear=None, start_date=None,
        start_time=None, startAMPM=None, end_date=None,
        stop_time=None, stopAMPM=None, location=None,
        contact_name=None, contact_email=None, contact_phone=None,
        event_url=None):

        if effectiveDay and effectiveMo and effectiveYear and start_time:
            sdate = '%s-%s-%s %s %s' % (
                effectiveDay, effectiveMo, effectiveYear,
                start_time, startAMPM
            )
        elif start_date:
            if not start_time:
                start_time = '00:00:00'
            sdate = '%s %s' % (start_date, start_time)
        else:
            sdate = None

        if expirationDay and expirationMo and expirationYear and stop_time:
            edate = '%s-%s-%s %s %s' % (expirationDay, expirationMo,
                                        expirationYear, stop_time, stopAMPM)
        elif end_date:
            if not stop_time:
                stop_time = '00:00:00'
            edate = '%s %s' % (end_date, stop_time)
        else:
            edate = None

        if sdate and edate:
            if edate < sdate:
                edate = sdate
            self.setStartDate(sdate)
            self.setEndDate(edate)

        self.update(
            title=title, description=description, location=location,
            contactName=contact_name, contactEmail=contact_email,
            contactPhone=contact_phone, eventUrl=event_url)

    ###
    # Timezone / start / end getter / setter
    security.declareProtected(ModifyPortalContent, 'setTimezone')
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

    security.declarePrivate('_dt_getter')
    def _dt_getter(self, field):
        # Always get the date in event's timezone
        timezone = self.getField('timezone').get(self)
        dt = self.getField(field).get(self)
        return dt.toZone(timezone)

    security.declarePrivate('_dt_setter')
    def _dt_setter(self, fieldtoset, value, **kwargs):
        """Always set the date in UTC, saving the timezone in another field.
        But since the timezone value isn't known at the time of saving the
        form, we have to save it timezone-naive first and let
        timezone_handler convert it to the target zone afterwards.
        """
        # Note: The name of the first parameter shouldn't be field, because
        # it's already in kwargs in some case.

        if not isinstance(value, DateTime):
            value = DT(value)

        # This way, we set DateTime timezoneNaive
        value = DateTime(
            '%04d-%02d-%02dT%02d:%02d:%02d' % (
                value.year(),
                value.month(),
                value.day(),
                value.hour(),
                value.minute(),
                int(value.second())  # No microseconds
            )
        )
        self.getField(fieldtoset).set(self, value, **kwargs)

    security.declareProtected(View, 'start')
    def start(self):
        return self._dt_getter('startDate')

    security.declareProtected(View, 'end')
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
        return pydt(self.start(), exact=False)

    security.declareProtected(View, 'end_date')
    @property
    def end_date(self):
        """ Return end date as Python datetime.

        Please note, the end date marks only the end of an individual
        occurrence and not the end of a recurrence sequence.

        :returns: End of the event.
        :rtype: Python datetime
        """
        return pydt(self.end(), exact=False)

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
        """Compare method.

        If other is based on ATEvent, compare start, duration and title.
        #If other is a number, compare duration and number
        If other is a DateTime instance, compare start date with date
        In all other cases there is no specific order.
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


class StartEndDateValidator(object):
    """Checks whether startDate is before endDate. In case the event is
    openEnded this check is skipped.
    """
    implements(IObjectPostValidation)
    adapts(IATEvent)

    def __init__(self, context):
        self.context = context

    def __call__(self, request):
        rstartDate = request.form.get('startDate', None)
        rendDate = request.form.get('endDate', None)

        errors = {}

        if rstartDate:
            try:
                start = DateTime(rstartDate)
            except:
                errors['startDate'] = _(u'error_invalid_start_date',
                                        default=u'Start date is not valid.')
        else:
            start = self.context.start()

        openEnd = request.form.get('openEnd', False)
        if openEnd:
            # In case the event has an open end, enddate is set automatically
            # later and we need not check it
            return errors

        if rendDate:
            try:
                end = DateTime(rendDate)
            except:
                errors['endDate'] = _(u'error_invalid_end_date',
                                      default=u'End date is not valid.')
        else:
            end = self.context.end()

        if 'startDate' in errors or 'endDate' in errors:
            # No point in validating bad input
            return errors

        if start > end:
            errors['endDate'] = _(
                u'error_end_must_be_after_start_date',
                default=u'End date must be after start date.'
            )

        return errors and errors or None


## Event handlers

def data_postprocessing(obj, event):
    """When setting the startDate and endDate, the value of the timezone field
    isn't known, so we have to convert those timezone-naive dates into
    timezone-aware ones afterwards.

    For whole day events, set start time to 0:00:00 and end time to 23:59:59.
    For open end events, set end time to 23:59:59.
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
    if prev_tz:
        delattr(obj, 'previous_timezone')

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
            int(value.second()),  # No microseconds
            timezone)

    start = make_DT(start, timezone)
    end = make_DT(end, timezone)

    whole_day = obj.getWholeDay()
    open_end = obj.getOpenEnd()
    if whole_day:
        start = DateTime('%s 0:00:00 %s' % (start.Date(), timezone))
    if open_end:
        end = start  # Open end events end on same day
    if open_end or whole_day:
        end = DateTime('%s 23:59:59 %s' % (end.Date(), timezone))

    start_field.set(obj, start.toZone('UTC'))
    end_field.set(obj, end.toZone('UTC'))

    if not obj.getEventUid():
        # sync_uid has to be set for icalendar data exchange.
        uid = IUUID(obj)
        # We don't want to fail when getRequest() returns None, e.g when
        # creating an event during test layer setup time.
        request = getRequest() or {}
        domain = request.get('HTTP_HOST')
        obj.setEventUid('%s%s' % (
            uid,
            domain and '@%s' % domain or ''
        ))

    obj.reindexObject()


# icalendar event UID indexer
@indexer(IATEvent)
def sync_uid_indexer(obj):
    sync_uid = obj.getEventUid()
    if not sync_uid:
        return None
    return sync_uid


## Object adapters

class EventAccessor(object):
    """ Generic event accessor adapter implementation for Archetypes content
        objects.
    """
    implements(IEventAccessor)
    adapts(IATEvent)
    event_type = 'Event'  # If you use a custom content-type, override this.

    def __init__(self, context):
        self.context = context

    # Unified create method via Accessor
    @classmethod
    def create(cls, container, content_id, title, description=None,
               start=None, end=None, timezone=None, whole_day=None,
               open_end=None, **kwargs):
        container.invokeFactory(cls.event_type,
                                id=content_id,
                                title=title,
                                description=description,
                                startDate=start,
                                endDate=end,
                                wholeDay=whole_day,
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


    # RO PROPERTIES

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
        return safe_unicode(self.context.Description())
    @description.setter
    def description(self, value):
        self.context.setDescription(safe_unicode(value))

    @property
    def last_modified(self):
        return utc(self.context.modification_date)
    @last_modified.setter
    def last_modified(self, value):
        tz = default_timezone(self.context, as_tzinfo=True)
        mod = DT(pydt(value, missing_zone=tz))
        setattr(self.context, 'modification_date', mod)

    @property
    def start(self):
        return self.context.start_date
    @start.setter
    def start(self, value):
        self.context.setStartDate(value)

    @property
    def end(self):
        return self.context.end_date
    @end.setter
    def end(self, value):
        self.context.setEndDate(value)

    @property
    def whole_day(self):
        return self.context.getWholeDay()
    @whole_day.setter
    def whole_day(self, value):
        self.context.setWholeDay(value)

    @property
    def open_end(self):
        return self.context.getOpenEnd()
    @open_end.setter
    def open_end(self, value):
        self.context.setOpenEnd(value)

    @property
    def timezone(self):
        return safe_unicode(self.context.getTimezone())
    @timezone.setter
    def timezone(self, value):
        self.context.setTimezone(safe_unicode(value))

    @property
    def recurrence(self):
        return safe_unicode(self.context.getRecurrence())
    @recurrence.setter
    def recurrence(self, value):
        self.context.setRecurrence(safe_unicode(value))

    @property
    def location(self):
        return safe_unicode(self.context.getLocation())
    @location.setter
    def location(self, value):
        self.context.setLocation(safe_unicode(value))

    @property
    def attendees(self):
        return self.context.getAttendees()
    @attendees.setter
    def attendees(self, value):
        if value:
            self.context.setAttendees(value)

    @property
    def contact_name(self):
        return safe_unicode(self.context.contact_name())
    @contact_name.setter
    def contact_name(self, value):
        self.context.setContactName(safe_unicode(value))

    @property
    def contact_email(self):
        return safe_unicode(self.context.contact_email())
    @contact_email.setter
    def contact_email(self, value):
        self.context.setContactEmail(safe_unicode(value))

    @property
    def contact_phone(self):
        return safe_unicode(self.context.contact_phone())
    @contact_phone.setter
    def contact_phone(self, value):
        self.context.setContactPhone(safe_unicode(value))

    @property
    def event_url(self):
        return safe_unicode(self.context.event_url())
    @event_url.setter
    def event_url(self, value):
        self.context.setEventUrl(safe_unicode(value))

    @property
    def sync_uid(self):
        return self.context.getEventUid()
    @sync_uid.setter
    def sync_uid(self, value):
        self.context.setEventUid(value)

    @property
    def subjects(self):
        return self.context.Subject()
    @subjects.setter
    def subjects(self, value):
        if value:
            self.context.setSubject(value)

    @property
    def text(self):
        return safe_unicode(self.context.getText())
    @text.setter
    def text(self, value):
        self.context.setText(safe_unicode(value))
