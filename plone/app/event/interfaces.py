from zope.interface import Interface

class ICalendarSupport(Interface):
    """Calendar import/export
    """

class IEvent(Interface):
    """Generic calendar event for Plone
    """

class IRecurringEvent(Interface):
    """Generic recurring calendar event for Plone
    """

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