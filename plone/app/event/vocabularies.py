import pytz
from collective.elephantvocabulary import wrap_vocabulary
from zope.component import getUtility
from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.site.hooks import getSite
from Products.CMFCore.utils import getToolByName


replacement_zones = {
    'CET': 'Europe/Vienna',   # Central European Time
    'MET': 'Europe/Vienna',   # Middle European Time
    'EET': 'Europe/Helsinki', # East European Time
    'WET': 'Europe/Lisbon',   # West European Time
}

def Timezones(context):
    """ Vocabulary for all timezones.

    """
    rpl_keys = replacement_zones.keys()
    tz_list = [it for it in pytz.all_timezones if it not in rpl_keys]
    return SimpleVocabulary.fromValues(tz_list)

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
