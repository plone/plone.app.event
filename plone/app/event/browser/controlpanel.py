from plone.app.event import messageFactory as _
from plone.app.event.base import localized_now
from plone.app.event.interfaces import IEventSettings
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope.publisher.browser import BrowserView


class EventControlPanelEditForm(RegistryEditForm):
    schema = IEventSettings
    schema_prefix = 'plone.app.event'

    label = _(u"label_event_settings", default=u"Event settings")
    description = _(
        u"help_event_settings",
        default=u"Event related settings like timezone, etc."
    )


class EventControlPanel(BrowserView):

    def __call__(self):
        view_factor = layout.wrap_form(EventControlPanelEditForm,
                                       ControlPanelFormWrapper)
        self.form = view_factor(self.context, self.request)
        self.form.update()
        return super(EventControlPanel, self).__call__()

    def current_datetime(self):
        """
        Returns the current set date time, based on the registry
        settings.
        """
        return localized_now()

    def update(self):
        """
        Delegate to the wrapped form in order to please KSS form
        validation.
        """
        if hasattr(self, 'form'):
            return self.form.update()
