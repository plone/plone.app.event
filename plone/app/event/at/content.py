from plone.app.event.at import atapi

from zope.interface import implements

from DateTime import DateTime
from AccessControl import ClassSecurityInfo

from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from Products.CMFPlone.utils import safe_unicode
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

from plone.app.event.interfaces import IEvent
from plone.app.event.config import PROJECTNAME
from plone.app.event.base import default_end_date
from plone.app.event.base import default_timezone


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
        accessor='whole_day',
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
        required=True,
        searchable=False,
        languageIndependent=True,
        vocabulary_factory=u"plone.app.event.AvailableTimezonesVocabulary",
        enforceVocabulary=True,
        default_method='default_timezone',
        widget=atapi.SelectionWidget(
            label = _(u'label_event_timezone', default=u"Timezone"),
            description = _(u'help_event_timezone',
                default=u"Select the Timezone, where this event happens."),
            ),
        ),

    atapi.StringField('recurrence',
        storage=atapi.AnnotationStorage(),
        languageIndependent=True,
        write_permission=ModifyPortalContent,
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
ATEventSchema['subject'].widget.label = _(u'label_event_type', default=u'Event Type(s)')
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

    title = safe_unicode(atapi.ATFieldProperty('title'))
    description = safe_unicode(atapi.ATFieldProperty('description'))

    # TODO: do this for all event fields of IEvent interface
    recurrence = atapi.ATFieldProperty('recurrence')


    def default_timezone(self):
        return default_timezone(self)

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
        # The name of the first parameter shouldn't be field, because
        # it's already in kwargs in some case.
        #
        # always set the date in UTC
        # TODO timezone field is not already handled by the add form,
        # so we get the default timezone :(
        # TODO the endDate and startDate should be updated if the timezone
        # of the event change.
        timezone = self.getField('timezone').get(self)
        if not isinstance(value, DateTime): value = DateTime(value)
        value = DateTime(
                value.year(),
                value.month(),
                value.day(),
                value.hour(),
                value.minute(),
                value.second(),
                timezone)
        value = value.toZone('UTC')
        self.getField(fieldtoset).set(self, value, **kwargs)
        # TODO: remove that print statement
#        print("set %s: %s" % (field, value))
        #self.reindexObject()


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


registerATCT(ATEvent, PROJECTNAME)
