from Products.CMFPlone.utils import safe_unicode
from plone.app.event import base
from plone.event.interfaces import IEventAccessor
from plone.event.utils import is_date, date_to_dateime
from zope.container.interfaces import INameChooser
import icalendar
import datetime
import random
import transaction

from Products.Archetypes.interfaces.base import IBaseObject

FACTORY_TYPE = 'plone.app.event.dx.event'
ICS_RESOURCE = open('/home/thet/Desktop/ical/derkalender_at_2013_v1d.ics', 'rb').read()


def ical_import(container, ics_resource=ICS_RESOURCE, event_type=FACTORY_TYPE):
    cal = icalendar.Calendar.from_ical(ics_resource)
    subs = cal.subcomponents

    def _get_prop(prop, sub, _as_unicode=True):
        ret = None
        if prop in sub:
            if _as_unicode:
                ret = safe_unicode(sub.decoded(prop))
            else:
                ret = sub.decoded(prop)
        return ret

    for sub in subs:
        start = _get_prop('DTSTART')
        end = _get_prop('DTEND')
        if not end:
            duration = _get_prop('DURATION')
            end = start + duration

        timezone = getattr(getattr(start, 'tzinfo', None), 'zone', None) or\
                base.default_timezone(container)

        whole_day = False
        if is_date(start) and is_date(end):
            # All day / whole day events
            # End must be same type as start (RFC5545, 3.8.2.2)
            whole_day = True
            if start<end:
                # RFC5545 doesn't define clearly, if all day events should have
                # a end date one day after the start day at 0:00.
                # Internally, we handle all day events with start=0:00,
                # end=:23:59:59, so we substract one day here.
                end = end-datetime.timedelta(days=1)
            start = base.dt_start_of_day(date_to_dateime(start))
            end = base.dt_end_of_day(date_to_dateime(end))

        title = _get_prop('SUMMARY', sub)
        description = _get_prop('DESCRIPTION', sub)

        # TODO: better use plone.api, from which some of the code here is
        # copied
        content_id = str(random.randint(0, 99999999))

        container.invokeFactory(event_type,
                                id=content_id,
                                title=title,
                                description=description,
                                start=start,
                                end=end,
                                timezone=timezone)
        content = container[content_id]

        event = IEventAccessor(content)
        event.whole_day = whole_day

        # Archetypes specific code
        if IBaseObject.providedBy(content):
            # Will finish Archetypes content item creation process,
            # rename-after-creation and such
            content.processForm()

        # Create a new id from title
        chooser = INameChooser(container)
        new_id = chooser.chooseName(title, content)
        transaction.savepoint(optimistic=True)
        content.aq_parent.manage_renameObject(content_id, new_id)

