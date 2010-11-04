from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.ATContentTypes.tests.atcttestcase import ATCTTypeTestCase
from Products.ATContentTypes.tests.atcttestcase import ATCTFieldTestCase
from Products.ATContentTypes.tests.atctftestcase import ATCTIntegrationTestCase
from Products.PloneTestCase.layer import onsetup

# TODO: ??? move this to PloneTestCase
# index has to be installed first and not deferred via @onsetup
ztc.installProduct('DateRecurringIndex')

@onsetup
def setupPackage():
    fiveconfigure.debug_mode = True
    import plone.app.event
    zcml.load_config('configure.zcml', plone.app.event)
    ztc.installPackage('plone.app.event')
    fiveconfigure.debug_mode = False
setupPackage()

ptc.setupPloneSite(extension_profiles=['plone.app.event:default'])


class EventTestCase(ptc.PloneTestCase):
    """ Base class for plone.app.event tests """

class EventTypeTestCase(ATCTTypeTestCase):
    """ """

class EventFieldTestCase(ATCTFieldTestCase):
    """ """

class EventIntegrationTestCase(ATCTIntegrationTestCase):
    """ """

