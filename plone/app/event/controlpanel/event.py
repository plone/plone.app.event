from zope import schema
from zope.interface import Interface
from plone.app.registry.browser import controlpanel
from plone.app.event import messageFactory as _


class IEventSettings(Interface):
    """ Global settings for eventish content types.
    """

    portal_timezone = schema.Choice(
            title=_(u"Portal default timezone"),
            description=_(u"help_portal_timezone",
                default=u"The timezone setting of the portal. Users can set "
                         "their own timezone, if available timezones are defined."),
            required=True,
            default=u"",
            vocabulary="TimezoneVocabulary"
            )

    available_timezones = schema.List(
            title=_(u"Available timezones"),
            description=_(u"help_available_timezones",
                default=u"The timezones, which should be available for the portal. "
                         "Can be set for users and events"),
            required=False,
            default=None,
            value_type=schema.Choice(
                vocabulary="TimezoneVocabulary"
                )
            )


class EventSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IEventSettings
    label = _(u"Event settings")
    description = _(u"help_event_settings",
            default=u"Event related settings like timezone, etc.")

    def updateFields(self):
        super(EventSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(EventSettingsEditForm, self).updateWidgets()

class EventSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = EventSettingsEditForm
