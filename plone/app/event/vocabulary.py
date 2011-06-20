import pytz

from zope.interface import directlyProvides
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from collective.elephantvocabulary import wrap_vocabulary


def Timezones(context):
    """
    >>> import zope.component
    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> tzvocab = zope.component.getUtility(IVocabularyFactory, 'TimezoneVocabulary')

    TODO: find something more breakage proof than following test
    >>> assert('Africa/Abidjan' == list(tzvocab(None))[0].value)

    TODO: make timezone source adaptable to provide vocab with commont_timezones
          or all_timezones
    """
    return SimpleVocabulary.fromValues(pytz.all_timezones)


def AvailableTimezones(context):
    """
    """
    tzvocab = getUtility(IVocabularyFactory, 'plone.app.event.Timezones')(context)
    return wrap_vocabulary(
        tzvocab,
        visible_terms_from_registry=\
            'plone.app.event.available_timezones'
        )(context)


directlyProvides(Timezones, IVocabularyFactory)
directlyProvides(AvailableTimezones, IVocabularyFactory)
