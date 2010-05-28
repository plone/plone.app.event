import plone.app.event.tests.base

from Testing import ZopeTestCase # side effect import. leave it here.
from Products.ATContentTypes.tests import atcttestcase

from Products.Archetypes.atapi import *

tests = []

class TestBugs(atcttestcase.ATCTSiteTestCase):

    def afterSetUp(self):
        atcttestcase.ATCTSiteTestCase.afterSetUp(self)
        self.wf = self.portal.portal_workflow

    def test_dt2DT2dtTZbug(self):
        # Tests problems with conversion between datetime and DateTime becoming naive of timezones
        import DateTime
        from plone.app.event.dtutils import DT2dt,dt2DT
        PartyBST = DateTime.DateTime("2007-07-19 20:00 GMT+0100")
        PartyUTC = DateTime.DateTime("2007-07-19 19:00 GMT+0000")
        PartyEDT = DateTime.DateTime("2007-07-19 15:00 GMT-0400")
        self.assertEqual(PartyUTC, PartyBST)
        self.assertEqual(PartyUTC, PartyEDT)
        partyUTC = DT2dt(PartyUTC)
        self.assertEqual(str(dt2DT(partyUTC)), str(PartyUTC))
        partyEDT = DT2dt(PartyEDT)
        self.assertEqual(str(dt2DT(partyEDT)), str(PartyEDT))
        partyBST = DT2dt(PartyBST)
        self.assertEqual(str(dt2DT(partyBST)), str(PartyBST))
        self.assertNotEqual(str(dt2DT(partyEDT)), str(PartyBST))
        self.assertNotEqual(str(dt2DT(partyUTC)), str(PartyBST))
        self.assertNotEqual(str(dt2DT(partyEDT)), str(PartyUTC))

tests.append(TestBugs)

import unittest
def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite
