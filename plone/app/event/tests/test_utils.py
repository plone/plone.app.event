import unittest
from plone.app.event.tests.base import TestCase
from plone.app.event.utils import n2rn

class UtilsTestCase(unittest.TestCase):

    def test_n2rn(self):
        self.assertEqual(n2rn('hello\nworld'),
                         'hello\r\nworld')
        self.assertEqual(n2rn('foo'), 'foo')

def test_suite():
     return unittest.defaultTestLoader.loadTestsFromName(__name__)
