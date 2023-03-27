from plone.app.event.dx.behaviors import IEventAttendees
from plone.app.event.dx.behaviors import IEventContact
from plone.app.event.dx.behaviors import IEventLocation
from plone.app.event.dx.interfaces import IDXEvent
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import logging


log = logging.getLogger(__name__)

BEHAVIOR_LIST = [
    IEventAttendees,
    IEventContact,
    IEventLocation,
]


def enable_richtext_behavior(self):
    fti = queryUtility(IDexterityFTI, name="Event", default=None)
    if not fti:
        return
    behaviors = [
        it
        for it in fti.behaviors
        if "plone.app.event.dx.behaviors.IEventSummary" not in it
    ]
    behaviors.extend(
        [
            "plone.app.contenttypes.behaviors.richtext.IRichText",
        ]
    )
    behaviors = tuple(set(behaviors))
    fti._updateProperty("behaviors", behaviors)


def upgrade_attribute_storage(context):
    portal = getSite()
    catalog = getToolByName(portal, "portal_catalog")
    query = {}
    query["object_provides"] = IDXEvent.__identifier__
    results = catalog(**query)
    log.info(f"There are {len(results)} in total, stating migration...")
    for result in results:
        try:
            event = result.getObject()
        except Exception:
            log.warning(
                "Not possible to fetch event object from catalog result for "
                "item: {}.".format(result.getPath())
            )
            continue
        if not IAnnotatable.providedBy(event):
            log.warning(
                "The event at {} does provide annotation capabilities, "
                "skipping.".format(event.absolute_url())
            )
            continue
        annotations = IAnnotations(event)
        did_work = False
        for behavior in BEHAVIOR_LIST:
            for name in behavior.names():
                fullname = f"{behavior.__identifier__}.{name}"
                oldvalue = annotations.get(fullname, None)
                # Only write the old value if there is no new value yet
                if oldvalue and not getattr(event, name, None):
                    setattr(event, name, oldvalue)
                    did_work = True
        # The old IEventSummary behavior is gone, just look for the old name
        # inside the annotation storage
        oldvalue = annotations.get(
            "plone.app.event.dx.behaviors.IEventSummary.text", None
        )
        if oldvalue and not getattr(event, "text", None):
            setattr(event, "text", oldvalue)
            did_work = True
        if did_work:
            notify(ObjectModifiedEvent(event))
        log.debug(f"Handled event at {event.absolute_url()}")


def remove_event_listing_settings(context):
    portal = getSite()
    actions = getToolByName(portal, "portal_actions")
    ob = getattr(actions, "object")
    if ob and getattr(ob, "event_listing_settings", False):
        actions.object.manage_delObjects(
            [
                "event_listing_settings",
            ]
        )
        log.debug("Removed event_listing_settings from object actions.")
