from plone.app.contenttypes.migration.dxmigration import migrate
from zope.component.hooks import getSite


def upgrade_attribute_storage(context):
    portal = getSite()
    migrate(portal, AttributeStorageMigrator)
