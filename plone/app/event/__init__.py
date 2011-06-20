
try:
    from Products.LinguaPlone import public as atapi
except ImportError:
    from Products.Archetypes import atapi

from Products.CMFCore.utils import ContentInit
from plone.app.event import config

from zope.i18nmessageid import MessageFactory
MessageFactory = MessageFactory(config.PROJECTNAME)


def initialize(context):
    """Register content types through Archetypes with Zope and the CMF.
    """

    from plone.app.event.content import at

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)

