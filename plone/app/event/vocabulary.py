import pytz

from zope.interface import directlyProvides
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from collective.elephantvocabulary import wrap_vocabulary


def Timezones(context):
    """ Vocabulary for all timezones.
    >>> import zope.component
    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> tzvocab = zope.component.getUtility(IVocabularyFactory, 'plone.app.event.Timezones')

    TODO: find something more breakage proof than following test
    >>> assert('Africa/Abidjan' == list(tzvocab(None))[0].value)

    TODO: make timezone source adaptable to provide vocab with commont_timezones
          or all_timezones
    """
    return SimpleVocabulary.fromValues(pytz.all_timezones)


def AvailableTimezones(context):
    """ Vocabulary for available timezones, as set by in the controlpanel.

    >>> from zope.component import getUtility
    >>> from plone.registry.interfaces import IRegistry
    >>> from plone.app.event.controlpanel.event import IEventSettings
    >>> reg = getUtility(IRegistry)
    >>> settings = reg.forInterface(IEventSettings)

    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> tzvocab = getUtility(IVocabularyFactory,
    ...     'AvailableTimezonesVocabulary')
    >>> list(tzvocab(None))
    []

    >>> allzones = getUtility(IVocabularyFactory, 'TimezoneVocabulary')(None)
    >>> zones = [zone.value for zone in list(allzones)[:4]]

    >>> settings.portal_timezone = zones[0]
    >>> assert([term.value for term in list(tzvocab(None))] == zones[0:1])

    >>> settings.available_timezones = zones[1:]
    >>> assert([term.value for term in list(tzvocab(None))] == zones)

    >>> settings.available_timezones = zones
    >>> assert([term.value for term in list(tzvocab(None))] == zones)

    """
    tzvocab = getUtility(IVocabularyFactory, 'plone.app.event.Timezones')(context)
    return wrap_vocabulary(
        tzvocab,
        visible_terms_from_registry=\
            'plone.app.event.available_timezones'
        )(context)


directlyProvides(Timezones, IVocabularyFactory)
directlyProvides(AvailableTimezones, IVocabularyFactory)
