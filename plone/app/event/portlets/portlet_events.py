from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.contentprovider.interfaces import IContentProvider
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.event.base import get_occurrences_from_brains
from plone.app.event.base import get_portal_events
from plone.app.event.base import localized_now
from plone.app.event.interfaces import ICalendarLinkbase

from plone.app.portlets import PloneMessageFactory as _


class IEventsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
        description=_(u'How many items to list.'),
        required=True,
        default=5)

    state = schema.Tuple(title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=None,
        required=False,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates")
        )

    search_base = schema.Choice(
        title=_(u'portlet_label_search_base', default=u'Search base'),
        description=_(u'portlet_help_search_base',
                      default=u'Select events search base folder'),
        required=False,
        source=SearchableTextSourceBinder({'is_folderish': True},
                                           default_query='path:'),
    )


class Assignment(base.Assignment):
    implements(IEventsPortlet)

    # reduce upgrade pain
    search_base = None

    def __init__(self, count=5, state=None, search_base=None):
        self.count = count
        self.state = state
        self.search_base = search_base

    @property
    def title(self):
        return _(u"Events")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('portlet_events.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        self.calendar_linkbase = ICalendarLinkbase(self.context)
        #BBB
        self.prev_events_link = self.calendar_linkbase.past_events_url
        self.all_events_link = self.calendar_linkbase.next_events_url

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())

    def published_events(self):
        context = aq_inner(self.context)
        return get_occurrences_from_brains(context, self._data(),
                range_start=localized_now(), limit=self.data.count)

    def formated_date(self, event):
        provider = getMultiAdapter((self.context, self.request, self),
                IContentProvider, name=u"formated_date")
        return provider(event)

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        data = self.data

        query_kw = {}
        if data.search_base:
            query_kw['path'] = {'query': '%s%s' % (
                '/'.join(self.portal.getPhysicalPath()), data.search_base)}

        if data.state:
            query_kw['review_state'] = data.state

        ret = get_portal_events(
                context,
                range_start=localized_now(context),
                limit=data.count,
                **query_kw)

        return ret

class AddForm(base.AddForm):
    form_fields = form.Fields(IEventsPortlet)
    label = _(u"Add Events Portlet")
    description = _(u"This portlet lists upcoming Events.")

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          state=data.get('state', None),
                          search_base=data.get('search_base', 5))

class EditForm(base.EditForm):
    form_fields = form.Fields(IEventsPortlet)
    label = _(u"Edit Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
