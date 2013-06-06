from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.ZCatalog.Catalog import CatalogError
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

        plone.app.event:default .. Necessary, if you plan to use a custom type
        and not install the provided ones. But not necessary when creating a
        Plone site.

        plone.app.event.ploneintegration:prepare .. Called by
        plone.app.event.ploneintegration:default and used to upgrade from older
        Plone sites.

        """
        return [u'plone.app.event:default',
                u'profile-plone.app.event.ploneintegration:prepare']


def catalog_setup(context):
    """Setup plone.app.event's indices in the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.

    See these discussions for more info about index clearing with catalog.xml:
        http://plone.293351.n2.nabble.com/How-to-import-catalog-xml-without-emptying-the-indexes-td2302709.html
        https://mail.zope.org/pipermail/zope-cmf/2007-March/025664.html
    """
    if isNotThisProfile(context, 'plone.app.event-default.txt'): return

    site = context.getSite()
    catalog = getToolByName(site, 'portal_catalog')
    idxs = ['start', 'end']

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
            # create new DateRecurringIndex
            catalog.addIndex(name, 'DateRecurringIndex', extra=extra())
            logger.info('Catalog DateRecurringIndex %s created.' % name)
        try:
            catalog.addColumn(name)
            logger.info('Catalog metadata column %s created.' % name)
        except CatalogError:
            logger.info('Catalog metadata column %s already exists.' % name)
