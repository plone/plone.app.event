Developer documentation
=======================

Accessing event objects via an unified accessor object
------------------------------------------------------

To make it easier to support Archetypes and Dexterity based objects, an
adapter for content objects is provided, which allows unified interaction with
event objects.

The interface definition can be found in plone.event.interfaces.IEventAccessor.
Default accessors:

- For IEvent (```plone.event.interfaces.IEvent```) implementing objects:
  ```plone.event.adapters.EventAccessor```.

- For IATEvent (```plone.app.event.at.interfaces.IATEvent```):
  ```plone.app.event.at.content.EventAccessor```.

- For IDXEvent (```plone.app.event.dx.interfaces.IDXEvent```):
  ```plone.app.event.dx.behaviors.EventAccessor```.

- For IOccurrence (```plone.event.interfaces.IOccurrence```):
  ```plone.app.event.recurrence.EventAccessor```.


Event objects implement the ```IEvent``` interface from
```plone.event.interfaces```.

The objects can be accessed like so::

    from plone.event.interfaces import IEventAccessor
    acc = IEventAccessor(obj)
    assert(isinstance(acc.start, datetime)==True)
    assert(isinstance(acc.timezone, string)==True)
    assert(isinstance(acc.recurrence, string)==True)

Set properties of the object via the accessor::

    tz = pytz.timezone('Europe/Vienna')
    acc.start = datetime(2012,12,12, 10,10, tzinfo=tz)
    acc.timezone = 'Europe/London'

TODO: test the above! Are getters/setters properly called?


Getting occurrences from IEventRecurrence implementing objects
--------------------------------------------------------------

Events with recurrence support should implement the IEventRecurrence
(```plone.event.interfaces.IEventRecurrence```) interface.

An IRecurrenceSupport implementing adapter allows the calculation of all
occurrences::

    from plone.event.interfaces import IRecurrenceSupport
    rec_support = IRecurrenceSupport(obj)

    # All occurrences of the object
    rec_support.occurrences()

    # All occurrences within a time range
    start = datetime(2012,1,1)
    end = datetime(2012,1,3)
    rec_support.occurrences(range_start=start, range_end=end)


If you want to get all occurrences from any event within a timeframe, use the
get_events function like so::

    from plone.app.event.base import get_events, localized_now
    occ = get_events(context, start=localized_now(), ret_mode=2, expand=True)


The IEvent interface
--------------------

All event types should implement the ```IEvent``` interface from
```plone.event.interfaces```, in order that some functionality of
plone.app.event can be used. For example, catalog searches for event objects
ask for the ```IEvent``` interface in the ```object_provides``` index::

    from plone.event.interfaces import IEvent
    assert(IEvent.providedBy(obj)==True)

Custom event objects based on plone.app.event
---------------------------------------------

For archetypes, derive from ```plone.app.event.at.content.ATEvent```.

For Dexterity use the ```plone.app.event.dx.behaviors.IEventBasic``` and any
other event related behavior you might need from there.

If you cannot use the above two methods, you can still implement the
```plone.event.interfaces.IEvent``` interface.

In any case you might need to provide an ```IEventAccessor``` adapter. For more
information, see below.



Dexterity behaviors
-------------------

To use the functionality provided by the behaviors, get the behavior adapter
first. For example, for setting or getting attributes of an event object, do::

    from plone.app.event.dx.behaviors import IEventBasic
    event = IEventBasic(obj)
    event.start = datetime(2011,11,11,11,00)
    event.end = datetime(2011,11,11,12,00)
    event.timezone = 'CET'

    import transaction
    transaction.commit()
