import pkg_resources
from Testing import ZopeTestCase as ztc
from AccessControl.PermissionRole import rolesForPermissionOn
from Products.CMFPlone.tests import PloneTestCase

# without this some permissions don't get initialized
ztc.installProduct('Transience')


class TestSiteAdministratorRole(PloneTestCase.PloneTestCase):

    def testExpectedPermissions(self):
        # This integration test shows that the correct permissions were
        # assigned to the Site Administrator role (whether inherited from the
        # Zope application, or specified in the portal rolemap).
        expected = {
            
            }

        site = self.portal
        errors = []
        p = 'Add portal events'
        expected_value = 1
        enabled = 'Site Administrator' in rolesForPermissionOn(p, site)
        if expected_value and not enabled:
            errors.append('%s: should be enabled' % p)
        elif enabled and not expected_value:
            errors.append('%s: should be disabled' % p)
        if errors:
            self.fail(
                'Unexpected permissions for Site Administrator role:\n' +
                ''.join(['\t%s\n' % msg for msg in errors])
             )
