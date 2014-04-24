from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.event.base import RET_MODE_ACCESSORS
from plone.app.event.base import get_events
from plone.app.event.base import localized_now
from plone.app.event.browser.event_view import get_location
from plone.app.event.portlets import get_calendar_url
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.contentprovider.interfaces import IContentProvider
from zope.formlib import form
from zope.interface import implements


class IEventsPortlet(IPortletDataProvider):

    count = schema.Int(
        title=_(u'Number of items to display'),
        description=_(u'How many items to list.'),
        required=True,
        default=5
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

    search_base = schema.Choice(
        title=_(u'portlet_label_search_base', default=u'Search base'),
        description=_(
            u'portlet_help_search_base',
            default=u'Select search base folder to search for events. This '
                    u'folder will also be used to link to in calendar '
                    u'searches. If empty, the whole site will be searched and '
                    u'the event listing view will be called on the site root.'
        ),
        required=False,
        source=SearchableTextSourceBinder(
            {'is_folderish': True},
            default_query='path:'
        ),
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

        context = aq_inner(self.context)

        calendar_url = get_calendar_url(context, self.data.search_base)
        self.next_url = '%s?mode=future' % calendar_url
        self.prev_url = '%s?mode=past' % calendar_url

        portal_state = getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )
        self.portal = portal_state.portal()

    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self.events)

    @property
    @memoize
    def events(self):
        context = aq_inner(self.context)
        data = self.data

        kw = {}
        if data.search_base:
            kw['path'] = {'query': '%s%s' % (
                '/'.join(self.portal.getPhysicalPath()), data.search_base)}
        if data.state:
            kw['review_state'] = data.state

        return get_events(context, start=localized_now(context),
                          ret_mode=RET_MODE_ACCESSORS,
                          expand=True, limit=data.count, **kw)

    def formatted_date(self, event):
        provider = getMultiAdapter(
            (self.context, self.request, self),
            IContentProvider, name='formatted_date'
        )
        return provider(event)

    def get_location(self, event):
        return get_location(event)


class AddForm(base.AddForm):
    form_fields = form.Fields(IEventsPortlet)
    label = _(u"Add Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
    form_fields = form.Fields(IEventsPortlet)
    form_fields['search_base'].custom_widget = UberSelectionWidget

    def create(self, data):
        return Assignment(count=data.get('count', 5),
                          state=data.get('state', None),
                          search_base=data.get('search_base', 5))


class EditForm(base.EditForm):
    form_fields = form.Fields(IEventsPortlet)
    label = _(u"Edit Events Portlet")
    description = _(u"This portlet lists upcoming Events.")
    form_fields = form.Fields(IEventsPortlet)
    form_fields['search_base'].custom_widget = UberSelectionWidget
