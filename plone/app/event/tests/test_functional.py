# -*- coding: UTF-8 -*-
import plone.app.event.tests.base

from Testing import ZopeTestCase
from Products.ATContentTypes.tests.atcttestcase import ATCTFunctionalSiteTestCase

FILES = ['webdav.txt']

import doctest
OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_NDIFF)

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    from Testing.ZopeTestCase import FunctionalDocFileSuite as FileSuite
    for testfile in FILES:
        suite.addTest(FileSuite(testfile,
                                optionflags=OPTIONFLAGS,
                                package="plone.app.event.tests",
                                test_class=ATCTFunctionalSiteTestCase)
                     )
    return suite
