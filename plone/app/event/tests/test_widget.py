from plone.app.event.tests.base import EventTestCase
tests = []

from Products.Archetypes.tests.utils import makeContent
from Products.Archetypes.tests.test_fields import FakeRequest

TESTVALUE = "a testvalue"

class WidgetTestCase(EventTestCase):

    def test_processform(self):
        request = FakeRequest()
        doc = makeContent(self.folder, portal_type='Event', id='demoevent')
        field = doc.Schema()['recurrence']
        widget = field.widget
        form = { 'recurrence': TESTVALUE}
        result = widget.process_form(doc, field, form)
        print result
        assert result == (TESTVALUE, {})
tests.append(WidgetTestCase)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
