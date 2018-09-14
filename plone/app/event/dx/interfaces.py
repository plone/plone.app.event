# -*- coding: utf-8 -*-
from plone.event.interfaces import IEvent
from plone.event.interfaces import IEventRecurrence


class IDXEvent(IEvent):
    """ Marker interface for Dexterity events.
    """


class IDXEventRecurrence(IEventRecurrence):
    """ Marker interface for recurring Dexterity events.
    """
