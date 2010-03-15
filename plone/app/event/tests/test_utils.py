import unittest
from plone.app.event.tests.base import TestCase
from plone.app.event.utils import n2rn, vformat, rfc2445dt


class UtilsTestCase(unittest.TestCase):

    def test_n2rn(self):
        self.assertEqual(n2rn('hello\nworld'),
                         'hello\r\nworld')
        self.assertEqual(n2rn('foo'), 'foo')

    def test_vformat(self):
        self.assertEqual(vformat('foo'), 'foo')
        self.assertEqual(vformat('foo,bar'), 'foo\,bar')
        self.assertEqual(vformat('foo;bar'), 'foo\;bar')
        self.assertEqual(vformat('foo:bar'), 'foo\:bar')
        self.assertEqual(vformat('foo:bar,more'), 'foo\:bar\,more')
        
class MoreUtilsTestCase(TestCase):

    def test_rfc2445dt(self):
        pass
        

def test_suite():
     return unittest.defaultTestLoader.loadTestsFromName(__name__)
