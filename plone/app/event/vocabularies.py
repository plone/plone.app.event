from Products.CMFCore.utils import getToolByName
from plone.app.event import base
from plone.app.event import messageFactory as _
from plone.event.interfaces import IEvent
from plone.memoize import forever
from zope.component.hooks import getSite
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import random


@provider(IVocabularyFactory)
@forever.memoize
def EventTypes(context):
    # TODO: refactor for DX
    """Vocabulary for available event types.

    Insane stuff: All types are created temporary and checked if the provide
    the IEvent interface. At least, this function is cached forever the Zope
    process lives.
    """
    # TODO: I'd love to query the factory for types, who's instances are
    # implementing a specific interface via the portal_factory API.

    portal = getSite()
    tmp_folder_id = 'event_types_temp_folder__%s' % random.randint(0, 99999999)
    portal.invokeFactory('Folder', tmp_folder_id)
    try:
        tmp_folder = portal._getOb(tmp_folder_id)
        portal_types = getToolByName(portal, 'portal_types')
        all_types = portal_types.listTypeInfo(portal)
        event_types = []
        cnt = 0
        for fti in all_types:
            if not getattr(fti, 'global_allow', False):
                continue
            cnt += 1
            tmp_id = 'temporary__event_types__%s' % cnt
            tmp_obj = None
            fti.constructInstance(tmp_folder, tmp_id)
            tmp_obj = tmp_folder._getOb(tmp_id)
            if tmp_obj:
                if IEvent.providedBy(tmp_obj):
                    event_types.append(fti.id)
    finally:
        # Delete the tmp_folder again
        tmp_folder.__parent__.manage_delObjects([tmp_folder_id])

    return SimpleVocabulary.fromValues(event_types)


@provider(IVocabularyFactory)
def SynchronizationStrategies(context):
    """Vocabulary for icalendar synchronization strategies.

    SYNC_KEEP_NEWER:  Import, if the imported event is modified after the
                      existing one.
    SYNC_KEEP_MINE:   On conflicts, just do nothing.
    SYNC_KEEP_THEIRS: On conflicts, update the existing event with the external
                      one.
    SYNC_NONE:        Don't synchronize but import events and create new ones,
                      even if they already exist. For each one, create a new
                      sync_uid.
    """
    items = [
        (_('sync_keep_newer', default="Keep newer"), base.SYNC_KEEP_NEWER),
        (_('sync_keep_mine', default="Keep mine"), base.SYNC_KEEP_MINE),
        (_('sync_keep_theirs', default="Keep theirs"), base.SYNC_KEEP_THEIRS),
        (_('sync_none', default="No Syncing"), base.SYNC_NONE),
    ]
    items = [SimpleTerm(title=i[0], value=i[1]) for i in items]
    return SimpleVocabulary(items)
