import datetime
import unittest
from plone.app.event.utils import n2rn, vformat, rfc2445dt, foldline

from DateTime import DateTime

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
        
    def test_rfc2445dt(self):
        dt = DateTime('2005/07/20 18:00:00 Brazil/East')
        self.assertEqual(rfc2445dt(dt), '20050720T210000Z')
        
        dt = DateTime('2010/08/31 20:15:00 GMT+1')
        self.assertEqual(rfc2445dt(dt), '20100831T191500Z')
        
        # we need a DateTime-object as input
        dt = datetime.datetime.now()
        self.assertRaises(AttributeError, rfc2445dt, dt) 
 
    def test_foldline(self):
        self.assertEqual(foldline('foo'), 'foo\n')
        longtext = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                    "Vestibulum convallis imperdiet dui posuere.")
        self.assertEqual(foldline(longtext),
            ('Lorem ipsum dolor sit amet, consectetur adipiscing '
             'elit. Vestibulum co\n nvallis imperdiet dui posuere.\n'))
        
        
def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
