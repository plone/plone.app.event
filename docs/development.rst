Developer documentation
=======================

The IEvent interface
--------------------

All event types should implement the ``IEvent`` interface from ``plone.event.interfaces``, in order that some functionality of plone.app.event can be used. For example, catalog searches for event objects ask for the ``IEvent`` interface in the ``object_provides`` index::

    from plone.event.interfaces import IEvent
    assert(IEvent.providedBy(obj)==True)


Custom event content types
--------------------------

Using Dexterity behaviors to build new content types with IEvent support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For Dexterity use the ``plone.app.event.dx.behaviors.IEventBasic`` and optionally any other event related behavior from there.

You can just enable the behaviors you want to use for your custom content type in the FTI via GenericSetup or through the web. This ``types/Event.xml`` GenericSetup FTI configuration snippet from `plone.app.contenttypes <https://github.com/plone/plone.app.contenttypes/blob/paevent/plone/app/contenttypes/profiles/default/types/Event.xml>`_ shows an example. The only behavior, which is definitely needed is the IEventBasic behavior. All other are optional::

    <property name="behaviors">
        <element value="plone.app.event.dx.behaviors.IEventBasic"/>
        <element value="plone.app.event.dx.behaviors.IEventRecurrence"/>
        <element value="plone.app.event.dx.behaviors.IEventLocation"/>
        <element value="plone.app.event.dx.behaviors.IEventAttendees"/>
        <element value="plone.app.event.dx.behaviors.IEventContact"/>
        <element value="plone.app.contenttypes.behaviors.richtext.IRichText"/>
        <element value="plone.app.dexterity.behaviors.metadata.IDublinCore"/>
        <element value="plone.app.content.interfaces.INameFromTitle"/>
        <element value="plone.app.dexterity.behaviors.discussion.IAllowDiscussion"/>
        <element value="plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation"/>
        <element value="plone.app.relationfield.behavior.IRelatedItems"/>
        <element value="plone.app.versioningbehavior.behaviors.IVersionable" />
    </property>


Of course, it's also possible to create a new behavior which derives from plone.app.event's one, like so::

    from plone.app.event.dx.behaviors import IEventBasic
    from plone.app.event.dx.behaviors import IEventLocation
    from plone.app.event.dx.behaviors import IEventRecurrence
    from plone.app.event.dx.behaviors import first_weekday_sun0
    from plone.app.event.dx.interfaces import IDXEvent
    from plone.app.event.dx.interfaces import IDXEventLocation
    from plone.app.event.dx.interfaces import IDXEventRecurrence
    from plone.autoform import directives as form
    from plone.autoform.interfaces import IFormFieldProvider
    from zope.interface import alsoProvides


    class IEvent(IEventBasic, IEventRecurrence, IEventLocation,
                 IDXEvent, IDXEventLocation, IDXEventRecurrence):
        """Custom Event behavior."""
        form.widget('start', first_day=first_weekday_sun0)
        form.widget('end', first_day=first_weekday_sun0)
        form.widget('recurrence',
                    start_field='IEvent.start',
                    first_day=first_weekday_sun0)
    alsoProvides(IEvent, IFormFieldProvider)

.. note::

  If you don't register the behavior with a factory and a marker interface like it's done in plone.app.event, the behavior is the marker interface itself (see plone.app.dexterity's `documentation on behavior marker interfaces <https://developer.plone.org/reference_manuals/external/plone.app.dexterity/behaviors/providing-marker-interfaces.html>`_).  In this case, the behavior should also derive from the marker interfaces defined in ``plone.app.event.dx.interfaces`` in order to let it use all of plone.app.event's functionality (indexers, adapters and the like).

.. note::

  You have to reconfigure the start, end and recurrence fields' widgets again.  The widgets for the ``start`` and ``end`` fields have to be configured with the ``first_day`` parameter while the ``recurrence`` field widget has to be configured with the ``first_day`` and ``start_field`` parameters. Even if the ``start`` field is derived from another behavior, in this case the dotted-path includes the new behavior: ``IEvent.start``.


Then register the behavior in ZCML::

    <plone:behavior
        title="Event"
        description="A Event"
        provides=".behaviors.IEvent"
        for="plone.dexterity.interfaces.IDexterityContent"
        />

And register it in your FTI via GenericSetup as usual.


None of the above
~~~~~~~~~~~~~~~~~

If you cannot use the above two methods, you can still implement the ``plone.event.interfaces.IEvent`` interface.

In any case you might need to provide an ``IEventAccessor`` adapter. For more information, see below.


Getting and setting properties
------------------------------

Setting properties directly on the context
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since plone.app.event version 2.0, you can set properties directly on the context. There is no need to use behavior adaption any more.

Though, you have to take care to set properties wisely, read on.

1) Always use a timezone::
   
    import pytz
    tz = pytz.timezone("Europe/Vienna")
    event.start = tz.localize(datetime(2010, 10, 10, 12, 12))
    event.end = tz.localize(datetime(2010, 10, 10, 13, 13))

Always use pytz's `tz.localize(datetime(2010, 10, 10, 12, 12))`. If you set the tzinfo object directly on the datetime object like `datetime(2010, 10, 10, 12, 12, tzinfo=tz)`, the datetime object might not localized to the DST changes of your timezone!


2) Since plone.app.event 2.0b1, there is no need to call the ``data_postprocessing`` function to manipulate the object accordingly to the value of the ``whole_day`` or ``end_date`` attributes. The start and end dates are only converted to the beginning respectively to the end of the day for indexing and when accessing the dates via the IEventAccessor.


Accessing event objects via an unified accessor object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO: only DX

To make it easier to support Archetypes and Dexterity based objects, an adapter for content objects is provided, which allows unified interaction with event objects.

The interface definition can be found in plone.event.interfaces.IEventAccessor.

Default accessors:

- For IEvent (``plone.event.interfaces.IEvent``) implementing objects: ``plone.event.adapters.EventAccessor``.

- For IATEvent (``plone.app.event.at.interfaces.IATEvent``): ``plone.app.event.at.content.EventAccessor``.

- For IDXEvent (``plone.app.event.dx.interfaces.IDXEvent``): ``plone.app.event.dx.behaviors.EventAccessor``.

- For IOccurrence (``plone.event.interfaces.IOccurrence``): ``plone.app.event.recurrence.EventAccessor``.


Event objects implement the ``IEvent`` interface from ``plone.event.interfaces``.

The objects can be accessed like so::

    from plone.event.interfaces import IEventAccessor
    acc = IEventAccessor(obj)
    assert(isinstance(acc.start, datetime)==True)
    assert(isinstance(acc.timezone, string)==True)
    assert(isinstance(acc.recurrence, string)==True)

Set properties of the object via the accessor. Don't forget to throw ObjectModifiedEvent after setting properties to call an event subscriber which does some timezone related post calculations::

    from zope.event import notify
    from zope.lifecycleevent import ObjectModifiedEvent
    tz = pytz.timezone('Europe/Vienna')
    acc.start = datetime(2012, 12, 12, 10, 10, tzinfo=tz)
    acc.timezone = 'Europe/London'
    notify(ObjectModifiedEvent(obj))

You can also use the accessor edit method, which also throws the ObjectModifiedEvent event for you::

    acc.edit(end=datetime(2012, 12, 12, 20, 0, tzinfo=tz))

For creating events, you can use the accessor's create method, which again returns an accessor. E.g. if you want to create the Dexterity based event type::

    from plone.app.event.dx.behaviors import EventAccessor
    acc = EventAccessor.create(
        container=app.plone,
        content_id=u'new_event'
        title=u'New Event'
        start=datetime(2013, 7, 1, 10, 0, tzinfo=tz),
        end=datetime(2013, 7, 1, 12, 0, tzinfo=tz),
        timezone='Europe/Vienna'
    )
    acc.location = u"Graz, Austria"

Access the content object from an accessor like so::

    obj = acc.context
    from plone.event.interfaces import IEvent
    assert(not IEvent.providedBy(acc))
    assert(IEvent.providedBy(obj))


Getting occurrences from IEventRecurrence implementing objects
--------------------------------------------------------------

Events with recurrence support should implement the IEventRecurrence (``plone.event.interfaces.IEventRecurrence``) interface.

An IRecurrenceSupport implementing adapter allows the calculation of all occurrences::

    from plone.event.interfaces import IRecurrenceSupport
    rec_support = IRecurrenceSupport(obj)

    # All occurrences of the object
    rec_support.occurrences()

    # All occurrences within a time range
    start = datetime(2012,1,1)
    end = datetime(2012,1,3)
    rec_support.occurrences(range_start=start, range_end=end)


If you want to get all occurrences from any event within a timeframe, use the get_events function like so::

    from plone.app.event.base import get_events, localized_now
    occ = get_events(context, start=localized_now(), ret_mode=2, expand=True)


Reusing the @@event_summary view to list basic event information
----------------------------------------------------------------

The @@event_summary listing lists basic event information including microdata on the right hand side of the default event view. You can reuse this listing in custom views by calling the event_summary view on an IEvent providing context in page templates like so::

    <tal:eventsummary replace="structure context/@@event_summary"/>

or in Python code like so::

    context.restrictedTraverse('@@event_ticket_summary')()

There are cases where you might exclude some of this information. You can do that by overriding the `excludes` list of the view. Possible values are::

    title
    subjects
    date
    occurrences
    location
    contact
    event_url
    ical
