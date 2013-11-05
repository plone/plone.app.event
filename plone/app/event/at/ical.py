from Acquisition import aq_inner
from plone.app.event.ical.exporter import construct_icalendar
from plone.event.interfaces import IICalendar
from zope.interface import implementer


@implementer(IICalendar)
def calendar_from_topic(context):
    """Container/Event adapter. Returns an icalendar.Calendar object from a
    Collection.
    """
    context = aq_inner(context)
    result = context.queryCatalog(batch=False, full_objects=False)
    return construct_icalendar(context, result)
