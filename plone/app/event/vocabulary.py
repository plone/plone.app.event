import pytz

from zope.interface import directlyProvides
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from collective.elephantvocabulary import wrap_vocabulary


def Timezones(context):
    """ Vocabulary for all timezones.

    TODO: make timezone source adaptable to provide vocab with commont_timezones
          or all_timezones
    """
    return SimpleVocabulary.fromValues(pytz.all_timezones)


def AvailableTimezones(context):
    """ Vocabulary for available timezones, as set by in the controlpanel.

    This vocabulary is based on collective.elephantvocabulary. The reason is,
    that if timezones are used in events or in user's settings and later
    retracted by the portal manager, they should still be usable for those
    objects but not selectable in forms.

    Note: after setting available_timezones, this vocabulary must be
    reinstantiated to reflect the changes.

    # TODO: if the portal_timezone is not in available_timezones, also put it
    # in AvailableTimezone vocab.

    """
    tzvocab = getUtility(IVocabularyFactory, 'plone.app.event.Timezones')(context)
    return wrap_vocabulary(
            tzvocab,
            visible_terms_from_registry='plone.app.event.available_timezones'
        )(context)


directlyProvides(Timezones, IVocabularyFactory)
directlyProvides(AvailableTimezones, IVocabularyFactory)
