from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.interface import directlyProvides
from collective.elephantvocabulary import wrap_vocabulary
from plone.registry.interfaces import IRegistry
from plone.app.event.controlpanel.event import IEventSettings
from plone.event.interfaces import ITimezoneGetter
import pytz

class TimezoneGetter(object):
    """ Retrieve the timezone from the portal or user.

    """

    @property
    def timezone(self):
        """ Get the timezone.

        >>> from plone.event.interfaces import ITimezoneGetter
        >>> from zope.component import getUtility
        >>> tzutil = getUtility(ITimezoneGetter)
        >>> interact(locals(), use_ipython=False )
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IEventSettings)
        timezone = settings.portal_timezones
        # TODO: retrieve the timezone of the current user, if set.
        if not timezone:
            timezone = getUtility(ITimezoneGetter,
                    'FallbackTimezoneGetter')().timezone
        # following statement ensures, that timezone is a valid pytz zone
        return pytz.timezone(timezone).zone


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
