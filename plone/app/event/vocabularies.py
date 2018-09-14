# -*- coding: utf-8 -*-
from plone.app.event import _
from plone.app.event import base
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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
