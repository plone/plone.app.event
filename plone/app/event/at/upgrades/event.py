from Products.ATContentTypes.interfaces.event import IATEvent
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.archetypes import ATItemMigrator
from Products.contentmigration.walker import CustomQueryWalker
from transaction import savepoint
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

import transaction
import logging


logger = logging.getLogger('plone.app.event.at migration')


class PAEATMigrator(ATItemMigrator):
    src_portal_type = 'Event'
    src_meta_type = 'ATEvent'
    dst_portal_type = 'Event'
    dst_meta_type = 'ATEvent'

    def migrate_schema(self):
        """Migrate old ATEvent schema to plone.app.event's ATEvent.
        """
        # TODO: assure - if possible - that timezone is set correctly.
        # Call ObjectModifiedEvent to do data_postprocessing on each event
        # object.
        notify(ObjectModifiedEvent(self.new))


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
