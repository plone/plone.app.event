import pytz
from collective.elephantvocabulary import wrap_vocabulary
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite


def Timezones(context):
    """ Vocabulary for all timezones.

    """
    return SimpleVocabulary.fromValues(pytz.all_timezones)

directlyProvides(Timezones, IVocabularyFactory)


def AvailableTimezones(context):
    """ Vocabulary for available timezones, as set by in the controlpanel.

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
                         'plone.app.event.Timezones')(context)
    return wrap_vocabulary(
        tzvocab,
        visible_terms_from_registry='plone.app.event.available_timezones'
    )(context)

directlyProvides(AvailableTimezones, IVocabularyFactory)


def Weekdays(context):
    """ Vocabulary for Weekdays.

        Note: Context is here a RecordProxy and cannot be used to get the site
              root. zope.i18n.translate seems not to respect the portal
              language.

    """
    translate = getSite().translate

    domain = 'plonelocales'
    items =[(translate(u'weekday_mon', domain=domain, default=u'Monday'),0),
            (translate(u'weekday_tue', domain=domain, default=u'Tuesday'),1),
            (translate(u'weekday_wed', domain=domain, default=u'Wednesday'),2),
            (translate(u'weekday_thu', domain=domain, default=u'Thursday'),3),
            (translate(u'weekday_fri', domain=domain, default=u'Friday'),4),
            (translate(u'weekday_sat', domain=domain, default=u'Saturday'),5),
            (translate(u'weekday_sun', domain=domain, default=u'Sunday'),6),
           ]

    items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
    return SimpleVocabulary(items)

directlyProvides(Weekdays, IVocabularyFactory)
