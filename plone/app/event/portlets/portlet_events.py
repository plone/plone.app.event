# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from ComputedAttribute import ComputedAttribute
from plone.app.event import _
from plone.app.event.base import _prepare_range
from plone.app.event.base import expand_events
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.base import start_end_query
from plone.app.event.portlets import get_calendar_url
from plone.app.event.portlets.portlet_calendar import ICollection
from plone.app.event.portlets.portlet_calendar import search_base_uid_source
from plone.app.portlets.portlets import base
from plone.app.querystring import queryparser
from plone.app.uuid.utils import uuidToObject
from plone.memoize.compress import xhtml_compress
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zExceptions import NotFound
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.contentprovider.interfaces import IContentProvider
from zope.interface import implementer


class IEventsPortlet(IPortletDataProvider):

    count = schema.Int(
        title=_(u'Number of items to display'),
        description=_(u'How many items to list.'),
        required=True,
        default=5,
        min=1,
    )

    state = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=None,
        required=False,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates"
        )
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
    thumb_scale = schema.TextLine(
        title=_(u"Override thumb scale"),
        description=_(
            u"Enter a valid scale name"
            u" (see 'Image Handling' control panel) to override"
            u" (e.g. icon, tile, thumb, mini, preview, ... )."
            u" Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default=u'')

    no_thumbs = schema.Bool(
        title=_(u"Suppress thumbs"),
        description=_(
            u"If enabled, the portlet will not show thumbs."),
        required=True,
        default=False)


@implementer(IEventsPortlet)
class Assignment(base.Assignment):

    # reduce upgrade pain
    thumb_scale = None
    no_thumbs = False

    def __init__(self, count=5, state=None, search_base_uid=None,
                 thumb_scale=None, no_thumbs=False):
        self.count = count
        self.state = state
        self.search_base_uid = search_base_uid
        self.thumb_scale = thumb_scale
        self.no_thumbs = no_thumbs

    @property
    def title(self):
        return _(u"Events")

    def _uid(self):
        # This is only called if the instance doesn't have a search_base_uid
        # attribute, which is probably because it has an old
        # 'search_base' attribute that needs to be converted.
        path = self.search_base
        try:
            search_base = getSite().unrestrictedTraverse(path.lstrip('/'))
        except (AttributeError, KeyError, TypeError, NotFound):
            return
        return search_base.UID()
    search_base_uid = ComputedAttribute(_uid, 1)


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('portlet_events.pt')
    _search_base = None

    @property
    def search_base(self):
        if not self._search_base and self.data.search_base_uid:
            self._search_base = uuidToObject(self.data.search_base_uid)
        return aq_inner(self._search_base) if self._search_base else None

    @property
    def search_base_path(self):
        return '/'.join(self.search_base.getPhysicalPath()) if self.search_base else None  # noqa

    def update(self):
        context = aq_inner(self.context)
        calendar_url = get_calendar_url(context, self.search_base_path)
        self.next_url = '%s?mode=future' % calendar_url
        self.prev_url = '%s?mode=past' % calendar_url

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self.events)

    @property
    def events(self):
        context = aq_inner(self.context)
        data = self.data

        query = {}
        if data.state:
            query['review_state'] = data.state

        events = []
        query.update(self.request.get('contentFilter', {}))
        if ICollection and ICollection.providedBy(self.search_base):
            # Whatever sorting is defined, we're overriding it.
            query = queryparser.parseFormquery(
                self.search_base, self.search_base.query,
                sort_on='start', sort_order=None
            )

            start = None
            if 'start' in query:
                start = query['start']
            else:
                start = localized_now(context)

            end = None
            if 'end' in query:
                end = query['end']

            start, end = _prepare_range(self.search_base, start, end)
            query.update(start_end_query(start, end))
            events = self.search_base.results(
                batch=False, brains=True, custom_query=query,
                limit=data.count
            )
            events = expand_events(
                events, ret_mode=RET_MODE_ACCESSORS,
                start=start, end=end,
                sort='start', sort_reverse=False
            )
            events = events[:data.count]  # limit expanded
        else:
            if self.search_base_path:
                query['path'] = {'query': self.search_base_path}
            events = get_events(
                context, start=localized_now(context),
                ret_mode=RET_MODE_ACCESSORS,
                expand=True, limit=data.count, **query
            )

        return events

    def formatted_date(self, event):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(event)

    def thumb_scale(self):
        """Use override value or read thumb_scale from registry.
        Image sizes must fit to value in allowed image sizes.
        None will suppress thumb.
        """
        if getattr(self.data, 'no_thumbs', False):
            # Individual setting overrides ...
            return None
        thsize = getattr(self.data, 'thumb_scale', None)
        if thsize:
            return thsize
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)
        if settings.no_thumbs_portlet:
            return None
        thumb_scale_portlet = settings.thumb_scale_portlet
        return thumb_scale_portlet


class AddForm(base.AddForm):
    schema = IEventsPortlet
    label = _(u"Add Events Portlet")
    description = _(u"This portlet lists upcoming Events.")

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          state=data.get('state', None),
                          search_base_uid=data.get('search_base_uid', None))


class EditForm(base.EditForm):
    schema = IEventsPortlet
    label = _(u"Edit Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
