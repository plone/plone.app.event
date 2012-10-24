from Products.ATContentTypes.interfaces.event import IATEvent
from Products.contentmigration.archetypes import ATItemMigrator
from Products.contentmigration.migrator import InlineFieldActionMigrator
from Products.contentmigration.walker import CustomQueryWalker
from Products.CMFCore.utils import getToolByName
from plone.app.event.at import atapi
from transaction import savepoint
import logging

logger = logging.getLogger('plone.app.event.at migration')


class PAEATMigrator(ATItemMigrator):
    src_portal_type = 'Event'
    src_meta_type = 'ATEvent'
    dst_portal_type = 'Event'
    dst_meta_type = 'ATEvent'

class PAEATInlineMigrator(InlineFieldActionMigrator):
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

def upgrade_step_1(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    walker = CustomQueryWalker(
        portal, PAEATMigrator,
        query=dict(object_provides=IATEvent.__identifier__),
        callBefore=callBefore)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()

def upgrade_step_2(context):
    portal = getToolByName(context, 'portal_url').getPortalObject()
    PAEATInlineMigrator.fieldActions = (
        {'fieldName': 'timezone',
         'storage':    atapi.AnnotationStorage(),
         'newStorage': atapi.AttributeStorage()
        },
        {'fieldName': 'recurrence',
         'storage':    atapi.AnnotationStorage(),
         'newStorage': atapi.AttributeStorage()
        },
    )
    from plone.app.event.at.interfaces import IATEvent as IATEvent_PAE
    walker = CustomQueryWalker(
        portal, PAEATInlineMigrator,
        query=dict(object_provides=IATEvent_PAE.__identifier__))
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()
