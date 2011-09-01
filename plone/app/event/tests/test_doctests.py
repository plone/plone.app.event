import unittest2 as unittest
import doctest

DOCFILES = [
    'webdav.txt'
]
def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocFileSuite(
            docfile,
            optionflags=doctest.ELLIPSIS,
        ) for docfile in DOCFILES
    ])
    return suite
