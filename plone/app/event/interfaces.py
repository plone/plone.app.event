from zope.interface import Interface
from zope.interface import Attribute

class ICalendarSupport(Interface):
    """Calendar import/export
    """

class IEvent(Interface):
    """Generic calendar event for Plone
    """

class IRecurringEvent(Interface):
    """Generic recurring calendar event for Plone
    """
    recurrence = Attribute(u'Recurrence definition according to RFC2445')
    start_date = Attribute(u"""Date when the first occurence of the event
                               begins as datetime object""")
    end_date = Attribute(u"""Date when the first occurence of the event ends as
                             datetime object""")

class IRecurrenceSupport(Interface):
    """Interface for adapter providing recurrence support
    """

    def occurences_start():
        """Returns all the event's start occurences which indicates the
           beginning of each event.
        """

    def occurences_end():
        """Returns all the event's end occurences which indicates the
           ending of each event.
        """

    def occurences():
        """Returns all the event's start and end occurences as a list of tuples.
        """