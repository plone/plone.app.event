PROJECTNAME = "plone.app.event"

ADD_PERMISSIONS = {'Event': 'Add portal Events'}
CHANGE_PERMISSION = {'Event': 'Change portal events'}

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles(ADD_PERMISSIONS['Event'], ('Manager', 'Owner',))
setDefaultRoles(CHANGE_PERMISSION['Event'], ('Manager', 'Owner',))
