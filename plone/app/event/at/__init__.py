try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from Products.CMFCore.utils import ContentInit
from plone.app.event import PROJECTNAME, ADD_PERMISSION


def initialize(context):
    """Register content types through Archetypes with Zope and the CMF.
    """

    from plone.app.event.at import content

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(PROJECTNAME), PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        ContentInit("%s: %s" % (PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = ADD_PERMISSION,
            extra_constructors = (constructor,),
            ).initialize(context)
