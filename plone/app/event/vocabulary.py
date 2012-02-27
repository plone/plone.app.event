import pytz

from zope.interface import directlyProvides
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.site.hooks import getSite
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

def Weekdays(context):
    """ Vocabulary for Weekdays.
    """

    translate = getSite().translate

    items =[(translate(u'weekday_mon', domain='plonelocales', default=u'Monday'),0),
            (translate(u'weekday_tue', domain='plonelocales', default=u'Tuesday'),1),
            (translate(u'weekday_wed', domain='plonelocales', default=u'Wednesday'),2),
            (translate(u'weekday_thu', domain='plonelocales', default=u'Thursday'),3),
            (translate(u'weekday_fri', domain='plonelocales', default=u'Friday'),4),
            (translate(u'weekday_sat', domain='plonelocales', default=u'Saturday'),5),
            (translate(u'weekday_sun', domain='plonelocales', default=u'Sunday'),6),
           ]

    items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
    return SimpleVocabulary(items)

directlyProvides(Timezones, IVocabularyFactory)
directlyProvides(AvailableTimezones, IVocabularyFactory)
directlyProvides(Weekdays, IVocabularyFactory)
