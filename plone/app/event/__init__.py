from Products.CMFCore.permissions import setDefaultRoles
from zope.i18nmessageid import MessageFactory

packageName = __name__
messageFactory = MessageFactory(packageName)
PloneMessageFactory = MessageFactory('plone')

# BBB Permissions
PORTAL_ADD_PERMISSION = 'Add portal events'  # CMFCalendar/ATCT permissions

setDefaultRoles(
    PORTAL_ADD_PERMISSION,
    ('Manager', 'Site Administrator', 'Owner',)
)
