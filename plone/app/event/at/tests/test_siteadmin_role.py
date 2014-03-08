from AccessControl.PermissionRole import rolesForPermissionOn
from plone.app.event.testing import PAEventAT_INTEGRATION_TESTING

import unittest2 as unittest


class TestSiteAdministratorRole(unittest.TestCase):
    layer = PAEventAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_expected_permissions(self):
        """This integration test shows that the correct permissions were
        assigned to the Site Administrator role (whether inherited from the
        Zope application, or specified in the portal rolemap).
        """
        site = self.portal
        perm = 'Add portal events'
        role = 'Site Administrator'
        self.assertTrue(role in rolesForPermissionOn(perm, site))
