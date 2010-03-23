from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
#from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import onsetup
from Products.ATContentTypes.tests import atcttestcase, atctftestcase

@onsetup
def setupPackage():
    fiveconfigure.debug_mode = True
    import plone.app.event
    zcml.load_config('configure.zcml', plone.app.event)
    import Products.Five
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.Five)
    import Products.DateRecurringIndex
    zcml.load_config('configure.zcml', Products.DateRecurringIndex)
    ptc.installProduct('Products.DateRecurringIndex')
    ptc.installProduct('plone.app.event')
    fiveconfigure.debug_mode = False

setupPackage()

ptc.setupPloneSite()
# ptc.PloneTestCase.addProfile
#ptc.setupPloneSite(extension_profiles=['plone.app.event:default'])

class EventTestCase(ptc.PloneTestCase):
    """ Base class for plone.app.event tests """

class EventTypeTestCase(atcttestcase.ATCTTypeTestCase):
    """ """

class EventFieldTestCase(atcttestcase.ATCTFieldTestCase):
    """ """

class EventIntegrationTestCase(atctftestcase.ATCTIntegrationTestCase):
    """ """