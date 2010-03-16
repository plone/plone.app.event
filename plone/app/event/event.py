from types import StringType

from zope.interface import implements

from Products.CMFCore.permissions import ModifyPortalContent, View
from AccessControl import ClassSecurityInfo
from DateTime import DateTime
from ComputedAttribute import ComputedAttribute

from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import KeywordWidget
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import RFC822Marshaller
from Products.Archetypes.atapi import AnnotationStorage

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.interfaces import IATEvent
from Products.ATContentTypes.lib.historyaware import HistoryAwareMixin

from Products.ATContentTypes import ATCTMessageFactory as _

from plone.app.event.config import PROJECTNAME
from plone.app.event.dtutils import DT2dt

ATEventSchema = ATContentTypeSchema.copy() + Schema((
    StringField('location',
                searchable=True,
                write_permission = ModifyPortalContent,
                widget = StringWidget(
                    description = '',
                    label = _(u'label_event_location', default=u'Event Location')
                    )),

    DateTimeField('startDate',
                  required=True,
                  searchable=False,
                  accessor='start',
                  write_permission = ModifyPortalContent,
                  default_method=DateTime,
                  languageIndependent=True,
                  widget = CalendarWidget(
                        description= '',
                        label=_(u'label_event_start', default=u'Event Starts')
                        )),

    DateTimeField('endDate',
                  required=True,
                  searchable=False,
                  accessor='end',
                  write_permission = ModifyPortalContent,
                  default_method=DateTime,
                  languageIndependent=True,
                  widget = CalendarWidget(
                        description = '',
                        label = _(u'label_event_end', default=u'Event Ends')
                        )),

    TextField('text',
              required=False,
              searchable=True,
              primary=True,
              storage = AnnotationStorage(migrate=True),
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = '',
                        label = _(u'label_event_announcement', default=u'Event body text'),
                        rows = 25,
                        allow_file_upload = zconf.ATDocument.allow_document_upload)),

    LinesField('attendees',
               languageIndependent=True,
               searchable=True,
               write_permission=ModifyPortalContent,
               widget=LinesWidget(
                      description='',
                      label=_(u'label_event_attendees', default=u'Attendees')
                      )),

    StringField('eventUrl',
                required=False,
                searchable=True,
                accessor='event_url',
                write_permission = ModifyPortalContent,
                validators=('isURL',),
                widget = StringWidget(
                        description = _(u'help_event_url',
                                        default=u"Web address with more info about the event. "
                                                 "Add http:// for external links."),
                        label = _(u'label_event_url', default=u'Event URL')
                        )),

    StringField('contactName',
                required=False,
                searchable=True,
                accessor='contact_name',
                write_permission = ModifyPortalContent,
                widget = StringWidget(
                        description = '',
                        label = _(u'label_contact_name', default=u'Contact Name')
                        )),

    StringField('contactEmail',
                required=False,
                searchable=True,
                accessor='contact_email',
                write_permission = ModifyPortalContent,
                validators = ('isEmail',),
                widget = StringWidget(
                        description = '',
                        label = _(u'label_contact_email', default=u'Contact E-mail')
                        )),

    StringField('contactPhone',
                required=False,
                searchable=True,
                accessor='contact_phone',
                write_permission = ModifyPortalContent,
                validators= (),
                widget = StringWidget(
                        description = '',
                        label = _(u'label_contact_phone', default=u'Contact Phone')
                        )),
    ), marshall = RFC822Marshaller()
    )

# Repurpose the subject field for the event type
ATEventSchema.moveField('subject', before='eventUrl')
ATEventSchema['subject'].write_permission = ModifyPortalContent
ATEventSchema['subject'].widget.label = _(
    u'label_event_type', default=u'Event Type(s)')
ATEventSchema['subject'].widget.size = 6
ATEventSchema.changeSchemataForField('subject', 'default')

finalizeATCTSchema(ATEventSchema)
# finalizeATCTSchema moves 'location' into 'categories', we move it back:
ATEventSchema.changeSchemataForField('location', 'default')
ATEventSchema.moveField('location', before='startDate')

class ATEvent(ATCTContent, HistoryAwareMixin):
    """Information about an upcoming event, which can be displayed in the calendar."""

    schema         =  ATEventSchema

    portal_type    = 'Event'
    archetype_name = 'Event'
    _atct_newTypeFor = {'portal_type' : 'CMF Event', 'meta_type' : 'CMF Event'}
    assocMimetypes = ()
    assocFileExt   = ('event', )
    cmf_edit_kws   = ('effectiveDay', 'effectiveMo', 'effectiveYear',
                      'expirationDay', 'expirationMo', 'expirationYear',
                      'start_time', 'startAMPM', 'stop_time', 'stopAMPM',
                      'start_date', 'end_date', 'contact_name', 'contact_email',
                      'contact_phone', 'event_url')

    implements(IATEvent)

    security       = ClassSecurityInfo()

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
            sdate = '%s-%s-%s %s %s' % (effectiveDay, effectiveMo, effectiveYear,
                                         start_time, startAMPM)
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

    def _start_date(self):
        value = self['startDate']
        if value is None:
            value = self['creation_date']
        return DT2dt(value)

    security.declareProtected(View, 'start_date')
    start_date = ComputedAttribute(_start_date)

    def _end_date(self):
        value = self['endDate']
        if value is None:
            return self.start_date
        return DT2dt(value)

    security.declareProtected(View, 'end_date')
    end_date = ComputedAttribute(_end_date)

    def _duration(self):
        return self.end_date - self.start_date

    security.declareProtected(View, 'duration')
    duration = ComputedAttribute(_duration)

    def __cmp__(self, other):
        """Compare method

        If other is based on ATEvent, compare start, duration and title.
        #If other is a number, compare duration and number
        If other is a DateTime instance, compare start date with date
        In all other cases there is no specific order
        """
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
