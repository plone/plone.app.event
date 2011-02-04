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

        >>> from zope.component import getUtility
        >>> from plone.registry.interfaces import IRegistry
        >>> from plone.app.event.controlpanel.event import IEventSettings
        >>> reg = getUtility(IRegistry)
        >>> settings = reg.forInterface(IEventSettings)

        >>> from plone.event.interfaces import ITimezoneGetter
        >>> tzutil = getUtility(ITimezoneGetter)
        >>> tzutil().timezone
        'CET'

        >>> settings.portal_timezone = "Europe/Vienna"
        >>> tzutil().timezone
        'Europe/Vienna'

        #>>> from interlude import interact; interact(locals(), use_ipython=False )
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IEventSettings)
        timezone = settings.portal_timezone
        # TODO: retrieve the timezone of the current user, if set.
        if not timezone:
            timezone = getUtility(ITimezoneGetter,
                    'FallbackTimezoneGetter')().timezone
        # following statement ensures, that timezone is a valid pytz zone
        return pytz.timezone(timezone).zone


def AvailableTimezonesVocabulary(context):
    """
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
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IEventSettings)
    available = settings.available_timezones or []
    portaltz = settings.portal_timezone
    if portaltz and portaltz not in available: available.append(portaltz)
    tzvocab = getUtility(IVocabularyFactory, 'TimezoneVocabulary')(context)
    return wrap_vocabulary(tzvocab, visible_terms=available)(context)
    # TODO: remove following block
    #return wrap_vocabulary(
    #    tzvocab,
    #    visible_terms_from_registry=\
    #        'plone.app.event.controlpanel.event.IEventSettings.available_timezones'
    #    )(context)
directlyProvides(AvailableTimezonesVocabulary, IVocabularyFactory)
