from Products.CMFCore.permissions import setDefaultRoles
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

packageName = __name__

ADD_PERMISSION = 'ATContentTypes: Add Event'  # ATContentTypes permissions
PORTAL_ADD_PERMISSION = 'Add portal events'  # CMFCalendar permissions
PORTAL_CHANGE_PERMISSION = 'Change portal events'

setDefaultRoles(
    ADD_PERMISSION,
    ('Manager', 'Site Administrator', 'Owner',)
)
setDefaultRoles(
    PORTAL_ADD_PERMISSION,
    ('Manager', 'Site Administrator', 'Owner',)
)
setDefaultRoles(
    PORTAL_CHANGE_PERMISSION,
    ('Manager', 'Site Administrator', 'Owner',)
)


def initialize(context):
    """Register content types through Archetypes with Zope and the CMF.
    """
    from Products.CMFCore.utils import ContentInit
    from plone.app.event.at import content  # nopep8

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(packageName), packageName)

    assert len(content_types) == 1, 'only one new event, please!'

    for atype, constructor, fti in zip(content_types, constructors, ftis):
        ContentInit(
            "%s: %s" % (packageName, atype.portal_type),
            content_types=(atype,),
            permission=ADD_PERMISSION,
            extra_constructors=(constructor,),
            fti=(fti,),
        ).initialize(context)
