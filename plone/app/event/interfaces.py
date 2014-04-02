from plone.app.event import messageFactory as _
from zope import schema
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


ISO_DATE_FORMAT = '%Y-%m-%d'


class IBrowserLayer(IDefaultBrowserLayer):
    """plone.app.event specific browser layer.
    """


class IICalendarImportEnabled(Interface):
    """Marker interface for contexts, where icalendar import is enabled.
    """

# BBB
from Products.CMFPlone.interfaces.controlpanel import IDateAndTimeSchema
IEventSettings = IDateAndTimeSchema
