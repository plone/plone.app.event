import unittest2 as unittest
import doctest

from plone.testing import layered
from plone.app.event.testing import TIMEZONE_LAYER

DOCFILES = [
    '../recurrence.txt',
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
    suite.addTests([
        layered(doctest.DocTestSuite(
                    'plone.app.event.timezone',
                    optionflags=doctest.ELLIPSIS),
                layer = TIMEZONE_LAYER),
    ])
    return suite
