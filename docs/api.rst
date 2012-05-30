=================================
plone.app.event API documentation
=================================

... in progress

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



