import unittest
import doctest
from interlude import interact
import zope.component

OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    '../recurrence.txt',
]

from zope.interface import implements
from plone.app.event.interfaces import IRecurringEvent
class RecurrenceStub(object):
    """Basic stub object for testing events.
    """
    implements(IRecurringEvent)
    def __init__(self, recurrence=None, start_date=None, end_date=None):
        self.recurrence = recurrence
        self.start_date = start_date
        self.end_date = end_date
        self.duration = end_date - start_date
        #subject
        #location
        #wholeDay
        #startDate
        #endDate
        #text
        #attendees
        #eventUrl
        #contactName
        #contactEmail
        #contactPhone
        #recurrence
        #start_date
        #end_date
        #duration

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            optionflags=OPTIONFLAGS,
            globs={'interact': interact,},
            tearDown=zope.component.testing.tearDown
        ) for docfile in DOCFILES
    ])
    return suite