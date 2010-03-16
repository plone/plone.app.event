PROJECTNAME = "plone.app.event"

ADD_PERMISSIONS = {'Event': 'ATContentTypes: Add Event'}
CHANGE_PERMISSION = {'Event': 'Change portal events'}

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles(ADD_PERMISSIONS['Event'], ('Manager', 'Owner',))
setDefaultRoles(CHANGE_PERMISSION['Event'], ('Manager', 'Owner',))
