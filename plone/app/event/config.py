PROJECTNAME = "plone.app.event"

ADD_PERMISSIONS = {'Event': 'plone.app.event: Add portal events'}
CHANGE_PERMISSION = {'Event': 'plone.app.event: Change portal events'}

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles(ADD_PERMISSIONS['Event'], ('Manager', 'Owner',))
setDefaultRoles(CHANGE_PERMISSION['Event'], ('Manager', 'Owner',))