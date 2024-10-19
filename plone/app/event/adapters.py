from plone.app.contentlisting.interfaces import IContentListingObject
from plone.app.contentlisting.realobject import RealContentListingObject
from zope.interface import implementer


@implementer(IContentListingObject)
class OccurrenceContentListingObject(RealContentListingObject):

    def __getattr__(self, name):
        """We'll override getattr so that we can defer name lookups to
        the real underlying objects without knowing the names of all
        attributes.
        """
        if name.startswith("_"):
            raise AttributeError(name)
        obj = self.getObject()
        # we need to override the behavior of RealContentListingObject
        # because Occurrence objects rely on acquisition to show their title
        # and other attributes
        if hasattr(obj, name):
            return getattr(obj, name)
        raise AttributeError(name)
