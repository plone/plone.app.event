# -*- coding: utf-8 -*-
from ComputedAttribute import ComputedAttribute
from plone.app.layout.calendar import CalendarMixin
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import CatalogSource
from plone.portlets.interfaces import IPortletDataProvider
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from zope import schema
from zope.interface import implementer


try:
    from plone.app.contenttypes.behaviors.collection import ISyndicatableCollection as ICollection  # noqa
    from plone.app.contenttypes.interfaces import IFolder
    search_base_uid_source = CatalogSource(object_provides={
        'query': [
            ICollection.__identifier__,
            IFolder.__identifier__
        ],
        'operator': 'or'
    })
except ImportError:
    search_base_uid_source = CatalogSource(is_folderish=True)
    ICollection = None


class ICalendarPortlet(IPortletDataProvider):
    """A portlet displaying a calendar
    """

    state = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=None,
        required=False,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates")
    )

    search_base_uid = schema.Choice(
        title=_(u'portlet_label_search_base', default=u'Search base'),
        description=_(
            u'portlet_help_search_base',
            default=u'Select search base Folder or Collection to search for '
                    u'events. The URL to to this item will also be used to '
                    u'link to in calendar searches. If empty, the whole site '
                    u'will be searched and the event listing view will be '
                    u'called on the site root.'
        ),
        required=False,
        source=search_base_uid_source,
    )


@implementer(ICalendarPortlet)
class Assignment(base.Assignment):
    title = _(u'Calendar')

    # reduce upgrade pain
    state = None
    search_base = None

    def __init__(self, state=None, search_base_uid=None):
        self.state = state
        self.search_base_uid = search_base_uid

    def _uid(self):
        # This is only called if the instance doesn't have a search_base_uid
        # attribute, which is probably because it has an old
        # 'search_base' attribute that needs to be converted.
        path = self.search_base
        portal = getToolByName(self, 'portal_url').getPortalObject()
        try:
            search_base = portal.unrestrictedTraverse(path.lstrip('/'))
        except (AttributeError, KeyError, TypeError, NotFound):
            return
        return search_base.UID()
    search_base_uid = ComputedAttribute(_uid, 1)


class Renderer(CalendarMixin, base.Renderer):
    render = ViewPageTemplateFile('portlet_calendar.pt')

    def update(self):
        self.setup()


class AddForm(base.AddForm):
    schema = ICalendarPortlet
    label = _(u"Add Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")

    def create(self, data):
        return Assignment(state=data.get('state', None),
                          search_base_uid=data.get('search_base_uid', None))


class EditForm(base.EditForm):
    schema = ICalendarPortlet
    label = _(u"Edit Calendar Portlet")
    description = _(u"This portlet displays events in a calendar.")
