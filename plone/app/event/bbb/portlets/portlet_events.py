from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.browser.z3cformhelper import AddForm
from plone.app.portlets.browser.z3cformhelper import EditForm
from plone.app.event.portlets.portlet_events import Renderer as RendererBase
from plone.app.event.portlets.portlet_events import Assignment
from plone.app.event.portlets.portlet_events import IEventsPortlet
from z3c.form import field


class Renderer(RendererBase):
    render = ViewPageTemplateFile('portlet_events.pt')


class AddForm(AddForm):
    fields = field.Fields(IEventsPortlet)
    label = _(u"Add Events Portlet")
    description = _(u"This portlet lists upcoming Events.")

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          state=data.get('state', None),
                          search_base_uid=data.get('search_base_uid', 5))


class EditForm(EditForm):
    fields = field.Fields(IEventsPortlet)
    label = _(u"Edit Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
