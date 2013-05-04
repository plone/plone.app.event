from Products.ATContentTypes.interfaces.event import IATEvent
from Products.Archetypes.annotations import getAnnotation
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.archetypes import ATItemMigrator
from Products.contentmigration.migrator import InlineFieldActionMigrator
from Products.contentmigration.walker import CustomQueryWalker
from plone.app.event.at.interfaces import IATEvent as IATEvent_PAE
from transaction import savepoint
from zope.deprecation import deprecate

import transaction
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
    transaction.commit() # Do a commit before each migration, commiting the
                         # previous changes to avoid running out of space for
                         # large migrations.
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

@deprecate('upgrade_step_2 is an migration step between beta releases of '
           'plone.app.event and likely not neccessary for any installation. '
           'It will be removed with the plone.app.event 1.0 release.')
def upgrade_step_2(context):
    """Upgrade timezone and recurrence from AnnotationStorage to new storage
    (AttributeStorage).

    Using Products.contentmigration doesn't work here, since on migration time,
    the fields' storage is already an AttributeStorage.

    !!! ATTENTION !!!
    This upgrade steps migrates fields if there is a AnnotationStorage entry
    for it, even if there is already a value in AttributeStorage. We have to
    do so, because there is a default value for the timezone, which might not
    be the value previously set with AnnotationStorage.

    """
    migrate_fields = ['timezone', 'recurrence']

    query = {}
    query['object_provides'] = IATEvent_PAE.__identifier__
    cat = getToolByName(context, 'portal_catalog')
    result = cat(**query)

    for brain in result:
        obj = brain.getObject()
        ann = getAnnotation(obj)

        for field in migrate_fields:
            key = 'Archetypes.storage.AnnotationStorage-%s' % field
            if key in ann:
                val = key in ann and ann[key] or None
                del ann[key] # Delete the annotation entry

                getter = getattr(obj, 'get%s' % field.title()) # Get the getter
                prev_val = getter()

                setter = getattr(obj, 'set%s' % field.title()) # Get the setter
                setter(val) # Set the val on new storage

                logger.info("""'Field migration for obj %s, field %s from
                AnnotationStorage to AttributeStorage done. Previous value: %s,
                new value from AnnotationStorage: %s."""
                % (obj, field, prev_val, val))

        # done :)
