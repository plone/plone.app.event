from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.browser.z3cformhelper import AddForm
from plone.app.portlets.browser.z3cformhelper import EditForm
from plone.app.event.portlets.portlet_calendar import Renderer as RendererBase
from plone.app.event.portlets.portlet_calendar import ICalendarPortlet
from plone.app.event.portlets.portlet_calendar import Assignment
from z3c.form import field


class Renderer(RendererBase):
    render = ViewPageTemplateFile('portlet_calendar.pt')


class AddForm(AddForm):
    fields = field.Fields(ICalendarPortlet)
    label = _(u"Add Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")

    def create(self, data):
        return Assignment(state=data.get('state', None),
                          search_base_uid=data.get('search_base_uid', None))


class EditForm(EditForm):
    fields = field.Fields(ICalendarPortlet)
    label = _(u"Edit Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")
