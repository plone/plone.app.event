from distutils.version import StrictVersion
import pkg_resources

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets import PloneMessageFactory as _

from plone.app.portlets.portlets import base
from plone.app.event.portlets.portlet_events import Renderer as RendererBase
from plone.app.event.portlets.portlet_events import Assignment
from plone.app.event.portlets.portlet_events import IEventsPortlet


version = StrictVersion(pkg_resources.require("plone.app.portlets")[0].version)
wanted = StrictVersion('3.0')

if version >= wanted:
    P_A_PORTLETS_PRE_3 = False
    from z3c.form import field
else:
    P_A_PORTLETS_PRE_3 = True
    from plone.app.portlets.browser import z3cformhelper


class Renderer(RendererBase):
    render = ViewPageTemplateFile('portlet_events.pt')


class AddForm(base.AddForm):
    if P_A_PORTLETS_PRE_3:
        fields = field.Fields(IEventsPortlet)
    else:
        schema = IEventsPortlet
    label = _(u"Add Events Portlet")
    description = _(u"This portlet lists upcoming Events.")

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          state=data.get('state', None),
                          search_base_uid=data.get('search_base_uid', 5))


class EditForm(base.EditForm):
    if P_A_PORTLETS_PRE_3:
        fields = field.Fields(IEventsPortlet)
    else:
        schema = IEventsPortlet
    label = _(u"Edit Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
