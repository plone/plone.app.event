from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm

from plone.z3cform import layout

from plone.app.event import messageFactory as _
from plone.app.event.interfaces import IEventSettings


class EventControlPanelEditForm(RegistryEditForm):
    schema = IEventSettings
    schema_prefix = 'plone.app.event'

    label = _(u"label_event_settings", default=u"Event settings")
    description = _(u"help_event_settings",
            default=u"Event related settings like timezone, etc.")


EventControlPanel = layout.wrap_form(EventControlPanelEditForm,
                                     ControlPanelFormWrapper)
