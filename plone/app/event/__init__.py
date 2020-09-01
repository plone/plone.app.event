# -*- coding: utf-8 -*-
from AccessControl.Permission import addPermission
from zope.i18nmessageid import MessageFactory

packageName = __name__
_ = MessageFactory('plone')

# BBB Permissions
PORTAL_ADD_PERMISSION = 'Add portal events'  # CMFCalendar/ATCT permissions

addPermission(
    PORTAL_ADD_PERMISSION,
    ('Manager', 'Site Administrator', 'Owner',)
)
