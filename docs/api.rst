plone.app.event API
===================

... not far yet and still in progress.
Please also go through the the sourcecode.

Accessing event objects
-----------------------

Event objects implement the ```IEvent``` interface from
```plone.event.interfaces```.


The objects can be accessed like so::

>>> from plone.event.interfaces import IEvent
>>> from plone.event.interfaces import IEventAccessor

>>> IEvent.providedBy(obj)
True

>>> acc = IEventAccessor(obj)
>>> acc.start
datetime...

>>> acc.timezone
'Europe/Vienna'

>>> acc.recurrence
...

>>> acc.occurrences
[IEventAccessor...


dexterity
=========


plone.app.event behaviors
-------------------------

To use the functionality provided by the behaviors, get the behavior adapter
first. For example, for setting or getting attributes of an event object, do:

>>> from plone.app.event.dx.behaviors import IEventBasic
>>> event = IEventBasic(obj)
>>> event.start = datetime(2011,11,11,11,00)
>>> event.end = datetime(2011,11,11,12,00)
>>> event.timezone = 'CET'

>>> import transaction
>>> transaction.commit()



