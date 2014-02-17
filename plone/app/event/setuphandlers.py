from plone.app.event.base import wkday_to_mon0
from plone.app.event.interfaces import IEventSettings
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.ZCatalog.Catalog import CatalogError
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n.locales import locales
from zope.i18n.locales import LoadLocaleError
from zope.interface import implements
import logging


logger = logging.getLogger(__name__)


def isNotThisProfile(context, marker_file):
    return context.readDataFile(marker_file) is None


class HiddenProfiles(object):
    implements(INonInstallable)

    def getNonInstallableProfiles(self):
        """Prevents profiles, which should not be user-installable from showing
        up in the profile list when creating a Plone site.

        plone.app.event:testing .. Testing profile, which provides an
        example type.
        """
        return [u'plone.app.event:testing', ]


def catalog_setup(context):
    """Setup plone.app.event's indices in the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.

    See these discussions for more info about index clearing with catalog.xml:
        http://plone.293351.n2.nabble.com/How-to-import-catalog-xml-without-
        emptying-the-indexes-td2302709.html
        https://mail.zope.org/pipermail/zope-cmf/2007-March/025664.html
    """
    site = getSite()
    catalog = getToolByName(site, 'portal_catalog')
    date_idxs = ['start', 'end']
    field_idxs = ['sync_uid']
    idxs = date_idxs + field_idxs

    class extra(object):
        recurdef = 'recurrence'
        until = ''

    idxobj = catalog.Indexes
    for name in idxs:
        if name in idxobj:
            if idxobj[name].meta_type == 'DateIndex':
                # delete old standard DateIndex
                catalog.delIndex(name)
                logger.info('Old catalog DateIndex %s deleted.' % name)
        if name not in idxobj:
            if name in date_idxs:
                # create new DateRecurringIndex
                catalog.addIndex(name, 'DateRecurringIndex', extra=extra())
                logger.info('Catalog DateRecurringIndex %s created.' % name)
            elif name in field_idxs:
                catalog.addIndex(name, 'FieldIndex')
                logger.info('Catalog FieldIndex %s created.' % name)
        try:
            catalog.addColumn(name)
            logger.info('Catalog metadata column %s created.' % name)
        except CatalogError:
            logger.info('Catalog metadata column %s already exists.' % name)


def first_weekday_setup(context):
    """Set the first day of the week based on the portal's locale.
    """
    reg = getUtility(IRegistry)
    settings = reg.forInterface(IEventSettings, prefix="plone.app.event")
    if settings.first_weekday is not None:
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
            first = wkday_to_mon0(gregorian_calendar.week.get('firstDay', 7))
    except LoadLocaleError:
        # If we cannot get the locale, just Sunday as first weekday
        pass
    # save setting
    settings.first_weekday = first


def setup_misc(context):
    if isNotThisProfile(context, 'plone.app.event-default.txt'):
        return

    portal = context.getSite()

    catalog_setup(portal)
    first_weekday_setup(portal)
