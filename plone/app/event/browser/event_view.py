from AccessControl import getSecurityManager
from Acquisition import aq_parent
from Products.CMFCore import permissions
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.event import messageFactory as _
from plone.event.interfaces import IEventAccessor
from plone.event.interfaces import IOccurrence


def get_location(accessor):
    """Return the location.
    This method can be overwritten by external packages, for example to provide
    a reference to a Location object as done by collective.venue.

    :param accessor: Event, Occurrence or IEventAccessor object.
    :type accessor: IEvent, IOccurrence or IEventAccessor

    :returns: A location string. Possibly a HTML structure to link to another
              object, representing the location.
    :rtype: string
    """
    if not IEventAccessor.providedBy(accessor):
        accessor = IEventAccessor(accessor)
    return accessor.location


class EventView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.data = IEventAccessor(context)

    def __call__(self):
        if IOccurrence.providedBy(self.context):
            # If the context is a Occurrence, and the user has edit rights,
            # tell the user to go onle level up to be able to edit the event
            # via a IStatusMessage.
            # Actually, a HTML link would be better, but that's not supported
            # by the globalstatusmessage template at the moment
            # (https://github.com/plone/Products.CMFPlone/issues/206).
            event = aq_parent(self.context)
            sm = getSecurityManager()
            can_edit = sm.checkPermission(
                permissions.ModifyPortalContent, event)
            if can_edit:
                msg = _(
                    'part_of_recurring_event',
                    default=u'This event is part of a recurring Event. '
                            u'To edit the original event, go one level up.'
                )
                IStatusMessage(self.request).addStatusMessage(msg, 'info')
        return self.index()  # render me.
