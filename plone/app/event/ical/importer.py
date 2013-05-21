# TODO:
#  - implement sync strategies,
#  - cleanup,
#  - tests
from Products.CMFPlone.utils import safe_unicode
from plone.app.event import base
from plone.event.interfaces import IEventAccessor
from plone.event.utils import date_to_datetime
from plone.event.utils import is_date
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import datetime
import icalendar
import random
import transaction
import urllib2


def ical_import(container, ics_resource, event_type):
    cal = icalendar.Calendar.from_ical(ics_resource)
    events = cal.walk('VEVENT')

    def _get_prop(prop, item):
        ret = None
        if prop in item:
            ret = safe_unicode(item.decoded(prop))
        return ret

    count = 0
    for item in events:
        start = _get_prop('DTSTART', item)
        end = _get_prop('DTEND', item)
        if not end:
            duration = _get_prop('DURATION', item)
            if duration:
                end = start + duration
            # else: whole day or open end

        timezone = getattr(getattr(start, 'tzinfo', None), 'zone', None) or\
                base.default_timezone(container)

        whole_day = False
        open_end = False
        if is_date(start) and (is_date(end) or end is None):
            # All day / whole day events
            # End must be same type as start (RFC5545, 3.8.2.2)
            whole_day = True
            if end is None: end = start
            if start < end:
                # RFC5545 doesn't define clearly, if all day events should have
                # a end date one day after the start day at 0:00.
                # Internally, we handle all day events with start=0:00,
                # end=:23:59:59, so we substract one day here.
                end = end - datetime.timedelta(days=1)
            start = base.dt_start_of_day(date_to_datetime(start))
            end = base.dt_end_of_day(date_to_datetime(end))
        elif isinstance(start, datetime) and end is None:
            # Open end event, see RFC 5545, 3.6.1
            open_end = True
            end = base.dt_end_of_day(date_to_datetime(start))
        assert(isinstance(start, datetime.datetime))
        assert(isinstance(end, datetime.datetime))

        title = _get_prop('SUMMARY', item)
        description = _get_prop('DESCRIPTION', item)
        location = _get_prop('LOCATION', item)

        url = _get_prop('URL', item)

        rrule = _get_prop('RRULE', item)
        rrule = rrule and 'RRULE:%s' % rrule.to_ical() or ''
        rdate = _get_prop('RDATE', item)
        rrule = rdate and '%s\nRDATE:%s' % (rrule, rdate.to_ical()) or ''
        exdate = _get_prop('EXDATE', item)
        rrule = exdate and '%s\nEXDATE:%s' % (rrule, exdate.to_ical()) or ''

        attendees = _get_prop('ATTENDEE', item)
        contact = _get_prop('CONTACT', item)
        categories = _get_prop('CATEGORIES', item)
        if hasattr(categories, '__iter__'):
            categories = [safe_unicode(it) for it in categories]

        # for sync
        created = _get_prop('CREATED', item)
        modified = _get_prop('LAST-MODIFIED', item)

        # TODO: better use plone.api, from which some of the code here is
        # copied
        content_id = str(random.randint(0, 99999999))

        # TODO: if AT had the same attrs like IDXEventBase, we could set
        # everything within this invokeFactory call.
        container.invokeFactory(event_type,
                                id=content_id,
                                title=title,
                                description=description)
        content = container[content_id]

        event = IEventAccessor(content)
        event.start = start
        event.end = end
        event.timezone = timezone
        event.whole_day = whole_day
        event.open_end = open_end
        event.location = location
        event.event_url = url
        event.recurrence = rrule
        event.attendees = attendees
        event.contact_name = contact
        event.subjects = categories
        notify(ObjectModifiedEvent(content))

        # Archetypes specific code
        if getattr(content, 'processForm', False):
            # Will finish Archetypes content item creation process,
            # rename-after-creation and such
            content.processForm()

        if content_id in container:
            # Rename with new id from title, if processForm didn't do it.
            chooser = INameChooser(container)
            new_id = chooser.chooseName(title, content)
            transaction.savepoint(optimistic=True)  # Commit before renaming
            content.aq_parent.manage_renameObject(content_id, new_id)
        else:
            transaction.savepoint(optimistic=True)

        count += 1

    return {'count': count}


from zope.interface import Interface
from zope import schema
from plone.app.event import messageFactory as _
from plone.namedfile.field import NamedFile


class IIcalendarImportSettings(Interface):

    event_type = schema.Choice(
        title=_(u'Event Type'),
        vocabulary='plone.app.event.EventTypes',
        required=True
    )

    ical_url = schema.URI(
        title=_(u'Icalendar URL'),
        required=False
    )

    ical_file = NamedFile(
        title=_(u"Icalendar File"),
        required=False
    )

    # TODO: to implement
    #sync_strategy = schema.Choice(
    #    title=_(u"Synchronization Strategy"),
    #    vocabulary='plone.app.event.SynchronizationStrategies',
    #    required=True
    #)


from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict


class AnnotationAdapter(object):
    """Abstract Base Class for an annotation storage.
    """
    ANNOTATION_KEY = None

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self._data = annotations.get(self.ANNOTATION_KEY, None)
        if self._data is None:
            self._data = PersistentDict()
            annotations[self.ANNOTATION_KEY] = self._data

    def __setattr__(self, name, value):
        if name in ('context', '_data'):
            self.__dict__[name] = value
        else:
            self._data[name] = value

    def __getattr__(self, name):
        return self._data.get(name, None)


from zope.component import adapts
from zope.interface import implements
#from plone.folder.interfaces import IFolder


class IcalendarImportSettings(AnnotationAdapter):
    """Annotation Adapter for IIcalendarImportSettings.
    """
    implements(IIcalendarImportSettings)
    adapts(Interface)

    #adapts(IFolder) ## ?? TODO: when adapting this in z3c.form, why is a
                     ## ATFolder not adaptable to this adapter, when it
                     ## implements IFolder?

    ANNOTATION_KEY = "icalendar_import_settings"


from Products.Five.browser import BrowserView
from plone.folder.interfaces import IFolder
from plone.app.event.interfaces import IICalendarImportEnabled


class IcalendarImportTool(BrowserView):

    @property
    def available(self):
        return IFolder.providedBy(self.context)

    @property
    def available_disabled(self):
        return self.available and not self.enabled

    @property
    def enabled(self):
        return IICalendarImportEnabled.providedBy(self.context)


from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import form, field
from zope.interface import alsoProvides, noLongerProvides


class IcalendarImportSettingsForm(form.Form):

    fields = field.Fields(IIcalendarImportSettings)
    ignoreContext = False

    def updateWidgets(self):
        super(IcalendarImportSettingsForm, self).updateWidgets()

    def getContent(self):
        data = {}
        settings = IIcalendarImportSettings(self.context)
        data['event_type'] = settings.event_type
        data['ical_url'] = settings.ical_url
        #data['sync_strategy'] = settings.sync_strategy
        return data

    @button.buttonAndHandler(u'Save and Import')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        settings = IIcalendarImportSettings(self.context)

        ical_file = data['ical_file']
        if ical_file:
            # File upload is not saved in settings
            ical_resource = ical_file.data
            ical_import_from = ical_file.filename
        else:
            ical_url = settings.ical_url = data['ical_url']
            ical_resource = urllib2.urlopen(ical_url, 'rb').read()
            ical_import_from = ical_url
        event_type = settings.event_type = data['event_type']

        import_metadata = ical_import(
            self.context,
            ics_resource=ical_resource,
            event_type=event_type
        )

        count = import_metadata['count']

        IStatusMessage(self.request).addStatusMessage(
            "%s events imported from %s" % (count, ical_import_from),
            'info')
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())


from plone.z3cform.layout import FormWrapper


class IcalendarImportSettingsFormView(FormWrapper):
    form = IcalendarImportSettingsForm

    def enable(self):
        """Enable icalendar import on this context.
        """
        alsoProvides(self.context, IICalendarImportEnabled)
        self.context.reindexObject(idxs=('object_provides'))
        self.request.response.redirect(self.context.absolute_url())

    def disable(self):
        """Disable icalendar import on this context.
        """
        noLongerProvides(self.context, IICalendarImportEnabled)
        self.context.reindexObject(idxs=('object_provides'))
        self.request.response.redirect(self.context.absolute_url())
