import plone.app.event as config
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi
from Products.CMFCore.utils import ContentInit


def initialize(context):
    """Register content types through Archetypes with Zope and the CMF.
    """

    from plone.app.event.at import content

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME), config.PROJECTNAME)

    assert len(content_types) == 1, 'only one new event, please!'

    for atype, constructor, fti in zip(content_types, constructors, ftis):
        ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = ADD_PERMISSION,
            extra_constructors = (constructor,),
            fti = (fti,),
            ).initialize(context)
