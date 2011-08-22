PROJECTNAME = "plone.app.event"

ADD_PERMISSION = 'ATContentTypes: Add Event' # ATContentTypes permissions
PORTAL_ADD_PERMISSION = 'Add portal events' # CMFCalendar permissions
PORTAL_CHANGE_PERMISSION = 'Change portal events'

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles(PORTAL_ADD_PERMISSION, ('Manager', 'Site Administrator', 'Owner',))
setDefaultRoles(PORTAL_CHANGE_PERMISSION, ('Manager', 'Site Administrator', 'Owner',))
setDefaultRoles(ADD_PERMISSION, ('Manager', 'Site Administrator', 'Owner',))
