from cStringIO import StringIO
from zope.interface import implements

from DateTime import DateTime
from App.class_init import InitializeClass

from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.interfaces import ICalendarSupport

class CalendarSupportMixin:
    """Mixin class for iCal/vCal support
    """

    implements(ICalendarSupport)

    security       = ClassSecurityInfo()

    actions = ({
        'id'          : 'ics',
        'name'        : 'iCalendar',
        'action'      : 'string:${object_url}/ics_view',
        'permissions' : (View, ),
        'category'    : 'document_actions',
         },
         {
        'id'          : 'vcs',
        'name'        : 'vCalendar',
        'action'      : 'string:${object_url}/vcs_view',
        'permissions' : (View, ),
        'category'    : 'document_actions',
         },
    )

    _at_action_icons = ({
        'category'  : 'plone',
        'action_id' : 'ics',
        'icon_expr' : 'ical_icon.gif',
        'title'     : 'iCalendar export',
        'priority'  : 0,
        },
        {
        'category'  : 'plone',
        'action_id' : 'vcs',
        'icon_expr' : 'vcal_icon.gif',
        'title'     : 'vCalendar export',
        'priority'  : 0,
        },
        )

    security.declareProtected(View, 'getICal')

    security.declareProtected(View, 'ics_view')
    def ics_view(self, REQUEST, RESPONSE):
        """iCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/calendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.ics"' % self.getId())
        out = StringIO()
        out.write(ICS_HEADER % { 'prodid' : PRODID, })
        out.write(self.getICal())
        out.write(ICS_FOOTER)
        return n2rn(out.getvalue())

    security.declareProtected(View, 'getVCal')
    def getVCal(self):
        """get vCal data
        """
        out = StringIO()
        map = {
            'dtstamp'   : rfc2445dt(DateTime()),
            'created'   : rfc2445dt(DateTime(self.CreationDate())),
            'uid'       : self.UID(),
            'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
            'summary'   : vformat(self.Title()),
            'startdate' : rfc2445dt(self.start()),
            'enddate'   : rfc2445dt(self.end()),
            }
        out.write(VCS_EVENT_START % map)
        description = self.Description()
        if description:
            out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
        location = self.getLocation()
        if location:
            out.write('LOCATION:%s\n' % vformat(location))
        out.write(VCS_EVENT_END)
        # TODO
        # Insert missing code here :]
        return out.getvalue()

    security.declareProtected(View, 'vcs_view')
    def vcs_view(self, REQUEST, RESPONSE):
        """vCalendar output
        """
        RESPONSE.setHeader('Content-Type', 'text/x-vCalendar')
        RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s.vcs"' % self.getId())
        out = StringIO()
        out.write(VCS_HEADER % { 'prodid' : PRODID, })
        out.write(self.getVCal())
        out.write(VCS_FOOTER)
        return n2rn(out.getvalue())

InitializeClass(CalendarSupportMixin)

def vformat(s):
    # return string with escaped commas, colons and semicolons
    return s.strip().replace(',','\,').replace(':','\:').replace(';','\;')


def foldLine(s):
    # returns string folded per RFC2445 (each line must be less than 75 octets)
    # This code is a minor modification of MakeICS.py, available at:
    # http://www.zope.org/Members/Feneric/MakeICS/
    
    lineLen = 70
    
    workStr = s.strip().replace('\r\n','\n').replace('\r','\n').replace('\n','\\n')
    numLinesToBeProcessed = len(workStr)/lineLen
    startingChar = 0
    res = ''
    while numLinesToBeProcessed >= 1:
        res = '%s%s\n '%(res, workStr[startingChar:startingChar+lineLen])
        startingChar += lineLen
        numLinesToBeProcessed -= 1
    return '%s%s\n' % (res, workStr[startingChar:])

