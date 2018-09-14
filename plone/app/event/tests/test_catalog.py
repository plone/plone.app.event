# -*- coding: utf-8 -*-
from plone.app.event.testing import PAEvent_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

import unittest


class TextDXIntegration(unittest.TestCase):
    layer = PAEvent_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.catalog = getToolByName(self.portal, 'portal_catalog')

    def test_end_is_DateRecurringIndex(self):
        # end should be a DateRecurringIndex
        self.assertEqual(self.catalog.Indexes['end'].__class__.__name__,
                         'DateRecurringIndex')

    def test_start_is_DateRecurringIndex(self):
        # start should be a DateRecurringIndex
        self.assertEqual(self.catalog.Indexes['start'].__class__.__name__,
                         'DateRecurringIndex')
