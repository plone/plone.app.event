from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n.locales import locales, LoadLocaleError


def first_weekday_setup(context):
    """Set the first day of the week based on the portal's locale.
    """
    reg = getUtility(IRegistry)
    if "plone.first_weekday" in reg and reg["plone.first_weekday"] is not None:
        # don't overwrite if it's already set
        return

    first = 6
    try:
        site = getSite()
        # find the locale implied by the portal's language
        language = site.Language()
        parts = (language.split('-') + [None, None])[:3]
        locale = locales.getLocale(*parts)
        # look up first day of week
        gregorian_calendar = locale.dates.calendars.get(u'gregorian', None)
        if gregorian_calendar is not None:
            day = gregorian_calendar.week.get('firstDay', 7)
            first = 6 if day == 0 else day - 1
    except LoadLocaleError:
        # If we cannot get the locale, just Sunday as first weekday
        pass

    # save setting
    reg['plone.first_weekday'] = first


def setup_misc(context):
    if context.readDataFile('plone.app.event.bbb.txt') is None:
        return

    portal = context.getSite()
    first_weekday_setup(context)
