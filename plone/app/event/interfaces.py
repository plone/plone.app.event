from zope.interface import Interface
from Products.ATContentTypes.interfaces.interfaces import IATContentType

class IATEvent(IATContentType):
    """AT Event marker interface
     """

class ICalendarSupport(Interface):
    """Calendar import/export
    """