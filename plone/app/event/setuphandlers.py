# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INonInstallable
from Products.ZCatalog.Catalog import CatalogError
from zope.interface import implementer

import logging


logger = logging.getLogger(__name__)


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Prevents profiles, which should not be user-installable from showing
        up in the profile list when creating a Plone site.

        plone.app.event:testing .. Testing profile, which provides an
        example type.
        """
        return [u'plone.app.event:testing', ]


def setup_catalog(context):
    """Setup plone.app.event's indices in the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.

    See these discussions for more info about index clearing with catalog.xml:
        http://plone.293351.n2.nabble.com/How-to-import-catalog-xml-without-
        emptying-the-indexes-td2302709.html
        https://mail.zope.org/pipermail/zope-cmf/2007-March/025664.html
    """
    if context.readDataFile('plone.app.event-default.txt') is None:
        return
    portal = context.getSite()
    catalog = getToolByName(portal, 'portal_catalog')
    date_idxs = ['start', 'end']
    field_idxs = ['sync_uid']
    idxs = date_idxs + field_idxs

    class extra(object):
        recurdef = 'recurrence'
        until = ''

    _catalog = catalog._catalog
    for name in idxs:
        if name in catalog.indexes():
            if _catalog.getIndex(name).meta_type == 'DateIndex':
                # delete old standard DateIndex
                catalog.delIndex(name)
                logger.info('Old catalog DateIndex %s deleted.' % name)
        if name not in catalog.indexes():
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
