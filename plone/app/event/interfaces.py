import zope.interface


class ICalendarSupport(zope.interface.Interface):
    """Calendar import/export
    """

class IEvent(zope.interface.Interface):
    """Generic calendar event for Plone
    """

class IRecurringEvent(zope.interface.Interface):
    """Generic recurring calendar event for Plone
    """

class IRecurrence(zope.interface.Interface):
    """Interface for adapter providing recurrence support
    """

    def recurrence_ruleset():
        """Returns the recurrence ruleset as dateutil.rrule.rruleset instance.
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
