from plone.app.event.event import ATEvent

from zope.i18nmessageid import MessageFactory

from plone.app.event import config

try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from Products.CMFCore.utils import ContentInit

messageFactory = MessageFactory(config.PROJECTNAME)


def initialize(context):
    """Register content types through Archetypes with Zope and the CMF.
    """
    import plone.app.event.event

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)

