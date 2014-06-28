# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.event.dx.interfaces import IDXEvent
from plone.app.event.dx.behaviors import IEventAttendees
from plone.app.event.dx.behaviors import IEventContact
from plone.app.event.dx.behaviors import IEventLocation
from plone.dexterity.interfaces import IDexterityFTI
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.component import queryUtility
from zope.component.hooks import getSite
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
    behaviors = [it for it in fti.behaviors
                 if 'plone.app.event.dx.behaviors.IEventSummary' not in it]
    behaviors.extend([
        'plone.app.contenttypes.behaviors.richtext.IRichText',
    ])
    behaviors = tuple(set(behaviors))
    fti._updateProperty('behaviors', behaviors)


def upgrade_attribute_storage(context):
    portal = getSite()
    catalog = getToolByName(portal, 'portal_catalog')
    query = {}
    query['object_provides'] = IDXEvent.__identifier__
    results = catalog(**query)
    log.info('There are {0} in total, stating migration...'.format(
        len(results)))
    for result in results:
        try:
            event = result.getObject()
        except:
            log.warning(
                'Not possible to fetch event object from catalog result for '
                'item: {0}.'.format(result.getPath()))
            continue
        if not IAnnotatable.providedBy(event):
            log.warning(
                'The event at {0} does provide annotation capabilities, '
                'skipping.'.format(event.absolute_url()))
            continue
        annotations = IAnnotations(event)
        did_work = False
        for behavior in BEHAVIOR_LIST:
            for name in behavior.names():
                fullname = '{0}.{1}'.format(behavior.__identifier__, name)
                oldvalue = annotations.get(fullname, None)
                # Only write the old value if there is no new value yet
                if oldvalue and not getattr(event, name, None):
                    setattr(event, name, oldvalue)
                    did_work = True
        # The old IEventSummary behavior is gone, just look for the old name
        # inside the annotation storage
        oldvalue = annotations.get(
            'plone.app.event.dx.behaviors.IEventSummary.text', None)
        if oldvalue and not getattr(event, 'text', None):
            setattr(event, 'text', oldvalue)
            did_work = True
        if did_work:
            notify(ObjectModifiedEvent(event))
        log.debug('Handled event at {0}'.format(event.absolute_url()))


def upgrade_defaults_wholeday_openend(context):
    portal = getSite()
    catalog = getToolByName(portal, 'portal_catalog')
    query = {}
    query['object_provides'] = IDXEvent.__identifier__
    results = catalog(**query)
    log.info('There are {0} in total, stating migration...'.format(
        len(results)))
    for result in results:
        changed = False
        try:
            event = result.getObject()
        except:
            log.warning(
                'Not possible to fetch event object from catalog result for '
                'item: {0}.'.format(result.getPath()))
            continue

        if not hasattr(event, 'whole_day'):
            event.whole_day = False
            log.info('set whole_day = false for event at {0}'.format(
                event.absolute_url()))
            changed = True
        if not hasattr(event, 'open_end'):
            event.open_end = False
            log.info('Set open_end = False for event at {0}'.format(
                event.absolute_url()))
            changed = True

        if changed:
            notify(ObjectModifiedEvent(event))
