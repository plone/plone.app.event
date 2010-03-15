
from cStringIO import StringIO

from Products.Five import BrowserView

class iCalendarView(BrowserView):
    
    def __call__(self):
        response = self.request.response
        response.setHeader('Content-Type', 'text/calendar')
        response.setHeader('Content-Disposition', 'attachment; filename="%s.ics"'
                % self.context.getId())
        out = StringIO()
        out.write(ICS_HEADER % { 'prodid' : PRODID, })
        out.write(self.getICal())
        out.write(ICS_FOOTER)
        return n2rn(out.getvalue())

class vCalendarView(BrowserView):

    def __call_(self):
        pass
