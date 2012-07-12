from Products.ATContentTypes.interfaces.event import IATEvent
from Products.contentmigration.archetypes import ATItemMigrator
from Products.contentmigration.walker import CustomQueryWalker
from Products.CMFCore.utils import getToolByName
from transaction import savepoint
import logging


logger = logging.getLogger('plone.app.event.at migration')


def migrateATEvents(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    walker = CustomQueryWalker(
        portal, PAEATMigrator,
        query=dict(object_provides=IATEvent.__identifier__),
        callBefore=callBefore)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


class PAEATMigrator(ATItemMigrator):
    src_portal_type = 'Event'
    src_meta_type = 'ATEvent'
    dst_portal_type = 'Event'
    dst_meta_type = 'ATEvent'


def callBefore(oldobj):
    if 'portal_factory' in oldobj.getPhysicalPath():
        logger.info('Skipping factory obj: {0}'.format(
            '/'.join(oldobj.getPhysicalPath())))
        return False
    return True
