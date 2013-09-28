from Products.CMFCore.permissions import setDefaultRoles
from zope.i18nmessageid import MessageFactory

packageName = __name__
messageFactory = MessageFactory(packageName)

ADD_PERMISSION = 'ATContentTypes: Add Event'  # ATContentTypes permissions
PORTAL_ADD_PERMISSION = 'Add portal events'  # CMFCalendar permissions
PORTAL_CHANGE_PERMISSION = 'Change portal events'

setDefaultRoles(ADD_PERMISSION, ('Manager', 'Site Administrator', 'Owner',))
setDefaultRoles(PORTAL_ADD_PERMISSION, ('Manager', 'Site Administrator', 'Owner',))
setDefaultRoles(PORTAL_CHANGE_PERMISSION, ('Manager', 'Site Administrator', 'Owner',))
