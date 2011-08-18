
from plone.app.registry.browser import controlpanel

from plone.app.event import messageFactory as _
from plone.app.event.interfaces import IEventSettings


class EventControlPanelEditForm(controlpanel.RegistryEditForm):
    """
    """

    schema = IEventSettings
    schema_prefix = 'plone.app.event'

    label = _(u"Event settings")
    description = _(u"help_event_settings",
            default=u"Event related settings like timezone, etc.")

    def updateFields(self):
        super(EventControlPanelEditForm, self).updateFields()

    def updateWidgets(self):
        super(EventControlPanelEditForm, self).updateWidgets()


class EventSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    """

    form = EventControlPanelEditForm
