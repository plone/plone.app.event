from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.event import base
from plone.app.event import messageFactory as _
from plone.app.event.base import AnnotationAdapter
from plone.app.event.interfaces import IICalendarImportEnabled
from plone.event.interfaces import IEventAccessor
from plone.event.utils import date_to_datetime
from plone.event.utils import is_date
from plone.event.utils import is_datetime
from plone.event.utils import utc
from plone.folder.interfaces import IFolder
from plone.namedfile.field import NamedFile
from plone.z3cform.layout import FormWrapper
from z3c.form import button
from z3c.form import form, field
from zope import schema
from zope.component import adapts
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.interface import Interface
from zope.interface import alsoProvides, noLongerProvides
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent

import datetime
import icalendar
import random
import transaction
import urllib2


def ical_import(container, ics_resource, event_type,
                sync_strategy=base.SYNC_KEEP_NEWER):
    cal = icalendar.Calendar.from_ical(ics_resource)
    events = cal.walk('VEVENT')

    cat = getToolByName(container, 'portal_catalog')
    container_path = '/'.join(container.getPhysicalPath())

    def _get_by_sync_uid(uid):
        return cat(
            sync_uid=uid,
            path={'query': container_path, 'depth': 1}
        )

    def _get_prop(prop, item, default=None):
        ret = default
        if prop in item:
            ret = safe_unicode(item.decoded(prop))
        return ret

    def _from_list(ical, prop):
        """For EXDATE and RDATE recurrence component properties, the dates can
        be defined within one EXDATE/RDATE line or for each date an individual
        line.
        In the latter case, icalendar creates a list.
        This method handles this case.

        TODO: component property parameters like TZID are not used here.
        """
        val = prop in ical and ical[prop] or []
        if not isinstance(val, list):
            val = [val]
        #ret = ''
        #for item in val:
        #    ret = ret and '%s\n' % ret or ret  # insert linebreak
        #    ret = '%s%s:%s' % (ret, prop, item.to_ical())
        #return ret

        # Zip multiple lines into one, since jquery.recurrenceinput.js does
        # not support multiple lines here
        # https://github.com/collective/jquery.recurrenceinput.js/issues/15
        ret = ''
        for item in val:
            ret = ret and '%s,' % ret or ret  # insert linebreak
            ret = '%s%s' % (ret, item.to_ical())
        return ret and '%s:%s' % (prop, ret) or None

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
            if end is None:
                end = start
            if start < end:
                # RFC5545 doesn't define clearly, if all day events should have
                # a end date one day after the start day at 0:00.
                # Internally, we handle all day events with start=0:00,
                # end=:23:59:59, so we substract one day here.
                end = end - datetime.timedelta(days=1)
            start = base.dt_start_of_day(date_to_datetime(start))
            end = base.dt_end_of_day(date_to_datetime(end))
        elif is_datetime(start) and end is None:
            # Open end event, see RFC 5545, 3.6.1
            open_end = True
            end = base.dt_end_of_day(date_to_datetime(start))
        assert(is_datetime(start))
        assert(is_datetime(end))

        title = _get_prop('SUMMARY', item)
        description = _get_prop('DESCRIPTION', item)
        location = _get_prop('LOCATION', item)

        url = _get_prop('URL', item)

        rrule = _get_prop('RRULE', item)
        rrule = rrule and 'RRULE:%s' % rrule.to_ical() or ''
        rdates = _from_list(item, 'RDATE')
        exdates = _from_list(item, 'EXDATE')
        rrule = '\n'.join([it for it in [rrule, rdates, exdates] if it])

        # TODO: attendee-lists are not decoded properly and contain only
        # vCalAddress values
        attendees = item.get('ATTENDEE', ())

        contact = _get_prop('CONTACT', item)
        categories = item.get('CATEGORIES', ())
        if hasattr(categories, '__iter__'):
            categories = [safe_unicode(it) for it in categories]

        ext_modified = utc(_get_prop('LAST-MODIFIED', item))

        # TODO: better use plone.api for content creation, from which some of
        # the code here is copied

        content = None
        new_content_id = None
        existing_event = None
        sync_uid = _get_prop('UID', item)
        if sync_strategy != base.SYNC_NONE and sync_uid:
            existing_event = _get_by_sync_uid(sync_uid)
        if existing_event:
            if sync_strategy == base.SYNC_KEEP_MINE:
                # On conflict, keep mine
                continue

            exist_event = existing_event[0].getObject()
            acc = IEventAccessor(exist_event)

            if sync_strategy == base.SYNC_KEEP_NEWER and\
                    (not ext_modified or acc.last_modified > ext_modified):
                # Update only if modified date was passed in and it is not
                # older than the current modified date.  The client is not
                # expected to update the "last-modified" property, it is the
                # job of the server (calendar store) to keep it up to date.
                # This makes sure the client did the change on an up-to-date
                # version of the object.  See
                # http://tools.ietf.org/search/rfc5545#section-3.8.7.3
                continue

            # Else: update
            content = exist_event
        else:
            # TODO: if AT had the same attrs like IDXEventBase, we could set
            # everything within this invokeFactory call.
            new_content_id = str(random.randint(0, 99999999))
            container.invokeFactory(event_type,
                                    id=new_content_id,
                                    title=title,
                                    description=description)
            content = container[new_content_id]

        assert(content)  # At this point, a content must be available.

        event = IEventAccessor(content)
        event.title = title
        event.description = description
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
        if sync_strategy != base.SYNC_NONE:
            # Don't import the sync_uid, if no sync strategy is chosen. Let the
            # sync_uid be autogenerated then.
            event.sync_uid = sync_uid
        notify(ObjectModifiedEvent(content))

        # Archetypes specific code
        if getattr(content, 'processForm', False):
            # Will finish Archetypes content item creation process,
            # rename-after-creation and such
            content.processForm()

        # Use commits instead of savepoints to avoid "FileStorageError:
        # description too long" on large imports.
        transaction.get().commit()  # Commit before rename

        if new_content_id and new_content_id in container:
            # Rename with new id from title, if processForm didn't do it.
            chooser = INameChooser(container)
            new_id = chooser.chooseName(title, content)
            content.aq_parent.manage_renameObject(new_content_id, new_id)

        # Do this at the end, otherwise it's overwritten
        if ext_modified:
            event.last_modified = ext_modified

        count += 1

    return {'count': count}


class IIcalendarImportSettings(Interface):

    event_type = schema.Choice(
        title=_('ical_import_event_type_title', default=u'Event Type'),
        description=_(
            'ical_import_event_type_desc',
            default=u"Content type of the event, which is created when "
                    u"importing icalendar resources."),
        vocabulary='plone.app.event.EventTypes',
        required=True
    )

    ical_url = schema.URI(
        title=_('ical_import_url_title', default=u'Icalendar URL'),
        description=_(
            'ical_import_url_desc',
            default=u"URL to an external icalendar resource file."),
        required=False
    )

    ical_file = NamedFile(
        title=_('ical_import_file_title', default=u"Icalendar File"),
        description=_(
            'ical_import_file_desc',
            default=u"Icalendar resource file, if no URL is given."),
        required=False
    )

    sync_strategy = schema.Choice(
        title=_(
            'ical_import_sync_strategy_title',
            default=u"Synchronization Strategy"
        ),
        description=_(
            'ical_import_sync_strategy_desc',
            default=u"""Defines how to synchronize:
1) "Keep newer": Import, if the imported event is modified after the existing
   one.
2) "Keep mine": On conflicts, just do nothing.
3) "Keep theirs": On conflicts, update the existing event with the external
   one.
4) "No Syncing": Don't synchronize but import events and create new ones, even
    if they already exist. For each one, create a new sync_uid."""),
        vocabulary='plone.app.event.SynchronizationStrategies',
        required=True,
        default=base.SYNC_KEEP_NEWER
    )


class IcalendarImportSettings(AnnotationAdapter):
    """Annotation Adapter for IIcalendarImportSettings.
    """
    implements(IIcalendarImportSettings)
    adapts(Interface)
    #adapts(IFolder) ## ?? TODO: when adapting this in z3c.form, why is a
                     ## ATFolder not adaptable to this adapter, when it
                     ## implements IFolder?
    ANNOTATION_KEY = "icalendar_import_settings"


class IcalendarImportSettingsForm(form.Form):
    fields = field.Fields(IIcalendarImportSettings)
    ignoreContext = False

    #TODO: needed?
    def updateWidgets(self):
        super(IcalendarImportSettingsForm, self).updateWidgets()

    def getContent(self):
        data = {}
        settings = IIcalendarImportSettings(self.context)
        data['event_type'] = settings.event_type
        data['ical_url'] = settings.ical_url
        data['sync_strategy'] = settings.sync_strategy
        return data

    def save_data(self, data):
        settings = IIcalendarImportSettings(self.context)
        settings.ical_url = data['ical_url']
        settings.event_type = data['event_type']
        settings.sync_strategy = data['sync_strategy']

    @button.buttonAndHandler(u'Save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        self.save_data(data)

        IStatusMessage(self.request).addStatusMessage(
            _('msg_ical_import_settings_saved',
              default=u"Ical import settings saved."), 'info'
        )
        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(u'Save and Import')
    def handleSaveImport(self, action):
        data, errors = self.extractData()
        if errors:
            return False

        self.save_data(data)

        ical_file = data['ical_file']
        ical_url = data['ical_url']
        event_type = data['event_type']
        sync_strategy = data['sync_strategy']

        if ical_file or ical_url:

            if ical_file:
                # File upload is not saved in settings
                ical_resource = ical_file.data
                ical_import_from = ical_file.filename
            else:
                ical_resource = urllib2.urlopen(ical_url).read()
                ical_import_from = ical_url

            import_metadata = ical_import(
                self.context,
                ics_resource=ical_resource,
                event_type=event_type,
                sync_strategy=sync_strategy,
            )

            count = import_metadata['count']

            IStatusMessage(self.request).addStatusMessage(
                _('ical_import_imported',
                  default=u"${num} events imported from ${filename}",
                  mapping={'num': count, 'filename': ical_import_from}),
                'info')

        else:
            IStatusMessage(self.request).addStatusMessage(
                _('ical_import_no_ics',
                  default=u"Please provide either a icalendar ics file or a "
                          u"URL to a file."), 'error')

        self.request.response.redirect(self.context.absolute_url())

    @button.buttonAndHandler(u'Cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.context.absolute_url())


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
