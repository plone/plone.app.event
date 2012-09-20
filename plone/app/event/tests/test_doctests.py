import unittest2 as unittest
import doctest
import os.path
from interlude import interact
from plone.testing import layered
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING


OPTIONFLAGS = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
DOCFILES = [
    'controlpanel.rst',
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
    return suite
