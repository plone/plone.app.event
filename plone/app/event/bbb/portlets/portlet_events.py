from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from distutils.version import LooseVersion
from plone.app.event.portlets.portlet_events import Assignment
from plone.app.event.portlets.portlet_events import IEventsPortlet
from plone.app.event.portlets.portlet_events import Renderer as RendererBase
from plone.app.portlets import PloneMessageFactory as _
import pkg_resources


version = LooseVersion(pkg_resources.require("plone.app.portlets")[0].version)
wanted = LooseVersion('3.0')


if version >= wanted:
    P_A_PORTLETS_PRE_3 = False
    from plone.app.portlets.portlets import base
else:
    P_A_PORTLETS_PRE_3 = True
    from z3c.form import field
    from plone.app.portlets.browser import z3cformhelper as base


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
