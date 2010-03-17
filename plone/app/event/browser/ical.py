from cStringIO import StringIO

from zope.publisher.browser import BrowserView
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from DateTime import DateTime

from plone.memoize import ram
from Products.CMFCore.utils import getToolByName

from plone.app.event.constants import (
    PRODID, ICS_HEADER, ICS_FOOTER, ICS_EVENT_START, ICS_EVENT_END)
from plone.app.event.interfaces import ICalendarSupport
from plone.app.event.utils import n2rn, rfc2445dt, vformat, foldline
from plone.app.event import event_util 

def cachekey(fun, self):
    """ generate a cache key based on the following data:
          * context URL
          * fingerprint of the brains found in the query
        the returned key is suitable for usage with `memoize.ram.cache` """
    context = self.context
    def add(brain):
        path = brain.getPath().decode('ascii', 'replace').encode('utf-8')
        return '%s\n%s\n\n' % (path, brain.modified)
    url = context.absolute_url()
    title = context.Title()
    fingerprint = ''.join(map(add, self.events))
    return ''.join((url, title, fingerprint))


class EventsICal(BrowserView):
    """ view for event data into an `.ics` feed """

    def update(self):
        context = aq_inner(self.context)
        path = '/'.join(context.getPhysicalPath())
        provides = ICalendarSupport.__identifier__
        self.events = context.queryCatalog(REQUEST={'path':path, 'object_provides':provides})

    def render(self):
        self.update()       # collect events
        context = self.context
        request = self.request
        name = '%s.ics' % context.getId()
        request.RESPONSE.setHeader('Content-Type', 'text/calendar')
        request.RESPONSE.setHeader('Content-Disposition',
                                   'attachment; filename="%s"' % name)
        request.RESPONSE.write(self.feeddata())

    @ram.cache(cachekey)
    def feeddata(self):
        context = self.context
        data = ICS_HEADER % dict(prodid=PRODID)
        data += 'X-WR-CALNAME:%s\n' % context.Title()
        data += 'X-WR-CALDESC:%s\n' % context.Description()
        for brain in self.events:
            data += getMultiAdapter((brain.getObject(), self.request),
                                     name=u'ics_view').getICal()
        data += ICS_FOOTER
        return data

    def getICal(self):
        """get iCal data
        """

        start_str, end_str = event_util.dateStringsForEvent(self.context)
        out = StringIO()
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(self.context.CreationDate())),
            'uid'       : self.context.UID(),
            'modified'  : rfc2445dt(DateTime(self.context.ModificationDate())),
            'summary'   : vformat(self.context.Title()),
            'startdate' : start_str,
            'enddate'   : end_str,
            }
        out.write(ICS_EVENT_START % map)

        description = self.context.Description()
        if description:
            out.write(foldline('DESCRIPTION:%s\n' % vformat(description)))

        location = self.context.getLocation()
        if location:
            out.write('LOCATION:%s\n' % vformat(location))

        subject = self.context.Subject()
        if subject:
            out.write('CATEGORIES:%s\n' % ','.join(subject))

        # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
        #ORGANIZER;CN=%(name):MAILTO=%(email)
        #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)

        cn = []
        contact = self.context.contact_name()
        if contact:
            cn.append(contact)
        phone = self.context.contact_phone()
        if phone:
            cn.append(phone)
        email = self.context.contact_email()
        if email:
            cn.append(email)
        if cn:
            out.write('CONTACT:%s\n' % vformat(', '.join(cn)))

        url = self.context.event_url()
        if url:
            out.write('URL:%s\n' % url)

        # allow derived event types to inject additional data for iCal
        try:
            self.context.getICalSupplementary(out)
        except AttributeError:
            pass

        out.write(ICS_EVENT_END)
        return out.getvalue()

    __call__ = render
