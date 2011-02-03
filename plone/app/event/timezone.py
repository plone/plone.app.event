from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import directlyProvides
from collective.elephantvocabulary import wrap_vocabulary
from plone.registry.interfaces import IRegistry
from plone.app.event.controlpanel.event import IEventSettings

# TODO: cache me
def AvailableTimezonesVocabulary(context):
    """
    >>> import zope.component
    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> tzvocab = zope.component.getUtility(IVocabularyFactory,
    ...     'AvailableTimezonesVocabulary')
    >>> interact(locals(), use_ipython=False )
    """
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IEventSettings)
    available = settings.available_timezones
    if settings.portal_timezone not in available:
        available.append(settings.portal_timezone)
    tzvocab = getUtility(IVocabularyFactory, 'TimezoneVocabulary')
    return wrap_vocabulary(tzvocab, visible_terms=available)
directlyProvides(AvailableTimezonesVocabulary, IVocabularyFactory)
