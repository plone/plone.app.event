import unittest2 as unittest
import doctest
import os.path
from interlude import interact
from plone.testing import layered
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'webdav.txt',
    'controlpanel.txt'
]
DOCMODS = [
    'plone.app.event.base',
]

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(
            doctest.DocFileSuite(
                os.path.join(os.path.dirname(__file__), docfile),
                module_relative=False,
                optionflags=OPTIONFLAGS,
                globs={'interact': interact}
                ), layer=PAEvent_INTEGRATION_TESTING
            ) for docfile in DOCFILES
    ])
    suite.addTests([
        doctest.DocTestSuite(
            docmod,
            optionflags=OPTIONFLAGS,
            globs={'interact': interact}
        ) for docmod in DOCMODS
    ])
    return suite
