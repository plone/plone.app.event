from Products.CMFCore.utils import getToolByName
from collective.elephantvocabulary import wrap_vocabulary
from plone.app.event import base
from plone.app.event import messageFactory as _
from plone.event.interfaces import IEvent
from plone.memoize import forever
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import pytz
import random


def Timezones(context, query=None):
    """Vocabulary for all timezones.
    """
    rpl_keys = base.replacement_zones.keys()
    tz_list = [SimpleTerm(value=it, title=it)
               for it in pytz.all_timezones if it not in rpl_keys and (
                   query is None
                   or query.lower() in it.lower())]
    return SimpleVocabulary(tz_list)
directlyProvides(Timezones, IVocabularyFactory)


def AvailableTimezones(context, query=None):
    """Vocabulary for available timezones, as set by in the controlpanel.

    This vocabulary is based on collective.elephantvocabulary. The reason is,
    that if timezones are used in events or in user's settings and later
    retracted by the portal manager, they should still be usable for those
    objects but not selectable in forms.

    Note: after setting available_timezones, this vocabulary must be
    reinstantiated to reflect the changes.
    """
    # TODO: if the portal_timezone is not in available_timezones, also put it
    #       in AvailableTimezone vocab.
    tzvocab = getUtility(IVocabularyFactory,
                         'plone.app.event.Timezones')(context, query)
    return wrap_vocabulary(
        tzvocab,
        visible_terms_from_registry='plone.app.event.available_timezones'
    )(context)
directlyProvides(AvailableTimezones, IVocabularyFactory)


def Weekdays(context):
    """Vocabulary for Weekdays.

    PLEASE NOTE: strftime %w interprets 0 as Sunday unlike the calendar module!

        Note: Context is here a RecordProxy and cannot be used to get the site
              root. zope.i18n.translate seems not to respect the portal
              language.
    """

    # TODO: revisit, use zope.i18n
    # see: http://weblion.psu.edu/chatlogs/%23plone/2012/08/15.txt
    # avoid using:
    # translate = getSite().translate
    # it breaks tests. it's defined in:
    # Products.CMFPlone.skins.plone_scripts.translate.py
    # better use:
    # from zope.i18n import translate
    translate = getToolByName(getSite(), 'translation_service').translate

    domain = 'plonelocales'
    items = [
        (translate(u'weekday_mon', domain=domain, default=u'Monday'), 0),
        (translate(u'weekday_tue', domain=domain, default=u'Tuesday'), 1),
        (translate(u'weekday_wed', domain=domain, default=u'Wednesday'), 2),
        (translate(u'weekday_thu', domain=domain, default=u'Thursday'), 3),
        (translate(u'weekday_fri', domain=domain, default=u'Friday'), 4),
        (translate(u'weekday_sat', domain=domain, default=u'Saturday'), 5),
        (translate(u'weekday_sun', domain=domain, default=u'Sunday'), 6),
    ]

    items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
    return SimpleVocabulary(items)
directlyProvides(Weekdays, IVocabularyFactory)


@forever.memoize
def EventTypes(context):
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
directlyProvides(EventTypes, IVocabularyFactory)


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
directlyProvides(SynchronizationStrategies, IVocabularyFactory)
