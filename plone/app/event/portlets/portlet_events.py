#from datetime import datetime
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.event.interfaces import IEventAccessor
from plone.app.event.base import get_occurrences
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

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal = portal_state.portal()
        #self.navigation_root_url = portal_state.navigation_root_url()
        #self.navigation_root_object = getNavigationRootObject(self.context, self.portal)

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())

    def published_events(self):
        context = aq_inner(self.context)
        return [IEventAccessor(occ) for occ in\
                get_occurrences(context, self._data(), limit=self.data.count)]

    """
    @memoize
    def have_events_folder(self):
        return 'events' in self.navigation_root_object.objectIds()

    def all_events_link(self):
        navigation_root_url = self.navigation_root_url
        url = None
        if self.have_events_folder():
            url = '%s/events' % navigation_root_url
        else:
            # search all events which are in the future or ongoing
            now = datetime.utcnow().strftime('%Y-%m-%d+%H:%M')
            url = '%s/@@search?advanced_search=True'\
                  '&start.query:record:list:date=%s'\
                  '&start.range:record=min'\
                  '&end.query:record:list:date=%s'\
                  '&end.range:record=min'\
                  '&object_provides=plone.event.interfaces.IEvent'\
                   % (navigation_root_url, now, now)
        return url

    def prev_events_link(self):
        # take care dont use self.portal here since support
        # of INavigationRoot features likely will breake #9246 #9668
        url = None
        navigation_root_url = self.navigation_root_url
        events_folder = self.have_events_folder()\
                and self.navigation_root_object['events'] or None
        if (events_folder and
            'aggregator' in events_folder.objectIds() and
            'previous' in events_folder['aggregator'].objectIds()):
            url = '%s/events/aggregator/previous' % navigation_root_url
        elif (events_folder and 'previous' in events_folder.objectIds()):
            url = '%s/events/previous' % navigation_root_url
        else:
            # show all past events
            now = datetime.utcnow().strftime('%Y-%m-%d+%H:%M')
            url = '%s/@@search?advanced_search=True'\
                  '&end.query:record:list:date=%s'\
                  '&end.range:record=max'\
                  '&object_provides=plone.event.interfaces.IEvent'\
                   % (navigation_root_url, now)
        return url
    """

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
